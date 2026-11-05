"""Technical QA for a finished episode file.

    python3 -m engine.verify path/to/video.mp4 [more.mp4 ...]

Reports container/stream facts, loudness of the *encoded* audio (EBU R128 via
ffmpeg), black/frozen frames, long silences, and a loop check (first frame vs
last frame). Prints JSON so the numbers can go straight into a QA report.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys

import numpy as np


def _run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(path):
    r = _run(["ffprobe", "-v", "error", "-show_entries",
              "format=duration,bit_rate,size:stream=index,codec_type,codec_name,profile,width,height,r_frame_rate,"
              "pix_fmt,color_space,color_transfer,color_primaries,sample_rate,channels,nb_frames,bit_rate",
              "-of", "json", path])
    return json.loads(r.stdout)


def loudness(path):
    r = _run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-map", "0:a:0", "-af", "ebur128=peak=true",
              "-f", "null", "-"])
    txt = r.stderr
    summ = txt[txt.rfind("Summary:"):]
    get = lambda k: float(re.search(k + r":\s+(-?[\d.]+)", summ).group(1))  # noqa: E731
    return {"integrated_lufs": get("I"), "lra_lu": get("LRA"), "true_peak_dbfs": get("Peak")}


def detect(path):
    r = _run(["ffmpeg", "-hide_banner", "-nostats", "-i", path,
              "-vf", "blackdetect=d=0.25:pix_th=0.06,freezedetect=n=0.0005:d=1.5",
              "-af", "silencedetect=n=-50dB:d=1.2", "-f", "null", "-"])
    t = r.stderr
    return {"black_segments": re.findall(r"black_start:([\d.]+)", t),
            "frozen_segments": re.findall(r"freeze_start: ([\d.]+)", t),
            "silences_over_1.2s": re.findall(r"silence_start: ([\d.]+)", t)}


def frame(path, t):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", path, "-frames:v", "1", "-f", "rawvideo",
                        "-pix_fmt", "rgb24", "-"], capture_output=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(1920, 1080, 3).astype(np.float32)


def loop_check(path, duration):
    a = frame(path, 0.0)
    b = frame(path, duration - 1 / 30 - 0.001)
    # ignore the caption band, which legitimately differs at the loop point
    mask = np.ones((1920, 1080, 1), np.float32)
    mask[1240:1440] = 0
    diff = np.abs(a - b) * mask
    return {"first_vs_last_mean_abs_diff_0_255": round(float(diff.mean()), 2),
            "first_vs_last_pct_pixels_over_24": round(float((diff.max(axis=2) > 24).mean() * 100), 2)}


def verify(path):
    p = probe(path)
    dur = float(p["format"]["duration"])
    out = {"file": path, "size_mb": round(int(p["format"]["size"]) / 1e6, 2), "duration_s": dur,
           "overall_bitrate_mbps": round(int(p["format"]["bit_rate"]) / 1e6, 2), "streams": p["streams"]}
    if any(s["codec_type"] == "audio" for s in p["streams"]):
        out["loudness"] = loudness(path)
    out.update(detect(path))
    out["loop"] = loop_check(path, dur)
    return out


if __name__ == "__main__":
    print(json.dumps([verify(x) for x in sys.argv[1:]], indent=1))
