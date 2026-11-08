"""EP007 sound design: from the bottom of the sea to the top of the world.

Musical idea: E minor / G major, wide and cold. Harmony walks Em9 -> Cmaj7 ->
(under water) a warm, muffled Gmaj9 -> Am -> a dark C/E for the collision ->
D -> Em -> (1924) a sparse piano motif B4 G4 E4 D4 over Cmaj7 -> Am7 -> D ->
Gmaj7, then Dsus4 into the loop so the opening Em9 lands as an answer.

Concrete sounds: summit wind and spindrift, bubbles and a muffled drone in
the ancient sea, a tectonic rumble and boom for the collision, a rising
whoosh with the altitude counter, film flicker for 1924, meltwater drips for
the boot, a camera shutter that never fires (a dry click, then silence).
All cues come from the timeline (scratch read now, the creator's read later).
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
MOTIF = ("B4", "G4", "E4", "D4")


def cues(T: Timeline):
    import episode
    ep = episode.Episode.__new__(episode.Episode)
    ep.T = T
    ep.duration = T.duration
    st = T.scene_starts()
    ep.scenes = [(sid, s0, st[i + 1][1] if i + 1 < len(st) else T.duration) for i, (sid, s0) in enumerate(st)]
    c = ep._cues()
    c["sc"] = dict(st)
    return c


def wind(dur, seed=1, lo=200, hi=1400):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = A.bp(np.random.default_rng(seed).normal(0, 1, n), lo, hi)
    gust = 0.55 + 0.45 * np.sin(2 * np.pi * 0.13 * t + 1.0) * np.sin(2 * np.pi * 0.07 * t)
    return x * gust * 0.18


def bubbles(dur, seed=3, rate=9.0):
    n = int(dur * SR)
    rng = np.random.default_rng(seed)
    out = np.zeros(n)
    t = 0.0
    while t < dur:
        t += rng.exponential(1.0 / rate)
        i = int(t * SR)
        f = rng.uniform(500, 1600)
        m = int(0.07 * SR)
        if i + m < n:
            tt = np.arange(m) / SR
            out[i:i + m] += np.sin(2 * np.pi * f * (1 + 6 * tt) * tt) * np.exp(-tt / 0.02) * rng.uniform(0.1, 0.35)
    return out


def drip(seed=0):
    m = int(0.25 * SR)
    tt = np.arange(m) / SR
    f = 1400 + 500 * np.random.default_rng(seed).random()
    return np.sin(2 * np.pi * f * (1 + 2.5 * tt) * tt) * np.exp(-tt / 0.03) * 0.5


def flicker(dur, seed=5):
    """Projector-like film flutter for 1924."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = A.bp(np.random.default_rng(seed).normal(0, 1, n), 1500, 5000) * 0.03
    return x * (0.6 + 0.4 * (np.sin(2 * np.pi * 18 * t) > 0))


def piano(nm, dur=2.8):
    return A.pluck(A.note_hz(nm), dur, bright=0.35, decay=1.3)


def build_music(T: Timeline, dur: float):
    c = cues(T)
    sc = c["sc"]
    m = A.Track(dur)
    ir = A.make_ir(5.0, damp=4200, seed=91)
    plan = [
        (0.0, ["E2", "B2", "G3", "D4", "F#4"], 1200, 0.45, 0.05),
        (sc["summit"] - 0.2, ["C2", "G2", "E3", "B3"], 1100, 0.45, 0.6),
        (sc["sea"] - 0.3, ["G1", "D2", "B2", "F#3", "A3"], 700, 0.52, 1.0),
        (sc["drift"] - 0.2, ["A1", "E2", "C3", "E3", "A3"], 1300, 0.48, 0.5),
        (c["slammed"] - 0.1, ["E1", "C2", "G2", "E3"], 900, 0.55, 0.05),
        (sc["rise"] - 0.2, ["D2", "A2", "F#3", "A3", "E4"], 1600, 0.50, 0.6),
        (sc["grow"] - 0.2, ["E2", "B2", "G3", "B3", "D4"], 1400, 0.46, 0.6),
        (sc["climbers"] - 0.2, ["C2", "G2", "E3", "B3"], 1000, 0.40, 1.0),
        (sc["boot"] - 0.2, ["A1", "E2", "C3", "G3"], 900, 0.40, 1.0),
        (c["y2024"] - 0.2, ["D2", "A2", "F#3", "C4"], 1000, 0.40, 0.8),
        (sc["camera"] - 0.2, ["G1", "D2", "B2", "F#3"], 1100, 0.42, 0.8),
        (sc["outro"] - 0.2, ["D2", "A2", "D3", "G3", "A3"], 1300, 0.46, 0.6),
    ]
    for i, (t0, notes, cut, g, att) in enumerate(plan):
        t1 = plan[i + 1][0] if i + 1 < len(plan) else dur
        m.add(t0, A.pad_chord(notes, (t1 - t0) + 2.2, cutoff=cut, attack=att, release=2.0, seed=90 + i), gain=g)
    m.add(0.0, A.stereo(A.drone(A.note_hz("E1") * 2, dur + 1.0, lfo=0.05)), gain=0.13)
    # the 1924 motif, then again (softer, higher) into the loop
    for j, nm in enumerate(MOTIF):
        m.add(c["y1924"] + j * 0.55, piano(nm), gain=0.22, pan=-0.2 + 0.12 * j)
    for j, nm in enumerate(MOTIF):
        m.add(c["camera"] + j * 0.7, piano(nm, 3.2), gain=0.16, pan=0.15 - 0.1 * j)
    for j, nm in enumerate(("B5", "G5", "E5")):
        m.add(c["seashells11"] + j * 0.45, piano(nm, 3.0), gain=0.16, pan=0.2)
    m.buf = A.reverb(m.buf, ir, wet=0.46)
    m.buf = A.dip(m.buf, c["never"] - 0.1, 1.5, depth_db=-8)
    return m


def build_sfx(T: Timeline, dur: float):
    c = cues(T)
    sc = c["sc"]
    s = A.Track(dur)
    ir = A.make_ir(2.8, damp=6000, seed=93)
    s.add(0.0, A.stereo(wind(dur + 1.0, seed=2), 0.0, 0.7), gain=0.30)
    s.add(0.0, A.sfx_boom(2.0, 60, 26, seed=94), gain=0.25)
    s.add(c["seashells"] - 0.05, A.sfx_chime(("E6", "B6"), 0.09, 2.0), gain=0.20)
    # fossils: three soft taps on stone as the rings appear
    for k in range(3):
        s.add(c["fossil"] + 0.32 * k, A.sfx_tick(1800 + 300 * k, 0.08, seed=95 + k), gain=0.25)
    # into the sea
    s.add(sc["sea"] - 0.5, A.sfx_whoosh(1.2, 2500, 300, seed=98, peak=0.6), gain=0.25)
    s.add(sc["sea"] - 0.1, A.stereo(bubbles(sc["drift"] - sc["sea"] + 0.4, seed=99), 0.0, 0.7), gain=0.45)
    s.add(c["n450"] - 0.3, A.sfx_counter(1.1, 24, 1800), gain=0.16)
    # India races north
    s.add(sc["drift"] - 0.2, A.sfx_whoosh(0.8, 400, 2400, seed=100), gain=0.2)
    s.add(c["india"], A.sfx_riser(c["slammed"] - c["india"], 120, 900, seed=101), gain=0.16)
    s.add(c["four"] - 0.05, A.sfx_blip(1500, 0.06), gain=0.15)
    s.add(c["fingernails"] - 0.05, A.sfx_blip(1100, 0.06), gain=0.15)
    # the collision
    s.add(c["slammed"] - 0.04, A.sfx_boom(3.2, 70, 22, seed=102), gain=0.42)
    s.add(c["slammed"] - 0.04, A.sfx_rumble(3.5, seed=103), gain=0.30)
    # folding and rising
    s.add(c["crumpled"] - 0.1, A.sfx_rumble(1.8, seed=104), gain=0.18)
    s.add(c["rose"] - 0.2, A.sfx_whoosh(c["kilometers"] - c["rose"] + 0.9, 250, 3200, seed=105, peak=0.7), gain=0.22)
    s.add(c["kilometers"] + 0.5, A.sfx_chime(("E6", "G6", "B6"), 0.08, 2.0), gain=0.20)
    # still rising: tiny ticks
    for k in range(4):
        s.add(c["two"] + 0.25 * k, A.sfx_tick(3000, 0.05, seed=106 + k), gain=0.14)
    # 1924
    s.add(sc["climbers"] - 0.1, A.stereo(flicker(sc["boot"] - sc["climbers"] + 1.0), 0.0, 0.5), gain=0.35)
    s.add(sc["climbers"] - 0.2, A.stereo(wind(sc["boot"] - sc["climbers"] + 2.5, seed=7, lo=150, hi=900), 0.2, 0.7),
          gain=0.35)
    # 2024: meltwater
    for k in range(6):
        s.add(c["y2024"] + 0.2 + 0.55 * k, drip(seed=k), gain=0.22, pan=-0.3 + 0.12 * k)
    s.add(c["name"] - 0.1, A.sfx_zip(0.15, 900, 3000, seed=110), gain=0.18)
    # the camera: a dry click, then silence
    s.add(c["camera"] - 0.05, A.sfx_shutter(seed=111), gain=0.35)
    s.add(sc["camera"] - 0.2, A.stereo(wind(sc["outro"] - sc["camera"] + 1.0, seed=9, lo=600, hi=3500), 0.0, 0.8),
          gain=0.30)
    # back to the summit, into the loop
    s.add(sc["outro"] - 0.3, A.sfx_whoosh(0.9, 3000, 400, seed=112), gain=0.2)
    s.add(dur - 0.85, A.sfx_reverse_swell(0.87), gain=0.26)
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
