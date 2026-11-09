#!/usr/bin/env python3
"""Find pages that are almost empty — usually a chapter spilling over by a few lines.

    python3 guide/scripts/check_layout.py            # pages under 30 % full
    python3 guide/scripts/check_layout.py 0.4        # custom threshold

Run it after build.py. Needs `pdftoppm` (poppler-utils) and Pillow.
A short last page of a chapter is normal; a page with one or two lines on
it is worth fixing (trim a sentence, or shrink a box or table).
"""

from __future__ import annotations

import glob
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml
from PIL import Image
from pypdf import PdfReader

GUIDE = Path(__file__).resolve().parent.parent
DPI = 30
TOP_MM, BOTTOM_MM, SIDE_MM = 16, 19, 17  # keep in sync with @page margins in style.css


def chapter_starts(pdf: Path) -> list[tuple[int, str]]:
    reader = PdfReader(str(pdf))
    starts = []

    def walk(items, depth):
        for item in items:
            if isinstance(item, list):
                if depth < 1:
                    walk(item, depth + 1)
            else:
                starts.append((reader.get_destination_page_number(item) + 1, item.title))

    walk(reader.outline, 0)
    return starts  # document order: a chapter comes after the part that starts on the same page


def main() -> None:
    threshold = float(sys.argv[1]) if len(sys.argv) > 1 else 0.3
    cfg = yaml.safe_load((GUIDE / "config.yml").read_text(encoding="utf-8"))
    pdf = GUIDE / cfg["output"]
    starts = chapter_starts(pdf)
    px_per_mm = DPI / 25.4

    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdftoppm", "-r", str(DPI), "-gray", str(pdf), os.path.join(tmp, "p")],
                       check=True, stderr=subprocess.DEVNULL)
        low = []
        for path in sorted(glob.glob(os.path.join(tmp, "p-*.pgm"))):
            page = int(path.rsplit("-", 1)[1].split(".")[0])
            image = Image.open(path)
            width, height = image.size
            top, bottom = int(TOP_MM * px_per_mm), int(height - BOTTOM_MM * px_per_mm)
            left, right = int(SIDE_MM * px_per_mm), int(width - SIDE_MM * px_per_mm)
            pixels = image.load()
            last = top
            for y in range(bottom, top, -1):
                if any(pixels[x, y] < 235 for x in range(left, right)):
                    last = y
                    break
            fill = (last - top) / (bottom - top)
            if fill < threshold:
                chapter = next((t for p, t in reversed(starts) if p <= page), "?")
                low.append((page, fill, chapter))

    if not low:
        print(f"✔ no page is less than {threshold:.0%} full")
    for page, fill, chapter in low:
        print(f"page {page:>2}: {fill:4.0%} full — {chapter}")


if __name__ == "__main__":
    main()
