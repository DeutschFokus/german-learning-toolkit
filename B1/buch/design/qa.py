"""Layout QA on the raw interior: page fill, stranded headings, lonely lines."""
import json
import sys
from pathlib import Path

import pymupdf

out = Path(sys.argv[1])
d = pymupdf.open(out / "interior-raw.pdf")
a = json.load(open(out / "anchors.json"))
openers = {a["anchors"][f"kap{c['k']}"] for c in a["chapters"]}
part_ends = {a["anchors"][k] - 1 for k in ("einstufungstest", "abschlusstest", "nachwort", "anhang")} | {p - 1 for p in openers} | {d.page_count}
front = set(range(1, 7))
MM = 72 / 25.4
top, bottom = 21 * MM, d[0].rect.height - 26 * MM   # below the running heads
issues = []
for i, pg in enumerate(d):
    pno = i + 1
    if pno in front or pno in openers:
        continue
    lines = []
    for b in pg.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            y = l["bbox"][1]
            if top < y < bottom and "".join(s["text"] for s in l["spans"]).strip():
                lines.append((l["bbox"], l["spans"]))
    if not lines:
        issues.append((pno, "empty page")); continue
    fill = (max(bb[3] for bb, _ in lines) - top) / (bottom - top)
    if fill < .5 and pno not in part_ends:
        issues.append((pno, f"only {fill:.0%} filled (mid-part)"))
    if len(lines) <= 2:
        issues.append((pno, f"lonely: {len(lines)} line(s)"))
    last_bb, last_spans = max(lines, key=lambda x: x[0][3])
    s0 = last_spans[0]
    if "Sans" in s0["font"] and "Bold" in s0["font"] and s0["size"] > 10.5:
        issues.append((pno, f"heading at page bottom: {s0['text'][:40]!r}"))
short_ends = [p for p in sorted(part_ends) if p not in front]
print("pages:", d.page_count)
print("issues:", issues or "none")
