"""A photographic-style human eye close-up, built procedurally.

HeroEye pre-renders its textures once (skin + sclera, iris, lid shadow, lashes)
with numpy, then composites them per frame with cairo so the iris can move,
the pupil can breathe and anything (e.g. a mushroom cloud) can be reflected in
the cornea. Low-key lighting: the eye floats in darkness, lit from top-left.
"""
from __future__ import annotations

import math

import cairo
import cv2
import numpy as np

from .gfx import Canvas, clamp, lerp

EW, EH = 1200, 820            # texture canvas (eye centred)


def _surf(rgb, a):
    """float RGB (h, w, 3) in RGB order + alpha (h, w) -> premultiplied cairo surface."""
    h, w = a.shape
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    buf = np.ndarray((h, s.get_stride() // 4, 4), np.uint8, s.get_data())
    a = np.clip(a, 0, 1)
    pm = np.clip(rgb, 0, 1) * a[..., None]
    buf[:, :w, 0] = (pm[..., 2] * 255 + 0.5).astype(np.uint8)
    buf[:, :w, 1] = (pm[..., 1] * 255 + 0.5).astype(np.uint8)
    buf[:, :w, 2] = (pm[..., 0] * 255 + 0.5).astype(np.uint8)
    buf[:, :w, 3] = (a * 255 + 0.5).astype(np.uint8)
    s.mark_dirty()
    return s


def _noise2(rng, h, w, scale, octaves=4):
    acc = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        sh, sw = max(2, int(h / scale * 2 ** o)), max(2, int(w / scale * 2 ** o))
        acc += amp * cv2.resize(rng.random((sh, sw)).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC)
        tot += amp
        amp *= 0.5
    acc /= tot
    return (acc - acc.min()) / (np.ptp(acc) + 1e-6)


class HeroEye:
    def __init__(self, seed=5, iris_r=205.0):
        rng = np.random.default_rng(seed)
        self.R = iris_r
        self.cx, self.cy = EW / 2, EH / 2 - 10
        # ---- lid margins (texture coords)
        self.x_in, self.y_in = 118.0, 452.0      # inner corner (left)
        self.x_out, self.y_out = 1088.0, 398.0   # outer corner (right)
        xs = np.linspace(self.x_in, self.x_out, 220)
        u = (xs - self.x_in) / (self.x_out - self.x_in)
        base = lerp(self.y_in, self.y_out, u)
        up = base - 218 * np.sin(np.pi * u) ** 0.80 * (1 + 0.10 * np.sin(np.pi * u - 1.0))
        lo = base + 178 * np.sin(np.pi * np.clip(u * 0.94 + 0.04, 0, 1)) ** 1.35
        self.upper = np.stack([xs, up], 1)
        self.lower = np.stack([xs, lo], 1)
        yy, xx = np.mgrid[0:EH, 0:EW].astype(np.float32)
        upy = np.interp(xx, xs, up, left=1e4, right=1e4)
        loy = np.interp(xx, xs, lo, left=-1e4, right=-1e4)
        inside = (yy > upy) & (yy < loy)
        d_open = np.minimum(yy - upy, loy - yy)                 # distance into the opening
        self.open_mask = np.clip(d_open / 2.0, 0, 1) * inside
        # ---- skin, lit from top-left, falling into darkness
        n1 = _noise2(rng, EH, EW, 60)
        n2 = _noise2(rng, EH, EW, 6, octaves=2)
        skin = np.array([0.60, 0.42, 0.35], np.float32)
        light = np.clip(1.15 - np.hypot((xx - 380) / 900, (yy - 120) / 620), 0, 1) ** 1.5
        spot = np.exp(-(((xx - self.cx) / 560) ** 2 + ((yy - self.cy) / 360) ** 2))
        sk = skin[None, None, :] * (0.25 + 0.95 * light)[..., None] * (0.82 + 0.25 * n1[..., None]) * \
            (0.94 + 0.10 * n2[..., None])
        # upper lid crease and the fold above it
        crease = np.interp(xx, xs, up - 70 - 25 * np.sin(np.pi * u), left=1e4, right=1e4)
        cd = yy - crease
        sk *= (1 - 0.35 * np.exp(-(cd / 10) ** 2))[..., None]
        sk *= (1 - 0.25 * np.clip(cd / 70, 0, 1) * (yy < upy))[..., None]          # lid skin a touch darker
        lower_fold = np.interp(xx, xs, lo + 58 + 20 * np.sin(np.pi * u), left=-1e4, right=-1e4)
        sk *= (1 - 0.18 * np.exp(-((yy - lower_fold) / 14) ** 2))[..., None]
        # lid margins: pink rim and a wet line
        rim = np.exp(-((yy - upy + 3) / 5.0) ** 2) * (yy < upy + 2)
        rim_lo = np.exp(-((yy - loy - 5) / 5.0) ** 2) * (yy > loy - 1)
        pink = np.array([0.62, 0.32, 0.30], np.float32)
        sk = sk * (1 - 0.6 * rim_lo[..., None]) + pink * 0.6 * rim_lo[..., None] * (0.4 + 0.6 * light[..., None])
        sk = sk * (1 - 0.7 * rim[..., None])
        # sclera: an eyeball, curving away into shadow, pink toward the inner corner, a few veins
        dx = (xx - self.cx) / 520
        dy = (yy - self.cy) / 420
        ball = np.clip(1 - (dx ** 2 + dy ** 2), 0, 1) ** 0.6
        sc = np.array([0.80, 0.80, 0.82], np.float32)[None, None, :] * (0.22 + 0.70 * ball)[..., None]
        sc *= (0.50 + 0.50 * light)[..., None]
        limb = np.clip(1 - (np.hypot(xx - self.cx, yy - self.cy) - self.R) / 46, 0, 1)
        sc *= (1 - 0.45 * limb ** 2)[..., None]                      # limbal shadow around the iris
        tint = _noise2(rng, EH, EW, 90, octaves=3)
        sc *= (0.93 + 0.12 * tint[..., None]) * np.array([1.0, 0.985, 0.97], np.float32)
        corners = np.exp(-((np.abs(xx - self.cx) - 430) / 120).clip(-9, 0) ** 2 * 0) * \
            np.clip((np.abs(xx - self.cx) - 300) / 170, 0, 1)
        sc = sc * (1 - 0.22 * corners[..., None]) + np.array([0.60, 0.40, 0.40], np.float32) * 0.22 * \
            corners[..., None] * (0.3 + 0.7 * light[..., None])
        caru = np.exp(-(((xx - self.x_in - 55) / 70) ** 2 + ((yy - self.y_in + 6) / 55) ** 2))
        sc = sc * (1 - 0.6 * caru[..., None]) + np.array([0.72, 0.38, 0.38], np.float32) * 0.6 * caru[..., None]
        veins = np.zeros((EH, EW), np.uint8)
        for k in range(26):
            side = -1 if k % 2 == 0 else 1
            x = self.cx + side * rng.uniform(300, 470)
            y = self.cy + rng.uniform(-120, 140)
            ang = math.atan2(self.cy - y, self.cx - x) + rng.normal(0, 0.5)
            pts = [(x, y)]
            for j in range(int(rng.uniform(8, 22))):
                ang += rng.normal(0, 0.35)
                x += math.cos(ang) * 9
                y += math.sin(ang) * 9
                pts.append((x, y))
            cv2.polylines(veins, [np.array(pts, np.int32)], False, 255, 1, cv2.LINE_AA)
        vm = cv2.GaussianBlur(veins.astype(np.float32) / 255, (0, 0), 0.8)
        far = np.clip((np.hypot(xx - self.cx, (yy - self.cy) * 1.2) - self.R * 1.05) / 120, 0, 1)
        sc = sc * (1 - 0.35 * vm[..., None] * far[..., None]) + np.array([0.65, 0.20, 0.20]) * 0.25 * \
            (vm * far)[..., None]
        m = self.open_mask[..., None]
        base = sk * (1 - m) + sc * m
        # fade the face into darkness (the eye floats) and feather the texture's edges away
        base *= (0.15 + 0.85 * spot)[..., None]
        re = np.sqrt(((xx - self.cx) / 600) ** 2 + ((yy - self.cy) / 405) ** 2)
        fa = np.clip((1.0 - re) / 0.28, 0, 1)
        fa = fa * fa * (3 - 2 * fa)
        self.base = _surf(base, np.maximum(fa, self.open_mask).astype(np.float32))
        # ---- lid shadow over the eyeball (upper lid and lashes overhang)
        dup = np.clip((yy - upy) / 95, 0, 1)
        dlo = np.clip((loy - yy) / 30, 0, 1)
        shade = (1 - (1 - dup) ** 1.3 * 0.90) * (1 - (1 - dlo) ** 2 * 0.50)
        sh_a = (1 - shade) * inside
        self.lid_shadow = _surf(np.zeros((EH, EW, 3), np.float32), sh_a.astype(np.float32))
        # tear-film highlight along the lower lid
        wet = np.exp(-((yy - loy + 4) / 2.2) ** 2) * inside * np.clip(1 - np.abs(xx - 620) / 420, 0, 1)
        self.wet = _surf(np.ones((EH, EW, 3), np.float32), (wet * 0.55).astype(np.float32))
        # ---- iris texture
        self.iris = self._iris(rng)
        # ---- lashes
        self.lashes = self._lashes(rng, xs, up, lo)

    # ------------------------------------------------------------------ iris
    def _iris(self, rng):
        R = int(self.R)
        S = 2 * R + 8
        NR, NT = 160, 1440                     # polar texture: rows = radius (pupil -> limbus), cols = angle

        def aniso(rows, cols, seed, smooth_r=0.0):
            g = np.random.default_rng(seed).random((rows, cols)).astype(np.float32)
            g = np.concatenate([g, g[:, :1]], 1)        # wrap in angle
            out = cv2.resize(g, (NT + NT // cols, NR), interpolation=cv2.INTER_CUBIC)[:, :NT]
            return (out - out.min()) / (np.ptp(out) + 1e-6)

        rr = np.linspace(0, 1, NR, dtype=np.float32)[:, None]
        tt = np.linspace(0, 2 * np.pi, NT, endpoint=False, dtype=np.float32)[None, :]
        # fibres: long along the radius, fine across; they wander a little
        f1 = aniso(6, 260, 1)
        f2 = aniso(10, 520, 2)
        f3 = aniso(20, 900, 3)
        fib = 0.45 * f1 + 0.35 * f2 + 0.20 * f3
        shift = (6 * np.sin(rr * 9 + tt * 2) + 4 * np.sin(rr * 17 + tt * 5)).astype(np.float32)
        cols = (np.arange(NT)[None, :] + shift) % NT
        fib = np.take_along_axis(fib, cols.astype(int), axis=1)
        blot = aniso(5, 40, 4)                                   # slow colour patches
        coll = 0.42 + 0.025 * np.sin(tt * 6 + 1.3) + 0.015 * np.sin(tt * 11 + 0.4) + 0.04 * (blot - 0.5)
        t_in = np.clip((rr - coll + 0.10) / 0.24, 0, 1)
        t_in = t_in * t_in * (3 - 2 * t_in)
        amber = np.array([0.58, 0.40, 0.20], np.float32)
        hazel = np.array([0.42, 0.42, 0.26], np.float32)
        blue1 = np.array([0.30, 0.46, 0.52], np.float32)
        blue2 = np.array([0.20, 0.33, 0.42], np.float32)
        inner = amber * (1 - blot[..., None] * 0.5) + hazel * blot[..., None] * 0.5
        outer = blue1 * (1 - rr[..., None]) + blue2 * rr[..., None]
        outer = outer * (0.94 + 0.12 * blot[..., None])
        col = inner * (1 - t_in[..., None]) + outer * t_in[..., None]
        col = col * (0.68 + 0.52 * fib[..., None])
        # collarette relief: a soft raised ridge, lit on its upper-left side
        ridge = np.exp(-((rr - coll) / 0.04) ** 2)
        col *= (1 + 0.22 * ridge[..., None])
        # crypts: dark lacunae just outside the collarette
        cry = np.zeros((NR, NT), np.float32)
        for k in range(30):
            c0 = rng.uniform(0, NT)
            r0 = rng.uniform(0.44, 0.78)
            wr, wt = rng.uniform(0.03, 0.08), rng.uniform(10, 34)
            dt_ = np.minimum(np.abs(np.arange(NT) - c0), NT - np.abs(np.arange(NT) - c0))[None, :]
            cry = np.maximum(cry, np.exp(-((rr - r0) / wr) ** 2 - (dt_ / wt) ** 2) * rng.uniform(0.5, 1.0))
        col *= (1 - 0.55 * cry[..., None])
        # contraction furrows (broken rings)
        brk = aniso(4, 30, 5)
        for rf in (0.70, 0.80, 0.88):
            col *= (1 - 0.09 * np.exp(-((rr - rf) / 0.012) ** 2) * (brk > 0.45))[..., None]
        # limbal ring
        limb = np.clip((rr - 0.84) / 0.16, 0, 1) ** 1.5
        col *= (1 - 0.80 * limb[..., None])
        col *= (1 - 0.35 * np.clip((0.22 - rr) / 0.12, 0, 1))[..., None]          # pupillary ruff
        # remap polar -> image
        yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
        dx, dy = xx - S / 2, yy - S / 2
        r = np.hypot(dx, dy) / R
        th = (np.arctan2(dy, dx) + 2 * np.pi) % (2 * np.pi)
        mx = (th / (2 * np.pi) * NT).astype(np.float32)
        my = np.clip(r * (NR - 1), 0, NR - 1).astype(np.float32)
        img = cv2.remap(col.astype(np.float32), mx, my, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
        # 3D shading: shallow cone, lit from the top-left; specks of pigment
        lit = 0.78 + 0.32 * np.clip(-(dx * 0.6 + dy * 0.8) / R, -1, 1)
        img *= lit[..., None]
        sp = cv2.GaussianBlur((rng.random((S, S)) > 0.9983).astype(np.float32), (0, 0), 1.3)
        spk = np.clip(sp * 6, 0, 1)[..., None] * (r[..., None] > 0.3)
        img = img * (1 - 0.7 * spk) + np.array([0.42, 0.26, 0.10]) * 0.7 * spk
        a = np.clip((1.0 - r) * R / 3.5, 0, 1)                   # soft limbus edge
        return _surf(img, a.astype(np.float32))

    # ------------------------------------------------------------------ lashes
    def _lashes(self, rng, xs, up, lo):
        s = cairo.ImageSurface(cairo.FORMAT_ARGB32, EW, EH)
        c = cairo.Context(s)
        c.set_source_rgba(0.045, 0.03, 0.025, 1.0)

        def lash(x, y, nx, ny, length, bend, w0, curl):
            # a tapered, curved hair
            tx, ty = -ny, nx
            p0 = (x, y)
            p1 = (x + nx * length * 0.45 + tx * bend * 0.3, y + ny * length * 0.45 + ty * bend * 0.3)
            p2 = (x + nx * length * 0.85 + tx * bend, y + ny * length * 0.85 + ty * bend + curl)
            p3 = (x + nx * length + tx * bend * 1.6, y + ny * length + ty * bend * 1.6 + curl * 1.8)
            c.new_path()
            c.move_to(p0[0] - tx * w0, p0[1] - ty * w0)
            c.curve_to(p1[0] - tx * w0 * 0.6, p1[1] - ty * w0 * 0.6, p2[0] - tx * w0 * 0.25, p2[1] - ty * w0 * 0.25,
                       p3[0], p3[1])
            c.curve_to(p2[0] + tx * w0 * 0.25, p2[1] + ty * w0 * 0.25, p1[0] + tx * w0 * 0.6, p1[1] + ty * w0 * 0.6,
                       p0[0] + tx * w0, p0[1] + ty * w0)
            c.close_path()
            c.fill()

        n_up = 170
        for k in range(n_up):
            u = rng.uniform(0.06, 0.97) ** 0.95
            i = int(u * (len(xs) - 1))
            x, y = xs[i], up[i] + rng.uniform(-1, 3)
            j = min(i + 1, len(xs) - 1)
            gx, gy = xs[j] - xs[max(i - 1, 0)], up[j] - up[max(i - 1, 0)]
            gl = math.hypot(gx, gy) + 1e-6
            nx, ny = gy / gl, -gx / gl                       # outward normal (up)
            outward = (u - 0.42) * 0.9                        # fan toward the outer corner
            nx, ny = nx * math.cos(outward) - ny * math.sin(outward), nx * math.sin(outward) + ny * math.cos(outward)
            length = (55 + 70 * math.sin(math.pi * min(1, u * 1.05)) ** 0.7) * rng.uniform(0.75, 1.15)
            lash(x, y, nx, ny, length, rng.uniform(4, 16) * (1 if u > 0.4 else -0.4), rng.uniform(1.4, 2.4),
                 -rng.uniform(4, 14))
        for k in range(70):
            u = rng.uniform(0.18, 0.95)
            i = int(u * (len(xs) - 1))
            x, y = xs[i], lo[i] + rng.uniform(2, 6)
            j = min(i + 1, len(xs) - 1)
            gx, gy = xs[j] - xs[max(i - 1, 0)], lo[j] - lo[max(i - 1, 0)]
            gl = math.hypot(gx, gy) + 1e-6
            nx, ny = -gy / gl, gx / gl                       # outward normal (down)
            outward = -(u - 0.45) * 0.8
            nx, ny = nx * math.cos(outward) - ny * math.sin(outward), nx * math.sin(outward) + ny * math.cos(outward)
            lash(x, y, nx, ny, rng.uniform(18, 38), rng.uniform(-4, 6), rng.uniform(0.8, 1.3), rng.uniform(1, 5))
        s.flush()
        # soften slightly (depth of field on the lashes)
        a = np.ndarray((EH, s.get_stride() // 4, 4), np.uint8, s.get_data())[:, :EW].astype(np.float32) / 255
        a = cv2.GaussianBlur(a, (0, 0), 1.3)
        return _surf(np.stack([a[..., 2], a[..., 1], a[..., 0]], -1) / np.maximum(a[..., 3:4], 1e-3),
                     a[..., 3])

    # ------------------------------------------------------------------ path helpers
    def _opening_path(self, ctx):
        ctx.new_path()
        ctx.move_to(*self.upper[0])
        for p in self.upper[1:]:
            ctx.line_to(*p)
        for p in self.lower[::-1]:
            ctx.line_to(*p)
        ctx.close_path()

    # ------------------------------------------------------------------ draw
    def draw(self, cv: Canvas, x, y, scale=1.0, alpha=1.0, look=(0.0, 0.0), pupil=0.34, reflect=None,
             reflect_alpha=1.0, spec=1.0, t=0.0):
        """Centre the eye at (x, y). look shifts the iris (px, texture units); pupil = radius / iris radius.
        reflect(ctx, cx, cy, r, glow_ctx) draws into the cornea (texture coords) - e.g. a mushroom cloud."""
        if alpha <= 0.003:
            return
        ix, iy = self.cx + look[0], self.cy + look[1]
        for ctx, is_glow in ((cv.b, False), (cv.g, True)):
            ctx.save()
            ctx.translate(x, y)
            ctx.scale(scale, scale)
            ctx.translate(-EW / 2, -EH / 2)
            if not is_glow:
                ctx.push_group()
                ctx.set_source_surface(self.base, 0, 0)
                ctx.paint()
                ctx.save()
                self._opening_path(ctx)
                ctx.clip()
                ctx.set_source_surface(self.iris, ix - self.iris.get_width() / 2, iy - self.iris.get_height() / 2)
                ctx.paint()
                # pupil with a soft rim
                pr = self.R * pupil
                pat = cairo.RadialGradient(ix, iy, pr * 0.9, ix, iy, pr * 1.08)
                pat.add_color_stop_rgba(0, 0.012, 0.01, 0.012, 1)
                pat.add_color_stop_rgba(1, 0.012, 0.01, 0.012, 0)
                ctx.arc(ix, iy, pr * 1.08, 0, 2 * math.pi)
                ctx.set_source(pat)
                ctx.fill()
                # reflection in the cornea
                if reflect is not None and reflect_alpha > 0.003:
                    ctx.save()
                    ctx.arc(ix, iy, self.R * 1.02, 0, 2 * math.pi)
                    ctx.clip()
                    ctx.push_group()
                    reflect(ctx, ix, iy, self.R, None)
                    ctx.pop_group_to_source()
                    ctx.set_operator(cairo.OPERATOR_ADD)
                    ctx.paint_with_alpha(reflect_alpha)
                    ctx.restore()
                ctx.set_source_surface(self.lid_shadow, 0, 0)
                ctx.paint()
                ctx.set_source_surface(self.wet, 0, 0)
                ctx.paint()
                # specular highlights: a window and a small kicker
                if spec > 0:
                    hx, hy = ix - self.R * 0.38, iy - self.R * 0.42
                    ctx.save()
                    ctx.translate(hx, hy)
                    ctx.rotate(-0.25)
                    pat = cairo.RadialGradient(0, 0, 0, 0, 0, 34)
                    pat.add_color_stop_rgba(0, 1, 1, 1, 0.95 * spec)
                    pat.add_color_stop_rgba(0.55, 1, 1, 1, 0.85 * spec)
                    pat.add_color_stop_rgba(1, 1, 1, 1, 0)
                    ctx.scale(1.35, 1.0)
                    ctx.arc(0, 0, 34, 0, 2 * math.pi)
                    ctx.set_source(pat)
                    ctx.fill()
                    ctx.restore()
                    ctx.save()
                    ctx.translate(ix, iy)
                    pat = cairo.LinearGradient(0, -self.R, 0, -self.R * 0.2)
                    pat.add_color_stop_rgba(0, 0.75, 0.85, 1.0, 0.16 * spec)
                    pat.add_color_stop_rgba(1, 0.75, 0.85, 1.0, 0.0)
                    ctx.arc(0, 0, self.R * 0.96, math.pi * 1.08, math.pi * 1.92)
                    ctx.close_path()
                    ctx.set_source(pat)
                    ctx.fill()
                    ctx.restore()
                    ctx.arc(ix + self.R * 0.30, iy + self.R * 0.36, 7, 0, 2 * math.pi)
                    ctx.set_source_rgba(1, 1, 1, 0.55 * spec)
                    ctx.fill()
                ctx.restore()
                ctx.set_source_surface(self.lashes, 0, 0)
                ctx.paint()
                ctx.pop_group_to_source()
                ctx.paint_with_alpha(alpha)
            else:
                # bloom: highlight + the reflection
                if spec > 0:
                    ctx.arc(ix - self.R * 0.38, iy - self.R * 0.42, 30, 0, 2 * math.pi)
                    ctx.set_source_rgba(1, 1, 1, 0.55 * spec * alpha)
                    ctx.fill()
                if reflect is not None and reflect_alpha > 0.003:
                    ctx.save()
                    ctx.arc(ix, iy, self.R * 1.02, 0, 2 * math.pi)
                    ctx.clip()
                    ctx.push_group()
                    reflect(ctx, ix, iy, self.R, True)
                    ctx.pop_group_to_source()
                    ctx.paint_with_alpha(reflect_alpha * alpha * 0.8)
                    ctx.restore()
            ctx.restore()

    def screen_point(self, x, y, scale, px, py):
        """Texture point -> screen."""
        return x + (px - EW / 2) * scale, y + (py - EH / 2) * scale
