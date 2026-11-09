#!/usr/bin/env python3
"""Build "Your Learning Profile" — the fillable form students complete before lesson one.

    python3 guide/scripts/build_form.py       # -> guide/Your-Learning-Profile.pdf

1. Reads the questions from guide/form/learning-profile.yml (teacher name and
   brand come from guide/config.yml).
2. Writes an HTML page (guide/build/form.html) styled by guide/form/form.css.
3. scripts/render_form.cjs splits it into A4 pages (sections never split),
   prints it with Chromium and lays real PDF form fields over every drawn
   box: tick boxes, round buttons and text fields that work in Adobe Reader,
   Preview, browsers and phone PDF apps — and still print well on paper.

Requirements: as for build.py, plus `npm install` in guide/ (pdf-lib).
"""

from __future__ import annotations

import html
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

import yaml

GUIDE = Path(__file__).resolve().parent.parent
FORM = GUIDE / "form"
BUILD = GUIDE / "build"
SCRIPTS = GUIDE / "scripts"

FIELD_FONTS = [  # Unicode font for typed answers (first one found is embedded)
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "C:/Windows/Fonts/arial.ttf",
]

used_names: set[str] = set()


def esc(text) -> str:
    return html.escape(str(text), quote=True)


def slug(text) -> str:
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_") or "x"


def field_name(name: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_]+", name):
        sys.exit(f"Field name '{name}' may only contain letters, digits and underscores.")
    if name in used_names:
        sys.exit(f"Field name '{name}' is used twice in learning-profile.yml.")
    used_names.add(name)
    return name


# --------------------------------------------------------------------------
# building blocks — every clickable element carries data-field / data-kind
# --------------------------------------------------------------------------

def checkbox(name: str) -> str:
    return f'<span class="cb" data-field="{field_name(name)}" data-kind="check"></span>'


def radio(group: str, value: str) -> str:
    return f'<span class="rb" data-field="{group}" data-kind="radio" data-value="{value}"></span>'


def textbox(name: str, kind: str = "text", cls: str = "tf-box", style: str = "") -> str:
    style_attr = f' style="{style}"' if style else ""
    return f'<span class="{cls}" data-field="{field_name(name)}" data-kind="{kind}"{style_attr}></span>'


def title(q: dict, extra: str = "") -> str:
    hint = q.get("hint")
    if hint is None and q["type"] == "checks":
        hint = "Tick all that apply"
    hint_html = f'<span class="q-hint">{esc(hint)}</span>' if hint else ""
    return f'<div class="q-title">{esc(q["q"])}{hint_html}{extra}</div>'


def radio_group(q: dict) -> str:
    name = q["name"]
    field_name(name)
    return name


# --------------------------------------------------------------------------
# question types
# --------------------------------------------------------------------------

def q_text(q: dict) -> str:
    fields = q["fields"]
    cells = []
    for f in fields:
        hint = f'<span class="tf-hint">{esc(f["hint"])}</span>' if f.get("hint") else ""
        cells.append(
            f'<label class="tf"><span class="tf-label">{esc(f["label"])}{hint}</span>'
            f'{textbox(f["name"])}</label>'
        )
    return f'<div class="q tfs" style="--cols:{len(fields)}">{"".join(cells)}</div>'


def q_area(q: dict) -> str:
    height = 7 * int(q.get("lines", 2)) + 1
    box = textbox(q["name"], "multiline", "area", f"display:block;height:{height}mm")
    return f'<div class="q">{title(q)}{box}</div>'


def q_choices(q: dict, multiple: bool) -> str:
    name = q["name"]
    group = None if multiple else radio_group(q)
    items = []
    for option in q["options"]:
        control = checkbox(f"{name}_{slug(option)}") if multiple else radio(group, slug(option))
        items.append(f'<label class="opt">{control}<span>{esc(option)}</span></label>')
    if q.get("other"):
        control = checkbox(f"{name}_other") if multiple else radio(group, "other")
        items.append(
            f'<label class="opt opt-other">{control}<span>Other:</span>'
            f'{textbox(f"{name}_other_text", cls="tf-box tf-inline")}</label>'
        )
    return f'<div class="q">{title(q)}<div class="opts" style="--cols:{q.get("cols", 3)}">{"".join(items)}</div></div>'


def q_cards(q: dict) -> str:
    group = radio_group(q)
    cards = []
    for option in q["options"]:
        cards.append(
            f'<label class="card">{radio(group, slug(option["title"]))}'
            f'<span class="card-head"><span class="card-icon">{esc(option["icon"])}</span>'
            f'<span class="card-title">{esc(option["title"])}</span></span>'
            f'<span class="card-text">{esc(option["text"])}</span></label>'
        )
    return f'<div class="q">{title(q)}<div class="cards" style="--cols:{len(cards)}">{"".join(cards)}</div></div>'


def q_ratio(q: dict) -> str:
    group = radio_group(q)
    legend = '<span class="legend"><i class="you"></i>You speak<i class="me"></i>I speak</span>'
    cells = []
    for you, me in q["options"]:
        cells.append(
            f'<label class="ratio-opt"><span class="ratio-top">{radio(group, f"{you}_{me}")}'
            f'<span><b>{you}</b> / {me}</span></span>'
            f'<span class="bar"><span class="you" style="width:{you}%"></span></span></label>'
        )
    if q.get("decide"):
        cells.append(
            f'<label class="ratio-opt"><span class="ratio-top">{radio(group, "teacher_decides")}'
            f'<span class="decide">{esc(q["decide"])}</span></span><span class="bar unknown"></span></label>'
        )
    return f'<div class="q">{title(q, legend)}<div class="ratio" style="--cols:{len(cells)}">{"".join(cells)}</div></div>'


def q_scale(q: dict) -> str:
    name, cols = q["name"], q.get("cols", [1, 2, 3, 4, 5])
    rows = q["rows"]
    half = (len(rows) + 1) // 2
    tables = []
    for chunk in (rows[:half], rows[half:]):
        head = "".join(f"<th>{c}</th>" for c in cols)
        body = []
        for row in chunk:
            group = f"{name}_{slug(row)}"
            field_name(group)
            cells = "".join(f"<td>{radio(group, str(c))}</td>" for c in cols)
            body.append(f"<tr><td>{esc(row)}</td>{cells}</tr>")
        tables.append(f"<table><thead><tr><th></th>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>")
    hint = " · ".join(x for x in (q.get("low"), q.get("high")) if x)
    return f'<div class="q">{title({**q, "hint": hint})}<div class="scale">{"".join(tables)}</div></div>'


def q_grid(q: dict) -> str:
    name = q["name"]
    head = "".join(f"<th>{esc(c)}</th>" for c in q["cols"])
    body = []
    for row in q["rows"]:
        row_key = slug(row).split("_")[0]
        cells = "".join(f"<td>{checkbox(f'{name}_{slug(c)}_{row_key}')}</td>" for c in q["cols"])
        body.append(f"<tr><td>{esc(row)}</td>{cells}</tr>")
    table = f'<table class="avail"><thead><tr><th></th>{head}</tr></thead><tbody>{"".join(body)}</tbody></table>'
    return f'<div class="q">{title({**q, "hint": q.get("hint", "Tick all that apply")})}{table}</div>'


def q_numbers(q: dict) -> str:
    group = radio_group(q)
    nums = "".join(
        f'<label class="num">{radio(group, str(n))}<span>{n}</span></label>'
        for n in range(int(q.get("from", 1)), int(q.get("to", 10)) + 1)
    )
    return (
        f'<div class="q">{title(q)}<div class="numbers"><span class="end">{esc(q.get("low", ""))}</span>'
        f'<span class="num-line">{nums}</span><span class="end">{esc(q.get("high", ""))}</span></div></div>'
    )


def q_row(q: dict) -> str:
    items = q["items"]
    spans = " ".join(f'{item.get("span", 1)}fr' for item in items)
    inner = "".join(render_question(item) for item in items)
    return f'<div class="row" style="grid-template-columns:{spans}">{inner}</div>'


RENDERERS = {
    "text": q_text,
    "area": q_area,
    "checks": lambda q: q_choices(q, multiple=True),
    "radio": lambda q: q_choices(q, multiple=False),
    "cards": q_cards,
    "ratio": q_ratio,
    "scale": q_scale,
    "grid": q_grid,
    "numbers": q_numbers,
    "row": q_row,
}


def render_question(q: dict) -> str:
    if q.get("type") not in RENDERERS:
        sys.exit(f"Unknown question type {q.get('type')!r} in learning-profile.yml")
    return RENDERERS[q["type"]](q)


# --------------------------------------------------------------------------
# page
# --------------------------------------------------------------------------

def build_html(spec: dict, cfg: dict) -> str:
    blocks = [f"""
<div class="hero">
  <div class="hero-top"><span class="eyebrow">{esc(spec['eyebrow'])}</span><span class="brand">{esc(cfg.get('brand', ''))}</span></div>
  <h1>{esc(spec['title'])}</h1>
  <p>{esc(spec['intro'])}</p>
  <div class="chips"><span>⏱️ about 10 minutes</span><span>✔️ mostly tick boxes</span><span>🔒 just for planning our lessons</span></div>
</div>""",
        '<div class="how">' + "".join(f"<div><i>{esc(icon)}</i>{esc(text)}</div>" for icon, text in spec["how"]) + "</div>",
    ]
    for number, section in enumerate(spec["sections"], 1):
        questions = "".join(render_question(q) for q in section["questions"])
        blocks.append(
            f'<section class="sec"><div class="sec-head"><span class="sec-num">{number}</span>'
            f'<span class="sec-icon">{esc(section["icon"])}</span><h2>{esc(section["title"])}</h2>'
            f'<span class="sec-de">{esc(section["de"])}</span></div>{questions}</section>'
        )
    if spec.get("next"):
        nxt = spec["next"]
        steps = "".join(f'<div class="step"><b>{i}</b><span>{esc(text)}</span></div>'
                        for i, text in enumerate(nxt["steps"], 1))
        blocks.append(
            f'<div class="next"><h2>{esc(nxt["title"])}<span>{esc(nxt.get("de", ""))}</span></h2>'
            f'<div class="steps" style="--cols:{len(nxt["steps"])}">{steps}</div></div>'
        )
    blocks.append(f"""
<div class="closing">
  <div>
    <p><strong>{esc(spec['closing'].split(' ', 1)[0])}</strong> {esc(spec['closing'].split(' ', 1)[1])}</p>
    <div>Bis bald, <span class="sig">{esc(cfg.get('teacher', ''))}</span></div>
  </div>
  <label class="tf"><span class="tf-label">Date</span>{textbox('date')}</label>
</div>""")
    css = (FORM / "form.css").read_text(encoding="utf-8")
    footer = f"{spec['title']} · {cfg.get('brand', '')}".strip(" ·")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{esc(spec['title'])}</title>
<style>
{css}
</style>
</head>
<body data-footer="{esc(footer)}">
<div id="flow">
{''.join(blocks)}
</div>
</body>
</html>
"""


def main() -> None:
    spec = yaml.safe_load((FORM / "learning-profile.yml").read_text(encoding="utf-8"))
    cfg = yaml.safe_load((GUIDE / "config.yml").read_text(encoding="utf-8"))
    BUILD.mkdir(exist_ok=True)
    html_path = BUILD / "form.html"
    html_path.write_text(build_html(spec, cfg), encoding="utf-8")

    out_path = GUIDE / spec.get("output", "Your-Learning-Profile.pdf")
    font = next((f for f in FIELD_FONTS if Path(f).exists()), "")
    meta = f"{spec['title']}|{spec['eyebrow']}|{cfg.get('brand', '')}"
    result = subprocess.run(
        ["node", str(SCRIPTS / "render_form.cjs"), str(html_path), str(out_path), font, meta],
        capture_output=True, text=True,
    )
    sys.stdout.write(result.stdout)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        sys.exit("Building the form failed.")


if __name__ == "__main__":
    main()
