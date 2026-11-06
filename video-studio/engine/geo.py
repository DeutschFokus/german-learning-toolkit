"""Geology & engineering props: a painted rock column for vertical dives, a drill
rig, a rusty welded cap, a tricone drill bit, microfossils, a dinner plate and
the Voyager probe. Textures are pre-rendered with numpy (fBm noise) once.
"""
from __future__ import annotations

import math

import cairo
import cv2
import numpy as np

from .gfx import L, Canvas, W, H, clamp, lerp, mix


def _fbm(rng, h, w, octaves=5, stretch=1.0):
    acc = np.zeros((h, w), np.float32)
    amp, total = 1.0, 0.0
    for o in range(octaves):
        sh = max(2, int(h / (64 / 2 ** o)))
        sw = max(2, int(w / (64 * stretch / 2 ** o)))
        n = rng.random((sh, sw)).astype(np.float32)
        acc += amp * cv2.resize(n, (w, h), interpolation=cv2.INTER_CUBIC)
        total += amp
        amp *= 0.5
    acc /= total
    return (acc - acc.min()) / (np.ptp(acc) + 1e-6)


def _surface_from_bgr(img_bgr, alpha=None):
    h, w = img_bgr.shape[:2]
    a = np.ones((h, w), np.float32) if alpha is None else alpha
    buf = np.zeros((h, w, 4), np.uint8)
    buf[..., :3] = (np.clip(img_bgr * a[..., None], 0, 1) * 255).astype(np.uint8)
    buf[..., 3] = (np.clip(a, 0, 1) * 255).astype(np.uint8)
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    stride = s.get_stride()
    arr = np.ndarray((h, stride // 4, 4), np.uint8, s.get_data())
    arr[:, :w] = buf
    s.mark_dirty()
    return s


# depth (km) -> rock colour (RGB); painted, not photographic
RAMP = [(0.0, (0.34, 0.38, 0.46)), (0.4, (0.42, 0.40, 0.44)), (3.0, (0.47, 0.40, 0.40)),
        (6.0, (0.36, 0.33, 0.38)), (7.0, (0.30, 0.31, 0.38)), (9.0, (0.40, 0.27, 0.22)),
        (11.0, (0.60, 0.25, 0.12)), (12.3, (0.86, 0.37, 0.11))]


def rock_color(km):
    for (k0, c0), (k1, c1) in zip(RAMP, RAMP[1:]):
        if km <= k1:
            return mix(c0, c1, clamp((km - k0) / (k1 - k0)))
    return RAMP[-1][1]


class RockColumn:
    """A tall painted cross-section of the crust. 1 km = px_per_km pixels (full res)."""

    def __init__(self, depth_km=14.6, px_per_km=520, seed=7):
        self.ppk = px_per_km
        self.top_pad = 0
        hh = int(depth_km * px_per_km)
        self.full_h = hh
        rng = np.random.default_rng(seed)
        h2, w2 = hh // 2, W // 2
        strata = _fbm(rng, h2, w2, octaves=6, stretch=6.0)
        grain = _fbm(rng, h2, w2, octaves=4, stretch=1.0)
        ys_km = (np.arange(h2) * 2 / px_per_km)[:, None]
        base = np.zeros((h2, w2, 3), np.float32)
        lut_km = np.linspace(0, depth_km, 256)
        lut = np.array([rock_color(k) for k in lut_km], np.float32)
        idx = np.clip((ys_km / depth_km * 255).astype(int), 0, 255)
        col = lut[idx[:, 0]][:, None, :]
        # banded geology: each band nudges hue and brightness around the depth ramp
        band_mod = np.ones((h2, 1, 3), np.float32)
        y = 0
        while y < h2:
            hb = int(rng.uniform(0.18, 0.7) * px_per_km / 2)
            tint = np.array([rng.uniform(0.94, 1.07), rng.uniform(0.95, 1.05), rng.uniform(0.94, 1.06)], np.float32)
            band_mod[y:y + hb, 0, :] = tint * rng.uniform(0.86, 1.14)
            y += hb
        band_mod = cv2.GaussianBlur(band_mod, (1, 21), sigmaX=0, sigmaY=3.5)       # soft contacts between beds
        mottle = cv2.GaussianBlur(rng.random((h2, w2)).astype(np.float32), (0, 0), 1.1)
        mottle = (mottle - mottle.mean()) / (mottle.std() + 1e-6)                  # crystalline grain
        shade = 0.62 + 0.62 * strata[..., None] + 0.18 * (grain[..., None] - 0.5) + 0.045 * mottle[..., None]
        light = np.linspace(1.12, 0.78, w2, dtype=np.float32)[None, :, None]      # lit from the left
        base = np.clip(col * band_mod * shade * light * 1.18, 0, 1)
        # layer lines
        wav = np.sin(np.arange(w2)[None, :] / w2 * 2 * math.pi * 1.3) * 6
        for k in range(int(depth_km * 7)):
            yy = int((k + rng.random()) * h2 / (depth_km * 7))
            ln = (yy + wav + rng.normal(0, 1.2, (1, w2))).astype(int)[0]
            ok = (ln >= 0) & (ln < h2)
            base[ln[ok], np.arange(w2)[ok]] *= 0.78
        bgr = base[..., ::-1].copy()
        # fractures + water between 7 and 9.6 km: branching crack networks with wet, darkened halos
        img = (np.clip(bgr, 0, 1) * 255).astype(np.uint8).copy()
        cracks = np.zeros((h2, w2), np.uint8)
        glints = np.zeros((h2, w2), np.uint8)
        self.cracks = []

        def crack(x, y, ang, length, depth=0):
            pts, total = [(x, y)], 0.0
            while total < length:
                s_ = rng.uniform(7, 16)
                ang += rng.normal(0, 0.07) + (rng.choice((-1, 1)) * rng.uniform(0.25, 0.5) if rng.random() < 0.12 else 0)
                x += math.cos(ang) * s_
                y += math.sin(ang) * s_
                pts.append((x, y))
                total += s_
                if depth < 1 and rng.random() < 0.05:
                    crack(x, y, ang + rng.choice((-1, 1)) * rng.uniform(0.6, 1.0), length * rng.uniform(0.2, 0.45),
                          depth + 1)
            arr = np.array(pts, np.int32)
            self.cracks.append(arr.astype(np.float32) * 2)
            cv2.polylines(cracks, [arr], False, 255, 1, cv2.LINE_AA)
            cv2.polylines(glints, [arr + np.array([1, -1], np.int32)], False, 255, 1, cv2.LINE_AA)

        sets = (math.radians(72), math.radians(112), math.radians(8))      # joint sets: fractures run in families
        for k in range(80):
            km = rng.uniform(6.95, 9.55)
            ang = sets[int(rng.integers(0, 3))] + rng.normal(0, 0.08) + rng.choice((0, math.pi))
            crack(rng.uniform(0, w2), km * px_per_km / 2, ang, rng.uniform(50, 220))
        cm = cracks.astype(np.float32) / 255
        wet = cv2.GaussianBlur(cv2.dilate(cm, np.ones((5, 5), np.uint8)), (0, 0), 6.0)
        wet = np.clip(wet / (wet.max() + 1e-6) * 1.6, 0, 1)
        f = img.astype(np.float32)
        f *= (1 - 0.30 * wet[..., None]) * np.array([1.06, 1.0, 0.92], np.float32) ** wet[..., None]  # wet = darker, cooler
        f *= (1 - 0.62 * cm[..., None])
        gl = glints.astype(np.float32)[..., None] / 255 * (1 - cm[..., None])
        f = f * (1 - 0.55 * gl) + np.array([235, 205, 150], np.float32) * 0.55 * gl                # water glint (BGR)
        img = np.clip(f, 0, 255).astype(np.uint8)
        gy, gx = np.nonzero(glints > 140)
        pick = rng.choice(len(gy), size=min(700, len(gy)), replace=False)
        self.glint_pts = np.stack([gx[pick] * 2.0, gy[pick] * 2.0, rng.uniform(0, 2 * math.pi, len(pick)),
                                   rng.uniform(2.0, 6.0, len(pick))], axis=1)
        self.crack_y = np.array([c[:, 1].mean() for c in self.cracks])
        # quartz veins (few, faint)
        veins = img.copy()
        for k in range(int(depth_km * 3)):
            y = int(rng.uniform(0, h2))
            x = int(rng.uniform(0, w2))
            ang = rng.uniform(-0.5, 0.5)
            ln = int(rng.uniform(60, 260))
            pts = []
            for j in range(12):
                u = j / 11
                pts.append([int(x + math.cos(ang) * ln * u), int(y + math.sin(ang) * ln * u + 6 * math.sin(u * 7))])
            cv2.polylines(veins, [np.array(pts, np.int32)], False, (200, 205, 215), 1, cv2.LINE_AA)
        img = cv2.addWeighted(img, 0.65, veins, 0.35, 0)
        # mineral speckles
        for k in range(9000):
            y = int(rng.uniform(0, h2))
            x = int(rng.uniform(0, w2))
            v = int(rng.uniform(150, 235))
            img[y, x] = (v, v, v) if rng.random() < 0.7 else (v // 2, v // 2, v)
        self.img = img
        self.surf = _surface_from_bgr(img.astype(np.float32) / 255)
        # crisp full-resolution grain, tileable (blurred on a 3x3 tiling, centre kept)
        nz = rng.random((540, 540)).astype(np.float32)
        big = np.tile(nz, (3, 3))
        fine = cv2.GaussianBlur(big, (0, 0), 0.7)[540:1080, 540:1080]
        mid = cv2.GaussianBlur(big, (0, 0), 3.0)[540:1080, 540:1080]
        d = 0.5 + 0.045 * (fine - fine.mean()) / (fine.std() + 1e-6) + 0.06 * (mid - mid.mean()) / (mid.std() + 1e-6)
        d = np.clip(cv2.resize(np.tile(d, (2, 2)), (2160, 2160), interpolation=cv2.INTER_LINEAR)[540:1620, 540:1620],
                    0, 1)
        self.detail = _surface_from_bgr(np.repeat(d[..., None], 3, axis=2))
        # foreground edge silhouettes (parallax, pre-blurred = out of focus); periodic so they wrap seamlessly
        fh = h2
        yy = np.arange(fh, dtype=np.float32) / fh * 2 * math.pi

        def profile():
            acc = np.zeros(fh, np.float32)
            for k in range(3, 90):
                acc += rng.normal(0, 1) / k ** 0.9 * np.sin(k * yy + rng.uniform(0, 2 * math.pi))
            acc = (acc - acc.min()) / (np.ptp(acc) + 1e-6)
            return 14 + 34 * acc

        prof_l, prof_r = profile(), profile()
        xs = np.arange(w2)[None, :]
        edge = ((xs < prof_l[:, None]) | (xs > w2 - prof_r[:, None])).astype(np.float32)
        edge = np.concatenate([edge[-24:], edge, edge[:24]])
        edge = cv2.GaussianBlur(edge, (0, 0), 6)[24:-24]
        fg = np.zeros((fh, w2, 3), np.float32)
        fg[..., :] = (0.03, 0.03, 0.05)
        self.fg = _surface_from_bgr(fg, edge * 0.95)

    def y_of(self, km):
        return km * self.ppk

    def draw(self, cv: Canvas, cam_y, alpha=1.0, fg_alpha=1.0, fg_speed=1.35, shaft_w=64.0, squeeze=0.0, t=0.0,
             shaft=True, glow_bottom=0.0, bottom_km=12.262, span=None, detail=0.6):
        """cam_y: world y (px) at the screen centre. span: world (y0, y1) of the shaft to draw when the
        caller zooms out (default: just the visible window)."""
        b = cv.b
        top = cam_y - H / 2
        b.save()
        b.translate(0, -top)
        b.scale(2, 2)
        b.set_source_surface(self.surf, 0, 0)
        b.get_source().set_filter(cairo.FILTER_BILINEAR)
        b.paint_with_alpha(alpha)
        b.restore()
        if detail > 0:
            b.save()
            b.rectangle(0, -top, W, self.full_h)
            b.clip()
            b.set_operator(cairo.OPERATOR_OVERLAY)
            off = top % 1080
            for k in range(3):
                b.save()
                b.translate(0, -off + k * 1080)
                b.set_source_surface(self.detail, 0, 0)
                b.paint_with_alpha(alpha * detail)
                b.restore()
            b.restore()
        if shaft:
            # the borehole (exaggerated width), with the drill string inside
            ybot = self.y_of(bottom_km)
            if span is None:
                y0, y1 = max(0.0, top - 10), min(top + H + 10, ybot)
            else:
                y0, y1 = max(0.0, span[0]), min(span[1], ybot)
            if y1 > y0:
                pts_l, pts_r = [], []
                n = 60
                for i in range(n + 1):
                    wy = lerp(y0, y1, i / n)
                    sq = squeeze * (0.5 + 0.5 * math.sin(wy * 0.02 + t * 3.0))
                    hw = shaft_w / 2 * (1 - 0.55 * sq)
                    wob = 6 * squeeze * math.sin(wy * 0.035 + t * 2.0)
                    pts_l.append((W / 2 - hw + wob, wy - top))
                    pts_r.append((W / 2 + hw + wob, wy - top))
                b.new_path()
                b.move_to(*pts_l[0])
                for p in pts_l[1:]:
                    b.line_to(*p)
                for p in reversed(pts_r):
                    b.line_to(*p)
                b.close_path()
                b.set_source_rgba(0.02, 0.02, 0.03, 0.96 * alpha)
                b.fill()
                cv.line(pts_l, (0.75, 0.78, 0.85), width=1.5, alpha=0.5 * alpha)
                cv.line(pts_r, (0.75, 0.78, 0.85), width=1.5, alpha=0.5 * alpha)
                cv.line([(W / 2, y0 - top), (W / 2, y1 - top)], (0.62, 0.66, 0.74), width=3, alpha=0.8 * alpha)
        if glow_bottom > 0:
            yb = self.y_of(bottom_km) - top
            cv.radial(W / 2, yb, 420, (1.0, 0.45, 0.15), alpha=0.6 * glow_bottom * alpha, glow=glow_bottom)
        if fg_alpha > 0:
            off = (cam_y * fg_speed - H / 2) % self.full_h
            for dy in (-off, self.full_h - off):
                if dy > H or dy + self.full_h < 0:
                    continue
                b.save()
                b.translate(0, dy)
                b.scale(2, 2)
                b.set_source_surface(self.fg, 0, 0)
                b.get_source().set_extend(cairo.EXTEND_NONE)
                b.paint_with_alpha(fg_alpha * alpha)
                b.restore()


# --------------------------------------------------------------------------- props

def drill_rig(cv: Canvas, x, base_y, h=760.0, alpha=1.0, t=0.0, lights=1.0):
    """A lattice derrick with work lights."""
    if alpha <= 0.003:
        return
    wb, wt = h * 0.30, h * 0.06
    col = (0.62, 0.68, 0.80)
    L_ = [(x - wb / 2, base_y), (x - wt / 2, base_y - h)]
    R_ = [(x + wb / 2, base_y), (x + wt / 2, base_y - h)]
    cv.line(L_, col, width=5, alpha=alpha)
    cv.line(R_, col, width=5, alpha=alpha)
    n = 14
    for k in range(n):
        u0, u1 = k / n, (k + 1) / n
        lx0, rx0 = lerp(L_[0][0], L_[1][0], u0), lerp(R_[0][0], R_[1][0], u0)
        lx1, rx1 = lerp(L_[0][0], L_[1][0], u1), lerp(R_[0][0], R_[1][0], u1)
        y0, y1 = base_y - h * u0, base_y - h * u1
        cv.line([(lx0, y0), (rx1, y1)], col, width=2, alpha=alpha * 0.8)
        cv.line([(rx0, y0), (lx1, y1)], col, width=2, alpha=alpha * 0.8)
        cv.line([(lx1, y1), (rx1, y1)], col, width=2, alpha=alpha * 0.8)
    cv.rect(x - wb * 0.85, base_y - 70, wb * 1.7, 70, (0.10, 0.12, 0.18), alpha=alpha, radius=4)
    cv.rect(x - wb * 0.85, base_y - 70, wb * 1.7, 70, col, alpha=alpha * 0.7, fill=False, width=2, radius=4)
    for k in range(6):
        u = (k + 0.5) / 6
        ly = base_y - h * u
        flick = 0.85 + 0.15 * math.sin(t * 2 * math.pi * (k + 2) / 6.0)
        for sgn in (-1, 1):
            lx = x + sgn * lerp(wb / 2, wt / 2, u)
            cv.circle(lx, ly, 5, (1.0, 0.8, 0.45), alpha=alpha * lights * flick, glow=1.0)
    cv.circle(x, base_y - h - 8, 7, (1.0, 0.25, 0.2), alpha=alpha * lights * (0.6 + 0.4 * math.sin(t * math.pi)),
              glow=1.0)


class RustyCap:
    """A welded steel lid with bolts, seen in perspective on a concrete pad."""

    def __init__(self, r=230, seed=12):
        rng = np.random.default_rng(seed)
        size = int(r * 2.4)
        self.r, self.size = r, size
        n1 = _fbm(rng, size, size, octaves=5)
        n2 = _fbm(rng, size, size, octaves=3)
        steel = np.array([0.30, 0.29, 0.28], np.float32)       # BGR
        rust = np.array([0.08, 0.24, 0.50], np.float32)
        dark = np.array([0.05, 0.10, 0.18], np.float32)
        m = np.clip((n1 - 0.22) * 2.0, 0, 1)[..., None]
        img = steel * (1 - m) + rust * m
        img = img * (0.75 + 0.45 * n2[..., None])
        img = img * (1 - 0.35 * np.clip((n2 - 0.7) * 3, 0, 1))[..., None] + dark * 0.0
        yy, xx = np.mgrid[0:size, 0:size]
        d = np.hypot(xx - size / 2, yy - size / 2)
        a = np.clip((r - d) / 2.0 + 0.5, 0, 1).astype(np.float32)
        rim = np.exp(-((d - r * 0.93) / 4.0) ** 2)
        img = img * (1 - 0.35 * rim[..., None])
        img = img * (0.75 + 0.25 * np.clip(1 - d / r, 0, 1))[..., None]
        self.surf = _surface_from_bgr(img.astype(np.float32), a)
        self.bolts = [(math.cos(k / 12 * 2 * math.pi) * r * 0.86, math.sin(k / 12 * 2 * math.pi) * r * 0.86)
                      for k in range(12)]

    def draw(self, cv: Canvas, x, y, tilt=0.42, scale=1.0, alpha=1.0, snow=0.0):
        """Centre at (x, y); tilt squashes it vertically (perspective)."""
        if alpha <= 0.003:
            return
        b = cv.b
        r = self.r * scale
        # concrete pad
        b.save()
        b.translate(x, y)
        b.scale(1, tilt)
        pad = r * 1.45
        pat = cairo.RadialGradient(0, 0, r * 0.5, 0, 0, pad * 1.4)
        pat.add_color_stop_rgba(0, 0.36, 0.37, 0.40, alpha)
        pat.add_color_stop_rgba(0.7, 0.30, 0.31, 0.34, alpha * 0.9)
        pat.add_color_stop_rgba(1, 0.30, 0.31, 0.34, 0.0)
        b.arc(0, 0, pad * 1.4, 0, 2 * math.pi)
        b.set_source(pat)
        b.fill()
        b.set_source_rgba(0.12, 0.12, 0.14, alpha * 0.5)
        b.set_line_width(3)
        b.move_to(-pad * 0.9, -pad * 0.5)
        b.line_to(-pad * 0.3, pad * 0.2)
        b.line_to(pad * 0.4, pad * 0.75)
        b.stroke()
        # the lid
        b.scale(scale, scale)
        b.set_source_surface(self.surf, -self.size / 2, -self.size / 2)
        b.paint_with_alpha(alpha)
        for (bx, by) in self.bolts:
            b.arc(bx, by, 11, 0, 2 * math.pi)
            b.set_source_rgba(0.20, 0.17, 0.15, alpha)
            b.fill()
            b.arc(bx - 2, by - 2, 5, 0, 2 * math.pi)
            b.set_source_rgba(0.55, 0.42, 0.32, alpha * 0.8)
            b.fill()
        # weld seam
        b.arc(0, 0, self.r * 0.995, 0, 2 * math.pi)
        b.set_line_width(5)
        b.set_source_rgba(0.62, 0.55, 0.48, alpha * 0.5)
        b.stroke()
        b.restore()
        if snow > 0:
            rng = np.random.default_rng(3)
            for k in range(26):
                a_ = rng.uniform(0, 2 * math.pi)
                d = r * rng.uniform(1.05, 1.9)
                rr = rng.uniform(25, 60) * scale
                b.save()
                b.translate(x + math.cos(a_) * d, y + math.sin(a_) * d * tilt)
                b.scale(1.0, tilt * rng.uniform(0.8, 1.3))
                pat = cairo.RadialGradient(0, 0, 0, 0, 0, rr)
                pat.add_color_stop_rgba(0, 0.70, 0.75, 0.84, alpha * snow * rng.uniform(0.25, 0.5))
                pat.add_color_stop_rgba(1, 0.70, 0.75, 0.84, 0)
                b.arc(0, 0, rr, 0, 2 * math.pi)
                b.set_source(pat)
                b.fill()
                b.restore()


class Snowfield:
    """A pre-rendered snowy plain from a horizon line to the bottom of the frame."""

    def __init__(self, horizon=1150, seed=21):
        rng = np.random.default_rng(seed)
        self.horizon = horizon
        h = H - horizon
        n = _fbm(rng, h // 2, W // 2, octaves=5, stretch=4.0)
        ys = np.linspace(0, 1, h // 2, dtype=np.float32)[:, None]
        far = np.array([0.40, 0.35, 0.28], np.float32)       # BGR: night snow, blue-grey far away
        near = np.array([0.68, 0.62, 0.56], np.float32)      # cold, moonlit snow up close
        col = far * (1 - ys[..., None] ** 0.7) + near * ys[..., None] ** 0.7
        img = col * (0.80 + 0.32 * n[..., None])
        fine = cv2.GaussianBlur(rng.random(n.shape).astype(np.float32), (0, 0), 0.8)
        img = img * (0.94 + 0.12 * fine[..., None])                                  # sparkle/grain of snow
        drift = np.clip((n - 0.55) * 3, 0, 1)[..., None]
        img = img * (1 - 0.18 * drift)
        self.surf = _surface_from_bgr(np.clip(img, 0, 1).astype(np.float32))
        n_g = 220
        gy = rng.uniform(0, 1, n_g) ** 1.6                       # more glints near the camera
        self.glints = np.stack([rng.uniform(0, W, n_g), horizon + 8 + gy * (h - 8), rng.uniform(0, 2 * math.pi, n_g),
                                rng.integers(5, 19, n_g).astype(np.float64), 0.6 + 1.6 * gy], axis=1)

    def draw(self, cv: Canvas, alpha=1.0, dy=0.0, t=0.0, loop=60.0):
        b = cv.b
        b.save()
        b.translate(0, self.horizon + dy)
        b.scale(2, 2)
        b.set_source_surface(self.surf, 0, 0)
        b.paint_with_alpha(alpha)
        b.restore()
        cv.line([(0, self.horizon + dy), (W, self.horizon + dy)], (0.75, 0.85, 1.0), width=2, alpha=0.35 * alpha,
                glow=0.4)
        # snow crystals catching the light (whole cycles per loop)
        for x, y, ph, cyc, r in self.glints:
            yy = y + dy
            if yy > H + 4:
                continue
            tw = math.sin(2 * math.pi * cyc * t / loop + ph)
            if tw < 0.55:
                continue
            a = alpha * (tw - 0.55) / 0.45
            cv.circle(x, yy, r, (0.92, 0.96, 1.0), alpha=a, glow=0.8)


def dinner_plate(cv: Canvas, x, y, r, alpha=1.0, tilt=1.0):
    if alpha <= 0.003:
        return
    b = cv.b
    b.save()
    b.translate(x, y)
    b.scale(1, tilt)
    pat = cairo.RadialGradient(-r * 0.2, -r * 0.2, r * 0.1, 0, 0, r)
    pat.add_color_stop_rgba(0, 0.98, 0.98, 1.0, alpha)
    pat.add_color_stop_rgba(1, 0.80, 0.83, 0.90, alpha)
    b.arc(0, 0, r, 0, 2 * math.pi)
    b.set_source(pat)
    b.fill()
    b.arc(0, 0, r * 0.72, 0, 2 * math.pi)
    b.set_source_rgba(0.70, 0.74, 0.82, alpha * 0.8)
    b.set_line_width(3)
    b.stroke()
    b.restore()


def drill_bit(cv: Canvas, x, y, s=1.0, alpha=1.0, heat=0.0, t=0.0):
    """Tricone bit, tip at (x, y)."""
    if alpha <= 0.003:
        return
    col = mix((0.62, 0.66, 0.74), (1.0, 0.55, 0.25), heat)
    cv.rect(x - 22 * s, y - 230 * s, 44 * s, 150 * s, (0.30, 0.32, 0.38), alpha=alpha, radius=4)
    cv.poly([(x - 60 * s, y - 80 * s), (x + 60 * s, y - 80 * s), (x + 40 * s, y - 30 * s), (x - 40 * s, y - 30 * s)],
            (0.36, 0.38, 0.44), alpha=alpha)
    for k, dx in enumerate((-34, 0, 34)):
        cx_ = x + dx * s
        cy_ = y - 22 * s + (6 * s if k == 1 else 0)
        cv.circle(cx_, cy_, 24 * s, col, alpha=alpha, glow=heat * 0.8)
        for j in range(8):
            a = j / 8 * 2 * math.pi + t * (2.0 + k)
            cv.line([(cx_ + math.cos(a) * 14 * s, cy_ + math.sin(a) * 14 * s),
                     (cx_ + math.cos(a) * 26 * s, cy_ + math.sin(a) * 26 * s)], (0.15, 0.15, 0.18), width=4 * s,
                    alpha=alpha)


def microfossil(cv: Canvas, x, y, r, kind=0, alpha=1.0, rot=0.0, color=(0.70, 1.0, 0.85)):
    """Radiolarian (kind 0) or diatom (kind 1) outline, glowing."""
    if alpha <= 0.003:
        return
    if kind == 0:
        cv.circle(x, y, r, color, alpha=alpha, fill=False, width=2, glow=0.7)
        cv.circle(x, y, r * 0.55, color, alpha=alpha * 0.7, fill=False, width=1.5)
        for k in range(14):
            a = k / 14 * 2 * math.pi + rot
            cv.line([(x + math.cos(a) * r, y + math.sin(a) * r), (x + math.cos(a) * r * 1.6, y + math.sin(a) * r * 1.6)],
                    color, width=1.5, alpha=alpha * 0.9)
    else:
        b = cv.b
        b.save()
        b.translate(x, y)
        b.rotate(rot)
        b.scale(r * 1.8, r * 0.6)
        b.arc(0, 0, 1, 0, 2 * math.pi)
        b.restore()
        b.set_source_rgba(*color, alpha)
        b.set_line_width(2)
        b.stroke()
        for k in range(-4, 5):
            ux = k / 5 * r * 1.6
            dx, dy = math.cos(rot), math.sin(rot)
            px, py = -dy, dx
            cv.line([(x + dx * ux - px * r * 0.5, y + dy * ux - py * r * 0.5),
                     (x + dx * ux + px * r * 0.5, y + dy * ux + py * r * 0.5)], color, width=1.2, alpha=alpha * 0.7)


def voyager(cv: Canvas, x, y, s=1.0, alpha=1.0, rot=-0.3):
    if alpha <= 0.003:
        return
    with cv.transform(tx=x - W / 2, ty=y - H / 2, s=s, rot=rot):
        cx, cy = W / 2, H / 2
        b = cv.b
        b.save()
        b.translate(cx, cy)
        b.scale(1.0, 0.55)
        b.arc(0, 0, 70, 0, 2 * math.pi)
        b.restore()
        b.set_source_rgba(0.92, 0.94, 1.0, alpha)
        b.fill()
        cv.rect(cx - 26, cy + 20, 52, 34, (0.75, 0.62, 0.32), alpha=alpha, radius=3)
        cv.line([(cx, cy + 30), (cx + 230, cy + 120)], (0.85, 0.88, 0.95), width=3, alpha=alpha)
        cv.line([(cx - 20, cy + 40), (cx - 140, cy + 90)], (0.85, 0.88, 0.95), width=5, alpha=alpha)
        cv.circle(cx - 150, cy + 94, 10, (0.85, 0.88, 0.95), alpha=alpha)
        cv.circle(cx, cy, 6, L.WHITE, alpha=alpha, glow=1.0)
