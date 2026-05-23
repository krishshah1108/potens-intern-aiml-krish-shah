"""Append each Q&A interaction to evaluation/eval_dataset.json."""

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.utils.logging_config import logger

LOG_PATH = Path(__file__).parent / "eval_dataset.json"


def _load_records() -> list[dict]:
    if not LOG_PATH.exists():
        return []
    with open(LOG_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def append_interaction(record: dict) -> None:
    """Persist one full pipeline trace for debugging."""
    entry = {
        "id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **record,
    }
    records = _load_records()
    records.append(entry)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    logger.info("Logged interaction %s to %s", entry["id"], LOG_PATH.name)


def clear_log() -> None:
    """Reset interaction log (fresh testing)."""
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump([], f)
    logger.info("Cleared interaction log at %s", LOG_PATH)
