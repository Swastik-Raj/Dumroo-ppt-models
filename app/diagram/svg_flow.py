from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class SvgFlowStyle:
    background_rgb: tuple[int, int, int] = (255, 255, 255)
    node_fill_rgb: tuple[int, int, int] = (234, 242, 255)
    node_line_rgb: tuple[int, int, int] = (79, 129, 189)
    text_rgb: tuple[int, int, int] = (31, 55, 94)
    font_family: str = "Calibri"


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def _wrap_words(text: str, max_chars: int) -> list[str]:
    words = [w for w in text.split() if w]
    if not words:
        return [""]

    lines: list[str] = []
    cur: list[str] = []
    for w in words:
        trial = (" ".join(cur + [w])).strip()
        if cur and len(trial) > max_chars:
            lines.append(" ".join(cur))
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(" ".join(cur))
    return lines[:3]


def _iter_edges(edges: Iterable[tuple[str, str] | list[str]]) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for e in edges:
        if isinstance(e, tuple) and len(e) == 2:
            out.append((str(e[0]), str(e[1])))
        elif isinstance(e, list) and len(e) == 2:
            out.append((str(e[0]), str(e[1])))
    return out


def render_flow_svg(
    nodes: list[str],
    edges: Iterable[tuple[str, str] | list[str]],
    style: SvgFlowStyle | None = None,
    *,
    width_px: int = 1600,
    height_px: int = 900,
) -> str:
    style = style or SvgFlowStyle()

    # Adaptive layout: for 5-8 nodes, use smart positioning to prevent overlap
    node_count = len(nodes)
    if node_count <= 4:
        max_per_row = node_count
    elif node_count <= 6:
        max_per_row = 3
    else:
        max_per_row = 4

    cols = min(max_per_row, max(node_count, 1))
    rows = max(1, math.ceil(node_count / max_per_row))

    # Increase spacing to prevent arrow overlaps
    pad_x = 100
    pad_y = 110
    hgap = 80
    vgap = 90

    box_w = 320
    box_h = 110
    corner = 18

    # Compute required canvas and scale into requested width/height.
    needed_w = pad_x * 2 + cols * box_w + (cols - 1) * hgap
    needed_h = pad_y * 2 + rows * box_h + (rows - 1) * vgap

    scale = min(width_px / needed_w, height_px / needed_h)
    scale = min(scale, 1.0)

    view_w = needed_w
    view_h = needed_h

    # Node positions (top-left) in viewBox space.
    pos: dict[str, tuple[float, float]] = {}
    for i, name in enumerate(nodes):
        r = i // max_per_row
        c = i % max_per_row
        x = pad_x + c * (box_w + hgap)
        y = pad_y + r * (box_h + vgap)
        pos[name] = (x, y)

    # SVG header + arrow marker
    bg = _rgb_to_hex(style.background_rgb)
    node_fill = _rgb_to_hex(style.node_fill_rgb)
    node_line = _rgb_to_hex(style.node_line_rgb)
    text_color = _rgb_to_hex(style.text_rgb)

    svg: list[str] = []
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width_px}" height="{height_px}" '
        f'viewBox="0 0 {view_w} {view_h}">'  # scale handled via viewBox
    )
    svg.append(
        f'<rect x="0" y="0" width="{view_w}" height="{view_h}" fill="{bg}"/>')
    svg.append(
        "<defs>"
        "<marker id=\"arrow\" markerWidth=\"12\" markerHeight=\"12\" refX=\"10\" refY=\"6\" orient=\"auto\">"
        f"<path d=\"M0,0 L12,6 L0,12 Z\" fill=\"{node_line}\"/>"
        "</marker>"
        "</defs>"
    )

    # Edges first (under nodes) with smart routing to reduce overlaps
    for src, dst in _iter_edges(edges):
        if src not in pos or dst not in pos:
            continue
        ax, ay = pos[src]
        bx, by = pos[dst]

        # Use edge connection points instead of center for cleaner arrows
        src_idx = nodes.index(src) if src in nodes else 0
        dst_idx = nodes.index(dst) if dst in nodes else 0

        # Horizontal routing
        if dst_idx > src_idx:
            # Right edge to left edge
            x1 = ax + box_w
            y1 = ay + box_h / 2
            x2 = bx
            y2 = by + box_h / 2
        elif dst_idx < src_idx:
            # Left edge to right edge (backward)
            x1 = ax
            y1 = ay + box_h / 2
            x2 = bx + box_w
            y2 = by + box_h / 2
        else:
            # Same column: top to bottom or center
            x1 = ax + box_w / 2
            y1 = ay + box_h
            x2 = bx + box_w / 2
            y2 = by

        svg.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{node_line}" stroke-width="4" marker-end="url(#arrow)" opacity="0.85" />'
        )

    # Nodes on top
    for name in nodes:
        x, y = pos[name]
        svg.append(
            f'<rect x="{x}" y="{y}" width="{box_w}" height="{box_h}" '
            f'rx="{corner}" ry="{corner}" fill="{node_fill}" stroke="{node_line}" stroke-width="4" />'
        )

        lines = _wrap_words(name, max_chars=18)
        # Center the block of lines.
        font_size = 34
        line_h = 40
        block_h = len(lines) * line_h
        start_y = y + (box_h - block_h) / 2 + font_size

        svg.append(
            f'<text x="{x + box_w / 2}" y="{start_y}" text-anchor="middle" '
            f'fill="{text_color}" font-family="{style.font_family}" font-size="{font_size}" '
            f'font-weight="600">'
        )
        for i, ln in enumerate(lines):
            dy = 0 if i == 0 else line_h
            safe = (
                ln.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            svg.append(f'<tspan x="{x + box_w / 2}" dy="{dy}">{safe}</tspan>')
        svg.append("</text>")

    svg.append("</svg>")

    if scale < 1.0:
        # If we needed scaling down, wrap in a group transform.
        # Simpler: re-render with scaled viewBox by expanding canvas.
        # (Keep current output; cairosvg will rasterize to requested width/height.)
        pass

    return "\n".join(svg)


def svg_to_png_bytes(svg_text: str, *, output_width_px: int = 1600) -> bytes | None:
    try:
        import cairosvg  # type: ignore[import-not-found]
    except Exception:
        return None

    try:
        return cairosvg.svg2png(bytestring=svg_text.encode("utf-8"), output_width=output_width_px)
    except Exception:
        return None
