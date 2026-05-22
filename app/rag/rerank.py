"""Hybrid re-ranking: embedding similarity + lexical overlap for policy-style PDFs."""

import re
from typing import Any

# When query and chunk both mention these, add a small boost (capped in hybrid_similarity).
_TERM_BOOSTS: tuple[tuple[str, str], ...] = (
    ("github", "github"),
    ("repo", "repo"),
    ("repository", "repo"),
    ("potens-intern", "potens-intern"),
    ("ship it on github", "ship it on github"),
)

_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9-]{1,}")



def _token_set(text: str) -> set[str]:
    return set(_TOKEN_RE.findall(text.lower()))


def hybrid_similarity(query: str, chunk_text: str, embedding_similarity: float) -> float:
    """Combine dense retrieval score with light lexical overlap."""
    q_tokens = _token_set(query)
    c_tokens = _token_set(chunk_text)
    if q_tokens:
        lexical = len(q_tokens & c_tokens) / len(q_tokens)
    else:
        lexical = 0.0

    boost = 0.0
    q_lower = query.lower()
    c_lower = chunk_text.lower()
    for q_term, c_term in _TERM_BOOSTS:
        if q_term in q_lower and c_term in c_lower:
            boost += 0.12

    score = 0.6 * embedding_similarity + 0.4 * lexical + boost
    return round(min(score, 1.0), 4)


def rerank_chunks(query: str, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort chunks by hybrid score; preserve original embedding score for debug."""
    for chunk in chunks:
        emb = chunk.get("embedding_similarity", chunk["similarity"])
        chunk["embedding_similarity"] = emb
        chunk["similarity"] = hybrid_similarity(query, chunk.get("text", ""), emb)
    return sorted(chunks, key=lambda c: c["similarity"], reverse=True)
