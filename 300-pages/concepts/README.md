# 300 Pages of German — design concepts

Round 1: three cover directions, two chapter-opener directions, one practice spread.
All pages are rendered from HTML/CSS with the same toolchain the final books use
(WeasyPrint), so nothing here is a mock-up that the engine could not reproduce.

Shared decisions in every direction:

- **Type:** Fraunces (display), Source Sans 3 (tasks and UI), Source Serif 4 (reading texts),
  Caveat (handwritten model answers). All SIL OFL, all tested with ä ö ü ß and ç ğ ı İ ş.
- **Colour:** the six levels each own a slice of the colour wheel; the twelve chapters of a
  level step through that slice, so every chapter in the whole series has its own hue.
  Article colours stay fixed: der blue, die pink-red, das green, plural navy.
- **Logo:** the ring-and-dot mark is a placeholder for the real Deutsch Fokus logo.

## Covers

| File | Direction |
| --- | --- |
| `02-cover-A-monument.png` | **A · Monument.** A full colour field in the level hue carries a huge soft-serif 300 that runs off both edges. All small print sits on a cream band at the foot, so every text pair passes WCAG AA on every level colour. |
| `02-cover-B-spectrum.png` | **B · Spectrum.** The 300 is cut into twelve slices, one per chapter, coloured with the same tints the chapter tabs use inside the book. A numbered strip below shows the real structure: 12 chapters and 3 review stations. |
| `02-cover-C-fokus.png` | **C · Fokus.** A geometric 300 drawn from rings on deep navy; the last zero becomes a focus ring that holds the level. The mark works as an app icon and avatar on its own. |

`03-family-*.png` shows each direction across A1–C2.

## Chapter openers

| File | Direction |
| --- | --- |
| `05-opener-1-buehne.png` | **1 · Bühne.** The illustration fills the top of the page edge to edge and the chapter number overlaps it. Goal, can-do list and chapter map sit in a calm two-column block below. |
| `05-opener-2-register.png` | **2 · Register.** A full-height band in the chapter colour carries the number and the chapter map, like an index tab grown to page size. The illustration sits in an arched frame, which uses far less ink when printed at home. |

## Practice spread

`06-practice-spread.png` — pages 110–111. Tasks sit in the main column with their address
(5.6 a) and skill icons in a fixed label column; notes, audio and word help sit in the outer
margin, level with the task they belong to. The page shows the dialogue, true/false grid,
grammar box, word bank, gap fill, e-mail with line numbers, A/B/C, typical-mistake box,
handwritten model answer, score fields, answer-key pointers and the words-on-this-page footer.
