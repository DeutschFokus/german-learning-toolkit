"""Crisp UI-layer text and lines (no motion blur / depth of field / grading),
with optional bloom, plus a scope that makes the UI layer follow scene
transitions. Shared by EP004 onward.
"""
from __future__ import annotations

import cairo

from .gfx import H, L, W, _text_path, clamp, rounded_rect, text_width


def htext(cv, s, x, y, size, color=L.WHITE, alpha=1.0, glow=0.0, font=L.DISPLAY, anchor="center",
          tracking=0.0, shadow=0.7, glow_alpha=None):
    k = getattr(cv, "ui_alpha", 1.0)
    alpha *= k
    ga = alpha * glow if glow_alpha is None else glow_alpha * k
    if alpha <= 0.003 and ga <= 0.003:
        return 0.0
    w = text_width(cv.b, s, size, font, tracking)
    if alpha > 0.003:
        cv.text(s, x, y, size, font=font, color=color, alpha=alpha, anchor=anchor, tracking=tracking,
                layer="ui", shadow=shadow)
    if ga > 0.003:
        x0 = x - w / 2 if anchor == "center" else (x - w if anchor == "right" else x)
        g = cv.g
        g.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        g.set_font_size(size)
        g.new_path()
        _text_path(g, s, x0, y + size * 0.365, size, tracking)
        g.set_source_rgba(*color, clamp(ga))
        g.fill()
    return w


def uline(cv, pts, color, width=2.0, alpha=1.0, dash=None):
    alpha *= getattr(cv, "ui_alpha", 1.0)
    if alpha <= 0.003 or len(pts) < 2:
        return
    u = cv.u
    u.new_path()
    u.move_to(*pts[0])
    for p in pts[1:]:
        u.line_to(*p)
    u.set_dash(dash or [])
    u.set_line_width(width)
    u.set_source_rgba(*color, clamp(alpha))
    u.stroke()
    u.set_dash([])


def upoly(cv, pts, color, alpha=1.0):
    alpha *= getattr(cv, "ui_alpha", 1.0)
    if alpha <= 0.003:
        return
    u = cv.u
    u.new_path()
    u.move_to(*pts[0])
    for p in pts[1:]:
        u.line_to(*p)
    u.close_path()
    u.set_source_rgba(*color, clamp(alpha))
    u.fill()


def ucard(cv, x, y, w, h, alpha=1.0, border=L.CYAN, fill=(0.03, 0.05, 0.10), radius=18, fill_alpha=0.82):
    alpha *= getattr(cv, "ui_alpha", 1.0)
    if alpha <= 0.003:
        return
    u = cv.u
    u.save()
    u.new_path()
    rounded_rect(u, x, y, w, h, radius)
    u.set_source_rgba(*fill, fill_alpha * alpha)
    u.fill_preserve()
    u.set_source_rgba(*border, 0.65 * alpha)
    u.set_line_width(2)
    u.stroke()
    u.restore()


class ui_scope:
    """Apply a scene transition (alpha, scale about (cx, cy), vertical offset) to the UI layer too."""

    def __init__(self, cv, a, s=1.0, ty=0.0, cx=W / 2, cy=H / 2):
        self.cv, self.a, self.s, self.ty, self.cx, self.cy = cv, a, s, ty, cx, cy

    def __enter__(self):
        cv = self.cv
        self.prev = getattr(cv, "ui_alpha", 1.0)
        cv.ui_alpha = self.prev * self.a
        u = cv.u
        u.save()
        u.translate(self.cx, self.cy + self.ty)
        u.scale(self.s, self.s)
        u.translate(-self.cx, -self.cy)
        return self

    def __exit__(self, *exc):
        self.cv.u.restore()
        self.cv.ui_alpha = self.prev
        return False
