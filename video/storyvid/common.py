"""Shared constants and small DSP helpers."""
import numpy as np
import scipy.io.wavfile as wavfile
from scipy import signal

SR = 48000          # audio sample rate
FPS = 30            # video frame rate
W, H = 1080, 1920   # output size (9:16)


def read_wav(path, mono=True):
    sr, x = wavfile.read(path)
    if x.dtype == np.int16:
        x = x.astype(np.float32) / 32768.0
    elif x.dtype == np.int32:
        x = x.astype(np.float32) / 2147483648.0
    else:
        x = x.astype(np.float32)
    if sr != SR:
        g = np.gcd(sr, SR)
        x = signal.resample_poly(x, SR // g, sr // g, axis=0).astype(np.float32)
    if mono and x.ndim == 2:
        x = x.mean(axis=1)
    return x


def write_wav(path, x):
    wavfile.write(path, SR, np.asarray(x, dtype=np.float32))


def db(v):
    return 10 ** (v / 20.0)


def butter(x, kind, freq, order=4):
    sos = signal.butter(order, freq, btype=kind, fs=SR, output="sos")
    return signal.sosfilt(sos, x, axis=0).astype(np.float32)


def peaking(x, f0, gain_db, q=1.0):
    """RBJ peaking EQ."""
    a = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * f0 / SR
    alpha = np.sin(w0) / (2 * q)
    b = [1 + alpha * a, -2 * np.cos(w0), 1 - alpha * a]
    aa = [1 + alpha / a, -2 * np.cos(w0), 1 - alpha / a]
    return signal.lfilter(b, aa, x, axis=0).astype(np.float32)


def shelf(x, f0, gain_db, high=True):
    """RBJ shelving EQ (slope 1)."""
    a = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * f0 / SR
    alpha = np.sin(w0) / 2 * np.sqrt(2)
    cw = np.cos(w0)
    sa = 2 * np.sqrt(a) * alpha
    if high:
        b = [a * ((a + 1) + (a - 1) * cw + sa), -2 * a * ((a - 1) + (a + 1) * cw), a * ((a + 1) + (a - 1) * cw - sa)]
        aa = [(a + 1) - (a - 1) * cw + sa, 2 * ((a - 1) - (a + 1) * cw), (a + 1) - (a - 1) * cw - sa]
    else:
        b = [a * ((a + 1) - (a - 1) * cw + sa), 2 * a * ((a - 1) - (a + 1) * cw), a * ((a + 1) - (a - 1) * cw - sa)]
        aa = [(a + 1) + (a - 1) * cw + sa, -2 * ((a - 1) + (a + 1) * cw), (a + 1) + (a - 1) * cw - sa]
    return signal.lfilter(b, aa, x, axis=0).astype(np.float32)


def make_ir(seconds=2.5, decay=2.2, predelay=0.02, lp=6000, stereo=True, seed=1, early=True):
    """Synthetic reverb impulse response: filtered noise with exponential decay."""
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    chans = []
    for c in range(2 if stereo else 1):
        noise = rng.standard_normal(n).astype(np.float32)
        env = np.exp(-6.9 * t / decay)          # -60 dB at `decay` seconds
        ir = noise * env
        # darker tail: progressively low-passed copy blended in
        dark = butter(ir, "low", 1800)
        mix = np.clip(t / (decay * 0.6), 0, 1)
        ir = ir * (1 - mix) + dark * mix
        ir = butter(ir, "low", lp, 2)
        ir = butter(ir, "high", 120, 2)
        if early:
            for k in range(8):
                pos = int((0.004 + rng.random() * 0.05) * SR)
                ir[pos] += (0.6 - 0.06 * k) * (1 if rng.random() > 0.5 else -1)
        pad = np.zeros(int(predelay * SR), np.float32)
        chans.append(np.concatenate([pad, ir]))
    ir = np.stack(chans, axis=1)
    return ir / np.sqrt((ir ** 2).sum(axis=0, keepdims=True))


def convolve_reverb(x, ir, wet=0.3, dry=1.0):
    """x mono or stereo -> stereo with reverb."""
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    out = np.zeros((len(x) + len(ir) - 1, 2), np.float32)
    for c in range(2):
        out[:, c] = signal.fftconvolve(x[:, c], ir[:, c], mode="full")
    out *= wet
    out[: len(x)] += dry * x
    return out


def to_stereo(x):
    return np.stack([x, x], axis=1) if x.ndim == 1 else x


def place(buf, x, t, gain=1.0):
    """Add stereo clip x into stereo buffer buf at time t (seconds)."""
    x = to_stereo(x) * gain
    i = int(round(t * SR))
    if i < 0:
        x = x[-i:]
        i = 0
    j = min(len(buf), i + len(x))
    if j > i:
        buf[i:j] += x[: j - i]


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0 + 1e-9), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def ease(t, kind="inout"):
    t = float(np.clip(t, 0.0, 1.0))
    if kind == "linear":
        return t
    if kind == "in":
        return t * t * t
    if kind == "out":
        return 1 - (1 - t) ** 3
    if kind == "sine":
        return 0.5 - 0.5 * np.cos(np.pi * t)
    # gentle cubic in-out
    return 4 * t * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2
