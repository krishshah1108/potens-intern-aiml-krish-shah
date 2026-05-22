"""Tests for document chunking and metadata."""

from app.ingestion.chunker import chunk_pages, detect_language, make_document_id


def test_chunk_metadata_fields():
    pages = [
        {
            "page_number": 1,
            "text": "Potens IT Services policy document. " * 50,
            "source_file": "test_policy.pdf",
        }
    ]
    chunks = chunk_pages(pages, chunk_size=200, chunk_overlap=30)
    assert len(chunks) >= 1
    meta = chunks[0]["metadata"]
    assert meta["source_file"] == "test_policy.pdf"
    assert meta["page_number"] == 1
    assert "chunk_id" in meta
    assert "document_id" in meta
    assert meta["language"] in {"en", "hi"}


def test_document_id_stable():
    assert make_document_id("policy.pdf") == make_document_id("policy.pdf")


def test_detect_language_hindi():
    text = "सभी कर्मचारियों को प्रत्येक वर्ष अपडेट करना अनिवार्य है"
    assert detect_language(text) == "hi"
