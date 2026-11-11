#!/usr/bin/env python3
"""Generate the static font instances the books are set in.

The four families ship as variable fonts (assets/fonts/variable, unmodified, SIL OFL 1.1).
This script cuts the handful of instances the design uses and stores them, renamed, in
assets/fonts/static. Static instances make the PDFs smaller and render identically on every
machine. The instances are Modified Versions in the sense of the OFL: they carry new names
("DF …") and stay under the OFL.

    python tools/make_fonts.py
"""
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "fonts" / "variable"
OUT = ROOT / "assets" / "fonts" / "static"

# (output name, source file, axis location, CSS weight, italic)
INSTANCES = [
    # Fraunces — one instance per typographic role; the CSS weight selects the role
    ("DFFraunces-Hero", "Fraunces-VF.ttf", {"wght": 900, "opsz": 144, "SOFT": 100, "WONK": 0}),
    ("DFFraunces-Num", "Fraunces-VF.ttf", {"wght": 800, "opsz": 24, "SOFT": 100, "WONK": 0}),
    ("DFFraunces-Sub", "Fraunces-VF.ttf", {"wght": 650, "opsz": 24, "SOFT": 80, "WONK": 0}),
    ("DFFraunces-Title", "Fraunces-VF.ttf", {"wght": 620, "opsz": 72, "SOFT": 60, "WONK": 0}),
    ("DFFraunces-Cover", "Fraunces-VF.ttf", {"wght": 540, "opsz": 144, "SOFT": 70, "WONK": 0}),
    ("DFFraunces-Text", "Fraunces-VF.ttf", {"wght": 500, "opsz": 24, "SOFT": 60, "WONK": 0}),
    ("DFFraunces-TextItalic", "Fraunces-Italic-VF.ttf", {"wght": 500, "opsz": 36, "SOFT": 50, "WONK": 0}),
    # Source Sans 3
    ("DFSans-Regular", "SourceSans3-VF.ttf", {"wght": 400}),
    ("DFSans-Italic", "SourceSans3-Italic-VF.ttf", {"wght": 400}),
    ("DFSans-SemiBold", "SourceSans3-VF.ttf", {"wght": 600}),
    ("DFSans-Bold", "SourceSans3-VF.ttf", {"wght": 700}),
    ("DFSans-BoldItalic", "SourceSans3-Italic-VF.ttf", {"wght": 700}),
    ("DFSans-ExtraBold", "SourceSans3-VF.ttf", {"wght": 800}),
    # Source Serif 4 at its text optical size
    ("DFSerif-Regular", "SourceSerif4-VF.ttf", {"wght": 400, "opsz": 11}),
    ("DFSerif-Italic", "SourceSerif4-Italic-VF.ttf", {"wght": 400, "opsz": 11}),
    ("DFSerif-Bold", "SourceSerif4-VF.ttf", {"wght": 700, "opsz": 11}),
    # Caveat
    ("DFHand-Medium", "Caveat-VF.ttf", {"wght": 500}),
    ("DFHand-Bold", "Caveat-VF.ttf", {"wght": 700}),
]


def rename(font: TTFont, full: str) -> None:
    family, _, style = full.partition("-")
    family = {"DFFraunces": "DF Fraunces", "DFSans": "DF Sans", "DFSerif": "DF Serif", "DFHand": "DF Hand"}[family]
    name = font["name"]
    for rec in list(name.names):
        if rec.nameID in (1, 16):
            rec.string = f"{family} {style}"
        elif rec.nameID in (2, 17):
            rec.string = "Regular"
        elif rec.nameID == 4:
            rec.string = f"{family} {style}"
        elif rec.nameID == 6:
            rec.string = full
        elif rec.nameID == 3:
            rec.string = f"DeutschFokus:{full}"
        elif rec.nameID in (21, 22, 25):
            name.names.remove(rec)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    for full, src, loc in INSTANCES:
        font = TTFont(SRC / src)
        axes = {a.axisTag for a in font["fvar"].axes}
        inst = instancer.instantiateVariableFont(font, {k: v for k, v in loc.items() if k in axes}, static=True)
        rename(inst, full)
        for tag in ("STAT", "MVAR", "avar"):
            if tag in inst:
                del inst[tag]
        path = OUT / f"{full}.ttf"
        inst.save(path)
        total += path.stat().st_size
        print(f"{full:24} {path.stat().st_size / 1024:7.0f} KB   {loc}")
    print(f"{len(INSTANCES)} instances, {total / 1048576:.1f} MB")


if __name__ == "__main__":
    main()
