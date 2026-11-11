# Demo build · A2 · Kapitel 5 „Wohnen“ + Zwischenstation 2

Built from this repository, nothing edited by hand. Rebuild everything with the commands below;
fresh output goes to `dist/`.

| Folder | What | Command |
| --- | --- | --- |
| `pdf/300-pages-a2-en.pdf` | English edition: cover, imprint, contents, how the book works, the people, Kapitel 5 (pp. 101–124), Zwischenstation 2 (pp. 197–200), answer key, transcripts, word list, sales page | `python build.py --level a2 --lang en --chapters 5,Z2 --preview` |
| `pdf/300-pages-a2-tr.pdf` | the same book with Turkish explanations | `… --lang tr …` |
| `pdf/300-pages-a2-en-sample.pdf`, `…-tr-sample.pdf` | free sample: 11 learning pages, one page each of answer key and word list, sales page | `… --sample` |
| `pdf/300-pages-a2-en-print.pdf` | 3 mm bleed, crop marks, TrimBox and BleedBox | `… --print` |
| `pdf/300-pages-a2-en-forms.pdf` | write-in lines, gaps and tick boxes as fillable fields | `… --forms` |
| `covers/300-pages-lineup-en.png`, `…-tr.png` | all six levels side by side | `python build.py --covers` |
| `covers/…-cover-store-1600x2560.png` | store cover, 5 : 8 | `python build.py --covers` |
| `covers/…-cover-square-3000x3000.png` | square cover for social media | `python build.py --covers` |
| `covers/…-cover-a4-1654x2339.png` | the book cover as an image | `python build.py --covers` |
| `pages-en/`, `pages-tr/` | every page of the demo as PNG (100 dpi, reduced to 256 colours to keep the repository small) plus contact sheets `_sheet-1…3.png` | `--preview` |

`python build.py --covers` writes these cover files for all six levels in both languages.

QA: [`../docs/QA-REPORT.md`](../docs/QA-REPORT.md). Open the PDFs in a viewer that shows bookmarks
and page labels (Acrobat, Preview, PDF Expert) to see the navigation; the page numbers in the
viewer match the printed folios.
