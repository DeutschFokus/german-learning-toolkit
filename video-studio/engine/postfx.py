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
        # --- camera effects on the scene (before light is added)
        mot = getattr(cv, "motion", None)
        if mot:
            img = self._motion_blur(img, *mot)
        dof = getattr(cv, "dof", None)
        if dof:
            img = self._dof(img, *dof)
        heat = getattr(cv, "heat", None)
        if heat:
            img = self._heat(img, frame_idx, *heat)
        glow = np.ndarray((H // 2, W // 2, 4), np.uint8, cv.glow_s.get_data())[..., :3]
        if glow.any():
            gl = glow.astype(np.float32) * (1 / 255)
            b1 = cv2.GaussianBlur(gl, (0, 0), 4.0)
            small = cv2.resize(gl, (W // 8, H // 8), interpolation=cv2.INTER_AREA)
            b2 = cv2.GaussianBlur(small, (0, 0), 5.0)
            b2 = cv2.resize(b2, (W // 2, H // 2), interpolation=cv2.INTER_LINEAR)
            bloom = cv2.resize(0.85 * b1 + 1.25 * b2, (W, H), interpolation=cv2.INTER_LINEAR)
            img += bloom * self.bloom
            rays = getattr(cv, "rays", None)
            if rays:
                img += self._rays(gl, *rays)
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

    # ------------------------------------------------------------------ camera / light effects
    @staticmethod
    def _motion_blur(img, dx, dy):
        """Directional blur for fast camera moves (pixels of travel during the shutter)."""
        n = int(round(max(abs(dx), abs(dy))))
        if n < 2:
            return img
        if abs(dx) < 0.5:
            return cv2.blur(img, (1, n))
        if abs(dy) < 0.5:
            return cv2.blur(img, (n, 1))
        k = np.zeros((2 * n + 1, 2 * n + 1), np.float32)
        cv2.line(k, (int(n - dx / 2), int(n - dy / 2)), (int(n + dx / 2), int(n + dy / 2)), 1.0, 1)
        return cv2.filter2D(img, -1, k / max(k.sum(), 1e-6))

    @staticmethod
    def _dof(img, focus_y, band, sigma):
        """Tilt-shift depth of field: sharp around focus_y, softer toward top and bottom."""
        if sigma <= 0.3:
            return img
        small = cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
        bl = cv2.resize(cv2.GaussianBlur(small, (0, 0), sigma / 4), (W, H), interpolation=cv2.INTER_LINEAR)
        ys = np.arange(H, dtype=np.float32)
        d = np.clip((np.abs(ys - focus_y) - band) / max(band, 1.0), 0, 1)
        m = (d * d * (3 - 2 * d))[:, None, None]
        return img + (bl - img) * m

    @staticmethod
    def _heat(img, frame_idx, amount, y0, y1):
        """Heat shimmer: a gentle horizontal wobble that grows from y0 to y1."""
        if amount <= 0.05:
            return img
        ys = np.arange(H, dtype=np.float32)[:, None]
        xs = np.arange(W, dtype=np.float32)[None, :]
        w = np.clip((ys - y0) / max(1.0, y1 - y0), 0, 1)
        ph = frame_idx * 0.37
        dx = amount * w * (np.sin(ys * 0.043 + ph + xs * 0.012) + 0.6 * np.sin(ys * 0.11 - ph * 1.31))
        dy = amount * 0.35 * w * np.sin(xs * 0.05 + ph * 0.8)
        mx = (xs + dx).astype(np.float32)
        my = (ys + dy).astype(np.float32)
        return cv2.remap(img, mx, my, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

    @staticmethod
    def _rays(gl, x, y, strength, n=12, decay=0.032):
        """Volumetric light shafts: radial blur of the glow layer toward a light at (x, y)."""
        if strength <= 0.01:
            return 0.0
        cx, cy = x / 2, y / 2
        acc = np.zeros_like(gl)
        for k in range(1, n + 1):
            s = 1.0 - decay * k
            M = np.float32([[s, 0, cx * (1 - s)], [0, s, cy * (1 - s)]])
            acc += cv2.warpAffine(gl, M, (W // 2, H // 2), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP) * (
                1 - k / (n + 1))
        acc *= strength / n
        return cv2.resize(cv2.GaussianBlur(acc, (0, 0), 2.0), (W, H), interpolation=cv2.INTER_LINEAR)
