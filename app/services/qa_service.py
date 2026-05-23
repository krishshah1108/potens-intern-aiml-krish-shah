"""Question answering orchestration with full explainability trace."""

import time
from typing import Any

from app.prompts.grounded_answer import (
    GROUNDED_SYSTEM,
    GROUNDED_USER_TEMPLATE,
    INSUFFICIENT_ANSWER,
)
from app.rag.retriever import retrieve
from app.rag.scoring import compute_confidence, filter_by_threshold
from app.services.language import (
    detect_query_language,
    get_answer_language_instruction,
    translate_to_english,
)
from app.services.llm import generate_text
from app.utils.citations import build_context_block, format_citations
from app.utils.config import settings
from app.utils.logging_config import logger


def _chunk_detail(chunk: dict, used_in_context: bool) -> dict[str, Any]:
    meta = chunk.get("metadata", {})
    sim = chunk.get("similarity", 0)
    return {
        "chunk_id": chunk.get("chunk_id") or meta.get("chunk_id"),
        "source_file": meta.get("source_file"),
        "page_number": meta.get("page_number"),
        "document_id": meta.get("document_id"),
        "language": meta.get("language"),
        "similarity": sim,
        "distance": chunk.get("distance"),
        "above_threshold": sim >= settings.similarity_threshold,
        "used_in_llm_context": used_in_context,
        "text": chunk.get("text", ""),
    }


def answer_question(question: str) -> dict[str, Any]:
    """
    Full Q&A pipeline with complete trace for UI and interaction logging.
    """
    start = time.perf_counter()
    query_lang = detect_query_language(question)
    retrieval_query = translate_to_english(question, query_lang)

    all_chunks = retrieve(retrieval_query)
    relevant_chunks = filter_by_threshold(all_chunks)
    relevant_ids = {
        c.get("chunk_id") or c.get("metadata", {}).get("chunk_id") for c in relevant_chunks
    }
    confidence = compute_confidence(relevant_chunks if relevant_chunks else all_chunks)

    retrieval_trace = {
        "query_language_detected": query_lang,
        "retrieval_query_english": retrieval_query,
        "answer_language_instruction": get_answer_language_instruction(query_lang),
        "top_k": settings.top_k,
        "similarity_threshold": settings.similarity_threshold,
        "chunks_retrieved": len(all_chunks),
        "chunks_above_threshold": len(relevant_chunks),
        "confidence_heuristic": confidence,
        "all_retrieved_chunks": [
            _chunk_detail(
                c,
                (c.get("chunk_id") or c.get("metadata", {}).get("chunk_id")) in relevant_ids,
            )
            for c in all_chunks
        ],
        "chunks_sent_to_llm": [_chunk_detail(c, True) for c in relevant_chunks],
    }

    prompts_trace = {
        "system_prompt": GROUNDED_SYSTEM,
        "user_prompt": None,
        "context_block": None,
    }

    citations: list[dict] = []
    answer = INSUFFICIENT_ANSWER
    llm_latency: float | None = None
    refused = True

    if not relevant_chunks:
        logger.info("No chunks above threshold; insufficient-information response")
    else:
        context = build_context_block(relevant_chunks)
        language_instruction = get_answer_language_instruction(query_lang)
        user_prompt = GROUNDED_USER_TEMPLATE.format(
            context=context,
            question=question,
            language_instruction=language_instruction,
        )
        prompts_trace["user_prompt"] = user_prompt
        prompts_trace["context_block"] = context

        answer, llm_latency = generate_text(GROUNDED_SYSTEM, user_prompt)
        citations = format_citations(relevant_chunks)
        refused = INSUFFICIENT_ANSWER.lower() in answer.lower() and len(answer) < 200
        if refused:
            citations = format_citations(relevant_chunks[:2])

    total_latency = time.perf_counter() - start
    logger.info(
        "Q&A complete | lang=%s | confidence=%.3f | refused=%s | latency=%.2fs",
        query_lang,
        confidence,
        refused,
        total_latency,
    )

    # Backward-compatible fields for API + Streamlit
    return {
        "question": question,
        "answer": answer,
        "llm_response": answer,
        "citations": citations,
        "confidence_score": confidence,
        "retrieved_chunks": [
            {
                "chunk_id": c["chunk_id"],
                "source_file": c["source_file"],
                "page_number": c["page_number"],
                "similarity": c["similarity"],
                "text_preview": (c["text"] or "")[:200],
            }
            for c in retrieval_trace["all_retrieved_chunks"]
        ],
        "query_language": query_lang,
        "latency_seconds": round(total_latency, 3),
        "llm_latency_seconds": round(llm_latency, 3) if llm_latency is not None else None,
        "refused_insufficient_evidence": refused,
        "retrieval": retrieval_trace,
        "prompts": prompts_trace,
    }
