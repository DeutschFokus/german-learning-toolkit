"""Stage 2 of the import: raw.json (elements per page) → book.json (chapters → sections → blocks → tasks).

Still no interpretation of the content – only the nesting that the old layout expressed through
headings: chapter opener · section head · block head · task head · everything below it.

    python tools/a1_import/assemble.py          # → tools/a1_import/book.json
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
SECTION_IDS = {"Wortschatz": "wortschatz", "Hauptteil": "hauptteil", "Vertiefung": "vertiefung", "Übersicht": "uebersicht",
               "Abschlusstest": "abschlusstest"}
INPUT = {"turn", "picture", "caption"}          # what a task reads or looks at
WORK = {"item", "line", "hand", "bank", "tfhead"}   # what a task makes the learner do


def assemble(raw: dict) -> dict:
    chapters: dict[int, dict] = {}
    revisions: dict[int, dict] = {}
    footers = {p["page"]: p["footer"] for p in raw["pages"] if p["footer"]}
    part = section = block = None

    def new_block(no, title, page, y):
        nonlocal block
        block = {"no": no, "title": title, "page": page, "seq": []}
        (section["blocks"] if section is not None else part["blocks"]).append(block)

    for p in raw["pages"]:
        n = p["page"]
        if p["opener"]:
            o = p["opener"]
            part = {"kind": "chapter", **o, "page": n, "sections": []}
            chapters[o["number"]] = part
            section = block = None
            continue
        for el in p["els"]:
            t = el["t"]
            el = {**el, "page": n}
            if t == "?" and re.match(r"\d+ Wiederholung Kapitel", el["text"]):
                m = re.match(r"(\d+) Wiederholung (Kapitel \d+: .*)", el["text"])
                t, el = "section", {**el, "t": "section", "no": m.group(1), "title": "Wiederholung", "sub": m.group(2)}
            if t == "section":
                if el["title"] == "Wiederholung":
                    k = int(el["no"])
                    part = {"kind": "revision", "number": k, "title": el["sub"].split(": ", 1)[1], "page": n, "blocks": []}
                    revisions[k] = part
                    section = block = None
                else:
                    section = {"id": SECTION_IDS[el["title"]], "title": el["title"], "sub": el["sub"], "page": n, "blocks": []}
                    part["sections"].append(section)
                    block = None
                    if section["id"] in ("wortschatz", "abschlusstest"):
                        new_block(None, "", n, el["y"])       # cards before block 1 · the test has no block heading
                continue
            if t == "block":
                new_block(el["no"], el["title"], n, el["y"])
                continue
            if block is None:
                raise SystemExit(f"page {n}: element {el} outside of a block")
            seq = block["seq"]
            if t == "task":
                seq.append({"kind": "task", "letter": el["letter"].lower(), "instr": el["instr"], "tag": el["tag"], "points": el["points"],
                            "page": n, "els": []})
                continue
            last = seq[-1] if seq else None
            if t == "task+" and last and last["kind"] == "task" and not last["els"]:
                last["instr"] += " " + el["text"]
                continue
            is_input = t in INPUT or (t == "text" and el.get("x", 0) < 66)
            if last is None or (last["kind"] == "task" and is_input and any(e["t"] in WORK for e in last["els"])):
                last = {"kind": "input", "page": n, "els": []}
                seq.append(last)
            if t == "tfhead" and any(e["t"] == "tfhead" for e in last["els"]):
                continue
            last["els"].append(el)
    return {"chapters": chapters, "revisions": revisions, "answers": raw["answers"], "footers": footers}


def summary(book: dict, chapter: int) -> None:
    ch = book["chapters"][chapter]
    print(f"Kapitel {ch['number']} · {ch['title']} · {ch['subtitle']} · p. {ch['page']}")
    print("  can-do:", ch["cando"], "\n  topics:", ch["topics"], "\n  goal:", ch["goal"])
    for s in ch["sections"]:
        print(f"  [{s['id']}] {s['sub']} (p. {s['page']})")
        for b in s["blocks"]:
            print(f"    {b['no']} {b['title']!r} p.{b['page']}")
            for e in b["seq"]:
                kinds: dict[str, int] = {}
                for x in e["els"]:
                    kinds[x["t"]] = kinds.get(x["t"], 0) + 1
                head = f"task {e['letter']} [{e['tag']}{' /' + str(e['points']) if e['points'] else ''}] {e['instr']}" if e["kind"] == "task" else "input"
                print(f"       · {head}  {kinds}")


def main() -> None:
    raw = json.loads((HERE / "raw.json").read_text())
    book = assemble(raw)
    (HERE / "book.json").write_text(json.dumps(book, ensure_ascii=False, indent=1))
    n_tasks = sum(1 for ch in book["chapters"].values() for s in ch["sections"] for b in s["blocks"] for e in b["seq"] if e["kind"] == "task")
    n_rev = sum(1 for rv in book["revisions"].values() for b in rv["blocks"] for e in b["seq"] if e["kind"] == "task")
    print(f"chapters: {len(book['chapters'])} · revision units: {len(book['revisions'])} · tasks: {n_tasks} + {n_rev}")
    for a in sys.argv[1:]:
        summary(book, int(a))


if __name__ == "__main__":
    main()
