"""Post-processing with PyMuPDF (the typesetting itself stays in HTML/CSS):
thumb-index tabs, bleed + TrimBox for print, paper tone + cover for screen,
bookmarks, document metadata and language.

Usage: python3 finish.py OUTDIR   (expects interior-raw.pdf, anchors.json, front.pdf, back.pdf)
"""
import json
import re
import sys
from pathlib import Path

import pymupdf
from fontTools.ttLib import TTFont

HERE = Path(__file__).parent
MM = 72 / 25.4
BLEED = 3 * MM
W, H = 210 * MM, 297 * MM
TAB_W, TAB_H, TAB_TOP, TAB_PITCH = 6.5 * MM, 16 * MM, 34 * MM, 19 * MM

tokens = (HERE / "tokens.css").read_text()
hexc = lambda name: re.search(rf"--{name}:\s*(#[0-9A-Fa-f]{{6}})", tokens).group(1)
rgb = lambda h: tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
META = {"title": "100 B1-Fehler – Korrigiere sie vor B2", "author": "DeutschFokus",
        "subject": "Deutsch als Fremdsprache · Niveau B1 → B2 · 100 typische Fehler mit Korrektur, Regel, Mini-Test und B2-Upgrade",
        "keywords": "Deutsch, DaF, B1, B2, Grammatik, Fehler, Korrektur, Übungsbuch",
        "creator": "HTML/CSS · Chromium · PyMuPDF", "producer": "DeutschFokus"}


def sans_ttf(out):
    f = TTFont(HERE / "fonts" / "sans-700-latin.woff2")
    f.flavor = None
    path = out / "_b1sans-bold.ttf"
    f.save(path)
    return str(path)


def chapter_pages(anchors, chapters):
    starts = sorted((anchors[f"kap{c['k']}"], c["k"]) for c in chapters)
    end = anchors["abschlusstest"]
    ranges = {}
    for i, (p, k) in enumerate(starts):
        ranges[k] = range(p, (starts[i + 1][0] if i + 1 < len(starts) else end))
    return ranges


def draw_tab(page, k, recto, fontfile, x0, y0, bleed=0.0):
    """Tab on the outer trim edge; with bleed>0 it runs on into the bleed."""
    y = y0 + TAB_TOP + (k - 1) * TAB_PITCH
    if recto:
        r = pymupdf.Rect(x0 + W - TAB_W, y, x0 + W + bleed, y + TAB_H)
        text_x = x0 + W - TAB_W
    else:
        r = pymupdf.Rect(x0 - bleed, y, x0 + TAB_W, y + TAB_H)
        text_x = x0
    page.draw_rect(r, color=None, fill=rgb(hexc(f"ch{k}")), overlay=True)
    label = str(k)
    fs = 8.2
    font = pymupdf.Font(fontfile=fontfile)
    tw = font.text_length(label, fs)
    page.insert_text((text_x + (TAB_W - tw) / 2, y + TAB_H / 2 + fs * .36), label, fontsize=fs,
                     fontname="B1Sans", fontfile=fontfile, color=(1, 1, 1))


def toc_entries(anchors, chapters, offset):
    plain = lambda s: re.sub(r"[*`]", "", s)
    t = [[1, "Inhalt", anchors.get("inhalt", 5) + offset], [1, "Vorwort", anchors["vorwort"] + offset],
         [1, "Einstufungstest", anchors["einstufungstest"] + offset]]
    for c in chapters:
        t.append([1, f"Kapitel {c['k']} · {plain(c['title'])}", anchors[f"kap{c['k']}"] + offset])
        for n, title in c["entries"]:
            t.append([2, f"{n:03d} · {plain(title)}", anchors[f"f{n:03d}"] + offset])
    t += [[1, "Abschlusstest", anchors["abschlusstest"] + offset], [1, "Nachwort", anchors["nachwort"] + offset],
          [1, "Anhang", anchors["anhang"] + offset]]
    return t


def set_common(doc, toc):
    doc.set_metadata(META)
    doc.xref_set_key(doc.pdf_catalog(), "Lang", "(de-DE)")
    doc.set_toc(toc)


def main():
    out = Path(sys.argv[1])
    data = json.load(open(out / "anchors.json"))
    anchors, chapters = data["anchors"], data["chapters"]
    ranges = chapter_pages(anchors, chapters)
    page_ch = {p: k for k, r in ranges.items() for p in r}
    openers = {anchors[f"kap{c['k']}"]: c["k"] for c in chapters}
    fontfile = sans_ttf(out)
    paper = rgb(hexc("paper"))

    # ---- print interior: 216 x 303 mm with 3 mm bleed, TrimBox set --------
    src = pymupdf.open(out / "interior-raw.pdf")
    pr = pymupdf.open()
    for i in range(src.page_count):
        pno = i + 1
        pg = pr.new_page(width=W + 2 * BLEED, height=H + 2 * BLEED)
        pg.show_pdf_page(pymupdf.Rect(BLEED, BLEED, BLEED + W, BLEED + H), src, i)
        if pno in openers:   # extend the tinted opener band into the bleed
            tint = rgb(hexc(f"ch{openers[pno]}-tint"))
            band_h = 142 * MM
            for r in (pymupdf.Rect(0, 0, W + 2 * BLEED, BLEED),
                      pymupdf.Rect(0, 0, BLEED, BLEED + band_h), pymupdf.Rect(W + BLEED, 0, W + 2 * BLEED, BLEED + band_h)):
                pg.draw_rect(r, color=None, fill=tint)
        if pno in page_ch:
            draw_tab(pg, page_ch[pno], pno % 2 == 1, fontfile, BLEED, BLEED, bleed=BLEED)
        pg.set_trimbox(pymupdf.Rect(BLEED, BLEED, BLEED + W, BLEED + H))
        pg.set_bleedbox(pg.rect)
    set_common(pr, toc_entries(anchors, chapters, 0))
    pr.save(out / "100-B1-Fehler_Innenteil_Druck.pdf", garbage=3, deflate=True)

    # ---- screen edition: paper tone, tabs, cover front/back, links kept ----
    sc = pymupdf.open(out / "interior-raw.pdf")
    for i, pg in enumerate(sc):
        pno = i + 1
        pg.draw_rect(pg.rect, color=None, fill=paper, overlay=False)
        if pno in page_ch:
            draw_tab(pg, page_ch[pno], pno % 2 == 1, fontfile, 0, 0)
    sc.insert_pdf(pymupdf.open(out / "front.pdf"), start_at=0)
    sc.insert_pdf(pymupdf.open(out / "back.pdf"))
    toc = [[1, "Umschlag", 1]] + toc_entries(anchors, chapters, 1) + [[1, "Rückseite", sc.page_count]]
    set_common(sc, toc)
    sc.save(out / "100-B1-Fehler_Bildschirm.pdf", garbage=3, deflate=True)
    print("print:", pr.page_count, "pages · screen:", sc.page_count, "pages")


if __name__ == "__main__":
    main()
