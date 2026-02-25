from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.pipeline import generate_pptx_for_topic
from app.ppt.theme import available_themes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    topic: str
    slides: int = 5
    theme: str = "Education Light"


class ThemesResponse(BaseModel):
    themes: list[str]


@app.get("/api/themes", response_model=ThemesResponse)
async def get_themes():
    return ThemesResponse(themes=available_themes())


@app.post("/api/generate")
async def generate_presentation(request: GenerateRequest):
    try:
        output_path = generate_pptx_for_topic(
            topic=request.topic,
            slide_count=request.slides,
            theme_name=request.theme,
        )

        if not Path(output_path).exists():
            raise HTTPException(status_code=500, detail="Failed to generate presentation")

        filename = os.path.basename(output_path)

        return FileResponse(
            path=output_path,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            filename=filename,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
