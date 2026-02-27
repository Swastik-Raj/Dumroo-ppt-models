from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DesignTemplate:
    name: str
    description: str
    color_palette: list[str]
    use_case: str
    style: str


DESIGN_TEMPLATES: dict[str, DesignTemplate] = {
    "Modern Minimal": DesignTemplate(
        name="Modern Minimal",
        description="Clean, sophisticated design with black and white aesthetics",
        color_palette=["#1A1A1A", "#4A4A4A", "#FFFFFF", "#0A0A0A", "#F8F8F8"],
        use_case="Professional presentations, portfolio showcases, minimalist designs",
        style="Minimalist"
    ),
    "Bold & Vibrant": DesignTemplate(
        name="Bold & Vibrant",
        description="Eye-catching design with bright, energetic colors",
        color_palette=["#FF6B6B", "#4ECDC4", "#FFE66D", "#2D3436", "#FFFFFF"],
        use_case="Creative pitches, marketing presentations, youth-oriented content",
        style="Vibrant"
    ),
    "Corporate Professional": DesignTemplate(
        name="Corporate Professional",
        description="Traditional business aesthetic with blue tones",
        color_palette=["#003B5C", "#0066A1", "#E8F4F8", "#333333", "#FFFFFF"],
        use_case="Business reports, corporate meetings, investor presentations",
        style="Corporate"
    ),
    "Creative Gradient": DesignTemplate(
        name="Creative Gradient",
        description="Modern design with gradient accents and vibrant colors",
        color_palette=["#6C5CE7", "#00B894", "#DFE6E9", "#2D3436", "#FFFFFF"],
        use_case="Tech startups, creative agencies, innovative product launches",
        style="Modern"
    ),
    "Dark Mode Elegant": DesignTemplate(
        name="Dark Mode Elegant",
        description="Sophisticated dark theme with gold accents",
        color_palette=["#1A1A1A", "#FFD700", "#FFFFFF", "#B2B2B2", "#2A2A2A"],
        use_case="Tech presentations, evening events, luxury product showcases",
        style="Elegant"
    ),
    "Ocean Blue": DesignTemplate(
        name="Ocean Blue",
        description="Calming blue tones inspired by ocean depths",
        color_palette=["#0C4A6E", "#0EA5E9", "#E0F2FE", "#334155", "#FFFFFF"],
        use_case="Healthcare, wellness, environmental presentations",
        style="Calm"
    ),
    "Warm Sunset": DesignTemplate(
        name="Warm Sunset",
        description="Warm orange and amber tones with cream background",
        color_palette=["#7C2D12", "#F97316", "#FED7AA", "#FFFBEB", "#44403C"],
        use_case="Food & beverage, hospitality, warm brand presentations",
        style="Warm"
    ),
    "Fresh Green": DesignTemplate(
        name="Fresh Green",
        description="Natural green tones promoting growth and sustainability",
        color_palette=["#14532D", "#22C55E", "#DCFCE7", "#374151", "#FFFFFF"],
        use_case="Environmental, sustainability, organic product presentations",
        style="Natural"
    ),
    "Soft Pastel": DesignTemplate(
        name="Soft Pastel",
        description="Gentle pastel colors with lavender accents",
        color_palette=["#5B21B6", "#A855F7", "#E9D5FF", "#FAF5FF", "#4B5563"],
        use_case="Beauty, fashion, lifestyle brand presentations",
        style="Soft"
    ),
    "Tech Startup": DesignTemplate(
        name="Tech Startup",
        description="Modern tech aesthetic with blue and gray tones",
        color_palette=["#1E293B", "#3B82F6", "#DBEAFE", "#F8FAFC", "#475569"],
        use_case="Tech companies, SaaS presentations, startup pitches",
        style="Tech"
    ),
}


def get_template_info(theme_name: str) -> DesignTemplate | None:
    return DESIGN_TEMPLATES.get(theme_name)


def get_all_templates() -> list[dict]:
    return [
        {
            "name": template.name,
            "description": template.description,
            "style": template.style,
            "use_case": template.use_case,
            "color_palette": template.color_palette,
        }
        for template in DESIGN_TEMPLATES.values()
    ]
