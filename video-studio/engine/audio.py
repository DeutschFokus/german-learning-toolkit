"""Procedural sound for LUMEN episodes: synths, SFX, score helpers, mixing.

Everything is generated from scratch with numpy/scipy (no samples, no
licences to track). Sounds are placed on a stereo Track at cue times taken
from the timeline, so a re-timed narration moves the sound design with it.
"""
from __future__ import annotations

import math

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt, resample_poly

SR = 48000


# --------------------------------------------------------------------------- basics

def t_axis(dur):
    return np.arange(int(round(dur * SR))) / SR


def note_hz(name: str) -> float:
    """'A4' -> 440.0, supports sharps/flats ('Bb3', 'F#2')."""
    names = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    n = names[name[0]]
    rest = name[1:]
    if rest.startswith("#"):
        n += 1
        rest = rest[1:]
    elif rest.startswith("b"):
        n -= 1
        rest = rest[1:]
    octave = int(rest)
    midi = 12 * (octave + 1) + n
    return 440.0 * 2 ** ((midi - 69) / 12)


def sos(kind, f, order=2):
    f = np.atleast_1d(f) / (SR / 2)
    f = np.clip(f, 1e-4, 0.999)
    return butter(order, f if len(f) > 1 else f[0], btype=kind, output="sos")


def lp(x, f, order=2):
    return sosfilt(sos("lowpass", f, order), x, axis=0)


def hp(x, f, order=2):
    return sosfilt(sos("highpass", f, order), x, axis=0)


def bp(x, lo, hi, order=2):
    return sosfilt(sos("bandpass", [lo, hi], order), x, axis=0)


def sweep_filter(x, f_start, f_end, kind="bandpass", q=1.2, block=512, curve="exp"):
    """Time-varying filter by blocks (filter state carried across blocks)."""
    n = len(x)
    out = np.zeros_like(x)
    zi = None
    nb = max(1, n // block + 1)
    for b in range(nb):
        i0, i1 = b * block, min(n, (b + 1) * block)
        if i0 >= n:
            break
        u = b / max(1, nb - 1)
        f = f_start * (f_end / f_start) ** u if curve == "exp" else f_start + (f_end - f_start) * u
        if kind == "bandpass":
            s = sos("bandpass", [f / (1 + 0.5 / q), min(f * (1 + 0.5 / q), SR * 0.45)], 2)
        else:
            s = sos(kind, f, 2)
        if zi is None or zi.shape != (s.shape[0], 2):
            zi = np.zeros((s.shape[0], 2))
        out[i0:i1], zi = sosfilt(s, x[i0:i1], zi=zi)
    return out


def env_adsr(n, a, d, s, r, sustain_level=0.7):
    a_n, d_n, r_n = int(a * SR), int(d * SR), int(r * SR)
    s_n = max(0, n - a_n - d_n - r_n)
    e = np.concatenate([np.linspace(0, 1, max(a_n, 1), endpoint=False) ** 1.5,
                        np.linspace(1, sustain_level, max(d_n, 1), endpoint=False),
                        np.full(s_n, sustain_level),
                        np.linspace(sustain_level, 0, max(r_n, 1)) ** 1.6])
    return e[:n] if len(e) >= n else np.pad(e, (0, n - len(e)))


def env_exp(n, decay, attack=0.002):
    t = np.arange(n) / SR
    e = np.exp(-t / decay)
    a = int(attack * SR)
    if a > 0:
        e[:a] *= np.linspace(0, 1, a)
    return e


def saw(freq, n, phase=0.0):
    """Band-limited-ish saw (additive, harmonics up to 9 kHz)."""
    t = np.arange(n) / SR
    out = np.zeros(n)
    kmax = max(1, int(9000 / max(freq, 1)))
    for k in range(1, min(kmax, 40) + 1):
        out += ((-1) ** (k + 1)) * np.sin(2 * np.pi * k * freq * t + phase * k) / k
    return out * (2 / np.pi)


def stereo(x, pan=0.0, width=0.0):
    """Mono -> stereo with equal-power pan (-1..1); width adds a tiny Haas offset."""
    pan = max(-1.0, min(1.0, pan))
    l = math.cos((pan + 1) * math.pi / 4)
    r = math.sin((pan + 1) * math.pi / 4)
    L_, R_ = x * l, x * r
    if width > 0:
        d = int(width * 0.012 * SR)
        R_ = np.concatenate([np.zeros(d), R_[:len(R_) - d]]) if d > 0 else R_
    return np.stack([L_, R_], axis=1)


def make_ir(seconds=3.0, damp=6000.0, predelay=0.02, seed=2, decay_db=60.0):
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    env = 10 ** (-(decay_db / 20) * t / seconds)
    ir = rng.normal(0, 1, (n, 2)) * env[:, None]
    # darker tail: progressively low-passed
    early = lp(ir, damp)
    late = lp(ir, damp * 0.35)
    mixk = np.clip(t / seconds * 1.6, 0, 1)[:, None]
    ir = early * (1 - mixk) + late * mixk
    pd = int(predelay * SR)
    ir = np.concatenate([np.zeros((pd, 2)), ir])
    return ir / np.sqrt((ir ** 2).sum(axis=0, keepdims=True))


def reverb(x, ir, wet=0.3):
    if x.ndim == 1:
        x = stereo(x)
    y = np.stack([fftconvolve(x[:, 0], ir[:, 0])[:len(x)], fftconvolve(x[:, 1], ir[:, 1])[:len(x)]], axis=1)
    return x * (1 - wet) + y * wet * 2.0


# --------------------------------------------------------------------------- track

class Track:
    """A stereo buffer you drop sounds into at cue times."""

    def __init__(self, dur, extra=4.0):
        self.dur = dur
        self.buf = np.zeros((int((dur + extra) * SR), 2))

    def add(self, t, x, gain=1.0, pan=0.0):
        if x.ndim == 1:
            x = stereo(x, pan)
        i0 = int(round(t * SR))
        if i0 < 0:
            x = x[-i0:]
            i0 = 0
        i1 = min(len(self.buf), i0 + len(x))
        self.buf[i0:i1] += x[:i1 - i0] * gain

    def wrapped(self):
        """Fold everything past `dur` back onto the start (seamless loop tails)."""
        n = int(round(self.dur * SR))
        out = self.buf[:n].copy()
        tail = self.buf[n:]
        out[:min(n, len(tail))] += tail[:n]
        return out


# --------------------------------------------------------------------------- SFX

def sfx_boom(dur=2.6, f0=95, f1=32, seed=1):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t / 0.18)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * env_exp(n, 0.75, 0.003)
    rng = np.random.default_rng(seed)
    crack = lp(rng.normal(0, 1, n), 1800) * env_exp(n, 0.05, 0.001) * 0.7
    air = hp(rng.normal(0, 1, n), 4000) * env_exp(n, 0.25, 0.001) * 0.08
    return np.tanh((body * 1.0 + crack + air) * 1.4) * 0.9


def sfx_tick(pitch=2600.0, dur=0.12, bright=1.0, seed=3):
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    click = bp(rng.normal(0, 1, n), pitch * 0.8, min(pitch * 2.5, 20000)) * env_exp(n, 0.006, 0.0005)
    tone = (np.sin(2 * np.pi * pitch * t) + 0.5 * np.sin(2 * np.pi * pitch * 2.71 * t)) * env_exp(n, 0.018, 0.0005)
    body = np.sin(2 * np.pi * pitch * 0.25 * t) * env_exp(n, 0.012, 0.0005) * 0.6
    return (click * 0.6 * bright + tone * 0.5 + body) * 0.5


def sfx_whoosh(dur=1.0, f0=300, f1=4000, seed=5, peak=0.55):
    n = int(dur * SR)
    rng = np.random.default_rng(seed)
    noise = rng.normal(0, 1, n)
    x = sweep_filter(noise, f0, f1, "bandpass", q=1.5)
    u = np.linspace(0, 1, n)
    env = np.exp(-((u - peak) / 0.22) ** 2)
    return x * env * 0.9


def sfx_riser(dur=2.0, f0=200, f1=2400, seed=6):
    n = int(dur * SR)
    rng = np.random.default_rng(seed)
    noise = sweep_filter(rng.normal(0, 1, n), f0 * 2, f1 * 3, "bandpass", q=2.0)
    t = np.arange(n) / SR
    f = f0 * (f1 / f0) ** (t / dur)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25 + np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * 0.12
    env = (t / dur) ** 2.2
    return (noise * 0.7 + tone) * env * 0.8


def sfx_reverse_swell(dur=1.4, seed=7):
    x = sfx_whoosh(dur, 6000, 600, seed=seed, peak=0.5)
    n = len(x)
    env = np.linspace(0, 1, n) ** 3
    return x * env * 1.4


def sfx_ping(freq=1500.0, dur=1.2, decay=0.25):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = freq * (1 - 0.02 * (1 - np.exp(-t / 0.05)))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, decay, 0.002)
    x += 0.25 * np.sin(2 * np.pi * freq * 2.01 * t) * env_exp(n, decay * 0.4, 0.002)
    return x * 0.5


def sfx_blip(freq=1800.0, dur=0.07):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * freq * t) * env_exp(n, 0.02, 0.001) * 0.4


def sfx_chime(notes=("E6", "A6"), gap=0.09, dur=1.8):
    n = int((dur + gap * len(notes)) * SR)
    out = np.zeros(n)
    for k, nm in enumerate(notes):
        f = note_hz(nm)
        i0 = int(k * gap * SR)
        m = n - i0
        t = np.arange(m) / SR
        mod = 1.8 * np.exp(-t / 0.25)
        x = np.sin(2 * np.pi * f * t + mod * np.sin(2 * np.pi * f * 3.5 * t)) * env_exp(m, 0.55, 0.002)
        out[i0:] += x * 0.4
    return out


def sfx_buzz(dur=0.35, freq=92.0):
    n = int(dur * SR)
    x = lp(saw(freq, n) + 0.5 * saw(freq * 1.01, n), 1400)
    return x * env_adsr(n, 0.005, 0.05, 0.6, 0.12, 0.6) * 0.35


def sfx_laser(dur=0.9, f0=2600, f1=420):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t / 0.18)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.35, 0.002) * 0.35
    rng = np.random.default_rng(9)
    x += sweep_filter(rng.normal(0, 1, n), 7000, 900, "bandpass", q=2.0) * env_exp(n, 0.3, 0.002) * 0.5
    return x


def sfx_rumble(dur=3.0, seed=11):
    n = int(dur * SR)
    rng = np.random.default_rng(seed)
    x = lp(rng.normal(0, 1, n), 110, order=4) * 3.0
    x += lp(rng.normal(0, 1, n), 400) * 0.25
    return x * env_adsr(n, 0.08, 0.4, 0.6, dur * 0.6, 0.6)


def sfx_thump(freq=58.0, dur=0.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = freq * (1 + 0.6 * np.exp(-t / 0.03))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.12, 0.002) * 0.9


def sfx_shimmer(dur=3.0, base="D6", seed=13):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f0 = note_hz(base)
    out = np.zeros(n)
    rng = np.random.default_rng(seed)
    for k, ratio in enumerate((1.0, 1.5, 2.0, 2.5, 3.0)):
        trem = 0.6 + 0.4 * np.sin(2 * np.pi * rng.uniform(3, 7) * t + rng.uniform(0, 6))
        out += np.sin(2 * np.pi * f0 * ratio * t) * trem / (k + 1.5)
    return out * env_adsr(n, dur * 0.25, 0.2, 0.7, dur * 0.5, 0.7) * 0.18


def sfx_ruler(n_ticks=33, dur=1.2, f0=2200, f1=3400):
    """A fast run of tiny ticks (the ruler counting up)."""
    out = np.zeros(int((dur + 0.2) * SR))
    for k in range(n_ticks):
        u = k / max(1, n_ticks - 1)
        t0 = dur * (u ** 0.85)
        tick = sfx_tick(f0 + (f1 - f0) * u, 0.05, bright=0.6, seed=k) * (0.35 + 0.65 * (k % 10 == 0))
        i0 = int(t0 * SR)
        out[i0:i0 + len(tick)] += tick[:len(out) - i0]
    return out


def sfx_counter(dur=0.8, rate=26.0, f=2100.0):
    out = np.zeros(int((dur + 0.1) * SR))
    k = 0
    tt = 0.0
    while tt < dur:
        b = sfx_blip(f * (1 + 0.15 * (k % 3)), 0.03) * 0.5
        i0 = int(tt * SR)
        out[i0:i0 + len(b)] += b[:len(out) - i0]
        tt += 1.0 / rate
        k += 1
    return out


# --------------------------------------------------------------------------- music helpers

def pad_chord(notes, dur, cutoff=1400.0, detune_cents=7.0, attack=1.2, release=1.6, seed=0):
    n = int(dur * SR)
    out = np.zeros((n, 2))
    rng = np.random.default_rng(seed)
    for k, nm in enumerate(notes):
        f = note_hz(nm)
        for v, (cents, pan) in enumerate(((-detune_cents, -0.6), (0.0, 0.0), (detune_cents, 0.6))):
            fv = f * 2 ** (cents / 1200)
            x = saw(fv, n, phase=rng.uniform(0, 6.28))
            out += stereo(x, pan) * (0.6 if v == 1 else 0.45)
    out = lp(out, cutoff, order=2)
    env = env_adsr(n, attack, 0.5, 0.85, release, 0.85)
    return out * env[:, None] / max(1, len(notes)) * 0.5


def drone(freq, dur, lfo=0.07, amp=0.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * freq * 2 * t + 0.4) + 0.12 * np.sin(
        2 * np.pi * freq * 3 * t + 1.1)
    x *= 1 + 0.25 * np.sin(2 * np.pi * lfo * t)
    return x * env_adsr(n, 1.0, 0.3, 0.9, 1.5, 0.9) * amp


def pluck(freq, dur=1.6, bright=1.0, decay=0.45):
    n = int(dur * SR)
    t = np.arange(n) / SR
    mod = bright * 2.2 * np.exp(-t / 0.08)
    x = np.sin(2 * np.pi * freq * t + mod * np.sin(2 * np.pi * freq * 2.0 * t))
    x += 0.3 * np.sin(2 * np.pi * freq * 2 * t) * np.exp(-t / 0.2)
    return x * env_exp(n, decay, 0.003) * 0.35


def bass_note(freq, dur=0.5):
    n = int(dur * SR)
    x = lp(saw(freq, n) + 0.6 * np.sin(2 * np.pi * freq * np.arange(n) / SR), 500)
    return x * env_adsr(n, 0.008, 0.12, 0.55, 0.12, 0.55) * 0.45


# --------------------------------------------------------------------------- dynamics + mastering

def envelope(x, attack=0.02, release=0.25, win=0.01):
    mono = np.abs(x if x.ndim == 1 else x.mean(axis=1))
    w = max(1, int(win * SR))
    rms = np.sqrt(np.convolve(mono ** 2, np.ones(w) / w, mode="same"))
    out = np.zeros_like(rms)
    a = math.exp(-1 / (attack * SR))
    r = math.exp(-1 / (release * SR))
    # vectorised-enough one-pole follower on a decimated signal
    dec = 48
    small = rms[::dec]
    acc = np.zeros_like(small)
    prev = 0.0
    a_d, r_d = a ** dec, r ** dec
    for i, v in enumerate(small):
        k = a_d if v > prev else r_d
        prev = k * prev + (1 - k) * v
        acc[i] = prev
    out = np.interp(np.arange(len(rms)), np.arange(len(small)) * dec, acc)
    return out


def duck(music, voice, depth_db=-9.0, threshold=0.02, attack=0.04, release=0.35):
    env = envelope(voice, attack, release)
    k = np.clip(env / threshold, 0, 1)
    gain = 10 ** (depth_db * k / 20)
    return music * gain[:, None]


def compress(x, threshold_db=-22.0, ratio=3.0, attack=0.005, release=0.12, makeup_db=0.0):
    env = envelope(x, attack, release, win=0.005)
    lvl = 20 * np.log10(np.maximum(env, 1e-6))
    over = np.maximum(lvl - threshold_db, 0)
    gain_db = -over * (1 - 1 / ratio) + makeup_db
    g = 10 ** (gain_db / 20)
    return x * (g[:, None] if x.ndim == 2 else g)


def voice_chain(v):
    """Narration polish: rumble filter, gentle presence, smooth compression."""
    v = hp(v, 75, order=2)
    presence = bp(v, 2500, 5500) * 0.18
    warmth = bp(v, 120, 260) * 0.10
    v = v + presence + warmth
    v = compress(v, threshold_db=-26, ratio=2.6, attack=0.008, release=0.15)
    return v


def true_peak(x):
    up = resample_poly(x, 4, 1, axis=0)
    return 20 * np.log10(np.max(np.abs(up)) + 1e-12)


def limiter(x, ceiling_db=-1.2, lookahead=0.004, release=0.08):
    ceiling = 10 ** (ceiling_db / 20)
    peak = np.max(np.abs(x), axis=1) if x.ndim == 2 else np.abs(x)
    w = int(lookahead * SR)
    from scipy.ndimage import maximum_filter1d
    pk = maximum_filter1d(peak, size=2 * w + 1)
    g = np.minimum(1.0, ceiling / np.maximum(pk, 1e-9))
    # smooth gain (fast attack via lookahead window, slow release)
    r = math.exp(-1 / (release * SR))
    dec = 16
    gs = g[::dec]
    out = np.empty_like(gs)
    prev = 1.0
    rd = r ** dec
    for i, v in enumerate(gs):
        prev = v if v < prev else rd * prev + (1 - rd) * v
        out[i] = prev
    g2 = np.interp(np.arange(len(g)), np.arange(len(gs)) * dec, out)
    g2 = np.minimum(g2, g)
    return x * (g2[:, None] if x.ndim == 2 else g2)


def loudness(x):
    import pyloudnorm as pyln
    meter = pyln.Meter(SR)
    return meter.integrated_loudness(x)


def master(x, target_lufs=-14.0, ceiling_db=-1.2):
    for _ in range(3):
        lufs = loudness(x)
        x = x * 10 ** ((target_lufs - lufs) / 20)
        x = limiter(x, ceiling_db)
    return x, loudness(x), true_peak(x)


# --------------------------------------------------------------------------- EP002 additions

def sfx_shutter(seed=21):
    """Camera-shutter-like double click (blink)."""
    rng = np.random.default_rng(seed)
    out = np.zeros(int(0.16 * SR))
    for k, (t0, f) in enumerate(((0.0, 3200), (0.075, 2200))):
        n = int(0.05 * SR)
        x = bp(rng.normal(0, 1, n), f * 0.6, min(f * 2.2, 20000)) * env_exp(n, 0.008, 0.0005)
        i0 = int(t0 * SR)
        out[i0:i0 + n] += x * (0.8 if k == 0 else 0.6)
    return out * 0.6


def sfx_zip(dur=0.11, f0=900, f1=3800, seed=23):
    """A tiny fast swish for one eye jump."""
    n = int(dur * SR)
    rng = np.random.default_rng(seed)
    x = sweep_filter(rng.normal(0, 1, n), f0, f1, "bandpass", q=2.5, block=128)
    env = np.sin(np.linspace(0, np.pi, n)) ** 1.5
    return x * env * 0.5


def sfx_snip(seed=25):
    """Scissors: two bright metallic snips."""
    out = np.zeros(int(0.35 * SR))
    for k, t0 in enumerate((0.0, 0.14)):
        n = int(0.09 * SR)
        tt = np.arange(n) / SR
        rng = np.random.default_rng(seed + k)
        x = (bp(rng.normal(0, 1, n), 3500, 9000) * env_exp(n, 0.012, 0.0005) * 0.8
             + np.sin(2 * np.pi * 5200 * tt) * env_exp(n, 0.02, 0.0005) * 0.3)
        i0 = int(t0 * SR)
        out[i0:i0 + n] += x
    return out * 0.6


def reverse(x):
    return x[::-1].copy()


def stutter(buf, t0, slice_s=0.07, repeats=4, sr=SR):
    """Repeat a short slice of a stereo buffer in place (a deliberate 'edit' glitch)."""
    i0, n = int(t0 * sr), int(slice_s * sr)
    sl = buf[i0:i0 + n].copy()
    fade = np.linspace(0, 1, min(64, n))[:, None]
    sl[:len(fade)] *= fade
    sl[-len(fade):] *= fade[::-1]
    for k in range(repeats):
        j = i0 + k * n
        buf[j:j + n] = sl * (1 - 0.12 * k)
    return buf


def dip(buf, t0, dur, depth_db=-12.0, sr=SR):
    """Momentary duck (blink darkness)."""
    i0, n = int(t0 * sr), int(dur * sr)
    if i0 >= len(buf):
        return buf
    n = min(n, len(buf) - i0)
    g = 10 ** (depth_db / 20)
    env = 1 - (1 - g) * np.sin(np.linspace(0, np.pi, n))
    buf[i0:i0 + n] *= env[:, None]
    return buf
