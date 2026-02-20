from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    # --- AI provider configuration ---
    # AI_PROVIDER can be: auto | gemini | openai
    ai_provider: str = os.getenv("AI_PROVIDER", "auto").strip().lower()

    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY") or None
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest")

    openai_api_key: str | None = os.getenv("OPENAI_API_KEY") or None
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    default_slide_count: int = int(os.getenv("DEFAULT_SLIDE_COUNT", "6"))

    # Images (Unsplash-only)
    unsplash_access_key: str | None = os.getenv("UNSPLASH_ACCESS_KEY") or None

    # --- Rendering / styling ---
    theme_name: str = os.getenv("THEME", "Education Light")
    # diagram_engine: svg | ppt (svg uses cairosvg; ppt uses python-pptx shapes)
    diagram_engine: str = os.getenv("DIAGRAM_ENGINE", "svg").strip().lower()

    output_dir: str = os.getenv("OUTPUT_DIR", "output")
    cache_dir: str = os.getenv("CACHE_DIR", "cache")


settings = Settings()
