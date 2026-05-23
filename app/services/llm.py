"""Gemini LLM client (google-genai SDK) with rate-limit retries."""

import json
import re
import time

from google import genai
from google.genai import types

from app.utils.config import settings
from app.utils.logging_config import logger

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if not settings.gemini_api_key:
        raise ValueError(
            "GEMINI_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    if _client is None:
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


def generate_text(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.1,
    max_retries: int = 3,
) -> tuple[str, float]:
    """Generate text; returns (response, latency_seconds). Retries on 429 quota errors."""
    client = _get_client()
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=temperature,
        max_output_tokens=1024,
    )

    last_error: Exception | None = None
    for attempt in range(max_retries):
        start = time.perf_counter()
        try:
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=user_prompt,
                config=config,
            )
            latency = time.perf_counter() - start
            text = (response.text or "").strip()
            logger.info("LLM response generated in %.2fs (%d chars)", latency, len(text))
            return text, latency
        except Exception as exc:
            last_error = exc
            msg = str(exc).lower()
            if "429" in msg or "quota" in msg or "resource_exhausted" in msg:
                wait = 15 * (attempt + 1)
                logger.warning("Gemini rate limit — retry %d/%d in %ds", attempt + 1, max_retries, wait)
                time.sleep(wait)
                continue
            raise

    raise last_error or RuntimeError("LLM request failed after retries")


def generate_json(system_prompt: str, user_prompt: str) -> dict:
    """Generate and parse JSON response."""
    text, _ = generate_text(system_prompt, user_prompt, temperature=0.0)
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
