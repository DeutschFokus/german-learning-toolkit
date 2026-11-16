#!/usr/bin/env python3
"""Build the Russian Grammar Mastery Workbook.

Content lives in ../content as plain-text files (one per module / review).
This script parses them, runs consistency checks, writes an exercise ledger,
renders HTML and typesets the PDF with WeasyPrint.

Usage:
    python3 tools/build.py                 # full book -> output/*.pdf
    python3 tools/build.py --only sample   # one content file -> output/sample.pdf
    python3 tools/build.py --qa            # checks only (no PDF)
"""
import argparse
import collections
import csv
import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
OUT = ROOT / "output"
CSS = ROOT / "tools" / "style.css"
BOOK_TITLE = "Russian Grammar Mastery"
BOOK_SUB = "A personalized A1–A2 workbook"

TYPES = {
    "A": ("ENDINGS", "Missing endings"),
    "B": ("FORM", "Form from the dictionary form"),
    "C": ("PREP+CASE", "Preposition + ending"),
    "D": ("VERB FORM", "Conjugation"),
    "E": ("ASPECT", "Perfective or imperfective"),
    "F": ("UNJUMBLE", "Sentence building"),
    "G": ("CORRECT", "Error correction"),
    "H": ("TRANSFORM", "Transformation"),
    "I": ("MIXED", "Mixed completion"),
}
TYPE_GROUPS = [  # (label, type codes, target share)
    ("Missing endings & noun phrases", "AB", 0.40),
    ("Verb conjugation & aspect", "DE", 0.20),
    ("Sentence unjumbling", "F", 0.15),
    ("Prepositions & case government", "C", 0.10),
    ("Error correction & transformation", "GH", 0.10),
    ("Advanced mixed completion", "I", 0.05),
]
STAGES = {
    "A": ("Guided practice", 1, "One rule at a time. Hints name the question word or the case."),
    "B": ("Independent practice", 2, "Longer sentences and fewer clues. Decide every form yourself."),
    "C": ("Contrast practice", 3, "Look-alike sentences that need different forms. Find the trigger first."),
    "D": ("Mixed practice", 4, "Several rules at once: build, fix, transform and complete."),
    "E": ("Mastery check", 5, "No hints. Cover the answers, then aim for at least 36 of 40."),
}

# Planned exercise-type mix per module / review (targets; the QA report compares).
PLAN = {
    1: "A15 B12 D3 F5 G1 H2 I2", 2: "A15 B12 C1 D3 F5 G1 H1 I2", 3: "A12 B7 C10 D3 F5 G1 H1 I1",
    4: "A16 B12 C2 D2 F5 G1 H1 I1", 5: "A12 B9 C10 D2 F4 G1 H1 I1", 6: "A14 B12 C3 D3 F5 G1 H1 I1",
    7: "A14 B12 C3 D3 F5 G1 H1 I1", 8: "A14 B10 C6 D2 F5 G1 H1 I1", 9: "A19 B13 C2 F4 G1 I1",
    10: "A16 B13 C1 F4 G2 H1 I3", 11: "A15 B12 C2 F4 G1 H3 I3", 12: "A17 B10 C4 F4 G1 H1 I3",
    13: "A9 B7 C16 F4 G1 H1 I2", 14: "A9 B7 C16 F4 G1 H1 I2", 15: "A9 B11 C12 F4 G1 H1 I2",
    16: "A12 B18 C2 F4 G1 H1 I2", 17: "A10 B13 C8 D2 F4 G1 H1 I1", 18: "A12 B9 C6 D2 F4 G1 H1 I5",
    19: "A2 D26 F5 G2 H2 I3", 20: "A2 D24 E2 F5 G2 H2 I3", 21: "A2 D16 E10 F5 G2 H3 I2",
    22: "D5 E27 F4 G2 H1 I1", 23: "D4 E27 F4 G2 H1 I2", 24: "A6 B4 D16 E2 F5 G2 H2 I3",
    25: "A2 B2 C1 D12 E11 F5 G3 H2 I2", 26: "A2 C6 D18 E4 F5 G2 H1 I2", 27: "A4 B4 F23 G1 H5 I3",
    28: "F40", 29: "G40", 30: "A8 B6 C4 D4 E4 F5 G2 H2 I5",
    "R1": "A10 B6 C6 D3 F5 G2 H1 I2", "R2": "A10 B7 C4 D4 F5 G2 H1 I2",
    "R3": "A10 B7 C4 D4 F5 G2 H1 I2", "R4": "A9 B7 C6 D4 F5 G2 H1 I1",
    "R5": "A9 B7 C5 D4 F5 G2 H1 I2", "R6": "A5 B4 C2 D10 E5 F4 G2 H1 I2",
    "R7": "A5 B3 C2 D5 E10 F4 G3 H1 I2", "R8": "A6 B5 C4 D4 E6 F4 G3 H2 I1",
}

PARTS = {
    "I": ("Essential Grammar Foundations",
          "Gender and agreement, then the three cases that carry most everyday sentences: the accusative "
          "for objects and destinations, and the genitive for absence, possession and origin."),
    "II": ("Mastering All Six Cases",
           "Dative, instrumental and prepositional, then the endings that make phrases agree: adjectives, "
           "possessive and demonstrative pronouns, plurals. Ends with case choice without labels."),
    "III": ("Prepositions and Grammatical Relationships",
            "Which little word triggers which case: в / на / из / с, к / от / у / для / без, time expressions, "
            "numbers with nouns and the verbs that demand a particular case."),
    "IV": ("Verb Mastery",
           "Conjugation in the present, past and future, perfective versus imperfective aspect, reflexive "
           "verbs, verbs learners mix up, and the essential verbs of motion."),
    "V": ("Natural Russian Sentence Construction",
          "Word order, sentence building, error hunting and full integration: every decision from the "
          "workbook, made independently in complete sentences."),
}
ORDER = ["P:I", 1, 2, 3, 4, 5, "R1",
         "P:II", 6, 7, 8, 9, "R2", 10, 11, 12, "R3",
         "P:III", 13, 14, 15, "R4", 16, 17, 18, "R5",
         "P:IV", 19, 20, 21, "R6", 22, 23, 24, 25, 26, "R7",
         "P:V", 27, 28, 29, 30, "R8"]

FIELD_RE = re.compile(r"^([QHNAWV]):\s?(.*)$")
MULTI = {"learn", "target", "remix"}


def die(msg):
    sys.exit("ERROR: " + msg)


# ----------------------------------------------------------------------------- parsing
def parse(path):
    d = {"meta": {k: [] for k in MULTI}, "lesson": [], "blocks": [], "file": path.name}
    in_lesson, block, ex = False, None, None
    for ln, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.rstrip()
        if in_lesson:
            if line.strip() == "@endlesson":
                in_lesson = False
            else:
                d["lesson"].append(line)
            continue
        s = line.strip()
        if not s or s.startswith("//"):
            continue
        if s == "@lesson":
            in_lesson = True
            continue
        if s.startswith("@stage") or s.startswith("@block"):
            kw, _, rest = s.partition(" ")
            sid, _, title = rest.partition("|")
            block = {"kind": kw[1:], "id": sid.strip(), "title": title.strip(), "items": []}
            d["blocks"].append(block)
            ex = None
            continue
        if s.startswith("@"):
            k, _, v = s[1:].partition(" ")
            if k in MULTI:
                d["meta"][k].append(v.strip())
            else:
                d["meta"][k] = v.strip()
            continue
        if s.startswith("#"):
            t = s[1:].strip()
            if t not in TYPES:
                die(f"{path.name}:{ln}: unknown exercise type '{t}'")
            if block is None:
                die(f"{path.name}:{ln}: exercise outside a @stage/@block")
            ex = {"type": t, "line": ln, "file": path.name}
            block["items"].append(ex)
            continue
        m = FIELD_RE.match(s)
        if m and ex is not None:
            k, v = m.groups()
            if k in ex:
                die(f"{path.name}:{ln}: duplicate field {k}")
            ex[k] = v.strip()
            continue
        die(f"{path.name}:{ln}: cannot parse line: {s[:70]}")
    return d


def load_unit(key):
    """key: int module number, 'R1'.., or a bare file stem such as 'sample'."""
    if isinstance(key, int):
        p = CONTENT / f"m{key:02d}.txt"
    elif re.fullmatch(r"R\d", key):
        p = CONTENT / f"r{key[1:]}.txt"
    else:
        p = CONTENT / f"{key}.txt"
    if not p.exists():
        return None
    u = parse(p)
    u["key"] = key
    u["kind"] = "review" if (isinstance(key, str) and key.startswith("R")) else "module"
    n = 0
    for b in u["blocks"]:
        for ex in b["items"]:
            n += 1
            ex["n"] = n
            ex["stage"] = b["id"]
    return u


# ----------------------------------------------------------------------------- inline markup
CYR = "А-Яа-яЁё́"
RU_RUN = re.compile(rf"«?[{CYR}](?:[{CYR}\-\s,.!?;:«»—–…]*[{CYR}»])?")
GAP_RE = re.compile(r"_{2,}")


def esc(s):
    return html.escape(s, quote=False)


def gapify(s):
    def rep(m):
        n = len(m.group(0))
        if n >= 5:
            return '<span class="gap gap-long"></span>'
        if n >= 3:
            return '<span class="gap gap-word"></span>'
        return '<span class="gap gap-end"></span>'
    return GAP_RE.sub(rep, s)


def wrap_ru(s):
    # only touch text outside tags
    parts = re.split(r"(<[^>]+>)", s)
    for i, p in enumerate(parts):
        if p and not p.startswith("<"):
            parts[i] = RU_RUN.sub(lambda m: f'<span class="ru">{m.group(0)}</span>', p)
    return "".join(parts)


def inline(s, gaps=False, ru=False):
    s = esc(s)
    if gaps:
        s = gapify(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", s)
    s = s.replace("{tab}", '<span class="tab"></span>')
    if ru:
        s = wrap_ru(s)
    return s


def L(s):  # lesson text: English in sans, Russian runs in serif
    return inline(s, ru=True)


# ----------------------------------------------------------------------------- lesson markup
def render_table(rows):
    cells = []
    for r in rows:
        parts = [c.strip() for c in r.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in parts if c):
            continue
        cells.append(parts)
    if not cells:
        return ""
    head, body = cells[0], cells[1:]
    h = "".join(f"<th>{L(c)}</th>" for c in head)
    b = "".join("<tr>" + "".join(f"<td>{L(c)}</td>" for c in r) + "</tr>" for r in body)
    return f'<table class="mini"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>'


def render_eg(rows):
    out = []
    for r in rows:
        ru, _, en = r.partition("||")
        out.append(f'<tr><td class="eg-ru">{inline(ru.strip())}</td><td class="eg-en">{L(en.strip())}</td></tr>')
    return '<table class="eg">' + "".join(out) + "</table>"


def render_mist(rows):
    out = []
    for r in rows:
        bits = [x.strip() for x in r.split("||")] + ["", ""]
        wrong, right, note = bits[0], bits[1], bits[2]
        out.append(
            f'<tr><td class="m-wrong"><span class="m-x">✗</span> <span class="m-s">{inline(wrong)}</span></td>'
            f'<td class="m-ok"><span class="m-v">✓</span> {inline(right)}</td>'
            f'<td class="m-note">{L(note)}</td></tr>')
    return '<table class="mist">' + "".join(out) + "</table>"


def render_markup(lines):
    out, buf, cur, depth = [], [], [None], 0

    def flush():
        if buf:
            k = cur[0]
            if k == "p":
                out.append("<p>" + L(" ".join(buf)) + "</p>")
            elif k == "table":
                out.append(render_table(buf))
            elif k == "eg":
                out.append(render_eg(buf))
            elif k == "mist":
                out.append(render_mist(buf))
            elif k == "ul":
                out.append("<ul>" + "".join(f"<li>{L(x)}</li>" for x in buf) + "</ul>")
        buf.clear()
        cur[0] = None

    def add(kind, item):
        if cur[0] != kind:
            flush()
            cur[0] = kind
        buf.append(item)

    for raw in lines:
        s = raw.strip()
        if not s:
            flush()
            continue
        if s.startswith(":::"):
            flush()
            rest = s[3:].strip()
            if rest:
                kind, _, title = rest.partition(" ")
                t = f'<div class="box-title">{L(title)}</div>' if title else ""
                out.append(f'<div class="box box-{kind}">{t}')
                depth += 1
            else:
                out.append("</div>")
                depth -= 1
            continue
        if s.startswith("### "):
            flush()
            out.append(f"<h4>{L(s[4:])}</h4>")
        elif s.startswith("## "):
            flush()
            out.append(f"<h3>{L(s[3:])}</h3>")
        elif s.startswith("|"):
            add("table", s)
        elif s.startswith("!>"):
            add("mist", s[2:].strip())
        elif s.startswith(">"):
            add("eg", s[1:].strip())
        elif s.startswith("- "):
            add("ul", s[2:])
        elif s == "@pagebreak":
            flush()
            out.append('<div class="pb"></div>')
        else:
            add("p", s)
    flush()
    if depth != 0:
        die("unbalanced ::: boxes in lesson markup")
    return "\n".join(out)


# ----------------------------------------------------------------------------- exercises
def answer_lines(ex):
    a = ex.get("A", "")
    if ex["type"] in "FGHI" and len(a) > 62:
        return 2
    return 1


def render_ex(ex):
    t = ex["type"]
    q = ex.get("Q", "")
    if t == "F":
        qhtml = " ".join(f'<span class="chip">{inline(c.strip())}</span>' for c in q.split(" / "))
    else:
        qhtml = inline(q, gaps=True)
    hint = f'<span class="hint">{inline(ex["H"])}</span>' if "H" in ex else ""
    instr = f'<div class="ex-n">{inline(ex["N"])}</div>' if "N" in ex else ""
    lines = '<div class="ex-line"></div>' * answer_lines(ex)
    var = f'<div class="ex-v">Also correct: {inline(ex["V"])}</div>' if "V" in ex else ""
    return (f'<div class="ex t{t}"><div class="ex-num">{ex["n"]}</div>'
            f'<div class="ex-tag">{TYPES[t][0]}</div>{instr}'
            f'<div class="ex-q">{qhtml}{hint}</div>{lines}'
            f'<div class="ex-a">{inline(ex.get("A", ""))}</div>{var}'
            f'<div class="ex-w">{inline(ex.get("W", ""))}</div></div>')


def dots(n, total=5):
    return "".join('<span class="dot on"></span>' if i < n else '<span class="dot"></span>' for i in range(total))


def render_block(b, unit):
    if b["kind"] == "stage":
        title, lvl, desc = STAGES[b["id"]]
        if b["title"]:
            desc = b["title"]
        head = (f'<div class="stage"><div class="stage-k">Stage {b["id"]} <span class="dots">{dots(lvl)}</span></div>'
                f'<div class="stage-t">{title}</div><div class="stage-d">{L(desc)}</div></div>')
    else:
        head = (f'<div class="stage"><div class="stage-k">Section {b["id"]}</div>'
                f'<div class="stage-t">{L(b["title"])}</div></div>')
    items = b["items"]
    # keep the header together with the first exercise
    first = f'<div class="keep">{head}{render_ex(items[0])}</div>' if items else head
    return first + "".join(render_ex(ex) for ex in items[1:])


def tracker(unit, total):
    label = f'Module {unit["key"]}' if unit["kind"] == "module" else f'Review {unit["key"][1:]}'
    need = round(total * 0.9)
    return f'''<div class="tracker"><div class="tr-title">Progress tracker · {label}</div>
<table><thead><tr><th class="w1">Attempt</th><th class="w2">Date</th><th class="w2">Correct</th><th class="w3">%</th><th>Main recurring mistake</th></tr></thead>
<tbody><tr><td>First attempt</td><td></td><td class="frac">/ {total}</td><td></td><td></td></tr>
<tr><td>Retry</td><td></td><td class="frac">/ {total}</td><td></td><td></td></tr></tbody></table>
<div class="tr-note">Mastery target: {need} / {total} (90%) without looking at the answers. Below that, do the retry remix first and come back to this {label.split()[0].lower()} after a few days.</div></div>'''


def render_module(u):
    m = u["meta"]
    num = u["key"]
    total = sum(len(b["items"]) for b in u["blocks"])
    numtxt = f"{num:02d}" if isinstance(num, int) else "00"
    part = m.get("part", "")
    runhead = f'Module {num} · {m.get("title", "")}'
    learn = "".join(f"<li>{L(x)}</li>" for x in m["learn"])
    targets = "".join(f'<span class="tchip">{inline(x)}</span>' for x in m["target"])
    out = [f'<section class="module" id="m{numtxt}">',
           f'<div class="mod-open" style="string-set: runhead \'{esc(runhead)}\'; bookmark-level: 2; '
           f'bookmark-label: \'Module {num} — {esc(m.get("title", ""))}\'">',
           f'<div class="mod-num">{numtxt}</div>',
           f'<div class="mod-kicker">Part {part} · Module {num}</div>',
           f'<h2 class="mod-title">{L(m.get("title", ""))}</h2>',
           f'<div class="mod-ru">{inline(m.get("ru", ""))}</div>',
           f'<div class="mod-cols"><div class="mod-learn"><div class="mod-lab">In this module</div><ul>{learn}</ul></div>',
           f'<div class="mod-targets"><div class="mod-lab">Your target patterns</div>{targets}</div></div>',
           "</div>",
           f'<div class="lesson">{render_markup(u["lesson"])}</div>',
           '<div class="practice-head"><span>Practice</span> · {} exercises · answers in grey under each line — cover them with a card while you work</div>'.format(total)]
    for b in u["blocks"]:
        out.append(render_block(b, u))
    out.append('<div class="keep-end">')
    out.append(tracker(u, total))
    if m["remix"]:
        out.append('<div class="remix"><div class="remix-title">Retry remix — new examples from the same sentences</div><ul>'
                   + "".join(f"<li>{L(x)}</li>" for x in m["remix"]) + "</ul></div>")
    out.append("</div></section>")
    return "\n".join(out)


def render_review(u):
    m = u["meta"]
    k = u["key"]
    n = k[1:]
    total = sum(len(b["items"]) for b in u["blocks"])
    runhead = f"Cumulative review {n}"
    out = [f'<section class="review" id="r{n}">',
           f'<div class="rev-open" style="string-set: runhead \'{runhead}\'; bookmark-level: 2; '
           f'bookmark-label: \'Review {n} — {esc(m.get("covers", ""))}\'">',
           f'<div class="rev-k">Cumulative review {n}</div>',
           f'<h2 class="rev-title">{L(m.get("title", ""))}</h2>',
           f'<div class="rev-cov">Covers {L(m.get("covers", ""))} · {total} questions · no hints</div>',
           f'<p class="rev-intro">{L(m.get("intro", ""))}</p></div>']
    for b in u["blocks"]:
        out.append(render_block(b, u))
    out.append('<div class="keep-end">')
    out.append(tracker(u, total))
    out.append("</div></section>")
    return "\n".join(out)


def render_part(pid, units):
    title, desc = PARTS[pid]
    rows = []
    for key in units:
        u = UNITS.get(key)
        if not u:
            continue
        if u["kind"] == "module":
            anchor = f'#m{key:02d}'
            lab = f'<span class="pl-n">{key:02d}</span>{L(u["meta"].get("title", ""))}'
        else:
            anchor = f'#r{key[1:]}'
            lab = f'<span class="pl-n">R{key[1:]}</span>Cumulative review {key[1:]}'
        rows.append(f'<li><a href="{anchor}">{lab}</a></li>')
    return (f'<section class="part-open" id="part{pid}" style="string-set: parthead \'Part {pid} · {esc(title)}\'; '
            f'bookmark-level: 1; bookmark-label: \'Part {pid} — {esc(title)}\'">'
            f'<div class="po-k">Part {pid}</div><div class="po-num">{pid}</div>'
            f'<h1 class="po-title">{esc(title)}</h1><p class="po-desc">{esc(desc)}</p>'
            f'<ul class="po-list">{"".join(rows)}</ul></section>')


# ----------------------------------------------------------------------------- QA
LAT = re.compile(r"[A-Za-z]")
CYRW = re.compile(rf"[{CYR}]")
WORD = re.compile(r"[А-Яа-яЁё]+(?:-[А-Яа-яЁё]+)*")
CASE_NAMES = {"nominative": {"nomn"}, "genitive": {"gent", "gen2"}, "dative": {"datv"},
              "accusative": {"accs"}, "instrumental": {"ablt"}, "prepositional": {"loct", "loc2"}}
SKIP_POS = {"PREP", "CONJ", "PRCL", "INTJ", "ADVB", "PRED", "COMP", "NUMR"}


def norm(s):
    return s.lower().replace("ё", "е").replace("́", "")


def qa(units, strict=False, morph_checks=True):
    warns, errs = [], []
    seenq, seenw = {}, {}
    morph = None
    if morph_checks:
        try:
            import pymorphy3
            morph = pymorphy3.MorphAnalyzer()
        except Exception as e:  # pragma: no cover
            warns.append(f"pymorphy3 unavailable: {e}")
    for u in units:
        uid = u["key"]
        exs = [ex for b in u["blocks"] for ex in b["items"]]
        for ex in exs:
            ref = f'{u["file"]}:{ex["line"]} ({uid}.{ex["n"]} {ex["type"]})'
            for f in "QAW":
                if not ex.get(f):
                    errs.append(f"{ref}: missing {f}")
            q, a, w = ex.get("Q", ""), ex.get("A", ""), ex.get("W", "")
            if len(w) < 45:
                warns.append(f"{ref}: very short explanation")
            # mixed-script words (Latin letters inside Cyrillic words)
            for fld in (q, a, w, ex.get("N", ""), ex.get("V", "")):
                for tok in re.findall(r"[A-Za-zА-Яа-яЁё]+", fld):
                    if LAT.search(tok) and CYRW.search(tok):
                        errs.append(f"{ref}: mixed Latin/Cyrillic token '{tok}'")
            nq = norm(re.sub(r"\s+", " ", q))
            if nq in seenq:
                errs.append(f"{ref}: duplicate question (also {seenq[nq]})")
            seenq[nq] = ref
            if w in seenw:
                warns.append(f"{ref}: identical explanation reused (also {seenw[w]})")
            seenw[w] = ref
            t = ex["type"]
            if t in "ABCDEI" and "_" not in q:
                errs.append(f"{ref}: gap exercise without a gap")
            if t == "G" and norm(q) == norm(a):
                errs.append(f"{ref}: correction identical to question")
            if t in "FGH" and not re.search(r"[.!?…]$", a.split(" / ")[0].strip()):
                warns.append(f"{ref}: sentence answer without final punctuation")
            if t in "AC":
                check_gaps(ref, q, a, warns)
            if morph:
                morph_check(ref, ex, morph, warns)
    return errs, warns


def check_gaps(ref, q, a, warns):
    """Align answer words with the gapped tokens of the question.
    Ungapped question words may be repeated in the answer (they must then match) or omitted."""
    qtok = re.findall(r"[А-Яа-яЁё]*_{2,}|[А-Яа-яЁё]+(?:-[А-Яа-яЁё]+)*", q)
    gi = [i for i, t in enumerate(qtok) if "_" in t]
    if not gi:
        return
    span = qtok
    ans = [t for t in re.split(r"[\s;,]+", a.replace("(", " ").replace(")", " ")) if t and WORD.fullmatch(t)]
    j = 0
    for t in span:
        if "_" in t:
            if j >= len(ans):
                warns.append(f"{ref}: fewer answer words than gaps")
                return
            stem = t.split("_")[0]
            if stem and not norm(ans[j]).startswith(norm(stem)):
                warns.append(f"{ref}: answer '{ans[j]}' does not continue stem '{stem}'")
            j += 1
        elif j < len(ans) and norm(ans[j]) == norm(t):
            j += 1
    if j != len(ans):
        warns.append(f"{ref}: answer has extra words ({' '.join(ans[j:])})")


def morph_check(ref, ex, morph, warns):
    t, q, a, w = ex["type"], ex.get("Q", ""), ex.get("A", ""), ex.get("W", "")
    # 1) every Cyrillic word in the answer must be a known form
    for tok in WORD.findall(a):
        if not morph.word_is_known(norm(tok)) and len(tok) > 1:
            warns.append(f"{ref}: unknown word in answer: {tok}")
    if t not in "G":
        for tok in WORD.findall(re.sub(r"[А-Яа-яЁё]*_{2,}", " ", q)):
            if not morph.word_is_known(norm(tok)) and len(tok) > 1:
                warns.append(f"{ref}: unknown word in question: {tok}")
    # 2) agreement inside noun-phrase answers (A/B): one shared case+number
    if t in "AB":
        for part in a.split(";"):
            words = [x for x in WORD.findall(part)]
            if len(words) < 2:
                continue
            sets, verb = [], False
            for wd in words:
                ps = morph.parse(norm(wd))
                if any(p.tag.POS in ("VERB", "INFN", "PRTS", "ADJS") for p in ps if p.score > 0.2):
                    verb = True
                    break
                cand = [p for p in ps if p.tag.POS not in SKIP_POS and p.tag.case]
                if not cand:
                    continue
                sets.append({(p.tag.case.replace("gen2", "gent").replace("loc2", "loct"), p.tag.number or "x") for p in cand})
            if verb or len(sets) < 2:
                continue
            common = set.intersection(*[{c for c, _ in s} for s in sets])
            if not common:
                warns.append(f"{ref}: no shared case in answer phrase '{part.strip()}'")
                continue
            if ";" not in a:
                named = [n for n in CASE_NAMES if re.search(rf"\b{n}\b", w, re.I)]
                if len(named) == 1 and not (CASE_NAMES[named[0]] & common):
                    warns.append(f"{ref}: explanation says {named[0]} but '{part.strip()}' parses as {sorted(common)}")
    # 3) verb answers come from the verb(s) given in brackets
    if t in "DE":
        lemmas = re.findall(r"\(([^)]*)\)", q)
        cands = set()
        for grp in lemmas:
            for x in re.split(r"[/,]", grp):
                x = x.strip()
                if x:
                    cands.add(norm(x.split()[0]))
        if cands:
            got = set()
            for tok in WORD.findall(a):
                for p in morph.parse(norm(tok)):
                    got.add(norm(p.normal_form))
                    if p.tag.POS in ("PRTF", "PRTS", "GRND"):
                        got.add(norm(p.inflect({"INFN"}).word) if p.inflect({"INFN"}) else "")
            if not (cands & got):
                warns.append(f"{ref}: answer '{a}' not recognised as a form of {sorted(cands)}")


def stats(units):
    c = collections.Counter()
    for u in units:
        for b in u["blocks"]:
            for ex in b["items"]:
                c[ex["type"]] += 1
    return c


def plan_check(u):
    want = collections.Counter({x[0]: int(x[1:]) for x in PLAN.get(u["key"], "").split()})
    got = collections.Counter(ex["type"] for b in u["blocks"] for ex in b["items"])
    if want and want != got:
        diff = {k: got[k] - want[k] for k in "ABCDEFGHI" if got[k] != want[k]}
        return f"{u['key']}: type mix differs from plan {dict(diff)}"
    return None


def write_ledger(units, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["global_no", "unit", "local_no", "stage_or_block", "difficulty", "type", "type_name",
                     "cases_in_explanation", "question", "hint", "instruction", "answer", "also_correct",
                     "explanation", "source"])
        g = 0
        for u in units:
            for b in u["blocks"]:
                for ex in b["items"]:
                    g += 1
                    diff = STAGES[b["id"]][1] if b["kind"] == "stage" and b["id"] in STAGES else 3
                    cases = [n for n in CASE_NAMES if re.search(rf"\b{n}\b", ex.get("W", ""), re.I)]
                    unit = f'M{u["key"]:02d}' if u["kind"] == "module" and isinstance(u["key"], int) else str(u["key"])
                    wr.writerow([g, unit, ex["n"], b["id"], diff, ex["type"], TYPES[ex["type"]][1],
                                 "|".join(cases), ex.get("Q", ""), ex.get("H", ""), ex.get("N", ""),
                                 ex.get("A", ""), ex.get("V", ""), ex.get("W", ""), f'{ex["file"]}:{ex["line"]}'])
    return g


# ----------------------------------------------------------------------------- front / back matter
def markup_file(stem):
    p = CONTENT / f"{stem}.txt"
    if not p.exists():
        return None
    return p.read_text(encoding="utf-8").splitlines()


def render_front_section(stem, anchor, title, runhead, level=1):
    lines = markup_file(stem)
    if lines is None:
        return ""
    return (f'<section class="front" id="{anchor}"><h1 class="fm-title" style="string-set: runhead \'{runhead}\'; '
            f'parthead \'\'; bookmark-level: {level}; bookmark-label: \'{title}\'">{esc(title)}</h1>'
            f'<div class="lesson">{render_markup(lines)}</div></section>')


def render_cover(total_ex):
    pattern = ["кто? что?", "кого? чего?", "кому? чему?", "кого? что?", "кем? чем?", "о ком? о чём?"]
    pat = "".join(f'<div class="cv-q">{p}</div>' for p in pattern)
    return f'''<section class="cover"><div class="cv-pattern">{pat}</div>
<div class="cv-top">Personal edition · CEFR A1 → A2</div>
<div class="cv-main"><div class="cv-title">Russian<br/>Grammar<br/>Mastery</div>
<div class="cv-ru">Русская грамматика без угадывания</div>
<div class="cv-rule"></div>
<div class="cv-sub">A personalized workbook built from real mistakes.<br/>30 modules · 8 cumulative reviews · {total_ex:,} sentence exercises,<br/>each with its answer and a short explanation directly underneath.</div></div>
<div class="cv-foot">Cases · Endings · Prepositions · Conjugation · Aspect · Word order</div></section>'''


def render_toc():
    rows = ['<li class="toc-fm"><a href="#intro">Introduction</a></li>',
            '<li class="toc-fm"><a href="#howto">How to use this workbook</a></li>',
            '<li class="toc-fm"><a href="#tracker">Master progress tracker</a></li>',
            '<li class="toc-fm"><a href="#reference">A1–A2 grammar reference</a></li>']
    for key in ORDER:
        if isinstance(key, str) and key.startswith("P:"):
            pid = key[2:]
            rows.append(f'<li class="toc-part"><a href="#part{pid}"><span class="tp-k">Part {pid}</span>{esc(PARTS[pid][0])}</a></li>')
            continue
        u = UNITS.get(key)
        if not u:
            continue
        if u["kind"] == "module":
            rows.append(f'<li class="toc-mod"><a href="#m{key:02d}"><span class="tm-n">{key:02d}</span>{L(u["meta"].get("title", ""))}</a></li>')
        else:
            rows.append(f'<li class="toc-rev"><a href="#r{key[1:]}"><span class="tm-n">R{key[1:]}</span>Cumulative review {key[1:]} <span class="toc-cov">· {L(u["meta"].get("covers", ""))}</span></a></li>')
    rows.append('<li class="toc-fm"><a href="#summary">Compact grammar summary</a></li>')
    return (f'<section class="toc" id="toc"><h1 class="fm-title" style="string-set: runhead \'Contents\'; bookmark-level: 1; '
            f'bookmark-label: \'Contents\'">Contents</h1><ul>{"".join(rows)}</ul></section>')


def render_master_tracker():
    rows = []
    for key in ORDER:
        if isinstance(key, str) and key.startswith("P:"):
            rows.append(f'<tr class="mt-part"><td colspan="7">Part {key[2:]} · {esc(PARTS[key[2:]][0])}</td></tr>')
            continue
        u = UNITS.get(key)
        if not u:
            continue
        total = sum(len(b["items"]) for b in u["blocks"])
        if u["kind"] == "module":
            lab = f'<span class="tm-n">{key:02d}</span>{L(u["meta"].get("title", ""))}'
        else:
            lab = f'<span class="tm-n">R{key[1:]}</span>Cumulative review {key[1:]}'
        rows.append(f'<tr><td class="mt-l">{lab}</td><td class="mt-c">/ {total}</td><td></td><td class="mt-c">/ {total}</td><td></td><td class="mt-box"><span class="cb"></span></td><td></td></tr>')
    return (f'<section class="front mtracker" id="tracker"><h1 class="fm-title" style="string-set: runhead \'Master progress tracker\'; '
            f'bookmark-level: 1; bookmark-label: \'Master progress tracker\'">Master progress tracker</h1>'
            f'<p class="mt-intro">One line per unit. Record your first score and your retry score; tick the box when you reach 90% without looking at the answers.</p>'
            f'<table class="mt"><thead><tr><th>Unit</th><th>1st score</th><th>Date</th><th>Retry</th><th>Date</th><th>90%</th><th>Recurring mistake</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></section>')


# ----------------------------------------------------------------------------- assembly
UNITS = {}


def html_doc(body, title):
    css = CSS.read_text(encoding="utf-8")
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/>
<title>{esc(title)}</title><meta name="author" content="Russian Grammar Mastery Workbook"/>
<meta name="description" content="Personalized Russian A1–A2 grammar mastery workbook with answers and explanations under every exercise."/>
<meta name="keywords" content="Russian grammar, cases, aspect, A1, A2, workbook"/>
<style>{css}</style></head><body>{body}</body></html>'''


def build_book():
    total_ex = sum(len(b["items"]) for u in UNITS.values() for b in u["blocks"])
    body = [render_cover(total_ex), render_toc(),
            render_front_section("front_intro", "intro", "Introduction", "Introduction"),
            render_front_section("front_howto", "howto", "How to use this workbook", "How to use this workbook"),
            render_master_tracker(),
            render_front_section("reference", "reference", "A1–A2 grammar reference", "Grammar reference")]
    for i, key in enumerate(ORDER):
        if isinstance(key, str) and key.startswith("P:"):
            pid = key[2:]
            # units until next part marker
            nxt = []
            for k2 in ORDER[i + 1:]:
                if isinstance(k2, str) and k2.startswith("P:"):
                    break
                nxt.append(k2)
            body.append(render_part(pid, nxt))
            continue
        u = UNITS.get(key)
        if not u:
            continue
        body.append(render_module(u) if u["kind"] == "module" else render_review(u))
    body.append(render_front_section("summary", "summary", "Compact grammar summary", "Grammar summary"))
    return html_doc("\n".join(body), f"{BOOK_TITLE} — {BOOK_SUB}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="build a single content file stem, e.g. sample or m07")
    ap.add_argument("--qa", action="store_true", help="run checks only")
    ap.add_argument("--no-morph", action="store_true")
    ap.add_argument("--html", action="store_true", help="also write the HTML file")
    ap.add_argument("--name", default="russian-grammar-mastery-workbook")
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)

    if args.only:
        key = args.only
        if re.fullmatch(r"m\d\d", key):
            key = int(key[1:])
        elif re.fullmatch(r"r\d", key):
            key = "R" + key[1:]
        u = load_unit(key)
        if not u:
            die(f"no content for {args.only}")
        if isinstance(key, str) and not key.startswith("R"):
            u["kind"] = "module"
        UNITS[key] = u
        units = [u]
    else:
        for key in ORDER:
            if isinstance(key, str) and key.startswith("P:"):
                continue
            u = load_unit(key)
            if u:
                UNITS[key] = u
        units = list(UNITS.values())

    errs, warns = qa(units, morph_checks=not args.no_morph)
    for u in units:
        msg = plan_check(u)
        if msg:
            warns.append(msg)
        total = sum(len(b["items"]) for b in u["blocks"])
        want = 35 if u["kind"] == "review" else 40
        if not args.only and total != want:
            errs.append(f'{u["key"]}: {total} exercises (expected {want})')
    st = stats(units)
    total = sum(st.values())
    print(f"units: {len(units)}   exercises: {total}")
    for lab, codes, share in TYPE_GROUPS:
        n = sum(st[c] for c in codes)
        print(f"  {lab:<36} {n:>5}  {100 * n / max(total, 1):5.1f}%  (target {share * 100:.0f}%)")
    for w in warns:
        print("WARN ", w)
    for e in errs:
        print("ERROR", e)
    print(f"{len(errs)} errors, {len(warns)} warnings")
    if args.qa:
        return
    g = write_ledger(units, OUT / ("ledger-" + args.only + ".csv" if args.only else "exercise-ledger.csv"))
    if args.only:
        u = units[0]
        body = render_module(u) if u["kind"] == "module" else render_review(u)
        doc = html_doc(body, f"{BOOK_TITLE} — sample")
        name = args.only
    else:
        doc = build_book()
        name = args.name
    if args.html:
        (OUT / f"{name}.html").write_text(doc, encoding="utf-8")
    from weasyprint import HTML
    HTML(string=doc, base_url=str(ROOT)).write_pdf(OUT / f"{name}.pdf")
    print(f"wrote {OUT / (name + '.pdf')}  ({g} exercises in ledger)")


if __name__ == "__main__":
    main()
