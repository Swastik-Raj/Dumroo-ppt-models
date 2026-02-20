from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class DiagramSpec(BaseModel):
    nodes: list[str] = Field(min_length=1)
    edges: list[tuple[str, str]] = Field(default_factory=list)


SlideType = Literal["intro", "process", "flow", "summary"]


class SlideSpec(BaseModel):
    type: SlideType
    title: str
    content: str
    keywords: list[str] = Field(default_factory=list)
    # Optional: explicit image query/alt text controlled by the JSON.
    # If not provided, the planner will derive a query from title/keywords.
    image_query: str | None = None
    image_alt: str | None = None
    # Optional: structured image intent to improve search relevance.
    image_subject: str | None = None
    image_setting: str | None = None
    image_style: str | None = None
    # Optional: layout preference override (if AI wants a specific layout)
    layout_preference: str | None = None
    # Optional: visual emphasis (affects font sizes, spacing)
    emphasis: str | None = None  # "high", "medium", "low"
    diagram: DiagramSpec | None = None


class PresentationSpec(BaseModel):
    title: str
    slides: list[SlideSpec] = Field(min_length=1)


class GenerateRequest(BaseModel):
    topic: str = Field(min_length=2)
    slide_count: int | None = Field(default=None, ge=3, le=15)
    theme: str | None = Field(
        default=None, description="Optional theme preset name")


class GenerateResponse(BaseModel):
    pptx_path: str
