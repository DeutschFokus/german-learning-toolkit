"""Place voiceover lines on a timeline and resolve time anchors.

Anchors are strings such as "L04.end+0.3", "L12.w8.start", "L12.w8", "START",
"END-2", or plain numbers (seconds). Word indices are 0-based caption tokens.
"""
import re


class Timeline:
    def __init__(self, story, timing, lead_in=0.9, tail=6.0):
        self.story = story
        self.timing = timing
        self.lines = {}
        t = lead_in
        for line in story["lines"]:
            lid = line["id"]
            d = timing[lid]["dur"]
            words = [dict(w, start=w["start"] + t, end=w["end"] + t) for w in timing[lid]["words"]]
            self.lines[lid] = {"start": t, "end": t + d, "dur": d, "words": words,
                               "voice": line["voice"], "line": line}
            t += d + line.get("pause", 0.6)
        last = story["lines"][-1]["id"]
        self.speech_end = self.lines[last]["end"]
        self.duration = self.speech_end + tail

    _re = re.compile(r"^\s*([A-Za-z_][\w]*)(?:\.(w-?\d+))?(?:\.(start|end|mid))?\s*([+-]\s*[\d.]+)?\s*$")

    def t(self, anchor):
        if isinstance(anchor, (int, float)):
            return float(anchor)
        a = anchor.strip()
        try:
            return float(a)
        except ValueError:
            pass
        m = self._re.match(a)
        if not m:
            raise ValueError(f"bad anchor {anchor!r}")
        name, word, edge, off = m.groups()
        off = float(off.replace(" ", "")) if off else 0.0
        edge = edge or "start"
        if name == "START":
            base = 0.0
        elif name == "END":
            base = self.duration
        elif name == "SPEECH_END":
            base = self.speech_end
        else:
            ln = self.lines[name]
            if word:
                w = ln["words"][int(word[1:])]
                base = {"start": w["start"], "end": w["end"], "mid": 0.5 * (w["start"] + w["end"])}[edge]
            else:
                base = {"start": ln["start"], "end": ln["end"], "mid": 0.5 * (ln["start"] + ln["end"])}[edge]
        return base + off

    def word_index(self, lid, token):
        for i, w in enumerate(self.lines[lid]["words"]):
            if token.lower() in w["tok"].lower():
                return i
        raise KeyError(f"{token} not in {lid}")

    def speech_intervals(self):
        return [(v["start"], v["end"]) for v in self.lines.values()]

    def chunks(self):
        """Subtitle chunks with absolute timing: list of dicts."""
        out = []
        for line in self.story["lines"]:
            ln = self.lines[line["id"]]
            for ci, (de, en) in enumerate(line["chunks"]):
                ws = [w for w in ln["words"] if w["chunk"] == ci]
                out.append({"line": line["id"], "idx": ci, "de": de, "en": en,
                            "start": ws[0]["start"], "end": ws[-1]["end"], "words": ws,
                            "voice": line["voice"], "handwriting": line.get("handwriting", False)})
        return out
