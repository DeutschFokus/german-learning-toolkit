"""EP003 — He Cut Down the Oldest Tree on Earth.

Narrated by the creator (no AI voice in any deliverable). Until his take
exists, animation timing comes from a scratch read (build/timeline_scratch.json);
`build.py human take.wav` re-times everything to the real voice.

guide=True renders the record-along version: a teleprompter band at the
top (current line, next line, count-in dot) on top of captions.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))

import cv2  # noqa: E402

cv2.setNumThreads(1)

from engine.captions import Captions  # noqa: E402
from engine.gfx import (H, L, W, Canvas, Starfield, background, clamp, ease_in_cubic, ease_in_out,  # noqa: E402
                        ease_out_back, ease_out_cubic, ease_out_expo, lerp, mix, prog, smooth, text_width, window)
from engine.nature import Bristlecone, Ridges, RingSection, moon, pyramid, stamp  # noqa: E402
from engine.postfx import Post  # noqa: E402
from engine.timeline import Timeline  # noqa: E402

HOOK_TREE_SEED, HOOK_TREE_H = 5, 600.0
MOON = (720.0, 860.0, 170.0)
CUT_Y = -46.0                     # local y of the cut (above the base)
ACCENTS = {"L04": L.MAGENTA, "L05": L.AMBER, "L07": L.AMBER, "L08": L.CYAN, "L09": L.MINT, "L10": L.AMBER,
           "L11": L.MAGENTA, "L14": L.AMBER}
HARD_CUTS = {"cut"}
X_IN = {}
X_OUT = {}


class Episode:
    def __init__(self, timeline_path, captions=True, grain=0.007, guide=False):
        self.T = Timeline(timeline_path)
        self.fps = self.T.fps
        self.duration = self.T.duration
        self.post = Post(grain=grain)
        self.stars = Starfield(seed=21)
        self.caps = Captions(self.T, accent_by_line=ACCENTS) if captions else None
        self.guide = guide
        self.ridges = Ridges(seed=5, peak_y=1205.0)
        self.tree = Bristlecone(seed=HOOK_TREE_SEED, height=HOOK_TREE_H)
        self.big = Bristlecone(seed=8, height=1180.0, alive_limbs=(1,), n_limbs=6)
        self.meth = Bristlecone(seed=13, height=560.0, alive_limbs=(0, 1, 3), n_limbs=7)
        self.grove = [(Bristlecone(seed=30 + k, height=h), x) for k, (h, x) in
                      enumerate(((300, 150), (380, 340), (330, 540), (420, 740), (300, 930)))]
        self.seedling = Bristlecone(seed=44, height=240.0, alive_limbs=(0, 1, 2, 3), n_limbs=4, dead_spikes=0)
        self.rings = RingSection(size=980, seed=9)
        st = self.T.scene_starts()
        self.scenes = [(sid, s0, st[i + 1][1] if i + 1 < len(st) else self.duration)
                       for i, (sid, s0) in enumerate(st)]
        self.c = self._cues()

    def _cues(self):
        T = self.T
        w = lambda l, k: T.word(l, k).start  # noqa: E731
        c = {"sc_" + sid: (s0, s1) for sid, s0, s1 in self.scenes}
        c.update({
            "L02": T.line("L02").start, "vandal": w("L02", "vandal."), "L03": T.line("L03").start,
            "scientist": w("L03", "scientist,"), "count": w("L03", "count"), "rings3": w("L03", "rings."),
            "L04": T.line("L04").start, "permission": w("L04", "permission,"), "down": w("L04", "down."),
            "L04end": T.line("L04").end,
            "L05": T.line("L05").start, "n4844": w("L05", "4,844"), "ringsword": w("L05", "rings."),
            "L05end": T.line("L05").end,
            "L06": T.line("L06").start, "most": w("L06", "most"), "die": w("L06", "die."),
            "L07": T.line("L07").start, "single": w("L07", "single"), "strip": w("L07", "strip"),
            "L08": T.line("L08").start, "reliable": w("L08", "reliable,"), "correct": w("L08", "correct"),
            "carbon": w("L08", "carbon"), "L08end": T.line("L08").end,
            "L09": T.line("L09").start, "meth": w("L09", "Methuselah,"), "still": w("L09", "still"),
            "L10": T.line("L10").start, "seedling": w("L10", "seedling"), "before": w("L10", "before"),
            "pyramid": w("L10", "Pyramid"), "built": w("L10", "built."), "L10end": T.line("L10").end,
            "L11": T.line("L11").start, "secret": w("L11", "secret."), "L12": T.line("L12").start,
            "wont": w("L12", "won't"), "L13": T.line("L13").start, "blame": w("L13", "blame"),
            "L14": T.line("L14").start, "last": w("L14", "last"), "L14end": T.line("L14").end,
        })
        return c

    # ------------------------------------------------------------------ frame
    def frame(self, i):
        t = i / self.fps
        cv = Canvas()
        self.draw(cv, t)
        return self.post.finish(cv, i)

    def draw(self, cv, t):
        background(cv, t, haze=(0.62, 0.45), haze_color=(0.10, 0.20, 0.50), haze_amt=0.85)
        self.stars.draw(cv, t, alpha=0.9, dust_alpha=0.6)
        n = len(self.scenes)
        for k, (sid, s0, s1) in enumerate(self.scenes):
            first, last = k == 0, k == n - 1
            cut_in = sid in HARD_CUTS
            cut_out = (not last) and self.scenes[k + 1][0] in HARD_CUTS
            Xi = 0.0 if (first or cut_in) else X_IN.get(sid, 0.18)
            Xo = 0.0 if (last or cut_out) else X_OUT.get(sid, 0.18)
            if not (s0 - Xi <= t < s1 + Xo):
                continue
            a, sc, ty = 1.0, 1.0, 0.0
            if Xi and t < s0 + Xi:
                p = prog(t, s0 - Xi, s0 + Xi)
                a, sc, ty = smooth(p), 0.97 + 0.03 * ease_out_cubic(p), 80 * (1 - ease_out_cubic(p))
            if Xo and t > s1 - Xo:
                p = prog(t, s1 - Xo, s1 + Xo)
                a, sc, ty = 1 - smooth(p), 1 + 0.05 * ease_in_cubic(p), -80 * ease_in_cubic(p)
            if a <= 0.003:
                continue
            fn = getattr(self, "s_" + sid)
            if a >= 0.999 and sc == 1.0 and ty == 0.0:
                fn(cv, t)
            else:
                with cv.group(a), cv.transform(ty=ty, s=sc):
                    fn(cv, t)
        if self.caps:
            self.caps.draw(cv, t)
        if self.guide:
            self._teleprompter(cv, t)

    # ================================================================== shared world
    def _world(self, cv, t, tree_alpha=1.0, fall=None, cut_glow=0.0, moon_a=1.0, strip=0.0):
        moon(cv, *MOON, alpha=moon_a)
        self.ridges.draw(cv)
        bx, by = 540.0, self.ridges.y_at(540.0) + 16
        sway = 0.25 * math.sin(2 * math.pi * t / 7.5)          # 7.5 s period: loops cleanly in 60 s
        if fall is None:
            self.tree.draw(cv, bx, by, 1.0, alpha=tree_alpha, t=t, sway=sway, strip=strip)
        else:
            self.tree.draw(cv, bx, by, 1.0, alpha=tree_alpha, t=t, cut=(CUT_Y, fall))
        if cut_glow > 0:
            yy = by + CUT_Y
            wdt = self.tree.trunk_w[0][0] * 0.55
            cv.line([(bx - wdt, yy), (bx + wdt, yy)], (1.0, 0.35, 0.25), width=4, alpha=cut_glow, glow=1.0)
            for k in range(7):
                f = (t * 1.3 + k / 7) % 1.0
                cv.circle(bx + wdt * (k / 3.5 - 1), yy - 30 * f, 2.5, L.AMBER, alpha=cut_glow * (1 - f), glow=0.9)
        return bx, by

    def _headline(self, cv, t, alpha=1.0, offs=(0, 0, 0, 0)):
        if alpha <= 0.003:
            return
        cv.text("1964", W / 2 + offs[0], 300, 150, color=L.AMBER, alpha=alpha, glow=0.55, shadow=0.6)
        cv.text("A STUDENT CUT DOWN", W / 2 + offs[1], 432, 64, color=L.WHITE, alpha=alpha, shadow=0.7)
        cv.text("THE OLDEST KNOWN", W / 2 + offs[2], 508, 64, color=L.WHITE, alpha=alpha, shadow=0.7)
        cv.text("TREE ON EARTH", W / 2 + offs[3], 584, 64, color=L.WHITE, alpha=alpha, shadow=0.7)

    # ================================================================== scenes
    def s_hook(self, cv, t):
        self._world(cv, t, cut_glow=0.9)
        self._headline(cv, t)

    def s_cut(self, cv, t):
        c = self.c
        s0, s1 = c["sc_cut"]
        # the headline steps away
        ex = ease_in_cubic(prog(t, s0 - 0.05, s0 + 0.45))
        self._headline(cv, t, alpha=1 - ex, offs=(0, -60 * ex, 60 * ex, -60 * ex))
        fall_p = prog(t, c["down"] + 0.15, c["down"] + 1.45)
        fall = -1.45 * ease_in_cubic(fall_p) if fall_p > 0 else None
        tree_a = 1.0 - 0.0 * fall_p
        shake = window(t, c["down"] + 1.3, c["down"] + 1.5, 0.02, 0.5) * 7
        with cv.transform(tx=shake * math.sin(t * 61), ty=shake * math.cos(t * 47)):
            bx, by = self._world(cv, t, tree_alpha=tree_a, fall=fall if fall_p > 0 else None,
                                 cut_glow=0.9 * (1 - smooth(prog(t, c["down"], c["down"] + 0.3))) + 0.0)
            if fall_p >= 1:
                # dust settling
                k = prog(t, c["down"] + 1.45, c["down"] + 3.0)
                for j in range(14):
                    ang = math.pi + j / 13 * math.pi
                    cv.circle(bx + math.cos(ang) * 260 * ease_out_cubic(k), by - 10 + math.sin(ang) * 60 * k,
                              14 * (1 - k) + 2, (0.6, 0.65, 0.8), alpha=0.25 * (1 - k))
        # "NOT A VANDAL"
        va = window(t, c["L02"] - 0.05, c["scientist"] - 0.2, 0.2, 0.3)
        if va > 0:
            cv.text("VANDAL", W / 2, 400, 120, color=L.WHITE, alpha=va, shadow=0.6)
            sp = ease_out_cubic(prog(t, c["vandal"] + 0.15, c["vandal"] + 0.5))
            tw = text_width(cv.b, "VANDAL", 120, L.DISPLAY)
            cv.line([(W / 2 - tw / 2 - 20, 400), (W / 2 - tw / 2 - 20 + (tw + 40) * sp, 400)], L.MAGENTA, width=10,
                    alpha=va, glow=0.6)
        # the scientist's file card
        fa = smooth(prog(t, c["scientist"] - 0.15, c["scientist"] + 0.3)) * (1 - smooth(prog(t, c["permission"] - 0.35,
                                                                                              c["permission"] - 0.05)))
        if fa > 0:
            x0, y0, w0, h0 = 110.0, 270.0, 860.0, 250.0
            cv.rect(x0, y0, w0, h0, (0.04, 0.07, 0.14), alpha=0.92 * fa, radius=18)
            cv.rect(x0, y0, w0, h0, L.CYAN, alpha=0.6 * fa, fill=False, width=2, radius=18)
            cv.text("FIELD NOTES · 1964", x0 + 30, y0 + 40, 22, font=L.MONO, anchor="left", color=L.DIM, alpha=fa,
                    tracking=0.2)
            cv.text("DONALD CURREY", x0 + 30, y0 + 96, 52, anchor="left", color=L.WHITE, alpha=fa)
            cv.text("graduate student · studying Ice Age glaciers", x0 + 30, y0 + 152, 26, font=L.UI_MED,
                    anchor="left", color=L.CYAN, alpha=fa)
            cv.text("WHEELER PEAK, NEVADA · ~3,300 m", x0 + 30, y0 + 200, 22, font=L.MONO_XB, anchor="left",
                    color=L.DIM, alpha=fa, tracking=0.1)
        # the core sample
        ca = window(t, c["count"] - 0.1, c["L04"] + 0.2, 0.2, 0.3)
        if ca > 0:
            bx, by = 540.0, self.ridges.y_at(540.0) + 16
            yy = by - 150
            push = ease_out_cubic(prog(t, c["count"], c["count"] + 0.6))
            x_tip = lerp(980, 560, push)
            cv.line([(x_tip, yy), (1000, yy)], (0.85, 0.88, 0.95), width=8, alpha=ca)
            cv.line([(1000, yy - 26), (1000, yy + 26)], (0.85, 0.88, 0.95), width=10, alpha=ca)
            pull = ease_out_cubic(prog(t, c["rings3"], c["rings3"] + 0.6))
            if pull > 0:
                cx0 = lerp(560, 620, pull)
                cy0 = lerp(yy, 640, pull)
                cv.rect(cx0, cy0 - 14, 330, 28, (0.75, 0.58, 0.36), alpha=ca, radius=8)
                for j in range(40):
                    xx = cx0 + 8 + j * 8 + (3 if j % 3 == 0 else 0)
                    cv.line([(xx, cy0 - 13), (xx, cy0 + 13)], (0.40, 0.24, 0.12), width=1.5, alpha=ca * 0.8)
                cv.text("CORE SAMPLE", cx0 + 165, cy0 + 44, 22, font=L.MONO_XB, color=L.WHITE, alpha=ca * pull,
                        tracking=0.15, shadow=0.8)
        # permission stamp
        pa = window(t, c["permission"] - 0.05, c["down"] + 0.9, 0.12, 0.4)
        if pa > 0:
            pop = 1 - ease_out_back(prog(t, c["permission"] - 0.05, c["permission"] + 0.35))
            stamp(cv, "APPROVED", 540, 420, size=70, angle=-0.10, color=L.MINT, alpha=pa, pop=pop,
                  sub="U.S. FOREST SERVICE PERMISSION")
        after = smooth(prog(t, c["down"] + 1.6, c["down"] + 2.0))
        if after > 0:
            cv.text("AUGUST 1964", W / 2, 360, 40, font=L.MONO_XB, color=L.DIM, alpha=after, tracking=0.25)
            cv.text("ONLY THE STUMP REMAINS", W / 2, 430, 54, color=L.WHITE, alpha=after, shadow=0.6)

    def s_count(self, cv, t):
        c = self.c
        s0, s1 = c["sc_count"]
        a = smooth(prog(t, s0 - 0.1, s0 + 0.4))
        zoom = lerp(0.82, 0.95, ease_out_cubic(prog(t, s0, s1)))
        cx_, cy_ = 540.0, 930.0
        self.rings.draw(cv, cx_, cy_, zoom, alpha=a)
        # scan from bark to pith while the count rolls
        sp = ease_in_out(prog(t, c["n4844"] - 0.2, c["n4844"] + 1.8))
        px, py = self.rings.to_screen(cx_, cy_, zoom, *self.rings.pith)
        ang = math.radians(-35)
        R = self.rings.R * zoom
        ex_, ey_ = px + math.cos(ang) * R * 1.1, py + math.sin(ang) * R * 1.1
        if sp > 0:
            hx, hy = lerp(ex_, px, sp), lerp(ey_, py, sp)
            cv.line([(ex_, ey_), (hx, hy)], L.WHITE, width=3, alpha=a * 0.9, glow=0.8)
            cv.circle(hx, hy, 9, L.AMBER, alpha=a, glow=1.0)
            rr = math.hypot(hx - px, hy - py)
            cv.circle(px, py, rr, L.AMBER, alpha=a * 0.35, fill=False, width=2, glow=0.6)
        n = int(4844 * ease_out_cubic(sp))
        ta = smooth(prog(t, c["n4844"] - 0.3, c["n4844"]))
        cv.text(f"{n:,}", W / 2, 300, 150, color=L.AMBER, alpha=ta * a, glow=0.55, shadow=0.7)
        cv.text("RINGS", W / 2, 410, 40, font=L.MONO_XB, color=L.WHITE, alpha=ta * a, tracking=0.5, shadow=0.7)
        fa = smooth(prog(t, c["L05end"], c["L05end"] + 0.4))
        cv.text("later estimate ≈ 4,900 years: in harsh years, no ring forms", W / 2, 1450, 22, font=L.MONO,
                color=L.DIM, alpha=fa * a)

    def s_strip(self, cv, t):
        c = self.c
        s0, s1 = c["sc_strip"]
        a = smooth(prog(t, s0 - 0.1, s0 + 0.4))
        dead = smooth(prog(t, c["most"] - 0.1, c["die"] + 0.3))
        st = ease_in_out(prog(t, c["single"] - 0.1, c["strip"] + 0.9))
        moon(cv, 850, 470, 110, alpha=0.6 * a)
        bx, by = 500.0, 1660.0
        bleach = dead * (1 - 0.5 * st)

        def above_ground(ctx):
            ctx.rectangle(0, 0, W, 1530)

        with cv.clip(above_ground):
            self.tree.draw(cv, bx, by, 1.9, alpha=a, t=t, strip=st, alive_glow=0.6 * st, foliage=1.0,
                           rim=mix((0.62, 0.70, 0.82), (0.95, 0.97, 1.0), bleach),
                           body=mix((0.075, 0.09, 0.14), (0.26, 0.29, 0.36), bleach))
        cv.line([(0, 1530), (W, 1530)], (0.5, 0.6, 0.85), width=2, alpha=0.5 * a)
        la = smooth(prog(t, c["die"] - 0.1, c["die"] + 0.3)) * (1 - 0.6 * st)
        cv.text("DEAD WOOD", 120, 330, 40, font=L.MONO_XB, anchor="left", color=(0.85, 0.9, 1.0), alpha=la * a,
                tracking=0.2, shadow=0.8)
        cv.text("bleached, but still standing", 120, 378, 24, font=L.MONO, anchor="left", color=L.DIM, alpha=la * a)
        sa = smooth(prog(t, c["strip"] + 0.2, c["strip"] + 0.6))
        cv.text("LIVING BARK", 620, 1150, 48, anchor="left", color=L.AMBER, alpha=sa * a, glow=0.4, shadow=0.8)
        cv.text("one strip ≈ 48 cm wide", 620, 1210, 28, font=L.MONO_XB, anchor="left", color=L.WHITE,
                alpha=sa * a, shadow=0.8)
        cv.text("on this tree, 1964", 620, 1250, 22, font=L.MONO, anchor="left", color=L.DIM, alpha=sa * a)

    def s_carbon(self, cv, t):
        c = self.c
        s0, s1 = c["sc_carbon"]
        a = smooth(prog(t, s0 - 0.1, s0 + 0.4))
        x0, y0, w0, h0 = 150.0, 520.0, 780.0, 640.0
        cv.line([(x0, y0 + h0), (x0 + w0, y0 + h0)], L.DIM, width=2.5, alpha=a)
        cv.line([(x0, y0 + h0), (x0, y0)], L.DIM, width=2.5, alpha=a)
        cv.text("TRUE AGE  (counted rings) →", x0 + w0, y0 + h0 + 40, 22, font=L.MONO_XB, anchor="right",
                color=L.WHITE, alpha=a, tracking=0.06)
        cv.text("CARBON-14 AGE ↑", x0, y0 - 30, 22, font=L.MONO_XB, anchor="left", color=L.WHITE, alpha=a,
                tracking=0.06)
        da = smooth(prog(t, s0 + 0.2, s0 + 0.7))
        cv.line([(x0, y0 + h0), (x0 + w0, y0)], L.DIM, width=2, alpha=a * da, dash=[10, 10])
        cv.text("if carbon dating were exact", x0 + w0 * 0.53, y0 + h0 * 0.36, 20, font=L.MONO, color=L.DIM,
                alpha=a * da)
        # radiocarbon ages drift younger than true ages for older wood (schematic, with wiggles)
        cp = ease_in_out(prog(t, c["reliable"] - 0.2, c["correct"] + 0.4))
        pts = []
        N = 120
        for i in range(int(N * cp) + 1):
            u = i / N
            dev = 0.17 * u ** 1.5 + 0.012 * math.sin(u * 37) + 0.008 * math.sin(u * 71 + 1)
            pts.append((x0 + w0 * u, y0 + h0 - h0 * (u - dev)))
        if len(pts) > 1:
            cv.line(pts, L.AMBER, width=4, alpha=a, glow=0.7)
            hx, hy = pts[-1]
            cv.circle(hx, hy, 7, L.AMBER, alpha=a, glow=1.0)
        aa = smooth(prog(t, c["correct"], c["correct"] + 0.4))
        for u in (0.55, 0.75, 0.92):
            dev = 0.17 * u ** 1.5 + 0.012 * math.sin(u * 37) + 0.008 * math.sin(u * 71 + 1)
            xx = x0 + w0 * u
            yt, yc = y0 + h0 - h0 * u, y0 + h0 - h0 * (u - dev)
            k = ease_out_cubic(aa)
            cv.line([(xx, yc), (xx, lerp(yc, yt + 12, k))], L.CYAN, width=5, alpha=a * aa, glow=0.7)
            cv.poly([(xx, yt), (xx - 12, yt + 20), (xx + 12, yt + 20)], L.CYAN, alpha=a * aa * k)
        cv.text("CORRECTED", x0 + w0 * 0.80, y0 + h0 * 0.56, 34, color=L.CYAN, alpha=a * aa, glow=0.4)
        ta = smooth(prog(t, s0, s0 + 0.4))
        cv.text("THE TREE-RING CALENDAR", W / 2, 300, 58, color=L.WHITE, alpha=ta, glow=0.15)
        cv.text("bristlecone rings · first calibration curve: Suess, 1967", W / 2, 372, 22, font=L.MONO,
                color=L.DIM, alpha=ta)
        oa = smooth(prog(t, c["carbon"], c["carbon"] + 0.4))
        cv.text("carbon dates had been off by centuries", W / 2, 1280, 26, font=L.MONO_XB, color=L.AMBER,
                alpha=oa * a, tracking=0.04)

    def s_methuselah(self, cv, t):
        c = self.c
        s0, s1 = c["sc_methuselah"]
        a = smooth(prog(t, s0 - 0.1, s0 + 0.4))
        two = smooth(prog(t, c["L10"] - 0.25, c["L10"] + 0.2))      # switch to the time-lapse
        # part 1: Methuselah, alive today
        if two < 1:
            a1 = a * (1 - two)
            moon(cv, 760, 700, 130, alpha=0.8 * a1)
            self.ridges.draw(cv, alpha=a1)
            bx, by = 540.0, self.ridges.y_at(540.0) + 14
            self.meth.draw(cv, bx, by, 1.0, alpha=a1, t=t, alive_glow=0.4 * smooth(prog(t, c["still"], c["still"] + 0.4)))
            na = smooth(prog(t, c["meth"] - 0.1, c["meth"] + 0.3))
            cv.text("METHUSELAH", W / 2, 320, 96, color=L.WHITE, alpha=na * a1, glow=0.25, shadow=0.6)
            cv.text("WHITE MOUNTAINS, CALIFORNIA", W / 2, 410, 26, font=L.MONO_XB, color=L.DIM, alpha=na * a1,
                    tracking=0.2)
            sa = smooth(prog(t, c["still"] - 0.05, c["still"] + 0.3))
            pop = 1 - ease_out_back(prog(t, c["still"] - 0.05, c["still"] + 0.4))
            with cv.transform(s=1 + 0.2 * pop, cx=540, cy=495):
                cv.text("● STILL ALIVE", W / 2, 495, 44, color=L.MINT, alpha=sa * a1, glow=0.5)
        # part 2: seedling vs. pyramid time-lapse
        if two > 0:
            a2 = a * two
            ground = 1120.0
            cv.rect(0, ground, W, H - ground, (0.03, 0.04, 0.08), alpha=a2)
            cv.line([(0, ground), (W, ground)], (0.5, 0.6, 0.85), width=2, alpha=a2 * 0.6)
            yp = prog(t, c["seedling"] - 0.2, c["built"] + 0.3)
            year = int(lerp(2833, 2560, ease_in_out(yp)))
            cv.text(f"{year} BC", W / 2, 320, 110, font=L.DISPLAY, color=L.AMBER, alpha=a2, glow=0.5)
            cv.text("YEAR", W / 2, 410, 26, font=L.MONO_XB, color=L.DIM, alpha=a2, tracking=0.5)
            grow = ease_out_cubic(prog(t, c["seedling"] - 0.2, c["built"] + 0.6))
            sx = 290.0
            self.seedling.draw(cv, sx, ground + 4, lerp(0.35, 1.45, grow), alpha=a2, t=t, foliage=1.0,
                               alive_glow=0.3)
            cv.text("METHUSELAH", sx, ground + 60, 26, font=L.MONO_XB, color=L.MINT, alpha=a2, tracking=0.12)
            cv.text("2833 BC", sx, ground + 96, 22, font=L.MONO, color=L.DIM, alpha=a2)
            build = ease_in_out(prog(t, c["before"], c["built"] + 0.5))
            px = 730.0
            pyramid(cv, px, ground, 560, build=build, alpha=a2)
            pa = smooth(prog(t, c["pyramid"] - 0.1, c["pyramid"] + 0.3))
            cv.text("GREAT PYRAMID", px, ground + 60, 26, font=L.MONO_XB, color=(0.95, 0.78, 0.45), alpha=a2 * pa,
                    tracking=0.12)
            cv.text("c. 2560 BC", px, ground + 96, 22, font=L.MONO, color=L.DIM, alpha=a2 * pa)
            la = smooth(prog(t, c["L10end"] - 0.1, c["L10end"] + 0.3))
            cv.text("≈ 270 YEARS OLDER", W / 2, 520, 44, color=L.WHITE, alpha=a2 * la, glow=0.2)

    def s_secret(self, cv, t):
        c = self.c
        s0, s1 = c["sc_secret"]
        a = smooth(prog(t, s0 - 0.1, s0 + 0.4))
        self.ridges.draw(cv, alpha=a)
        trees = []
        for k, (tr, x) in enumerate(self.grove):
            by = self.ridges.y_at(x) + 12
            tr.draw(cv, x, by, 1.0, alpha=a, t=t, sway=0.2 * math.sin(2 * math.pi * t / 7.5 + k))
            trees.append((x, by - tr.h * 0.62))
        # a reticle hops between candidates: which one?
        hop = 0.42
        i = int(max(0.0, t - s0) / hop) % len(trees)
        u = (max(0.0, t - s0) % hop) / hop
        prv = trees[i - 1]
        cur = trees[i]
        k = ease_in_out(min(1.0, u / 0.35))
        gx, gy = lerp(prv[0], cur[0], k), lerp(prv[1], cur[1], k)
        ra = smooth(prog(t, s0, s0 + 0.4)) * (1 - smooth(prog(t, c["secret"], c["secret"] + 0.3)))
        cv.circle(gx, gy, 46, L.CYAN, alpha=a * ra, fill=False, width=3, glow=0.7)
        cv.text("?", gx, gy, 54, color=L.CYAN, alpha=a * ra, glow=0.5)
        for (x, y) in trees:
            cv.text("?", x, y - 90, 40, color=L.WHITE, alpha=a * 0.55 * smooth(prog(t, c["secret"], c["secret"] + 0.4)))
        sa = smooth(prog(t, c["secret"] - 0.05, c["secret"] + 0.1))
        pop = 1 - ease_out_back(prog(t, c["secret"] - 0.05, c["secret"] + 0.35))
        stamp(cv, "UNDISCLOSED", 540, 400, size=72, angle=-0.10, color=L.MAGENTA, alpha=sa * a, pop=pop,
              sub="EXACT LOCATION")
        wa = smooth(prog(t, c["wont"] - 0.1, c["wont"] + 0.3))
        if wa > 0:
            cv.rect(200, 560, 680, 64, (0.03, 0.05, 0.10), alpha=0.92 * wa * a, radius=12)
            cv.text("INYO NATIONAL FOREST ·", 230, 592, 22, font=L.MONO_XB, anchor="left", color=L.WHITE,
                    alpha=wa * a, tracking=0.08)
            cv.rect(600, 574, 250, 36, (0.0, 0.0, 0.0), alpha=wa * a, radius=4)
            cv.text("REDACTED", 725, 592, 18, font=L.MONO_XB, color=(0.5, 0.5, 0.55), alpha=wa * a, tracking=0.25)
            cv.text("official reason: to protect it from vandalism", W / 2, 668, 22, font=L.MONO, color=L.DIM,
                    alpha=wa * a)

    def s_outro(self, cv, t):
        c = self.c
        s0, s1 = c["sc_outro"]
        a = smooth(prog(t, s0 - 0.1, s0 + 0.5))
        with cv.group(a) if a < 0.999 else _null():
            self._world(cv, t, cut_glow=0.9 * smooth(prog(t, c["L14"], c["L14"] + 0.6)))
        back = prog(t, c["last"] - 0.1, c["last"] + 1.6)
        if back > 0:
            ks = [ease_out_expo(prog(back, 0.12 * k, 0.5 + 0.12 * k)) for k in range(4)]
            al = [smooth(prog(back, 0.12 * k, 0.3 + 0.12 * k)) for k in range(4)]
            # the headline returns line by line; at the end it is exactly frame 0
            self._headline_parts(cv, al, [-120 * (1 - k) for k in ks])

    def _headline_parts(self, cv, alphas, offs):
        rows = [("1964", 300, 150, L.AMBER, 0.55), ("A STUDENT CUT DOWN", 432, 64, L.WHITE, 0),
                ("THE OLDEST KNOWN", 508, 64, L.WHITE, 0), ("TREE ON EARTH", 584, 64, L.WHITE, 0)]
        for (txt, y, size, col, gl), a_, o in zip(rows, alphas, offs):
            cv.text(txt, W / 2 + o, y, size, color=col, alpha=a_, glow=gl, shadow=0.6 if size > 100 else 0.7)

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
