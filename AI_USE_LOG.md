# AI Use Log

Transparency for Potens internship take-home reviewers.

## Tools used

| Tool | Approx. usage | What it was used for |
|------|----------------|----------------------|
| **Cursor (Agent)** | ~35–45 multi-step sessions over ~12 hours | Scaffolding, implementation, refactors, README, debugging Chroma/Gemini/Streamlit on Windows |
| **Gemini 2.5 Flash** | Runtime API (not training) | Grounded answers and contradiction JSON via `google-genai` |
| **ChatGPT** | ~2–3 optional reviews | Wording checks on README sections (not code generation) |

Rough Cursor scale: on the order of **hundreds of tool calls** (file edits, terminal, search) — not token-precise; treat as **heavy AI-assisted implementation**.

## What AI generated or heavily shaped

- Initial repo layout and module boundaries  
- FastAPI route boilerplate, Pydantic models, Streamlit layout  
- First-pass prompt templates (grounded + contradiction)  
- Early sample HR PDF generator and eval script (later **removed** when scope was tightened)  
- README structure and architecture diagram drafts  

## What I decided manually (engineering judgment)

- **Scope cuts:** no reranking, hybrid BM25, OCR, LangGraph, Docker, auth  
- **Chunking:** 800 / 150 with metadata prefix in chunk text  
- **Threshold:** 0.45 cosine similarity; **no** “borderline” fallback that sends weak chunks to the LLM (removed after review — it weakened refusal honesty)  
- **Multilingual:** translation boundary (query → EN for retrieval → answer in query language)  
- **Corpus:** switched from synthetic HR PDFs to **real education policy/research PDFs** I sourced for harder RAG testing  
- **Eval honesty:** dropped automated “accuracy” script that hit Gemini rate limits; kept `manual_benchmark.json` + interaction log instead of fake metrics  
- **UI:** merged Streamlit into `ui.py` to avoid shadowing the `app` package  

## What I verified myself

- End-to-end Ask + Contradiction flows in Streamlit  
- Hindi/Marathi sample questions in `examples/education_sample_questions.md`  
- Refusal on out-of-corpus question (Q18)  
- Retrieval debug: scores, threshold flags, citations match chunks  

## Known limitations (model + stack)

- Gemini may still paraphrase; prompts require context-only answers but are not a formal guarantee  
- `langdetect` / Google Translate can misclassify or mistranslate short queries  
- Contradiction endpoint depends on topic-specific retrieval finding both sides  
- Confidence score is a **heuristic**, not calibrated probability  

## Candidate statement

I used AI as an **implementation accelerator**, not as a substitute for judgment. The submission prioritizes grounded retrieval, visible debugging, and honest scope over impressive-sounding extras. If something is not in the README or code, I did not claim it works.
