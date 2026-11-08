"""Build a story video end to end.

    python -m storyvid.build stories/der-brief --work /tmp/der-brief
    python -m storyvid.build stories/der-brief --work /tmp/der-brief --stills 2,13.5,50
"""
import argparse
import importlib.util
import json
import os
import sys
import time

import numpy as np
from PIL import Image

from . import assets as assetsmod
from . import mix as mixmod
from . import render as rendermod
from . import tts as ttsmod
from .common import FPS, H, W
from .text import Captions, Handwriting, TitleCard
from .timeline import Timeline

HERE = os.path.dirname(os.path.abspath(__file__))


def load_cues(story_dir):
    sys.path.insert(0, os.path.dirname(HERE))
    spec = importlib.util.spec_from_file_location("cues", os.path.join(story_dir, "cues.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def srt_time(t):
    t = max(0.0, t)
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"


def write_srt(chunks, path, key, offset=0.0):
    with open(path, "w", encoding="utf-8") as f:
        for i, c in enumerate(chunks, 1):
            f.write(f"{i}\n{srt_time(c['show'] + offset)} --> {srt_time(c['hide'] + offset)}\n{c[key]}\n\n")


def make_overlays(story, tl, cues):
    chunks = tl.chunks()
    cap = Captions(chunks, story["vocab"], top_lines=getattr(cues, "CAPTIONS_TOP", ()))
    overlays = []
    prof = np.exp(-0.5 * ((np.arange(H) - (cap.y_top + 120)) / 190.0) ** 2).astype(np.float32)[:, None, None]
    prof_top = np.exp(-0.5 * ((np.arange(H) - (cap.y_top_alt + 110)) / 190.0) ** 2).astype(np.float32)[:, None, None]

    def scrim(frame, t):
        for idx, a in cap.visible(t):
            pr = prof_top if cap.chunks[idx]["line"] in cap.top_lines else prof
            frame *= 1 - 0.38 * a * pr

    overlays += [scrim, lambda fr, t: cap.draw(fr, t)]
    if hasattr(cues, "handwriting"):
        hcfg = cues.handwriting(tl)
        hw_line = next(l for l in story["lines"] if l["id"] == hcfg["line"])
        hw = Handwriting(hcfg["text"], tl.lines[hcfg["line"]]["words"], en=hw_line["chunks"][0][1],
                         y=hcfg.get("y", 600))
        overlays.append(lambda fr, t: hw.draw(fr, t, *hcfg["fade"]))
    if hasattr(cues, "title_window"):
        title = TitleCard(story["title"], f"{story.get('subtitle', '')} · {story.get('level', '')}")
        t0, t1 = cues.title_window(tl)
        overlays.append(lambda fr, t: title.draw(fr, t, t0, t1))
    return overlays, cap


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("story_dir")
    ap.add_argument("--work", required=True)
    ap.add_argument("--models", default=os.environ.get("STORYVID_MODELS", "models"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--stills", default=None, help="comma separated times; renders PNG previews only")
    ap.add_argument("--frames", default=None, help="a:b frame range (preview render)")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--remix", action="store_true", help="rebuild the audio mix")
    ap.add_argument("--extended", action="store_true",
                    help="also build the long cut with the vocabulary moment and outro (extended.json)")
    ap.add_argument("--extended-only", action="store_true", help="reuse an existing story render")
    args = ap.parse_args(argv)

    t_start = time.time()
    story_dir = os.path.abspath(args.story_dir)
    work = os.path.abspath(args.work)
    os.makedirs(work, exist_ok=True)
    story = json.load(open(os.path.join(story_dir, "story.json"), encoding="utf-8"))
    cues = load_cues(story_dir)

    print("1/5 voiceover")
    timing = ttsmod.generate(story, story_dir, work)
    tl = Timeline(story, timing, lead_in=getattr(cues, "LEAD_IN", 0.9), tail=getattr(cues, "TAIL", 6.0))
    print(f"    duration {tl.duration:.2f}s")

    print("2/5 image analysis")
    img_dir = os.path.join(story_dir, "images")
    images = {int(os.path.splitext(f)[0]): os.path.join(img_dir, f) for f in sorted(os.listdir(img_dir))
              if f.lower().endswith((".webp", ".png", ".jpg", ".jpeg"))}
    models = {"depth": os.path.join(args.models, "depth_anything_v2_vitb.onnx"),
              "sr": os.path.join(args.models, "EDSR_x3.pb")}
    adir = assetsmod.prepare(images, work, models, do_sr=not args.stills)

    mix_path = os.path.join(work, "mix.wav")
    if not args.stills and (args.remix or not os.path.exists(mix_path)):
        print("3/5 score, sound design, mix")
        mix_path, lufs, peak = mixmod.build(story, tl, work, cues)
        print(f"    {lufs:.1f} LUFS, peak {peak:.1f} dBFS")

    print("4/5 frames")
    imgs = {iid: rendermod.Img(iid, p, adir) for iid, p in images.items()}
    overlays, cap = make_overlays(story, tl, cues)
    renderer = rendermod.Renderer(imgs, cues.shots(tl), overlays, tl)

    if args.stills:
        outs = []
        for ts in args.stills.split(","):
            p = os.path.join(work, f"still_{float(ts):07.2f}.png")
            rendermod.still(renderer, float(ts), p)
            outs.append(p)
        print("\n".join(outs))
        return

    nframes = int(round(tl.duration * FPS))
    out = args.out or os.path.join(work, f"{os.path.basename(story_dir)}.mp4")
    frames = tuple(int(x) for x in args.frames.split(":")) if args.frames else None
    if not args.extended_only:
        rendermod.render_video(renderer, nframes, out, mix_path, work, workers=args.workers, frames=frames)

    print("5/5 subtitles")
    base = os.path.splitext(out)[0]
    write_srt(cap.chunks, base + ".de.srt", "de")
    write_srt(cap.chunks, base + ".en.srt", "en")
    print(f"done: {out}  ({time.time() - t_start:.0f}s)")

    if (args.extended or args.extended_only) and os.path.exists(os.path.join(story_dir, "extended.json")):
        from . import extended
        print("extended cut: vocabulary moment + outro")
        ext_out = base + "_lang.mp4"
        _, etl, erend = extended.build(story_dir, story, work, tl, out, images, ext_out, workers=args.workers)
        # subtitles for the long cut: story chunks, then the narrated extra lines and card sentences
        extra = []
        for it in etl.items:
            if it["type"] == "say":
                for ci, (de, en) in enumerate(it["chunks"]):
                    ws = [w for w in it["words"] if w["chunk"] == ci]
                    extra.append({"show": ws[0]["start"] - 0.14, "hide": ws[-1]["end"] + 0.4, "de": de, "en": en})
            else:
                line = next(l for l in story["lines"] if l["id"] == it["replay"])
                extra.append({"show": it["a0"] - 0.14, "hide": it["end"],
                              "de": " ".join(c[0] for c in line["chunks"]),
                              "en": " ".join(c[1] for c in line["chunks"])})
        off = tl.duration
        allc = [dict(c) for c in cap.chunks] + [dict(c, show=c["show"] + off, hide=c["hide"] + off) for c in extra]
        eb = os.path.splitext(ext_out)[0]
        write_srt(allc, eb + ".de.srt", "de")
        write_srt(allc, eb + ".en.srt", "en")
        print(f"done: {ext_out}")


if __name__ == "__main__":
    main()
