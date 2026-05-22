"""End-to-end document ingestion pipeline."""

from pathlib import Path

from app.ingestion.chunker import chunk_pages
from app.ingestion.pdf_loader import load_pdf_pages
from app.rag.vector_store import get_vector_store
from app.utils.config import settings
from app.utils.logging_config import logger


def ingest_pdf(file_path: Path, replace: bool = True) -> dict:
    """
    Ingest a single PDF: extract, chunk, embed, store.

    Returns summary with chunk count and source file.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"PDF not found: {file_path}")

    if file_path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected PDF file: {file_path}")

    store = get_vector_store()
    source_file = file_path.name

    if replace:
        store.delete_by_source(source_file)

    pages = load_pdf_pages(file_path)
    if not pages:
        raise ValueError(f"No extractable text in {source_file}")

    chunks = chunk_pages(pages)
    count = store.add_chunks(chunks)

    return {
        "source_file": source_file,
        "pages": len(pages),
        "chunks_indexed": count,
        "total_in_store": store.count,
    }


def ingest_directory(directory: Path | None = None) -> list[dict]:
    """Ingest all PDFs in the documents directory."""
    docs_dir = directory or settings.docs_path
    docs_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []
    pdfs = sorted(docs_dir.glob("*.pdf"))

    if not pdfs:
        logger.warning("No PDF files found in %s", docs_dir)
        return results

    for pdf_path in pdfs:
        try:
            result = ingest_pdf(pdf_path)
            results.append(result)
        except Exception as exc:
            logger.error("Failed to ingest %s: %s", pdf_path.name, exc)
            results.append({"source_file": pdf_path.name, "error": str(exc)})

    return results
