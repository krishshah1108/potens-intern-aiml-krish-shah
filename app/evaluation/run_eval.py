"""
Evaluation script: retrieval hit rate, top-k relevance, grounded answer quality.

Run from project root:
  python -m app.evaluation.run_eval
"""

import json
import sys
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.ingestion.pipeline import ingest_directory
from app.rag.vector_store import get_vector_store
from app.services.qa_service import answer_question
from app.services.language import translate_to_english, detect_query_language
from app.rag.retriever import retrieve
from app.rag.scoring import filter_by_threshold

DATASET_PATH = Path(__file__).parent / "eval_dataset.json"


def load_dataset() -> list[dict]:
    with open(DATASET_PATH, encoding="utf-8") as f:
        return json.load(f)


def retrieval_hit(question: str, expected_source: str, top_k: int = 5) -> dict:
    lang = detect_query_language(question)
    query = translate_to_english(question, lang)
    chunks = retrieve(query, top_k=top_k)
    sources = [c.get("metadata", {}).get("source_file") for c in chunks]
    hit = expected_source in sources
    rank = sources.index(expected_source) + 1 if hit else None
    return {"hit": hit, "rank": rank, "top_source": sources[0] if sources else None}


def keyword_match(answer: str, keywords: list[str]) -> bool:
    lower = answer.lower()
    return any(kw.lower() in lower for kw in keywords)


def run_evaluation() -> None:
    store = get_vector_store()
    if store.count == 0:
        print("Vector store empty — ingesting documents first...")
        ingest_directory()

    dataset = load_dataset()
    results: list[dict] = []

    retrieval_hits = 0
    keyword_hits = 0
    grounded_refusals = 0

    print(f"\nEvaluating {len(dataset)} questions...\n")
    print("-" * 70)

    for item in dataset:
        q = item["question"]
        expected_src = item["expected_source"]
        keywords = item["expected_keywords"]

        ret = retrieval_hit(q, expected_src)
        if ret["hit"]:
            retrieval_hits += 1

        qa = answer_question(q)
        answer = qa.get("answer", "")
        has_keywords = keyword_match(answer, keywords)
        is_refusal = "do not contain enough information" in answer.lower()

        if has_keywords:
            keyword_hits += 1
        if is_refusal:
            grounded_refusals += 1

        results.append(
            {
                "id": item["id"],
                "retrieval_hit": ret["hit"],
                "retrieval_rank": ret["rank"],
                "confidence": qa.get("confidence_score"),
                "keyword_match": has_keywords,
                "refusal": is_refusal,
            }
        )

        status = "PASS" if ret["hit"] and (has_keywords or is_refusal) else "CHECK"
        print(f"[{status}] Q{item['id']}: retrieval={'hit' if ret['hit'] else 'miss'} "
              f"| keywords={'yes' if has_keywords else 'no'} | conf={qa.get('confidence_score')}")

    n = len(dataset)
    print("-" * 70)
    print(f"Retrieval hit rate (@top-5): {retrieval_hits}/{n} ({100*retrieval_hits/n:.1f}%)")
    print(f"Keyword match rate:         {keyword_hits}/{n} ({100*keyword_hits/n:.1f}%)")
    print(f"Insufficient-info responses: {grounded_refusals}/{n}")

    out_path = ROOT / "app" / "evaluation" / "eval_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"summary": results, "metrics": {
            "retrieval_hit_rate": retrieval_hits / n,
            "keyword_match_rate": keyword_hits / n,
        }}, f, indent=2)
    print(f"\nDetailed results saved to {out_path}")


if __name__ == "__main__":
    run_evaluation()
