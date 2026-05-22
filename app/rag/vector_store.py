"""ChromaDB persistent vector storage."""

from typing import Any

from app.rag.embeddings import embed_texts
from app.utils.config import settings
from app.utils.logging_config import logger


def _get_chroma_client():
    import chromadb
    from chromadb.config import Settings as ChromaSettings

    return chromadb, ChromaSettings


class VectorStore:
    def __init__(self) -> None:
        chromadb, ChromaSettings = _get_chroma_client()
        settings.chroma_path.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(
            path=str(settings.chroma_path),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=settings.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("ChromaDB collection ready: %s", settings.collection_name)

    @property
    def count(self) -> int:
        return self._collection.count()

    def add_chunks(self, chunks: list[dict[str, Any]]) -> int:
        if not chunks:
            return 0

        ids = [c["metadata"]["chunk_id"] for c in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]
        embeddings = embed_texts(documents)

        # Upsert to allow re-ingestion of same document
        self._collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )
        logger.info("Upserted %d chunks into vector store", len(chunks))
        return len(chunks)

    def query(
        self,
        query_text: str,
        top_k: int | None = None,
        where: dict | None = None,
    ) -> list[dict[str, Any]]:
        k = top_k or settings.top_k
        query_embedding = embed_texts([query_text])[0]

        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        retrieved: list[dict[str, Any]] = []
        if not results["ids"] or not results["ids"][0]:
            return retrieved

        for i, chunk_id in enumerate(results["ids"][0]):
            distance = results["distances"][0][i] if results["distances"] else 1.0
            # Chroma cosine distance: lower is more similar; convert to similarity
            similarity = max(0.0, 1.0 - distance)
            retrieved.append(
                {
                    "chunk_id": chunk_id,
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "similarity": round(similarity, 4),
                    "distance": round(distance, 4),
                }
            )

        logger.info(
            "Retrieved %d chunks for query (top similarity=%.3f)",
            len(retrieved),
            retrieved[0]["similarity"] if retrieved else 0.0,
        )
        return retrieved

    def delete_by_source(self, source_file: str) -> None:
        self._collection.delete(where={"source_file": source_file})
        logger.info("Deleted chunks for source: %s", source_file)


_vector_store: VectorStore | None = None


def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
