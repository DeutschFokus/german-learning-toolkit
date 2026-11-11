"""PDF post-processing with pikepdf: page labels, bookmarks, metadata, print boxes, link check."""
from __future__ import annotations

import datetime as _dt
import io
from pathlib import Path

import pikepdf
from pikepdf import Array, Dictionary, Name, OutlineItem, String

from .config import MM


def _labels(pdf: pikepdf.Pdf, pages) -> None:
    """PDF page labels that match the printed folios: Cover, ii…vi, 101…, L 1…, T 1…, W 1…"""
    nums = []
    prev = None
    for i, p in enumerate(pages):
        lab = p.label
        if lab.isdigit():
            kind = ("D", "", int(lab))
        elif lab in ("ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"):
            kind = ("r", "", ["", "i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"].index(lab))
        elif " " in lab and lab.split()[1].isdigit():
            kind = ("D", lab.split()[0] + " ", int(lab.split()[1]))
        else:
            kind = (None, lab, 1)
        cont = prev is not None and prev[0] == kind[0] and prev[1] == kind[1] and kind[0] is not None and kind[2] == prev[2] + 1
        if not cont:
            d = Dictionary()
            if kind[0]:
                d[Name.S] = Name("/" + kind[0])
                d[Name.St] = kind[2]
            if kind[1]:
                d[Name.P] = String(kind[1])
            nums += [i, d]
        prev = kind
    pdf.Root[Name.PageLabels] = Dictionary(Nums=Array(nums))


def finish_pdf(raw: bytes, path: Path, cfg, res, doc) -> dict:
    pdf = pikepdf.open(io.BytesIO(raw))
    pages = res.pages
    assert len(pdf.pages) == len(pages), f"page count mismatch: PDF {len(pdf.pages)} vs layout {len(pages)}"
    _labels(pdf, pages)

    # anchors → (page index, top) for bookmarks
    where = {}
    for i, page in enumerate(doc.pages):
        for name, box in page.anchors.items():
            where.setdefault(name, (i, box[1] * 0.75))
    sheet_h = float(pdf.pages[0].MediaBox[3]) - float(pdf.pages[0].MediaBox[1])
    with pdf.open_outline() as outline:
        del outline.root[:]                 # drop the automatic heading outline; ours is Kapitel → Teil → Aufgabe
        stack: list[tuple[int, OutlineItem]] = []
        for i, p in enumerate(pages):
            for level, title, anchor in p.outline:
                pi, top = where.get(anchor, (i, 0.0))
                item = OutlineItem(title, pi, "XYZ", top=sheet_h - max(0.0, top - 12), left=0)
                while stack and stack[-1][0] >= level:
                    stack.pop()
                if stack:
                    stack[-1][1].children.append(item)
                    stack[-1][1].is_closed = stack[-1][0] >= 2
                else:
                    outline.root.append(item)
                stack.append((level, item))
    S = cfg.series["series"]
    with pdf.open_metadata(set_pikepdf_as_editor=False) as meta:
        meta["dc:title"] = res.title
        meta["dc:creator"] = [S["author"]]
        meta["dc:language"] = ["de-DE"]
        meta["dc:description"] = cfg.ui("toc.intro", level=cfg.level_name)
        meta["dc:rights"] = cfg.ui("imprint.copyright", year=S["year"], publisher=S["publisher"])
        meta["pdf:Producer"] = f"300 Pages engine {S['version']} (WeasyPrint + pikepdf)"
        meta["xmp:CreatorTool"] = "300 Pages of German publishing engine"
    pdf.docinfo[Name.Title] = res.title
    pdf.docinfo[Name.Author] = S["author"]
    pdf.docinfo[Name.Subject] = cfg.ui("cover.explanations")
    pdf.docinfo[Name.Keywords] = f"Deutsch, German, {cfg.level_name}, Deutsch Fokus"
    pdf.Root[Name.Lang] = String("de-DE")
    pdf.Root[Name.PageMode] = Name.UseOutlines
    vp = pdf.Root.get(Name.ViewerPreferences, Dictionary())
    vp[Name.DisplayDocTitle] = True
    pdf.Root[Name.ViewerPreferences] = vp
    if cfg.flags.get("print"):
        pg = cfg.page
        o = (pg["slug"] + pg["bleed"]) * MM
        b = pg["slug"] * MM
        for page in pdf.pages:
            mb = [float(x) for x in page.MediaBox]
            w, h = mb[2] - mb[0], mb[3] - mb[1]
            page[Name.TrimBox] = Array([mb[0] + o, mb[1] + o, mb[0] + w - o, mb[1] + h - o])
            page[Name.BleedBox] = Array([mb[0] + b, mb[1] + b, mb[0] + w - b, mb[1] + h - b])
    path.parent.mkdir(parents=True, exist_ok=True)
    pdf.save(path, linearize=True, object_stream_mode=pikepdf.ObjectStreamMode.generate, compress_streams=True)
    return {"pages": len(pdf.pages), "size": path.stat().st_size}
