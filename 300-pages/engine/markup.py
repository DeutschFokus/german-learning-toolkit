"""Inline markup → HTML, plus language-aware micro-typography.

Authors type plain text with a handful of marks; this module turns it into
clean, correctly typeset HTML. Letter-spacing is never faked with spaces, so
text extracted from the PDF stays searchable.

    [[Antwort]]  [[Antwort|Hinweis]]     write-in gap sized to the answer; answer goes to the key
    {?den|dem*}                          inline tick choice (* = correct)
    ==Endung==  **fett**  *kursiv*  ~~falsch~~
    {der Tisch} {die Lampe} {das Bad}    noun phrase, article in its colour
    {m:dem Tisch} {f:der Wand} {n:dem Sofa} {p:den Fenstern}   same, for inflected articles
    {de:Hausverwaltung}                  a German word inside an explanation
    {S:5.3a} {S:5.uebersicht}            page reference, live link ("S. 104")
    {z:anker} {z:von-bis}                line reference ("Z. 4", "Z. 4–5")
    {#anker}                             line anchor inside a reading text
"""
from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from typing import Callable, Optional

NBSP = " "
NNBSP = " "        # narrow no-break space: S. 101, z. B.

_UNITS = (r"Uhr|Euro|€|m²|qm|%|Cent|kg|km|cm|mm|Min\.|Minuten|Stunden|Prozent|Punkte|Punkt|Wochen|Monaten|Monate|"
          r"Jahren|Jahre|Zimmer|MM|P\.")
_MONTHS = "Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember"

_RE_DE = [
    (re.compile(r"\b(S|Z|Nr|Kap|Abb|Tel)\.[  ]?(?=\d)"), r"\1." + NNBSP),
    (re.compile(r"\bz\.[  ]?B\."), "z." + NNBSP + "B."),
    (re.compile(r"\bd\.[  ]?h\."), "d." + NNBSP + "h."),
    (re.compile(r"\bu\.[  ]?a\."), "u." + NNBSP + "a."),
    (re.compile(r"(\d) (?=(?:%s)(?![A-Za-zÄÖÜäöüß]))" % _UNITS), r"\1" + NBSP),
    (re.compile(r"\b(\d{1,2}\.) (?=(?:Stock|OG|Etage|Klasse|%s)\b)" % _MONTHS), r"\1" + NBSP),
    (re.compile(r"\b(Herr|Herrn|Frau|Familie|Dr\.) (?=[A-ZÄÖÜİ])"), r"\1" + NBSP),
    (re.compile(r"\b(\d{1,2})-(\d{1,2})\b(?=[  ](?:Uhr|Euro|€|%|Jahre|Punkte))"), r"\1–\2"),
]
_RE_EN = [
    (re.compile(r"\b(p|pp|no)\.[  ]?(?=\d)"), r"\1." + NNBSP),
]
_RE_COMMON = [
    (re.compile(r"\.\.\."), "…"),
    (re.compile(r"(?<=\S) - (?=\S)"), " – "),
    (re.compile(r"(?<=\w)'(?=\w)|(?<=\w)'(?=\s|$)"), "’"),
]


def typo(text: str, lang: str) -> str:
    """Micro-typography on raw text (before HTML escaping)."""
    if not text:
        return ""
    out = []
    opening = True
    # typographic double quotes: „…“ in German, “…” elsewhere
    for i, ch in enumerate(text):
        if ch == '"':
            prev = text[i - 1] if i else " "
            is_open = prev.isspace() or prev in "([{–—-/>" or i == 0
            if lang == "de":
                out.append("„" if is_open else "“")
            else:
                out.append("“" if is_open else "”")
            opening = not is_open
        else:
            out.append(ch)
    text = "".join(out)
    for rx, rep in _RE_COMMON:
        text = rx.sub(rep, text)
    for rx, rep in (_RE_DE if lang == "de" else _RE_EN):
        text = rx.sub(rep, text)
    return text


# ── inline markup ────────────────────────────────────────────────────────────
_RE_GAP = re.compile(r"\[\[(.*?)\]\]")
_RE_CHOICE = re.compile(r"\{\?([^{}]*)\}")
_RE_DE_SPAN = re.compile(r"\{de:([^{}]*)\}")
_RE_ART = re.compile(r"\{(der|die|das) ([^{}]+)\}")
_RE_ART2 = re.compile(r"\{(m|f|n|p|pl):([^{}]+)\}")
_RE_PAGE = re.compile(r"\{S:([^{}]+)\}")
_RE_LINE = re.compile(r"\{z:([^{}]+)\}")
_RE_ANCHOR = re.compile(r"\{#([A-Za-z0-9_-]+)\}")
_RE_MARK = re.compile(r"==(.+?)==")
_RE_BOLD = re.compile(r"\*\*(.+?)\*\*")
_RE_ITAL = re.compile(r"(?<![*\w])\*(?!\*)(.+?)(?<!\*)\*(?![*\w])")
_RE_STRIKE = re.compile(r"~~(.+?)~~")
_RE_ANY_TOKEN = re.compile(r"\[\[.*?\]\]|\{[^{}]*\}")
_GENDER = {"m": "der", "f": "die", "n": "das", "p": "pl", "pl": "pl"}


def gap_width_mm(answer: str) -> float:
    """Width of a write-in gap: room for the longest accepted answer in handwriting."""
    longest = max((len(a.strip()) for a in answer.split(" / ")), default=4)
    return round(min(60.0, max(13.0, 8.0 + 2.15 * longest)), 1)


@dataclass
class Collected:
    """What the inline pass found inside one task: answers and line anchors."""
    answers: list[tuple[int, str]] = field(default_factory=list)   # (item number, answer)
    item: int = 0
    fields: int = 0


@dataclass
class Inline:
    """Stateful inline renderer. One instance per build; `scope` changes per task."""
    lang: str                                       # edition language (en / tr)
    forms: bool = False
    page_ref: Optional[Callable[[str], Optional[tuple[str, str]]]] = None   # target → (label, href)
    line_ref: Optional[Callable[[str, str], Optional[str]]] = None          # (scope, anchor) → line number
    de_page_abbr: str = "S."
    de_line_abbr: str = "Z."
    scope: str = "x"                                # unique prefix for ids / form field names
    text_scope: str = "x"                           # the reading text line anchors belong to
    col: Collected = field(default_factory=Collected)
    unresolved: list[str] = field(default_factory=list)

    # -- scope handling ------------------------------------------------------
    def begin(self, scope: str) -> None:
        self.scope = scope
        self.col = Collected()

    def item(self, n: int) -> None:
        self.col.item = n

    # -- public API ----------------------------------------------------------
    def de(self, text: Optional[str]) -> str:
        """German text → HTML."""
        return self._render(text, "de")

    def ex(self, text: Optional[str]) -> str:
        """Explanation-language text → HTML."""
        return self._render(text, self.lang)

    def plain(self, text: Optional[str], lang: str = "de") -> str:
        """Visible plain text (gaps removed) — for bookmarks, alt text and the word index."""
        if not text:
            return ""
        t = _RE_GAP.sub("…", text)
        t = _RE_CHOICE.sub(lambda m: " / ".join(o.rstrip("*") for o in m.group(1).split("|")), t)
        t = _RE_DE_SPAN.sub(r"\1", t)
        t = _RE_ART.sub(r"\1 \2", t)
        t = _RE_ART2.sub(r"\2", t)
        t = _RE_ANY_TOKEN.sub("", t)
        t = re.sub(r"==|\*\*|~~|(?<!\w)\*|\*(?!\w)", "", t)
        return typo(t, lang).strip()

    # -- implementation ------------------------------------------------------
    def _render(self, text: Optional[str], lang: str) -> str:
        if not text:
            return ""
        t = html.escape(typo(str(text), lang), quote=False)
        t = _RE_GAP.sub(self._gap, t)
        t = _RE_CHOICE.sub(self._choice, t)
        t = _RE_DE_SPAN.sub(lambda m: f'<span class="dw" lang="de">{m.group(1)}</span>', t)
        t = _RE_ART.sub(lambda m: f'<span class="np"><span class="{m.group(1)}">{m.group(1)}</span> {m.group(2)}</span>', t)
        t = _RE_ART2.sub(self._art2, t)
        t = _RE_PAGE.sub(self._page, t)
        t = _RE_LINE.sub(self._line, t)
        t = _RE_ANCHOR.sub(lambda m: f'<span class="la" id="la-{self.text_scope}-{m.group(1)}"></span>', t)
        t = _RE_MARK.sub(self._mark, t)
        t = _RE_BOLD.sub(r"<b>\1</b>", t)
        t = _RE_STRIKE.sub(r'<span class="strike">\1</span>', t)
        t = _RE_ITAL.sub(r"<i>\1</i>", t)
        return t

    def _art2(self, m: re.Match) -> str:
        cls = _GENDER[m.group(1)]
        first, _, rest = m.group(2).partition(" ")
        return f'<span class="np"><span class="{cls}">{first}</span> {rest}</span>'

    @staticmethod
    def _mark(m: re.Match) -> str:
        """==x== → highlight. Inside a word (Fenster==n==) the highlight must not reach back over the letter before it."""
        before = m.string[m.start() - 1] if m.start() else " "
        joined = not (before.isspace() or before in ">\u00a0\u202f")
        return f'<mark class="j">{m.group(1)}</mark>' if joined else f"<mark>{m.group(1)}</mark>"

    def _gap(self, m: re.Match) -> str:
        answer, _, hint = m.group(1).partition("|")
        answer = html.unescape(answer).strip()
        self.col.answers.append((self.col.item, answer))
        self.col.fields += 1
        width = gap_width_mm(answer)
        hint_html = f' <span class="hint">({hint.strip()})</span>' if hint.strip() else ""
        if self.forms:
            name = f"{self.scope}-g{self.col.fields}"
            return (f'<input class="gap" type="text" name="{name}" aria-label="{name}" '
                    f'style="width:{width}mm">{hint_html}')
        return f'<span class="gap" style="width:{width}mm"></span>{hint_html}'

    def _choice(self, m: re.Match) -> str:
        opts = [o.strip() for o in m.group(1).split("|")]
        right = [o.rstrip("*").strip() for o in opts if o.endswith("*")]
        self.col.answers.append((self.col.item, " / ".join(right)))
        out = []
        for o in opts:
            label = o.rstrip("*").strip()
            self.col.fields += 1
            if self.forms:
                name = f"{self.scope}-c{self.col.fields}"
                box = f'<input class="box" type="checkbox" name="{name}" aria-label="{label}">'
            else:
                box = '<span class="box"></span>'
            out.append(f'<span class="ich">{box}{label}</span>')
        return '<span class="ichs">' + "".join(out) + "</span>"

    def _page(self, m: re.Match) -> str:
        target = m.group(1).strip()
        res = self.page_ref(target) if self.page_ref else None
        if not res:
            self.unresolved.append(f"page reference {{S:{target}}}")
            return f'<span class="xr">{self.de_page_abbr}{NNBSP}000</span>'
        label, href = res
        text = f"{self.de_page_abbr}{NNBSP}{label}"
        if href:
            return f'<a class="xr" href="{href}">{text}</a>'
        return f'<span class="xr">{text}</span>'

    def _line(self, m: re.Match) -> str:
        spec = m.group(1).strip()
        parts = spec.split("-") if "-" in spec else [spec]
        nums = []
        for p in parts:
            n = self.line_ref(self.text_scope, p) if self.line_ref else None
            nums.append(n)
        if any(n is None for n in nums):
            if self.line_ref is not None:
                self.unresolved.append(f"line reference {{z:{spec}}}")
            label = "00–00" if len(nums) > 1 else "00"
        else:
            label = "–".join(str(n) for n in nums) if len(set(nums)) > 1 else str(nums[0])
        return f'<span class="zr">{self.de_line_abbr}{NNBSP}{label}</span>'


def german_sort_key(word: str) -> str:
    """Dictionary order as in German word lists: ä = a, ö = o, ü = u, ß = ss, case-insensitive."""
    w = word.lower().replace("|", "")
    for a, b in (("ä", "a"), ("ö", "o"), ("ü", "u"), ("ß", "ss"), ("é", "e"), ("ı", "i")):
        w = w.replace(a, b)
    return re.sub(r"[^a-z0-9 ]", "", w)


_UMLAUT = {"a": "ä", "o": "ö", "u": "ü", "A": "Ä", "O": "Ö", "U": "Ü"}


def plural_form(noun: str, notation: str) -> Optional[str]:
    """Derive the plural word from the series notation ("¨-er", "-n", "-", "-s" …)."""
    n = (notation or "").strip()
    if not n or n.lower().strip("().") in ("pl", "sg"):
        return noun if n.lower().strip("().") == "pl" else None
    if not re.fullmatch(r"¨?-?[a-zäöü]*", n):
        return None
    umlaut = n.startswith("¨")
    suffix = n.lstrip("¨").lstrip("-")
    stem = noun
    if umlaut:
        # the last a / o / u (or au) of the stem takes the umlaut
        m = list(re.finditer(r"au|[aouAOU]", stem))
        if m:
            last = m[-1]
            seg = last.group(0)
            rep = "äu" if seg == "au" else _UMLAUT[seg]
            stem = stem[:last.start()] + rep + stem[last.end():]
    return stem + suffix
