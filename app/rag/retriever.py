"""Semantic retrieval with similarity thresholding."""

from typing import Any

from app.rag.scoring import compute_confidence, filter_by_threshold
from app.rag.vector_store import get_vector_store
from app.utils.config import settings
from app.utils.logging_config import logger

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
    chunks = store.query(query, top_k=top_k or settings.top_k, where=where)
    return chunks


__all__ = [
    "retrieve",
    "filter_by_threshold",
    "compute_confidence",
    "INSUFFICIENT_MSG",
]
