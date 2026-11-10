#!/usr/bin/env python3
"""Print how full every page is — the quickest way to see where content must be cut or added.

    python tools/layout_report.py --level a2 --lang en --chapters 5,Z2
"""
import argparse
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from engine.config import load_config  # noqa: E402
from engine.loader import load_book  # noqa: E402
from engine.pipeline import Builder  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--level", default="a2")
ap.add_argument("--lang", default="en")
ap.add_argument("--chapters", default=None)
a = ap.parse_args()
cfg = load_config(a.level, a.lang)
book = load_book(cfg, a.chapters)
b = Builder(cfg, book)
res = b.build()
bl = cfg.bl
print(f"page capacity: {cfg.body_lines} lines of {bl} pt\n")
for s in res.pages:
    if s.kind != "flow":
        continue
    fp = s.flow
    bar = "█" * round(fp.used / bl) + "·" * round(fp.leftover / bl)
    flag = " OVERFLOW" if fp.overflow > 0.6 else ""
    print(f"S. {s.label:>4} {s.meta['section']:<13} natural {fp.natural / bl:5.1f}  slack {(cfg.body_height_pt - fp.natural) / bl:5.1f}  final free {fp.leftover / bl:4.1f}{flag}  {bar}")
    for pl in fp.placed:
        u = pl.unit
        print(f"          {pl.top / bl:5.1f}  {u.height / bl:5.1f}  {u.uid:<22} {u.address}")
print()
for i in book.issues:
    print(i)
