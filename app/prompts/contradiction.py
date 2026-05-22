"""Contradiction analysis prompts."""

CONTRADICTION_SYSTEM = """You analyze two sets of document excerpts for factual conflicts on a given topic.

Rules:
1. Compare ONLY the provided excerpts — no outside knowledge.
2. Identify explicit or clearly implied contradictions.
3. If no meaningful conflict exists, set conflict to false and explain alignment.
4. Cite evidence using Document A / Document B labels and chunk references.
5. Be precise — do not invent conflicts or evidence."""

CONTRADICTION_USER_TEMPLATE = """Topic: {topic}

Document A excerpts ({doc_a}):
{excerpts_a}

Document B excerpts ({doc_b}):
{excerpts_b}

Analyze whether these excerpts contradict each other on the topic.
Return JSON with keys:
- conflict (boolean)
- reasoning (string, clear explanation)
- evidence (list of objects with: document, chunk_id, quote)"""
