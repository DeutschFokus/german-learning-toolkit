#!/usr/bin/env python3
"""Builds copy-paste image prompts for all 12 scripts plus the consistency bible.

Change a character card (CHARS) or the style block (STYLE) here once and rebuild:
every prompt that uses it changes together, so the text stays identical.

Scene lines live in prompts/src/NN.txt, one line per image cue:
    <cue number> | <character tags, comma separated, or -> | <english scene description>

Usage (from anywhere):
    python3 youtube-skripte/prompts/build.py            # build all prompt files + bible
    python3 youtube-skripte/prompts/build.py --dump 01  # list German cues of script 01
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
CUE = re.compile(r"^\*\*(\d+)\*\* · ~(\d+) s · \*(.*)\*$")

STYLE = (
    "Cinematic documentary still, 16:9 widescreen, 35mm film look, soft natural light, "
    "shallow depth of field, realistic detail. No visible faces, no text, no subtitles, "
    "no logos, no watermark, no brand names. Never depict the Prophet Muhammad or any prophet."
)

CHARS = {
    "VIEWER": (
        "VIEWER (recurring modern protagonist, always the same person): slim young adult, "
        "short dark hair, always seen from behind, face never visible; navy wool jacket over "
        "a grey hoodie, dark slim jeans, white sneakers, grey canvas backpack with a brown leather strap."
    ),
    "ALKHWARIZMI": (
        "AL-KHWARIZMI (9th-century Baghdad mathematician), seen from behind or in shadow: long "
        "pale-blue linen robe, dark brown wool outer robe, white turban, reed pen in hand, wooden writing board."
    ),
    "IBNHAYTHAM": (
        "IBN AL-HAYTHAM (10th-century scientist), seen in silhouette or from behind: long dark-green "
        "robe, dark wool cloak, white turban, brass oil lamp in one hand, small lens in the other."
    ),
    "FATIMA": (
        "FATIMA AL-FIHRI (9th-century founder in Fes), always from behind or in silhouette: long "
        "deep-blue dress with gold-embroidered hem, white head veil covering hair and shoulders, "
        "leather coin pouch at the waist."
    ),
    "IBNSINA": (
        "IBN SINA (AVICENNA, 11th-century physician), seen from behind: long ochre-brown robe, "
        "dark wool turban, leather-bound medical book under one arm."
    ),
    "ZAHRAWI": (
        "AL-ZAHRAWI (10th-century surgeon of Cordoba), seen from behind: long brown robe, white "
        "turban, a red velvet cloth with surgical instruments laid out in front of him."
    ),
    "FIRNAS": (
        "ABBAS IBN FIRNAS (9th-century inventor of Cordoba), seen from behind or in silhouette: "
        "sleeveless cream tunic over dark trousers, bare arms, wooden wing frame with white silk "
        "and feathers strapped to his back."
    ),
    "JAZARI": (
        "AL-JAZARI (13th-century engineer), seen from behind: long white robe with gold trim, dark "
        "brown turban, rolled technical drawing under one arm."
    ),
    "BIRUNI": (
        "AL-BIRUNI (11th-century scholar of Ghazni), seen from behind: long dark-blue robe, white "
        "turban, brass astrolabe hanging from a cord around his neck."
    ),
    "IDRISI": (
        "AL-IDRISI (12th-century cartographer of Sicily), seen from behind: long grey-green robe, "
        "white turban, parchment map rolled under one arm."
    ),
    "MARIAM": (
        "MARIAM AL-ASTURLABI (10th-century instrument maker of Aleppo), seen from behind or only her "
        "hands: long dark-teal dress, white head veil, fine metal tools in her hands."
    ),
    "MAHMUD": (
        "MAHMUD OF GHAZNI (11th-century ruler), seen in silhouette from behind: gold-embroidered "
        "dark-red robe, tall jeweled cap, guards standing around him."
    ),
    "MANSA_MUSA": (
        "MANSA MUSA (14th-century king of Mali), seen from behind or in silhouette: long white robe "
        "with gold embroidery, gold-trimmed cap, large gold pendant on the chest."
    ),
    "FUGGER": (
        "JAKOB FUGGER (16th-century Augsburg merchant), seen from behind or in silhouette: dark-burgundy "
        "velvet coat with a fur collar, black cap, heavy gold chain across the chest, ledger in hand."
    ),
    "KHADIJA": (
        "KHADIJA BINT KHUWAYLID (7th-century Meccan merchant), seen from behind or in silhouette: long "
        "dark-red dress, white veil covering her hair, trade ledger and a small brass scale."
    ),
    "ABDURRAHMAN": (
        "ABDURRAHMAN IBN AUF (7th-century Medinan merchant), seen from behind: simple white cotton "
        "robe, dusty leather sandals, small cloth bag over one shoulder."
    ),
    "IBNBATTUTA": (
        "IBN BATTUTA (14th-century traveler from Tangier), seen from behind: dusty beige travel robe, "
        "white turban, leather water flask, wooden staff, leather satchel."
    ),
    "SULTAN_DELHI": (
        "SULTAN MUHAMMAD IBN TUGHLUQ (14th-century ruler of Delhi), seen from behind or in silhouette: "
        "gold-embroidered red silk robe, jeweled turban, guards with spears."
    ),
    "ZHENG_HE": (
        "ZHENG HE (15th-century Chinese Muslim admiral), seen from behind or in silhouette: very tall, "
        "long dark-red silk robe with gold embroidery, black official's hat with side flaps, sword at the "
        "belt, a rolled sea chart in one hand."
    ),
    "EMPEROR_YONGLE": (
        "YONGLE EMPEROR (15th-century Ming ruler), only in silhouette from behind: yellow dragon robe, "
        "black winged crown, seated or standing in a vast palace hall."
    ),
    "HAFIZ_CHILD": (
        "HAFIZ CHILD (12-year-old boy), always from behind: short white prayer cap, light-blue long "
        "shirt, dark trousers, wooden Quran stand in front of him."
    ),
    "TEACHER": (
        "QURAN TEACHER (older man), seen in profile with face turned away: long grey robe, white cap, "
        "thin wooden pointer in one hand."
    ),
    "SAVER": (
        "ELDERLY SAVER (old woman, 1920s), seen from behind: black dress, grey wool shawl, holding a "
        "worn passbook."
    ),
    "CHILDREN_1923": (
        "CHILDREN OF 1923 (two children), seen from behind: short trousers, knitted jumpers, cloth caps, "
        "1920s styling."
    ),
}

# (number, script file, title, palette)
LIST = [
    ("01", "01-muslimische-erfinder.md", "Wie Muslime die moderne Welt erfunden haben", "warm gold, deep teal and candlelight amber"),
    ("02", "02-geld-inflation.md", "Warum du trotz Vollzeitjob nie reich wirst", "cool steel grey and blue, one single gold accent"),
    ("03", "03-gehirn-gehackt.md", "Dein Gehirn wird gehackt", "dark violet with electric red notification accents"),
    ("04", "04-deutsche-bahn.md", "Warum die Deutsche Bahn nie pünktlich ist", "overcast grey, signal red and amber warning light"),
    ("05", "05-al-biruni-erde-vermessen.md", "Al-Biruni: die Erde mit einem Berg vermessen", "desert ochre, deep night blue, moonlight silver"),
    ("06", "06-reichste-haendler.md", "So dachten die reichsten Händler der Geschichte", "rich amber, marketplace warmth, polished gold"),
    ("07", "07-konzentration-30-tage.md", "So trainierst du deine Konzentration in 30 Tagen", "soft morning green, warm beige, calm"),
    ("08", "08-deutsches-internet.md", "Warum das deutsche Internet so langsam ist", "cool screen blue and warm wood"),
    ("09", "09-ibn-battuta.md", "Ibn Battuta: 24 Jahre unterwegs", "dusty ochre, sunrise orange, aged parchment"),
    ("10", "10-islamische-finanzierung.md", "Geld ohne Zinsen: islamisches Finanzwesen", "emerald green and cream, clean architectural light"),
    ("11", "11-hafiz-gedaechtnis.md", "Wie Kinder 600 Seiten auswendig lernen", "candlelight gold and deep indigo"),
    ("12", "12-bargeld-1923.md", "Warum die Deutschen ihr Bargeld so lieben", "sepia for 1914–1948 scenes, cool modern tones for today"),
    ("13", "13-zheng-he.md", "Zheng He: der muslimische Admiral", "deep ocean blue, crimson sails, lantern gold"),
    ("14", "14-zakat-berechnen.md", "Zakat: Wie viel musst du wirklich geben?", "warm kitchen lamplight, soft gold and deep green"),
    ("15", "15-schlaf-lernhack.md", "Was nachts in deinem Gehirn passiert", "midnight blue, moonlight silver, soft violet"),
    ("16", "16-miete-deutschland.md", "Warum so viele Deutsche zur Miete wohnen", "warm brick red, overcast grey, golden window light"),
]


def parse_script(path):
    """Return ('h', heading) and ('c', no, seconds, german_prompt, narration) items in order."""
    lines = open(path, encoding="utf-8").read().split("\n")
    items, i = [], 0
    while i < len(lines):
        line = lines[i].strip()
        m = CUE.match(line)
        if line.startswith("### "):
            items.append(("h", line[4:].split(" · ")[0]))
        elif m:
            narr, j = [], i + 1
            while j < len(lines):
                nxt = lines[j].strip()
                if not nxt or CUE.match(nxt) or nxt.startswith("#"):
                    break
                narr.append(nxt)
                j += 1
            items.append(("c", int(m.group(1)), int(m.group(2)), m.group(3), " ".join(narr)))
            i = j
            continue
        i += 1
    return items


def load_specs(num):
    path = os.path.join(HERE, "src", f"{num}.txt")
    specs = {}
    if not os.path.exists(path):
        return specs
    for raw in open(path, encoding="utf-8"):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        idx, tags, scene = [p.strip() for p in line.split("|", 2)]
        specs[int(idx)] = (tags_of(tags), scene)
    return specs


def tags_of(text):
    out = []
    for t in text.split(","):
        t = t.strip()
        if t in ("", "-"):
            continue
        if t not in CHARS:
            sys.exit(f"unknown character tag: {t}")
        out.append(t)
    return out


def prompt_for(scene, tags, palette):
    parts = [scene.rstrip(".") + "."]
    parts += [CHARS[t] for t in tags]
    parts.append(f"Palette: {palette}.")
    parts.append(STYLE)
    return " ".join(parts)


def build_script(num, fname, title, palette):
    items = parse_script(os.path.join(SCRIPTS, fname))
    cues = [it for it in items if it[0] == "c"]
    specs = load_specs(num)
    nums = [c[1] for c in cues]
    if sorted(specs) != nums:
        missing = sorted(set(nums) - set(specs))
        extra = sorted(set(specs) - set(nums))
        sys.exit(f"{num}: {len(nums)} cues in script, {len(specs)} specs. missing={missing[:5]} extra={extra[:5]}")
    used = []
    for c in cues:
        for t in specs[c[1]][0]:
            if t not in used:
                used.append(t)
    secs = [c[2] for c in cues]
    out = [
        f"# Bildprompts – Skript {num}: {title}", "",
        f"**Palette:** {palette}  ",
        f"**Format:** 16:9 · **Bilder:** {len(cues)} · **Ø Standzeit:** {sum(secs) / len(secs):.1f} s · "
        f"**Gesamt:** ca. {sum(secs) // 60}:{sum(secs) % 60:02d} min", "",
        "Jeder Code-Block ist ein **eigenständiger Prompt**: kompletten Block kopieren und in Copilot einfügen. "
        "Die Figuren-Beschreibung steht immer vollständig drin, damit das Bild gleich aussieht.", "",
        "## Figuren in diesem Video", "",
    ]
    if used:
        out += [f"- {CHARS[t]}" for t in used]
    else:
        out.append("- Keine benannten Figuren, nur Umgebungen, Symbole und Hände.")
    out += ["", "## Prompts", ""]
    for it in items:
        if it[0] == "h":
            out += [f"## Abschnitt: {it[1]}", ""]
        else:
            _, idx, sec, _, narr = it
            tags, scene = specs[idx]
            out += [
                f"### {idx:02d} · ~{sec} s", "", "```text",
                prompt_for(scene, tags, palette), "```", "",
                f"*Sprechtext:* {narr}", "",
            ]
    return "\n".join(out) + "\n", len(cues), used


def usage_map():
    usage = {t: [] for t in CHARS}
    for num, _, _, _ in LIST:
        for t in {t for spec in load_specs(num).values() for t in spec[0]}:
            usage[t].append(num)
    return usage


BIBLE_HEAD = """# Konsistenz-Bibel: Figuren und Stil für alle 12 Skripte

## Warum das funktioniert
Copilot und andere Bildgeneratoren merken sich keine Gesichter von Bild zu Bild. Konsistenz entsteht deshalb nur durch drei Dinge:

1. Die Figuren-Beschreibung ist **wortgleich** in jedem Prompt (genau diese Texte unten).
2. Figuren werden **nie frontal mit Gesicht** gezeigt, nur von hinten, im Profil, als Silhouette oder mit Händen. Dort gibt es nichts, was abweichen kann.
3. Stil, Format und Palette sind **in jedem Prompt gleich**.

Zusätzlich gilt: Der Prophet wird nie dargestellt, und Menschen erscheinen nie mit erkennbarem Gesicht. Das ist halal-freundlich und macht die Figuren leichter konsistent.

## Regeln
- Format immer 16:9 (Querformat).
- Kein Text, keine Logos, keine Untertitel im Bild. Text kommt später im Schnitt.
- Kein Bild zeigt ein erkennbares Gesicht.
- Gleiche Figur = gleicher Kartentext. Nie umformulieren, nie kürzen.
- Symbole (Zahlen, Diagramme, Karten, Gegenstände) sind frei, aber immer im Stil des Videos.
- Die Bildbeschreibungen sind auf Englisch, weil Bildgeneratoren Englisch am zuverlässigsten verstehen. Die Sprechtexte bleiben auf Deutsch.

## Stil-Block (steht in jedem Prompt)
```text
STYLE_BLOCK
```

## Figuren-Karten
Jede Figur hat genau einen festen Kartentext. Die Liste zeigt, in welchen Skripten sie vorkommt.
"""

BIBLE_TAIL = """
## So nutzt du es in Copilot
1. Den kompletten Code-Block eines Prompts kopieren, inklusive Figuren-Karte und Stil. Nichts weglassen.
2. Jeden Prompt als neue Anfrage stellen, damit nichts aus dem vorherigen Bild übernommen wird.
3. Passt das Format nicht, "16:9 widescreen" im Prompt lassen und das Bildformat auf Querformat stellen, falls Copilot das anbietet.
4. Wenn eine Figur trotzdem abweicht: denselben Prompt neu generieren, bis das Ergebnis passt. Die beste Variante einer Figur für das ganze Video festhalten und nur noch diese verwenden.
5. Ehrlich dazu: Keine Methode garantiert 100 %. Mit Rücken, Silhouetten und Profilen fallen kleine Abweichungen im bewegten Video aber kaum auf.

## Palette pro Video
| Skript | Titel | Palette |
|---|---|---|
"""


def build_bible():
    usage = usage_map()
    lines = [BIBLE_HEAD.replace("STYLE_BLOCK", STYLE)]
    for t, card in CHARS.items():
        where = ", ".join(usage[t]) or "–"
        lines.append(f"- {card}  \n  *Skripte: {where}*")
    tail = BIBLE_TAIL + "\n".join(f"| {n} | {title} | {pal} |" for n, _, title, pal in LIST) + "\n"
    return "\n".join(lines) + "\n" + tail


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--dump":
        num = sys.argv[2]
        fname = next(f for n, f, _, _ in LIST if n == num)
        for it in parse_script(os.path.join(SCRIPTS, fname)):
            if it[0] == "c":
                print(f"{it[1]:02d} | ~{it[2]}s | {it[3]}")
        return
    total = 0
    for num, fname, title, palette in LIST:
        if not os.path.exists(os.path.join(HERE, "src", f"{num}.txt")):
            print(f"{num}: no src file yet, skipped")
            continue
        text, count, used = build_script(num, fname, title, palette)
        open(os.path.join(HERE, fname), "w", encoding="utf-8").write(text)
        total += count
        print(f"{num}: {count} prompts, characters: {', '.join(used) or '-'}")
    open(os.path.join(HERE, "00-konsistenz-bibel.md"), "w", encoding="utf-8").write(build_bible())
    print(f"total prompts: {total}; bible written")


if __name__ == "__main__":
    main()
