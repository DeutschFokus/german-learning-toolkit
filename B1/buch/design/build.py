"""Build every deliverable of the B1 book.  Usage: python3 build.py OUTDIR

  interior-raw.pdf                  typeset interior (Chrome)
  100-B1-Fehler_Innenteil_Druck.pdf print interior, 3 mm bleed, TrimBox, thumb tabs
  umschlag-druck.pdf                cover spread (back | spine | front) with bleed, spine from page count
  100-B1-Fehler_Bildschirm.pdf      screen edition: cover, paper tone, links, bookmarks
"""
import subprocess
import sys
from pathlib import Path

import pymupdf

HERE = Path(__file__).parent
out = Path(sys.argv[1]).resolve()
run = lambda *a: subprocess.run([sys.executable, *map(str, a)], check=True, cwd=a[0].parent)

run(HERE / "build_book.py", out)
pages = pymupdf.open(out / "interior-raw.pdf").page_count
run(HERE / "umschlag" / "build_covers.py", out, pages)
run(HERE / "finish.py", out)
