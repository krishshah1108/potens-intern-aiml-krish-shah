"""Retrieval scoring utilities (no ChromaDB dependency)."""

from typing import Any

from app.utils.config import settings
from app.utils.logging_config import logger

INSUFFICIENT_MSG = (
    "The provided documents do not contain enough information to answer "
    "this question confidently."
)


def filter_by_threshold(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    threshold = settings.similarity_threshold
    filtered = [c for c in chunks if c["similarity"] >= threshold]
    logger.info(
        "Threshold filter: %d/%d chunks above %.2f",
        len(filtered),
        len(chunks),
        threshold,
    )
    return filtered


def compute_confidence(chunks: list[dict[str, Any]]) -> float:
    if not chunks:
        return 0.0

    max_sim = max(c["similarity"] for c in chunks)
    above = sum(1 for c in chunks if c["similarity"] >= settings.similarity_threshold)
    support_ratio = above / len(chunks)
    confidence = 0.7 * max_sim + 0.3 * support_ratio
    return round(min(confidence, 1.0), 3)
