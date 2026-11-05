"""EP002 sound design: score + SFX cue sheet + mix.

Musical idea: the music itself gets edited. It stutters on "not the only
edit", dips into darkness on every blink, zips with every eye jump, plays a
sound backwards for "back in time", and the clock's tick goes missing while
the second hand appears frozen. Harmony sits in E minor and ends on B7sus4,
so the loop back to the opening E-minor chord lands as a cadence.
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
    c = {"sc": sc,
         "want": w("L02", "Want"), "close": w("L02", "Close"), "stare": w("L02", "Stare"),
         "slowly": w("L03", "slowly"), "L04end": T.line("L04").end, "L05": T.line("L05").start,
         "blind": w("L05", "blind"), "optic": w("L05", "optic"), "nothing": w("L05", "nothing"),
         "paints": w("L06", "paints"), "L07": T.line("L07").start, "edit7": w("L07", "edit."),
         "blink": w("L08", "blink"), "fifteen": w("L08", "fifteen"), "darkness": w("L08", "darkness."),
         "jump": w("L09", "jump"), "smears": w("L10", "smears"), "cuts": w("L10", "cuts"),
         "stretching": w("L11", "stretching"), "back": w("L11", "back"),
         "glance": w("L12", "glance"), "freeze": w("L12", "freeze."), "didnt": w("L13", "didn't."),
         "stretched": w("L13", "stretched"), "live": w("L14", "live."), "edit14": w("L14", "edit."),
         "L15": T.line("L15").start}
    # timings that must match episode.py exactly
    c["blinks"] = [c["blink"] + 0.15, c["fifteen"] + 0.55, c["darkness"] - 0.75]
    g0 = c["jump"] - 0.2
    c["hops"] = [g0 + k / 3 for k in range(1, 200) if g0 + k / 3 < sc["stretch"] - 0.1]
    s0 = sc["clock"]
    glance = c["glance"] + 0.1
    freeze_until = c["freeze"] + 0.65
    ticks = [s0 + k for k in range(1, 20) if s0 + k < glance] + [glance]
    k = 0
    end = sc["outro"] + 0.2
    while freeze_until + k < end:
        ticks.append(freeze_until + k)
        k += 1
    c["ticks"], c["glance_t"], c["freeze_until"] = ticks, glance, freeze_until
    return c


def build_music(T: Timeline, dur: float):
    c = cues(T)
    sc = c["sc"]
    m = A.Track(dur)
    ir = A.make_ir(3.6, damp=5000, seed=31)
    chords = [("test", ["E2", "B2", "G3", "B3", "F#4"], 900, 0.40),
              ("anatomy", ["C3", "G3", "B3", "E4"], 1300, 0.50),
              ("paint", ["A2", "E3", "G3", "B3", "C4"], 1400, 0.50),
              ("blink", ["G2", "D3", "B3", "D4"], 1500, 0.50),
              ("saccade", ["D3", "F#3", "A3", "E4"], 1700, 0.50),
              ("stretch", ["B2", "F#3", "A3", "D4"], 1300, 0.50),
              ("clock", ["E2", "B2", "G3", "D4"], 1000, 0.45),
              ("outro", ["C3", "G3", "B3", "E4"], 1400, 0.55)]
    order = [k for k, *_ in chords]
    for i, (sid, notes, cut, g) in enumerate(chords):
        t0 = sc[sid]
        t1 = sc[order[i + 1]] if i + 1 < len(order) else c["L15"] - 0.1
        attack = 0.05 if sid == "test" else 0.8
        x = A.pad_chord(notes, (t1 - t0) + 1.8, cutoff=cut, attack=attack, release=1.8, seed=40 + i)
        m.add(t0 - (0 if sid == "test" else 0.35), x, gain=g)
    # B7sus4 at the end: the dominant that the loop resolves into E minor
    x = A.pad_chord(["B2", "F#3", "A3", "E4"], dur - c["L15"] + 2.0, cutoff=1500, attack=0.5, release=1.5, seed=49)
    m.add(c["L15"] - 0.15, x, gain=0.55)
    m.add(0.0, A.stereo(A.drone(A.note_hz("E2"), dur + 1.0, lfo=0.05)), gain=0.14)
    # gentle music-box arpeggio after the test, 8ths at 84 bpm
    beat = 60 / 84
    seqs = {"anatomy": ["E5", "G5", "B5", "E6"], "paint": ["A4", "C5", "E5", "G5"], "blink": ["G4", "B4", "D5", "G5"],
            "saccade": ["F#5", "A5", "D5", "E5"], "stretch": ["D5", "F#5", "B4", "A4"], "outro": ["E5", "G5", "B5", "D6"]}
    t = sc["anatomy"] + 0.4
    k = 0
    order2 = ["anatomy", "paint", "blink", "saccade", "stretch"]
    while t < sc["clock"] - 0.3:
        sid = [s for s in order2 if sc[s] <= t][-1]
        m.add(t, A.pluck(A.note_hz(seqs[sid][k % 4]), 1.2, bright=0.6, decay=0.35), gain=0.16,
              pan=-0.4 if k % 2 else 0.4)
        t += beat / 2
        k += 1
    t = sc["outro"] + 0.3
    while t < c["L15"]:
        m.add(t, A.pluck(A.note_hz(seqs["outro"][k % 4]), 1.6, bright=0.5, decay=0.5), gain=0.17,
              pan=-0.3 if k % 2 else 0.3)
        t += beat / 2
        k += 1
    # clock section: the music holds its breath while time "freezes"
    m.buf = A.reverb(m.buf, ir, wet=0.38)
    m.buf = A.stutter(m.buf, c["edit7"] - 0.02, slice_s=0.07, repeats=4)
    for b in c["blinks"]:
        m.buf = A.dip(m.buf, b, 0.36, depth_db=-14)
    m.buf = A.dip(m.buf, c["glance_t"], c["freeze_until"] - c["glance_t"] + 0.1, depth_db=-8)
    return m


def build_sfx(T: Timeline, dur: float):
    c = cues(T)
    sc = c["sc"]
    s = A.Track(dur)
    ir = A.make_ir(2.0, damp=7000, seed=33)
    # hook: soft impact + shimmer, gentle enough for the test that follows
    s.add(0.0, A.sfx_boom(2.0, 80, 32, seed=34), gain=0.42)
    s.add(0.0, A.stereo(A.sfx_shimmer(2.6, "B5"), 0, 0.6), gain=0.26)
    for k, key in enumerate(("close", "stare", "slowly")):
        s.add(c[key] - 0.12, A.sfx_blip(1600 + 250 * k, 0.07), gain=0.32, pan=-0.2 + 0.2 * k)
    # the try-it pause: a slow heartbeat, then a soft "did it?" chime
    t = c["L04end"] + 0.2
    while t < sc["anatomy"] - 0.5:
        s.add(t, A.sfx_thump(54, 0.45), gain=0.38)
        s.add(t + 0.26, A.sfx_thump(50, 0.45), gain=0.26)
        t += 1.0
    s.add(sc["anatomy"] - 0.45, A.sfx_chime(("B5", "E6"), 0.09, 1.4), gain=0.26)
    for sid in ("anatomy", "paint", "blink", "saccade", "stretch", "clock", "outro"):
        s.add(sc[sid] - 0.3, A.sfx_whoosh(0.7, 300, 4200, seed=50 + len(sid)), gain=0.22,
              pan=0.25 if len(sid) % 2 else -0.25)
    # anatomy
    s.add(sc["anatomy"] + 0.2, A.sfx_laser(0.9, 1800, 600), gain=0.16, pan=-0.3)
    s.add(c["blind"], A.sfx_ping(900, 1.0, 0.22), gain=0.28, pan=0.3)
    s.add(c["nothing"], A.sfx_thump(46, 0.5), gain=0.4)
    # paint: brush sweep + sparkle
    s.add(c["paints"] - 0.1, A.sfx_whoosh(1.0, 2500, 600, seed=61, peak=0.4), gain=0.3, pan=0.3)
    s.add(c["paints"] + 0.3, A.stereo(A.sfx_shimmer(1.6, "E6"), 0.3, 0.5), gain=0.3)
    # blinks: shutter + delete
    for b in c["blinks"]:
        s.add(b, A.sfx_shutter(), gain=0.42, pan=0.0)
    s.add(c["darkness"] + 0.05, A.sfx_snip(), gain=0.32, pan=0.2)
    # saccades: a tiny zip on every hop
    for k, h in enumerate(c["hops"]):
        s.add(h, A.sfx_zip(seed=70 + k % 5), gain=0.16, pan=-0.35 + 0.7 * ((k % 4) / 3))
    s.add(c["cuts"] - 0.02, A.sfx_snip(seed=80), gain=0.42)
    # stretch: literally backwards
    s.add(c["stretching"] - 0.05, A.reverse(A.sfx_whoosh(1.1, 300, 5000, seed=81, peak=0.25)), gain=0.32)
    s.add(c["back"] - 0.9, A.sfx_reverse_swell(1.0), gain=0.3)
    # the clock: ticks follow the second hand; nothing while it "freezes"
    for k, tt in enumerate(c["ticks"]):
        s.add(tt, A.sfx_tick(2900 if k % 2 == 0 else 2500, 0.12, seed=90 + k % 3), gain=0.42, pan=0.15)
    s.add(c["glance_t"] - 0.22, A.sfx_zip(0.16, 700, 3200, seed=95), gain=0.3, pan=-0.4)
    s.add(c["didnt"], A.sfx_thump(60, 0.5), gain=0.38)
    long_tick = A.sfx_tick(1300, 0.6, seed=96)
    s.add(c["stretched"] + 0.1, np.repeat(long_tick, 2)[:int(1.2 * SR)] * 0.8, gain=0.35)
    # outro: LIVE gets struck, EDIT stamps in, riser into the loop
    s.add(c["live"], A.sfx_buzz(0.22, 120), gain=0.16, pan=0.3)
    s.add(c["edit14"], A.sfx_boom(1.4, 120, 50, seed=97), gain=0.42)
    s.add(c["edit14"] + 0.02, A.sfx_chime(("E6", "B6"), 0.07, 1.4), gain=0.24)
    s.add(c["L15"], A.sfx_riser(dur - c["L15"] + 0.05, 180, 1400, seed=98), gain=0.28)
    s.add(dur - 0.85, A.sfx_reverse_swell(0.87), gain=0.32)
    s.buf = A.reverb(s.buf, ir, wet=0.16)
    return s


def build_mix(timeline_path: Path, voice_wav: Path | None, out_dir: Path, tag: str):
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
    sf.write(stems / f"voice_{tag}_processed.flac", (voice[:, 0] * gain).astype(np.float32), SR, subtype="PCM_24")
    report = {"integrated_lufs": round(float(lufs), 2), "true_peak_dbtp": round(float(tp), 2),
              "bed_lufs": round(float(A.loudness(bed)), 2), "master_gain_db": round(float(20 * np.log10(gain)), 2)}
    (out_dir / f"mix_{tag}_report.json").write_text(json.dumps(report, indent=1))
    print(f"[mix:{tag}] {report}")
    return report


if __name__ == "__main__":
    tl = Path(sys.argv[1])
    build_mix(tl, Path(sys.argv[2]), tl.parent, sys.argv[3] if len(sys.argv) > 3 else "ai")
