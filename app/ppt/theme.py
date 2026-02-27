from __future__ import annotations

from dataclasses import dataclass


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    v = value.strip().lstrip("#")
    if len(v) != 6:
        raise ValueError(f"Invalid hex color: {value}")
    return (int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16))


@dataclass(frozen=True)
class Theme:
    name: str = "Education Light"
    font_title: str = "Calibri"
    font_body: str = "Calibri"
    title_rgb: tuple[int, int, int] = (31, 78, 121)
    body_rgb: tuple[int, int, int] = (51, 51, 51)
    background_rgb: tuple[int, int, int] = (255, 255, 255)
    accent_rgb: tuple[int, int, int] = (56, 189, 248)

    # Diagram styling (used by both PPT-shape and SVG diagram engines)
    diagram_node_fill_rgb: tuple[int, int, int] = (234, 242, 255)
    diagram_node_line_rgb: tuple[int, int, int] = (79, 129, 189)
    diagram_text_rgb: tuple[int, int, int] = (31, 55, 94)


THEME_PRESETS: dict[str, Theme] = {
    "Modern Minimal": Theme(
        name="Modern Minimal",
        font_title="Calibri",
        font_body="Calibri",
        title_rgb=_hex_to_rgb("#1A1A1A"),
        body_rgb=_hex_to_rgb("#4A4A4A"),
        background_rgb=_hex_to_rgb("#FFFFFF"),
        accent_rgb=_hex_to_rgb("#0A0A0A"),
        diagram_node_fill_rgb=_hex_to_rgb("#F8F8F8"),
        diagram_node_line_rgb=_hex_to_rgb("#1A1A1A"),
        diagram_text_rgb=_hex_to_rgb("#1A1A1A"),
    ),
    "Bold & Vibrant": Theme(
        name="Bold & Vibrant",
        font_title="Calibri",
        font_body="Calibri",
        title_rgb=_hex_to_rgb("#FF6B6B"),
        body_rgb=_hex_to_rgb("#2D3436"),
        background_rgb=_hex_to_rgb("#FFFFFF"),
        accent_rgb=_hex_to_rgb("#4ECDC4"),
        diagram_node_fill_rgb=_hex_to_rgb("#FFE66D"),
        diagram_node_line_rgb=_hex_to_rgb("#FF6B6B"),
        diagram_text_rgb=_hex_to_rgb("#2D3436"),
    ),
    "Corporate Professional": Theme(
        name="Corporate Professional",
        font_title="Calibri",
        font_body="Calibri",
        title_rgb=_hex_to_rgb("#003B5C"),
        body_rgb=_hex_to_rgb("#333333"),
        background_rgb=_hex_to_rgb("#FFFFFF"),
        accent_rgb=_hex_to_rgb("#0066A1"),
        diagram_node_fill_rgb=_hex_to_rgb("#E8F4F8"),
        diagram_node_line_rgb=_hex_to_rgb("#0066A1"),
        diagram_text_rgb=_hex_to_rgb("#003B5C"),
    ),
    "Creative Gradient": Theme(
        name="Creative Gradient",
        font_title="Calibri",
        font_body="Calibri",
        title_rgb=_hex_to_rgb("#6C5CE7"),
        body_rgb=_hex_to_rgb("#2D3436"),
        background_rgb=_hex_to_rgb("#FFFFFF"),
        accent_rgb=_hex_to_rgb("#00B894"),
        diagram_node_fill_rgb=_hex_to_rgb("#DFE6E9"),
        diagram_node_line_rgb=_hex_to_rgb("#6C5CE7"),
        diagram_text_rgb=_hex_to_rgb("#2D3436"),
    ),
    "Dark Mode Elegant": Theme(
        name="Dark Mode Elegant",
        font_title="Calibri",
        font_body="Calibri",
        title_rgb=_hex_to_rgb("#FFFFFF"),
        body_rgb=_hex_to_rgb("#B2B2B2"),
        background_rgb=_hex_to_rgb("#1A1A1A"),
        accent_rgb=_hex_to_rgb("#FFD700"),
        diagram_node_fill_rgb=_hex_to_rgb("#2A2A2A"),
        diagram_node_line_rgb=_hex_to_rgb("#FFD700"),
        diagram_text_rgb=_hex_to_rgb("#FFFFFF"),
    ),
    "Ocean Blue": Theme(
        name="Ocean Blue",
        font_title="Calibri",
        font_body="Calibri",
        title_rgb=_hex_to_rgb("#0C4A6E"),
        body_rgb=_hex_to_rgb("#334155"),
        background_rgb=_hex_to_rgb("#FFFFFF"),
        accent_rgb=_hex_to_rgb("#0EA5E9"),
        diagram_node_fill_rgb=_hex_to_rgb("#E0F2FE"),
        diagram_node_line_rgb=_hex_to_rgb("#0EA5E9"),
        diagram_text_rgb=_hex_to_rgb("#0C4A6E"),
    ),
    "Warm Sunset": Theme(
        name="Warm Sunset",
        font_title="Calibri",
        font_body="Calibri",
        title_rgb=_hex_to_rgb("#7C2D12"),
        body_rgb=_hex_to_rgb("#44403C"),
        background_rgb=_hex_to_rgb("#FFFBEB"),
        accent_rgb=_hex_to_rgb("#F97316"),
        diagram_node_fill_rgb=_hex_to_rgb("#FED7AA"),
        diagram_node_line_rgb=_hex_to_rgb("#EA580C"),
        diagram_text_rgb=_hex_to_rgb("#7C2D12"),
    ),
    "Fresh Green": Theme(
        name="Fresh Green",
        font_title="Calibri",
        font_body="Calibri",
        title_rgb=_hex_to_rgb("#14532D"),
        body_rgb=_hex_to_rgb("#374151"),
        background_rgb=_hex_to_rgb("#FFFFFF"),
        accent_rgb=_hex_to_rgb("#22C55E"),
        diagram_node_fill_rgb=_hex_to_rgb("#DCFCE7"),
        diagram_node_line_rgb=_hex_to_rgb("#16A34A"),
        diagram_text_rgb=_hex_to_rgb("#14532D"),
    ),
    "Soft Pastel": Theme(
        name="Soft Pastel",
        font_title="Calibri",
        font_body="Calibri",
        title_rgb=_hex_to_rgb("#5B21B6"),
        body_rgb=_hex_to_rgb("#4B5563"),
        background_rgb=_hex_to_rgb("#FAF5FF"),
        accent_rgb=_hex_to_rgb("#A855F7"),
        diagram_node_fill_rgb=_hex_to_rgb("#E9D5FF"),
        diagram_node_line_rgb=_hex_to_rgb("#9333EA"),
        diagram_text_rgb=_hex_to_rgb("#5B21B6"),
    ),
    "Tech Startup": Theme(
        name="Tech Startup",
        font_title="Calibri",
        font_body="Calibri",
        title_rgb=_hex_to_rgb("#1E293B"),
        body_rgb=_hex_to_rgb("#475569"),
        background_rgb=_hex_to_rgb("#F8FAFC"),
        accent_rgb=_hex_to_rgb("#3B82F6"),
        diagram_node_fill_rgb=_hex_to_rgb("#DBEAFE"),
        diagram_node_line_rgb=_hex_to_rgb("#2563EB"),
        diagram_text_rgb=_hex_to_rgb("#1E293B"),
    ),
}


def get_theme(name: str | None) -> Theme:
    if not name:
        return THEME_PRESETS["Modern Minimal"]
    key = name.strip()
    return THEME_PRESETS.get(key, THEME_PRESETS["Modern Minimal"])


def available_themes() -> list[str]:
    return sorted(THEME_PRESETS.keys())
