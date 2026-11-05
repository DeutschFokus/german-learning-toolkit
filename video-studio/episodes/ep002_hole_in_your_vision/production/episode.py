"""EP002 — There's a Hole in Your Vision Right Now.

The viewer finds their own blind spot, then discovers four edits their brain
makes every second: fill-in (space), blink deletion (darkness), blur cuts
(motion) and backdating (time) — ending on the stopped-clock illusion.
Every animation is anchored to narration cues from the timeline. The test
card at the start is also the last frame, so the loop gives a second try.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))

import cv2  # noqa: E402

cv2.setNumThreads(1)

from engine.anatomy import eye_front, eye_section, iris_glyph  # noqa: E402
from engine.captions import Captions  # noqa: E402
from engine.gfx import (H, L, W, Canvas, Starfield, background, clamp, ease_in_cubic, ease_in_out,  # noqa: E402
                        ease_out_back, ease_out_cubic, ease_out_expo, lerp, mix, prog, smooth, text_width, window)
from engine.postfx import Post  # noqa: E402
from engine.timeline import Timeline  # noqa: E402
from engine.ui import analog_clock, chip, editor_timeline, film_strip, gaze_reticle  # noqa: E402

# ---------------------------------------------------------------- layout (test card = first and last frame)
CROSS = (150.0, 760.0)
DOT = (930.0, 760.0)
DOT_R = 26.0
HEAD1_Y, HEAD2_Y, TAG_Y = 318.0, 438.0, 528.0
HEAD_SIZE = 96
ACCENTS = {"L06": L.AMBER, "L08": L.MAGENTA, "L10": L.MAGENTA, "L11": L.AMBER, "L13": L.AMBER, "L14": L.AMBER}
HARD_CUTS = set()
X_IN = {}
X_OUT = {}


class Episode:
    def __init__(self, timeline_path, captions=True, grain=0.007):
        self.T = Timeline(timeline_path)
        self.fps = self.T.fps
        self.duration = self.T.duration
        self.post = Post(grain=grain)
        self.stars = Starfield(seed=11)
        self.caps = Captions(self.T, accent_by_line=ACCENTS) if captions else None
        st = self.T.scene_starts()
        self.scenes = [(sid, s0, st[i + 1][1] if i + 1 < len(st) else self.duration)
                       for i, (sid, s0) in enumerate(st)]
        self.c = self._cues()

    def _cues(self):
        T = self.T
        w = lambda l, k: T.word(l, k).start  # noqa: E731
        we = lambda l, k: T.word(l, k).end  # noqa: E731
        c = {"sc_" + sid: (s0, s1) for sid, s0, s1 in self.scenes}
        c.update({
            "want": w("L02", "Want"), "close": w("L02", "Close"), "stare": w("L02", "Stare"),
            "L03": T.line("L03").start, "slowly": w("L03", "slowly"), "L04": T.line("L04").start,
            "L04end": T.line("L04").end, "L05": T.line("L05").start,
            "blind": w("L05", "blind"), "optic": w("L05", "optic"), "nothing": w("L05", "nothing"),
            "L05end": T.line("L05").end,
            "notice": w("L06", "notice"), "paints": w("L06", "paints"), "L06end": T.line("L06").end,
            "L07": T.line("L07").start, "edit7": w("L07", "edit."),
            "blink": w("L08", "blink"), "fifteen": w("L08", "fifteen"), "darkness": w("L08", "darkness."),
            "L08end": T.line("L08").end,
            "jump": w("L09", "jump"), "three": w("L09", "three"), "even": w("L09", "Even"),
            "reading": w("L09", "reading"), "smears": w("L10", "smears"), "cuts": w("L10", "cuts"),
            "blur": w("L10", "blur..."), "L10end": T.line("L10").end,
            "covers": w("L11", "covers"), "stretching": w("L11", "stretching"), "back": w("L11", "back"),
            "L11end": T.line("L11").end,
            "glance": w("L12", "glance"), "clock": w("L12", "clock,"), "freeze": w("L12", "freeze."),
            "L12end": T.line("L12").end, "didnt": w("L13", "didn't."), "stretched": w("L13", "stretched"),
            "L13end": T.line("L13").end,
            "L14": T.line("L14").start, "live": w("L14", "live."), "edit14": w("L14", "edit."),
            "L14end": T.line("L14").end, "L15": T.line("L15").start, "hole15": w("L15", "hole..."),
            "L15end": T.line("L15").end,
        })
        return c

    # ------------------------------------------------------------------ frame
    def frame(self, i):
        t = i / self.fps
        cv = Canvas()
        self.draw(cv, t)
        return self.post.finish(cv, i)

    def draw(self, cv, t):
        c = self.c
        background(cv, t, haze=(0.5, 0.42), haze_color=(0.10, 0.22, 0.55), haze_amt=0.9)
        # calm sky behind the test card (nothing moving near the dot), full sky elsewhere
        calm = max(1 - smooth(prog(t, c["sc_anatomy"][0] - 0.2, c["sc_anatomy"][0] + 0.4)),
                   smooth(prog(t, c["L15"] - 0.2, c["L15"] + 0.6)))
        self.stars.draw(cv, t, alpha=lerp(0.85, 0.35, calm), dust_alpha=1 - calm)
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

    # ================================================================== shared pieces
    def _headline(self, cv, t, alpha=1.0, text2="IN YOUR VISION", a2=1.0, tag_a=1.0):
        """THERE'S A H(iris)LE / IN YOUR VISION / RIGHT NOW"""
        if alpha <= 0.003:
            return
        s = HEAD_SIZE
        w1 = text_width(cv.b, "THERE'S A H", s, L.DISPLAY)
        w2 = text_width(cv.b, "LE", s, L.DISPLAY)
        r = s * 0.37
        gap = s * 0.04
        total = w1 + gap + 2 * r + gap + w2
        x0 = W / 2 - total / 2
        cv.text("THERE'S A H", x0, HEAD1_Y, s, anchor="left", color=L.WHITE, alpha=alpha, shadow=0.5)
        iris_glyph(cv, x0 + w1 + gap + r, HEAD1_Y, r, t, alpha=alpha)
        cv.text("LE", x0 + w1 + gap * 2 + 2 * r, HEAD1_Y, s, anchor="left", color=L.WHITE, alpha=alpha, shadow=0.5)
        cv.text(text2, W / 2, HEAD2_Y, s, color=L.CYAN, alpha=alpha * a2, glow=0.5, shadow=0.5)
        cv.text("RIGHT NOW", W / 2, TAG_Y, 30, font=L.MONO_XB, color=L.AMBER, alpha=alpha * tag_a, tracking=0.4)

    def _test_pair(self, cv, t, alpha=1.0, ring=0.0):
        if alpha <= 0.003:
            return
        x, y = CROSS
        for (dx, dy) in ((1, 0), (0, 1)):
            cv.line([(x - 36 * dx, y - 36 * dy), (x + 36 * dx, y + 36 * dy)], L.WHITE, width=10, alpha=alpha, glow=0.5)
        if ring > 0:
            cv.arc(x, y, 62, -math.pi / 2, -math.pi / 2 + 2 * math.pi * ring, color=L.CYAN, alpha=alpha * 0.9, width=4,
                   glow=0.7)
        cv.circle(DOT[0], DOT[1], DOT_R, L.AMBER, alpha=alpha, glow=0.8)

    def _edit_chip(self, cv, k, name, color, alpha):
        """Progress chip: EDIT k/4 · NAME (top-left, above the scene content)."""
        if alpha <= 0.003:
            return
        txt = f"EDIT {k}/4 · {name}"
        w = text_width(cv.b, txt, 24, L.MONO_XB, 0.12) + 48
        cv.rect(96, 262, w, 46, (0.04, 0.07, 0.14), alpha=0.9 * alpha, radius=23)
        cv.rect(96, 262, w, 46, color, alpha=0.9 * alpha, fill=False, width=2, radius=23, glow=0.4)
        cv.text(txt, 120, 285, 24, font=L.MONO_XB, anchor="left", color=color, alpha=alpha, tracking=0.12)
        for j in range(4):
            cv.circle(96 + w + 26 + j * 22, 285, 6, color if j < k else L.FAINT, alpha=alpha)

    # ================================================================== scenes
    def s_test(self, cv, t):
        c = self.c
        try_p = prog(t, c["L04end"] + 0.05, c["sc_anatomy"][0] - 0.05)
        swap = smooth(prog(t, c["L04end"] + 0.05, c["L04end"] + 0.4))
        self._headline(cv, t, alpha=1.0, a2=1 - swap, tag_a=1 - swap)
        if swap > 0:
            cv.text("DID THE DOT VANISH?", W / 2, HEAD2_Y + 20, 64, color=L.AMBER, alpha=swap, glow=0.4,
                    shadow=0.6)
        self._test_pair(cv, t, ring=ease_in_out(try_p) if try_p > 0 else 0.0)
        self._hero_eye(cv, t, 1 - smooth(prog(t, c["want"] + 0.2, c["close"] - 0.1)))
        # numbered instructions arrive with the narration
        items = [(c["close"], "CLOSE YOUR LEFT EYE", self._icon_eye_closed),
                 (c["stare"], "STARE AT THE  +", self._icon_cross),
                 (c["slowly"], "BRING THE PHONE CLOSER", self._icon_phone)]
        for k, (t0, txt, icon) in enumerate(items):
            a = smooth(prog(t, t0 - 0.15, t0 + 0.2))
            pop = 1 - ease_out_cubic(prog(t, t0 - 0.15, t0 + 0.35))
            chip(cv, 140, 930 + k * 92, 800, 72, k + 1, txt, alpha=a, icon=icon, pop=pop)
        ha = smooth(prog(t, c["slowly"] + 0.6, c["slowly"] + 1.0))
        cv.text("usually about 15–25 cm from your face", 540, 1222, 24, font=L.MONO, color=L.DIM, alpha=ha)

    def _hero_eye(self, cv, t, alpha):
        """The big eye under the test card on the first (and last) frame."""
        if alpha <= 0.003:
            return
        look = (0.30 * math.sin(2 * math.pi * t / 10.0), -0.25)   # 10 s period: loops cleanly
        eye_front(cv, 540, 1150, 620, open_amt=1.0, t=t, alpha=alpha, look=look, glow=0.7)

    def _icon_eye_closed(self, cv, x, y, s, a):
        eye_front(cv, x - s * 0.28, y, s * 0.5, open_amt=0.0, alpha=a, outline=L.WHITE, glow=0)
        eye_front(cv, x + s * 0.30, y, s * 0.5, open_amt=1.0, alpha=a, outline=L.WHITE, glow=0)

    def _icon_cross(self, cv, x, y, s, a):
        cv.line([(x - s * 0.25, y), (x + s * 0.25, y)], L.WHITE, width=4, alpha=a)
        cv.line([(x, y - s * 0.25), (x, y + s * 0.25)], L.WHITE, width=4, alpha=a)
        cv.circle(x, y, s * 0.38, L.CYAN, alpha=a, fill=False, width=2)

    def _icon_phone(self, cv, x, y, s, a):
        cv.rect(x - s * 0.17, y - s * 0.3, s * 0.34, s * 0.6, L.WHITE, alpha=a, fill=False, width=3, radius=5)
        cv.line([(x + s * 0.32, y), (x + s * 0.55, y)], L.CYAN, width=3, alpha=a)
        cv.poly([(x + s * 0.62, y), (x + s * 0.50, y - 7), (x + s * 0.50, y + 7)], L.CYAN, alpha=a)

    def s_anatomy(self, cv, t):
        c = self.c
        s0, s1 = c["sc_anatomy"]
        ex, ey, er = 520.0, 800.0, 310.0
        intro = ease_out_cubic(prog(t, s0 - 0.1, s0 + 0.6))
        with cv.transform(s=lerp(0.86, 1.0, intro), cx=ex, cy=ey):
            g = eye_section(cv, ex, ey, er, t, alpha=intro,
                            receptors_lit=0.6 * smooth(prog(t, c["nothing"] - 0.2, c["nothing"] + 0.3)),
                            fibers=smooth(prog(t, c["optic"] - 0.3, c["optic"] + 0.3)),
                            flow=smooth(prog(t, c["optic"], c["optic"] + 0.4)),
                            disc_highlight=smooth(prog(t, c["blind"] - 0.1, c["blind"] + 0.3)))
            # light from the dot: rays through the pupil onto the optic disc
            rp = ease_out_cubic(prog(t, s0 + 0.15, s0 + 1.0))
            if rp > 0 and g:
                px, py = g["pupil"]
                dxs, dys = g["disc"]
                for src in ((40.0, ey - 120), (40.0, ey + 110)):
                    seg1 = ((src[0], src[1]), (px, py))
                    k1 = min(1.0, rp * 2)
                    cv.line([seg1[0], (lerp(src[0], px, k1), lerp(src[1], py, k1))], L.AMBER, width=3, alpha=0.9,
                            glow=0.7)
                    if rp > 0.5:
                        k2 = (rp - 0.5) * 2
                        cv.line([(px, py), (lerp(px, dxs, k2), lerp(py, dys, k2))], L.AMBER, width=3, alpha=0.9,
                                glow=0.7)
                # ...and nothing happens there
                fz = window(t, c["nothing"], c["L05end"] + 0.3, 0.15, 0.3)
                if fz > 0:
                    cv.circle(dxs, dys, 26 + 18 * math.sin(t * 9), L.MAGENTA, alpha=0.5 * fz, fill=False, width=3,
                              glow=0.6)
            # labels
            la = smooth(prog(t, c["blind"] - 0.05, c["blind"] + 0.3))
            if g and la > 0:
                dxs, dys = g["disc"]
                cv.line([(dxs - 8, dys + 16), (690, 1168), (650, 1168)], L.MAGENTA, width=2, alpha=la)
                cv.text("BLIND SPOT", 640, 1168, 46, anchor="right", color=L.MAGENTA, alpha=la, glow=0.4,
                        shadow=0.8)
                na = smooth(prog(t, c["nothing"] - 0.1, c["nothing"] + 0.3))
                cv.text("NO LIGHT SENSORS HERE", 640, 1222, 24, font=L.MONO_XB, anchor="right", color=L.WHITE,
                        alpha=na, tracking=0.08, shadow=0.8)
            oa = smooth(prog(t, c["optic"] - 0.1, c["optic"] + 0.3))
            if g and oa > 0:
                tx_, ty_ = g["nerve_tip"]
                cv.text("OPTIC NERVE", 925, 1075, 26, font=L.MONO_XB, anchor="right", color=L.WHITE, alpha=oa,
                        tracking=0.1, shadow=0.8)
                cv.text("→ to the brain", 925, 1110, 22, font=L.MONO, anchor="right", color=L.DIM, alpha=oa)
            sa = smooth(prog(t, s0 + 0.5, s0 + 1.0))
            cv.text("LENS", g["lens"][0] + 4 if g else 300, ey - er * 0.42, 22, font=L.MONO_XB, color=L.DIM,
                    alpha=sa * 0.9, tracking=0.12)
            cv.text("RETINA", ex + er * 0.55, ey - er * 0.98, 22, font=L.MONO_XB, color=L.CYAN, alpha=sa * 0.9,
                    tracking=0.12)
        ta = smooth(prog(t, s0, s0 + 0.4))
        cv.text("THE BLIND SPOT", W / 2, 300, 72, color=L.WHITE, alpha=ta, glow=0.2)
        cv.text("≈ 6° × 7° of your view · first described by Mariotte, 1660s", W / 2, 368, 22, font=L.MONO,
                color=L.DIM, alpha=ta)

    def s_paint(self, cv, t):
        c = self.c
        s0, s1 = c["sc_paint"]
        px, py, pw, ph = 100.0, 430.0, 880.0, 720.0
        a = smooth(prog(t, s0 - 0.1, s0 + 0.35))
        hx, hy, hrx, hry = 690.0, 770.0, 120.0, 140.0
        fill = ease_in_out(prog(t, c["paints"] - 0.1, c["paints"] + 0.9))

        def panel(ctx):
            from engine.gfx import rounded_rect
            ctx.new_path()
            rounded_rect(ctx, px, py, pw, ph, 22)

        with cv.clip(panel):
            cv.rect(px, py, pw, ph, (0.04, 0.08, 0.17), alpha=a)
            self._pattern(cv, px, py, pw, ph, a)
            # the hole, filled from its rim inward as the brain paints
            if fill < 1:
                cv.b.save()
                cv.b.translate(hx, hy)
                cv.b.scale(hrx * (1 - fill), hry * (1 - fill))
                cv.b.arc(0, 0, 1, 0, 2 * math.pi)
                cv.b.restore()
                cv.b.set_source_rgba(0.0, 0.0, 0.0, a)
                cv.b.fill()
            if 0 < fill < 1:
                rr = 1 - fill
                for k in range(26):
                    ang = k / 26 * 2 * math.pi + t * 3
                    sx_, sy_ = hx + hrx * rr * math.cos(ang), hy + hry * rr * math.sin(ang)
                    cv.circle(sx_, sy_, 3.5, L.AMBER, alpha=a * 0.9, glow=1.0)
        cv.rect(px, py, pw, ph, L.FAINT, alpha=a, fill=False, width=2, radius=22)
        cv.text("YOUR VIEW (ONE EYE)", px + 24, py + 30, 20, font=L.MONO_XB, anchor="left", color=L.DIM, alpha=a,
                tracking=0.15)
        ha = window(t, s0 + 0.2, c["paints"] + 0.1, 0.25, 0.25)
        cv.b.save()
        cv.b.translate(hx, hy)
        cv.b.scale(hrx + 12, hry + 12)
        cv.b.arc(0, 0, 1, 0, 2 * math.pi)
        cv.b.restore()
        cv.b.set_source_rgba(*L.MAGENTA, 0.9 * ha)
        cv.b.set_line_width(3)
        cv.b.set_dash([10, 8])
        cv.b.stroke()
        cv.b.set_dash([])
        cv.text("THE HOLE", hx, hy - hry - 40, 32, font=L.MONO_XB, color=L.MAGENTA, alpha=ha, tracking=0.15,
                shadow=0.9, outline=(0.02, 0.03, 0.08), outline_w=8)
        fa = smooth(prog(t, c["paints"] + 0.5, c["paints"] + 0.9))
        cv.text("FILLED IN BY YOUR BRAIN", W / 2, py + ph + 52, 40, color=L.AMBER, alpha=fa, glow=0.5)
        ba = smooth(prog(t, c["L06end"] - 0.2, c["L06end"] + 0.2))
        cv.text("both eyes open? each eye also covers the other's hole", W / 2, 336, 24, font=L.MONO, color=L.DIM,
                alpha=ba)

    def _pattern(self, cv, x, y, w, h, a):
        """Bold dot lattice + diagonal bands: easy to see a hole in, easy to see it filled."""
        step = 54
        rows = int(h / step) + 2
        cols = int(w / step) + 2
        for r in range(rows):
            for q in range(cols):
                cx_ = x + q * step + (step / 2 if r % 2 else 0)
                cy_ = y + r * step
                k = (r * 3 + q * 5) % 7
                col = L.CYAN if k < 3 else (L.AMBER if k < 5 else L.WHITE)
                cv.circle(cx_, cy_, 9, col, alpha=a * (0.75 if col != L.WHITE else 0.5))
        for k in range(-6, 14):
            x0 = x + k * 110
            cv.line([(x0, y + h), (x0 + h * 0.7, y)], (0.25, 0.4, 0.75), width=14, alpha=a * 0.18)

    def s_blink(self, cv, t):
        c = self.c
        s0, s1 = c["sc_blink"]
        a = smooth(prog(t, s0 - 0.1, s0 + 0.35))
        # blink schedule (inside the blink line), each ~0.32 s
        blinks = [c["blink"] + 0.15, c["fifteen"] + 0.55, c["darkness"] - 0.75]
        openv = 1.0
        for b in blinks:
            u = prog(t, b, b + 0.32)
            if 0 < u < 1:
                openv = min(openv, abs(math.cos(u * math.pi)) ** 0.7)
        # editor timeline: the blind-spot fill-in sits on the track; blinks drop black clips in
        card = window(t, c["L07"] - 0.05, c["blink"] - 0.45, 0.25, 0.3)
        if card > 0:
            pop = 1 + 0.12 * (1 - ease_out_back(prog(t, c["L07"] - 0.05, c["L07"] + 0.4)))
            with cv.transform(s=pop, cx=540, cy=880):
                cv.text("EDIT 1 OF 4", 540, 850, 92, color=L.WHITE, alpha=card, glow=0.2)
                cv.text("THE HOLE · FILLED IN", 540, 940, 30, font=L.MONO_XB, color=L.AMBER, alpha=card,
                        tracking=0.12)
                cv.text("3 MORE TO GO", 540, 1010, 26, font=L.MONO, color=L.DIM, alpha=card, tracking=0.3)
        self._edit_chip(cv, 2, "DARKNESS", L.MAGENTA, smooth(prog(t, c["blink"] - 0.4, c["blink"])) * a)
        view = (s0 - 1.5, s0 + 6.5)
        play = lerp(s0 - 0.5, s0 + 6.0, prog(t, s0, s1))
        clips = [{"t0": s0 - 1.3, "t1": s0 + 0.2, "text": "BLIND SPOT · FILLED", "color": L.AMBER}]
        gone = smooth(prog(t, c["darkness"] + 0.05, c["darkness"] + 0.5))
        for k, b in enumerate(blinks):
            ins = smooth(prog(t, b, b + 0.1))
            if ins > 0:
                cl = {"t0": play - (t - b) - 0.0, "t1": play - (t - b) + 0.45, "text": "BLINK", "color": (0.4, 0.4, 0.5),
                      "a": ins * (1 - gone), "cross": ease_out_cubic(prog(t, c["darkness"], c["darkness"] + 0.3))}
                cl["t0"] = s0 + (b - s0) * 0.95
                cl["t1"] = cl["t0"] + 0.9
                cl["fill"] = (0.0, 0.0, 0.0)
                clips.append(cl)
        editor_timeline(cv, 80, 380, 920, 300, [("VISION", clips)], t_view=view, playhead=play, alpha=a,
                        title="EDIT · YOUR BRAIN", fs=1.25)
        ra = smooth(prog(t, c["darkness"] + 0.2, c["darkness"] + 0.5))
        cv.text("DARKNESS · DELETED", 540, 720, 34, font=L.MONO_XB, color=L.MAGENTA, alpha=ra, tracking=0.08,
                glow=0.3)
        # the eye
        ea = smooth(prog(t, c["blink"] - 0.4, c["blink"] - 0.05))
        eye_front(cv, 540, 980, 560, open_amt=openv, t=t, alpha=ea * a, look=(0.15 * math.sin(t * 0.7), 0))
        ca = smooth(prog(t, c["fifteen"] - 0.1, c["fifteen"] + 0.3))
        cv.text("≈ 15 BLINKS A MINUTE", 540, 1205, 30, font=L.MONO_XB, color=L.CYAN, alpha=ca * a, tracking=0.1)
        # what the darkness would look like if your brain kept it
        dark = (1 - openv) * smooth(prog(t, c["blink"] - 0.4, c["blink"]))
        if dark > 0:
            cv.b.set_source_rgba(0, 0, 0.01, 0.55 * dark)
            cv.b.paint()

    def s_saccade(self, cv, t):
        c = self.c
        s0, s1 = c["sc_saccade"]
        a = smooth(prog(t, s0 - 0.1, s0 + 0.35))
        self._edit_chip(cv, 3, "BLUR", L.MAGENTA, a)
        lines = ["YOUR EYES ARE", "JUMPING RIGHT NOW,", "WORD BY WORD,", "AS YOU READ THIS."]
        size = 66
        x0, y0, lh = 120.0, 470.0, 92.0
        words = []
        for li, ln in enumerate(lines):
            x = x0
            for wd in ln.split():
                ww = text_width(cv.b, wd, size, L.DISPLAY)
                words.append((x + ww * 0.42, y0 + li * lh, wd, x, li))
                x += ww + size * 0.28
        for (wx, wy, wd, xl, li) in words:
            cv.text(wd, xl, wy, size, anchor="left", color=L.WHITE, alpha=a * 0.92)
        # gaze hops three times a second; the reticle smears during each hop
        g0 = c["jump"] - 0.2
        hop = 1 / 3
        n_done = int(max(0.0, t - g0) / hop)
        idx = n_done % len(words)
        u = (max(0.0, t - g0) % hop) / hop
        cur = words[idx]
        prv = words[idx - 1] if n_done > 0 else cur
        sac = 0.12 / hop
        ga = smooth(prog(t, g0 - 0.3, g0))
        if u < sac and n_done > 0:
            k = ease_in_out(u / sac)
            gx, gy = lerp(prv[0], cur[0], k), lerp(prv[1], cur[1], k)
            for j in range(6):           # motion smear
                kk = max(0.0, k - j * 0.06)
                cv.circle(lerp(prv[0], cur[0], kk), lerp(prv[1], cur[1], kk), 30, L.CYAN, alpha=ga * 0.12, glow=0.4)
        else:
            gx, gy = cur[0], cur[1]
        for j in range(1, 6):            # fading fixation trail
            wj = words[(idx - j) % len(words)]
            cv.circle(wj[0], wj[1] + 46, 6, L.CYAN, alpha=ga * 0.5 * (1 - j / 6))
        gaze_reticle(cv, gx, gy, 34, alpha=ga)
        ja = smooth(prog(t, c["three"] - 0.1, c["three"] + 0.3))
        cv.text("≈ 3 JUMPS EVERY SECOND", 540, 870, 34, font=L.MONO_XB, color=L.CYAN, alpha=ja * a, tracking=0.08)
        # film strip of what reaches the brain: blur frames, then cut
        fa = smooth(prog(t, c["smears"] - 0.3, c["smears"] + 0.2))
        if fa > 0:
            cut = ease_in_out(prog(t, c["cuts"], c["cuts"] + 0.6))
            frames = []
            for k in range(9):
                kind = "blur" if k % 2 == 1 else "clear"
                fr = {"w": 1.0, "kind": kind, "i": k}
                if kind == "blur":
                    fr["a"] = 1 - cut
                    if cut > 0.98:
                        fr["kind"] = "gap"
                        fr["a"] = 1.0
                frames.append(fr)
            film_strip(cv, 70, 1080, 92, 120, frames, alpha=fa * a, gap=10, draw_frame=self._mini_frame,
                       scroll=(t - c["smears"]) * 14)
            ca = smooth(prog(t, c["cuts"], c["cuts"] + 0.25))
            sa = smooth(prog(t, c["smears"], c["smears"] + 0.3)) * (1 - smooth(prog(t, c["cuts"] - 0.25, c["cuts"])))
            cv.text("SMEARED FRAMES", 540, 975, 28, font=L.MONO_XB, color=L.MAGENTA, alpha=sa, tracking=0.15)
            cv.text("BLUR FRAMES · CUT", 540, 975, 32, font=L.MONO_XB, color=L.MAGENTA, alpha=ca, tracking=0.1,
                    glow=0.4)

    def _mini_frame(self, cv, x, y, w, h, fr, a):
        kind = fr.get("kind")
        if kind == "blur":
            for k in range(7):
                yy = y + 16 + k * (h - 32) / 6
                cv.line([(x + 8, yy), (x + w - 8, yy + 3)], (1.0, 0.6, 0.75), width=6, alpha=a * 0.35)
        else:
            for k in range(4):
                yy = y + 22 + k * (h - 44) / 3
                cv.line([(x + 12, yy), (x + 12 + (w - 24) * (0.9 - 0.15 * (k % 2)), yy)], L.WHITE, width=5,
                        alpha=a * 0.7)

    def s_stretch(self, cv, t):
        c = self.c
        s0, s1 = c["sc_stretch"]
        a = smooth(prog(t, s0 - 0.1, s0 + 0.35))
        st = ease_in_out(prog(t, c["stretching"] - 0.1, c["stretching"] + 0.8))
        frames = []
        for k in range(7):
            if k % 2 == 1:
                frames.append({"w": 1.0 * (1 - st), "kind": "gap", "a": 1 - st})
            else:
                fr = {"w": 1.0 + (1.0 + 10 / 116) * st if 0 < k else 1.0, "kind": "clear", "i": k}
                if 0 < k and st > 0.02:
                    fr["kind"] = "stretch"
                frames.append(fr)
        total = film_strip(cv, 104, 760, 116, 170, frames, alpha=a, gap=10, draw_frame=self._stretch_frame)
        # arrows pointing back in time on the stretched parts
        for fr in frames:
            if fr.get("kind") == "stretch" and st > 0.1:
                x_ = fr["_x"]
                cv.line([(x_ + 110, 760), (x_ + 24, 760)], L.AMBER, width=4, alpha=a * st, glow=0.6)
                cv.poly([(x_ + 14, 760), (x_ + 32, 748), (x_ + 32, 772)], L.AMBER, alpha=a * st)
        # time axis
        cv.line([(96, 930), (980, 930)], L.DIM, width=2, alpha=a)
        cv.poly([(990, 930), (976, 922), (976, 938)], L.DIM, alpha=a)
        cv.text("TIME", 980, 962, 22, font=L.MONO_XB, anchor="right", color=L.DIM, alpha=a, tracking=0.2)
        ba = smooth(prog(t, c["back"] - 0.1, c["back"] + 0.3))
        pop = 1 + 0.15 * (1 - ease_out_back(prog(t, c["back"] - 0.1, c["back"] + 0.4)))
        with cv.transform(s=pop, cx=540, cy=470):
            cv.text("← BACK IN TIME", 540, 470, 76, color=L.AMBER, alpha=ba, glow=0.6)
        self._edit_chip(cv, 4, "TIME", L.AMBER, a)
        ga = smooth(prog(t, s0 + 0.1, s0 + 0.5))
        cv.text("THE GAPS GET COVERED", 540, 590, 30, font=L.MONO_XB, color=L.WHITE, alpha=ga * (1 - ba * 0.0),
                tracking=0.12)

    def _stretch_frame(self, cv, x, y, w, h, fr, a):
        for k in range(4):
            yy = y + 30 + k * (h - 60) / 3
            cv.line([(x + w - 14 - (min(w, 116) - 28) * (0.9 - 0.15 * (k % 2)), yy), (x + w - 14, yy)], L.WHITE,
                    width=6, alpha=a * 0.75)

    def s_clock(self, cv, t):
        c = self.c
        s0, s1 = c["sc_clock"]
        a = smooth(prog(t, s0 - 0.1, s0 + 0.4))
        cx_, cy_, r = 540.0, 760.0, 280.0
        glance = c["glance"] + 0.1
        freeze_until = c["freeze"] + 0.65
        # second hand: steady ticks before the glance, a long hold after it, then steady again
        base_sec = 17.0
        if t < glance:
            sec = base_sec + math.floor(t - s0)
            frac = (t - s0) % 1.0
        elif t < freeze_until:
            sec = base_sec + math.floor(glance - s0) + 1
            frac = 1.0
        else:
            sec = base_sec + math.floor(glance - s0) + 1 + math.floor(t - freeze_until) + 1
            frac = (t - freeze_until) % 1.0
        sec_pos = sec + (ease_out_back(min(1.0, frac / 0.12)) - 1 if frac < 0.12 else 0)
        analog_clock(cv, cx_, cy_, r, sec_pos, minute=9.0, hour=10.15, alpha=a)
        # the glance: a saccade from the left edge to the clock face
        gp = prog(t, glance - 0.25, glance)
        if gp > 0:
            sx0, sy0 = 120.0, 470.0
            k = ease_in_out(gp)
            gx, gy = lerp(sx0, cx_, k), lerp(sy0, cy_ - r * 0.45, k)
            if gp < 1:
                for j in range(7):
                    kk = max(0.0, k - j * 0.07)
                    cv.circle(lerp(sx0, cx_, kk), lerp(sy0, cy_ - r * 0.45, kk), 30, L.CYAN, alpha=0.12, glow=0.4)
            ga = 1 - smooth(prog(t, freeze_until + 0.3, freeze_until + 0.8))
            gaze_reticle(cv, gx, gy, 32, alpha=ga)
        # seconds bar: the first second after the glance feels longer
        by = 1150.0
        ba = smooth(prog(t, glance, glance + 0.3))
        unit = 170.0
        fixed = smooth(prog(t, c["didnt"] - 0.05, c["didnt"] + 0.35))
        stretch_amt = 0.55 * (1 - fixed) + 0.55 * smooth(prog(t, c["stretched"], c["stretched"] + 0.4))
        x = 130.0
        if ba > 0:
            ext = unit * stretch_amt
            if ext > 1:
                cv.rect(x, by - 22, ext, 44, L.AMBER, alpha=0.35 * ba, radius=8)
                cv.rect(x, by - 22, ext, 44, L.AMBER, alpha=0.9 * ba, fill=False, width=2, radius=8, glow=0.5)
            xs = x + ext + 6
            for k in range(4):
                cv.rect(xs, by - 22, unit - 8, 44, (0.12, 0.2, 0.36), alpha=ba, radius=8)
                cv.rect(xs, by - 22, unit - 8, 44, L.CYAN if k else L.WHITE, alpha=0.8 * ba, fill=False, width=2,
                        radius=8)
                cv.text("1 s", xs + (unit - 8) / 2, by, 22, font=L.MONO_XB, color=L.WHITE, alpha=ba)
                xs += unit
            la = ba * (1 - fixed)
            cv.text("FIRST SECOND FEELS LONGER", 540, by - 62, 26, font=L.MONO_XB, color=L.AMBER, alpha=la,
                    tracking=0.08)
            ra = smooth(prog(t, c["didnt"], c["didnt"] + 0.3)) * (1 - smooth(prog(t, c["stretched"] - 0.1,
                                                                                   c["stretched"] + 0.2)))
            cv.text("REAL CLOCK: EVERY SECOND IS 1 s", 540, by - 62, 26, font=L.MONO_XB, color=L.WHITE, alpha=ra,
                    tracking=0.08)
            sa = smooth(prog(t, c["stretched"], c["stretched"] + 0.3))
            cv.text("← STRETCHED BACK TO THE JUMP", 540, by - 62, 26, font=L.MONO_XB, color=L.AMBER, alpha=sa,
                    tracking=0.06, glow=0.3)
        ta = smooth(prog(t, s0, s0 + 0.4))
        cv.text("THE STOPPED-CLOCK ILLUSION", W / 2, 300, 54, color=L.WHITE, alpha=ta, glow=0.2)
        fa = smooth(prog(t, c["freeze"] - 0.2, c["freeze"] + 0.3))
        cv.text("chronostasis · Yarrow et al., Nature 2001 · hold time exaggerated", W / 2, 1230, 20,
                font=L.MONO, color=L.DIM, alpha=fa * a)

    def s_outro(self, cv, t):
        c = self.c
        s0, s1 = c["sc_outro"]
        out = smooth(prog(t, c["L15"] - 0.1, c["L15"] + 0.7))
        a = smooth(prog(t, s0 - 0.1, s0 + 0.35)) * (1 - out)
        if a > 0.003:
            live_x = ease_out_cubic(prog(t, c["live"], c["live"] + 0.3))
            flip = smooth(prog(t, c["edit14"] - 0.05, c["edit14"] + 0.25))

            def badge(cv_, x, y, al):
                if flip < 1:
                    w_ = 120
                    cv_.rect(x - w_, y - 18, w_, 36, L.MAGENTA, alpha=al * (1 - flip) * 0.25, radius=18)
                    cv_.circle(x - w_ + 22, y, 7, L.MAGENTA, alpha=al * (1 - flip))
                    cv_.text("LIVE", x - w_ + 40, y, 20, font=L.MONO_XB, anchor="left", color=L.WHITE,
                             alpha=al * (1 - flip), tracking=0.15)
                    if live_x > 0:
                        cv_.line([(x - w_ - 4, y), (x - w_ - 4 + (w_ + 8) * live_x, y)], L.MAGENTA, width=3,
                                 alpha=al * (1 - flip))
                if flip > 0:
                    pop = 1 + 0.3 * (1 - ease_out_back(flip))
                    with cv_.transform(s=pop, cx=x - 70, cy=y):
                        cv_.rect(x - 140, y - 20, 140, 40, L.AMBER, alpha=al * flip * 0.3, radius=20)
                        cv_.rect(x - 140, y - 20, 140, 40, L.AMBER, alpha=al * flip, fill=False, width=2, radius=20,
                                 glow=0.6)
                        cv_.text("EDIT", x - 70, y, 22, font=L.MONO_XB, color=L.AMBER, alpha=al * flip,
                                 tracking=0.2)

            tracks = [
                ("SPACE", [{"t0": 0.4, "t1": 3.4, "text": "BLIND SPOT · FILLED", "color": L.AMBER}]),
                ("DARK", [{"t0": 0.9, "t1": 1.5, "text": "", "color": (0.5, 0.5, 0.6), "cross": 1.0},
                          {"t0": 2.6, "t1": 3.2, "text": "", "color": (0.5, 0.5, 0.6), "cross": 1.0},
                          {"t0": 3.6, "t1": 5.6, "text": "BLINKS · DELETED", "color": L.MAGENTA}]),
                ("MOTION", [{"t0": 0.2 + k * 1.1, "t1": 0.55 + k * 1.1, "text": "", "color": L.MAGENTA, "cross": 1.0}
                            for k in range(5)]),
                ("TIME", [{"t0": 1.0, "t1": 4.8, "text": "← STRETCHED", "color": L.AMBER}]),
            ]
            play = lerp(1.0, 5.0, prog(t, s0, c["L15"]))
            rv = ease_out_cubic(prog(t, s0 - 0.1, s0 + 0.6))
            editor_timeline(cv, 70, lerp(470, 390, rv), 940, 760, tracks, t_view=(0.0, 6.0), playhead=play, alpha=a,
                            title="YOUR BRAIN · FINAL CUT", live_badge=badge, fs=1.45)
        # the test card returns: identical to the first frame
        if out > 0:
            self._headline(cv, t, alpha=out)
            self._test_pair(cv, t, alpha=out)
            self._hero_eye(cv, t, out)


def make_episode(timeline_path, **opts):
    return Episode(timeline_path, **opts)
