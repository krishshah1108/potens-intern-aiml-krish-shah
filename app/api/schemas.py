"""Pydantic request/response models."""

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User question in any supported language")


class CitationResponse(BaseModel):
    label: str
    source_file: str
    page_number: str
    chunk_id: str
    snippet: str
    similarity: str | None = None


class RetrievedChunkResponse(BaseModel):
    chunk_id: str | None
    source_file: str | None
    page_number: int | str | None
    similarity: float | None
    text_preview: str | None


class AskResponse(BaseModel):
    answer: str
    citations: list[CitationResponse]
    confidence_score: float
    retrieved_chunks: list[RetrievedChunkResponse]


class ContradictRequest(BaseModel):
    document_1: str = Field(..., description="Source filename for first document")
    document_2: str = Field(..., description="Source filename for second document")
    topic: str = Field(..., min_length=1, description="Topic to compare")


class EvidenceItem(BaseModel):
    document: str | None = None
    chunk_id: str | None = None
    quote: str | None = None


class ContradictResponse(BaseModel):
    conflict: bool
    reasoning: str
    evidence: list[dict] | list[EvidenceItem] = []


class IngestResponse(BaseModel):
    source_file: str
    pages: int | None = None
    chunks_indexed: int | None = None
    total_in_store: int | None = None
    error: str | None = None


class HealthResponse(BaseModel):
    status: str
    vector_store_chunks: int
    documents_dir: str
