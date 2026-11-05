"""Anatomy props in the LUMEN line-art style: eye cross-section and a front-view
eye that can blink. Schematic, but with honest proportions and labels.
"""
from __future__ import annotations

import math

import cairo
import numpy as np

from .gfx import L, Canvas, clamp, mix


def eye_section(cv: Canvas, x, y, r, t, alpha=1.0, disc_angle=math.radians(14), receptors_lit=0.0,
                fibers=1.0, flow=0.0, disc_highlight=0.0):
    """Side cross-section of an eyeball, light entering from the LEFT.

    Returns geometry dict: pupil, lens, fovea and disc positions for rays/labels.
    """
    if alpha <= 0.003:
        return {}
    b = cv.b
    # sclera body
    pat = cairo.RadialGradient(x - r * 0.2, y - r * 0.2, r * 0.1, x, y, r)
    pat.add_color_stop_rgba(0, 0.08, 0.14, 0.28, 0.55 * alpha)
    pat.add_color_stop_rgba(1, 0.03, 0.06, 0.14, 0.75 * alpha)
    b.new_path()
    b.arc(x, y, r, 0, 2 * math.pi)
    b.set_source(pat)
    b.fill()
    cv.circle(x, y, r, (0.75, 0.88, 1.0), alpha=0.85 * alpha, fill=False, width=4, glow=0.35)
    # cornea bulge (front, left)
    cx_c = x - r * 0.62
    cv.arc(cx_c, y, r * 0.48, math.radians(128), math.radians(232), color=L.CYAN, alpha=alpha, width=4,
           glow=0.7)
    # iris (two bars with the pupil gap between)
    ix = x - r * 0.80
    for sgn in (-1, 1):
        cv.line([(ix, y + sgn * r * 0.13), (ix, y + sgn * r * 0.42)], (0.35, 0.75, 0.9), width=10,
                alpha=alpha * 0.95)
    # lens
    lx = x - r * 0.64
    b.save()
    b.translate(lx, y)
    b.scale(r * 0.13, r * 0.30)
    b.arc(0, 0, 1, 0, 2 * math.pi)
    b.restore()
    b.set_source_rgba(0.75, 0.95, 1.0, 0.22 * alpha)
    b.fill_preserve()
    b.set_source_rgba(0.75, 0.95, 1.0, 0.8 * alpha)
    b.set_line_width(2.5)
    b.stroke()
    # retina: receptor ticks along the back wall, with a gap at the optic disc
    a0, a1 = math.radians(-118), math.radians(118)
    n = 150
    gap = math.radians(7.5)
    for k in range(n + 1):
        a = a0 + (a1 - a0) * k / n
        if abs(a - disc_angle) < gap:
            continue
        r0, r1 = r * 0.90, r * 0.965
        ca, sa = math.cos(a), math.sin(a)
        lit = receptors_lit * (0.5 + 0.5 * math.sin(k * 1.7 + t * 9.0))
        col = mix((0.35, 0.8, 1.0), (0.85, 1.0, 1.0), lit)
        cv.b.set_source_rgba(*col, alpha * (0.55 + 0.45 * lit))
        cv.b.set_line_width(2.4)
        cv.b.move_to(x + r0 * ca, y + r0 * sa)
        cv.b.line_to(x + r1 * ca, y + r1 * sa)
        cv.b.stroke()
        if lit > 0.6:
            cv.g.set_source_rgba(*col, alpha * lit * 0.6)
            cv.g.set_line_width(3)
            cv.g.move_to(x + r0 * ca, y + r0 * sa)
            cv.g.line_to(x + r1 * ca, y + r1 * sa)
            cv.g.stroke()
    # fovea dip on the visual axis
    cv.arc(x + r * 0.93, y, r * 0.06, math.radians(100), math.radians(260), color=L.WHITE, alpha=0.6 * alpha,
           width=2)
    # optic nerve: a tube leaving the back at disc_angle
    da = disc_angle
    dx, dy = math.cos(da), math.sin(da)
    px, py = -dy, dx                             # perpendicular
    base = (x + r * 0.97 * dx, y + r * 0.97 * dy)
    w = r * 0.12
    length = r * 0.75
    tip = (base[0] + length * dx + r * 0.10, base[1] + length * dy + r * 0.20)
    for sgn in (-1, 1):
        p0 = (base[0] + sgn * w * px, base[1] + sgn * w * py)
        p3 = (tip[0] + sgn * w * 0.9 * px, tip[1] + sgn * w * 0.9 * py)
        p1 = (p0[0] + dx * length * 0.5, p0[1] + dy * length * 0.5)
        p2 = (p3[0] - dx * length * 0.3, p3[1] - dy * length * 0.1)
        cv.curve(p0, p1, p2, p3, (0.85, 0.9, 1.0), width=4, alpha=alpha, glow=0.3)
    # nerve fibres converging from the retina into the disc
    disc = (x + r * 0.93 * dx, y + r * 0.93 * dy)
    if fibers > 0:
        for k in range(14):
            a = a0 + (a1 - a0) * (k + 0.5) / 14
            if abs(a - da) < gap * 1.4:
                continue
            sx_, sy_ = x + r * 0.87 * math.cos(a), y + r * 0.87 * math.sin(a)
            mx, my = x + r * 0.70 * math.cos((a + da) / 2), y + r * 0.70 * math.sin((a + da) / 2)
            cv.curve((sx_, sy_), (mx, my), (mx, my), disc, (0.55, 0.85, 1.0), width=1.4, alpha=0.30 * alpha * fibers)
            if flow > 0:
                f = (t * 0.8 + k * 0.137) % 1.0
                bx = (1 - f) ** 2 * sx_ + 2 * (1 - f) * f * mx + f * f * disc[0]
                by = (1 - f) ** 2 * sy_ + 2 * (1 - f) * f * my + f * f * disc[1]
                cv.circle(bx, by, 3.2, L.CYAN, alpha=alpha * flow, glow=0.9)
    if disc_highlight > 0:
        cv.circle(disc[0], disc[1], r * 0.09, L.MAGENTA, alpha=alpha * disc_highlight * 0.9, fill=False, width=3,
                  glow=0.8)
    return {"pupil": (ix, y), "lens": (lx, y), "fovea": (x + r * 0.93, y), "disc": disc,
            "nerve_tip": tip, "r": r}


def eye_front(cv: Canvas, x, y, w, open_amt=1.0, t=0.0, alpha=1.0, iris_color=(0.25, 0.75, 0.85), look=(0.0, 0.0),
              outline=L.CYAN, glow=0.6):
    """Front view of an eye (almond). open_amt 0 = closed (a lash line), 1 = open."""
    if alpha <= 0.003:
        return
    h = w * 0.30 * clamp(open_amt)
    x0, x1 = x - w / 2, x + w / 2

    def lids(c):
        c.new_path()
        c.move_to(x0, y)
        c.curve_to(x0 + w * 0.25, y - h * 1.25, x1 - w * 0.25, y - h * 1.25, x1, y)
        c.curve_to(x1 - w * 0.25, y + h * 1.05, x0 + w * 0.25, y + h * 1.05, x0, y)
        c.close_path()

    if open_amt > 0.02:
        with cv.clip(lids):
            cv.rect(x0, y - w, w, 2 * w, (0.92, 0.95, 1.0), alpha=0.10 * alpha)
            ir = w * 0.20
            ix, iy = x + look[0] * w * 0.18, y + look[1] * w * 0.08
            pat = cairo.RadialGradient(ix, iy, ir * 0.2, ix, iy, ir)
            pat.add_color_stop_rgba(0, *mix(iris_color, (1, 1, 1), 0.35), alpha)
            pat.add_color_stop_rgba(0.75, *iris_color, alpha)
            pat.add_color_stop_rgba(1, *mix(iris_color, (0, 0, 0), 0.6), alpha)
            cv.b.new_path()
            cv.b.arc(ix, iy, ir, 0, 2 * math.pi)
            cv.b.set_source(pat)
            cv.b.fill()
            for k in range(28):
                a = k / 28 * 2 * math.pi
                cv.b.set_source_rgba(1, 1, 1, 0.10 * alpha)
                cv.b.set_line_width(1.2)
                cv.b.move_to(ix + ir * 0.5 * math.cos(a), iy + ir * 0.5 * math.sin(a))
                cv.b.line_to(ix + ir * 0.95 * math.cos(a), iy + ir * 0.95 * math.sin(a))
                cv.b.stroke()
            cv.circle(ix, iy, ir * 0.45, (0.0, 0.0, 0.02), alpha=alpha)
            cv.circle(ix - ir * 0.28, iy - ir * 0.30, ir * 0.13, L.WHITE, alpha=0.9 * alpha, glow=0.6)
        for c, a_mul, wd in ((cv.b, 1.0, 4.0), (cv.g, glow, 6.0)):
            if a_mul <= 0:
                continue
            lids(c)
            c.set_source_rgba(*outline, alpha * a_mul)
            c.set_line_width(wd)
            c.stroke()
    else:
        cv.curve((x0, y), (x0 + w * 0.25, y + w * 0.06), (x1 - w * 0.25, y + w * 0.06), (x1, y), outline, width=4,
                 alpha=alpha, glow=glow)
    # lashes on the upper lid
    for k in range(7):
        u = 0.2 + 0.6 * k / 6
        bx = (1 - u) ** 3 * x0 + 3 * (1 - u) ** 2 * u * (x0 + w * 0.25) + 3 * (1 - u) * u * u * (x1 - w * 0.25) + u ** 3 * x1
        lid_h = -h * 1.25 if open_amt > 0.02 else w * 0.06
        by = y + 3 * (1 - u) ** 2 * u * lid_h + 3 * (1 - u) * u * u * lid_h
        ang = -math.pi / 2 + (u - 0.5) * 1.2
        if open_amt <= 0.02:
            ang = math.pi / 2 + (u - 0.5) * 1.2
        L_ = w * 0.06
        cv.line([(bx, by), (bx + L_ * math.cos(ang), by + L_ * math.sin(ang))], outline, width=3, alpha=alpha * 0.85)


def iris_glyph(cv: Canvas, x, y, r, t=0.0, alpha=1.0):
    """A glowing iris used as the letter O ("a hole")."""
    pat = cairo.RadialGradient(x, y, r * 0.2, x, y, r)
    pat.add_color_stop_rgba(0, 0.6, 0.95, 1.0, alpha)
    pat.add_color_stop_rgba(0.7, *L.CYAN, alpha)
    pat.add_color_stop_rgba(1, 0.05, 0.35, 0.5, alpha)
    for c, a in ((cv.b, 1.0), (cv.g, 0.9)):
        c.new_path()
        c.arc(x, y, r, 0, 2 * math.pi)
        c.set_source(pat)
        c.fill()
    for k in range(36):
        a = k / 36 * 2 * math.pi + t * 0.05
        cv.b.set_source_rgba(1, 1, 1, 0.16 * alpha)
        cv.b.set_line_width(1.5)
        cv.b.move_to(x + r * 0.52 * math.cos(a), y + r * 0.52 * math.sin(a))
        cv.b.line_to(x + r * 0.96 * math.cos(a), y + r * 0.96 * math.sin(a))
        cv.b.stroke()
    pr = r * (0.48 + 0.04 * math.sin(t * 2 * math.pi / 6.0))   # breathing pupil, 6 s period
    cv.circle(x, y, pr, (0.0, 0.0, 0.015), alpha=alpha)
    cv.circle(x - r * 0.3, y - r * 0.32, r * 0.12, L.WHITE, alpha=0.9 * alpha, glow=0.5)
