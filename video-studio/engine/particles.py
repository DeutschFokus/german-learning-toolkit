"""Loop-safe particle fields: snow, dust, embers.

Every particle wraps the screen a whole number of times per loop, and every
sway has a whole number of cycles per loop, so the last frame of a 60 s video
flows straight into the first.
"""
from __future__ import annotations

import math

import cairo
import numpy as np

from .gfx import Canvas, W, H

KINDS = {
    #          size range    laps/loop   sway px     colour               alpha range   dir
    "snow":   ((1.2, 3.8), (3, 8), (6, 26), (0.92, 0.95, 1.00), (0.35, 0.90), +1),
    "dust":   ((0.8, 2.6), (1, 3), (8, 30), (0.80, 0.85, 1.00), (0.10, 0.35), -1),
    "embers": ((1.0, 3.4), (2, 6), (6, 22), (1.00, 0.55, 0.20), (0.35, 0.95), -1),
}


class Particles:
    def __init__(self, n=160, seed=1, kind="snow", loop=60.0):
        rng = np.random.default_rng(seed)
        (s0, s1), (l0, l1), (w0, w1), col, (a0, a1), sign = KINDS[kind]
        self.kind, self.col, self.loop = kind, col, loop
        self.x0 = rng.uniform(-20, W + 20, n)
        self.y0 = rng.uniform(-20, H + 20, n)
        self.depth = rng.uniform(0.35, 1.0, n)
        self.size = rng.uniform(s0, s1, n) * self.depth
        self.alpha = rng.uniform(a0, a1, n) * (0.4 + 0.6 * self.depth)
        laps = rng.integers(l0, l1 + 1, n)
        self.vy = sign * laps * (H + 40) / loop
        self.amp = rng.uniform(w0, w1, n)
        self.f = rng.integers(2, 7, n) * 2 * math.pi / loop
        self.ph = rng.uniform(0, 2 * math.pi, n)

    def draw(self, cv: Canvas, t, alpha=1.0, cam_dy=0.0, glow=0.0, color=None):
        """cam_dy: camera travel in px (parallax: near particles move more)."""
        if alpha <= 0.003:
            return
        col = color or self.col
        y = (self.y0 + self.vy * t - cam_dy * (0.6 + 0.8 * self.depth)) % (H + 40) - 20
        x = self.x0 + self.amp * np.sin(self.f * t + self.ph)
        b = cv.b
        for X, Y, r, a in zip(x, y, self.size, self.alpha):
            b.set_source_rgba(*col, a * alpha)
            b.arc(X, Y, r, 0, 2 * math.pi)
            b.fill()
            if glow > 0 and r > 1.6:
                cv.g.set_source_rgba(*col, a * alpha * glow)
                cv.g.arc(X, Y, r * 2.2, 0, 2 * math.pi)
                cv.g.fill()


class Aurora:
    """Northern-lights curtains rendered with numpy at half resolution.

    Phases advance by whole cycles per loop, so the sky loops cleanly.
    """

    def __init__(self, seed=4, y_base=560.0, loop=60.0):
        rng = np.random.default_rng(seed)
        self.loop = loop
        self.y_base = y_base / 2
        self.w, self.h = W // 2, H // 2
        self.ribbons = []
        for k in range(3):
            self.ribbons.append({
                "dy": rng.uniform(-70, 40), "amp": rng.uniform(18, 46), "f": rng.uniform(1.2, 2.6),
                "cyc": int(rng.integers(1, 4)), "ph": rng.uniform(0, 6.28), "height": rng.uniform(45, 110),
                "gain": rng.uniform(0.55, 1.0)})
        raw = rng.random(self.w * 2)                       # periodic over 2w, so the ray drift loops
        k = np.hanning(9)
        per = np.convolve(np.tile(raw, 3), k / k.sum(), mode="same")[self.w * 2:self.w * 4]
        per = (per - per.min()) / (np.ptp(per) + 1e-6)
        self.rays = np.concatenate([per, per[:self.w]])
        self._buf = np.zeros((self.h, self.w, 4), np.uint8)
        self.surf = cairo.ImageSurface.create_for_data(self._buf, cairo.FORMAT_ARGB32, self.w, self.h)

    def draw(self, cv: Canvas, t, alpha=1.0, offset_y=0.0):
        if alpha <= 0.003:
            return
        xs = np.arange(self.w, dtype=np.float32)
        ys = np.arange(self.h, dtype=np.float32)[:, None]
        acc = np.zeros((self.h, self.w, 3), np.float32)
        ph_t = 2 * math.pi * t / self.loop
        for r in self.ribbons:
            u = xs / self.w * 2 * math.pi
            yc = (self.y_base + offset_y / 2 + r["dy"]
                  + r["amp"] * np.sin(u * r["f"] + r["ph"] + r["cyc"] * ph_t)
                  + r["amp"] * 0.45 * np.sin(u * r["f"] * 2.7 + r["ph"] * 1.7 - (r["cyc"] + 1) * ph_t)
                  + r["amp"] * 0.25 * np.sin(u * r["f"] * 5.3 + r["ph"] * 0.3 + 2 * r["cyc"] * ph_t))
            yc = yc[None, :]
            above = np.clip(yc - ys, 0, None)
            below = np.clip(ys - yc, 0, None)
            inten = np.where(ys <= yc, np.exp(-above / r["height"]), np.exp(-(below / 4.0) ** 2))
            shift = int((r["cyc"] * t / self.loop) * self.w * 2) % (self.w * 2)
            rays = 0.35 + 0.65 * self.rays[shift:shift + self.w][None, :]
            inten = inten * rays * r["gain"]
            hfrac = np.clip(above / (r["height"] * 2.2), 0, 1)
            green = np.array([0.45, 1.0, 0.55], np.float32)   # BGR order below
            violet = np.array([1.0, 0.35, 0.55], np.float32)
            colr = green[None, None, :] * (1 - hfrac[..., None]) + violet[None, None, :] * hfrac[..., None]
            acc += inten[..., None] * colr
        acc = np.clip(acc * 0.85, 0, 1)
        a = np.clip(acc.max(axis=2), 0, 1)
        self._buf[..., :3] = (acc * 255).astype(np.uint8)
        self._buf[..., 3] = (a * 255).astype(np.uint8)
        self.surf.mark_dirty()
        for ctx, mul in ((cv.b, 0.85), (cv.g, 0.6)):
            ctx.save()
            ctx.scale(2, 2)
            ctx.set_source_surface(self.surf, 0, 0)
            ctx.paint_with_alpha(alpha * mul)
            ctx.restore()
