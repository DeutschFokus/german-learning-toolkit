"""EP003 sound design: wind, wood and stone.

Musical idea: a slow F-minor elegy for a 4,900-year-old tree, with the
mountain wind always underneath. Concrete sounds tell the story: the wood
cracks and the tree falls on "down", ticks race the ring counter, a warm
pulse marks the one living strip, stone courses thud as the pyramid rises.
Harmony ends on C7sus4 so the loop back to the opening F-minor chord lands
as a cadence. All cues come from the timeline (scratch read now, the
creator's own read later), so the score follows his voice.
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

from engine import audio as A  # noqa: E402
from engine.timeline import Timeline  # noqa: E402

SR = A.SR


def cues(T: Timeline):
    w = lambda l, k: T.word(l, k).start  # noqa: E731
    sc = dict(T.scene_starts())
    return {"sc": sc,
            "vandal": w("L02", "vandal."), "scientist": w("L03", "scientist,"), "count": w("L03", "count"),
            "rings3": w("L03", "rings."), "permission": w("L04", "permission,"), "down": w("L04", "down."),
            "n4844": w("L05", "4,844"), "L05end": T.line("L05").end, "die": w("L06", "die."),
            "single": w("L07", "single"), "strip": w("L07", "strip"), "reliable": w("L08", "reliable,"),
            "correct": w("L08", "correct"), "still": w("L09", "still"), "L10": T.line("L10").start,
            "before": w("L10", "before"), "pyramid": w("L10", "Pyramid"), "built": w("L10", "built."),
            "L10end": T.line("L10").end, "secret": w("L11", "secret."), "wont": w("L12", "won't"),
            "L14": T.line("L14").start, "last": w("L14", "last")}


def wind(dur, seed=61, level=1.0):
    n = int(dur * SR)
    rng = np.random.default_rng(seed)
    t = np.arange(n) / SR
    out = np.zeros((n, 2))
    for ch in range(2):
        x = A.sweep_filter(rng.normal(0, 1, n), 380, 900, "bandpass", q=0.8, block=4096, curve="lin")
        gust = 0.55 + 0.45 * np.sin(2 * np.pi * t / 7.5 + ch * 1.7) * np.sin(2 * np.pi * t / 12.0 + 0.4)
        out[:, ch] = x * gust
    return out * 0.5 * level


def build_music(T: Timeline, dur: float):
    c = cues(T)
    sc = c["sc"]
    m = A.Track(dur)
    ir = A.make_ir(4.0, damp=4200, seed=63)
    chords = [("hook", ["F2", "C3", "Ab3", "G4"], 900, 0.45),
              ("cut", ["Db3", "Ab3", "C4", "F4"], 1000, 0.45),
              ("count", ["Ab2", "Eb3", "C4", "G4"], 1400, 0.50),
              ("strip", ["Bb2", "F3", "Db4", "C5"], 1200, 0.50),
              ("carbon", ["Eb3", "Bb3", "G4", "D5"], 1600, 0.50),
              ("methuselah", ["Db3", "Ab3", "F4", "C5"], 1500, 0.55),
              ("secret", ["F2", "C3", "Ab3", "Db4"], 1000, 0.45),
              ("outro", ["Db3", "Ab3", "C4", "F4"], 1100, 0.50)]
    order = [k for k, *_ in chords]
    for i, (sid, notes, cut, g) in enumerate(chords):
        t0 = sc[sid]
        t1 = sc[order[i + 1]] if i + 1 < len(order) else c["L14"] - 0.1
        x = A.pad_chord(notes, (t1 - t0) + 2.0, cutoff=cut, attack=0.05 if sid == "hook" else 1.0, release=2.0,
                        seed=70 + i)
        m.add(t0 - (0 if sid == "hook" else 0.4), x, gain=g)
    x = A.pad_chord(["C3", "G3", "Bb3", "F4"], dur - c["L14"] + 2.0, cutoff=1300, attack=0.6, release=1.5, seed=79)
    m.add(c["L14"] - 0.15, x, gain=0.55)
    m.add(0.0, A.stereo(A.drone(A.note_hz("F1") * 2, dur + 1.0, lfo=0.04)), gain=0.16)
    # a sparse, slow melody that only plays in the quiet middle (strip -> methuselah)
    mel = [("C5", 0.0), ("Ab4", 1.6), ("G4", 3.2), ("F4", 4.8), ("Eb4", 7.2), ("F4", 8.8), ("C5", 10.4),
           ("Db5", 12.0), ("C5", 13.6)]
    for nm, dt in mel:
        tt = sc["strip"] + 0.6 + dt
        if tt < sc["secret"] - 0.5:
            m.add(tt, A.pluck(A.note_hz(nm), 2.6, bright=0.35, decay=0.9), gain=0.20, pan=0.15)
    m.buf = A.reverb(m.buf, ir, wet=0.42)
    # the world holds its breath while the tree falls
    m.buf = A.dip(m.buf, c["down"] + 0.1, 1.6, depth_db=-10)
    return m


def build_sfx(T: Timeline, dur: float):
    c = cues(T)
    sc = c["sc"]
    s = A.Track(dur)
    ir = A.make_ir(2.4, damp=6000, seed=65)
    # wind under the landscape scenes, swelling into the loop
    s.add(0.0, wind(dur + 1.0), gain=0.55)
    s.add(0.0, A.sfx_boom(2.4, 70, 28, seed=66), gain=0.45)
    # "not a vandal": marker strike
    s.add(c["vandal"] + 0.15, A.sfx_whoosh(0.35, 2500, 6000, seed=67, peak=0.5), gain=0.35, pan=0.2)
    s.add(c["scientist"] - 0.15, A.sfx_whoosh(0.6, 600, 2500, seed=68), gain=0.25, pan=-0.3)
    # increment borer: a dry, creaking twist into the wood, then the core slides out
    n = int(0.9 * SR)
    tt = np.arange(n) / SR
    rng = np.random.default_rng(69)
    creak = A.bp(rng.normal(0, 1, n), 300, 1400) * (0.5 + 0.5 * np.sin(2 * np.pi * 9 * tt) ** 2) * A.env_adsr(
        n, 0.05, 0.1, 0.8, 0.2, 0.8)
    s.add(c["count"], creak * 0.6, gain=0.4, pan=0.4)
    s.add(c["rings3"], A.sfx_whoosh(0.5, 900, 3000, seed=70), gain=0.25, pan=0.3)
    # permission: rubber stamp
    s.add(c["permission"] - 0.02, A.sfx_thump(90, 0.35), gain=0.55)
    s.add(c["permission"] - 0.02, A.sfx_tick(700, 0.12, seed=71), gain=0.5)
    # "cut it down": crack, creaking fall, heavy landing
    s.add(c["down"] + 0.12, A.sfx_boom(0.9, 240, 80, seed=72), gain=0.5)
    s.add(c["down"] + 0.12, A.sfx_snip(seed=73), gain=0.35)
    n = int(1.4 * SR)
    tt = np.arange(n) / SR
    f = 260 * (0.45 ** (tt / 1.4))
    fall_creak = (np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3 + A.bp(rng.normal(0, 1, n), 200, 900) * 0.4) * (
        tt / 1.4) ** 1.5
    s.add(c["down"] + 0.2, fall_creak, gain=0.45, pan=-0.3)
    s.add(c["down"] + 1.42, A.sfx_boom(2.6, 75, 24, seed=74), gain=0.85)
    s.add(c["down"] + 1.42, A.sfx_rumble(2.0, seed=75), gain=0.45)
    # counting 4,844 rings: ticks accelerate with the counter, a chime when it lands
    t0, t1 = c["n4844"] - 0.2, c["n4844"] + 1.8
    k = 0
    tt_ = t0
    while tt_ < t1:
        u = (tt_ - t0) / (t1 - t0)
        s.add(tt_, A.sfx_tick(1800 + 1600 * u, 0.05, bright=0.5, seed=80 + k % 4), gain=0.22 + 0.1 * u)
        tt_ += 0.11 * (1 - u) ** 1.4 + 0.022
        k += 1
    s.add(t1, A.sfx_chime(("C6", "G6"), 0.08, 1.6), gain=0.3)
    # the living strip: a warm double pulse and a shimmer
    s.add(c["single"], A.sfx_thump(58, 0.5), gain=0.45)
    s.add(c["single"] + 0.3, A.sfx_thump(54, 0.5), gain=0.32)
    s.add(c["strip"] + 0.2, A.stereo(A.sfx_shimmer(2.2, "C6"), 0.2, 0.5), gain=0.35)
    s.add(c["die"] - 0.1, A.sfx_whoosh(0.9, 1800, 400, seed=81), gain=0.2)
    # carbon dating: data blips, then the correction chime
    for j in range(5):
        s.add(c["reliable"] + j * 0.14, A.sfx_blip(1500 + 220 * j, 0.06), gain=0.22, pan=-0.4 + 0.2 * j)
    s.add(c["correct"], A.sfx_chime(("Eb6", "Bb6"), 0.07, 1.5), gain=0.28)
    # Methuselah: a soft bell on "still alive"; stone courses thud as the pyramid rises; a gong at the end
    s.add(c["still"], A.sfx_chime(("Ab5", "Eb6", "Ab6"), 0.10, 2.2), gain=0.26)
    b0, b1 = c["before"], c["built"] + 0.5
    for j in range(14):
        s.add(b0 + (b1 - b0) * (j + 0.5) / 14, A.sfx_thump(70 - j, 0.35), gain=0.30)
    gong = A.pad_chord(["F2", "C3", "F3"], 3.0, cutoff=900, attack=0.005, release=2.6, seed=82)
    s.add(c["L10end"], gong, gain=0.55)
    s.add(c["L10end"], A.sfx_boom(1.6, 90, 40, seed=83), gain=0.4)
    # the secret: reticle hops, stamp, redaction
    hop = 0.42
    j = 1
    while sc["secret"] + j * hop < c["secret"]:
        s.add(sc["secret"] + j * hop, A.sfx_blip(1300 + 90 * (j % 4), 0.05), gain=0.18, pan=-0.4 + 0.2 * (j % 5))
        j += 1
    s.add(c["secret"] - 0.02, A.sfx_thump(80, 0.4), gain=0.55)
    s.add(c["secret"] - 0.02, A.sfx_tick(600, 0.15, seed=84), gain=0.5)
    s.add(c["wont"], A.sfx_whoosh(0.4, 2000, 5000, seed=85, peak=0.6), gain=0.28, pan=0.3)
    # scene transitions
    for sid in ("count", "strip", "carbon", "methuselah", "secret", "outro"):
        s.add(sc[sid] - 0.3, A.sfx_whoosh(0.7, 300, 3800, seed=90 + len(sid)), gain=0.20,
              pan=0.25 if len(sid) % 2 else -0.25)
    # into the loop
    s.add(c["L14"], A.sfx_riser(dur - c["L14"] + 0.05, 160, 1200, seed=91), gain=0.26)
    s.add(dur - 0.85, A.sfx_reverse_swell(0.87), gain=0.32)
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
    sfx *= 10 ** ((-25.0 - A.loudness(sfx)) / 20)
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
