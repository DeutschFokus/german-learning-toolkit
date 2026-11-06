"""Volumetric effects rendered with numpy: a ray-marched mushroom cloud.

The cloud is a density field (torus cap + dome + stem + base surge) carved by
tileable 3D value noise, marched front to back with emission from the hot core
and cool sky light. It renders at a fraction of the frame size and is
upscaled; bloom and grain in postfx hide the softness.
"""
from __future__ import annotations

import math

import cairo
import numpy as np
from scipy.ndimage import gaussian_filter, map_coordinates

from .gfx import Canvas, clamp, lerp


class Noise3:
    """Tileable 3D value noise (smoothed random grid, trilinear sampling)."""

    def __init__(self, n=40, seed=1):
        rng = np.random.default_rng(seed)
        v = gaussian_filter(rng.random((n, n, n)).astype(np.float32), 1.7, mode="wrap")
        self.v = ((v - v.min()) / (np.ptp(v) + 1e-6)).astype(np.float32)
        self.n = n

    def sample(self, x, y, z):
        return map_coordinates(self.v, np.stack([x, y, z]), order=1, mode="grid-wrap")

    def fbm(self, x, y, z, octaves=3, lac=2.03, gain=0.5):
        acc, amp, tot = 0.0, 1.0, 0.0
        for o in range(octaves):
            acc = acc + amp * self.sample(x, y, z)
            tot += amp
            amp *= gain
            x, y, z = x * lac + 11.3, y * lac + 7.1, z * lac + 3.7
        return acc / tot


def _smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h - k * h * (1 - h)


def blackbody(tk):
    """Rough colour of a glowing gas for a 0..1 'temperature'."""
    tk = np.clip(tk, 0, 1)[..., None]
    c0 = np.array([0.35, 0.05, 0.02], np.float32)    # dull red
    c1 = np.array([1.00, 0.42, 0.10], np.float32)    # orange
    c2 = np.array([1.00, 0.85, 0.55], np.float32)    # yellow-white
    c3 = np.array([1.00, 0.98, 0.95], np.float32)    # white
    a = np.clip(tk * 3, 0, 1)
    b = np.clip(tk * 3 - 1, 0, 1)
    d = np.clip(tk * 3 - 2, 0, 1)
    return c0 * (1 - a) + c1 * a * (1 - b) + c2 * b * (1 - d) + c3 * d - c1 * 0 * a


class MushroomCloud:
    """age: 0 (fireball) .. 1 (mature cloud). Units: cap height ~1, y up.

    The cloud is a few hundred soft puffs (cap ring vortex, dome, stem, base
    surge) splatted into a 3D density grid each frame, broken up with 3D
    noise, then ray-marched front to back with one-tap self-shadowing, sky
    light and emission from the hot core.
    """

    BOX = (-0.95, 0.95, -0.06, 1.84, -0.95, 0.95)

    def __init__(self, seed=3, res=(68, 68, 68), loop=60.0):
        self.loop = loop                          # all motion repeats exactly over this many seconds
        self.noise = Noise3(n=56, seed=seed)
        self.res = res
        rng = np.random.default_rng(seed + 100)
        # puff templates: (kind, u, v, size jitter, phase)
        self.cap = [(rng.uniform(0, 2 * math.pi), rng.uniform(0, 2 * math.pi), rng.uniform(0.75, 1.25))
                    for _ in range(260)]
        self.dome = [(rng.uniform(0, 2 * math.pi), rng.uniform(0.0, 1.0), rng.uniform(0.7, 1.2)) for _ in range(110)]
        self.stem = [(rng.uniform(0, 1), rng.uniform(0, 2 * math.pi), rng.uniform(0.7, 1.3)) for _ in range(90)]
        self.surge = [(rng.uniform(0, 2 * math.pi), rng.uniform(0.2, 1.0), rng.uniform(0.7, 1.3)) for _ in range(90)]
        x0, x1, y0, y1, z0, z1 = self.BOX
        nx, ny, nz = res
        self.gx = np.linspace(x0, x1, nx, dtype=np.float32)
        self.gy = np.linspace(y0, y1, ny, dtype=np.float32)
        self.gz = np.linspace(z0, z1, nz, dtype=np.float32)
        Z, Y, X = np.meshgrid(self.gz, self.gy, self.gx, indexing="ij")
        self.X, self.Y, self.Z = X, Y, Z

    def shape(self, age):
        a = clamp(age)
        rise = 1 - (1 - a) ** 2.2
        Hc = 0.12 + 0.95 * rise                 # cap (ring vortex) height
        R = 0.06 + 0.30 * rise ** 0.8           # ring radius
        r = 0.10 + 0.16 * rise ** 0.7           # tube radius
        stem = 0.035 + 0.045 * rise
        heat = (1 - a) ** 1.6
        return Hc, R, r, stem, heat

    def puffs(self, age, t):
        Hc, R, r, stem, heat = self.shape(age)
        out = []
        roll = 2 * math.pi * 9 * t / self.loop               # 9 turns of the ring vortex per loop
        for th, ph, k in self.cap:                         # ring vortex: rolls up the inside, out over the top
            p = ph + roll
            q = R + r * 0.72 * math.cos(p)
            out.append((q * math.cos(th), Hc + r * 0.62 * math.sin(p), q * math.sin(th), r * 0.40 * k))
        for th, u, k in self.dome:                          # cap top
            rr = (R + r * 0.4) * math.sqrt(u)
            out.append((rr * math.cos(th), Hc + r * (0.55 + 0.5 * (1 - u)), rr * math.sin(th), r * 0.42 * k))
        for u, th, k in self.stem:                          # stem, gas rising through it
            y = ((u + 11 * t / self.loop) % 1.0) * Hc
            w = stem * (1 + 1.7 * math.exp(-y / 0.06))
            out.append((w * 0.35 * math.cos(th + y * 6), y, w * 0.35 * math.sin(th + y * 6), w * 1.05 * k))
        sr = 0.10 + 0.62 * clamp(age * 1.3)
        for th, u, k in self.surge:                         # base surge spreading over the water
            rr = sr * (0.35 + 0.65 * u)
            out.append((rr * math.cos(th), 0.02, rr * math.sin(th), (0.035 + 0.03 * u) * k * (1 - 0.3 * age)))
        return out, (Hc, R, r, heat)

    def grid(self, age, t):
        x0, x1, y0, y1, z0, z1 = self.BOX
        nx, ny, nz = self.res
        sx, sy, sz = (nx - 1) / (x1 - x0), (ny - 1) / (y1 - y0), (nz - 1) / (z1 - z0)
        g = np.zeros((nz, ny, nx), np.float32)
        puffs, info = self.puffs(age, t)
        for (px, py, pz, pr) in puffs:
            i0, i1 = max(0, int((px - pr - x0) * sx)), min(nx, int((px + pr - x0) * sx) + 2)
            j0, j1 = max(0, int((py - pr - y0) * sy)), min(ny, int((py + pr - y0) * sy) + 2)
            k0, k1 = max(0, int((pz - pr - z0) * sz)), min(nz, int((pz + pr - z0) * sz) + 2)
            if i0 >= i1 or j0 >= j1 or k0 >= k1:
                continue
            X = self.X[k0:k1, j0:j1, i0:i1]
            Y = self.Y[k0:k1, j0:j1, i0:i1]
            Z = self.Z[k0:k1, j0:j1, i0:i1]
            d = np.sqrt((X - px) ** 2 + (Y - py) ** 2 + (Z - pz) ** 2) / pr
            f = np.clip(1.2 - d, 0, 1)
            f = f * f * (3 - 2 * f) * 0.85
            sub = g[k0:k1, j0:j1, i0:i1]
            sub[...] = 1 - (1 - sub) * (1 - f)            # soft union: neighbouring puffs merge
        # break the puffs up with drifting noise (fine billows)
        g = gaussian_filter(g, 0.8)
        drift = self.noise.n * t / self.loop                  # one full wrap of the noise per loop
        n = self.noise.fbm(self.X * 9 + 5, self.Y * 9 + 5 - drift, self.Z * 9 + 5, octaves=2, lac=2.0)
        g = np.clip(g * (0.45 + 1.05 * n) - 0.10, 0, 1)
        return g, info

    def render(self, w, h, age, t, view=(-0.9, 0.9, -0.15, 1.75), steps=40,
               sun=(-0.65, 0.55, -0.45), sun_col=(1.0, 0.66, 0.44), sky_col=(0.30, 0.38, 0.58)):
        """Premultiplied RGBA float32 (h, w, 4) of the cloud over transparency.
        view = (x0, x1, y0, y1) in cloud units (y up)."""
        G, (Hc, R, r, heat) = self.grid(age, t)
        bx0, bx1, by0, by1, bz0, bz1 = self.BOX
        nx, ny, nz = self.res
        x0, x1, y0, y1 = view
        xs = np.linspace(x0, x1, w, dtype=np.float32)
        ys = np.linspace(y1, y0, h, dtype=np.float32)
        X, Y = np.meshgrid(xs, ys)
        top = min(by1, Hc + r * 2.2)
        mask = (Y < top) & (Y > by0) & (X > bx0) & (X < bx1)
        idx = np.nonzero(mask)
        px, py = X[idx], Y[idx]
        n = px.size
        col = np.zeros((n, 3), np.float32)
        trans = np.ones(n, np.float32)
        zs = np.linspace(bz0, bz1, steps, dtype=np.float32)
        dz = (bz1 - bz0) / steps
        sigma = 30.0
        L_ = np.array(sun, np.float32)
        L_ /= np.linalg.norm(L_)
        sun_c = np.array(sun_col, np.float32)
        sky_c = np.array(sky_col, np.float32)

        def samp(qx, qy, qz):
            ci = (qx - bx0) / (bx1 - bx0) * (nx - 1)
            cj = (qy - by0) / (by1 - by0) * (ny - 1)
            ck = (qz - bz0) / (bz1 - bz0) * (nz - 1)
            return map_coordinates(G, np.stack([ck, cj, ci]), order=1, mode="constant", cval=0.0)

        for z in zs:
            live = np.nonzero(trans > 0.02)[0]
            if live.size == 0:
                break
            qx, qy = px[live], py[live]
            qz = np.full(live.size, z, np.float32)
            rho = samp(qx, qy, qz)
            m = rho > 0.004
            if not m.any():
                continue
            li = live[m]
            qx, qy, qz, rho = qx[m], qy[m], qz[m], rho[m]
            a = 1 - np.exp(-sigma * rho * dz)
            sh1 = samp(qx + L_[0] * 0.05, qy + L_[1] * 0.05, qz + L_[2] * 0.05)
            sh2 = samp(qx + L_[0] * 0.12, qy + L_[1] * 0.12, qz + L_[2] * 0.12)
            sky = samp(qx, qy + 0.10, qz)
            lit = np.exp(-2.0 * sh1 - 1.6 * sh2)[:, None]
            skyl = np.exp(-1.5 * sky)[:, None]
            dist = np.sqrt(qx ** 2 + (qy - Hc) ** 2 + qz ** 2)
            temp = heat * (np.exp(-dist / (0.08 + 0.22 * r)) * 1.3 + 0.5)
            em = blackbody(temp) * (1.5 * heat * np.exp(-dist / (0.14 + r)))[:, None]
            hgt = np.clip((qy - (Hc - r * 0.9)) / (1.8 * r), 0, 1)[:, None]
            albedo = np.array([0.46, 0.38, 0.34], np.float32) * (1 - hgt) + np.array([0.94, 0.86, 0.80], np.float32) * hgt
            c = albedo * (sun_c * lit * 1.1 * (1 - 0.55 * heat) + sky_c * skyl * 0.36) + em
            col[li] += (trans[li] * a)[:, None] * c
            trans[li] *= 1 - a
        out = np.zeros((h, w, 4), np.float32)
        out[idx[0], idx[1], :3] = col
        out[idx[0], idx[1], 3] = 1 - trans
        return out, (Hc, R, r, heat)


def rgba_surface(img):
    """Premultiplied float RGBA (h, w, 4), RGB order -> cairo ARGB32 surface."""
    h, w = img.shape[:2]
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    stride = s.get_stride()
    buf = np.ndarray((h, stride // 4, 4), np.uint8, s.get_data())
    a = np.clip(img[..., 3], 0, 1)
    rgb = np.clip(img[..., :3], 0, None)
    rgb = np.minimum(rgb, a[..., None])
    buf[:, :w, 0] = (rgb[..., 2] * 255).astype(np.uint8)
    buf[:, :w, 1] = (rgb[..., 1] * 255).astype(np.uint8)
    buf[:, :w, 2] = (rgb[..., 0] * 255).astype(np.uint8)
    buf[:, :w, 3] = (a * 255).astype(np.uint8)
    s.mark_dirty()
    return s


def paint_rgba(cv: Canvas, img, x, y, w, h, alpha=1.0, glow=0.0, glow_img=None):
    """Paint a premultiplied float RGBA image scaled into the rect (x, y, w, h)."""
    s = rgba_surface(img)
    ih, iw = img.shape[:2]
    for ctx, a in ((cv.b, alpha), (cv.g, alpha * glow)):
        if a <= 0.003:
            continue
        src = s if (ctx is cv.b or glow_img is None) else rgba_surface(glow_img)
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(w / iw, h / ih)
        ctx.set_source_surface(src, 0, 0)
        ctx.get_source().set_filter(cairo.FILTER_BILINEAR)
        ctx.paint_with_alpha(a)
        ctx.restore()
