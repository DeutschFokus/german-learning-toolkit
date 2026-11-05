"""EP001 — Your Head Is Older Than Your Feet.

Every animation is anchored to narration cues from the timeline (line and word
times), so swapping the AI voice for the creator's own recording re-times
the whole edit automatically. Ambient motion is periodic over 60 s so the
last frame flows straight back into the first.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STUDIO = HERE.parents[2]
sys.path.insert(0, str(STUDIO))

import cv2  # noqa: E402

cv2.setNumThreads(1)

from engine.captions import Captions  # noqa: E402
from engine.figure import Figure  # noqa: E402
from engine.gfx import (H, L, W, Canvas, Starfield, background, blueprint_grid, clamp,  # noqa: E402
                        ease_in_cubic, ease_in_out, ease_out_back, ease_out_cubic, ease_out_expo,
                        lerp, mix, prog, ring_clock, smooth, text_width, window)
from engine.postfx import Post  # noqa: E402
from engine.props import (DottedEarth, Fabric, LAYERS, Limb, atmosphere, cross_section,  # noqa: E402
                          phone, satellite)
from engine.timeline import Timeline  # noqa: E402

# ---------------------------------------------------------------- layout constants (hook = loop frame)
FIG_X, FIG_Y, FIG_S = 790.0, 300.0, 900 / 960
TXT_X = 96.0
HEAD_Y = 363.0
FEET_Y = 1182.0
LIMB_TOP = 1194.0
CLOCK_X = 662.0
ACCENTS = {"L04": L.AMBER, "L05": L.AMBER, "L13": L.AMBER, "L14": L.AMBER}
HARD_CUTS = {"outro"}          # content continues across this boundary: cut, don't dissolve
X_IN = {"you": 0.30}           # half-length of each scene's incoming dissolve (s)
X_OUT = {"dive": 0.40}         # half-length of each scene's outgoing transition (s)


class Episode:
    def __init__(self, timeline_path, captions=True, grain=0.007):
        self.T = Timeline(timeline_path)
        self.fps = self.T.fps
        self.duration = self.T.duration
        self.post = Post(grain=grain)
        self.stars = Starfield()
        self.fig = Figure(height=960)
        self.earth = DottedEarth()
        self.limb = Limb(top=LIMB_TOP, R=1500, home=(52.37, 9.73), home_x=FIG_X)
        self.fabric = Fabric()
        self.caps = Captions(self.T, accent_by_line=ACCENTS) if captions else None
        st = self.T.scene_starts()
        self.scenes = [(sid, s0, st[i + 1][1] if i + 1 < len(st) else self.duration)
                       for i, (sid, s0) in enumerate(st)]
        self.c = self._cues()

    # ------------------------------------------------------------------ cues
    def _cues(self):
        T = self.T
        w = lambda l, k: T.word(l, k).start  # noqa: E731
        c = {"sc_" + sid: (s0, s1) for sid, s0, s1 in self.scenes}
        c.update({
            "L02": T.line("L02").start, "L03": T.line("L03").start, "faster3": w("L03", "faster"),
            "einstein": w("L04", "Einstein"), "gravity": w("L04", "gravity"), "down4": w("L04", "down"),
            "closer": w("L05", "closer"), "earth5": w("L05", "Earth"), "slower": w("L05", "slower"),
            "y2010": w("L06", "2010"), "measured": w("L06", "measured"),
            "lifted": w("L07", "lifted"), "atomic": w("L07", "atomic"), "just": w("L07", "just"),
            "33": w("L07", "33"), "cm": w("L07", "centimeters"), "L08": T.line("L08").start,
            "faster8": w("L08", "faster"),
            "phone": w("L09", "phone"), "orbit": w("L10", "orbit"), "gps": w("L10", "GPS"),
            "38": w("L10", "38"), "second": w("L10", "second"), "everyday": w("L10", "every"),
            "light": w("L11", "Light"), "km": w("L11", "kilometers"), "km_end": T.word("L11", "kilometers").end,
            "L12": T.line("L12").start, "built": w("L12", "built"), "einstein12": w("L12", "Einstein"),
            "now": w("L13", "Now"), "down13": w("L13", "down"), "deep": w("L14", "Deep"),
            "well14": w("L14", "well"), "center": w("L14", "center"), "two": w("L14", "two"),
            "younger": w("L14", "younger"), "surface": w("L14", "surface"), "L14end": T.line("L14").end,
            "L15": T.line("L15").start, "lifetime": w("L16", "lifetime"), "head16": w("L16", "head"),
            "few": w("L16", "few"), "second16": w("L16", "second"), "L16end": T.line("L16").end,
            "tiny": T.line("L17").start, "real": T.line("L18").start, "which": T.line("L19").start,
            "L19end": T.line("L19").end,
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
        # background: haze warms as we go deeper into the Earth
        warm = window(t, c["sc_dive"][0] + 0.6, c["sc_dive"][1] - 0.2, 0.8, 0.8)
        hz = mix((0.12, 0.25, 0.60), (0.55, 0.22, 0.10), warm)
        background(cv, t, haze=(0.5, 0.45), haze_color=hz, haze_amt=1.0 + 0.3 * warm)
        warp = window(t, c["now"] + 0.25, c["down13"] + 0.5, 0.25, 0.5) * 0.9
        self.stars.draw(cv, t, cam_y=0.0, alpha=1.0 - 0.4 * warm, warp=warp)
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
            cx_, cy_ = W / 2, H / 2
            if Xi and t < s0 + Xi:
                p = prog(t, s0 - Xi, s0 + Xi)
                a, sc, ty = smooth(p), 0.97 + 0.03 * ease_out_cubic(p), 80 * (1 - ease_out_cubic(p))
            if Xo and t > s1 - Xo:
                p = prog(t, s1 - Xo, s1 + Xo)
                if sid == "dive":       # sink the cut-away Earth down into the planet under your feet
                    a, sc, ty = 1 - smooth(p), lerp(1.0, 0.30, ease_in_cubic(p)), 0.0
                    cx_, cy_ = W / 2, lerp(1000, 2600, ease_in_cubic(p))
                else:
                    a, sc, ty = 1 - smooth(p), 1 + 0.05 * ease_in_cubic(p), -80 * ease_in_cubic(p)
            if a <= 0.003:
                continue
            fn = getattr(self, "s_" + sid)
            if a >= 0.999 and sc == 1.0 and ty == 0.0:
                fn(cv, t)
            else:
                with cv.group(a), cv.transform(tx=0, ty=ty, s=sc, cx=cx_, cy=cy_ if sid != "dive" else 1000):
                    fn(cv, t)
        if self.caps:
            self.caps.draw(cv, t)

    # ================================================================== shared pieces
    def _limb(self, cv, t, alpha=1.0):
        self.limb.draw(cv, t, alpha=alpha)

    def _figure(self, cv, t, alpha=1.0, reveal=1.0, scan=(150.0, 45.0)):
        self.fig.draw(cv, t, FIG_X, FIG_Y, FIG_S, alpha=alpha, reveal=reveal, scan_speed=scan)

    def _probe(self, cv, t, which, alpha=1.0, draw_p=1.0, label=True, rate=None, pulse=None):
        """Leader line + ring clock from a text label to the head or feet."""
        if alpha <= 0.003:
            return
        y = HEAD_Y if which == "head" else FEET_Y
        col = L.CYAN if which == "head" else L.AMBER
        rate = rate if rate is not None else (1.2 if which == "head" else 1.0)
        pulse = pulse if pulse is not None else (0.4 if which == "head" else 0.5)
        tx_end = TXT_X + text_width(cv.b, "YOUR HEAD", 84, L.DISPLAY) + 16
        target = (FIG_X - 0.37 * self.fig.u * FIG_S - 10) if which == "head" else \
            (FIG_X - (0.42 + 0.25) * self.fig.u * FIG_S - 8)
        r = 34
        p = ease_out_cubic(draw_p)
        x1 = lerp(tx_end, target, p)
        cv.line([(tx_end, y), (min(x1, CLOCK_X - r - 6), y)], col, width=2.2, alpha=0.75 * alpha,
                dash=[7, 7])
        if x1 > CLOCK_X + r + 6:
            cv.line([(CLOCK_X + r + 6, y), (x1, y)], col, width=2.2, alpha=0.75 * alpha, dash=[7, 7])
            cv.circle(x1, y, 4, col, alpha=alpha, glow=0.8)
        ca = alpha * smooth(prog(draw_p, 0.25, 0.6))
        ring_clock(cv, CLOCK_X, y, r, t, rate=rate, color=col, alpha=ca, glow=0.9, pulse_every=pulse)

    def _headline(self, cv, t, a_head=1.0, a_mid=(1.0, 1.0, 1.0), a_feet=1.0, offs=(0, 0, 0, 0, 0)):
        cv.text("YOUR HEAD", TXT_X + offs[0], HEAD_Y, 84, anchor="left", color=L.CYAN, glow=0.55,
                alpha=a_head, shadow=0.5)
        cv.text("IS", TXT_X + offs[1], 628, 84, anchor="left", color=L.WHITE, alpha=a_mid[0], shadow=0.5)
        cv.text("OLDER", TXT_X - 6 + offs[2], 760, 150, anchor="left", color=L.WHITE, alpha=a_mid[1],
                glow=0.18, shadow=0.6)
        cv.text("THAN", TXT_X + offs[3], 892, 84, anchor="left", color=L.WHITE, alpha=a_mid[2], shadow=0.5)
        cv.text("YOUR FEET", TXT_X + offs[4], FEET_Y, 84, anchor="left", color=L.AMBER, glow=0.45,
                alpha=a_feet, shadow=0.9, outline=(0.02, 0.03, 0.08), outline_w=7)

    # ================================================================== scenes
    def s_hook(self, cv, t):
        c = self.c
        self._limb(cv, t)
        self._figure(cv, t)
        # headline: holds through the hook line, then the middle words step aside
        ex = [ease_in_cubic(prog(t, c["L02"] - 0.25 + k * 0.06, c["L02"] + 0.15 + k * 0.06)) for k in range(3)]
        self._headline(cv, t, a_mid=tuple(1 - e for e in ex),
                       offs=(0, -140 * ex[0], -140 * ex[1], -140 * ex[2], 0))
        self._probe(cv, t, "head")
        self._probe(cv, t, "feet")
        # L03: time-rate axis rises from the feet to the head
        p = prog(t, c["L03"] - 0.1, c["L03"] + 0.9)
        if p > 0:
            x = 150
            y0, y1 = FEET_Y - 95, HEAD_Y + 110
            yt = lerp(y0, y1, ease_out_cubic(p))
            n = 24
            for k in range(n):
                ya = lerp(y0, yt, k / n)
                yb = lerp(y0, yt, (k + 1) / n)
                col = mix(L.AMBER, L.CYAN, ((y0 - ya) / (y0 - y1)))
                cv.line([(x, ya), (x, yb)], col, width=5, alpha=0.95, glow=0.7)
            cv.poly([(x, yt - 26), (x - 16, yt + 4), (x + 16, yt + 4)], mix(L.AMBER, L.CYAN, (y0 - yt) / (y0 - y1)),
                    alpha=1.0, glow=0.8)
            for k in range(8):
                yy = lerp(y0, y1, k / 7)
                if yy >= yt:
                    cv.line([(x - 12, yy), (x + 12, yy)], L.DIM, width=2, alpha=0.6)
            a2 = smooth(prog(t, c["L03"] + 0.5, c["L03"] + 1.0))
            cv.text("TIME RUNS", x + 34, 520, 40, font=L.DISPLAY, anchor="left", color=L.CYAN, alpha=a2,
                    glow=0.4)
            cv.text("FASTER", x + 34, 572, 58, font=L.DISPLAY, anchor="left", color=L.CYAN, alpha=a2,
                    glow=0.6)
            cv.text("SLOWER", x + 34, FEET_Y - 160, 40, font=L.DISPLAY, anchor="left", color=L.AMBER,
                    alpha=a2 * 0.9, glow=0.3)
            # "faster": the head clock flashes
            f = window(t, c["faster3"], c["faster3"] + 0.15, 0.05, 0.6)
            if f > 0:
                cv.circle(CLOCK_X, HEAD_Y, 34 + 40 * (1 - f), L.CYAN, alpha=0.6 * f, fill=False, width=4,
                          glow=1.0)

    def s_well(self, cv, t):
        c = self.c
        s0, s1 = c["sc_well"]
        F = self.fabric
        depth = 3.4 * ease_in_out(prog(t, c["gravity"] - 0.25, c["gravity"] + 1.1))
        ripple = window(t, c["gravity"], c["gravity"] + 1.2, 0.2, 0.8)
        drift = prog(t, s0, s1)
        F.cam_pos = [lerp(-0.7, 0.7, drift), 5.4, -8.4]
        F.cam_tgt = [0.0, -1.6, 1.0]
        F.focal = 1180.0
        F.center = (W / 2, 1010.0)
        F.draw(cv, depth, alpha=smooth(prog(t, s0, s0 + 0.5)), ripple=ripple, t=t)
        # Earth sitting in the well
        ex, ey, ez = F.point(0.0, 0.0, depth, lift=1.0)
        er = F.focal * 1.0 / ez
        self.earth.draw(cv, ex, ey, er, lon0=0.6 + 0.25 * t, tilt=0.4, alpha=smooth(prog(t, s0 + 0.1, s0 + 0.6)),
                        glow=0.5)
        # name card
        a = smooth(prog(t, c["einstein"] + 0.02, c["einstein"] + 0.42))
        sc = lerp(1.08, 1.0, ease_out_cubic(prog(t, c["einstein"] + 0.02, c["einstein"] + 0.7)))
        with cv.transform(s=sc, cx=W / 2, cy=330):
            cv.text("EINSTEIN", W / 2, 330, 116, font=L.DISPLAY, color=L.WHITE, alpha=a, glow=0.25,
                    tracking=0.04)
        cv.text("GENERAL RELATIVITY", W / 2, 418, 28, font=L.MONO_XB, color=L.DIM, alpha=a, tracking=0.32)
        a = smooth(prog(t, c["gravity"] + 0.3, c["gravity"] + 0.8))
        cv.text("MASS BENDS SPACETIME", W / 2, 505, 50, font=L.DISPLAY, color=L.WHITE, alpha=a, glow=0.15)
        cv.text("…and time runs slower down in the well", W / 2, 562, 34, font=L.UI_MED, color=L.AMBER,
                alpha=a * smooth(prog(t, c["down4"], c["down4"] + 0.4)), shadow=0.6)
        # clocks on the fabric: deeper = slower
        ca = smooth(prog(t, c["closer"] - 0.6, c["closer"] - 0.1))
        for (x, z, ph) in ((-4.6, 3.6, 0.1), (4.4, 3.2, 0.5), (-2.3, -1.2, 0.3)):
            px, py, pz = F.point(x, z, depth, lift=0.05)
            deep = clamp(-F.height(x, z, depth) / max(depth, 1e-6)) if depth > 0 else 0
            col = mix(L.CYAN, L.AMBER, deep ** 0.9)
            r = 560 / pz
            ring_clock(cv, px, py - r * 1.25, r, t, rate=lerp(1.6, 0.35, deep ** 0.9), color=col,
                       alpha=ca, glow=0.8, phase=ph)
        # the travelling clock slides down into the well
        mp = ease_in_out(prog(t, c["closer"], c["slower"] + 0.6))
        ma = smooth(prog(t, c["closer"] - 0.4, c["closer"]))
        if ma > 0:
            x = lerp(5.4, 1.55, mp)
            z = lerp(-2.6, -0.9, mp)
            px, py, pz = F.point(x, z, depth, lift=0.05)
            deep = clamp(-F.height(x, z, depth) / max(depth, 1e-6))
            col = mix(L.CYAN, L.AMBER, deep ** 0.9)
            r = 640 / pz
            ph = self._integrated_phase(t, c["closer"] - 0.4, lambda tt: lerp(1.7, 0.3, ease_in_out(
                prog(tt, c["closer"], c["slower"] + 0.6))))
            ring_clock(cv, px, py - r * 1.3, r, 0.0, rate=0.0, color=col, alpha=ma, glow=1.0, phase=ph)
            la = smooth(prog(t, c["slower"], c["slower"] + 0.3))
            cv.text("SLOWER", px, py - r * 2.65 - 22, 40, font=L.DISPLAY, color=L.AMBER, alpha=la, glow=0.5,
                    shadow=0.7)

    @staticmethod
    def _integrated_phase(t, t0, rate_fn, dt=1 / 60):
        """Phase (revolutions) of a clock whose rate (rev per 4 s) varies with time."""
        if t <= t0:
            return 0.0
        n = int((t - t0) / dt)
        acc = 0.0
        tt = t0
        for _ in range(n):
            acc += rate_fn(tt) * dt / 4.0
            tt += dt
        acc += rate_fn(tt) * (t - tt) / 4.0
        return acc

    def s_lab(self, cv, t):
        c = self.c
        s0, s1 = c["sc_lab"]
        blueprint_grid(cv, alpha=0.05 * smooth(prog(t, s0, s0 + 0.5)), step=54, oy=-t * 6)
        # "2010" rolls in like a counter, then steps up out of the way
        ap = prog(t, c["y2010"] - 0.15, c["y2010"] + 0.55)
        up = ease_in_out(prog(t, c["lifted"] - 0.4, c["lifted"] + 0.3))
        if ap > 0:
            rolled = "".join(d if ap > 0.25 + 0.18 * i else str(int(t * 37 + i * 3) % 10)
                             for i, d in enumerate("2010"))
            sc = lerp(1.25, 1.0, ease_out_expo(ap)) * lerp(1.0, 0.52, up)
            ty = lerp(380, 285, up)
            with cv.transform(s=sc, cx=W / 2, cy=ty):
                cv.text(rolled, W / 2, ty, 230, font=L.DISPLAY, color=L.WHITE, alpha=smooth(ap * 2), glow=0.35,
                        tracking=0.02)
            a = smooth(prog(t, c["y2010"] + 0.4, c["y2010"] + 0.9))
            cv.text("NIST · BOULDER, COLORADO", W / 2, lerp(515, 362, up), 28, font=L.MONO, color=L.DIM, alpha=a,
                    tracking=0.2)
        # bench + two optical clocks
        bench_y = 1190
        ba = smooth(prog(t, s0 + 0.2, s0 + 0.8))
        cv.line([(130, bench_y), (950, bench_y)], L.DIM, width=3, alpha=ba)
        cv.text("TWO OPTICAL ATOMIC CLOCKS", 540, bench_y + 42, 24, font=L.MONO, color=L.DIM, alpha=ba * 0.9,
                tracking=0.22)
        lift = 330 * ease_in_out(prog(t, c["lifted"], c["33"] + 0.3))
        ax, bx = 260, 560
        ion_y = bench_y - 110
        for k, (x, dy, col, name) in enumerate(((ax, 0.0, L.AMBER, "A"), (bx, lift, L.CYAN, "B"))):
            a = ba * smooth(prog(t, s0 + 0.35 + 0.15 * k, s0 + 0.85 + 0.15 * k))
            self._optical_clock(cv, t, x, bench_y - dy, col, a, name, faster=(k == 1))
        # ruler between the two ions (1 px = 1 mm)
        ra = smooth(prog(t, c["just"] - 0.1, c["just"] + 0.3))
        if ra > 0:
            rx = 790
            ya, yb = ion_y, ion_y - lift
            cv.line([(ax + 110, ya), (rx - 10, ya)], L.AMBER, width=2, alpha=0.6 * ra, dash=[6, 6])
            cv.line([(bx + 110, yb), (rx - 10, yb)], L.CYAN, width=2, alpha=0.6 * ra, dash=[6, 6])
            cv.line([(rx, ya), (rx, yb)], L.WHITE, width=3, alpha=ra, glow=0.4)
            for k in range(int(lift / 10) + 1):
                yy = ya - k * 10
                wlen = 18 if k % 10 == 0 else (12 if k % 5 == 0 else 7)
                cv.line([(rx - wlen, yy), (rx, yy)], L.WHITE, width=1.6, alpha=0.8 * ra)
            la = smooth(prog(t, c["33"] - 0.05, c["33"] + 0.25))
            pop = 1 + 0.25 * (1 - ease_out_back(prog(t, c["33"] - 0.05, c["33"] + 0.35)))
            ym = (ya + yb) / 2
            with cv.transform(s=pop, cx=810, cy=ym):
                cv.text(f"{min(33, int(lift / 10 + 0.5))} cm", 810, ym, 52, font=L.DISPLAY, anchor="left",
                        color=L.CYAN, alpha=la, glow=0.6)
            cv.text("≈ 2 stairs", 812, ym + 50, 24, font=L.MONO, anchor="left", color=L.DIM, alpha=la * 0.9)
        # tick traces
        ta = smooth(prog(t, c["atomic"], c["atomic"] + 0.5))
        if ta > 0:
            self._traces(cv, t, ta, speedup=ease_in_out(prog(t, c["33"], c["L08"] + 0.4)),
                         highlight=smooth(prog(t, c["faster8"] - 0.1, c["faster8"] + 0.3)))

    def _optical_clock(self, cv, t, x, base_y, col, alpha, name, faster=False):
        if alpha <= 0.003:
            return
        cv.rect(x - 86, base_y - 30, 172, 30, (0.10, 0.14, 0.24), alpha=alpha, radius=5)
        cv.rect(x - 86, base_y - 30, 172, 30, col, alpha=alpha * 0.7, fill=False, width=2, radius=5)
        cv.line([(x, base_y - 30), (x, base_y - 70)], L.DIM, width=5, alpha=alpha)
        iy = base_y - 110
        cv.line([(x - 110, iy), (x + 110, iy)], col, width=3, alpha=alpha * 0.8, glow=0.7)
        for k, (rx, ry, ang) in enumerate(((54, 19, 0.3), (54, 19, -0.3), (37, 37, 0.0))):
            c = cv.b
            c.save()
            c.translate(x, iy)
            c.rotate(ang + t * (0.9 if faster else 0.8) * (1 if k % 2 else -1) * 0.4)
            c.scale(rx, ry)
            c.arc(0, 0, 1, 0, 2 * math.pi)
            c.restore()
            c.set_source_rgba(*col, alpha * 0.6)
            c.set_line_width(2.0)
            c.stroke()
        pulse = 0.5 + 0.5 * math.sin(t * (13.0 if faster else 11.0))
        cv.circle(x, iy, 11 + 2.5 * pulse, L.WHITE, alpha=alpha, glow=1.0)
        cv.radial(x, iy, 58, col, alpha=alpha * 0.5, glow=0.8)
        cv.text(f"CLOCK {name}", x, base_y + 30 if name == "B" and base_y < 1150 else base_y + 80,
                26, font=L.MONO_XB, color=col, alpha=alpha * 0.95, tracking=0.15, shadow=0.7)

    def _traces(self, cv, t, alpha, speedup, highlight):
        x0, x1 = 175, 690
        top, bot = 430, 650
        rows = ((505, L.AMBER, "A", 0.0), (590, L.CYAN, "B", speedup))
        cv.rect(110, top, 845, bot - top, (0.03, 0.06, 0.13), alpha=alpha * 0.8, radius=14)
        cv.rect(110, top, 845, bot - top, L.FAINT, alpha=alpha, fill=False, width=1.5, radius=14)
        cv.text("TICK RATE", 132, top + 26, 20, font=L.MONO, anchor="left", color=L.DIM, alpha=alpha, tracking=0.25)
        cv.text("spacing exaggerated", 690, top + 26, 18, font=L.MONO, anchor="right", color=L.DIM,
                alpha=alpha * 0.8)
        for y, col, name, sp in rows:
            cv.text(name, 145, y, 30, font=L.MONO_XB, anchor="center", color=col, alpha=alpha)
            period = 40.0 * (1 - 0.18 * sp)
            off = (t * 110.0) % period
            x = x0 + off
            while x < x1:
                cv.line([(x, y - 26), (x, y + 26)], col, width=3, alpha=alpha * 0.9,
                        glow=0.4 if name == "B" else 0)
                x += period
            cv.line([(x0, y), (x1, y)], col, width=1, alpha=alpha * 0.35)
        cv.line([(712, top + 18), (712, bot - 18)], L.FAINT, width=1.5, alpha=alpha)
        if highlight > 0:
            cv.rect(114, 548, 590, 84, L.CYAN, alpha=0.10 * highlight, radius=10)
            pop = 1 + 0.2 * (1 - ease_out_back(prog(highlight, 0, 1)))
            with cv.transform(s=pop, cx=832, cy=560):
                cv.text("B TICKS", 832, 530, 40, font=L.DISPLAY, color=L.CYAN, alpha=highlight, glow=0.5)
                cv.text("FASTER", 832, 580, 48, font=L.DISPLAY, color=L.CYAN, alpha=highlight, glow=0.7)
            cv.text("shift: 4 parts in 10¹⁷", 832, 626, 20, font=L.MONO, color=L.WHITE, alpha=highlight * 0.85)

    def s_gps(self, cv, t):
        c = self.c
        s0, s1 = c["sc_gps"]
        zoom = ease_in_out(prog(t, c["orbit"] - 0.2, c["orbit"] + 0.8))
        # phase 1: the phone
        pa = 1 - smooth(prog(t, c["orbit"], c["orbit"] + 0.6))
        if pa > 0:
            ps = lerp(1.0, 0.05, ease_in_cubic(zoom))
            py = lerp(800, 690, zoom)
            for k, sx in enumerate((190, 540, 890)):
                p0 = (sx, 250 - 40 * (k == 1))
                p1 = (540, py - 330 * ps)
                cv.line([p0, p1], L.CYAN, width=2, alpha=0.35 * pa, dash=[4, 10])
                for j in range(3):
                    f = ((t * 0.9 + j / 3 + k * 0.17) % 1.0)
                    cv.circle(lerp(p0[0], p1[0], f), lerp(p0[1], p1[1], f), 5, L.CYAN, alpha=pa * (1 - f) * 0.9,
                              glow=0.8)
            phone(cv, 540, py, ps, t, alpha=pa)
        # phase 2: Earth + orbit + satellites
        ea = smooth(prog(t, c["orbit"] - 0.1, c["orbit"] + 0.5))
        if ea > 0:
            er = lerp(900, 230, ease_out_cubic(zoom))
            ey = lerp(1500, 920, ease_out_cubic(zoom))
            rx, ry, tilt = 430, 125, -0.22
            sats = []
            for k in range(4):
                th = t * 0.42 + k * math.pi / 2
                ox, oy = rx * math.cos(th), ry * math.sin(th)
                sx = 540 + ox * math.cos(tilt) - oy * math.sin(tilt)
                sy = ey + ox * math.sin(tilt) + oy * math.cos(tilt)
                sats.append((math.sin(th), sx, sy, th))
            self._orbit(cv, ey, rx, ry, tilt, ea, back=True)
            for s, sx, sy, th in sats:
                if s < 0:
                    satellite(cv, sx, sy, 0.42, ang=th * 0.3, alpha=ea * 0.55)
            self.earth.draw(cv, 540, ey, er, lon0=1.3 + 0.12 * t, tilt=0.35, alpha=ea)
            self._orbit(cv, ey, rx, ry, tilt, ea, back=False)
            for s, sx, sy, th in sats:
                if s >= 0:
                    satellite(cv, sx, sy, 0.5, ang=th * 0.3, alpha=ea)
            la = smooth(prog(t, c["gps"], c["gps"] + 0.4))
            cv.text("GPS ORBIT · 20,200 km UP", 540, ey + 262, 26, font=L.MONO_XB, color=L.CYAN, alpha=la * 0.9,
                    tracking=0.15, shadow=0.8)
        # readout
        ra = smooth(prog(t, c["38"] - 0.15, c["38"] + 0.25))
        if ra > 0:
            v = 38 * ease_out_expo(prog(t, c["38"] - 0.1, c["38"] + 0.6))
            pop = 1 + 0.15 * (1 - ease_out_back(prog(t, c["38"] - 0.1, c["38"] + 0.4)))
            with cv.transform(s=pop, cx=540, cy=350):
                cv.text(f"+{v:0.0f} µs", 540, 350, 150, font=L.DISPLAY, color=L.CYAN, alpha=ra, glow=0.55)
            cv.text("GAINED PER DAY vs. CLOCKS ON THE GROUND", 540, 455, 24, font=L.MONO, color=L.WHITE,
                    alpha=ra * 0.85, tracking=0.12)
            ba = smooth(prog(t, c["second"] - 0.1, c["second"] + 0.3))
            cv.text("+45 µs  weaker gravity", 540, 522, 34, font=L.MONO_XB, color=L.CYAN, alpha=ba)
            cv.text(" −7 µs  orbital speed ", 540, 572, 34, font=L.MONO_XB, color=L.AMBER, alpha=ba)

    def _orbit(self, cv, cy, rx, ry, tilt, alpha, back):
        pts = []
        rng = (math.pi, 2 * math.pi) if back else (0, math.pi)
        for k in range(61):
            th = lerp(rng[0], rng[1], k / 60)
            ox, oy = rx * math.cos(th), ry * math.sin(th)
            pts.append((540 + ox * math.cos(tilt) - oy * math.sin(tilt), cy + ox * math.sin(tilt) + oy * math.cos(tilt)))
        cv.line(pts, L.CYAN, width=2.2, alpha=alpha * (0.35 if back else 0.75), glow=0 if back else 0.5)

    def s_light(self, cv, t):
        c = self.c
        s0, s1 = c["sc_light"]
        shrink = ease_in_out(prog(t, c["L12"] - 0.3, c["L12"] + 0.6))
        # map panel moves down and shrinks when the satellite arrives
        my = lerp(560, 960, shrink)
        mh = lerp(500, 330, shrink)
        mx, mw = 90, 900
        pa = smooth(prog(t, s0, s0 + 0.4))
        self._map(cv, mx, my, mw, mh, pa)
        lp = ease_in_out(prog(t, c["light"], c["km_end"]))
        x_start, x_end = mx + 50, mx + mw - 50
        ly = my + mh * 0.5
        xl = lerp(x_start, x_end, lp)
        if lp > 0:
            fade = 1 - 0.75 * smooth(prog(t, c["L12"] - 0.2, c["L12"] + 0.4))
            cv.line([(x_start, ly), (xl, ly)], L.WHITE, width=4, alpha=pa * fade, glow=1.0)
            cv.circle(xl, ly, 12, L.WHITE, alpha=pa * fade * (1.0 if lp < 1 else 0.6), glow=1.0)
            cv.radial(xl, ly, 60, L.CYAN, alpha=0.6 * pa * fade, glow=1.0)
        # pins: true position vs. 38 µs-late ranging
        pin_a = smooth(prog(t, c["km_end"] - 0.2, c["km_end"] + 0.2))
        snap = ease_in_out(prog(t, c["einstein12"] - 0.1, c["einstein12"] + 0.5))
        self._pin(cv, x_start, ly, L.MINT, pa * smooth(prog(t, c["light"], c["light"] + 0.3)), "TRUE")
        if pin_a > 0:
            gx = lerp(x_end, x_start, snap)
            self._pin(cv, gx, ly, mix(L.MAGENTA, L.MINT, snap), pa * pin_a * (1 - 0.0 * snap),
                      "38 µs OFF" if snap < 0.5 else "")
        # counters
        ca = pa * (1 - smooth(prog(t, c["L12"] - 0.3, c["L12"] + 0.2)))
        if ca > 0:
            us = 38 * lp
            km = 11.4 * lp
            cv.text(f"{us:4.1f} µs", 540, 330, 120, font=L.DISPLAY, color=L.CYAN, alpha=ca, glow=0.5)
            cv.text("OF TRAVEL TIME FOR LIGHT", 540, 425, 24, font=L.MONO, color=L.DIM, alpha=ca, tracking=0.2)
            ka = ca * smooth(prog(t, c["light"] + 0.2, c["light"] + 0.6))
            cv.text(f"= {km:4.1f} km", 540, my + mh + 70, 64, font=L.DISPLAY, color=L.WHITE, alpha=ka,
                    glow=0.25)
        # satellite + clock retune
        sa = smooth(prog(t, c["L12"] - 0.1, c["L12"] + 0.5))
        if sa > 0:
            satellite(cv, 540, lerp(500, 420, ease_out_cubic(sa)), 1.7, ang=0.08 * math.sin(t * 0.8), alpha=sa)
            rp = prog(t, c["built"] - 0.1, c["built"] + 0.9)
            target = "10.22999999543"
            start = "10.23000000000"
            nd = int(len(target) * ease_out_cubic(rp))
            shown = target[:nd] + start[nd:] if rp > 0 else "10.23"
            cv.text(f"{shown} MHz", 540, 650, 54, font=L.MONO_XB, color=L.WHITE, alpha=sa, glow=0.15)
            cv.text("ONBOARD CLOCK TUNED SLOW BEFORE LAUNCH", 540, 712, 22, font=L.MONO, color=L.DIM,
                    alpha=sa * smooth(prog(t, c["built"], c["built"] + 0.4)), tracking=0.12)
            ok = smooth(prog(t, c["einstein12"] - 0.05, c["einstein12"] + 0.3))
            if ok > 0:
                pop = 1 + 0.2 * (1 - ease_out_back(prog(t, c["einstein12"] - 0.05, c["einstein12"] + 0.4)))
                with cv.transform(s=pop, cx=540, cy=800):
                    cv.rect(540 - 250, 770, 500, 60, L.MINT, alpha=0.12 * ok, radius=30)
                    cv.rect(540 - 250, 770, 500, 60, L.MINT, alpha=0.9 * ok, fill=False, width=2.5, radius=30,
                            glow=0.6)
                    cv.text("✓  RELATIVITY CORRECTED", 540, 800, 30, font=L.DISPLAY, color=L.MINT, alpha=ok,
                            glow=0.4)

    def _map(self, cv, x, y, w, h, alpha):
        if alpha <= 0.003:
            return
        cv.rect(x, y, w, h, (0.03, 0.07, 0.14), alpha=alpha * 0.92, radius=18)
        rng_seed = 11
        import numpy as np
        rng = np.random.default_rng(rng_seed)

        def clip(c):
            from engine.gfx import rounded_rect
            c.new_path()
            rounded_rect(c, x, y, w, h, 18)

        with cv.clip(clip):
            # contour rings (terrain)
            for k in range(5):
                cx_, cy_ = x + rng.uniform(0.1, 0.9) * w, y + rng.uniform(0.15, 0.85) * h
                for j in range(1, 6):
                    rr = j * 26
                    cv.circle(cx_, cy_, rr * rng.uniform(0.9, 1.1), (0.25, 0.45, 0.75), alpha=alpha * 0.18,
                              fill=False, width=1.4)
            for k in range(9):
                yy = y + rng.uniform(0, h)
                cv.curve((x, yy), (x + w * 0.3, yy + rng.uniform(-80, 80)), (x + w * 0.7, yy + rng.uniform(-80, 80)),
                         (x + w, yy + rng.uniform(-60, 60)), (0.3, 0.45, 0.7), width=2, alpha=alpha * 0.35)
            for k in range(7):
                xx = x + rng.uniform(0, w)
                cv.curve((xx, y), (xx + rng.uniform(-60, 60), y + h * 0.4), (xx + rng.uniform(-60, 60), y + h * 0.6),
                         (xx + rng.uniform(-40, 40), y + h), (0.3, 0.45, 0.7), width=2, alpha=alpha * 0.3)
        cv.rect(x, y, w, h, L.FAINT, alpha=alpha, fill=False, width=1.5, radius=18)
        # scale bar
        cv.line([(x + 50, y + h - 30), (x + w - 50, y + h - 30)], L.DIM, width=2, alpha=alpha * 0.8)
        for k in range(12):
            xx = lerp(x + 50, x + w - 50, k / 11.4) if k <= 11 else x + w - 50
            cv.line([(xx, y + h - 38), (xx, y + h - 22)], L.DIM, width=2, alpha=alpha * 0.8)
        cv.text("0", x + 50, y + h - 58, 18, font=L.MONO, color=L.DIM, alpha=alpha)
        cv.text("11.4 km", x + w - 50, y + h - 58, 18, font=L.MONO, color=L.DIM, alpha=alpha)

    def _pin(self, cv, x, y, col, alpha, label):
        if alpha <= 0.003:
            return
        c = cv.b
        top = y - 74
        for ctx, a in ((cv.b, alpha), (cv.g, alpha * 0.8)):
            ctx.new_path()
            ctx.move_to(x, y)
            ctx.curve_to(x - 14, y - 26, x - 28, top + 30, x - 28, top + 26)
            ctx.arc(x, top + 26, 28, math.pi, 2 * math.pi)
            ctx.curve_to(x + 28, top + 30, x + 14, y - 26, x, y)
            ctx.close_path()
            ctx.set_source_rgba(*col, a)
            ctx.fill()
        cv.circle(x, top + 26, 10, (0.03, 0.06, 0.12), alpha=alpha)
        if label:
            cv.text(label, x, top - 26, 22, font=L.MONO_XB, color=col, alpha=alpha, tracking=0.1)

    def s_dive(self, cv, t):
        c = self.c
        s0, s1 = c["sc_dive"]
        ex, ey, R = 540, 1000, 320
        push = ease_in_out(prog(t, s0, c["down13"] + 0.2))
        shake = window(t, c["down13"], c["down13"] + 0.4, 0.05, 0.5) * 6 + \
            window(t, c["two"], c["two"] + 0.25, 0.02, 0.5) * 9
        sx = shake * math.sin(t * 71.0)
        sy = shake * math.cos(t * 53.0)
        cv.aberration = window(t, c["two"], c["two"] + 0.1, 0.02, 0.4) * 4
        cut = ease_in_out(prog(t, c["down13"] - 0.05, c["down13"] + 0.75))
        cv.flash = max(cv.flash, 0.22 * window(t, c["down13"], c["down13"] + 0.05, 0.03, 0.35))
        focus = smooth(prog(t, c["center"] - 0.3, c["center"] + 0.4))   # dim the core glow for the clocks
        with cv.transform(tx=sx, ty=sy, s=lerp(0.78, 1.0, push), cx=ex, cy=ey):
            if cut > 0:
                cross_section(cv, ex, ey, R, t, alpha=1.0, glow=smooth(cut) * lerp(0.8, 0.3, focus))
            if cut < 1:
                a0 = -math.pi / 2
                a1 = a0 + 2 * math.pi * cut

                def outside(ctx):
                    ctx.new_path()
                    ctx.move_to(ex, ey)
                    ctx.arc(ex, ey, R * 1.25, a1, a0 + 2 * math.pi)
                    ctx.close_path()

                if cut > 0:
                    with cv.clip(outside):
                        self.earth.draw(cv, ex, ey, R, lon0=2.0 + 0.1 * t, tilt=0.3, alpha=1.0)
                    cv.line([(ex, ey), (ex + R * 1.06 * math.cos(a1), ey + R * 1.06 * math.sin(a1))], L.WHITE,
                            width=4, alpha=1.0, glow=1.0)
                else:
                    self.earth.draw(cv, ex, ey, R, lon0=2.0 + 0.1 * t, tilt=0.3, alpha=1.0)
            else:
                atmosphere(cv, ex, ey, R, 0.6, color=(1.0, 0.55, 0.3), width=0.07)
            # layer labels: points along one ray, labels level with their points (no crossings)
            ang = math.radians(232)
            for k, (fr, _, _, name) in enumerate(LAYERS):
                la = window(t, c["down13"] + 0.75 + 0.16 * k, c["center"] - 0.25, 0.25, 0.4)
                if la <= 0:
                    continue
                rr = {0: R * 0.997, 1: R * 0.77, 2: R * 0.37, 3: R * 0.06}[k]
                px, py = ex + rr * math.cos(ang), ey + rr * math.sin(ang)
                lx = 96
                tw = text_width(cv.b, name, 30, L.MONO_XB, 0.1)
                draw_to = lerp(lx + tw + 14, px, ease_out_cubic(prog(t, c["down13"] + 0.75 + 0.16 * k,
                                                                      c["down13"] + 1.2 + 0.16 * k)))
                cv.line([(lx + tw + 14, py), (draw_to, py)], L.WHITE, width=2, alpha=0.8 * la)
                cv.circle(px, py, 6, L.WHITE, alpha=la, glow=0.8)
                cv.text(name, lx, py, 30, font=L.MONO_XB, anchor="left", color=L.WHITE, alpha=la, tracking=0.1,
                        shadow=1.0, outline=(0.03, 0.02, 0.05), outline_w=6)
            # gravity-well rings flowing inward, slowing near the centre
            wa = window(t, c["deep"], c["two"] + 0.2, 0.3, 0.5)
            for k in range(5):
                f = ((t * 0.45 + k / 5) % 1.0)
                rr = R * (1 - ease_out_cubic(f) * 0.9)
                cv.circle(ex, ey, rr, (1.0, 0.85, 0.6), alpha=wa * 0.35 * math.sin(math.pi * f), fill=False,
                          width=2.5, glow=0.5)
            # clocks: surface vs centre
            ca = smooth(prog(t, c["center"] - 0.1, c["center"] + 0.35))
            if ca > 0:
                cv.circle(ex, ey, 62, (0.04, 0.03, 0.06), alpha=0.85 * ca)
                ring_clock(cv, ex, ey, 50, t, rate=0.55, color=L.AMBER, alpha=ca, glow=0.6, pulse_every=0.9)
                cv.text("CENTER", ex, ey + 92, 26, font=L.MONO_XB, color=(0.06, 0.04, 0.08), alpha=ca, tracking=0.14)
                ring_clock(cv, ex, ey - R - 2, 40, t, rate=1.45, color=L.CYAN, alpha=ca, glow=1.0, pulse_every=0.5)
                cv.text("SURFACE", ex + 58, ey - R - 2, 26, font=L.MONO_XB, anchor="left", color=L.CYAN,
                        alpha=ca, tracking=0.12, shadow=0.9)
            # shockwave on the reveal
            sw = prog(t, c["two"], c["two"] + 0.9)
            if 0 < sw < 1:
                cv.circle(ex, ey, R * 0.2 + R * 1.2 * ease_out_cubic(sw), (1.0, 0.9, 0.7), alpha=0.8 * (1 - sw),
                          fill=False, width=6 * (1 - sw) + 1, glow=1.0)
        cv.flash = max(cv.flash, 0.18 * window(t, c["two"], c["two"] + 0.04, 0.02, 0.35))
        # the number
        na = smooth(prog(t, c["two"] - 0.1, c["two"] + 0.15))
        if na > 0:
            v = 2.5 * ease_out_expo(prog(t, c["two"] - 0.05, c["two"] + 0.75))
            pop = 1 + 0.35 * (1 - ease_out_back(prog(t, c["two"] - 0.1, c["two"] + 0.45)))
            num, unit = f"{v:0.1f}", "YEARS"
            wn = text_width(cv.b, "2.5", 220, L.DISPLAY)
            wu = text_width(cv.b, unit, 92, L.DISPLAY)
            gap = 26
            x0 = 540 - (wn + gap + wu) / 2
            with cv.transform(s=pop, cx=540, cy=330):
                cv.text(num, x0, 330, 220, font=L.DISPLAY, anchor="left", color=(1.0, 0.93, 0.8), alpha=na, glow=0.7)
                cv.text(unit, x0 + wn + gap, 368, 92, font=L.DISPLAY, anchor="left", color=L.WHITE, alpha=na,
                        glow=0.2)
            ya = smooth(prog(t, c["younger"] - 0.05, c["younger"] + 0.25))
            yp = 1 + 0.2 * (1 - ease_out_back(prog(t, c["younger"] - 0.05, c["younger"] + 0.35)))
            with cv.transform(s=yp, cx=540, cy=485):
                cv.text("YOUNGER", 540, 485, 100, font=L.DISPLAY, color=L.AMBER, alpha=ya, glow=0.6)
            fa = smooth(prog(t, c["surface"], c["surface"] + 0.4))
            cv.text("CENTER vs. SURFACE · ADDED UP OVER 4.5 BILLION YEARS", 540, 565, 22, font=L.MONO,
                    color=L.WHITE, alpha=fa * 0.85, tracking=0.04)
            fy = smooth(prog(t, c["L14end"] + 0.1, c["L14end"] + 0.45))
            if fy > 0:
                tw = cv.text("FEYNMAN'S GUESS: “A DAY OR TWO”", 540, 610, 24, font=L.MONO_XB, color=L.MAGENTA,
                             alpha=fy, tracking=0.04, shadow=0.9)
                sp = ease_out_cubic(prog(t, c["L14end"] + 0.4, c["L14end"] + 0.75))
                cv.line([(540 - tw / 2 - 8, 610), (540 - tw / 2 - 8 + (tw + 16) * sp, 610)], L.MAGENTA,
                        width=3, alpha=fy)

    def s_you(self, cv, t):
        c = self.c
        s0, s1 = c["sc_you"]
        a = smooth(prog(t, s0 - 0.2, s0 + 0.4))
        self._limb(cv, t, alpha=a)
        self._figure(cv, t, reveal=ease_out_cubic(prog(t, s0 + 0.15, c["L15"] + 0.8)))
        pa = smooth(prog(t, c["L15"] + 0.3, c["L15"] + 0.9))
        self._probe(cv, t, "head", alpha=pa, draw_p=prog(t, c["L15"] + 0.3, c["L15"] + 1.1), label=False)
        self._probe(cv, t, "feet", alpha=pa, draw_p=prog(t, c["L15"] + 0.4, c["L15"] + 1.2), label=False)
        self._lifetime(cv, t, 1.0)

    def _lifetime(self, cv, t, alpha):
        c = self.c
        la = alpha * smooth(prog(t, c["lifetime"] - 0.3, c["lifetime"] + 0.2))
        if la <= 0:
            return
        fill = ease_in_out(prog(t, c["lifetime"], c["second16"] + 0.3))
        x0, x1, y = TXT_X, 590, 760
        cv.text("HEAD vs. FEET", x0, 470, 28, font=L.MONO_XB, anchor="left", color=L.DIM, alpha=la, tracking=0.2)
        d = f"{int(300 * fill):09d}"
        cv.text(f"+0.{d[:3]} {d[3:6]} {d[6:]}", x0, 552, 58, font=L.MONO_XB, anchor="left", color=L.CYAN,
                alpha=la, glow=0.5)
        cv.text("s", x0 + text_width(cv.b, "+0.000 000 000 ", 58, L.MONO_XB), 556, 40, font=L.MONO_XB,
                anchor="left", color=L.CYAN, alpha=la * 0.8)
        cv.text(f"AGE {int(80 * fill):2d}", x0, 690, 32, font=L.MONO_XB, anchor="left", color=L.WHITE, alpha=la)
        cv.text("80 YRS", x1, 690, 24, font=L.MONO, anchor="right", color=L.DIM, alpha=la)
        cv.rect(x0, y - 9, x1 - x0, 18, L.FAINT, alpha=la, radius=9)
        cv.rect(x0, y - 9, max(18, (x1 - x0) * fill), 18, L.CYAN, alpha=la, radius=9, glow=0.6)
        ba = la * smooth(prog(t, c["few"] - 0.1, c["few"] + 0.4))
        cv.text("≈ a few hundred", x0, 850, 38, font=L.UI, anchor="left", color=L.WHITE, alpha=ba, shadow=0.6)
        cv.text("billionths of a second", x0, 900, 38, font=L.UI, anchor="left", color=L.WHITE, alpha=ba,
                shadow=0.6)

    def s_outro(self, cv, t):
        c = self.c
        s0, s1 = c["sc_outro"]
        self._limb(cv, t)
        self._figure(cv, t)
        # "Tiny." — the counter collapses into a point
        tp = ease_in_cubic(prog(t, c["tiny"] - 0.05, c["tiny"] + 0.55))
        rp = prog(t, c["real"] - 0.05, c["real"] + 0.4)
        back = prog(t, c["which"] - 0.2, c["which"] + 1.4)
        if tp < 1:
            with cv.transform(s=lerp(1.0, 0.02, tp), cx=200, cy=560):
                self._lifetime(cv, max(t, c["second16"] + 0.31), 1 - tp * 0.3)
        dot_a = smooth(prog(t, c["tiny"] + 0.35, c["tiny"] + 0.55)) * (1 - smooth(prog(t, c["which"] - 0.3, c["which"])))
        if dot_a > 0:
            cv.circle(200, 560, 7, L.CYAN, alpha=dot_a, glow=1.0)
            if rp > 0:
                cv.circle(200, 560, 7 + 90 * ease_out_cubic(rp), L.MINT, alpha=dot_a * (1 - rp) * 0.9, fill=False,
                          width=4, glow=1.0)
            ma = smooth(prog(t, c["real"], c["real"] + 0.3)) * (1 - smooth(prog(t, c["which"] - 0.3, c["which"])))
            cv.text("✓ MEASURED", 240, 560, 46, font=L.DISPLAY, anchor="left", color=L.MINT, alpha=ma, glow=0.5)
            cv.text("NIST 2010: 33 cm", 242, 616, 24, font=L.MONO_XB, anchor="left", color=L.WHITE, alpha=ma * 0.9)
            cv.text("JILA 2022: just 1 mm", 242, 652, 24, font=L.MONO_XB, anchor="left", color=L.WHITE,
                    alpha=ma * 0.9)
        # probes stay alive the whole time
        self._probe(cv, t, "head", draw_p=1.0)
        self._probe(cv, t, "feet", draw_p=1.0)
        # "Which means, right now…" — the headline flies back in = the very first frame
        if back > 0:
            ks = [ease_out_expo(prog(back, 0.0 + 0.11 * k, 0.45 + 0.11 * k)) for k in range(5)]
            a = [smooth(prog(back, 0.0 + 0.11 * k, 0.25 + 0.11 * k)) for k in range(5)]
            self._headline(cv, t, a_head=a[0], a_mid=(a[1], a[2], a[3]), a_feet=a[4],
                           offs=tuple(-160 * (1 - k) for k in ks))


def make_episode(timeline_path, **opts):
    return Episode(timeline_path, **opts)
