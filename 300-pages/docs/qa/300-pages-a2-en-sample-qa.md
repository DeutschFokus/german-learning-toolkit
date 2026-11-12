# QA report · 300-pages-a2-en-sample.pdf

Built 2026-11-12 01:44 · level A2 · language en · flags: sample

## Summary

| Check | Result | |
| --- | --- | --- |
| Validation | 0 errors, 0 warnings | pass |
| Layout geometry | 0 problems on 11 learning pages and 7 front-matter and appendix pages | pass |
| Links | 198 internal link areas to 47 targets, 73 external to 8 URLs, 0 broken | pass |
| Fonts | 16 faces, all embedded | pass |
| Text extraction | 0 broken characters, 0 letter-spaced runs | pass |
| Tagged PDF | 106/106 figures with alt text, language de-DE | pass |
| Cover | 10 text elements, 0 duplicated or missing | pass |
| Contrast | 101 colour pairs, 0 below WCAG AA | pass |
| Baseline grid | 96% of body lines on the half-baseline grid, 100% on the quarter grid | pass |

File: 20 pages, 2423 KB · layout 1.0 s (3 rounds) · render 4.9 s · write 4.3 s

## 1 · Validation log

```
Validation: 0 error(s), 0 warning(s)
  parts: 5, Z2 · tasks: 60 · vocabulary: 118 · audio tracks: 9
```

## 2 · Overflow, clipping, collisions, empty space, footers

No block overflows its page, no two blocks overlap, every block has the height the paginator planned, nothing comes closer than 1 mm to the footer strip, and no line of text is printed over another on any page.

`natural` = how full the page is before spare room is used; `final` = after write-in areas and picture slots have grown and the gaps were opened. Pages marked `open` end with more than 20 % free space.

| Page | Section | natural | final | clearance | state |
| --- | --- | --- | --- | --- | --- |
| 101 | Auftakt | – | – | 5.5 mm to footer | ok |
| 102 | wortschatz | 92% | 92% | 22.7 mm to footer | ok |
| 103 | wortschatz | 79% | 89% | 32.0 mm to footer | ok |
| 104 | hauptteil | 87% | 100% | 4.2 mm to footer | ok |
| 105 | hauptteil | 85% | 100% | 4.2 mm to footer | ok |
| 106 | hauptteil | 84% | 100% | 4.2 mm to footer | ok |
| 107 | hauptteil | 99% | 100% | 4.2 mm to footer | ok |
| 120 | uebersicht | 91% | 91% | 25.4 mm to footer | ok |
| 121 | uebersicht | 96% | 96% | 14.8 mm to footer | ok |
| 122 | abschlusstest | 92% | 100% | 4.2 mm to footer | ok |
| 123 | abschlusstest | 96% | 100% | 4.2 mm to footer | ok |

Front matter and appendix pages are composed as whole pages; they are measured in the finished PDF (lowest text line against the folio line, at least 2 mm required).

| Page | Part | clearance | state |
| --- | --- | --- | --- |
| ii | front | 11.8 mm to folio | ok |
| iii | front | 16.8 mm to folio | ok |
| iv | front | 15.9 mm to folio | ok |
| v | front | 29.8 mm to folio | ok |
| vi | front | 62.4 mm to folio | ok |
| L 1 | answers | 16.2 mm to folio | ok |
| W 1 | wordlist | 15.3 mm to folio | ok |

## 3 · Baseline alignment on facing pages

Every block starts on a multiple of half a baseline (7.5 pt), so running text on facing pages shares the same lines. Measured in the finished PDF over 312 body-size lines (tolerance 0.35 pt): **96%** sit on the half-baseline grid, **100%** on the quarter grid. The rest is text on ruled write-in lines and in phrase lists, which follow their own ruling. `shared` = grid lines that carry text on both pages of a spread.

| Spread | body lines | on half grid | on quarter grid | shared lines |
| --- | --- | --- | --- | --- |
| 101 | 13 | 100% | 100% | – |
| 102–103 | 51 | 100% | 100% | 0 |
| 104–105 | 41 | 100% | 100% | 0 |
| 106–107 | 80 | 100% | 100% | 6 |
| 120–121 | 58 | 79% | 100% | 2 |
| 122–123 | 69 | 100% | 100% | 6 |

## 4 · Links and navigation

- internal link areas: **198** pointing to 47 different targets, all resolved: **yes** (one link can consist of several clickable areas)
- named destinations in the file: 215
- external link areas: 73 → https://www.deutschfokus.example (69), https://www.youtube.com (3), mailto:hallo@deutschfokus.example (1)
- 8 different URLs, all well-formed: `https://www.deutschfokus.example/300`, `https://www.deutschfokus.example/audio`, `https://www.deutschfokus.example/audio/a2/5.01`, `https://www.deutschfokus.example/audio/a2/5.02`, `https://www.deutschfokus.example/audio/a2/5.03`, `https://www.deutschfokus.example/audio/a2/5.08`, `https://www.youtube.com/@DeutschFokus`, `mailto:hallo@deutschfokus.example`
- bookmarks: level 1: 9, level 2: 7, level 3: 21 (Kapitel → Teil → Aufgabe)
- page labels: Cover, ii, iii, iv, v, vi, 101, 102 … 121, 122, 123, L 1, W 1, Info
- metadata: title “300 Pages of A2 German – With English explanations (Free sample)”, author “Deutsch Fokus”, language de-DE
- tagged PDF: yes · figures with alternative text: 106 of 106

## 5 · Fonts

| Font | Type | Embedded |
| --- | --- | --- |
| BJLCUM+DF-Hand-Medium | Type0 | yes |
| BRSPYU+DF-Serif | Type0 | yes |
| CSPVMU+DF-Fraunces | Type0 | yes |
| DVHMTC+DF-Fraunces-Heavy | Type0 | yes |
| FOKVBL+DF-Sans-Bold-Italic | Type0 | yes |
| IIPPKY+DF-Sans-Ultra-Bold | Type0 | yes |
| LVCMSK+DF-Sans-Bold | Type0 | yes |
| NGBVPN+DF-Fraunces-Medium-Italic | Type0 | yes |
| NRGEVD+DF-Fraunces-Medium | Type0 | yes |
| OSRKMZ+DF-Hand-Bold | Type0 | yes |
| RQFTGW+DF-Fraunces-Bold | Type0 | yes |
| TAJBHQ+DF-Fraunces-Ultra-Bold | Type0 | yes |
| UBWAFX+DF-Fraunces-Semi-Bold | Type0 | yes |
| VAYXSQ+DF-Sans | Type0 | yes |
| YRHWMB+DF-Sans-Semi-Bold | Type0 | yes |
| ZGCQZL+DF-Sans-Italic | Type0 | yes |

Embedded font data: 78 KB (subsets).

## 6 · Text extraction

Whole file: 30,104 characters · 0 replacement characters · 0 letter-spaced runs · 190 umlauts/ß · 0 Turkish letters (ç ğ ı İ ş) · 0 soft hyphens · 0 zero-width characters.

### Page Cover

```text
FREE SAMPLE
NIVEAU
A2
300
Pages of
A2 German
With English explanations
ANSWER KEY
WORD LISTS
CHAPTER TESTS
Deutsch Fokus
```

### Page ii

```text
Deutsch Fokus
300 Pages of A2 German
With English explanations
© 2026 Deutsch Fokus. All rights reserved.
Version 1.0-demo · built 2026-11-12
Personal-use licence
You have bought this book for yourself. You may save it on your own devices and print it for
your own learning. Please do not share, resell or upload the file, and do not use it to train AI
systems. Teachers: one copy per learner, please – class licences are available on request.
Audio
Scan the QR code next to a listening task or tap the track number. All tracks: 
www.deutschfokus.example/audio
Typefaces
Set in Fraunces, Source Sans 3, Source Serif 4 and Caveat – all published under the SIL Open
Font License 1.1.
Fraunces © The Fraunces Project Authors · Source Sans 3 and Source Serif 4 © Adobe · Caveat
© The Caveat Project Authors
All people and events in this book are fictional.
Questions, corrections, ideas? hallo@deutschfokus.example
ii
```

### Page iii

```text
Inhalt
Twelve chapters of 24 pages each and three review stations of four pages: exactly
300 pages of A2 German.
BEFORE YOU START
So funktioniert dieses Buch How this book works
iv
Die Personen The people in this book
vi
300 SEITEN · 12 KAPITEL
Ankommen Arriving – introductions and your story so far
Perfekt (Wiederholung) · Präteritum: war, hatte
1
Familie und Freunde Family and friends – people in your life
Possessivartikel im Dativ · Nebensatz mit weil
25
Essen und Einkaufen Food and shopping – at the market, at the till
Komparativ und Superlativ · welch-?
49
Arbeit und Beruf Work – jobs, colleagues, daily routine
Nebensatz mit dass · Modalverben im Präteritum
73
Zwischenstation 1 Review of chapters 1–4 and mini exam
97
5
Wohnen Home sweet home – flats, neighbours, house rules
Wechselpräpositionen · wenn-Sätze · Passiv
Präsens
101
Gesundheit Health – at the doctor’s and at the chemist’s
Ratschläge mit sollte · Reflexive Verben
125
Unterwegs Out and about – tickets, directions, delays
Lokale Präpositionen · Verben mit Dativ
149
Feste und Freizeit Celebrations and free time – invitations and plans
Adjektive nach ein / kein · Datum und
Ordinalzahlen
173
Z2
Zwischenstation 2 Review of chapters 5–8 and mini exam
197
Lernen und Schule Learning – courses, school, memories
Nebensätze mit als und wenn · Relativsätze im
Nominativ
201
Ämter und Dienste Offices and services – forms, bank, post office
Konjunktiv II: könnte, würde, hätte · Indirekte
Fragen
225
Medien und Konsum Media and shopping – online, reviews,
complaints
Adjektive nach der / die / das · Verben mit
Präpositionen
249
Pläne und Träume Plans and dreams – what comes next
Futur mit werden · um … zu
273
Zwischenstation 3 Review of chapters 9–12 and mock exam
297
APPENDIX
Lösungen
Answer key
L 1
Transkripte Transcripts
T 1
Wortliste A–Z
Word list A–Z
W 1
1
2
3
4
Z1
6
7
8
9
10
11
12
Z3
iii
```

### Page iv

```text
So funktioniert dieses Buch
Every chapter follows the same path, so you always know where you are. Two
minutes on this spread will save you hours later.
24 Seiten – immer derselbe Weg
1
Auftakt
A picture, your goal
and a checklist. Tick
what you can
already do.
2
Wortschatz
The words of the
topic, with pictures
and first exercises.
6
Hauptteil
Dialogues, texts and
audio. New gram-
mar appears in real
situations.
10
Vertiefung
Practice in listening,
reading, writing and
speaking.
2
Übersicht
Grammar and
phrases on two
pages. Screenshot
them.
2
Abschlusstest
An exam-style test
with points.
1
Rückblick
Tick the checklist
again and see how
far you have come.
Jede Aufgabe hat eine Adresse
5.2 d means chapter 5, part 2, task d. You find the same address in the answer key, in cross-references and in the word list.
1
Address of the task
2
What you practise
3
Instruction in German,
then in English
4
Your score
5
Tap to jump to the
answer – and back again
Sechs Symbole
The icons show which skill a task trains.
Hören
Lesen
Schreiben
Sprechen
Partnerarbeit
Grammatik
Artikel haben Farben
Every noun appears with its article in a fixed colour: der blue, die red, das green, plural navy. Learn the colour together with the
word.
der Flur, -e
die Küche, -n
das Bad, ¨-er
die Nebenkosten (Pl.)
Hilfe am Rand
Four kinds of help sit next to the task they belong to.
TIPP
a learning tip
WORT-HILFE
words you need right now
LANDESKUNDE
life in Germany
SO GEHT’S
how to do it, step by step
5.2
d
Lies die Anzeige und ergänze die Tabelle.
/ 6
L 3
Instruction in German, then in English
1
2
3
4
5
iv
```

### Page v

```text
Hören mit QR-Code
Scan the code with your phone or tap the track number on a
tablet. The transcript of every track is at the back.
TRACK
5.01
0:48 Min.
Typische Fehler
A mistake many learners make, the correct sentence and one
line that says why.
TYPISCHER FEHLER
Handschrift heißt Beispiel
Blue handwriting shows one possible answer. The empty lines
are yours.
Kann ich das?
The same checklist opens and closes each chapter. Compare
your ticks.
Das kann ich …
NOCH
NICHT
FAST
SICHER
Ich kann meine Wohnung
beschreiben.
Wörter auf dieser Seite
At the foot of each page: the new words with article, plural
and translation.
Zeilen und Seiten
Reading texts carry line numbers. Z. 5 points to a line, S. 120
to a page – in the PDF you can tap both.
Z. 5 = Zeile 5 · S. 120 = Seite 120
Ich wohne in die Nordstadt.
Ich wohne in der Nordstadt.
Meine Wohnung hat zwei Zimmer.
WÖRTER AUF DIESER SEITE Words on this page
der Flur, -e hallway
das Wohnzimmer, - living room
das Schlafzimmer, - bedroom
Liebe Nachbarn,
am Samstag feiere ich Geburtstag.
Es kann etwas lauter werden.
Wenn es Sie stört, klingeln Sie
einfach – oder kommen Sie vorbei!
1
5
Three habits that work
1
Little and often: twenty minutes a day beats two hours on Sunday.
2
Say it out loud. Read every dialogue twice – once as each speaker.
3
Check the answer key only after you have tried. Mistakes are part of the plan.
v
```

## 7 · Contrast (WCAG 2.x)

| Pair | Foreground | Background | Ratio | Needs | |
| --- | --- | --- | --- | --- | --- |
| article der on paper | `#005DCA` | `#FFFFFF` | 6.14 | 4.5 | pass |
| article der on its tint | `#005DCA` | `#E7F1FF` | 5.39 | 4.5 | pass |
| article die on paper | `#BF1070` | `#FFFFFF` | 5.96 | 4.5 | pass |
| article die on its tint | `#BF1070` | `#FFEAF1` | 5.19 | 4.5 | pass |
| article das on paper | `#007835` | `#FFFFFF` | 5.62 | 4.5 | pass |
| article das on its tint | `#007835` | `#E3F6E6` | 4.97 | 4.5 | pass |
| article pl on paper | `#1C2967` | `#FFFFFF` | 13.44 | 4.5 | pass |
| article pl on its tint | `#1C2967` | `#EAF0FF` | 11.78 | 4.5 | pass |
| note tipp label on paper | `#7B5100` | `#FFFFFF` | 6.96 | 4.5 | pass |
| note wort label on paper | `#693996` | `#FFFFFF` | 8.00 | 4.5 | pass |
| note landeskunde label on paper | `#006169` | `#FFFFFF` | 7.21 | 4.5 | pass |
| note sogehts label on paper | `#404E63` | `#FFFFFF` | 8.44 | 4.5 | pass |
| body ink on paper | `#1B1E2F` | `#FFFFFF` | 16.49 | 4.5 | pass |
| muted text on paper | `#5A5F73` | `#FFFFFF` | 6.33 | 4.5 | pass |
| handwriting ink on paper | `#2A3F9D` | `#FFFFFF` | 9.15 | 4.5 | pass |
| chapter 1: ink on mid (tab, chips) | `#1B1E2F` | `#EAAA00` | 8.05 | 4.5 | pass |
| chapter 1: ink on wash (boxes) | `#1B1E2F` | `#FEF5E6` | 15.25 | 4.5 | pass |
| chapter 1: muted on wash | `#5A5F73` | `#FEF5E6` | 5.85 | 4.5 | pass |
| chapter 1: ink on highlight | `#1B1E2F` | `#FAD18A` | 11.43 | 4.5 | pass |
| chapter 1: deep on paper (labels) | `#5E4200` | `#FFFFFF` | 9.31 | 4.5 | pass |
| chapter 1: deep on soft (pointer) | `#5E4200` | `#FBE7C5` | 7.69 | 4.5 | pass |
| chapter 2: ink on mid (tab, chips) | `#1B1E2F` | `#F0A600` | 7.98 | 4.5 | pass |
| chapter 2: ink on wash (boxes) | `#1B1E2F` | `#FEF4E6` | 15.15 | 4.5 | pass |
| chapter 2: muted on wash | `#5A5F73` | `#FEF4E6` | 5.81 | 4.5 | pass |
| chapter 2: ink on highlight | `#1B1E2F` | `#FDCF8B` | 11.37 | 4.5 | pass |
| chapter 2: deep on paper (labels) | `#614000` | `#FFFFFF` | 9.37 | 4.5 | pass |
| chapter 2: deep on soft (pointer) | `#614000` | `#FDE6C5` | 7.72 | 4.5 | pass |
| chapter 3: ink on mid (tab, chips) | `#1B1E2F` | `#F4A100` | 7.81 | 4.5 | pass |
| chapter 3: ink on wash (boxes) | `#1B1E2F` | `#FFF4E7` | 15.19 | 4.5 | pass |
| chapter 3: muted on wash | `#5A5F73` | `#FFF4E7` | 5.83 | 4.5 | pass |
| chapter 3: ink on highlight | `#1B1E2F` | `#FFCE90` | 11.37 | 4.5 | pass |
| chapter 3: deep on paper (labels) | `#633F00` | `#FFFFFF` | 9.37 | 4.5 | pass |
| chapter 3: deep on soft (pointer) | `#633F00` | `#FFE5C6` | 7.71 | 4.5 | pass |
| chapter 4: ink on mid (tab, chips) | `#1B1E2F` | `#F99D00` | 7.74 | 4.5 | pass |
| chapter 4: ink on wash (boxes) | `#1B1E2F` | `#FFF4E8` | 15.20 | 4.5 | pass |
| chapter 4: muted on wash | `#5A5F73` | `#FFF4E8` | 5.83 | 4.5 | pass |
| chapter 4: ink on highlight | `#1B1E2F` | `#FFCD97` | 11.33 | 4.5 | pass |
| chapter 4: deep on paper (labels) | `#663D00` | `#FFFFFF` | 9.41 | 4.5 | pass |
| chapter 4: deep on soft (pointer) | `#663D00` | `#FFE5C9` | 7.75 | 4.5 | pass |
| chapter 5: ink on mid (tab, chips) | `#1B1E2F` | `#FD9913` | 7.65 | 4.5 | pass |
| chapter 5: ink on wash (boxes) | `#1B1E2F` | `#FFF4E9` | 15.21 | 4.5 | pass |
| chapter 5: muted on wash | `#5A5F73` | `#FFF4E9` | 5.84 | 4.5 | pass |
| chapter 5: ink on highlight | `#1B1E2F` | `#FFCC9E` | 11.30 | 4.5 | pass |
| chapter 5: deep on paper (labels) | `#693B00` | `#FFFFFF` | 9.43 | 4.5 | pass |
| chapter 5: deep on soft (pointer) | `#693B00` | `#FFE4CC` | 7.74 | 4.5 | pass |
| chapter 6: ink on mid (tab, chips) | `#1B1E2F` | `#FF9524` | 7.52 | 4.5 | pass |
| chapter 6: ink on wash (boxes) | `#1B1E2F` | `#FFF3EA` | 15.13 | 4.5 | pass |
| chapter 6: muted on wash | `#5A5F73` | `#FFF3EA` | 5.80 | 4.5 | pass |
| chapter 6: ink on highlight | `#1B1E2F` | `#FFCCA3` | 11.32 | 4.5 | pass |
| chapter 6: deep on paper (labels) | `#6B3900` | `#FFFFFF` | 9.50 | 4.5 | pass |
| chapter 6: deep on soft (pointer) | `#6B3900` | `#FFE4CF` | 7.80 | 4.5 | pass |
| chapter 7: ink on mid (tab, chips) | `#1B1E2F` | `#FF9236` | 7.40 | 4.5 | pass |
| chapter 7: ink on wash (boxes) | `#1B1E2F` | `#FFF3EC` | 15.14 | 4.5 | pass |
| chapter 7: muted on wash | `#5A5F73` | `#FFF3EC` | 5.81 | 4.5 | pass |
| chapter 7: ink on highlight | `#1B1E2F` | `#FFCBA8` | 11.28 | 4.5 | pass |
| chapter 7: deep on paper (labels) | `#6E3700` | `#FFFFFF` | 9.50 | 4.5 | pass |
| chapter 7: deep on soft (pointer) | `#6E3700` | `#FFE4D1` | 7.82 | 4.5 | pass |
| chapter 8: ink on mid (tab, chips) | `#1B1E2F` | `#FF8F43` | 7.27 | 4.5 | pass |
| chapter 8: ink on wash (boxes) | `#1B1E2F` | `#FFF3EC` | 15.14 | 4.5 | pass |
| chapter 8: muted on wash | `#5A5F73` | `#FFF3EC` | 5.81 | 4.5 | pass |
| chapter 8: ink on highlight | `#1B1E2F` | `#FFCBAC` | 11.30 | 4.5 | pass |
| chapter 8: deep on paper (labels) | `#703505` | `#FFFFFF` | 9.54 | 4.5 | pass |
| chapter 8: deep on soft (pointer) | `#703505` | `#FFE3D3` | 7.81 | 4.5 | pass |
| chapter 9: ink on mid (tab, chips) | `#1B1E2F` | `#FF8C4C` | 7.15 | 4.5 | pass |
| chapter 9: ink on wash (boxes) | `#1B1E2F` | `#FFF3ED` | 15.15 | 4.5 | pass |
| chapter 9: muted on wash | `#5A5F73` | `#FFF3ED` | 5.81 | 4.5 | pass |
| chapter 9: ink on highlight | `#1B1E2F` | `#FFCAB0` | 11.25 | 4.5 | pass |
| chapter 9: deep on paper (labels) | `#71330D` | `#FFFFFF` | 9.63 | 4.5 | pass |
| chapter 9: deep on soft (pointer) | `#71330D` | `#FFE3D5` | 7.88 | 4.5 | pass |
| chapter 10: ink on mid (tab, chips) | `#1B1E2F` | `#FF8854` | 6.99 | 4.5 | pass |
| chapter 10: ink on wash (boxes) | `#1B1E2F` | `#FFF3EE` | 15.16 | 4.5 | pass |
| chapter 10: muted on wash | `#5A5F73` | `#FFF3EE` | 5.82 | 4.5 | pass |
| chapter 10: ink on highlight | `#1B1E2F` | `#FFCAB4` | 11.28 | 4.5 | pass |
| chapter 10: deep on paper (labels) | `#723214` | `#FFFFFF` | 9.62 | 4.5 | pass |
| chapter 10: deep on soft (pointer) | `#723214` | `#FFE3D7` | 7.89 | 4.5 | pass |
| chapter 11: ink on mid (tab, chips) | `#1B1E2F` | `#FF855B` | 6.88 | 4.5 | pass |
| chapter 11: ink on wash (boxes) | `#1B1E2F` | `#FFF3EF` | 15.17 | 4.5 | pass |
| chapter 11: muted on wash | `#5A5F73` | `#FFF3EF` | 5.82 | 4.5 | pass |
| chapter 11: ink on highlight | `#1B1E2F` | `#FFC9B8` | 11.23 | 4.5 | pass |
| chapter 11: deep on paper (labels) | `#73311A` | `#FFFFFF` | 9.62 | 4.5 | pass |
| chapter 11: deep on soft (pointer) | `#73311A` | `#FFE2D9` | 7.85 | 4.5 | pass |
| chapter 12: ink on mid (tab, chips) | `#1B1E2F` | `#FF8161` | 6.73 | 4.5 | pass |
| chapter 12: ink on wash (boxes) | `#1B1E2F` | `#FFF3EF` | 15.17 | 4.5 | pass |
| chapter 12: muted on wash | `#5A5F73` | `#FFF3EF` | 5.82 | 4.5 | pass |
| chapter 12: ink on highlight | `#1B1E2F` | `#FFC9BB` | 11.25 | 4.5 | pass |
| chapter 12: deep on paper (labels) | `#74301F` | `#FFFFFF` | 9.61 | 4.5 | pass |
| chapter 12: deep on soft (pointer) | `#74301F` | `#FFE2DB` | 7.85 | 4.5 | pass |
| cover A1: cream on level field (large type) | `#FBF4E6` | `#00926E` | 3.59 | 3.0 | pass |
| cover A1: cream 300 on the lighter circle | `#FBF4E6` | `#00A17A` | 3.01 | 3.0 | pass |
| cover A2: cream on level field (large type) | `#FBF4E6` | `#D75B00` | 3.56 | 3.0 | pass |
| cover A2: cream 300 on the lighter circle | `#FBF4E6` | `#EB6400` | 3.02 | 3.0 | pass |
| cover B1: cream on level field (large type) | `#FBF4E6` | `#D32C4D` | 4.53 | 3.0 | pass |
| cover B1: cream 300 on the lighter circle | `#FBF4E6` | `#E5405C` | 3.68 | 3.0 | pass |
| cover B2: cream on level field (large type) | `#FBF4E6` | `#963AA5` | 5.57 | 3.0 | pass |
| cover B2: cream 300 on the lighter circle | `#FBF4E6` | `#A64AB5` | 4.49 | 3.0 | pass |
| cover C1: cream on level field (large type) | `#FBF4E6` | `#3641BC` | 7.27 | 3.0 | pass |
| cover C1: cream 300 on the lighter circle | `#FBF4E6` | `#4252CD` | 5.78 | 3.0 | pass |
| cover C2: cream on level field (large type) | `#FBF4E6` | `#006483` | 6.09 | 3.0 | pass |
| cover C2: cream 300 on the lighter circle | `#FBF4E6` | `#007397` | 4.92 | 3.0 | pass |
| cover: navy on cream band | `#161B36` | `#FBF4E6` | 15.42 | 4.5 | pass |
| cover: cream on navy badge | `#FBF4E6` | `#161B36` | 15.42 | 4.5 | pass |

## 8 · Cover

Every text element of the cover exists exactly once in the PDF (the level appears twice by design: in the badge and in the title).

| Element | expected | found | |
| --- | --- | --- | --- |
| 300 | 1 | 1 | pass |
| Niveau | 1 | 1 | pass |
| A2 (badge and title) | 2 | 2 | pass |
| Pages of | 1 | 1 | pass |
| German | 1 | 1 | pass |
| With English explanations | 1 | 1 | pass |
| Answer key | 1 | 1 | pass |
| Word lists | 1 | 1 | pass |
| Chapter tests | 1 | 1 | pass |
| Deutsch Fokus (logo) | 1 | 1 | pass |

## 9 · File size

- this build: 2423 KB for 20 pages (11 learning pages, 9 others); 117.3 KB per page without fonts
- full book, vector artwork only: about **41.6 MB** for roughly 362 pages
- full book with final illustrations: about 109 picture slots; at 150 KB each (JPEG, 150 dpi) that adds 16 MB → about **58 MB** (target: under 40 MB)
