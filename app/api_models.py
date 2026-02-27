from __future__ import annotations

from pydantic import BaseModel


class GenerateRequest(BaseModel):
    topic: str
    slides: int = 5
    theme: str = "Modern Minimal"


class SlideData(BaseModel):
    id: int
    type: str
    title: str
    content: str
    keywords: list[str] = []
    image_url: str | None = None


class PreviewResponse(BaseModel):
    presentation_id: str
    topic: str
    theme: str
    slides: list[SlideData]


class UpdateSlideRequest(BaseModel):
    title: str
    content: str


class ThemesResponse(BaseModel):
    themes: list[str]
