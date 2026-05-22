"""Tests for retrieval threshold behavior."""

from app.rag.scoring import filter_by_threshold, compute_confidence, INSUFFICIENT_MSG


def test_filter_by_threshold():
    chunks = [
        {"similarity": 0.6},
        {"similarity": 0.3},
        {"similarity": 0.5},
    ]
    filtered = filter_by_threshold(chunks)
    assert len(filtered) == 2
    assert all(c["similarity"] >= 0.45 for c in filtered)


def test_compute_confidence_empty():
    assert compute_confidence([]) == 0.0


def test_insufficient_message_constant():
    assert "do not contain enough information" in INSUFFICIENT_MSG.lower()
