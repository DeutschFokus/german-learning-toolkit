import fitz, glob, re
UP = "/root/.claude/uploads/9f8f440e-accd-5562-9a69-0ddd5b4d7ae8/"
FILES = sorted(glob.glob(UP + "*Deutsch_in_Farbe*.pdf"), key=lambda f: int(re.search(r"Part_(\d)", f).group(1)))
DOCS = [fitz.open(f) for f in FILES]
def page(n):
    return DOCS[(n - 1) // 80][(n - 1) % 80]
def spans(n):
    out = []
    for b in page(n).get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                if s["text"].strip():
                    out.append((round(s["bbox"][0], 1), round(s["origin"][1], 1), round(s["size"], 1), s["font"].split("+")[-1].replace("Poppins-", "P-").replace("Fraunces-", "F-").replace("Caveat-", "C-"), "%06x" % s["color"], s["text"]))
    return out

def lines(n, skip_furniture=True):
    """Merge spans into visual lines: [(y, x0, [(size, font, color, text), ...])]"""
    sp = sorted(spans(n), key=lambda s: (round(s[1]), s[0]))
    out = []
    for s in sp:
        if skip_furniture and (s[1] < 40 or (s[2] == 20.0 and s[0] > 560) or (s[2] == 11.5 and s[1] > 795 and s[0] > 520)):
            continue
        if out and abs(out[-1][0] - s[1]) < 2.6:
            out[-1][2].append(s)
        else:
            out.append([s[1], s[0], [s]])
    return out

def show(n, maxlen=150):
    print(f"=== page {n}")
    for y, x0, ss in lines(n):
        ss = sorted(ss, key=lambda s: s[0])
        parts = []
        for s in ss:
            tag = f"{s[2]:g}{s[3][0]}{s[3][2:5]}"
            if s[4] not in ("1b1e4b",):
                tag += "#" + s[4][:3]
            parts.append(f"[{tag}@{s[0]:.0f}]{s[5]}")
        print(f" {y:5.0f} " + " ".join(parts)[:maxlen])
