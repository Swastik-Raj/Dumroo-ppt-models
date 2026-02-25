from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

STORAGE_DIR = Path("data/presentations")
STORAGE_FILE = STORAGE_DIR / "presentations.json"


def _ensure_storage_dir():
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    if not STORAGE_FILE.exists():
        STORAGE_FILE.write_text("[]", encoding="utf-8")


def _load_presentations() -> list[dict[str, Any]]:
    _ensure_storage_dir()
    try:
        data = json.loads(STORAGE_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_presentations(presentations: list[dict[str, Any]]) -> None:
    _ensure_storage_dir()
    STORAGE_FILE.write_text(
        json.dumps(presentations, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def _cleanup_old_presentations(max_age_hours: int = 24) -> None:
    presentations = _load_presentations()
    cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)

    cleaned = [
        p for p in presentations
        if datetime.fromisoformat(p.get("created_at", "1970-01-01T00:00:00")) > cutoff_time
    ]

    if len(cleaned) != len(presentations):
        _save_presentations(cleaned)


def create_presentation(topic: str, theme: str, slides_data: list[dict[str, Any]]) -> str:
    _cleanup_old_presentations()

    presentation_id = str(uuid.uuid4())
    presentations = _load_presentations()

    presentation = {
        "id": presentation_id,
        "topic": topic,
        "theme": theme,
        "slides_data": slides_data,
        "created_at": datetime.utcnow().isoformat(),
    }

    presentations.append(presentation)
    _save_presentations(presentations)

    return presentation_id


def get_presentation(presentation_id: str) -> dict[str, Any] | None:
    presentations = _load_presentations()
    for p in presentations:
        if p.get("id") == presentation_id:
            return p
    return None


def update_slide(presentation_id: str, slide_id: int, title: str, content: str) -> bool:
    presentations = _load_presentations()

    for p in presentations:
        if p.get("id") == presentation_id:
            slides_data = p.get("slides_data", [])
            if 0 <= slide_id < len(slides_data):
                slides_data[slide_id]["title"] = title
                slides_data[slide_id]["content"] = content
                _save_presentations(presentations)
                return True
            return False

    return False


def delete_presentation(presentation_id: str) -> bool:
    presentations = _load_presentations()
    original_count = len(presentations)

    presentations = [p for p in presentations if p.get("id") != presentation_id]

    if len(presentations) < original_count:
        _save_presentations(presentations)
        return True

    return False
