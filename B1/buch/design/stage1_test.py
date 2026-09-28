"""Stage 1 proof: renders the design tokens on a specimen page plus two pages of
real chapter text on the grid. Output goes to the given directory."""
import re
import subprocess
import sys
from pathlib import Path

from markdown_it import MarkdownIt

from hyphenate import hyphenate_html, protect_suffixes

HERE = Path(__file__).parent
BOOK = HERE.parent
OUT = Path(sys.argv[1])
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
md = MarkdownIt("commonmark").enable("table")

tokens = (HERE / "tokens.css").read_text()
names = re.findall(r"--([\w-]+):\s*(#[0-9A-F]{6})", tokens)

swatch = lambda n, h: (f'<div class="sw"><div class="chip" style="background:var(--{n})"></div>'
                       f'<div class="chip grey" style="background:var(--{n})"></div>'
                       f'<div class="sw-n">{n}</div><div class="sw-h num">{h}</div></div>')
core = [n for n, _ in names if not n.startswith("ch")]
palette = "".join(swatch(n, h) for n, h in names if n in core)
chapters = "".join(f'<div class="cht" style="background:var(--ch{i})"><span>{i}</span></div>' for i in range(1, 12))
chapter_tints = "".join(f'<div class="cht tint" style="background:var(--ch{i}-tint);color:var(--ch{i})"><span>{i}</span></div>' for i in range(1, 12))

scale = [
    ("Display · Serif Display 51,2 pt", "h-display", "100 B1-Fehler"),
    ("H1 · Serif Display 25,6 pt", "s-h1", "Adjektivendungen"),
    ("H2 · Sans 11,2 pt Bold", "s-h2", "Die Kernregel"),
    ("Lead · Serif Display 13,1 pt", "s-lead", "Nach der im Dativ: -en"),
    ("Body · Serif Text 10,5 / 15,5 pt", "s-body", "Viele Lernende lassen die Endung einfach weg: <em>ein kompliziert Thema</em>. Das Ergebnis klingt sofort nach Lernenden."),
    ("Small · Serif Text 9,4 pt", "s-small", "Achtung: Im gesprochenen Deutsch hörst du manchmal weil mit Verb auf Position 2."),
    ("Caption · Sans 8,4 pt", "caption", "Kapitel 5 · Fehler 40–48"),
    ("Label · Sans 7,25 pt, +16 % Sperrung", "eyebrow", "Grammatikfehler · Korrekt, aber unnatürlich · Stil"),
]
scale_html = "".join(f'<div class="row"><div class="role caption">{r}</div><div class="{c}">{t}</div></div>' for r, c, t in scale)

ch5 = (BOOK / "07-kapitel-05-adjektivendungen.md").read_text(encoding="utf-8")
problem = ch5.split("## Das Problem")[1].split("## Die Kernregel")[0]
kern = ch5.split("## Die Kernregel")[1].split("> **Merksatz:**")[0]
entries = re.findall(r"### (\d+) · (.*?)\n\n`(.*?)`\n\n[✗○] (.*?)\n\n✓ \*\*(.*?)\*\*\n\n\*\*Warum\?\*\* (.*?)\n\n\*\*Regel:\*\* (.*?)\n", ch5)[:2]


def entry(n, title, label, wrong, right, warum, regel):
    r = md.renderInline
    return f"""<section class="entry">
  <div class="rail"><div class="enum num">{int(n):03d}</div><div class="eyebrow chip-l">{label}</div></div>
  <div class="main">
    <h3>{r(title)}</h3>
    <div class="card"><p class="w">{r(wrong)}</p><p class="r">{r(right)}</p></div>
    <p><span class="role-in">Warum?</span> {r(warum)}</p>
    <p><span class="role-in">Regel</span> {r(regel)}</p>
  </div></section>"""


body_pages = f"""
<article class="chapter">
  <h1>Adjektivendungen</h1>
  <h2>Das Problem</h2>
  <div class="prose measure">{hyphenate_html(md.render(problem))}</div>
  <h2>Die Kernregel</h2>
  <div class="measure-full">{md.render(kern)}</div>
  {''.join(entry(*e) for e in entries)}
  <div class="prose measure">{hyphenate_html(md.render(problem))}</div>
</article>"""

WARMER = '<div class="font-warmer" aria-hidden="true">' + "".join(
    f'<span style="font-family:\'{f}\';font-weight:{w};font-style:{s}">Aa1→✓</span>'
    for f, ws in (("B1 Serif Text", (400, 600, 700)), ("B1 Serif Display", (400, 600, 700, 900)), ("B1 Sans", (400, 500, 600, 700, 800)), ("B1 Symbols", (400, 700)))
    for w in ws for s in ("normal", "italic") if s == "normal" or (f.startswith("B1 Serif") and w == 400)) + "</div>"

html = f"""<!doctype html><html lang="de"><head><meta charset="utf-8"><title>Stufe 1 · Designsystem</title>
<style>{(HERE / 'fonts.css').read_text()}{tokens}{(HERE / 'base.css').read_text()}
@page specimen {{ @bottom-right {{ content: none; }} @top-right {{ content: none; }} }}
@page :left {{ @top-left {{ content: "Kapitel 5 · Adjektivendungen"; }} }}
@page :right {{ @top-right {{ content: "100 B1-Fehler"; }} }}
.specimen {{ page: specimen; break-after: page; }}
.specimen h1 {{ margin-bottom: var(--sp-2); }}
.specimen h2:first-of-type {{ margin-top: var(--sp-2); }}
.grid {{ display: grid; grid-template-columns: repeat(8, 1fr); gap: 2.5mm 2.5mm; }}
.sw .chip {{ height: 6.5mm; border-radius: var(--radius) var(--radius) 0 0; border: var(--hair) solid rgba(0,0,0,.08); }}
.sw .chip.grey {{ height: 3mm; filter: grayscale(1); border-radius: 0 0 var(--radius) var(--radius); border-top: 0; }}
.sw-n {{ font-family: var(--font-sans); font-size: 7pt; font-weight: 600; margin-top: 1mm; }}
.sw-h {{ font-family: var(--font-sans); font-size: 6.6pt; color: var(--ink-soft); }}
.chrow {{ display: grid; grid-template-columns: repeat(11, 1fr); gap: 1.5mm; margin-bottom: 1.5mm; }}
.cht {{ height: 8mm; border-radius: var(--radius); color: #fff; font-family: var(--font-display); font-size: 15pt; font-weight: 600; display: flex; align-items: flex-end; padding: 1mm 1.8mm; }}
.row {{ display: grid; grid-template-columns: 38mm 1fr; gap: 4mm; align-items: baseline; padding: 1mm 0; border-bottom: var(--hair) solid var(--rule); }}
.s-h1 {{ font-family: var(--font-display); font-size: var(--fs-h1); line-height: 1.1; font-weight: 600; }}
.s-h2 {{ font-family: var(--font-sans); font-size: 11.2pt; font-weight: 700; color: var(--primary); }}
.s-lead {{ font-family: var(--font-display); font-size: var(--fs-lead); font-weight: 600; }}
.s-small {{ font-size: var(--fs-small); line-height: 1.4; color: var(--ink-soft); }}
.feat {{ font-size: 11pt; line-height: 1.7; }}
.feat .k {{ font-family: var(--font-sans); font-size: 7pt; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--ink-soft); display: inline-block; width: 38mm; }}
.chapter h1 {{ margin-top: 0; }}
.measure {{ max-width: var(--measure); margin-left: calc(var(--rail-w) + var(--gutter)); }}
.chapter h2 {{ margin-left: calc(var(--rail-w) + var(--gutter)); }}
.chapter h1 {{ margin-left: calc(var(--rail-w) + var(--gutter)); }}
.entry {{ display: grid; grid-template-columns: var(--rail-w) var(--measure); column-gap: var(--gutter); padding: var(--sp-3) 0; border-top: var(--hair) solid var(--rule); break-inside: avoid; }}
.enum {{ font-family: var(--font-display); font-size: 30pt; line-height: .9; font-weight: 600; color: var(--accent); letter-spacing: -.01em; }}
.chip-l {{ margin-top: var(--sp-2); color: var(--wrong); font-size: 6.6pt; letter-spacing: .12em; }}
.card {{ margin: var(--sp-2) 0 var(--sp-3); border: var(--hair) solid var(--rule); border-radius: var(--radius); overflow: hidden; }}
.card p {{ margin: 0; padding: 2mm 4mm; font-size: 11.5pt; line-height: 1.4; }}
.card .w {{ background: var(--wrong-tint); color: var(--wrong-ink); text-decoration: line-through; text-decoration-color: var(--wrong); text-decoration-thickness: .8pt; }}
.card .r {{ background: var(--right-tint); color: var(--right-ink); font-weight: 600; }}
.role-in {{ font-family: var(--font-sans); font-size: var(--fs-label); font-weight: 700; letter-spacing: .14em; text-transform: uppercase; color: var(--primary); margin-right: 1.5mm; }}
</style></head><body>{WARMER}
<section class="specimen">
  <div class="eyebrow">Stufe 1 · Designsystem</div>
  <h1>Tokens & Typografie</h1>
  <h2>Farben <span class="caption">(unterer Streifen = Graustufen-Druck)</span></h2>
  <div class="grid">{palette}</div>
  <h2>Kapitelfarben 1–11 <span class="caption">(OKLCH L 0,50 · C 0,085)</span></h2>
  <div class="chrow">{chapters}</div><div class="chrow">{chapter_tints}</div>
  <div class="chrow" style="filter:grayscale(1)">{chapters}</div>
  <h2>Schriftgrade (große Terz, ×1,25)</h2>
  {scale_html}
  <h2>OpenType</h2>
  <div class="feat">
    <div><span class="k">Ligaturen</span>fi fl ff ffi · Auffinden, flach, Stoff</div>
    <div><span class="k">Kerning</span>AV Wa To Te Yo · „Tatort“</div>
    <div><span class="k">Mediävalziffern</span>1.600 Korrekturen · 36 Dokumente · 2019</div>
    <div><span class="k">Tabellenziffern</span><span class="num">1.600 · 36 · 2019 · 0123456789</span></div>
    <div><span class="k">Versal-Label</span><span class="eyebrow">Grammatikfehler · Kapitel 5</span></div>
    <div><span class="k">Symbole</span>→ ✓ ✗ ○ · – … „ “ · ß ä ö ü</div>
  </div>
</section>
{body_pages}
</body></html>"""

OUT.mkdir(parents=True, exist_ok=True)
(HERE / "stage1_test.html").write_text(protect_suffixes(html.split("<body>")[0]) if False else html.split("<body>")[0] + "<body>" + protect_suffixes(html.split("<body>", 1)[1]), encoding="utf-8")
pdf = OUT / "stage1_test.pdf"
subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                f"--print-to-pdf={pdf}", "--virtual-time-budget=10000", (HERE / "stage1_test.html").as_uri()],
               check=True, capture_output=True)
print(pdf)
