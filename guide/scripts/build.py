#!/usr/bin/env python3
"""Build "Your German Journey" into a print-ready, clickable PDF.

    python3 guide/scripts/build.py

What it does
------------
1. Reads guide/guide.md and guide/config.yml.
2. Expands the shortcodes used in guide.md:
       {{qr:KEY}}         QR code(s) for a resource (one per store for apps)
       {{resource:KEY}}   a full resource card (name, level, cost, QR code)
       {{link:KEY}}       a clickable link to the resource
       {{teacher}} {{brand}} {{version}} {{date}} {{title}}
   KEY refers to an entry under `resources:` in config.yml.
3. Converts the Markdown to HTML with pandoc (+ scripts/structure.lua,
   which numbers the parts and chapters).
4. Adds the cover and a table of contents, then prints the HTML to PDF
   with headless Chromium (scripts/render.cjs).
5. Reads the page of every heading back from that PDF, writes the page
   numbers into the table of contents and prints again.
6. Replaces Chromium's raw bookmarks with clean, numbered ones
   (Parts > Chapters > Sections), sets the PDF metadata and makes the
   bookmarks panel open by default.

Requirements: pandoc 2.11+, Node.js with the `playwright` package and its
Chromium, and the Python packages in guide/requirements.txt.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import segno
    import yaml
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import Fit
except ImportError as exc:  # pragma: no cover - friendly message only
    sys.exit(f"Missing Python package ({exc.name}). Run: pip install -r guide/requirements.txt")

GUIDE = Path(__file__).resolve().parent.parent
SCRIPTS = GUIDE / "scripts"
BUILD = GUIDE / "build"

ZONE_COLORS = {"blue": "#4f9bff", "green": "#34c17e", "purple": "#a97dff"}
LEVELS = [("A0", "blue"), ("A1", "blue"), ("A2", "blue"), ("B1", "green"),
          ("B2", "green"), ("C1", "purple"), ("C2", "purple")]


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def strip_tags(fragment: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", fragment))


def squash(text: str) -> str:
    """Normalise a title for comparison (no whitespace or emoji variation selectors, no case)."""
    return re.sub(r"[\s️]+", "", text).casefold()


def same_title(bookmark: str, heading: str) -> bool:
    # Chromium builds bookmark titles from the *rendered* text, so CSS
    # text-transform changes them and some titles come out duplicated.
    a, b = squash(bookmark), squash(heading)
    return a == b or b in a


def run(cmd: list[str]) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.stderr.write(result.stdout + result.stderr)
        sys.exit(f"Command failed: {' '.join(cmd)}")
    if result.stderr.strip():
        sys.stderr.write(result.stderr)


# --------------------------------------------------------------------------
# QR codes and resource cards
# --------------------------------------------------------------------------

def qr_svg(url: str) -> str:
    # Lowest error-correction level -> fewest, largest modules -> easiest to
    # scan at small print sizes (segno still boosts the level when it fits).
    qr = segno.make(url, error="l", micro=False)
    return qr.svg_inline(scale=1, border=0, dark="#14233a", omitsize=True)


def qr_targets(res: dict) -> list[tuple[str | None, str, str]]:
    """(platform caption, url, printed label) for every QR code of a resource."""
    if res.get("url"):
        return [(None, res["url"], res.get("label") or res["url"])]
    targets = []
    if res.get("ios"):
        targets.append(("iPhone", res["ios"], "App Store"))
    if res.get("android"):
        targets.append(("Android", res["android"], "Google Play"))
    return targets


def primary_url(res: dict) -> str:
    return res.get("url") or res.get("android") or res.get("ios")


def qr_group(res: dict) -> str:
    items = []
    for platform, url, label in qr_targets(res):
        plat = f'<span class="qr-plat">{esc(platform)}</span>' if platform else ""
        caption = esc(label).replace("/", "/<wbr>")  # long addresses wrap after a slash
        items.append(
            f'<a class="qr" href="{esc(url)}">{qr_svg(url)}'
            f'<span class="qr-cap">{plat}{caption}</span></a>'
        )
    cls = "qr-group multi" if len(items) > 1 else "qr-group"
    return f'<div class="{cls}">{"".join(items)}</div>'


def resource_card(key: str, res: dict) -> str:
    meta = []
    for label, field in (("Level", "level"), ("Cost", "cost"), ("Works on", "platforms")):
        if res.get(field):
            meta.append(f"<dt>{label}</dt><dd>{esc(res[field])}</dd>")
    icon = f'<span class="res-icon">{esc(res["icon"])}</span>' if res.get("icon") else ""
    return (
        f'<div class="res-card" id="res-{esc(key)}">'
        f'<div class="res-body">'
        f'<div class="res-name">{icon}<a href="{esc(primary_url(res))}">{esc(res["name"])}</a></div>'
        f'<dl class="res-meta">{"".join(meta)}</dl>'
        f'<p class="res-best">{esc(res.get("best", ""))}</p>'
        f"</div>"
        f'<div class="res-qr">{qr_group(res)}</div>'
        f"</div>"
    )


# --------------------------------------------------------------------------
# Markdown pre-processing (shortcodes)
# --------------------------------------------------------------------------

BLOCK_CODE = re.compile(r"^[ \t]*\{\{\s*(qr|resource)\s*:\s*([\w-]+)\s*\}\}[ \t]*$", re.M)
INLINE_CODE = re.compile(r"\{\{\s*(link|url)\s*:\s*([\w-]+)\s*\}\}")
VARIABLE = re.compile(r"\{\{\s*(teacher|brand|version|date|title|subtitle)\s*\}\}")


def expand_shortcodes(text: str, cfg: dict) -> str:
    resources = cfg["resources"]

    def lookup(key: str) -> dict:
        if key not in resources:
            sys.exit(f"guide.md refers to unknown resource '{key}' (add it to config.yml)")
        return resources[key]

    def block(match: re.Match) -> str:
        kind, key = match.groups()
        res = lookup(key)
        markup = qr_group(res) if kind == "qr" else resource_card(key, res)
        return f"\n```{{=html}}\n{markup}\n```\n"

    def inline(match: re.Match) -> str:
        kind, key = match.groups()
        res = lookup(key)
        url = primary_url(res)
        return url if kind == "url" else f"[{res['name']}]({url})"

    text = BLOCK_CODE.sub(block, text)
    text = INLINE_CODE.sub(inline, text)
    text = VARIABLE.sub(lambda m: str(cfg[m.group(1)]), text)
    leftover = re.findall(r"\{\{[^}]*\}\}", text)
    if leftover:
        sys.exit(f"Unknown shortcode(s) in guide.md: {', '.join(sorted(set(leftover)))}")
    return text


# --------------------------------------------------------------------------
# Cover and table of contents
# --------------------------------------------------------------------------

def smooth_path(points: list[tuple[float, float]]) -> str:
    """Catmull-Rom spline through the points, as an SVG cubic Bézier path."""
    d = [f"M{points[0][0]:.1f} {points[0][1]:.1f}"]
    for i in range(len(points) - 1):
        p0 = points[i - 1] if i > 0 else points[i]
        p1, p2 = points[i], points[i + 1]
        p3 = points[i + 2] if i + 2 < len(points) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}")
    return " ".join(d)


def journey_svg() -> str:
    pts = [(52 + i * 89, 206 - 27 * i - 2.2 * i * i) for i in range(len(LEVELS))]
    path = smooth_path(pts)
    nodes = []
    for (label, zone), (x, y) in zip(LEVELS, pts):
        nodes.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="19" fill="{ZONE_COLORS[zone]}" '
            f'stroke="#ffffff" stroke-width="3"/>'
            f'<text x="{x:.1f}" y="{y + 4.6:.1f}" class="node">{label}</text>'
        )
    zones = [
        ("BASIC USER", "blue", (pts[0][0] + pts[2][0]) / 2, 252),
        ("INDEPENDENT", "green", (pts[3][0] + pts[4][0]) / 2, 252),
        ("PROFICIENT", "purple", (pts[5][0] + pts[6][0]) / 2, 252),
    ]
    zone_text = "".join(
        f'<text x="{x:.1f}" y="{y}" class="zone" fill="{ZONE_COLORS[z]}">{t}</text>'
        for t, z, x, y in zones
    )
    ax, ay = pts[0]
    here = (
        f'<text x="{ax:.1f}" y="{ay - 52:.1f}" class="here">YOU ARE HERE</text>'
        f'<path d="M{ax:.1f} {ay - 44:.1f} L{ax:.1f} {ay - 27:.1f}" stroke="#f2b632" '
        f'stroke-width="2.5" stroke-linecap="round"/>'
        f'<path d="M{ax - 5:.1f} {ay - 33:.1f} L{ax:.1f} {ay - 26:.1f} L{ax + 5:.1f} {ay - 33:.1f}" '
        f'fill="none" stroke="#f2b632" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
    )
    return (
        '<svg class="journey" viewBox="0 0 640 262" xmlns="http://www.w3.org/2000/svg" '
        'role="img" aria-label="The path from A0 to C2">'
        f'<path d="{path}" fill="none" stroke="rgba(255,255,255,0.35)" stroke-width="4" '
        'stroke-dasharray="2 10" stroke-linecap="round"/>'
        f'{"".join(nodes)}{zone_text}{here}</svg>'
    )


def cover_html(cfg: dict) -> str:
    return f"""
<div class="cover">
  <div class="cover-top">
    <span class="cover-brand">{esc(cfg['brand'])}</span>
    <span class="cover-badge">German Learning Roadmap · A0 → C2</span>
  </div>
  <div class="cover-title">{esc(cfg['title'])}</div>
  <div class="cover-subtitle">{esc(cfg['subtitle'])}</div>
  {journey_svg()}
  <div class="cover-rule"></div>
  <div class="cover-quote-de">Sprache ist der Schlüssel zu neuen Welten.</div>
  <div class="cover-quote-en">Language is the key to new worlds.</div>
  <div class="cover-motto">“Small steps every day beat giant leaps once a week.”</div>
  <div class="cover-foot">
    <span>For motivated adult learners with 20–30 minutes per day</span>
    <span>Version {esc(cfg['version'])} · {esc(cfg['date'])}</span>
  </div>
</div>
"""


HEADING = re.compile(r"<h([1-6])((?:\s[^>]*)?)>(.*?)</h\1>", re.S)
ATTR = re.compile(r'([\w-]+)="([^"]*)"')


def parse_headings(body: str) -> list[dict]:
    heads = []
    for m in HEADING.finditer(body):
        level, attr_text, inner = int(m.group(1)), m.group(2), m.group(3)
        attrs = dict(ATTR.findall(attr_text))
        title_inner = re.sub(r'<span class="(?:part-num|ch-num)">.*?</span>', "", inner, flags=re.S)
        heads.append({
            "level": level,
            "id": attrs.get("id", ""),
            "classes": attrs.get("class", "").split(),
            "part": attrs.get("data-part"),
            "chapter": attrs.get("data-chapter"),
            "hint": attrs.get("data-hint", ""),
            "title": " ".join(strip_tags(title_inner).split()),
            "visible": strip_tags(inner),
        })
    return heads


def toc_html(heads: list[dict], pages: dict[str, int] | None) -> str:
    def page_of(h):
        return str(pages.get(h["id"], "")) if pages else "00"

    rows = []
    for h in heads:
        if h["level"] == 1 and h["part"]:
            hint = f'<span class="toc-hint">{esc(h["hint"])}</span>' if h["hint"] else ""
            rows.append(
                f'<li class="toc-part"><a href="#{h["id"]}">'
                f'<span class="toc-part-num">Part {h["part"]}</span>'
                f'<span class="toc-text">{esc(h["title"])}{hint}</span>'
                f'<span class="toc-page">{page_of(h)}</span></a></li>'
            )
        elif h["level"] == 2 and "notoc" not in h["classes"]:
            num = h["chapter"] or ""
            rows.append(
                f'<li class="toc-ch{" toc-extra" if not num else ""}"><a href="#{h["id"]}">'
                f'<span class="toc-num">{num}</span>'
                f'<span class="toc-text">{esc(h["title"])}</span>'
                f'<span class="toc-dots"></span>'
                f'<span class="toc-page">{page_of(h)}</span></a></li>'
            )
    return f"""
<section class="toc">
  <h1 class="toc-title" id="contents">Contents</h1>
  <p class="toc-note"><strong>How to navigate:</strong> every line below is clickable.
  Your PDF reader’s <em>bookmarks</em> panel is another quick way to jump between sections.</p>
  <ol class="toc-list">{"".join(rows)}</ol>
</section>
"""


def page_html(cfg: dict, css: str, cover: str, toc: str, body: str) -> str:
    footer = f"{cfg['title']} · {cfg['brand']}" if cfg.get("brand") else cfg["title"]
    css = css.replace("__FOOTER__", footer.replace('"', '\\"'))
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{esc(cfg['title'])}</title>
<style>
{css}
</style>
</head>
<body>
{cover}
{toc}
<main>
{body}
</main>
</body>
</html>
"""


# --------------------------------------------------------------------------
# PDF passes
# --------------------------------------------------------------------------

def render(html_path: Path, pdf_path: Path) -> None:
    run(["node", str(SCRIPTS / "render.cjs"), str(html_path), str(pdf_path)])


def flat_outline(reader: PdfReader) -> list:
    items = []

    def walk(nodes):
        for node in nodes:
            if isinstance(node, list):
                walk(node)
            else:
                items.append(node)

    walk(reader.outline)
    return items


def heading_positions(pdf_path: Path, heads: list[dict]) -> list[tuple[int, object]]:
    """Page index and destination for every heading, in document order."""
    reader = PdfReader(str(pdf_path))
    outline = flat_outline(reader)
    if len(outline) != len(heads):
        sys.exit(f"Bookmark count ({len(outline)}) does not match heading count ({len(heads)}).")
    positions = []
    for item, head in zip(outline, heads):
        if not same_title(item.title, head["visible"]):
            sys.exit(f"Bookmark/heading mismatch: {item.title!r} vs {head['visible']!r}")
        positions.append((reader.get_destination_page_number(item), item))
    return positions


def finish_pdf(pdf_path: Path, out_path: Path, heads: list[dict], cfg: dict) -> None:
    positions = heading_positions(pdf_path, heads)
    writer = PdfWriter(clone_from=str(pdf_path))
    writer._root_object.pop("/Outlines", None)  # drop Chromium's raw bookmarks

    part_item = chapter_item = None
    for head, (page_index, dest) in zip(heads, positions):
        level = head["level"]
        if level > 3:
            continue
        fit = Fit.xyz(left=dest.left, top=dest.top, zoom=None)
        if level == 1:
            title = f"Part {head['part']} · {head['title']}" if head["part"] else head["title"]
            part_item = writer.add_outline_item(title, page_index, fit=fit, bold=bool(head["part"]))
            chapter_item = None
            if not head["part"]:
                part_item = None
        elif level == 2:
            title = f"{head['chapter']}. {head['title']}" if head["chapter"] else head["title"]
            parent = None if "toplevel" in head["classes"] else part_item
            chapter_item = writer.add_outline_item(title, page_index, parent=parent, fit=fit)
        elif chapter_item is not None:
            writer.add_outline_item(head["title"], page_index, parent=chapter_item, fit=fit)

    writer.add_metadata({
        "/Title": cfg["title"],
        "/Subject": cfg["subtitle"],
        "/Author": cfg.get("brand") or cfg.get("teacher") or "",
        "/Keywords": "German, Deutsch lernen, learning guide, CEFR, A1, A2, B1, B2, C1, C2",
    })
    writer.page_mode = "/UseOutlines"
    with open(out_path, "wb") as fh:
        writer.write(fh)


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, help="output PDF (default: guide/<output from config.yml>)")
    args = parser.parse_args()

    for tool in ("pandoc", "node"):
        if not shutil.which(tool):
            sys.exit(f"'{tool}' is not installed or not on PATH.")

    cfg = yaml.safe_load((GUIDE / "config.yml").read_text(encoding="utf-8"))
    if not cfg.get("date"):
        cfg["date"] = dt.date.today().strftime("%B %Y")
    out_path = args.out or GUIDE / cfg["output"]
    BUILD.mkdir(exist_ok=True)

    source = (GUIDE / "guide.md").read_text(encoding="utf-8")
    (BUILD / "guide.pre.md").write_text(expand_shortcodes(source, cfg), encoding="utf-8")
    run([
        "pandoc", str(BUILD / "guide.pre.md"),
        "--from", "markdown", "--to", "html5",
        "--columns", "9999",
        "--lua-filter", str(SCRIPTS / "structure.lua"),
        "--output", str(BUILD / "body.html"),
    ])

    body = (BUILD / "body.html").read_text(encoding="utf-8")
    css = (GUIDE / "assets" / "style.css").read_text(encoding="utf-8")
    cover = cover_html(cfg)
    body_heads = parse_headings(body)

    def build_html(pages: dict | None) -> tuple[str, list[dict]]:
        toc = toc_html(body_heads, pages)
        doc = page_html(cfg, css, cover, toc, body)
        return doc, parse_headings(toc) + body_heads

    html_path = BUILD / "guide.html"
    draft_pdf = BUILD / "draft.pdf"

    # pass 1: placeholder page numbers in the table of contents
    doc, heads = build_html(None)
    html_path.write_text(doc, encoding="utf-8")
    render(html_path, draft_pdf)

    # pass 2..n: real page numbers (repeat until the layout is stable)
    for attempt in range(3):
        before = [p + 1 for p, _ in heading_positions(draft_pdf, heads)]
        pages = {h["id"]: p for h, p in zip(heads, before) if h["id"]}
        doc, heads = build_html(pages)
        html_path.write_text(doc, encoding="utf-8")
        render(html_path, draft_pdf)
        after = [p + 1 for p, _ in heading_positions(draft_pdf, heads)]
        if after == before:
            break
    else:
        sys.exit("Table of contents page numbers did not stabilise.")

    finish_pdf(draft_pdf, out_path, heads, cfg)
    pages_total = len(PdfReader(str(out_path)).pages)
    print(f"✔ {out_path.relative_to(GUIDE.parent)} — {pages_total} pages")


if __name__ == "__main__":
    main()
