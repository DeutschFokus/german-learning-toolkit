"""Store-preview images (1920 × 1080): hero, look inside, the cast, what is in the book.

    python build.py --promo --level a2 --lang en      # needs dist/300-pages-<level>-<lang>.pdf

Everything is taken from the finished PDF and the cast portraits, so the images always show the real book.
"""
from __future__ import annotations

import base64
from pathlib import Path

import fitz
from weasyprint import HTML

from .config import load_config
from .render import esc

W, H = 1920, 1080


def _page_uri(doc, label: str, width: int, tmp: Path) -> str:
    i = next(k for k in range(len(doc)) if doc[k].get_label() == label)
    pix = doc[i].get_pixmap(matrix=fitz.Matrix(width / doc[i].rect.width, width / doc[i].rect.width), alpha=False)
    f = tmp / f"p-{label.replace(' ', '')}-{width}.png"
    pix.save(f)
    return f.as_uri()


def export(out: Path, level: str, lang: str, pdf: Path) -> list[Path]:
    cfg = load_config(level, lang)
    lt, col = cfg.level_tokens(), cfg.series["colors"]
    tmp = out / "_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf)
    first = cfg.chapter_start(5)
    fd = (cfg.root / cfg.series["fonts"]["dir"]).as_uri()
    css = (f'@font-face{{font-family:F;src:url("{fd}/DFFraunces-Title.ttf")}}@font-face{{font-family:F;font-weight:900;src:url("{fd}/DFFraunces-Hero.ttf")}}'
           f'@font-face{{font-family:S;src:url("{fd}/DFSans-Regular.ttf")}}@font-face{{font-family:S;font-weight:700;src:url("{fd}/DFSans-Bold.ttf")}}'
           f'@font-face{{font-family:S;font-style:italic;src:url("{fd}/DFSans-Italic.ttf")}}'
           f"@page{{size:{W}px {H}px;margin:0}}body{{margin:0;font-family:S;color:{col['navy']}}}"
           f".s{{position:relative;width:{W}px;height:{H}px;overflow:hidden;break-after:page}}"
           f".cream{{background:{col['cream']}}}.lv{{background:{lt['cover']};color:{col['cream']}}}.navy{{background:{col['navy']};color:{col['cream']}}}"
           f".sun{{position:absolute;width:1500px;height:1500px;border-radius:50%;background:{lt['cover_lite']};left:900px;top:-900px}}"
           f".sun2{{position:absolute;width:1300px;height:1300px;border-radius:50%;background:{lt['cover']};left:-420px;top:330px}}"
           "h1{font-family:F;font-weight:400;font-size:92px;line-height:1.02;letter-spacing:-.018em;margin:0}h1 b{font-weight:900}"
           "h2{position:absolute;left:110px;top:70px;font-family:F;font-weight:400;font-size:76px;letter-spacing:-.016em;margin:0;white-space:nowrap}"
           ".pg{position:absolute;box-shadow:14px 14px 0 rgba(22,27,54,.22);background:#fff}.pg img{display:block;width:100%}"
           ".kick{font-size:22px;font-weight:700;letter-spacing:.14em;text-transform:uppercase}"
           ".pts{list-style:none;padding:0;margin:44px 0 0;font-size:34px;line-height:60px}.pts li::before{content:'✓';font-weight:700;margin-right:18px;color:" + lt["cover"] + "}"
           ".cap{position:absolute;font-size:30px;font-weight:700;text-align:center}"
           ".who{position:absolute;width:300px;text-align:center}.who img{display:block;width:210px;height:210px;border-radius:50%;margin:0 auto 14px}"
           ".who b{display:block;font-family:F;font-size:34px}.who span{font-size:21px;font-style:italic;opacity:.75}")
    P = lambda label, w: _page_uri(doc, label, w, tmp)
    title = esc(cfg.ui("cover.title", level=cfg.level_name)).replace("300", "<b>300</b>", 1)
    pts = "".join(f"<li>{esc(x)}</li>" for x in cfg.ui("promo.hero_points"))
    s1 = (f'<section class="s cream"><div class="sun2"></div><div class="pg" style="left:170px;top:120px;width:594px"><img src="{P("Cover", 1188)}"></div>'
          f'<div style="position:absolute;left:900px;top:190px;width:900px"><div class="kick">Deutsch Fokus</div><h1 style="margin-top:22px">{title}</h1>'
          f'<p style="font-size:34px;font-style:italic;margin:22px 0 0">{esc(cfg.ui("cover.explanations"))}</p><ul class="pts">{pts}</ul></div></section>')
    inside = [(str(first), 150, 230, -5), (str(first + 5), 745, 190, 0), (str(first + 17), 1340, 230, 5)]
    s2 = (f'<section class="s lv"><div class="sun"></div><h2>{esc(cfg.ui("promo.inside"))}</h2>'
          + "".join(f'<div class="pg" style="left:{x}px;top:{y}px;width:470px;transform:rotate({r}deg)"><img src="{P(l, 940)}"></div>' for l, x, y, r in inside)
          + "</section>")
    bios = cfg.series.get("bios", {})
    who = ""
    for k, key in enumerate(bios):
        f = cfg.root / "assets" / "cast" / f"{key}.png"
        if not f.exists():
            continue
        x, y = 150 + (k % 4) * 420, 300 + (k // 4) * 370
        role = cfg.t(bios[key]).split(".")[0].split(",", 1)[-1].strip()
        who += f'<div class="who" style="left:{x}px;top:{y}px"><img src="{f.as_uri()}"><b>{esc(cfg.series["cast"][key]["name"])}</b><span>{esc(role)}</span></div>'
    s3 = (f'<section class="s cream"><h2>{esc(cfg.ui("promo.cast"))}</h2>'
          f'<p style="position:absolute;left:112px;top:178px;font-size:30px;font-style:italic;margin:0">{esc(cfg.ui("promo.cast_sub"))}</p>{who}</section>')
    four = [str(first + 19), str(first + 21), "L 1", "W 1"]
    caps = cfg.ui("promo.captions")
    s4 = (f'<section class="s navy"><h2>{esc(cfg.ui("promo.all"))}</h2>'
          + "".join(f'<div class="pg" style="left:{110 + k * 440}px;top:230px;width:380px"><img src="{P(l, 760)}"></div>'
                    f'<div class="cap" style="left:{110 + k * 440}px;top:800px;width:380px">{esc(caps[k])}</div>' for k, l in enumerate(four))
          + "</section>")
    html = f'<html lang="{lang}"><head><meta charset="utf-8"><style>{css}</style></head><body>{s1}{s2}{s3}{s4}</body></html>'
    res = fitz.open(stream=HTML(string=html, base_url=str(cfg.root)).write_pdf(), filetype="pdf")
    made = []
    out.mkdir(parents=True, exist_ok=True)
    for i, name in enumerate(("1-hero", "2-look-inside", "3-cast", "4-everything")):
        z = W / res[i].rect.width
        f = out / f"300-pages-{level}-{lang}-promo-{name}.png"
        res[i].get_pixmap(matrix=fitz.Matrix(z, z), alpha=False).save(f)
        made.append(f)
    for f in tmp.glob("p-*.png"):
        f.unlink()
    return made
