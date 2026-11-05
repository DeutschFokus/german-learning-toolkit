"""Script markup.

A narration line is plain text, with one extension: ``{display|spoken}``
shows ``display`` on screen while the narrator says ``spoken``.

    "In {2010|twenty ten}, physicists measured it."

Each display token knows which spoken words belong to it, so word-level
timings from the aligner map straight back onto the captions.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

_TOKEN = re.compile(r"\{[^}]*\}[^\s{]*|\S+")
_NORM = re.compile(r"[^a-z0-9']+")


@dataclass
class Token:
    display: str                      # what the caption shows ("2010,")
    spoken: list[str]                 # what is said (["twenty", "ten,"])
    align: list[str] = field(default_factory=list)  # normalised aligner words


def normalise(word: str) -> list[str]:
    """Spoken word -> aligner words (lower case, no punctuation, hyphens split)."""
    out = []
    for part in word.lower().replace("-", " ").replace("—", " ").split():
        part = _NORM.sub("", part).strip("'")
        if part:
            out.append(part)
    return out


def parse(text: str) -> list[Token]:
    tokens: list[Token] = []
    for raw in _TOKEN.findall(text):
        if raw.startswith("{"):
            body, _, trail = raw[1:].partition("}")
            disp, _, spoken = body.partition("|")
            spoken = spoken or disp
            words = spoken.split()
            if trail and words:
                words[-1] += trail
            tok = Token(display=disp + trail, spoken=words)
        else:
            tok = Token(display=raw, spoken=[raw])
        for w in tok.spoken:
            tok.align.extend(normalise(w))
        tokens.append(tok)
    return tokens


def display_text(text: str) -> str:
    return " ".join(t.display for t in parse(text))


def spoken_text(text: str) -> str:
    return " ".join(w for t in parse(text) for w in t.spoken)


def align_words(text: str) -> list[str]:
    return [w for t in parse(text) for w in t.align]
