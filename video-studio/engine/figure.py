"""Hologram human figure: a reusable LUMEN character.

Built once from capsules, smoothed into a single silhouette, then drawn per
frame as a glowing outline with an animated interior (scanlines whose speed
can vary with height: handy for anything "faster at the top").
"""
from __future__ import annotations

import math

import cairo
import cv2
import numpy as np

from .gfx import L, Canvas, mix


def _a8_from_array(a: np.ndarray) -> cairo.ImageSurface:
    h, w = a.shape
    s = cairo.ImageSurface(cairo.FORMAT_A8, w, h)
    stride = s.get_stride()
    buf = np.ndarray((h, stride), np.uint8, s.get_data())
    buf[:, :w] = (np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)
    s.mark_dirty()
    return s


class Figure:
    def __init__(self, height=1000, pad=40):
        self.height = height
        u = height / 7.6
        self.u = u
        self.w = int(3.0 * u + 2 * pad)
        self.h = int(height + 2 * pad)
        self.cx = self.w / 2
        self.top = pad
        surf = cairo.ImageSurface(cairo.FORMAT_A8, self.w, self.h)
        c = cairo.Context(surf)
        c.set_source_rgba(0, 0, 0, 1)
        c.set_line_cap(cairo.LINE_CAP_ROUND)

        def P(x, y):
            return (self.cx + x * u, self.top + y * u)

        def capsule(p, q, wd):
            c.set_line_width(wd)
            c.move_to(*p)
            c.line_to(*q)
            c.stroke()

        def ellipse(p, rx, ry):
            c.save()
            c.translate(*p)
            c.scale(rx, ry)
            c.arc(0, 0, 1, 0, 2 * math.pi)
            c.restore()
            c.fill()

        ellipse(P(0, 0.53), 0.37 * u, 0.50 * u)               # head
        capsule(P(0, 0.85), P(0, 1.35), 0.32 * u)             # neck
        side = [(0.17, 1.20), (0.55, 1.33), (0.86, 1.47), (0.97, 1.70), (0.90, 2.20), (0.80, 2.60),
                (0.66, 3.02), (0.68, 3.35), (0.80, 3.70), (0.80, 3.98), (0.45, 4.10), (0.06, 4.12)]
        pts = [P(x, y) for x, y in side] + [P(-x, y) for x, y in reversed(side)]
        c.move_to(*pts[0])
        for p in pts[1:]:
            c.line_to(*p)
        c.close_path()
        c.fill()
        for sgn in (1, -1):
            capsule(P(sgn * 0.86, 1.66), P(sgn * 1.06, 2.86), 0.33 * u)   # upper arm
            capsule(P(sgn * 1.06, 2.86), P(sgn * 1.15, 3.88), 0.27 * u)   # forearm
            ellipse(P(sgn * 1.17, 4.16), 0.14 * u, 0.26 * u)              # hand
            capsule(P(sgn * 0.40, 3.90), P(sgn * 0.39, 5.55), 0.52 * u)   # thigh
            capsule(P(sgn * 0.39, 5.55), P(sgn * 0.34, 7.12), 0.36 * u)   # shin
            ellipse(P(sgn * 0.42, 7.40), 0.25 * u, 0.12 * u)              # foot
        stride = surf.get_stride()
        raw = np.ndarray((self.h, stride), np.uint8, surf.get_data())[:, :self.w].astype(np.float32) / 255
        blur = cv2.GaussianBlur(raw, (0, 0), 0.035 * u)
        m = np.clip((blur - 0.42) / 0.16, 0, 1)
        m = m * m * (3 - 2 * m)
        k = max(3, int(0.045 * u)) | 1
        er = cv2.erode(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
        edge = cv2.GaussianBlur(np.clip(m - er, 0, 1), (0, 0), 0.8)
        edge = np.clip(edge * 1.6, 0, 1)
        self.mask = _a8_from_array(m)
        self.edge = _a8_from_array(edge)
        # landmarks in figure-local pixels (relative to figure centre-top)
        self.head = (0.0, 0.53 * u)
        self.feet = (0.0, 7.45 * u)
        self.chest = (0.0, 2.2 * u)

    def draw(self, cv: Canvas, t, x, y, s=1.0, alpha=1.0, top_color=L.CYAN, bottom_color=L.AMBER,
             scan_speed=(140.0, 40.0), fill_alpha=0.16, glow=1.0, scan_alpha=0.22, reveal=1.0,
             loop_len=60.0):
        """Draw with the top-centre of the head at (x, y). reveal<1 wipes in from the feet up."""
        if alpha <= 0.002:
            return
        if alpha < 0.999:
            with cv.group(alpha):
                self.draw(cv, t, x, y, s, 1.0, top_color, bottom_color, scan_speed, fill_alpha,
                          glow, scan_alpha, reveal, loop_len)
            return
        ox = x - self.cx * s
        oy = y - self.top * s
        hh = self.h
        for ci, c in enumerate((cv.b, cv.g)):
            if ci == 1 and glow <= 0:
                continue
            c.save()
            c.translate(ox, oy)
            c.scale(s, s)
            if reveal < 1.0:
                c.rectangle(0, hh * (1 - reveal), self.w, hh * reveal + 2)
                c.clip()
            grad = cairo.LinearGradient(0, self.top, 0, self.top + self.height)
            grad.add_color_stop_rgb(0.0, *top_color)
            grad.add_color_stop_rgb(0.55, *mix(top_color, bottom_color, 0.55))
            grad.add_color_stop_rgb(1.0, *bottom_color)
            if ci == 0:
                # interior: soft gradient + scanlines
                c.push_group()
                c.set_source(grad)
                c.paint_with_alpha(fill_alpha)
                step = 11.0
                c.set_line_width(2.0)
                n = int(hh / step) + 2
                period = hh + step
                for k in range(n):
                    frac = k / n                      # 0 top .. 1 bottom
                    speed = scan_speed[0] * (1 - frac) + scan_speed[1] * frac
                    # quantise to whole wraps per loop_len seconds so loops are seamless
                    laps = max(1, round(speed * loop_len / period))
                    yy = (k * step - t * laps * period / loop_len) % period
                    col = mix(top_color, bottom_color, yy / hh)
                    c.set_source_rgba(*col, scan_alpha)
                    c.move_to(0, yy)
                    c.line_to(self.w, yy)
                    c.stroke()
                c.pop_group_to_source()
                c.mask_surface(self.mask, 0, 0)
            # outline
            c.push_group()
            c.set_source(grad)
            c.paint()
            c.pop_group_to_source()
            c.mask_surface(self.edge, 0, 0)
            if ci == 1:
                c.push_group()
                c.set_source(grad)
                c.paint_with_alpha(0.25)
                c.pop_group_to_source()
                c.mask_surface(self.mask, 0, 0)
            c.restore()

    def point(self, which, x, y, s=1.0):
        """Screen position of a landmark when the figure is drawn at (x, y) with scale s."""
        px, py = {"head": self.head, "feet": self.feet, "chest": self.chest}[which]
        return (x + px * s, y + py * s)
