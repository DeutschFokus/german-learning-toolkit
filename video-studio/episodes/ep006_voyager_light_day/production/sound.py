"""EP006 sound design: a call across a light-day.

Musical idea: D major, warm and a little nostalgic. A four-note radio "hello"
(D5 A5 F#5 D6) is the motif: it rides every wave in the hook, returns faintly
when the light pulse reaches Voyager, and closes the loop. Harmony: Dmaj9 ->
G -> Bm9 -> A -> Gmaj7 -> D/F# -> Bm -> G -> Em9 -> A -> A7sus4, so the loop
back to the opening D lands as a cadence.

Concrete sounds tell the story: radio blips and a far-off hiss in deep space,
the 1977 launch (ignition crackle, roar, rumble), a clock racing to 24 hours,
a filament tink and mains hum for the fridge bulb, a camera shutter for the
pale blue dot, vinyl crackle and a music box for the golden record, a real
heartbeat, and a soft beating hum for her brainwaves. All cues come from the
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
HELLO = ("D5", "A5", "F#5", "D6")


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


# --------------------------------------------------------------------------- bespoke sounds

def radio_hello(level=1.0, seed=0):
    """The motif as four soft radio blips with a touch of static."""
    out = np.zeros(int(1.2 * SR))
    for k, nm in enumerate(HELLO):
        b = A.sfx_blip(A.note_hz(nm), 0.11) * 0.9
        i = int(k * 0.13 * SR)
        out[i:i + len(b)] += b
    n = len(out)
    out += A.bp(np.random.default_rng(seed).normal(0, 1, n), 2500, 6000) * 0.02 * np.exp(-np.arange(n) / (0.5 * SR))
    return out * level


def hiss(dur, seed=1):
    n = int(dur * SR)
    x = A.bp(np.random.default_rng(seed).normal(0, 1, n), 1800, 7000)
    t = np.arange(n) / SR
    return x * (0.6 + 0.4 * np.sin(2 * np.pi * 0.21 * t)) * 0.08


def tick(freq=3000.0, seed=0):
    n = int(0.06 * SR)
    t = np.arange(n) / SR
    x = A.bp(np.random.default_rng(seed).normal(0, 1, n), freq * 0.6, min(freq * 1.6, 9000)) * np.exp(-t / 0.004)
    return (x + np.sin(2 * np.pi * 900 * t) * np.exp(-t / 0.012) * 0.3) * 0.6


def crackle(dur, seed=2, rate=14.0):
    """Vinyl surface noise: soft hiss plus sparse pops."""
    n = int(dur * SR)
    rng = np.random.default_rng(seed)
    out = A.lp(rng.normal(0, 1, n), 3500) * 0.02
    t = 0.0
    while t < dur:
        t += rng.exponential(1.0 / rate)
        i = int(t * SR)
        if i + 60 < n:
            out[i:i + 60] += rng.normal(0, 1, 60) * np.exp(-np.arange(60) / 8.0) * rng.uniform(0.1, 0.5)
    return out


def music_box(notes, step=0.32, dur_each=1.8):
    n = int((len(notes) * step + dur_each) * SR)
    out = np.zeros(n)
    for k, nm in enumerate(notes):
        if nm is None:
            continue
        f = A.note_hz(nm)
        m = int(dur_each * SR)
        tt = np.arange(m) / SR
        x = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * f * 3.01 * tt) * np.exp(-tt / 0.15)
             + 0.15 * np.sin(2 * np.pi * f * 5.4 * tt) * np.exp(-tt / 0.05)) * np.exp(-tt / 0.6)
        i = int(k * step * SR)
        out[i:i + m] += x[:n - i] * 0.25
    return out


def heartbeat(bpm, beats):
    period = 60.0 / bpm
    n = int((beats * period + 0.6) * SR)
    out = np.zeros(n)
    for k in range(beats):
        for dt, f, g in ((0.0, 58.0, 1.0), (0.22, 64.0, 0.7)):
            th = A.sfx_thump(f, 0.30) * g
            i = int((k * period + dt) * SR)
            out[i:i + len(th)] += th[:n - i]
    return out


def beating_hum(dur, f=196.0, beat=10.0):
    """Two close tones beating at ~10 Hz, the rhythm of relaxed brainwaves."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * t) + np.sin(2 * np.pi * (f + beat) * t)
    return x * A.env_adsr(n, 0.6, 0.3, 0.8, 1.0, 0.8) * 0.12


def mains_hum(dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 100 * t) + 0.4 * np.sin(2 * np.pi * 200 * t) + 0.2 * np.sin(2 * np.pi * 300 * t)
    return x * A.env_adsr(n, 0.05, 0.1, 0.9, 0.4, 0.9) * 0.05


def ignition(seed=5):
    n = int(5.5 * SR)
    rng = np.random.default_rng(seed)
    t = np.arange(n) / SR
    roar = A.lp(rng.normal(0, 1, n), 900) * (1 - np.exp(-t / 0.3)) * np.exp(-np.maximum(t - 3.5, 0) / 1.2)
    crack = A.bp(rng.normal(0, 1, n), 1500, 6000) * (0.4 + 0.6 * (rng.random(n) > 0.995)) * 0.25 * np.exp(-t / 2.0)
    return (roar * 0.8 + crack) * 0.6


# --------------------------------------------------------------------------- music

def build_music(T: Timeline, dur: float):
    c = cues(T)
    sc = c["sc"]
    m = A.Track(dur)
    ir = A.make_ir(4.6, damp=4500, seed=63)
    plan = [
        (0.0, ["D2", "A2", "F#3", "C#4", "E4"], 1100, 0.45, 0.05),
        (sc["launch"] - 0.2, ["G1", "D2", "B2", "D3", "A3"], 1100, 0.48, 0.5),
        (sc["lightday"] - 0.2, ["B1", "F#2", "D3", "A3", "C#4"], 1300, 0.48, 0.6),
        (sc["bulb"] - 0.2, ["A1", "E2", "C#3", "E3", "B3"], 1200, 0.46, 0.6),
        (sc["dot"] - 0.2, ["G2", "D3", "F#3", "B3"], 1000, 0.40, 1.0),
        (sc["record"] - 0.2, ["F#2", "A2", "D3", "F#3", "A3"], 1600, 0.48, 0.6),
        (sc["love"] - 0.2, ["B1", "F#2", "D3", "A3"], 1200, 0.48, 0.8),
        (c["ann"] - 0.2, ["G1", "D2", "B2", "F#3", "D4"], 1300, 0.48, 0.8),
        (sc["star"] - 0.2, ["E2", "B2", "G3", "F#4"], 1500, 0.50, 0.8),
        (c["carrying"] - 0.2, ["A1", "E2", "C#3", "G3", "B3"], 1500, 0.50, 0.6),
        (sc["outro"] - 0.2, ["A1", "E2", "G2", "D3", "E3"], 1200, 0.50, 0.6),
    ]
    for i, (t0, notes, cut, g, att) in enumerate(plan):
        t1 = plan[i + 1][0] if i + 1 < len(plan) else dur
        x = A.pad_chord(notes, (t1 - t0) + 2.2, cutoff=cut, attack=att, release=2.0, seed=80 + i)
        m.add(t0, x, gain=g)
    m.add(0.0, A.stereo(A.drone(A.note_hz("D1") * 2, dur + 1.0, lfo=0.05)), gain=0.13)
    # the music box: an original lullaby for the record and the love story
    tune = ["D5", "F#5", "A5", "F#5", "E5", "D5", "B4", "D5", "A4", None, "B4", "D5", "E5", "F#5", "E5", "D5"]
    m.add(c["music"] - 0.05, A.stereo(music_box(tune, step=0.30), 0.2, 0.4), gain=0.38)
    m.add(c["carrying"] - 0.1, A.stereo(music_box(tune[:9], step=0.42, dur_each=2.4), -0.1, 0.5), gain=0.36)
    # a slow, tender line over the love story
    for j, nm in enumerate(("F#4", "A4", "B4", "D5", "C#5", "A4")):
        m.add(c["brainwaves"] + j * 0.62, A.pluck(A.note_hz(nm), 2.6, bright=0.25, decay=1.1), gain=0.17,
              pan=-0.2 + 0.08 * j)
    m.buf = A.reverb(m.buf, ir, wet=0.44)
    # a held breath for the pale blue dot
    m.buf = A.dip(m.buf, c["pale"] - 0.2, 1.6, depth_db=-8)
    return m


# --------------------------------------------------------------------------- SFX

def build_sfx(T: Timeline, dur: float):
    c = cues(T)
    sc = c["sc"]
    s = A.Track(dur)
    ir = A.make_ir(2.6, damp=6000, seed=65)
    # deep-space hiss under the space scenes; a "hello" rides every wave of the hook and the outro (3 s period)
    s.add(0.0, A.stereo(hiss(dur + 1.0), 0.0, 0.6), gain=0.5)
    for k in range(int(dur / 3.0)):
        tt = k * 3.0 + 0.4
        if tt < sc["launch"] - 0.4 or tt >= sc["outro"] - 0.1:
            s.add(tt, radio_hello(seed=k), gain=0.32, pan=-0.45)
    s.add(0.0, A.sfx_boom(2.0, 60, 26, seed=66), gain=0.30)
    s.add(c["tomorrow"] - 0.05, A.sfx_chime(("D6", "A6"), 0.09, 1.8), gain=0.22)
    # launch
    ign = sc["launch"] + 0.35
    s.add(ign, ignition(seed=67), gain=0.16)
    s.add(ign, A.sfx_rumble(5.0, seed=68), gain=0.22)
    s.add(ign + 0.1, A.sfx_boom(3.0, 55, 20, seed=69), gain=0.28)
    s.add(c["y1977"] - 0.05, A.sfx_thump(64, 0.5), gain=0.40)
    # one light-day: the zoom out, the pulse, a clock racing to 24:00, the motif arriving
    s.add(sc["lightday"] - 0.3, A.sfx_whoosh(1.4, 3000, 300, seed=70), gain=0.25)
    s.add(c["nov18"] - 0.1, A.sfx_tick(900, 0.10, seed=71), gain=0.30)
    s.add(c["crosses"], A.sfx_whoosh(c["lightday"] + 0.5 - c["crosses"], 300, 2400, seed=72, peak=0.8), gain=0.25)
    t0, t1 = c["crosses"], c["lightday"] + 0.5
    tt, k = t0, 0
    while tt < t1:
        u = (tt - t0) / (t1 - t0)
        s.add(tt, tick(2400 + 2400 * u, seed=k % 5), gain=0.20 + 0.10 * u)
        tt += 0.16 * (1 - u) ** 1.3 + 0.03
        k += 1
    s.add(t1, A.sfx_chime(("D6", "F#6", "A6"), 0.08, 2.2), gain=0.30)
    s.add(t1 + 0.1, radio_hello(level=0.7, seed=9), gain=0.28, pan=0.3)
    # the bulb
    s.add(c["calls"] - 0.1, A.stereo(hiss(3.0, seed=10), 0.4, 0.4), gain=0.4)
    s.add(c["fridge"] - 0.1, A.sfx_tick(4200, 0.05, seed=73), gain=0.40)
    s.add(c["fridge"] - 0.1, A.stereo(mains_hum(c["L04end"] - c["fridge"] + 1.2), -0.3), gain=0.35)
    # the pale blue dot: a turn, a shutter, silence, one bell
    s.add(c["turned"] - 0.1, A.sfx_whoosh(1.2, 400, 1600, seed=74, peak=0.5), gain=0.20)
    s.add(c["photo"] - 0.05, A.sfx_shutter(seed=75), gain=0.45)
    s.add(c["pale"] - 0.05, A.sfx_chime(("D5", "A5"), 0.20, 3.2), gain=0.24)
    # the golden record: stylus drop, crackle, the heartbeat
    s.add(c["golden"] - 0.1, A.sfx_whoosh(0.6, 1800, 5200, seed=76, peak=0.6), gain=0.22)
    s.add(c["golden"] + 0.3, A.sfx_thump(120, 0.15), gain=0.30)
    s.add(c["golden"] + 0.3, A.stereo(crackle(sc["love"] - c["golden"] + 0.5, seed=77), 0.0, 0.5), gain=0.34)
    s.add(c["whoever"] - 0.2, A.sfx_whoosh(0.7, 600, 2600, seed=78), gain=0.18)
    for j in range(6):
        s.add(c["greetings"] + 0.1 + j * 0.22, A.sfx_blip(1200 + 160 * j, 0.06), gain=0.12, pan=-0.6 + 0.24 * j)
    s.add(c["heartbeat"] - 0.05, heartbeat(64, 2), gain=0.55)
    # her brainwaves; two names; two stars drawn together
    s.add(c["brainwaves"] - 0.2, A.stereo(beating_hum(c["L08end"] - c["brainwaves"] + 1.5), 0.0, 0.7), gain=0.45)
    s.add(c["ann"] - 0.05, A.sfx_chime(("F#5", "D6"), 0.10, 2.0), gain=0.20)
    s.add(c["carl"] - 0.05, A.sfx_chime(("A5", "E6"), 0.10, 2.0), gain=0.20)
    # 40,000 years: a vast swell, the star's shimmer
    s.add(sc["star"] - 0.2, A.sfx_reverse_swell(1.2), gain=0.28)
    s.add(c["n40000"], A.stereo(A.sfx_shimmer(3.5, "A5", seed=79), 0.2, 0.6), gain=0.35)
    s.add(c["star"] - 0.3, A.sfx_boom(2.4, 48, 22, seed=80), gain=0.35)
    # back home, into the loop
    s.add(sc["outro"] - 0.3, A.sfx_whoosh(0.9, 3000, 400, seed=81), gain=0.22)
    s.add(c["listening"] - 0.2, A.sfx_riser(dur - c["listening"] + 0.25, 180, 1300, seed=82), gain=0.22)
    s.add(dur - 0.85, A.sfx_reverse_swell(0.87), gain=0.30)
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
