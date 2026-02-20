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
    "Education Light": Theme(
        name="Education Light",
        font_title="Calibri",
        font_body="Calibri",
        title_rgb=_hex_to_rgb("#1F4E79"),
        body_rgb=_hex_to_rgb("#333333"),
        background_rgb=_hex_to_rgb("#FFFFFF"),
        accent_rgb=_hex_to_rgb("#38BDF8"),
        diagram_node_fill_rgb=_hex_to_rgb("#EAF2FF"),
        diagram_node_line_rgb=_hex_to_rgb("#4F81BD"),
        diagram_text_rgb=_hex_to_rgb("#1F375E"),
    ),
    "Dark Tech": Theme(
        name="Dark Tech",
        font_title="Calibri",
        font_body="Calibri",
        title_rgb=_hex_to_rgb("#E6F0FF"),
        body_rgb=_hex_to_rgb("#D1D5DB"),
        background_rgb=_hex_to_rgb("#0B1220"),
        accent_rgb=_hex_to_rgb("#22D3EE"),
        diagram_node_fill_rgb=_hex_to_rgb("#111827"),
        diagram_node_line_rgb=_hex_to_rgb("#22D3EE"),
        diagram_text_rgb=_hex_to_rgb("#E5E7EB"),
    ),
    "Corporate Blue": Theme(
        name="Corporate Blue",
        font_title="Calibri",
        font_body="Calibri",
        title_rgb=_hex_to_rgb("#0F2A43"),
        body_rgb=_hex_to_rgb("#1F2937"),
        background_rgb=_hex_to_rgb("#FFFFFF"),
        accent_rgb=_hex_to_rgb("#2563EB"),
        diagram_node_fill_rgb=_hex_to_rgb("#EFF6FF"),
        diagram_node_line_rgb=_hex_to_rgb("#2563EB"),
        diagram_text_rgb=_hex_to_rgb("#0F2A43"),
    ),
    "Minimal": Theme(
        name="Minimal",
        font_title="Calibri",
        font_body="Calibri",
        title_rgb=_hex_to_rgb("#111827"),
        body_rgb=_hex_to_rgb("#374151"),
        background_rgb=_hex_to_rgb("#FFFFFF"),
        accent_rgb=_hex_to_rgb("#6B7280"),
        diagram_node_fill_rgb=_hex_to_rgb("#FFFFFF"),
        diagram_node_line_rgb=_hex_to_rgb("#6B7280"),
        diagram_text_rgb=_hex_to_rgb("#111827"),
    ),
}


def get_theme(name: str | None) -> Theme:
    if not name:
        return THEME_PRESETS["Education Light"]
    key = name.strip()
    return THEME_PRESETS.get(key, THEME_PRESETS["Education Light"])


def available_themes() -> list[str]:
    return sorted(THEME_PRESETS.keys())
