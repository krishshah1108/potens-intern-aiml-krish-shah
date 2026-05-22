"""Question answering orchestration."""

import time

from app.utils.config import settings
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
from app.utils.logging_config import logger


def answer_question(question: str) -> dict:
    """
    Full Q&A pipeline: language detect → translate → retrieve → ground → cite.
    """
    start = time.perf_counter()
    query_lang = detect_query_language(question)
    retrieval_query = translate_to_english(question, query_lang)

    all_chunks = retrieve(retrieval_query)
    relevant_chunks = filter_by_threshold(all_chunks)

    # Borderline matches (e.g. internship PDF rule phrasing) still get grounded context.
    if not relevant_chunks and all_chunks:
        best_sim = all_chunks[0]["similarity"]
        if best_sim >= 0.35:
            relevant_chunks = all_chunks[:3]
            logger.info(
                "Using top %d chunks below threshold (best similarity=%.3f)",
                len(relevant_chunks),
                best_sim,
            )

    confidence = compute_confidence(relevant_chunks if relevant_chunks else all_chunks)

    citations = format_citations(relevant_chunks if relevant_chunks else [])

    if not relevant_chunks:
        logger.info("No chunks above threshold; returning insufficient-information response")
        return {
            "answer": INSUFFICIENT_ANSWER,
            "citations": [],
            "confidence_score": confidence,
            "retrieved_chunks": _serialize_chunks(all_chunks),
            "query_language": query_lang,
            "latency_seconds": round(time.perf_counter() - start, 3),
        }

    context = build_context_block(relevant_chunks)
    language_instruction = get_answer_language_instruction(query_lang)

    user_prompt = GROUNDED_USER_TEMPLATE.format(
        context=context,
        question=question,
        language_instruction=language_instruction,
    )

    answer, llm_latency = generate_text(GROUNDED_SYSTEM, user_prompt)

    if INSUFFICIENT_ANSWER.lower() in answer.lower() and len(answer) < 200:
        citations = format_citations(relevant_chunks[:2])  # still show nearest evidence

    total_latency = time.perf_counter() - start
    logger.info(
        "Q&A complete | lang=%s | confidence=%.3f | chunks=%d | latency=%.2fs",
        query_lang,
        confidence,
        len(relevant_chunks),
        total_latency,
    )

    return {
        "answer": answer,
        "citations": citations,
        "confidence_score": confidence,
        "retrieved_chunks": _serialize_chunks(all_chunks),
        "query_language": query_lang,
        "latency_seconds": round(total_latency, 3),
        "llm_latency_seconds": round(llm_latency, 3),
    }


def _serialize_chunks(chunks: list[dict]) -> list[dict]:
    return [
        {
            "chunk_id": c.get("chunk_id") or c.get("metadata", {}).get("chunk_id"),
            "source_file": c.get("metadata", {}).get("source_file"),
            "page_number": c.get("metadata", {}).get("page_number"),
            "similarity": c.get("similarity"),
            "embedding_similarity": c.get("embedding_similarity"),
            "text_preview": (c.get("text") or "")[:200],
        }
        for c in chunks
    ]
