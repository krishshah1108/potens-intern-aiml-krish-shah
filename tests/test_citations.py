"""Tests for citation formatting."""

from app.utils.citations import format_citation, build_context_block


def test_citation_format():
    chunk = {
        "text": "Personal data must be retained for seven years.",
        "metadata": {
            "source_file": "policy.pdf",
            "page_number": 4,
            "chunk_id": "abc_18",
        },
        "similarity": 0.82,
    }
    cite = format_citation(chunk)
    assert "policy.pdf" in cite["label"]
    assert "Page 4" in cite["label"]
    assert "abc_18" in cite["label"]
    assert "Personal data" in cite["snippet"]


def test_context_block_numbering():
    chunks = [
        {
            "text": "First chunk text.",
            "metadata": {"source_file": "a.pdf", "page_number": 1, "chunk_id": "c1"},
        },
        {
            "text": "Second chunk text.",
            "metadata": {"source_file": "b.pdf", "page_number": 2, "chunk_id": "c2"},
        },
    ]
    ctx = build_context_block(chunks)
    assert "[1]" in ctx
    assert "[2]" in ctx
    assert "First chunk" in ctx
