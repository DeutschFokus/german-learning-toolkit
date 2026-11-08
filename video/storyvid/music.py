"""Original score, composed against the story timeline and rendered with FluidSynth.

The cue sheet for "Der Brief": D minor, 72 BPM, piano ostinato + strings, a celesta
"memory" theme for the flashback, near-silence during the phone call, and a
D-major resolution that lands on the last word.
"""
import os
import subprocess

import mido
import numpy as np

from .common import SR, read_wav

SOUNDFONT_CANDIDATES = [
    "/usr/share/sounds/sf3/MuseScore_General_Full.sf3",
    "/usr/share/sounds/sf3/MuseScore_General.sf3",
    "/usr/share/sounds/sf2/FluidR3_GM.sf2",
]

NOTE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def n(name):
    """'C#4' -> 61, 'Bb2' -> 46."""
    base = NOTE[name[0]]
    i = 1
    while i < len(name) and name[i] in "#b":
        base += 1 if name[i] == "#" else -1
        i += 1
    return base + 12 * (int(name[i:]) + 1)


# 8th-note ostinato figures and bass notes per chord (voice-led around D3..A4)
OSTINATO = {
    "Dm": ["D3", "A3", "D4", "F4", "A4", "F4", "D4", "A3"],
    "Bb": ["D3", "F3", "Bb3", "D4", "F4", "D4", "Bb3", "F3"],
    "F":  ["C3", "F3", "A3", "C4", "F4", "C4", "A3", "F3"],
    "C":  ["C3", "G3", "C4", "E4", "G4", "E4", "C4", "G3"],
    "Gm": ["D3", "G3", "Bb3", "D4", "G4", "D4", "Bb3", "G3"],
    "A":  ["C#3", "E3", "A3", "C#4", "E4", "C#4", "A3", "E3"],
    "D":  ["D3", "A3", "D4", "F#4", "A4", "F#4", "D4", "A3"],
}
BASS = {"Dm": "D2", "Bb": "Bb1", "F": "F2", "C": "C2", "Gm": "G1", "A": "A1", "D": "D2"}
PAD = {"Dm": ["D3", "A3", "F4"], "Bb": ["D3", "Bb3", "F4"], "F": ["C3", "A3", "F4"],
       "C": ["C3", "G3", "E4"], "Gm": ["D3", "Bb3", "G4"], "A": ["C#3", "A3", "E4"],
       "D": ["D3", "A3", "F#4"]}


class Part:
    def __init__(self, program, name):
        self.program = program
        self.name = name
        self.notes = []   # (t, dur, note, vel)
        self.ccs = []     # (t, cc, value)

    def note(self, t, dur, pitch, vel):
        if isinstance(pitch, str):
            pitch = n(pitch)
        self.notes.append((float(t), float(dur), int(pitch), int(np.clip(vel, 1, 127))))

    def cc(self, t, num, val):
        self.ccs.append((float(t), int(num), int(np.clip(val, 0, 127))))

    def ramp(self, t0, t1, num, v0, v1, steps=24):
        for k in range(steps + 1):
            a = k / steps
            self.cc(t0 + (t1 - t0) * a, num, v0 + (v1 - v0) * a)

    def write_midi(self, path):
        tpb = 960  # tempo 60 BPM -> 1 beat = 1 s, so ticks = seconds * 960
        mid = mido.MidiFile(ticks_per_beat=tpb)
        tr = mido.MidiTrack()
        mid.tracks.append(tr)
        tr.append(mido.MetaMessage("set_tempo", tempo=1_000_000, time=0))
        tr.append(mido.Message("program_change", program=self.program, channel=0, time=0))
        tr.append(mido.Message("control_change", control=7, value=110, channel=0, time=0))
        ev = []
        for t, d, p, v in self.notes:
            ev.append((t, 1, mido.Message("note_on", note=p, velocity=v, channel=0)))
            ev.append((t + d, 0, mido.Message("note_off", note=p, velocity=0, channel=0)))
        for t, c, v in self.ccs:
            ev.append((t, 2, mido.Message("control_change", control=c, value=v, channel=0)))
        ev.sort(key=lambda e: (e[0], e[1]))
        cur = 0
        for t, _, msg in ev:
            tick = int(round(max(0.0, t) * tpb))
            msg.time = tick - cur
            cur = tick
            tr.append(msg)
        tr.append(mido.MetaMessage("end_of_track", time=tpb * 4))
        mid.save(path)


def render(parts, work, duration):
    sf = next((p for p in SOUNDFONT_CANDIDATES if os.path.exists(p)), None)
    if sf is None:
        raise RuntimeError("no soundfont found (apt install musescore-general-soundfont fluidsynth)")
    out = {}
    mdir = os.path.join(work, "music")
    os.makedirs(mdir, exist_ok=True)
    for name, part in parts.items():
        mid = os.path.join(mdir, f"{name}.mid")
        wav = os.path.join(mdir, f"{name}.wav")
        part.write_midi(mid)
        subprocess.run(["fluidsynth", "-ni", "-q", "-R", "0", "-C", "0", "-g", "0.9", "-r", str(SR),
                        "-F", wav, sf, mid], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        x = read_wav(wav, mono=False)
        if x.ndim == 1:
            x = np.stack([x, x], axis=1)
        nlen = int(duration * SR)
        if len(x) < nlen:
            x = np.concatenate([x, np.zeros((nlen - len(x), 2), np.float32)])
        out[name] = x[:nlen]
    return out
