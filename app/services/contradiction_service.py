"""Cross-document contradiction analysis."""

import time

from app.prompts.contradiction import CONTRADICTION_SYSTEM, CONTRADICTION_USER_TEMPLATE
from app.rag.retriever import retrieve
from app.rag.scoring import filter_by_threshold
from app.services.llm import generate_json
from app.utils.logging_config import logger


def analyze_contradiction(
    document_1: str,
    document_2: str,
    topic: str,
) -> dict:
    """
    Retrieve topic-specific chunks from two documents and compare via LLM.
    """
    start = time.perf_counter()

    chunks_a = filter_by_threshold(
        retrieve(topic, top_k=4, source_filter=document_1)
    )
    chunks_b = filter_by_threshold(
        retrieve(topic, top_k=4, source_filter=document_2)
    )

    if not chunks_a or not chunks_b:
        return {
            "conflict": False,
            "reasoning": (
                "Insufficient topic-specific evidence in one or both documents "
                f"to assess contradictions on '{topic}'."
            ),
            "evidence": [],
            "document_1_chunks": len(chunks_a),
            "document_2_chunks": len(chunks_b),
            "latency_seconds": round(time.perf_counter() - start, 3),
        }

    excerpts_a = _format_excerpts(chunks_a, "A")
    excerpts_b = _format_excerpts(chunks_b, "B")

    user_prompt = CONTRADICTION_USER_TEMPLATE.format(
        topic=topic,
        doc_a=document_1,
        doc_b=document_2,
        excerpts_a=excerpts_a,
        excerpts_b=excerpts_b,
    )

    result = generate_json(CONTRADICTION_SYSTEM, user_prompt)
    result["latency_seconds"] = round(time.perf_counter() - start, 3)
    result["document_1_chunks"] = len(chunks_a)
    result["document_2_chunks"] = len(chunks_b)

    logger.info(
        "Contradiction analysis | conflict=%s | topic=%s",
        result.get("conflict"),
        topic,
    )
    return result


def _format_excerpts(chunks: list[dict], label: str) -> str:
    parts: list[str] = []
    for chunk in chunks:
        meta = chunk.get("metadata", {})
        parts.append(
            f"- [{label}] Chunk {meta.get('chunk_id')} (Page {meta.get('page_number')}):\n"
            f"  {chunk.get('text', '')[:500]}"
        )
    return "\n".join(parts)
