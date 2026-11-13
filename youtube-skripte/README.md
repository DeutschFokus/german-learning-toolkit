# Virale Edutainment-Skripte (Deutsch, 16:9, nur Bilder)

| # | Skript | Bilder | Ø pro Bild | Länge* |
|---|--------|--------|-----------|--------|
| 1 | [Wie Muslime die moderne Welt erfunden haben](01-muslimische-erfinder.md) | 103 | 6,0 s | ~10:18 |
| 2 | [Warum du trotz Vollzeitjob nie reich wirst](02-geld-inflation.md) | 107 | 5,8 s | ~10:21 |
| 3 | [Dein Gehirn wird gehackt](03-gehirn-gehackt.md) | 104 | 5,7 s | ~9:55 |
| 4 | [Warum die Deutsche Bahn nie pünktlich ist](04-deutsche-bahn.md) | 96 | 5,7 s | ~9:10 |
| 5 | [Al-Biruni: Er hat die Erde mit einem Berg vermessen](05-al-biruni-erde-vermessen.md) | 85 | 7,1 s | ~10:02 |
| 6 | [So dachten die reichsten Händler der Geschichte](06-reichste-haendler.md) | 80 | 7,4 s | ~9:48 |
| 7 | [Konzentration in 30 Tagen zurücktrainieren](07-konzentration-30-tage.md) | 74 | 7,8 s | ~9:40 |
| 8 | [Warum das deutsche Internet so langsam ist](08-deutsches-internet.md) | 75 | 7,8 s | ~9:44 |
| 9 | [Ibn Battuta: 24 Jahre unterwegs](09-ibn-battuta.md) | 76 | 7,6 s | ~9:36 |
| 10 | [Geld ohne Zinsen: islamisches Finanzwesen](10-islamische-finanzierung.md) | 80 | 7,4 s | ~9:55 |
| 11 | [Wie Kinder 600 Seiten auswendig lernen](11-hafiz-gedaechtnis.md) | 78 | 7,4 s | ~9:35 |
| 12 | [Warum die Deutschen ihr Bargeld so lieben](12-bargeld-1923.md) | 73 | 7,8 s | ~9:33 |
| 13 | [Zheng He: der muslimische Admiral](13-zheng-he.md) | 74 | 7,5 s | ~9:13 |
| 14 | [Zakat: Wie viel musst du wirklich geben?](14-zakat-berechnen.md) | 88 | 6,9 s | ~10:07 |
| 15 | [Was nachts in deinem Gehirn passiert](15-schlaf-lernhack.md) | 76 | 7,6 s | ~9:39 |
| 16 | [Warum so viele Deutsche zur Miete wohnen](16-miete-deutschland.md) | 75 | 7,8 s | ~9:43 |
| 17 | [Warum ausgerechnet Europa die Ozeane beherrschte](17-europa-ozeane.md) | 80 | 7,1 s | ~9:29 |
| 18 | [Waqf: Wie ein Brunnen seit 1.400 Jahren Gutes tut](18-waqf-stiftungen.md) | 76 | 7,5 s | ~9:31 |
| 19 | [Was beim Fasten in deinem Körper passiert](19-fasten-koerper.md) | 80 | 7,2 s | ~9:35 |
| 20 | [Warum Deutschland so viel Bürokratie hat](20-buerokratie.md) | 76 | 7,3 s | ~9:12 |

Die Skripte 13–16 sind nach einer stärkeren Story-Formel gebaut: kalter Einstieg, drei offene Fragen, eine Figur als roter Faden, Re-Hooks und ein Wendepunkt am Ende. Die Formel und über 25 neue Ideen stehen in [IDEEN.md](IDEEN.md).

Die Skripte 5–8 sind die Folgevideos, die in den Outros von 1–4 angekündigt werden (1→5, 2→6, 3→7, 4→8). Jedes Folgevideo kündigt im Outro schon das nächste Thema an: Ibn Battuta, islamische Finanzierung ohne Zinsen, Gedächtnistechniken der Koran-Hafiz und die Bargeld-Liebe der Deutschen.

Die Skripte 9–12 sind genau diese Themen (5→9, 6→10, 7→11, 8→12). Ihre Outros kündigen wiederum an: Zheng He, den muslimischen Admiral aus China, Zakat richtig berechnen, Schlaf als Lernhack und warum so viele Deutsche zur Miete wohnen.

\*Gemessen bei 135 Wörtern/Min. (ruhige Doku-Stimme). Bei einer schnelleren KI-Stimme werden die Bilder kürzer und das Video kürzer. Dann zwischen den Abschnitten kurze Pausen lassen, damit es über 8 Minuten bleibt (Mid-Roll-Werbung).

## Bild-Regeln

- Jeder Block = **ein Bild**: Nummer · geschätzte Standzeit · *Bild-Prompt*, darunter der Sprechertext, der während dieses Bildes läuft.
- Kein Bild steht länger als ca. 12 Sekunden. Im Durchschnitt wechselt das Bild alle 6–8 Sekunden. Der Hook ist absichtlich schneller geschnitten (2–6 s), weil die ersten 30 Sekunden über die Watchtime entscheiden.
- Jedes Bild mit leichtem Zoom oder Schwenk (Ken Burns) animieren, damit nichts statisch wirkt.
- Die Abschnitts-Überschriften zeigen die ungefähre Startzeit, damit du die Bilder beim Schneiden schnell zur Tonspur zuordnen kannst.

## Bild-Stil (für alle Prompts anhängen)

`cinematic, dramatic lighting, 16:9, hyper-detailed, muted colors with one strong accent color`

Halal-Hinweise: Propheten werden nie dargestellt (nur Orte, Licht, Kalligrafie). Personen erscheinen meist von hinten oder als Silhouette, das passt auch zu Zuschauern, die Abbildungen von Gesichtern meiden. Keine freizügigen Bilder. Statt Musik reichen Ambient-Sounds.

## Copy-paste-Bildprompts für Copilot

- **`prompts/00-konsistenz-bibel.md`**: Figuren-Karten, Stil-Block, Palette pro Video und Anleitung für Copilot. Zuerst lesen.
- **`prompts/01-…` bis `12-…`**: je ein Dokument pro Skript. Jeder Code-Block ist ein vollständiger, eigenständiger Prompt (Szene + Figuren-Karte + Palette + Stil). Einfach kopieren und einfügen.
- **Änderungen**: Figuren und Stil stehen einmal in `prompts/build.py`, die Szenen in `prompts/src/NN.txt`. Nach einer Änderung `python3 prompts/build.py` ausführen, dann sind alle Prompts wieder einheitlich.

## Hochladen und Monetarisierung

- **Reihenfolge:** Skript 4 (Bahn) zuerst für Reichweite, dann Skript 2 (Geld, höchster CPM), danach 1 und 3.
- **Folgevideos:** Lade jedes Folgevideo 1–2 Wochen nach seinem Vorgänger hoch und verlinke beide gegenseitig über Endscreen und angepinnten Kommentar. So schauen die Zuschauer direkt das nächste Video.
- **Shorts:** Aus jedem Skript 3–5 Shorts schneiden, z. B. „5:59 gilt als pünktlich“, „Algorithmus ist der Name eines Muslims“, „Die Taube in deinem Handy“, „Dein Dönerpreis erklärt Inflation“, „Er vermaß die Erde mit einem Berg“, „88 Cent Miete im Jahr“, „Die Übung, die fast niemand macht“, „Geld zurück bei langsamem Internet“. Am Ende jedes Shorts: „Ganzes Video auf dem Kanal“.
- **Fakten vor Veröffentlichung kurz prüfen**, vor allem Bahn-Pünktlichkeit, Inflationszahlen und Fahrgastrechte, weil sich diese Werte jedes Jahr ändern.
