"""Cairo rendering: transparent PNGs, shapes, and real alpha erasing."""
import math

import cairo


def _stroke(cr, stroke, whiteboard=False):
    points = stroke.points
    first, last = points[0], points[-1]
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_line_join(cairo.LINE_JOIN_ROUND)
    width = stroke.width * (4 if stroke.tool == "highlighter" else 1)
    cr.set_line_width(width)
    if stroke.tool == "eraser" and not whiteboard:
        cr.set_operator(cairo.OPERATOR_CLEAR)
    else:
        cr.set_operator(cairo.OPERATOR_OVER)
        if stroke.tool == "eraser" and whiteboard:
            cr.set_source_rgb(1, 1, 1)
        else:
            r, g, b = (int(stroke.color[n:n + 2], 16) / 255 for n in (1, 3, 5))
            cr.set_source_rgba(r, g, b, 0.35 if stroke.tool == "highlighter" else 1)
    tool = stroke.tool
    if tool in ("pen", "highlighter", "eraser"):
        cr.move_to(*first)
        if len(points) == 1:
            cr.line_to(first[0] + 0.01, first[1] + 0.01)
        else:
            for point in points[1:]:
                cr.line_to(*point)
    elif tool in ("line", "arrow"):
        cr.move_to(*first)
        cr.line_to(*last)
        if tool == "arrow":
            dx, dy = last[0] - first[0], last[1] - first[1]
            distance = math.hypot(dx, dy)
            if distance > 0.01:
                angle = math.atan2(dy, dx)
                head = min(max(12, width * 3.5), distance / 2)
                for side in (-1, 1):
                    a = angle + math.pi + side * math.pi / 6
                    cr.move_to(*last)
                    cr.line_to(last[0] + head * math.cos(a),
                               last[1] + head * math.sin(a))
    elif tool == "rectangle":
        cr.rectangle(min(first[0], last[0]), min(first[1], last[1]),
                     abs(last[0] - first[0]), abs(last[1] - first[1]))
    elif tool == "ellipse":
        rx, ry = abs(last[0] - first[0]) / 2, abs(last[1] - first[1]) / 2
        if rx > 0.01 and ry > 0.01:
            cr.save()
            cr.translate((first[0] + last[0]) / 2,
                         (first[1] + last[1]) / 2)
            cr.scale(rx, ry)
            cr.arc(0, 0, 1, 0, 2 * math.pi)
            cr.restore()
    cr.stroke()
    cr.set_operator(cairo.OPERATOR_OVER)


def surface(document, width, height, preview=None, whiteboard=False):
    width, height = int(width), int(height)
    if width <= 0 or height <= 0 or width * height > 100_000_000:
        raise ValueError("Geçersiz tuval boyutu.")
    image = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    cr = cairo.Context(image)
    cr.set_operator(cairo.OPERATOR_SOURCE)
    cr.set_source_rgba(1, 1, 1, 1 if whiteboard else 0)
    cr.paint()
    cr.set_operator(cairo.OPERATOR_OVER)
    for stroke in document.strokes:
        _stroke(cr, stroke, whiteboard)
    if preview is not None:
        _stroke(cr, preview, whiteboard)
    return image
