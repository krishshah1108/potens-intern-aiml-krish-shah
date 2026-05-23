"""Fast unit tests (no ChromaDB / LLM). Run: pytest tests/ -q"""

from app.ingestion.chunker import chunk_pages, make_document_id
from app.prompts.grounded_answer import INSUFFICIENT_ANSWER
from app.services.language import detect_query_language, translate_to_english
from app.utils.citations import build_context_block, format_citation


def test_chunk_metadata():
    pages = [
        {
            "page_number": 2,
            "text": "National curriculum monitoring clause. " * 40,
            "source_file": "national_curriculum_framework_2023.pdf",
        }
    ]
    chunks = chunk_pages(pages, chunk_size=200, chunk_overlap=30)
    assert chunks
    meta = chunks[0]["metadata"]
    assert meta["source_file"] == "national_curriculum_framework_2023.pdf"
    assert meta["page_number"] == 2
    assert meta["chunk_id"]
    assert meta["document_id"] == make_document_id(pages[0]["source_file"])
    assert meta["language"] == "en"


def test_citation_format():
    chunk = {
        "text": "Source: policy.pdf | page 1. Retention is seven years.",
        "metadata": {
            "source_file": "policy.pdf",
            "page_number": 1,
            "chunk_id": "abc_1",
        },
        "similarity": 0.72,
    }
    cite = format_citation(chunk)
    assert cite["source_file"] == "policy.pdf"
    assert cite["page_number"] == "1"
    assert cite["chunk_id"] == "abc_1"
    assert "Retention" in cite["snippet"]


def test_context_block_numbering():
    chunks = [
        {
            "text": "first",
            "metadata": {"source_file": "a.pdf", "page_number": 1, "chunk_id": "a_1"},
        },
        {
            "text": "second",
            "metadata": {"source_file": "b.pdf", "page_number": 2, "chunk_id": "b_2"},
        },
    ]
    block = build_context_block(chunks)
    assert "[1]" in block and "[2]" in block
    assert "a.pdf" in block and "b.pdf" in block


def test_insufficient_answer_constant():
    assert "do not contain enough information" in INSUFFICIENT_ANSWER.lower()


def test_multilingual_boundary_english_passthrough():
    assert translate_to_english("What is NCF 2023?", "en") == "What is NCF 2023?"


def test_language_detection_english():
    assert detect_query_language("What is the fine for data breach?") == "en"
