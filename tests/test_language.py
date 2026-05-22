"""Tests for multilingual flow."""

from app.services.language import (
    detect_query_language,
    translate_to_english,
    get_answer_language_instruction,
    SUPPORTED,
)


def test_english_detection():
    assert detect_query_language("What is the leave policy?") == "en"


def test_translate_english_passthrough():
    q = "How many leave days?"
    assert translate_to_english(q, "en") == q


def test_answer_language_instruction():
    instr = get_answer_language_instruction("hi")
    assert "Hindi" in instr
    assert "hi" in instr


def test_supported_languages_set():
    assert SUPPORTED == {"en", "hi"}
