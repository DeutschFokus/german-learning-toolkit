"""EP004 sound design: wind above, stone and heat below.

Musical idea: the score itself goes down. Every scene's chord sits lower than
the last (D minor at the surface, B-flat at the rig, G minor in the dive,
E-flat in the heat), the music drops out at the bottom of the hole, opens up
into F major for "deeper than the deepest ocean", deflates back to D minor on
"0.2 %", lifts to C for Voyager and ends on A7sus4, so the loop back to the
opening D minor lands as a cadence.

Concrete sounds tell the story: Arctic wind at the surface, a diesel drive
and the bit grinding, a sonar ping for every kilometre crossed, cracking rock
and dripping water, a heat roar, groaning walls, an impact at 12,262 m, a
metal clank for the cap, telemetry beeps for Voyager. All cues come from the
timeline (scratch read now, the creator's own read later).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
sys.path.insert(0, str(HERE))

from engine import audio as A  # noqa: E402
from engine.timeline import Timeline  # noqa: E402

SR = A.SR


def cues(T: Timeline):
    import episode
    ep = episode.Episode.__new__(episode.Episode)
    ep.T = T
    ep.duration = T.duration
    st = T.scene_starts()
    ep.scenes = [(sid, s0, st[i + 1][1] if i + 1 < len(st) else T.duration) for i, (sid, s0) in enumerate(st)]
    c = ep._cues()
    c["sc"] = dict(st)
    c["t_bottom"] = c["meters"] + 0.25
    return c


# --------------------------------------------------------------------------- bespoke sounds

def wind(dur, seed=61, level=1.0, lo=420, hi=1300):
    n = int(dur * SR)
    rng = np.random.default_rng(seed)
    t = np.arange(n) / SR
    out = np.zeros((n, 2))
    for ch in range(2):
        x = A.sweep_filter(rng.normal(0, 1, n), lo, hi, "bandpass", q=0.9, block=4096, curve="lin")
        gust = 0.55 + 0.45 * np.sin(2 * np.pi * t / 7.5 + ch * 1.7) * np.sin(2 * np.pi * t / 12.0 + 0.4)
        out[:, ch] = x * gust
    return out * 0.5 * level


def engine_hum(dur, f=46.0, seed=3):
    """Diesel drive: a low saw with a slow wobble, filtered."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    wob = 1 + 0.01 * np.sin(2 * np.pi * 0.7 * t)
    x = A.saw(f, n) * 0.6 + np.sin(2 * np.pi * f * 0.5 * t) * 0.5
    x = A.lp(x * wob, 380, order=2)
    rng = np.random.default_rng(seed)
    x += A.bp(rng.normal(0, 1, n), 120, 600) * 0.08
    return x * A.env_adsr(n, 0.6, 0.3, 0.9, 0.8, 0.9)


def grind(dur, seed=4, rate=6.0):
    """The bit chewing rock: band-passed noise pulsing with the rotation."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    x = A.bp(rng.normal(0, 1, n), 180, 2400) * (0.55 + 0.45 * np.sin(2 * np.pi * rate * t) ** 2)
    x += A.lp(rng.normal(0, 1, n), 140, order=4) * 1.4
    return x * A.env_adsr(n, 0.2, 0.2, 0.85, 0.5, 0.85) * 0.5


def drip(freq=1400.0, seed=0):
    """A water drop: short sine with a fast upward glide (the 'bloop')."""
    n = int(0.16 * SR)
    t = np.arange(n) / SR
    f = freq * (0.55 + 0.45 * (1 - np.exp(-t / 0.02)) * 1.6)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * A.env_exp(n, 0.035, 0.001) * 0.5


def crackle(dur, seed=7, density=55.0, lo=900, hi=5000):
    n = int(dur * SR)
    rng = np.random.default_rng(seed)
    out = np.zeros(n)
    k = int(dur * density)
    for _ in range(k):
        i = int(rng.uniform(0, n - 900))
        L_ = int(rng.uniform(80, 700))
        burst = rng.normal(0, 1, L_) * np.exp(-np.arange(L_) / (L_ * 0.25)) * rng.uniform(0.3, 1.0)
        out[i:i + L_] += burst
    return A.bp(out, lo, hi) * 0.6


def roar(dur, seed=9):
    """Heat: low broadband roar that opens up."""
    n = int(dur * SR)
    rng = np.random.default_rng(seed)
    x = A.sweep_filter(rng.normal(0, 1, n), 200, 1400, "lowpass", q=0.7, block=4096, curve="lin")
    return x * A.env_adsr(n, dur * 0.35, 0.3, 0.8, dur * 0.35, 0.8) * 0.6


def groan(dur, f0=62.0, seed=10):
    """Stone under stress: a slow, bending low tone plus grit."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    f = f0 * (1 + 0.08 * np.sin(2 * np.pi * 0.6 * t) + 0.05 * np.sin(2 * np.pi * 1.7 * t + 1))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.4 * np.sin(2 * np.pi * np.cumsum(f * 2.01) / SR)
    x += A.bp(rng.normal(0, 1, n), 200, 900) * (0.3 + 0.3 * np.sin(2 * np.pi * 3.1 * t) ** 2)
    return x * A.env_adsr(n, 0.4, 0.3, 0.8, 0.6, 0.8) * 0.45


def wind_down(dur=1.6, f0=46.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 * (1 - 0.6 * (t / dur) ** 1.4)
    x = A.lp(np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.4 + np.sin(2 * np.pi * np.cumsum(f) / SR), 300)
    return x * (1 - t / dur) ** 1.5 * 0.5


def clank(seed=12):
    """Heavy steel cap: a short inharmonic metallic hit."""
    n = int(1.8 * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for k, (fr, d) in enumerate(((180, 0.9), (412, 0.6), (731, 0.4), (1187, 0.25), (1630, 0.18))):
        out += np.sin(2 * np.pi * fr * t + k) * np.exp(-t / d) / (k + 1)
    rng = np.random.default_rng(seed)
    out += A.bp(rng.normal(0, 1, n), 800, 5000) * np.exp(-t / 0.02) * 0.6
    return out * 0.5


def telemetry(seed=13):
    """Voyager-style radio blips."""
    pattern = [(0.00, 1760), (0.12, 1760), (0.30, 2350), (0.62, 1760), (0.74, 2640), (0.86, 2350)]
    out = np.zeros(int(1.2 * SR))
    for dt, f in pattern:
        b = A.sfx_blip(f, 0.07)
        i0 = int(dt * SR)
        out[i0:i0 + len(b)] += b
    return out


# --------------------------------------------------------------------------- music

def build_music(T: Timeline, dur: float):
    c = cues(T)
    sc = c["sc"]
    m = A.Track(dur)
    ir = A.make_ir(4.5, damp=3800, seed=63)
    # (start, chord, cutoff, gain, attack)
    plan = [
        (0.0, ["D2", "A2", "F3", "E4"], 900, 0.45, 0.05),
        (sc["rig"] - 0.3, ["Bb1", "F2", "D3", "A3"], 1000, 0.48, 0.8),
        (c["dive"] - 0.2, ["G1", "D2", "Bb2", "A3"], 1100, 0.50, 0.4),
        (c["L07"] - 0.2, ["Eb1", "Bb1", "G2", "D3", "A3"], 1300, 0.55, 0.3),
        (c["L10"] - 0.1, ["F2", "C3", "A3", "E4"], 1700, 0.52, 0.6),
        (c["pct"] - 0.05, ["D2", "A2", "F3", "E4"], 1200, 0.50, 0.15),
        (sc["cap"] - 0.2, ["Bb1", "F2", "D3", "C4"], 1000, 0.48, 0.8),
        (c["L13"] - 0.2, ["C2", "G2", "E3", "D4"], 1600, 0.52, 0.8),
        (c["L14"] - 0.15, ["A1", "E2", "G2", "D3", "E4"], 1200, 0.52, 0.6),
    ]
    silent = (c["L09"] - 0.1, c["L10"] - 0.1)            # the bottom of the hole: music drops out
    for i, (t0, notes, cut, g, att) in enumerate(plan):
        t1 = plan[i + 1][0] if i + 1 < len(plan) else dur
        if t0 < silent[0] < t1:
            t1 = silent[0] + 0.4
        x = A.pad_chord(notes, (t1 - t0) + 2.2, cutoff=cut, attack=att, release=2.0, seed=70 + i)
        m.add(t0, x, gain=g)
    # sub drone in D, out at the bottom of the hole, back for the ocean
    dr = A.stereo(A.drone(A.note_hz("D1") * 2, dur + 1.0, lfo=0.05))
    k0, k1 = int(silent[0] * SR), int(silent[1] * SR)
    fade = np.ones(len(dr))
    fade[k0:k1] = 0.15
    fade = np.convolve(fade, np.ones(4800) / 4800, mode="same")
    m.add(0.0, dr * fade[:, None], gain=0.16)
    # the descent motif: four falling notes, a register lower each time
    for t0, octv in ((sc["rig"] + 0.2, 5), (c["dive"] + 0.1, 4), (c["L07"], 3)):
        for j, nm in enumerate(("A", "F", "D", "A")):
            o = octv if j < 3 else octv - 1
            m.add(t0 + j * 0.28, A.pluck(A.note_hz(f"{nm}{o}"), 2.2, bright=0.4, decay=0.7), gain=0.22,
                  pan=-0.2 + 0.13 * j)
    # wonder: a slow rising line over the ocean / globe
    for j, nm in enumerate(("C5", "E5", "G5", "A5")):
        m.add(c["L10"] + 0.3 + j * 0.55, A.pluck(A.note_hz(nm), 2.6, bright=0.3, decay=0.9), gain=0.18, pan=0.2)
    # Voyager: high, open
    for j, nm in enumerate(("G5", "D6", "E6", "G6")):
        m.add(c["interstellar"] - 0.3 + j * 0.45, A.pluck(A.note_hz(nm), 2.4, bright=0.25, decay=1.0), gain=0.16,
              pan=-0.3 + 0.2 * j)
    # heat: a pulse that quickens
    tt, k = c["n180"], 0
    while tt < silent[0]:
        u = (tt - c["n180"]) / max(0.1, silent[0] - c["n180"])
        m.add(tt, A.sfx_thump(52, 0.4), gain=0.28 + 0.12 * u)
        tt += 0.62 - 0.22 * u
        k += 1
    m.buf = A.reverb(m.buf, ir, wet=0.42)
    return m


# --------------------------------------------------------------------------- SFX

def build_sfx(T: Timeline, dur: float):
    c = cues(T)
    sc = c["sc"]
    s = A.Track(dur)
    ir = A.make_ir(2.4, damp=6000, seed=65)
    surf_end = c["dive"] + 1.0
    # Arctic wind: surface scenes only
    w = wind(dur + 1.0)
    env = np.ones(len(w))
    a0, a1 = int(c["dive"] * SR), int(surf_end * SR)
    b0, b1 = int((sc["cap"] - 0.3) * SR), int((sc["cap"] + 0.6) * SR)
    env[a0:a1] = np.linspace(1, 0, a1 - a0)
    env[a1:b0] = 0
    env[b0:b1] = np.linspace(0, 1, b1 - b0)
    s.add(0.0, w * env[:, None], gain=0.55)
    s.add(0.0, A.sfx_boom(2.4, 70, 28, seed=66), gain=0.40)
    # sonar pings with the cap's ripples
    for tp in (0.0, 2.5):
        s.add(tp + 0.05, A.sfx_ping(880, 1.4, 0.35), gain=0.20)
    s.add(c["n12"], A.sfx_thump(48, 0.6), gain=0.45)
    # L02: falling into the well, the plate slides in and settles
    s.add(c["L01end"] - 0.25, A.sfx_whoosh(0.8, 3000, 300, seed=67), gain=0.30)
    s.add(c["dinner"] - 0.1, A.sfx_whoosh(0.45, 1200, 4000, seed=68, peak=0.6), gain=0.30, pan=0.5)
    s.add(c["plate"] + 0.2, A.sfx_chime(("E7", "B7"), 0.03, 0.6), gain=0.20)
    s.add(c["plate"] + 0.2, A.sfx_tick(3200, 0.08, seed=69), gain=0.35)
    # rig: transition, 1970, the drive starts, the bit bites
    s.add(sc["rig"] - 0.3, A.sfx_whoosh(0.7, 300, 3200, seed=70), gain=0.22)
    s.add(c["y1970"] - 0.05, A.sfx_thump(64, 0.5), gain=0.5)
    s.add(c["y1970"] - 0.05, A.sfx_chime(("A5", "E6"), 0.06, 1.4), gain=0.18)
    s.add(c["started"] - 0.2, A.stereo(engine_hum(c["dive"] + 0.8 - c["started"]), 0.0, 0.4), gain=0.42)
    s.add(c["drilling"] - 0.1, A.stereo(grind(c["dive"] + 0.6 - c["drilling"]), 0.0, 0.4), gain=0.32)
    s.add(c["n15"], A.sfx_blip(1760, 0.08), gain=0.30)
    s.add(c["n15"] + 0.1, A.sfx_blip(2350, 0.08), gain=0.25)

    # dives: a whoosh down, rumble, and a ping for every kilometre crossed
    def dive(t0, t1, km0, km1, big=True):
        s.add(t0 - 0.1, A.sfx_whoosh(t1 - t0 + 0.4, 4200, 220, seed=int(t0 * 10)), gain=0.38 if big else 0.25)
        s.add(t0, A.sfx_rumble(t1 - t0 + 1.2, seed=int(t1 * 10)), gain=0.55 if big else 0.35)
        ks = range(int(math.floor(km0)) + 1, int(math.floor(km1)) + 1)
        for km in ks:
            u = (km - km0) / max(1e-6, km1 - km0)
            # depth(t) is an ease-in-out; invert approximately
            tt = t0 + (t1 - t0) * (0.5 - math.cos(math.pi * u) * 0.5) ** 0.85
            s.add(tt, A.sfx_ping(1500 - 70 * km, 0.6, 0.12), gain=0.20, pan=-0.3 + 0.05 * km)
        s.add(t1 - 0.05, A.sfx_thump(46, 0.6), gain=0.55 if big else 0.4)

    dive(c["dive"], c["km6"] + 0.2, 0.25, 6.0)
    dive(c["L04end"] + 0.2, c["seven"] + 0.35, 6.12, 7.05, big=False)
    dive(c["L06"], c["cracked"] + 0.4, 7.12, 8.30, big=False)
    dive(c["L07"] - 0.1, c["n180"] + 0.2, 8.42, 11.70)
    s.add(c["dive"], A.stereo(A.sfx_counter(c["km6"] + 0.2 - c["dive"], 22.0, 2100), -0.3), gain=0.10)
    # a low bed of grinding under the whole descent
    s.add(c["km6"], A.stereo(grind(c["t_bottom"] - c["km6"] + 0.4, seed=14, rate=4.0), 0.0, 0.5), gain=0.12)
    # fossils
    s.add(c["fossils"] - 0.05, A.stereo(A.sfx_shimmer(2.4, "E6"), 0.3, 0.5), gain=0.40)
    s.add(c["fossils"] + 0.1, A.sfx_chime(("B5", "E6"), 0.07, 1.4), gain=0.20, pan=0.4)
    # predicted basalt: a scan, then the glitch and the stamp
    for j in range(4):
        s.add(c["predicted"] - 0.2 + j * 0.12, A.sfx_blip(1300 + 160 * j, 0.05), gain=0.18, pan=0.3)
    s.add(c["wasnt"] - 0.05, A.sfx_buzz(0.35, 92.0), gain=0.25)
    for j in range(6):
        s.add(c["wasnt"] + j * 0.05, A.sfx_tick(900 + 400 * (j % 3), 0.04, seed=j), gain=0.22, pan=-0.5 + 0.2 * j)
    s.add(c["there"] - 0.05, A.sfx_thump(80, 0.4), gain=0.5)
    s.add(c["there"] - 0.05, A.sfx_tick(600, 0.15, seed=21), gain=0.45)
    # cracked rock, water
    s.add(c["cracked"] - 0.15, crackle(1.4, seed=22), gain=0.45, pan=-0.2)
    s.add(c["cracked"] - 0.1, A.sfx_whoosh(0.9, 800, 3000, seed=23, peak=0.3), gain=0.18)
    rng = np.random.default_rng(24)
    tt = c["soaked"] - 0.1
    while tt < c["L07"] - 0.3:
        s.add(tt, drip(rng.uniform(900, 1900)), gain=rng.uniform(0.12, 0.25), pan=rng.uniform(-0.6, 0.6))
        tt += rng.uniform(0.14, 0.42)
    n = int((c["L07"] - c["soaked"]) * SR)
    trickle = A.bp(np.random.default_rng(25).normal(0, 1, n), 1800, 6000) * A.env_adsr(n, 0.4, 0.2, 0.8, 0.6, 0.8)
    s.add(c["soaked"], A.stereo(trickle * 0.25, 0.0, 0.6), gain=0.4)
    # heat
    s.add(c["L07"] + 0.1, A.stereo(roar(c["L09end"] - c["L07"] + 0.5), 0.0, 0.6), gain=0.36)
    s.add(c["n180"] - 0.1, crackle(4.0, seed=26, density=26, lo=1500, hi=7000), gain=0.35, pan=0.25)
    s.add(c["twice"] - 0.05, A.sfx_zip(0.15, 900, 3800, seed=27), gain=0.35)
    s.add(c["twice"] + 0.15, A.sfx_thump(70, 0.4), gain=0.4)
    # soft rock, squeezing walls
    s.add(c["soft"] - 0.2, groan(2.6, 58, seed=28), gain=0.38, pan=-0.2)
    s.add(c["hole8"] - 0.1, groan(2.2, 44, seed=29), gain=0.40, pan=0.25)
    s.add(c["squeezing"], A.sfx_rumble(2.0, seed=30), gain=0.30)
    # the bottom: final approach, impact, the drive winds down, silence
    tb = c["t_bottom"]
    s.add(c["L09"] - 0.05, A.sfx_whoosh(tb - c["L09"] + 0.2, 2600, 160, seed=31), gain=0.30)
    s.add(c["L09"], A.stereo(A.sfx_counter(tb - c["L09"], 18.0, 1700), 0.2), gain=0.10)
    s.add(tb - 0.02, A.sfx_boom(2.8, 85, 26, seed=32), gain=0.62)
    s.add(tb - 0.02, clank(seed=33), gain=0.22)
    s.add(tb - 0.02, A.sfx_rumble(2.4, seed=34), gain=0.32)
    s.add(c["further"] - 0.4, wind_down(1.8), gain=0.5)
    # scale: pull back, the ocean pours in, then the whole Earth
    s.add(sc["scale"] - 0.1, A.sfx_reverse_swell(1.0), gain=0.30)
    s.add(sc["scale"] + 0.1, A.sfx_whoosh(1.1, 300, 2600, seed=35), gain=0.28)
    n = int(1.4 * SR)
    pour = A.sweep_filter(np.random.default_rng(36).normal(0, 1, n), 2400, 500, "lowpass", q=0.8, block=2048,
                          curve="lin") * A.env_adsr(n, 0.25, 0.2, 0.8, 0.6, 0.8)
    s.add(c["deepest10"] - 0.1, A.stereo(pour * 0.5, -0.3, 0.5), gain=0.45)
    s.add(c["ocean"] + 0.4, A.sfx_chime(("C6", "G6"), 0.08, 1.6), gain=0.22)
    s.add(c["L11"] - 0.05, A.sfx_whoosh(1.8, 200, 1800, seed=37, peak=0.7), gain=0.35)
    s.add(c["pct"] - 0.05, A.sfx_boom(3.0, 60, 22, seed=38), gain=0.55)
    s.add(c["pct"] + 0.2, A.stereo(A.sfx_shimmer(3.0, "A5", seed=39), 0.0, 0.6), gain=0.35)
    s.add(c["center"], A.sfx_chime(("D6", "A6"), 0.09, 1.6), gain=0.20)
    # dive through the marker: whoosh into the surface, wind returns, the cap
    s.add(sc["cap"] - 0.45, A.sfx_whoosh(0.9, 400, 5000, seed=40, peak=0.75), gain=0.35)
    s.add(sc["cap"] + 0.1, A.sfx_thump(52, 0.5), gain=0.35)
    s.add(c["sealed"] - 0.05, clank(seed=41), gain=0.45)
    s.add(c["rusty"] - 0.1, A.sfx_whoosh(0.5, 2000, 5200, seed=42, peak=0.5), gain=0.12, pan=0.3)
    # outro: tilt up to Voyager, telemetry, tilt down, home
    s.add(c["L13"] - 0.1, A.sfx_whoosh(1.6, 250, 3800, seed=43), gain=0.28)
    s.add(c["interstellar"] - 0.05, A.stereo(A.sfx_shimmer(2.6, "D6", seed=44), 0.2, 0.6), gain=0.30)
    s.add(c["interstellar"] + 0.25, telemetry(), gain=0.22, pan=0.35)
    s.add(c["L14"] - 0.1, A.sfx_whoosh(1.5, 3600, 260, seed=45), gain=0.28)
    s.add(c["deeper14"] + 0.3, A.sfx_thump(46, 0.6), gain=0.35)
    # into the loop
    s.add(c["own"] - 0.3, A.sfx_riser(dur - c["own"] + 0.35, 160, 1200, seed=46), gain=0.24)
    s.add(dur - 0.85, A.sfx_reverse_swell(0.87), gain=0.30)
    for tp in (dur - 2.5 + 0.05,):
        s.add(tp, A.sfx_ping(880, 1.4, 0.35), gain=0.16)
    s.buf = A.reverb(s.buf, ir, wet=0.18)
    return s


def build_mix(timeline_path: Path, voice_wav: Path, out_dir: Path, tag: str):
    """Mix against a voice (scratch or the creator's). With tag='scratch' only the
    bed is meant for delivery; the scratch voice just sets ducking and levels."""
    T = Timeline(timeline_path)
    dur = T.duration
    n = int(round(dur * SR))
    music = build_music(T, dur).wrapped()
    sfx = build_sfx(T, dur).wrapped()
    v, vsr = sf.read(voice_wav, dtype="float64", always_2d=False)
    if v.ndim > 1:
        v = v.mean(axis=1)
    if vsr != SR:
        g = math.gcd(SR, vsr)
        v = resample_poly(v, SR // g, vsr // g)
    v = A.voice_chain(v)
    v = v[:n] if len(v) >= n else np.pad(v, (0, n - len(v)))
    voice = np.stack([v, v], axis=1)
    voice *= 10 ** ((-17.0 - A.loudness(voice)) / 20)
    music *= 10 ** ((-27.0 - A.loudness(music)) / 20)
    sfx *= 10 ** ((-24.5 - A.loudness(sfx)) / 20)
    music_d = A.duck(music, voice, depth_db=-8.0, threshold=0.02)
    sfx_d = A.duck(sfx, voice, depth_db=-5.0, threshold=0.02)
    mix = voice + music_d + sfx_d
    mastered, lufs, tp = A.master(mix, -14.0, -2.0)
    gain = mastered.std() / max(mix.std(), 1e-12)
    bed = A.limiter((music_d + sfx_d) * gain, -2.0)
    out_dir.mkdir(parents=True, exist_ok=True)
    sf.write(out_dir / f"mix_{tag}.wav", mastered.astype(np.float32), SR, subtype="PCM_24")
    sf.write(out_dir / f"bed_{tag}.wav", bed.astype(np.float32), SR, subtype="PCM_24")
    stems = out_dir / "stems"
    stems.mkdir(exist_ok=True)
    sf.write(stems / f"music_unducked_{tag}.flac", (music * gain).astype(np.float32), SR, subtype="PCM_24")
    sf.write(stems / f"sfx_{tag}.flac", (sfx * gain).astype(np.float32), SR, subtype="PCM_24")
    if tag != "scratch":
        sf.write(stems / f"voice_{tag}_processed.flac", (voice[:, 0] * gain).astype(np.float32), SR,
                 subtype="PCM_24")
    report = {"integrated_lufs": round(float(lufs), 2), "true_peak_dbtp": round(float(tp), 2),
              "bed_lufs": round(float(A.loudness(bed)), 2), "master_gain_db": round(float(20 * np.log10(gain)), 2)}
    (out_dir / f"mix_{tag}_report.json").write_text(json.dumps(report, indent=1))
    print(f"[mix:{tag}] {report}")
    return report


if __name__ == "__main__":
    tl = Path(sys.argv[1])
    build_mix(tl, Path(sys.argv[2]), tl.parent, sys.argv[3] if len(sys.argv) > 3 else "scratch")
