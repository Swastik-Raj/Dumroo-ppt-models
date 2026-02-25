from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.ai.openai_client import generate_presentation_spec
from app.api_models import (
    GenerateRequest,
    PreviewResponse,
    SlideData,
    ThemesResponse,
    UpdateSlideRequest,
)
from app.config import settings
from app.planner import normalize_presentation_spec
from app.ppt.theme import available_themes
from app.storage import create_presentation, delete_presentation, get_presentation, update_slide as update_slide_storage

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/themes", response_model=ThemesResponse)
async def get_themes():
    return ThemesResponse(themes=available_themes())


@app.post("/api/generate/preview", response_model=PreviewResponse)
async def generate_preview(request: GenerateRequest):
    try:
        slide_count_final = request.slides or settings.default_slide_count

        spec_raw = generate_presentation_spec(
            topic=request.topic, slide_count=slide_count_final
        )
        spec = normalize_presentation_spec(
            spec_raw, topic=request.topic, slide_count=slide_count_final
        )

        slides_data = [
            {
                "id": idx,
                "type": slide.type,
                "title": slide.title,
                "content": slide.content,
                "keywords": slide.keywords,
                "image_url": None,
            }
            for idx, slide in enumerate(spec.slides)
        ]

        presentation_id = create_presentation(
            topic=request.topic,
            theme=request.theme,
            slides_data=slides_data
        )

        return PreviewResponse(
            presentation_id=presentation_id,
            topic=request.topic,
            theme=request.theme,
            slides=[SlideData(**slide) for slide in slides_data],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/presentation/{presentation_id}", response_model=PreviewResponse)
async def get_presentation_endpoint(presentation_id: str):
    try:
        data = get_presentation(presentation_id)

        if not data:
            raise HTTPException(status_code=404, detail="Presentation not found")

        return PreviewResponse(
            presentation_id=data["id"],
            topic=data["topic"],
            theme=data["theme"],
            slides=[SlideData(**slide) for slide in data["slides_data"]],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/presentation/{presentation_id}/slide/{slide_id}")
async def update_slide_endpoint(presentation_id: str, slide_id: int, update: UpdateSlideRequest):
    try:
        success = update_slide_storage(
            presentation_id=presentation_id,
            slide_id=slide_id,
            title=update.title,
            content=update.content
        )

        if not success:
            raise HTTPException(status_code=404, detail="Presentation or slide not found")

        return {"success": True}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/presentation/{presentation_id}/download")
async def download_presentation(presentation_id: str):
    try:
        data = get_presentation(presentation_id)

        if not data:
            raise HTTPException(status_code=404, detail="Presentation not found")

        from app.models import PresentationSpec, SlideSpec

        slides = [
            SlideSpec(
                type=slide["type"],
                title=slide["title"],
                content=slide["content"],
                keywords=slide["keywords"],
            )
            for slide in data["slides_data"]
        ]

        spec = PresentationSpec(title=data["topic"], slides=slides)

        from app.images.cache import ImageCache
        from app.images.unsplash import UnsplashImageSearch
        from app.planner import plan_slides
        from app.ppt.builder import build_pptx
        from app.ppt.theme import get_theme

        plans = plan_slides(spec)
        cache = ImageCache(base_dir=settings.cache_dir)

        image_search = None
        if settings.unsplash_access_key:
            image_search = UnsplashImageSearch(
                access_key=settings.unsplash_access_key, cache=cache
            )

        theme = get_theme(data["theme"])

        output_path = build_pptx(
            presentation_spec=spec,
            slide_plans=plans,
            image_search=image_search,
            output_dir=settings.output_dir,
            theme=theme,
            diagram_engine=settings.diagram_engine,
        )

        if not Path(output_path).exists():
            raise HTTPException(
                status_code=500, detail="Failed to generate presentation"
            )

        filename = f"{data['topic'].replace(' ', '_')}.pptx"

        delete_presentation(presentation_id)

        return FileResponse(
            path=output_path,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            filename=filename,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
