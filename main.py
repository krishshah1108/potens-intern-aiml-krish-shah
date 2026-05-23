"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.ingestion.pipeline import ingest_directory
from app.rag.vector_store import get_vector_store
from app.utils.logging_config import logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    store = get_vector_store()
    if store.count == 0:
        logger.info("Vector store empty — ingest PDFs via POST /ingest or Streamlit")
    else:
        logger.info("Vector store ready with %d chunks", store.count)
    yield


app = FastAPI(
    title="Potens Document Q&A API",
    description="Grounded RAG with citations and contradiction analysis",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    from app.utils.config import settings

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
    )
