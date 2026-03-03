from __future__ import annotations

import json
import re
from typing import Any

from app.ai.prompt import mock_presentation, system_prompt, user_prompt
from app.config import settings
from app.models import PresentationSpec


def _calculate_optimal_slide_count(topic: str, requested_count: int) -> int:
    """Calculate optimal slide count based on content structure.

    For lesson plans with multiple sections, we need more slides to avoid cramming.
    This function detects structured content and recommends a minimum slide count.
    """
    print(f"\n[OPTIMAL] Calculating optimal slide count")
    print(f"[OPTIMAL] Topic length: {len(topic)} chars")
    print(f"[OPTIMAL] Requested count: {requested_count}")

    topic_lower = topic.lower()

    # Detect lesson plan sections
    lesson_sections = []
    section_patterns = [
        r'\bengage\b.*?(?=\n\n|\nexplore|\nexplain|\nelaborate|\nevaluate|$)',
        r'\bexplore\b.*?(?=\n\n|\nengage|\nexplain|\nelaborate|\nevaluate|$)',
        r'\bexplain\b.*?(?=\n\n|\nengage|\nexplore|\nelaborate|\nevaluate|$)',
        r'\belaborate\b.*?(?=\n\n|\nengage|\nexplore|\nexplain|\nevaluate|$)',
        r'\bevaluate\b.*?(?=\n\n|\nengage|\nexplore|\nexplain|\nelaborate|$)',
    ]

    for pattern in section_patterns:
        if re.search(pattern, topic_lower, re.DOTALL | re.IGNORECASE):
            lesson_sections.append(pattern)

    print(f"[OPTIMAL] Found {len(lesson_sections)} lesson sections")

    # Check for other indicators of structured content
    has_objectives = 'learning objective' in topic_lower or 'students will' in topic_lower
    has_materials = 'material' in topic_lower and ':' in topic
    has_assessment = 'assessment' in topic_lower or 'evaluation' in topic_lower

    print(f"[OPTIMAL] has_objectives: {has_objectives}, has_materials: {has_materials}, has_assessment: {has_assessment}")

    # Count distinct activities/sections
    section_count = len(lesson_sections)

    # Calculate minimum needed slides for lesson plans
    if section_count >= 3:  # Likely a 5E lesson plan
        print(f"[OPTIMAL] Detected lesson plan with {section_count} sections")
        # Structure: Intro + Objectives + (5 sections) + Flow + Summary = 9 slides minimum
        min_slides = 2 + section_count + 2  # intro + objectives + sections + flow + summary

        if has_materials:
            min_slides += 1
        if has_assessment and section_count < 5:  # Don't double-count if Evaluate exists
            min_slides += 1

        print(f"[OPTIMAL] Calculated min_slides: {min_slides}")

        # If user requested fewer slides than needed, recommend more
        if requested_count < min_slides:
            print(f"[OPTIMAL] Recommending {min_slides} instead of {requested_count}")
            return min_slides

    # For other long content, check paragraph/section count
    paragraphs = topic.count('\n\n')
    headings = topic.count('**') + topic.count('##')

    print(f"[OPTIMAL] paragraphs: {paragraphs}, headings: {headings}")

    if paragraphs > 5 or headings > 5:
        min_slides = min(15, paragraphs + headings + 3)  # Cap at 15
        print(f"[OPTIMAL] Long content detected, min_slides: {min_slides}")
        if requested_count < min_slides:
            print(f"[OPTIMAL] Recommending {min_slides} instead of {requested_count}")
            return min_slides

    print(f"[OPTIMAL] Using requested count: {requested_count}")
    return requested_count


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
        print("[AI] No OpenAI API key configured")
        return None

    try:
        from openai import OpenAI  # type: ignore[import-not-found]
    except Exception as e:
        print(f"[AI] Failed to import OpenAI: {e}")
        return None

    print(f"[AI] Creating OpenAI client")
    client = OpenAI(api_key=settings.openai_api_key)
    prompt = _build_prompt(topic, slide_count)
    print(f"[AI] Built prompt, length: {len(prompt)} chars")

    text: str | None = None
    # Prefer JSON mode when available; fall back to plain text + extraction.
    try:
        print(f"[AI] Calling OpenAI with model: {settings.openai_model}")
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
        print(f"[AI] OpenAI response received, length: {len(text) if text else 0} chars")
    except Exception as e:
        print(f"[AI] JSON mode failed: {e}, trying plain mode")
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
            print(f"[AI] Plain mode response received, length: {len(text) if text else 0} chars")
        except Exception as e2:
            print(f"[AI] Plain mode also failed: {e2}")
            return None

    result = _parse_spec_from_text(topic, slide_count, text or "")
    print(f"[AI] Parsed spec with {len(result.slides)} slides")
    return result


def generate_presentation_spec(topic: str, slide_count: int) -> PresentationSpec:
    print(f"\n[AI] Starting spec generation")
    print(f"[AI] Requested slide count: {slide_count}")

    # Calculate optimal slide count based on content structure
    optimal_count = _calculate_optimal_slide_count(topic, slide_count)
    print(f"[AI] Calculated optimal count: {optimal_count}")

    # Use the higher of requested or calculated count
    actual_count = max(slide_count, optimal_count)
    print(f"[AI] Actual count (max of requested/optimal): {actual_count}")

    provider = (settings.ai_provider or "auto").strip().lower()
    print(f"[AI] Provider: {provider}")

    # Route based on explicit provider selection.
    if provider == "gemini":
        print(f"[AI] Using Gemini provider")
        spec = _generate_with_gemini(topic, actual_count)
        if spec:
            print(f"[AI] Gemini returned spec with {len(spec.slides)} slides")
            return spec
        print(f"[AI] Gemini failed, using mock data")
        return PresentationSpec.model_validate(mock_presentation(topic, actual_count))
    if provider == "openai":
        print(f"[AI] Using OpenAI provider")
        spec = _generate_with_openai(topic, actual_count)
        if spec:
            print(f"[AI] OpenAI returned spec with {len(spec.slides)} slides")
            return spec
        print(f"[AI] OpenAI failed, using mock data")
        return PresentationSpec.model_validate(mock_presentation(topic, actual_count))

    # Auto mode: try Gemini first (if configured), then OpenAI.
    print(f"[AI] Auto mode: trying Gemini first")
    spec = _generate_with_gemini(topic, actual_count)
    if spec is not None:
        print(f"[AI] Gemini succeeded with {len(spec.slides)} slides")
        return spec

    print(f"[AI] Gemini failed, trying OpenAI")
    spec = _generate_with_openai(topic, actual_count)
    if spec is not None:
        print(f"[AI] OpenAI succeeded with {len(spec.slides)} slides")
        return spec

    print(f"[AI] All providers failed, using mock data")
    return PresentationSpec.model_validate(mock_presentation(topic, actual_count))
