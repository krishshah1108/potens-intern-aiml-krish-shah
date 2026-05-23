# potens-intern-aiml-techiekrish

**Document Q&A with Citations** — Focused, production-aware RAG for Potens IT Services.

Built for **reliability**, **grounded answers**, and **full pipeline transparency**.

---

## Project Overview

- Multilingual **queries** (English, Hindi, Gujarati, Marathi) over an **English PDF** corpus
- Grounded answers with **citations** (source, page, chunk ID, snippet)
- **Refusal** when retrieval evidence is weak
- **Streamlit UI** shows the complete RAG flow per question
- Each `/ask` interaction is appended to `app/evaluation/eval_dataset.json` for debugging

---

## Folder Structure

```
project-root/
├── app/
│   ├── api/              # FastAPI routes
│   ├── rag/              # Embeddings, ChromaDB, retrieval
│   ├── ingestion/        # PDF load, chunking, pipeline
│   ├── evaluation/       # Interaction log (eval_dataset.json)
│   ├── prompts/          # LLM prompt templates
│   ├── utils/            # Config, logging, citations
│   └── services/         # QA, LLM, language, contradiction
├── documents/            # Place PDFs here, then ingest
├── chroma_db/            # Vector store (generated locally)
├── streamlit_app/        # UI with full pipeline visibility
├── main.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env          # set GEMINI_API_KEY
```

Place PDFs in `documents/`, then:

```bash
python main.py                  # API — ingests if chroma_db is empty
streamlit run streamlit_app/app.py
```

---

## Fresh testing (clean slate)

```powershell
Remove-Item documents\*.pdf -Force -ErrorAction SilentlyContinue
Remove-Item chroma_db\* -Recurse -Force -ErrorAction SilentlyContinue
# Reset interaction log:
# app/evaluation/eval_dataset.json should contain: []
```

Upload PDFs via Streamlit sidebar or copy files into `documents/` and click **Re-ingest all**.

---

## Streamlit — full pipeline per question

1. **Your question** (with detected language)
2. **Retrieval** — English query, all chunks, scores, threshold flags
3. **Prompts** — system + user prompt (with context block)
4. **LLM response**
5. **Citations**
6. Confirmation that the trace was saved to `eval_dataset.json`

Use the **Interaction log** tab to inspect all past runs as JSON.

---

## Interaction log (`eval_dataset.json`)

Path: `app/evaluation/eval_dataset.json`

Each `POST /ask` appends one record:

| Field | Content |
|-------|---------|
| `question` | Original user query |
| `retrieval` | All chunks, scores, threshold filter, English retrieval query |
| `prompts` | System and user prompts |
| `llm_response` | Final answer |
| `citations` | References with snippets |
| `refused_insufficient_evidence` | Safe refusal flag |
| `latency_seconds` | End-to-end timing |

This is an **explainability log**, not a labeled accuracy benchmark.

---

## API

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Status and chunk count |
| `POST /ask` | Full trace + logging |
| `POST /contradict` | Compare two documents on a topic |
| `POST /ingest` | Re-index all PDFs in `documents/` |
| `POST /ingest/upload` | Upload one PDF |

---

## Technology Choices

| Component | Choice |
|-----------|--------|
| Vector DB | ChromaDB |
| LLM | Gemini 2.5 Flash (`google-genai`) |
| Embeddings | paraphrase-multilingual-MiniLM-L12-v2 |
| Chunking | RecursiveCharacterTextSplitter (800 / 150 overlap) |
| Backend | FastAPI |
| UI | Streamlit |

---

## Hallucination prevention

- Similarity threshold on retrieved chunks
- Strict context-only prompts
- Fixed insufficient-information refusal message
- Heuristic confidence score

---

## Limitations

- English PDFs only (queries may be multilingual)
- No OCR, reranking, or hybrid BM25
- Gemini free tier rate limits apply
- `eval_dataset.json` grows with each question — clear it when restarting tests

---

## AI Use Log

See [AI_USE_LOG.md](AI_USE_LOG.md).
