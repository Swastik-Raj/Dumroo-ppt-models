from __future__ import annotations

from dataclasses import dataclass

from pydantic import ValidationError

from app.models import DiagramSpec, PresentationSpec, SlideSpec


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
    - Intelligently distributes content when slides need padding
    """

    print(f"\n[NORMALIZE] Starting normalization")
    print(f"[NORMALIZE] Target slide count: {slide_count}")

    from app.ai.prompt import mock_presentation

    if spec is None:
        print(f"[NORMALIZE] Spec is None, using mock")
        return PresentationSpec.model_validate(mock_presentation(topic, slide_count))

    slides = list(spec.slides or [])
    print(f"[NORMALIZE] Input slides count: {len(slides)}")
    if not slides:
        print(f"[NORMALIZE] No slides in spec, using mock")
        return PresentationSpec.model_validate(mock_presentation(topic, slide_count))

    # Enforce count by truncating/padding intelligently
    if len(slides) > slide_count:
        print(f"[NORMALIZE] Truncating from {len(slides)} to {slide_count}")
        slides = slides[:slide_count]

    # Smart padding: instead of generic slides, try to expand existing content
    print(f"[NORMALIZE] Current slides: {len(slides)}, need: {slide_count}")
    while len(slides) < slide_count:
        print(f"[NORMALIZE] Padding: {len(slides)}/{slide_count}")
        # Find process slides with lots of content that could be split
        splittable = None
        for i, s in enumerate(slides):
            if s.type == "process" and s.content:
                lines = [ln.strip() for ln in s.content.split("\n") if ln.strip()]
                if len(lines) > 6:  # More than 6 bullets can be split
                    splittable = i
                    break

        if splittable is not None:
            # Split this slide into two
            s = slides[splittable]
            lines = [ln.strip() for ln in s.content.split("\n") if ln.strip()]
            mid = len(lines) // 2
            first_half = "\n".join(lines[:mid])
            second_half = "\n".join(lines[mid:])

            slides[splittable] = s.model_copy(update={"content": first_half})
            slides.insert(splittable + 1, SlideSpec(
                type="process",
                title=f"{s.title} (cont.)",
                content=second_half,
                keywords=s.keywords,
            ))
        else:
            # Add a generic process slide
            slides.append(
                SlideSpec(
                    type="process",
                    title=f"Additional Points",
                    content="- Key point\n- Key point\n- Key point",
                    keywords=[topic, "overview"],
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

        # If it's a long paragraph (200+ chars, no newlines), try to intelligently split
        if "\n" not in text and len(text) > 200:
            # Try splitting on sentence boundaries
            parts = []
            for sentence in text.replace("•", "").split("."):
                sentence = sentence.strip()
                if not sentence:
                    continue
                # If sentence is still too long, try splitting on commas or semicolons
                if len(sentence) > 100:
                    subparts = [p.strip() for p in sentence.replace(";", ",").split(",") if p.strip()]
                    parts.extend(subparts[:3])  # Take first 3 parts
                else:
                    parts.append(sentence)
            if parts:
                text = "\n".join([f"- {p}" for p in parts[:8]])
            else:
                text = f"- {text[:80]}"  # Truncate if all else fails

        # If it's a short paragraph, split into sentences
        elif "\n" not in text and len(text) > 0:
            parts = [p.strip() for p in text.replace("•", "").split(".") if p.strip()]
            if len(parts) >= 2:
                text = "\n".join([f"- {p}" for p in parts[:8]])
            else:
                text = f"- {text}"

        # Ensure bullet prefix and clean up
        lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
        fixed = []
        for ln in lines[:10]:  # Allow up to 10 bullets, layouts will handle sizing
            if ln.startswith(("- ", "• ")):
                cleaned = ln.replace("• ", "- ")
                # Truncate overly long bullets
                if len(cleaned) > 120:
                    cleaned = cleaned[:117] + "..."
                fixed.append(cleaned)
            else:
                # Add bullet prefix and truncate if needed
                if len(ln) > 120:
                    ln = ln[:117] + "..."
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
                "diagram": DiagramSpec(nodes=nodes, edges=edges),
            }
        )

    try:
        print(f"[NORMALIZE] Final slide count: {len(slides)}")
        print(f"[NORMALIZE] Slide types: {[s.type for s in slides]}")
        result = PresentationSpec.model_validate({"title": spec.title or topic, "slides": [s.model_dump() for s in slides]})
        print(f"[NORMALIZE] Validation successful")
        return result
    except ValidationError as e:
        print(f"[NORMALIZE] Validation failed: {e}")
        return PresentationSpec.model_validate(mock_presentation(topic, slide_count))


def plan_slides(spec: PresentationSpec) -> list[SlidePlan]:
    print(f"\n[PLAN] Planning slides for {len(spec.slides)} slides")
    plans: list[SlidePlan] = []

    for i, slide in enumerate(spec.slides):
        print(f"[PLAN] Slide {i+1}: {slide.title} (type: {slide.type})")
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
