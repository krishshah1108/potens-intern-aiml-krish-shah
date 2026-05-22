"""Tests for hybrid retrieval re-ranking."""

from app.rag.rerank import hybrid_similarity, rerank_chunks


def test_github_repo_query_boosts_rules_chunk():
    query = "what shall be the repo name while Shipping it on GitHub"
    rules_chunk = (
        "Document: Potens_Intern_Take_Home_2026.pdf (page 3). "
        "3. Ship it on GitHub. Repo name: potens-intern-[role]-[your-name] "
        "(example: potens-intern-backend-rohan-mehta)."
    )
    cover_chunk = (
        "Document: Potens_Intern_Take_Home_2026.pdf (page 1). "
        "INTERNSHIP HIRING 2026 The 24-Hour Take-Home."
    )

    rules_hybrid = hybrid_similarity(query, rules_chunk, embedding_similarity=0.19)
    cover_hybrid = hybrid_similarity(query, cover_chunk, embedding_similarity=0.26)

    assert rules_hybrid > cover_hybrid
    assert rules_hybrid >= 0.45


def test_rerank_orders_by_hybrid_score():
    query = "GitHub repo naming convention"
    chunks = [
        {"text": "unrelated policy leave days", "similarity": 0.5},
        {
            "text": "Ship it on GitHub. Repo name: potens-intern-[role]-[your-name]",
            "similarity": 0.32,
        },
    ]
    ranked = rerank_chunks(query, chunks)
    assert "potens-intern" in ranked[0]["text"]
    assert ranked[0]["similarity"] >= ranked[1]["similarity"]
