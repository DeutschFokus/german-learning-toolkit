"""EP007 — There Are Seashells on Top of Everest.

Narrated by the creator (no AI voice in any deliverable). Until his take exists,
animation timing comes from a scratch read; `build.py human take.wav` re-times
everything to the real voice.

First LUMEN episode built on photo plates: the creator's images (assets/) become
2.5D camera moves (engine/plates.py); the engine adds everything that must be
exact: India's journey on a real-data globe, the collision, the altitude
counter, labels and the stitched name tag.

Journey: the summit at dawn ("there are seashells up here") -> fossils in the
summit limestone -> the Ordovician sea -> India races north -> it slams into
Asia -> the seafloor folds and rises 9 km -> still rising -> 1924: Mallory and
Irvine last seen -> 2024: a boot melts out of the ice -> the camera never found
-> "if they did, they stood on seashells" (loop).

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
from engine.gfx import (H, L, W, Canvas, background, clamp, ease_in_cubic, ease_in_out,  # noqa: E402
                        ease_out_cubic, lerp, prog, smooth, window)
from engine.hud import htext, ui_scope  # noqa: E402
from engine.particles import Particles  # noqa: E402
from engine.plates import Cam, Plate, rgba_layer  # noqa: E402
from engine.postfx import Post  # noqa: E402
from engine.props import DottedEarth  # noqa: E402
from engine.timeline import Timeline  # noqa: E402

ASSETS = HERE.parent / "assets"
GOLD = (1.0, 0.78, 0.35)
ICE = (0.70, 0.88, 1.0)
SEPIA = (0.93, 0.80, 0.60)
RED = (0.86, 0.16, 0.14)
ACCENTS = {"L01": GOLD, "L02": GOLD, "L03": L.CYAN, "L04": L.AMBER, "L05": L.CORE, "L06": GOLD, "L07": L.CYAN,
           "L08": SEPIA, "L09": ICE, "L10": ICE, "L11": GOLD}
CONTINUOUS = {"crash"}
X_IN = {"sea": 0.55, "outro": 0.35}
X_OUT = {}
T_HEAD = 0.10                      # the headline lives just in front of the sky


# --------------------------------------------------------------------------- image painting
def _surface(img):
    """float BGR (h, w, 3) -> cairo surface (keeps the buffer alive on the object)."""
    h, w = img.shape[:2]
    buf = np.empty((h, w, 4), np.uint8)
    buf[..., :3] = (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)
    buf[..., 3] = 255
    s = cairo.ImageSurface.create_for_data(memoryview(buf), cairo.FORMAT_ARGB32, w, h, w * 4)
    return s, buf


def paint_img(cv: Canvas, img, alpha=1.0, glow=0.5, thresh=0.84):
    """Paint a full-frame plate render into the scene (respects groups/transforms) and send
    its highlights to the bloom layer."""
    if alpha <= 0.003:
        return
    s, _buf = _surface(img)
    cv.b.save()
    cv.b.set_source_surface(s, 0, 0)
    cv.b.paint_with_alpha(clamp(alpha))
    cv.b.restore()
    if glow > 0:
        small = cv2.resize(img, (W // 2, H // 2), interpolation=cv2.INTER_AREA)
        lum = small.max(axis=2, keepdims=True)
        g = np.clip((lum - thresh) / (1 - thresh), 0, 1) ** 1.5 * small
        gs, _gbuf = _surface(g)
        cv.g.save()
        cv.g.scale(2, 2)
        cv.g.set_source_surface(gs, 0, 0)
        cv.g.paint_with_alpha(clamp(alpha * glow))
        cv.g.restore()


def scrim(cv, a=1.0, y0=150.0, y1=560.0, k=0.6):
    """Dark gradient behind the top titles so they read on bright plates."""
    if a <= 0.003:
        return
    pat = cairo.LinearGradient(0, y0, 0, y1)
    pat.add_color_stop_rgba(0, 0.01, 0.02, 0.05, k * a)
    pat.add_color_stop_rgba(1, 0.01, 0.02, 0.05, 0.0)
    cv.b.save()
    cv.b.rectangle(0, 0, W, y1)
    cv.b.set_source(pat)
    cv.b.fill()
    cv.b.restore()


def ring(cv, x, y, r, a, color=L.WHITE):
    cv.circle(x, y, r, color, alpha=0.9 * a, fill=False, width=3.0, glow=0.6)
    cv.circle(x, y, r + 10, color, alpha=0.25 * a, fill=False, width=1.5)


class Episode:
    def __init__(self, timeline_path, captions=True, grain=0.008, guide=False):
        self.T = Timeline(timeline_path)
        self.fps = self.T.fps
        self.duration = self.T.duration
        self.post = Post(grain=grain)
        self.caps = Captions(self.T, accent_by_line=ACCENTS) if captions else None
        self.guide = guide
        P = lambda n, **k: Plate(ASSETS / f"{n}.png", **k)  # noqa: E731
        self.p = {
            "summit": P("s01_summit"),
            "fossil": P("s02_fossil_rock"),
            "sea": P("s03_ancient_sea"),
            "folds": P("s05_folded_strata"),
            "range": P("s06_himalaya_above_clouds"),
            "alt": P("s07_himalaya_alt"),
            "climbers": P("s08_two_climbers_1924", layers=2),
            "boot": P("s09_boot_in_ice"),
            "camera": P("s10_camera_in_snow"),
        }
        self.earth = DottedEarth(n=9000, seed=4)
        lat, lon = np.degrees(self.earth.lat), np.degrees(self.earth.lon)
        # the Indian subcontinent (south of the Himalayan front), moved as one block
        india = (lat < 28.5) & (lat > 5) & (lon > 67) & (lon < 92.5) & ~((lat > 24) & (lon > 89))
        india |= (lat > 5.5) & (lat < 10) & (lon > 79.5) & (lon < 82)        # Sri Lanka
        self.india = india
        self.snow = Particles(n=140, seed=7, kind="snow", loop=self.duration)
        self.dust = Particles(n=90, seed=8, kind="dust", loop=self.duration)
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
            "seashells": w("L01", "seashells"), "everest": w("L01", "Everest"),
            "limestone": w("L02", "limestone"), "fossil": w("L02", "fossil"), "creatures": w("L02", "creatures"),
            "n450": T.word("L03", 2).start, "floor": w("L03", "floor"), "sea3": w("L03", "sea"),
            "india": w("L04", "India"), "raced": w("L04", "raced"), "four": w("L04", "four"),
            "fingernails": w("L04", "fingernails"),
            "slammed": w("L05", "slammed"), "asia": w("L05", "Asia"),
            "crumpled": w("L06", "crumpled"), "rose": w("L06", "rose"), "nine": w("L06", "nine"),
            "kilometers": w("L06", "kilometers"),
            "still": w("L07", "still"), "two": w("L07", "two"),
            "y1924": T.word("L08", 1).start, "mallory": w("L08", "Mallory"), "irvine": w("L08", "Irvine"),
            "lastseen": w("L08", "last"), "top8": w("L08", "top"),
            "never": w("L09", "never"), "y2024": T.word("L09", 5).start, "boot": w("L09", "boot"),
            "name": w("L09", "name"), "sock": w("L09", "sock"),
            "camera": w("L10", "camera"), "nobody": w("L10", "Nobody"), "summit10": w("L10", "summit"),
            "did": w("L11", "did"), "seashells11": w("L11", "seashells"),
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
            Xo = 0.0 if (last or self.scenes[k + 1][0] in CONTINUOUS) else X_OUT.get(sid, 0.22)
            if not (s0 - Xi <= t < s1 + Xo):
                continue
            a, sc, ty = 1.0, 1.0, 0.0
            if Xi and t < s0 + Xi:
                p = prog(t, s0 - Xi, s0 + Xi)
                a, sc = smooth(p), 0.985 + 0.015 * ease_out_cubic(p)
            if Xo and t > s1 - Xo:
                p = prog(t, s1 - Xo, s1 + Xo)
                a, sc = 1 - smooth(p), 1 + 0.03 * ease_in_cubic(p)
            if a <= 0.003:
                continue
            fn = getattr(self, "s_" + sid)
            if a >= 0.999 and sc == 1.0:
                fn(cv, t)
            else:
                with cv.group(a), cv.transform(s=sc), ui_scope(cv, a, sc, ty, W / 2, H / 2):
                    fn(cv, t)
        if self.caps:
            self.caps.draw(cv, t)
        if self.guide:
            self._teleprompter(cv, t)

    # ================================================================== the summit (hook + outro)
    def _headline(self, cam, alphas):
        """THERE ARE / SEASHELLS / UP HERE, drawn at depth T_HEAD so the peak passes in front."""
        if max(alphas) <= 0.003:
            return None
        m = cam.mag(T_HEAD)
        ox = cam.orbit[0] * (T_HEAD - cam.focus) + cam.pan[0]
        oy = cam.orbit[1] * (T_HEAD - cam.focus) + cam.pan[1]
        cx, cy = cam.center
        rows = (("THERE ARE", 64, L.WHITE, 330, L.DISPLAY_XB, 6), ("SEASHELLS", 176, GOLD, 520, L.DISPLAY, 0),
                ("UP HERE", 64, L.WHITE, 640, L.DISPLAY_XB, 6))

        def draw(ctx):
            ctx.translate(cx + ox, cy + oy)
            ctx.scale(m, m)
            ctx.translate(-cx, -cy)
            for (s, size, col, y, font, track), a in zip(rows, alphas):
                if a <= 0.003:
                    continue
                ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                ctx.set_font_size(size)
                widths = [ctx.text_extents(ch).x_advance for ch in s]
                x = W / 2 - (sum(widths) + track * (len(s) - 1)) / 2
                for ch, cw in zip(s, widths):
                    ctx.move_to(x, y)
                    ctx.text_path(ch)
                    x += cw + track
                ctx.set_source_rgba(*col, a)
                ctx.fill()
        txt = rgba_layer(draw)
        al = txt[..., 3]
        sh = np.zeros_like(al)
        sh[8:] = al[:-8]
        sh = cv2.GaussianBlur(sh, (0, 0), 9) * 0.6
        out = np.empty_like(txt)
        out[..., :3] = txt[..., :3] + (1 - al)[..., None] * np.array([0.10, 0.05, 0.02], np.float32) * sh[..., None]
        out[..., 3] = al + (1 - al) * sh
        return out

    def _summit(self, cv, t, cam, head, figures=0.0):
        pl = self.p["summit"]
        ins = self._headline(cam, head)
        img = pl.render(cam, inserts=[(1, ins)] if ins is not None else [])
        paint_img(cv, img, glow=0.45)
        if figures > 0:
            # two tiny silhouettes on the very top
            tx, ty = pl.screen_point(cam, 404, 630)
            for dx, h_ in ((-9, 15), (7, 17)):
                x, y = tx + dx, ty - 2
                cv.line([(x, y), (x, y - h_)], (0.05, 0.05, 0.08), width=3.2, alpha=figures)
                cv.circle(x, y - h_ - 3, 3.0, (0.05, 0.05, 0.08), alpha=figures)
        with cv.transform(tx=cam.orbit[0] * 0.8, s=1 + cam.push):
            self.snow.draw(cv, t, alpha=0.55, glow=0.3, color=(0.95, 0.97, 1.0))

    def s_hook(self, cv, t):
        c = self.c
        s0, s1 = c["sc_hook"]
        x = ease_in_out(prog(t, 0.0, s1 + 0.3))
        cam = Cam(push=0.06 * x, orbit=(-12 * x, 0), focus=0.45)
        out = 1 - smooth(prog(t, c["L01end"] - 0.1, c["L01end"] + 0.35))
        self._summit(cv, t, cam, (out, out, out))

    def s_outro(self, cv, t):
        c = self.c
        s0, s1 = c["sc_outro"]
        x = ease_in_out(prog(t, s0 - 0.35, self.duration))
        cam = Cam(push=0.05 * (1 - x), orbit=(14 * (1 - x), 0), focus=0.45)
        head = tuple(smooth(prog(t, c["seashells11"] + 0.15 + 0.25 * k, c["seashells11"] + 0.55 + 0.25 * k))
                     for k in range(3))
        if self.duration - t < 0.4:
            head = (1.0, 1.0, 1.0)
        figs = smooth(prog(t, c["did"] - 0.1, c["did"] + 0.4)) * (1 - smooth(prog(t, c["seashells11"] + 0.3,
                                                                                    c["seashells11"] + 1.1)))
        self._summit(cv, t, cam, head, figures=figs * 0.85)

    # ================================================================== fossils in the summit rock
    def s_summit(self, cv, t):
        c = self.c
        s0, s1 = c["sc_summit"]
        x = ease_in_out(prog(t, s0 - 0.3, s1 + 0.3))
        pl = self.p["fossil"]
        cam = Cam(push=0.09 * x, orbit=(10 - 20 * x, -4 + 8 * x), focus=0.6)
        paint_img(cv, pl.render(cam), glow=0.4)
        la = smooth(prog(t, c["limestone"] - 0.1, c["limestone"] + 0.3))
        scrim(cv, la)
        htext(cv, "SUMMIT ROCK", W / 2, 300, 34, color=L.WHITE, alpha=la, font=L.MONO_XB, tracking=0.14, shadow=1.0)
        htext(cv, "LIMESTONE", W / 2, 380, 92, color=GOLD, alpha=la, glow=0.35, shadow=1.0)
        for k, (ix, iy, r, label, lx) in enumerate(((560, 555, 92, "SEA LILY (stem)", 1), (230, 790, 96, "SHELL", 0),
                                                    (640, 1120, 120, "TRILOBITE", 1))):
            fa = smooth(prog(t, c["fossil"] - 0.1 + 0.32 * k, c["fossil"] + 0.25 + 0.32 * k))
            if fa <= 0:
                continue
            sx, sy = pl.screen_point(cam, ix, iy)
            rr = r * 1.32 * (1 + cam.push) * (0.85 + 0.15 * fa)
            ring(cv, sx, sy, rr, fa)
            ly = sy + rr + 36 if sy < 1150 else sy - rr - 30
            htext(cv, label, min(max(sx, 200), W - 200), ly, 30, color=L.WHITE, alpha=fa, font=L.MONO_XB,
                  tracking=0.08, shadow=1.0)

    # ================================================================== the Ordovician sea
    def s_sea(self, cv, t):
        c = self.c
        s0, s1 = c["sc_sea"]
        x = ease_in_out(prog(t, s0 - 0.5, s1 + 0.3))
        pl = self.p["sea"]
        cam = Cam(push=0.08 * x, orbit=(16 - 32 * x, 0), focus=0.55)
        paint_img(cv, pl.render(cam), glow=0.55, thresh=0.80)
        with cv.transform(tx=cam.orbit[0], s=1 + cam.push * 1.3):
            self.dust.draw(cv, t, alpha=0.9, glow=0.5, color=(0.75, 0.95, 1.0))
        ya = smooth(prog(t, c["n450"] - 0.3, c["n450"] + 0.1))
        scrim(cv, ya)
        yrs = int(450 * ease_out_cubic(prog(t, c["n450"] - 0.3, c["n450"] + 0.9)))
        htext(cv, f"−{yrs},000,000 YEARS", W / 2, 310, 60, color=GOLD, alpha=ya, glow=0.35, shadow=1.0)
        oa = smooth(prog(t, c["sea3"] - 0.2, c["sea3"] + 0.3))
        htext(cv, "THE ORDOVICIAN SEA", W / 2, 380, 30, color=L.WHITE, alpha=oa, font=L.MONO_XB, tracking=0.12,
              shadow=1.0)

    # ================================================================== India races north (real-data globe)
    def _globe(self, cv, t, a=1.0):
        c = self.c
        gx, gy, r = 540.0, 980.0, 400.0
        lon0, tilt = math.radians(80.0), 0.15
        # India's offset in latitude: ~ -38 deg (70 Myr ago) -> 0 at the collision
        u = ease_in_out(prog(t, c["india"] - 0.2, c["slammed"]))
        off = math.radians(-38.0 * (1 - u))
        e = self.earth
        cv.circle(gx, gy, r + 26, (0.35, 0.6, 1.0), alpha=0.10 * a, glow=0.6)
        pat = cairo.RadialGradient(gx - r * 0.35, gy - r * 0.4, r * 0.1, gx, gy, r)
        pat.add_color_stop_rgba(0, 0.06, 0.16, 0.38, a)
        pat.add_color_stop_rgba(0.75, 0.03, 0.07, 0.19, a)
        pat.add_color_stop_rgba(1, 0.02, 0.04, 0.12, a)
        cv.b.new_path()
        cv.b.arc(gx, gy, r, 0, 2 * math.pi)
        cv.b.set_source(pat)
        cv.b.fill()
        lat, lon = e.lat, e.lon

        def proj(la, lo):
            X = np.cos(la) * np.sin(lo - lon0)
            Y = np.sin(la)
            Z = np.cos(la) * np.cos(lo - lon0)
            return gx + r * X, gy - r * (Y * math.cos(tilt) - Z * math.sin(tilt)), \
                Y * math.sin(tilt) + Z * math.cos(tilt)

        b = cv.b
        d = max(1.0, r * 0.0105)
        sx, sy, sz = proj(lat[~self.india], lon[~self.india])
        for X, Y, Z in zip(sx, sy, sz):
            if Z > 0.02:
                b.set_source_rgba(0.55, 0.85, 1.0, a * (0.25 + 0.75 * Z))
                b.arc(X, Y, d * (0.6 + 0.4 * Z), 0, 2 * math.pi)
                b.fill()
        ix, iy, iz = proj(lat[self.india] + off, lon[self.india])
        hot = window(t, c["slammed"] - 0.05, c["slammed"] + 0.1, 0.05, 1.2)
        col = (1.0, 0.70 + 0.2 * hot, 0.30 + 0.5 * hot)
        for X, Y, Z in zip(ix, iy, iz):
            if Z > 0.02:
                b.set_source_rgba(*col, a * (0.35 + 0.65 * Z))
                b.arc(X, Y, d * 1.05, 0, 2 * math.pi)
                b.fill()
                cv.g.set_source_rgba(1.0, 0.6, 0.25, a * 0.35)
                cv.g.arc(X, Y, d * 2.0, 0, 2 * math.pi)
                cv.g.fill()
        # path of India's centre
        la_c = math.radians(21.0)
        lo_c = math.radians(79.0)
        pts = []
        for k in range(40):
            o = math.radians(-38.0) * (1 - k / 39 * u)
            X, Y, Z = proj(np.array([la_c + o]), np.array([lo_c]))
            pts.append((float(X[0]), float(Y[0])))
        cv.line(pts, L.AMBER, width=2.5, alpha=0.7 * a * smooth(prog(t, c["india"], c["india"] + 0.5)), glow=0.5,
                dash=[10, 10])
        hx, hy = pts[-1]
        htext(cv, "INDIA", hx + 70, hy + 40, 34, color=L.AMBER, alpha=a * smooth(prog(t, c["india"] - 0.2,
                                                                                      c["india"] + 0.3)),
              font=L.MONO_XB, tracking=0.1, shadow=1.0)
        X, Y, _ = proj(np.array([math.radians(48.0)]), np.array([math.radians(88.0)]))
        htext(cv, "ASIA", float(X[0]), float(Y[0]), 34, color=L.WHITE, alpha=a * 0.9, font=L.MONO_XB, tracking=0.1,
              shadow=1.0)
        # the collision: a shockwave along the Himalayan front
        if t > c["slammed"] - 0.05:
            p = prog(t, c["slammed"] - 0.05, c["slammed"] + 1.4)
            X, Y, _ = proj(np.array([math.radians(29.0)]), np.array([math.radians(84.0)]))
            fx, fy = float(X[0]), float(Y[0])
            for j in range(3):
                q = clamp(p * 1.4 - j * 0.18)
                if 0 < q < 1:
                    cv.circle(fx, fy, 20 + 260 * ease_out_cubic(q), (1.0, 0.75, 0.45), alpha=a * (1 - q) * 0.8,
                              fill=False, width=4 - j, glow=1.0)
            cv.radial(fx, fy, 120, (1.0, 0.8, 0.5), alpha=a * 0.9 * (1 - p), glow=1.0)
        return gx, gy, r

    def s_drift(self, cv, t):
        c = self.c
        self._globe(cv, t)
        my = int(round(lerp(70, 50, ease_in_out(prog(t, c["india"] - 0.2, c["slammed"])))))
        ya = smooth(prog(t, c["india"] - 0.3, c["india"] + 0.2))
        htext(cv, f"{my} MILLION YEARS AGO", W / 2, 262, 40, color=L.WHITE, alpha=ya, font=L.MONO_XB, tracking=0.1)
        # speed race: India vs your fingernails
        ba = smooth(prog(t, c["four"] - 0.2, c["four"] + 0.3))
        if ba > 0:
            g = prog(t, c["four"] - 0.2, c["L04end"] + 0.4)
            x0, wmax = 110.0, 760.0
            for k, (lab, v, col) in enumerate((("INDIA  up to ~15 cm / year", 15.0, L.AMBER),
                                               ("YOUR FINGERNAILS  ~4 cm / year", 4.0, L.WHITE))):
                yy = [372, 462][k]
                ln = wmax * v / 15.0 * ease_out_cubic(g)
                cv.rect(x0, yy, ln, 22, col, alpha=0.85 * ba, radius=11, glow=0.4)
                htext(cv, lab, x0, yy - 26, 26, color=col, alpha=ba, font=L.MONO_XB, anchor="left", tracking=0.06,
                      shadow=1.0)

    def s_crash(self, cv, t):
        c = self.c
        sh = window(t, c["slammed"] - 0.02, c["slammed"] + 0.05, 0.02, 0.6)
        jx = 10 * sh * math.sin(t * 90)
        jy = 8 * sh * math.cos(t * 77)
        cv.flash = max(cv.flash, 0.35 * window(t, c["slammed"] - 0.03, c["slammed"] + 0.02, 0.02, 0.35))
        with cv.transform(tx=jx, ty=jy):
            self._globe(cv, t)
        ca = smooth(prog(t, c["slammed"], c["slammed"] + 0.3))
        htext(cv, "COLLISION", W / 2, 300, 72, color=L.CORE, alpha=ca, glow=0.5)
        htext(cv, "about 50 million years ago", W / 2, 370, 28, color=L.WHITE, alpha=ca, font=L.MONO_XB)

    # ================================================================== the seafloor folds and rises
    def s_rise(self, cv, t):
        c = self.c
        s0, s1 = c["sc_rise"]
        sw = smooth(prog(t, c["rose"] - 0.35, c["rose"] + 0.15))
        if sw < 1:
            x = ease_in_out(prog(t, s0 - 0.3, c["rose"] + 0.2))
            cam = Cam(push=0.10 * x, roll=-0.02 + 0.03 * x, orbit=(10 - 20 * x, 0), focus=0.5)
            paint_img(cv, self.p["folds"].render(cam), alpha=1.0, glow=0.35)
            fa = smooth(prog(t, c["crumpled"] - 0.1, c["crumpled"] + 0.3)) * (1 - sw)
            scrim(cv, fa)
            htext(cv, "THE OLD SEAFLOOR,", W / 2, 300, 40, color=L.WHITE, alpha=fa, font=L.MONO_XB, tracking=0.1,
                  shadow=1.0)
            htext(cv, "FOLDED", W / 2, 390, 100, color=GOLD, alpha=fa, glow=0.35, shadow=1.0)
        if sw > 0:
            x = ease_in_out(prog(t, c["rose"] - 0.35, s1 + 0.3))
            cam = Cam(push=0.05 * x, pan=(0, 120 * (1 - x)), orbit=(0, -10 + 20 * x), focus=0.5)
            paint_img(cv, self.p["range"].render(cam), alpha=sw, glow=0.45)
            # altitude counter: from the old sea floor to the summit
            g = ease_out_cubic(prog(t, c["rose"], c["kilometers"] + 0.6))
            alt = int(round(8849 * g))
            xb, y0, y1 = 96.0, 1300.0, 420.0
            cv.rect(0, 360, 460, 1000, (0.01, 0.02, 0.05), alpha=0.0)
            yy = lerp(y0, y1, g)
            cv.line([(xb, y0), (xb, y1)], L.WHITE, width=2, alpha=0.35 * sw)
            cv.line([(xb, y0), (xb, yy)], GOLD, width=5, alpha=0.95 * sw, glow=0.6)
            cv.circle(xb, yy, 9, GOLD, alpha=sw, glow=1.0)
            htext(cv, f"{alt:,} m", xb + 26, yy, 44, color=GOLD, alpha=sw, glow=0.3, anchor="left", shadow=1.0)
            htext(cv, "0 m  ·  old sea floor", xb + 26, y0, 24, color=L.WHITE, alpha=0.9 * sw, font=L.MONO_XB,
                  anchor="left", shadow=1.0)

    # ================================================================== still rising
    def s_grow(self, cv, t):
        c = self.c
        s0, s1 = c["sc_grow"]
        x = ease_in_out(prog(t, s0 - 0.3, s1 + 0.3))
        pl = self.p["alt"]
        cam = Cam(push=0.07 * x, orbit=(-10 + 20 * x, 0), focus=0.5)
        paint_img(cv, pl.render(cam), glow=0.45)
        px, py = pl.screen_point(cam, 528, 290)
        a = smooth(prog(t, c["two"] - 0.2, c["two"] + 0.2))
        if a > 0:
            for k in range(3):
                ph = ((t - c["two"]) * 0.9 + k / 3) % 1.0
                cv.line([(px - 30, py - 30 - 70 * ph), (px, py - 60 - 70 * ph), (px + 30, py - 30 - 70 * ph)], GOLD,
                        width=4, alpha=a * math.sin(math.pi * ph), glow=0.7)
            htext(cv, "+2 mm", px, py - 200, 76, color=GOLD, alpha=a, glow=0.4, shadow=1.0)
            htext(cv, "EVERY YEAR", px, py - 140, 28, color=L.WHITE, alpha=a, font=L.MONO_XB, tracking=0.14, shadow=1.0)
        sa = smooth(prog(t, c["still"] - 0.15, c["still"] + 0.25))
        scrim(cv, sa)
        htext(cv, "STILL RISING", W / 2, 300, 40, color=L.WHITE, alpha=sa * (1 - a * 0.0), font=L.MONO_XB,
              tracking=0.14, shadow=1.0)

    # ================================================================== 1924
    def _climbers(self, cv, t, cam, fog=0.0, alpha=1.0):
        pl = self.p["climbers"]
        img = pl.render(cam)
        flick = 1.0 + 0.025 * math.sin(t * 37.0) * math.sin(t * 13.0)
        img = img * flick
        if fog > 0:
            img = img * (1 - 0.8 * fog) + np.array([0.62, 0.70, 0.76], np.float32) * 0.8 * fog
        paint_img(cv, img, alpha=alpha, glow=0.3, thresh=0.88)
        return pl

    def s_climbers(self, cv, t):
        c = self.c
        s0, s1 = c["sc_climbers"]
        x = ease_in_out(prog(t, s0 - 0.3, s1 + 1.5))
        cam = Cam(push=0.12 * x, center=(560, 640), focus=0.5)
        pl = self._climbers(cv, t, cam)
        da = smooth(prog(t, c["y1924"] - 0.1, c["y1924"] + 0.3))
        scrim(cv, da)
        htext(cv, "JUNE 8, 1924", W / 2, 300, 64, color=SEPIA, alpha=da, glow=0.3, shadow=1.0)
        na = smooth(prog(t, c["mallory"] - 0.1, c["mallory"] + 0.3))
        htext(cv, "GEORGE MALLORY  &  SANDY IRVINE", W / 2, 362, 26, color=L.WHITE, alpha=na, font=L.MONO_XB,
              tracking=0.06, shadow=1.0)
        la = smooth(prog(t, c["lastseen"] - 0.1, c["lastseen"] + 0.3))
        if la > 0:
            sx, sy = pl.screen_point(cam, 476, 590)
            ring(cv, sx, sy, 70 * (1 + cam.push), la, SEPIA)
            htext(cv, "last seen", sx, sy + 110, 28, color=L.WHITE, alpha=la, font=L.MONO_XB, tracking=0.1, shadow=1.0)
            htext(cv, "high on the Northeast Ridge", sx, sy + 148, 22, color=SEPIA, alpha=la, font=L.MONO_XB,
                  shadow=1.0)

    # ================================================================== 2024: the boot
    def s_boot(self, cv, t):
        c = self.c
        s0, s1 = c["sc_boot"]
        sw = smooth(prog(t, c["y2024"] - 0.45, c["y2024"] + 0.1))
        if sw < 1:
            x = ease_in_out(prog(t, s0 - 0.3, c["y2024"]))
            cam = Cam(push=0.12 + 0.05 * x, center=(560, 640), focus=0.5)
            fog = smooth(prog(t, c["never"] - 0.2, c["y2024"] - 0.3))
            self._climbers(cv, t, cam, fog=fog)
        if sw > 0:
            x = ease_in_out(prog(t, c["y2024"] - 0.45, s1 + 0.3))
            pl = self.p["boot"]
            cam = Cam(push=0.09 * x, orbit=(12 - 24 * x, 0), focus=0.6)
            paint_img(cv, pl.render(cam), alpha=sw, glow=0.45)
            ya = smooth(prog(t, c["y2024"], c["y2024"] + 0.3)) * sw
            scrim(cv, ya)
            htext(cv, "2024", W / 2, 290, 72, color=ICE, alpha=ya, glow=0.3, shadow=1.0)
            htext(cv, "CENTRAL RONGBUK GLACIER", W / 2, 350, 26, color=L.WHITE, alpha=ya, font=L.MONO_XB,
                  tracking=0.1, shadow=1.0)
            ta = smooth(prog(t, c["name"] - 0.15, c["name"] + 0.35)) * sw
            if ta > 0:
                sx, sy = pl.screen_point(cam, 235, 395)
                bx, by = sx + 300, sy + 60
                cv.line([(sx + 40, sy), (bx - 4, by)], L.WHITE, width=2, alpha=0.8 * ta)
                cv.circle(sx + 40, sy, 6, L.WHITE, alpha=ta, glow=0.6)
                u = cv.u
                u.save()
                u.translate(bx + 120, by)
                u.rotate(-0.06)
                u.translate(-120, -32)
                u.new_path()
                u.rectangle(0, 0, 240 * ease_out_cubic(ta), 64)
                u.set_source_rgba(*RED, 0.95 * ta)
                u.fill()
                u.set_dash([6, 5])
                u.set_line_width(2)
                u.rectangle(6, 6, 228 * ease_out_cubic(ta), 52)
                u.set_source_rgba(1, 0.9, 0.85, 0.8 * ta)
                u.stroke()
                u.set_dash([])
                u.restore()
                htext(cv, "A.C. IRVINE", bx + 120, by - 4, 30, color=(1.0, 0.96, 0.92), alpha=ta, font=L.MONO_XB,
                      tracking=0.08, shadow=0.0)

    # ================================================================== the camera
    def s_camera(self, cv, t):
        c = self.c
        s0, s1 = c["sc_camera"]
        x = ease_in_out(prog(t, s0 - 0.3, s1 + 0.3))
        pl = self.p["camera"]
        cam = Cam(push=0.08 * x, orbit=(-12 + 24 * x, 0), focus=0.6)
        paint_img(cv, pl.render(cam), glow=0.5)
        # spindrift streaks
        rng = np.random.default_rng(3)
        for k in range(70):
            y0 = rng.uniform(0, H)
            sp = rng.uniform(500, 1100)
            xx = (rng.uniform(0, W + 400) + sp * t) % (W + 400) - 200
            yy = y0 + 0.18 * xx
            ln = rng.uniform(20, 60)
            cv.line([(xx, yy), (xx - ln, yy - 0.18 * ln)], (0.95, 0.97, 1.0), width=rng.uniform(1, 2.4),
                    alpha=rng.uniform(0.15, 0.5))
        ka = smooth(prog(t, c["camera"] - 0.1, c["camera"] + 0.3))
        scrim(cv, ka)
        htext(cv, "THEIR KODAK", W / 2, 300, 64, color=ICE, alpha=ka, glow=0.3, shadow=1.0)
        htext(cv, "never found", W / 2, 362, 28, color=L.WHITE, alpha=ka, font=L.MONO_XB, tracking=0.1, shadow=1.0)
        qa = smooth(prog(t, c["nobody"] - 0.1, c["nobody"] + 0.4))
        htext(cv, "DID THEY REACH THE TOP?", W / 2, 1180, 40, color=GOLD, alpha=qa, glow=0.4, shadow=1.0)

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
