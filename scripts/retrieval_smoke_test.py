"""
Smoke-test retrieval against indexed documents.

Run (API must be up, or uses in-process retrieval if import works):
  python scripts/retrieval_smoke_test.py
  python scripts/retrieval_smoke_test.py --api http://localhost:8000
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Take-home + policy questions a reviewer should pass
CASES: list[dict] = [
    {
        "id": "takehome_hours",
        "question": "How many hours do I have to complete the take-home assignment?",
        "must_contain_any": ["24", "twenty-four", "hour"],
        "expect_source": "Potens_Intern_Take_Home_2026.pdf",
    },
    {
        "id": "takehome_github_repo",
        "question": "what shall be the repo name while Shipping it on GitHub",
        "must_contain_any": ["potens-intern", "potens intern"],
        "expect_source": "Potens_Intern_Take_Home_2026.pdf",
    },
    {
        "id": "takehome_pick_one",
        "question": "How many questions should I attempt from my role?",
        "must_contain_any": ["one", "1", "exactly one"],
        "expect_source": "Potens_Intern_Take_Home_2026.pdf",
    },
    {
        "id": "leave_days",
        "question": "How many days of paid annual leave do full-time employees receive?",
        "must_contain_any": ["20", "twenty"],
        "expect_source": "leave_policy.pdf",
    },
    {
        "id": "remote_days",
        "question": "How many remote work days per week are allowed?",
        "must_contain_any": ["three", "3"],
        "expect_source": "remote_work_policy.pdf",
    },
    {
        "id": "refusal",
        "question": "What is the CEO's favorite programming language?",
        "must_contain_any": ["do not contain enough information"],
        "expect_source": None,
    },
]


def run_in_process() -> int:
    from app.services.qa_service import answer_question

    failed = 0
    for case in CASES:
        result = answer_question(case["question"])
        answer = (result.get("answer") or "").lower()
        chunks = result.get("retrieved_chunks") or []
        top = chunks[0] if chunks else {}
        top_source = top.get("source_file", "")
        top_sim = top.get("similarity", 0)

        ok_answer = any(k.lower() in answer for k in case["must_contain_any"])
        ok_source = (
            case["expect_source"] is None
            or top_source == case["expect_source"]
            or case["expect_source"] in answer
        )

        status = "PASS" if ok_answer else "FAIL"
        if status == "FAIL":
            failed += 1
        print(f"[{status}] {case['id']}")
        print(f"  Q: {case['question']}")
        print(f"  top: {top_source} sim={top_sim} conf={result.get('confidence_score')}")
        print(f"  A: {(result.get('answer') or '')[:160]}...")
        print()
    return failed


def run_via_api(base: str) -> int:
    import httpx

    failed = 0
    for case in CASES:
        r = httpx.post(f"{base}/ask", json={"question": case["question"]}, timeout=120)
        r.raise_for_status()
        result = r.json()
        answer = (result.get("answer") or "").lower()
        chunks = result.get("retrieved_chunks") or []
        top = chunks[0] if chunks else {}
        ok_answer = any(k.lower() in answer for k in case["must_contain_any"])
        status = "PASS" if ok_answer else "FAIL"
        if status == "FAIL":
            failed += 1
        print(f"[{status}] {case['id']} | top={top.get('source_file')} sim={top.get('similarity')}")
        if status == "FAIL":
            print(f"  answer: {answer[:200]}")
    return failed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", help="Use HTTP API base URL instead of in-process")
    args = parser.parse_args()

    failed = run_via_api(args.api.rstrip("/")) if args.api else run_in_process()
    print(f"Failed: {failed} / {len(CASES)}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
