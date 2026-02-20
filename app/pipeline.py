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


def generate_pptx_for_topic(topic: str, slide_count: int | None, *, theme_name: str | None = None) -> str:
    slide_count_final = slide_count or settings.default_slide_count

    spec_raw = generate_presentation_spec(
        topic=topic, slide_count=slide_count_final)
    spec = normalize_presentation_spec(
        spec_raw, topic=topic, slide_count=slide_count_final)

    plans = plan_slides(spec)

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
