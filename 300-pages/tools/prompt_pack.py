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

STYLE = ("Flat vector editorial illustration for a language course book. Bold simple geometric shapes, no outlines, "
         "no gradients, no texture, flat colour with at most one darker tone for shadows. Rounded forms; circles and arches "
         "in the background; generous empty areas; calm and friendly. People have simple faces with two dot eyes and a small "
         "smile, natural adult proportions, mitten-like hands, clothes in solid colours. "
         "Never draw any text, letters, numbers, logos or watermarks: signs, screens and notes stay blank.")
CAST = {
    "elif": "Elif – woman, 27, long dark brown hair, warm light brown skin, vermilion red top (#E4572E), navy trousers",
    "jonas": "Jonas – man, 30, short light brown hair, fair skin, periwinkle blue top (#5B6EE1)",
    "becker": "Herr Becker – man, 68, short grey hair and grey beard, fair skin, green top (#3F7D6A), brown trousers",
    "yilmaz": "Frau Yılmaz – woman, 45, dark bob haircut, glasses, light brown skin, dark blue top (#2E4A8F)",
    "mariam": "Mariam – woman, 34, plum headscarf (#7A3E69), brown skin, plum top",
    "kofi": "Kofi – man, 25, short black curly hair, dark brown skin, yellow top (#E9A21F)",
    "lena": "Lena – woman, 29, red hair in a bun, fair skin, teal top (#2A9D8F)",
    "nowak": "Herr Nowak – man, 52, bald with brown hair at the sides, glasses, light skin, grey top (#6B7280)",
}
NAMES = {"Elif": "elif", "Jonas": "jonas", "Becker": "becker", "Yılmaz": "yilmaz", "Mariam": "mariam", "Kofi": "kofi", "Lena": "lena", "Nowak": "nowak"}
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
A("## Step 2 · Character sheets (eight pictures, once)\n")
A("One prompt per person. Approve each sheet before you go on – they are the reference for all scenes. "
  "Save them as `cast-elif.png`, `cast-jonas.png` and so on.\n")
for key, line in CAST.items():
    A(f"**{line.split(' – ')[0]}**\n")
    A(f"```text\nCharacter sheet, square 1:1, plain cream background (#FBF4E6).\n{line}.\n"
      "Show the same person three times, full body, standing: front view, three-quarter view, and walking. "
      "Friendly, relaxed. No props, no text.\n```\n")
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
