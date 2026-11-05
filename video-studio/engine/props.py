"""Reusable LUMEN props: dotted Earth, planet limb, satellite, phone, 3D grid
fabric, Earth cross-section. All procedural, all original artwork.
"""
from __future__ import annotations

import math

import cairo
import numpy as np

from .gfx import L, Canvas, W, H, clamp, mix, smooth

# --------------------------------------------------------------------------- Earth


class DottedEarth:
    """Real continents (global-land-mask) as a halftone dot globe."""

    def __init__(self, n=5200, seed=0):
        from global_land_mask import globe
        i = np.arange(n) + 0.5
        lat = np.arcsin(1 - 2 * i / n)
        lon = (np.pi * (1 + 5 ** 0.5) * i) % (2 * np.pi) - np.pi
        land = globe.is_land(np.degrees(lat), np.degrees(lon))
        self.lat, self.lon = lat[land], lon[land]
        rng = np.random.default_rng(seed)
        k = rng.choice(len(self.lat), size=90, replace=False)
        self.city = k          # indices of "city lights"

    def _proj(self, lat, lon, lon0, tilt):
        x = np.cos(lat) * np.sin(lon - lon0)
        y = np.sin(lat)
        z = np.cos(lat) * np.cos(lon - lon0)
        y2 = y * math.cos(tilt) - z * math.sin(tilt)
        z2 = y * math.sin(tilt) + z * math.cos(tilt)
        return x, y2, z2

    def draw(self, cv: Canvas, x, y, r, lon0=0.0, tilt=0.35, alpha=1.0, dot=None, glow=0.7,
             land_color=None, ocean=True, rim=True, clip_fn=None):
        if alpha <= 0.002 or r < 2:
            return
        land_color = land_color or (0.55, 0.85, 1.0)
        c = cv.b
        if ocean:
            pat = cairo.RadialGradient(x - r * 0.35, y - r * 0.4, r * 0.1, x, y, r)
            pat.add_color_stop_rgba(0, 0.06, 0.16, 0.38, alpha)
            pat.add_color_stop_rgba(0.75, 0.03, 0.07, 0.19, alpha)
            pat.add_color_stop_rgba(1, 0.02, 0.04, 0.12, alpha)
            c.new_path()
            c.arc(x, y, r, 0, 2 * math.pi)
            c.set_source(pat)
            c.fill()
        px, py, pz = self._proj(self.lat, self.lon, lon0, tilt)
        vis = pz > 0.02
        d = dot or max(1.0, r * 0.0105)
        sx = x + r * px[vis]
        sy = y - r * py[vis]
        sz = pz[vis]
        for X, Y, Z in zip(sx, sy, sz):
            a = alpha * (0.25 + 0.75 * Z)
            c.set_source_rgba(*land_color, a)
            c.arc(X, Y, d * (0.6 + 0.4 * Z), 0, 2 * math.pi)
            c.fill()
        # a few warm city lights, also into the glow layer
        cx_, cy_, cz_ = px[self.city], py[self.city], pz[self.city]
        for X, Y, Z in zip(cx_, cy_, cz_):
            if Z > 0.1:
                sx_, sy_ = x + r * X, y - r * Y
                c.set_source_rgba(1.0, 0.82, 0.5, alpha * 0.9 * Z)
                c.arc(sx_, sy_, d * 0.9, 0, 2 * math.pi)
                c.fill()
                if glow > 0:
                    cv.g.set_source_rgba(1.0, 0.75, 0.4, alpha * glow * 0.8 * Z)
                    cv.g.arc(sx_, sy_, d * 2.2, 0, 2 * math.pi)
                    cv.g.fill()
        # graticule
        c.set_line_width(max(0.8, r * 0.003))
        for lat_d in range(-60, 61, 30):
            lat = math.radians(lat_d)
            lons = np.linspace(-math.pi, math.pi, 120)
            gx, gy, gz = self._proj(np.full_like(lons, lat), lons, lon0, tilt)
            _poly_visible(c, x + r * gx, y - r * gy, gz, (0.4, 0.7, 1.0), alpha * 0.18)
        for lon_d in range(0, 360, 30):
            lats = np.linspace(-math.pi / 2, math.pi / 2, 80)
            gx, gy, gz = self._proj(lats, np.full_like(lats, math.radians(lon_d)), lon0, tilt)
            _poly_visible(c, x + r * gx, y - r * gy, gz, (0.4, 0.7, 1.0), alpha * 0.14)
        if rim:
            atmosphere(cv, x, y, r, alpha)


def _poly_visible(c, xs, ys, zs, color, alpha):
    c.set_source_rgba(*color, alpha)
    drawing = False
    for X, Y, Z in zip(xs, ys, zs):
        if Z > 0:
            if drawing:
                c.line_to(X, Y)
            else:
                c.move_to(X, Y)
                drawing = True
        else:
            drawing = False
    c.stroke()


def atmosphere(cv: Canvas, x, y, r, alpha=1.0, color=(0.35, 0.75, 1.0), width=0.12):
    for ctx, a_mul in ((cv.b, 1.0), (cv.g, 0.9)):
        pat = cairo.RadialGradient(x, y, r * 0.92, x, y, r * (1 + width))
        pat.add_color_stop_rgba(0, *color, 0)
        pat.add_color_stop_rgba(0.38, *color, 0.55 * alpha * a_mul)
        pat.add_color_stop_rgba(0.55, *color, 0.30 * alpha * a_mul)
        pat.add_color_stop_rgba(1, *color, 0)
        ctx.new_path()
        ctx.arc(x, y, r * (1 + width), 0, 2 * math.pi)
        ctx.set_source(pat)
        ctx.fill()


class Limb:
    """A huge planet whose upper edge sits at y=top — something to stand on.

    Rendered once (dense real-geography dots) and blitted every frame. By
    default the top of the limb is northern Germany: `home` (lat, lon) is
    marked with a warm light right where `home_x` is.
    """

    def __init__(self, top=1194, R=1500, cx=W / 2, home=(52.37, 9.73), home_x=790.0, n=140000):
        from global_land_mask import globe
        self.top, self.R, self.cx = top, R, cx
        lat0 = math.radians(home[0])
        tilt = -math.acos(math.sin(lat0)) + 0.07   # `home`'s latitude just inside the limb's top edge
        dlon = math.asin(clamp((home_x - cx) / R / max(math.cos(lat0), 1e-3), -1, 1))
        lon0 = math.radians(home[1]) - dlon
        self.surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, int(H - top + 40))
        c = cairo.Context(self.surf)
        cy = R + 40                                  # sphere centre in surface coordinates
        pat = cairo.RadialGradient(cx, cy, R * 0.2, cx, cy, R)
        pat.add_color_stop_rgba(0, 0.02, 0.05, 0.13, 1)
        pat.add_color_stop_rgba(0.85, 0.03, 0.08, 0.20, 1)
        pat.add_color_stop_rgba(1, 0.05, 0.14, 0.32, 1)
        c.arc(cx, cy, R, 0, 2 * math.pi)
        c.set_source(pat)
        c.fill()
        i = np.arange(n) + 0.5
        lat = np.arcsin(1 - 2 * i / n)
        lon = (np.pi * (1 + 5 ** 0.5) * i) % (2 * np.pi) - np.pi
        land = globe.is_land(np.degrees(lat), np.degrees(lon))
        lat, lon = lat[land], lon[land]
        x = np.cos(lat) * np.sin(lon - lon0)
        y = np.sin(lat)
        z = np.cos(lat) * np.cos(lon - lon0)
        y2 = y * math.cos(tilt) - z * math.sin(tilt)
        z2 = y * math.sin(tilt) + z * math.cos(tilt)
        vis = z2 > 0
        sx, sy, sz = cx + R * x[vis], cy - R * y2[vis], z2[vis]
        keep = (sy > 0) & (sy < self.surf.get_height()) & (sx > -5) & (sx < W + 5)
        rng = np.random.default_rng(1)
        for X, Y, Z in zip(sx[keep], sy[keep], sz[keep]):
            edge = clamp(Z * 3.0)
            c.set_source_rgba(0.45, 0.78, 1.0, 0.18 + 0.42 * edge)
            c.arc(X, Y, 1.25, 0, 2 * math.pi)
            c.fill()
            if rng.random() < 0.035:
                c.set_source_rgba(1.0, 0.8, 0.45, 0.55 * edge)
                c.arc(X, Y, 1.6, 0, 2 * math.pi)
                c.fill()
        # graticule
        c.set_line_width(1.0)
        for lat_d in range(-60, 90, 15):
            la = math.radians(lat_d)
            lons = np.linspace(-math.pi, math.pi, 400)
            gx = np.cos(la) * np.sin(lons - lon0)
            gy = np.full_like(lons, math.sin(la))
            gz = np.cos(la) * np.cos(lons - lon0)
            gy2 = gy * math.cos(tilt) - gz * math.sin(tilt)
            gz2 = gy * math.sin(tilt) + gz * math.cos(tilt)
            _poly_visible(c, cx + R * gx, cy - R * gy2, gz2, (0.4, 0.7, 1.0), 0.10)
        # home light
        hx = cx + R * math.cos(lat0) * math.sin(math.radians(home[1]) - lon0)
        hy_y = math.sin(lat0)
        hz = math.cos(lat0) * math.cos(math.radians(home[1]) - lon0)
        hy = cy - R * (hy_y * math.cos(tilt) - hz * math.sin(tilt))
        self.home = (hx, hy + top - 40)
        # inner shadow toward the bottom (night side feel)
        sh = cairo.LinearGradient(0, 40, 0, self.surf.get_height())
        sh.add_color_stop_rgba(0, 0, 0, 0, 0)
        sh.add_color_stop_rgba(0.35, 0, 0, 0.02, 0.15)
        sh.add_color_stop_rgba(1, 0, 0, 0.02, 0.65)
        c.set_source(sh)
        c.arc(cx, cy, R, 0, 2 * math.pi)
        c.fill()

    def draw(self, cv: Canvas, t=0.0, alpha=1.0):
        if alpha <= 0.002:
            return
        b = cv.b
        b.save()
        b.set_source_surface(self.surf, 0, self.top - 40)
        b.paint_with_alpha(alpha)
        b.restore()
        cy = self.top + self.R
        # thin atmosphere: crisp rim + soft halo
        for ctx, a_mul, wdt in ((cv.b, 0.55, 4.0), (cv.g, 0.8, 7.0)):
            ctx.new_path()
            ctx.arc(self.cx, cy, self.R + 1, math.radians(200), math.radians(340))
            ctx.set_line_width(wdt)
            ctx.set_source_rgba(0.45, 0.8, 1.0, a_mul * alpha)
            ctx.stroke()
        pat = cairo.RadialGradient(self.cx, cy, self.R - 6, self.cx, cy, self.R + 46)
        pat.add_color_stop_rgba(0, 0.3, 0.65, 1.0, 0.0)
        pat.add_color_stop_rgba(0.15, 0.3, 0.65, 1.0, 0.28 * alpha)
        pat.add_color_stop_rgba(1, 0.3, 0.65, 1.0, 0.0)
        b.new_path()
        b.arc(self.cx, cy, self.R + 46, math.radians(195), math.radians(345))
        b.arc_negative(self.cx, cy, self.R - 6, math.radians(345), math.radians(195))
        b.close_path()
        b.set_source(pat)
        b.fill()
        hx, hy = self.home
        cv.circle(hx, hy + 3, 3.2, (1.0, 0.85, 0.55), alpha=alpha, glow=1.0)


# --------------------------------------------------------------------------- machines

def satellite(cv: Canvas, x, y, s=1.0, ang=0.0, alpha=1.0, color=L.CYAN, glow=0.8):
    if alpha <= 0.002:
        return
    with cv.transform(tx=x - W / 2, ty=y - H / 2, s=s, rot=ang):
        cx, cy = W / 2, H / 2
        # panels
        for sgn in (-1, 1):
            px0 = cx + sgn * 26
            px1 = cx + sgn * 120
            cv.line([(px0, cy), (cx + sgn * 34, cy)], L.DIM, width=4, alpha=alpha)
            x0 = min(cx + sgn * 34, px1)
            cv.rect(x0, cy - 22, 86, 44, (0.10, 0.22, 0.48), alpha=alpha * 0.95)
            cv.rect(x0, cy - 22, 86, 44, color, alpha=alpha * 0.9, fill=False, width=2, glow=glow * 0.5)
            for k in range(1, 4):
                xx = x0 + k * 86 / 4
                cv.line([(xx, cy - 22), (xx, cy + 22)], color, width=1, alpha=alpha * 0.45)
            cv.line([(x0, cy), (x0 + 86, cy)], color, width=1, alpha=alpha * 0.45)
        # body
        cv.rect(cx - 24, cy - 30, 48, 60, (0.85, 0.72, 0.38), alpha=alpha, radius=4)
        cv.rect(cx - 24, cy - 30, 48, 60, L.WHITE, alpha=alpha * 0.6, fill=False, width=1.5, radius=4)
        cv.line([(cx - 24, cy - 8), (cx + 24, cy - 8)], (0.5, 0.4, 0.2), width=1.5, alpha=alpha)
        # antenna
        cv.line([(cx, cy + 30), (cx, cy + 46)], L.WHITE, width=3, alpha=alpha)
        cv.circle(cx, cy + 52, 8, L.WHITE, alpha=alpha, glow=glow)


def phone(cv: Canvas, x, y, s, t, alpha=1.0, dot_alpha=1.0, earth=None):
    if alpha <= 0.002:
        return
    w, h = 330 * s, 650 * s
    x0, y0 = x - w / 2, y - h / 2
    cv.rect(x0 - 6 * s, y0 - 6 * s, w + 12 * s, h + 12 * s, (0.08, 0.10, 0.16), alpha=alpha,
            radius=54 * s)
    cv.rect(x0 - 6 * s, y0 - 6 * s, w + 12 * s, h + 12 * s, (0.55, 0.65, 0.85), alpha=alpha * 0.8,
            fill=False, width=2.5 * s, radius=54 * s)

    def scr(c):
        from .gfx import rounded_rect
        c.new_path()
        rounded_rect(c, x0, y0, w, h, 46 * s)

    with cv.clip(scr):
        cv.rect(x0, y0, w, h, (0.03, 0.06, 0.13), alpha=alpha)
        rng = np.random.default_rng(4)
        # map: blocks + roads
        for k in range(14):
            yy = y0 + (k + 0.5) * h / 14 + rng.uniform(-8, 8) * s
            cv.line([(x0, yy), (x0 + w, yy + rng.uniform(-20, 20) * s)], (0.2, 0.32, 0.55),
                    width=(5 if k % 4 == 0 else 2) * s, alpha=alpha * 0.8)
        for k in range(7):
            xx = x0 + (k + 0.5) * w / 7 + rng.uniform(-8, 8) * s
            cv.line([(xx, y0), (xx + rng.uniform(-25, 25) * s, y0 + h)], (0.2, 0.32, 0.55),
                    width=(5 if k % 3 == 0 else 2) * s, alpha=alpha * 0.8)
        cv.curve((x0, y0 + h * 0.8), (x0 + w * 0.3, y0 + h * 0.6), (x0 + w * 0.6, y0 + h * 0.75),
                 (x0 + w, y0 + h * 0.55), (0.15, 0.4, 0.75), width=10 * s, alpha=alpha * 0.7)
        # location dot
        ph = (t * 0.9) % 1.0
        cv.circle(x, y, 70 * s * (0.3 + ph), L.BLUE, alpha=alpha * dot_alpha * 0.35 * (1 - ph))
        cv.circle(x, y, 60 * s, L.BLUE, alpha=alpha * dot_alpha * 0.18)
        cv.circle(x, y, 17 * s, L.WHITE, alpha=alpha * dot_alpha)
        cv.circle(x, y, 12 * s, (0.2, 0.55, 1.0), alpha=alpha * dot_alpha, glow=0.8)
    cv.rect(x - 55 * s, y0 + 14 * s, 110 * s, 26 * s, (0.0, 0.0, 0.0), alpha=alpha, radius=13 * s)


# --------------------------------------------------------------------------- 3D grid fabric

class Fabric:
    """A perspective rubber-sheet grid with a gravity well at the origin."""

    def __init__(self, n=29, extent=7.0, samples=70):
        self.n, self.ext, self.samples = n, extent, samples
        self.cam_pos = np.array([0.0, 6.2, -9.5])
        self.cam_tgt = np.array([0.0, -0.9, 1.2])
        self.focal = 1050.0
        self.center = (W / 2, 900.0)

    def height(self, x, z, depth, a=1.25):
        r2 = x * x + z * z
        return -depth / np.sqrt(1 + r2 / (a * a))

    def project(self, P):
        C, T = np.asarray(self.cam_pos, float), np.asarray(self.cam_tgt, float)
        f = T - C
        f = f / np.linalg.norm(f)
        r = np.cross(f, np.array([0.0, 1.0, 0.0]))
        r = r / np.linalg.norm(r)
        u = np.cross(r, f)
        d = P - C
        xc, yc, zc = d @ r, d @ u, d @ f
        zc = np.maximum(zc, 0.05)
        return (self.center[0] + self.focal * xc / zc, self.center[1] - self.focal * yc / zc, zc)

    def point(self, x, z, depth, lift=0.0):
        P = np.array([[x, self.height(x, z, depth) + lift, z]])
        sx, sy, zc = self.project(P)
        return float(sx[0]), float(sy[0]), float(zc[0])

    def draw(self, cv: Canvas, depth, alpha=1.0, far=L.CYAN, near=L.AMBER, ripple=0.0, t=0.0):
        if alpha <= 0.002:
            return
        e, n, m = self.ext, self.n, self.samples
        vals = np.linspace(-e, e, n)
        s = np.linspace(-e, e, m)
        c = cv.b
        c.set_line_width(1.6)
        for k, v in enumerate(vals):
            for axis in (0, 1):
                if axis == 0:
                    X, Z = s, np.full_like(s, v)
                else:
                    X, Z = np.full_like(s, v), s
                Y = self.height(X, Z, depth)
                if ripple > 0:
                    rr = np.sqrt(X * X + Z * Z)
                    Y = Y + ripple * 0.12 * np.sin(rr * 2.2 - t * 5.0) * np.exp(-rr * 0.25)
                sx, sy, zc = self.project(np.stack([X, Y, Z], axis=1))
                deep = np.clip(-Y / max(depth, 1e-6), 0, 1) if depth > 0 else np.zeros_like(Y)
                fog = np.clip(1.25 - (zc - 6.0) / 12.0, 0.08, 1.0)
                for j in range(0, m - 1, 2):
                    col = mix(far, near, float(deep[j]) ** 0.8)
                    a = alpha * 0.55 * float(fog[j]) * (0.6 + 0.4 * float(deep[j]))
                    c.set_source_rgba(*col, a)
                    c.move_to(sx[j], sy[j])
                    c.line_to(sx[j + 1], sy[j + 1])
                    c.line_to(sx[min(j + 2, m - 1)], sy[min(j + 2, m - 1)])
                    c.stroke()
                    if deep[j] > 0.35:
                        cv.g.set_source_rgba(*col, a * 0.7)
                        cv.g.set_line_width(2.5)
                        cv.g.move_to(sx[j], sy[j])
                        cv.g.line_to(sx[min(j + 2, m - 1)], sy[min(j + 2, m - 1)])
                        cv.g.stroke()


# --------------------------------------------------------------------------- Earth cross-section

LAYERS = [  # (outer radius fraction, inner colour, outer colour, label)
    (1.000, (0.92, 0.42, 0.20), (0.55, 0.20, 0.12), "CRUST"),
    (0.990, (0.98, 0.45, 0.16), (0.48, 0.12, 0.07), "MANTLE"),
    (0.546, (1.00, 0.70, 0.25), (0.95, 0.40, 0.10), "OUTER CORE"),
    (0.192, (1.00, 0.97, 0.85), (1.00, 0.78, 0.35), "INNER CORE"),
]


def cross_section(cv: Canvas, x, y, r, t, alpha=1.0, glow=1.0):
    """Concentric interior layers with true radius ratios (PREM: 3480 km / 1220 km / 6371 km)."""
    if alpha <= 0.002:
        return
    for k, (fr, cin, cout, _) in enumerate(LAYERS):
        rr = r * fr
        pat = cairo.RadialGradient(x, y, 0, x, y, rr)
        inner_fr = LAYERS[k + 1][0] / fr if k + 1 < len(LAYERS) else 0.0
        pat.add_color_stop_rgba(0, *cin, alpha)
        pat.add_color_stop_rgba(max(inner_fr, 0.0), *cin, alpha)
        pat.add_color_stop_rgba(1, *cout, alpha)
        cv.b.new_path()
        cv.b.arc(x, y, rr, 0, 2 * math.pi)
        cv.b.set_source(pat)
        cv.b.fill()
        cv.circle(x, y, rr, (1.0, 0.85, 0.6), alpha=alpha * 0.35, fill=False, width=1.5)
    # convection swirl hints in the mantle
    c = cv.b
    c.set_line_width(2.0)
    for k in range(10):
        a0 = k / 10 * 2 * math.pi + t * 0.15
        rr = r * (0.62 + 0.28 * ((k * 37) % 10) / 10)
        c.set_source_rgba(1.0, 0.6, 0.3, 0.13 * alpha)
        c.arc(x, y, rr, a0, a0 + 0.9)
        c.stroke()
    # core heat glow
    if glow > 0:
        cv.radial(x, y, r * 0.55, (1.0, 0.75, 0.35), alpha=0.55 * alpha, glow=glow, layer_base=False)
        cv.radial(x, y, r * 0.25, (1.0, 0.95, 0.8), alpha=0.9 * alpha, glow=glow, layer_base=False)
