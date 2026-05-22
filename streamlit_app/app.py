"""
Potens Document Q&A — Streamlit UI

Run: streamlit run streamlit_app/app.py
Requires FastAPI backend at http://localhost:8000
"""

import os

import httpx
import streamlit as st

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Potens Document Q&A",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Minimal professional styling
st.markdown(
    """
    <style>
    .main { max-width: 1100px; }
    .stMetric { background: #f8f9fa; padding: 0.5rem; border-radius: 4px; }
    .citation-box {
        background: #f1f3f5;
        border-left: 3px solid #495057;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    h1 { font-weight: 600; color: #212529; }
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


# Sidebar
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
    st.header("Upload document")
    uploaded = st.file_uploader("PDF only", type=["pdf"])
    if uploaded and st.button("Ingest uploaded PDF"):
        with st.spinner("Indexing..."):
            try:
                result = api_upload(uploaded.read(), uploaded.name)
                st.success(
                    f"Indexed {result.get('chunks_indexed', 0)} chunks from "
                    f"{result.get('source_file')}"
                )
            except Exception as exc:
                st.error(str(exc))

    if st.button("Re-ingest all documents"):
        with st.spinner("Re-indexing..."):
            try:
                results = api_post("/ingest", {})
                st.success(f"Processed {len(results)} files")
            except Exception as exc:
                st.error(str(exc))

# Main
st.title("Potens Document Q&A")
st.caption(
    "Grounded answers with citations · English · Hindi"
)

tab_ask, tab_contradict = st.tabs(["Ask a question", "Contradiction analysis"])

with tab_ask:
    question = st.text_area(
        "Your question",
        placeholder="Ask in English or Hindi...",
        height=100,
    )
    if st.button("Get answer", type="primary", disabled=not question.strip()):
        with st.spinner("Retrieving and generating..."):
            try:
                data = api_post("/ask", {"question": question.strip()})
            except Exception as exc:
                st.error(f"Request failed: {exc}")
                st.stop()

        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("Answer")
            st.write(data.get("answer", ""))
        with col2:
            conf = data.get("confidence_score", 0)
            st.metric("Confidence", f"{conf:.0%}")
            if conf < 0.45:
                st.warning("Low confidence — verify citations")

        st.subheader("Citations")
        citations = data.get("citations", [])
        if not citations:
            st.info("No citations — answer may be insufficient-evidence response.")
        for cite in citations:
            st.markdown(
                f'<div class="citation-box">'
                f"<strong>{cite.get('label', '')}</strong><br>"
                f'<em>"{cite.get("snippet", "")}..."</em>'
                f"</div>",
                unsafe_allow_html=True,
            )

        with st.expander("Retrieval debug (transparency)", expanded=False):
            chunks = data.get("retrieved_chunks", [])
            if not chunks:
                st.write("No chunks retrieved.")
            for ch in chunks:
                emb = ch.get("embedding_similarity")
                sim_line = f"Similarity: **{ch.get('similarity', 0):.3f}**"
                if emb is not None:
                    sim_line += f" (embedding: {emb:.3f})"
                st.markdown(
                    f"**{ch.get('source_file')}** · Page {ch.get('page_number')} · "
                    f"Chunk `{ch.get('chunk_id')}` · {sim_line}"
                )
                st.text(ch.get("text_preview", ""))
                st.divider()

with tab_contradict:
    st.caption("Compare two documents on a specific topic")
    c1, c2, c3 = st.columns(3)
    with c1:
        doc1 = st.text_input("Document 1 filename", placeholder="leave_policy.pdf")
    with c2:
        doc2 = st.text_input("Document 2 filename", placeholder="hr_handbook.pdf")
    with c3:
        topic = st.text_input("Topic", placeholder="annual leave entitlement")

    if st.button("Analyze contradiction", disabled=not (doc1 and doc2 and topic)):
        with st.spinner("Analyzing..."):
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

        if result.get("conflict"):
            st.error("Conflict detected")
        else:
            st.success("No explicit conflict detected")

        st.subheader("Reasoning")
        st.write(result.get("reasoning", ""))

        evidence = result.get("evidence", [])
        if evidence:
            st.subheader("Evidence")
            for item in evidence:
                if isinstance(item, dict):
                    st.markdown(f"- **{item.get('document', '')}** ({item.get('chunk_id', '')})")
                    st.text(item.get("quote", ""))

st.divider()
st.caption("Potens IT Services · Internship take-home · Grounded RAG")
