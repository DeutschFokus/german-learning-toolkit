"""EP001 sound design: score + SFX cue sheet + mix.

Musical idea: two clocks that tick at different rates (head 2.5 Hz, feet
2 Hz) so they drift in and out of phase — time dilation you can hear. The
harmony walks D minor -> warm F/Bb -> and parks on A7sus4 at the end, so the
loop back to the opening D-minor boom resolves like a cadence.

All times come from the timeline, so a re-timed narration moves the score.
"""
from __future__ import annotations

import json
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
    return {
        "sc": sc,
        "L02": T.line("L02").start, "up": w("L03", "Up"), "faster3": w("L03", "faster"),
        "einstein": w("L04", "Einstein"), "gravity": w("L04", "gravity"), "closer": w("L05", "closer"),
        "slower": w("L05", "slower"),
        "y2010": w("L06", "2010"), "atomic": w("L07", "atomic"), "lifted": w("L07", "lifted"), "33": w("L07", "33"),
        "faster8": w("L08", "faster"),
        "phone": w("L09", "phone"), "orbit": w("L10", "orbit"), "38": w("L10", "38"), "second": w("L10", "second"),
        "light": w("L11", "Light"), "km_end": T.word("L11", "kilometers").end, "L12": T.line("L12").start,
        "built": w("L12", "built"), "einstein12": w("L12", "Einstein"),
        "now": w("L13", "Now"), "down": w("L13", "down"), "deep": w("L14", "Deep"), "center": w("L14", "center"),
        "two": w("L14", "two"), "younger": w("L14", "younger"), "L14end": T.line("L14").end,
        "L15": T.line("L15").start, "lifetime": w("L16", "lifetime"), "second16": w("L16", "second"),
        "tiny": T.line("L17").start, "real": T.line("L18").start, "which": T.line("L19").start,
    }


# ----------------------------------------------------------------------------- score

def build_music(T: Timeline, dur: float) -> np.ndarray:
    c = cues(T)
    sc = c["sc"]
    m = A.Track(dur)
    ir = A.make_ir(3.2, damp=5200)
    chords = [
        ("hook", ["D3", "A3", "C4", "E4", "F4"], 1100),
        ("well", ["Bb2", "F3", "A3", "D4"], 1300),
        ("lab", ["G2", "D3", "F3", "A3", "Bb3"], 1500),
        ("gps", ["C3", "F3", "A3", "E4", "G4"], 1700),
        ("light", ["Bb2", "F3", "C4", "D4", "E4"], 1800),
        ("dive", ["D2", "A2", "E3"], 700),
        ("you", ["F2", "C3", "E3", "A3"], 1300),
        ("outro", ["G2", "D3", "F3", "Bb3"], 1200),
    ]
    order = [k for k, _, _ in chords]
    for i, (sid, notes, cut) in enumerate(chords):
        t0 = sc[sid]
        t1 = sc[order[i + 1]] if i + 1 < len(order) else dur
        if sid == "outro":
            t1 = c["which"] - 0.1
        attack = 0.04 if sid == "hook" else 0.9
        x = A.pad_chord(notes, (t1 - t0) + 1.8, cutoff=cut, attack=attack, release=1.8, seed=i)
        m.add(t0 - (0 if sid == "hook" else 0.4), x, gain=0.55 if sid != "dive" else 0.45)
    # A7sus4 at the end: the dominant that the loop resolves
    x = A.pad_chord(["A2", "E3", "G3", "D4"], dur - c["which"] + 2.0, cutoff=1500, attack=0.6, release=1.5, seed=9)
    m.add(c["which"] - 0.2, x, gain=0.6)
    # drone on D throughout except the bright middle
    for t0, t1, f, g in ((0, sc["lab"], A.note_hz("D2"), 0.22), (sc["dive"], sc["you"] + 0.5, A.note_hz("D1") * 2, 0.32),
                         (sc["you"], dur, A.note_hz("D2"), 0.16)):
        m.add(t0, A.stereo(A.drone(f, t1 - t0 + 1.5)), gain=g)
    # arpeggio: lab -> light (8th notes on the beat grid)
    beat = 60 / 96
    arp = {"lab": ["G3", "D4", "F4", "A4", "Bb4", "A4", "F4", "D4"],
           "gps": ["C4", "F4", "A4", "E5", "G4", "A4", "F4", "C5"],
           "light": ["Bb3", "F4", "C5", "D5", "E5", "D5", "C5", "F4"]}
    t = sc["lab"] + 0.3
    k = 0
    while t < sc["dive"] - 0.4:
        sid = "lab" if t < sc["gps"] else "gps" if t < sc["light"] else "light"
        nm = arp[sid][k % 8]
        g = 0.20 if sid == "lab" else 0.24
        m.add(t, A.pluck(A.note_hz(nm), 1.2, bright=0.8, decay=0.32), gain=g, pan=-0.35 if k % 2 else 0.35)
        t += beat / 2
        k += 1
    # bass pulse: gps + light
    roots = {"gps": "C2", "light": "Bb1"}
    t = sc["gps"] + 0.2
    k = 0
    while t < sc["dive"] - 0.5:
        sid = "gps" if t < sc["light"] else "light"
        m.add(t, A.stereo(A.bass_note(A.note_hz(roots[sid]), beat / 2 * 0.95)), gain=0.38 if k % 2 == 0 else 0.25)
        t += beat / 2
        k += 1
    # dive heartbeat under the reveal
    t = c["down"] + 0.9
    while t < c["two"] - 0.3:
        m.add(t, A.sfx_thump(52, 0.5), gain=0.5)
        m.add(t + 0.28, A.sfx_thump(48, 0.5), gain=0.35)
        t += 1.25
    # big chord stab on "two and a half years"
    stab = A.pad_chord(["D2", "A2", "F3", "E4", "A4"], 3.5, cutoff=2600, attack=0.01, release=2.5, seed=21)
    m.add(c["two"], stab, gain=0.6)
    # warm plucks in the "you" section
    seq = ["F4", "A4", "C5", "E5", "D5", "C5", "A4", "G4"]
    t = sc["you"] + 0.6
    k = 0
    while t < sc["outro"] + 2.0:
        m.add(t, A.pluck(A.note_hz(seq[k % len(seq)]), 1.8, bright=0.5, decay=0.6), gain=0.22,
              pan=-0.3 if k % 2 else 0.3)
        t += beat
        k += 1
    wet = A.reverb(m.buf, ir, wet=0.38)
    m.buf = wet
    return m


# ----------------------------------------------------------------------------- SFX

def build_sfx(T: Timeline, dur: float) -> np.ndarray:
    c = cues(T)
    sc = c["sc"]
    s = A.Track(dur)
    ir = A.make_ir(2.2, damp=7000, seed=5)
    # the two clocks (hook, you, outro) — 0.4 s and 0.5 s periods, phase-locked to the visuals
    head = A.sfx_tick(3300, 0.1, seed=1)
    feet = A.sfx_tick(2300, 0.1, seed=2)
    spans = [(0.0, sc["well"] + 0.1, 1.0), (c["L15"] + 0.4, dur, 1.0)]
    for t0, t1, g in spans:
        for period, snd, pan, gg in ((0.4, head, 0.35, 0.16), (0.5, feet, -0.35, 0.18)):
            k = int(np.ceil(t0 / period))
            while k * period < t1:
                tt = k * period
                fade = min(1.0, (tt - t0) / 0.6 + (1.0 if t0 == 0 else 0.0), (t1 - tt) / 0.4)
                s.add(tt, snd, gain=gg * g * fade, pan=pan)
                k += 1
    # hook impact
    s.add(0.0, A.sfx_boom(2.4, 92, 30), gain=0.5)
    s.add(0.0, A.stereo(A.sfx_shimmer(2.5, "A5"), 0, 0.6), gain=0.28)
    # headline exits, arrow rises, "faster"
    s.add(c["L02"] - 0.25, A.sfx_whoosh(0.7, 400, 3000, seed=2), gain=0.22, pan=-0.4)
    s.add(c["up"] - 0.1, A.sfx_riser(1.0, 300, 1800, seed=3), gain=0.25)
    s.add(c["faster3"], A.sfx_ping(2600, 1.0, 0.18), gain=0.3, pan=0.3)
    # scene transitions
    for sid in ("well", "lab", "gps", "light"):
        s.add(sc[sid] - 0.35, A.sfx_whoosh(0.8, 250, 4500, seed={"well": 21, "lab": 22, "gps": 23, "light": 24}[sid]), gain=0.28,
              pan=0.2 if sid in ("lab", "light") else -0.2)
    # well
    s.add(c["einstein"] - 0.05, A.sfx_thump(70, 0.6), gain=0.45)
    s.add(c["gravity"] - 0.1, A.sfx_boom(2.4, 70, 26, seed=4), gain=0.55)
    s.add(c["gravity"], A.sfx_whoosh(1.4, 1800, 200, seed=8), gain=0.25)
    n = int(1.6 * SR)
    tt = np.arange(n) / SR
    f = 900 * (0.35 ** (tt / 1.6))
    gliss = np.sin(2 * np.pi * np.cumsum(f) / SR) * A.env_adsr(n, 0.2, 0.3, 0.6, 0.8, 0.6) * 0.18
    s.add(c["closer"] + 0.2, gliss, gain=0.6, pan=0.3)
    # lab
    s.add(c["y2010"] - 0.15, A.sfx_counter(0.65, 28, 1900), gain=0.35)
    s.add(c["y2010"] + 0.5, A.sfx_thump(80, 0.5), gain=0.5)
    s.add(c["y2010"] + 0.5, A.sfx_tick(1500, 0.12, seed=4), gain=0.5)
    s.add(c["atomic"], A.sfx_blip(1700, 0.08), gain=0.4, pan=-0.2)
    lift_dur = (c["33"] + 0.3) - c["lifted"]
    s.add(c["lifted"], A.sfx_ruler(33, lift_dur, 1800, 3600), gain=0.32, pan=0.25)
    s.add(c["33"], A.sfx_ping(2200, 1.0, 0.2), gain=0.32)
    s.add(c["faster8"] - 0.05, A.sfx_chime(("A5", "E6", "A6"), 0.07, 1.6), gain=0.26)
    # gps
    for k in range(3):
        s.add(c["phone"] - 0.2 + 0.18 * k, A.sfx_blip(2400 + 300 * k, 0.06), gain=0.3, pan=-0.4 + 0.4 * k)
    s.add(c["orbit"] - 0.25, A.sfx_reverse_swell(0.9), gain=0.3)
    t = c["orbit"] + 0.4
    k = 0
    while t < sc["light"] - 0.3:
        s.add(t, A.sfx_ping(1450 if k % 2 == 0 else 1800, 1.3, 0.3), gain=0.13, pan=-0.5 if k % 2 else 0.5)
        t += 1.25
        k += 1
    s.add(c["38"] - 0.08, A.sfx_boom(1.6, 120, 45, seed=6), gain=0.45)
    s.add(c["38"] - 0.08, A.sfx_counter(0.6, 30, 2200), gain=0.3)
    s.add(c["second"], A.sfx_blip(1500, 0.07), gain=0.35, pan=-0.2)
    s.add(c["second"] + 0.12, A.sfx_blip(1200, 0.07), gain=0.35, pan=0.2)
    # light
    laser = A.sfx_laser(1.4, 3000, 500)
    nL = len(laser)
    pan_env = np.linspace(-0.8, 0.8, nL)
    st = np.stack([laser * np.cos((pan_env + 1) * np.pi / 4), laser * np.sin((pan_env + 1) * np.pi / 4)], axis=1)
    s.add(c["light"], st, gain=0.38)
    s.add(c["km_end"] - 0.05, A.sfx_ping(1000, 0.9, 0.15), gain=0.3, pan=0.5)
    s.add(c["km_end"] + 0.05, A.sfx_buzz(0.3, 92), gain=0.22, pan=0.5)
    s.add(c["L12"] - 0.2, A.sfx_whoosh(0.9, 300, 3800, seed=12), gain=0.25)
    s.add(c["built"] - 0.05, A.sfx_counter(0.9, 22, 2000), gain=0.25)
    s.add(c["einstein12"] - 0.05, A.sfx_chime(("D6", "F#6", "A6"), 0.06, 1.8), gain=0.36)
    # dive
    s.add(c["now"] - 0.1, A.sfx_reverse_swell(max(0.6, c["down"] - c["now"] + 0.1)), gain=0.45)
    s.add(c["down"] + 0.18, A.sfx_boom(3.2, 80, 24, seed=10), gain=0.6)
    s.add(c["down"] + 0.15, A.sfx_rumble(3.6), gain=0.42)
    s.add(c["down"], A.sfx_whoosh(1.3, 3000, 150, seed=13), gain=0.35)
    s.add(c["center"] - 0.1, A.sfx_tick(900, 0.15, seed=7), gain=0.35)
    s.add(c["two"] - 0.6, A.sfx_riser(0.65, 200, 900, seed=14), gain=0.3)
    s.add(c["two"], A.sfx_boom(3.0, 110, 28, seed=15), gain=0.62)
    s.add(c["two"], A.stereo(A.sfx_shimmer(3.5, "D6"), 0, 0.8), gain=0.42)
    s.add(c["L14end"] + 0.4, A.sfx_buzz(0.18, 140), gain=0.12, pan=-0.2)
    # you
    s.add(sc["you"] - 0.2, A.sfx_whoosh(1.0, 3500, 300, seed=16), gain=0.25)
    s.add(c["lifetime"], A.sfx_counter(max(0.5, c["second16"] + 0.3 - c["lifetime"]), 9, 2600), gain=0.12)
    # outro
    s.add(c["tiny"] + 0.35, A.pluck(A.note_hz("A6"), 1.2, bright=0.3, decay=0.4), gain=0.35)
    s.add(c["real"], A.sfx_thump(64, 0.5), gain=0.4)
    s.add(c["real"] + 0.02, A.sfx_chime(("A5", "D6"), 0.08, 1.4), gain=0.25)
    rise = dur - c["which"] + 0.05
    s.add(c["which"], A.sfx_riser(rise, 160, 1500, seed=17), gain=0.32)
    s.add(dur - 0.9, A.sfx_reverse_swell(0.92), gain=0.35)
    s.buf = A.reverb(s.buf, ir, wet=0.18)
    return s


# ----------------------------------------------------------------------------- mix

def build_mix(timeline_path: Path, voice_wav: Path | None, out_dir: Path, tag: str):
    T = Timeline(timeline_path)
    dur = T.duration
    n = int(round(dur * SR))
    music = build_music(T, dur).wrapped()
    sfx = build_sfx(T, dur).wrapped()
    voice = np.zeros((n, 2))
    if voice_wav is not None:
        v, vsr = sf.read(voice_wav, dtype="float64", always_2d=False)
        if v.ndim > 1:
            v = v.mean(axis=1)
        if vsr != SR:
            g = np.gcd(SR, vsr)
            v = resample_poly(v, SR // g, vsr // g)
        v = A.voice_chain(v)
        v = v[:n] if len(v) >= n else np.pad(v, (0, n - len(v)))
        voice = np.stack([v, v], axis=1)
    # levels before mastering
    vl = A.loudness(voice) if voice_wav is not None else -20.0
    voice *= 10 ** ((-17.0 - vl) / 20) if voice_wav is not None else 1.0
    music *= 10 ** ((-27.0 - A.loudness(music)) / 20)
    sfx *= 10 ** ((-25.0 - A.loudness(sfx)) / 20)
    # duck the bed under the narration: by the real voice if present, else by the AI timeline
    key = voice if voice_wav is not None else _speech_key(T, n)
    music_d = A.duck(music, key, depth_db=-8.0, threshold=0.02 if voice_wav is not None else 0.5)
    sfx_d = A.duck(sfx, key, depth_db=-5.0, threshold=0.02 if voice_wav is not None else 0.5)
    mix = voice + music_d + sfx_d
    mastered, lufs, tp = A.master(mix, -14.0, -1.7)
    gain = mastered.std() / max(mix.std(), 1e-12)
    bed = A.limiter((music_d + sfx_d) * gain, -1.7)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    paths["mix"] = out_dir / f"mix_{tag}.wav"
    sf.write(paths["mix"], mastered.astype(np.float32), SR, subtype="PCM_24")
    paths["bed"] = out_dir / f"bed_{tag}.wav"
    sf.write(paths["bed"], bed.astype(np.float32), SR, subtype="PCM_24")
    stems = out_dir / "stems"
    stems.mkdir(exist_ok=True)
    sf.write(stems / f"music_unducked_{tag}.flac", (music * gain).astype(np.float32), SR, subtype="PCM_24")
    sf.write(stems / f"sfx_{tag}.flac", (sfx * gain).astype(np.float32), SR, subtype="PCM_24")
    if voice_wav is not None:
        sf.write(stems / f"voice_{tag}_processed.flac", (voice[:, 0] * gain).astype(np.float32), SR,
                 subtype="PCM_24")
    report = {"integrated_lufs": round(float(lufs), 2), "true_peak_dbtp": round(float(tp), 2),
              "bed_lufs": round(float(A.loudness(bed)), 2), "master_gain_db": round(float(20 * np.log10(gain)), 2)}
    (out_dir / f"mix_{tag}_report.json").write_text(json.dumps(report, indent=1))
    print(f"[mix:{tag}] {report}")
    return paths, report


def _speech_key(T: Timeline, n: int) -> np.ndarray:
    """Synthetic sidechain from line timings (used for the no-voice bed)."""
    k = np.zeros(n)
    for line in T.lines:
        i0, i1 = int(line["start"] * SR), int(line["end"] * SR)
        k[i0:i1] = 1.0
    return np.stack([k, k], axis=1)


if __name__ == "__main__":
    tl = Path(sys.argv[1])
    vw = Path(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] != "-" else None
    build_mix(tl, vw, tl.parent, sys.argv[3] if len(sys.argv) > 3 else "ai")
