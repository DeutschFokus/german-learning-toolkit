"""Biology & data props for EP005 (bomb-pulse dating), reusable elsewhere.

- C14Chart: the real Northern-Hemisphere atmospheric 14C record (Hua et al. 2022)
  as a luminous chart that can morph into a circular clock.
- Leaf: a backlit leaf with a vein network (numpy texture).
- cow_path / grazing animal silhouette, Cell (dividing, metaball membrane),
  dna_helix (3D, depth-sorted), FatCells, heart, Brain (folds from noise
  contours), Lens (growth shells, sutures), eye_side (cross-section with rays).
"""
from __future__ import annotations

import math
from pathlib import Path

import cairo
import cv2
import numpy as np

from .gfx import L, Canvas, clamp, ease_out_cubic, lerp, mix, smooth

DATA = Path(__file__).resolve().parent / "data"


def _surf(rgb, a):
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


def paint(cv: Canvas, surf, x, y, scale=1.0, alpha=1.0, glow=0.0, rot=0.0, anchor=(0.5, 0.5)):
    """Paint a cairo surface centred (anchor) at (x, y)."""
    w, h = surf.get_width(), surf.get_height()
    for ctx, a in ((cv.b, alpha), (cv.g, alpha * glow)):
        if a <= 0.003:
            continue
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(rot)
        ctx.scale(scale, scale)
        ctx.translate(-w * anchor[0], -h * anchor[1])
        ctx.set_source_surface(surf, 0, 0)
        ctx.get_source().set_filter(cairo.FILTER_GOOD)
        ctx.paint_with_alpha(a)
        ctx.restore()


# =========================================================================== the bomb curve

class C14Chart:
    """F14C (1 = natural level) by year, Northern Hemisphere zone 1, monthly."""

    def __init__(self):
        d = np.loadtxt(DATA / "c14_nh1_monthly.txt", comments="#")
        yr = 1950 - d[:, 0]
        F = np.exp(-d[:, 1] / 8033.0)
        o = np.argsort(yr)
        self.year, self.F = yr[o], F[o]
        k = np.ones(3) / 3
        self.Fs = np.convolve(np.pad(self.F, 1, mode="edge"), k, mode="valid")

    def level(self, year):
        return float(np.interp(year, self.year, self.Fs))

    def year_for(self, F, after=1964.0):
        """Year on the falling branch where the level was F."""
        m = self.year >= after
        y, f = self.year[m], self.Fs[m]
        return float(np.interp(-F, -f, y))

    def peak(self):
        i = int(np.argmax(self.F))
        return float(self.year[i]), float(self.F[i])

    def xy(self, year, F, box, yr=(1950.0, 2020.0), fr=(0.9, 2.05)):
        x0, y0, w, h = box
        return x0 + (year - yr[0]) / (yr[1] - yr[0]) * w, y0 + h - (F - fr[0]) / (fr[1] - fr[0]) * h

    def polar(self, year, F, c, r0, k, yr=(1950.0, 2020.0)):
        a = -math.pi / 2 + (year - yr[0]) / (yr[1] - yr[0]) * 2 * math.pi * 0.96
        r = r0 + (F - 1.0) * k
        return c[0] + math.cos(a) * r, c[1] + math.sin(a) * r

    def points(self, box, upto=2020.0, morph=0.0, center=(540, 960), r0=250.0, k=260.0, start=1950.0,
               step=0.25):
        out = []
        y = start
        while y <= upto:
            F = self.level(y)
            p = self.xy(y, F, box)
            if morph > 0:
                q = self.polar(y, F, center, r0, k)
                p = (lerp(p[0], q[0], morph), lerp(p[1], q[1], morph))
            out.append(p)
            y += step
        return out


# =========================================================================== leaf

class Leaf:
    """A backlit leaf (texture), petiole at the bottom, tip at the top."""

    def __init__(self, length=900, width=560, seed=3):
        rng = np.random.default_rng(seed)
        H, W = length + 60, width + 60
        cx = W / 2
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        v = np.clip((H - 40 - yy) / length, 0, 1)                    # 0 at base, 1 at tip
        hw = width / 2 * np.clip(np.sin(np.pi * np.clip(v, 0, 1)), 0, 1) ** 0.75 * (1 - 0.30 * v) * (v > 0)
        bend = 18 * np.sin(v * np.pi)
        dx = xx - cx - bend
        inside = (np.abs(dx) < hw) & (v > 0.0) & (v < 1.0)
        edge = np.clip((hw - np.abs(dx)) / 3.0, 0, 1) * inside
        # veins
        vm = np.zeros((H, W), np.uint8)
        pts = [(cx + 18 * math.sin(t * math.pi), H - 40 - t * length) for t in np.linspace(0, 1, 60)]
        cv2.polylines(vm, [np.array(pts, np.int32)], False, 255, 7, cv2.LINE_AA)
        for k in range(14):
            t0 = 0.08 + k * 0.062
            for sgn in (-1, 1):
                x, y = cx + 18 * math.sin(t0 * math.pi), H - 40 - t0 * length
                ang = math.pi / 2 + sgn * (0.95 - 0.25 * t0)
                ln = width * 0.48 * math.sin(math.pi * min(1, t0 + 0.08)) ** 0.7
                seg = []
                for j in range(26):
                    q = j / 25
                    seg.append((x + sgn * ln * q, y - ln * q * (0.35 + 0.45 * q)))
                cv2.polylines(vm, [np.array(seg, np.int32)], False, 255, 3, cv2.LINE_AA)
        # tertiary network: Delaunay edges of random points
        sub = cv2.Subdiv2D((0, 0, W, H))
        for _ in range(900):
            px, py = rng.uniform(5, W - 5), rng.uniform(5, H - 5)
            sub.insert((float(px), float(py)))
        for e in sub.getEdgeList():
            p, q = (int(e[0]), int(e[1])), (int(e[2]), int(e[3]))
            if 0 <= p[0] < W and 0 <= q[0] < W and 0 <= p[1] < H and 0 <= q[1] < H:
                cv2.line(vm, p, q, 110, 1, cv2.LINE_AA)
        veins = cv2.GaussianBlur(vm.astype(np.float32) / 255, (0, 0), 0.9)
        n = cv2.GaussianBlur(rng.random((H, W)).astype(np.float32), (0, 0), 6)
        n = (n - n.min()) / (np.ptp(n) + 1e-6)
        rim = np.clip(1 - (hw - np.abs(dx)) / (0.22 * width + 1), 0, 1) * inside
        light = np.clip(1.2 - np.hypot((xx - cx * 0.9) / W, (yy - H * 0.35) / H) * 1.4, 0.2, 1)
        base = np.array([0.30, 0.62, 0.16], np.float32)
        deep = np.array([0.08, 0.30, 0.10], np.float32)
        col = base * (1 - rim[..., None] * 0.7) + deep * rim[..., None] * 0.7
        col = col * (0.75 + 0.45 * n[..., None]) * light[..., None]
        col = col * (1 - 0.35 * veins[..., None]) + np.array([0.85, 0.95, 0.45]) * 0.45 * veins[..., None]
        petiole = (np.abs(xx - cx) < 6) & (yy > H - 46) & (yy < H - 2)
        a = np.maximum(edge, petiole.astype(np.float32))
        col[petiole] = (0.30, 0.50, 0.14)
        self.surf = _surf(col, a.astype(np.float32))
        self.size = (W, H)
        self.base_xy = (cx, H - 40)


# =========================================================================== animal + human glyphs

def cow_points():
    """A grazing cow in profile, facing right, ground at y=340 (box 0..600)."""
    P = [(40, 72), (110, 60), (230, 56), (330, 58), (390, 52), (430, 70), (470, 112), (505, 170), (520, 205),
         (540, 232), (556, 268), (562, 300), (552, 318), (528, 316), (505, 298), (482, 262), (452, 228),
         (418, 214), (402, 236), (400, 330), (386, 340), (368, 340), (366, 246), (352, 238), (300, 243),
         (240, 242), (182, 236), (168, 250), (160, 330), (148, 340), (128, 340), (126, 262), (104, 214),
         (80, 176), (58, 136), (44, 100)]
    return P


def smooth_path(ctx, pts, closed=True, tension=0.5):
    n = len(pts)
    ctx.new_path()
    ctx.move_to(*pts[0])
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) * tension / 3, p1[1] + (p2[1] - p0[1]) * tension / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * tension / 3, p2[1] - (p3[1] - p1[1]) * tension / 3)
        ctx.curve_to(*c1, *c2, *p2)
    if closed:
        ctx.close_path()


def hologram_shape(cv: Canvas, pts, x, y, s, color, alpha=1.0, fill=0.10, glow=0.8, t=0.0, scan=True):
    """Glowing outline + faint fill + scanlines for any closed silhouette (points in local px)."""
    if alpha <= 0.003:
        return
    P = [(x + px * s, y + py * s) for px, py in pts]
    for ctx, gl in ((cv.b, False), (cv.g, True)):
        if gl and glow <= 0:
            continue
        smooth_path(ctx, P)
        ctx.set_source_rgba(*color, alpha * (fill if not gl else fill * glow))
        ctx.fill_preserve()
        ctx.set_source_rgba(*color, alpha * (0.95 if not gl else 0.8 * glow))
        ctx.set_line_width(3.0 if not gl else 5.0)
        ctx.stroke()
    if scan:
        ctx = cv.b
        ctx.save()
        smooth_path(ctx, P)
        ctx.clip()
        ys = min(p[1] for p in P)
        ye = max(p[1] for p in P)
        yy = ys + (t * 90) % 12
        ctx.set_line_width(1.0)
        while yy < ye:
            ctx.move_to(min(p[0] for p in P), yy)
            ctx.line_to(max(p[0] for p in P), yy)
            yy += 12
        ctx.set_source_rgba(*color, 0.18 * alpha)
        ctx.stroke()
        ctx.restore()


# =========================================================================== cells

def cell_outline(cx, cy, r, split, res=360):
    """Membrane of a dividing cell: metaball of two daughter centres; split 0..1."""
    d = r * 1.05 * split
    g = np.linspace(-r * 2.3, r * 2.3, res, dtype=np.float32)
    X, Y = np.meshgrid(g, g * 0.9)
    k = r * (1 - 0.18 * split)
    f = k * k / ((X - d) ** 2 + Y ** 2 + 1e-3) + k * k / ((X + d) ** 2 + Y ** 2 + 1e-3)
    f = f * (1 + 0.04 * np.sin(np.arctan2(Y, X) * 7))
    m = (f > 1.0).astype(np.uint8)
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    out = []
    step = (g[-1] - g[0]) / (res - 1)
    for c in cs:
        c = c[:, 0, :][::3]
        out.append([(cx + g[0] + px * step, cy + (g[0] + py * step) * 0.9) for px, py in c])
    return out, d


def draw_cell(cv: Canvas, cx, cy, r, split=0.0, t=0.0, alpha=1.0, color=L.CYAN, nucleus=(0.55, 0.85, 1.0)):
    if alpha <= 0.003:
        return
    outs, d = cell_outline(cx, cy, r, split)
    for poly in outs:
        if len(poly) < 6:
            continue
        for ctx, gl in ((cv.b, False), (cv.g, True)):
            smooth_path(ctx, poly)
            if not gl:
                pat = cairo.RadialGradient(cx, cy - r * 0.3, r * 0.1, cx, cy, r * 2.0)
                pat.add_color_stop_rgba(0, 0.10, 0.22, 0.32, 0.75 * alpha)
                pat.add_color_stop_rgba(1, 0.03, 0.08, 0.14, 0.85 * alpha)
                ctx.set_source(pat)
                ctx.fill_preserve()
            ctx.set_source_rgba(*color, alpha * (0.95 if not gl else 0.7))
            ctx.set_line_width(4 if not gl else 7)
            ctx.stroke()
    rng = np.random.default_rng(7)
    for sgn in ((-1, 1) if split > 0.02 else (0,)):
        nx = cx + sgn * d
        nr = r * (0.42 - 0.08 * split)
        cv.circle(nx, cy, nr, nucleus, alpha=0.30 * alpha, glow=0.4)
        cv.circle(nx, cy, nr, nucleus, alpha=0.9 * alpha, fill=False, width=2.5, glow=0.6)
        for k in range(14):
            a = rng.uniform(0, 2 * math.pi) + t * 0.3
            rr = rng.uniform(nr * 1.25, r * 0.85)
            cv.circle(nx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.9, rng.uniform(2, 5), (0.5, 0.8, 0.9),
                      alpha=0.55 * alpha)


# =========================================================================== DNA

def dna_helix(cv: Canvas, x, y, length, radius, t, alpha=1.0, turns=3.2, built=1.0, glow_from=None, glow_col=L.AMBER,
              rot=0.0, n=120, phase_speed=1.2):
    """Vertical double helix centred on x, from y (top) downwards. built: fraction assembled from the bottom.
    glow_from: (y0, y1) fraction band of freshly made rungs that glow."""
    if alpha <= 0.003:
        return
    items = []
    for i in range(n):
        s = i / (n - 1)
        if s < 1 - built:
            continue
        yy = y + s * length
        a = 2 * math.pi * turns * s + t * phase_speed
        for strand, off in ((0, 0.0), (1, 2.3)):
            ca, sa = math.cos(a + off), math.sin(a + off)
            items.append((sa, "b", x + ca * radius, yy, strand, s))
        if i % 3 == 0:
            p1 = (x + math.cos(a) * radius, yy, math.sin(a))
            p2 = (x + math.cos(a + 2.3) * radius, yy, math.sin(a + 2.3))
            items.append(((p1[2] + p2[2]) / 2 - 0.01, "r", p1, p2, i, s))
    items.sort(key=lambda it: it[0])
    for it in items:
        z = it[0]
        depth = 0.45 + 0.55 * (z + 1) / 2
        if it[1] == "b":
            _, _, px, py, strand, s = it
            col = (0.55, 0.85, 1.0) if strand == 0 else (0.75, 0.70, 1.0)
            hot = glow_from is not None and glow_from[0] <= s <= glow_from[1]
            if hot:
                col = mix(col, glow_col, 0.85)
            cv.circle(px, py, radius * 0.10 * (0.7 + 0.5 * depth), col, alpha=alpha * depth,
                      glow=(0.9 if hot else 0.35) * depth)
        else:
            _, _, p1, p2, i, s = it
            hot = glow_from is not None and glow_from[0] <= s <= glow_from[1]
            base_cols = ((0.95, 0.45, 0.55), (0.45, 0.95, 0.65), (0.98, 0.80, 0.35), (0.45, 0.65, 1.0))
            c1 = base_cols[i % 4]
            c2 = base_cols[(i + 2) % 4]
            mx_, my_ = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
            if hot:
                c1 = c2 = glow_col
            cv.line([(p1[0], p1[1]), (mx_, my_)], c1, width=radius * 0.06 * (0.6 + 0.6 * depth),
                    alpha=alpha * depth * 0.9, glow=0.5 if hot else 0.0)
            cv.line([(mx_, my_), (p2[0], p2[1])], c2, width=radius * 0.06 * (0.6 + 0.6 * depth),
                    alpha=alpha * depth * 0.9, glow=0.5 if hot else 0.0)


# =========================================================================== fat cells

class FatCells:
    def __init__(self, n=34, radius=260, seed=4):
        rng = np.random.default_rng(seed)
        cells = []
        tries = 0
        while len(cells) < n and tries < 20000:
            tries += 1
            r = rng.uniform(34, 60)
            a = rng.uniform(0, 2 * math.pi)
            d = math.sqrt(rng.uniform(0, 1)) * (radius - r)
            x, y = math.cos(a) * d, math.sin(a) * d
            if all(math.hypot(x - c[0], y - c[1]) > r + c[2] - 6 for c in cells):
                cells.append((x, y, r, rng.uniform(0, 1)))
        self.cells = cells
        self.radius = radius

    def draw(self, cv: Canvas, x, y, s=1.0, alpha=1.0, years=0.0, rate=0.10, t=0.0):
        """years: elapsed simulated years; each cell renews with probability `rate` per year."""
        if alpha <= 0.003:
            return
        yr = int(years)
        fr = years - yr
        for i, (cx_, cy_, r, ph) in enumerate(self.cells):
            # deterministic renewal schedule: cell i renews in year k if hash < rate
            renew = ((i * 7919 + yr * 104729) % 1000) / 1000.0 < rate and years > 0
            pop = 0.0
            if renew:
                pop = clamp(1 - fr * 1.6)
            rr = r * s * (1 - 0.35 * pop * (1 - pop) * 4 * 0.3)
            px, py = x + cx_ * s, y + cy_ * s
            col = mix((1.0, 0.82, 0.42), (1.0, 1.0, 0.95), pop)
            cv.circle(px, py, rr, col, alpha=alpha * (0.22 + 0.4 * pop), glow=0.6 * pop)
            cv.circle(px, py, rr, col, alpha=alpha * 0.85, fill=False, width=2.2, glow=0.25 + 0.6 * pop)
            cv.circle(px + rr * 0.45, py - rr * 0.35, rr * 0.13, (0.8, 0.6, 0.35), alpha=alpha * 0.6)


# =========================================================================== heart

def heart_points():
    """Anatomical-ish heart (front view), local box ~0..300 x 0..340, apex bottom-left (patient's left)."""
    return [(96, 70), (128, 52), (168, 50), (206, 58), (238, 76), (262, 108), (272, 150), (266, 196), (246, 236),
            (214, 276), (172, 310), (132, 330), (100, 318), (70, 286), (46, 240), (38, 190), (44, 140), (64, 100)]


def draw_heart(cv: Canvas, x, y, s, t, alpha=1.0, beat=1.0, bpm=60.0, color=(1.0, 0.32, 0.42)):
    """Centred at (x, y). Beats with a lub-dub at bpm."""
    if alpha <= 0.003:
        return
    ph = (t * bpm / 60.0) % 1.0
    pulse = math.exp(-((ph - 0.05) / 0.05) ** 2) + 0.6 * math.exp(-((ph - 0.22) / 0.05) ** 2)
    k = 1 + 0.06 * beat * pulse

    def T(px, py):
        return x + ((px - 160) * k) * s, y + ((py - 190) * k) * s

    # great vessels behind the heart: aortic arch, pulmonary trunk, superior vena cava
    vessels = [([(150, 70), (152, 20), (170, -30), (215, -48), (252, -28), (262, 20)], 30),
               ([(118, 80), (104, 30), (84, -2), (52, -10)], 24),
               ([(206, 70), (210, 10), (212, -60)], 22)]
    for pts, wd in vessels:
        P = [T(*p) for p in pts]
        for ctx, gl in ((cv.b, False), (cv.g, True)):
            ctx.new_path()
            ctx.move_to(*P[0])
            for q in P[1:]:
                ctx.line_to(*q)
            ctx.set_line_width(wd * s * k + (6 if gl else 0))
            ctx.set_source_rgba(*color, alpha * (0.35 if not gl else 0.35))
            ctx.stroke()
    pts = [((px - 160) * k + 160, (py - 190) * k + 190) for px, py in heart_points()]
    hologram_shape(cv, pts, x - 160 * s, y - 190 * s, s, color, alpha=alpha, fill=0.20 + 0.18 * pulse * beat,
                   glow=0.9, t=t)
    # coronary vessels on the surface
    for pts in ([(150, 70), (140, 140), (120, 220), (110, 300)], [(150, 70), (200, 120), (236, 190)]):
        cv.line([T(*p) for p in pts], (1.0, 0.65, 0.70), width=2.5 * s, alpha=alpha * 0.7)
    return pulse


# =========================================================================== brain

class Brain:
    """Side-view brain (facing left) with folds traced from noise contours (cached texture)."""

    OUT = [(30, 215), (42, 150), (80, 92), (140, 48), (215, 22), (300, 16), (380, 30), (450, 64), (505, 112),
           (540, 170), (548, 228), (530, 270), (500, 292), (440, 300), (380, 328), (320, 348), (250, 352),
           (190, 336), (150, 302), (118, 270), (78, 262), (44, 246)]

    def __init__(self, seed=6, color=(0.55, 0.85, 1.0)):
        w, h = 600, 470
        rng = np.random.default_rng(seed)
        s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        c = cairo.Context(s)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.set_line_join(cairo.LINE_JOIN_ROUND)
        # cerebellum and brainstem behind
        c.save()
        c.translate(472, 338)
        c.scale(78, 46)
        c.arc(0, 0, 1, 0, 2 * math.pi)
        c.restore()
        c.set_source_rgba(*color, 0.16)
        c.fill_preserve()
        c.set_source_rgba(*color, 0.9)
        c.set_line_width(2.5)
        c.stroke()
        for k in range(6):
            yy = 312 + k * 9
            c.move_to(410, yy)
            c.curve_to(450, yy - 6, 500, yy + 4, 545, yy - 2)
        c.set_source_rgba(*color, 0.45)
        c.set_line_width(1.5)
        c.stroke()
        smooth_path(c, [(392, 318), (430, 322), (440, 450), (408, 452)])
        c.set_source_rgba(*color, 0.14)
        c.fill_preserve()
        c.set_source_rgba(*color, 0.8)
        c.set_line_width(2.5)
        c.stroke()
        # cerebrum
        smooth_path(c, self.OUT)
        c.set_source_rgba(0.02, 0.05, 0.10, 1.0)
        c.fill_preserve()
        c.set_source_rgba(*color, 0.16)
        c.fill_preserve()
        c.save()
        c.clip()
        n = cv2.GaussianBlur(rng.random((h // 5, w // 5)).astype(np.float32), (0, 0), 1.0)
        n = cv2.resize(n, (w, h), interpolation=cv2.INTER_CUBIC)
        n = (n - n.min()) / (np.ptp(n) + 1e-6)
        for lev in np.linspace(0.18, 0.82, 9):
            cs, _ = cv2.findContours((n > lev).astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
            for cnt in cs:
                if len(cnt) < 30:
                    continue
                pts = cnt[:, 0, :][::4].astype(float)
                c.new_path()
                c.move_to(*pts[0])
                for q in pts[1:]:
                    c.line_to(*q)
                c.set_source_rgba(*color, 0.42)
                c.set_line_width(2.0)
                c.stroke()
        # the two great landmarks: lateral and central sulci
        c.move_to(170, 262)
        c.curve_to(250, 230, 330, 222, 420, 190)
        c.move_to(300, 20)
        c.curve_to(285, 90, 270, 160, 250, 236)
        c.set_source_rgba(*color, 0.85)
        c.set_line_width(3.2)
        c.stroke()
        c.restore()
        smooth_path(c, self.OUT)
        c.set_source_rgba(*color, 0.95)
        c.set_line_width(3.5)
        c.stroke()
        s.flush()
        self.surf = s
        self.w, self.h = w, h


# =========================================================================== the eye lens

def lens_shape(cx, cy, w, h, k=1.0, n=90):
    """Biconvex lens outline (front at left), half-width w (thickness), half-height h."""
    pts = []
    for i in range(n):
        a = -math.pi / 2 + i / (n - 1) * math.pi
        pts.append((cx + w * k * 1.0 * math.cos(a) ** 0.9, cy + h * k * math.sin(a)))
    for i in range(n):
        a = math.pi / 2 + i / (n - 1) * math.pi
        pts.append((cx + w * k * 1.25 * math.cos(a) * abs(math.cos(a)) ** -0.1, cy + h * k * math.sin(a)))
    return pts


def draw_lens(cv: Canvas, cx, cy, w, h, t, alpha=1.0, shells=11, core_glow=1.0, reveal=1.0, labels=None,
              hue=(0.55, 0.85, 1.0), core_col=(1.0, 0.62, 0.22)):
    """Cross-section of the lens: growth shells from the core (made in the womb) outward (added through life)."""
    if alpha <= 0.003:
        return
    for i in range(shells, 0, -1):
        k = i / shells
        if k > reveal + 1e-6:
            continue
        pts = lens_shape(cx, cy, w, h, k=k)
        age = 1 - k                                         # 1 = oldest (core)
        col = mix(hue, core_col, smooth(clamp((age - 0.55) / 0.35)))
        fill = 0.025 + 0.06 * age
        for ctx, gl in ((cv.b, False), (cv.g, True)):
            ctx.new_path()
            ctx.move_to(*pts[0])
            for p in pts[1:]:
                ctx.line_to(*p)
            ctx.close_path()
            ctx.set_source_rgba(*col, alpha * (fill if not gl else fill * 0.6))
            ctx.fill_preserve()
            ctx.set_source_rgba(*col, alpha * ((0.55 + 0.4 * age) if not gl else 0.4 * age))
            ctx.set_line_width(1.6 if not gl else 3)
            ctx.stroke()
    # embryonic core with its Y suture
    if core_glow > 0:
        cw, ch = w * 0.18, h * 0.16
        cv.radial(cx - w * 0.05, cy, ch * 2.0, core_col, alpha=0.30 * alpha * core_glow, glow=0.25 * core_glow)
        pts = lens_shape(cx - w * 0.03, cy, cw, ch)
        cv.poly(pts, core_col, alpha=0.85 * alpha * core_glow, glow=0.45 * core_glow)
        for a in (-math.pi / 2, math.pi / 6, 5 * math.pi / 6):
            cv.line([(cx - w * 0.03, cy), (cx - w * 0.03 + math.cos(a) * cw * 0.55, cy + math.sin(a) * ch * 0.6)],
                    (1.0, 0.95, 0.8), width=2, alpha=0.8 * alpha * core_glow)
