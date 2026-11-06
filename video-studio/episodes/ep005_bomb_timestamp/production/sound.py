"""EP005 sound design: a clock inside you.

Musical idea: E minor, with a soft clock tick that frames the story (hook,
clock, outro) and a *sonified* bomb curve: while the real carbon-14 record is
drawn, a pure tone follows it, rising almost an octave for the 1963 peak and
sliding back down year by year. Harmony: Em(add9) -> Cmaj7 -> G -> Em9 ->
Am7 -> Cmaj7/D/Em -> Cmaj9 -> B7sus4, so the loop back to the opening E minor
lands as a cadence.

Concrete sounds tell the story: the flash, then the boom a beat later (sound
is slower than light), Geiger clicks as the carbon rises, a rustling leaf,
a cell dividing, a lock clicking shut on "DNA", a heartbeat for the heart,
neural sparks for the cortex, a muffled womb heartbeat on "before you were
born". All cues come from the timeline (scratch read now, the creator's own
read later).
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
from engine.bio import C14Chart  # noqa: E402
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
    return c


# --------------------------------------------------------------------------- bespoke sounds

def tick(freq=3200.0, seed=0, level=1.0):
    """A soft mechanical clock tick: click + tiny wooden body."""
    n = int(0.06 * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    x = A.bp(rng.normal(0, 1, n), freq * 0.6, min(freq * 1.6, 9000)) * np.exp(-t / 0.004)
    x += np.sin(2 * np.pi * 900 * t) * np.exp(-t / 0.012) * 0.3
    return x * 0.6 * level


def flash_burst(seed=1):
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    x = A.hp(np.random.default_rng(seed).normal(0, 1, n), 2500) * np.exp(-t / 0.06)
    return x * 0.5


def geiger(dur, seed=3, rate0=2.0, rate1=26.0):
    """Clicks with a rising average rate (Poisson-like)."""
    n = int(dur * SR)
    out = np.zeros(n)
    rng = np.random.default_rng(seed)
    t = 0.0
    while t < dur:
        u = t / dur
        rate = rate0 + (rate1 - rate0) * u
        t += rng.exponential(1.0 / rate)
        i = int(t * SR)
        if i + 200 >= n:
            break
        click = rng.normal(0, 1, 200) * np.exp(-np.arange(200) / 18.0)
        out[i:i + 200] += A.hp(click, 1800) * rng.uniform(0.5, 1.0)
    return out * 0.5


def curve_tone(times, freqs, dur):
    """A pure, slightly breathy tone following a frequency trajectory (Hz) given at times (s)."""
    n = int(dur * SR)
    tt = np.arange(n) / SR
    f = np.interp(tt, times, freqs)
    ph = 2 * np.pi * np.cumsum(f) / SR
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * tt)
    x = np.sin(ph * vib) + 0.25 * np.sin(2 * ph) + 0.08 * np.sin(3 * ph)
    env = A.env_adsr(n, 0.25, 0.2, 0.85, 0.8, 0.85)
    return x * env * 0.35


def rustle(dur, seed=5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    x = A.bp(rng.normal(0, 1, n), 2500, 8000) * (0.4 + 0.6 * np.abs(np.sin(2 * np.pi * 3.3 * t + rng.uniform(0, 3))))
    return x * A.env_adsr(n, 0.15, 0.2, 0.7, 0.4, 0.7) * 0.4


def squelch(seed=6):
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f = 180 + 420 * np.exp(-t / 0.08)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.12)
    x += A.bp(np.random.default_rng(seed).normal(0, 1, n), 300, 1500) * np.exp(-t / 0.05) * 0.4
    return x * 0.5


def heartbeat(bpm, beats, muffled=False, seed=7):
    period = 60.0 / bpm
    n = int((beats * period + 0.6) * SR)
    out = np.zeros(n)
    for k in range(beats):
        for dt, f, g in ((0.0, 58.0, 1.0), (0.22, 64.0, 0.7)):
            th = A.sfx_thump(f, 0.30) * g
            i = int((k * period + dt) * SR)
            out[i:i + len(th)] += th[:n - i]
    if muffled:
        out = A.lp(out, 260, order=4) * 1.6
    return out


def pop(freq=900.0, seed=8):
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    f = freq * (1.6 - 0.6 * np.exp(-t / 0.01))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.025) * 0.35


def sparks(dur, seed=9, rate=18.0):
    n = int(dur * SR)
    out = np.zeros(n)
    rng = np.random.default_rng(seed)
    t = 0.0
    while t < dur:
        t += rng.exponential(1.0 / rate)
        i = int(t * SR)
        b = A.sfx_blip(rng.uniform(2400, 5200), 0.03) * rng.uniform(0.3, 1.0)
        if i + len(b) < n:
            out[i:i + len(b)] += b
    return out


# --------------------------------------------------------------------------- music

def build_music(T: Timeline, dur: float):
    c = cues(T)
    sc = c["sc"]
    m = A.Track(dur)
    ir = A.make_ir(4.2, damp=4200, seed=63)
    plan = [
        (0.0, ["E2", "B2", "G3", "F#4"], 950, 0.45, 0.05),
        (sc["curve"] - 0.2, ["C2", "G2", "E3", "B3"], 1200, 0.48, 0.6),
        (sc["chain"] - 0.2, ["G2", "D3", "B3", "A4"], 1500, 0.48, 0.6),
        (sc["dna"] - 0.2, ["E2", "B2", "G3", "D4", "F#4"], 1400, 0.50, 0.5),
        (sc["clock"] - 0.2, ["A1", "E2", "G2", "C3", "E3"], 1200, 0.50, 0.6),
        (c["L07"] - 0.2, ["C2", "G2", "E3", "B3"], 1300, 0.48, 0.5),
        (c["L08"] - 0.2, ["D2", "A2", "F#3", "C4"], 1300, 0.48, 0.5),
        (c["L09"] - 0.2, ["E2", "B2", "G3", "D4"], 1300, 0.48, 0.5),
        (sc["lens"] - 0.2, ["C2", "G2", "E3", "B3", "D4"], 1700, 0.52, 0.8),
        (c["L12"] - 0.2, ["G1", "D2", "B2", "F#3", "A3"], 1500, 0.50, 0.6),
        (sc["outro"] - 0.2, ["B1", "F#2", "A2", "E3", "A3"], 1200, 0.52, 0.6),
    ]
    for i, (t0, notes, cut, g, att) in enumerate(plan):
        t1 = plan[i + 1][0] if i + 1 < len(plan) else dur
        x = A.pad_chord(notes, (t1 - t0) + 2.2, cutoff=cut, attack=att, release=2.0, seed=70 + i)
        m.add(t0, x, gain=g)
    m.add(0.0, A.stereo(A.drone(A.note_hz("E1") * 2, dur + 1.0, lfo=0.05)), gain=0.14)
    # sonified bomb curve: frequency follows the measured carbon-14 level while the chart is drawn
    ch = C14Chart()
    s0 = sc["curve"]
    up = [(s0 + (c["y1963"] + 0.2 - s0) * u, 1950 + 13.6 * u) for u in np.linspace(0, 1, 30)]
    t_dn0, t_dn1 = c["fade"] - 0.6, c["year_b"] + 0.6
    dn = [(t_dn0 + (t_dn1 - t_dn0) * u, 1963.6 + (2019.4 - 1963.6) * u) for u in np.linspace(0, 1, 60)]
    traj = up + [(c["y1963"] + 0.3, 1963.6), (t_dn0, 1963.6)] + dn
    times = np.array([p[0] for p in traj]) - s0
    freqs = np.array([330.0 * ch.level(p[1]) ** 1.0 for p in traj])
    tone_dur = t_dn1 - s0 + 1.2
    m.add(s0, A.stereo(curve_tone(times, freqs, tone_dur), 0.0, 0.3), gain=0.30)
    # crystalline arpeggio while the helix assembles
    arp = ["E5", "B5", "G5", "D6", "F#6", "B5", "G5", "E6"]
    t_ = c["locks"]
    k = 0
    while t_ < c["dna"] + 0.2:
        m.add(t_, A.pluck(A.note_hz(arp[k % len(arp)]), 1.6, bright=0.5, decay=0.5), gain=0.16, pan=-0.4 + 0.1 * (k % 8))
        t_ += 0.16
        k += 1
    # wonder: rising plucks for the lens
    for j, nm in enumerate(("G4", "B4", "D5", "F#5", "A5")):
        m.add(c["lens"] - 0.1 + j * 0.42, A.pluck(A.note_hz(nm), 2.6, bright=0.3, decay=1.0), gain=0.18,
              pan=-0.3 + 0.15 * j)
    m.buf = A.reverb(m.buf, ir, wet=0.42)
    # the world holds its breath for "right now"
    m.buf = A.dip(m.buf, c["now"] + 0.25, 1.2, depth_db=-9)
    return m


# --------------------------------------------------------------------------- SFX

def build_sfx(T: Timeline, dur: float):
    c = cues(T)
    sc = c["sc"]
    s = A.Track(dur)
    ir = A.make_ir(2.4, damp=6000, seed=65)
    # the clock: one soft tick per second in the hook, the clock scene and the outro (loop-safe: whole seconds)
    for k in range(int(dur)):
        tt = float(k)
        inside = tt < sc["bomb"] - 0.2 or (c["clock"] - 0.2 <= tt < sc["body"]) or tt >= sc["outro"] - 0.1
        if inside:
            s.add(tt, tick(3000 if k % 2 else 2600, seed=k % 5), gain=0.30, pan=-0.15 if k % 2 else 0.15)
    s.add(0.0, A.sfx_boom(2.2, 64, 26, seed=66), gain=0.32)
    # the seconds ring sweeping round the iris on "timestamp"
    s.add(c["timestamp"] - 0.1, A.stereo(A.sfx_ruler(30, 1.3, 2600, 4200), 0.2), gain=0.20)
    # into the reflection
    s.add(c["L01end"] - 0.3, A.sfx_whoosh(0.9, 400, 5200, seed=67, peak=0.75), gain=0.32)
    # detonation: flash first, the boom arrives a beat later
    t0 = sc["bomb"] + 0.10
    s.add(t0, flash_burst(seed=68), gain=0.45)
    s.add(t0 + 0.42, A.sfx_boom(4.0, 70, 18, seed=69), gain=0.95)
    s.add(t0 + 0.42, A.sfx_rumble(5.0, seed=70), gain=0.65)
    n = int(5.5 * SR)
    roar = A.sweep_filter(np.random.default_rng(71).normal(0, 1, n), 200, 1600, "lowpass", q=0.7, block=4096,
                          curve="lin") * A.env_adsr(n, 0.8, 0.5, 0.7, 2.5, 0.7)
    s.add(t0 + 0.5, A.stereo(roar * 0.5, 0.0, 0.6), gain=0.45)
    # the years tick by with distant flashes
    y0, y1 = c["L02"], c["sixties"] + 1.2
    for k in range(11):
        tt = y0 + (y1 - y0) * k / 10
        s.add(tt, tick(4200, seed=k), gain=0.22, pan=-0.6)
        if k % 2 == 1:
            s.add(tt + 0.25, A.sfx_thump(44, 0.5), gain=0.18, pan=0.5 - 0.1 * k)
    # nearly doubled: the gauge fills
    s.add(c["nearly"], A.sfx_riser(c["doubled"] + 0.5 - c["nearly"], 300, 1400, seed=72), gain=0.22)
    s.add(c["doubled"] + 0.45, A.sfx_chime(("E6", "B6"), 0.07, 1.4), gain=0.20)
    # radioactive carbon: Geiger clicks rising into the air
    s.add(c["radioactive"] - 0.1, A.stereo(geiger(sc["curve"] - c["radioactive"] + 0.6, seed=73), 0.25, 0.5),
          gain=0.38)
    s.add(c["air"] - 0.2, A.sfx_whoosh(1.2, 300, 3200, seed=74), gain=0.25)
    # the chart: treaty stamp, a ping per year marker
    s.add(c["banned"] - 0.08, A.sfx_thump(80, 0.4), gain=0.5)
    s.add(c["banned"] - 0.08, A.sfx_tick(650, 0.14, seed=75), gain=0.45)
    t_dn0, t_dn1 = c["fade"] - 0.6, c["year_b"] + 0.6
    for k, yr in enumerate((1970, 1980, 1990, 2000, 2010, 2019)):
        u = (yr - 1963.6) / (2019.4 - 1963.6)
        # the drawing is eased; place the ping where the line passes the year (approximate inverse)
        uu = math.acos(1 - 2 * u) / math.pi if u < 1 else 1.0
        s.add(t_dn0 + (t_dn1 - t_dn0) * uu + 0.08, A.sfx_ping(1760 - 90 * k, 0.6, 0.12), gain=0.16, pan=-0.3 + 0.12 * k)
    # air -> leaf -> animal -> you
    s.add(c["plants"] - 0.1, A.stereo(rustle(1.6, seed=76), -0.2, 0.6), gain=0.35)
    pent = ["E6", "G6", "A6", "B6", "D7"]
    for k in range(9):
        s.add(c["breathed"] + k * 0.13, A.sfx_blip(A.note_hz(pent[k % 5]), 0.06), gain=0.12, pan=-0.5 + 0.12 * k)
    s.add(c["animals"] - 0.45, A.sfx_whoosh(0.8, 400, 2400, seed=77), gain=0.22, pan=0.4)
    s.add(c["so4"] - 0.45, A.sfx_whoosh(0.8, 400, 2400, seed=78), gain=0.22, pan=0.4)
    s.add(c["you4"], A.sfx_chime(("B5", "E6", "G6"), 0.08, 1.8), gain=0.22)
    # a cell divides; zoom into the nucleus; the lock clicks shut
    s.add(sc["dna"] - 0.3, A.sfx_whoosh(0.7, 3000, 300, seed=79), gain=0.25)
    s.add(c["new"] + 0.4, squelch(seed=80), gain=0.40)
    s.add(c["locks"] - 0.35, A.sfx_whoosh(0.6, 500, 4200, seed=81, peak=0.7), gain=0.25)
    s.add(c["level"] - 0.1, A.sfx_zip(0.5, 800, 3200, seed=82), gain=0.22)
    s.add(c["dna"] + 0.05, A.sfx_tick(1200, 0.08, seed=83), gain=0.55)
    s.add(c["dna"] + 0.05, A.sfx_thump(90, 0.3), gain=0.40)
    # the clock: card, reading the sample, the curve curls into a dial
    s.add(c["stockholm"] - 0.15, A.sfx_blip(1760, 0.07), gain=0.20)
    s.add(c["scientists"], A.sfx_zip(0.6, 600, 2600, seed=84), gain=0.18)
    s.add(c["clock"] - 0.3, A.sfx_whoosh(1.0, 600, 3400, seed=85), gain=0.22)
    s.add(c["clock"] + 0.6, A.sfx_chime(("A5", "E6", "A6"), 0.10, 2.2), gain=0.26)
    # body: fat cells renew (pops), the heart beats, the cortex sparks
    for k in range(5):
        s.add(c["L07"] + 0.6 + k * 0.85, pop(700 + 120 * k, seed=k), gain=0.25, pan=0.4)
    s.add(c["L08"] - 0.1, heartbeat(66, 3, seed=86), gain=0.75)
    s.add(c["L09"] - 0.1, A.stereo(sparks(3.2, seed=87), 0.3, 0.6), gain=0.18)
    s.add(c["L09"] - 0.1, A.stereo(A.sfx_shimmer(3.0, "E6", seed=88), 0.2, 0.6), gain=0.25)
    # the lens: x-ray shimmer, a muffled heartbeat from before birth, a bell for "right now"
    s.add(sc["lens"] - 0.25, A.sfx_whoosh(0.7, 2600, 400, seed=89), gain=0.22)
    s.add(c["lens"] - 0.2, A.stereo(A.sfx_shimmer(2.4, "B6", seed=90), 0.0, 0.6), gain=0.30)
    s.add(c["L11end"] + 0.08, heartbeat(140, 3, muffled=True, seed=91), gain=0.55)     # in the pause after "born"
    s.add(c["L12"] - 0.35, A.sfx_whoosh(0.8, 300, 2800, seed=92), gain=0.22)
    s.add(c["now"], A.sfx_chime(("E6", "B6", "E7"), 0.12, 2.6), gain=0.30)
    # back to the eye, into the loop
    s.add(sc["outro"] - 0.3, A.sfx_whoosh(0.9, 3200, 300, seed=93), gain=0.22)
    s.add(c["because"] - 0.4, A.sfx_riser(dur - c["because"] + 0.45, 160, 1300, seed=94), gain=0.24)
    s.add(dur - 0.85, A.sfx_reverse_swell(0.87), gain=0.30)
    s.buf = A.reverb(s.buf, ir, wet=0.16)
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
