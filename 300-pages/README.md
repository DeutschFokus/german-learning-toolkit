# 300 Pages of German · book engine

One codebase that builds every book of the series: six levels (A1–C2), exactly 300 learning
pages each, in two editions that differ only in the explanation language (English, Turkish).

Content is data, design is code. A chapter is one YAML file of typed blocks; the engine turns it
into a designed, interactive PDF – answer key, transcripts, word list, page footers, line numbers,
cross-references, bookmarks and page labels are all generated.

```bash
pip install -r requirements.txt
python build.py --level a2 --lang en --chapters 5,Z2 --preview     # English demo
python build.py --level a2 --lang tr --chapters 5,Z2 --preview     # Turkish: one switch
python build.py --covers                                            # cover PNGs, all levels
```

Results land in `dist/`: the PDF, a PNG of every page (`preview/`), and a QA report (`qa/`).

Needs Python 3.10 or newer and, for WeasyPrint, the Pango library on the system
(Debian/Ubuntu: `apt install libpango-1.0-0 libpangoft2-1.0-0`, macOS: `brew install pango`).
The finished demo – PDFs, covers and a picture of every page – is in [`demo/`](demo/).

## What is in the box

```
series.yaml               series-wide design: page geometry, fonts, colours, structure, cast
levels/a1.yaml … c2.yaml  per level: colour, type size, baseline, density, sample pages
i18n/de.yaml              German interface words (same in every edition)
i18n/en.yaml, tr.yaml     everything that changes with the explanation language
content/a2/book.yaml      outline of the 12 chapters (drives the table of contents)
content/a2/kapitel-05.yaml   one chapter = one file
content/a2/station-2.yaml    one Zwischenstation = one file
engine/                   models (validation) · markup · render · layout · pipeline · post · qa · covers
engine/templates/         book.css.j2 (all design) · blocks.html.j2 · pages.html.j2
assets/fonts/             variable sources, static instances, licences
tools/                    layout_report · baseline_probe · image_briefs · qa_summary · make_fonts
docs/                     illustration style guide, image briefs, QA report
demo/                     the built demo: PDFs, cover PNGs, a PNG of every page
concepts/                 the design directions that were explored first
```

## Command line

| Option | What it does |
| --- | --- |
| `--level a2` | which level (`a1` … `c2`) |
| `--lang en` | explanation language (`en`, `tr`) |
| `--chapters 5,Z2` | what to build: `5`, `1-4,Z1`, `5,Z2`; default is everything that has content |
| `--preview` | PNG of every page and contact sheets (`--dpi`, default 110) |
| `--print` | print edition: 3 mm bleed, crop marks, TrimBox and BleedBox |
| `--sample` | free sample: front matter, the pages listed in `levels/<level>.yaml → sample`, sales page |
| `--forms` | fillable fields on write-in lines, gaps and tick boxes |
| `--covers` | cover as A4, store format 1600 × 2560 and square 3000 × 3000, plus the six-level line-up |
| `--promo` | four store-preview images (1920 × 1080) made from the built PDF: hero, look inside, the cast, what is in the book |
| `--draft` | build although validation found errors |
| `--no-qa` | skip the QA report |
| `--no-cache` | measure every block again (the cache in `.cache/` is otherwise used and kept valid automatically) |
| `--keep-html` | also write the intermediate HTML |

A build stops when validation or layout finds an error. The message names the file, the task and
what to change.

## How a build works

1. **Load and validate.** Every YAML file is checked against the content model
   (`engine/models.py`) and then against the rules of the book (`engine/loader.py`).
2. **Render blocks.** Each task, box and heading becomes a piece of HTML.
3. **Measure.** WeasyPrint lays out every block once to learn its exact height.
4. **Paginate.** Python fills the pages: every block starts on the baseline grid, a heading never
   ends a page, write-in lines and pictures grow into spare room, and every section must fit its
   page budget (Wortschatz 2, Hauptteil 6, Vertiefung 10 …). Page numbers appear inside the text
   ("L 1", "S. 120", line numbers), so steps 2–4 repeat until nothing moves – two or three rounds.
5. **Compose and render** one HTML document; WeasyPrint writes a tagged PDF with live links.
6. **Finish.** pikepdf adds bookmarks (Kapitel → Teil → Aufgabe), page labels that match the
   folios (ii … vi, 1–300, L 1, T 1, W 1), metadata and, for print, the page boxes.
7. **Check.** PyMuPDF renders previews and the QA report is written.

Page numbers are fixed by the structure, not by the content: chapter *n* starts on page
1 + 24 (n − 1) + 4 × (stations before it). Kapitel 5 is always pages 101–124.

## Writing content

### A chapter file

```yaml
type: chapter
level: a2
number: 5
title: Wohnen
subtitle: {en: "Home sweet home – …", tr: "Evim evim, güzel evim – …"}
goal:     {de: "Du kommst in deiner Wohnung … zurecht.", en: "…", tr: "…"}
can_do:
  - {de: "Ich kann meine Wohnung beschreiben.", en: "…", tr: "…", ref: "5.2"}
grammar: [Wechselpräpositionen, wenn-Sätze, Passiv Präsens]
image: {id: k5-auftakt, format: banner, description: "…", alt: {en: "…", tr: "…"}}

vocabulary:
  - {id: bad, de: Bad, article: das, plural: "¨-er", en: bathroom, tr: banyo}
  - {id: nebenkosten, de: Nebenkosten, article: die, plural: "Pl.", en: service charges, tr: aidat}
  - {id: einziehen, de: einziehen, sep: ein, perfekt: "ist eingezogen", en: to move in, tr: taşınmak}

teile:
  - nr: 2
    section: wortschatz          # auftakt | wortschatz | hauptteil | vertiefung | abschlusstest | rueckblick
    title: Zimmer, Möbel, Haus
    subtitle: {en: "Rooms, furniture and the building", tr: "…"}
    blocks:
      - type: task
        id: c                    # address becomes 5.2c
        skills: [hoeren]         # hoeren lesen schreiben sprechen partner grammatik
        rubric: {de: "Hör zu und kreuze an: A, B oder C?", en: "…", tr: "…"}
        points: 4
        audio:
          track: "5.01"
          title: Elifs neue Wohnung
          duration: "0:48"
          transcript:
            turns:
              - {speaker: elif, text: "Komm rein, Jonas!"}
        body:
          - type: multiple_choice
            items:
              - {q: "Elifs Wohnung hat …", options: ["ein Zimmer.", "zwei Zimmer.", "drei Zimmer."], answer: B}
        notes:
          - {kind: wort, words: [keller, herd]}
        words: [zimmer]          # vocabulary this task introduces → page footer and word list

uebersicht:                      # the two overview pages
  grammar: [ … grammar boxes … ]
  phrases: { … }
next: {title: Gesundheit, teaser: {…}, points: [ … ]}
```

The complete example is `content/a2/kapitel-05.yaml`.

### Blocks

Inside `blocks:` of a Teil: `task`, `box` (a grammar box, mistake box or picture between tasks)
and `page_break`. Inside `body:` of a task or box:

| `type` | What it is | Answer key |
| --- | --- | --- |
| `dialogue` | turns with avatars | – |
| `reading_text` | `genre`: email, notice, listing, article, chat, note, plain; line numbers every 5 lines | – |
| `gap_text` | sentences with `[[gaps]]`, optional word `bank`, `compact` for two columns | automatic |
| `multiple_choice` | questions with options A–C | automatic |
| `true_false` | statements with R / F boxes | automatic |
| `matching` | two columns to connect | automatic |
| `table_fill` | table with `[[gaps]]` in the cells | automatic |
| `odd_one_out` | four words, one does not belong | automatic |
| `sort_table` | words to sort into columns | automatic |
| `sentence_build` | prompt and ruled line, optional worked example | automatic |
| `write_lines` | ruled lines, optional handwritten `model` answer | model or `open` |
| `picture_dictionary` | picture with numbered pins and a legend with article colours | – |
| `role_cards`, `bubbles`, `game_grid` | speaking prompts | `open` |
| `word_bank`, `text`, `image` | helpers | – |
| `grammar_box` | table or sentence bracket with highlights, `rule` in the explanation language | – |
| `typical_mistake` | wrong, right, why | – |
| `phrases` | useful phrases in groups | – |
| `self_eval` | sentence starters for the Rückblick | `open` |

Margin notes (`notes:` of a task or box) have a `kind`: `tipp`, `wort`, `landeskunde`, `sogehts`.

### Inline markup

| You write | You get |
| --- | --- |
| `[[die]]` · `[[frei\|Adjektiv]]` | a gap sized to its answer, with an optional hint; the answer goes to the key |
| `{?den\|dem*}` | inline tick boxes; `*` marks the right one |
| `==den==` | highlight in the chapter colour |
| `{der Tisch}` · `{p:die Fenster}` · `{m:dem Tisch}` | noun phrase with the article in its colour (`m` `f` `n` `p` when the article is declined) |
| `**bold**` · `*italic*` · `~~struck~~` | emphasis |
| `{de:Wohin?}` | a German word inside an English or Turkish explanation |
| `{S:5.3a}` · `{S:5.uebersicht}` | live page reference: "S. 104" |
| `{#frist}` in a reading text, `{z:frist}` in a question | line anchor and line reference: "Z. 7" |

Typography is automatic: „German quotes“, en dashes, a thin space in "S. 101", non-breaking
spaces before units and after "Herr" and "Frau".

### What validation refuses

A noun without article or plural · a word without translation in the edition language · the same
task address or track number twice · a task without answer · an answer without task · audio
without transcript · a transcript without audio · a speaker who is not in the cast · a word used
in a task but missing from the vocabulary · sections in the wrong order · a test task without
points · a section that needs more pages than its budget.

## Add a chapter

1. Add the chapter to `content/<level>/book.yaml` if it is not there (title, subtitle, grammar).
2. Copy `content/a2/kapitel-05.yaml` to `kapitel-06.yaml` and replace the content. Twelve Teile:
   1 Auftakt, 2 Wortschatz, 3–5 Hauptteil, 6–10 Vertiefung, 11 Abschlusstest, 12 Rückblick.
3. Build it: `python build.py --level a2 --lang en --chapters 6 --preview`.
4. If a section does not fit, look at the page budget:

   ```bash
   python tools/layout_report.py --level a2 --lang en --chapters 6
   ```

   It shows how many lines every page uses and how tall every block is. Cut or add accordingly –
   a page should end with a few free lines at most.
5. Build the other language. Turkish explanations run a little longer; check both.

A Zwischenstation works the same way (`station-<n>.yaml`, built with `Z<n>`): Teil 1 is mixed
revision, Teil 2 (`kind: exam`) a mini mock exam; four pages.

## Add a level

1. Copy `levels/a2.yaml` to the new level and set `hue` (the level's slice of the colour wheel),
   `cover` (the cover colour as OKLCH – cream type must reach 3 : 1 on it; the QA report checks)
   and `type` (body size, baseline, lines per page). A1 is larger and airier, B2–C2 denser.
   `body_lines × baseline` is the height of the text block; it must not exceed 690 pt, the room
   between the running header and the footer strip.
2. Create `content/<level>/book.yaml` with the outline of the twelve chapters.
3. Write chapters. Nothing else changes: chapter colours, cover and all page furniture follow
   from the level file.

The six levels in this repository are already configured; `python build.py --covers` shows them.

## Add a language

1. Copy `i18n/en.yaml` to `i18n/<code>.yaml` and translate every value. Keep the keys and the
   placeholders in braces.
2. Add the code to `languages:` in `series.yaml` and to `LANGS` in `engine/models.py`.
3. Add the new key next to `en:` and `tr:` wherever content carries translations (rubrics,
   explanations, vocabulary, notes, alt texts). Validation lists every string that is missing.
4. Check that the fonts cover the script. Source Sans 3, Source Serif 4 and Fraunces cover Latin
   with German and Turkish letters; other scripts need other fonts in `series.yaml → fonts`.
5. If the language has its own typographic rules, add them in `engine/markup.py → typo()`.

## Pictures and characters

- **Scenes** – `assets/images/<level>/<id>.jpg`, switched on in the content file with `src:`. A slot
  crops its picture; `focus: 30` keeps the upper part visible (0 = top, 100 = bottom).
  `python tools/image_briefs.py --level a2` lists every slot with size, palette and scene;
  `python tools/prompt_pack.py --level a2` writes ready-to-paste prompts for an image model.
- **Portraits** – `assets/cast/<key>.png` (square, the face centred) replaces the drawn avatar of
  that cast member in dialogues, chats and on the people page. The full character sheets are kept
  next to them as `cast-<key>.png`.
- **Cover figure** – `assets/cast/cover-<key>.png` (full body, transparent background) stands in
  front of the 300 when `series.yaml → design.cover_figure` names the cast member. Leave it empty
  for the type-only cover.
- The cast itself – names, roles, bios – is `series.yaml → cast` and `bios`.
  `docs/illustration-style-guide.md` defines the style.

## Design in one place

- **Colours** – `series.yaml → colors`. Chapter colours are computed in OKLCH from the level hue,
  article colours and note colours are fixed for the whole series.
- **Page** – `series.yaml → page`: A4, mirrored margins, an outer column for notes, the baseline
  grid from the level file.
- **Fonts** – Fraunces (display), Source Sans 3 (text), Source Serif 4 (reading texts), Caveat
  (handwriting), all under the SIL Open Font License. The books use static instances cut by
  `python tools/make_fonts.py`. WeasyPrint only knows font weights in steps of 100, so each
  Fraunces weight is a role: 900 the big numerals, 800 small numerals, 700 titles, 600 box titles,
  500 text, 400 the cover line.
- **Chapter opener** – `series.yaml → design.opener`: `buehne` (picture on top, numeral
  overlapping) or `register` (coloured band on the right).
- **Everything else** – `engine/templates/book.css.j2`. Vertical measures are multiples of half a
  baseline; `python tools/baseline_probe.py --chapters 5` shows any line that leaves the grid.

## Quality checks

Every build writes `dist/qa/<edition>-qa.md`: validation log, overflow and collisions, free space
per page, baseline grid, links, bookmarks, page labels, fonts, tagged PDF and alternative texts,
text extraction samples, cover elements, contrast table and a file-size estimate for the full
book. `docs/QA-REPORT.md` is the report for the demo, with a list of known weaknesses.

## Before you publish

These are placeholders and must be replaced in `series.yaml`:

- `website`, `shop_url`, `audio_url`, `contact` – the demo uses the reserved domain
  `deutschfokus.example`. QR codes and all links are built from these values.
- `youtube_url` – check the channel handle.
- The logo: `engine/art.py → logo()` draws a speech bubble with a focus point next to the name. Replace it if
  you have your own mark.
- Audio does not exist yet. Record each track and publish it at `audio_url` (`{level}/{track}`).
- `version` and `year` for the imprint.

Print: the PDF is RGB. A printer will ask for PDF/X with an output intent – convert the
`--print` file before sending it (see `docs/QA-REPORT.md`, weaknesses).

## Licences

The fonts are licensed under the SIL Open Font License 1.1 (`assets/fonts/OFL-*.txt`); the static
instances are renamed modified versions as the licence requires. The licence texts must stay with
the fonts.
