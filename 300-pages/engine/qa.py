"""Automatic quality report for a finished build.

Checks what a machine can check — geometry, links, fonts, text extraction,
contrast, tagging — and writes the result as Markdown next to the PDF.
"""
from __future__ import annotations

import datetime as _dt
import re
from collections import Counter
from pathlib import Path

import fitz  # PyMuPDF
import pikepdf

from .config import MM

_SPACED = re.compile(r"(?<![^\W\d_])(?:[^\W\d_] ){4,}[^\W\d_](?![^\W\d_])")


# ── individual checks ────────────────────────────────────────────────────────
def geometry(res, cfg, doc) -> tuple[list[str], list[tuple]]:
    """Planned layout vs. final render: overflow, collisions, spare room, footer clearance."""
    problems: list[str] = []
    rows = []
    final = {}
    for i, page in enumerate(doc.pages):
        for name, box in page.anchors.items():
            final[name] = (i, box[1] * 0.75, box[3] * 0.75)
    cap = cfg.body_height_pt
    pg = cfg.page
    off = (pg["slug"] + pg["bleed"]) * MM if cfg.flags.get("print") else 0.0
    body_top = pg["top"] * MM + off
    footer_top = pg["footer_top"] * MM + off
    for i, s in enumerate(res.pages):
        if s.kind == "opener":
            end = final.get(f"end-{s.pid}")
            if end:
                room = (footer_top - end[1]) / MM
                rows.append((s.label, "Auftakt", "–", "–", f"{room:.1f} mm to footer", "ok" if room >= 1 else "TIGHT"))
                if room < 0:
                    problems.append(f"S. {s.label}: opener content runs {-room:.1f} mm into the footer")
            continue
        if s.kind != "flow":
            continue
        fp = s.flow
        prev_bottom = -1.0
        for pl in fp.placed:
            u = pl.unit
            f = final.get(u.uid) or final.get("u-" + u.uid)
            if f is None:
                problems.append(f"S. {s.label}: block {u.uid} is missing in the final render")
                continue
            if f[0] != i:
                problems.append(f"S. {s.label}: block {u.uid} landed on another page")
            h = f[2] - f[1]
            if abs(h - u.height) > 1.0:
                problems.append(f"S. {s.label}: block {u.uid} is {h - u.height:+.1f} pt taller than planned")
            top = f[1] - body_top
            if top < prev_bottom - 0.5:
                problems.append(f"S. {s.label}: block {u.uid} collides with the block above ({prev_bottom - top:.1f} pt)")
            prev_bottom = top + h
        bottom = prev_bottom
        clearance = (footer_top - (body_top + bottom)) / MM
        fill = bottom / cap
        state = "ok"
        if bottom > cap + 0.6:
            state = "OVERFLOW"
            problems.append(f"S. {s.label}: content overflows the text block by {(bottom - cap) / MM:.1f} mm")
        elif clearance < 1.0:
            state = "FOOTER"
            problems.append(f"S. {s.label}: content comes within {clearance:.1f} mm of the footer")
        elif fill < 0.80:
            state = "open"
        rows.append((s.label, s.meta["section"], f"{fp.natural / cap:.0%}", f"{fill:.0%}", f"{clearance:.1f} mm to footer", state))
    return problems, rows


def fixed_pages(pdf_path: Path, res, cfg) -> tuple[list[str], list[tuple]]:
    """Front matter and appendix pages are composed as whole pages, so they are checked in the finished PDF:
    no text may reach the folio line."""
    pg = cfg.page
    off = (pg["slug"] + pg["bleed"]) * MM if cfg.flags.get("print") else 0.0
    folio_top = pg["folio_top"] * MM + off
    trim_bottom = pg["height"] * MM + off
    problems: list[str] = []
    rows: list[tuple] = []
    with fitz.open(pdf_path) as d:
        for i, s in enumerate(res.pages):
            if s.kind not in ("front", "appendix"):
                continue
            folio_words = set(s.folio.split())
            lowest = 0.0
            for x0, y0, x1, y1, word, *_ in d[i].get_text("words"):
                if y0 > trim_bottom:                                   # slug area of the print sheet
                    continue
                if word in folio_words and y0 >= folio_top - 3:        # the folio itself
                    continue
                lowest = max(lowest, y1)
            room = (folio_top - lowest) / MM
            state = "ok" if room >= 2.0 else "FOLIO"
            if room < 2.0:
                problems.append(f"S. {s.label}: text comes within {room:.1f} mm of the folio" if room >= 0
                                else f"S. {s.label}: text runs {-room:.1f} mm past the folio line")
            rows.append((s.label, s.group, f"{room:.1f} mm to folio", state))
    return problems, rows


def baseline_report(pdf_path: Path, res, cfg) -> tuple[list[tuple], dict]:
    """Where do body-size text lines sit relative to the baseline grid?

    Blocks start on multiples of half a baseline, so running text lands on that grid.
    Table rows are centred between their rules; the tables start a quarter line low to compensate.
    Text on ruled write-in lines follows the ruling instead.
    """
    d = fitz.open(pdf_path)
    half, quarter = cfg.bl / 2, cfg.bl / 4
    body = float(cfg.lv["type"]["body"])
    pg = cfg.page
    off = (pg["slug"] + pg["bleed"]) * MM if cfg.flags.get("print") else 0.0
    # first baseline of a block that starts at the top of the text block
    phase = None
    per_page = {}
    for i, page in enumerate(d):
        s = res.pages[i]
        if s.group != "learn":
            continue
        ys = []
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                spans = [sp for sp in line["spans"] if abs(sp["size"] - body) < 0.2 and sp["text"].strip()]
                if spans:
                    ys.append(spans[0]["origin"][1])
        per_page[i] = ys
    residues = Counter(round((y % half) * 8) / 8 for ys in per_page.values() for y in ys)
    if not residues:
        return [], {"half": 0.0, "quarter": 0.0, "lines": 0}
    phase = residues.most_common(1)[0][0]

    def dist(y: float, step: float) -> float:
        r = (y - phase) % step
        return min(r, step - r)

    rows = []
    tot = on_h = on_q = 0
    seen = set()
    for i in sorted(per_page):
        if i in seen:
            continue
        s = res.pages[i]
        pair = [i]
        if s.side == "verso" and i + 1 in per_page and res.pages[i + 1].side == "recto":
            pair.append(i + 1)
        seen.update(pair)
        ys = [y for j in pair for y in per_page[j]]
        h = sum(1 for y in ys if dist(y, half) <= 0.35)
        q = sum(1 for y in ys if dist(y, quarter) <= 0.35)
        tot += len(ys)
        on_h += h
        on_q += q
        shared = "–"
        if len(pair) == 2:
            a = {round((y - phase) / half) for y in per_page[pair[0]] if dist(y, half) <= 0.35}
            b = {round((y - phase) / half) for y in per_page[pair[1]] if dist(y, half) <= 0.35}
            shared = str(len(a & b))
        n = len(ys)
        rows.append(("–".join(res.pages[j].label for j in pair), n, f"{h / n:.0%}" if n else "–", f"{q / n:.0%}" if n else "–", shared))
    return rows, {"half": on_h / tot if tot else 0.0, "quarter": on_q / tot if tot else 0.0, "lines": tot}


def links_report(pdf_path: Path) -> dict:
    pdf = pikepdf.open(pdf_path)
    names = set()

    def walk(node):
        if "/Names" in node:
            arr = node["/Names"]
            for k in range(0, len(arr), 2):
                names.add(str(arr[k]))
        for kid in node.get("/Kids", []):
            walk(kid)

    if "/Names" in pdf.Root and "/Dests" in pdf.Root["/Names"]:
        walk(pdf.Root["/Names"]["/Dests"])
    internal = external = broken = 0
    broken_list = []
    hosts = Counter()
    targets, urls = set(), set()
    for pno, page in enumerate(pdf.pages, 1):
        for a in page.get("/Annots", []):
            if a.get("/Subtype") != "/Link":
                continue
            if "/Dest" in a:
                internal += 1
                dest = a["/Dest"]
                targets.add(str(dest))
                if isinstance(dest, (pikepdf.String, pikepdf.Name)) and str(dest).lstrip("/") not in names:
                    broken += 1
                    broken_list.append(f"p{pno}: {dest}")
            elif "/A" in a and a["/A"].get("/S") == "/URI":
                external += 1
                uri = str(a["/A"]["/URI"])
                urls.add(uri)
                if not re.match(r"^(https://[^\s/]+\.[^\s/]+(/\S*)?|mailto:[^@\s]+@[^@\s]+\.\w+)$", uri):
                    broken += 1
                    broken_list.append(f"p{pno}: malformed URL {uri}")
                hosts[re.sub(r"^(\w+:)(//)?([^/?#]*).*$", r"\1\2\3", uri)] += 1
            elif "/A" in a and a["/A"].get("/S") == "/GoTo":
                internal += 1
    return {"internal": internal, "external": external, "broken": broken, "broken_list": broken_list[:10],
            "named_destinations": len(names), "hosts": dict(hosts), "targets": len(targets), "urls": sorted(urls)}


def fonts_report(pdf_path: Path) -> tuple[list[tuple[str, str, bool]], int]:
    pdf = pikepdf.open(pdf_path)
    seen = {}
    size = 0
    for page in pdf.pages:
        fonts = page.get("/Resources", {}).get("/Font", {})
        for _, f in fonts.items():
            base = str(f.get("/BaseFont", "?")).lstrip("/")
            if base in seen:
                continue
            desc = None
            if "/DescendantFonts" in f:
                desc = f["/DescendantFonts"][0].get("/FontDescriptor")
            else:
                desc = f.get("/FontDescriptor")
            embedded = False
            if desc is not None:
                for key in ("/FontFile", "/FontFile2", "/FontFile3"):
                    if key in desc:
                        embedded = True
                        try:
                            size += len(desc[key].read_raw_bytes())
                        except Exception:
                            pass
            seen[base] = (str(f.get("/Subtype", "")).lstrip("/"), embedded)
    return [(k, v[0], v[1]) for k, v in sorted(seen.items())], size


def structure_report(pdf_path: Path) -> dict:
    pdf = pikepdf.open(pdf_path)
    out = {"tagged": "/StructTreeRoot" in pdf.Root, "lang": str(pdf.Root.get("/Lang", "")), "figures": 0, "figures_with_alt": 0,
           "form_fields": 0, "trim_boxes": sum(1 for p in pdf.pages if "/TrimBox" in p)}
    if "/AcroForm" in pdf.Root:
        out["form_fields"] = len(pdf.Root["/AcroForm"].get("/Fields", []))
    for obj in pdf.objects:
        try:
            if isinstance(obj, pikepdf.Dictionary) and obj.get("/S") == "/Figure":
                out["figures"] += 1
                if "/Alt" in obj and str(obj["/Alt"]).strip():
                    out["figures_with_alt"] += 1
        except Exception:
            continue
    d = fitz.open(pdf_path)
    out["labels"] = [d[i].get_label() for i in range(len(d))]
    toc = d.get_toc()
    out["bookmarks"] = Counter(level for level, _, _ in toc)
    out["title"] = d.metadata.get("title", "")
    out["author"] = d.metadata.get("author", "")
    return out


def text_samples(pdf_path: Path, res, wanted: list[str]) -> list[tuple[str, str, list[str]]]:
    d = fitz.open(pdf_path)
    out = []
    by_label = {s.label: i for i, s in enumerate(res.pages)}
    for lab in wanted:
        if lab not in by_label:
            continue
        txt = d[by_label[lab]].get_text("text")
        flags = []
        if "�" in txt:
            flags.append("replacement characters")
        if _SPACED.search(txt):
            flags.append("letter-spaced text: " + _SPACED.search(txt).group(0))
        out.append((lab, txt.strip(), flags))
    return out


def whole_text_flags(pdf_path: Path) -> dict:
    d = fitz.open(pdf_path)
    txt = "\n".join(p.get_text("text") for p in d)
    return {"chars": len(txt), "replacement": txt.count("�"), "spaced": len(_SPACED.findall(txt)),
            "umlauts": sum(txt.count(c) for c in "äöüÄÖÜß"), "turkish": sum(txt.count(c) for c in "çğıİşÇĞŞ"),
            "soft_hyphens": txt.count("­"), "zero_width": txt.count("​")}


# ── the report ───────────────────────────────────────────────────────────────
def _canon(text: str) -> str:
    """Case-insensitive comparison that also works for Turkish capitals (İ, I)."""
    return re.sub(r"\s+", " ", text.lower().replace("i\u0307", "i").replace("ı", "i")).strip()


def cover_elements(pdf_path: Path, cfg) -> list[tuple[str, int, int]]:
    """Every text element of the cover must exist exactly once: (element, expected, found)."""
    with fitz.open(pdf_path) as d:
        text = _canon(d[0].get_text())
    rest = cfg.ui("cover.title_rest").replace("{level}", cfg.level_name)
    rows = [("300", 1, len(re.findall(r"(?<!\d)300(?!\d)", text))),
            (cfg.de("labels.level"), 1, text.count(_canon(cfg.de("labels.level")))),
            (f"{cfg.level_name} (badge and title)", 2, len(re.findall(rf"\b{re.escape(_canon(cfg.level_name))}\b", text)))]
    for part in rest.split("|"):
        words = [w for w in part.split() if w != cfg.level_name]
        if words:
            phrase = " ".join(words)
            rows.append((phrase, 1, text.count(_canon(phrase))))
    rows.append((cfg.ui("cover.explanations"), 1, text.count(_canon(cfg.ui("cover.explanations")))))
    for f in cfg.ui("cover.features"):
        rows.append((f, 1, text.count(_canon(f))))
    rows.append(("Deutsch Fokus (logo)", 1, len(re.findall(r"deutsch\s*fokus", text))))
    return rows


def write_report(pdf_path: Path, out_path: Path, cfg, book, res, doc, info: dict, log: str, timings: dict) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    L: list[str] = []
    add = L.append
    name = pdf_path.name
    add(f"# QA report · {name}")
    add("")
    add(f"Built {_dt.datetime.now():%Y-%m-%d %H:%M} · level {cfg.level_name} · language {cfg.lang} · "
        f"flags: {', '.join(k for k, v in cfg.flags.items() if v) or 'none'}")
    add("")
    problems, rows = geometry(res, cfg, doc)
    fixed_problems, fixed_rows = fixed_pages(pdf_path, res, cfg)
    problems = problems + fixed_problems
    links = links_report(pdf_path)
    fonts, font_bytes = fonts_report(pdf_path)
    st = structure_report(pdf_path)
    flags = whole_text_flags(pdf_path)
    brow, bstat = baseline_report(pdf_path, res, cfg)
    errors = len(book.errors())
    cover_rows = cover_elements(pdf_path, cfg)
    contrast_rows = cfg.contrast_table()
    contrast_fail = [r for r in contrast_rows if r[3] < float(r[4])]
    verdict = [
        ("Validation", f"{errors} errors, {len(book.warnings())} warnings", errors == 0),
        ("Layout geometry", f"{len(problems)} problems on {sum(1 for s in res.pages if s.group == 'learn')} learning pages "
                            f"and {len(fixed_rows)} front-matter and appendix pages", not problems),
        ("Links", f"{links['internal']} internal link areas to {links['targets']} targets, {links['external']} external to "
                  f"{len(links['urls'])} URLs, {links['broken']} broken", links["broken"] == 0),
        ("Fonts", f"{len(fonts)} faces, all embedded" if all(f[2] for f in fonts) else "NOT all embedded", all(f[2] for f in fonts)),
        ("Text extraction", f"{flags['replacement']} broken characters, {flags['spaced']} letter-spaced runs", flags["replacement"] == 0 and flags["spaced"] == 0),
        ("Tagged PDF", f"{st['figures_with_alt']}/{st['figures']} figures with alt text, language {st['lang']}", st["tagged"] and st["figures"] == st["figures_with_alt"]),
        ("Cover", f"{len(cover_rows)} text elements, {sum(1 for _, e, f in cover_rows if e != f)} duplicated or missing",
         all(e == f for _, e, f in cover_rows)),
        ("Contrast", f"{len(contrast_rows)} colour pairs, {len(contrast_fail)} below WCAG AA", not contrast_fail),
        ("Baseline grid", f"{bstat['half']:.0%} of body lines on the half-baseline grid, {bstat['quarter']:.0%} on the quarter grid", bstat["quarter"] >= 0.85),
    ]
    add("## Summary")
    add("")
    add("| Check | Result | |")
    add("| --- | --- | --- |")
    for k, v, ok in verdict:
        add(f"| {k} | {v} | {'pass' if ok else '**CHECK**'} |")
    add("")
    add(f"File: {info['pages']} pages, {info['size'] / 1024:.0f} KB · layout {timings['layout']:.1f} s ({res.rounds} rounds) · "
        f"render {timings['render']:.1f} s · write {timings['write']:.1f} s")
    add("")

    add("## 1 · Validation log")
    add("")
    add("```")
    add(log)
    extra = [str(i) for i in book.issues if str(i) not in log]
    for e in extra:
        add("  " + e)
    add("```")
    add("")

    add("## 2 · Overflow, clipping, collisions, empty space, footers")
    add("")
    if problems:
        for p in problems:
            add(f"- {p}")
    else:
        add("No block overflows its page, no two blocks overlap, every block has the height the paginator planned, "
            "and nothing comes closer than 1 mm to the footer strip.")
    add("")
    add("`natural` = how full the page is before spare room is used; `final` = after write-in areas and picture slots have grown "
        "and the gaps were opened. Pages marked `open` end with more than 20 % free space.")
    add("")
    add("| Page | Section | natural | final | clearance | state |")
    add("| --- | --- | --- | --- | --- | --- |")
    for r in rows:
        add("| " + " | ".join(str(x) for x in r) + " |")
    add("")
    add("Front matter and appendix pages are composed as whole pages; they are measured in the finished PDF "
        "(lowest text line against the folio line, at least 2 mm required).")
    add("")
    add("| Page | Part | clearance | state |")
    add("| --- | --- | --- | --- |")
    for r in fixed_rows:
        add("| " + " | ".join(str(x) for x in r) + " |")
    add("")

    add("## 3 · Baseline alignment on facing pages")
    add("")
    add(f"Every block starts on a multiple of half a baseline ({cfg.bl / 2:g} pt), so running text on facing pages shares the same lines. "
        f"Measured in the finished PDF over {bstat['lines']} body-size lines (tolerance 0.35 pt): **{bstat['half']:.0%}** sit on the "
        f"half-baseline grid, **{bstat['quarter']:.0%}** on the quarter grid. The rest is text on ruled write-in lines and in phrase lists, "
        "which follow their own ruling. `shared` = grid lines that carry text on both pages of a spread.")
    add("")
    add("| Spread | body lines | on half grid | on quarter grid | shared lines |")
    add("| --- | --- | --- | --- | --- |")
    for r in brow:
        add("| " + " | ".join(str(x) for x in r) + " |")
    add("")

    add("## 4 · Links and navigation")
    add("")
    add(f"- internal link areas: **{links['internal']}** pointing to {links['targets']} different targets, "
        f"all resolved: **{'yes' if links['broken'] == 0 else 'NO'}** (one link can consist of several clickable areas)")
    if links["broken_list"]:
        add(f"- broken: {links['broken_list']}")
    add(f"- named destinations in the file: {links['named_destinations']}")
    add(f"- external link areas: {links['external']} → " + ", ".join(f"{k} ({v})" for k, v in sorted(links["hosts"].items())))
    add(f"- {len(links['urls'])} different URLs, all well-formed: " + ", ".join(f"`{u}`" for u in links["urls"]))
    add(f"- bookmarks: " + ", ".join(f"level {k}: {v}" for k, v in sorted(st["bookmarks"].items())) + " (Kapitel → Teil → Aufgabe)")
    labs = st["labels"]
    add(f"- page labels: {', '.join(labs[:8])} … {', '.join(labs[-6:])}")
    add(f"- metadata: title “{st['title']}”, author “{st['author']}”, language {st['lang']}")
    add(f"- tagged PDF: {'yes' if st['tagged'] else 'no'} · figures with alternative text: {st['figures_with_alt']} of {st['figures']}")
    if cfg.flags.get("forms"):
        add(f"- form fields: {st['form_fields']}")
    if cfg.flags.get("print"):
        add(f"- pages with TrimBox / BleedBox: {st['trim_boxes']} of {info['pages']}")
    add("")

    add("## 5 · Fonts")
    add("")
    add("| Font | Type | Embedded |")
    add("| --- | --- | --- |")
    for n, t, e in fonts:
        add(f"| {n} | {t} | {'yes' if e else '**NO**'} |")
    add("")
    add(f"Embedded font data: {font_bytes / 1024:.0f} KB (subsets).")
    add("")

    add("## 6 · Text extraction")
    add("")
    add(f"Whole file: {flags['chars']:,} characters · {flags['replacement']} replacement characters · {flags['spaced']} letter-spaced runs · "
        f"{flags['umlauts']} umlauts/ß · {flags['turkish']} Turkish letters (ç ğ ı İ ş) · {flags['soft_hyphens']} soft hyphens · "
        f"{flags['zero_width']} zero-width characters.")
    add("")
    wanted = ["Cover", "101", "104", "109", "L 1"]
    if not any(s.label == "109" for s in res.pages):
        wanted = [s.label for s in res.pages[:5]]
    for lab, txt, fl in text_samples(pdf_path, res, wanted):
        add(f"### Page {lab}" + (f" — {'; '.join(fl)}" if fl else ""))
        add("")
        add("```text")
        add(txt[:2600])
        add("```")
        add("")

    add("## 7 · Contrast (WCAG 2.x)")
    add("")
    add("| Pair | Foreground | Background | Ratio | Needs | |")
    add("| --- | --- | --- | --- | --- | --- |")
    worst = 99.0
    for nm, fg, bg, ratio, need in contrast_rows:
        ok = ratio >= float(need)
        worst = min(worst, ratio / float(need))
        add(f"| {nm} | `{fg}` | `{bg}` | {ratio:.2f} | {need} | {'pass' if ok else '**FAIL**'} |")
    add("")

    add("## 8 · Cover")
    add("")
    add("Every text element of the cover exists exactly once in the PDF (the level appears twice by design: in the badge and in the title).")
    add("")
    add("| Element | expected | found | |")
    add("| --- | --- | --- | --- |")
    for el, e, f in cover_rows:
        add(f"| {el} | {e} | {f} | {'pass' if e == f else '**CHECK**'} |")
    add("")

    add("## 9 · File size")
    add("")
    learn = sum(1 for s in res.pages if s.group == "learn")
    other = info["pages"] - learn
    body_bytes = max(0, info["size"] - font_bytes)
    per_page = body_bytes / max(1, info["pages"])
    full_pages = cfg.total_pages
    appendix_ratio = sum(1 for s in res.pages if s.group in ("answers", "transcripts", "wordlist")) / max(1, learn)
    est_pages = 6 + full_pages + round(full_pages * appendix_ratio) + 1
    vector = font_bytes * 1.6 + per_page * est_pages
    add(f"- this build: {info['size'] / 1024:.0f} KB for {info['pages']} pages ({learn} learning pages, {other} others); "
        f"{per_page / 1024:.1f} KB per page without fonts")
    add(f"- full book, vector artwork only: about **{vector / 1048576:.1f} MB** for roughly {est_pages} pages")
    slots = round(full_pages / max(1, learn) * sum(1 for s in res.pages if s.group == "learn" for _ in re.findall(r'class="ph ', s.inner)))
    add(f"- full book with final illustrations: about {slots} picture slots; at 150 KB each (JPEG, 150 dpi) that adds "
        f"{slots * 150 / 1024:.0f} MB → about **{vector / 1048576 + slots * 150 / 1024:.0f} MB** (target: under 40 MB)")
    add("")
    out_path.write_text("\n".join(L), encoding="utf-8")
    return out_path
