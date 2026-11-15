"""Stage 1 of the import of «Deutsch in Farbe · A1»: the four source PDFs → raw.json.

The old book only exists as PDF. Its pages were generated, so every element has a fixed
typographic signature (font, size, colour, position). This module reads those signatures and
writes down *what is there*, without interpreting it yet:

    chapters[n]   = {number, title, subtitle, cando, topics, goal, picture, sections[...]}
    revisions[n]  = {number, title, blocks[...]}
    answers       = {"K1": [entries], "W1": [entries], ...}
    footers       = {page: [[word, gloss], ...]}

Stage 2 (convert.py) turns raw.json into content files for the engine.

    python tools/a1_import/parse.py            # → tools/a1_import/raw.json
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pdfsrc  # noqa: E402

FIRST, LAST = 4, 303
KEY_FIRST, KEY_LAST = 304, 320
OUT = Path(__file__).parent / "raw.json"

X, Y, SIZE, FONT, COL, TEXT = range(6)


def raw_spans(n: int) -> list[tuple]:
    """Like pdfsrc.spans, but the text keeps its leading and trailing blanks (they tell where a gap sits)."""
    out = []
    for b in pdfsrc.page(n).get_text("dict")["blocks"]:
        for ln in b.get("lines", []):
            for s in ln["spans"]:
                if s["text"].strip():
                    font = s["font"].split("+")[-1].replace("Poppins-", "P-").replace("Fraunces-", "F-").replace("Caveat-", "C-")
                    out.append((round(s["bbox"][0], 1), round(s["origin"][1], 1), round(s["size"], 1), font, "%06x" % s["color"],
                                s["text"], round(s["bbox"][2], 1)))
    return out


def furniture(s) -> bool:
    return (s[Y] < 40 or (s[SIZE] == 20.0 and s[X] > 560) or (s[FONT].startswith("F-") and s[Y] > 795 and s[X] > 500))


def page_lines(n: int) -> list[list[tuple]]:
    sp = sorted((s for s in raw_spans(n) if not furniture(s)), key=lambda s: (round(s[Y]), s[X]))
    lines: list[list[tuple]] = []
    for s in sp:
        if lines and abs(lines[-1][0][Y] - s[Y]) < 2.6:
            lines[-1].append(s)
        else:
            lines.append([s])
    for ln in lines:
        ln.sort(key=lambda s: s[X])
    return lines


def norm(t: str) -> str:
    return re.sub(r"\s+", " ", t).strip()


def images(n: int) -> tuple[list[tuple], list[tuple]]:
    """(gap images, pictures) as bboxes."""
    gaps, pics = [], []
    for im in pdfsrc.page(n).get_image_info():
        x0, y0, x1, y1 = im["bbox"]
        if 30 < x1 - x0 < 50 and y1 - y0 < 12:
            gaps.append((x0, y0, x1, y1))
        elif x1 - x0 > 120:
            pics.append((round(x0), round(y0), round(x1), round(y1)))
    return gaps, pics


def dashed(n: int) -> list[float]:
    """y of every dashed write-in line."""
    out = []
    for d in pdfsrc.page(n).get_drawings():
        r = d["rect"]
        if d.get("dashes") and d["dashes"] != "[] 0" and r.width > 200 and r.height < 1:
            out.append(round(r.y0, 1))
    return sorted(out)


# ── footer: "Wörter der Seite" ───────────────────────────────────────────────
def footer_words(spans_: list[tuple]) -> list[list[str]]:
    cols: dict[int, list[tuple]] = {0: [], 1: [], 2: []}
    for s in spans_:
        cols[0 if s[X] < 200 else 1 if s[X] < 344 else 2].append(s)
    entries = []
    for c, ss in cols.items():
        ss.sort(key=lambda s: (round(s[Y]), s[X]))
        cur = None
        for s in ss:
            if s[FONT] == "P-Bold":
                cur = [s[Y], c, norm(s[TEXT]), ""]
                entries.append(cur)
            elif cur is not None:
                cur[3] = norm(cur[3] + " " + s[TEXT])
    entries.sort(key=lambda e: (round(e[0] / 14), e[1]))
    return [[e[2], e[3]] for e in entries]


# ── vocabulary cards ─────────────────────────────────────────────────────────
def card_col(x: float) -> int:
    return 0 if x < 216 else 1 if x < 388 else 2


def cards_on(spans_: list[tuple]) -> list[dict]:
    words = [s for s in spans_ if s[SIZE] == 11.0 and s[FONT] == "P-Bold"]
    out = []
    for w in words:
        c = card_col(w[X])
        same = [s for s in spans_ if card_col(s[X]) == c]
        chip = next((norm(s[TEXT]) for s in same if s[SIZE] == 7.5 and s[FONT] == "P-Bold" and -9 < s[Y] - w[Y] < -1), "")
        plural = next((norm(s[TEXT]) for s in same if s[SIZE] == 8.5 and s[FONT] == "P-Italic" and 6 < s[Y] - w[Y] < 20), "")
        nxt = min((s[Y] for s in words if card_col(s[X]) == c and s[Y] > w[Y] + 5), default=1e9)
        tr = [s for s in same if s[SIZE] == 8.5 and s[FONT] == "P-Regular" and s[COL] != "1b1e4b" and w[Y] + 20 < s[Y] < min(nxt - 20, w[Y] + 80)]
        tr.sort(key=lambda s: (round(s[Y]), s[X]))
        out.append({"y": w[Y], "col": c, "word": norm(w[TEXT]), "chip": chip, "plural": plural, "tr": norm(" ".join(s[TEXT] for s in tr))})
    out.sort(key=lambda d: (round(d["y"]), d["col"]))
    return out


# ── the elements of one page ─────────────────────────────────────────────────
def page_elements(n: int) -> dict:
    lines = page_lines(n)
    gaps, pics = images(n)
    dash = dashed(n)
    res = {"page": n, "els": [], "footer": [], "opener": None}
    # footer
    fy = next((ln[0][Y] for ln in lines if "WÖRTER DER SEITE" in ln[0][TEXT]), None)
    if fy is not None:
        res["footer"] = footer_words([s for ln in lines for s in ln if s[Y] > fy + 3])
        lines = [ln for ln in lines if ln[0][Y] < fy - 3]
    flat = [s for ln in lines for s in ln]
    # chapter opener
    if any(s[SIZE] >= 100 for s in flat):
        num = next(s[TEXT] for s in flat if s[SIZE] >= 100)
        title = norm(" ".join(s[TEXT] for s in flat if s[SIZE] >= 40 and s[FONT] == "F-Black"))
        sub = norm(" ".join(s[TEXT] for s in flat if s[SIZE] == 14.0 and s[FONT] == "P-Regular"))
        y_im = next((s[Y] for s in flat if norm(s[TEXT]) == "IM KAPITEL"), 1e9)
        y_by = next((s[Y] for s in flat if s[TEXT].startswith("BY THE END")), 0)
        cando = [norm(s[TEXT]) for s in flat if s[SIZE] == 10.0 and s[FONT] == "P-Regular" and y_by < s[Y] < y_im and s[X] < 60]
        y_th = next((s[Y] for s in flat if norm(s[TEXT]) == "THEMEN"), 1e9)
        topics = [norm(s[TEXT]) for s in sorted(flat, key=lambda s: (round(s[Y] / 6), s[X]))
                  if s[SIZE] == 8.5 and s[FONT] == "P-Regular" and s[X] > 320 and s[Y] > y_th]
        goal = norm(" ".join(s[TEXT] for s in flat if s[SIZE] == 11.0 and s[FONT] == "P-Medium"))
        res["opener"] = {"number": int(num), "title": title, "subtitle": sub, "cando": cando, "topics": topics, "goal": goal,
                         "picture": pics[0] if pics else None}
        return res
    els = res["els"]
    card_spans = [s for s in flat if (s[SIZE] == 11.0 and s[FONT] == "P-Bold") or (s[SIZE] == 7.5 and s[FONT] == "P-Bold" and not s[TEXT].strip().isdigit())
                  or (s[SIZE] == 8.5 and s[FONT] == "P-Italic") or (s[SIZE] == 8.5 and s[FONT] == "P-Regular" and s[COL] != "1b1e4b")]
    cards = cards_on(card_spans) if any(s[SIZE] == 11.0 and s[FONT] == "P-Bold" for s in card_spans) else []
    card_ids = {id(s) for s in card_spans} if cards else set()
    for c in cards:
        els.append({"t": "card", "y": c["y"], **{k: c[k] for k in ("word", "chip", "plural", "tr", "col")}})
    for p in pics:
        els.append({"t": "picture", "y": p[1], "bbox": p})
    for ln in lines:
        ln = [s for s in ln if id(s) not in card_ids]
        if not ln:
            continue
        s0 = ln[0]
        y, size, font, col = s0[Y], s0[SIZE], s0[FONT], s0[COL]
        text = norm(" ".join(s[TEXT] for s in ln))
        if size in (15.0, 13.0) and font == "F-Bold" and any(x[SIZE] == 22.0 for x in ln):
            els.append({"t": "section", "y": y, "no": norm(s0[TEXT]), "title": norm(" ".join(s[TEXT] for s in ln if s[SIZE] == 22.0)),
                        "sub": norm(" ".join(s[TEXT] for s in ln if s[SIZE] == 14.0))})
        elif size == 22.0 and font == "F-Black":
            els.append({"t": "bigtitle", "y": y, "text": text})
        elif size == 12.0 and font == "F-Bold" and len(ln) > 1:
            els.append({"t": "block", "y": y, "no": int(norm(s0[TEXT])), "title": norm(" ".join(s[TEXT] for s in ln[1:]))})
        elif size == 11.0 and font == "F-Bold" and col == "ffffff":
            instr = norm(" ".join(s[TEXT] for s in ln if s[SIZE] == 10.0 and s[FONT] == "P-Bold"))
            tag = norm(" ".join(s[TEXT] for s in ln if s[SIZE] in (7.0, 7.2) and s[X] > 440))
            pts = next((norm(s[TEXT]) for s in ln if s[SIZE] == 9.0 and s[FONT] == "P-Bold"), "")
            els.append({"t": "task", "y": y, "letter": norm(s0[TEXT]), "instr": instr, "tag": tag,
                        "points": int(pts.replace("/", "").strip()) if pts else None})
        elif size == 10.0 and font == "P-Bold" and 70 < s0[X] < 76:
            els.append({"t": "task+", "y": y, "text": text})
        elif size == 7.0 and font == "P-Bold" and s0[X] < 56 and norm(s0[TEXT]).isdigit() and len(ln) > 1:
            el = {"t": "item", "y": y, "no": int(norm(s0[TEXT]))}
            rest = ln[1:]
            letters = [s for s in rest if s[SIZE] == 6.5]
            if letters and any(norm(s[TEXT]) in ("der", "die", "das") for s in rest):
                el["kind"] = "article"
                el["text"] = norm(" ".join(s[TEXT] for s in rest if s[X] < 330))
            elif letters:
                el["kind"] = "match"
                el["text"] = norm(" ".join(s[TEXT] for s in rest if s[X] < letters[0][X] and s[SIZE] == 10.0))
                el["letter"] = norm(letters[0][TEXT])
                el["right"] = norm(" ".join(s[TEXT] for s in rest if s[X] > letters[0][X]))
            else:
                el["kind"] = "plain"
                toks = [(s[X], s[TEXT]) for s in rest]
                for g in gaps:
                    if abs((g[1] + g[3]) / 2 - (y - 2.5)) < 7:
                        toks.append((g[0], "\x00"))
                toks.sort(key=lambda t: t[0])
                raw = "".join(t[1] for t in toks)
                el["text"] = re.sub(r"\s+", " ", raw).strip().replace("\x00", "[[]]")
                el["text"] = re.sub(r"\s+([.,?!])", r"\1", el["text"])
            els.append(el)
        elif size == 7.5 and font == "P-Bold" and s0[X] < 56 and norm(s0[TEXT]).isdigit():
            els.append({"t": "phrase", "y": y, "no": int(norm(s0[TEXT])), "text": norm(" ".join(s[TEXT] for s in ln[1:]))})
        elif size == 8.5 and font == "P-Medium" and text.startswith("true"):
            els.append({"t": "tfhead", "y": y})
        elif size == 8.5 and font == "P-Medium" and col == "ffffff":
            els.append({"t": "score", "y": y, "text": text})
        elif size == 8.5 and font == "P-Medium":
            els.append({"t": "caption", "y": y, "text": text})
        elif size == 9.0 and font == "P-Medium":
            els.append({"t": "bank", "y": y, "words": [norm(s[TEXT]) for s in ln]})
        elif size == 10.0 and font == "P-Bold" and s0[X] < 60 and norm(s0[TEXT]).endswith(":"):
            els.append({"t": "turn", "y": y, "speaker": norm(s0[TEXT])[:-1], "text": norm(" ".join(s[TEXT] for s in ln[1:]))})
        elif size == 10.0 and font == "P-Regular":
            toks = [(s[X], s[TEXT]) for s in ln]
            for g in gaps:
                if abs((g[1] + g[3]) / 2 - (y - 2.5)) < 7:
                    toks.append((g[0], "\x00"))
            toks.sort(key=lambda t: t[0])
            raw = re.sub(r"\s+", " ", "".join(t[1] for t in toks)).strip().replace("\x00", "[[]]")
            els.append({"t": "text", "y": y, "x": round(s0[X]), "text": raw})
        elif size == 10.0 and font == "P-Italic":
            els.append({"t": "exline", "y": y, "text": text})
        elif size == 13.0 and font.startswith("C-"):
            els.append({"t": "hand", "y": y, "text": text})
        elif size == 7.0 and font == "P-Bold" and len(ln) >= 2 and s0[X] > 100:
            els.append({"t": "thead", "y": y, "cells": [norm(s[TEXT]) for s in ln]})
        elif size == 7.0 and font == "P-Bold":
            els.append({"t": "label", "y": y, "x": round(s0[X]), "text": text})
        elif size == 8.5 and font == "P-Bold" and s0[X] < 60 and len(ln) > 1 and all(s[SIZE] == 8.5 for s in ln):
            els.append({"t": "trow", "y": y, "cells": [norm(s[TEXT]) for s in ln], "xs": [round(s[X]) for s in ln]})
        elif size == 8.5 and font == "P-Regular" and col == "1b1e4b":
            els.append({"t": "vlist", "y": y, "cells": [norm(s[TEXT]) for s in ln]})
        elif size == 8.5 and font == "P-Light":
            els.append({"t": "circlehead", "y": y})
        elif size == 14.0 and font == "P-Light":
            els.append({"t": "sub", "y": y, "text": text})
        else:
            els.append({"t": "?", "y": y, "sig": f"{size}/{font}/{col}/{round(s0[X])}", "text": text})
    for d in dash:
        els.append({"t": "line", "y": d})
    els.sort(key=lambda e: e["y"])
    return res


# ── answer key ───────────────────────────────────────────────────────────────
def answer_key() -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    scope = None
    cur = None
    for n in range(KEY_FIRST, KEY_LAST + 1):
        sp = [s for s in raw_spans(n) if not furniture(s)]
        for lo, hi in ((0, 300), (300, 600)):
            col = sorted((s for s in sp if lo <= s[X] < hi), key=lambda s: (round(s[Y]), s[X]))
            lines: list[list[tuple]] = []
            for s in col:
                if lines and abs(lines[-1][0][Y] - s[Y]) < 2.6:
                    lines[-1].append(s)
                else:
                    lines.append([s])
            for ln in lines:
                ln.sort(key=lambda s: s[X])
                s0 = ln[0]
                text = norm(" ".join(s[TEXT] for s in ln))
                if s0[SIZE] in (22.0, 14.0) or (s0[SIZE] == 10.0) or text == "TIP":
                    continue                                   # page title and the tip box on the first key page
                head7 = [s for s in ln if s[SIZE] == 7.0 and s[FONT] == "P-Bold"]
                m = re.search(r"(KAPITEL (\d+) ·|WIEDERHOLUNG · KAPITEL (\d+))", text)
                if head7 and m and not any(s[SIZE] == 8.5 for s in ln):
                    scope = f"W{m.group(3)}" if m.group(3) else f"K{m.group(2)}"
                    out.setdefault(scope, [])
                    cur = None
                    continue
                if s0[SIZE] == 8.5 and s0[FONT] == "P-Bold" and head7 and re.match(r"S\. \d+", norm(head7[-1][TEXT])):
                    title = norm(" ".join(s[TEXT] for s in ln if s[SIZE] == 8.5))
                    t, _, letter = title.rpartition(" · ")
                    cur = {"title": t, "letter": letter, "page": int(norm(head7[-1][TEXT])[3:]), "runs": []}
                    out[scope].append(cur)
                    continue
                if cur is not None:
                    for s in ln:
                        cur["runs"].append(["b" if s[FONT] == "P-Bold" else "r", s[TEXT]])
    for entries in out.values():
        for e in entries:
            e["text"], e["items"] = fold_answer(e.pop("runs"))
    return out


def fold_answer(runs: list[list[str]]) -> tuple[str, dict[str, str]]:
    """Bold numbers start an item: [b '1'] [r ' der '] [b '2'] … → {'1': 'der', '2': …}; text before the first number stays."""
    pre, items, cur = [], {}, None
    for kind, t in runs:
        if kind == "b" and norm(t).isdigit():
            cur = norm(t)
            items[cur] = ""
        elif cur is None:
            pre.append(t)
        else:
            items[cur] += " " + t
    return norm(" ".join(pre)), {k: norm(v) for k, v in items.items()}


def main() -> None:
    pages = [page_elements(n) for n in range(FIRST, LAST + 1)]
    data = {"pages": pages, "answers": answer_key()}
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1))
    kinds: dict[str, int] = {}
    for p in pages:
        for e in p["els"]:
            kinds[e["t"]] = kinds.get(e["t"], 0) + 1
    print("pages:", len(pages), "· openers:", sum(1 for p in pages if p["opener"]))
    print("elements:", dict(sorted(kinds.items(), key=lambda kv: -kv[1])))
    unknown = [(p["page"], e["sig"], e["text"][:60]) for p in pages for e in p["els"] if e["t"] == "?"]
    print("unknown:", len(unknown))
    for u in unknown[:40]:
        print("  ", u)
    print("answer scopes:", {k: len(v) for k, v in data["answers"].items()})


if __name__ == "__main__":
    main()
