"""Parallel frame renderer -> ffmpeg (H.264 High, yuv420p, BT.709, +faststart).

An episode module exposes `make_episode(timeline_path, **opts)` returning an
object with `.fps`, `.duration` and `.frame(i) -> BGR24 bytes`.
"""
from __future__ import annotations

import importlib.util
import multiprocessing as mp
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

from .gfx import W, H

_EP = None


def _load(module_path: str):
    spec = importlib.util.spec_from_file_location("episode_mod", module_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["episode_mod"] = mod
    spec.loader.exec_module(mod)
    return mod


def _init(module_path, timeline_path, opts):
    global _EP
    _EP = _load(module_path).make_episode(timeline_path, **opts)


def _frame(i):
    return i, _EP.frame(i)


def encode_cmd(out: Path, fps: int, audio: Path | None, crf: int = 19):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
           "-s", f"{W}x{H}", "-r", str(fps), "-i", "-"]
    if audio:
        cmd += ["-i", str(audio)]
    cmd += ["-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
            "-c:v", "libx264", "-preset", "slow", "-crf", str(crf), "-maxrate", "12M",
            "-bufsize", "24M", "-profile:v", "high", "-level", "4.2", "-g", str(fps * 2),
            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
            "-color_range", "tv"]
    if audio:
        cmd += ["-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-map", "0:v:0", "-map", "1:a:0"]
    cmd += ["-movflags", "+faststart", "-t", "%.3f" % 0, str(out)]
    return cmd


def render_video(module_path, timeline_path, out_path, audio_path=None, workers=4,
                 start_frame=0, end_frame=None, crf=19, opts=None):
    opts = opts or {}
    ep = _load(module_path).make_episode(timeline_path, **opts)
    fps, n_total = ep.fps, int(round(ep.duration * ep.fps))
    end_frame = n_total if end_frame is None else min(end_frame, n_total)
    frames = list(range(start_frame, end_frame))
    final_path = Path(out_path)
    tmp_path = final_path.with_name(final_path.stem + ".partial" + final_path.suffix)
    cmd = encode_cmd(tmp_path, fps, Path(audio_path) if audio_path else None, crf)
    cmd[cmd.index("-t") + 1] = "%.3f" % (len(frames) / fps)
    if audio_path and start_frame:
        i = cmd.index(str(audio_path))
        cmd[i - 1:i - 1] = ["-ss", "%.3f" % (start_frame / fps)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    with mp.get_context("fork").Pool(workers, initializer=_init,
                                     initargs=(str(module_path), str(timeline_path), opts)) as pool:
        for k, (i, buf) in enumerate(pool.imap(_frame, frames, chunksize=2)):
            proc.stdin.write(buf)
            if k % 150 == 0:
                el = time.time() - t0
                print(f"[render] frame {i}/{end_frame}  {el:6.1f}s  "
                      f"({(k + 1) / max(el, 1e-6):4.1f} fps)", flush=True)
    proc.stdin.close()
    rc = proc.wait()
    if rc:
        raise SystemExit(f"ffmpeg failed with {rc}; {final_path} left untouched")
    tmp_path.replace(final_path)      # only a finished encode ever replaces a deliverable
    print(f"[render] done {final_path} in {time.time() - t0:.1f}s rc={rc}")
    return final_path


def render_stills(module_path, timeline_path, times, out_dir, opts=None, scale=1.0):
    import cv2
    opts = opts or {}
    ep = _load(module_path).make_episode(timeline_path, **opts)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for t in times:
        i = int(round(t * ep.fps))
        img = np.frombuffer(ep.frame(i), np.uint8).reshape(H, W, 3)
        if scale != 1.0:
            img = cv2.resize(img, (int(W * scale), int(H * scale)), interpolation=cv2.INTER_AREA)
        p = out_dir / f"still_{t:06.2f}.png"
        cv2.imwrite(str(p), img)
        paths.append(p)
    return paths
