"""EP004 — The Deepest Hole Ever Dug (the Kola Superdeep Borehole).

Narrated by the creator (no AI voice in any deliverable). Until his take
exists, animation timing comes from a scratch read (build/timeline_scratch.json);
`build.py human take.wav` re-times everything to the real voice.

One continuous camera: from the Arctic night (aurora, snow, a rusty cap) down
a 12 km borehole, out to the whole Earth, back to the cap, up to Voyager and
home again — the last frame is the first.

guide=True renders the record-along version (teleprompter band + captions).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))

import cairo  # noqa: E402
import cv2  # noqa: E402
import numpy as np  # noqa: E402

cv2.setNumThreads(1)

from engine.captions import Captions  # noqa: E402
from engine.geo import RockColumn, RustyCap, Snowfield, dinner_plate, drill_bit, drill_rig, microfossil, voyager  # noqa: E402
from engine.gfx import (H, L, W, Canvas, Starfield, _text_path, background, clamp, ease_in_cubic,  # noqa: E402
                        ease_in_out, ease_out_back, ease_out_cubic, ease_out_expo, lerp, mix, prog, rounded_rect,
                        smooth, text_width, window)
from engine.nature import stamp  # noqa: E402
from engine.particles import Aurora, Particles  # noqa: E402
from engine.postfx import Post  # noqa: E402
from engine.props import cross_section  # noqa: E402
from engine.timeline import Timeline  # noqa: E402

PPK = 520.0                 # rock column: px per km
GROUND = 1100.0             # screen y of the surface in the cut-away rig shot
BIT_Y = 1150.0              # screen y the camera keeps the drill bit at
CAM0 = H / 2 - GROUND       # camera (world y at screen centre) in the rig shot
BOTTOM_KM = 12.262
TARGET_KM = 15.0
HORIZON = 1000.0            # perspective shots
CAP = (540.0, 1235.0)
RULER = (92.0, 470.0, 1190.0)       # x, y(0 km), y(15 km)
CMP_TOP, CMP_PPK, KX, OX = 380.0, 820.0 / BOTTOM_KM, 660.0, 380.0
OCEAN_KM = 10.935
EARTH_R, EARTH_C = 600.0, (540.0, 1090.0)
SKY_TILT = 1450.0

ACCENTS = {"L01": L.AMBER, "L02": L.CYAN, "L03": L.AMBER, "L04": L.MINT, "L05": L.MAGENTA, "L06": L.CYAN,
           "L07": L.CORE, "L08": L.AMBER, "L09": L.AMBER, "L10": L.CYAN, "L11": L.AMBER, "L12": L.AMBER,
           "L13": L.CYAN, "L14": L.AMBER}
CONTINUOUS = {"descent", "heat", "stop", "scale", "cap", "outro"}   # one camera: no dissolve into these
X_IN = {"rig": 0.22}
X_OUT = {"hook": 0.22}


def htext(cv, s, x, y, size, color=L.WHITE, alpha=1.0, glow=0.0, font=L.DISPLAY, anchor="center",
          tracking=0.0, shadow=0.7, glow_alpha=None):
    """Crisp text on the UI layer (no motion blur / depth of field), with optional bloom.
    glow_alpha overrides the bloom strength (e.g. a pulse on text that is already drawn)."""
    k = getattr(cv, "ui_alpha", 1.0)
    alpha *= k
    ga = alpha * glow if glow_alpha is None else glow_alpha * k
    if alpha <= 0.003 and ga <= 0.003:
        return 0.0
    w = text_width(cv.b, s, size, font, tracking)
    if alpha > 0.003:
        cv.text(s, x, y, size, font=font, color=color, alpha=alpha, anchor=anchor, tracking=tracking,
                layer="ui", shadow=shadow)
    if ga > 0.003:
        x0 = x - w / 2 if anchor == "center" else (x - w if anchor == "right" else x)
        g = cv.g
        g.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        g.set_font_size(size)
        g.new_path()
        _text_path(g, s, x0, y + size * 0.365, size, tracking)
        g.set_source_rgba(*color, clamp(ga))
        g.fill()
    return w


def uline(cv, pts, color, width=2.0, alpha=1.0, dash=None):
    alpha *= getattr(cv, "ui_alpha", 1.0)
    if alpha <= 0.003 or len(pts) < 2:
        return
    u = cv.u
    u.new_path()
    u.move_to(*pts[0])
    for p in pts[1:]:
        u.line_to(*p)
    u.set_dash(dash or [])
    u.set_line_width(width)
    u.set_source_rgba(*color, clamp(alpha))
    u.stroke()
    u.set_dash([])


def upoly(cv, pts, color, alpha=1.0):
    alpha *= getattr(cv, "ui_alpha", 1.0)
    if alpha <= 0.003:
        return
    u = cv.u
    u.new_path()
    u.move_to(*pts[0])
    for p in pts[1:]:
        u.line_to(*p)
    u.close_path()
    u.set_source_rgba(*color, clamp(alpha))
    u.fill()


class ui_scope:
    """Apply a scene transition (alpha, scale about (cx, cy), vertical offset) to the UI layer too."""

    def __init__(self, cv, a, s=1.0, ty=0.0, cx=W / 2, cy=H / 2):
        self.cv, self.a, self.s, self.ty, self.cx, self.cy = cv, a, s, ty, cx, cy

    def __enter__(self):
        cv = self.cv
        self.prev = getattr(cv, "ui_alpha", 1.0)
        cv.ui_alpha = self.prev * self.a
        u = cv.u
        u.save()
        u.translate(self.cx, self.cy + self.ty)
        u.scale(self.s, self.s)
        u.translate(-self.cx, -self.cy)
        return self

    def __exit__(self, *exc):
        self.cv.u.restore()
        self.cv.ui_alpha = self.prev
        return False


def seg(t, keys):
    """Piecewise eased value: keys = [(t0, t1, v0, v1, ease), ...] in time order; holds between."""
    v = keys[0][2]
    for t0, t1, v0, v1, ease in keys:
        if t < t0:
            return v
        v = lerp(v0, v1, ease(prog(t, t0, t1)))
    return v


class Episode:
    def __init__(self, timeline_path, captions=True, grain=0.007, guide=False):
        self.T = Timeline(timeline_path)
        self.fps = self.T.fps
        self.duration = self.T.duration
        loop = self.duration
        self.post = Post(grain=grain)
        self.stars = Starfield(seed=31)
        self.caps = Captions(self.T, accent_by_line=ACCENTS) if captions else None
        self.guide = guide
        self.rock = RockColumn(depth_km=14.6, px_per_km=PPK, seed=7)
        self.cap = RustyCap(r=230, seed=12)
        self.field = Snowfield(horizon=int(HORIZON), seed=21)
        self.aurora = Aurora(seed=4, y_base=880.0, loop=loop)
        self.snow = Particles(n=170, seed=2, kind="snow", loop=loop)
        self.dust = Particles(n=120, seed=5, kind="dust", loop=loop)
        self.embers = Particles(n=110, seed=9, kind="embers", loop=loop)
        rng = np.random.default_rng(44)
        self.fossils = []
        while len(self.fossils) < 34:
            x = rng.uniform(130, 950)
            if abs(x - 540) < 70:
                continue
            self.fossils.append((x, rng.uniform(5.55, 6.45) * PPK, rng.uniform(7, 13), int(rng.integers(0, 2)),
                                 rng.uniform(0, 6.28), rng.uniform(0, 6.28)))
        st = self.T.scene_starts()
        self.scenes = [(sid, s0, st[i + 1][1] if i + 1 < len(st) else self.duration)
                       for i, (sid, s0) in enumerate(st)]
        self.c = self._cues()
        c = self.c
        # ---- the drill's depth (km) over time, anchored to the words
        self.depth_keys = [
            (c["started"], c["aiming"], 0.0, 0.22, ease_in_out),
            (c["aiming"], c["dive"], 0.22, 0.25, smooth),
            (c["dive"], c["km6"] + 0.2, 0.25, 6.0, ease_in_out),
            (c["km6"] + 0.2, c["L04end"] + 0.2, 6.0, 6.12, smooth),
            (c["L04end"] + 0.2, c["seven"] + 0.35, 6.12, 7.05, ease_in_out),
            (c["seven"] + 0.35, c["L06"], 7.05, 7.12, smooth),
            (c["L06"], c["cracked"] + 0.4, 7.12, 8.30, ease_in_out),
            (c["cracked"] + 0.4, c["L07"] - 0.1, 8.30, 8.42, smooth),
            (c["L07"] - 0.1, c["n180"] + 0.2, 8.42, 11.70, ease_in_out),
            (c["n180"] + 0.2, c["L09"], 11.70, 11.90, smooth),
            (c["L09"], c["meters"] + 0.25, 11.90, BOTTOM_KM, smooth),
        ]
        self.t_bottom = c["meters"] + 0.25          # the bit hits bottom in the pause after "meters," 

    def _cues(self):
        T = self.T
        w = lambda l, k: T.word(l, k).start  # noqa: E731
        c = {"sc_" + sid: (s0, s1) for sid, s0, s1 in self.scenes}
        c.update({
            "n12": w("L01", "12"), "deep1": w("L01", "deep."), "L01end": T.line("L01").end,
            "L02": T.line("L02").start, "narrower": w("L02", "narrower"), "dinner": w("L02", "dinner"),
            "plate": w("L02", "plate."), "L02end": T.line("L02").end,
            "L03": T.line("L03").start, "y1970": w("L03", "1970,"), "soviet": w("L03", "Soviet"),
            "started": w("L03", "started"), "drilling": w("L03", "drilling,"), "aiming": w("L03", "aiming"),
            "n15": w("L03", "15"), "km15": w("L03", "kilometers."), "L03end": T.line("L03").end,
            "L04": T.line("L04").start, "six": w("L04", "6"), "km6": w("L04", "kilometers:"),
            "fossils": w("L04", "fossils"), "microscopic": w("L04", "microscopic"), "plankton": w("L04", "plankton."),
            "L04end": T.line("L04").end,
            "L05": T.line("L05").start, "seven": w("L05", "7,"), "predicted": w("L05", "predicted"),
            "simply": w("L05", "simply"), "wasnt": w("L05", "wasn't"), "there": w("L05", "there."),
            "L05end": T.line("L05").end,
            "L06": T.line("L06").start, "cracked": w("L06", "cracked"), "soaked": w("L06", "soaked"),
            "water": w("L06", "water"), "nobody": w("L06", "nobody"), "L06end": T.line("L06").end,
            "L07": T.line("L07").start, "bottom": w("L07", "bottom:"), "n180": w("L07", "180"),
            "degrees": w("L07", "degrees."), "almost": w("L07", "Almost"), "twice": w("L07", "twice"),
            "L07end": T.line("L07").end,
            "L08": T.line("L08").start, "soft": w("L08", "soft,"), "hole8": w("L08", "hole"),
            "squeezing": w("L08", "squeezing"), "shut": w("L08", "shut."), "L08end": T.line("L08").end,
            "L09": T.line("L09").start, "n12262": w("L09", "12,262"), "meters": w("L09", "meters,"),
            "further": w("L09", "further."), "L09end": T.line("L09").end,
            "L10": T.line("L10").start, "deepest10": w("L10", "deepest"), "ocean": w("L10", "ocean..."),
            "L10end": T.line("L10").end,
            "L11": T.line("L11").start, "pct": w("L11", "0.2%"), "earths": w("L11", "Earth's"),
            "center": w("L11", "center."), "L11end": T.line("L11").end,
            "L12": T.line("L12").start, "sealed": w("L12", "sealed"), "rusty": w("L12", "rusty"),
            "capw": w("L12", "cap."), "L12end": T.line("L12").end,
            "L13": T.line("L13").start, "spacecraft": w("L13", "spacecraft"),
            "interstellar": w("L13", "interstellar"), "L13end": T.line("L13").end,
            "L14": T.line("L14").start, "deeper14": w("L14", "deeper"), "own": w("L14", "own"),
            "planet": w("L14", "planet."), "L14end": T.line("L14").end,
        })
        c["dive"] = c["km15"] - 0.1
        return c

    # ------------------------------------------------------------------ frame
    def frame(self, i):
        t = i / self.fps
        cv = Canvas()
        self.draw(cv, t)
        return self.post.finish(cv, i)

    def draw(self, cv, t):
        background(cv, t, haze=(0.5, 0.36), haze_color=(0.08, 0.22, 0.40), haze_amt=0.8)
        n = len(self.scenes)
        for k, (sid, s0, s1) in enumerate(self.scenes):
            first, last = k == 0, k == n - 1
            cut_in = sid in CONTINUOUS
            cut_out = (not last) and self.scenes[k + 1][0] in CONTINUOUS
            Xi = 0.0 if (first or cut_in) else X_IN.get(sid, 0.18)
            Xo = 0.0 if (last or cut_out) else X_OUT.get(sid, 0.18)
            if not (s0 - Xi <= t < s1 + Xo):
                continue
            a, sc, ty, cx, cy = 1.0, 1.0, 0.0, W / 2, H / 2
            if Xi and t < s0 + Xi:
                p = prog(t, s0 - Xi, s0 + Xi)
                a, sc, ty = smooth(p), 0.97 + 0.03 * ease_out_cubic(p), 60 * (1 - ease_out_cubic(p))
            if Xo and t > s1 - Xo:
                p = prog(t, s1 - Xo, s1 + Xo)
                if sid == "hook":           # the well view drops away
                    a, sc, ty = 1 - smooth(p), 1 + 0.25 * ease_in_cubic(p), 0.0
                else:
                    a, sc, ty = 1 - smooth(p), 1 + 0.05 * ease_in_cubic(p), -60 * ease_in_cubic(p)
            if a <= 0.003:
                continue
            fn = getattr(self, "s_" + sid)
            if a >= 0.999 and sc == 1.0 and ty == 0.0:
                fn(cv, t)
            else:
                with cv.group(a), cv.transform(ty=ty, s=sc, cx=cx, cy=cy), ui_scope(cv, a, sc, ty, cx, cy):
                    fn(cv, t)
        if self.caps:
            self.caps.draw(cv, t)
        if self.guide:
            self._teleprompter(cv, t)

    # ================================================================== the Arctic surface (perspective)
    def _surface(self, cv, t, tilt=0.0, cap_s=1.0, cap_dy=0.0, alpha=1.0, ping=1.0):
        """tilt > 0 lifts the camera toward the sky (the world slides down)."""
        self.stars.draw(cv, t, cam_y=-tilt * 0.55, alpha=alpha, dust_alpha=0.0)
        self.aurora.draw(cv, t, alpha=0.5 * alpha, offset_y=tilt * 0.8)
        self._station(cv, 205.0, HORIZON + tilt + 2, alpha=alpha)
        self.field.draw(cv, alpha=alpha, dy=tilt, t=t, loop=self.duration)
        cx, cy = CAP[0], CAP[1] + cap_dy + tilt
        if cy - 200 * cap_s < H:
            # sonar-style depth pings from the cap (period 2.5 s: 24 per loop)
            if ping > 0:
                for k in range(2):
                    ph = (t / 2.5 + k * 0.5) % 1.0
                    r = 260 * cap_s * (0.9 + 1.6 * ease_out_cubic(ph))
                    a_ = alpha * ping * 0.35 * (1 - ph) ** 1.6 * smooth(ph / 0.08)
                    b = cv.b
                    b.save()
                    b.translate(cx, cy)
                    b.scale(1, 0.42)
                    b.arc(0, 0, r, 0, 2 * math.pi)
                    b.restore()
                    b.set_line_width(2.5)
                    b.set_source_rgba(*L.AMBER, a_)
                    b.stroke()
            self.cap.draw(cv, cx, cy, tilt=0.42, scale=cap_s, alpha=alpha, snow=0.75)
        self.snow.draw(cv, t, alpha=0.85 * alpha, cam_dy=-tilt, glow=0.25)
        cv.rays = (W / 2, 420 + tilt * 0.8, 0.30 * alpha)

    def _station(self, cv, x, y, alpha=1.0):
        """The abandoned SG-3 research buildings on the horizon (silhouette)."""
        if alpha <= 0.003 or y > H + 10:
            return
        col = (0.035, 0.045, 0.08)
        b = cv.b
        blocks = [(-150, 70, 300, 70), (-60, 175, 70, 105), (40, 120, 120, 50), (-200, 40, 60, 40)]
        for dx, hh, ww, _ in blocks:
            cv.rect(x + dx, y - hh, ww, hh, col, alpha=alpha)
        # tower with a lattice crown
        tx = x - 25
        cv.poly([(tx - 18, y - 175), (tx + 18, y - 175), (tx + 6, y - 300), (tx - 6, y - 300)], col, alpha=alpha)
        for k in range(5):
            yy = y - 185 - k * 22
            cv.line([(tx - 15 + k * 2.4, yy), (tx + 15 - k * 2.4, yy - 20)], (0.10, 0.13, 0.20), width=1.5,
                    alpha=alpha * 0.7)
        cv.line([(x - 150, y - 70), (x + 150, y - 70)], (0.35, 0.65, 0.55), width=1.2, alpha=alpha * 0.25)
        cv.line([(tx - 18, y - 175), (tx - 6, y - 300)], (0.35, 0.65, 0.55), width=1.2, alpha=alpha * 0.25)
        b.new_path()

    def _headline(self, cv, alphas=(1, 1, 1), offs=(0, 0, 0)):
        rows = [("12 KM", 330, 200, L.AMBER, 0.55), ("THE DEEPEST HOLE", 488, 68, L.WHITE, 0.0),
                ("EVER DUG", 566, 68, L.WHITE, 0.0)]
        for (txt, y, size, col, gl), a_, o in zip(rows, alphas, offs):
            htext(cv, txt, W / 2 + o, y, size, color=col, alpha=a_, glow=gl, shadow=0.8)

    # ================================================================== scenes
    def s_hook(self, cv, t):
        c = self.c
        go = smooth(prog(t, c["L01end"] + 0.05, c["L02"] - 0.05))          # surface -> top-down well
        if go < 1:
            push = ease_in_cubic(prog(t, c["L01end"] - 0.6, c["L02"] - 0.05))
            with cv.transform(s=1 + 1.6 * push, cx=CAP[0], cy=CAP[1]):
                self._surface(cv, t, alpha=1.0)
            pulse = window(t, c["n12"] - 0.05, c["n12"] + 0.25, 0.05, 0.6)
            ex = ease_in_cubic(prog(t, c["L01end"] - 0.1, c["L01end"] + 0.35))
            self._headline(cv, alphas=[1 - ex] * 3, offs=(0, -50 * ex, 50 * ex))
            if pulse > 0:
                htext(cv, "12 KM", W / 2, 330, 200, color=L.AMBER, alpha=0.0, glow_alpha=0.7 * pulse * (1 - ex))
        if go > 0:
            with cv.group(go):
                self._well(cv, t)

    def _well(self, cv, t):
        """Top-down: looking straight down the borehole, then a dinner plate covers it."""
        c = self.c
        cx, cy, r = 540.0, 900.0, 230.0
        b = cv.b
        pat = cairo.RadialGradient(cx, cy, r, cx, cy, 900)
        pat.add_color_stop_rgb(0, 0.30, 0.32, 0.36)
        pat.add_color_stop_rgb(0.35, 0.20, 0.22, 0.27)
        pat.add_color_stop_rgb(1, 0.05, 0.06, 0.10)
        b.set_source(pat)
        b.paint()
        # snow drifted around the casing
        rng = np.random.default_rng(8)
        for k in range(22):
            a_ = rng.uniform(0, 2 * math.pi)
            d = r * rng.uniform(1.45, 3.2)
            cv.radial(cx + math.cos(a_) * d, cy + math.sin(a_) * d, rng.uniform(60, 150), (0.85, 0.9, 1.0),
                      alpha=rng.uniform(0.15, 0.35))
        # steel casing
        cas = cairo.RadialGradient(cx - 40, cy - 60, r * 0.9, cx, cy, r * 1.22)
        cas.add_color_stop_rgb(0, 0.55, 0.50, 0.46)
        cas.add_color_stop_rgb(0.6, 0.36, 0.28, 0.22)
        cas.add_color_stop_rgb(1, 0.18, 0.13, 0.10)
        b.new_path()
        b.arc(cx, cy, r * 1.2, 0, 2 * math.pi)
        b.set_source(cas)
        b.fill()
        # the shaft: rings receding to a vanishing point, flowing outward (you are falling in)
        ph = (t - c["L01end"]) * 0.9
        vx, vy = cx + 26, cy - 18
        N = 34
        for k in range(N, -1, -1):
            u = (k - ph % 1.0)
            fr = 0.86 ** max(u, 0.0)
            rr = r * fr
            px, py = lerp(vx, cx, fr), lerp(vy, cy, fr)
            v = 0.12 * fr ** 0.8
            cv.circle(px, py, rr, (v * 0.9, v * 0.95, v * 1.15), alpha=1.0)
            cv.circle(px, py, rr, (0.55, 0.62, 0.75), alpha=0.22 * fr, fill=False, width=1.5)
        cv.radial(vx, vy, 30, (0.0, 0.0, 0.0), alpha=0.9)
        cv.circle(cx, cy, r, (0.75, 0.70, 0.62), alpha=0.65, fill=False, width=4)
        # dimension: the hole
        da = smooth(prog(t, c["narrower"] - 0.2, c["narrower"] + 0.2))
        yd = cy - r * 1.2 - 70
        uline(cv, [(cx - r, yd), (cx + r, yd)], L.CYAN, width=3, alpha=da)
        for sx in (-1, 1):
            uline(cv, [(cx + sx * r, yd - 18), (cx + sx * r, yd + 18)], L.CYAN, width=3, alpha=da)
            uline(cv, [(cx + sx * r, yd + 18), (cx + sx * r, cy - r * 0.9)], L.CYAN, width=1.5, alpha=da * 0.5,
                  dash=[6, 6])
        htext(cv, "23 cm", cx, yd - 52, 58, color=L.CYAN, alpha=da, glow=0.4, font=L.MONO_XB)
        htext(cv, "THE BOREHOLE", cx, yd - 112, 26, color=L.WHITE, alpha=da, font=L.MONO_XB, tracking=0.25)
        # the plate slides in and covers it completely
        pp = prog(t, c["dinner"] - 0.15, c["plate"] + 0.25)
        if pp > 0:
            k = ease_out_back(pp, 1.2)
            rp = r * 27 / 23
            px = lerp(W + rp + 40, cx, k)
            cv.radial(px + 18, cy + 26, rp * 1.25, (0.0, 0.0, 0.02), alpha=0.55)
            dinner_plate(cv, px, cy, rp, alpha=1.0)
            la = smooth(prog(t, c["plate"] + 0.05, c["plate"] + 0.4))
            b.save()
            b.set_dash([10, 9])
            b.new_path()
            b.arc(cx, cy, r, 0, 2 * math.pi)
            b.set_line_width(3)
            b.set_source_rgba(*L.CYAN, 0.85 * la)
            b.stroke()
            b.restore()
            htext(cv, "DINNER PLATE ≈ 27 cm", cx, cy + rp + 70, 38, color=L.WHITE, alpha=la, font=L.MONO_XB)

    # ------------------------------------------------------------------ the dive (rig, descent, heat, stop)
    def depth(self, t):
        return seg(t, self.depth_keys)

    def cam(self, t):
        return max(CAM0, self.depth(t) * PPK - (BIT_Y - H / 2))

    def s_rig(self, cv, t):
        self._dive(cv, t)

    s_descent = s_heat = s_stop = s_rig

    def _dive(self, cv, t):
        c = self.c
        D = self.depth(t)
        cam = self.cam(t)
        top = cam - H / 2
        ground_y = -top                       # screen y of the surface
        shift = ground_y - GROUND             # <= 0 once the camera dives
        vel = cam - self.cam(t - 1 / self.fps)
        if abs(vel) > 3:
            cv.motion = (0.0, vel * 0.55)
        # ---- sky + rig while visible
        if ground_y > -40:
            sa = 1.0
            self.stars.draw(cv, t, cam_y=-shift, alpha=sa, dust_alpha=0.0)
            self.aurora.draw(cv, t, alpha=0.5 * sa, offset_y=shift * 0.85)
            rig_h = 600.0
            lights = smooth(prog(t, c["sc_rig"][0] - 0.2, c["sc_rig"][0] + 0.6))
            drill_rig(cv, W / 2, ground_y - 2, h=rig_h, alpha=1.0, t=t, lights=lights)
            cv.line([(W / 2, ground_y - rig_h + 30), (W / 2, ground_y)], (0.62, 0.66, 0.74), width=3, alpha=0.9)
            cv.rays = (W / 2, ground_y - rig_h, 0.55 * lights)
        # ---- the rock column (and the borehole down to the bit)
        heat = smooth(prog(t, c["L07"], c["degrees"] + 0.3))
        sq = smooth(prog(t, c["hole8"] - 0.1, c["shut"] + 0.4)) * (1 - smooth(prog(t, c["L09"], c["L09"] + 1.0)))
        fade_out = smooth(prog(t, c["L09end"] + 0.1, c["L09end"] + 0.5))           # hand-off to the zoom-out
        bottom_glow = smooth(prog(D, 11.0, 12.2)) * (0.6 + 0.4 * (1 - smooth(prog(t, c["further"], c["further"]
                                                                                    + 0.8))))
        fg = smooth(prog(D, 0.3, 1.6)) * (1 - fade_out)
        self.rock.draw(cv, cam, t=t, bottom_km=D, squeeze=sq, glow_bottom=bottom_glow, fg_alpha=fg)
        if ground_y > -40:
            # snow lying on the surface of the cut-away
            pts = [(x, ground_y - 14 - 5 * math.sin(x * 0.013) - 3 * math.sin(x * 0.041 + 1)) for x in
                   range(-10, W + 20, 20)]
            cv.poly(pts + [(W + 10, ground_y + 3), (-10, ground_y + 3)], (0.86, 0.90, 0.98), alpha=0.97)
            cv.line(pts, (0.9, 0.95, 1.0), width=2, alpha=0.6, glow=0.4)
            with cv.clip(lambda ctx: ctx.rectangle(0, 0, W, ground_y - 10)):
                self.snow.draw(cv, t, alpha=0.8 * smooth(prog(ground_y, 200, 700)), cam_dy=-shift, glow=0.2)
        # planned path toward 15 km (dashed), shown while they are "aiming"
        pa = window(t, c["aiming"], c["dive"] + 0.8, 0.3, 0.5)
        if pa > 0:
            y0 = D * PPK - top
            cv.line([(W / 2, y0 + 40), (W / 2, H + 20)], L.AMBER, width=3, alpha=0.7 * pa, dash=[14, 12], glow=0.5)
        # fossils glowing in the rock around 6 km
        fa = smooth(prog(t, c["fossils"] - 0.1, c["fossils"] + 0.5)) * (1 - smooth(prog(t, c["L05"] + 0.3,
                                                                                     c["seven"] + 0.6)))
        if fa > 0:
            for (fx, fy, fr, kind, rot, ph) in self.fossils:
                sy = fy - top
                if -30 < sy < H + 30:
                    tw = 0.6 + 0.4 * math.sin(t * 2.1 + ph)
                    microfossil(cv, fx, sy, fr, kind=kind, alpha=fa * tw, rot=rot + t * 0.2, color=L.MINT)
        # predicted basalt layer that isn't there
        self._basalt(cv, t, top)
        # fractures light up, then water glints along them
        self._fractures(cv, t, top)
        # the drill bit
        if D > 0.0:
            spin = t * (1.0 - smooth(prog(t, c["further"] - 0.3, c["further"] + 0.9)))
            hb = smooth(prog(D, 10.0, 12.0))
            jolt = window(t, self.t_bottom - 0.02, self.t_bottom + 0.05, 0.02, 0.45)
            jy = 6 * jolt * math.sin(t * 70)
            drill_bit(cv, W / 2, D * PPK - top + 6 + jy, s=0.42, alpha=1.0, heat=hb, t=spin * 6)
            if hb > 0.1:
                for k in range(10):
                    f = (t * (1.6 + 0.1 * k) + k * 0.37) % 1.0
                    cv.circle(W / 2 + (k - 4.5) * 7 + 22 * math.sin(k * 3.1 + t * 4) * f, D * PPK - top + 4 - 70 * f,
                              2.2, (1.0, 0.6, 0.25), alpha=hb * (1 - f) * (1 - fade_out) * 0.9, glow=1.0)
        # particles: dust in the dark, embers in the heat
        da = smooth(prog(D, 0.4, 1.4)) * (1 - fade_out)
        self.dust.draw(cv, t, alpha=0.9 * da * (1 - heat * 0.6), cam_dy=cam * 0.35, glow=0.2)
        self.embers.draw(cv, t, alpha=heat * (1 - fade_out), cam_dy=cam * 0.35, glow=0.8)
        # camera finishing
        dof = smooth(prog(D, 0.5, 1.8)) * (1 - fade_out)
        if dof > 0.02:
            cv.dof = (900.0, 520.0, 8.0 * dof)
        hz = heat * (3.0 + 4.0 * sq) * (1 - fade_out)
        if hz > 0.05:
            cv.heat = (hz, 250.0, 1700.0)
        if t < self.t_bottom + 0.6 and t > self.t_bottom - 0.05:
            j = window(t, self.t_bottom - 0.02, self.t_bottom + 0.05, 0.02, 0.5)
            cv.aberration = 3.0 * j
        self._dive_text(cv, t, D, heat)
        self._hud(cv, t, D)

    def _basalt(self, cv, t, top):
        c = self.c
        ga = smooth(prog(t, c["predicted"] - 0.25, c["predicted"] + 0.05))
        brk = prog(t, c["wasnt"] - 0.05, c["there"] + 0.45)
        if ga <= 0 or brk >= 1:
            return
        y0, y1 = 6.80 * PPK - top, 7.32 * PPK - top
        if y1 < -10 or y0 > H + 10:
            return
        n = 9
        rng = np.random.default_rng(11)
        for i in range(n):
            ya, yb = lerp(y0, y1, i / n), lerp(y0, y1, (i + 1) / n)
            off = (rng.uniform(-1, 1) * 160 + 60 * math.sin(t * 40 + i)) * ease_in_cubic(brk)
            fa = ga * (1 - smooth(prog(brk, 0.15 + 0.06 * i, 0.55 + 0.05 * i)))
            if fa <= 0.003:
                continue
            b = cv.b
            b.save()
            b.rectangle(0, ya, W, yb - ya)
            b.clip()
            cv.rect(off, ya, W, yb - ya, (0.22, 0.34, 0.70), alpha=0.42 * fa)
            for k in range(-20, 40):
                x = off + k * 34 - (yb - ya)
                cv.line([(x, yb), (x + (yb - ya), ya)], (0.55, 0.75, 1.0), width=1.5, alpha=0.45 * fa)
            b.restore()
        la = ga * (1 - smooth(prog(brk, 0.0, 0.3)))
        for yy in (y0, y1):
            cv.line([(0, yy), (W, yy)], (0.55, 0.80, 1.0), width=2.5, alpha=0.9 * la, dash=[16, 10], glow=0.4)
        htext(cv, "PREDICTED:", 785, y0 + 50, 30, color=(0.75, 0.88, 1.0), alpha=la, font=L.MONO_XB, tracking=0.1)
        htext(cv, "BASALT", 785, y0 + 104, 64, color=L.WHITE, alpha=la, glow=0.3)
        # shards drifting away
        if 0 < brk < 1:
            for k in range(40):
                f = clamp(brk * 1.3 - k / 80)
                x = (k * 97) % W
                y = lerp(y0, y1, (k * 37 % 100) / 100) - 120 * f
                cv.rect(x + 40 * math.sin(k), y, 8, 8, (0.55, 0.75, 1.0), alpha=0.6 * (1 - f) * (f > 0))

    def _fractures(self, cv, t, top):
        c = self.c
        sweep = prog(t, c["cracked"] - 0.15, c["cracked"] + 0.9)
        ca = smooth(prog(t, c["cracked"] - 0.15, c["cracked"] + 0.2)) * (1 - smooth(prog(t, c["L06end"] + 0.1,
                                                                                           c["L07"] + 0.3)))
        wa = smooth(prog(t, c["soaked"] - 0.1, c["water"] + 0.4)) * (1 - smooth(prog(t, c["L07"], c["L07"] + 0.5)))
        if ca <= 0 and wa <= 0:
            return
        ys = lerp(-100, H + 100, ease_in_out(sweep))
        if ca > 0:
            for arr in self.rock.cracks:
                sy = arr[:, 1] - top
                if sy.max() < -20 or sy.min() > H + 20:
                    continue
                vis = clamp((ys - sy.mean()) / 120 + 0.5)
                if vis <= 0:
                    continue
                pts = [(float(x), float(y - top)) for x, y in arr]
                cv.line(pts, (0.55, 0.85, 1.0), width=1.6, alpha=0.55 * ca * vis, glow=0.8)
            if 0 < sweep < 1:
                cv.line([(0, ys), (W, ys)], L.CYAN, width=2, alpha=0.6 * ca, glow=1.0)
        if wa > 0:
            g = self.rock.glint_pts
            sy = g[:, 1] - top
            m = (sy > -10) & (sy < H + 10)
            for x, y, ph, sp in g[m]:
                tw = 0.5 + 0.5 * math.sin(t * sp + ph)
                if tw < 0.25:
                    continue
                cv.circle(float(x), float(y - top), 1.6 + 1.4 * tw, (0.7, 0.92, 1.0), alpha=wa * tw, glow=0.9)

    def _dive_text(self, cv, t, D, heat):
        c = self.c
        scrim = max(window(t, c["fossils"] - 0.1, c["L04end"] + 0.15, 0.25, 0.35),
                    window(t, c["cracked"] - 0.05, c["L06end"] + 0.15, 0.25, 0.35),
                    window(t, c["n180"] - 0.12, c["L08end"] + 0.2, 0.15, 0.35),
                    window(t, c["n12262"] - 0.15, c["L09end"] + 0.3, 0.15, 0.35))
        if scrim > 0:
            b = cv.b
            g = cairo.LinearGradient(0, 330, 0, 760)
            g.add_color_stop_rgba(0, 0.0, 0.0, 0.02, 0.0)
            g.add_color_stop_rgba(0.3, 0.0, 0.0, 0.02, 0.55 * scrim)
            g.add_color_stop_rgba(0.7, 0.0, 0.0, 0.02, 0.55 * scrim)
            g.add_color_stop_rgba(1, 0.0, 0.0, 0.02, 0.0)
            b.new_path()
            b.rectangle(0, 330, W, 430)
            b.set_source(g)
            b.fill()
        # 1970
        ya = window(t, c["y1970"] - 0.15, c["dive"] - 0.2, 0.25, 0.35)
        if ya > 0:
            pop = 1 - ease_out_back(prog(t, c["y1970"] - 0.15, c["y1970"] + 0.3))
            htext(cv, "1970", W / 2, 300, 170 * (1 + 0.15 * pop), color=L.AMBER, alpha=ya, glow=0.5)
            sa = smooth(prog(t, c["soviet"] - 0.1, c["soviet"] + 0.3)) * ya
            htext(cv, "KOLA PENINSULA · USSR", W / 2, 414, 32, color=L.WHITE, alpha=ya, font=L.MONO_XB,
                  tracking=0.14, shadow=1.0)
            htext(cv, "SOVIET SUPERDEEP DRILLING PROJECT", W / 2, 460, 24, color=(0.80, 0.86, 0.98), alpha=sa,
                  font=L.MONO_XB, tracking=0.06, shadow=1.0)
        # fossils
        fa = window(t, c["fossils"] - 0.1, c["L04end"] + 0.15, 0.25, 0.35)
        if fa > 0:
            htext(cv, "PLANKTON FOSSILS", W / 2, 470, 66, color=L.WHITE, alpha=fa, glow=0.15)
            ma = smooth(prog(t, c["microscopic"] - 0.1, c["microscopic"] + 0.3)) * fa
            htext(cv, "MICROFOSSILS · 6 KM DOWN", W / 2, 546, 30, color=L.MINT, alpha=ma, font=L.MONO_XB,
                  tracking=0.08, glow=0.3)
            self._lens(cv, t, fa)
        # basalt: not there
        na = window(t, c["there"] - 0.05, c["L05end"] + 0.25, 0.1, 0.3)
        if na > 0:
            pop = 1 - ease_out_back(prog(t, c["there"] - 0.05, c["there"] + 0.35))
            stamp(cv, "NOT THERE", W / 2, 500, size=86, angle=-0.09, color=L.MAGENTA, alpha=na, pop=pop,
                  sub="NO BASALT AT 7 KM")
        # fractured granite + water
        ga = window(t, c["cracked"] - 0.05, c["L06end"] + 0.15, 0.25, 0.35)
        if ga > 0:
            htext(cv, "FRACTURED GRANITE", W / 2, 470, 64, color=L.WHITE, alpha=ga, glow=0.15)
            wa = smooth(prog(t, c["water"] - 0.1, c["water"] + 0.3)) * ga
            htext(cv, "SOAKED WITH WATER", W / 2, 548, 36, color=L.CYAN, alpha=wa, font=L.MONO_XB, tracking=0.1,
                  glow=0.5)
        # 180 °C
        ha = window(t, c["n180"] - 0.12, c["L07end"] + 0.2, 0.15, 0.35)
        if ha > 0:
            k = ease_out_cubic(prog(t, c["n180"] - 0.12, c["degrees"] + 0.15))
            temp = int(round(lerp(100, 180, k)))
            col = mix(L.WHITE, (1.0, 0.86, 0.75), k)
            htext(cv, f"{temp} °C", W / 2, 470, 170, color=col, alpha=ha, glow_alpha=0.9 * ha, shadow=1.0)
            htext(cv, f"{temp} °C", W / 2, 470, 170, color=(1.0, 0.35, 0.15), alpha=0.0, glow_alpha=0.8 * ha * k)
            ea = smooth(prog(t, c["almost"] - 0.15, c["almost"] + 0.25)) * ha
            wexp = htext(cv, "EXPECTED: ~100 °C", W / 2, 615, 42, color=L.WHITE, alpha=ea, font=L.MONO_XB, shadow=1.0)
            st = ease_out_cubic(prog(t, c["twice"] - 0.05, c["twice"] + 0.35))
            if st > 0:
                x0 = W / 2 - wexp / 2 - 14
                uline(cv, [(x0, 615), (x0 + (wexp + 28) * st, 615)], L.MAGENTA, width=7, alpha=ea)
                htext(cv, "≈ 2×", W / 2, 712, 72, color=L.WHITE, alpha=ea * smooth(prog(st, 0.6, 1.0)), glow=0.5,
                      shadow=1.0)
        # plastic rock
        pa = window(t, c["soft"] - 0.2, c["L08end"] + 0.2, 0.25, 0.35)
        if pa > 0:
            wob = 6 * smooth(prog(t, c["hole8"], c["shut"])) * math.sin(t * 9)
            htext(cv, "ROCK BEHAVED", W / 2 + wob, 470, 64, color=L.WHITE, alpha=pa)
            htext(cv, "LIKE PLASTIC", W / 2 - wob, 548, 64, color=L.AMBER, alpha=pa, glow=0.35)
        # 12,262 m
        ba = smooth(prog(t, c["n12262"] - 0.15, c["n12262"] + 0.2)) * (1 - smooth(prog(t, c["L09end"] + 0.05,
                                                                                        c["L09end"] + 0.45)))
        if ba > 0:
            k = ease_out_cubic(prog(t, c["L09"], self.t_bottom))
            val = int(round(lerp(11900, 12262, k)))
            pop = 1 - ease_out_back(prog(t, self.t_bottom - 0.02, self.t_bottom + 0.35))
            htext(cv, f"{val:,} m", W / 2, 470, 150 * (1 + 0.12 * pop), color=L.AMBER, alpha=ba, glow=0.55)
            sa = smooth(prog(t, c["meters"] - 0.1, c["meters"] + 0.3)) * ba
            htext(cv, "DEEPEST HUMAN-MADE POINT ON EARTH", W / 2, 586, 30, color=L.WHITE, alpha=sa,
                  font=L.MONO_XB, tracking=0.02, shadow=1.0)
            htext(cv, "REACHED IN 1989", W / 2, 636, 28, color=(0.80, 0.86, 0.98), alpha=sa, font=L.MONO_XB,
                  tracking=0.12, shadow=1.0)

    def _lens(self, cv, t, a):
        """Magnifier on the fossils."""
        c = self.c
        k = ease_out_back(prog(t, c["fossils"] + 0.05, c["fossils"] + 0.5))
        if k <= 0:
            return
        lx, ly, r = 770.0, 790.0, 165.0 * k
        top = self.cam(t) - H / 2
        src = (630.0, 5.86 * PPK - top)
        cv.line([src, (lx - r * 0.72, ly + r * 0.72)], L.MINT, width=2, alpha=0.8 * a, glow=0.5)
        cv.circle(src[0], src[1], 16, L.MINT, alpha=0.9 * a, fill=False, width=2, glow=0.6)
        b = cv.b
        b.save()
        b.new_path()
        b.arc(lx, ly, r, 0, 2 * math.pi)
        b.clip()
        pat = cairo.RadialGradient(lx - r * 0.3, ly - r * 0.3, 0, lx, ly, r)
        pat.add_color_stop_rgba(0, 0.20, 0.20, 0.26, a)
        pat.add_color_stop_rgba(1, 0.06, 0.06, 0.09, a)
        b.set_source(pat)
        b.paint()
        rng = np.random.default_rng(3)
        for _ in range(60):
            cv.circle(lx + rng.uniform(-r, r), ly + rng.uniform(-r, r), rng.uniform(1, 3), (0.5, 0.5, 0.6),
                      alpha=0.4 * a)
        microfossil(cv, lx - 58, ly - 30, 44 * k, kind=0, alpha=a, rot=t * 0.25, color=L.MINT)
        microfossil(cv, lx + 50, ly + 52, 36 * k, kind=1, alpha=a, rot=0.6 + t * 0.12, color=L.MINT)
        microfossil(cv, lx + 62, ly - 72, 22 * k, kind=0, alpha=a * 0.9, rot=-t * 0.3, color=L.MINT)
        b.restore()
        cv.circle(lx, ly, r, L.WHITE, alpha=0.9 * a, fill=False, width=4, glow=0.6)
        cv.circle(lx, ly, r + 7, L.MINT, alpha=0.5 * a, fill=False, width=2)

    def _hud(self, cv, t, D):
        """Depth ruler (0-15 km) on the left and live readouts."""
        c = self.c
        out = 1 - smooth(prog(t, c["L09end"] + 0.1, c["L09end"] + 0.5))
        ra = smooth(prog(t, c["aiming"] - 0.3, c["aiming"] + 0.3)) * out
        if ra <= 0:
            return
        x, y0, y1 = RULER
        kmy = lambda km: y0 + (y1 - y0) * km / TARGET_KM  # noqa: E731
        draw_in = ease_out_cubic(prog(t, c["aiming"] - 0.3, c["aiming"] + 0.5))
        ye = lerp(y0, y1, draw_in)
        uline(cv, [(x, y0), (x, ye)], (0.80, 0.86, 0.98), width=3, alpha=0.85 * ra)
        for km in range(0, 16):
            yy = kmy(km)
            if yy > ye:
                break
            big = km % 3 == 0
            uline(cv, [(x - (16 if big else 8), yy), (x, yy)], (0.80, 0.86, 0.98), width=3 if big else 2,
                  alpha=0.85 * ra)
            if big and km < 15:
                htext(cv, f"{km}", x + 16, yy, 24, color=(0.80, 0.86, 0.98), alpha=ra, font=L.MONO_XB,
                      anchor="left", shadow=0.8)
        # drilled so far
        yd = kmy(min(D, TARGET_KM))
        uline(cv, [(x, y0), (x, yd)], L.AMBER, width=5, alpha=ra)
        upoly(cv, [(x + 6, yd), (x + 22, yd - 9), (x + 22, yd + 9)], L.AMBER, alpha=ra)
        # target
        hl = window(t, c["n15"] - 0.1, c["n15"] + 0.6, 0.1, 0.5)
        tcol = mix(L.AMBER, L.WHITE, hl)
        yt = kmy(TARGET_KM)
        uline(cv, [(x - 16, yt), (x + 16, yt)], tcol, width=4, alpha=ra * draw_in)
        htext(cv, "TARGET 15 KM", x + 26, yt, 26 + 4 * hl, color=tcol, alpha=ra * draw_in, font=L.MONO_XB,
              anchor="left", glow=0.3 + 0.4 * hl, shadow=0.8)
        # never reached
        nr = smooth(prog(t, c["further"] - 0.1, c["further"] + 0.4))
        if nr > 0:
            uline(cv, [(x, kmy(BOTTOM_KM)), (x, yt)], L.MAGENTA, width=5, alpha=ra * nr, dash=[8, 7])
            htext(cv, "NEVER REACHED", x + 26, yt + 34, 20, color=L.MAGENTA, alpha=ra * nr, font=L.MONO_XB,
                  anchor="left", shadow=0.6)
        # readouts
        da = smooth(prog(t, c["dive"] - 0.3, c["dive"] + 0.1)) * out
        da *= 1 - window(t, c["n12262"] - 0.15, c["L09end"] + 2.0, 0.2, 0.01)
        if da > 0:
            htext(cv, "DEPTH", x - 12, 300, 24, color=(0.80, 0.86, 0.98), alpha=da, font=L.MONO_XB, anchor="left",
                  tracking=0.3)
            htext(cv, f"{int(round(D * 1000)):,} m", x - 12, 348, 52, color=L.WHITE, alpha=da, font=L.MONO_XB,
                  anchor="left")
        ta = smooth(prog(t, c["L07end"] + 0.05, c["L08"] + 0.1)) * out
        if ta > 0:
            htext(cv, "TEMPERATURE", W - 92, 300, 24, color=(0.80, 0.86, 0.98), alpha=ta, font=L.MONO_XB,
                  anchor="right", tracking=0.3)
            htext(cv, "180 °C", W - 92, 348, 52, color=(1.0, 0.45, 0.25), alpha=ta, font=L.MONO_XB, anchor="right",
                  glow=0.4)

    # ------------------------------------------------------------------ scale: ocean, then the whole Earth
    def _scale_view(self, t):
        """(pz, pe, px-per-km, anchor x, anchor y): the hole's mouth is the anchor of every zoom."""
        c = self.c
        s0 = c["sc_scale"][0]
        pz = ease_in_out(prog(t, s0, s0 + 1.05))                     # rock column -> bars on a chart
        pe = ease_in_out(prog(t, c["L11"] - 0.05, c["pct"] + 1.25))  # chart -> the whole Earth
        s_cmp = CMP_PPK / PPK
        if pe <= 0:
            ppk = PPK * s_cmp ** pz
            bx, by = lerp(W / 2, KX, pz), lerp(BIT_Y, CMP_TOP + BOTTOM_KM * CMP_PPK, pz)
            return pz, pe, ppk, bx, by - BOTTOM_KM * ppk
        ppk = CMP_PPK * (EARTH_R / 6371.0 / CMP_PPK) ** pe
        return pz, pe, ppk, lerp(KX, EARTH_C[0], pe), lerp(CMP_TOP, EARTH_C[1] - EARTH_R, pe)

    def s_scale(self, cv, t):
        s0, s1 = self.c["sc_scale"]
        z = ease_in_cubic(prog(t, s1 - 0.35, s1 + 0.5))
        if z <= 0:
            self._scale_body(cv, t)
            return
        mx, my = EARTH_C[0], EARTH_C[1] - EARTH_R
        sc = 1 + 11 * z
        with cv.transform(s=sc, cx=mx, cy=my), ui_scope(cv, 1.0, sc, 0.0, mx, my):
            self._scale_body(cv, t)

    def _scale_body(self, cv, t):
        c = self.c
        s0, s1 = c["sc_scale"]
        pz, pe, ppk, ax, ay = self._scale_view(t)
        clear = 1 - smooth(prog(t, s1 - 0.55, s1 - 0.2))
        prev_ui = getattr(cv, "ui_alpha", 1.0)
        cv.ui_alpha = prev_ui * clear
        R = 6371.0 * ppk
        ea = smooth(prog(-math.log(R), -math.log(20000), -math.log(5000)))      # the globe fades in as R shrinks
        rt = smooth(prog(ppk, 14.0, 30.0))                 # textured rock while the column is wide enough
        if ea > 0:
            cross_section(cv, ax, ay + R, R, t, alpha=ea, glow=0.55 * ea)
        ca = smooth(prog(t, s0 + 0.5, s0 + 1.0))
        # the surface (an arc of the real Earth radius at every zoom level)
        half = min(math.pi, 1.6 * W / R + 0.02)
        cv.arc(ax, ay + R, R, -math.pi / 2 - half, -math.pi / 2 + half, (0.75, 0.85, 1.0), alpha=0.8 * ca,
               width=2.5, glow=0.3)
        # ocean column
        fill = ease_in_out(prog(t, c["deepest10"] - 0.1, c["ocean"] + 0.5))
        ox = ax + (OX - KX) * ppk / CMP_PPK
        cw = 139.0 * ppk / CMP_PPK
        if fill > 0 and cw > 0.4:
            hh = OCEAN_KM * ppk * fill
            g = cairo.LinearGradient(0, ay, 0, ay + OCEAN_KM * ppk)
            g.add_color_stop_rgba(0, 0.25, 0.70, 0.95, 0.95 * (1 - ea))
            g.add_color_stop_rgba(1, 0.02, 0.10, 0.35, 0.95 * (1 - ea))
            cv.b.new_path()
            cv.b.rectangle(ox - cw / 2, ay, cw, hh)
            cv.b.set_source(g)
            cv.b.fill()
            if ppk > 20:
                for k in range(6):
                    yy = ay + hh * (k + 0.5) / 6 + 6 * math.sin(t * 2 + k)
                    cv.line([(ox - cw / 2 + 8, yy), (ox + cw / 2 - 8, yy + 4 * math.sin(t * 3 + k))],
                            (0.6, 0.9, 1.0), width=1.2, alpha=0.25 * fill * (1 - ea))
        # the Kola column: real rock texture, then a plain bar once it is tiny
        if rt > 0:
            self._rock_at(cv, t, ppk, ax, ay, pz, alpha=rt)
        kw = 139.0 * ppk / CMP_PPK
        if rt < 1 and kw > 0.4:
            g = cairo.LinearGradient(0, ay, 0, ay + BOTTOM_KM * ppk)
            a_ = (1 - rt) * (1 - ea)
            g.add_color_stop_rgba(0, 0.40, 0.38, 0.44, a_)
            g.add_color_stop_rgba(0.75, 0.45, 0.28, 0.22, a_)
            g.add_color_stop_rgba(1, 0.95, 0.45, 0.15, a_)
            cv.b.new_path()
            cv.b.rectangle(ax - kw / 2, ay, kw, BOTTOM_KM * ppk)
            cv.b.set_source(g)
            cv.b.fill()
            cv.line([(ax, ay), (ax, ay + BOTTOM_KM * ppk)], (0.05, 0.05, 0.07), width=max(1.2, 4 * ppk / CMP_PPK),
                    alpha=a_)
        # labels at chart scale
        la = ca * (1 - smooth(prog(t, c["L11"] - 0.1, c["L11"] + 0.25)))
        if la > 0:
            axis_x = 230.0
            for km in range(0, 13, 2):
                yy = ay + km * ppk
                uline(cv, [(axis_x - 10, yy), (axis_x, yy)], (0.75, 0.82, 0.95), width=2, alpha=0.6 * la)
                htext(cv, f"{km}", axis_x - 18, yy, 20, color=L.DIM, alpha=la, font=L.MONO_XB, anchor="right",
                      shadow=0.4)
            uline(cv, [(axis_x, ay), (axis_x, ay + 12 * ppk)], (0.75, 0.82, 0.95), width=2, alpha=0.6 * la)
            htext(cv, "KM", axis_x - 18, ay - 34, 18, color=L.DIM, alpha=la, font=L.MONO_XB, anchor="right")
            htext(cv, "TO SCALE", W / 2, 292, 22, color=L.DIM, alpha=la, font=L.MONO_XB, tracking=0.4)
            oa = smooth(prog(t, c["ocean"] + 0.2, c["ocean"] + 0.6)) * la
            yb = ay + OCEAN_KM * ppk
            htext(cv, "≈ 10,935 m", ox, yb + 38, 32, color=L.CYAN, alpha=oa, font=L.MONO_XB, glow=0.3)
            htext(cv, "DEEPEST OCEAN", ox, yb + 76, 20, color=L.DIM, alpha=oa, font=L.MONO_XB, tracking=0.12)
            uline(cv, [(ox + 70, yb), (ax - 70, yb)], L.CYAN, width=2, alpha=0.7 * oa, dash=[8, 8])
            yk = ay + BOTTOM_KM * ppk
            htext(cv, "12,262 m", ax + 84, yk - 14, 32, color=L.AMBER, alpha=la, font=L.MONO_XB, anchor="left",
                  glow=0.3)
            htext(cv, "KOLA BOREHOLE", ax + 84, yk + 24, 20, color=L.DIM, alpha=la, font=L.MONO_XB, anchor="left",
                  tracking=0.12)
        # the globe: 0.2 %
        pa = smooth(prog(t, c["pct"] - 0.1, c["pct"] + 0.3))
        if pa > 0:
            pop = 1 - ease_out_back(prog(t, c["pct"] - 0.1, c["pct"] + 0.35))
            htext(cv, "0.2%", W / 2, 290, 170 * (1 + 0.12 * pop), color=L.AMBER, alpha=pa, glow=0.55)
            htext(cv, "12 km  ÷  6,371 km", W / 2, 400, 28, color=L.WHITE, alpha=pa, font=L.MONO_XB, tracking=0.06)
        ra = smooth(prog(t, c["earths"] - 0.2, c["center"] + 0.2)) * ea
        if ra > 0:
            ex, ey = ax, ay + R
            k = ease_out_cubic(prog(t, c["earths"] - 0.2, c["center"] + 0.3))
            cv.line([(ax, ay), (ax, lerp(ay, ey, k))], L.WHITE, width=2.5, alpha=0.85 * ra * clear, dash=[10, 9],
                    glow=0.4)
            cv.circle(ex, ey, 7, L.WHITE, alpha=ra * k * clear, glow=1.0)
            htext(cv, "6,371 km TO THE CENTER", ax + 22, lerp(ay, ey, 0.5), 24, color=L.WHITE, alpha=ra,
                  font=L.MONO_XB, anchor="left", tracking=0.04)
        ma = ea * smooth(prog(t, c["pct"] + 0.9, c["pct"] + 1.4))
        if ma > 0:
            ph = (t * 1.2) % 1.0
            cv.circle(ax, ay, 16 + 20 * ph, L.CYAN, alpha=ma * (1 - ph), fill=False, width=2.5, glow=0.6)
            cv.circle(ax, ay, 4, L.CYAN, alpha=ma, glow=1.0)
            htext(cv, "THE HOLE", ax - 34, ay - 28, 20, color=L.CYAN, alpha=ma, font=L.MONO_XB, anchor="right",
                  tracking=0.12)
        cv.ui_alpha = prev_ui

    def _rock_at(self, cv, t, ppk, ax, ay, pz, alpha=1.0):
        """Draw the descent shot's rock column so its mouth sits at (ax, ay) at ppk px/km."""
        cam_end = BOTTOM_KM * PPK - (BIT_Y - H / 2)
        top = cam_end - H / 2
        s = ppk / PPK
        b = cv.b
        with cv.transform(tx=ax - W / 2, ty=ay + top, s=s, cx=W / 2, cy=-top):
            b.push_group()
            self.rock.draw(cv, cam_end, t=t, bottom_km=BOTTOM_KM, glow_bottom=0.6 * (1 - pz), fg_alpha=0.0,
                           span=(0.0, BOTTOM_KM * PPK))
            drill_bit(cv, W / 2, BOTTOM_KM * PPK - top + 6, s=0.42, alpha=1.0, heat=1.0 - pz, t=0.0)
            b.pop_group_to_source()
            yb = BOTTOM_KM * PPK - top
            m = cairo.LinearGradient(0, yb - 10, 0, yb + 420)
            m.add_color_stop_rgba(0, 0, 0, 0, alpha)
            m.add_color_stop_rgba(1, 0, 0, 0, alpha * (1 - smooth(pz)))
            b.mask(m)

    # ------------------------------------------------------------------ cap + outro (back on the surface)
    def s_cap(self, cv, t):
        s0, s1 = self.c["sc_cap"]
        iris = ease_in_out(prog(t, s0 - 0.02, s0 + 0.5))
        if iris >= 1:
            self._cap_body(cv, t)
            return
        self.s_scale(cv, t)                       # the globe keeps rushing toward the hole...
        mx, my = EARTH_C[0], EARTH_C[1] - EARTH_R
        r = 1750 * iris
        if r > 0.5:
            def disc(ctx):
                ctx.new_path()
                ctx.arc(mx, my, r, 0, 2 * math.pi)

            with cv.clip(disc):                   # ...and the surface opens up out of it
                cv.g.save()
                cv.g.set_operator(cairo.OPERATOR_CLEAR)
                cv.g.paint()
                cv.g.restore()
                background(cv, t, haze=(0.5, 0.36), haze_color=(0.08, 0.22, 0.40), haze_amt=0.8)
                self._cap_body(cv, t)
            cv.circle(mx, my, r, L.CYAN, alpha=0.9 * (1 - iris), fill=False, width=5, glow=1.0)

    def _cap_body(self, cv, t):
        c = self.c
        s0, s1 = c["sc_cap"]
        push = ease_in_out(prog(t, s0, s1 + 0.4))
        self._surface(cv, t, cap_s=1.0 + 0.35 * push, cap_dy=-40 * push)
        ia = smooth(prog(t, c["sealed"] - 0.15, c["sealed"] + 0.25))
        ui_k = getattr(cv, "ui_alpha", 1.0)
        if ia > 0:
            x0, y0, w0, h0 = 110.0, 262.0, 860.0, 196.0
            u = cv.u
            u.save()
            u.new_path()
            rounded_rect(u, x0, y0, w0, h0, 18)
            u.set_source_rgba(0.03, 0.05, 0.10, 0.82 * ia * ui_k)
            u.fill_preserve()
            u.set_source_rgba(*L.AMBER, 0.6 * ia * ui_k)
            u.set_line_width(2)
            u.stroke()
            u.restore()
            htext(cv, "TODAY", x0 + 30, y0 + 40, 22, color=L.DIM, alpha=ia, font=L.MONO_XB, anchor="left",
                  tracking=0.3, shadow=0)
            htext(cv, "KOLA SUPERDEEP BOREHOLE", x0 + 30, y0 + 96, 46, color=L.WHITE, alpha=ia, anchor="left",
                  shadow=0)
            htext(cv, "SG-3 · KOLA PENINSULA, RUSSIA · SEALED", x0 + 30, y0 + 152, 22, color=L.AMBER, alpha=ia,
                  font=L.MONO_XB, anchor="left", tracking=0.06, shadow=0)
        ra = smooth(prog(t, c["rusty"] - 0.1, c["capw"] + 0.2))
        if ra > 0:
            cs = 1.0 + 0.35 * push
            cx, cy = CAP[0], CAP[1] - 40 * push
            b = cv.b
            b.save()
            b.translate(cx, cy)
            b.scale(1, 0.42)
            b.arc(0, 0, 230 * cs * 1.18, -math.pi * 0.95, -math.pi * 0.95 + 2 * math.pi * ease_out_cubic(ra))
            b.restore()
            b.set_dash([12, 10])
            b.set_line_width(3)
            b.set_source_rgba(*L.AMBER, 0.85 * ra)
            b.stroke()
            b.set_dash([])

    def s_outro(self, cv, t):
        c = self.c
        s0, s1 = c["sc_outro"]
        up = ease_in_out(prog(t, c["L13"] - 0.05, c["interstellar"] - 0.1))
        down = ease_in_out(prog(t, c["L14"] - 0.05, c["deeper14"] + 0.3))
        tilt = SKY_TILT * up * (1 - down)
        settle = ease_in_out(prog(t, s0, c["L13"] + 0.4))
        cap_s = lerp(1.35, 1.0, settle)
        cap_dy = lerp(-40, 0, settle)
        prev_tilt = SKY_TILT * ease_in_out(prog(t - 1 / self.fps, c["L13"] - 0.05, c["interstellar"] - 0.1)) * (
            1 - ease_in_out(prog(t - 1 / self.fps, c["L14"] - 0.05, c["deeper14"] + 0.3)))
        vel = tilt - prev_tilt
        if abs(vel) > 3:
            cv.motion = (0.0, vel * 0.5)
        self._surface(cv, t, tilt=tilt, cap_s=cap_s, cap_dy=cap_dy)
        # Voyager 1, far above the aurora
        va = smooth(prog(tilt, 500, 1100))
        if va > 0:
            vx = lerp(760, 560, prog(t, c["L13"], c["L14"] + 1.0))
            vy = -640 + tilt
            pts = []
            for k in range(40):
                u_ = k / 39
                pts.append((lerp(-80, vx - 40, u_), lerp(vy + 900, vy + 30, u_) - 120 * math.sin(u_ * math.pi)))
            for k, (px, py) in enumerate(pts[:-1]):
                if k % 2 == 0:
                    cv.circle(px, py, 2.2, L.CYAN, alpha=0.45 * va * k / 40)
            voyager(cv, vx, vy, s=0.95, alpha=va, rot=-0.32 + 0.05 * math.sin(t * 0.5))
            la = smooth(prog(t, c["interstellar"] - 0.1, c["interstellar"] + 0.3)) * va
            htext(cv, "VOYAGER 1", vx, vy - 170, 54, color=L.WHITE, alpha=la, glow=0.2)
            htext(cv, "IN INTERSTELLAR SPACE SINCE 2012", vx, vy - 108, 27, color=L.CYAN, alpha=la, font=L.MONO_XB,
                  tracking=0.04, glow=0.3)
        # the headline returns: the last frame is the first frame
        back = prog(t, c["own"] - 0.25, c["own"] + 1.25)
        if back > 0:
            ks = [ease_out_expo(prog(back, 0.14 * k, 0.55 + 0.14 * k)) for k in range(3)]
            al = [smooth(prog(back, 0.14 * k, 0.35 + 0.14 * k)) for k in range(3)]
            self._headline(cv, alphas=al, offs=[-140 * (1 - k) for k in ks])

    # ================================================================== record-along guide
    def _teleprompter(self, cv, t):
        lines = self.T.lines
        cur = None
        nxt = None
        for i, l in enumerate(lines):
            if l["start"] - 0.6 <= t:
                cur = i
        if cur is None:
            nxt = 0
        elif cur + 1 < len(lines):
            nxt = cur + 1
        u = cv.u
        u.save()
        u.set_source_rgba(0.0, 0.0, 0.02, 0.72)
        u.rectangle(0, 40, W, 230)
        u.fill()
        u.restore()
        cv.text("● RECORD-ALONG GUIDE · timing is a suggestion", 40, 70, 20, font=L.MONO_XB, anchor="left",
                color=L.MAGENTA, alpha=0.95, tracking=0.08, layer="ui")
        if cur is not None:
            l = lines[cur]
            live = l["start"] <= t <= l["end"] + 0.3
            self._wrap(cv, l["text"], 40, 118, 34, L.WHITE if live else L.DIM, 52)
        if nxt is not None:
            l = lines[nxt]
            lead = l["start"] - t
            self._wrap(cv, "next: " + l["text"], 40, 214, 24, (0.55, 0.62, 0.78), 62)
            if 0 < lead < 0.6:
                cv.u.new_path()
                cv.u.arc(1030, 70, 12, 0, 2 * math.pi)
                cv.u.set_source_rgba(*L.MINT, 1.0 - lead / 0.6 * 0.5)
                cv.u.fill()

    def _wrap(self, cv, text, x, y, size, color, max_chars):
        words, rows, row = text.split(), [], ""
        for w_ in words:
            if len(row) + len(w_) + 1 > max_chars and row:
                rows.append(row)
                row = w_
            else:
                row = (row + " " + w_).strip()
        rows.append(row)
        for k, r in enumerate(rows[:2]):
            cv.text(r, x, y + k * size * 1.25, size, font=L.UI, anchor="left", color=color, alpha=1.0, layer="ui")


def make_episode(timeline_path, **opts):
    return Episode(timeline_path, **opts)
