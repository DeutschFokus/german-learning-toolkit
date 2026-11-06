#!/usr/bin/env python3
"""Generate the recording-ready human voiceover script from script.json + the AI timeline.

    python3 make_docs.py            -> ../human_voiceover_script.txt
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))

from engine import markup  # noqa: E402


def ts(t: float) -> str:
    m, s = divmod(max(0.0, t), 60)
    return f"{int(m):02d}:{s:05.2f}"


def pause_mark(p: float) -> str:
    if p <= 0:
        return ""
    if p < 0.4:
        return " /"
    if p < 0.8:
        return " //"
    return " ///"


def emphasise(text: str, emphasis: list[str]) -> str:
    keys = {e.lower().strip(".,:;!?…'\"") for e in emphasis}
    out = []
    for tok in markup.parse(text):
        spoken = " ".join(tok.spoken)
        key = tok.display.lower().strip(".,:;!?…'\"")
        out.append(spoken.upper() if key in keys else spoken)
    return " ".join(out)


def main():
    script = json.loads((HERE / "script.json").read_text())
    tl = json.loads((HERE / "build" / "timeline_ai.json").read_text())
    lines = {l["id"]: l for l in tl["lines"]}
    pauses = tl["layout"]["pauses"] + [0.0]
    scenes = {s["first_line"]: s["name"] for s in script["scenes"]}
    words = sum(len(markup.spoken_text(l["text"]).split()) for l in script["lines"])
    first, last = tl["lines"][0]["start"], tl["lines"][-1]["end"]
    o = []
    o.append(f"{script['episode'].upper()} — {script['title'].upper()}")
    o.append("Recording-ready voiceover script (deep, calm male narrator)")
    o.append("=" * 72)
    o.append(f"Video length: {script['duration']:.0f} s   |   Spoken words: {words}   |   "
             f"Narration window: {ts(first)} – {ts(last)}")
    o.append("")
    o.append("THE VOICE")
    o.append("  Intelligent, calm, quietly fascinated. Authority without lecturing; a close-mic,")
    o.append("  one-to-one conversation, not a trailer. Deep does not mean slow: keep momentum")
    o.append("  (about 165–175 words per minute inside sentences) and let the PAUSES do the drama.")
    o.append("  Let a slight smile in on the lighter lines. Never push or shout.")
    o.append("")
    o.append("MARKS")
    o.append("  CAPS      = lean on this word (pitch or weight, not volume)")
    o.append("  /         = short breath, about 0.2–0.4 s")
    o.append("  //        = beat, about 0.4–0.8 s")
    o.append("  ///       = let it land, 0.8 s or more")
    o.append("  ...       = suspend the pitch: the thought continues")
    o.append("")
    o.append("HOW TO RECORD")
    o.append("  1. Quiet, soft room (closet or duvet fort beats a bare room). Mic 15–20 cm away,")
    o.append("     slightly off-axis to avoid plosives. Peaks around -10 dBFS, never above -3.")
    o.append("  2. Record the whole script in one take as WAV (48 kHz, 24-bit, mono).")
    o.append("     Leave 2 s of silence at the start. Do a second full take if a line slips.")
    o.append("  3. The timings below are a GUIDE from the AI reference read, not a click track.")
    o.append("     Read naturally. The pipeline aligns your take word by word, keeps your voice")
    o.append("     at its natural speed, and re-times the scenes, captions and sound design to it.")
    o.append("  4. If your read runs long, the pipeline tightens the pauses first. If it still")
    o.append("     overruns 60 s it tells you which lines to trim; it never speeds your voice up.")
    o.append("  5. Then run:  python3 production/build.py human path/to/your_take.wav")
    o.append("")
    o.append("=" * 72)
    o.append("TIMED SCRIPT")
    o.append("=" * 72)
    for i, L in enumerate(script["lines"]):
        tlL = lines[L["id"]]
        if L["id"] in scenes:
            o.append("")
            o.append(f"--- SCENE: {scenes[L['id']].upper()} " + "-" * max(4, 56 - len(scenes[L['id']])))
        o.append("")
        o.append(f"[{ts(tlL['start'])} – {ts(tlL['end'])}]  {L['id']}")
        o.append(f"   {emphasise(L['text'], L.get('emphasis', []))}{pause_mark(pauses[i])}")
        if markup.display_text(L["text"]) != markup.spoken_text(L["text"]):
            o.append(f"   (on screen: \"{markup.display_text(L['text'])}\")")
        o.append(f"   Delivery: {L.get('delivery', '')}")
        if L.get("pronounce"):
            pr = "; ".join(f"{k} = {v}" for k, v in L["pronounce"].items())
            o.append(f"   Say it:   {pr}")
        if pauses[i] > 0:
            o.append(f"   Pause after: {pauses[i]:.2f} s")
    o.append("")
    o.append("=" * 72)
    o.append("PRONUNCIATION GUIDE")
    o.append("=" * 72)
    seen = {}
    for L in script["lines"]:
        for k, v in (L.get("pronounce") or {}).items():
            seen.setdefault(k, v)
    for k, v in seen.items():
        o.append(f"  {k:<12} {v}")
    o.append("")
    o.append("=" * 72)
    o.append("CLEAN READ (no marks) — for a first run-through")
    o.append("=" * 72)
    para = " ".join(markup.spoken_text(L["text"]) for L in script["lines"])
    o.append(re.sub(r"(.{1,70})(\s+|$)", r"  \1\n", para).rstrip())
    o.append("")
    out = HERE.parent / "human_voiceover_script.txt"
    out.write_text("\n".join(o) + "\n", encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
