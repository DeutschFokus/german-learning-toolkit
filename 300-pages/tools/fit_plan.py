#!/usr/bin/env python3
"""How long does every chapter come out – and which page plan adds up to exactly 300?

For books with flowing blocks (levels/<level>.yaml → structure.mode: flex) the length of a chapter
is not fixed by a page budget per section. This tool lays out every chapter once, prints the
smallest number of pages each one needs, and proposes `chapter_pages` so that the book has 300
pages and every chapter gets its share of the spare room.

    python tools/fit_plan.py --level a1
    python tools/fit_plan.py --level a1 --body 11 --baseline 15.5 --lines 45     # try another type size
"""
import argparse
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine import models as M  # noqa: E402
from engine.config import load_config  # noqa: E402
from engine.layout import paginate  # noqa: E402
from engine.loader import load_book  # noqa: E402
from engine.pipeline import Builder  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--level", default="a1")
ap.add_argument("--lang", default="en")
ap.add_argument("--chapters", default=None)
ap.add_argument("--body", type=float)
ap.add_argument("--baseline", type=float)
ap.add_argument("--lines", type=int)
ap.add_argument("--hand", type=float)
ap.add_argument("--total", type=int, default=300)
args = ap.parse_args()

cfg = load_config(args.level, args.lang)
cfg.flags["no_cache"] = bool(args.body or args.baseline or args.lines)
t = cfg.lv["type"]
for key, val in (("body", args.body), ("baseline", args.baseline), ("body_lines", args.lines), ("hand", args.hand)):
    if val:
        t[key] = val
book = load_book(cfg, args.chapters)
if book.errors():
    sys.exit("\n".join(str(e) for e in book.errors()[:20]))
b = Builder(cfg, book)
b.layout_round()
units = b._round["units"]
print(f"type {t['body']}/{t['baseline']} pt · {t['body_lines']} lines per page ({b.cap:.1f} pt)\n")
print(f"{'part':>6}  {'min':>4}  {'content':>8}  {'plan':>5}")
need: dict[str, int] = {}
content: dict[str, float] = {}
for part in book.parts():
    op, flow = units[part.key]
    pages = paginate(flow, b.cap, b.bl)
    extra = 1 if isinstance(part, M.Chapter) else 0
    need[part.key] = len(pages) + extra
    content[part.key] = sum(p.used for p in pages) / b.cap + extra
    print(f"{part.key:>6}  {need[part.key]:>4}  {content[part.key]:>8.1f}  {b.part_len(part):>5}{'   ← too long' if need[part.key] > b.part_len(part) else ''}")
chapters = [p for p in book.parts() if isinstance(p, M.Chapter)]
stations = [p for p in book.parts() if not isinstance(p, M.Chapter)]
if cfg.flex and len(chapters) == cfg.n_chapters:
    rev = sum(b.part_len(p) for p in stations) if len(stations) == cfg.n_stations else cfg.n_stations * cfg.station_len(1)
    room = args.total - rev
    mins = [need[p.key] for p in chapters]
    spare = room - sum(mins)
    print(f"\nchapters need {sum(mins)} pages, revision part has {rev}, room for chapters: {room} → spare pages: {spare}")
    if spare >= 0:
        plan = list(mins)
        # the spare pages go to the chapters that are packed most tightly
        order = sorted(range(len(plan)), key=lambda i: content[chapters[i].key] / plan[i], reverse=True)
        for k in range(spare):
            i = max(range(len(plan)), key=lambda i: content[chapters[i].key] / plan[i])
            plan[i] += 1
        print("chapter_pages:", plan, "· sum", sum(plan))
    else:
        print("The book is too long for this type size: make the type smaller or the page taller.")
