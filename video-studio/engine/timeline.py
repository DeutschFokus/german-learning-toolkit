"""Narration -> timeline.

The timeline is the single source of truth for an episode's timing. Every
scene, caption and sound cue is anchored to line/word times in it, so a new
narration (AI or the creator's own recording) re-times the whole edit.

    build_ai(...)     synthesise each script line, align words, lay out pauses
    build_human(...)  align a creator recording to the script, cut it into
                      lines and lay those out on the same 60 s canvas. The
                      voice is never time-stretched: only the gaps between
                      lines move.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf

from . import markup
from .align import align


# --------------------------------------------------------------------------- layout

def layout(lines: list[dict], seg_lens: list[float], duration: float, lead_in: float,
           tail_min: float, tail_max: float = 1.4, floor: float | None = None) -> tuple[list[float], dict]:
    """Choose a start time for every line so the narration fills `duration`.

    Preferred pauses come from the script; they shrink toward `min_pause`
    when the read is long and grow (up to 1.6x) when it is short, with any
    remainder parked in the tail before the loop point.
    """
    speech = sum(seg_lens)
    pref = [l.get("pause_after", 0.3) for l in lines[:-1]]
    mins = [l.get("min_pause", 0.15) for l in lines[:-1]]
    room = duration - lead_in - tail_min - speech
    info = {"speech": speech, "room_for_pauses": room, "pref_pauses": sum(pref)}
    if room >= sum(pref):
        extra = room - sum(pref)
        flex = [0.0 if "pause_max" in l else p for l, p in zip(lines[:-1], pref)]
        grow = min(extra, 0.6 * sum(flex))
        pauses = [p + grow * f / max(1e-9, sum(flex)) for p, f in zip(pref, flex)]
        info["status"] = "fits"
    elif room >= sum(mins):
        k = (room - sum(mins)) / max(1e-9, sum(pref) - sum(mins))
        pauses = [m + k * (p - m) for p, m in zip(pref, mins)]
        info["status"] = "pauses tightened"
    elif floor is not None and room >= floor * len(mins):
        k = (room - floor * len(mins)) / max(1e-9, sum(mins) - floor * len(mins))
        pauses = [floor + k * (m - floor) for m in mins]
        info["status"] = "pauses compressed below script minimums"
    else:
        pauses = mins
        info["status"] = "OVERRUN: narration longer than the canvas even with minimum pauses"
    starts, t = [], lead_in
    for i, L in enumerate(seg_lens):
        starts.append(t)
        t += L + (pauses[i] if i < len(pauses) else 0)
    info["speech_end"] = t
    info["tail"] = duration - t
    info["pauses"] = pauses
    return starts, info


def _place(lines, segs, words_rel, starts, sr, duration):
    total = max(duration, starts[-1] + len(segs[-1]) / sr + 0.05)
    out = np.zeros(int(round(total * sr)) + 1, dtype=np.float32)
    tl_lines = []
    for L, seg, wr, st in zip(lines, segs, words_rel, starts):
        i0 = int(round(st * sr))
        out[i0:i0 + len(seg)] += seg
        toks = markup.parse(L["text"])
        tok_times, wi = [], 0
        for tok in toks:
            n = len(tok.align)
            ws = wr[wi:wi + n]
            wi += n
            tok_times.append({"display": tok.display,
                              "start": round(st + ws[0]["start"], 3),
                              "end": round(st + ws[-1]["end"], 3)})
        tl_lines.append({"id": L["id"], "text": markup.display_text(L["text"]),
                         "start": round(st, 3), "end": round(st + len(seg) / sr, 3),
                         "caption": L.get("caption", True), "emphasis": L.get("emphasis", []),
                         "tokens": tok_times})
    return out, tl_lines


def _tighten_gaps(segs, words_rel, sr, need, keep=0.30, min_gap=0.42):
    """Shorten the longest silent gaps between words inside lines until `need` seconds are saved.

    Only the middle of a pause is removed (10 ms crossfade); the words themselves are untouched
    and keep their natural speed. Word times after each cut shift left. Returns seconds saved.
    """
    cands = []
    for i, ws in enumerate(words_rel):
        for j in range(len(ws) - 1):
            g = ws[j + 1]["start"] - ws[j]["end"]
            if g > min_gap:
                cands.append((g, i, j))
    cands.sort(reverse=True)
    saved, cuts = 0.0, {}
    for g, i, j in cands:
        if saved >= need:
            break
        cut = min(g - keep, need - saved)
        a = words_rel[i][j]["end"] + (g - cut) / 2
        cuts.setdefault(i, []).append((a, a + cut))
        saved += cut
    f = int(0.01 * sr)
    for i, ivs in cuts.items():
        seg = segs[i]
        for a, b in sorted(ivs, reverse=True):
            ia, ib = int(a * sr), int(b * sr)
            head, tail = seg[:ia].copy(), seg[ib:].copy()
            if len(head) > f and len(tail) > f:
                head[-f:] *= np.linspace(1, 0, f)
                tail[:f] *= np.linspace(0, 1, f)
            seg = np.concatenate([head, tail])
            for w in words_rel[i]:
                if w["start"] >= b - 1e-6:
                    w["start"] -= (b - a)
                    w["end"] -= (b - a)
        segs[i] = seg
    return saved


def _word_fix(ws: list[dict], seg_len: float) -> list[dict]:
    """Clamp aligner output into the segment and keep it monotonic."""
    prev = 0.0
    for w in ws:
        w["start"] = max(prev, min(w["start"], seg_len))
        w["end"] = max(w["start"] + 0.04, min(w["end"], seg_len))
        prev = w["start"]
    return ws


# --------------------------------------------------------------------------- AI voice

def build_ai(script_path: Path, out_dir: Path, max_tries: int = 4) -> Path:
    from .tts import Narrator
    script = json.loads(Path(script_path).read_text())
    v = script["voice"]
    speed = v.get("speed", 1.0)
    nar = Narrator(v["blend"], speed=speed, lang=v.get("lang", "en-us"))
    for attempt in range(max_tries):
        segs, words_rel = [], []
        for L in script["lines"]:
            a = nar.say(markup.spoken_text(L["text"]), speed=speed)
            segs.append(a)
            ws = align(a, nar.sr, markup.align_words(L["text"]))
            words_rel.append(_word_fix(ws, len(a) / nar.sr))
        lens = [len(s) / nar.sr for s in segs]
        starts, info = layout(script["lines"], lens, script["duration"], script.get("lead_in", 0.1),
                              script.get("tail_min", 0.6))
        print(f"[timeline] speed={speed:.3f} speech={info['speech']:.2f}s status={info['status']} "
              f"tail={info['tail']:.2f}s")
        if not info["status"].startswith("OVERRUN"):
            break
        speed *= 1.03  # an AI read may be nudged; a human read never is
    audio, tl_lines = _place(script["lines"], segs, words_rel, starts, nar.sr, script["duration"])
    out_dir.mkdir(parents=True, exist_ok=True)
    wav = out_dir / "narration_ai.wav"
    sf.write(wav, audio, nar.sr, subtype="PCM_16")
    tl = {"source": "ai", "voice": wav.name, "sample_rate": nar.sr, "duration": script["duration"],
          "fps": script["fps"], "speed": speed, "layout": info, "scenes": script["scenes"],
          "lines": tl_lines}
    p = out_dir / "timeline_ai.json"
    p.write_text(json.dumps(tl, indent=1))
    return p


# --------------------------------------------------------------------------- human voice

def build_human(script_path: Path, voice_path: Path, out_dir: Path) -> Path:
    """Align a full recording of the script, cut it per line, re-lay it out."""
    script = json.loads(Path(script_path).read_text())
    audio, sr = sf.read(voice_path, dtype="float32", always_2d=False)
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    words_all, owner = [], []
    for i, L in enumerate(script["lines"]):
        w = markup.align_words(L["text"])
        words_all += w
        owner += [i] * len(w)
    ws = align(audio, sr, words_all)
    segs, words_rel = [], []
    n = len(script["lines"])
    pad_in, pad_out = 0.06, 0.12
    for i, L in enumerate(script["lines"]):
        mine = [w for w, o in zip(ws, owner) if o == i]
        t0 = max(0.0, mine[0]["start"] - pad_in)
        t1 = min(len(audio) / sr, mine[-1]["end"] + pad_out)
        if i + 1 < n:  # never bleed into the next line's first word
            nxt = next(w for w, o in zip(ws, owner) if o == i + 1)
            t1 = min(t1, max(mine[-1]["end"], nxt["start"] - 0.02))
        seg = audio[int(t0 * sr):int(t1 * sr)].copy()
        f = int(0.01 * sr)  # 10 ms fades kill clicks at the cut points
        seg[:f] *= np.linspace(0, 1, f)
        seg[-f:] *= np.linspace(1, 0, f)
        segs.append(seg)
        words_rel.append(_word_fix([{"word": w["word"], "start": w["start"] - t0, "end": w["end"] - t0}
                                    for w in mine], len(seg) / sr))
    lead_in, tail_min = script.get("lead_in", 0.1), script.get("tail_min", 0.6)
    lens = [len(s) / sr for s in segs]
    starts, info = layout(script["lines"], lens, script["duration"], lead_in, tail_min)
    print(f"[timeline/human] speech={info['speech']:.2f}s status={info['status']} tail={info['tail']:.2f}s")
    if info["status"].startswith("OVERRUN"):
        # 1) shorten long silences *inside* lines (between words) — never the speech itself
        need = tail_min - info["tail"]
        saved = _tighten_gaps(segs, words_rel, sr, need)
        lens = [len(s) / sr for s in segs]
        starts, info = layout(script["lines"], lens, script["duration"], lead_in, tail_min)
        print(f"[timeline/human] tightened in-line pauses by {saved:.2f}s -> status={info['status']} "
              f"tail={info['tail']:.2f}s")
    if info["status"].startswith("OVERRUN"):
        # 2) give up most of the loop tail, 3) let pauses between lines go below the script minimums
        tail_min = 0.25
        starts, info = layout(script["lines"], lens, script["duration"], lead_in, tail_min, floor=0.12)
        print(f"[timeline/human] shorter loop tail + compressed line pauses -> status={info['status']} "
              f"tail={info['tail']:.2f}s")
    if info["status"].startswith("OVERRUN"):
        over = tail_min - info["tail"]
        longest = sorted(script["lines"], key=lambda L: -len(markup.spoken_text(L["text"]).split()))[:3]
        print(f"[timeline/human] WARNING: the read is {over:.2f}s longer than the 60 s canvas allows. "
              f"The video will run {script['duration'] + over:.2f}s rather than speed your voice up. "
              f"To land exactly on 60 s, re-record a slightly tighter read or trim words from the longest "
              f"lines: {', '.join(L['id'] for L in longest)}.")
    info["tail_min_used"] = tail_min
    out, tl_lines = _place(script["lines"], segs, words_rel, starts, sr, script["duration"])
    out_dir.mkdir(parents=True, exist_ok=True)
    wav = out_dir / "narration_human.wav"
    sf.write(wav, out, sr, subtype="PCM_24")
    duration = script["duration"]
    if info["status"].startswith("OVERRUN"):
        duration = round(info["speech_end"] + tail_min, 2)
    tl = {"source": "human", "voice": wav.name, "sample_rate": sr, "duration": duration,
          "fps": script["fps"], "layout": info, "scenes": script["scenes"], "lines": tl_lines}
    p = out_dir / "timeline_human.json"
    p.write_text(json.dumps(tl, indent=1))
    return p


# --------------------------------------------------------------------------- lookups

@dataclass
class Span:
    start: float
    end: float

    @property
    def mid(self):
        return 0.5 * (self.start + self.end)


class Timeline:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.data = json.loads(self.path.read_text())
        self.duration = self.data["duration"]
        self.fps = self.data["fps"]
        self._lines = {l["id"]: l for l in self.data["lines"]}

    def line(self, lid: str) -> Span:
        l = self._lines[lid]
        return Span(l["start"], l["end"])

    def word(self, lid: str, key: int | str) -> Span:
        toks = self._lines[lid]["tokens"]
        if isinstance(key, int):
            t = toks[key]
        else:
            k = key.lower().strip(".,:;!?…'\"")
            t = next(t for t in toks if t["display"].lower().strip(".,:;!?…'\"") == k)
        return Span(t["start"], t["end"])

    def scene_starts(self, lead: float = 0.22) -> list[tuple[str, float]]:
        out = []
        for i, sc in enumerate(self.data["scenes"]):
            t = 0.0 if i == 0 else max(0.0, self.line(sc["first_line"]).start - lead)
            out.append((sc["id"], t))
        return out

    @property
    def lines(self):
        return self.data["lines"]
