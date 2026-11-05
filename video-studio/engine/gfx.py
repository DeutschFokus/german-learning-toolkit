"""Drawing layer for the LUMEN look.

A Canvas has three cairo layers:
  base  everything visible
  glow  a half-resolution copy of what should bloom (blurred in postfx)
  ui    captions and overlays, composited after grading so they stay crisp

Draw helpers write to base and, when glow > 0, also to glow. Transforms and
groups apply to base and glow together.
"""
from __future__ import annotations

import math
from contextlib import contextmanager

import cairo
import numpy as np

W, H = 1080, 1920


# --------------------------------------------------------------------------- the look

def hexrgb(h: str) -> tuple[float, float, float]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


class Look:
    """LUMEN visual identity. Change it here, every episode follows."""
    BG_TOP = hexrgb("#03050c")
    BG_MID = hexrgb("#07102a")
    BG_BOT = hexrgb("#020309")
    CYAN = hexrgb("#55e6ff")      # fast time / up / signal
    AMBER = hexrgb("#ffb347")     # slow time / gravity / deep
    CORE = hexrgb("#ff7a2f")      # heat, the deep interior
    WHITE = hexrgb("#f3f6ff")
    DIM = hexrgb("#7d8db0")
    FAINT = hexrgb("#2a3a5e")
    MAGENTA = hexrgb("#ff4f8b")   # error / warning
    MINT = hexrgb("#62ffb5")      # confirmed / correct
    BLUE = hexrgb("#2f6bff")

    DISPLAY = "Inter Display Black"
    DISPLAY_XB = "Inter Display ExtraBold"
    DISPLAY_B = "Inter Display"          # with bold weight
    UI = "Inter SemiBold"
    UI_MED = "Inter Medium"
    MONO = "JetBrains Mono"
    MONO_XB = "JetBrains Mono ExtraBold"

    # safe zones for Shorts / TikTok / Reels / FB Reels (1080x1920)
    SAFE_TOP = 230
    SAFE_BOTTOM = 1480      # below this: platform captions + buttons
    SAFE_LEFT = 80
    SAFE_RIGHT = 940        # right rail icons live beyond this (y > ~880)
    CAPTION_Y = 1338


L = Look


# --------------------------------------------------------------------------- easing

def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def prog(t, t0, t1):
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    return clamp((t - t0) / (t1 - t0))


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_out_cubic(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in_cubic(x):
    x = clamp(x)
    return x ** 3


def ease_in_out(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_out_expo(x):
    x = clamp(x)
    return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)


def ease_in_expo(x):
    x = clamp(x)
    return 0.0 if x <= 0 else 2 ** (10 * x - 10)


def ease_out_back(x, s=1.70158):
    x = clamp(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def lerp(a, b, x):
    return a + (b - a) * x


def mix(c1, c2, x):
    return tuple(lerp(a, b, x) for a, b in zip(c1, c2))


def window(t, t0, t1, fade_in=0.25, fade_out=0.25):
    """1 inside [t0, t1], smooth ramps outside."""
    return smooth(prog(t, t0 - fade_in, t0)) * (1 - smooth(prog(t, t1, t1 + fade_out)))


# --------------------------------------------------------------------------- canvas

class Canvas:
    def __init__(self, bg_alpha=1.0):
        self.base_s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        self.glow_s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W // 2, H // 2)
        self.ui_s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        self.b = cairo.Context(self.base_s)
        self.g = cairo.Context(self.glow_s)
        self.g.scale(0.5, 0.5)
        self.u = cairo.Context(self.ui_s)
        for c in (self.b, self.g, self.u):
            c.set_line_cap(cairo.LINE_CAP_ROUND)
            c.set_line_join(cairo.LINE_JOIN_ROUND)
            fo = cairo.FontOptions()
            fo.set_antialias(cairo.ANTIALIAS_GRAY)
            fo.set_hint_style(cairo.HINT_STYLE_NONE)
            fo.set_hint_metrics(cairo.HINT_METRICS_OFF)
            c.set_font_options(fo)
        self.flash = 0.0          # full-frame flash amount, read by postfx
        self.shake = (0.0, 0.0)
        self.aberration = 0.0

    # ---- layer plumbing
    def both(self, glow=True):
        return (self.b, self.g) if glow else (self.b,)

    @contextmanager
    def transform(self, tx=0.0, ty=0.0, s=1.0, rot=0.0, cx=W / 2, cy=H / 2):
        """Scale/rotate about (cx, cy), then translate. Applies to base+glow."""
        for c in (self.b, self.g):
            c.save()
            c.translate(cx + tx, cy + ty)
            c.rotate(rot)
            c.scale(s, s)
            c.translate(-cx, -cy)
        try:
            yield
        finally:
            for c in (self.b, self.g):
                c.restore()

    @contextmanager
    def group(self, alpha=1.0):
        for c in (self.b, self.g):
            c.push_group()
        try:
            yield
        finally:
            for c in (self.b, self.g):
                c.pop_group_to_source()
                c.paint_with_alpha(clamp(alpha))

    @contextmanager
    def clip(self, path_fn):
        """path_fn(ctx) builds a path; drawing inside is clipped to it."""
        for c in (self.b, self.g):
            c.save()
            path_fn(c)
            c.clip()
        try:
            yield
        finally:
            for c in (self.b, self.g):
                c.restore()

    # ---- primitives
    def _src(self, c, color, alpha):
        c.set_source_rgba(*color, clamp(alpha))

    def line(self, pts, color=L.WHITE, width=3.0, alpha=1.0, glow=0.0, dash=None):
        if len(pts) < 2 or alpha <= 0.002:
            return
        for i, c in enumerate(self.both(glow > 0)):
            a = alpha if i == 0 else alpha * glow
            c.new_path()
            c.move_to(*pts[0])
            for p in pts[1:]:
                c.line_to(*p)
            c.set_line_width(width if i == 0 else width * 1.6)
            c.set_dash(dash or [])
            self._src(c, color, a)
            c.stroke()
            c.set_dash([])

    def curve(self, p0, p1, p2, p3, color=L.WHITE, width=3.0, alpha=1.0, glow=0.0):
        for i, c in enumerate(self.both(glow > 0)):
            c.new_path()
            c.move_to(*p0)
            c.curve_to(*p1, *p2, *p3)
            c.set_line_width(width if i == 0 else width * 1.6)
            self._src(c, color, alpha if i == 0 else alpha * glow)
            c.stroke()

    def circle(self, x, y, r, color=L.WHITE, alpha=1.0, glow=0.0, fill=True, width=3.0):
        if r <= 0 or alpha <= 0.002:
            return
        for i, c in enumerate(self.both(glow > 0)):
            c.new_path()
            c.arc(x, y, r, 0, 2 * math.pi)
            self._src(c, color, alpha if i == 0 else alpha * glow)
            if fill:
                c.fill()
            else:
                c.set_line_width(width if i == 0 else width * 1.6)
                c.stroke()

    def arc(self, x, y, r, a0, a1, color=L.WHITE, alpha=1.0, width=3.0, glow=0.0):
        if alpha <= 0.002 or r <= 0:
            return
        for i, c in enumerate(self.both(glow > 0)):
            c.new_path()
            c.arc(x, y, r, a0, a1)
            c.set_line_width(width if i == 0 else width * 1.6)
            self._src(c, color, alpha if i == 0 else alpha * glow)
            c.stroke()

    def rect(self, x, y, w, h, color=L.WHITE, alpha=1.0, fill=True, width=2.0, radius=0.0, glow=0.0):
        if alpha <= 0.002:
            return
        for i, c in enumerate(self.both(glow > 0)):
            c.new_path()
            rounded_rect(c, x, y, w, h, radius)
            self._src(c, color, alpha if i == 0 else alpha * glow)
            if fill:
                c.fill()
            else:
                c.set_line_width(width if i == 0 else width * 1.6)
                c.stroke()

    def radial(self, x, y, r, color, alpha=1.0, glow=0.0, inner=0.0, layer_base=True):
        """Soft radial light blob."""
        cs = ((self.b,) if layer_base else ()) + ((self.g,) if glow > 0 else ())
        for c in cs:
            a = alpha if c is self.b else alpha * glow
            pat = cairo.RadialGradient(x, y, r * inner, x, y, r)
            pat.add_color_stop_rgba(0, *color, a)
            pat.add_color_stop_rgba(0.45, *color, a * 0.35)
            pat.add_color_stop_rgba(1, *color, 0)
            c.new_path()
            c.arc(x, y, r, 0, 2 * math.pi)
            c.set_source(pat)
            c.fill()

    def poly(self, pts, color, alpha=1.0, glow=0.0):
        for i, c in enumerate(self.both(glow > 0)):
            c.new_path()
            c.move_to(*pts[0])
            for p in pts[1:]:
                c.line_to(*p)
            c.close_path()
            self._src(c, color, alpha if i == 0 else alpha * glow)
            c.fill()

    # ---- text
    def text(self, s, x, y, size, font=L.DISPLAY, color=L.WHITE, alpha=1.0, anchor="center",
             glow=0.0, tracking=0.0, bold=False, layer="scene", outline=None, outline_w=0.0,
             shadow=0.0):
        """Draw text with its vertical centre (cap-height middle) at y.

        tracking: extra letter spacing in em. layer: 'scene' (base+glow) or 'ui'.
        outline: colour of a stroke drawn under the fill (legibility).
        """
        if alpha <= 0.002 or not s:
            return 0.0
        ctxs = [self.u] if layer == "ui" else list(self.both(glow > 0))
        width = text_width(self.b, s, size, font, tracking, bold)
        if anchor == "center":
            x0 = x - width / 2
        elif anchor == "right":
            x0 = x - width
        else:
            x0 = x
        base_y = y + size * 0.365
        for i, c in enumerate(ctxs):
            a = alpha if (i == 0 or layer == "ui") else alpha * glow
            c.select_font_face(font, cairo.FONT_SLANT_NORMAL,
                               cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
            c.set_font_size(size)
            c.new_path()
            _text_path(c, s, x0, base_y, size, tracking)
            if shadow > 0 and (i == 0 or layer == "ui"):
                c.save()
                for k, (dx, dy, sa) in enumerate(((0, 6, 0.30), (0, 3, 0.35), (0, 10, 0.18))):
                    c.save()
                    c.translate(dx, dy)
                    c.set_source_rgba(0, 0, 0.02, a * shadow * sa)
                    c.fill_preserve()
                    c.restore()
                c.restore()
            if outline is not None and outline_w > 0 and (i == 0 or layer == "ui"):
                c.set_source_rgba(*outline, a)
                c.set_line_width(outline_w)
                c.stroke_preserve()
            c.set_source_rgba(*color, a)
            c.fill()
        return width


def _text_path(c, s, x0, base_y, size, tracking):
    if tracking == 0:
        c.move_to(x0, base_y)
        c.text_path(s)
        return
    x = x0
    for ch in s:
        c.move_to(x, base_y)
        c.text_path(ch)
        x += c.text_extents(ch).x_advance + tracking * size


_width_cache: dict = {}


def text_width(c, s, size, font, tracking=0.0, bold=False):
    key = (s, size, font, tracking, bold)
    if key in _width_cache:
        return _width_cache[key]
    c.save()
    c.select_font_face(font, cairo.FONT_SLANT_NORMAL,
                       cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)
    if tracking == 0:
        w = c.text_extents(s).x_advance
    else:
        w = sum(c.text_extents(ch).x_advance + tracking * size for ch in s) - tracking * size
    c.restore()
    _width_cache[key] = w
    return w


def rounded_rect(c, x, y, w, h, r):
    r = max(0.0, min(r, w / 2, h / 2))
    if r == 0:
        c.rectangle(x, y, w, h)
        return
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    c.close_path()


# --------------------------------------------------------------------------- shared props

class Starfield:
    """Three parallax layers of stars plus slow drifting dust."""

    def __init__(self, seed=7):
        rng = np.random.default_rng(seed)
        self.layers = []
        for n, rmin, rmax, depth, amin, amax in ((260, 0.6, 1.3, 0.15, 0.25, 0.65),
                                                 (90, 1.0, 1.9, 0.35, 0.35, 0.85),
                                                 (22, 1.8, 2.8, 0.7, 0.55, 1.0)):
            xs = rng.uniform(-300, W + 300, n)
            ys = rng.uniform(-400, H + 400, n)
            rs = rng.uniform(rmin, rmax, n)
            al = rng.uniform(amin, amax, n)
            ph = rng.uniform(0, 2 * math.pi, n)
            sp = rng.integers(6, 22, n) * (2 * math.pi / 60.0)   # integer cycles per 60 s
            tint = rng.uniform(0, 1, n)
            self.layers.append((xs, ys, rs, al, ph, sp, tint, depth))
        m = 26
        # drift = whole screen-wraps per 60 s (seamless loop)
        self.dust = (rng.uniform(0, W, m), rng.uniform(0, H, m), rng.uniform(2, 7, m),
                     rng.uniform(0.04, 0.12, m), np.zeros(m),
                     -rng.integers(1, 3, m) * (H + 40) / 60.0)

    def draw(self, cv: Canvas, t, cam_x=0.0, cam_y=0.0, cam_s=1.0, alpha=1.0, warp=0.0, dust_alpha=1.0):
        c = cv.b
        for xs, ys, rs, al, ph, sp, tint, depth in self.layers:
            ox, oy = -cam_x * depth, -cam_y * depth
            s = 1 + (cam_s - 1) * depth
            tw = 0.75 + 0.25 * np.sin(t * sp + ph)
            for x, y, r, a, k, ti in zip(xs, ys, rs, al, tw, tint):
                px = (x + ox - W / 2) * s + W / 2
                py = (y + oy - H / 2) * s + H / 2
                if px < -10 or px > W + 10 or py < -10 or py > H + 10:
                    continue
                col = mix((0.75, 0.85, 1.0), (1.0, 0.92, 0.8), ti)
                c.set_source_rgba(*col, a * k * alpha)
                if warp > 0:
                    dx, dy = px - W / 2, py - H / 2
                    d = math.hypot(dx, dy) + 1e-6
                    L_ = warp * d * 0.25
                    c.set_line_width(r * 1.6)
                    c.move_to(px, py)
                    c.line_to(px + dx / d * L_, py + dy / d * L_)
                    c.stroke()
                else:
                    c.arc(px, py, r * s, 0, 2 * math.pi)
                    c.fill()
                if r > 2.2 and alpha > 0.1:
                    cv.g.set_source_rgba(*col, 0.5 * a * k * alpha)
                    cv.g.arc(px, py, r * 2.2, 0, 2 * math.pi)
                    cv.g.fill()
        xs, ys, rs, al, vx, vy = self.dust
        if dust_alpha <= 0.003:
            return
        for x, y, r, a, ux, uy in zip(xs, ys, rs, al * dust_alpha, vx, vy):
            px = (x + ux * t - cam_x * 0.9) % (W + 40) - 20
            py = (y + uy * t - cam_y * 0.9) % (H + 40) - 20
            pat = cairo.RadialGradient(px, py, 0, px, py, r * 3)
            pat.add_color_stop_rgba(0, 0.7, 0.85, 1.0, a * alpha)
            pat.add_color_stop_rgba(1, 0.7, 0.85, 1.0, 0)
            c.set_source(pat)
            c.arc(px, py, r * 3, 0, 2 * math.pi)
            c.fill()


def background(cv: Canvas, t, haze=(0.5, 0.42), haze_color=None, haze_amt=1.0):
    c = cv.b
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *L.BG_TOP)
    g.add_color_stop_rgb(0.5, *L.BG_MID)
    g.add_color_stop_rgb(1, *L.BG_BOT)
    c.set_source(g)
    c.paint()
    hc = haze_color or (0.12, 0.25, 0.6)
    x, y = haze[0] * W, haze[1] * H
    r = 1100
    pat = cairo.RadialGradient(x, y, 0, x, y, r)
    pat.add_color_stop_rgba(0, *hc, 0.32 * haze_amt)
    pat.add_color_stop_rgba(0.5, *hc, 0.10 * haze_amt)
    pat.add_color_stop_rgba(1, *hc, 0)
    c.set_source(pat)
    c.paint()


def blueprint_grid(cv: Canvas, alpha=0.05, step=60, ox=0.0, oy=0.0, color=None):
    c = cv.b
    col = color or (0.45, 0.6, 1.0)
    c.set_line_width(1.0)
    c.set_source_rgba(*col, alpha)
    x = (ox % step) - step
    while x < W + step:
        c.move_to(x, 0)
        c.line_to(x, H)
        x += step
    y = (oy % step) - step
    while y < H + step:
        c.move_to(0, y)
        c.line_to(W, y)
        y += step
    c.stroke()


def ring_clock(cv: Canvas, x, y, r, t, rate=1.0, color=L.CYAN, alpha=1.0, glow=0.8,
               ticks=12, phase=0.0, pulse_every=None, label=None, label_color=None):
    """Glowing ring clock. rate: revolutions of the hand per 4 s (visual only)."""
    if alpha <= 0.002:
        return
    cv.circle(x, y, r * 1.02, (0.02, 0.04, 0.09), alpha=0.75 * alpha)
    cv.circle(x, y, r, color, alpha=alpha, fill=False, width=max(2.0, r * 0.06), glow=glow)
    for k in range(ticks):
        a = k / ticks * 2 * math.pi
        r0 = r * (0.78 if k % 3 == 0 else 0.84)
        cv.line([(x + math.cos(a) * r0, y + math.sin(a) * r0),
                 (x + math.cos(a) * r * 0.92, y + math.sin(a) * r * 0.92)],
                color, width=max(1.5, r * (0.05 if k % 3 == 0 else 0.03)), alpha=0.8 * alpha)
    ang = (t * rate / 4.0 + phase) * 2 * math.pi - math.pi / 2
    cv.line([(x, y), (x + math.cos(ang) * r * 0.72, y + math.sin(ang) * r * 0.72)],
            L.WHITE, width=max(2.0, r * 0.06), alpha=alpha, glow=glow)
    cv.circle(x, y, max(2.5, r * 0.08), L.WHITE, alpha=alpha, glow=glow)
    if pulse_every:
        ph = (t / pulse_every + phase) % 1.0
        cv.circle(x, y, r * (1.0 + 0.9 * ease_out_cubic(ph)), color,
                  alpha=alpha * 0.55 * (1 - ph) ** 1.5, fill=False, width=2.5, glow=glow * 0.6)
    if label:
        cv.text(label, x, y + r + 34, 26, font=L.MONO, color=label_color or color,
                alpha=alpha * 0.9, tracking=0.12)
