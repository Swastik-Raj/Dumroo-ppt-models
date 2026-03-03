from __future__ import annotations

import json
import os
from pathlib import Path

from app.ai.openai_client import generate_presentation_spec
from app.config import settings
from app.images.cache import ImageCache
from app.images.unsplash import UnsplashImageSearch
from app.planner import normalize_presentation_spec, plan_slides
from app.ppt.builder import build_pptx
from app.ppt.theme import get_theme


def preprocess_topic_input(topic: str) -> str:
    """Preprocess user input to make it more AI-friendly.

    Helps the AI better understand structured content like lesson plans by:
    - Normalizing section markers
    - Cleaning up formatting artifacts
    - Preserving important structure
    """
    # Don't modify short inputs
    if len(topic) < 200:
        return topic

    # Normalize common section markers to make them more visible
    markers = [
        ("**Engage:**", "\n\n=== ENGAGE SECTION ===\n"),
        ("**Explore:**", "\n\n=== EXPLORE SECTION ===\n"),
        ("**Explain:**", "\n\n=== EXPLAIN SECTION ===\n"),
        ("**Elaborate:**", "\n\n=== ELABORATE SECTION ===\n"),
        ("**Evaluate:**", "\n\n=== EVALUATE SECTION ===\n"),
        ("**Materials:**", "\n\n=== MATERIALS SECTION ===\n"),
        ("**Objectives:**", "\n\n=== OBJECTIVES SECTION ===\n"),
        ("**Learning Objectives:**", "\n\n=== LEARNING OBJECTIVES SECTION ===\n"),
        ("**Assessment:**", "\n\n=== ASSESSMENT SECTION ===\n"),
        ("**Vocabulary:**", "\n\n=== VOCABULARY SECTION ===\n"),
        ("**Standards:**", "\n\n=== STANDARDS SECTION ===\n"),
        ("Engage:", "\n\n=== ENGAGE SECTION ===\n"),
        ("Explore:", "\n\n=== EXPLORE SECTION ===\n"),
        ("Explain:", "\n\n=== EXPLAIN SECTION ===\n"),
        ("Elaborate:", "\n\n=== ELABORATE SECTION ===\n"),
        ("Evaluate:", "\n\n=== EVALUATE SECTION ===\n"),
    ]

    processed = topic
    for marker, replacement in markers:
        processed = processed.replace(marker, replacement)

    # Clean up multiple consecutive newlines (but preserve double newlines for sections)
    while "\n\n\n" in processed:
        processed = processed.replace("\n\n\n", "\n\n")

    return processed


def generate_pptx_for_topic(topic: str, slide_count: int | None, *, theme_name: str | None = None) -> str:
    from app.ai.openai_client import _calculate_optimal_slide_count

    slide_count_requested = slide_count or settings.default_slide_count

    print(f"\n[PIPELINE] Starting generation")
    print(f"[PIPELINE] Topic length: {len(topic)} chars")
    print(f"[PIPELINE] Topic preview: {topic[:100]}...")
    print(f"[PIPELINE] Requested slide count: {slide_count_requested}")
    print(f"[PIPELINE] Theme: {theme_name}")

    # Preprocess the input to make it more AI-friendly
    processed_topic = preprocess_topic_input(topic)
    if processed_topic != topic:
        print(f"[PIPELINE] Preprocessed topic (normalized section markers)")

    # Calculate optimal count and use it for normalization
    optimal_count = _calculate_optimal_slide_count(processed_topic, slide_count_requested)
    slide_count_final = max(slide_count_requested, optimal_count)
    print(f"[PIPELINE] Using slide count: {slide_count_final} (optimal: {optimal_count})")

    spec_raw = generate_presentation_spec(
        topic=processed_topic, slide_count=slide_count_requested)

    print(f"[PIPELINE] Generated raw spec with {len(spec_raw.slides)} slides")
    print(f"[PIPELINE] Spec title: {spec_raw.title}")

    # Use the final count (which may be higher than requested) for normalization
    spec = normalize_presentation_spec(
        spec_raw, topic=topic, slide_count=slide_count_final)

    print(f"[PIPELINE] Normalized spec with {len(spec.slides)} slides")

    plans = plan_slides(spec)
    print(f"[PIPELINE] Created {len(plans)} slide plans")

    cache = ImageCache(base_dir=settings.cache_dir)

    image_search = None
    if settings.unsplash_access_key:
        image_search = UnsplashImageSearch(
            access_key=settings.unsplash_access_key, cache=cache)

    theme = get_theme(theme_name or settings.theme_name)

    output_path = build_pptx(
        presentation_spec=spec,
        slide_plans=plans,
        image_search=image_search,
        output_dir=settings.output_dir,
        theme=theme,
        diagram_engine=settings.diagram_engine,
    )

    # Optional: write the final JSON spec used to generate the PPTX.
    # Helps verify whether you're using real AI output or the mock fallback.
    if os.getenv("SAVE_SPEC_JSON", "").strip() in {"1", "true", "yes", "on"}:
        try:
            spec_path = str(Path(output_path).with_suffix(".spec.json"))
            Path(spec_path).write_text(
                json.dumps(spec.model_dump(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

    return str(Path(output_path).resolve())
