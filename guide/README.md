# Your German Journey — Learner Guide

**[📄 Download the PDF](Your-German-Journey.pdf)** · 52 pages · A4 · clickable contents, bookmarks and QR codes

The guide new students receive before their first lesson. It explains how to learn German efficiently from zero with 20–30 minutes a day, and it grows with the learner from A0 to C2.

| Part | What’s inside |
|---|---|
| **1 · Start Here** | Welcome, the CEFR levels, the method (four pillars, 20-minute rule, speaking, article and review rules), how to get the most out of lessons, A0 first steps, a seven-day plan |
| **2 · Your Level Roadmap** | One chapter per level (A1–C2): goal, four pillars with resources, grammar focus, can-do checklist, common pitfall |
| **3 · Skills Toolbox** | Pronunciation (26 rules), mediation, self-correction, the science behind the method, timelines and exams, immersion, pitfalls, mindset |
| **4 · Tools & Templates** | Resource directory with QR codes and nine printable templates (goal sheet, planner, dashboard, flashcard, retelling, self-assessment, mistake log, habit tracker, lesson notes) |

## Your Learning Profile — the form before lesson one

**[📋 Download the form](Your-Learning-Profile.pdf)** · 4 pages · fillable PDF

Students fill it in on their phone or computer — it uses standard PDF form fields (tick boxes, round buttons, text fields) that most PDF apps can fill, such as Adobe Reader, Apple Preview/Files and browser PDF viewers — or print it, then send it back. It covers:

1. **About you** — contact, native and other languages, city, job
2. **Your goals** — why German, target level and date, exam, where German is needed, the 1–2-year goal
3. **Your German today** — level, how long, certificates, how they learned so far, self-rating of six skills
4. **Your ideal lesson** — textbook / conversation / grammar / mix, how much the student wants to speak (50/50 to 90/10), focus areas, how and how much to correct, du or Sie, language for explanations
5. **Homework & practice** — homework yes/no, time per week, favourite types, daily practice
6. **Schedule & long-term plan** — lessons per week, length, online or in person, weekly availability grid, how long they plan to learn, how often to review progress, start date, breaks
7. **Almost done** — favourite and avoided topics, what usually stops them, motivation 1–10, anything else, their questions

**To change a question**, edit `form/learning-profile.yml` (every question type is explained at the top of the file) and run:

```bash
python3 guide/scripts/build_form.py
```

Page breaks and the clickable fields are placed automatically; a section is never split across pages.

## Editing the guide

| To change … | edit … |
|---|---|
| any text | `guide.md` |
| a link or app recommendation (and its QR code) | `config.yml` → `resources` |
| the version, date, teacher name or brand | `config.yml` |
| colors, fonts, spacing | `assets/style.css` |

Then rebuild the PDF (see below). Page numbers, the table of contents, bookmarks and every QR code are regenerated automatically.

**Referral links:** put your referral link in the resource’s `url` in `config.yml` — the clickable link and the QR code both use it.

### Writing conventions in `guide.md`

- `# Part title {#id hint="…"}` starts a part; `## Chapter title {#id}` starts a chapter on a new page. Parts and chapters are numbered automatically.
- Level chapters get a color: `{.zone-blue}` (A0–A2), `{.zone-green}` (B1–B2), `{.zone-purple}` (C1–C2).
- German examples go in blockquotes (`> **Ich heiße Maria.**`).
- Boxes are fenced divs: `::: {.callout .tip}`, `::: {.callout .natulang}`, `::: {.callout .pitfall}`, `::: checklist`, `::: dont`, `::: steps`, `::: cols`, `::: motto`, `::: big-goal`, `::: quote-box`.
- Fill-in elements: `[]{.box}` (tick box), `[]{.blank}` (line to write on), `::: write-box` + `:::` (lined writing area).
- Shortcodes, filled in from `config.yml`:
  - `{{qr:KEY}}` — QR code (one per app store for apps without a website)
  - `{{resource:KEY}}` — resource card with level, cost, platforms and QR code
  - `{{link:KEY}}` — clickable name of the resource
  - `{{teacher}}`, `{{brand}}`, `{{version}}`, `{{date}}`

## Building the PDF

Requirements: Python 3.10+, [pandoc](https://pandoc.org) 2.11+, Node.js with [Playwright](https://playwright.dev) and its Chromium, the [Inter](https://rsms.me/inter/) and Noto Color Emoji fonts for the intended look, and — for the form — `npm install` in `guide/` (pdf-lib) plus a Unicode TrueType font such as DejaVu Sans for the typed answers.

```bash
pip install -r guide/requirements.txt
```

```bash
npm install playwright && npx playwright install chromium
```

```bash
cd guide && npm install
```

```bash
python3 guide/scripts/build.py
```

The build prints the PDF twice: the first pass finds the page of every heading, the second writes those page numbers into the table of contents. Intermediate files go to `guide/build/` (ignored by git).

After editing, check for chapters that spill onto an almost empty page:

```bash
python3 guide/scripts/check_layout.py
```

## Sources

- Hours per level: Goethe-Institut, *Wie lange dauert es, Deutsch zu lernen?* (A1 60–150 h … C2 750+ h).
- All resource links were checked in November 2026. Apps change their offers — re-check `config.yml` once or twice a year.
