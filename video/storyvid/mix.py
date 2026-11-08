"""Voice processing, music stem processing, ducking and mastering."""
import os

import numpy as np
import pyloudnorm as pyln
from scipy import signal

from . import music as musicmod
from . import sfx
from .common import SR, butter, convolve_reverb, db, make_ir, peaking, place, read_wav, shelf, write_wav


def _rms(x):
    return float(np.sqrt(np.mean(x ** 2) + 1e-12))


def _compress(x, thresh_db=-20, ratio=2.5, attack=0.005, release=0.12):
    """Simple feed-forward RMS compressor (mono)."""
    env = np.abs(x)
    a = np.exp(-1 / (attack * SR))
    r = np.exp(-1 / (release * SR))
    # one-pole with separate attack/release, vectorised via lfilter on a decimated signal
    dec = 32
    e = env[: len(env) // dec * dec].reshape(-1, dec).max(axis=1)
    out = np.zeros_like(e)
    prev = 0.0
    aa, rr = a ** dec, r ** dec
    for i, v in enumerate(e):
        prev = aa * prev + (1 - aa) * v if v > prev else rr * prev + (1 - rr) * v
        out[i] = prev
    env = np.repeat(out, dec)
    env = np.concatenate([env, np.full(len(x) - len(env), env[-1] if len(env) else 0)])
    lvl = 20 * np.log10(env + 1e-9)
    gr = np.where(lvl > thresh_db, (lvl - thresh_db) * (1 - 1 / ratio), 0.0)
    return (x * 10 ** (-gr / 20)).astype(np.float32)


def process_voice(x, kind):
    x = butter(x, "high", 75, 2)
    if kind == "phone":
        y = sfx.phone_filter(x, 1.8)
        y = _compress(y, -18, 3.0)
        return np.stack([y, y], axis=1) * 0.9
    x = shelf(x, 160, 1.0, high=False)
    x = peaking(x, 3200, 1.5, 1.0)
    x = shelf(x, 9000, -1.0, high=True)
    x = _compress(x, -22, 2.2)
    if kind == "room":       # Lorenz, alone in the archive hall
        ir = make_ir(2.4, 1.9, 0.025, 5000, seed=5)
        return convolve_reverb(x, ir, wet=0.2)[: len(x) + int(1.5 * SR)]
    ir = make_ir(0.8, 0.45, 0.008, 7000, seed=4)
    return convolve_reverb(x, ir, wet=0.055)[: len(x) + int(0.4 * SR)]


def duck_env(tl, n, depth_db, attack=0.12, release=0.6, pad=0.06):
    """1.0 when no speech; dips by depth_db while speech is active."""
    hop = 480  # 10 ms
    m = np.zeros(n // hop + 2, np.float32)
    for a, b in tl.speech_intervals():
        m[int((a - pad) * SR / hop): int((b + pad) * SR / hop) + 1] = 1.0
    out = np.zeros_like(m)
    ka = 1 - np.exp(-hop / (attack * SR))
    kr = 1 - np.exp(-hop / (release * SR))
    prev = 0.0
    for i, v in enumerate(m):
        prev += (v - prev) * (ka if v > prev else kr)
        out[i] = prev
    g = 1 - (1 - db(depth_db)) * out
    return np.interp(np.arange(n), np.arange(len(g)) * hop, g).astype(np.float32)


def limiter(x, ceiling_db=-1.0, lookahead=0.004, release=0.08):
    ceil = db(ceiling_db)
    peak = np.abs(x).max(axis=1)
    la = int(lookahead * SR)
    # sliding max over lookahead window
    from scipy.ndimage import maximum_filter1d
    pk = maximum_filter1d(peak, size=2 * la + 1)
    need = np.minimum(1.0, ceil / (pk + 1e-9))
    # smooth gain: instant attack, exponential release
    g = np.empty_like(need)
    r = np.exp(-1 / (release * SR))
    prev = 1.0
    dec = 16
    nd = need[: len(need) // dec * dec].reshape(-1, dec).min(axis=1)
    gd = np.empty_like(nd)
    rr = r ** dec
    for i, v in enumerate(nd):
        prev = v if v < prev else rr * prev + (1 - rr) * v
        gd[i] = prev
    g = np.repeat(gd, dec)
    g = np.concatenate([g, np.full(len(need) - len(g), g[-1])])
    g = np.minimum(g, need)
    return (x * g[:, None]).astype(np.float32)


def build(story, tl, work, cues, out_name="mix.wav", target_lufs=-14.0):
    n = int(tl.duration * SR)
    vo = np.zeros((n + 3 * SR, 2), np.float32)
    # voice levels: normalise each line to a common RMS, then per-voice trims
    trims = {"narrator": 0.0, "lorenz": -0.5, "brother": -1.5}
    for line in story["lines"]:
        lid = line["id"]
        kind = story["voices"][line["voice"]].get("fx", "narrator")
        x = read_wav(os.path.join(work, "tts", f"{lid}.wav"))
        x = x * (0.1 / _rms(x[np.abs(x) > 0.01] if (np.abs(x) > 0.01).any() else x))
        y = process_voice(x, kind) * db(trims.get(line["voice"], 0.0))
        place(vo, y, tl.lines[lid]["start"])
    vo = vo[:n]

    # music
    parts = cues.compose_music(tl)
    stems = musicmod.render(parts, work, tl.duration + 2)
    mfx = cues.music_fx(tl)
    hall = make_ir(4.0, 3.2, 0.03, 6500, seed=7)
    mus = np.zeros((n, 2), np.float32)
    t = np.arange(n) / SR
    muffle = np.zeros(n, np.float32)
    for a, b in mfx.get("muffle", []):
        muffle = np.maximum(muffle, np.clip((t - a) / 0.8, 0, 1) * np.clip((b - t) / 0.8, 0, 1))
    for name, x in stems.items():
        x = butter(x, "high", 45, 2)
        y = convolve_reverb(x, hall, wet=mfx["reverb"].get(name, 0.35))[: n]
        y *= db(mfx["gain_db"].get(name, 0.0))
        mus += y
    if muffle.any():
        dark = butter(mus, "low", 1400, 2)
        mus = mus * (1 - muffle[:, None]) + (dark * 1.25) * muffle[:, None]
    mus_peak = np.abs(mus).max() + 1e-9
    mus = mus / mus_peak * 0.5

    buses = cues.sound_design(tl)
    amb, fx = buses["ambience"][:n], buses["sfx"][:n]

    # levels and ducking
    lv = getattr(cues, "LEVELS", {})
    g_mus, g_amb, g_fx = db(lv.get("music", -9.5)), db(lv.get("ambience", -14.0)), db(lv.get("sfx", -4.0))
    duck_m = duck_env(tl, n, lv.get("duck_music", -9.0))
    duck_a = duck_env(tl, n, lv.get("duck_ambience", -6.0))
    duck_f = duck_env(tl, n, lv.get("duck_sfx", -5.0))
    mus_b = mus * g_mus * duck_m[:, None]
    amb_b = amb * g_amb * duck_a[:, None]
    fx_b = fx * g_fx * duck_f[:, None]
    mix = vo + mus_b + amb_b + fx_b
    mix = butter(mix, "high", 28, 2)
    # fade in/out
    fi = np.clip(t / 0.35, 0, 1)
    fo = np.clip((tl.duration - t) / 2.0, 0, 1)
    mix *= (fi * fo)[:, None]

    meter = pyln.Meter(SR)
    loud = meter.integrated_loudness(mix.astype(np.float64))
    mix *= db(target_lufs - loud)
    mix = limiter(mix, -1.7)
    loud2 = meter.integrated_loudness(mix.astype(np.float64))
    mix *= db(target_lufs - loud2)
    mix = limiter(mix, -1.5)
    final = meter.integrated_loudness(mix.astype(np.float64))
    path = os.path.join(work, out_name)
    write_wav(path, mix)
    # stems for re-editing
    sd = os.path.join(work, "stems")
    os.makedirs(sd, exist_ok=True)
    # same make-up gain as the master (the limiter only touches a few peaks)
    master_gain = db(final - loud) if np.isfinite(loud) else 1.0
    for name, bus in (("voice", vo), ("music", mus_b), ("ambience", amb_b), ("sfx", fx_b)):
        write_wav(os.path.join(sd, f"{name}.wav"), bus * (fi * fo)[:, None] * master_gain)
    return path, final, float(20 * np.log10(np.abs(mix).max() + 1e-9))
