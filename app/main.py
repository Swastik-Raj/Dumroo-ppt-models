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
    return {"themes": available_themes()}


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
        pptx_path = generate_pptx_for_topic(
            topic=req.topic, slide_count=req.slide_count, theme_name=req.theme)

        presentation_id = str(uuid.uuid4())
        presentations_store[presentation_id] = pptx_path

        slides = []
        for i in range(req.slide_count or 5):
            slides.append({
                "id": i + 1,
                "type": "content" if i > 0 else "intro",
                "title": f"Slide {i + 1}",
                "content": "Generated content",
                "keywords": [],
                "image_url": None
            })

        return {
            "presentation_id": presentation_id,
            "topic": req.topic,
            "theme": req.theme or "Modern Minimal",
            "slides": slides
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/presentation/{presentation_id}/download")
def download_presentation(presentation_id: str) -> FileResponse:
    if presentation_id not in presentations_store:
        raise HTTPException(status_code=404, detail="Presentation not found")

    pptx_path = presentations_store[presentation_id]
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
