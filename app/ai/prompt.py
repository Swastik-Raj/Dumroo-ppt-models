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

    # Count paragraphs/sections to detect long input
    topic_length = len(topic)
    sections = topic.count('\n\n') + topic.count('**') + topic.count('##')
    paragraphs = len([p for p in topic.split('\n\n') if len(p.strip()) > 50])
    is_long_input = topic_length > 500 or sections > 3 or paragraphs > 4

    # Different approach for short vs long inputs
    if is_long_input:
        # For detailed lesson plans or long content
        return f"""
You are creating a {slide_count}-slide presentation from the following detailed content:

{topic}

{domain_hints}

CRITICAL INSTRUCTIONS - READ CAREFULLY:
This is a LONG, structured input. You MUST extract content properly:

1. READ THE ENTIRE INPUT FIRST - understand all sections before creating slides
2. IDENTIFY distinct sections/activities/topics in the content
3. CREATE ONE SLIDE per major section - DO NOT skip sections
4. DISTRIBUTE content evenly across all {slide_count} slides
5. Each slide should have 3-5 focused bullet points (max 80 chars each)
6. If a section has too much content, split it across 2 slides

SLIDE STRUCTURE for {slide_count} slides:
- Slide 1 (intro): Main title and overview
- Slides 2 to {slide_count-2}: One slide per major section/activity/concept
- Slide {slide_count-1} (flow): Process diagram showing the overall flow
- Slide {slide_count} (summary): Key takeaways

{_get_json_format_rules(slide_count)}
"""
    else:
        # For short topics (1-2 sentences or single concept)
        return f"""
You are creating a {slide_count}-slide educational presentation about:

{topic}

{domain_hints}

INSTRUCTIONS:
Create a comprehensive, educational slide deck that teaches this topic from scratch.

CONTENT STRATEGY:
- Slide 1 (intro): Define the topic and why it's important
- Slides 2-4: Break down the topic into key concepts/components (one concept per slide)
- Slide 5: How it works or real-world examples
- Middle slides: Deep dive into important aspects, processes, or applications
- Slide {slide_count-1} (flow): Create a diagram showing the process/system/cycle
- Slide {slide_count} (summary): Key takeaways and main points

CONTENT QUALITY:
- Be informative and educational - teach the audience about this topic
- Use specific, factual information (not generic statements)
- Each slide should cover ONE clear concept or idea
- Include 3-5 bullet points per slide (each 60-80 characters)
- Make content engaging and easy to understand
- Build logically from basic concepts to more advanced ideas

EXAMPLES OF GOOD CONTENT:
"Photosynthesis converts light energy into chemical energy"
"Chloroplasts contain chlorophyll which captures sunlight"
"Products: glucose (C6H12O6) and oxygen (O2)"

EXAMPLES OF BAD CONTENT:
"Important process in plants"
"Key concept to understand"
"Main topic of discussion"

{_get_json_format_rules(slide_count)}
"""


def _get_json_format_rules(slide_count: int) -> str:
    return f"""

JSON OUTPUT FORMAT - CRITICAL:
Return ONLY valid JSON. No markdown, no commentary. Must match this structure:
{{
  "title": "Presentation Title (4-8 words)",
  "slides": [
    {{
      "type": "intro"|"process"|"flow"|"summary",
      "title": "Slide Title (3-7 words, max 60 chars)",
      "content": "Content (see formatting rules below)",
      "keywords": ["keyword1", "keyword2", "keyword3", "keyword4"],
      "image_query": "photo search query (3-8 words)",
      "image_subject": "main subject",
      "image_setting": "context/setting",
      "image_style": "style cue",
      "diagram": {{ "nodes": [...], "edges": [[...]] }}
    }}
  ]
}}

SLIDE COUNT: Create exactly {slide_count} slides.

SLIDE TYPE REQUIREMENTS:
- Slide 1: MUST be type "intro"
- Slide {slide_count}: MUST be type "summary"
- At least 1 slide: MUST be type "flow" with a diagram (usually slide {slide_count-1})
- All other slides: type "process"

CONTENT FORMATTING BY TYPE:

1. type "intro":
   - Write 1-2 short sentences in plain text
   - NO bullet points
   - Maximum 200 characters total
   - Example: "Machine learning enables computers to learn from data without explicit programming. It powers modern AI applications."

2. type "process":
   - Write 3-5 bullet points
   - Each bullet starts with "- "
   - Newline-separated (use \\n)
   - Each bullet 60-80 characters max
   - Be specific and informative, not generic
   - Example: "- Algorithms learn patterns from training data\\n- Models improve accuracy through iteration\\n- Applications: recommendation systems, image recognition\\n- Requires large datasets for best results"

3. type "summary":
   - Write 3-5 bullet points (same format as process)
   - Summarize key takeaways
   - Example: "- Machine learning automates pattern recognition\\n- Three main types: supervised, unsupervised, reinforcement\\n- Powers modern AI applications\\n- Requires quality data and careful validation"

4. type "flow":
   - MUST include a diagram object
   - Content can be brief or empty
   - The diagram tells the story

DIAGRAM REQUIREMENTS (for type "flow"):
- Must have 4-6 nodes representing steps/components
- Node names: SHORT (1-3 words, max 25 chars)
- Edges: Array of [source, destination] pairs showing flow
- Create logical left-to-right progression
- Example for machine learning:
  {{
    "nodes": ["Raw Data", "Training", "Model", "Predictions", "Validation"],
    "edges": [["Raw Data", "Training"], ["Training", "Model"], ["Model", "Predictions"], ["Predictions", "Validation"], ["Validation", "Training"]]
  }}

IMAGE REQUIREMENTS (all slides except flow):
- image_query: 3-8 words, photo-friendly (e.g., "artificial intelligence neural network")
- image_subject: main subject (e.g., "computer circuit board")
- image_setting: context (e.g., "technology lab")
- image_style: style (e.g., "modern digital")
- Avoid brand names and abstract concepts

TITLE REQUIREMENTS:
- Presentation title: 4-8 words, engaging and descriptive
- Slide titles: 3-7 words, max 60 characters
- Be specific: "Neural Network Architecture" not "Overview"

KEYWORDS:
- 4-8 relevant keywords per slide
- Use specific terms related to the content

QUALITY STANDARDS:
DO: Use specific, factual, educational content
DO: Make each slide cover ONE clear concept
DO: Build logically from basics to advanced
DO: Use all {slide_count} slides effectively

DON'T: Use generic phrases like "important concept"
DON'T: Put more than 5 bullets on one slide
DON'T: Leave slides empty or underutilized
DON'T: Create vague or unclear content
""".strip()


def _detect_domain_hints(topic: str) -> str:
    """Generate adaptive instructions based on topic domain."""
    topic_lower = topic.lower()

    # Lesson plan detection
    if any(word in topic_lower for word in ["lesson plan", "learning objective", "students will", "grade", "curriculum", "classroom", "homework", "engage", "explore", "explain", "elaborate", "evaluate"]):
        return (
            "Domain: Education/Lesson Plan\n"
            "CRITICAL INSTRUCTIONS FOR LESSON PLANS - READ CAREFULLY:\n\n"
            "PARSING STRATEGY:\n"
            "1. First, read through the ENTIRE lesson plan from start to finish\n"
            "2. Identify all distinct sections: Engage, Explore, Explain, Elaborate, Evaluate, Materials, Objectives, Activities, etc.\n"
            "3. Count how many distinct sections/activities exist\n"
            "4. Allocate slides: 1 intro + (N sections/activities) + 1 flow diagram + 1 summary\n\n"
            "SLIDE BREAKDOWN RULES:\n"
            "- Slide 1 (intro): Main lesson topic and grade level\n"
            "- Slide 2 (process): Learning objectives ONLY (3-5 bullets)\n"
            "- Slide 3+ (process): ONE slide for EACH major activity/section:\n"
            "  * 'Engage Activity' → extract engage content (3-5 bullets)\n"
            "  * 'Explore Activity' → extract explore content (3-5 bullets)\n"
            "  * 'Explain Phase' → extract explain content (3-5 bullets)\n"
            "  * 'Elaborate Activity' → extract elaborate content (3-5 bullets)\n"
            "  * 'Evaluate Assessment' → extract evaluation methods (3-5 bullets)\n"
            "  * If materials are extensive, create 'Required Materials' slide\n"
            "  * If vocabulary is present, create 'Key Vocabulary' slide\n"
            "- Second-to-last slide (flow): Show lesson flow as a diagram (Engage→Explore→Explain→Elaborate→Evaluate)\n"
            "- Last slide (summary): Key takeaways and learning outcomes\n\n"
            "CONTENT EXTRACTION:\n"
            "- For each section, extract the MAIN POINTS only\n"
            "- Convert long paragraphs into 3-5 concise bullet points\n"
            "- Remove filler words and teacher instructions\n"
            "- Focus on what students will DO and LEARN\n"
            "- Keep each bullet under 80 characters\n\n"
            "TITLES:\n"
            "- Use action-oriented titles: 'Engage: Hook Activity', 'Explore: Hands-On Investigation'\n"
            "- NOT generic titles like 'Section 1' or 'Part 2'\n\n"
            "IMAGES:\n"
            "- Use educational imagery: 'students learning', 'classroom activity', 'hands-on science experiment'\n"
            "- Image style: 'educational', 'bright', 'engaging', 'classroom', 'students'\n\n"
            "NEVER DO THIS:\n"
            "- Put entire lesson plan in one slide\n"
            "- Create slides with more than 5 bullets\n"
            "- Combine multiple activities into one slide\n"
            "- Use generic titles like 'Content' or 'Information'\n\n"
            "ALWAYS DO THIS:\n"
            "- One distinct section/activity = One slide\n"
            "- Clear, specific titles for each slide\n"
            "- Concise bullet points (not paragraphs)\n"
            "- Use all {slide_count} slides efficiently"
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
