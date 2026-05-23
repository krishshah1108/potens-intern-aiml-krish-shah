"""Append each Q&A interaction to evaluation/eval_dataset.json (project root)."""

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.utils.config import settings
from app.utils.logging_config import logger

LOG_PATH = settings.interaction_log_path
_LEGACY_LOG_PATH = Path(__file__).parent / "eval_dataset.json"


def _migrate_legacy_log() -> None:
    """Move log from app/evaluation/ if it exists and root log does not."""
    if _LEGACY_LOG_PATH.exists() and not LOG_PATH.exists():
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(_LEGACY_LOG_PATH, LOG_PATH)
        logger.info("Migrated interaction log to %s", LOG_PATH)


def _load_records() -> list[dict]:
    _migrate_legacy_log()
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
    logger.info("Logged interaction %s to %s", entry["id"], LOG_PATH)


def clear_log() -> None:
    """Reset interaction log (fresh testing)."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump([], f)
    logger.info("Cleared interaction log at %s", LOG_PATH)
