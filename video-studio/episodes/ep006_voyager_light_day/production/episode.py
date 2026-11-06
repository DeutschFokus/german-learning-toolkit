"""EP006 — It Would Hear You Tomorrow (Voyager 1, one light-day from home).

Narrated by the creator (no AI voice in any deliverable). Until his take
exists, animation timing comes from a scratch read (build/timeline_scratch.json);
`build.py human take.wav` re-times everything to the real voice.

Journey: Voyager 1 in deep space ("say hello now, it hears you tomorrow") ->
the 1977 launch -> a light pulse needing a full day to reach it (Nov 18, 2026)
-> a fridge-bulb transmitter heard by a 70 m dish -> it turns around for the
pale blue dot -> the golden record (music, 55 languages, a heartbeat) ->
Ann Druyan's brainwaves, recorded days after she and Carl Sagan fell in love
-> 40,000 years to another star, still carrying their love story -> still
listening (loop).

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

from engine import space  # noqa: E402
from engine.captions import Captions  # noqa: E402
from engine.gfx import (H, L, W, Canvas, background, clamp, ease_in_cubic, ease_in_out,  # noqa: E402
                        ease_out_back, ease_out_cubic, ease_out_expo, lerp, mix, prog, smooth, window)
from engine.hud import htext, ucard, uline, ui_scope  # noqa: E402
from engine.postfx import Post  # noqa: E402
from engine.timeline import Timeline  # noqa: E402

GOLD = (1.0, 0.78, 0.35)
RX = 680.0                                     # rocket x
PINK = (1.0, 0.45, 0.65)
VOY = dict(x=560.0, y=1030.0, scale=118.0, yaw=0.50, pitch=-0.95, roll=0.10)
SUN = (540.0, 1180.0)
LD_R = 520.0                                   # one light-day on the map, px (173 AU)
AU = LD_R / 173.1
ACCENTS = {"L01": GOLD, "L02": L.AMBER, "L03": L.CYAN, "L04": L.AMBER, "L05": L.CYAN, "L06": GOLD, "L07": GOLD,
           "L08": PINK, "L09": PINK, "L10": L.AMBER, "L11": L.CYAN}
CONTINUOUS = set()
X_IN = {"outro": 0.35}
X_OUT = {}
GREETINGS = ["Hello", "Hola", "Bonjour", "Merhaba", "Привет", "こんにちは", "Ciao", "Olá", "Salve", "Hallo", "Hej",
             "Cześć", "Szia", "Γεια σας", "Xin chào", "Ahoj", "Bună"]


class Episode:
    def __init__(self, timeline_path, captions=True, grain=0.007, guide=False):
        self.T = Timeline(timeline_path)
        self.fps = self.T.fps
        self.duration = self.T.duration
        self.post = Post(grain=grain)
        self.caps = Captions(self.T, accent_by_line=ACCENTS) if captions else None
        self.guide = guide
        self.sky = space.MilkyWay(seed=11)
        self.voy = space.Voyager3D()
        self.rec = space.GoldenRecord()
        rng = np.random.default_rng(21)
        self.smoke = [(rng.uniform(-1, 1), rng.uniform(0, 1), rng.uniform(0.6, 1.4), rng.uniform(0, 6.28))
                      for _ in range(140)]
        st = self.T.scene_starts()
        self.scenes = [(sid, s0, st[i + 1][1] if i + 1 < len(st) else self.duration)
                       for i, (sid, s0) in enumerate(st)]
        self.c = self._cues()

    def _cues(self):
        T = self.T
        w = lambda l, k: T.word(l, k).start  # noqa: E731
        c = {"sc_" + sid: (s0, s1) for sid, s0, s1 in self.scenes}
        for lid in [l["id"] for l in T.lines]:
            c[lid] = T.line(lid).start
            c[lid + "end"] = T.line(lid).end
        c.update({
            "hello": w("L01", "hello"), "now1": w("L01", "now,"), "hear": w("L01", "hear"), "tomorrow": w("L01", "tomorrow."),
            "left": w("L02", "left"), "y1977": w("L02", "1977."),
            "nov18": T.word("L03", 1).start, "crosses": w("L03", "crosses"), "full": w("L03", "full"),
            "lightday": w("L03", "light-day"), "home3": w("L03", "home."),
            "calls": w("L04", "calls"), "power": w("L04", "power"), "fridge": w("L04", "fridge"), "bulb": w("L04", "bulb."),
            "y1990": w("L05", "1990,"), "turned": w("L05", "turned"), "photo": w("L05", "photo"), "pale": w("L05", "pale"),
            "dot": w("L05", "dot."),
            "golden": w("L06", "golden"), "whoever": w("L06", "whoever"),
            "music": w("L07", "Music."), "greetings": w("L07", "Greetings"), "n55": w("L07", "55"),
            "heartbeat": w("L07", "heartbeat."),
            "brainwaves": w("L08", "brainwaves"), "fallen": w("L08", "fallen"), "love8": w("L08", "love."),
            "ann": w("L09", "Ann"), "loved": w("L09", "loved,"), "carl": w("L09", "Carl"), "led": w("L09", "led"),
            "n40000": w("L10", "40,000"), "drift": w("L10", "drift"), "star": w("L10", "star,"),
            "carrying": w("L10", "carrying"), "story": w("L10", "story."),
            "now11": w("L11", "now..."), "listening": w("L11", "listening."),
        })
        return c

    # ------------------------------------------------------------------ frame
    def frame(self, i):
        t = i / self.fps
        cv = Canvas()
        self.draw(cv, t)
        return self.post.finish(cv, i)

    def draw(self, cv, t):
        background(cv, t, haze=(0.5, 0.40), haze_color=(0.08, 0.12, 0.30), haze_amt=0.6)
        n = len(self.scenes)
        for k, (sid, s0, s1) in enumerate(self.scenes):
            first, last = k == 0, k == n - 1
            Xi = 0.0 if (first or sid in CONTINUOUS) else X_IN.get(sid, 0.22)
            Xo = 0.0 if (last or (not last and self.scenes[k + 1][0] in CONTINUOUS)) else X_OUT.get(sid, 0.22)
            if not (s0 - Xi <= t < s1 + Xo):
                continue
            a, sc, ty, cx, cy = 1.0, 1.0, 0.0, W / 2, H / 2
            if Xi and t < s0 + Xi:
                p = prog(t, s0 - Xi, s0 + Xi)
                a, sc, ty = smooth(p), 0.97 + 0.03 * ease_out_cubic(p), 60 * (1 - ease_out_cubic(p))
            if Xo and t > s1 - Xo:
                p = prog(t, s1 - Xo, s1 + Xo)
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

    # ================================================================== Voyager in deep space (hook, outro)
    def _voyager_shot(self, cv, t, record_glow=0.0, alpha=1.0, pulses=1.0):
        Lp = self.duration
        self.sky.draw(cv, t, alpha=alpha, loop=Lp)
        yaw = VOY["yaw"] + 0.05 * math.sin(2 * math.pi * t / Lp)
        pitch = VOY["pitch"] + 0.03 * math.sin(2 * math.pi * 2 * t / Lp + 1.0)
        # a "hello" travelling up from the lower left (toward Earth), every 3 s
        if pulses > 0:
            ox_, oy_ = -40.0, 1800.0                       # toward home (the Sun, Earth)
            cv.radial(ox_ + 70, oy_ - 60, 110, (1.0, 0.92, 0.75), alpha=alpha * pulses * 0.55, glow=0.9)
            for k in range(2):
                ph = (t / 3.0 + k / 2) % 1.0
                rr = 160 + 1000 * ph
                fade = math.sin(math.pi * ph) ** 1.2
                for j in range(3):
                    cv.arc(ox_, oy_, rr - j * 16, -1.30, -0.22, color=L.CYAN, alpha=alpha * pulses * fade * (0.55 - 0.15 * j),
                           width=3.2 - j * 0.8, glow=0.7)
                hx, hy = ox_ + math.cos(-0.78) * rr, oy_ + math.sin(-0.78) * rr
                htext(cv, "hello", hx + 26, hy + 22, 26, color=L.CYAN, alpha=alpha * pulses * fade * 0.9,
                      font=L.MONO_XB, anchor="left", glow=0.4, shadow=0.6)
        self.voy.draw(cv, VOY["x"], VOY["y"], VOY["scale"], yaw=yaw, pitch=pitch, roll=VOY["roll"], alpha=alpha,
                      record_glow=record_glow, t=t)

    def _headline(self, cv, alphas=(1, 1, 1), offs=(0, 0, 0)):
        rows = [("SAY HELLO NOW,", 300, 64, L.WHITE, 0.0), ("IT HEARS YOU", 378, 64, L.WHITE, 0.0),
                ("TOMORROW", 490, 132, GOLD, 0.5)]
        for (txt, y, size, col, gl), a_, o in zip(rows, alphas, offs):
            htext(cv, txt, W / 2 + o, y, size, color=col, alpha=a_, glow=gl, shadow=0.85)

    def s_hook(self, cv, t):
        c = self.c
        self._voyager_shot(cv, t)
        pulse = window(t, c["tomorrow"] - 0.05, c["tomorrow"] + 0.3, 0.05, 0.6)
        ex = ease_in_cubic(prog(t, c["L01end"] - 0.05, c["L01end"] + 0.4))
        self._headline(cv, alphas=[1 - ex] * 3, offs=(0, -40 * ex, 40 * ex))
        if pulse > 0:
            htext(cv, "TOMORROW", W / 2, 490, 132, color=GOLD, alpha=0.0, glow_alpha=0.6 * pulse * (1 - ex))
        ta = window(t, 0.6, c["L01end"] - 0.2, 0.4, 0.3)
        if ta > 0:
            rem = 24 * 3600 - t
            hh, mm, ss = int(rem // 3600), int(rem % 3600 // 60), int(rem % 60)
            htext(cv, "YOUR 'HELLO' ARRIVES IN", 92, 1228, 20, color=(0.8, 0.86, 0.98), alpha=ta, font=L.MONO_XB,
                  anchor="left", tracking=0.1)
            htext(cv, f"{hh:02d}:{mm:02d}:{ss:02d}", 92, 1272, 44, color=L.CYAN, alpha=ta, font=L.MONO_XB, anchor="left",
                  glow=0.4)

    def s_outro(self, cv, t):
        c = self.c
        s0, s1 = c["sc_outro"]
        z = 1 + 0.25 * (1 - ease_out_cubic(prog(t, s0 - 0.35, s0 + 1.4)))
        with cv.transform(s=z, cx=VOY["x"], cy=VOY["y"]):
            self._voyager_shot(cv, t)
        la = smooth(prog(t, c["now11"] - 0.2, c["now11"] + 0.3)) * (1 - smooth(prog(t, c["listening"] + 0.4,
                                                                                    c["listening"] + 0.8)))
        if la > 0:
            htext(cv, "● RECEIVING COMMANDS", W / 2, 1210, 26, color=L.MINT, alpha=la, font=L.MONO_XB, glow=0.4,
                  tracking=0.1)
        back = prog(t, c["listening"] - 0.1, c["listening"] + 1.0)
        if back > 0:
            ks = [ease_out_expo(prog(back, 0.14 * k, 0.55 + 0.14 * k)) for k in range(3)]
            al = [smooth(prog(back, 0.14 * k, 0.35 + 0.14 * k)) for k in range(3)]
            self._headline(cv, alphas=al, offs=[-140 * (1 - k) for k in ks])

    # ================================================================== 1977
    def s_launch(self, cv, t):
        c = self.c
        s0, s1 = c["sc_launch"]
        ign = s0 + 0.35
        rise = ease_in_cubic(prog(t, ign + 0.4, s1 + 0.4))
        b = cv.b
        g = cairo.LinearGradient(0, 0, 0, H)
        g.add_color_stop_rgb(0, 0.02, 0.03, 0.08)
        g.add_color_stop_rgb(0.6, 0.12, 0.10, 0.20)
        g.add_color_stop_rgb(0.85, 0.55, 0.30, 0.25)
        g.add_color_stop_rgb(1, 0.85, 0.50, 0.30)
        b.rectangle(0, 0, W, H)
        b.set_source(g)
        b.fill()
        cam = 900 * rise                                  # camera follows the rocket up
        ground = 1560 + cam
        shake = window(t, ign, ign + 2.2, 0.05, 0.8) * 6
        with cv.transform(tx=shake * math.sin(t * 57), ty=shake * math.cos(t * 41)):
            cv.rect(0, ground, W, H, (0.03, 0.03, 0.05), alpha=1.0)
            # launch tower
            cv.rect(880, ground - 760, 60, 760, (0.08, 0.08, 0.10), alpha=1.0)
            for k in range(14):
                yy = ground - 50 * k
                cv.line([(880, yy), (940, yy - 50)], (0.20, 0.20, 0.24), width=2)
            ry = ground - 40 - 2600 * rise                # rocket base
            fl = clamp((t - ign) / 0.3)
            # exhaust: flame core and billowing smoke (deterministic puffs)
            for (u, v, sz, ph) in self.smoke:
                born = ign + v * (s1 - ign)
                age = t - born
                if age < 0 or fl <= 0:
                    continue
                py = lerp(ground - 30, ry + 120, clamp(v * 0.3)) + age * 30
                px = RX + u * (60 + 180 * clamp(age / 2.5)) + 30 * math.sin(age + ph)
                r = (40 + 120 * clamp(age / 3.0)) * sz
                a_ = 0.55 * clamp(1 - age / 6.0)
                col = mix((1.0, 0.75, 0.45), (0.62, 0.60, 0.62), clamp(age / 1.2))
                cv.radial(px, py, r, col, alpha=a_)
            if fl > 0:
                for dx in (-58, 58):
                    cv.radial(RX + dx, ry + 60, 120, (1.0, 0.85, 0.55), alpha=0.9 * fl, glow=1.2)
                    cv.poly([(RX + dx - 22, ry + 10), (RX + dx + 22, ry + 10), (RX + dx, ry + 260)], (1.0, 0.95, 0.80),
                            alpha=0.9 * fl, glow=1.0)
            self._titan(cv, RX, ry)
        ya = smooth(prog(t, c["y1977"] - 0.15, c["y1977"] + 0.2))
        htext(cv, "1977", 300, 330, 170, color=L.AMBER, alpha=ya, glow=0.5)
        htext(cv, "SEPT 5", 300, 440, 30, color=L.WHITE, alpha=ya, font=L.MONO_XB, tracking=0.12)
        htext(cv, "CAPE CANAVERAL", 300, 480, 26, color=(0.8, 0.86, 0.98), alpha=ya, font=L.MONO_XB, tracking=0.08)
        va = smooth(prog(t, c["L02"] - 0.1, c["L02"] + 0.3)) * (1 - ya)
        htext(cv, "VOYAGER 1", 300, 330, 80, color=L.WHITE, alpha=va, glow=0.15)

    def _titan(self, cv, x, y):
        """Titan IIIE-Centaur, base at y (stylised)."""
        k = 15.0
        core_w, core_h = 3.05 * k, 48.0 * k
        cv.rect(x - core_w / 2, y - core_h, core_w, core_h, (0.78, 0.76, 0.70), alpha=1.0)
        cv.poly([(x - core_w / 2, y - core_h), (x + core_w / 2, y - core_h), (x + core_w * 0.25, y - core_h - 70),
                 (x - core_w * 0.25, y - core_h - 70)], (0.92, 0.92, 0.95), alpha=1.0)
        for dx in (-1, 1):
            sx = x + dx * (core_w / 2 + 1.55 * k)
            cv.rect(sx - 1.55 * k, y - 25.9 * k, 3.1 * k, 25.9 * k, (0.90, 0.90, 0.92), alpha=1.0)
            cv.poly([(sx - 1.55 * k, y - 25.9 * k), (sx + 1.55 * k, y - 25.9 * k), (sx, y - 25.9 * k - 70)],
                    (0.92, 0.92, 0.95), alpha=1.0)
            for j in range(5):
                cv.rect(sx - 1.55 * k, y - 25.9 * k + 60 + j * 70, 3.1 * k, 8, (0.15, 0.15, 0.18), alpha=1.0)
        cv.rect(x - core_w / 2, y - core_h + 0.62 * core_h, core_w, 10, (0.2, 0.2, 0.22), alpha=1.0)

    # ================================================================== one light-day
    def s_lightday(self, cv, t):
        c = self.c
        s0, s1 = c["sc_lightday"]
        a = smooth(prog(t, s0 - 0.1, s0 + 0.4))
        self.sky.draw(cv, t, alpha=0.5 * a, loop=self.duration)
        zoom = math.exp(lerp(math.log(9.0), 0.0, ease_in_out(prog(t, s0, c["nov18"] + 1.6))))
        vang = math.radians(-62)
        vx, vy = SUN[0] + math.cos(vang) * LD_R * 0.995, SUN[1] + math.sin(vang) * LD_R * 0.995
        with cv.transform(s=zoom, cx=vx, cy=vy):
            cv.radial(*SUN, 70, (1.0, 0.9, 0.6), alpha=a, glow=1.2)
            cv.circle(*SUN, 6, L.WHITE, alpha=a, glow=1.0)
            for au, col in ((1.0, L.CYAN), (5.2, (0.9, 0.75, 0.55)), (9.5, (0.95, 0.85, 0.6)), (19.2, (0.6, 0.85, 0.9)),
                            (30.1, (0.4, 0.6, 1.0))):
                cv.circle(*SUN, au * AU, col, alpha=0.55 * a, fill=False, width=1.6 / zoom ** 0.3)
            # Voyager's path: Jupiter (1979), Saturn (1980), then out
            pts = []
            for k in range(120):
                u = k / 119
                ang = lerp(math.radians(-10), vang, smooth(clamp(u * 3)))
                rr = lerp(1.0, 173.1 * 0.995, u ** 1.25) * AU
                pts.append((SUN[0] + math.cos(ang) * rr, SUN[1] + math.sin(ang) * rr))
            cv.line(pts, L.AMBER, width=2.4 / zoom ** 0.5, alpha=0.85 * a, dash=[8, 6], glow=0.4)
            cv.circle(vx, vy, 6, L.WHITE, alpha=a, glow=1.0)
            # the light-day sphere
            la = smooth(prog(t, c["crosses"] - 0.3, c["crosses"] + 0.3))
            cv.circle(*SUN, LD_R, L.CYAN, alpha=0.75 * a * la, fill=False, width=2.5, glow=0.5)
            # a pulse of light from home
            lp = prog(t, c["crosses"], c["lightday"] + 0.5)
            if 0 < lp < 1:
                cv.circle(*SUN, LD_R * lp, (1.0, 0.95, 0.85), alpha=0.85 * a * (1 - 0.3 * lp), fill=False, width=4,
                          glow=1.0)
            if lp >= 1:
                fl = 1 - smooth(prog(t, c["lightday"] + 0.5, c["lightday"] + 1.3))
                cv.circle(vx, vy, 30 + 40 * (1 - fl), L.WHITE, alpha=a * fl * 0.8, fill=False, width=3, glow=1.0)
        # labels (crisp)
        ma = smooth(prog(t, c["nov18"] + 1.2, c["nov18"] + 1.7))
        htext(cv, "THE SUN", SUN[0], SUN[1] + 62, 20, color=(0.8, 0.86, 0.98), alpha=ma * a, font=L.MONO_XB, tracking=0.1)
        htext(cv, "NEPTUNE'S ORBIT", SUN[0], SUN[1] - 30.1 * AU - 22, 18, color=(0.55, 0.7, 1.0), alpha=ma * a,
              font=L.MONO_XB)
        da = smooth(prog(t, c["nov18"] - 0.15, c["nov18"] + 0.3))
        ucard(cv, 300, 268, 480, 132, alpha=da * a, border=L.CYAN)
        htext(cv, "NOV 18, 2026", W / 2, 318, 52, color=L.WHITE, alpha=da * a, font=L.MONO_XB, shadow=0)
        htext(cv, "VOYAGER 1", W / 2, 370, 22, color=L.CYAN, alpha=da * a, font=L.MONO_XB, tracking=0.3, shadow=0)
        lp = prog(t, c["crosses"], c["lightday"] + 0.5)
        ka = smooth(prog(t, c["crosses"] - 0.2, c["crosses"] + 0.2))
        if ka > 0:
            hrs = 24 * ease_out_cubic(lp) if lp < 1 else 24.0
            h_ = int(hrs)
            m_ = int((hrs - h_) * 60)
            htext(cv, "LIGHT TRAVEL TIME", 92, 470, 20, color=(0.8, 0.86, 0.98), alpha=ka * a, font=L.MONO_XB,
                  anchor="left", tracking=0.2)
            htext(cv, f"{h_:02d}:{m_:02d}:00", 92, 520, 52, color=(1.0, 0.95, 0.85), alpha=ka * a, font=L.MONO_XB,
                  anchor="left", glow=0.4)
        ea = smooth(prog(t, c["lightday"] + 0.3, c["lightday"] + 0.7))
        htext(cv, "1 LIGHT-DAY · 25.9 BILLION KM", vx - 30, vy - 60, 26, color=L.CYAN, alpha=ea * a, font=L.MONO_XB,
              anchor="right", glow=0.4)
        fa = smooth(prog(t, c["home3"] - 0.1, c["home3"] + 0.3))
        htext(cv, "the first human-made object this far", vx - 30, vy - 22, 22, color=L.WHITE, alpha=fa * a,
              font=L.MONO_XB, anchor="right")

    # ================================================================== a fridge bulb
    def s_bulb(self, cv, t):
        c = self.c
        s0, s1 = c["sc_bulb"]
        a = smooth(prog(t, s0 - 0.1, s0 + 0.4))
        self.sky.draw(cv, t, alpha=0.6 * a, loop=self.duration)
        on = smooth(prog(t, c["fridge"] - 0.15, c["fridge"] + 0.2))
        space.bulb(cv, 300, 760, 1.25, alpha=a, glow=0.15 + 0.85 * on, t=t)
        htext(cv, "≈ 22 W", 300, 1010, 64, color=GOLD, alpha=on * a, glow=0.5)
        htext(cv, "VOYAGER'S RADIO", 300, 1076, 22, color=(0.8, 0.86, 0.98), alpha=on * a, font=L.MONO_XB, tracking=0.12)
        da = smooth(prog(t, c["calls"] - 0.2, c["calls"] + 0.3))
        feed = space.dsn_dish(cv, 760, 1170, 0.85, alpha=da * a)
        htext(cv, "70 m DISH", 760, 1204, 26, color=L.WHITE, alpha=da * a, font=L.MONO_XB)
        htext(cv, "NASA DEEP SPACE NETWORK", 760, 1240, 18, color=(0.8, 0.86, 0.98), alpha=da * a, font=L.MONO_XB,
              tracking=0.1)
        # a trickle of photons from the far corner into the dish
        if feed and da > 0:
            src = (980.0, 120.0)
            for k in range(16):
                f = (t * 0.55 + k / 16) % 1.0
                x = lerp(src[0], feed[0], f)
                y = lerp(src[1], feed[1], f)
                cv.circle(x, y, 2.2, L.CYAN, alpha=da * a * 0.8 * math.sin(math.pi * f), glow=0.8)
            htext(cv, "≈ 1 day later →", 930, 400, 20, color=L.CYAN, alpha=da * a, font=L.MONO_XB, anchor="right")
        pa = smooth(prog(t, c["power"] - 0.1, c["power"] + 0.3)) * (1 - on)
        htext(cv, "TRANSMITTER POWER?", W / 2, 330, 40, color=L.WHITE, alpha=pa * a, font=L.MONO_XB)

    # ================================================================== the pale blue dot
    def s_dot(self, cv, t):
        c = self.c
        s0, s1 = c["sc_dot"]
        a = smooth(prog(t, s0 - 0.1, s0 + 0.4))
        view = smooth(prog(t, c["photo"] - 0.35, c["photo"] + 0.25))
        if view < 1:
            turn = ease_in_out(prog(t, c["turned"] - 0.2, c["photo"] + 0.1))
            with cv.group(1 - view) if view > 0 else _null():
                self.sky.draw(cv, t, alpha=a, loop=self.duration)
                self.voy.draw(cv, 540, 980, 105, yaw=0.5 + math.pi * 0.85 * turn, pitch=-0.95 + 0.3 * turn, roll=0.1,
                              alpha=a, t=t)
            ya = smooth(prog(t, c["y1990"] - 0.15, c["y1990"] + 0.2))
            htext(cv, "1990", W / 2, 330, 150, color=L.AMBER, alpha=ya * a * (1 - view), glow=0.5)
            htext(cv, "ONE LAST LOOK BACK", W / 2, 432, 28, color=L.WHITE, alpha=ya * a * (1 - view), font=L.MONO_XB,
                  tracking=0.12)
        if view > 0:
            z = lerp(1.0, 1.25, ease_in_out(prog(t, c["pale"] - 0.3, c["dot"] + 0.6)))
            with cv.group(view * a) if view < 1 or a < 1 else _null(), cv.transform(s=z, cx=650, cy=1010):
                dx, dy = space.pale_blue_dot(cv, 40, 260, 1000, 1180, alpha=1.0, dot=(0.61, 0.64), t=t)
            ra = smooth(prog(t, c["pale"] - 0.2, c["pale"] + 0.3))
            if ra > 0:
                sx, sy = 650 + (dx - 650) * z, 1010 + (dy - 1010) * z
                ph = (t * 0.8) % 1.0
                cv.circle(sx, sy, 34 + 10 * math.sin(t * 3), L.CYAN, alpha=ra * a, fill=False, width=3, glow=0.6)
                htext(cv, "EARTH", sx + 50, sy - 28, 30, color=L.CYAN, alpha=ra * a, font=L.MONO_XB, anchor="left",
                      glow=0.4)
                htext(cv, "0.12 pixel · 6 billion km", sx + 50, sy + 12, 20, color=L.WHITE, alpha=ra * a, font=L.MONO_XB,
                      anchor="left")
            htext(cv, "FEB 14, 1990 · VOYAGER 1", W / 2, 230, 22, color=(0.8, 0.86, 0.98), alpha=view * a, font=L.MONO_XB,
                  tracking=0.1)

    # ================================================================== the golden record
    def s_record(self, cv, t):
        c = self.c
        s0, s1 = c["sc_record"]
        a = smooth(prog(t, s0 - 0.1, s0 + 0.4))
        self.sky.draw(cv, t, alpha=0.5 * a, loop=self.duration)
        # first: find it on the spacecraft
        on_ship = 1 - smooth(prog(t, c["golden"] - 0.1, c["golden"] + 0.5))
        if on_ship > 0:
            with cv.group(on_ship * a) if on_ship < 1 or a < 1 else _null():
                z = lerp(1.0, 2.4, ease_in_out(prog(t, s0, c["golden"] + 0.4)))
                with cv.transform(s=z, cx=470, cy=1120):
                    self.voy.draw(cv, VOY["x"], VOY["y"], VOY["scale"], yaw=VOY["yaw"], pitch=VOY["pitch"], roll=VOY["roll"],
                                  record_glow=smooth(prog(t, s0 + 0.2, s0 + 0.8)), t=t)
        ra = 1 - on_ship
        if ra <= 0:
            return
        cover = smooth(prog(t, c["whoever"] - 0.2, c["whoever"] + 0.4)) * (1 - smooth(prog(t, c["music"] - 0.3,
                                                                                            c["music"] + 0.2)))
        rx, ry, rr = 540.0, 840.0, 300.0
        pop = ease_out_back(prog(t, c["golden"] - 0.1, c["golden"] + 0.5))
        self.rec.draw(cv, rx, ry, rr * pop, rot=t * 0.35, alpha=ra * a, glow=0.35, cover=cover)
        htext(cv, "THE GOLDEN RECORD", W / 2, 330, 56, color=GOLD, alpha=ra * a * (1 - cover * 0.0), glow=0.35)
        wa = smooth(prog(t, c["whoever"] - 0.1, c["whoever"] + 0.3)) * (1 - smooth(prog(t, c["music"] - 0.3, c["music"])))
        htext(cv, "the cover: how to play it, and where we are", W / 2, 1190, 22, color=L.WHITE, alpha=wa * a,
              font=L.MONO_XB)
        # music: rings of sound
        ma = smooth(prog(t, c["music"] - 0.1, c["music"] + 0.3))
        if ma > 0:
            for k in range(4):
                ph = (t * 0.6 + k / 4) % 1.0
                cv.circle(rx, ry, rr * (1.02 + 0.5 * ph), GOLD, alpha=ma * a * 0.5 * (1 - ph), fill=False, width=3,
                          glow=0.5)
            htext(cv, "90 MIN OF MUSIC", W / 2, 410, 26, color=L.WHITE, alpha=ma * a, font=L.MONO_XB, tracking=0.12)
        # greetings orbiting
        ga = smooth(prog(t, c["greetings"] - 0.1, c["greetings"] + 0.4))
        if ga > 0:
            n = len(GREETINGS)
            for k, word in enumerate(GREETINGS):
                ang = 2 * math.pi * k / n + t * 0.25
                gx = rx + math.cos(ang) * (rr + 120)
                gy = ry + math.sin(ang) * (rr + 120) * 0.85
                appear = smooth(clamp((t - c["greetings"]) * 3 - k * 0.15))
                font = "IPAGothic" if word == "こんにちは" else L.UI
                htext(cv, word, gx, gy, 30, color=L.WHITE, alpha=ga * a * appear * 0.95, font=font, shadow=0.7)
            na = smooth(prog(t, c["n55"] - 0.1, c["n55"] + 0.3))
            htext(cv, "55 LANGUAGES", W / 2, 1258, 34, color=GOLD, alpha=na * a, font=L.MONO_XB, glow=0.4)
            htext(cv, "+ 115 images", W / 2, 1210, 22, color=(0.8, 0.86, 0.98), alpha=na * a, font=L.MONO_XB)
        ha = smooth(prog(t, c["heartbeat"] - 0.15, c["heartbeat"] + 0.2))
        if ha > 0:
            space.ekg(cv, 90, 990, ry + 10, t - c["heartbeat"], alpha=ha * a, bpm=64, amp=90)

    # ================================================================== a love story
    def s_love(self, cv, t):
        c = self.c
        s0, s1 = c["sc_love"]
        a = smooth(prog(t, s0 - 0.1, s0 + 0.4))
        self.sky.draw(cv, t, alpha=0.35 * a, loop=self.duration)
        warm = smooth(prog(t, c["fallen"] - 0.2, c["love8"] + 0.4))
        ea = smooth(prog(t, c["brainwaves"] - 0.2, c["brainwaves"] + 0.4)) * (1 - 0.65 * smooth(prog(t, c["ann"] - 0.3,
                                                                                                     c["ann"] + 0.3)))
        space.eeg(cv, 70, 560, 940, 620, t, channels=6, alpha=ea * a, color=mix(PINK, (1.0, 0.35, 0.40), warm))
        ta = smooth(prog(t, c["brainwaves"] - 0.1, c["brainwaves"] + 0.3)) * (1 - smooth(prog(t, c["ann"] - 0.3,
                                                                                               c["ann"])))
        htext(cv, "HER BRAINWAVES", W / 2, 330, 64, color=PINK, alpha=ta * a, glow=0.4)
        htext(cv, "1 hour of them, recorded June 1977", W / 2, 410, 24, color=L.WHITE, alpha=ta * a, font=L.MONO_XB)
        da = smooth(prog(t, c["love8"] - 0.1, c["love8"] + 0.3)) * (1 - smooth(prog(t, c["ann"] - 0.3, c["ann"])))
        htext(cv, "two days after they decided to marry", W / 2, 1240, 24, color=PINK, alpha=da * a, font=L.MONO_XB,
              glow=0.3)
        # two stars, drawn to each other
        sa = smooth(prog(t, c["ann"] - 0.3, c["ann"] + 0.4))
        if sa > 0:
            close = ease_in_out(prog(t, c["ann"], c["led"] + 0.6))
            sep = lerp(260, 90, close)
            ang = t * 0.9
            for k, col in ((0, PINK), (1, (0.55, 0.85, 1.0))):
                sx = W / 2 + math.cos(ang + k * math.pi) * sep
                sy = 900 + math.sin(ang + k * math.pi) * sep * 0.35
                cv.radial(sx, sy, 90, col, alpha=0.7 * sa * a, glow=1.0)
                cv.circle(sx, sy, 9, L.WHITE, alpha=sa * a, glow=1.0)
            na = smooth(prog(t, c["ann"] - 0.1, c["ann"] + 0.3))
            htext(cv, "ANN DRUYAN", W / 2, 330, 72, color=L.WHITE, alpha=na * a, glow=0.15)
            htext(cv, "her brainwaves are on the record", W / 2, 404, 24, color=PINK, alpha=na * a, font=L.MONO_XB)
            ca = smooth(prog(t, c["carl"] - 0.1, c["carl"] + 0.3))
            htext(cv, "CARL SAGAN", W / 2, 1090, 64, color=L.WHITE, alpha=ca * a, glow=0.15)
            htext(cv, "chaired the committee that chose its contents", W / 2, 1152, 22, color=(0.55, 0.85, 1.0),
                  alpha=ca * a, font=L.MONO_XB)

    # ================================================================== 40,000 years
    def s_star(self, cv, t):
        c = self.c
        s0, s1 = c["sc_star"]
        a = smooth(prog(t, s0 - 0.1, s0 + 0.4))
        drift = ease_in_out(prog(t, s0, s1 + 0.3))
        self.sky.draw(cv, t, ox=-120 * drift, oy=60 * drift, alpha=a, loop=self.duration)
        # Gliese 445 approaches (a red dwarf)
        ga = smooth(prog(t, c["drift"] - 0.5, c["star"] + 0.3))
        sx, sy = lerp(980, 820, ga), lerp(360, 520, ga)
        if ga > 0:
            cv.radial(sx, sy, 60 + 260 * ga, (1.0, 0.45, 0.30), alpha=0.6 * ga * a, glow=1.0)
            cv.circle(sx, sy, 10 + 8 * ga, (1.0, 0.85, 0.75), alpha=ga * a, glow=1.0)
            for k in range(4):
                ang = k * math.pi / 4
                cv.line([(sx - math.cos(ang) * 140 * ga, sy - math.sin(ang) * 140 * ga),
                         (sx + math.cos(ang) * 140 * ga, sy + math.sin(ang) * 140 * ga)], (1.0, 0.7, 0.6), width=1.5,
                        alpha=0.4 * ga * a, glow=0.6)
            la = smooth(prog(t, c["star"] - 0.1, c["star"] + 0.3)) * (1 - smooth(prog(t, c["carrying"] - 0.6,
                                                                                    c["carrying"] - 0.25)))
            htext(cv, "GLIESE 445", W / 2, 470, 40, color=(1.0, 0.72, 0.62), alpha=la * a, font=L.MONO_XB, glow=0.3,
                  shadow=1.0)
            htext(cv, "a red dwarf · passing within 1.6 light-years", W / 2, 520, 22, color=L.WHITE, alpha=la * a,
                  font=L.MONO_XB, shadow=1.0)
        love = smooth(prog(t, c["carrying"] - 0.2, c["story"] + 0.4))
        vs = lerp(70, 92, love)
        self.voy.draw(cv, 470, 1080, vs, yaw=0.5 + 0.15 * drift, pitch=-0.95, roll=0.10, alpha=a, record_glow=love, t=t)
        if love > 0:
            # the record glows; her brainwaves wrap it
            rc = (470 - 70, 1135)
            for k in range(3):
                pts = [(rc[0] + math.cos(th) * (36 + k * 10 + 4 * math.sin(th * 9 + t * 4)),
                        rc[1] + math.sin(th) * (36 + k * 10 + 4 * math.sin(th * 9 + t * 4)) * 0.6)
                       for th in np.linspace(0, 2 * math.pi, 80)]
                cv.line(pts, PINK, width=2, alpha=love * a * (0.7 - 0.2 * k), glow=0.8)
        ya = smooth(prog(t, c["n40000"] - 0.15, c["n40000"] + 0.3)) * (1 - smooth(prog(t, c["carrying"] - 0.6,
                                                                                         c["carrying"] - 0.25)))
        yrs = int(40000 * ease_out_cubic(prog(t, c["n40000"] - 0.15, c["L10"] + 2.0)))
        htext(cv, f"+{yrs:,} YEARS", W / 2, 330, 96, color=L.AMBER, alpha=ya * a, glow=0.45)
        lt = smooth(prog(t, c["carrying"] - 0.2, c["carrying"] + 0.3))
        htext(cv, "STILL CARRYING", W / 2, 300, 40, color=L.WHITE, alpha=lt * a, font=L.MONO_XB, tracking=0.1)
        htext(cv, "THEIR LOVE STORY", W / 2, 370, 64, color=PINK, alpha=lt * a, glow=0.4)

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
