"""Creative direction for "Der Brief": score, sound design and shot list.

Everything is timed from the voiceover timeline, so re-recording a line keeps
music hits, knocks and camera moves in sync.
"""
import numpy as np

from storyvid import sfx
from storyvid.common import SR, butter, db, place
from storyvid.music import BASS, OSTINATO, PAD, Part, n

# Bus levels (dB) and ducking depth under speech. Narration must stay clearly on top:
# language learners are listening to every word.
LEVELS = {"music": -9.5, "ambience": -16.0, "sfx": -4.0,
          "duck_music": -9.0, "duck_ambience": -6.0, "duck_sfx": -5.0}

# ============================================================================ music


def compose_music(tl):
    rng = np.random.default_rng(42)
    piano = Part(0, "piano")
    strings = Part(49, "strings")      # String Ensemble 2 (slow attack)
    cello = Part(42, "cello")
    celesta = Part(8, "celesta")
    bar = 60 / 72 * 4
    e8 = bar / 8

    def hum(t):
        return t + rng.normal(0, 0.008)

    def pedal(t):
        piano.cc(t - 0.03, 64, 0)
        piano.cc(t + 0.02, 64, 127)

    def ostinato(t0, chord, vel, top_accent=6):
        for k, p in enumerate(OSTINATO[chord]):
            v = vel + (top_accent if k == 4 else 0) + rng.integers(-4, 5)
            piano.note(hum(t0 + k * e8), e8 * 2.2, p, v)
        piano.note(t0, bar * 1.05, BASS[chord], vel + 4)
        piano.note(t0 + 0.01, bar * 1.05, n(BASS[chord]) + 12, vel - 6)
        pedal(t0)

    def pad(t0, chord, dur, vel=58, extra=()):
        for p in PAD[chord] + list(extra):
            strings.note(t0, dur, p, vel)

    def melody(t0, notes, vel=50):
        for b, l, p in notes:
            piano.note(hum(t0 + b * bar / 4), l * bar / 4, p, vel + rng.integers(-3, 4))

    # ---- hook: low drone, sparse piano, a low hit right after "Ihm selbst." ----
    hit = tl.t("L04.end+0.05")
    strings.cc(0.0, 11, 18)
    strings.ramp(0.3, hit - 0.2, 11, 18, 78)
    for p in ("D2", "A2", "D3"):
        strings.note(0.3, hit - 0.15, p, 62)
    for at, p, v in ((0.9, "D4", 40), (tl.t("L02.start"), "A4", 44), (tl.t("L02.end"), "F4", 36),
                     (tl.t("L03.start+0.2"), "E4", 34), (tl.t("L03.w3.start"), "F4", 33),
                     (tl.t("L03.w6.start"), "E4", 33), (tl.t("L03.end+0.25"), "C#4", 38)):
        pedal(at)
        piano.note(at, 3.0, p, v)
    pedal(hit)
    for p, v in (("D1", 78), ("D2", 72), ("A2", 52)):
        piano.note(hit, 4.5, p, v)
    piano.cc(hit + 4.0, 64, 0)

    # ---- section A: fourteen years ... no "but" ----
    a0 = tl.t("L05.start-1.5")
    chords_a = ["Dm", "Bb", "F", "C", "Dm", "Bb", "Gm", "A"]
    for i, ch in enumerate(chords_a):
        ostinato(a0 + i * bar, ch, 36 + (i // 2) * 2)
    cello.cc(a0, 11, 40)
    cello.ramp(a0 + 2 * bar, a0 + 8 * bar, 11, 40, 90)
    for i, ch in enumerate(chords_a[2:], start=2):
        cello.note(a0 + i * bar, bar * 1.02, n(BASS[ch]) + (12 if ch in ("Gm", "A", "Bb") else 0), 52)
    strings.cc(a0 + 4 * bar - 0.1, 11, 30)
    strings.ramp(a0 + 4 * bar, a0 + 8 * bar, 11, 30, 92)
    for i, ch in enumerate(chords_a[4:], start=4):
        pad(a0 + i * bar, ch, bar * 1.02, 60)
    melody(a0 + 4 * bar, [(0, 2, "A4"), (2, 1, "F5"), (3, 1, "E5")], 50)
    melody(a0 + 5 * bar, [(0, 3, "D5"), (3, 1, "C5")], 48)
    melody(a0 + 6 * bar, [(0, 2, "Bb4"), (2, 1, "D5"), (3, 1, "C5")], 50)
    melody(a0 + 7 * bar, [(0, 4, "C#5")], 52)
    a9 = a0 + 8 * bar
    pad(a9, "A", bar * 0.9, 56, extra=("E2",))
    strings.ramp(a9, a9 + bar * 0.9, 11, 92, 20)
    pedal(a9)
    piano.note(a9, bar, "A1", 50)
    piano.note(a9, bar, "A2", 44)
    piano.cc(a9 + bar, 64, 0)

    # ---- flashback: celesta memory theme over a high string halo ----
    f0 = a0 + 9 * bar
    fb_end = tl.t("L14.end+0.6")
    knock_t = tl.t("L12.w8.start")
    celesta.cc(f0, 11, 100)
    theme = [(0, "A5", 2), (2, "F5", 1), (3, "E5", 1), (4, "D5", 3), (7, "C5", 1),
             (8, "Bb4", 2), (10, "D5", 1), (11, "C5", 1), (12, "C#5", 4)]
    beat = bar / 4
    for b, p, l in theme:
        t = f0 + 0.6 + b * beat * 1.15
        if knock_t - 0.6 < t < knock_t + 1.8:
            continue
        celesta.note(t, l * beat * 1.1, p, 46)
    strings.cc(f0, 11, 25)
    strings.ramp(f0, f0 + 2 * bar, 11, 25, 55)
    strings.note(f0, fb_end - f0, "A5", 34)
    strings.note(f0, fb_end - f0, "D5", 30)
    strings.ramp(fb_end - 1.6, fb_end, 11, 55, 10)
    cello.cc(f0, 11, 60)
    cello.note(f0, fb_end - f0 + 0.5, "D2", 46)
    cello.ramp(fb_end - 1.5, fb_end + 0.5, 11, 60, 0)

    # ---- section B: glorified hurt ... had its price ----
    b0 = tl.t("L15.start+0.4")
    chords_b = ["Dm", "Bb", "F", "C", "Gm", "Bb"]
    for i, ch in enumerate(chords_b):
        ostinato(b0 + i * bar, ch, 38 + i * 3)
    cello.cc(b0 - 0.1, 11, 45)
    cello.ramp(b0, b0 + 6 * bar, 11, 45, 88)
    for i, ch in enumerate(chords_b):
        cello.note(b0 + i * bar, bar * 1.02, n(BASS[ch]) + 12, 54 + i * 3)
    strings.cc(b0 + 2 * bar - 0.1, 11, 35)
    strings.ramp(b0 + 2 * bar, b0 + 6 * bar, 11, 35, 96)
    for i, ch in enumerate(chords_b[2:], start=2):
        pad(b0 + i * bar, ch, bar * 1.02, 64 + i * 3)
    melody(b0 + 2 * bar, [(0, 2, "A4"), (2, 1, "C5"), (3, 1, "F5")], 52)
    melody(b0 + 3 * bar, [(0, 3, "E5"), (3, 1, "G5")], 54)
    melody(b0 + 4 * bar, [(0, 2, "G5"), (2, 1, "F5"), (3, 1, "D5")], 56)
    melody(b0 + 5 * bar, [(0, 2, "F5"), (2, 2, "D5")], 56)
    peak = tl.t("L18.end+0.08")       # right after "... einen Preis."
    pad(peak - 0.1, "A", 2.6, 84, extra=("A4", "E2"))
    strings.cc(peak - 0.15, 11, 112)
    strings.ramp(peak + 0.3, peak + 2.4, 11, 112, 0)
    pedal(peak - 0.1)
    for p, v in (("A1", 66), ("A2", 58), ("E3", 46), ("C#4", 44)):
        piano.note(peak - 0.1, 3.5, p, v)
    piano.cc(peak + 3.0, 64, 0)

    # ---- phone call: almost nothing ----
    p0 = tl.t("L19.start+0.6")
    silent = tl.t("L23.start")
    strings.cc(p0 - 0.1, 11, 0)
    strings.ramp(p0, p0 + 3.0, 11, 0, 46)
    for p in ("D3", "A3", "E4", "F4"):
        strings.note(p0, silent - p0 + 0.6, p, 50)
    strings.ramp(silent - 0.6, silent + 0.5, 11, 46, 0)
    br0 = tl.t("L25.start")
    br1 = tl.t("L25.end")
    strings.cc(br0 - 0.1, 11, 0)
    strings.ramp(br0, br1, 11, 0, 44)
    for p in ("D5", "A5"):
        strings.note(br0, br1 - br0 + 1.2, p, 34)
    strings.ramp(br1 + 0.2, br1 + 1.2, 11, 44, 0)

    # ---- ending: Bb - F - C, then D major exactly as the last word ends ----
    d_final = tl.t("L28.end+0.05")
    e0 = d_final - 3 * bar
    for i, ch in enumerate(["Bb", "F", "C"]):
        ostinato(e0 + i * bar, ch, 40 + i * 2)
    melody(e0, [(0, 2, "D5"), (2, 1, "F5"), (3, 1, "E5")], 52)
    melody(e0 + bar, [(0, 3, "C5"), (3, 1, "A4")], 50)
    melody(e0 + 2 * bar, [(0, 2, "G4"), (2, 1, "C5"), (3, 1, "E5")], 52)
    strings.cc(e0 - 0.1, 11, 40)
    strings.ramp(e0, d_final, 11, 40, 88)
    for i, ch in enumerate(["Bb", "F", "C"]):
        pad(e0 + i * bar, ch, bar * 1.02, 62)
    cello.cc(e0 - 0.1, 11, 55)
    for i, ch in enumerate(["Bb", "F", "C"]):
        cello.note(e0 + i * bar, bar * 1.02, n(BASS[ch]) + 12, 56)
    tail = tl.duration - d_final
    pedal(d_final)
    for p, v in (("D2", 52), ("D3", 46), ("A3", 42), ("F#4", 44), ("D5", 40), ("F#5", 50)):
        piano.note(d_final + (0.03 if p == "F#5" else 0), tail, p, v)
    pad(d_final, "D", tail, 64, extra=("D5",))
    strings.ramp(d_final + 1.0, tl.duration - 0.3, 11, 88, 0)
    cello.note(d_final, tail, "D2", 54)
    cello.ramp(d_final + 1.0, tl.duration - 0.3, 11, 60, 0)
    return {"piano": piano, "strings": strings, "cello": cello, "celesta": celesta}


def music_fx(tl):
    """Per-stem processing hints and the flashback window (stems get muffled there)."""
    return {
        "reverb": {"piano": 0.32, "strings": 0.42, "cello": 0.36, "celesta": 0.55},
        "gain_db": {"piano": 0.0, "strings": -2.0, "cello": -3.0, "celesta": -5.0},
        "muffle": [(tl.t("L10.end+0.3"), tl.t("L14.end+0.8"))],
    }


# ============================================================================ sound design


def sound_design(tl):
    """Return {'ambience': stereo, 'sfx': stereo} buses for the whole timeline."""
    dur = tl.duration
    N = int(dur * SR) + SR
    amb = np.zeros((N, 2), np.float32)
    fx = np.zeros((N, 2), np.float32)
    t = np.arange(N) / SR

    fb0, fb1 = tl.t("L10.end+0.35"), tl.t("L14.end+0.9")

    # rain: interior bed always, exterior storm in the flashback
    inner = sfx.rain(dur + 1, "interior", seed=1)[:N]
    outer = sfx.rain(dur + 1, "exterior", seed=2)[:N]
    x_in = np.clip((t - fb0) / 0.9, 0, 1) * np.clip((fb1 - t) / 0.9, 0, 1)
    g_in = (1 - 0.8 * x_in) * np.clip(t / 0.8, 0, 1) * np.clip((dur - t) / 4.5, 0, 1)
    amb += inner * g_in[:, None] * db(-3)
    amb += outer * x_in[:, None] * db(-2.5)
    amb += sfx.room_tone(dur + 1)[:N] * db(-40)

    # thunder
    place(fx, sfx.thunder("distant", seed=11), 0.0, db(-19))
    place(fx, sfx.thunder("close", seed=12), tl.t("L04.end+0.3"), db(-8))
    place(fx, sfx.boom(), tl.t("L04.end+0.05"), db(-12))
    place(fx, sfx.thunder("distant", seed=13), tl.t("L10.end+0.5"), db(-23))
    place(fx, sfx.thunder("distant", seed=14), tl.t("L18.end+0.25"), db(-18))

    # the archive clock (time passing)
    for a, b in ((tl.t("L05.start-1.0"), tl.t("L06.end+0.6")), (tl.t("L17.start-0.4"), tl.t("L18.end-0.3"))):
        c = sfx.clock(b - a + 1.0)
        env = np.clip(np.arange(len(c)) / SR / 1.5, 0, 1) * np.clip((b - a - np.arange(len(c)) / SR) / 1.5, 0, 1)
        place(fx, butter(c * env, "low", 6000), a, db(-33))

    # into and out of the memory
    place(fx, sfx.whoosh(1.7, reverse=True, seed=21), fb0 - 1.45, db(-9))
    place(fx, sfx.whoosh(1.5, reverse=False, seed=22), fb1 - 0.5, db(-14))

    # the timid knocking: two soft knocks, a pause, one softer
    k0 = tl.t("L12.end+0.05")
    for i, (dt, s) in enumerate(((0.0, 0.85), (0.29, 0.7), (1.25, 0.5))):
        k = sfx.knock(s, seed=30 + i)
        k = butter(k, "low", 4200)
        place(fx, k, k0 + dt, db(-6))
        # stairwell echo
        place(fx, butter(k, "low", 1500) * 0.35, k0 + dt + 0.11, db(-9))
        place(fx, butter(k, "low", 900) * 0.2, k0 + dt + 0.27, db(-9))

    # phone: ringback twice, pickup, open line
    r1 = tl.t("L19.end+0.25")
    place(fx, sfx.ringback(1.0), r1, db(-29))
    place(fx, sfx.ringback(1.0), r1 + 3.05, db(-29))
    pick = r1 + 4.4
    place(fx, sfx.pickup_click(), pick, db(-24))
    line_end = tl.t("L25.end+0.7")
    ln = sfx.line_noise(line_end - pick)
    env = np.clip(np.arange(len(ln)) / SR / 0.05, 0, 1) * np.clip((line_end - pick - np.arange(len(ln)) / SR) / 0.6, 0, 1)
    place(fx, ln * env, pick, db(-20))

    # held breath: a heartbeat in the brother's silence
    s0 = tl.t("L23.end+0.35")
    for i in range(2):
        place(fx, butter(sfx.heartbeat(), "low", 300), s0 + i * 0.95, db(-12 - 2 * i))

    # the letter laid down
    place(fx, sfx.paper(1.15), tl.t("L27.w1.start-0.05"), db(-15))
    return {"ambience": amb[: int(dur * SR)], "sfx": fx[: int(dur * SR)]}


# ============================================================================ shots

# The opening frames the boys' photo at the bottom of the picture, so the first
# subtitles sit at the top of the frame instead.
CAPTIONS_TOP = ("L01", "L02")
#
# Camera keys: cx, cy = point of the source image at the frame centre (0..1),
# z = zoom (1 = image width fills the frame), rot in degrees,
# px/py/dolly = depth parallax (output pixels at one unit of depth from d0).
# A push-in animates dolly from + to - (near objects grow faster than far ones).


def shots(tl):
    T = tl.t
    s2, s3, s4 = T("L04.end+2.3"), T("L06.end+0.15"), T("L10.end+0.12")
    s5, s6, s7 = T("L14.end+0.2"), T("L16.end+0.1"), T("L18.end+0.5")
    s7b, s8 = T("L22.end+0.3"), T("L25.end+0.35")
    k0 = T("L12.end+0.05")
    return [
        # 1 - hook: the boys' photo, the note, then up to his face. "Ihm selbst." + lightning
        dict(image=1, start=0.0, end=s2 + 1.2, fade_in=0.3,
             cam=[dict(t=0.0, cx=0.64, cy=0.80, z=2.22, d0=0.5, dolly=0.03, py=0),
                  dict(t=T("L03.start"), cx=0.62, cy=0.79, z=2.12, dolly=-0.02),
                  dict(t=T("L04.start-0.15"), cx=0.47, cy=0.30, z=1.72, py=34, dolly=0.0),
                  dict(t=s2 + 1.2, cx=0.46, cy=0.285, z=1.86, py=40, dolly=-0.03)],
             dof=[dict(t=0.0, focus=0.7, ap=0.5), dict(t=T("L03.start+1.0"), focus=0.7, ap=0.6),
                  dict(t=T("L04.start-0.3"), focus=0.21, ap=0.8)],
             exp=[dict(t=0.0, ev=0.0), dict(t=T("L04.end+0.35"), ev=0.0), dict(t=T("L04.end+1.4"), ev=-1.3)],
             fx=dict(glass_rain=0.9, flicker=0.05, dust=70, bloom=0.35, lightning=[T("L04.end+0.2")])),
        # 2 - fourteen years of his version: push towards him at the window
        dict(image=3, start=s2, end=s3 + 1.0, fade_in=1.2,
             cam=[dict(t=s2, cx=0.5, cy=0.5, z=1.06, d0=0.08, dolly=0.05, px=-12),
                  dict(t=s3 + 1.0, cx=0.56, cy=0.37, z=1.5, dolly=-0.05, px=12)],
             dof=[dict(t=s2, focus=0.08, ap=1.0)],
             fx=dict(glass_rain=1.0, flicker=0.05, dust=90, bloom=0.4)),
        # 3 - the letter was unmistakable: over the desk, onto the envelopes
        dict(image=5, start=s3, end=s4 + 1.2, fade_in=1.0,
             cam=[dict(t=s3, cx=0.60, cy=0.56, z=2.0, d0=0.13, dolly=0.04, px=18),
                  dict(t=s4 + 1.2, cx=0.665, cy=0.59, z=2.55, dolly=-0.04, px=-18)],
             dof=[dict(t=s3, focus=0.13, ap=1.0)],
             fx=dict(glass_rain=0.7, flicker=0.05, dust=80, bloom=0.4)),
        # 4 - flashback: stairwell, soaked coat, timid knocking, the door stays shut
        dict(image=4, start=s4, end=s5 + 1.2, fade_in=1.2, trans="memory_in", grade="flashback",
             handheld=0.35, seed=7, shake=[(k0, 1.0), (k0 + 0.29, 0.8), (k0 + 1.25, 0.6)],
             cam=[dict(t=s4, cx=0.33, cy=0.62, z=1.55, d0=0.5, px=26),
                  dict(t=T("L12.start"), cx=0.34, cy=0.57, z=1.55),
                  dict(t=T("L12.w3.start"), cx=0.46, cy=0.48, z=1.52, px=8),
                  dict(t=T("L12.w6.start"), cx=0.62, cy=0.31, z=1.75, px=-8),
                  dict(t=T("L13.start"), cx=0.64, cy=0.30, z=1.86),
                  dict(t=T("L14.start"), cx=0.70, cy=0.34, z=1.95),
                  dict(t=s5 + 1.2, cx=0.76, cy=0.40, z=2.15, px=-24)],
             dof=[dict(t=s4, focus=0.5, ap=0.45)],
             fx=dict(outdoor_rain=1.0, flicker=0.09, bloom=0.5, lightning=[T("L10.end+0.75")])),
        # 5 - hurt turned into principle: into his face, a slight dutch angle
        dict(image=1, start=s5, end=s6 + 0.9, fade_in=1.2, trans="memory_out",
             cam=[dict(t=s5, cx=0.5, cy=0.45, z=1.1, d0=0.21, dolly=0.05, rot=0.0),
                  dict(t=s6 + 0.9, cx=0.465, cy=0.27, z=2.15, dolly=-0.05, rot=-1.6)],
             dof=[dict(t=s5, focus=0.21, ap=0.6)],
             fx=dict(glass_rain=0.9, flicker=0.05, dust=60, bloom=0.35)),
        # 6 - the price: pull back until he is small in the archive
        dict(image=5, start=s6, end=s7 + 1.2, fade_in=0.9,
             cam=[dict(t=s6, cx=0.53, cy=0.51, z=2.65, d0=0.12, dolly=-0.06),
                  dict(t=s7 + 1.2, cx=0.5, cy=0.5, z=1.04, dolly=0.06)],
             dof=[dict(t=s6, focus=0.12, ap=0.8)],
             fx=dict(glass_rain=0.9, flicker=0.05, dust=70, bloom=0.4, lightning=[T("L18.end+0.12")])),
        # 7a - the call
        dict(image=2, start=s7, end=s7b + 0.3, fade_in=1.2, handheld=0.5, seed=11,
             cam=[dict(t=s7, cx=0.52, cy=0.46, z=1.12, d0=0.29, dolly=0.04),
                  dict(t=s7b + 0.3, cx=0.55, cy=0.35, z=1.48, dolly=-0.04)],
             dof=[dict(t=s7, focus=0.29, ap=0.7)],
             fx=dict(glass_rain=1.0, flicker=0.04, bloom=0.35)),
        # 7b - close-up through the silence and the brother's answer
        dict(image=2, start=s7b, end=s8 + 1.3, fade_in=0.3, handheld=0.6, seed=13,
             cam=[dict(t=s7b, cx=0.56, cy=0.265, z=2.0, d0=0.29, dolly=0.02),
                  dict(t=s8 + 1.3, cx=0.545, cy=0.27, z=2.3, dolly=-0.03)],
             dof=[dict(t=s7b, focus=0.29, ap=1.2)],
             fx=dict(glass_rain=0.9, flicker=0.04, bloom=0.35)),
        # 8 - he lays the letter down: from him to the letter and the boys' photo
        dict(image=3, start=s8, end=tl.duration, fade_in=1.3, fade_out=3.2,
             cam=[dict(t=s8, cx=0.56, cy=0.30, z=1.95, d0=0.3, dolly=0.0),
                  dict(t=T("L27.start"), cx=0.56, cy=0.31, z=1.9),
                  dict(t=T("L27.end+0.5"), cx=0.58, cy=0.69, z=1.58, dolly=0.03),
                  dict(t=tl.duration, cx=0.6, cy=0.72, z=1.74, dolly=-0.02)],
             dof=[dict(t=s8, focus=0.08, ap=1.5), dict(t=T("L27.w1.start"), focus=0.08),
                  dict(t=T("L27.end+0.4"), focus=0.66)],
             exp=[dict(t=s8, ev=0.0, warmth=0.0), dict(t=T("L28.start"), ev=0.0, warmth=0.3),
                  dict(t=T("L28.end+0.5"), ev=0.08, warmth=1.0)],
             fx=dict(glass_rain=1.0, flicker=0.05, dust=90, bloom=0.45)),
    ]


def title_window(tl):
    return tl.t("L04.end+0.55"), tl.t("L05.start-0.15")


def handwriting(tl):
    """The note on the envelope, written word by word with L02."""
    return {"line": "L02", "text": ["Unter keinen Umständen", "antworten."], "y": 690,
            "fade": (tl.t("L03.start+0.3"), tl.t("L03.start+1.3"))}
