from __future__ import annotations

from dataclasses import dataclass

from pydantic import ValidationError

from app.models import PresentationSpec, SlideSpec


@dataclass(frozen=True)
class SlidePlan:
    layout: str
    image_query: str | None
    slide: SlideSpec


def _image_query_for_slide(slide: SlideSpec, deck_title: str) -> str:
    # If the model provided an explicit query, prefer it verbatim.
    explicit = (getattr(slide, "image_query", None) or "").strip()
    if explicit:
        return explicit

    # Build a tight query from structured image intent first.
    subject = (getattr(slide, "image_subject", None) or "").strip()
    setting = (getattr(slide, "image_setting", None) or "").strip()
    style = (getattr(slide, "image_style", None) or "").strip()
    structured = " ".join([s for s in [subject, setting, style] if s]).strip()
    if structured:
        return structured

    # Unsplash search performs poorly with overly long, brand-heavy queries.
    # Prefer slide-specific terms and a few keywords; avoid the deck title.
    base_terms = [slide.title, *slide.keywords]
    terms: list[str] = []
    seen: set[str] = set()
    for t in base_terms:
        t = (t or "").strip()
        if not t:
            continue
        key = t.lower()
        if key in seen:
            continue
        seen.add(key)
        terms.append(t)

    base = " ".join(terms[:6]).strip()

    if slide.type == "flow":
        return f"{base} workflow".strip()
    if slide.type == "process":
        return f"{base} business workflow".strip()
    if slide.type == "intro":
        return f"{base} abstract background".strip()
    return base


def normalize_presentation_spec(
    spec: PresentationSpec | None,
    *,
    topic: str,
    slide_count: int,
) -> PresentationSpec:
    """Make output predictable and slide-friendly even when the model drifts.

    - Ensures exactly `slide_count` slides
    - Ensures slide 1 is intro, last is summary
    - Ensures at least one flow slide with a basic diagram
    - Coerces process/summary content into newline bullets when possible
    """

    from app.ai.prompt import mock_presentation

    if spec is None:
        return PresentationSpec.model_validate(mock_presentation(topic, slide_count))

    slides = list(spec.slides or [])
    if not slides:
        return PresentationSpec.model_validate(mock_presentation(topic, slide_count))

    # Enforce count by truncating/padding with simple process slides.
    if len(slides) > slide_count:
        slides = slides[:slide_count]
    while len(slides) < slide_count:
        slides.append(
            SlideSpec(
                type="process",
                title=f"Step {len(slides)}",
                content="- Key point\n- Key point\n- Key point\n- Key point",
                keywords=[topic, "steps", "process", "overview"],
            )
        )

    # Slide 1 intro.
    if slides[0].type != "intro":
        slides[0] = slides[0].model_copy(update={"type": "intro"})

    # Last slide summary.
    if slides[-1].type != "summary":
        slides[-1] = slides[-1].model_copy(
            update={"type": "summary", "title": "Summary"})

    # Bullet coercion for process + summary.
    for i, s in enumerate(slides):
        if s.type not in ("process", "summary"):
            continue
        text = (s.content or "").strip()
        if not text:
            text = "- Key point\n- Key point\n- Key point\n- Key point"
        # If it's a paragraph, split into sentence-ish bullets.
        if "\n" not in text:
            parts = [p.strip()
                     for p in text.replace("•", "").split(".") if p.strip()]
            if len(parts) >= 2:
                text = "\n".join([f"- {p}" for p in parts[:6]])
            else:
                text = f"- {text}"
        # Ensure bullet prefix.
        lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
        fixed = []
        for ln in lines[:8]:
            if ln.startswith(("- ", "• ")):
                fixed.append(ln.replace("• ", "- "))
            else:
                fixed.append(f"- {ln}")
        slides[i] = s.model_copy(update={"content": "\n".join(fixed)})

    # Ensure at least one flow slide with a diagram.
    has_flow = any(s.type == "flow" and s.diagram is not None for s in slides)
    if not has_flow:
        mid = max(1, min(len(slides) - 2, len(slides) // 2))
        nodes = ["Input", "Step 1", "Step 2", "Output", "Result"]
        edges = [(nodes[i], nodes[i + 1]) for i in range(len(nodes) - 1)]
        slides[mid] = slides[mid].model_copy(
            update={
                "type": "flow",
                "title": "Process Flow",
                "diagram": {"nodes": nodes, "edges": edges},
            }
        )

    try:
        return PresentationSpec.model_validate({"title": spec.title or topic, "slides": [s.model_dump() for s in slides]})
    except ValidationError:
        return PresentationSpec.model_validate(mock_presentation(topic, slide_count))


def plan_slides(spec: PresentationSpec) -> list[SlidePlan]:
    plans: list[SlidePlan] = []

    for slide in spec.slides:
        if slide.type == "intro":
            layout = "title_full_image"
            image_query = _image_query_for_slide(slide, spec.title)
        elif slide.type == "process":
            layout = "image_left_text_right"
            image_query = _image_query_for_slide(slide, spec.title)
        elif slide.type == "flow":
            layout = "diagram_center"
            image_query = None  # diagram-first slide
        else:
            # Summary normally uses a clean bullets slide, but if the JSON
            # explicitly requests an image, honor it.
            requested = (getattr(slide, "image_query", None) or "").strip()
            if requested:
                layout = "image_left_text_right"
                image_query = requested
            else:
                layout = "bullets"
                image_query = None

        plans.append(
            SlidePlan(layout=layout, image_query=image_query, slide=slide))

    return plans
