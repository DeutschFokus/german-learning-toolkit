#!/usr/bin/env python3
"""Which lines inside a block miss the baseline grid?

Every block starts on a multiple of half a baseline. This tool lays out each block on its own,
reads the baselines of all body-size lines and prints those that do not sit on the half-baseline grid
(relative to the top of the block), plus block heights that are not a multiple of half a baseline.

    python tools/baseline_probe.py --chapters 5,Z2            # summary for every block
    python tools/baseline_probe.py --chapters 5 --unit 5.4a   # every line of the blocks of one task
"""
import argparse
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import fitz  # noqa: E402
from weasyprint import HTML  # noqa: E402

from engine.config import MM, load_config  # noqa: E402
from engine.loader import load_book  # noqa: E402
from engine.pipeline import Builder  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--level", default="a2")
ap.add_argument("--lang", default="en")
ap.add_argument("--chapters", default=None)
ap.add_argument("--unit", default=None, help="only these blocks (ids or task addresses, comma-separated); prints every line")
ap.add_argument("--css", default=None, help="extra CSS to try out (appended to the stylesheet)")
a = ap.parse_args()

cfg = load_config(a.level, a.lang)
book = load_book(cfg, a.chapters)
b = Builder(cfg, book)
res = b.build()                                   # final HTML of every block, with real page numbers
units = [pl.unit for s in res.pages if s.kind == "flow" for pl in s.flow.placed]
if a.unit:
    keys = a.unit.split(",")
    units = [u for u in units if any(k == u.uid or k == (u.address or "") for k in keys)]
css = b.css + (a.css or "")
pad = 6 * MM
pages = "".join(f'<div class="mpage"><div class="m" style="width:{cfg.text_width_mm}mm">{u.html}</div></div>' for u in units)
doc = (f'<html lang="de"><head><meta charset="utf-8"><style>{css}\n@page{{size:240mm 700mm;margin:0}}'
       f'.mpage{{padding:6mm;break-after:page}}</style></head><body>{pages}</body></html>')
pdf = HTML(string=doc, base_url=str(cfg.root)).write_pdf()
d = fitz.open(stream=pdf, filetype="pdf")
half = cfg.bl / 2
body = float(cfg.lv["type"]["body"])
first = None
rows = []
for u, page in zip(units, d):
    lines = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            spans = [sp for sp in line["spans"] if abs(sp["size"] - body) < 0.2 and sp["text"].strip()]
            if spans:
                lines.append((spans[0]["origin"][1] - pad, spans[0]["text"].strip()[:34]))
    rows.append((u, lines))
# phase: the most common residue is the grid
from collections import Counter  # noqa: E402
phase = Counter(round((y % half) * 4) / 4 for _, ls in rows for y, _ in ls).most_common(1)[0][0]
tot = off = 0
for u, lines in rows:
    bad = []
    for y, t in lines:
        r = (y - phase) % half
        r = r if r <= half / 2 else r - half
        tot += 1
        if abs(r) > 0.35:
            off += 1
            bad.append((y, r, t))
    hres = (u.height % half)
    hres = hres if hres <= half / 2 else hres - half
    if a.unit:
        print(f"{u.uid}  {u.address or ''}  height {u.height:.2f} pt ({hres:+.2f})")
        for y, t in lines:
            r = (y - phase) % half
            r = r if r <= half / 2 else r - half
            print(f"   {y:7.2f}  {r:+5.2f}  {t}")
    elif bad or abs(hres) > 0.3:
        print(f"{u.uid:<24} {u.address or '':<7} {len(bad):>3}/{len(lines):<3} off  height {hres:+.2f}   " +
              "  ".join(f"{r:+.2f} {t[:18]!r}" for _, r, t in bad[:4]))
print(f"\n{tot - off}/{tot} body lines on the half-baseline grid ({(tot - off) / max(tot, 1):.0%}); phase {phase}")
