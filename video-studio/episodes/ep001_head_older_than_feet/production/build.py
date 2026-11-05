#!/usr/bin/env python3
"""EP001 build orchestrator.

  python3 build.py voice                 # AI narration -> build/timeline_ai.json
  python3 build.py audio                 # score + SFX + mix for the AI voice
  python3 build.py video                 # final_video_ai_voice.mp4 + final_video_no_voice.mp4
  python3 build.py srt                   # subtitles.srt from the AI timeline
  python3 build.py stills 0,12.5,44.8    # review frames -> build/stills/
  python3 build.py all                   # voice + audio + video + srt

  python3 build.py human path/to/my_take.wav [out_dir]
      Aligns the creator's recording to the script, re-times every scene,
      caption and sound cue to it (the voice itself is never sped up), mixes,
      and renders ../final_video_human_voice.mp4 + ../subtitles_human.srt.
      With out_dir, everything (including the video) goes there instead: a dry run.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parent
sys.path.insert(0, str(HERE.parents[2]))

from engine.captions import write_srt  # noqa: E402
from engine.render import render_stills, render_video  # noqa: E402
from engine.timeline import Timeline, build_ai, build_human  # noqa: E402

BUILD = HERE / "build"
SCRIPT = HERE / "script.json"
EPISODE = HERE / "episode.py"


def voice():
    return build_ai(SCRIPT, BUILD)


def audio(tag="ai"):
    import sound
    tl = BUILD / f"timeline_{tag}.json"
    vw = BUILD / f"narration_{tag}.wav"
    return sound.build_mix(tl, vw, BUILD, tag)


def video(tag="ai", no_voice=True, workers=4):
    tl = BUILD / f"timeline_{tag}.json"
    name = {"ai": "final_video_ai_voice.mp4", "human": "final_video_human_voice.mp4"}[tag]
    render_video(EPISODE, tl, EP / name, audio_path=BUILD / f"mix_{tag}.wav", workers=workers)
    if no_voice:
        render_video(EPISODE, tl, EP / "final_video_no_voice.mp4", audio_path=BUILD / f"bed_{tag}.wav",
                     workers=workers, opts={"captions": False})


def srt(tag="ai"):
    T = Timeline(BUILD / f"timeline_{tag}.json")
    name = "subtitles.srt" if tag == "ai" else "subtitles_human.srt"
    n = write_srt(T, EP / name)
    print(f"[srt] {n} cues -> {EP / name}")


def stills(times):
    ts = [float(x) for x in times.split(",")]
    for p in render_stills(EPISODE, BUILD / "timeline_ai.json", ts, BUILD / "stills"):
        print(p)


def human(wav, out_dir=None):
    """Creator's recording -> re-timed edit. out_dir: write everything there instead (dry runs)."""
    global BUILD
    if out_dir:
        BUILD = Path(out_dir)
        BUILD.mkdir(parents=True, exist_ok=True)
    build_human(SCRIPT, Path(wav), BUILD)
    import sound
    sound.build_mix(BUILD / "timeline_human.json", BUILD / "narration_human.wav", BUILD, "human")
    T = Timeline(BUILD / "timeline_human.json")
    srt_path = (BUILD if out_dir else EP) / "subtitles_human.srt"
    print(f"[srt] {write_srt(T, srt_path)} cues -> {srt_path}")
    out = (BUILD if out_dir else EP) / "final_video_human_voice.mp4"
    render_video(EPISODE, BUILD / "timeline_human.json", out, audio_path=BUILD / "mix_human.wav")
    probe(out)


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration:stream=codec_name,width,height,r_frame_rate,sample_rate,channels",
                          "-of", "compact", str(path)], capture_output=True, text=True).stdout
    print(out)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd == "voice":
        voice()
    elif cmd == "audio":
        audio()
    elif cmd == "video":
        video()
    elif cmd == "srt":
        srt()
    elif cmd == "stills":
        stills(sys.argv[2])
    elif cmd == "human":
        human(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif cmd == "all":
        voice()
        audio()
        srt()
        video()
        probe(EP / "final_video_ai_voice.mp4")
    else:
        sys.exit(__doc__)
