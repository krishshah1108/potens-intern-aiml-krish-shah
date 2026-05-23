"""
Potens Document Q&A — Streamlit UI (full pipeline transparency)

Run: streamlit run streamlit_app/app.py
Requires: python main.py
"""

import json
import os
from pathlib import Path

import httpx
import streamlit as st

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")
LOG_PATH = Path(__file__).resolve().parents[1] / "app" / "evaluation" / "eval_dataset.json"

st.set_page_config(
    page_title="Potens Document Q&A",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main { max-width: 1200px; }
    .citation-box {
        background: #f1f3f5;
        border-left: 3px solid #495057;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    .chunk-box {
        background: #fafafa;
        border: 1px solid #dee2e6;
        padding: 0.6rem 0.8rem;
        margin: 0.4rem 0;
        border-radius: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def api_get(path: str) -> dict | list:
    with httpx.Client(timeout=120.0) as client:
        r = client.get(f"{API_BASE}{path}")
        r.raise_for_status()
        return r.json()


def api_post(path: str, json_body: dict) -> dict:
    with httpx.Client(timeout=120.0) as client:
        r = client.post(f"{API_BASE}{path}", json=json_body)
        r.raise_for_status()
        return r.json()


def api_upload(file_bytes: bytes, filename: str) -> dict:
    with httpx.Client(timeout=180.0) as client:
        r = client.post(
            f"{API_BASE}/ingest/upload",
            files={"file": (filename, file_bytes, "application/pdf")},
        )
        r.raise_for_status()
        return r.json()


def render_ask_flow(data: dict) -> None:
    st.subheader("1. Your question")
    st.info(data.get("question", ""))
    st.caption(f"Detected language: **{data.get('query_language', 'en')}**")

    retrieval = data.get("retrieval", {})
    st.subheader("2. Retrieval")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Chunks retrieved", retrieval.get("chunks_retrieved", 0))
    c2.metric("Above threshold", retrieval.get("chunks_above_threshold", 0))
    c3.metric("Confidence", f"{data.get('confidence_score', 0):.0%}")
    c4.metric("Latency", f"{data.get('latency_seconds', 0)}s")

    st.markdown("**English retrieval query (translation boundary):**")
    st.code(retrieval.get("retrieval_query_english", ""), language=None)
    st.caption(
        f"top_k={retrieval.get('top_k')} · threshold={retrieval.get('similarity_threshold')} · "
        f"{retrieval.get('answer_language_instruction', '')}"
    )

    st.markdown("**All retrieved chunks**")
    for ch in retrieval.get("all_retrieved_chunks", []):
        flag = "✓ used" if ch.get("used_in_llm_context") else ("✓ above thr" if ch.get("above_threshold") else "below thr")
        st.markdown(
            f'<div class="chunk-box">'
            f"<strong>{ch.get('source_file')}</strong> · p.{ch.get('page_number')} · "
            f"`{ch.get('chunk_id')}` · sim **{ch.get('similarity', 0):.3f}** · {flag}"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.text(ch.get("text", "")[:600] + ("…" if len(ch.get("text", "")) > 600 else ""))

    prompts = data.get("prompts", {})
    st.subheader("3. Prompts sent to LLM")
    with st.expander("System prompt", expanded=True):
        st.text(prompts.get("system_prompt", ""))
    with st.expander("User prompt (context + question)", expanded=True):
        st.text(prompts.get("user_prompt") or "(not sent — insufficient retrieval evidence)")

    st.subheader("4. LLM response")
    if data.get("refused_insufficient_evidence"):
        st.warning("Insufficient evidence — safe refusal")
    st.write(data.get("llm_response", data.get("answer", "")))
    if data.get("llm_latency_seconds"):
        st.caption(f"LLM latency: {data.get('llm_latency_seconds')}s")

    st.subheader("5. Citations")
    citations = data.get("citations", [])
    if not citations:
        st.info("No citations for this response.")
    for cite in citations:
        st.markdown(
            f'<div class="citation-box">'
            f"<strong>{cite.get('label', '')}</strong><br>"
            f'<em>"{cite.get("snippet", "")}"</em>'
            f"</div>",
            unsafe_allow_html=True,
        )

    st.subheader("6. Logged to eval_dataset.json")
    st.caption(f"Each ask appends a full trace to `{LOG_PATH}`")


with st.sidebar:
    st.header("System")
    try:
        health = api_get("/health")
        st.success(f"API: {health['status']}")
        st.caption(f"Indexed chunks: {health['vector_store_chunks']}")
    except Exception as exc:
        st.error(f"API unreachable: {exc}")
        st.caption("Start backend: `python main.py`")

    st.divider()
    st.header("Documents")
    uploaded = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded and st.button("Ingest PDF"):
        with st.spinner("Indexing..."):
            try:
                result = api_upload(uploaded.read(), uploaded.name)
                st.success(f"Indexed {result.get('chunks_indexed', 0)} chunks")
            except Exception as exc:
                st.error(str(exc))

    if st.button("Re-ingest all in documents/"):
        with st.spinner("Re-indexing..."):
            try:
                results = api_post("/ingest", {})
                st.success(f"Processed {len(results)} files")
            except Exception as exc:
                st.error(str(exc))

    st.divider()
    st.header("Interaction log")
    if LOG_PATH.exists():
        try:
            records = json.loads(LOG_PATH.read_text(encoding="utf-8"))
            st.caption(f"{len(records)} interactions logged")
        except json.JSONDecodeError:
            st.caption("Log file empty or invalid")
    else:
        st.caption("No interactions yet")

st.title("Potens Document Q&A")
st.caption("Full RAG pipeline visibility · English PDFs · multilingual queries")

tab_ask, tab_contradict, tab_log = st.tabs(["Ask", "Contradiction", "Interaction log"])

with tab_ask:
    question = st.text_area(
        "Your question",
        placeholder="English, Hindi, Gujarati, or Marathi...",
        height=90,
    )
    if st.button("Run RAG pipeline", type="primary", disabled=not question.strip()):
        with st.spinner("Retrieve → prompt → generate..."):
            try:
                data = api_post("/ask", {"question": question.strip()})
            except Exception as exc:
                st.error(str(exc))
                st.stop()
        render_ask_flow(data)

with tab_contradict:
    c1, c2, c3 = st.columns(3)
    with c1:
        doc1 = st.text_input("Document 1", placeholder="leave_policy.pdf")
    with c2:
        doc2 = st.text_input("Document 2", placeholder="hr_handbook_excerpt.pdf")
    with c3:
        topic = st.text_input("Topic", placeholder="annual leave entitlement")

    if st.button("Analyze contradiction", disabled=not (doc1 and doc2 and topic)):
        with st.spinner("Analyzing..."):
            try:
                result = api_post(
                    "/contradict",
                    {"document_1": doc1.strip(), "document_2": doc2.strip(), "topic": topic.strip()},
                )
            except Exception as exc:
                st.error(str(exc))
                st.stop()
        if result.get("conflict"):
            st.error("Conflict detected")
        else:
            st.success("No explicit conflict")
        st.write(result.get("reasoning", ""))
        for item in result.get("evidence", []):
            if isinstance(item, dict):
                st.markdown(f"- **{item.get('document', '')}** — {item.get('quote', '')}")

with tab_log:
    st.caption(f"File: `{LOG_PATH}`")
    if LOG_PATH.exists():
        try:
            records = json.loads(LOG_PATH.read_text(encoding="utf-8"))
            st.json(records)
        except Exception as exc:
            st.error(str(exc))
    else:
        st.info("No interactions logged yet. Ask a question in the Ask tab.")
