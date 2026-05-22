"""Citation formatting for grounded answers."""

from typing import Any


def format_citation(chunk: dict[str, Any]) -> dict[str, str]:
    meta = chunk.get("metadata", {})
    source = meta.get("source_file", "unknown")
    page = str(meta.get("page_number", "?"))
    chunk_id = meta.get("chunk_id", chunk.get("chunk_id", "unknown"))
    snippet = chunk.get("text", "")[:300].strip()
    label = f"[Source: {source} | Page {page} | Chunk {chunk_id}]"

    return {
        "label": label,
        "source_file": source,
        "page_number": page,
        "chunk_id": chunk_id,
        "snippet": snippet,
        "similarity": str(chunk.get("similarity", 0)),
    }


def format_citations(chunks: list[dict]) -> list[dict[str, str]]:
    return [format_citation(c) for c in chunks]


def build_context_block(chunks: list[dict]) -> str:
    """Build numbered context block for the LLM prompt."""
    blocks: list[str] = []
    for i, chunk in enumerate(chunks, start=1):
        meta = chunk.get("metadata", {})
        header = (
            f"[{i}] Source: {meta.get('source_file')} | "
            f"Page: {meta.get('page_number')} | "
            f"Chunk: {meta.get('chunk_id')}"
        )
        blocks.append(f"{header}\n{chunk.get('text', '')}")
    return "\n\n---\n\n".join(blocks)
