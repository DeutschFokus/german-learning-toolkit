# QA report · demo build

A2 · Kapitel 5 „Wohnen“ (pages 101–124) and Zwischenstation 2 (pages 197–200) · built 2026-11-11 · engine 1.0-demo

Every build writes its own report to `dist/qa/`. This page sums up the six demo builds (`python tools/qa_summary.py`);
the full generated reports are in [`docs/qa/`](qa/). Only the last section is written by hand – all numbers come
from the finished PDFs.

## Verdict

| Check | English | Turkish | English · free sample | Turkish · free sample | English · print | English · fillable |
| --- | --- | --- | --- | --- | --- | --- |
| Pages · size | 41 · 853 KB | 41 · 856 KB | 20 · 446 KB | 20 · 447 KB | 41 · 876 KB | 41 · 1070 KB |
| Validation | pass | pass | pass | pass | pass | pass |
| Layout geometry | pass | pass | pass | pass | pass | pass |
| Links | pass | pass | pass | pass | pass | pass |
| Fonts | pass | pass | pass | pass | pass | pass |
| Text extraction | pass | pass | pass | pass | pass | pass |
| Tagged PDF | pass | pass | pass | pass | pass | pass |
| Cover | pass | pass | pass | pass | pass | pass |
| Contrast | pass | pass | pass | pass | pass | pass |
| Baseline grid | pass | pass | pass | pass | pass | pass |

All 9 checks pass in all 6 builds.

## What the checks do

| Check | How it is measured | Result (English edition) |
| --- | --- | --- |
| Validation | content model and book rules: missing article, plural or translation, duplicate address or track, task without answer, answer without task, audio without transcript, unknown speaker, page budgets | 0 errors, 0 warnings |
| Layout geometry | the position of every block in the finished PDF against the paginator's plan: overflow, overlap, height, distance to the footer; front matter and appendix against the folio line; text printed over text on any page | 0 problems on 28 learning pages and 11 front-matter and appendix pages |
| Links | every link annotation in the PDF is resolved against the named destinations; external URLs are checked for form | 648 internal link areas to 163 targets, 108 external to 13 URLs, 0 broken |
| Fonts | font dictionaries of the PDF | 16 faces, all embedded |
| Text extraction | all text is extracted with MuPDF and searched for replacement characters, letter-spaced runs, soft hyphens and zero-width characters | 0 broken characters, 0 letter-spaced runs |
| Tagged PDF | structure tree: every figure needs alternative text; document language | 225/225 figures with alt text, language de-DE |
| Cover | each text element of the cover must appear exactly once in the extracted text | 10 text elements, 0 duplicated or missing |
| Contrast | WCAG 2 contrast ratio of the text/background pairs of the design, for all 12 chapter palettes and all 6 covers | 101 colour pairs, 0 below WCAG AA |
| Baseline grid | the baseline of every body-size line in the PDF against the half-baseline grid | 98% of body lines on the half-baseline grid, 100% on the quarter grid |

## Validation log

```
Validation: 0 error(s), 0 warning(s)
  parts: 5, Z2 · tasks: 60 · vocabulary: 118 · audio tracks: 9
```

## Overflow, clipping, collisions, empty space, footers

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
| 108 | hauptteil | 93% | 100% | 4.2 mm to footer | ok |
| 109 | hauptteil | 95% | 95% | 17.4 mm to footer | ok |
| 110 | vertiefung | 93% | 93% | 20.1 mm to footer | ok |
| 111 | vertiefung | 92% | 100% | 4.2 mm to footer | ok |
| 112 | vertiefung | 95% | 99% | 5.5 mm to footer | ok |
| 113 | vertiefung | 91% | 100% | 4.2 mm to footer | ok |
| 114 | vertiefung | 97% | 100% | 4.2 mm to footer | ok |
| 115 | vertiefung | 99% | 100% | 4.2 mm to footer | ok |
| 116 | vertiefung | 97% | 100% | 4.2 mm to footer | ok |
| 117 | vertiefung | 92% | 92% | 23.0 mm to footer | ok |
| 118 | vertiefung | 96% | 100% | 4.2 mm to footer | ok |
| 119 | vertiefung | 75% | 100% | 4.2 mm to footer | ok |
| 120 | uebersicht | 91% | 91% | 25.4 mm to footer | ok |
| 121 | uebersicht | 96% | 96% | 14.8 mm to footer | ok |
| 122 | abschlusstest | 92% | 100% | 4.2 mm to footer | ok |
| 123 | abschlusstest | 96% | 100% | 4.2 mm to footer | ok |
| 124 | rueckblick | 95% | 100% | 4.2 mm to footer | ok |
| 197 | station | 96% | 100% | 4.2 mm to footer | ok |
| 198 | station | 91% | 91% | 26.6 mm to footer | ok |
| 199 | station | 90% | 100% | 4.2 mm to footer | ok |
| 200 | station | 97% | 100% | 4.2 mm to footer | ok |

Front matter and appendix pages are composed as whole pages; they are measured in the finished PDF (lowest text line against the folio line, at least 2 mm required).

| Page | Part | clearance | state |
| --- | --- | --- | --- |
| ii | front | 11.8 mm to folio | ok |
| iii | front | 16.8 mm to folio | ok |
| iv | front | 15.9 mm to folio | ok |
| v | front | 29.8 mm to folio | ok |
| vi | front | 57.1 mm to folio | ok |
| L 1 | answers | 16.2 mm to folio | ok |
| L 2 | answers | 21.5 mm to folio | ok |
| T 1 | transcripts | 30.6 mm to folio | ok |
| T 2 | transcripts | 141.2 mm to folio | ok |
| W 1 | wordlist | 15.3 mm to folio | ok |
| W 2 | wordlist | 15.3 mm to folio | ok |

The Turkish edition paginates identically (same pages, same blocks per page); its table is in `docs/qa/300-pages-a2-tr-qa.md`.

## Baseline alignment on facing pages

Every block starts on a multiple of half a baseline (7.5 pt), so running text on facing pages shares the same lines. Measured in the finished PDF over 705 body-size lines (tolerance 0.35 pt): **98%** sit on the half-baseline grid, **100%** on the quarter grid. The rest is text on ruled write-in lines and in phrase lists, which follow their own ruling. `shared` = grid lines that carry text on both pages of a spread.

| Spread | body lines | on half grid | on quarter grid | shared lines |
| --- | --- | --- | --- | --- |
| 101 | 13 | 100% | 100% | – |
| 102–103 | 51 | 100% | 100% | 0 |
| 104–105 | 41 | 100% | 100% | 0 |
| 106–107 | 80 | 100% | 100% | 6 |
| 108–109 | 51 | 100% | 100% | 4 |
| 110–111 | 66 | 100% | 100% | 2 |
| 112–113 | 43 | 88% | 100% | 2 |
| 114–115 | 41 | 100% | 100% | 2 |
| 116–117 | 54 | 100% | 100% | 3 |
| 118–119 | 23 | 100% | 100% | 0 |
| 120–121 | 58 | 79% | 100% | 2 |
| 122–123 | 69 | 100% | 100% | 6 |
| 124–197 | 42 | 100% | 100% | 2 |
| 198–199 | 57 | 100% | 100% | 1 |
| 200 | 16 | 100% | 100% | – |

## Links, bookmarks, page labels, metadata

- internal link areas: **648** pointing to 163 different targets, all resolved: **yes** (one link can consist of several clickable areas)
- named destinations in the file: 444
- external link areas: 108 → https://www.deutschfokus.example (104), https://www.youtube.com (3), mailto:hallo@deutschfokus.example (1)
- 13 different URLs, all well-formed: `https://www.deutschfokus.example/300`, `https://www.deutschfokus.example/audio`, `https://www.deutschfokus.example/audio/a2/5.01`, `https://www.deutschfokus.example/audio/a2/5.02`, `https://www.deutschfokus.example/audio/a2/5.03`, `https://www.deutschfokus.example/audio/a2/5.04`, `https://www.deutschfokus.example/audio/a2/5.05`, `https://www.deutschfokus.example/audio/a2/5.06`, `https://www.deutschfokus.example/audio/a2/5.07`, `https://www.deutschfokus.example/audio/a2/5.08`, `https://www.deutschfokus.example/audio/a2/Z2.01`, `https://www.youtube.com/@DeutschFokus`, `mailto:hallo@deutschfokus.example`
- bookmarks: level 1: 11, level 2: 16, level 3: 59 (Kapitel → Teil → Aufgabe)
- page labels: Cover, ii, iii, iv, v, vi, 101, 102 … L 2, T 1, T 2, W 1, W 2, Info
- metadata: title “300 Pages of A2 German – With English explanations”, author “Deutsch Fokus”, language de-DE
- tagged PDF: yes · figures with alternative text: 225 of 225

## Fonts

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

Embedded font data: 89 KB (subsets).

## Text extraction

Five pages, extracted with MuPDF and pasted unchanged: cover, chapter opener, a practice page, a page with an e-mail and
multiple choice, the first page of the answer key. Letter-spacing is done in CSS only, so headings come out as words; German
quotes, dashes and umlauts survive; the thin space in „S. 101“ is U+202F.

Whole file: 65,512 characters · 0 replacement characters · 0 letter-spaced runs · 461 umlauts/ß · 6 Turkish letters (ç ğ ı İ ş) · 0 soft hyphens · 0 zero-width characters.

### Page Cover

```text
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

### Page 101

```text
ILLUSTRATION
Elif steht mit einem Umzugskarton in ihrem neuen, noch leeren Wohnzimmer. Großes Fenster, Abendlicht,
Blick auf Dächer. In der Tür steht Herr Becker mit einer Pflanze.
5
5
KAPITEL 5
Wohnen
Home sweet home – flats, neighbours, house rules
DEIN ZIEL
Du kommst in deiner Wohnung und mit deinen
Nachbarn gut zurecht – von der Anzeige bis zur
Reparatur.
Handle life in your flat and with your neighbours – from listing to repair.
Das kann ich …
NOCH
NICHT
FAST
SICHER
Ich kann meine Wohnung beschreiben.
I can describe my flat.
Ich kann eine Wohnungsanzeige verstehen.
I can understand a flat listing.
Ich kann sagen, wo etwas steht und wohin es kommt.
I can say where things are and where they go.
Ich kann der Hausverwaltung ein Problem melden.
I can report a problem to the property management.
Ich kann Nachbarn höflich um Hilfe bitten.
I can politely ask neighbours for help.
Ich kann den Müll richtig trennen.
I can sort my rubbish correctly.
IN DIESEM KAPITEL
Wortschatz
102
Hauptteil
104
Vertiefung
110
Übersicht
120
Abschlusstest
122
Rückblick
124
GRAMMATIK
Wechselpräpositionen
wenn-Sätze
Passiv Präsens
5.1
a
Sieh das Bild an. Wie findest du Elifs Wohnung? Sprecht zu zweit.
L 1
Look at the picture. What do you think of Elif’s flat? Talk in pairs.
Ich finde die Wohnung …
Das Wohnzimmer ist hell / klein / gemütlich.
Mir gefällt …
WÖRTER AUF DIESER SEITE Words on this page
hell bright
gemütlich cosy
der Nachbar, -n neighbour
101
```

### Page 104

```text
KAPITEL 5 · WOHNEN / HAUPTTEIL
5
3
Die Wohnungsanzeige
Reading a flat listing and calling the landlord
ILLUSTRATION
Elif sitzt abends mit Laptop und Tee am Küchentisch. Auf dem Bildschirm sieht man drei
Wohnungsanzeigen mit kleinen Fotos; neben dem Laptop liegt ein Zettel mit ihren Wünschen.
5.3
a
Elif sucht eine Wohnung. Lies ihren Zettel und die
Anzeigen. Welche Wohnung passt?
/ 1
L 1
Elif is looking for a flat. Read her note and the listings. Which flat suits her?
Zu Elif passt …
Wohnung A.
Wohnung B.
Wohnung C.
WORT-HILFE
ZKB Zimmer, Küche, Bad
OG · EG upper floor · ground floor
EBK Einbauküche, fitted kitchen
KM · WM Kaltmiete · Warmmiete
NK Nebenkosten, service charges
MM Monatsmieten, months’ rent
LANDESKUNDE
Kaltmiete + Nebenkosten (heat-
ing, water, rubbish) = 
Warmmiete. Electricity and inter-
net usually cost extra.
Ich suche:
2 Zimmer · Balkon · höchstens 750 € warm · nicht im
Erdgeschoss
2-Zi.-Whg., Nordstadt 2 ZKB, 54 m², 3. OG, Balkon, EBK. KM 560 €
+ NK 140 €. Kaution: 2 MM. Frei ab 1. April.
A
Helle 1-Zi.-Whg., Zentrum 1 ZKB, 38 m², EG, kein Balkon. WM
520 €. Kaution: 1000 €. Ab sofort frei.
B
3-Zi.-Whg. mit Garten, Südstadt 3 ZKB, 78 m², EG, Garten, Keller.
KM 890 € + NK 210 €. Kaution: 3 MM.
C
A
B
C
5.3
b
Lies Anzeige A noch einmal und ergänze die Tabelle.
/ 6
L 1
Read listing A again and complete the table.
Zimmer
Kaltmiete
Größe
Nebenkosten
Stock
Warmmiete
WÖRTER AUF DIESER SEITE Words on this page
die Anzeige, -n ad, listing
die Miete, -n rent
die Kaltmiete, -n basic rent
die Warmmiete, -n rent incl. charges
die Nebenkosten (Pl.) service charges
die Kaution, -en deposit
das Erdgeschoss, -e ground floor
die Einbauküche, -n fitted kitchen
der Stock, Stockwerke floor
der Quadratmeter, - square metre
104
```

### Page 109

```text
KAPITEL 5 · WOHNEN / HAUPTTEIL
5
5.5
c
Ergänze die Verben in der richtigen Form.
/ 4
L 1
Fill in the verbs in the correct form.
nehmen
schließen
schreiben
sein
Wenn das Fenster nicht 
, 
 ich eine E-
Mail.
1
Wenn der Aufzug kaputt 
, 
 wir die Treppe.
2
TYPISCHER FEHLER
After a wenn-clause, the main clause starts with the verb.
Wenn ich die Heizung aufdrehe, sie bleibt kalt.
Wenn ich die Heizung aufdrehe, bleibt sie kalt.
5.5
d
Lies die E-Mail und kreuze an: A, B oder C?
/ 3
L 1
Read the email and tick A, B or C.
1 Seit wann ist die Heizung kalt? (Z. 4)
seit Samstag
seit Montag
seit drei Monaten
2 Was soll die Hausverwaltung tun? (Z. 6)
Elif anrufen
einen Handwerker schicken
eine neue Heizung kaufen
3 Wann ist Elif zu Hause? (Z. 6)
am Vormittag
am Wochenende
ab 15 Uhr
SO GEHT’S
A formal email starts with Sehr
geehrte Frau … or Sehr geehrter
Herr … and ends with Mit
freundlichen Grüßen. After the
greeting, carry on in lower case.
WORT-HILFE
erreichen to reach
der Handwerker, - repairman
defekt faulty
VON
elif.demir@post.example
|
AN
info@hv-nordstadt.example
BETREFF Heizung defekt – Lindenstraße 12
Sehr geehrte Frau Yılmaz,
ich wohne seit drei Monaten in der Lindenstraße 12, im
dritten Stock links. Leider gibt es ein Problem: Die
Heizung im Wohnzimmer funktioniert seit Samstag
nicht. Wenn ich sie aufdrehe, bleibt sie kalt.
Können Sie bitte einen Handwerker schicken? Ich bin
von Montag bis Mittwoch ab 15 Uhr zu Hause. Wenn Sie
mich anrufen möchten, erreichen Sie mich unter 0171
3920045.
Vielen Dank für Ihre Hilfe!
Mit freundlichen Grüßen
Elif Demir
5
10
A
B
C
A
B
C
A
B
C
WÖRTER AUF DIESER SEITE Words on this page
kaputt broken
schließen (hat geschlossen) to close
die Treppe, -n stairs
der Handwerker, - repairman
der Betreff, -e subject
erreichen to reach
das Problem, -e problem
109
```

### Page L 1

```text
ANHANG / LÖSUNGEN
L
Lösungen
Tap a task address to jump back to the task.
Kapitel 5 · Wohnen
5.1a
BEISPIEL Ich finde die Wohnung schön. Das Wohnzimmer
ist hell, aber noch leer. Mir gefällt das große Fenster.
S. 101
5.2a
Individuelle Lösung
S. 102
5.2b
1 die   2 das   3 der   4 das   5 die   6 der   7 das   8 der 
S. 102
5.2c
1 B   2 A   3 C   4 B S. 103
5.2d
BEISPIEL Meine Wohnung hat zwei Zimmer. Das Wohn-
zimmer ist hell und gemütlich. Leider habe ich keinen
Balkon.
S. 103
5.2e
BEISPIEL Meine Wohnung hat drei Zimmer. Ich habe
einen Balkon, aber keinen Keller. Mein Lieblingszimmer
ist die Küche, weil ich gern koche.
S. 103
5.3a
A S. 104
5.3b
1 2 · 560 €   2 54 m² · 140 €   3 3. Stock · 700 €
Warmmiete = Kaltmiete + Nebenkosten: 560 € + 140 € =
700 €.
S. 104
5.3c
1 frei   2 140 · extra   3 nein   4 Samstag · elf / 11   5
Lindenstraße S. 105
5.3d
BEISPIEL Guten Tag, ich rufe wegen der Wohnung in der
Südstadt an. Ist sie noch frei? – Ja, sie ist noch frei. – Wie
hoch sind die Nebenkosten? – 210 Euro im Monat, mit
Heizung. – Kann ich die Wohnung besichtigen? – Gern.
Passt es Ihnen am Freitag um 17 Uhr?
S. 105
5.3e
BEISPIEL Schöne 2-Zi.-Whg., 48 m², 2. OG, Balkon. KM
520 € + NK 120 €. Frei ab 1. Juni. Tel. 0171 3920012
S. 105
5.4a
Hören und Mitlesen
Listen and read along – nothing to check here.
S. 106
5.4b
1 die · der   2 das · dem   3 das · dem S. 106
5.4c
1 stelle   2 stehen   3 legt   4 liegt   5 stehen S. 107
5.4d
1 dem   2 das   3 im   4 den   5 dem   6 das S. 107
5.5a
Hören und Mitlesen
Listen and read along – nothing to check here.
S. 108
5.5b
1 R   2 F   3 R   4 F S. 108
5.5c
1 schließt · schreibe   2 ist · nehmen S. 109
5.5d
1 A   2 B   3 C S. 109
5.6a
1 C   2 E   3 D   4 A   5 B S. 110
5.6b
1 Mittwoch   2 Freitag   3 Dienstag S. 110
5.6c
1 wird · abgeholt   2 werden · geleert   3 wird · ge-
trennt   4 wird · geputzt   5 werden · gebracht   6
wird · repariert S. 111
5.6d
BEISPIEL Bei uns wird der Müll am Montag abgeholt. Das
Treppenhaus wird jede Woche geputzt. Die Fahrräder
werden im Keller abgestellt.
S. 111
5.7a
1 B   2 A   3 C S. 112
5.7b
1 B   2 A   3 B S. 112
5.7c
1 R   2 F   3 F   4 R S. 113
5.7d
BEISPIEL Liebe Frau Haddad, ab Montag bin ich zwei
Wochen im Urlaub. Könnten Sie bitte meine Blumen gie-
ßen? Der Schlüssel liegt bei Herrn Becker. Vielen Dank
und liebe Grüße, Elif Demir
S. 113
5.7e
BEISPIEL Entschuldigen Sie die Störung. Mein Internet
funktioniert nicht. Dürfte ich vielleicht kurz Ihr WLAN be-
nutzen? – Ja, gern. Kein Problem. Das Passwort steht
hier.
S. 113
5.8a
1 B   2 C   3 A   4 B S. 114
5.8b
1 F   2 R   3 R   4 R   5 F S. 115
```

Turkish edition, whole file: 65,303 characters · 0 replacement characters · 0 letter-spaced runs · 777 umlauts/ß · 1002 Turkish letters (ç ğ ı İ ş) · 0 soft hyphens · 0 zero-width characters.

## Cover

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

## Contrast (WCAG 2)

101 colour pairs are computed for every build; the table shows the weakest pair of each group. Normal text needs 4.5 : 1, large type 3 : 1.
The full table is section 7 of each generated report.

| Group | Pairs | Lowest ratio | Needs | |
| --- | --- | --- | --- | --- |
| Article colours on paper | 4 | 5.62 | 4.5 | pass |
| Article colours on their tint | 4 | 4.97 | 4.5 | pass |
| Margin-note labels on paper | 4 | 6.96 | 4.5 | pass |
| Body text on paper | 1 | 16.49 | 4.5 | pass |
| Muted text (explanations) on paper | 1 | 6.33 | 4.5 | pass |
| Handwriting on paper | 1 | 9.15 | 4.5 | pass |
| Text on chapter colour (tabs, chips) · 12 chapters | 12 | 6.73 | 4.5 | pass |
| Text on chapter wash (boxes) · 12 chapters | 12 | 15.13 | 4.5 | pass |
| Muted text on chapter wash · 12 chapters | 12 | 5.80 | 4.5 | pass |
| Text on highlight · 12 chapters | 12 | 11.23 | 4.5 | pass |
| Chapter labels on paper · 12 chapters | 12 | 9.31 | 4.5 | pass |
| Answer pointer on soft tint · 12 chapters | 12 | 7.69 | 4.5 | pass |
| Cover: cream type on the level colour · 6 levels | 6 | 3.56 | 3.0 | pass |
| Cover: cream 300 on the lighter circle · 6 levels | 6 | 3.01 | 3.0 | pass |
| Cover: navy on the cream band | 1 | 15.42 | 4.5 | pass |
| Cover: cream on the navy badge | 1 | 15.42 | 4.5 | pass |

## File size and build time

- this build: 853 KB for 41 pages (28 learning pages, 13 others); 18.6 KB per page without fonts
- full book, vector artwork only: about **6.9 MB** for roughly 371 pages
- full book with final illustrations: about 96 picture slots; at 150 KB each (JPEG, 150 dpi) that adds 14 MB → about **21 MB** (target: under 40 MB)
- build time: the 41-page demo takes about 30 s (layout 16 s cold, about 1 s with the block cache; render and write 14 s). Measuring costs
  about 40 ms per block and a full book has roughly 1,300 blocks, so a 300-page book should build in 4–5 minutes cold and 2–3 minutes
  with a warm cache. This is extrapolated – only one chapter exists.

## The five weakest things – and how to fix them

**1 · The pictures are placeholders.**
The demo proves the layout, not the look of a finished page. Nine picture slots show a calm
placeholder with the brief; the picture dictionary on page 102 teaches twelve words with a
picture that does not exist yet, and its pin positions are estimates. A course book lives from
its pictures – this is the largest gap between the demo and a product.
*Fix:* produce the pictures from `docs/image-briefs-a2.md` in the style of
`docs/illustration-style-guide.md`, starting with `k5-wohnung`; switch each one on with `src:`
and correct the pins in the content file. A full book needs about a hundred.

**2 · The print file is RGB, not PDF/X.**
`--print` adds 3 mm bleed, crop marks, TrimBox and BleedBox, and the tabs and cover really bleed.
But all colours are sRGB, black text is RGB black (on an offset press it would print in four
inks), and there is no output intent. Print-on-demand services that accept RGB will be fine;
an offset printer will send the file back.
*Fix:* add a last step to `--print` that converts to PDF/X-4 with a CMYK profile and pure-black
text (Ghostscript: `-dPDFX -sColorConversionStrategy=CMYK` with a black-preserving profile), then
run the result through a preflight tool once per level. Until then the PDF is a digital product.

**3 · The pages fit because the text was cut to fit.**
Every section has a fixed page budget and the build stops when a section is one line too long.
That is the point – nothing overflows silently – but it makes writing slow: pages 107 and 115
have half a line to spare in English, Turkish explanations run a little longer, and seventy-one
more chapters mean many rounds of trimming.
*Fix:* `tools/layout_report.py` already shows lines used per page and per block. Next step: let
the paginator squeeze before it fails (close the gaps between blocks by up to half a line,
let pictures shrink below their default height) and say in the error which block to shorten by
how many lines.

**4 · Long texts cannot run over a page, and the dense levels are only scaled.**
Every block is placed whole. That is right for A1–B1. At B2–C2 a full-page article with tasks
will not fit, and the level files only make type smaller and lines closer – there is no
two-column setting for long reading texts yet.
*Fix:* make `reading_text` breakable between paragraphs with running line numbers (the lines of
every paragraph are already measured), and add a two-column variant for B2–C2. This is needed
before the first B2 chapter, not before A1–B1.

**5 · Fillable fields and accessibility are a first step.**
In the `--forms` edition the answer circles of a multiple-choice question are independent tick
boxes (two can be ticked), nothing is checked or scored, and each PDF viewer draws typed text in
its own way. The PDF is tagged, every figure has alternative text and the language is set, but
the reading order follows the source – a margin note is read after its task – and it has not
been tested with a screen reader or a PDF/UA checker.
*Fix:* turn options into radio groups in `engine/post.py`; test the reading order with NVDA and
VoiceOver, then run PAC and fix what it reports.

**Smaller things**

- Phrase lists and chat bubbles keep their own rhythm; that is the 2–3 % of lines on the
  quarter grid instead of the half grid.
- With `design.opener: register` the side column of the opener is not on the baseline grid.
- Web address, shop link, audio links, contact and logo are placeholders; the audio itself does
  not exist. All links and QR codes are built from `series.yaml`.
- Only one chapter and one station exist. Build time and file size of a 300-page book are
  extrapolated from them.
- The word list gives page numbers only for the chapters that were built.
