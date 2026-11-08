"""Frame renderer: 2.5D camera moves on stills plus atmospheric effects, encoded with x264."""
import math
import multiprocessing as mp
import os
import subprocess

import cv2
import numpy as np
from PIL import Image

from .common import FPS, H, W, smoothstep

cv2.setNumThreads(1)

# --------------------------------------------------------------------------- utilities


def hermite_track(keys, name, t):
    """Smooth (C1) interpolation of keyframed parameter `name` at time t.

    keys: list of dicts with 't' and parameters; missing values carry over.
    Interior tangents are Catmull-Rom style; first/last keys ease in/out.
    """
    T, V = [], []
    last = None
    for k in keys:
        v = k.get(name, last)
        if v is None:
            continue
        T.append(k["t"])
        V.append(v)
        last = v
    if not T:
        return None
    if t <= T[0]:
        return V[0]
    if t >= T[-1]:
        return V[-1]
    i = max(j for j in range(len(T) - 1) if T[j] <= t)
    t0, t1 = T[i], T[i + 1]
    v0, v1 = V[i], V[i + 1]

    def tangent(j):
        if j == 0 or j == len(T) - 1 or keys_hold(keys, T[j]):
            return 0.0
        return (V[j + 1] - V[j - 1]) / (T[j + 1] - T[j - 1])

    m0, m1 = tangent(i) * (t1 - t0), tangent(i + 1) * (t1 - t0)
    s = (t - t0) / (t1 - t0)
    h00 = 2 * s ** 3 - 3 * s ** 2 + 1
    h10 = s ** 3 - 2 * s ** 2 + s
    h01 = -2 * s ** 3 + 3 * s ** 2
    h11 = s ** 3 - s ** 2
    return h00 * v0 + h10 * m0 + h01 * v1 + h11 * m1


def keys_hold(keys, t):
    for k in keys:
        if abs(k["t"] - t) < 1e-6 and k.get("hold"):
            return True
    return False


def value_noise(t, seed, freq):
    """Smooth 1D noise in [-1, 1]."""
    x = t * freq
    i = math.floor(x)
    f = x - i

    def h(n):
        n = (n * 374761393 + seed * 668265263) & 0xFFFFFFFF
        n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
        return ((n ^ (n >> 16)) & 0xFFFF) / 32767.5 - 1.0

    u = f * f * (3 - 2 * f)
    return h(i) * (1 - u) + h(i + 1) * u


def fbm(t, seed, freq=1.0):
    return 0.6 * value_noise(t, seed, freq) + 0.3 * value_noise(t, seed + 7, freq * 2.3) + 0.1 * value_noise(t, seed + 13, freq * 5.1)


def lightning_env(t, strikes):
    v = 0.0
    for s in strikes:
        dt = t - s
        if dt < 0 or dt > 1.4:
            continue
        if dt < 0.05:
            v += 1.0
        elif dt < 0.11:
            v += 0.12
        elif dt < 0.18:
            v += 0.8
        else:
            v += 0.8 * math.exp(-(dt - 0.18) / 0.2)
    return v


# --------------------------------------------------------------------------- images


class Img:
    def __init__(self, iid, orig_path, adir):
        self.iid = iid
        self.orig = np.array(Image.open(orig_path).convert("RGB"))
        self.h0, self.w0 = self.orig.shape[:2]
        self.depth = np.load(os.path.join(adir, f"{iid}_depth.npy"))
        self.window = np.load(os.path.join(adir, f"{iid}_window.npy"))
        self.warm = np.load(os.path.join(adir, f"{iid}_warm.npy"))
        self.sr_path = os.path.join(adir, f"{iid}_sr.png")
        self._master = None
        self._levels = {}

    def master(self):
        if self._master is None:
            if os.path.exists(self.sr_path):
                m = np.array(Image.open(self.sr_path).convert("RGB"))
            else:
                m = cv2.resize(self.orig, (self.w0 * 3, self.h0 * 3), interpolation=cv2.INTER_LANCZOS4)
            self._master = m
            self.L = m.shape[1] / self.w0
        return self._master

    def _level(self, k):
        if k not in self._levels:
            m = self.master()
            sc = self.L * 2 ** (-k / 4)
            im = m if k == 0 else cv2.resize(m, (max(1, round(self.w0 * sc)), max(1, round(self.h0 * sc))),
                                              interpolation=cv2.INTER_AREA)
            self._levels[k] = (im.astype(np.float32) / 255.0, im.shape[1] / self.w0)
        return self._levels[k]

    def levels_for(self, s):
        """Two neighbouring pyramid levels and blend weights (trilinear), so zooms never 'pop'."""
        self.master()
        if s >= self.L:
            return [(self._level(0), 1.0)]
        kf = math.log2(self.L / s) * 4
        k0 = int(math.floor(kf))
        w = kf - k0
        if w < 0.02:
            return [(self._level(k0), 1.0)]
        if w > 0.98:
            return [(self._level(k0 + 1), 1.0)]
        return [(self._level(k0), 1.0 - w), (self._level(k0 + 1), w)]


# --------------------------------------------------------------------------- procedural textures


def _streak_texture(w, h, n, len_rng, width, bright_rng, slant, seed, blur=0.0, heads=False):
    rng = np.random.default_rng(seed)
    tex = np.zeros((h, w), np.float32)
    for _ in range(n):
        x = rng.uniform(0, w)
        y = rng.uniform(0, h)
        ln = rng.uniform(*len_rng)
        b = rng.uniform(*bright_rng)
        dx = slant * ln
        for ox in (-w, 0, w):           # draw wrapped copies so the texture tiles
            for oy in (-h, 0, h):
                p0 = (int((x + ox) * 16), int((y + oy) * 16))
                p1 = (int((x + ox + dx) * 16), int((y + oy + ln) * 16))
                if -200 * 16 < p0[1] < (h + 200) * 16 and -200 * 16 < p0[0] < (w + 200) * 16:
                    cv2.line(tex, p0, p1, float(b), width, cv2.LINE_AA, shift=4)
                    if heads:
                        cv2.circle(tex, p1, 2 * 16, float(min(1.0, b * 1.4)), -1, cv2.LINE_AA, shift=4)
    if blur > 0:
        tex = cv2.GaussianBlur(tex, (0, 0), blur)
    return tex


class Textures:
    def __init__(self, seed=0):
        self.glass_fast = _streak_texture(W, H, 1400, (25, 110), 1, (0.15, 0.7), 0.0, seed + 1, 0.6)
        self.glass_slow = _streak_texture(W, H, 160, (40, 160), 2, (0.15, 0.55), 0.0, seed + 2, 0.8, heads=True)
        self.rain_far = _streak_texture(W, H, 3600, (14, 40), 1, (0.2, 0.6), -0.13, seed + 3, 0.5)
        self.rain_mid = _streak_texture(W, H, 900, (40, 95), 2, (0.25, 0.7), -0.13, seed + 4, 0.8)
        self.rain_near = _streak_texture(W, H, 110, (140, 300), 4, (0.3, 0.8), -0.13, seed + 5, 2.4)
        rng = np.random.default_rng(seed + 9)
        self.grain = [cv2.resize(rng.standard_normal((H // 2, W // 2)).astype(np.float32), (W, H),
                                 interpolation=cv2.INTER_LINEAR) for _ in range(10)]
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
        self.vignette = (1 - 0.30 * np.clip(r, 0, 1.6) ** 2.4).clip(0.35, 1).astype(np.float32)
        self.radial = np.clip((r - 0.55) / 0.6, 0, 1).astype(np.float32)
        # dust sprites (gaussian dots)
        self.sprites = {}
        for rad in (1.0, 1.6, 2.4, 6.0):
            k = int(rad * 3) * 2 + 1
            g = cv2.getGaussianKernel(k, rad)
            self.sprites[rad] = (g @ g.T / (g @ g.T).max()).astype(np.float32)


def scroll(tex, dx, dy):
    """Wrap-scroll a tiled texture by (dx, dy) pixels."""
    h, w = tex.shape
    oy = int(dy) % h
    ox = int(dx) % w
    t = np.roll(tex, oy, axis=0) if oy else tex
    return np.roll(t, ox, axis=1) if ox else t


# --------------------------------------------------------------------------- shot rendering


class Renderer:
    def __init__(self, images, shots, overlays, tl, seed=0):
        self.images = images
        self.shots = shots
        self.overlays = overlays
        self.tl = tl
        self.tex = Textures(seed)
        self.U = (np.arange(W, dtype=np.float32) - W / 2 + 0.5)[None, :]
        self.V = (np.arange(H, dtype=np.float32) - H / 2 + 0.5)[:, None]
        hw, hh = W // 2, H // 2
        self.Uh = ((np.arange(hw, dtype=np.float32) + 0.5) * 2 - W / 2)[None, :]
        self.Vh = ((np.arange(hh, dtype=np.float32) + 0.5) * 2 - H / 2)[:, None]
        rng = np.random.default_rng(seed + 100)
        self.dust = {}
        for si, sh in enumerate(shots):
            n = sh.get("fx", {}).get("dust", 0)
            if n:
                self.dust[si] = {
                    "p": rng.uniform([0, 0], [W, H], (n, 2)),
                    "v": rng.normal([0, -6], [7, 6], (n, 2)),
                    "w": rng.uniform(0.08, 0.3, n), "ph": rng.uniform(0, 6.28, n),
                    "a": rng.uniform(0.25, 0.85, n),
                    "r": rng.choice([1.0, 1.6, 2.4, 6.0], n, p=[0.45, 0.33, 0.14, 0.08]),
                }

    # camera ------------------------------------------------------------------
    def camera(self, sh, t):
        keys = sh["cam"]
        c = {k: hermite_track(keys, k, t) for k in ("cx", "cy", "z", "rot", "px", "py", "dolly", "d0")}
        c["z"] = max(1.03, c["z"] or 1.0)
        c["rot"] = c["rot"] or 0.0
        c["px"] = c["px"] or 0.0
        c["py"] = c["py"] or 0.0
        c["dolly"] = c["dolly"] or 0.0
        c["d0"] = c["d0"] if c["d0"] is not None else 0.5
        hh = sh.get("handheld", 0.0)
        if hh:
            seed = sh.get("seed", 3)
            c["cx"] += hh * 0.010 * fbm(t, seed, 0.35)
            c["cy"] += hh * 0.008 * fbm(t, seed + 1, 0.3)
            c["rot"] += hh * 0.25 * fbm(t, seed + 2, 0.25)
        for kt, amp in sh.get("shake", []):
            dt = t - kt
            if 0 <= dt < 0.35:
                c["cy"] += amp * 0.0016 * math.exp(-dt / 0.06) * math.cos(dt * 70)
        return c

    def sample(self, img, c, need_masks=True):
        s = (W / img.w0) * c["z"]
        # keep the window inside the image
        # parallax can pull samples beyond the window: keep that margin inside the image
        margin = (abs(c["px"]) + abs(c["py"]) + abs(c["dolly"]) * H / 2) * 0.8 / s + 2
        hw, hh = W / (2 * s) + margin, H / (2 * s) + margin
        cx = min(max(c["cx"] * img.w0, hw), img.w0 - hw) if img.w0 > 2 * hw else img.w0 / 2
        cy = min(max(c["cy"] * img.h0, hh), img.h0 - hh) if img.h0 > 2 * hh else img.h0 / 2
        cr, sr = math.cos(math.radians(c["rot"])), math.sin(math.radians(c["rot"]))
        # half-res: depth and displacement
        uh = cr * self.Uh - sr * self.Vh
        vh = sr * self.Uh + cr * self.Vh
        x0h = (cx + uh / s).astype(np.float32)
        y0h = (cy + vh / s).astype(np.float32)
        Dh = cv2.remap(img.depth, x0h - 0.5, y0h - 0.5, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        k = Dh - c["d0"]
        dxh = (k * (c["px"] + c["dolly"] * uh) / s).astype(np.float32)
        dyh = (k * (c["py"] + c["dolly"] * vh) / s).astype(np.float32)
        dx = cv2.resize(dxh, (W, H), interpolation=cv2.INTER_LINEAR)
        dy = cv2.resize(dyh, (W, H), interpolation=cv2.INTER_LINEAR)
        u = cr * self.U - sr * self.V
        v = sr * self.U + cr * self.V
        x = cx + u / s + dx
        y = cy + v / s + dy
        frame = None
        for (lvl, L), wgt in img.levels_for(s):
            mx = (x * L - 0.5).astype(np.float32)
            my = (y * L - 0.5).astype(np.float32)
            f = cv2.remap(lvl, mx, my, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            frame = f * wgt if frame is None else frame + f * wgt
        out = {"frame": np.clip(frame, 0, 1), "s": s}
        if need_masks:
            xh = (x0h + dxh)
            yh = (y0h + dyh)
            out["D"] = cv2.resize(Dh, (W, H), interpolation=cv2.INTER_LINEAR)
            out["win"] = cv2.resize(cv2.remap(img.window, xh - 0.5, yh - 0.5, cv2.INTER_LINEAR,
                                              borderMode=cv2.BORDER_REFLECT), (W, H))
            out["warm"] = cv2.resize(cv2.remap(img.warm, xh - 0.5, yh - 0.5, cv2.INTER_LINEAR,
                                               borderMode=cv2.BORDER_REFLECT), (W, H))
        return out

    # effects -----------------------------------------------------------------
    def shot_frame(self, si, t, fi):
        sh = self.shots[si]
        img = self.images[sh["image"]]
        c = self.camera(sh, t)
        S = self.sample(img, c)
        f = S["frame"]
        sharp = sh.get("sharpen", 0.45)
        if sharp:
            f = f + sharp * (f - cv2.GaussianBlur(f, (0, 0), 1.3))
        fx = sh.get("fx", {})
        warm, win, D = S["warm"], S["win"], S["D"]
        tt = t - sh["start"]

        # lamp flicker (+ the light it throws)
        fl = fx.get("flicker", 0.0)
        if fl:
            n = fbm(t, 11 + si, 3.0) + 0.5 * fbm(t, 23 + si, 9.0)
            f *= (1 + fl * n * warm)[..., None]

        # exposure / warmth keyframes
        ev = hermite_track(sh.get("exp", []), "ev", t) if sh.get("exp") else 0.0
        if ev:
            f *= 2 ** ev
        warmth = hermite_track(sh.get("exp", []), "warmth", t) if sh.get("exp") else 0.0
        if warmth:
            f *= np.array([1 + 0.06 * warmth, 1 + 0.015 * warmth, 1 - 0.07 * warmth], np.float32)

        # rain on the window glass
        gr = fx.get("glass_rain", 0.0)
        if gr:
            fast = scroll(self.tex.glass_fast, 0, tt * 820)
            slow = scroll(self.tex.glass_slow, 0, tt * 55)
            m = win * gr
            lum = f.mean(axis=2)
            streak = (fast * 0.55 + slow * 0.8) * m * (0.35 + lum)
            f += streak[..., None] * np.array([0.78, 0.88, 1.0], np.float32)

        # outdoor rain, layered with depth occlusion and lantern light
        orr = fx.get("outdoor_rain", 0.0)
        if orr:
            glow = cv2.GaussianBlur(warm, (0, 0), 25)
            col_cool = np.array([0.72, 0.82, 0.95], np.float32)
            col_warm = np.array([1.0, 0.78, 0.48], np.float32)
            behind = np.clip((0.55 - D) / 0.2, 0, 1)
            far = scroll(self.tex.rain_far, tt * 1350 * 0.13 * -1, tt * 1350) * behind * 0.55
            mid = scroll(self.tex.rain_mid, tt * 1900 * 0.13 * -1, tt * 1900) * 0.42
            near = scroll(self.tex.rain_near, tt * 2700 * 0.13 * -1, tt * 2700) * 0.32
            r = (far + mid + near) * orr
            tint = col_cool[None, None, :] * (1 - glow[..., None]) + col_warm[None, None, :] * glow[..., None]
            f += (r * (0.25 + 1.3 * glow))[..., None] * tint
            f *= 1 - 0.06 * orr  # wet, dim air

        # lightning
        strikes = fx.get("lightning", [])
        if strikes:
            le = lightning_env(t, strikes)
            if le > 0:
                f += (le * (0.75 * win + 0.08 * (1 - D)))[..., None] * np.array([0.7, 0.82, 1.0], np.float32)
                f *= 1 + 0.12 * le

        # depth of field
        dof = sh.get("dof")
        if dof:
            fd = hermite_track(dof, "focus", t)
            ap = hermite_track(dof, "ap", t)
            if ap and ap > 0:
                coc = np.clip(np.abs(D - fd) * ap, 0, 1)
                small = cv2.resize(f, (W // 2, H // 2), interpolation=cv2.INTER_AREA)
                b1 = cv2.resize(cv2.GaussianBlur(small, (0, 0), 2.2), (W, H))
                b2 = cv2.resize(cv2.GaussianBlur(small, (0, 0), 6.0), (W, H))
                c1 = np.clip(coc * 2, 0, 1)[..., None]
                c2 = np.clip(coc * 2 - 1, 0, 1)[..., None]
                f = f * (1 - c1) + b1 * c1
                f = f * (1 - c2) + b2 * c2

        # bloom on bright warm light
        bl = fx.get("bloom", 0.35)
        if bl:
            small = cv2.resize(f, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
            bright = np.clip(small - 0.62, 0, None)
            glow = cv2.GaussianBlur(bright, (0, 0), 9) + 0.6 * cv2.GaussianBlur(bright, (0, 0), 26)
            f += cv2.resize(glow, (W, H)) * bl * np.array([1.0, 0.8, 0.58], np.float32)

        # dust motes floating in the lamp light
        if si in self.dust:
            f += self._dust(si, tt, warm)[..., None] * np.array([1.0, 0.86, 0.66], np.float32)

        # grade
        g = sh.get("grade")
        if g == "flashback":
            lum = (f * np.array([0.299, 0.587, 0.114], np.float32)).sum(axis=2, keepdims=True)
            f = lum + (f - lum) * 0.42
            f = f * np.array([0.9, 0.97, 1.07], np.float32) + np.array([0.01, 0.018, 0.04], np.float32) * (1 - lum)
            f = 0.045 + f * 0.93
            soft = cv2.resize(cv2.GaussianBlur(cv2.resize(f, (W // 4, H // 4), interpolation=cv2.INTER_AREA), (0, 0), 3), (W, H))
            rad = self.tex.radial[..., None]
            f = f * (1 - 0.75 * rad) + soft * (0.75 * rad)
            hal = cv2.resize(cv2.GaussianBlur(np.clip(cv2.resize(f, (W // 4, H // 4)) - 0.55, 0, None), (0, 0), 8), (W, H))
            f += hal * np.array([0.45, 0.16, 0.08], np.float32)
            rng = np.random.default_rng(fi)
            f *= 1 + 0.025 * rng.standard_normal()
        return f

    def _dust(self, si, tt, warm):
        d = self.dust[si]
        layer = np.zeros((H, W), np.float32)
        p = d["p"] + d["v"] * tt
        p[:, 0] += 9 * np.sin(d["w"] * tt * 6.28 + d["ph"])
        p[:, 1] += 6 * np.cos(d["w"] * 0.7 * tt * 6.28 + d["ph"])
        p[:, 0] %= W
        p[:, 1] %= H
        light = cv2.GaussianBlur(warm, (0, 0), 30) if warm is not None else np.ones((H, W), np.float32)
        for (x, y), a, r in zip(p, d["a"], d["r"]):
            spr = self.tex.sprites[r]
            k = spr.shape[0] // 2
            xi, yi = int(x), int(y)
            if k <= xi < W - k - 1 and k <= yi < H - k - 1:
                lit = light[yi, xi]
                amp = a * (0.04 + 1.6 * lit) * (0.35 if r == 6.0 else 1.0)
                fx, fy = x - xi, y - yi
                layer[yi - k:yi + k + 1, xi - k:xi + k + 1] += spr * amp * (1 - fx) * (1 - fy)
                layer[yi - k:yi + k + 1, xi - k + 1:xi + k + 2] += spr * amp * fx * (1 - fy)
                layer[yi - k + 1:yi + k + 2, xi - k:xi + k + 1] += spr * amp * (1 - fx) * fy
                layer[yi - k + 1:yi + k + 2, xi - k + 1:xi + k + 2] += spr * amp * fx * fy
        return layer * 0.55

    # compositing ---------------------------------------------------------------
    def frame(self, fi):
        t = fi / FPS
        active = []
        for si, sh in enumerate(self.shots):
            a, b = sh["start"], sh["end"]
            if a <= t < b:
                fin = sh.get("fade_in", 0.0)
                fout = sh.get("fade_out", 0.0)
                al = 1.0
                if fin > 0:
                    al *= smoothstep(a, a + fin, t)
                if fout > 0:
                    al *= 1 - smoothstep(b - fout, b, t)
                active.append((si, al))
        out = np.zeros((H, W, 3), np.float32)
        if not active:
            pass
        elif len(active) == 1:
            out = self.shot_frame(active[0][0], t, fi) * active[0][1]
        else:
            # two shots overlapping: transition
            (sa, aa), (sb, ab) = active[0], active[-1]
            A = self.shot_frame(sa, t, fi)
            B = self.shot_frame(sb, t, fi)
            trans = self.shots[sb].get("trans", "dissolve")
            p = smoothstep(self.shots[sb]["start"], self.shots[sb]["start"] + self.shots[sb].get("fade_in", 1.0), t)
            if trans in ("memory_in", "memory_out"):
                bell = math.sin(math.pi * p) ** 2
                sig = 0.5 + 6 * bell
                A = cv2.GaussianBlur(A, (0, 0), sig)
                B = cv2.GaussianBlur(B, (0, 0), sig)
                out = A * (1 - p) + B * p
                strength = 0.34 if trans == "memory_in" else 0.22
                out = out * (1 - 0.22 * bell) + bell * strength * np.array([1.0, 0.93, 0.85], np.float32)
            else:
                out = A * (1 - p) + B * p
        out = out * 1.06 + 0.006          # gentle lift: phones are often viewed at low brightness
        # global overlays (title, handwriting, subtitles, fades)
        for ov in self.overlays:
            ov(out, t)
        # vignette + grain
        out *= self.tex.vignette[..., None]
        lum = out.mean(axis=2, keepdims=True)
        gamt = 0.012 * (1.1 - np.clip(lum, 0, 1))
        out += self.tex.grain[fi % len(self.tex.grain)][..., None] * gamt
        return np.clip(out, 0, 1)


# --------------------------------------------------------------------------- encoding

FFMPEG_V = ["-c:v", "libx264", "-preset", "medium", "-crf", "19", "-maxrate", "10M", "-bufsize", "20M",
            "-tune", "film",
            "-pix_fmt", "yuv420p", "-profile:v", "high",
            "-x264-params", "keyint=60:min-keyint=60:scenecut=0",
            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709"]


_R = None  # renderer shared with forked workers (avoids pickling large arrays)


def _worker(args):
    a, b, path, threads = args
    renderer = _R
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-vf", "scale=out_color_matrix=bt709:out_range=tv",
           *FFMPEG_V, "-threads", str(threads), path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(a, b):
        fr = renderer.frame(fi)
        p.stdin.write((fr * 255 + 0.5).astype(np.uint8).tobytes())
    p.stdin.close()
    p.wait()
    return path


def render_video(renderer, nframes, out_path, audio_path, work, workers=4, threads=1, frames=None):
    seg_dir = os.path.join(work, "segments")
    os.makedirs(seg_dir, exist_ok=True)
    rng = frames or (0, nframes)
    bounds = np.linspace(rng[0], rng[1], workers + 1).astype(int)
    global _R
    _R = renderer
    jobs = [(int(bounds[i]), int(bounds[i + 1]), os.path.join(seg_dir, f"seg_{i:02d}.mp4"), threads)
            for i in range(workers)]
    ctx = mp.get_context("fork")
    with ctx.Pool(workers) as pool:
        segs = pool.map(_worker, jobs)
    lst = os.path.join(seg_dir, "list.txt")
    with open(lst, "w") as f:
        for s in segs:
            f.write(f"file '{s}'\n")
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst]
    if audio_path:
        t0 = rng[0] / FPS
        cmd += ["-ss", f"{t0:.4f}", "-i", audio_path, "-map", "0:v", "-map", "1:a",
                "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-shortest"]
    cmd += ["-c:v", "copy", "-movflags", "+faststart", out_path]
    subprocess.run(cmd, check=True)
    return out_path


def still(renderer, t, path):
    fr = renderer.frame(int(round(t * FPS)))
    Image.fromarray((fr * 255 + 0.5).astype(np.uint8)).save(path)
    return path
