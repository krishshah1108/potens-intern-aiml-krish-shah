"""Pydantic request/response models."""

from typing import Any

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
    question: str
    answer: str
    llm_response: str
    citations: list[CitationResponse]
    confidence_score: float
    retrieved_chunks: list[RetrievedChunkResponse]
    query_language: str
    latency_seconds: float | None = None
    llm_latency_seconds: float | None = None
    refused_insufficient_evidence: bool = False
    retrieval: dict[str, Any]
    prompts: dict[str, Any]


class ContradictRequest(BaseModel):
    document_1: str = Field(..., description="Source filename for first document")
    document_2: str = Field(..., description="Source filename for second document")
    topic: str = Field(..., min_length=1, description="Topic to compare")


class ContradictResponse(BaseModel):
    conflict: bool
    reasoning: str
    evidence: list[dict] = []


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
