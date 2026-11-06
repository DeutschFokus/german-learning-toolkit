"""EP005 — Nuclear Tests Left a Timestamp in Your Body (bomb-pulse dating).

Narrated by the creator (no AI voice in any deliverable). Until his take
exists, animation timing comes from a scratch read (build/timeline_scratch.json);
`build.py human take.wav` re-times everything to the real voice.

Journey: an eye with a mushroom cloud in its reflection -> into the reflection,
the tests -> the real atmospheric carbon-14 record (Hua et al. 2022) -> air,
plants, animals, you -> a dividing cell locks the year into its DNA -> the curve
becomes a clock -> fat, heart, cortex -> the core of the eye lens, made before
birth, that you are reading this through -> back to the eye (loop).

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

from engine import bio  # noqa: E402
from engine.anatomy import eye_section  # noqa: E402
from engine.captions import Captions  # noqa: E402
from engine.eye import EH, EW, HeroEye  # noqa: E402
from engine.figure import Figure  # noqa: E402
from engine.gfx import (H, L, W, Canvas, Starfield, background, clamp, ease_in_cubic, ease_in_out,  # noqa: E402
                        ease_out_back, ease_out_cubic, ease_out_expo, lerp, mix, prog, smooth, window)
from engine.hud import htext, ucard, uline, upoly, ui_scope  # noqa: E402
from engine.nature import stamp  # noqa: E402
from engine.particles import Particles  # noqa: E402
from engine.postfx import Post  # noqa: E402
from engine.timeline import Timeline  # noqa: E402
from engine.volume import MushroomCloud, paint_rgba  # noqa: E402

EYE = (540.0, 1060.0, 0.92)                      # hook / outro framing
C14C = (1.0, 0.62, 0.22)                         # the colour of carbon-14 everywhere
HORIZON = 1330.0
CPU = 568.0                                      # cloud units -> px
CHART = (110.0, 520.0, 860.0, 600.0)             # x, y, w, h of the bomb-curve chart
ACCENTS = {"L01": C14C, "L02": C14C, "L03": L.CYAN, "L04": L.MINT, "L05": C14C, "L06": L.CYAN, "L07": L.AMBER,
           "L08": L.MAGENTA, "L09": L.CYAN, "L10": L.AMBER, "L11": C14C, "L12": L.WHITE, "L13": C14C}
CONTINUOUS = set()
X_IN = {"bomb": 0.20, "dna": 0.28, "outro": 0.35}
X_OUT = {"hook": 0.20, "chain": 0.28, "lens": 0.35}


def rot_pt(cx, cy, s, px, py):
    return cx + (px - cx) * s, cy + (py - cy) * s


class Episode:
    def __init__(self, timeline_path, captions=True, grain=0.007, guide=False):
        self.T = Timeline(timeline_path)
        self.fps = self.T.fps
        self.duration = self.T.duration
        loop = self.duration
        self.post = Post(grain=grain)
        self.stars = Starfield(seed=41)
        self.caps = Captions(self.T, accent_by_line=ACCENTS) if captions else None
        self.guide = guide
        self.eye = HeroEye(seed=5)
        self.cloud = MushroomCloud(seed=3, loop=loop)
        self.chart = bio.C14Chart()
        self.leaf = bio.Leaf(seed=3)
        self.brain = bio.Brain(seed=6)
        self.fat = bio.FatCells(n=34, radius=170, seed=4)
        self.fig = Figure(height=1150)
        self.dust = Particles(n=90, seed=8, kind="dust", loop=loop)
        rng = np.random.default_rng(12)
        self.atoms = [(rng.uniform(-1, 1), rng.uniform(0, 1), rng.uniform(0.6, 1.4), rng.uniform(0, 6.28))
                      for _ in range(150)]
        self.flashes = [(rng.uniform(60, 1020), rng.uniform(0, 1)) for _ in range(12)]
        self.neurons = [(rng.uniform(-1, 1), rng.uniform(-1, 1)) for _ in range(26)]
        self.neurons = [(x, y) for x, y in self.neurons if x * x + y * y < 0.85][:20]
        st = self.T.scene_starts()
        self.scenes = [(sid, s0, st[i + 1][1] if i + 1 < len(st) else self.duration)
                       for i, (sid, s0) in enumerate(st)]
        self.c = self._cues()
        self._ref_cache = {}

    def _cues(self):
        T = self.T
        w = lambda l, k: T.word(l, k).start  # noqa: E731
        c = {"sc_" + sid: (s0, s1) for sid, s0, s1 in self.scenes}
        for lid in [l["id"] for l in T.lines]:
            c[lid] = T.line(lid).start
            c[lid + "end"] = T.line(lid).end
        c.update({
            "bomb": w("L01", "bomb"), "timestamp": w("L01", "timestamp"), "body1": w("L01", "body."),
            "fifties": w("L02", "fifties"), "sixties": w("L02", "sixties,"), "nearly": w("L02", "nearly"),
            "doubled": w("L02", "doubled"), "radioactive": w("L02", "radioactive"), "carbon": w("L02", "carbon"),
            "air": w("L02", "air."),
            "y1963": w("L03", "1963,"), "banned": w("L03", "banned,"), "fade": w("L03", "fade,"),
            "year_a": T.word("L03", -3).start, "year_b": T.word("L03", -1).start,
            "plants": w("L04", "Plants"), "breathed": w("L04", "breathed"), "animals": w("L04", "Animals"),
            "so4": w("L04", "So"), "you4": w("L04", "you."),
            "new": w("L05", "new"), "cell5": w("L05", "cell"), "locks": w("L05", "locks"), "years": w("L05", "year's"),
            "level": w("L05", "level"), "dna": w("L05", "DNA."),
            "scientists": w("L06", "scientists"), "stockholm": w("L06", "Stockholm"), "turned": w("L06", "turned"),
            "clock": w("L06", "clock"), "cells6": w("L06", "cells."),
            "fat": w("L07", "fat"), "ten": w("L07", "ten"), "replaced": w("L07", "replaced"),
            "heart": w("L08", "heart?"), "barely": w("L08", "Barely"), "one8": w("L08", "one"),
            "neurons": w("L09", "neurons"), "cortex": w("L09", "cortex?"), "old": w("L09", "old"),
            "center": w("L10", "center"), "eye10": w("L10", "eye"), "lens": w("L10", "lens..."),
            "made": w("L11", "made"), "before": w("L11", "before"), "born": w("L11", "born."),
            "reading": w("L12", "reading"), "through": w("L12", "through"), "now": w("L12", "now."),
            "measure": w("L13", "measure"), "because": w("L13", "because..."),
        })
        return c

    # ------------------------------------------------------------------ frame
    def frame(self, i):
        t = i / self.fps
        cv = Canvas()
        self.draw(cv, t)
        return self.post.finish(cv, i)

    def draw(self, cv, t):
        background(cv, t, haze=(0.5, 0.42), haze_color=(0.10, 0.18, 0.40), haze_amt=0.7)
        n = len(self.scenes)
        for k, (sid, s0, s1) in enumerate(self.scenes):
            first, last = k == 0, k == n - 1
            cut_in = sid in CONTINUOUS
            cut_out = (not last) and self.scenes[k + 1][0] in CONTINUOUS
            Xi = 0.0 if (first or cut_in) else X_IN.get(sid, 0.22)
            Xo = 0.0 if (last or cut_out) else X_OUT.get(sid, 0.22)
            if not (s0 - Xi <= t < s1 + Xo):
                continue
            a, sc, ty, cx, cy = 1.0, 1.0, 0.0, W / 2, H / 2
            if Xi and t < s0 + Xi:
                p = prog(t, s0 - Xi, s0 + Xi)
                if sid == "bomb":                 # out of the reflection into the real thing
                    a, sc, cx, cy = smooth(p), 1.0 + 0.6 * (1 - ease_out_cubic(p)), 540.0, 900.0
                elif sid == "dna":                # into the nucleus
                    a, sc = smooth(p), 1.0 + 0.5 * (1 - ease_out_cubic(p))
                else:
                    a, sc, ty = smooth(p), 0.97 + 0.03 * ease_out_cubic(p), 60 * (1 - ease_out_cubic(p))
            if Xo and t > s1 - Xo:
                p = prog(t, s1 - Xo, s1 + Xo)
                if sid == "hook":
                    a = 1 - smooth(p)
                elif sid == "chain":              # dive into the body
                    a, sc, cx, cy = 1 - smooth(p), 1 + 2.5 * ease_in_cubic(p), 540.0 + 0, 820.0
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

    # ================================================================== the eye (hook, lens, outro)
    def _reflection(self, t):
        key = round(t * self.fps)
        if key not in self._ref_cache:
            self._ref_cache = {}
            img, _ = self.cloud.render(72, 92, 0.62, t, view=(-0.95, 0.95, -0.05, 2.0), steps=26)
            self._ref_cache[key] = img
        img = self._ref_cache[key]

        def fn(ctx, ix, iy, R, glow):
            from engine.volume import rgba_surface
            cx_, cy_ = ix + R * 0.30, iy + R * 0.10
            w_, h_ = R * 0.95, R * 0.85
            ctx.save()
            ctx.translate(cx_, cy_)
            ctx.push_group()
            if not glow:
                # a tiny dawn sky over a dark sea, as seen in a convex mirror (curved, soft horizon)
                pat = cairo.LinearGradient(0, -h_ / 2, 0, h_ / 2)
                pat.add_color_stop_rgba(0.00, 0.10, 0.14, 0.30, 0.10)
                pat.add_color_stop_rgba(0.50, 0.60, 0.32, 0.22, 0.30)
                pat.add_color_stop_rgba(0.63, 1.00, 0.55, 0.28, 0.42)
                pat.add_color_stop_rgba(0.72, 0.10, 0.10, 0.16, 0.12)
                pat.add_color_stop_rgba(1.00, 0.02, 0.03, 0.06, 0.05)
                ctx.save()
                ctx.scale(1.0, h_ / w_)
                ctx.arc(0, 0, w_ / 2, 0, 2 * math.pi)
                ctx.restore()
                ctx.set_source(pat)
                ctx.fill()
            s_ = rgba_surface(img)
            sw, sh = img.shape[1], img.shape[0]
            scl = (w_ * 0.70) / sw
            ctx.save()
            ctx.translate(-sw * scl / 2, h_ * 0.16 - sh * scl)
            ctx.scale(scl, scl)
            ctx.set_source_surface(s_, 0, 0)
            ctx.get_source().set_filter(cairo.FILTER_BILINEAR)
            ctx.paint_with_alpha(1.0 if not glow else 0.9)
            ctx.restore()
            ctx.pop_group_to_source()
            m = cairo.RadialGradient(0, -h_ * 0.10, w_ * 0.30, 0, -h_ * 0.10, w_ * 0.60)
            m.add_color_stop_rgba(0, 0, 0, 0, 1)
            m.add_color_stop_rgba(1, 0, 0, 0, 0)
            ctx.mask(m)
            ctx.restore()
        return fn

    def _eye(self, cv, t, x, y, s, alpha=1.0, reflect=1.0, pupil=None, ticks=0.0):
        L_ = self.duration
        look = (5 * math.sin(2 * math.pi * 3 * t / L_) + 2 * math.sin(2 * math.pi * 7 * t / L_),
                3 * math.sin(2 * math.pi * 4 * t / L_ + 1.0))
        pu = pupil if pupil is not None else 0.33 + 0.015 * math.sin(2 * math.pi * 5 * t / L_)
        self.eye.draw(cv, x, y, scale=s, alpha=alpha, look=look, pupil=pu,
                      reflect=self._reflection(t) if reflect > 0.003 else None, reflect_alpha=reflect)
        if ticks > 0.003:
            ix, iy = x + (self.eye.cx + look[0] - EW / 2) * s, y + (self.eye.cy + look[1] - EH / 2) * s
            R = self.eye.R * s
            for k in range(60):
                a = -math.pi / 2 + k / 60 * 2 * math.pi
                lit = clamp(ticks * 60 - k)
                r0, r1 = R * (1.10 if k % 5 else 1.07), R * 1.16
                cv.line([(ix + math.cos(a) * r0, iy + math.sin(a) * r0), (ix + math.cos(a) * r1, iy + math.sin(a) * r1)],
                        C14C, width=3 if k % 5 == 0 else 1.6, alpha=alpha * lit * 0.85, glow=0.6 * lit)

    def _headline(self, cv, alphas=(1, 1, 1), offs=(0, 0, 0)):
        rows = [("NUCLEAR TESTS", 318, 96, C14C, 0.55), ("LEFT A TIMESTAMP", 424, 72, L.WHITE, 0.0),
                ("IN YOUR BODY", 504, 72, L.WHITE, 0.0)]
        for (txt, y, size, col, gl), a_, o in zip(rows, alphas, offs):
            htext(cv, txt, W / 2 + o, y, size, color=col, alpha=a_, glow=gl, shadow=0.85)

    def s_hook(self, cv, t):
        c = self.c
        s1 = c["sc_hook"][1]
        # the seconds ring around the iris on "timestamp" (gone again well before the loop point)
        tk = prog(t, c["timestamp"] - 0.1, c["body1"] + 0.4)
        tick_a = ease_out_cubic(tk) * (1 - smooth(prog(t, c["L01end"] - 0.1, c["L01end"] + 0.3)))
        z = ease_in_cubic(prog(t, c["L01end"] - 0.25, s1 + 0.30))
        rx, ry = self.eye.screen_point(EYE[0], EYE[1], EYE[2], self.eye.cx + self.eye.R * 0.30,
                                       self.eye.cy + self.eye.R * 0.10)
        with cv.transform(s=1 + 8 * z, cx=rx, cy=ry):
            self._eye(cv, t, *EYE, ticks=tick_a * (tk if tk < 1 else 1.0))
        ex = ease_in_cubic(prog(t, c["L01end"] - 0.15, c["L01end"] + 0.35))
        self._headline(cv, alphas=[1 - ex] * 3, offs=(0, -40 * ex, 40 * ex))
        if z > 0.01:
            cv.motion = None

    def s_outro(self, cv, t):
        c = self.c
        s0, s1 = c["sc_outro"]
        # from the lens diagram back out to the eye: the eye fades up, the headline returns line by line
        zoom = 1 + 0.35 * (1 - ease_out_cubic(prog(t, s0 - 0.35, s0 + 1.2)))
        with cv.transform(s=zoom, cx=EYE[0], cy=EYE[1]):
            self._eye(cv, t, *EYE)
        back = prog(t, c["because"] - 0.15, c["because"] + 1.0)
        if back > 0:
            ks = [ease_out_expo(prog(back, 0.14 * k, 0.55 + 0.14 * k)) for k in range(3)]
            al = [smooth(prog(back, 0.14 * k, 0.35 + 0.14 * k)) for k in range(3)]
            self._headline(cv, alphas=al, offs=[-140 * (1 - k) for k in ks])

    # ================================================================== the tests
    def _sky(self, cv, t, horizon, glow=1.0):
        b = cv.b
        g = cairo.LinearGradient(0, 0, 0, horizon)
        g.add_color_stop_rgb(0.0, 0.015, 0.02, 0.06)
        g.add_color_stop_rgb(0.55, 0.06, 0.08, 0.20)
        g.add_color_stop_rgb(0.86, 0.30, 0.20, 0.30)
        g.add_color_stop_rgb(1.0, 0.85 * glow + 0.1, 0.45 * glow + 0.08, 0.28 * glow + 0.08)
        b.rectangle(0, 0, W, horizon)
        b.set_source(g)
        b.fill()
        self.stars.draw(cv, t, alpha=0.6, dust_alpha=0.0)
        g = cairo.LinearGradient(0, horizon, 0, H)
        g.add_color_stop_rgb(0.0, 0.10, 0.08, 0.12)
        g.add_color_stop_rgb(0.15, 0.03, 0.05, 0.09)
        g.add_color_stop_rgb(1.0, 0.01, 0.015, 0.03)
        b.rectangle(0, horizon, W, H - horizon)
        b.set_source(g)
        b.fill()
        # ripples on the water
        b.set_line_width(1.2)
        for k in range(26):
            yy = horizon + 6 + (k ** 1.6) * 3.2
            off = (t * (14 + k) + k * 37) % 120
            b.set_source_rgba(0.55, 0.62, 0.85, 0.05 + 0.002 * k)
            x = -off
            while x < W:
                b.move_to(x, yy)
                b.line_to(x + 40 + k * 2, yy)
                x += 120
            b.stroke()

    def s_bomb(self, cv, t):
        c = self.c
        s0, s1 = c["sc_bomb"]
        t0 = s0 + 0.10                                        # detonation
        age = 0.02 + 0.86 * ease_out_cubic(prog(t, t0, s1 + 0.5)) ** 0.9
        tilt = 260 * ease_in_out(prog(t, c["air"] - 0.4, s1 + 0.3))     # follow the carbon up into the sky
        with cv.transform(ty=tilt):
            self._sky(cv, t, HORIZON, glow=0.8 + 0.4 * (1 - age))
            # distant tests flashing along the horizon while the years tick by
            yrs = prog(t, c["L02"], c["sixties"] + 1.2)
            for x, ph in self.flashes:
                f = (yrs * 1.0 - ph * 0.9)
                if 0 < f < 0.12:
                    k = 1 - f / 0.12
                    cv.radial(x, HORIZON - 4, 60 * k + 10, (1.0, 0.85, 0.6), alpha=0.8 * k, glow=1.0)
            img, (Hc, R, r, heat) = self.cloud.render(300, 339, age, t, view=(-0.95, 0.95, -0.05, 2.1), steps=36)
            top = HORIZON - 2.1 * CPU
            paint_rgba(cv, img, 0, top, W, 2.15 * CPU, alpha=1.0, glow=0.55 + 0.4 * heat)
            # fireball light on the water + flash + shock ring
            cv.radial(540, HORIZON + 10, 420, (1.0, 0.6, 0.3), alpha=0.35 * (0.3 + heat), glow=0.4 * heat)
            for k in range(14):
                yy = HORIZON + 14 + k * 26
                wv = 30 + 8 * math.sin(t * 3 + k)
                cv.line([(540 - wv, yy), (540 + wv, yy)], (1.0, 0.65, 0.35), width=3, alpha=(0.5 - 0.03 * k) * (0.3 + heat))
            sh = prog(t, t0, t0 + 1.6)
            if 0 < sh < 1:
                b = cv.b
                b.save()
                b.translate(540, HORIZON + 4)
                b.scale(1, 0.12)
                b.arc(0, 0, 60 + 1500 * ease_out_cubic(sh), 0, 2 * math.pi)
                b.restore()
                b.set_line_width(4)
                b.set_source_rgba(1.0, 0.9, 0.8, 0.6 * (1 - sh))
                b.stroke()
            # carbon-14 rising into the air
            ra = prog(t, c["radioactive"] - 0.2, s1 + 0.4)
            if ra > 0:
                for i, (u, v, sz, ph) in enumerate(self.atoms):
                    f = clamp(ra * 1.3 - v * 0.5)
                    if f <= 0:
                        continue
                    x = 540 + u * (R * CPU * 1.2 + 520 * f) + 18 * math.sin(t * 1.3 + ph)
                    y = HORIZON - (Hc + r) * CPU - 60 - 900 * ease_out_cubic(f) * (0.4 + 0.6 * v)
                    cv.circle(x, y, 3.2 * sz, C14C, alpha=0.85 * smooth(f * 4), glow=0.9)
                    if i % 19 == 0:
                        htext(cv, "¹⁴C", x + 14, y - 14, 22, color=C14C, alpha=0.9 * smooth(f * 4), font=L.MONO_XB,
                              anchor="left", shadow=0.6)
        if prog(t, t0, t0 + 0.6) < 1:
            cv.flash = 0.55 * (1 - ease_out_cubic(prog(t, t0, t0 + 0.6))) if t >= t0 else 0.0
        # year counter
        ya = window(t, c["L02"] - 0.1, c["L02end"] + 0.2, 0.25, 0.3)
        if ya > 0:
            yr = int(lerp(1952, 1962, prog(t, c["L02"], c["sixties"] + 1.2)))
            htext(cv, "YEAR", 92, 300, 22, color=(0.8, 0.86, 0.98), alpha=ya, font=L.MONO_XB, anchor="left",
                  tracking=0.3)
            htext(cv, f"{yr}", 92, 352, 56, color=L.WHITE, alpha=ya, font=L.MONO_XB, anchor="left")
        # the gauge: carbon-14 in the air, nearly doubled
        ga = window(t, c["nearly"] - 0.15, s1 + 0.4, 0.25, 0.3)
        if ga > 0:
            fill = ease_out_cubic(prog(t, c["nearly"], c["doubled"] + 0.5))
            val = lerp(1.0, self.chart.peak()[1], fill)
            x0, x1, yg = 560.0, 970.0, 372.0
            htext(cv, "CARBON-14 IN THE AIR", x1, 300, 24, color=(0.8, 0.86, 0.98), alpha=ga, font=L.MONO_XB,
                  anchor="right", tracking=0.08)
            uline(cv, [(x0, yg), (x1, yg)], (0.4, 0.45, 0.6), width=14, alpha=ga * 0.6)
            xm = lerp(x0, x1, (val - 1.0) / 1.0)
            uline(cv, [(x0, yg), (xm, yg)], C14C, width=14, alpha=ga)
            htext(cv, "×1", x0, yg + 34, 20, color=L.DIM, alpha=ga, font=L.MONO_XB)
            htext(cv, "×2", x1, yg + 34, 20, color=L.DIM, alpha=ga, font=L.MONO_XB)
            htext(cv, f"×{val:.2f}", xm, yg - 40, 40, color=C14C, alpha=ga, font=L.MONO_XB, glow=0.5)

    # ================================================================== the bomb curve
    def _chart_frame(self, cv, a, box=CHART, labels=True):
        x0, y0, w, h = box
        X = lambda yr: self.chart.xy(yr, 1.0, box)[0]  # noqa: E731
        Y = lambda f: self.chart.xy(1950, f, box)[1]   # noqa: E731
        uline(cv, [(x0, Y(0.9)), (x0 + w, Y(0.9))], (0.6, 0.66, 0.8), width=2, alpha=0.7 * a)
        uline(cv, [(x0, Y(1.0)), (x0 + w, Y(1.0))], (0.6, 0.66, 0.8), width=2, alpha=0.6 * a, dash=[8, 8])
        uline(cv, [(x0, Y(2.0)), (x0 + w, Y(2.0))], (0.6, 0.66, 0.8), width=1.5, alpha=0.35 * a, dash=[4, 10])
        if labels:
            htext(cv, "×1  NATURAL", x0 + w, Y(1.0) - 22, 20, color=(0.8, 0.86, 0.98), alpha=a, font=L.MONO_XB,
                  anchor="right", shadow=0.6)
            htext(cv, "×2", x0, Y(2.0) - 22, 20, color=(0.8, 0.86, 0.98), alpha=a, font=L.MONO_XB, anchor="left")
            for yr in range(1950, 2030, 10):
                uline(cv, [(X(yr), Y(0.9)), (X(yr), Y(0.9) + 10)], (0.6, 0.66, 0.8), width=2, alpha=0.7 * a)
                htext(cv, f"{yr}", X(yr), Y(0.9) + 34, 20, color=(0.8, 0.86, 0.98), alpha=a, font=L.MONO_XB,
                      shadow=0.6)

    def s_curve(self, cv, t):
        c = self.c
        s0, s1 = c["sc_curve"]
        a = smooth(prog(t, s0 - 0.1, s0 + 0.4))
        self.stars.draw(cv, t, alpha=0.5, dust_alpha=0.0)
        htext(cv, "CARBON-14 IN THE AIR", W / 2, 330, 54, color=L.WHITE, alpha=a, glow=0.1)
        htext(cv, "Northern Hemisphere · measured", W / 2, 396, 24, color=(0.8, 0.86, 0.98), alpha=a, font=L.MONO_XB,
              tracking=0.04)
        self._chart_frame(cv, a)
        up = lerp(1950, 1963.6, ease_in_out(prog(t, s0, c["y1963"] + 0.2)))
        down = lerp(1963.6, 2019.4, ease_in_out(prog(t, c["fade"] - 0.6, c["year_b"] + 0.6)))
        upto = down if t > c["fade"] - 0.6 else up
        pts = self.chart.points(CHART, upto=upto)
        if len(pts) > 1:
            cv.line(pts, C14C, width=5, alpha=a, glow=0.9)
            hx, hy = pts[-1]
            cv.circle(hx, hy, 9, L.WHITE, alpha=a, glow=1.0)
        py_, pf = self.chart.peak()
        pa = smooth(prog(t, c["y1963"] - 0.1, c["y1963"] + 0.3))
        if pa > 0:
            px, pyy = self.chart.xy(py_, pf, CHART)
            htext(cv, "1963", px + 18, pyy - 14, 34, color=C14C, alpha=pa * a, font=L.MONO_XB, anchor="left", glow=0.4)
            htext(cv, f"×{pf:.2f}", px + 18, pyy + 24, 24, color=L.WHITE, alpha=pa * a, font=L.MONO_XB, anchor="left")
        ba = window(t, c["banned"] - 0.1, s1, 0.12, 0.3)
        if ba > 0:
            pop = 1 - ease_out_back(prog(t, c["banned"] - 0.1, c["banned"] + 0.3))
            stamp(cv, "TEST BAN TREATY", 650, 700, size=48, angle=-0.08, color=L.MINT, alpha=ba * a, pop=pop,
                  sub="1963 · MOST TESTS IN THE AIR END")
        # every year gets its own level: ticks pop as the decline is drawn
        for yr in (1970, 1980, 1990, 2000, 2010, 2019):
            if upto >= yr:
                k = ease_out_back(clamp((upto - yr) / 4.0))
                x, y = self.chart.xy(yr, self.chart.level(yr), CHART)
                cv.circle(x, y, 7 * k, L.CYAN, alpha=a, glow=0.8)
                htext(cv, f"{yr}", x, y - 30, 20, color=L.CYAN, alpha=a * clamp(k), font=L.MONO_XB)
        na = smooth(prog(t, c["year_b"] - 0.3, c["year_b"] + 0.3))
        htext(cv, "today's dose from all test fallout ≈ 1/500 of natural radiation", W / 2, 1206, 21,
              color=(0.8, 0.86, 0.98), alpha=na * a, font=L.MONO, shadow=0.6)
        htext(cv, "data: Hua et al. 2022, Radiocarbon", W / 2, 1240, 18, color=L.DIM, alpha=a * 0.9, font=L.MONO,
              shadow=0.5)

    # ================================================================== air -> plants -> animals -> you
    def _chain_cam(self, t):
        c = self.c
        k1 = ease_in_out(prog(t, c["animals"] - 0.45, c["animals"] + 0.25))
        k2 = ease_in_out(prog(t, c["so4"] - 0.45, c["so4"] + 0.25))
        return 1080 * (k1 + k2)

    def s_chain(self, cv, t):
        c = self.c
        s0, s1 = c["sc_chain"]
        a = smooth(prog(t, s0 - 0.1, s0 + 0.4))
        camx = self._chain_cam(t)
        v = camx - self._chain_cam(t - 1 / self.fps)
        if abs(v) > 3:
            cv.motion = (v * 0.5, 0.0)
        # sunlight behind the leaf
        cv.radial(540 - camx * 0.3, 420, 700, (1.0, 0.78, 0.45), alpha=0.35 * a, glow=0.3)
        self.dust.draw(cv, t, alpha=0.6 * a)
        lx, ly = 540 - camx, 860
        bio.paint(cv, self.leaf.surf, lx, ly, scale=0.78, alpha=a, glow=0.25)
        # carbon-14 drifting into the leaf
        f1 = prog(t, s0, c["animals"] - 0.2)
        rng = np.random.default_rng(5)
        for k in range(60):
            u0, v0 = rng.uniform(-1, 1), rng.uniform(0, 1)
            tx, ty = lx + rng.uniform(-170, 170), ly + rng.uniform(-300, 300)
            sx, sy = lx + u0 * 520, 160 + v0 * 200
            f = clamp(f1 * 1.6 - v0 * 0.6)
            x, y = lerp(sx, tx, ease_in_out(f)), lerp(sy, ty, ease_in_out(f))
            cv.circle(x, y, 4, C14C, alpha=a * (0.9 - 0.4 * f) * (f1 > 0), glow=0.8)
        # the cow, grazing the same leaves
        cow_x, cow_y = 1080 + 540 - camx - 290, 840
        bio.hologram_shape(cv, bio.cow_points(), cow_x, cow_y, 1.0, L.MINT, alpha=a, t=t)
        f2 = prog(t, c["animals"] - 0.2, c["so4"] - 0.1)
        for k in range(40):
            f = clamp(f2 * 1.5 - k / 80)
            if f <= 0 or f >= 1:
                continue
            x = lerp(lx + 120, cow_x + 555, ease_in_out(f))
            y = lerp(ly + 100, cow_y + 305, ease_in_out(f)) - 140 * math.sin(f * math.pi)
            cv.circle(x, y, 4, C14C, alpha=a * 0.9, glow=0.8)
        if f2 > 0.5:
            for k in range(26):
                px = cow_x + 120 + (k * 53) % 300
                py = cow_y + 80 + (k * 37) % 150
                cv.circle(px, py, 3.5, C14C, alpha=a * smooth((f2 - 0.5) * 3) * (0.5 + 0.5 * math.sin(t * 3 + k)),
                          glow=0.7)
        # you
        fx = 2160 + 540 - camx
        fy = 300
        self.fig.draw(cv, t, fx, fy, s=1.0, alpha=a, top_color=L.CYAN, bottom_color=L.CYAN, fill_alpha=0.10)
        f3 = prog(t, c["so4"] - 0.2, s1 + 0.2)
        for k in range(40):
            f = clamp(f3 * 1.5 - k / 80)
            if f <= 0:
                continue
            ex_ = fx + ((k * 61) % 220 - 110) * 0.9
            ey_ = fy + 260 + (k * 97) % 700
            x = lerp(cow_x + 400, ex_, ease_in_out(f))
            y = lerp(cow_y + 150, ey_, ease_in_out(f)) - 160 * math.sin(clamp(f) * math.pi)
            cv.circle(x, y, 4, C14C, alpha=a * 0.9, glow=0.8)
        for name, x in (("¹⁴CO₂ → LEAF", lx), ("→ ANIMALS", cow_x + 290), ("→ YOU", fx)):
            htext(cv, name, x, 1236, 30, color=C14C, alpha=a * 0.95, font=L.MONO_XB, shadow=0.8)

    # ================================================================== a new cell locks in the year
    def s_dna(self, cv, t):
        c = self.c
        s0, s1 = c["sc_dna"]
        a = smooth(prog(t, s0 - 0.1, s0 + 0.3))
        split = ease_in_out(prog(t, c["new"] - 0.1, c["locks"] - 0.1))
        zin = ease_in_cubic(prog(t, c["locks"] - 0.35, c["locks"] + 0.25))
        if zin < 1:
            nx = 540 + 230 * 1.05 * split * 0.98
            with cv.group(1 - zin) if zin > 0 else _null(), cv.transform(s=1 + 4 * zin, cx=nx, cy=880):
                bio.draw_cell(cv, 540, 880, 230, split=split, t=t, alpha=a)
                htext(cv, "A NEW CELL", W / 2, 470, 44, color=L.WHITE, alpha=a * (1 - zin) *
                      smooth(prog(t, c["new"] - 0.1, c["new"] + 0.3)), glow=0.1)
        if zin > 0:
            yr = 1994
            lvl = self.chart.level(yr + 0.5)
            built = ease_in_out(prog(t, c["locks"], c["dna"] + 0.2))
            front = 1 - built
            bio.dna_helix(cv, 600, 430, 1000, 150, t, alpha=zin * a, built=max(built, 0.02),
                          glow_from=(front, min(1.0, front + 0.35)), glow_col=C14C)
            ma = smooth(prog(t, c["years"] - 0.2, c["years"] + 0.2)) * zin
            ucard(cv, 70, 560, 300, 170, alpha=ma, border=C14C)
            htext(cv, "THIS CELL", 96, 600, 20, color=(0.8, 0.86, 0.98), alpha=ma, font=L.MONO_XB, anchor="left",
                  tracking=0.2, shadow=0)
            htext(cv, f"MADE IN {yr}", 96, 646, 32, color=L.WHITE, alpha=ma, font=L.MONO_XB, anchor="left", shadow=0)
            htext(cv, f"¹⁴C  ×{lvl:.2f}", 96, 694, 32, color=C14C, alpha=ma, font=L.MONO_XB, anchor="left", glow=0.4,
                  shadow=0)
            # the value flies into the DNA and locks
            fl = ease_in_out(prog(t, c["level"] - 0.1, c["level"] + 0.6))
            if 0 < fl < 1:
                x = lerp(330, 600, fl)
                y = lerp(694, 1000, fl) - 120 * math.sin(fl * math.pi)
                cv.circle(x, y, 12, C14C, alpha=a, glow=1.0)
            la = smooth(prog(t, c["dna"] - 0.15, c["dna"] + 0.25))
            if la > 0:
                pop = 1 - ease_out_back(prog(t, c["dna"] - 0.15, c["dna"] + 0.3))
                self._padlock(cv, 880, 980, 1.0 + 0.3 * pop, la * a, closed=smooth(prog(t, c["dna"], c["dna"] + 0.3)))
                htext(cv, "LOCKED IN", 880, 1090, 34, color=L.MINT, alpha=la * a, font=L.MONO_XB, glow=0.4)
                htext(cv, "for the life", 880, 1130, 20, color=(0.8, 0.86, 0.98), alpha=la * a, font=L.MONO_XB)
                htext(cv, "of the cell", 880, 1158, 20, color=(0.8, 0.86, 0.98), alpha=la * a, font=L.MONO_XB)

    def _padlock(self, cv, x, y, s, a, closed=1.0):
        col = L.MINT
        cv.rect(x - 44 * s, y - 10 * s, 88 * s, 70 * s, col, alpha=0.25 * a, radius=10 * s, glow=0.4)
        cv.rect(x - 44 * s, y - 10 * s, 88 * s, 70 * s, col, alpha=a, fill=False, width=4, radius=10 * s, glow=0.6)
        lift = 18 * s * (1 - closed)
        cv.arc(x, y - 10 * s - lift, 30 * s, math.pi, 2 * math.pi, color=col, alpha=a, width=7 * s, glow=0.6)
        cv.line([(x - 30 * s, y - 10 * s - lift), (x - 30 * s, y - 2 * s - lift * 0)], col, width=7 * s, alpha=a)
        cv.line([(x + 30 * s, y - 10 * s - lift), (x + 30 * s, y - 2 * s)], col, width=7 * s, alpha=a)
        cv.circle(x, y + 22 * s, 7 * s, col, alpha=a)

    # ================================================================== the clock
    def s_clock(self, cv, t):
        c = self.c
        s0, s1 = c["sc_clock"]
        a = smooth(prog(t, s0 - 0.1, s0 + 0.4))
        self.stars.draw(cv, t, alpha=0.5, dust_alpha=0.0)
        morph = ease_in_out(prog(t, c["clock"] - 0.35, c["clock"] + 0.75))
        ka = smooth(prog(t, c["stockholm"] - 0.2, c["stockholm"] + 0.2))
        ucard(cv, 110, 262, 860, 150, alpha=ka * a, border=L.CYAN)
        htext(cv, "KAROLINSKA INSTITUTET · STOCKHOLM", 140, 310, 34, color=L.WHITE, alpha=ka * a, anchor="left", shadow=0)
        htext(cv, "Frisén lab · cell birth dating, first published 2005", 140, 366, 22, color=L.CYAN, alpha=ka * a,
              font=L.MONO_XB, anchor="left", shadow=0)
        box = (110.0, 600.0, 860.0, 560.0)
        fa = a * (1 - morph)
        self._chart_frame(cv, fa, box=box)
        center, r0, k = (540.0, 900.0), 230.0, 130.0
        pts = self.chart.points(box, upto=2019.4, morph=morph, center=center, r0=r0, k=k)
        cv.line(pts, C14C, width=5, alpha=a, glow=0.9)
        # reading a sample: level -> year
        lvl, yr = 1.25, self.chart.year_for(1.25)
        ra = smooth(prog(t, c["scientists"] - 0.1, c["scientists"] + 0.3)) * (1 - morph)
        if ra > 0:
            sweep = ease_in_out(prog(t, c["scientists"], c["stockholm"] + 0.2))
            x0, y0 = self.chart.xy(1950, lvl, box)
            xc, yc = self.chart.xy(yr, lvl, box)
            uline(cv, [(x0, y0), (lerp(x0, xc, sweep), y0)], L.CYAN, width=3, alpha=ra, dash=[10, 8])
            htext(cv, f"SAMPLE ¹⁴C ×{lvl:.2f}", x0 + 10, y0 - 28, 22, color=L.CYAN, alpha=ra, font=L.MONO_XB,
                  anchor="left", shadow=0.7)
            down = ease_in_out(prog(t, c["stockholm"] + 0.1, c["turned"] + 0.2))
            if down > 0:
                yb = self.chart.xy(yr, 0.9, box)[1]
                uline(cv, [(xc, yc), (xc, lerp(yc, yb, down))], L.CYAN, width=3, alpha=ra, dash=[10, 8])
                cv.circle(xc, yc, 9, L.WHITE, alpha=ra, glow=1.0)
        # the dial
        if morph > 0:
            for d in range(1950, 2020, 10):
                ang = -math.pi / 2 + (d - 1950) / 70 * 2 * math.pi * 0.96
                r1, r2 = r0 - 30, r0 - 12
                cv.line([(center[0] + math.cos(ang) * r1, center[1] + math.sin(ang) * r1),
                         (center[0] + math.cos(ang) * r2, center[1] + math.sin(ang) * r2)], L.WHITE, width=3,
                        alpha=a * morph)
                htext(cv, f"{d}", center[0] + math.cos(ang) * (r0 - 62), center[1] + math.sin(ang) * (r0 - 62), 20,
                      color=(0.8, 0.86, 0.98), alpha=a * morph, font=L.MONO_XB, shadow=0.6)
            ang = -math.pi / 2 + (yr - 1950) / 70 * 2 * math.pi * 0.96
            hand = ease_out_back(prog(t, c["clock"] + 0.3, c["cells6"] + 0.3))
            hx, hy = center[0] + math.cos(ang) * (r0 - 40) * hand, center[1] + math.sin(ang) * (r0 - 40) * hand
            cv.line([center, (hx, hy)], L.WHITE, width=6, alpha=a * morph, glow=0.7)
            cv.circle(*center, 10, L.WHITE, alpha=a * morph, glow=1.0)
        ya = smooth(prog(t, c["turned"] - 0.1, c["turned"] + 0.3))
        if ya > 0:
            xc, yc = self.chart.xy(yr, lvl, box)
            bx, by = lerp(xc + 200, 540, morph), lerp(yc + 80, 560, morph)
            htext(cv, f"CELLS BORN ≈ {int(round(yr))}", bx, by, 40, color=L.WHITE, alpha=ya * a, font=L.MONO_XB,
                  glow=0.3)

    # ================================================================== fat, heart, cortex
    def s_body(self, cv, t):
        c = self.c
        s0, s1 = c["sc_body"]
        a = smooth(prog(t, s0 - 0.1, s0 + 0.4))
        fig_x, fig_y = 300.0, 320.0
        u = self.fig.u
        self.fig.draw(cv, t, fig_x, fig_y, s=1.0, alpha=a, top_color=L.CYAN, bottom_color=L.CYAN, fill_alpha=0.08,
                      scan_alpha=0.12)
        beats = [("fat", c["L07"] - 0.2, c["L08"] - 0.3), ("heart", c["L08"] - 0.3, c["L09"] - 0.3),
                 ("cortex", c["L09"] - 0.3, s1 + 0.3)]
        ins = (770.0, 820.0, 165.0)
        for name, b0, b1 in beats:
            w_ = window(t, b0, b1, 0.3, 0.3)
            if w_ <= 0:
                continue
            if name == "fat":
                org = (fig_x, fig_y + 3.45 * u)
                for sgn in (-1, 1):
                    cv.radial(org[0] + sgn * 0.42 * u, org[1], 0.42 * u, L.AMBER, alpha=0.55 * w_ * a, glow=0.6)
                cv.radial(org[0], org[1] + 0.05 * u, 0.55 * u, L.AMBER, alpha=0.45 * w_ * a, glow=0.5)
                col = L.AMBER
            elif name == "heart":
                org = (fig_x + 0.22 * u, fig_y + 2.35 * u)
                bio.draw_heart(cv, org[0], org[1], 0.30, t, alpha=w_ * a, bpm=66)
                col = L.MAGENTA
            else:
                org = (fig_x, fig_y + 0.48 * u)
                bio.paint(cv, self.brain.surf, org[0], org[1], scale=0.36, alpha=w_ * a, glow=0.6)
                col = L.CYAN
            self._inset(cv, t, name, org, ins, w_ * a, col, b0)
        # the three answers stack up as a summary
        rows = [("FAT CELLS", "≈ 10% / YEAR", L.AMBER, c["ten"]), ("HEART MUSCLE", "≈ 1% / YEAR", L.MAGENTA, c["one8"]),
                ("CORTEX NEURONS", "NONE", L.CYAN, c["old"])]
        for i, (lab, val, col, tk) in enumerate(rows):
            ra = smooth(prog(t, tk - 0.1, tk + 0.3)) * a
            y = 300 + i * 66
            htext(cv, lab, 600, y, 22, color=(0.8, 0.86, 0.98), alpha=ra, font=L.MONO_XB, anchor="left", tracking=0.1)
            htext(cv, val, 980, y, 30, color=col, alpha=ra, font=L.MONO_XB, anchor="right", glow=0.4)
        htext(cv, "REPLACED", 980, 252, 20, color=L.DIM, alpha=smooth(prog(t, c["ten"] - 0.1, c["ten"] + 0.3)) * a,
              font=L.MONO_XB, anchor="right", tracking=0.2)

    def _inset(self, cv, t, name, org, ins, a, col, b0):
        ix, iy, r = ins
        pop = ease_out_back(clamp((t - b0 - 0.1) / 0.45))
        rr = r * pop
        if rr < 2:
            return
        cv.line([org, (ix - rr * 0.92, iy + rr * 0.3)], col, width=2, alpha=0.8 * a, glow=0.5)
        cv.circle(org[0], org[1], 14, col, alpha=0.9 * a, fill=False, width=2.5, glow=0.6)
        b = cv.b
        b.save()
        b.new_path()
        b.arc(ix, iy, rr, 0, 2 * math.pi)
        b.clip()
        cv.circle(ix, iy, rr, (0.03, 0.05, 0.10), alpha=0.92 * a)
        if name == "fat":
            yrs = clamp((t - b0 - 0.5) / 4.0) * 4.0
            self.fat.draw(cv, ix, iy, s=pop * 0.95, alpha=a, years=yrs, rate=0.10, t=t)
        elif name == "heart":
            yrs = int(clamp((t - b0 - 0.4) / 3.0) * 3.0)
            for k in range(100):
                gx, gy = k % 10, k // 10
                x = ix - 135 + gx * 30
                y = iy - 135 + gy * 30
                hot = (k == (37 + 29 * yrs) % 100) and t > b0 + 0.5
                cc = mix((0.85, 0.25, 0.40), (1.0, 0.95, 0.95), 1.0 if hot else 0.0)
                cv.rect(x - 12, y - 9, 24, 18, cc, alpha=a * (0.45 if not hot else 0.95), radius=5, glow=0.8 if hot else 0)
        else:
            for i, (x0, y0) in enumerate(self.neurons):
                px, py = ix + x0 * rr * 0.85, iy + y0 * rr * 0.85
                for j, (x1, y1) in enumerate(self.neurons[i + 1:i + 4]):
                    qx, qy = ix + x1 * rr * 0.85, iy + y1 * rr * 0.85
                    cv.line([(px, py), (qx, qy)], col, width=1.6, alpha=0.45 * a)
                    f = (t * 1.4 + i * 0.37 + j * 0.21) % 1.0
                    cv.circle(lerp(px, qx, f), lerp(py, qy, f), 3, L.WHITE, alpha=0.8 * a, glow=0.8)
                cv.circle(px, py, 7, col, alpha=a, glow=0.8)
        b.restore()
        cv.circle(ix, iy, rr, col, alpha=a, fill=False, width=4, glow=0.6)
        sub = {"fat": "fat cells · 10% swapped each year", "heart": "heart muscle cells · 1 in 100 a year, at 25",
               "cortex": "cortex neurons · formed before birth"}[name]
        htext(cv, sub, ix, iy + r + 40, 20, color=(0.8, 0.86, 0.98), alpha=a, font=L.MONO_XB, shadow=0.7)

    # ================================================================== the lens
    def s_lens(self, cv, t):
        c = self.c
        s0, s1 = c["sc_lens"]
        a = smooth(prog(t, s0 - 0.1, s0 + 0.4))
        side = smooth(prog(t, c["made"] - 0.35, c["made"] + 0.25))          # front view -> cross-section
        rays = smooth(prog(t, c["L12"] - 0.35, c["L12"] + 0.25))            # cross-section -> eye with light
        if side < 1:
            push = ease_in_out(prog(t, s0, c["made"]))
            s_eye = lerp(1.25, 1.75, push)
            xr = smooth(prog(t, c["lens"] - 0.3, c["lens"] + 0.4))
            with cv.group((1 - side) * a) if (side > 0 or a < 1) else _null():
                self._eye(cv, t, 540, 960, s_eye, reflect=0.0, pupil=0.36)
                # x-ray: the lens shows through the pupil, growth shells like tree rings
                if xr > 0:
                    ix, iy = 540 + (self.eye.cx - EW / 2) * s_eye, 960 + (self.eye.cy - EH / 2) * s_eye
                    R = self.eye.R * s_eye * 0.86
                    cv.circle(ix, iy, R * 1.02, (0.02, 0.03, 0.06), alpha=0.75 * xr)
                    for k in range(12, 0, -1):
                        f = k / 12
                        cc = mix(L.CYAN, C14C, smooth(clamp((1 - f - 0.5) / 0.4)))
                        cv.circle(ix, iy, R * f, cc, alpha=xr * (0.25 + 0.5 * (1 - f)), fill=False, width=2,
                                  glow=0.3 * (1 - f))
                    cv.circle(ix, iy, R * 0.16, C14C, alpha=0.75 * xr, glow=0.9)
                    for ang in (-math.pi / 2, math.pi / 6, 5 * math.pi / 6):
                        cv.line([(ix, iy), (ix + math.cos(ang) * R * 0.15, iy + math.sin(ang) * R * 0.15)],
                                (1.0, 0.95, 0.85), width=3, alpha=xr)
                    htext(cv, "YOUR LENS", 540, 470, 46, color=L.WHITE, alpha=xr * a, glow=0.15)
                    htext(cv, "it grows in layers, like tree rings", 540, 528, 24, color=(0.8, 0.86, 0.98),
                          alpha=xr * a, font=L.MONO_XB)
        if side > 0 and rays < 1:
            with cv.group(side * (1 - rays) * a) if (side < 1 or rays > 0 or a < 1) else _null():
                lx, ly, lw, lh = 430.0, 930.0, 190.0, 420.0
                rev = ease_out_cubic(prog(t, c["made"] - 0.3, c["before"] + 0.4))
                bio.draw_lens(cv, lx, ly, lw, lh, t, alpha=1.0, shells=12, reveal=1.0,
                              core_glow=smooth(prog(t, c["before"] - 0.2, c["before"] + 0.3)))
                labs = [("NEWEST LAYER", 0.97, L.CYAN, c["made"], 700),
                        ("CHILDHOOD", 0.60, (0.75, 0.80, 0.85), c["made"] + 0.3, 845),
                        ("BEFORE BIRTH", 0.12, C14C, c["before"], 960)]
                for i, (txt, f, col, tk, ty_) in enumerate(labs):
                    la = smooth(prog(t, tk - 0.1, tk + 0.3))
                    xx, yy = lx + lw * f * 0.95, ly - lh * 0.30 * f
                    uline(cv, [(xx, yy), (690, ty_)], col, width=2, alpha=la)
                    htext(cv, txt, 700, ty_, 26 if i < 2 else 34, color=col, alpha=la, font=L.MONO_XB, anchor="left",
                          glow=0.4 if i == 2 else 0)
                sa = smooth(prog(t, c["born"], c["born"] + 0.4))
                htext(cv, "THE CORE", 540, 372, 54, color=C14C, alpha=smooth(prog(t, c["before"] - 0.2, c["before"] + 0.3)),
                      glow=0.4)
                htext(cv, "formed in the first weeks in the womb", 540, 438, 24, color=L.WHITE, alpha=sa, font=L.MONO_XB)
                htext(cv, "and never replaced", 540, 474, 24, color=L.WHITE, alpha=sa, font=L.MONO_XB)
                _ = rev
        if rays > 0:
            with cv.group(rays * a) if (rays < 1 or a < 1) else _null():
                ex, ey, er = 700.0, 930.0, 300.0
                geo = eye_section(cv, ex, ey, er, t, alpha=1.0, fibers=0.6)
                lx, ly = geo["lens"]
                bio.draw_lens(cv, lx, ly, er * 0.13, er * 0.30, t, alpha=1.0, shells=8, core_glow=1.0)
                # the phone you're holding
                px, py = 150.0, 930.0
                cv.rect(px - 52, py - 105, 104, 210, (0.85, 0.9, 1.0), alpha=0.95, fill=False, width=4, radius=16, glow=0.5)
                cv.rect(px - 44, py - 95, 88, 190, (0.25, 0.45, 0.70), alpha=0.6, radius=10, glow=0.6)
                htext(cv, "YOU'RE", px, py - 20, 15, color=L.WHITE, alpha=rays * a, font=L.DISPLAY)
                htext(cv, "READING", px, py, 15, color=L.WHITE, alpha=rays * a, font=L.DISPLAY)
                htext(cv, "THIS", px, py + 20, 15, color=C14C, alpha=rays * a, font=L.DISPLAY)
                fx, fy = geo["fovea"]
                pp = ease_in_out(prog(t, c["L12"] - 0.1, c["through"] + 0.4))
                for k in range(7):
                    sy = py - 80 + k * 26.6
                    mid = (lx, ly + (sy - py) * 0.25)
                    tgt = (fx, fy - (sy - py) * 0.18)
                    p1 = (lerp(px + 50, mid[0], min(1, pp * 2)), lerp(sy, mid[1], min(1, pp * 2)))
                    cv.line([(px + 50, sy), p1], (1.0, 0.95, 0.85), width=2.5, alpha=0.75, glow=0.6)
                    if pp > 0.5:
                        q = (pp - 0.5) * 2
                        cv.line([mid, (lerp(mid[0], tgt[0], q), lerp(mid[1], tgt[1], q))], (1.0, 0.85, 0.6), width=2.5,
                                alpha=0.75, glow=0.6)
                ha = smooth(prog(t, c["through"] - 0.1, c["through"] + 0.3))
                cv.circle(lx - er * 0.01, ly, er * 0.05, C14C, alpha=ha * 0.9, glow=1.0)
                htext(cv, "THROUGH THE CORE", lx, ly - er * 0.48, 30, color=C14C, alpha=ha * a, font=L.MONO_XB, glow=0.4)
                na = smooth(prog(t, c["now"] - 0.1, c["now"] + 0.3))
                htext(cv, "RIGHT NOW", 540, 420, 64, color=L.WHITE, alpha=na * a, glow=0.15)

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


class _null:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def make_episode(timeline_path, **opts):
    return Episode(timeline_path, **opts)
