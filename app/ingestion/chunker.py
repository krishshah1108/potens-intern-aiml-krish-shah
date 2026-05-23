"""Document chunking with required metadata preservation."""

import hashlib
import re
from typing import Any

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.utils.config import settings
from app.utils.logging_config import logger

SUPPORTED_LANGUAGES = {"en", "hi", "gu", "mr"}


def detect_language(text: str) -> str:
    """Heuristic language detection for chunk metadata."""
    sample = text[:500]
    if re.search(r"[\u0A80-\u0AFF]", sample):
        return "gu"
    if re.search(r"[\u0900-\u097F]", sample) and re.search(
        r"(मराठी|महाराष्ट्र)", sample
    ):
        return "mr"
    if re.search(r"[\u0900-\u097F]", sample):
        return "hi"
    return "en"


def make_document_id(source_file: str) -> str:
    return hashlib.md5(source_file.encode()).hexdigest()[:12]


def chunk_pages(
    pages: list[dict],
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[dict[str, Any]]:
    """
    Split page texts into overlapping chunks with full metadata.

    Chunk size 800 / overlap 150 balances semantic continuity and citation precision.
    """
    size = chunk_size or settings.chunk_size
    overlap = chunk_overlap or settings.chunk_overlap

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    document_id = make_document_id(pages[0]["source_file"]) if pages else "unknown"
    chunks: list[dict[str, Any]] = []
    chunk_counter = 0

    for page in pages:
        page_text = page["text"]
        if not page_text.strip():
            continue

        splits = splitter.split_text(page_text)
        language = detect_language(page_text)

        for split in splits:
            chunk_counter += 1
            chunks.append(
                {
                    "text": split,
                    "metadata": {
                        "source_file": page["source_file"],
                        "page_number": page["page_number"],
                        "chunk_id": f"{document_id}_{chunk_counter}",
                        "document_id": document_id,
                        "language": language,
                    },
                }
            )

    logger.info(
        "Created %d chunks for %s (size=%d, overlap=%d)",
        len(chunks),
        pages[0]["source_file"] if pages else "unknown",
        size,
        overlap,
    )
    return chunks
