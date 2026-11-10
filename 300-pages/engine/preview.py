"""PNG previews of every page (PyMuPDF) and contact sheets for a quick visual check."""
from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image


def make_previews(pdf_path: Path, out_dir: Path, res=None, dpi: int = 110, sheets: bool = True) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.png"):
        old.unlink()
    doc = fitz.open(pdf_path)
    files = []
    for i, page in enumerate(doc):
        label = res.pages[i].label.replace(" ", "") if res else str(i + 1)
        f = out_dir / f"{i + 1:03d}-{label}.png"
        page.get_pixmap(dpi=dpi, alpha=False).save(f)
        files.append(f)
    if sheets:
        contact_sheets(files, out_dir)
    return out_dir


def contact_sheets(files: list[Path], out_dir: Path, per_row: int = 6, rows: int = 3, thumb_w: int = 420) -> list[Path]:
    out = []
    per = per_row * rows
    for s in range(0, len(files), per):
        chunk = files[s:s + per]
        ims = [Image.open(f).convert("RGB") for f in chunk]
        th = int(thumb_w * ims[0].height / ims[0].width)
        gap, pad = 18, 24
        n_rows = (len(chunk) + per_row - 1) // per_row
        sheet = Image.new("RGB", (pad * 2 + per_row * thumb_w + (per_row - 1) * gap, pad * 2 + n_rows * th + (n_rows - 1) * gap), "#E9E6E1")
        for i, im in enumerate(ims):
            x = pad + (i % per_row) * (thumb_w + gap)
            y = pad + (i // per_row) * (th + gap)
            sheet.paste(im.resize((thumb_w, th), Image.LANCZOS), (x, y))
        f = out_dir / f"_sheet-{s // per + 1}.png"
        sheet.save(f, optimize=True)
        out.append(f)
    return out
