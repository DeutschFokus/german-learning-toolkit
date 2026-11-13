#!/usr/bin/env python3
"""Export the narration of every script as a recording script for your own voice.

Reads youtube-skripte/NN-*.md and writes sprechertext/NN-*-sprechertext.txt with
chapter headings and [NN] scene markers. Run:  python3 youtube-skripte/sprechertext/export.py
"""
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
SCRIPTS_DIR = HERE.parent
SCENE_RE = re.compile(r"^\*\*(\d+)\*\* · `")

TIPS = [
    "So nimmst du auf:",
    "- Lies Kapitel für Kapitel ein und mach nach jedem Kapitel eine kurze Pause. So kannst du einzelne Kapitel neu aufnehmen.",
    "- Die Nummern in eckigen Klammern [01] sind die Szenen- und Bildnummern. Du liest sie nicht vor, sie helfen dir beim Schnitt.",
    "- Lass bei jedem Absatz eine Sekunde Luft. Kurze Sätze bewusst kurz und betont sprechen.",
    "- Jahreszahlen wie gewohnt sprechen: 1324 = dreizehnhundertvierundzwanzig.",
]


def export(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    title = lines[0].lstrip("# ").strip()
    words = sum(len(l[2:].split()) for l in lines if l.startswith("> "))
    out = [title.upper(), "Sprechertext zum Einsprechen",
           f"{words} Wörter · ca. {words / 150:.0f}–{words / 140:.0f} Minuten bei ruhigem Doku-Tempo "
           "(140–150 Wörter pro Minute)", "", *TIPS, ""]
    for i, line in enumerate(lines):
        if line.startswith("## Shorts"):
            break
        if line.startswith("## ") and not line.startswith("## Beschreibung"):
            out += ["", f"=== {line[3:].strip()} ===", ""]
        match = SCENE_RE.match(line)
        if match:
            narration, j = [], i + 1
            while j < len(lines) and lines[j].startswith("> "):
                narration.append(lines[j][2:])
                j += 1
            out += [f"[{match.group(1)}]", " ".join(narration), ""]
    target = HERE / f"{path.stem}-sprechertext.txt"
    target.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
    print(f"{target.name}: {words} words")


if __name__ == "__main__":
    for script in sorted(SCRIPTS_DIR.glob("[0-9][0-9]-*.md")):
        export(script)
