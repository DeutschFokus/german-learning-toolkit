"""Render chosen pages 4-up (2x2) for close inspection. Usage: quad.py PDF OUT.png p1 p2 p3 p4"""
import sys

import pymupdf
from PIL import Image

d = pymupdf.open(sys.argv[1])
pages = [int(p) for p in sys.argv[3:]]
ims = []
for p in pages:
    pix = d[p - 1].get_pixmap(dpi=int(__import__("os").environ.get("DPI", 55)))
    ims.append(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
w, h = ims[0].size
cols = 2 if len(ims) > 1 else 1
rows = (len(ims) + cols - 1) // cols
s = Image.new("RGB", (cols * (w + 6), rows * (h + 6)), "#666")
for i, im in enumerate(ims):
    s.paste(im, ((i % cols) * (w + 6), (i // cols) * (h + 6)))
s.save(sys.argv[2])
