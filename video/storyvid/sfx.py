"""Procedural sound effects (no samples needed, so everything is license-free)."""
import numpy as np
from scipy import signal

from .common import SR, butter, peaking


def _rng(seed):
    return np.random.default_rng(seed)


def smooth_noise(n, rate_hz, rng):
    """Smooth random curve in [-1, 1] with features at roughly `rate_hz`."""
    k = max(2, int(n / SR * rate_hz) + 3)
    pts = rng.uniform(-1, 1, k)
    x = np.linspace(0, k - 1, n)
    return np.interp(x, np.arange(k), pts).astype(np.float32)


def _droplet_layer(n, rate, f_lo, f_hi, dec_lo, dec_hi, rng, kernels=8):
    out = np.zeros(n, np.float32)
    for _ in range(kernels):
        imp = np.zeros(n, np.float32)
        cnt = rng.poisson(rate * n / SR / kernels)
        pos = rng.integers(0, n, cnt)
        amp = np.exp(rng.normal(0, 0.8, cnt)).astype(np.float32)
        amp *= rng.choice([-1, 1], cnt)
        np.add.at(imp, pos, amp)
        f = np.exp(rng.uniform(np.log(f_lo), np.log(f_hi)))
        d = rng.uniform(dec_lo, dec_hi)
        t = np.arange(int(d * 6 * SR)) / SR
        ker = np.sin(2 * np.pi * f * t * (1 - 0.15 * t / t[-1])) * np.exp(-t / d)
        out += signal.fftconvolve(imp, ker.astype(np.float32), mode="same")
    return out


def rain(duration, kind="interior", seed=0):
    """Stereo rain bed. kind: 'interior' (rain on glass, muffled) or 'exterior'."""
    rng = _rng(seed)
    n = int(duration * SR)
    chans = []
    for c in range(2):
        white = rng.standard_normal(n).astype(np.float32)
        hiss = butter(butter(white, "high", 400), "low", 7000 if kind == "exterior" else 2600)
        brown = np.cumsum(rng.standard_normal(n)).astype(np.float32)
        brown = butter(butter(brown, "high", 25, 2), "low", 250)
        brown /= np.abs(brown).max() + 1e-9
        if kind == "exterior":
            drops = _droplet_layer(n, 2600, 1500, 7000, 0.0015, 0.006, rng)
            drops += 0.6 * _droplet_layer(n, 260, 400, 1400, 0.004, 0.02, rng)
            x = 0.55 * hiss + 0.035 * drops + 0.25 * brown
        else:
            drops = _droplet_layer(n, 700, 900, 3200, 0.002, 0.008, rng)
            drops += 0.8 * _droplet_layer(n, 90, 250, 900, 0.006, 0.03, rng)
            drops = butter(drops, "low", 3500)
            x = 0.35 * hiss + 0.05 * drops + 0.18 * brown
        gust = 1.0 + 0.22 * smooth_noise(n, 0.15, rng) + 0.08 * smooth_noise(n, 0.7, rng)
        chans.append(x * gust)
    out = np.stack(chans, axis=1)
    return (out / (np.sqrt((out ** 2).mean()) + 1e-9) * 0.1).astype(np.float32)


def thunder(kind="close", seed=0):
    rng = _rng(seed)
    dur = 6.0 if kind == "close" else 7.0
    n = int(dur * SR)
    t = np.arange(n) / SR
    chans = []
    for c in range(2):
        brown = np.cumsum(rng.standard_normal(n)).astype(np.float32)
        brown = butter(brown, "high", 22, 2)
        rumble = butter(brown, "low", 260 if kind == "close" else 130)
        rumble /= np.abs(rumble).max() + 1e-9
        env = np.zeros(n, np.float32)
        bumps = [(0.12, 1.0, 0.55), (0.55, 0.85, 0.75), (1.25, 0.6, 0.9), (2.1, 0.35, 1.0)]
        if kind != "close":
            bumps = [(0.8, 0.7, 1.6), (2.0, 1.0, 2.0), (3.6, 0.6, 2.4)]
        for at, a, dec in bumps:
            at += rng.uniform(-0.1, 0.1)
            e = np.where(t >= at, np.exp(-(t - at) / dec) * (1 - np.exp(-(t - at) / 0.08)), 0)
            env += a * e
        sub = np.sin(2 * np.pi * 38 * t + 2 * np.sin(2 * np.pi * 0.7 * t)) * env * 0.35
        x = rumble * env * (1 + 0.3 * smooth_noise(n, 6, rng)) + sub
        if kind == "close":
            w = rng.standard_normal(n).astype(np.float32)
            crack = butter(butter(w, "high", 500), "low", 6500)
            ce = np.zeros(n, np.float32)
            for at, a in [(0.0, 1.0), (0.05, 0.7), (0.13, 0.55), (0.24, 0.35)]:
                ce += a * np.where(t >= at, np.exp(-(t - at) / 0.06), 0)
            x = x + 0.55 * crack * ce
        chans.append(x)
    out = np.stack(chans, axis=1)
    fade = np.clip((dur - t) / (2.5 if kind == "close" else 2.0), 0, 1)[:, None]
    return (out * fade / (np.abs(out).max() + 1e-9)).astype(np.float32)


def knock(strength=1.0, seed=0):
    rng = _rng(seed)
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    modes = [(92, 0.11, 1.0), (176, 0.08, 0.85), (287, 0.06, 0.6), (515, 0.04, 0.45),
             (860, 0.025, 0.3), (1580, 0.014, 0.18)]
    x = np.zeros(n, np.float32)
    for f, d, a in modes:
        f *= rng.uniform(0.96, 1.04)
        x += a * np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28)) * np.exp(-t / d)
    for f in (2350, 3720, 5100):  # glass pane rattle
        x += 0.06 * np.sin(2 * np.pi * f * rng.uniform(0.97, 1.03) * t) * np.exp(-t / 0.03)
    burst = rng.standard_normal(int(0.002 * SR)) * np.hanning(int(0.002 * SR))
    x[: len(burst)] += 0.5 * burst
    x *= (1 - np.exp(-t / 0.0015))
    return (x / np.abs(x).max() * strength).astype(np.float32)


def phone_filter(x, drive=1.6):
    y = butter(butter(x, "high", 330, 4), "low", 3300, 4)
    y = peaking(y, 1600, 4.0, 0.9)
    y = np.tanh(drive * y / (np.abs(y).max() + 1e-9)) / np.tanh(drive)
    return y.astype(np.float32)


def ringback(on=1.0):
    """German ringback tone (Freizeichen): 425 Hz."""
    n = int(on * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 425 * t)
    ramp = int(0.012 * SR)
    x[:ramp] *= np.linspace(0, 1, ramp)
    x[-ramp:] *= np.linspace(1, 0, ramp)
    return phone_filter(x.astype(np.float32), 1.2) * 0.8


def pickup_click(seed=3):
    rng = _rng(seed)
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    x = np.zeros(n, np.float32)
    x[0] = 1.0
    x[int(0.035 * SR)] = -0.6
    x = butter(x, "high", 900) * 6
    x += 0.4 * np.sin(2 * np.pi * 120 * t) * np.exp(-t / 0.02)
    x += 0.15 * rng.standard_normal(n) * np.exp(-t / 0.05)
    return phone_filter(x.astype(np.float32), 1.0) * 0.7


def line_noise(duration, seed=4):
    rng = _rng(seed)
    n = int(duration * SR)
    t = np.arange(n) / SR
    x = rng.standard_normal(n).astype(np.float32) * 0.6
    x += 0.15 * np.sin(2 * np.pi * 50 * t) + 0.08 * np.sin(2 * np.pi * 150 * t)
    return phone_filter(x, 1.0) * 0.12


def paper(duration=1.1, seed=5):
    rng = _rng(seed)
    n = int(duration * SR)
    t = np.arange(n) / SR
    w = rng.standard_normal(n).astype(np.float32)
    slide = butter(butter(w, "high", 1200), "low", 9000)
    crackle = np.zeros(n, np.float32)
    cnt = rng.poisson(55 * duration)
    np.add.at(crackle, rng.integers(0, n, cnt), rng.normal(0, 1, cnt))
    crackle = butter(signal.fftconvolve(crackle, np.exp(-np.arange(80) / 12.0), mode="same"), "high", 1500)
    env = np.clip(t / 0.12, 0, 1) * np.clip((duration - t) / 0.35, 0, 1)
    env *= 0.6 + 0.4 * smooth_noise(n, 9, rng) ** 2
    x = (0.5 * slide + 0.9 * crackle) * env
    # soft tap as it settles on the desk
    tt = np.arange(int(0.25 * SR)) / SR
    tap = (np.sin(2 * np.pi * 150 * tt) * np.exp(-tt / 0.03) + 0.3 * butter(rng.standard_normal(len(tt)), "low", 900) * np.exp(-tt / 0.02))
    i = int((duration - 0.25) * SR)
    x[i:i + len(tap)] += 0.5 * tap[: n - i]
    return (x / (np.abs(x).max() + 1e-9)).astype(np.float32)


def clock(duration, interval=1.0, seed=6):
    rng = _rng(seed)
    n = int(duration * SR)
    out = np.zeros(n, np.float32)
    tick_n = int(0.06 * SR)
    tt = np.arange(tick_n) / SR
    for k in range(int(duration / interval)):
        f = 3100 if k % 2 == 0 else 2550
        burst = rng.standard_normal(tick_n) * np.exp(-tt / 0.0025)
        res = np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.012) + 0.5 * np.sin(2 * np.pi * f * 1.7 * tt) * np.exp(-tt / 0.006)
        tick = butter(0.4 * burst + res, "high", 1200)
        i = int((k * interval + rng.normal(0, 0.004)) * SR)
        if 0 <= i < n - tick_n:
            out[i:i + tick_n] += tick * (0.85 if k % 2 else 1.0)
    return out / (np.abs(out).max() + 1e-9)


def whoosh(duration=1.5, reverse=True, seed=7):
    """Reverse-swell whoosh (reverse=True swells up, else decays)."""
    rng = _rng(seed)
    n = int(duration * SR)
    t = np.arange(n) / SR
    chans = []
    for c in range(2):
        w = rng.standard_normal(n).astype(np.float32)
        # sweep a band-pass by blending a few fixed bands
        bands = [butter(butter(w, "high", lo), "low", hi) for lo, hi in ((150, 500), (400, 1400), (1200, 4000), (3000, 9000))]
        pos = (t / duration) * (len(bands) - 1)
        x = np.zeros(n, np.float32)
        for k, b in enumerate(bands):
            x += b * np.clip(1 - np.abs(pos - k), 0, 1)
        env = (np.exp(3.2 * t / duration) - 1) / (np.e ** 3.2 - 1)
        env *= np.clip((duration - t) / 0.06, 0, 1)
        chans.append(x * env)
    out = np.stack(chans, axis=1)
    if not reverse:
        out = out[::-1]
    return (out / (np.abs(out).max() + 1e-9)).astype(np.float32)


def boom(seed=8):
    rng = _rng(seed)
    n = int(4.0 * SR)
    t = np.arange(n) / SR
    f = 34 + 40 * np.exp(-t / 0.25)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t / 1.3) * (1 - np.exp(-t / 0.004))
    x += 0.5 * butter(rng.standard_normal(n), "low", 160) * np.exp(-t / 0.18)
    return (x / np.abs(x).max()).astype(np.float32)


def heartbeat():
    n = int(0.75 * SR)
    t = np.arange(n) / SR
    x = np.zeros(n, np.float32)
    for at, f, a in ((0.0, 58, 1.0), (0.27, 46, 0.7)):
        tt = np.clip(t - at, 0, None)
        x += a * np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.07) * (t >= at) * (1 - np.exp(-tt / 0.006))
    return x / np.abs(x).max()


def room_tone(duration, seed=9):
    rng = _rng(seed)
    n = int(duration * SR)
    b = np.cumsum(rng.standard_normal(n)).astype(np.float32)
    b = butter(butter(b, "high", 30, 2), "low", 220)
    return np.stack([b, np.roll(b, 997)], axis=1) / (np.abs(b).max() + 1e-9)
