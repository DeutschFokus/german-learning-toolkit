# Russian Grammar Mastery — personalized A1–A2 workbook

A print-ready PDF workbook of 1,480 sentence-based Russian grammar exercises (30 modules, 8 cumulative reviews),
each with its answer and a short explanation printed in small grey type directly under the writing line.

- **PDF:** `output/russian-grammar-mastery-workbook.pdf` (A4, 304 pages, bookmarks, clickable contents)
- **Exercise ledger:** `output/exercise-ledger.csv` (every exercise with type, stage, answer, explanation, source line)
- **Phase-2 sample:** `output/sample-pages-phase2.pdf`

## Structure
| Part | Modules | Reviews |
|---|---|---|
| I · Essential grammar foundations | 1–5 | R1 |
| II · Mastering all six cases | 6–12 | R2, R3 |
| III · Prepositions and grammatical relationships | 13–18 | R4, R5 |
| IV · Verb mastery | 19–26 | R6, R7 |
| V · Natural Russian sentence construction | 27–30 | R8 |

Exercise mix: missing endings & noun phrases 40.1% · conjugation & aspect 20.0% · unjumbling 15.0% ·
prepositions 10.0% · error correction & transformation 9.9% · advanced mixed 5.0%.

## Building
```
pip install weasyprint pymorphy3 pymorphy3-dicts-ru pypdf
python3 tools/build.py            # full PDF + ledger (runs all checks first)
python3 tools/build.py --qa       # checks only
python3 tools/qa_extra.py         # aspect / gender / variant consistency checks
python3 tools/build.py --only m07 # one module as its own PDF
```
Fonts: PT Serif, Inter and Noto Serif Display (Debian/Ubuntu: `fonts-paratype`, `fonts-noto-core`; Inter installed separately).
Content format and house rules: `tools/PRODUCTION.md`. Content files: `content/`.

## Checks run on every build
Exact counts per unit (40 / 35, total 1,480), duplicate questions, missing answers or explanations, mixed Latin/Cyrillic
letters, gap–answer alignment for ending exercises, unknown word forms (pymorphy3), case agreement inside answer phrases,
the case named in each explanation, and verb answers belonging to the verb given in brackets.
