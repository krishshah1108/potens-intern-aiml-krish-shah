"""Gemini LLM client wrapper."""

import json
import re
import time

import google.generativeai as genai

from app.utils.config import settings
from app.utils.logging_config import logger


def _configure() -> None:
    if not settings.gemini_api_key:
        raise ValueError(
            "GEMINI_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    genai.configure(api_key=settings.gemini_api_key)


def generate_text(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.1,
) -> tuple[str, float]:
    """Generate text; returns (response, latency_seconds)."""
    _configure()
    model = genai.GenerativeModel(
        model_name=settings.gemini_model,
        system_instruction=system_prompt,
        generation_config=genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=1024,
        ),
    )

    start = time.perf_counter()
    response = model.generate_content(user_prompt)
    latency = time.perf_counter() - start

    text = (response.text or "").strip()
    logger.info("LLM response generated in %.2fs (%d chars)", latency, len(text))
    return text, latency


def generate_json(system_prompt: str, user_prompt: str) -> dict:
    """Generate and parse JSON response."""
    text, _ = generate_text(system_prompt, user_prompt, temperature=0.0)
    # Strip markdown code fences if present
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.MULTILINE)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning("Failed to parse JSON from LLM; wrapping raw text")
        return {
            "conflict": False,
            "reasoning": text,
            "evidence": [],
        }
