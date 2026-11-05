"""Word-synced captions (burned in) and SRT export.

Style: short uppercase chunks, the current word pops, words not yet spoken
wait at low opacity, script emphasis words carry the accent colour.
Captions sit at Look.CAPTION_Y, inside the safe zone of all four platforms.
"""
from __future__ import annotations

import math

from .gfx import L, Canvas, clamp, ease_out_back, ease_out_cubic, prog, text_width

PUNCT_BREAK = (",", ".", ":", ";", "?", "!", "…", "...")


def _key(s):
    return s.lower().strip(".,:;!?…'\"")


class Captions:
    def __init__(self, timeline, accent_by_line=None, max_chars=17, max_words=4, size=76,
                 y=L.CAPTION_Y, enabled_from=0.0):
        self.size = size
        self.y = y
        self.accent_by_line = accent_by_line or {}
        self.chunks = []
        lines = timeline.lines
        for li, line in enumerate(lines):
            if not line.get("caption", True):
                continue
            emph = {_key(e) for e in line.get("emphasis", [])}
            accent = self.accent_by_line.get(line["id"], L.CYAN)
            cur = []
            toks = line["tokens"]
            for ti, tok in enumerate(toks):
                word = {"text": tok["display"].upper(), "start": tok["start"], "end": tok["end"],
                        "emph": _key(tok["display"]) in emph, "accent": accent}
                if cur:
                    chars = sum(len(w["text"]) + 1 for w in cur) + len(word["text"])
                    gap = tok["start"] - cur[-1]["end"]
                    if (chars > max_chars or len(cur) >= max_words or gap > 0.35
                            or cur[-1]["text"].endswith(PUNCT_BREAK)):
                        self.chunks.append(cur)
                        cur = []
                cur.append(word)
            if cur:
                self.chunks.append(cur)
        # display windows: a chunk holds until the next one starts (max 0.6 s after its last word)
        for i, ch in enumerate(self.chunks):
            start = ch[0]["start"] - 0.06
            end = ch[-1]["end"] + 0.6
            if i + 1 < len(self.chunks):
                # hand over exactly when the next chunk appears: never two chunks on screen at once
                end = min(end, self.chunks[i + 1][0]["start"] - 0.06)
            for w in ch:
                w["text"] = w["text"].replace("...", "…")
            self.chunks[i] = {"words": ch, "start": start, "end": max(end, start + 0.05)}

    def draw(self, cv: Canvas, t, alpha=1.0, y=None):
        y = self.y if y is None else y
        for ch in self.chunks:
            if ch["start"] <= t < ch["end"]:
                self._draw_chunk(cv, ch, t, alpha, y)

    def _draw_chunk(self, cv, ch, t, alpha, y):
        size = self.size
        font = L.DISPLAY
        tracking = 0.01
        words = ch["words"]
        space = size * 0.28
        widths = [text_width(cv.u, w["text"], size, font, tracking) for w in words]
        total = sum(widths) + space * (len(words) - 1)
        maxw = L.SAFE_RIGHT - L.SAFE_LEFT - 60
        if total > maxw:
            k = maxw / total
            size *= k
            space *= k
            widths = [w * k for w in widths]
            total = maxw
        intro = ease_out_cubic(prog(t, ch["start"], ch["start"] + 0.12))
        a_chunk = alpha * intro
        cx = (L.SAFE_LEFT + L.SAFE_RIGHT) / 2
        x = cx - total / 2
        cv.u.save()
        cv.u.translate(cx, y)
        sc = 0.94 + 0.06 * intro
        cv.u.scale(sc, sc)
        cv.u.translate(-cx, -y)
        for w, wd in zip(words, widths):
            spoken = t >= w["start"] - 0.02
            active = w["start"] - 0.02 <= t < w["end"] + 0.05
            col = w["accent"] if w["emph"] else L.WHITE
            a = a_chunk * (1.0 if spoken else 0.42)
            pop = 0.0
            if active:
                pop = 1 - ease_out_cubic(prog(t, w["start"] - 0.02, w["start"] + 0.22))
            s = 1.0 + 0.10 * pop
            wx = x + wd / 2
            cv.u.save()
            cv.u.translate(wx, y)
            cv.u.scale(s, s)
            cv.u.translate(-wx, -y)
            cv.text(w["text"], wx, y, size, font=font, color=col, alpha=a, anchor="center",
                    tracking=tracking, layer="ui", outline=(0.01, 0.02, 0.06), outline_w=size * 0.16,
                    shadow=0.9)
            cv.u.restore()
            x += wd + space
        cv.u.restore()


# --------------------------------------------------------------------------- SRT

def _fmt(t):
    t = max(0.0, t)
    h = int(t // 3600)
    m = int(t % 3600 // 60)
    s = int(t % 60)
    ms = int(round((t - math.floor(t)) * 1000))
    if ms == 1000:
        s, ms = s + 1, 0
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(timeline, path, max_chars=38):
    """Readable closed captions: whole phrases, <= max_chars per event."""
    events = []
    for line in timeline.lines:
        toks = line["tokens"]
        cur = []
        for tok in toks:
            cand = " ".join([x["display"] for x in cur] + [tok["display"]])
            if cur and len(cand) > max_chars:
                events.append(cur)
                cur = []
            cur.append(tok)
        if cur:
            events.append(cur)
    out = []
    for i, ev in enumerate(events):
        start = ev[0]["start"]
        end = ev[-1]["end"] + 0.25
        if i + 1 < len(events):
            end = min(end, events[i + 1][0]["start"] - 0.02)
        out.append(f"{i + 1}\n{_fmt(start)} --> {_fmt(max(end, start + 0.4))}\n"
                   f"{' '.join(x['display'] for x in ev)}\n")
    open(path, "w", encoding="utf-8").write("\n".join(out))
    return len(out)
