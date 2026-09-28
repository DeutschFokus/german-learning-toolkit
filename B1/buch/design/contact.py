"""Contact sheets: every page of a PDF, 8 per row, page numbers underneath."""
import sys
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw

pdf, out = Path(sys.argv[1]), Path(sys.argv[2])
per_sheet = int(sys.argv[3]) if len(sys.argv) > 3 else 32
dpi = int(sys.argv[4]) if len(sys.argv) > 4 else 28
d = pymupdf.open(pdf)
out.mkdir(parents=True, exist_ok=True)
for s in range(0, d.page_count, per_sheet):
    ims = []
    for i in range(s, min(s + per_sheet, d.page_count)):
        pix = d[i].get_pixmap(dpi=dpi)
        ims.append(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
    w, h = ims[0].size
    cols = 8
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (w + 8) + 8, rows * (h + 22) + 8), "#777")
    dr = ImageDraw.Draw(sheet)
    for k, im in enumerate(ims):
        x, y = 8 + (k % cols) * (w + 8), 8 + (k // cols) * (h + 22)
        sheet.paste(im, (x, y))
        dr.text((x, y + h + 3), str(s + k + 1), fill="white")
    sheet.save(out / f"sheet-{s // per_sheet + 1:02d}.png")
print(out)
