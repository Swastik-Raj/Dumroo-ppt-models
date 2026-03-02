from __future__ import annotations

import os
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.config import settings
from app.models import GenerateRequest
from app.pipeline import generate_pptx_for_topic
from app.ppt.theme import available_themes
from app.templates import get_all_templates

app = FastAPI(title="AI-Assisted PPT Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

presentations_store = {}


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.get("/api/themes")
def get_themes() -> dict:
    from app.ppt.theme import THEME_PRESETS

    themes_with_details = []
    for theme_name in available_themes():
        theme = THEME_PRESETS.get(theme_name)
        if theme:
            themes_with_details.append({
                "name": theme.name,
                "title_color": f"rgb({theme.title_rgb[0]}, {theme.title_rgb[1]}, {theme.title_rgb[2]})",
                "background_color": f"rgb({theme.background_rgb[0]}, {theme.background_rgb[1]}, {theme.background_rgb[2]})",
                "accent_color": f"rgb({theme.accent_rgb[0]}, {theme.accent_rgb[1]}, {theme.accent_rgb[2]})",
            })

    return {"themes": themes_with_details}


@app.get("/api/templates")
def get_templates() -> dict:
    return {"templates": get_all_templates()}


@app.post("/api/generate")
def generate(req: GenerateRequest) -> FileResponse:
    pptx_path = generate_pptx_for_topic(
        topic=req.topic, slide_count=req.slide_count, theme_name=req.theme)

    path = Path(pptx_path)
    filename = path.name
    return FileResponse(
        path=str(path),
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=filename,
    )


@app.post("/api/generate/preview")
def generate_preview(req: GenerateRequest) -> dict:
    try:
        from app.ai.openai_client import generate_presentation_spec
        from app.planner import normalize_presentation_spec
        from app.config import settings

        print(f"[DEBUG] Generating preview for topic: {req.topic[:50]}...")
        print(f"[DEBUG] Slide count: {req.slide_count}, Theme: {req.theme}")

        slide_count_final = req.slide_count or settings.default_slide_count

        spec_raw = generate_presentation_spec(
            topic=req.topic, slide_count=slide_count_final)
        spec = normalize_presentation_spec(
            spec_raw, topic=req.topic, slide_count=slide_count_final)

        print(f"[DEBUG] Generated spec with title: {spec.title}")
        print(f"[DEBUG] Number of slides in spec: {len(spec.slides)}")

        pptx_path = generate_pptx_for_topic(
            topic=req.topic, slide_count=req.slide_count, theme_name=req.theme)

        print(f"[DEBUG] PPTX generated at: {pptx_path}")

        presentation_id = str(uuid.uuid4())
        presentations_store[presentation_id] = {
            "path": pptx_path,
            "spec": spec
        }

        slides = []
        for i, slide_spec in enumerate(spec.slides):
            print(f"[DEBUG] Slide {i+1}: {slide_spec.title} ({slide_spec.type})")
            slides.append({
                "id": i + 1,
                "type": slide_spec.type,
                "title": slide_spec.title,
                "content": slide_spec.content,
                "keywords": slide_spec.keywords,
                "image_url": None
            })

        response_data = {
            "presentation_id": presentation_id,
            "topic": spec.title,
            "theme": req.theme or "Modern Minimal",
            "slides": slides
        }

        print(f"[DEBUG] Returning response with {len(slides)} slides")
        return response_data
    except Exception as e:
        import traceback
        print(f"[ERROR] Exception in generate_preview: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/presentation/{presentation_id}/download")
def download_presentation(presentation_id: str) -> FileResponse:
    if presentation_id not in presentations_store:
        raise HTTPException(status_code=404, detail="Presentation not found")

    stored = presentations_store[presentation_id]

    if isinstance(stored, dict):
        pptx_path = stored["path"]
    else:
        pptx_path = stored

    path = Path(pptx_path)

    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    filename = path.name
    return FileResponse(
        path=str(path),
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=filename,
    )


@app.on_event("startup")
def _ensure_dirs() -> None:
    os.makedirs(settings.output_dir, exist_ok=True)
    os.makedirs(settings.cache_dir, exist_ok=True)
