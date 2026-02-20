from __future__ import annotations

import math
from dataclasses import dataclass

from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE, MSO_CONNECTOR
from pptx.util import Inches, Pt


@dataclass(frozen=True)
class FlowDiagramStyle:
    node_fill_rgb: tuple[int, int, int] = (234, 242, 255)
    node_line_rgb: tuple[int, int, int] = (79, 129, 189)
    text_rgb: tuple[int, int, int] = (31, 55, 94)
    font_name: str = "Calibri"
    font_size_pt: int = 16


def _set_rgb(color_format, rgb: tuple[int, int, int]) -> None:
    color_format.rgb = RGBColor(rgb[0], rgb[1], rgb[2])


def add_flow_diagram(slide, nodes: list[str], edges: list[tuple[str, str]], style: FlowDiagramStyle | None = None) -> None:
    style = style or FlowDiagramStyle()

    # Simple horizontal layout; wraps into two rows if needed.
    max_per_row = 4
    rows = (len(nodes) + max_per_row - 1) // max_per_row
    rows = max(rows, 1)

    left = Inches(1.0)
    top = Inches(2.0)
    hgap = Inches(0.4)
    vgap = Inches(0.6)
    box_w = Inches(2.2)
    box_h = Inches(0.9)

    node_to_shape = {}

    for i, name in enumerate(nodes):
        r = i // max_per_row
        c = i % max_per_row
        x = left + c * (box_w + hgap)
        y = top + r * (box_h + vgap)

        shape = slide.shapes.add_shape(
            MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, x, y, box_w, box_h)
        fill = shape.fill
        fill.solid()
        _set_rgb(fill.fore_color, style.node_fill_rgb)

        shape.line.width = Pt(2)
        _set_rgb(shape.line.color, style.node_line_rgb)

        tf = shape.text_frame
        tf.clear()
        p = tf.paragraphs[0]
        run = p.add_run()
        run.text = name
        run.font.name = style.font_name
        run.font.size = Pt(style.font_size_pt)
        _set_rgb(run.font.color, style.text_rgb)

        node_to_shape[name] = shape

    # Arrows/connectors between centers.
    for src, dst in edges:
        a = node_to_shape.get(src)
        b = node_to_shape.get(dst)
        if not a or not b:
            continue

        ax = a.left + a.width // 2
        ay = a.top + a.height // 2
        bx = b.left + b.width // 2
        by = b.top + b.height // 2

        conn = slide.shapes.add_connector(
            MSO_CONNECTOR.STRAIGHT, ax, ay, bx, by)
        conn.line.width = Pt(2)
        _set_rgb(conn.line.color, style.node_line_rgb)

        # python-pptx 1.0.x doesn't expose arrowhead enums; simulate arrowheads
        # with a small rotated triangle shape placed near the destination.
        dx = float(bx - ax)
        dy = float(by - ay)
        if abs(dx) + abs(dy) < 1.0:
            continue

        angle_deg = math.degrees(math.atan2(dy, dx))

        size = Inches(0.22)
        backoff = Inches(0.18)

        length = math.hypot(dx, dy)
        ux = dx / length
        uy = dy / length

        cx = bx - int(ux * float(backoff))
        cy = by - int(uy * float(backoff))

        tri_left = int(cx - size / 2)
        tri_top = int(cy - size / 2)

        tri = slide.shapes.add_shape(
            MSO_AUTO_SHAPE_TYPE.ISOSCELES_TRIANGLE,
            tri_left,
            tri_top,
            size,
            size,
        )
        tri.rotation = angle_deg + 90.0
        tri.fill.solid()
        _set_rgb(tri.fill.fore_color, style.node_line_rgb)
        tri.line.fill.background()
