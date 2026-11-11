"""Cover exports: the same cover template as the book, rendered in three formats for every level.

    a4      210 × 297 mm   → 1654 × 2339 px   the book cover itself
    store   210 × 336 mm   → 1600 × 2560 px   5:8, the usual e-book store format
    square  210 × 210 mm   → 3000 × 3000 px   social media and audio-style tiles

plus one line-up image per language with all six levels side by side.
Nothing here is drawn by hand: colours come from levels/<level>.yaml, words from i18n/<lang>.yaml.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

import fitz
from PIL import Image, ImageFilter
from weasyprint import HTML

from .config import load_config
from .pipeline import cover_view, stylesheet
from .render import Macros, make_env

FORMATS = {                     # name → (page height in mm, pixel width, pixel height)
    "a4": (297.0, 1654, 2339),
    "store": (336.0, 1600, 2560),
    "square": (210.0, 3000, 3000),
}
WIDTH_MM = 210.0


def cover_png(level: str, lang: str, fmt: str, path: Path, sample: bool = False) -> Path:
    """Render one cover and save it with exactly the pixel size of the format."""
    cfg = load_config(level, lang)
    env = make_env(cfg)
    height, px_w, px_h = FORMATS[fmt]
    css = stylesheet(cfg, env) + f"\n@page{{size:{WIDTH_MM}mm {height}mm;margin:0}}"
    inner = Macros(env.get_template("pages.html.j2").module).cover(cover_view(cfg, sample))
    cls = "" if fmt == "a4" else fmt
    doc = (f'<!DOCTYPE html><html lang="de-DE"><head><meta charset="utf-8"><style>{css}</style></head>'
           f'<body class="digital"><section class="page recto cn cover {cls}" lang="de">{inner}</section></body></html>')
    pdf = HTML(string=doc, base_url=str(cfg.root)).write_pdf()
    with fitz.open(stream=pdf, filetype="pdf") as d:
        page = d[0]
        zoom = px_w / page.rect.width
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    if img.size != (px_w, px_h):                       # at most one pixel of rounding
        img = img.resize((px_w, px_h), Image.LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, optimize=True)
    return path


def lineup(covers: list[Path], path: Path, cover_w: int = 640, gap: int = 46, margin: int = 110,
           background: str = "#EDE8DF") -> Path:
    """All levels side by side on a calm background, each with a soft shadow."""
    imgs = []
    for c in covers:
        im = Image.open(c).convert("RGB")
        imgs.append(im.resize((cover_w, round(im.height * cover_w / im.width)), Image.LANCZOS))
    ch = imgs[0].height
    W = 2 * margin + len(imgs) * cover_w + (len(imgs) - 1) * gap
    H = ch + 2 * margin + 20
    sheet = Image.new("RGB", (W, H), background)
    shadow = Image.new("L", (W, H), 0)
    for i, im in enumerate(imgs):
        x = margin + i * (cover_w + gap)
        shadow.paste(105, (x + 4, margin + 22, x + cover_w - 4, margin + ch + 16))
    shadow = shadow.filter(ImageFilter.GaussianBlur(20))
    sheet.paste(Image.new("RGB", (W, H), "#161B36"), (0, 0), shadow)
    for i, im in enumerate(imgs):
        sheet.paste(im, (margin + i * (cover_w + gap), margin))
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path, optimize=True)
    return path


def export_all(out: Path, langs: Optional[Iterable[str]] = None, levels: Optional[Iterable[str]] = None) -> list[Path]:
    base = load_config("a2", "en")
    langs = list(langs or base.series["languages"])
    levels = list(levels or base.series["levels"])
    made: list[Path] = []
    for lang in langs:
        a4s = []
        for level in levels:
            for fmt, (_, w, h) in FORMATS.items():
                p = cover_png(level, lang, fmt, out / f"300-pages-{level}-{lang}-cover-{fmt}-{w}x{h}.png")
                made.append(p)
                if fmt == "a4":
                    a4s.append(p)
            print(f"  covers {level}-{lang}")
        made.append(lineup(a4s, out / f"300-pages-lineup-{lang}.png"))
    return made
