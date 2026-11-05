"""Finishing: bloom, flash, grade, vignette, grain, then crisp UI on top.

Output is BGR24 bytes (cairo stores BGRA), fed straight to ffmpeg.
"""
from __future__ import annotations

import cv2
import numpy as np

from .gfx import W, H, Canvas


def _smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


class Post:
    def __init__(self, seed=3, grain=0.020, bloom=1.0, vignette=0.42):
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        nx = (xx - W / 2) / (W / 2)
        ny = (yy - H / 2) / (H / 2)
        d = np.sqrt(nx ** 2 * 0.85 + ny ** 2 * 0.62)
        self.vig = (1 - vignette * _smoothstep(0.45, 1.35, d)).astype(np.float32)[..., None]
        rng = np.random.default_rng(seed)
        self.grain_tiles = [rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32) for _ in range(8)]
        self.grain = grain
        self.bloom = bloom
        x = np.linspace(0, 1, 256)
        s = 0.86 * x + 0.14 * (x * x * (3 - 2 * x))           # gentle S-curve
        lift = (1 - x) ** 3
        # BGR order: navy shadows, very slightly warm highlights
        b = np.clip(s + 0.030 * lift - 0.012 * x ** 4, 0, 1)
        g = np.clip(s + 0.012 * lift, 0, 1)
        r = np.clip(s + 0.006 * lift + 0.010 * x ** 4, 0, 1)
        self.lut = (np.stack([b, g, r], axis=-1) * 255 + 0.5).astype(np.uint8)[:, None, :]

    def finish(self, cv: Canvas, frame_idx: int) -> bytes:
        base = np.ndarray((H, W, 4), np.uint8, cv.base_s.get_data())[..., :3]
        img = base.astype(np.float32) * (1 / 255)
        glow = np.ndarray((H // 2, W // 2, 4), np.uint8, cv.glow_s.get_data())[..., :3]
        if glow.any():
            gl = glow.astype(np.float32) * (1 / 255)
            b1 = cv2.GaussianBlur(gl, (0, 0), 4.0)
            small = cv2.resize(gl, (W // 8, H // 8), interpolation=cv2.INTER_AREA)
            b2 = cv2.GaussianBlur(small, (0, 0), 5.0)
            b2 = cv2.resize(b2, (W // 2, H // 2), interpolation=cv2.INTER_LINEAR)
            bloom = cv2.resize(0.85 * b1 + 1.25 * b2, (W, H), interpolation=cv2.INTER_LINEAR)
            img += bloom * self.bloom
        if cv.flash > 0:
            img += cv.flash * np.array([1.0, 0.97, 0.92], np.float32)
        if cv.aberration > 0:
            k = int(round(cv.aberration))
            if k > 0:
                img[..., 2] = np.roll(img[..., 2], -k, axis=1)
                img[..., 0] = np.roll(img[..., 0], k, axis=1)
        # soft highlight roll-off instead of hard clipping
        img = img / (1 + 0.25 * np.maximum(img - 0.85, 0))
        img *= self.vig
        g = cv2.resize(self.grain_tiles[frame_idx % len(self.grain_tiles)], (W, H),
                       interpolation=cv2.INTER_LINEAR)[..., None]
        img += g * self.grain * (1 - 0.55 * np.clip(img, 0, 1))
        out = (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)
        out = cv2.LUT(out, self.lut)
        ui = np.ndarray((H, W, 4), np.uint8, cv.ui_s.get_data())
        if ui[..., 3].any():
            a = ui[..., 3:4].astype(np.float32) * (1 / 255)
            out = (out.astype(np.float32) * (1 - a) + ui[..., :3].astype(np.float32)).clip(0, 255) \
                .astype(np.uint8)
        return out.tobytes()
