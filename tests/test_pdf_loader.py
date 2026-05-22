"""Tests for PDF text normalization."""

from app.ingestion.pdf_loader import normalize_pdf_text


def test_normalize_collapses_word_per_line_layout():
    raw = "been\n \nlow\n \nfor\n \ntoo\n \nlong"
    assert normalize_pdf_text(raw) == "been low for too long"


def test_normalize_preserves_sentence_spacing():
    raw = "24  hours.   Pick   exactly   one   question."
    assert "24 hours" in normalize_pdf_text(raw)
