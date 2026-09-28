"""Interior builder: Markdown chapters -> designed HTML -> headless Chrome PDF.

Two passes: the first render locates every anchor (named destinations) so the
table of contents can print real page numbers; the second render is final.
Writes <out>/interior-raw.pdf and <out>/anchors.json for finish.py.
Usage: python3 build_book.py OUTDIR
"""
import difflib
import html
import json
import re
import subprocess
import sys
from pathlib import Path

import pymupdf
from markdown_it import MarkdownIt

from hyphenate import hyphenate_html, protect_suffixes

HERE = Path(__file__).parent
BOOK = HERE.parent
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
md = MarkdownIt("commonmark").enable("table").enable("strikethrough")

# Display copy added by the design (not part of the manuscript). Change here.
IMPRINT = "DeutschFokus"
SERIES = "Fehlerwerkstatt Deutsch · Band B1"
TITLE, SUBTITLE = "100 B1-Fehler", "Korrigiere sie vor B2"
AUDIENCE = "Für Lernende auf Niveau B1, die den Sprung zu B2 schaffen wollen"
YEAR = 2026
TEASERS = {
    1: "Ein Satzteil vorne – dann sofort das Verb.",
    2: "Nach weil, dass und ob wartet das Verb bis zum Schluss.",
    3: "Der Artikel bestimmt alles, was danach kommt.",
    4: "Wo oder wohin? Wen oder wem? Zwei Fragen statt zehn Tabellen.",
    5: "Eine Frage entscheidet: Hat der Artikel die Arbeit schon gemacht?",
    6: "Lerne Chunks statt einzelner Wörter.",
    7: "Nicht die Form ist schwer, sondern die Wahl der Zeit.",
    8: "Ein kleines Wort entscheidet, wie fortgeschritten du klingst.",
    9: "wann fragt, wenn stellt eine Bedingung, als erzählt, ob wartet auf Ja oder Nein.",
    10: "Genus vom Nomen, Fall aus dem Relativsatz, Verb ans Ende.",
    11: "Nicht nur richtig, sondern natürlich.",
}
LABELS = {"Grammatikfehler": "lab-err", "Korrekt, aber unnatürlich": "lab-unnat", "Stil": "lab-style"}

PENCIL = ('<svg class="ico" viewBox="0 0 24 24"><path d="M4 20 L5.2 15.2 L15.8 4.6 a1.9 1.9 0 0 1 2.7 0 l.9 .9 a1.9 1.9 0 0 1 0 2.7 '
          'L8.8 18.8 Z M13.8 6.6 l3.6 3.6 M4 20 l4.8 -1.2" /></svg>')
ARROW_UP = '<svg class="ico" viewBox="0 0 24 24"><path d="M6 18 L18 6 M9 6 H18 V15" /></svg>'


def esc(s):
    return html.escape(s, quote=False)


def inline(s):
    return md.renderInline(s)


def xref(h):
    """Link "Fehler 60" and "Kapitel 4" (incl. "Kapitel 1, 2 und 4") in text, never inside tags."""
    def fehler(m):
        n = int(m.group(1))
        return f'<a class="xref" href="#f{n:03d}">Fehler {n}</a>' if 1 <= n <= 100 else m.group(0)

    def kapitel(m):
        nums = re.sub(r"\d+", lambda d: f'<a class="xref" href="#kap{d.group(0)}">{d.group(0)}</a>'
                      if 1 <= int(d.group(0)) <= 11 else d.group(0), m.group(1))
        return "Kapitel " + nums
    out = []
    for part in re.split(r"(<[^>]+>)", h):
        if not part.startswith("<"):
            part = re.sub(r"\bFehler (\d{1,3})\b", fehler, part)
            part = re.sub(r"\bKapitel ((?:\d{1,2}(?:, | und ))*\d{1,2})\b", kapitel, part)
        out.append(part)
    return "".join(out)


def prose(h):
    return hyphenate_html(xref(h))


def role(h, cls="role"):
    """Turn the leading <strong>Label</strong> of a block into a styled run-in label (text unchanged)."""
    return re.sub(r"<p><strong>(.*?)</strong>", rf'<p><span class="{cls}">\1</span>', h, count=1)


# ---------------------------------------------------------------- entries
def mark_diff(wrong, right):
    """Word-level diff: wavy-underline what changes in the wrong line, highlight the fix in the right line."""
    w, r = wrong.split(" "), right.split(" ")
    sm = difflib.SequenceMatcher(a=w, b=r, autojunk=False)
    if sm.ratio() < .45:
        return esc(wrong), esc(right)
    ow, orr = [], []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        a, b = " ".join(w[i1:i2]), " ".join(r[j1:j2])
        if op == "equal":
            ow.append(esc(a)); orr.append(esc(b))
            continue
        if a:
            ow.append(f'<span class="err">{esc(a)}</span>')
        if b:
            orr.append(f'<span class="fix">{esc(b)}</span>')
    return " ".join(x for x in ow if x), " ".join(x for x in orr if x)


def entry(block):
    blocks = [b.strip() for b in block.strip().split("\n\n") if b.strip() and b.strip() != "---"]
    num, title = re.match(r"### (\d+) · (.*)", blocks[0]).groups()
    num = int(num)
    label = blocks[1].strip("`")
    wrong_sym, wrong = blocks[2][0], blocks[2][2:]
    right = blocks[3][2:]
    right_plain = right[2:-2] if right.startswith("**") and right.endswith("**") else right
    if any(c in wrong + right_plain for c in "*`_["):
        w_html, r_html = inline(wrong), inline(right_plain)
    else:
        w_html, r_html = mark_diff(wrong, right_plain)
    groups, cur = {"a": [], "b": []}, "a"
    for b in blocks[4:]:
        if b.startswith("**Beispiele**"):
            cur = "b"
        kind = ("warum" if b.startswith("**Warum?**") else "regel" if b.startswith("**Regel") else
                "bsp" if b.startswith("**Beispiele**") else "note" if b.startswith(("**Achtung:**", "**Tipp:**")) else
                "mini" if b.startswith("**Mini-Test:**") else "up" if b.startswith("**Upgrade:**") else "cont")
        groups[cur].append((kind, b))

    def render(kind, b):
        h = md.render(b)
        if kind == "warum":
            return f'<div class="warum">{prose(role(h))}</div>'
        if kind == "regel":
            return f'<div class="regel">{prose(role(h, "role role-regel"))}</div>'
        if kind == "cont":
            return f'<div class="cont">{xref(h)}</div>'
        if kind == "bsp":
            return f'<div class="bsp">{role(h)}</div>'
        if kind == "note":
            return f'<div class="note">{prose(role(h))}</div>'
        if kind == "mini":
            return (f'<div class="mini"><div class="call-head">{PENCIL}</div><div class="call-body">{xref(role(h))}'
                    f'<div class="answer-line"></div></div></div>')
        if kind == "up":
            return f'<div class="up"><div class="call-head">{ARROW_UP}</div><div class="call-body">{xref(role(h))}</div></div>'

    # merge continuation blocks (lists/tables after "Regel:") into the preceding block
    def join(items):
        out = []
        for kind, b in items:
            h = render(kind, b)
            if kind == "cont" and out:
                out[-1] = out[-1][:-6] + h + "</div>"
            else:
                out.append(h)
        return "".join(out)

    sym_ok = "✓"
    card = (f'<div class="card {"k-maybe" if wrong_sym == "○" else "k-wrong"}">'
            f'<p class="c-line c-bad"><span class="c-mark">{wrong_sym}</span><span class="c-text">{w_html}</span></p>'
            f'<p class="c-line c-good"><span class="c-mark">{sym_ok}</span><span class="c-text"><strong>{r_html}</strong></span></p></div>')
    head = (f'<div class="rail"><div class="enum">{num:03d}</div>'
            f'<div class="lab {LABELS[label]}"><i></i>{esc(label)}</div></div>')
    return num, title, (f'<section class="entry" id="f{num:03d}">'
                        f'<div class="eg eg-a">{head}<div class="main"><h3>{inline(title)}</h3>{card}{join(groups["a"])}</div></div>'
                        f'<div class="eg eg-b"><div class="rail"></div><div class="main">{join(groups["b"])}</div></div>'
                        f'</section>')


# ---------------------------------------------------------------- tables
COLW = {"Kasus": "12%", "Nr.": "7%", "Kapitel": "10%", "Fehler": "11%", "Genus": "13%", "Typ": "13%", "Verb": "13%",
        "Chunk": "30%", "Beispiel": None, "Endung": "36%", "Woche": "12%"}


def tables(h, link_cols=False):
    def fix(m):
        t = m.group(0)
        heads = [re.sub(r"<[^>]+>", "", x) for x in re.findall(r"<th(?:\s[^>]*)?>(.*?)</th>", t, re.S)]
        n = len(heads)
        widths = [COLW.get(x) for x in heads]
        if n >= 5 and not widths[0]:
            widths[0] = "13%"
        if "Woche" in heads:   # "Kapitel" holds "9, 10 und 11" here, not a single number
            widths[heads.index("Kapitel")] = "22%"
        col = "".join(f'<col style="width:{w}">' if w else "<col>" for w in widths)
        t = t.replace("<table>", f'<table class="t{n}"><colgroup>{col}</colgroup>', 1)

        def row(rm):
            cells = re.findall(r"<td[^>]*>(.*?)</td>", rm.group(0), re.S)
            out = []
            for i, c in enumerate(cells):
                plain = re.sub(r"<[^>]+>", "", c).strip()
                if re.fullmatch(r"[\d, ]+", plain):
                    if link_cols and i < n and heads[i] in ("Fehler", "Kapitel"):
                        pre = "f" if heads[i] == "Fehler" else "kap"
                        c = re.sub(r"\d+", lambda d: f'<a class="xref" href="#{pre}{int(d.group(0)):03d}">{d.group(0)}</a>'
                                   if pre == "f" else f'<a class="xref" href="#kap{d.group(0)}">{d.group(0)}</a>', plain)
                    out.append(f'<td class="num">{c}</td>')
                else:
                    out.append(f"<td>{c}</td>")
            return "<tr>" + "".join(out) + "</tr>"
        t = re.sub(r"<tr>\s*(?:<td.*?</td>\s*)+</tr>", row, t, flags=re.S)
        for i, hd in enumerate(heads):
            if hd in ("Nr.", "Kapitel", "Fehler"):
                t = re.sub(rf"<th(?:\s[^>]*)?>{re.escape(hd)}</th>", f'<th class="num">{hd}</th>', t, count=1)
        return t
    return re.sub(r"<table>.*?</table>", fix, h, flags=re.S)


# ---------------------------------------------------------------- parts
def chapter(path):
    text = path.read_text(encoding="utf-8")
    k, ktitle = re.match(r"# Kapitel (\d+) – (.*)", text).groups()
    k = int(k)
    sol_i = text.find("\n## Lösungen zu Kapitel")
    body, sol = text[:sol_i], text[sol_i:]
    parts = re.split(r"\n(?=### )", body)
    intro = parts[0].split("\n", 1)[1]
    entries = [entry(p) for p in parts[1:]]
    first, last = entries[0][0], entries[-1][0]

    ih = md.render(intro.strip().removesuffix("---"))
    ih = re.sub(r"<blockquote>\s*(.*?)</blockquote>", lambda m: f'<aside class="merksatz">{role(m.group(1), "role")}</aside>', ih, flags=re.S)
    problem, _, kern = ih.partition("<h2>Die Kernregel</h2>")
    intro_html = (f'<div class="intro prose">{prose(problem)}</div>'
                  + (f'<div class="kern"><h2>Die Kernregel</h2>{tables(xref(kern))}</div>' if kern else ""))

    toc_items = "".join(f'<li><a href="#f{n:03d}"><span class="oe-n">{n:03d}</span><span class="oe-t">{inline(t)}</span></a></li>'
                        for n, t, _ in entries)
    opener = f"""<section class="opener" id="kap{k}" style="--c: var(--ch{k}); --ct: var(--ch{k}-tint)">
  <div class="op-band"><div class="op-eyebrow">Kapitel {k}</div><div class="op-num">{k}</div></div>
  <div class="op-body">
    <h1 class="op-title">{inline(ktitle)}</h1>
    <p class="op-teaser">{esc(TEASERS[k])}</p>
    <p class="op-range">Fehler {first}–{last}</p>
    <ol class="op-list">{toc_items}</ol>
  </div></section>"""
    sol_html = md.render(sol)
    sol_html = sol_html.replace("<h2>", '<h2 class="sol-h">', 1)
    content = (f'<article class="part chap" style="page: kap{k}; --c: var(--ch{k}); --ct: var(--ch{k}-tint)">{intro_html}'
               + "".join(e[2] for e in entries) + f'<section class="solutions">{xref(sol_html)}</section></article>')
    meta = {"k": k, "title": ktitle, "first": first, "last": last, "entries": [(n, t) for n, t, _ in entries]}
    return f'<div class="opener-wrap">{opener}</div>{content}', meta


def part_header(eyebrow, title, anchor):
    return (f'<header class="part-head" id="{anchor}"><div class="eyebrow">{esc(eyebrow)}</div>'
            f'<h1>{inline(title)}</h1></header>')


def vorwort():
    text = (BOOK / "01-vorwort.md").read_text(encoding="utf-8")
    h = md.render(text.split("\n", 1)[1])
    # Label table -> visual key (same words).
    def key(m):
        rows = re.findall(r"<tr>\s*<td><code>(.*?)</code></td>\s*<td>(.*?)</td>\s*</tr>", m.group(0), re.S)
        heads = re.findall(r"<th>(.*?)</th>", m.group(0))
        return (f'<div class="key"><div class="key-row key-head"><span>{heads[0]}</span><span>{heads[1]}</span></div>' + "".join(
            f'<div class="key-row"><div class="lab {LABELS[l]}"><i></i>{l}</div><p>{d}</p></div>' for l, d in rows) + "</div>")
    h = re.sub(r"<table>.*?</table>", key, h, count=1, flags=re.S)
    h = re.sub(r"<ul>\s*<li><strong>✗</strong>.*?</ul>",
               lambda m: '<div class="symkey">' + "".join(
                   f'<div class="sk sk-{c}"><span class="c-mark">{s}</span><span>{t}</span></div>'
                   for s, t, c in re.findall(r"<li><strong>(.)</strong> (– [^<]*)</li>", m.group(0)) and
                   [(s, t, {"✗": "bad", "○": "maybe", "✓": "good"}[s]) for s, t in re.findall(r"<li><strong>(.)</strong> (– [^<]*)</li>", m.group(0))]) + "</div>",
               h, flags=re.S)
    return (f'<article class="part" style="page: vorwort">{part_header("Vor dem Start", "Vorwort", "vorwort")}'
            f'<div class="prose">{prose(h)}</div></article>')


def test(path, anchor, eyebrow, page, split_nachwort=False):
    text = path.read_text(encoding="utf-8")
    nach = ""
    if split_nachwort:
        text, nach = text.split("\n# Nachwort", 1)
        nach = "# Nachwort" + nach
    title = re.match(r"# (.*)", text).group(1)
    body = text.split("\n", 1)[1]
    exam, _, sol = body.partition("\n---\n")
    eh = md.render(exam)
    eh = re.sub(r"<ol>(.*?)</ol>", lambda m: '<ol class="exam">' + re.sub(
        r"<li>(.*?)</li>", r'<li><span class="q">\1</span><span class="aline"></span></li>', m.group(1), flags=re.S) + "</ol>",
                eh, flags=re.S)
    eh = eh.replace("<p><strong>Achtung:</strong>", '<p class="exam-note"><strong>Achtung:</strong>')
    sh = tables(md.render(sol), link_cols=True)
    sh = re.sub(r"<p><strong>(\d+–\d+ Punkte:)</strong>", r'<p class="score"><span class="score-k">\1</span>', sh)
    sh = sh.replace("<p><strong>Tipp:</strong>", '<p class="tipp"><strong>Tipp:</strong>')
    cut = sh.find("<h2>Auswertung</h2>")
    cut = cut if cut != -1 else sh.find('<p class="score">')
    if cut != -1:
        sh = sh[:cut] + '<div class="auswertung">' + sh[cut:] + "</div>"
    out = (f'<article class="part test" style="page: {page}">{part_header(eyebrow, title, anchor)}'
           f'<div class="exam-intro">{prose(eh)}</div>'
           f'<section class="sol-page"><div class="sol-banner"><span>Lösungen</span><span class="sol-hint">Erst nach dem Test lesen</span></div>'
           f'{prose(sh)}</section></article>')
    if nach:
        nh = md.render(nach.split("\n", 1)[1])
        nh = tables(nh)
        out += (f'<article class="part" style="page: nachwort">{part_header("Nach dem Test", "Nachwort: Wie geht es weiter?", "nachwort")}'
                f'<div class="prose">{prose(nh)}</div></article>')
    return out


def anhang():
    text = (BOOK / "15-anhang.md").read_text(encoding="utf-8")
    title = re.match(r"# (.*)", text).group(1)
    h = tables(md.render(text.split("\n", 1)[1]))
    return (f'<article class="part anhang" style="page: anhang">{part_header("Zum Nachschlagen", title, "anhang")}'
            f'{xref(h)}</article>')


# ---------------------------------------------------------------- front matter
def front(chapters, pages=None):
    pg = lambda a: str(pages.get(a, "")) if pages else "000"
    toc_rows = [("", "Vorwort", "vorwort", "")]
    toc_rows.append(("", "Einstufungstest", "einstufungstest", "25 Sätze"))
    for c in chapters:
        toc_rows.append((str(c["k"]), inline(c["title"]), f"kap{c['k']}", f"Fehler {c['first']}–{c['last']}"))
    toc_rows += [("", "Abschlusstest", "abschlusstest", "20 Sätze"), ("", "Nachwort", "nachwort", ""),
                 ("", "Anhang", "anhang", "Tabellen und Listen")]
    rows = "".join(
        f'<a class="toc-row{" toc-ch" if n else ""}" href="#{a}" style="--c: var(--ch{n or 1})">'
        f'<span class="toc-n">{n}</span><span class="toc-t">{t}{f"<small>{r}</small>" if r else ""}</span>'
        f'<span class="toc-lead"></span><span class="toc-p">{pg(a)}</span></a>' for n, t, a, r in toc_rows)
    return f"""
<section class="fm halftitle"><p class="ht-title">{TITLE}</p><p class="ht-sub">{SUBTITLE}</p></section>
<section class="fm blank"></section>
<section class="fm titlepage">
  <p class="tp-series">{esc(SERIES)}</p>
  <div class="tp-100">100</div>
  <h1 class="tp-title">B1-Fehler</h1>
  <p class="tp-sub">{SUBTITLE}</p>
  <p class="tp-aud">{AUDIENCE}</p>
  <p class="tp-imprint">{IMPRINT}</p>
</section>
<section class="fm colophon"><div class="col-body">
  <p><b>{TITLE} – {SUBTITLE}</b><br>{esc(SERIES)}</p>
  <p>1. Auflage {YEAR}<br>© {YEAR} {IMPRINT}. Alle Rechte vorbehalten.<br>ISBN 978-3-XXXX-XXXX-X</p>
  <p>Alle Beispielsätze in diesem Buch sind anonymisiert und neutralisiert. Sie beruhen auf Fehlermustern aus dem
  Deutschunterricht und lassen keine Rückschlüsse auf einzelne Personen zu.</p>
  <p>Gestaltung und Satz: {IMPRINT}<br>Schriften: Source Serif 4 und Inter (SIL Open Font License)</p>
</div></section>
<section class="fm toc" id="inhalt"><div class="eyebrow">Übersicht</div><h1>Inhalt</h1><nav class="toc-list">{rows}</nav></section>
<section class="fm blank"></section>"""


def running_heads(chapters):
    def pr(name, verso):
        verso = verso.replace('"', '\\"')
        return (f'@page {name}:left {{ @top-left {{ content: "{verso}"; }} }}\n'
                f'@page {name}:right {{ @top-right {{ content: "{TITLE}"; }} }}\n')
    css = pr("vorwort", "Vorwort") + pr("einst", "Einstufungstest") + pr("abschl", "Abschlusstest")
    css += pr("nachwort", "Nachwort") + pr("anhang", "Anhang")
    for c in chapters:
        css += pr(f"kap{c['k']}", f"Kapitel {c['k']} · {c['title']}")
    return css


WARMER = '<div class="font-warmer" aria-hidden="true">' + "".join(
    f'<span style="font-family:\'{f}\';font-weight:{w};font-style:{s}">Aa1→✓✗○</span>'
    for f, ws in (("B1 Serif Text", (400, 600, 700)), ("B1 Serif Display", (400, 600, 700, 900)),
                  ("B1 Sans", (400, 500, 600, 700, 800)), ("B1 Symbols", (400, 700)))
    for w in ws for s in ("normal", "italic") if s == "normal" or (f.startswith("B1 Serif") and w == 400)) + "</div>"


def build_html(pages=None):
    chaps = [chapter(p) for p in sorted(BOOK.glob("*-kapitel-*.md"))]
    metas = [m for _, m in chaps]
    body = (front(metas, pages) + vorwort()
            + test(BOOK / "02-einstufungstest.md", "einstufungstest", "Wo stehst du?", "einst")
            + "".join(h for h, _ in chaps)
            + test(BOOK / "14-abschlusstest.md", "abschlusstest", "Was hast du gelernt?", "abschl", split_nachwort=True)
            + anhang())
    body = protect_suffixes(body)
    css = ((HERE / "fonts.css").read_text() + (HERE / "tokens.css").read_text() + (HERE / "base.css").read_text()
           + (HERE / "book.css").read_text() + running_heads(metas))
    doc = (f'<!doctype html><html lang="de"><head><meta charset="utf-8"><title>{TITLE} – {SUBTITLE}</title>'
           f'<style>{css}</style></head><body>{WARMER}{body}</body></html>')
    return doc, metas


def render(doc, out_pdf):
    src = HERE / "book.html"
    src.write_text(doc, encoding="utf-8")
    subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={out_pdf}", "--virtual-time-budget=20000", src.as_uri()], check=True, capture_output=True)


def anchors(pdf):
    d = pymupdf.open(pdf)
    names = d.resolve_names()
    return {k: v["page"] + 1 for k, v in names.items() if v.get("page", -1) >= 0}


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    doc, metas = build_html()
    render(doc, out / "pass1.pdf")
    pages = anchors(out / "pass1.pdf")
    doc, metas = build_html(pages)
    render(doc, out / "interior-raw.pdf")
    final = anchors(out / "interior-raw.pdf")
    moved = {k: (pages[k], final.get(k)) for k in pages if pages[k] != final.get(k)}
    if moved:
        raise SystemExit(f"TOC page numbers shifted between passes: {moved}")
    json.dump({"anchors": final, "chapters": metas}, open(out / "anchors.json", "w"), ensure_ascii=False, indent=1)
    print("pages:", pymupdf.open(out / "interior-raw.pdf").page_count, "anchors:", len(final))


if __name__ == "__main__":
    main()
