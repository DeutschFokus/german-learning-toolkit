"""Every manuscript text block (paragraph, list item, heading, table cell) must occur in the PDF text.
Comparison ignores case, whitespace, hyphens/soft hyphens and the list/number markers added by layout."""
import html
import re
import subprocess
import sys
from pathlib import Path

from markdown_it import MarkdownIt

BOOK = Path(__file__).parent.parent
md = MarkdownIt("commonmark").enable("table").enable("strikethrough")
norm = lambda s: re.sub(r"[\s\-­]", "", html.unescape(s)).casefold()


def blocks():
    for f in sorted(BOOK.glob("[0-9]*.md")):
        h = md.render(f.read_text(encoding="utf-8"))
        for m in re.finditer(r"<(p|li|h[1-6]|td|th|blockquote)>(.*?)</\1>", h, re.S):
            inner = m.group(2)
            if re.search(r"<(p|li|ul|ol)>", inner):
                continue
            t = re.sub(r"<[^>]+>", "", inner).strip()
            t = re.sub(r"^[✗○✓] ", "", t)
            t = re.sub(r"^Kapitel (\d+) – ", "", t)                 # opener splits "Kapitel N" from its title
            t = re.sub(r"^(\d+) · ", "", t)                          # entry numbers become "001" in the rail
            label = re.match(r"^(Mini-Test:|Upgrade:|Regel(?: –[^:]*)?:|Warum\?|Achtung:|Tipp:|Merksatz:|\d+–\d+ Punkte:)\s*", t)
            if label:                       # run-in labels are typeset (and extracted) apart from their text
                yield f.name, label.group(1)
                t = t[label.end():]
            if len(norm(t)) >= 2:
                yield f.name, t


pdf_text = subprocess.run(["pdftotext", "-raw", "-enc", "UTF-8", sys.argv[1], "-"], capture_output=True, text=True).stdout
hay = norm(pdf_text)
missing = [(f, t) for f, t in blocks() if norm(t) not in hay]
total = sum(1 for _ in blocks())
print(f"{sys.argv[1].split('/')[-1]}: {total - len(missing)}/{total} manuscript blocks found")
for f, t in missing:
    print(f"  MISSING [{f}] {t[:100]!r}")
