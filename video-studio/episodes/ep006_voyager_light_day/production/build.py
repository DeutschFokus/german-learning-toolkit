#!/usr/bin/env python3
"""EP006 build — narrated by the creator (no AI voice in any deliverable).

  python3 build.py scratch              # timing-only scratch read -> build/timeline_scratch.json
  python3 build.py audio                # music + SFX bed, ducked where the narration will sit
  python3 build.py video                # final_video_no_voice.mp4 + guide_record_along.mp4
  python3 build.py stills 0,12.5,44.8   # review frames -> build/stills/
  python3 build.py all                  # scratch + audio + video

  python3 build.py human path/to/your_take.wav [out_dir]
      Aligns your recording to the script (word by word), re-times every scene,
      caption and sound cue to YOUR read (the voice is never sped up), mixes at
      -14 LUFS and renders ../final_video_human_voice.mp4 + ../subtitles.srt.
      With out_dir, everything goes there instead (a dry run).
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


def scratch():
    return build_ai(SCRIPT, BUILD, tag="scratch")


def audio():
    import sound
    return sound.build_mix(BUILD / "timeline_scratch.json", BUILD / "narration_scratch.wav", BUILD, "scratch")


def video(workers=4):
    tl = BUILD / "timeline_scratch.json"
    render_video(EPISODE, tl, EP / "final_video_no_voice.mp4", audio_path=BUILD / "bed_scratch.wav",
                 workers=workers, opts={"captions": False})
    render_video(EPISODE, tl, EP / "guide_record_along.mp4", audio_path=BUILD / "bed_scratch.wav",
                 workers=workers, opts={"captions": True, "guide": True})


def stills(times):
    ts = [float(x) for x in times.split(",")]
    for p in render_stills(EPISODE, BUILD / "timeline_scratch.json", ts, BUILD / "stills"):
        print(p)


def human(wav, out_dir=None):
    global BUILD
    if out_dir:
        BUILD = Path(out_dir)
        BUILD.mkdir(parents=True, exist_ok=True)
    build_human(SCRIPT, Path(wav), BUILD)
    import sound
    sound.build_mix(BUILD / "timeline_human.json", BUILD / "narration_human.wav", BUILD, "human")
    T = Timeline(BUILD / "timeline_human.json")
    srt_path = (BUILD if out_dir else EP) / "subtitles.srt"
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
    if cmd == "scratch":
        scratch()
    elif cmd == "audio":
        audio()
    elif cmd == "video":
        video()
    elif cmd == "stills":
        stills(sys.argv[2])
    elif cmd == "human":
        human(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif cmd == "all":
        scratch()
        audio()
        video()
        probe(EP / "final_video_no_voice.mp4")
    else:
        sys.exit(__doc__)
