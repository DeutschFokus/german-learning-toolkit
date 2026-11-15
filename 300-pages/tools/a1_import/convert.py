"""Stage 3 of the import: book.json + tm.yaml + lexicon.yaml → content/a1/*.yaml and pictures.

This is where the old book is poured into the new template – and improved on the way:

  · instructions become bilingual (German first, then the language of the edition)
  · block titles are German, with a translation underneath
  · the answer key is merged into the tasks, so the engine can rebuild it with live links
  · reading texts, dialogues and pictures move into the task that works with them
    (a task is never split from its text any more)
  · vocabulary cards, article exercises and word matching refer to one vocabulary list,
    so the Turkish edition gets Turkish glosses everywhere
  · known glitches of the old book are repaired (see the FIXES section below)

    python tools/a1_import/convert.py --chapters 1            # chapter 1 and its revision unit
    python tools/a1_import/convert.py --chapters 1-12

Everything that could not be converted cleanly is listed in tools/a1_import/report.md.
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
from engine.markup import plural_form  # noqa: E402

LEVEL = "a1"
OUT = ROOT / "content" / LEVEL
IMG = ROOT / "assets" / "images" / LEVEL
TAG_SKILLS = {"LESEN": ["lesen"], "SCHREIBEN": ["schreiben"], "AB WORTSCHATZ": ["wortschatz"], "STRUKTUR": ["grammatik"],
              "PARTNERARBEIT": ["partner", "sprechen"], "": ["grammatik"]}
EN_WORDS = {"the", "is", "are", "with", "and", "you", "of", "to", "in", "for", "this", "that", "use", "when", "not", "it", "a", "an", "or"}


class Report:
    def __init__(self):
        self.items: dict[str, list[str]] = {}

    def add(self, kind: str, text: str) -> None:
        lst = self.items.setdefault(kind, [])
        if text not in lst:
            lst.append(text)

    def write(self, path: Path) -> None:
        out = ["# Import report · Deutsch in Farbe A1 → 300 Pages of A1 German", ""]
        if not self.items:
            out.append("Nothing to report: every string was found in tm.yaml and lexicon.yaml.")
        for kind, lst in self.items.items():
            out += [f"## {kind} ({len(lst)})", ""] + [f"- {x}" for x in lst] + [""]
        path.write_text("\n".join(out))


REP = Report()


def slug(s: str) -> str:
    s = s.lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss"), ("é", "e")):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "x"


def de_umlaut(s: str) -> str:
    return s.replace("äu", "au").replace("Äu", "Au").translate(str.maketrans("äöüÄÖÜ", "aouAOU"))


def notation(sg: str, pl: str) -> tuple[str, str | None]:
    """(notation, explicit plural form or None): Name/Namen → -n · Stadt/Städte → ¨-e · Lehrer/Lehrer → -"""
    if pl == sg:
        return "-", None
    if pl.startswith(sg):
        return "-" + pl[len(sg):], None
    flat = de_umlaut(pl)
    if flat.startswith(sg):
        n = "¨-" + flat[len(sg):]
        if plural_form(sg, n) == pl:
            return n, None
    return pl, pl


# ── vocabulary ───────────────────────────────────────────────────────────────
class Vocabulary:
    def __init__(self, lex: dict):
        self.lex = lex
        self.entries: dict[str, dict] = {}      # id → entry
        self.by_printed: dict[str, str] = {}    # "der Name" / "Name" / "heißen" → id
        self.used: list[str] = []

    def _register(self, printed: str, e: dict) -> str:
        lx = self.lex.get(printed) or {}
        for k in ("de", "pos", "en", "tr", "plural"):
            if k in lx:
                e[k] = lx[k]
        if "article" in lx:
            e["article"] = lx["article"]
        key = (e.get("article") or "", e["de"])
        for vid, old in self.entries.items():
            if (old.get("article") or "", old["de"]) == key:
                for k, v in e.items():                 # a later source fills what an earlier one did not know
                    if v and not old.get(k):
                        old[k] = v
                self.by_printed[printed] = vid
                return vid
        vid = base = slug(e["de"])
        i = 2
        while vid in self.entries:
            vid = f"{base}-{i}"
            i += 1
        e["id"] = vid
        self.entries[vid] = e
        for p in {printed, e["de"], f'{e.get("article")} {e["de"]}' if e.get("article") else e["de"]}:
            self.by_printed.setdefault(p, vid)
        return vid

    def add_card(self, c: dict) -> str:
        word, chip = c["word"], c["chip"]
        if word in self.by_printed:
            return self.by_printed[word]
        e: dict = {"de": word, "en": c["tr"]}
        m = re.match(r"(der|die|das) (.+)$", word)
        if m and chip in ("m.", "f.", "n.", "Pl.", ""):
            e.update({"article": m.group(1), "de": m.group(2)})
            if c["plural"]:
                pl = re.sub(r"^Pl\.\s*(die\s+)?", "", c["plural"]).strip()
                e["plural"], pf = notation(e["de"], pl)
                if pf:
                    e["plural_form"] = pf
        elif chip == "Verb":
            e["pos"] = "verb"
        return self._register(word, e)

    def add_footer(self, word: str, gloss: str) -> str | None:
        if word in self.by_printed:
            return self.by_printed[word]
        m = re.search(r"\(pl\. of (\w+)\)", gloss)
        if m:                                           # "die Freunde – friends (pl. of Freund)" is the entry "der Freund"
            for p, vid in self.by_printed.items():
                if p.split(" ")[-1] == m.group(1):
                    self.by_printed[word] = vid
                    return vid
        e: dict = {"de": word, "en": gloss}
        pm = re.search(r"\s*\(plural (?:die )?(\w+)\)", gloss)
        a = re.match(r"(der|die|das) (.+)$", word)
        if a:
            e.update({"article": a.group(1), "de": a.group(2)})
            if pm:
                e["plural"], pf = notation(e["de"], pm.group(1))
                if pf:
                    e["plural_form"] = pf
        if pm:
            e["en"] = (gloss[:pm.start()] + gloss[pm.end():]).strip()
        if not a and gloss.startswith("to ") and " " not in word:
            e["pos"] = "verb"
        return self._register(word, e)

    def find(self, printed: str) -> str | None:
        printed = printed.strip()
        if printed in self.by_printed:
            return self.by_printed[printed]
        bare = re.sub(r"^(der|die|das) ", "", printed)
        return self.by_printed.get(bare)

    def use(self, vid: str) -> str:
        if vid not in self.used:
            self.used.append(vid)
        return vid

    def dump(self) -> list[dict]:
        out = []
        for vid in self.used:
            e = dict(self.entries[vid])
            if e.get("article") and not e.get("plural"):
                REP.add("Nouns without plural (assumed singular only – add `plural` in lexicon.yaml)", f'{e["article"]} {e["de"]}')
                e["plural"] = "Sg."
            if not e.get("article") and e["de"][:1].isupper() and " " not in e["de"] and not e.get("pos"):
                e["pos"] = "name" if e.get("en", "")[:1].isupper() else "other"
            if not e.get("tr"):
                REP.add("Words without Turkish translation (lexicon.yaml)", f'"{(e.get("article") + " ") if e.get("article") else ""}{e["de"]}": {e.get("en")}')
                e["tr"] = "⟦TR⟧ " + (e.get("en") or "")
            order = ["id", "de", "article", "plural", "plural_form", "pos", "en", "tr"]
            out.append({k: e[k] for k in order if e.get(k)})
        return out

    def forms_rx(self, vid: str) -> re.Pattern:
        e = self.entries[vid]
        forms = {e["de"]}
        if e.get("article") and e.get("plural"):
            pf = e.get("plural_form") or plural_form(e["de"], e["plural"])
            if pf:
                forms.add(pf)
        if e.get("pos") == "verb" or (not e.get("article") and e["de"].endswith("en") and e["de"].islower() and " " not in e["de"]):
            forms.add(re.sub(r"e?n$", "", e["de"]))
        m = re.fullmatch(r"(?:ich|du|er|sie|es|wir|ihr|Sie|er/sie/es|sie/Sie) (\w+)", e["de"])
        if m:
            forms.add(m.group(1))
        pat = "|".join(re.escape(f) for f in sorted(forms, key=len, reverse=True))
        return re.compile(r"(?<![A-Za-zÄÖÜäöüß])(?:" + pat + r")", 0 if e.get("article") else re.I)


# ── translation memory ───────────────────────────────────────────────────────
class TM:
    def __init__(self, data: dict):
        self.d = data

    def _pattern(self, kind: str, text: str) -> dict | None:
        for p in self.d.get(kind, []):
            m = re.fullmatch(p["match"], text)
            if m:
                out = {}
                for k, v in p.items():
                    if isinstance(v, str) and k != "match":
                        for i, g in enumerate(m.groups(), 1):
                            v = v.replace("{" + str(i) + "}", g)
                    out[k] = v
                return out
        return None

    def rubric(self, instr: str, tag: str, prefix: str | None) -> tuple[dict, list[str]]:
        e = self.d["rubrics"].get(instr) or self._pattern("rubric_patterns", instr)
        if e is None:
            REP.add("Instructions without German / Turkish wording (tm.yaml → rubrics)", instr)
            e = {"de": "⟦DE⟧ " + instr, "tr": "⟦TR⟧ " + instr}
        bi = {"de": e["de"], "en": e.get("en", instr), "tr": e["tr"]}
        if prefix and not e.get("noprefix"):
            p = self.d["prefix"][prefix]
            bi = {k: f"{p[k]} {bi[k]}" for k in bi}
        return bi, list(e.get("skills") or TAG_SKILLS.get(tag, ["grammatik"]))

    def title(self, title: str) -> tuple[str, dict | None]:
        if not title:
            return "", None
        e = self.d["titles"].get(title) or self._pattern("title_patterns", title)
        if e is None:
            REP.add("Block titles without translation (tm.yaml → titles)", title)
            return title, {"en": "⟦EN⟧ " + title, "tr": "⟦TR⟧ " + title}
        return e.get("de", title), {"en": e["en"], "tr": e["tr"]}

    def text(self, en: str) -> dict:
        e = self.d["texts"].get(en)
        if e is None:
            REP.add("Explanations and tips without Turkish wording (tm.yaml → texts)", en)
            return {"en": en, "tr": "⟦TR⟧ " + en}
        return {"en": e.get("en", en), "tr": e["tr"]}

    def simple(self, kind: str, key: str, label: str) -> dict:
        e = self.d.get(kind, {}).get(key)
        if e is None:
            REP.add(f"{label} (tm.yaml → {kind})", key)
            return {"de": "⟦DE⟧ " + key, "en": "⟦EN⟧ " + key, "tr": "⟦TR⟧ " + key}
        return e


# ── small helpers on raw elements ────────────────────────────────────────────
def is_english(text: str) -> bool:
    words = re.findall(r"[A-Za-z]+", text.lower())
    return bool(words) and sum(w in EN_WORDS for w in words) / len(words) > 0.12


def join_lines(els: list[dict]) -> list[str]:
    """Text lines → paragraphs (a new paragraph starts after a wider gap or on a new page after a full stop)."""
    paras: list[str] = []
    prev = None
    for e in els:
        new = prev is None or (e["page"] == prev["page"] and e["y"] - prev["y"] > 17.5) or \
              (e["page"] != prev["page"] and re.search(r"[.!?…:]$", prev["text"].strip()) is not None and e["y"] < 80)
        if new:
            paras.append(e["text"].strip())
        else:
            paras[-1] += " " + e["text"].strip()
        prev = e
    return paras


def cap_first(s: str) -> str:
    return s[:1].upper() + s[1:] if s[:1].islower() else s


def clean_answer(a: str) -> str:
    return re.sub(r"\s*\(\d+ points?\)\s*$", "", a).strip()


class Converter:
    def __init__(self, book: dict, tm: TM, vocab: Vocabulary):
        self.book, self.tm, self.vocab = book, tm, vocab
        self.pictures: list[tuple[int, tuple, str]] = []     # (page, bbox, image id)

    # ── answer key ───────────────────────────────────────────────────────────
    def key_for(self, scope: str) -> dict:
        idx: dict[tuple[str, str], list[dict]] = {}
        for e in self.book["answers"].get(scope, []):
            idx.setdefault((e["title"], e["letter"].lower()), []).append(e)
        return idx

    # ── inputs ───────────────────────────────────────────────────────────────
    def input_blocks(self, els: list[dict], ctx: dict) -> tuple[list[dict], list[dict], str | None]:
        """→ (body blocks, margin notes, prefix kind for the following task)."""
        body: list[dict] = []
        notes: list[dict] = []
        prefix = None
        i = 0
        # tips first: label TIP + the lines after it
        rest = []
        while i < len(els):
            e = els[i]
            if e["t"] == "label" and e["text"] == "TIP":
                j = i + 1
                tip = []
                while j < len(els) and els[j]["t"] == "text" and els[j].get("x", 0) > 59:
                    tip.append(els[j]["text"])
                    j += 1
                if tip:
                    notes.append({"type": "margin_note", "kind": "tipp", "text": self.tm.text(" ".join(tip))})
                i = j
                continue
            rest.append(e)
            i += 1
        els = rest
        kinds = {e["t"] for e in els}
        if "card" in kinds:
            return self.card_boxes(els, ctx), notes, None
        if "turn" in kinds:
            turns = []
            for e in els:
                if e["t"] == "turn":
                    turns.append({"speaker": e["speaker"], "text": e["text"]})
                elif e["t"] == "text" and turns:
                    turns[-1]["text"] += " " + e["text"]
            body.append({"type": "dialogue", "turns": turns})
            return body, notes, "dialogue"
        if "picture" in kinds:
            pic = next(e for e in els if e["t"] == "picture")
            cap = next((e["text"] for e in els if e["t"] == "caption"), None)
            iid = f'k{ctx["chapter"]}-b{ctx["block"]}'
            self.pictures.append((pic["page"], tuple(pic["bbox"]), iid))
            body.append(self.image(iid, "wide", cap))
            return body, notes, "picture"
        if "thead" in kinds or "trow" in kinds:
            head = next((e["cells"] for e in els if e["t"] == "thead"), [])
            rows = [e["cells"] for e in els if e["t"] == "trow"]
            body.append({"type": "grammar_box", "title": "", "head": [""] + [self.verb_case(h) for h in head] if head else [],
                         "rows": rows, "first_col_head": True})
            return body, notes, None
        if "phrase" in kinds:
            items = []
            for e in els:
                if e["t"] == "phrase":
                    t = self.tm.simple("phrases", e["text"], "Phrases without translation")
                    items.append({"de": e["text"], "en": t["en"], "tr": t["tr"]})
            body.append({"type": "phrases", "groups": [{"items": items}]})
            return body, notes, None
        if "vlist" in kinds:
            ids = []
            for e in els:
                for cell in e["cells"]:
                    head = cell.split(", Pl.")[0].strip()
                    vid = self.vocab.find(head)
                    if vid is None:
                        REP.add("Word list entries that are not in the vocabulary", f'Kapitel {ctx["chapter"]}: {cell}')
                    else:
                        ids.append(self.vocab.use(vid))
            body.append({"type": "vocab_cards", "style": "list", "items": ids})
            return body, notes, None
        if any(e["t"] == "label" and e["text"].startswith("I CAN") for e in els):
            body.append({"type": "can_do_list"})
            return body, notes, None
        texts = [e for e in els if e["t"] == "text"]
        hands = [e["text"] for e in els if e["t"] == "hand"]
        if texts and (hands or is_english(" ".join(e["text"] for e in texts))):
            box = {"type": "grammar_box", "title": "", "intro": self.tm.text(" ".join(e["text"] for e in texts))}
            if hands:
                box["lines"] = hands
            body.append(box)
            return body, notes, None
        if texts:
            paras = join_lines(texts)
            title = ctx.get("title", "")
            if all(re.match(r"[A-ZÄÖÜ][\wäöüß]+: ", p) for p in paras) and len(paras) > 1:
                parts = [{"label": p.split(": ", 1)[0], "text": p.split(": ", 1)[1]} for p in paras]
                body.append({"type": "reading_text", "genre": "profile", "parts": parts, "line_numbers": False})
                return body, notes, "profiles"
            if "E-Mail" in title or "Mail" in title:
                meta = {}
                m = re.match(r"(?:Hallo|Liebe[r]?|Hi|Guten Tag),? ([\wäöüÄÖÜß ]+?),?$", paras[0])
                sig = paras[-1] if len(paras[-1].split()) <= 2 else ""
                if sig:
                    meta["von"] = sig
                if m:
                    meta["an"] = m.group(1)
                rt = {"type": "reading_text", "genre": "email", "text": "\n\n".join(paras), "line_numbers": False}
                if meta:
                    rt["meta"] = meta
                body.append(rt)
                return body, notes, "email"
            body.append({"type": "reading_text", "genre": "plain", "text": "\n\n".join(paras), "line_numbers": False})
            return body, notes, "text"
        if els and not notes:
            REP.add("Input elements that were not converted", f'Kapitel {ctx["chapter"]} · Block {ctx["block"]}: {sorted(kinds)}')
        return body, notes, prefix

    def verb_case(self, head: str) -> str:
        low = head.lower()
        for p in self.vocab.by_printed:
            if p.lower().replace("ß", "ss") == low:
                return p
        return low

    def image(self, iid: str, fmt: str, caption: str | None = None) -> dict:
        t = self.tm.d.get("images", {}).get(iid)
        im = {"type": "image", "id": iid, "format": fmt, "src": f"assets/images/{LEVEL}/{iid}.jpg"}
        if t is None:
            REP.add("Pictures without description (tm.yaml → images)", iid)
            im["description"] = caption or f"Bild {iid}"
        else:
            im["description"] = t["description"]
            im["alt"] = {"en": t["en"], "tr": t["tr"]}
            if "focus" in t:
                im["focus"] = t["focus"]
        if caption:
            im["caption"] = caption
        return im

    def card_boxes(self, els: list[dict], ctx: dict) -> list[dict]:
        groups: list[tuple[str, list[str]]] = []
        moved: dict[str, list[str]] = {}
        for e in els:
            if e["t"] == "label":
                groups.append((e["text"], []))
            elif e["t"] == "card":
                vid = self.vocab.use(self.vocab.add_card(e))
                ctx["cards"].append(vid)
                target = (self.vocab.lex.get(e["word"]) or {}).get("group")
                if target:
                    moved.setdefault(target, []).append(vid)
                else:
                    if not groups:
                        groups.append(("", []))
                    groups[-1][1].append(vid)
        out = []
        for label, ids in groups:
            ids = ids + moved.pop(label, [])
            if ids:
                out.append({"type": "vocab_cards", "title": label.capitalize() if label.isupper() else label, "items": ids})
        for label, ids in moved.items():
            out.append({"type": "vocab_cards", "title": label.capitalize(), "items": ids})
        for b in out:                                       # LÄNDER UND STÄDTE → Länder und Städte
            words = b["title"].split()
            small = {"und", "oder", "im", "in", "am", "an", "auf", "zu", "mit", "für", "von", "der", "die", "das", "wichtige", "neue"}
            b["title"] = " ".join(w if (i and w in small) else w.capitalize() for i, w in enumerate(words))
        return out

    # ── tasks ────────────────────────────────────────────────────────────────
    def task(self, t: dict, ctx: dict, key: dict, pre_body: list[dict], prefix: str | None) -> dict:
        ch, blk = ctx["chapter"], ctx["block"]
        where = f'{ctx["scope"]} · {ctx["title"] or "Abschlusstest"} · {t["letter"]}'
        rubric, skills = self.tm.rubric(t["instr"], t["tag"], prefix)
        entries = key.get((ctx["title"] or "Abschlusstest", t["letter"]), [])
        ans = entries.pop(0) if entries else None
        ans_items = {int(k): clean_answer(v) for k, v in (ans["items"].items() if ans else [])}
        ans_text = clean_answer(ans["text"]) if ans else ""
        individual = ans_text.startswith("Antworten individuell")
        model_text = re.sub(r"^Antworten individuell\.\s*(Modell:)?\s*", "", ans_text)

        items: list[dict] = []
        free_lines, hands, bank, exline, tf = 0, [], [], None, False
        for e in t["els"]:
            k = e["t"]
            if k == "item":
                items.append({**e, "lines": 0})
            elif k == "line":
                if items:
                    items[-1]["lines"] += 1
                else:
                    free_lines += 1
            elif k == "text" and items and e.get("x", 0) > 60:
                items[-1]["text"] += " " + e["text"]
            elif k == "hand":
                hands.append(e["text"])
            elif k == "bank":
                bank += e["words"]
            elif k == "exline":
                exline = e["text"]
            elif k == "tfhead":
                tf = True
            elif k in ("label", "circlehead"):
                pass
            else:
                REP.add("Task elements that were not converted", f'{where}: {k} “{e.get("text", "")[:50]}”')
        body = list(pre_body)
        task: dict = {"type": "task", "id": t["letter"], "skills": skills, "rubric": rubric}
        if t["points"]:
            task["points"] = t["points"]
        if exline:
            body.append({"type": "text", "de": re.sub(r"^Example:\s*", "*Beispiel:* ", exline)})
        kinds = {it.get("kind") for it in items}
        answer: dict | None = None

        if "article" in kinds:
            ids = []
            for it in items:
                vid = self.vocab.find(it["text"])
                e = self.vocab.entries.get(vid) if vid else None
                if e is None:
                    REP.add("Article exercise: noun is not in the vocabulary", f"{where}: {it['text']}")
                elif not e.get("article"):
                    REP.add("FIXED · article exercise item dropped (the word has no article)", f"{where}: {it['text']}")
                else:
                    if ans_items.get(it["no"]) and ans_items[it["no"]] != e["article"]:
                        REP.add("Article in the old key differs from the vocabulary", f"{where}: {it['text']} – key {ans_items[it['no']]}, vocabulary {e['article']}")
                    ids.append(self.vocab.use(vid))
            body.append({"type": "article_choice", "items": ids})
        elif "match" in kinds:
            pairs = dict(re.findall(r"(\d+)\s*([a-l])", ans_text)) if ans_text else {}
            left_ids = [self.vocab.find(it["text"]) for it in items]
            letters = [it["letter"] for it in items]
            if all(left_ids) and len(pairs) == len(items) and len(set(left_ids)) == len(left_ids):
                right = [None] * len(items)
                for it, vid in zip(items, left_ids):
                    right[letters.index(pairs[str(it["no"])])] = vid
                for v in left_ids:
                    self.vocab.use(v)
                body.append({"type": "vocab_match", "left": left_ids, "right": right})
            else:
                REP.add("Matching task kept with its original right-hand side (check the Turkish edition)", where)
                body.append({"type": "matching", "left": [it["text"] for it in items], "right": [it["right"] for it in items],
                             "answer": [pairs.get(str(it["no"]), "A").upper() for it in items]})
        elif tf:
            tf_items = []
            for it in items:
                a = ans_items.get(it["no"], "")
                m = re.match(r"(true|false)\s*(?:\((.*)\))?", a)
                if not m:
                    REP.add("True/false item without key", f"{where}: {it['no']}")
                    m = re.match(r"(true)", "true")
                item = {"text": it["text"], "answer": m.group(1) == "true"}
                if m.lastindex and m.lastindex >= 2 and m.group(2):
                    fix = m.group(2).strip()
                    item["fix"] = fix if fix.endswith((".", "!", "?")) else fix + "."
                tf_items.append(item)
            body.append({"type": "true_false", "items": tf_items})
        elif any("[[]]" in it["text"] for it in items):
            if t["instr"].startswith("How do you say it in German"):
                ids = []
                for it in items:
                    vid = self.vocab.find(ans_items.get(it["no"], ""))
                    if vid is None:
                        REP.add("Translation exercise: answer is not in the vocabulary", f"{where}: {it['text']} → {ans_items.get(it['no'])}")
                    else:
                        ids.append(self.vocab.use(vid))
                body.append({"type": "vocab_translate", "items": ids})
            else:
                body.append(self.gap_text(items, ans_items, bank, t, where))
        elif items:
            sb_items = []
            scrambled = all(" / " in it["text"] for it in items)
            for it in items:
                given = it["text"]
                a = ans_items.get(it["no"])
                if scrambled:
                    toks = [x for x in given.split(" / ") if not re.fullmatch(r"[A-ZÄÖÜ]\w+:", x.strip())]
                    if len(toks) != len(given.split(" / ")):
                        REP.add("FIXED · speaker label removed from a sentence puzzle", f"{where}: {given}")
                        a = re.sub(r"^[A-ZÄÖÜ]\w+:\s*", "", a) if a else a
                    given = " / ".join(toks)
                entry = {"given": given}
                if a and not individual:
                    entry["answer"] = a
                sb_items.append(entry)
            # one line per answer is the least; where a page has room, the paginator gives every answer a second line (as the old book had)
            sb = {"type": "sentence_build", "items": sb_items, "lines": 1, "grow": True}
            body.append(sb)
            if individual or not all("answer" in x for x in sb_items):
                model = " ".join(f"**{n}** {a}" for n, a in sorted(ans_items.items())) if ans_items else model_text
                for x in sb_items:
                    x.pop("answer", None)
                answer = {"open": True, **({"model": model} if model else {})}
        else:
            n = max(free_lines, 3)
            wl: dict = {"type": "write_lines", "lines": n - (1 if hands else 0)}
            if hands:
                wl["model"] = " ".join(hands)
            body.append(wl)
            answer = {"open": True}
            if model_text and model_text != " ".join(hands):
                answer["model"] = model_text
        if not pre_body and body:                          # long drills run in two columns across text column and margin
            ex = body[-1]
            n = len(ex.get("items", []))
            if (ex["type"] == "article_choice" and n > 6) or (ex["type"] == "vocab_translate" and n > 5) or \
               (ex["type"] == "gap_text" and n >= 6 and not ex.get("bank") and max(self.width(x) for x in ex["items"]) <= 68):
                task["wide"] = True
                ex.pop("compact", None)
        if body:
            task["body"] = body
        if answer:
            task["answer"] = answer
        return task

    @staticmethod
    def width(x: str) -> float:
        """Rough printed width of an item in mm: text plus its write-in gaps."""
        gaps = re.findall(r"\[\[(.*?)\]\]", x)
        return len(re.sub(r"\[\[.*?\]\]", "", x)) * 1.9 + sum(max(13, 8 + 2.15 * len(g.split("~")[-1])) + 1.6 for g in gaps)

    def gap_text(self, items: list[dict], ans: dict[int, str], bank: list[str], t: dict, where: str) -> dict:
        out_items = []
        example = None
        m = re.match(r"Write the plural\. Example: (.+?) – die (.+?)\.", t["instr"])
        for it in items:
            text = it["text"]
            a = ans.get(it["no"])
            if a is None:
                REP.add("Gap without answer in the old key", f"{where}: {it['no']} {text}")
                a = "?"
            n = text.count("[[]]")
            parts = [a] if n == 1 else [x.strip() for x in re.split(r"\s*[/,·]\s*", a)]
            if len(parts) != n:
                REP.add("Gaps and answers do not match – check by hand", f"{where}: {text} ← {a}")
                parts = (parts + ["?"] * n)[:n]
            for p in parts:
                lead = re.search(r"(?<![\wäöüÄÖÜß])([A-Za-zÄÖÜäöüß])\[\[\]\]", text)
                if lead and p[:1].lower() == lead.group(1).lower():
                    text = text[:lead.start(1)] + f"[[{p[:1]}~{p[1:]}]]" + text[lead.end():]
                else:
                    text = text.replace("[[]]", f"[[{p}]]", 1)
            if text[:1].islower() and not text.startswith(("der ", "die ", "das ")) and "[[" not in text[:3]:
                REP.add("FIXED · sentence start capitalised", f"{where}: {text}")
                text = cap_first(text)
            if m and re.sub(r"\[\[(.*?)\]\]", r"\1", text).replace("  ", " ") == f"{m.group(1)} – die {m.group(2)}":
                example = text                                 # the old instruction gave away item 1: it becomes the worked example
                REP.add("FIXED · the example of the instruction was also item 1; it is now shown as the solved example", where)
                continue
            out_items.append(text)
        gt: dict = {"type": "gap_text", "items": out_items}
        if m and example is None:
            example = f"{m.group(1)} – die [[{m.group(2)}]]"
        if example:
            gt["example"] = example
        if bank:
            gt["bank"] = bank
        if len(out_items) >= 4 and max(self.width(x) for x in out_items) <= 46:
            gt["compact"] = True
        return gt

    # ── one block → Teil ─────────────────────────────────────────────────────
    def teil(self, nr: int, section: str | None, blocks: list[dict], ctx: dict, key: dict) -> dict:
        title_src = next((b["title"] for b in blocks if b["title"]), "")
        ctx.update({"block": nr, "title": title_src})
        de, sub = self.tm.title(title_src)
        teil: dict = {"nr": nr, **({"section": section} if section else {}), "title": de, **({"subtitle": sub} if sub else {}), "blocks": []}
        units: list[dict] = []           # converted blocks plus bookkeeping for the footer words
        for b in blocks:
            pending: tuple[list[dict], list[dict], str | None, set, str] | None = None
            for e in b["seq"]:
                pages = {e["page"]} | {x["page"] for x in e["els"]}
                text = " ".join(str(x.get("text", "")) + " " + " ".join(x.get("words", [])) for x in e["els"]) + " " + e.get("instr", "")
                if e["kind"] == "input":
                    if pending:
                        units.append(self.box(pending))
                    if any(x["t"] == "score" for x in e["els"]) and section == "abschlusstest":
                        continue                               # "Read each task carefully …" + score field: the new test has its own
                    body, notes, prefix = self.input_blocks(e["els"], ctx)
                    if any(x.get("type") == "vocab_cards" and x.get("style") != "list" for x in body):
                        for i, vb in enumerate(body):          # one box per card group, so pages can break between groups
                            units.append({"block": {"type": "box", "body": [vb]}, "pages": pages, "text": "", "cards": True})
                        continue
                    pending = (body, notes, prefix, pages, text)
                else:
                    pre, notes, prefix, ppages, ptext = pending if pending else ([], [], None, set(), "")
                    attach = bool(pre) and prefix is not None      # dialogue, text or picture: it belongs to this task
                    if pending and not attach:
                        units.append(self.box(pending))
                        pre, notes, ppages, ptext, prefix = [], [], set(), "", None
                    task = self.task(e, ctx, key, pre, prefix)
                    if notes:
                        task["notes"] = notes
                    units.append({"block": task, "pages": pages | ppages, "text": text + " " + ptext})
                    pending = None
            if pending:
                units.append(self.box(pending))
        teil["_units"] = units
        return teil

    @staticmethod
    def box(p: tuple) -> dict:
        body, notes, _prefix, pages, text = p
        blk: dict = {"type": "box", "body": body}
        if notes:
            blk["notes"] = notes
        return {"block": blk, "pages": pages, "text": text}

    # ── footers → words of the units ─────────────────────────────────────────
    def assign_words(self, teile: list[dict], cards: list[str]) -> None:
        units = [(u, t) for t in teile for u in t["_units"]]
        pages = sorted({p for u, _ in units for p in u["pages"]})
        for p in pages:
            for word, gloss in self.book["footers"].get(str(p), []):
                vid = self.vocab.add_footer(word, gloss)
                if vid is None:
                    continue
                cands = [(u, t) for u, t in units if p in u["pages"] and u["block"].get("body") is not None]
                if not cands:
                    continue
                rx = self.vocab.forms_rx(vid)
                u, t = next(((u, t) for u, t in cands if rx.search(u["text"])), cands[0])
                if vid in cards and t.get("section") == "wortschatz":
                    continue                                   # the card on the same pages already explains the word
                words = u["block"].setdefault("words", [])
                if vid not in words:
                    words.append(self.vocab.use(vid))
        for t in teile:
            t["blocks"] = [u["block"] for u in t.pop("_units") if u["block"].get("body") or u["block"]["type"] == "task"]

    # ── chapter and revision unit ────────────────────────────────────────────
    def chapter(self, n: int) -> dict:
        src = self.book["chapters"][str(n)]
        ctx = {"chapter": n, "scope": f"Kapitel {n}", "cards": []}
        key = self.key_for(f"K{n}")
        sub = self.tm.simple("subtitles", src["subtitle"], "Chapter subtitles without translation")
        goal = self.tm.simple("goals", src["goal"], "Chapter goals without German / Turkish wording") if src["goal"] else None
        if goal is None:
            goal = (self.tm.d.get("goals_new") or {}).get(n)
            REP.add("FIXED · the old book printed no goal for this chapter; one was written" if goal else "Chapters without a goal in the old book", f"Kapitel {n}")
            goal = goal or {"de": "⟦DE⟧", "en": "⟦EN⟧", "tr": "⟦TR⟧"}
        iid = f"k{n}-auftakt"
        if src.get("picture"):
            self.pictures.append((src["page"], tuple(src["picture"]), iid))
        ch: dict = {"type": "chapter", "level": LEVEL, "number": n, "title": src["title"], "subtitle_de": src["subtitle"],
                    "subtitle": {"en": sub["en"], "tr": sub["tr"]},
                    "goal": {"de": goal["de"], "en": goal.get("en", src["goal"]), "tr": goal["tr"]}, "can_do": [],
                    "topics": src["topics"], "image": self.image(iid, "banner"), "teile": []}
        for c in src["cando"]:
            e = self.tm.simple("cando", c, "Can-do statements without German / Turkish wording")
            cd = {"de": e["de"], "en": e["en"], "tr": e["tr"]}
            if e.get("ref"):
                cd["ref"] = f'{n}.{e["ref"]}'
            ch["can_do"].append(cd)
        teile = []
        nr = 0
        for s in src["sections"]:
            groups: list[list[dict]] = []
            for b in s["blocks"]:
                if b["no"] is None and s["id"] == "wortschatz":
                    groups.append([b])                         # the cards: they open block 1
                elif groups and groups[-1][0]["no"] is None and s["id"] == "wortschatz" and len(groups[-1]) == 1:
                    groups[-1].append(b)
                else:
                    groups.append([b])
            for g in groups:
                nr += 1
                src_no = next((b["no"] for b in g if b["no"] is not None), None)
                if src_no is not None and src_no != nr:
                    REP.add("Block numbers differ from the old book", f"Kapitel {n}: old {src_no} → new {nr}")
                teile.append(self.teil(nr, s["id"], g, ctx, key))
        self.assign_words(teile, ctx["cards"])
        ch["teile"] = teile
        left = [f"{t} · {letter}" for (t, letter), v in key.items() for _ in v]
        if left:
            REP.add("Answers of the old key that found no task", f"Kapitel {n}: {left}")
        return ch

    def revision(self, n: int) -> dict:
        src = self.book["revisions"][str(n)]
        ctx = {"chapter": n, "scope": f"Wiederholung {n}", "cards": []}
        key = self.key_for(f"W{n}")
        sub = self.tm.d["revision"]["subtitle"]
        st: dict = {"type": "station", "kind": "revision", "level": LEVEL, "number": n, "title": src["title"],
                    "subtitle": {k: v.replace("{n}", str(n)) for k, v in sub.items()}, "covers": [n], "teile": []}
        teile = [self.teil(i, None, [b], ctx, key) for i, b in enumerate(src["blocks"], 1)]
        self.assign_words(teile, [])
        st["teile"] = teile
        left = [f"{t} · {letter}" for (t, letter), v in key.items() for _ in v]
        if left:
            REP.add("Answers of the old key that found no task", f"Wiederholung {n}: {left}")
        return st

    def outline(self) -> dict:
        chapters = []
        for n in range(1, 13):
            src = self.book["chapters"][str(n)]
            sub = self.tm.simple("subtitles", src["subtitle"], "Chapter subtitles without translation")
            chapters.append({"number": n, "title": src["title"], "subtitle": {"en": sub["en"], "tr": sub["tr"]}, "grammar": src["topics"][:3]})
        return {"level": LEVEL, "chapters": chapters}

    # ── pictures ─────────────────────────────────────────────────────────────
    def export_pictures(self) -> None:
        import pdfsrc
        from PIL import Image
        IMG.mkdir(parents=True, exist_ok=True)
        for page, bbox, iid in self.pictures:
            pg = pdfsrc.page(page)
            best = None
            for info in pg.get_image_info(xrefs=True):
                b = info["bbox"]
                if abs(b[0] - bbox[0]) < 3 and abs(b[1] - bbox[1]) < 3 and info["xref"]:
                    best = info["xref"]
            if best is None:
                REP.add("Pictures that could not be extracted", f"{iid} (page {page})")
                continue
            data = pg.parent.extract_image(best)
            im = Image.open(io.BytesIO(data["image"])).convert("RGB")
            if im.width > 1600:
                im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
            im.save(IMG / f"{iid}.jpg", quality=84, optimize=True, progressive=True)


class Dumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


def write_yaml(path: Path, data, head: str) -> None:
    text = yaml.dump(data, Dumper=Dumper, allow_unicode=True, sort_keys=False, width=180, default_flow_style=False)
    path.write_text(head + text)


def parse_range(spec: str) -> list[int]:
    out: list[int] = []
    for tok in spec.split(","):
        if "-" in tok:
            a, b = tok.split("-")
            out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(tok))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapters", default="1")
    ap.add_argument("--no-pictures", action="store_true")
    args = ap.parse_args()
    book = json.loads((HERE / "book.json").read_text())
    tm = TM(yaml.safe_load((HERE / "tm.yaml").read_text()))
    vocab = Vocabulary(yaml.safe_load((HERE / "lexicon.yaml").read_text()) or {})
    conv = Converter(book, tm, vocab)
    OUT.mkdir(parents=True, exist_ok=True)
    note = "# Generated by tools/a1_import/convert.py from «Deutsch in Farbe A1». Change the wording in tools/a1_import/tm.yaml\n# and lexicon.yaml and run the converter again – or edit this file and stop regenerating it.\n"
    for n in parse_range(args.chapters):
        write_yaml(OUT / f"kapitel-{n:02d}.yaml", conv.chapter(n), note)
        write_yaml(OUT / f"wiederholung-{n:02d}.yaml", conv.revision(n), note)
    write_yaml(OUT / "book.yaml", conv.outline(), note)
    write_yaml(OUT / "vocabulary.yaml", vocab.dump(), note)
    if not args.no_pictures:
        conv.export_pictures()
    REP.write(HERE / "report.md")
    print(f"chapters {args.chapters}: {len(vocab.used)} words · {len(conv.pictures)} pictures · report: {sum(len(v) for v in REP.items.values())} entries in {len(REP.items)} groups")
    for k, v in REP.items.items():
        print(f"  {len(v):3d} × {k}")


if __name__ == "__main__":
    main()
