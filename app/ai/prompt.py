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
Analyze the following content and create a professional slide deck. The content may be a topic, lesson plan, course material, or detailed text:

{topic}

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
- Analyze the provided content carefully and extract ONLY the most important points
- CRITICAL: If the input is very long (lesson plan, detailed text, etc.), YOU MUST break it down into multiple distinct slides
- DO NOT put large blocks of text into a single slide
- Extract key concepts, activities, and objectives and distribute them across slides
- Each slide should focus on ONE main idea or concept
- If the content is a lesson plan with multiple sections (Engage, Explore, Explain, etc.), create a separate slide for EACH section
- If there are multiple activities or steps, create a separate slide for EACH activity/step
- Titles must be short (3–7 words) and specific. Maximum 60 characters.
- For type "intro": 1–2 sentences, plain text. Maximum 200 characters total.
- For type "process": write 3–5 bullet points as newline-separated lines (no paragraphs). Each bullet maximum 80 characters. Example:
    "content": "- Brief point 1\n- Brief point 2\n- Brief point 3"
- For type "summary": write 3–5 bullet points as newline-separated lines (no paragraphs). Each bullet maximum 80 characters.
- Keep all content concise and readable. If text is too long, SPLIT IT into multiple slides instead.
- Preserve key information from the original content while making it presentation-friendly
- REMEMBER: More slides with focused content is BETTER than fewer slides with too much text

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
- For the flow slide: nodes must be 4–6 items and represent the real steps/components in order.
- Node names must be SHORT (1-3 words, max 25 characters each).
- Edges must show direction and mostly be a left-to-right chain (A->B->C...).
- Edges format: [["Node1", "Node2"], ["Node2", "Node3"], ...]
- Each edge array must have exactly 2 elements (source and destination).
- If there is a branch, add at most one branch from a single node.
- Example diagram:
  {{
    "nodes": ["Input", "Process", "Validate", "Output"],
    "edges": [["Input", "Process"], ["Process", "Validate"], ["Validate", "Output"]]
  }}

Keywords rules:
- Provide 4–8 keywords per slide.

Ordering rules:
- Slide 1 must be type "intro".
- Slide {slide_count} must be type "summary".
""".strip()


def _detect_domain_hints(topic: str) -> str:
    """Generate adaptive instructions based on topic domain."""
    topic_lower = topic.lower()

    # Lesson plan detection
    if any(word in topic_lower for word in ["lesson plan", "learning objective", "students will", "grade", "curriculum", "classroom", "homework", "engage", "explore", "explain", "elaborate", "evaluate"]):
        return (
            "Domain: Education/Lesson Plan\n"
            "CRITICAL INSTRUCTIONS FOR LESSON PLANS:\n"
            "- DO NOT create one slide with all the lesson plan text\n"
            "- Create SEPARATE slides for EACH major section (Engage, Explore, Explain, Elaborate, Evaluate, etc.)\n"
            "- If there are multiple activities, create ONE slide per activity\n"
            "- Extract the main concept/topic for the intro slide\n"
            "- Create individual slides for:\n"
            "  * Learning objectives (1 slide with 3-5 bullet points)\n"
            "  * Each activity or lesson phase (1 slide each)\n"
            "  * Key vocabulary or concepts (1 slide)\n"
            "  * Assessment or evaluation (1 slide)\n"
            "- Each slide should have a clear, focused title like 'Engage Activity', 'Core Concepts', 'Practice Exercise'\n"
            "- Keep bullet points short and actionable\n"
            "- Use educational imagery (classroom, students, books, learning)\n"
            "- For flow diagrams, show the lesson progression or concept relationships\n"
            "- Image style should be 'educational', 'bright', 'engaging', 'classroom'"
        )

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
