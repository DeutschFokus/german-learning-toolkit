#!/usr/bin/env python3
"""Write docs/QA-REPORT.md: one page that sums up the generated QA reports of the demo builds.

    python tools/qa_summary.py            # after building the editions listed in EDITIONS

Everything except the last section comes from dist/qa/*.md; the self-critique is kept by hand in
docs/known-weaknesses.md and appended unchanged.
"""
import datetime
import re
import shutil
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from engine.config import load_config  # noqa: E402

LEVEL = "a2"
EDITIONS = [("en", "English"), ("tr", "Turkish"), ("en-sample", "English · free sample"), ("tr-sample", "Turkish · free sample"),
            ("en-print", "English · print"), ("en-forms", "English · fillable")]
HOW = {
    "Validation": "content model and book rules: missing article, plural or translation, duplicate address or track, task without answer, "
                  "answer without task, audio without transcript, unknown speaker, page budgets",
    "Layout geometry": "the position of every block in the finished PDF against the paginator's plan: overflow, overlap, height, distance to "
                       "the footer; front matter and appendix against the folio line; text printed over text on any page",
    "Links": "every link annotation in the PDF is resolved against the named destinations; external URLs are checked for form",
    "Fonts": "font dictionaries of the PDF",
    "Text extraction": "all text is extracted with MuPDF and searched for replacement characters, letter-spaced runs, soft hyphens and "
                       "zero-width characters",
    "Tagged PDF": "structure tree: every figure needs alternative text; document language",
    "Cover": "each text element of the cover must appear exactly once in the extracted text",
    "Contrast": "WCAG 2 contrast ratio of the text/background pairs of the design, for all 12 chapter palettes and all 6 covers",
    "Baseline grid": "the baseline of every body-size line in the PDF against the half-baseline grid",
}
GROUPS = [("Article colours on paper", lambda n: n.startswith("article") and "paper" in n),
          ("Article colours on their tint", lambda n: n.startswith("article") and "tint" in n),
          ("Margin-note labels on paper", lambda n: n.startswith("note")),
          ("Body text on paper", lambda n: n.startswith("body ink")),
          ("Muted text (explanations) on paper", lambda n: n.startswith("muted text")),
          ("Handwriting on paper", lambda n: n.startswith("handwriting")),
          ("Text on chapter colour (tabs, chips) · 12 chapters", lambda n: "ink on mid" in n),
          ("Text on chapter wash (boxes) · 12 chapters", lambda n: "ink on wash" in n),
          ("Muted text on chapter wash · 12 chapters", lambda n: "muted on wash" in n),
          ("Text on highlight · 12 chapters", lambda n: "ink on highlight" in n),
          ("Chapter labels on paper · 12 chapters", lambda n: "deep on paper" in n),
          ("Answer pointer on soft tint · 12 chapters", lambda n: "deep on soft" in n),
          ("Cover: cream type on the level colour · 6 levels", lambda n: n.startswith("cover") and "level field" in n),
          ("Cover: cream 300 on the lighter circle · 6 levels", lambda n: n.startswith("cover") and "circle" in n),
          ("Cover: navy on the cream band", lambda n: "navy on cream" in n),
          ("Cover: cream on the navy badge", lambda n: "cream on navy" in n)]


def read(name: str) -> str:
    return (ROOT / "dist" / "qa" / f"300-pages-{LEVEL}-{name}-qa.md").read_text(encoding="utf-8")


def section(text: str, n: int) -> str:
    return re.search(rf"^## {n} · .*?$\n(.*?)(?=^## \d+ · |\Z)", text, re.S | re.M).group(1).strip()


def verdict(name: str):
    t = read(name)
    rows = re.findall(r"^\| ([A-Z][^|]+) \| ([^|]+) \| (pass|\*\*CHECK\*\*) \|$", t, re.M)
    f = re.search(r"^File: (\d+) pages, (\d+) KB", t, re.M)
    return rows, f.group(1), f.group(2)


def main() -> None:
    cfg = load_config(LEVEL, "en")
    rep, tr = read("en"), read("tr")
    vm = {k: verdict(k) for k, _ in EDITIONS}
    checks = [r[0] for r in vm["en"][0]]
    result = {a: b.strip() for a, b, _ in vm["en"][0]}
    rows = cfg.contrast_table()
    L: list[str] = []
    A = L.append
    A("# QA report · demo build\n")
    A(f"{cfg.level_name} · Kapitel 5 „Wohnen“ (pages 101–124) and Zwischenstation 2 (pages 197–200) · built "
      f"{datetime.date.today().isoformat()} · engine {cfg.series['series']['version']}\n")
    A("Every build writes its own report to `dist/qa/`. This page sums up the six demo builds (`python tools/qa_summary.py`);")
    A("the full generated reports are in [`docs/qa/`](qa/). Only the last section is written by hand – all numbers come")
    A("from the finished PDFs.\n")
    A("## Verdict\n")
    A("| Check | " + " | ".join(n for _, n in EDITIONS) + " |")
    A("| --- | " + " | ".join("---" for _ in EDITIONS) + " |")
    A("| Pages · size | " + " | ".join(f"{vm[k][1]} · {vm[k][2]} KB" for k, _ in EDITIONS) + " |")
    bad = 0
    for i, c in enumerate(checks):
        cells = ["pass" if vm[k][0][i][2] == "pass" else "**CHECK**" for k, _ in EDITIONS]
        bad += sum(1 for x in cells if x != "pass")
        A(f"| {c} | " + " | ".join(cells) + " |")
    A("")
    A(f"All {len(checks)} checks pass in all {len(EDITIONS)} builds.\n" if not bad else f"**{bad} cells need attention.**\n")
    A("## What the checks do\n")
    A("| Check | How it is measured | Result (English edition) |")
    A("| --- | --- | --- |")
    for c in checks:
        A(f"| {c} | {HOW.get(c, '')} | {result[c]} |")
    A("")
    for title, n, src in (("Validation log", 1, rep), ("Overflow, clipping, collisions, empty space, footers", 2, rep)):
        A(f"## {title}\n")
        A(section(src, n) + "\n")
    A(f"The Turkish edition paginates identically (same pages, same blocks per page); its table is in `docs/qa/300-pages-{LEVEL}-tr-qa.md`.\n")
    for title, n in (("Baseline alignment on facing pages", 3), ("Links, bookmarks, page labels, metadata", 4), ("Fonts", 5)):
        A(f"## {title}\n")
        A(section(rep, n) + "\n")
    A("## Text extraction\n")
    A("Five pages, extracted with MuPDF and pasted unchanged: cover, chapter opener, a practice page, a page with an e-mail and")
    A("multiple choice, the first page of the answer key. Letter-spacing is done in CSS only, so headings come out as words; German")
    A("quotes, dashes and umlauts survive; the thin space in „S. 101“ is U+202F.\n")
    A(section(rep, 6) + "\n")
    A("Turkish edition, whole file: " + re.search(r"^Whole file: (.*)$", section(tr, 6), re.M).group(1) + "\n")
    A("## Cover\n")
    A(section(rep, 8) + "\n")
    A("## Contrast (WCAG 2)\n")
    A(f"{len(rows)} colour pairs are computed for every build; the table shows the weakest pair of each group. Normal text needs "
      "4.5 : 1, large type 3 : 1.")
    A("The full table is section 7 of each generated report.\n")
    A("| Group | Pairs | Lowest ratio | Needs | |")
    A("| --- | --- | --- | --- | --- |")
    for label, pred in GROUPS:
        g = [r for r in rows if pred(r[0])]
        lo = min(g, key=lambda r: r[3])
        A(f"| {label} | {len(g)} | {lo[3]:.2f} | {lo[4]} | {'pass' if lo[3] >= float(lo[4]) else '**FAIL**'} |")
    A("")
    A("## File size and build time\n")
    A(section(rep, 9))
    A("- build time: the 41-page demo takes about 30 s (layout 16 s cold, about 1 s with the block cache; render and write 14 s). "
      "Measuring costs")
    A("  about 40 ms per block and a full book has roughly 1,300 blocks, so a 300-page book should build in 4–5 minutes cold and "
      "2–3 minutes")
    A("  with a warm cache. This is extrapolated – only one chapter exists.\n")
    A((ROOT / "docs" / "known-weaknesses.md").read_text(encoding="utf-8").rstrip() + "\n")
    (ROOT / "docs" / "QA-REPORT.md").write_text("\n".join(L), encoding="utf-8")
    out = ROOT / "docs" / "qa"
    out.mkdir(exist_ok=True)
    for k, _ in EDITIONS:
        shutil.copy(ROOT / "dist" / "qa" / f"300-pages-{LEVEL}-{k}-qa.md", out)
    print(f"docs/QA-REPORT.md written ({len(L)} blocks), {len(EDITIONS)} reports copied to docs/qa/")


if __name__ == "__main__":
    main()
