"""Semantic retrieval with similarity thresholding."""

from typing import Any

from app.rag.rerank import rerank_chunks
from app.rag.scoring import compute_confidence, filter_by_threshold
from app.rag.vector_store import get_vector_store
from app.utils.config import settings
from app.utils.logging_config import logger

# Re-export for backward compatibility
INSUFFICIENT_MSG = (
    "The provided documents do not contain enough information to answer "
    "this question confidently."
)


def retrieve(
    query: str,
    top_k: int | None = None,
    source_filter: str | None = None,
) -> list[dict[str, Any]]:
    where = {"source_file": source_filter} if source_filter else None
    store = get_vector_store()
    candidate_k = max(top_k or settings.top_k, settings.retrieval_candidates)
    chunks = store.query(query, top_k=candidate_k, where=where)
    chunks = rerank_chunks(query, chunks)
    limit = top_k or settings.top_k
    return chunks[:limit]


__all__ = [
    "retrieve",
    "filter_by_threshold",
    "compute_confidence",
    "INSUFFICIENT_MSG",
]
