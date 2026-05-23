"""
Potens Document Q&A — Streamlit UI

Run: streamlit run streamlit_app/ui.py
Requires: python main.py
"""

import html
import json
import os
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import httpx
import streamlit as st

from app.utils.config import settings

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")
LOG_PATH = settings.interaction_log_path

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
    .answer-highlight {
        background: linear-gradient(135deg, #e7f5ff 0%, #f8f9fa 100%);
        border: 2px solid #1971c2;
        border-radius: 10px;
        padding: 1.25rem 1.5rem;
        margin: 0.5rem 0 1.25rem 0;
        font-size: 1.05rem;
        line-height: 1.65;
        color: #212529;
    }
    .answer-label {
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #1971c2;
        margin-bottom: 0.5rem;
    }
    .citation-box {
        background: #f1f3f5;
        border-left: 3px solid #495057;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def _init_ask_state() -> None:
    for key, val in {
        "ask_processing": False,
        "ask_result": None,
        "ask_error": None,
        "pending_question": None,
        "question_field": "",
    }.items():
        if key not in st.session_state:
            st.session_state[key] = val


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


def render_answer(data: dict) -> None:
    answer_text = data.get("llm_response") or data.get("answer") or ""
    st.markdown('<div class="answer-label">Answer</div>', unsafe_allow_html=True)
    if data.get("refused_insufficient_evidence"):
        st.warning("Insufficient evidence — safe refusal")
    safe = html.escape(answer_text).replace("\n", "<br>")
    st.markdown(f'<div class="answer-highlight">{safe}</div>', unsafe_allow_html=True)

    retrieval = data.get("retrieval", {})
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Confidence", f"{data.get('confidence_score', 0):.0%}")
    c2.metric("Chunks used", retrieval.get("chunks_above_threshold", 0))
    c3.metric("Total latency", f"{data.get('latency_seconds', 0)}s")
    if data.get("llm_latency_seconds"):
        c4.metric("LLM latency", f"{data.get('llm_latency_seconds')}s")
    else:
        c4.metric("Language", data.get("query_language", "en"))


def render_pipeline_details(data: dict) -> None:
    retrieval = data.get("retrieval", {})
    prompts = data.get("prompts", {})
    citations = data.get("citations", [])

    with st.expander("Question & language", expanded=False):
        st.markdown(f"**Question:** {data.get('question', '')}")
        st.caption(f"Detected: **{data.get('query_language', 'en')}**")

    with st.expander("Retrieval", expanded=False):
        c1, c2, c3 = st.columns(3)
        c1.metric("Retrieved", retrieval.get("chunks_retrieved", 0))
        c2.metric("Above threshold", retrieval.get("chunks_above_threshold", 0))
        c3.metric("top_k", retrieval.get("top_k", "—"))
        st.code(retrieval.get("retrieval_query_english", ""), language=None)
        st.caption(
            f"threshold={retrieval.get('similarity_threshold')} · "
            f"{retrieval.get('answer_language_instruction', '')}"
        )

    chunks = retrieval.get("all_retrieved_chunks", [])
    with st.expander(f"Retrieved chunks ({len(chunks)})", expanded=False):
        if not chunks:
            st.info("No chunks retrieved.")
        for idx, ch in enumerate(chunks, start=1):
            flag = (
                "used in LLM"
                if ch.get("used_in_llm_context")
                else ("above threshold" if ch.get("above_threshold") else "below threshold")
            )
            with st.expander(
                f"{idx}. {ch.get('source_file')} · p.{ch.get('page_number')} · "
                f"sim {ch.get('similarity', 0):.3f} · {flag}",
                expanded=False,
            ):
                st.caption(f"`{ch.get('chunk_id')}`")
                st.text(ch.get("text", ""))

    with st.expander(f"Citations ({len(citations)})", expanded=False):
        if not citations:
            st.info("No citations.")
        for cite in citations:
            st.markdown(
                f'<div class="citation-box">'
                f"<strong>{cite.get('label', '')}</strong><br>"
                f'<em>"{cite.get("snippet", "")}"</em></div>',
                unsafe_allow_html=True,
            )

    with st.expander("Prompts", expanded=False):
        st.markdown("**System**")
        st.text(prompts.get("system_prompt", ""))
        st.markdown("**User (context + question)**")
        st.text(prompts.get("user_prompt") or "(not sent — insufficient evidence)")

    with st.expander("Full trace (JSON)", expanded=False):
        st.json(data)


def process_pending_question() -> None:
    question = st.session_state.pending_question
    if not question:
        return
    st.session_state.ask_processing = True
    st.session_state.ask_error = None
    try:
        with st.spinner("Retrieving and generating…"):
            st.session_state.ask_result = api_post("/ask", {"question": question})
        st.session_state.question_field = ""
    except Exception as exc:
        st.session_state.ask_error = str(exc)
        st.session_state.ask_result = None
    finally:
        st.session_state.pending_question = None
        st.session_state.ask_processing = False


# --- Sidebar ---
with st.sidebar:
    st.header("System")
    try:
        health = api_get("/health")
        st.success(f"API: {health['status']}")
        st.caption(f"Chunks indexed: {health['vector_store_chunks']}")
    except Exception as exc:
        st.error(f"API unreachable: {exc}")
        st.caption("Run `python main.py`")

    st.divider()
    st.header("Documents")
    uploaded = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded and st.button("Ingest PDF"):
        with st.spinner("Indexing…"):
            try:
                r = api_upload(uploaded.read(), uploaded.name)
                st.success(f"Indexed {r.get('chunks_indexed', 0)} chunks")
            except Exception as exc:
                st.error(str(exc))

    if st.button("Re-ingest all in documents/"):
        with st.spinner("Re-indexing…"):
            try:
                st.success(f"Processed {len(api_post('/ingest', {}))} files")
            except Exception as exc:
                st.error(str(exc))

    st.divider()
    if LOG_PATH.exists():
        try:
            n = len(json.loads(LOG_PATH.read_text(encoding="utf-8")))
            st.caption(f"Interaction log: {n} entries")
        except json.JSONDecodeError:
            st.caption("Interaction log: empty")

# --- Main ---
st.title("Potens Document Q&A")
st.caption("English PDFs · multilingual queries · full pipeline visibility")

tab_ask, tab_contradict, tab_log = st.tabs(["Ask", "Contradiction", "Interaction log"])

with tab_ask:
    _init_ask_state()

    if st.session_state.pending_question:
        process_pending_question()
        st.rerun()

    with st.form("ask_form", clear_on_submit=False):
        st.text_area(
            "Your question",
            placeholder="English, Hindi, Gujarati, or Marathi…",
            height=90,
            key="question_field",
            disabled=st.session_state.ask_processing,
        )
        submitted = st.form_submit_button(
            "Get answer",
            type="primary",
            disabled=st.session_state.ask_processing,
        )

    if submitted:
        q = (st.session_state.question_field or "").strip()
        if q and not st.session_state.ask_processing:
            st.session_state.ask_result = None
            st.session_state.ask_error = None
            st.session_state.pending_question = q
            st.rerun()
        elif not q:
            st.warning("Enter a question first.")

    if st.session_state.ask_processing:
        st.caption("Processing…")

    st.divider()

    if st.session_state.ask_error:
        st.error(st.session_state.ask_error)

    if st.session_state.ask_result:
        st.subheader("Response")
        render_answer(st.session_state.ask_result)
        st.divider()
        st.subheader("Pipeline details")
        render_pipeline_details(st.session_state.ask_result)

with tab_contradict:
    st.caption("See `examples/education_sample_questions.md` for sample pairs (C1–C4).")
    c1, c2, c3 = st.columns(3)
    with c1:
        doc1 = st.text_input("Document 1", placeholder="student_data_privacy_policy_2024.pdf")
    with c2:
        doc2 = st.text_input("Document 2", placeholder="national_curriculum_framework_2023.pdf")
    with c3:
        topic = st.text_input("Topic", placeholder="definition of compliance")

    if st.button("Analyze contradiction", disabled=not (doc1 and doc2 and topic)):
        with st.spinner("Analyzing…"):
            try:
                result = api_post(
                    "/contradict",
                    {
                        "document_1": doc1.strip(),
                        "document_2": doc2.strip(),
                        "topic": topic.strip(),
                    },
                )
            except Exception as exc:
                st.error(str(exc))
                st.stop()
        st.error("Conflict detected") if result.get("conflict") else st.success("No explicit conflict")
        st.write(result.get("reasoning", ""))
        for item in result.get("evidence", []):
            if isinstance(item, dict):
                st.markdown(f"- **{item.get('document', '')}** — {item.get('quote', '')}")

with tab_log:
    st.caption(f"`{LOG_PATH}`")
    if LOG_PATH.exists():
        try:
            st.json(json.loads(LOG_PATH.read_text(encoding="utf-8")))
        except Exception as exc:
            st.error(str(exc))
    else:
        st.info("No interactions yet. Ask a question in the Ask tab.")
