#!/usr/bin/env python3
"""Extra linguistic consistency checks on top of build.py --qa.

1. ASPECT: in aspect (E) and verb (D) answers, the aspect of each answer verb must match
   the aspect the explanation names ("→ imperfective" / "→ perfective").
2. BUDU: «буду / будешь …» + infinitive must use an imperfective infinitive.
3. GENDER: when the instruction says "The speaker is a man / woman" and the question has «я ___»,
   first-person past-tense answers must have that gender.
4. VARIANTS: an "Also correct" line must differ from the answer.
"""
import re
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build  # noqa: E402
import pymorphy3  # noqa: E402

morph = pymorphy3.MorphAnalyzer()
WORD = re.compile(r"[А-Яа-яЁё]+")


def verb_parses(tok):
    return [p for p in morph.parse(tok.lower()) if p.tag.POS in ("VERB", "INFN") and p.score > 0.05]


def aspects(tok):
    return {p.tag.aspect for p in verb_parses(tok) if p.tag.aspect}


issues = []
for key in build.ORDER:
    if isinstance(key, str) and key.startswith("P:"):
        continue
    u = build.load_unit(key)
    for b in u["blocks"]:
        for ex in b["items"]:
            ref = f'{u["file"]}:{ex["line"]} ({key}.{ex["n"]} {ex["type"]})'
            a, w, q, n = ex.get("A", ""), ex.get("W", ""), ex.get("Q", ""), ex.get("N", "")
            # 1. aspect vs explanation (E items, single-verb answers)
            if ex["type"] == "E":
                parts = [x.strip() for x in a.split(";")]
                claims = re.findall(r"(imperfective|perfective)", w)
                # explanation claims in order of appearance, one per answer part where possible
                for i, part in enumerate(parts):
                    toks = WORD.findall(part)
                    verbs = [t for t in toks if verb_parses(t) and t.lower() not in ("буду", "будешь", "будет", "будем", "будете", "будут")]
                    if not verbs:
                        continue
                    asp = set().union(*[aspects(v) for v in verbs])
                    if not claims:
                        issues.append(f"{ref}: explanation names no aspect")
                        continue
                    claim = claims[min(i, len(claims) - 1)]
                    want = "impf" if claim == "imperfective" else "perf"
                    if asp and want not in asp:
                        issues.append(f"{ref}: answer '{part}' is {sorted(asp)} but explanation says {claim}")
            # 2. буду + infinitive must be imperfective
            for m in re.finditer(r"\b(буду|будешь|будет|будем|будете|будут)\s+([А-Яа-яЁё]+)", a):
                inf = m.group(2)
                ps = [p for p in morph.parse(inf.lower()) if p.tag.POS == "INFN"]
                if ps and all(p.tag.aspect == "perf" for p in ps):
                    issues.append(f"{ref}: '{m.group(0)}' uses a perfective infinitive")
            # 3. speaker gender vs first-person past answers
            g = None
            if re.search(r"speaker is a man|speaker is a man\b", n):
                g = "masc"
            elif re.search(r"speaker is a woman", n):
                g = "femn"
            if g and ex["type"] in "DEI" and re.search(r"\bя\s+(не\s+)?(уже\s+)?(_{5,}|[А-Яа-яЁё]*_{2,})", q):
                for part in [x.strip() for x in a.split(";")]:
                    for tok in WORD.findall(part):
                        for p in morph.parse(tok.lower()):
                            if p.tag.POS == "VERB" and p.tag.tense == "past" and p.score > 0.3:
                                if p.tag.gender and p.tag.gender != g and p.tag.number == "sing":
                                    issues.append(f"{ref}: speaker {g} but answer form '{tok}' is {p.tag.gender}")
                                break
            # 4. variants differ from the answer
            v = ex.get("V", "")
            if v and build.norm(v.split("·")[0].strip()) == build.norm(a):
                issues.append(f"{ref}: 'Also correct' repeats the answer")

for i in issues:
    print("CHECK", i)
print(f"{len(issues)} items to review")
