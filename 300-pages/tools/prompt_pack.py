#!/usr/bin/env python3
"""Ready-to-paste prompts for an image model (ChatGPT etc.): project instructions, one prompt per
character sheet and one per picture slot. Writes docs/prompt-pack-<level>.md and a PDF of it.

    python tools/prompt_pack.py --level a2 --chapters 5,Z2
"""
import argparse
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pydantic import BaseModel  # noqa: E402

from engine import models as M  # noqa: E402
from engine.config import load_config  # noqa: E402
from engine.loader import load_book  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--level", default="a2")
ap.add_argument("--chapters", default=None)
a = ap.parse_args()
cfg = load_config(a.level, "en")
book = load_book(cfg, a.chapters)

STYLE = ("Flat vector illustration in exactly the style of the attached cast overview: bold simple shapes, no outlines, "
         "no gradients, no texture, flat colour with at most one darker tone for shadows. Rounded forms; circles and arches "
         "in the background; generous empty areas; calm and friendly. People look exactly like their character sheets: "
         "short friendly proportions with slightly large heads, dot eyes, eyebrows, clear mouth shapes, mitten-like hands. "
         "Never draw any text, letters, numbers, logos or watermarks: signs, screens and notes stay blank.")
CAST = {
    "elif": "Elif – woman, 27, nurse: teal headscarf, teal scrubs with a small white heart pin, light skin",
    "rahul": "Rahul – man, 24, student: black curly hair, round glasses, magenta hoodie, brown skin",
    "david": "Herr Berger (David) – man, 38, caretaker: tall and broad, short dark hair, moustache, orange work jacket, key ring",
    "amina": "Frau Diallo (Amina) – woman, 29, property manager: dark skin, afro curls with a colourful headband, ivory blazer",
    "maria": "Maria – woman, 48, neighbour: brown hair in a low bun with grey strands, rounder build, red top with cream apron",
    "yusuf": "Yusuf – man, 33, craftsman: blue baseball cap, dark beard, denim work shirt, tool belt",
    "anna": "Anna – woman, 25, student: long wavy brown hair, gold hoop earrings, cream jumper, backpack",
    "alvarez": "Herr Alvarez – man, 52, landlord: grey swept-back hair, grey beard, slate blazer",
}
NAMES = {"Elif": "elif", "Rahul": "rahul", "Berger": "david", "Diallo": "amina", "Maria": "maria", "Yusuf": "yusuf", "Anna": "anna", "Alvarez": "alvarez"}
FORMAT = {"banner": ("very wide banner, about 9:4 (ask for 16:9 and I crop top and bottom)",
                     "Put all people in the right two thirds. The lower left corner must be plain empty wall and floor."),
          "wide": ("landscape 4:3", "Keep everything important in the middle of the height; top and bottom may be cropped."),
          "strip": ("wide landscape 16:9", "Keep everything important in the middle band; top and bottom will be cropped."),
          "tall": ("almost square, 1:1", "Keep everything important away from the top and bottom edges."),
          "square": ("square 1:1", "")}


def walk(obj, found):
    if isinstance(obj, M.Image):
        found.append(obj)
    elif isinstance(obj, BaseModel):
        for v in obj.__dict__.values():
            walk(v, found)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            walk(v, found)


L = []
A = L.append
A(f"# Prompt pack · {cfg.level_name}\n")
A("Copy and paste, in this order. Everything in a grey box is one prompt.\n")
A("## Step 1 · Project instructions (once)\n")
A("In ChatGPT: create a Project, open its instructions and paste this. It then applies to every picture.\n")
A("```text\nYou are illustrating a German course book. Every image you make follows this style exactly:\n\n" + STYLE +
  "\n\nBase colours for every picture: navy #1B1E2F for the darkest details instead of black, cream #FBF4E6 and white for light. "
  "Each request names a few more palette colours – use only those plus the colours of the characters.\n"
  "When I attach character sheets, the people must match them exactly: same hair, same skin tone, same top.\n```\n")
A("## Step 2 · Character sheets (once)\n")
A("The eight people of this book come from the approved cast overview. Attach `cast-overview.png` to each request. "
  "Save the sheets as `cast-elif.png`, `cast-rahul.png` and so on.\n")
for key, line in CAST.items():
    A(f"**{line.split(' – ')[0]}**\n")
    A(f"```text\nCharacter sheet, square, plain cream background (#FBF4E6), matching this person exactly as shown in the cast overview.\n{line}.\n"
      "Top row: full body front view, three-quarter view, walking. "
      "Bottom row: five head close-ups – happy, surprised, confused, annoyed, proud. No text.\n```\n")
A("## Step 3 · The pictures\n")
A("For each picture: attach the character sheets of the people named in it (and one finished scene as a style example, "
  "once you have one), then paste the prompt. Save the result under the file name shown.\n")
for part in book.parts():
    is_ch = isinstance(part, M.Chapter)
    t = cfg.chapter_tokens(part.number) if is_ch else cfg.station_tokens()
    pal = f"{t['mid']} (the one strong colour), {t['hl']}, {t['soft']}, {t['wash']}, {t['deep']} for small dark details"
    found = []
    if is_ch:
        found.append(part.image.model_copy(update={"format": "banner"}))
    for teil in part.teile:
        walk(teil.blocks, found)
    A(f"### {'Kapitel ' + str(part.number) + ' · ' + part.title if is_ch else part.title}\n")
    for im in found:
        ratio, note = FORMAT[im.format]
        who = [CAST[k] for n, k in NAMES.items() if n in im.description]
        scene_en = cfg.t(im.alt) if im.alt else ""
        A(f"**`{im.id}.jpg`**\n")
        p = [f"Format: {ratio}.", f"Palette: {pal}.", f"Scene: {scene_en}", f"Details (German brief): {im.description}"]
        if who:
            p.append("People (match the attached character sheets):\n- " + "\n- ".join(who))
        if im.markers:
            p.append("This is a picture dictionary seen from above, like a colourful floor plan. Draw every object clearly and "
                     "separately with calm space around it; number labels are added later, so draw no numbers.")
        if note:
            p.append("Composition: " + note)
        p.append("No text, letters or numbers anywhere.")
        A("```text\n" + "\n".join(p) + "\n```\n")
A("## Step 4 · Send them back\n")
A(f"Put the files into `300-pages/assets/images/{cfg.level}/` with exactly the names above, or send them in the chat. "
  "They are then switched on, cropped to their slots and checked on the page.\n")
md = "\n".join(L)
out = ROOT / "docs" / f"prompt-pack-{cfg.level}.md"
out.write_text(md, encoding="utf-8")


def to_pdf(md_path: Path) -> Path:
    import markdown
    from weasyprint import HTML
    body = markdown.markdown(md_path.read_text(encoding="utf-8"), extensions=["fenced_code", "tables"])
    f = (ROOT / "assets/fonts/static").as_uri()
    css = (f'@font-face{{font-family:S;src:url("{f}/DFSans-Regular.ttf")}}@font-face{{font-family:S;font-weight:700;src:url("{f}/DFSans-Bold.ttf")}}'
           f'@font-face{{font-family:S;font-style:italic;src:url("{f}/DFSans-Italic.ttf")}}@font-face{{font-family:F;src:url("{f}/DFFraunces-Title.ttf")}}'
           "@page{size:A4;margin:18mm 18mm 20mm;@bottom-right{content:counter(page);font:8pt S;color:#888}}"
           "body{font:10pt/1.5 S;color:#1B1E2F}h1{font:26pt F;margin:0 0 4mm}h2{font:16pt F;margin:9mm 0 2mm;break-after:avoid}"
           "h3{font:700 11pt S;margin:6mm 0 1mm;break-after:avoid}p{margin:0 0 2.5mm}"
           "pre{background:#F3F1EC;border-radius:2mm;padding:3mm 4mm;font:8.6pt/1.45 S;white-space:pre-wrap;break-inside:avoid;margin:0 0 4mm}"
           "code{font:inherit;background:#F3F1EC;padding:0 .8mm;border-radius:.8mm}pre code{background:none;padding:0}"
           "table{border-collapse:collapse;width:100%;font-size:8.8pt;margin:0 0 4mm}td,th{border-top:.5pt solid #ccc;padding:1.4mm 2mm 1.4mm 0;text-align:left;vertical-align:top}"
           "ul,ol{margin:0 0 2.5mm;padding-left:5mm}")
    pdf = md_path.with_suffix(".pdf")
    HTML(string=f"<html><head><meta charset='utf-8'><style>{css}</style></head><body>{body}</body></html>").write_pdf(pdf)
    return pdf


print(to_pdf(out), to_pdf(ROOT / "docs" / "illustration-style-guide.md"))
