from __future__ import annotations

import json
from typing import Any

from app.ai.prompt import mock_presentation, system_prompt, user_prompt
from app.config import settings
from app.models import PresentationSpec


def _list_supported_models(client) -> list[str]:
    try:
        models = list(client.models.list())
    except Exception:
        return []

    supported: list[str] = []
    for m in models:
        name = getattr(m, "name", None)
        actions = getattr(m, "supported_actions", None) or []
        if not name:
            continue
        if any(a.lower() == "generatecontent" for a in actions):
            supported.append(name)
    return supported


def _pick_model_name(client, preferred: str) -> str:
    supported = _list_supported_models(client)
    if not supported:
        return preferred

    preferred_l = preferred.lower()
    for m in supported:
        if m.lower() == preferred_l:
            return m

    flash = [m for m in supported if "flash" in m.lower()]
    gemini = [m for m in supported if "gemini" in m.lower()]
    return (flash or gemini or supported)[0]


def _extract_json_object_text(text: str) -> str:
    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        return text

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in model output")
    return text[start: end + 1]


def _build_prompt(topic: str, slide_count: int) -> str:
    return (
        system_prompt()
        + "\n\n"
        + user_prompt(topic, slide_count)
        + "\n\nReturn ONLY valid JSON. Do not include markdown fences or commentary."
    )


def _parse_spec_from_text(topic: str, slide_count: int, text: str) -> PresentationSpec:
    if not text:
        return PresentationSpec.model_validate(mock_presentation(topic, slide_count))

    try:
        json_text = _extract_json_object_text(text)
        data: Any = json.loads(json_text)
        return PresentationSpec.model_validate(data)
    except Exception:
        return PresentationSpec.model_validate(mock_presentation(topic, slide_count))


def _generate_with_gemini(topic: str, slide_count: int) -> PresentationSpec | None:
    if not settings.gemini_api_key:
        return None

    # Import lazily so missing/failed installs cleanly fall back.
    try:
        from google import genai  # type: ignore[import-not-found]

        try:
            from google.genai import types  # type: ignore[import-not-found]
        except Exception:
            types = None  # type: ignore[assignment]
    except Exception:
        return None

    client = genai.Client(api_key=settings.gemini_api_key)
    model_name = _pick_model_name(client, settings.gemini_model)

    prompt = _build_prompt(topic, slide_count)

    text: str | None = None
    try:
        if types is not None:
            resp = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                ),
            )
        else:
            resp = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config={"response_mime_type": "application/json",
                        "temperature": 0.2},
            )
        text = getattr(resp, "text", None)
        if text is None:
            text = str(resp)
    except Exception:
        return None

    return _parse_spec_from_text(topic, slide_count, text or "")


def _generate_with_openai(topic: str, slide_count: int) -> PresentationSpec | None:
    if not settings.openai_api_key:
        return None

    try:
        from openai import OpenAI  # type: ignore[import-not-found]
    except Exception:
        return None

    client = OpenAI(api_key=settings.openai_api_key)
    prompt = _build_prompt(topic, slide_count)

    text: str | None = None
    # Prefer JSON mode when available; fall back to plain text + extraction.
    try:
        resp = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": system_prompt()},
                {"role": "user", "content": user_prompt(topic, slide_count)},
                {
                    "role": "user",
                    "content": "Return ONLY valid JSON. Do not include markdown fences or commentary.",
                },
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        text = resp.choices[0].message.content
    except Exception:
        try:
            resp = client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt()},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
            text = resp.choices[0].message.content
        except Exception:
            return None

    return _parse_spec_from_text(topic, slide_count, text or "")


def generate_presentation_spec(topic: str, slide_count: int) -> PresentationSpec:
    provider = (settings.ai_provider or "auto").strip().lower()

    # Route based on explicit provider selection.
    if provider == "gemini":
        spec = _generate_with_gemini(topic, slide_count)
        return spec or PresentationSpec.model_validate(mock_presentation(topic, slide_count))
    if provider == "openai":
        spec = _generate_with_openai(topic, slide_count)
        return spec or PresentationSpec.model_validate(mock_presentation(topic, slide_count))

    # Auto mode: try Gemini first (if configured), then OpenAI.
    spec = _generate_with_gemini(topic, slide_count)
    if spec is not None:
        return spec

    spec = _generate_with_openai(topic, slide_count)
    if spec is not None:
        return spec

    return PresentationSpec.model_validate(mock_presentation(topic, slide_count))
