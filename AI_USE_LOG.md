# AI Use Log

Transparency log for tools used while building this internship take-home project.

## Tools Used

| Tool | Approx. prompts / sessions | Purpose |
|------|---------------------------|---------|
| **Cursor AI** | ~25–30 agent interactions | Project scaffolding, architecture design, code implementation, test writing, README drafting, debugging |
| **Gemini 2.5 Flash** | Runtime (API calls) | Grounded answer generation, contradiction analysis JSON output |
| **ChatGPT** | ~3–5 (optional review) | Reviewing README clarity, sanity-checking evaluation metrics wording |

## What AI Helped With

- Initial folder structure and module boundaries
- Boilerplate for FastAPI routes, Pydantic schemas, and Streamlit layout
- Prompt templates for grounded answering and contradiction analysis
- Test case skeletons and manual test results script structure
- README architecture diagram (Mermaid) and tradeoffs section drafting

## What Was Done Manually / With Engineering Judgment

- Technology stack selection and explicit exclusions (no reranking, no hybrid BM25, no agents)
- Chunk size (800) and overlap (150) tuning rationale
- Similarity threshold (0.45) and confidence heuristic design
- Multilingual translation-boundary approach (simplicity over complexity)
- Hallucination refusal strategy (threshold + strict prompts)
- Intentional contradiction pair: `leave_policy.pdf` vs `hr_handbook_excerpt.pdf` (20 vs 18 leave days)
- Interaction log schema for app/evaluation/eval_dataset.json

## Honest Notes

- AI-assisted code was reviewed, simplified, and trimmed to avoid over-engineering.
- All prompts enforce context-only answers; this was a deliberate design choice, not auto-generated fluff.
- Limitations and future improvements were written to reflect real constraints, not marketing copy.

## Candidate Statement

I used AI as an accelerator for implementation and documentation, while retaining responsibility for architecture, reliability tradeoffs, and evaluation design. The final system reflects intentional engineering decisions suitable for a 24-hour focused assignment.
