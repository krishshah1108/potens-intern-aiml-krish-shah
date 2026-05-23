"""
Evaluation: 20 Q&A pairs with ground truth.

Usage:
  python -m app.evaluation.run_eval                  # retrieval only (no LLM quota)
  python -m app.evaluation.run_eval --full           # + grounded answers (slow; free tier ~5/min)
  python -m app.evaluation.run_eval --full --llm-delay 13

Metrics:
  - Retrieval hit @1, @3, @5
  - MRR, threshold pass
  - (full mode) keyword match, refusal accuracy
"""

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.ingestion.pipeline import ingest_directory
from app.rag.retriever import retrieve
from app.rag.scoring import filter_by_threshold
from app.rag.vector_store import get_vector_store
from app.services.language import detect_query_language, translate_to_english
from app.services.qa_service import answer_question
from app.utils.config import settings

DATASET_PATH = Path(__file__).parent / "eval_dataset.json"
INSUFFICIENT = "do not contain enough information"


def load_dataset() -> list[dict]:
    with open(DATASET_PATH, encoding="utf-8") as f:
        return json.load(f)


def retrieval_metrics(question: str, expected_source: str | None, top_k: int = 5) -> dict:
    lang = detect_query_language(question)
    query = translate_to_english(question, lang)
    chunks = retrieve(query, top_k=top_k)
    sources = [c.get("metadata", {}).get("source_file") for c in chunks]
    similarities = [c.get("similarity", 0) for c in chunks]

    if not expected_source:
        return {
            "sources": sources,
            "similarities": similarities,
            "hit_at_1": None,
            "hit_at_3": None,
            "hit_at_5": None,
            "mrr": None,
            "threshold_pass": None,
        }

    hit_at_1 = sources[0] == expected_source if sources else False
    hit_at_3 = expected_source in sources[:3]
    hit_at_5 = expected_source in sources[:5]
    mrr = 0.0
    if expected_source in sources:
        mrr = 1.0 / (sources.index(expected_source) + 1)

    filtered = filter_by_threshold(chunks)
    filtered_sources = [c.get("metadata", {}).get("source_file") for c in filtered]
    threshold_pass = expected_source in filtered_sources

    return {
        "sources": sources,
        "similarities": similarities,
        "hit_at_1": hit_at_1,
        "hit_at_3": hit_at_3,
        "hit_at_5": hit_at_5,
        "mrr": round(mrr, 4),
        "threshold_pass": threshold_pass,
    }


def keyword_match(answer: str, keywords: list[str]) -> bool:
    if not keywords:
        return False
    lower = answer.lower()
    return any(kw.lower() in lower for kw in keywords)


def run_evaluation(full: bool = False, llm_delay: float = 13.0) -> None:
    store = get_vector_store()
    if store.count == 0:
        print("Vector store empty — ingesting documents...")
        ingest_directory()

    dataset = load_dataset()
    results: list[dict] = []

    hits_1 = hits_3 = hits_5 = 0
    mrr_sum = 0.0
    mrr_count = 0
    threshold_passes = 0
    eval_with_source = 0
    keyword_hits = 0
    keyword_total = 0
    refusal_expected = 0
    refusal_correct = 0

    mode = "retrieval + LLM" if full else "retrieval only"
    print(f"\nEvaluating {len(dataset)} questions | mode={mode} | "
          f"top_k={settings.top_k} | threshold={settings.similarity_threshold}")
    if full:
        print(f"LLM delay between questions: {llm_delay}s (free tier ~5 requests/min)\n")
    else:
        print("Tip: use --full for keyword/refusal metrics (requires Gemini API quota)\n")
    print("-" * 88)

    for i, item in enumerate(dataset):
        q = item["question"]
        expected_src = item.get("expected_source")
        keywords = item.get("expected_keywords", [])
        expect_refusal = item.get("expect_refusal", False)

        ret = retrieval_metrics(q, expected_src)

        if expected_src:
            eval_with_source += 1
            if ret["hit_at_1"]:
                hits_1 += 1
            if ret["hit_at_3"]:
                hits_3 += 1
            if ret["hit_at_5"]:
                hits_5 += 1
            mrr_sum += ret["mrr"] or 0
            mrr_count += 1
            if ret["threshold_pass"]:
                threshold_passes += 1

        answer = ""
        is_refusal = False
        has_keywords = False
        confidence = None

        if full:
            if i > 0 and llm_delay > 0:
                time.sleep(llm_delay)
            try:
                qa = answer_question(q)
                answer = qa.get("answer", "")
                confidence = qa.get("confidence_score")
                is_refusal = INSUFFICIENT in answer.lower()
                has_keywords = keyword_match(answer, keywords)
            except Exception as exc:
                logger_msg = str(exc)
                print(f"[ERROR] Q{item['id']:02d} LLM failed: {logger_msg[:120]}")
                answer = f"[LLM error: {logger_msg[:80]}]"

            if expect_refusal:
                refusal_expected += 1
                if is_refusal:
                    refusal_correct += 1
            elif not expect_refusal:
                keyword_total += 1
                if has_keywords:
                    keyword_hits += 1

        row = {
            "id": item["id"],
            "query_language": item.get("query_language"),
            "expected_source": expected_src,
            "expect_refusal": expect_refusal,
            "retrieval_hit_at_1": ret["hit_at_1"],
            "retrieval_hit_at_3": ret["hit_at_3"],
            "retrieval_hit_at_5": ret["hit_at_5"],
            "mrr": ret["mrr"],
            "threshold_pass": ret["threshold_pass"],
            "top_similarity": ret["similarities"][0] if ret["similarities"] else None,
            "retrieved_top_sources": ret["sources"][:3],
            "confidence": confidence,
            "keyword_match": has_keywords if full else None,
            "refusal": is_refusal if full else None,
        }
        results.append(row)

        if full and expect_refusal:
            status = "PASS" if is_refusal else "FAIL"
            print(f"[{status}] Q{item['id']:02d} | refusal expected | refused={is_refusal}")
        elif full:
            status = "PASS" if ret["hit_at_5"] and (has_keywords or ret["threshold_pass"]) else "CHECK"
            print(
                f"[{status}] Q{item['id']:02d} | @{5}={'Y' if ret['hit_at_5'] else 'N'} "
                f"| thr={'Y' if ret['threshold_pass'] else 'N'} "
                f"| kw={'Y' if has_keywords else 'N'} "
                f"| conf={confidence}"
            )
        else:
            top = ret["sources"][0] if ret["sources"] else "-"
            status = "PASS" if ret["hit_at_5"] else "MISS"
            print(
                f"[{status}] Q{item['id']:02d} | hit@5={'Y' if ret['hit_at_5'] else 'N'} "
                f"| thr={'Y' if ret['threshold_pass'] else 'N'} "
                f"| top={top} | sim={ret['similarities'][0] if ret['similarities'] else 0:.3f}"
            )

    n = len(dataset)
    print("-" * 88)
    if eval_with_source:
        print(f"Retrieval hit@1:  {hits_1}/{eval_with_source} ({100*hits_1/eval_with_source:.1f}%)")
        print(f"Retrieval hit@3:  {hits_3}/{eval_with_source} ({100*hits_3/eval_with_source:.1f}%)")
        print(f"Retrieval hit@5:  {hits_5}/{eval_with_source} ({100*hits_5/eval_with_source:.1f}%)")
        print(f"MRR:              {mrr_sum/mrr_count:.3f}")
        print(f"Threshold pass:   {threshold_passes}/{eval_with_source} "
              f"({100*threshold_passes/eval_with_source:.1f}%)")
    if full and keyword_total:
        print(f"Keyword match:    {keyword_hits}/{keyword_total} ({100*keyword_hits/keyword_total:.1f}%)")
    if full and refusal_expected:
        print(f"Refusal accuracy: {refusal_correct}/{refusal_expected} "
              f"({100*refusal_correct/refusal_expected:.1f}%)")

    metrics = {
        "mode": mode,
        "total_questions": n,
        "retrieval_hit_at_1": hits_1 / eval_with_source if eval_with_source else 0,
        "retrieval_hit_at_3": hits_3 / eval_with_source if eval_with_source else 0,
        "retrieval_hit_at_5": hits_5 / eval_with_source if eval_with_source else 0,
        "mrr": mrr_sum / mrr_count if mrr_count else 0,
        "threshold_pass_rate": threshold_passes / eval_with_source if eval_with_source else 0,
        "keyword_match_rate": keyword_hits / keyword_total if keyword_total else None,
        "refusal_accuracy": refusal_correct / refusal_expected if refusal_expected else None,
        "top_k": settings.top_k,
        "similarity_threshold": settings.similarity_threshold,
    }

    out_path = ROOT / "app" / "evaluation" / "eval_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"metrics": metrics, "results": results}, f, indent=2)
    print(f"\nResults saved to {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run RAG evaluation dataset")
    parser.add_argument(
        "--full",
        action="store_true",
        help="Call Gemini for each question (slow; subject to API rate limits)",
    )
    parser.add_argument(
        "--llm-delay",
        type=float,
        default=13.0,
        help="Seconds between LLM calls in --full mode (default: 13 for free tier)",
    )
    args = parser.parse_args()
    run_evaluation(full=args.full, llm_delay=args.llm_delay)


if __name__ == "__main__":
    main()
