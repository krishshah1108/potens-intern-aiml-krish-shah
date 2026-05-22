"""Multilingual query handling via translation boundary."""

from deep_translator import GoogleTranslator
from langdetect import LangDetectException, detect

from app.utils.logging_config import logger

SUPPORTED = {"en", "hi", "gu", "mr"}
LANG_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "gu": "Gujarati",
    "mr": "Marathi",
}


def detect_query_language(text: str) -> str:
    try:
        code = detect(text)
        if code in SUPPORTED:
            return code
        # langdetect may return 'hi' for Devanagari used in Marathi; keep as detected
        if code.startswith("gu"):
            return "gu"
    except LangDetectException:
        logger.warning("Language detection failed; defaulting to English")
    return "en"


def translate_to_english(text: str, source_lang: str) -> str:
    if source_lang == "en":
        return text
    try:
        translated = GoogleTranslator(source=source_lang, target="en").translate(text)
        logger.info("Translated query from %s to English for retrieval", source_lang)
        return translated or text
    except Exception as exc:
        logger.warning("Translation failed (%s); using original query", exc)
        return text


def get_answer_language_instruction(lang_code: str) -> str:
    name = LANG_NAMES.get(lang_code, "English")
    return f"Respond entirely in {name} ({lang_code})."
