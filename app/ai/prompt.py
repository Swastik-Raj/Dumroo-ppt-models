from __future__ import annotations


def system_prompt() -> str:
    return (
        "You are a slide-content engine. "
        "Return ONLY valid JSON. "
        "No markdown, no extra keys, no commentary."
    )


def user_prompt(topic: str, slide_count: int) -> str:
    # Adaptive instruction based on topic domain
    domain_hints = _detect_domain_hints(topic)

    return f"""
Create a slide deck about: {topic}

{domain_hints}

Constraints:
- Output MUST be valid JSON matching this shape:
  {{
    "title": string,
    "slides": [
      {{
        "type": "intro"|"process"|"flow"|"summary",
        "title": string,
        "content": string,
        "keywords": string[],
        "image_query"?: string,
        "image_alt"?: string,
        "image_subject"?: string,
        "image_setting"?: string,
        "image_style"?: string,
        "layout_preference"?: "image_left"|"bullets"|"title_full_image",
        "emphasis"?: "high"|"medium"|"low",
        "diagram"?: {{
          "nodes": string[],
          "edges": [ [string,string], ... ]
        }}
      }},
      ...
    ]
  }}
- Use exactly {slide_count} slides.

Content rules (VERY IMPORTANT):
- Titles must be short (3–7 words) and specific.
- For type "intro": 1–2 sentences, plain text.
- For type "process": write 4–6 bullet points as newline-separated lines (no paragraphs). Example:
    "content": "- Bullet 1\n- Bullet 2\n- Bullet 3"
- For type "summary": write 4–6 bullet points as newline-separated lines (no paragraphs).

Image rules (VERY IMPORTANT):
- For every slide except the flow diagram slide, include an `image_query` optimized for Unsplash (3–8 words).
- `image_query` must describe a real photo subject (avoid brand names, avoid long phrases).
- Include `image_alt` as a short description of what the image should show.
- If the topic is abstract, use photo-friendly subjects ("team onboarding", "office workflow", "customer signup").
- Also include structured fields to improve relevance:
    - `image_subject`: the main subject (e.g., "Indian independence march")
    - `image_setting`: the setting/context (e.g., "historic street rally")
    - `image_style`: style cue (e.g., "archival photo", "documentary")

Diagram rules (VERY IMPORTANT):
- Include at least 1 slide of type "flow".
- For the flow slide: nodes must be 5–8 items and represent the real steps/components in order.
- Edges must show direction and mostly be a left-to-right chain (A->B->C...).
- If there is a branch, add at most one branch from a single node.

Keywords rules:
- Provide 4–8 keywords per slide.

Ordering rules:
- Slide 1 must be type "intro".
- Slide {slide_count} must be type "summary".
""".strip()


def _detect_domain_hints(topic: str) -> str:
    """Generate adaptive instructions based on topic domain."""
    topic_lower = topic.lower()

    # Historical/events
    if any(word in topic_lower for word in ["history", "war", "independence", "revolution", "invention", "discovery"]):
        return (
            "Domain: Historical/Documentary\n"
            "- Use archival, vintage, or historical imagery\n"
            "- Include specific dates and key figures in content\n"
            "- For flow diagrams, show chronological progression\n"
            "- Image style should be 'archival', 'vintage', 'documentary', 'sepia'"
        )

    # Business/corporate
    elif any(word in topic_lower for word in ["business", "strategy", "management", "corporate", "onboarding", "process"]):
        return (
            "Domain: Business/Corporate\n"
            "- Use professional office, team, meeting imagery\n"
            "- Content should be action-oriented with clear steps\n"
            "- For flow diagrams, show workflow/process stages\n"
            "- Image style should be 'professional', 'modern office', 'corporate'"
        )

    # Technology/science
    elif any(word in topic_lower for word in ["technology", "science", "innovation", "ai", "software", "programming", "data"]):
        return (
            "Domain: Technology/Science\n"
            "- Use futuristic, tech, code, circuit, lab imagery\n"
            "- Content should be technical yet accessible\n"
            "- For flow diagrams, show system architecture or data flow\n"
            "- Image style should be 'modern', 'digital', 'futuristic', 'tech'"
        )

    # Education/learning
    elif any(word in topic_lower for word in ["education", "learning", "teaching", "training", "course", "study"]):
        return (
            "Domain: Education/Learning\n"
            "- Use classroom, books, students, learning imagery\n"
            "- Content should be pedagogical with clear explanations\n"
            "- For flow diagrams, show learning journey or concept map\n"
            "- Image style should be 'educational', 'bright', 'engaging'"
        )

    # Nature/environment
    elif any(word in topic_lower for word in ["nature", "environment", "climate", "ecosystem", "biology", "photosynthesis"]):
        return (
            "Domain: Nature/Environment\n"
            "- Use natural landscapes, plants, wildlife imagery\n"
            "- Content should explain natural processes clearly\n"
            "- For flow diagrams, show ecological cycles or processes\n"
            "- Image style should be 'natural', 'organic', 'vibrant', 'documentary'"
        )

    # Default
    else:
        return (
            "Domain: General\n"
            "- Use relevant, high-quality imagery that matches the topic\n"
            "- Content should be clear and well-structured\n"
            "- For flow diagrams, show logical progression\n"
            "- Image style should be appropriate to the subject matter"
        )


def mock_presentation(topic: str, slide_count: int) -> dict:
    # Deterministic fallback for local testing without any API key.
    slides = [
        {
            "type": "intro",
            "title": f"{topic}",
            "content": f"An overview of {topic} and why it matters.",
            "keywords": [topic, "overview"],
        },
        {
            "type": "process",
            "title": "Core Components",
            "content": "Identify inputs, steps, and outputs. Then connect them logically.",
            "keywords": ["inputs", "steps", "outputs"],
        },
        {
            "type": "flow",
            "title": "End-to-End Flow",
            "content": "A simple flow diagram showing how the process moves from start to finish.",
            "keywords": ["flow", "diagram"],
            "diagram": {
                "nodes": ["Start", "Input", "Process", "Decision", "Output", "End"],
                "edges": [
                    ["Start", "Input"],
                    ["Input", "Process"],
                    ["Process", "Decision"],
                    ["Decision", "Output"],
                    ["Output", "End"],
                ],
            },
        },
    ]

    while len(slides) < max(slide_count - 1, 3):
        slides.append(
            {
                "type": "process",
                "title": f"Step {len(slides)}",
                "content": "Explain one key step with a clear takeaway.",
                "keywords": ["step", "takeaway"],
            }
        )

    slides.append(
        {
            "type": "summary",
            "title": "Summary",
            "content": "Key takeaways and what to remember.",
            "keywords": ["summary", "recap"],
        }
    )

    return {"title": topic, "slides": slides[:slide_count]}
