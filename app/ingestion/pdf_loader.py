"""PDF text extraction with page-level granularity."""

import re
from pathlib import Path

from pypdf import PdfReader

from app.utils.logging_config import logger

# Many PDFs (including Word exports) place each word on its own line; pypdf
# preserves those breaks and destroys embedding quality unless normalized.
_MULTI_SPACE = re.compile(r"[ \t\u00a0]+")
_MULTI_NEWLINE = re.compile(r"\n{2,}")


def normalize_pdf_text(text: str) -> str:
    """Collapse layout artifacts so chunks embed as continuous prose."""
    if not text:
        return ""
    text = text.replace("\ufffd", " ")
    text = _MULTI_NEWLINE.sub("\n", text)
    text = text.replace("\n", " ")
    text = _MULTI_SPACE.sub(" ", text)
    return text.strip()


def load_pdf_pages(file_path: Path) -> list[dict]:
    """
    Load a PDF and return page-level text segments.

    Returns list of dicts: {page_number, text, source_file}
    """
    reader = PdfReader(str(file_path))
    pages: list[dict] = []
    source_file = file_path.name

    for idx, page in enumerate(reader.pages, start=1):
        text = normalize_pdf_text(page.extract_text() or "")
        if not text:
            logger.warning("Empty page %s in %s", idx, source_file)
            continue
        pages.append(
            {
                "page_number": idx,
                "text": text,
                "source_file": source_file,
            }
        )

    logger.info("Loaded %d pages from %s", len(pages), source_file)
    return pages
