"""Tests for insufficient-information handling."""

from app.rag.scoring import filter_by_threshold
from app.prompts.grounded_answer import INSUFFICIENT_ANSWER


def test_all_chunks_below_threshold():
    chunks = [{"similarity": 0.1}, {"similarity": 0.2}]
    filtered = filter_by_threshold(chunks)
    assert filtered == []


def test_insufficient_answer_exact_wording():
    assert "confidently" in INSUFFICIENT_ANSWER
