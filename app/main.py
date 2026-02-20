from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.config import settings
from app.models import GenerateRequest
from app.pipeline import generate_pptx_for_topic

app = FastAPI(title="AI-Assisted PPT Generator")


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/generate")
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


@app.on_event("startup")
def _ensure_dirs() -> None:
    os.makedirs(settings.output_dir, exist_ok=True)
    os.makedirs(settings.cache_dir, exist_ok=True)
