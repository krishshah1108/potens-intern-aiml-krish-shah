"""FastAPI route definitions."""

from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.api.schemas import (
    AskRequest,
    AskResponse,
    ContradictRequest,
    ContradictResponse,
    HealthResponse,
    IngestResponse,
)
from app.ingestion.pipeline import ingest_directory, ingest_pdf
from app.rag.vector_store import get_vector_store
from app.services.contradiction_service import analyze_contradiction
from app.services.qa_service import answer_question
from app.utils.config import settings
from app.utils.logging_config import logger

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    store = get_vector_store()
    return HealthResponse(
        status="ok",
        vector_store_chunks=store.count,
        documents_dir=str(settings.docs_path),
    )


@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    logger.info("POST /ask | question=%s", request.question[:80])
    try:
        result = answer_question(request.question)
        return AskResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Ask endpoint failed")
        raise HTTPException(status_code=500, detail="Internal error processing question") from exc


@router.post("/contradict", response_model=ContradictResponse)
def contradict(request: ContradictRequest) -> ContradictResponse:
    logger.info(
        "POST /contradict | %s vs %s | topic=%s",
        request.document_1,
        request.document_2,
        request.topic,
    )
    try:
        result = analyze_contradiction(
            request.document_1,
            request.document_2,
            request.topic,
        )
        return ContradictResponse(
            conflict=bool(result.get("conflict", False)),
            reasoning=result.get("reasoning", ""),
            evidence=result.get("evidence", []),
        )
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Contradict endpoint failed")
        raise HTTPException(status_code=500, detail="Internal error analyzing contradiction") from exc


@router.post("/ingest", response_model=list[IngestResponse])
def ingest_all() -> list[IngestResponse]:
    """Re-ingest all PDFs from the documents directory."""
    results = ingest_directory()
    return [IngestResponse(**r) for r in results]


@router.post("/ingest/upload", response_model=IngestResponse)
async def ingest_upload(file: UploadFile = File(...)) -> IngestResponse:
    """Upload and ingest a single PDF."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    settings.docs_path.mkdir(parents=True, exist_ok=True)
    dest = settings.docs_path / file.filename
    content = await file.read()
    dest.write_bytes(content)

    try:
        result = ingest_pdf(dest)
        return IngestResponse(**result)
    except Exception as exc:
        logger.error("Upload ingest failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
