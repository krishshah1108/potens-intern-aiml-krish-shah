"""PDF text extraction with page-level granularity."""

from pathlib import Path

from pypdf import PdfReader

from app.utils.logging_config import logger


def load_pdf_pages(file_path: Path) -> list[dict]:
    """
    Load a PDF and return page-level text segments.

    Returns list of dicts: {page_number, text, source_file}
    """
    reader = PdfReader(str(file_path))
    pages: list[dict] = []
    source_file = file_path.name

    for idx, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
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
