"""Nature props in the LUMEN style: a procedural gnarled bristlecone pine,
mountain ridges, a pre-rendered tree-ring cross-section, a pyramid that
builds itself, and a rubber stamp. Night palette, moonlit rim light.
"""
from __future__ import annotations

import math

import cairo
import numpy as np

from .gfx import L, Canvas, W, H, clamp, ease_out_back, ease_out_cubic, lerp, mix, prog

WOOD_DEAD = (0.62, 0.70, 0.82)      # bleached, moonlit dead wood
WOOD_BODY = (0.05, 0.07, 0.12)
NEEDLE = (0.36, 0.66, 0.52)


def _value_noise(rng, n, smooth=9):
    v = rng.normal(0, 1, n)
    k = np.hanning(smooth + 2)[1:-1]
    k /= k.sum()
    pad = smooth
    return np.convolve(np.concatenate([v[-pad:], v, v[:pad]]), k, mode="same")[pad:-pad]


class Bristlecone:
    """A gnarled, mostly dead tree with a few living limbs and a living bark strip."""

    def __init__(self, seed=3, height=760.0, lean=-0.10, n_limbs=6, alive_limbs=(1, 3), dead_spikes=3):
        rng = np.random.default_rng(seed)
        self.h = height
        self.segs = []
        self.tufts = []
        K = 8
        pts = [(0.0, 0.0)]
        ang = -math.pi / 2 + lean
        seg_len = height * 0.46 / K
        for k in range(K):
            ang += rng.normal(0, 0.16)
            ang = clamp(ang, -math.pi / 2 - 0.55, -math.pi / 2 + 0.55)
            x, y = pts[-1]
            pts.append((x + math.cos(ang) * seg_len, y + math.sin(ang) * seg_len))
        self.trunk = pts
        w_base, w_top = height * 0.27, height * 0.10
        self.trunk_w = []
        for k in range(K):
            u0, u1 = k / K, (k + 1) / K
            w0 = lerp(w_base, w_top, u0 ** 0.7) * (1.55 if k == 0 else 1.0)
            w1 = lerp(w_base, w_top, u1 ** 0.7)
            self.trunk_w.append((w0, w1))
            self.segs.append({"p0": pts[k], "p1": pts[k + 1], "w0": w0, "w1": w1, "depth": 0, "alive": True,
                              "limb": -1})
        # limbs
        for i in range(n_limbs):
            k = int(rng.integers(3, K))
            side = -1 if i % 2 else 1
            a0 = -math.pi / 2 + side * rng.uniform(0.70, 1.35)
            alive = i in alive_limbs
            length = height * rng.uniform(0.30, 0.50) * (1.0 if alive else 0.8)
            width = self.trunk_w[min(k, K - 1)][1] * rng.uniform(0.55, 0.75)
            self._branch(rng, pts[k], a0, length, width, 1, alive, i)
        # bare dead spikes (bristlecones are famous for them)
        for j in range(dead_spikes):
            k = int(rng.integers(K - 3, K + 1))
            a0 = -math.pi / 2 + rng.normal(0, 0.35)
            self._branch(rng, pts[min(k, K)], a0, height * rng.uniform(0.15, 0.28), w_top * 0.5, 2, False, 100 + j)
        self.alive_limbs = alive_limbs

    def _branch(self, rng, p, ang, length, width, depth, alive, limb):
        n = 3 if depth < 3 else 2
        x, y = p
        sub = length / n
        w = width
        for k in range(n):
            ang += rng.normal(0, 0.32)
            ang = clamp(ang, -math.pi + 0.15, -0.15)
            nx, ny = x + math.cos(ang) * sub, y + math.sin(ang) * sub
            w1 = w * 0.78
            self.segs.append({"p0": (x, y), "p1": (nx, ny), "w0": w, "w1": w1, "depth": depth, "alive": alive,
                              "limb": limb})
            if depth < 3 and k == n - 2 and rng.random() < 0.85:
                side = rng.choice([-1, 1])
                self._branch(rng, (nx, ny), ang + side * rng.uniform(0.4, 0.9), length * 0.55, w1 * 0.7,
                             depth + 1, alive, limb)
            x, y, w = nx, ny, w1
        if alive and depth >= 1:
            ux, uy = math.cos(ang), math.sin(ang)
            for q in range(3):
                back = q * sub * 0.45
                self.tufts.append({"x": x - ux * back + rng.normal(0, 4), "y": y - uy * back + rng.normal(0, 4),
                                   "r": self.h * rng.uniform(0.045, 0.065), "seed": int(rng.integers(0, 1e6)),
                                   "limb": limb, "dir": ang})

    # ------------------------------------------------------------------ cached silhouette
    def _cache(self, s):
        if not hasattr(self, "_caches"):
            self._caches = {}
        key = round(s, 3)
        if key in self._caches:
            return self._caches[key]
        import cv2
        polys = []
        for seg in self.segs:
            (x0, y0), (x1, y1) = seg["p0"], seg["p1"]
            dx, dy = x1 - x0, y1 - y0
            d = math.hypot(dx, dy) + 1e-6
            nx, ny = -dy / d, dx / d
            w0, w1 = seg["w0"] / 2, seg["w1"] / 2
            polys.append(([(x0 + nx * w0, y0 + ny * w0), (x1 + nx * w1, y1 + ny * w1),
                           (x1 - nx * w1, y1 - ny * w1), (x0 - nx * w0, y0 - ny * w0)], (x1, y1, w1)))
        pts = np.array([q for poly, _ in polys for q in poly] +
                       [(tf["x"], tf["y"]) for tf in self.tufts]) * s
        pad = 60
        minx, miny = pts.min(axis=0) - pad
        maxx, maxy = pts.max(axis=0) + pad
        Wc, Hc = int(maxx - minx), int(maxy - miny)
        ox, oy = -minx, -miny
        m = cairo.ImageSurface(cairo.FORMAT_A8, Wc, Hc)
        c = cairo.Context(m)
        c.translate(ox, oy)
        c.scale(s, s)
        c.set_source_rgba(0, 0, 0, 1)
        bw = self.trunk_w[0][0]
        c.save()
        c.translate(0, -self.h * 0.012)
        c.scale(bw * 0.75, self.h * 0.05)
        c.arc(0, 0, 1, math.pi, 2 * math.pi)
        c.restore()
        c.close_path()
        c.fill()
        for poly, (jx, jy, jw) in polys:
            c.move_to(*poly[0])
            for q in poly[1:]:
                c.line_to(*q)
            c.close_path()
            c.fill()
            c.arc(jx, jy, jw * 0.98, 0, 2 * math.pi)
            c.fill()
        stride = m.get_stride()
        arr = np.ndarray((Hc, stride), np.uint8, m.get_data())[:, :Wc].astype(np.float32) / 255
        arr = cv2.GaussianBlur(arr, (0, 0), 0.9)
        k = max(3, int(3 * s)) | 1
        er = cv2.erode(arr, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
        edge = np.clip((arr - er) * 1.7, 0, 1)
        from .figure import _a8_from_array
        mask_s, edge_s = _a8_from_array(arr), _a8_from_array(edge)
        # twisted grain + bark detail, clipped to the silhouette
        det = cairo.ImageSurface(cairo.FORMAT_ARGB32, Wc, Hc)
        dc = cairo.Context(det)
        dc.translate(ox, oy)
        dc.set_line_width(max(1.0, 1.5 * s))
        tp = [(px * s, py * s) for px, py in self.trunk]
        for j in range(9):
            dc.new_path()
            for i, (px, py) in enumerate(tp[:-1]):
                w0 = self.trunk_w[i][0] * s / 2
                lane = (j / 8) * 2 - 1                      # parallel lanes across the trunk
                off = (lane * 0.80 + 0.18 * math.sin(i * 0.8 + 0.6)) * w0   # shared twist, no crossings
                qx, qy = tp[i + 1]
                dx, dy = qx - px, qy - py
                d = math.hypot(dx, dy) + 1e-6
                if i == 0:
                    dc.move_to(px - dy / d * off, py + dx / d * off)
                dc.line_to(qx - dy / d * off, qy + dx / d * off)
            dc.set_source_rgba(*WOOD_DEAD, 0.30)
            dc.stroke()
        for seg in self.segs:
            if seg["depth"] == 0:
                continue
            (x0, y0), (x1, y1) = seg["p0"], seg["p1"]
            dc.new_path()
            dc.move_to(x0 * s, y0 * s)
            dc.line_to(x1 * s, y1 * s)
            dc.set_source_rgba(*WOOD_DEAD, 0.16)
            dc.stroke()
        det.flush()
        da = np.ndarray((Hc, Wc, 4), np.uint8, det.get_data())
        da[:] = (da.astype(np.float32) * arr[..., None]).astype(np.uint8)
        det.mark_dirty()
        self._caches[key] = (mask_s, edge_s, det, ox, oy)
        return self._caches[key]

    def draw(self, cv: Canvas, x, y, s=1.0, alpha=1.0, t=0.0, sway=0.0, strip=0.0, foliage=1.0, glow=0.6,
             dim_dead=1.0, alive_glow=0.0, rim=WOOD_DEAD, rot=0.0, cut=None, body=(0.075, 0.09, 0.14)):
        """Base of the trunk at (x, y). rot rotates the tree about its base (or about the cut line
        when cut=(cut_y_local, fall_angle) is given: the stump stays, the rest falls)."""
        if alpha <= 0.003:
            return
        mask_s, edge_s, det, ox, oy = self._cache(s)
        Hs = mask_s.get_height()
        Ws = mask_s.get_width()

        def paint(ctx, glow_layer):
            if glow_layer:
                ctx.set_source_rgba(*rim, alpha * 0.55 * glow)
                ctx.mask_surface(edge_s, -ox, -oy)
                return
            ctx.set_source_rgba(*body, alpha)
            ctx.mask_surface(mask_s, -ox, -oy)
            ctx.set_source_surface(det, -ox, -oy)
            ctx.paint_with_alpha(alpha)
            ctx.set_source_rgba(*rim, alpha * 0.85)
            ctx.mask_surface(edge_s, -ox, -oy)

        parts = [(None, rot)] if cut is None else [("stump", 0.0), ("top", cut[1])]
        for which, ang in parts:
            for ci, ctx in enumerate((cv.b, cv.g)):
                if ci == 1 and glow <= 0:
                    continue
                ctx.save()
                if which is None:
                    ctx.translate(x, y)
                    ctx.rotate(ang)
                else:
                    cy_l = cut[0] * s
                    if which == "stump":
                        ctx.translate(x, y)
                        ctx.rectangle(-Ws, cy_l, 2 * Ws, Hs)
                        ctx.clip()
                    else:
                        ctx.translate(x, y + cy_l)
                        ctx.rotate(ang)
                        ctx.translate(0, -cy_l)
                        ctx.rectangle(-Ws, -Hs, 2 * Ws, Hs + cy_l)
                        ctx.clip()
                paint(ctx, ci == 1)
                ctx.restore()
        # foliage + living strip go with the moving part
        fa = foliage
        top_ang = rot if cut is None else cut[1]
        piv = (x, y) if cut is None else (x, y + cut[0] * s)

        def T(px, py):
            lx, ly = px * s, py * s
            if cut is not None:
                ly -= cut[0] * s
            ca, sa = math.cos(top_ang), math.sin(top_ang)
            return (piv[0] + lx * ca - ly * sa, piv[1] + lx * sa + ly * ca)

        if strip > 0:
            pts = []
            for k, (px, py) in enumerate(self.trunk):
                w0 = self.trunk_w[min(k, len(self.trunk_w) - 1)][0] / 2
                pts.append(T(px + w0 * 0.40, py) if cut is None else (x + (px + w0 * 0.4) * s, y + py * s))
            n = max(2, int(len(pts) * clamp(strip)))
            for ctx, wmul, amul in ((cv.b, 1.0, 0.95), (cv.g, 1.8, 0.9)):
                ctx.new_path()
                ctx.move_to(*pts[0])
                for q in pts[1:n]:
                    ctx.line_to(*q)
                ctx.set_line_width(max(3.0, self.h * 0.026 * s) * wmul)
                ctx.set_source_rgba(*L.AMBER, alpha * amul)
                ctx.stroke()
        if fa > 0:
            b = cv.b
            for tf in self.tufts:
                cx_, cy_ = T(tf["x"], tf["y"])
                r = tf["r"] * s
                rng = np.random.default_rng(tf["seed"])
                if glow > 0:
                    cv.radial(cx_, cy_, r * 1.5, NEEDLE, alpha=0.16 * alpha * fa, glow=glow * 0.7, layer_base=False)
                b.set_line_width(max(1.0, 1.5 * s))
                d0 = tf.get("dir", -math.pi / 2) + top_ang
                for q in range(30):
                    u = rng.uniform(-1, 1)
                    bx = cx_ + math.cos(d0) * u * r * 0.9
                    by = cy_ + math.sin(d0) * u * r * 0.9
                    a = d0 + math.pi / 2 * rng.choice([-1, 1]) + rng.normal(0, 0.35)
                    rr = r * rng.uniform(0.25, 0.55)
                    b.set_source_rgba(*NEEDLE, alpha * fa * rng.uniform(0.25, 0.6))
                    b.move_to(bx, by)
                    b.line_to(bx + math.cos(a) * rr, by + math.sin(a) * rr)
                    b.stroke()

    def top(self, x, y, s=1.0):
        lx, ly = self.trunk[-1]
        return (x + lx * s, y + ly * s)


# --------------------------------------------------------------------------- landscape

class Ridges:
    """Layered mountain silhouettes. Deterministic; the near ridge has a summit at (peak_x, peak_y)."""

    def __init__(self, seed=5, peak_x=W / 2, peak_y=1190.0):
        rng = np.random.default_rng(seed)
        self.layers = []
        xs = np.linspace(-60, W + 60, 260)
        for k, (base, amp, col, a) in enumerate((
                (1030.0, 180.0, (0.06, 0.09, 0.19), 1.0),
                (1120.0, 150.0, (0.04, 0.06, 0.13), 1.0),
                (peak_y, 0.0, (0.02, 0.03, 0.07), 1.0))):
            if k < 2:
                n = (_value_noise(rng, len(xs), 31) * 2.2 + np.sin(xs / (180 + 70 * k) + rng.uniform(0, 6)) * 0.8
                     + 0.25 * _value_noise(rng, len(xs), 7))
                ys = base - amp * (0.5 + 0.5 * n / (np.abs(n).max() + 1e-6))
            else:
                ys = peak_y + 0.00045 * (xs - peak_x) ** 2 + 18 * _value_noise(rng, len(xs)) / 2.5
            self.layers.append((xs, ys, col, a))

    def draw(self, cv: Canvas, alpha=1.0, rim=0.6):
        b = cv.b
        for k, (xs, ys, col, a) in enumerate(self.layers):
            b.new_path()
            b.move_to(xs[0], H + 10)
            for xx, yy in zip(xs, ys):
                b.line_to(xx, yy)
            b.line_to(xs[-1], H + 10)
            b.close_path()
            b.set_source_rgba(*col, a * alpha)
            b.fill()
            if rim > 0:
                b.new_path()
                for i, (xx, yy) in enumerate(zip(xs, ys)):
                    (b.move_to if i == 0 else b.line_to)(xx, yy)
                b.set_line_width(1.6)
                b.set_source_rgba(0.55, 0.7, 1.0, (0.18 + 0.12 * k) * alpha * rim)
                b.stroke()

    def y_at(self, x, layer=2):
        xs, ys, _, _ = self.layers[layer]
        return float(np.interp(x, xs, ys))


def moon(cv: Canvas, x, y, r, alpha=1.0, glow=0.35):
    """A big pale moon with soft maria and a gentle halo (kept out of the bloom so it stays a disc)."""
    if alpha <= 0.003:
        return
    cv.radial(x, y, r * 2.4, (0.45, 0.6, 0.95), alpha=0.16 * alpha, glow=0)
    pat = cairo.RadialGradient(x - r * 0.3, y - r * 0.35, r * 0.1, x, y, r)
    pat.add_color_stop_rgba(0, 0.93, 0.93, 0.90, 0.92 * alpha)
    pat.add_color_stop_rgba(1, 0.70, 0.75, 0.84, 0.92 * alpha)
    cv.b.new_path()
    cv.b.arc(x, y, r, 0, 2 * math.pi)
    cv.b.set_source(pat)
    cv.b.fill()
    rng = np.random.default_rng(2)
    for k in range(7):
        a, d = rng.uniform(0, 2 * math.pi), rng.uniform(0.1, 0.6)
        rr = r * rng.uniform(0.14, 0.30)
        mx, my = x + math.cos(a) * r * d, y + math.sin(a) * r * d
        pat2 = cairo.RadialGradient(mx, my, 0, mx, my, rr)
        pat2.add_color_stop_rgba(0, 0.50, 0.55, 0.66, 0.22 * alpha)
        pat2.add_color_stop_rgba(1, 0.50, 0.55, 0.66, 0.0)
        cv.b.new_path()
        cv.b.arc(mx, my, rr, 0, 2 * math.pi)
        cv.b.set_source(pat2)
        cv.b.fill()
    if glow > 0:
        cv.g.new_path()
        cv.g.arc(x, y, r * 1.02, 0, 2 * math.pi)
        cv.g.set_line_width(r * 0.10)
        cv.g.set_source_rgba(0.75, 0.85, 1.0, 0.5 * glow * alpha)
        cv.g.stroke()


# --------------------------------------------------------------------------- tree rings

class RingSection:
    """Pre-rendered stump cross-section: eccentric, cracked, ~280 visible rings."""

    def __init__(self, size=980, seed=9, n_rings=280):
        rng = np.random.default_rng(seed)
        self.size = size
        self.surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
        c = cairo.Context(self.surf)
        cx = cy = size / 2
        R = size * 0.46
        # pith off-centre: strip-bark trees grow lopsided
        px, py = cx - R * 0.16, cy + R * 0.10
        self.pith = (px, py)
        self.R = R
        th = np.linspace(0, 2 * np.pi, 360, endpoint=False)
        shape = 1 + 0.06 * np.sin(3 * th + 0.4) + 0.04 * np.sin(5 * th + 1.3) + 0.03 * _value_noise(rng, 360)
        widths = np.clip(rng.gamma(2.0, 1.0, n_rings), 0.25, 4.5)
        widths[: n_rings // 6] *= 2.2          # fast youth, slow old age
        radii = np.cumsum(widths)
        radii = radii / radii[-1]
        # bark + body
        def ring_path(frac, jitter=0.0):
            rr = frac * R * shape * (1 + jitter)
            # blend centre from pith to geometric centre as rings grow
            ox = lerp(px, cx, frac ** 0.6)
            oy = lerp(py, cy, frac ** 0.6)
            c.new_path()
            for i, (a, r_) in enumerate(zip(th, rr)):
                X, Y = ox + math.cos(a) * r_, oy + math.sin(a) * r_
                (c.move_to if i == 0 else c.line_to)(X, Y)
            c.close_path()
        ring_path(1.04)
        c.set_source_rgb(0.20, 0.12, 0.07)
        c.fill()
        ring_path(1.0)
        c.set_source_rgb(0.80, 0.62, 0.40)
        c.fill()
        for k, f in enumerate(radii):
            ring_path(f, 0.002 * rng.normal())
            late = 0.35 + 0.25 * rng.random()
            c.set_source_rgba(0.42, 0.26, 0.13, late)
            c.set_line_width(0.7 + 1.4 * widths[k] / 4.5)
            c.stroke()
        # cracks
        c.set_source_rgba(0.12, 0.07, 0.04, 0.85)
        for k in range(7):
            a = rng.uniform(0, 2 * np.pi)
            r0, r1 = rng.uniform(0.15, 0.5), rng.uniform(0.75, 1.0)
            c.set_line_width(rng.uniform(1.5, 4.0))
            c.move_to(cx + math.cos(a) * R * r0, cy + math.sin(a) * R * r0)
            c.line_to(cx + math.cos(a + rng.normal(0, 0.05)) * R * r1, cy + math.sin(a + rng.normal(0, 0.05)) * R * r1)
            c.stroke()
        # saw marks
        c.set_source_rgba(1, 1, 1, 0.05)
        for k in range(60):
            yy = k / 60 * size
            c.set_line_width(2)
            c.move_to(0, yy)
            c.line_to(size, yy + 30)
            c.stroke()
        self.ring_radii = radii

    def draw(self, cv: Canvas, x, y, scale=1.0, alpha=1.0):
        if alpha <= 0.003:
            return
        b = cv.b
        b.save()
        b.translate(x - self.size * scale / 2, y - self.size * scale / 2)
        b.scale(scale, scale)
        b.set_source_surface(self.surf, 0, 0)
        b.paint_with_alpha(alpha)
        b.restore()

    def to_screen(self, x, y, scale, fx, fy):
        return (x + (fx - self.size / 2) * scale, y + (fy - self.size / 2) * scale)


# --------------------------------------------------------------------------- objects

def pyramid(cv: Canvas, x, y, size, build=1.0, alpha=1.0, color=(0.95, 0.78, 0.45), glow=0.5):
    """Base centre at (x, y); size = base width. build 0..1 stacks courses from the bottom."""
    if alpha <= 0.003 or build <= 0:
        return
    h = size * 0.64
    courses = 14
    shown = build * courses
    for k in range(courses):
        f = clamp(shown - k)
        if f <= 0:
            break
        y0 = y - h * k / courses
        y1 = y - h * (k + 1) / courses
        w0 = size * (1 - k / courses) / 2
        w1 = size * (1 - (k + 1) / courses) / 2
        drop = (1 - ease_out_cubic(f)) * 40
        cv.poly([(x - w0, y0 - drop), (x + w0, y0 - drop), (x + w1, y1 - drop), (x - w1, y1 - drop)],
                mix((0.10, 0.08, 0.06), color, 0.35 + 0.4 * (k / courses)), alpha=alpha * f)
        cv.line([(x - w0, y0 - drop), (x + w0, y0 - drop)], color, width=1.5, alpha=alpha * f * 0.6)
    if build >= 0.999:
        cv.line([(x - size / 2, y), (x, y - h), (x + size / 2, y)], color, width=3, alpha=alpha, glow=glow)


def stamp(cv: Canvas, text, x, y, size=54, angle=-0.12, color=L.MAGENTA, alpha=1.0, pop=0.0, sub=None):
    if alpha <= 0.003:
        return
    from .gfx import text_width
    w = text_width(cv.b, text, size, L.DISPLAY, 0.06) + size * 0.9
    if sub:
        w = max(w, text_width(cv.b, sub, size * 0.42, L.MONO_XB, 0.12) + size * 0.9)
    h = size * (1.6 if not sub else 2.3)
    s = 1 + 0.35 * pop
    with cv.transform(s=s, rot=angle, cx=x, cy=y):
        cv.rect(x - w / 2, y - h / 2, w, h, color, alpha=alpha * 0.10, radius=10)
        cv.rect(x - w / 2, y - h / 2, w, h, color, alpha=alpha, fill=False, width=5, radius=10, glow=0.5)
        cv.rect(x - w / 2 + 9, y - h / 2 + 9, w - 18, h - 18, color, alpha=alpha * 0.6, fill=False, width=2, radius=6)
        ty = y - (size * 0.35 if sub else 0)
        cv.text(text, x, ty, size, color=color, alpha=alpha, tracking=0.06, glow=0.3)
        if sub:
            cv.text(sub, x, y + size * 0.62, size * 0.42, font=L.MONO_XB, color=color, alpha=alpha, tracking=0.12)
