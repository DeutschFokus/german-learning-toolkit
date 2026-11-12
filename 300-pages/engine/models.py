"""Typed content model (pydantic v2).

One YAML file per chapter is parsed into these classes. Nothing in here knows
about layout: a block says *what* it is (a dialogue, a gap text, a grammar box),
never where it goes or how it looks.

Text fields accept a small inline markup (see engine/markup.py):
    [[Antwort]]  [[Antwort|Hinweis]]      write-in gap, answer goes to the key
    {?den|dem*}                           inline tick choice, * marks the answer
    ==Endung==   **fett**   *kursiv*      highlight / bold / italic
    {der Tisch}  {f:der Wand}             noun phrase with coloured article
    {S:5.3a}     {z:anker}   {#anker}     page reference / line reference / line anchor
"""
from __future__ import annotations

from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, RootModel, model_validator

# Filled by the loader from series.yaml before any content is parsed.
LANGS: list[str] = ["en", "tr"]

Skill = Literal["hoeren", "lesen", "schreiben", "sprechen", "partner", "grammatik"]
SectionId = Literal["auftakt", "wortschatz", "hauptteil", "vertiefung", "abschlusstest", "rueckblick"]
NoteKind = Literal["tipp", "wort", "landeskunde", "sogehts"]


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Loc(RootModel[dict[str, str]]):
    """A string in every explanation language: {en: …, tr: …}."""

    @model_validator(mode="after")
    def _complete(self):
        missing = [lang for lang in LANGS if not str(self.root.get(lang, "")).strip()]
        if missing:
            raise ValueError(f"missing translation ({', '.join(missing)})")
        unknown = [k for k in self.root if k not in LANGS]
        if unknown:
            raise ValueError(f"unknown language key {unknown}; allowed: {LANGS}")
        return self

    def __getitem__(self, lang: str) -> str:
        return self.root[lang]


class Bi(RootModel[dict[str, str]]):
    """German text plus its explanation: {de: …, en: …, tr: …}."""

    @model_validator(mode="after")
    def _complete(self):
        if not str(self.root.get("de", "")).strip():
            raise ValueError("missing German text (de)")
        missing = [lang for lang in LANGS if not str(self.root.get(lang, "")).strip()]
        if missing:
            raise ValueError(f"missing translation ({', '.join(missing)})")
        unknown = [k for k in self.root if k not in LANGS + ["de"]]
        if unknown:
            raise ValueError(f"unknown language key {unknown}")
        return self

    def __getitem__(self, lang: str) -> str:
        return self.root[lang]

    @property
    def de(self) -> str:
        return self.root["de"]


# ── vocabulary ───────────────────────────────────────────────────────────────
class Vocab(Strict):
    """One entry of the chapter vocabulary.

    Nouns need `article` and `plural`; everything needs a translation in every language.
      {id: bad, de: Bad, article: das, plural: "¨-er", en: bathroom, tr: banyo}
      {id: nebenkosten, de: Nebenkosten, article: die, plural: Pl., en: …, tr: …}   plural only
      {id: muell, de: Müll, article: der, plural: Sg., en: …, tr: …}                no plural
      {id: einziehen, de: einziehen, sep: ein|ziehen, perfekt: ist eingezogen, en: …, tr: …}
    """
    type: Literal["vocab"] = "vocab"
    id: str
    de: str
    pos: Optional[Literal["noun", "verb", "adj", "adv", "phrase", "other"]] = None
    article: Optional[Literal["der", "die", "das"]] = None
    plural: Optional[str] = None
    plural_form: Optional[str] = None          # only if the plural cannot be derived from the notation
    sep: Optional[str] = None                  # separable verbs: ein|ziehen
    perfekt: Optional[str] = None              # ist eingezogen
    forms: list[str] = Field(default_factory=list)   # extra forms to find the word on other pages
    en: Optional[str] = None
    tr: Optional[str] = None
    model_config = ConfigDict(extra="allow")   # further languages (es, ar …) are plain extra keys

    @property
    def is_noun(self) -> bool:
        return self.pos == "noun" or (self.pos is None and (self.article is not None or self.plural is not None))

    @property
    def plural_only(self) -> bool:
        return (self.plural or "").strip().lower().strip("().") == "pl"

    @property
    def singular_only(self) -> bool:
        return (self.plural or "").strip().lower().strip("().") == "sg"

    def translation(self, lang: str) -> str:
        return getattr(self, lang, None) or (self.model_extra or {}).get(lang) or ""

    @property
    def gender_class(self) -> str:
        if self.plural_only:
            return "pl"
        return self.article or ""

    def notation(self) -> tuple[str, str, str]:
        """(article, headword, suffix) in the series notation.

        das Bad, ¨-er · der Keller, - · die Nebenkosten (Pl.) · der Müll (Sg.) · einziehen (ist eingezogen)
        """
        if self.is_noun:
            if self.plural_only:
                return self.article or "die", self.de, " (Pl.)"
            if self.singular_only:
                return self.article or "", self.de, " (Sg.)"
            return self.article or "", self.de, f", {self.plural}" if self.plural else ""
        if self.perfekt:
            return "", self.de, f" ({self.perfekt})"
        return "", self.de, ""


# ── small shared pieces ──────────────────────────────────────────────────────
class Turn(Strict):
    speaker: str
    text: str


class Transcript(Strict):
    type: Literal["transcript"] = "transcript"
    track: Optional[str] = None            # only for stand-alone transcripts
    turns: list[Turn] = Field(default_factory=list)
    text: Optional[str] = None


class Audio(Strict):
    type: Literal["audio"] = "audio"
    track: str                             # "5.03" — must match answer key and transcript
    title: str
    duration: str                          # "0:52"
    transcript: Optional[Transcript] = None
    transcript_from_body: bool = False     # the printed dialogue of this task is the transcript


class Answer(Strict):
    type: Literal["answer"] = "answer"
    task: Optional[str] = None             # only for stand-alone answers: "5.2d"
    text: Optional[str] = None             # the key (German, markup allowed)
    model: Optional[str] = None            # one possible answer for free writing / speaking
    open: bool = False                     # individual answer, nothing to check
    note: Optional[Loc] = None             # a short explanation in the edition language


class WordHelp(Strict):
    de: str
    en: Optional[str] = None
    tr: Optional[str] = None
    model_config = ConfigDict(extra="allow")

    @model_validator(mode="after")
    def _complete(self):
        missing = [lang for lang in LANGS if not (getattr(self, lang, None) or (self.model_extra or {}).get(lang))]
        if missing:
            raise ValueError(f"missing translation ({', '.join(missing)})")
        return self

    def translation(self, lang: str) -> str:
        return getattr(self, lang, None) or (self.model_extra or {}).get(lang) or ""


class MarginNote(Strict):
    type: Literal["margin_note"] = "margin_note"
    kind: NoteKind
    text: Optional[Loc] = None             # explanation-language text
    words: list[str] = Field(default_factory=list)       # vocab ids → "Wort translation"
    entries: list[WordHelp] = Field(default_factory=list)  # ad-hoc word help

    @model_validator(mode="after")
    def _has_content(self):
        if not (self.text or self.words or self.entries):
            raise ValueError("margin note is empty: give text, words or entries")
        return self


class Marker(Strict):
    n: int
    x: float        # position on the picture in per cent of its width
    y: float


class Image(Strict):
    """An illustration slot. `description` is the brief for the illustrator / image model
    and doubles as alternative text; `src` is filled in once the artwork exists."""
    type: Literal["image"] = "image"
    id: str
    description: str
    alt: Optional[Loc] = None
    format: Literal["wide", "square", "tall", "banner", "strip"] = "wide"
    src: Optional[str] = None
    focus: float = 50                         # which part stays visible when the slot crops the picture: 0 = top, 100 = bottom
    markers: list[Marker] = Field(default_factory=list)


# ── exercise and input blocks ────────────────────────────────────────────────
class Dialogue(Strict):
    type: Literal["dialogue"]
    turns: list[Turn]


class TextPart(Strict):
    label: Optional[str] = None
    title: Optional[str] = None
    text: str
    author: Optional[str] = None


class ReadingText(Strict):
    """A text to read. `genre` picks the typographic costume, nothing else."""
    type: Literal["reading_text"]
    id: Optional[str] = None
    genre: Literal["email", "notice", "listing", "article", "chat", "note", "plain"] = "plain"
    title: Optional[str] = None
    kicker: Optional[str] = None
    meta: dict[str, str] = Field(default_factory=dict)   # email: von / an / betreff
    text: Optional[str] = None                           # paragraphs separated by a blank line
    parts: list[TextPart] = Field(default_factory=list)  # several short texts (listings, notes)
    turns: list[Turn] = Field(default_factory=list)      # chat
    line_numbers: bool = True

    @model_validator(mode="after")
    def _has_text(self):
        if not (self.text or self.parts or self.turns):
            raise ValueError("reading_text needs text, parts or turns")
        return self


class GrammarBox(Strict):
    type: Literal["grammar_box"]
    title: str
    head: list[str] = Field(default_factory=list)
    rows: list[list[str]] = Field(default_factory=list)
    first_col_head: bool = False
    lines: list[str] = Field(default_factory=list)       # example sentences below the table
    rule: Optional[Loc] = None
    note: Optional[str] = None                           # extra German line (e.g. in + dem = im)


class TypicalMistake(Strict):
    type: Literal["typical_mistake"]
    wrong: str
    right: str            # mark the corrected part with ==…==
    why: Loc


class GapText(Strict):
    """Sentences or a running text with [[gaps]] and/or {?inline|choices*}."""
    type: Literal["gap_text"]
    items: list[str] = Field(default_factory=list)
    text: Optional[str] = None
    bank: Union[bool, list[str]] = False      # true = build the word bank from the answers
    compact: bool = False                     # short items → several per row
    example: Optional[str] = None             # a solved first item, shown in handwriting

    @model_validator(mode="after")
    def _has_content(self):
        if not (self.items or self.text):
            raise ValueError("gap_text needs items or text")
        return self


class TFItem(Strict):
    text: str
    answer: bool


class TrueFalse(Strict):
    type: Literal["true_false"]
    items: list[TFItem]


class MCItem(Strict):
    q: str
    options: list[str]
    answer: Literal["A", "B", "C", "D"]


class MultipleChoice(Strict):
    type: Literal["multiple_choice"]
    items: list[MCItem]

    @model_validator(mode="after")
    def _answers_in_range(self):
        for i, it in enumerate(self.items, 1):
            if "ABCD".index(it.answer) >= len(it.options):
                raise ValueError(f"item {i}: answer {it.answer} but only {len(it.options)} options")
        return self


class Matching(Strict):
    type: Literal["matching"]
    left: list[str]
    right: list[str]
    answer: list[str]          # one letter per left item: [C, E, D, A, B]

    @model_validator(mode="after")
    def _consistent(self):
        if len(self.answer) != len(self.left):
            raise ValueError("matching: one answer letter per left item is required")
        letters = "ABCDEFGHIJ"[:len(self.right)]
        bad = [a for a in self.answer if a not in letters]
        if bad:
            raise ValueError(f"matching: answer letters {bad} do not exist on the right side")
        return self


class WriteLines(Strict):
    type: Literal["write_lines"]
    lines: int = 4
    model: Optional[str] = None                 # shown in handwriting on the first lines
    prompts: list[str] = Field(default_factory=list)
    grow: bool = True                           # may take extra lines if the page has room


class SBItem(Strict):
    given: str
    answer: str


class SentenceBuild(Strict):
    """Build or transform a sentence: prompt on top, one write-in line below."""
    type: Literal["sentence_build"]
    items: list[SBItem]
    example: Optional[SBItem] = None


class TableFill(Strict):
    type: Literal["table_fill"]
    head: list[str] = Field(default_factory=list)
    rows: list[list[str]]
    first_col_head: bool = True


class OOItem(Strict):
    words: list[str]
    answer: str


class OddOneOut(Strict):
    type: Literal["odd_one_out"]
    items: list[OOItem]

    @model_validator(mode="after")
    def _answer_in_words(self):
        for i, it in enumerate(self.items, 1):
            if it.answer not in it.words:
                raise ValueError(f"odd_one_out item {i}: answer '{it.answer}' is not one of the words")
        return self


class SortTable(Strict):
    """Sort words into columns."""
    type: Literal["sort_table"]
    columns: list[str]
    words: list[str]
    answer: list[list[str]]          # one list per column
    rows: int = 3


class PhraseGroup(Strict):
    title: str
    items: list[Bi]


class Phrases(Strict):
    """Redemittel: useful phrases with translation."""
    type: Literal["phrases"]
    title: Optional[str] = None
    groups: list[PhraseGroup]


class RoleCard(Strict):
    label: str
    title: str
    points: list[str]


class RoleCards(Strict):
    type: Literal["role_cards"]
    cards: list[RoleCard]


class Bubbles(Strict):
    """Speech prompts shown as bubbles."""
    type: Literal["bubbles"]
    items: list[str]


class WordBank(Strict):
    type: Literal["word_bank"]
    items: list[str]


class GameGrid(Strict):
    type: Literal["game_grid"]
    cells: list[str]


class Paragraph(Strict):
    type: Literal["text"]
    de: Optional[str] = None
    expl: Optional[Loc] = None


class PictureDictionary(Strict):
    """A picture with numbered markers and the matching numbered word list."""
    type: Literal["picture_dictionary"]
    image: Image
    items: list[str]                 # vocab ids, in marker order


class SelfEval(Strict):
    type: Literal["self_eval"]
    items: list[Bi]


class PageBreak(Strict):
    """Editorial page break, like in a manuscript. Rarely needed."""
    type: Literal["page_break"]


BodyBlock = Annotated[
    Union[Dialogue, ReadingText, GrammarBox, TypicalMistake, GapText, TrueFalse, MultipleChoice, Matching,
          WriteLines, SentenceBuild, TableFill, OddOneOut, SortTable, Phrases, RoleCards, Bubbles, WordBank,
          GameGrid, Paragraph, PictureDictionary, SelfEval, Image],
    Field(discriminator="type")]


class Task(Strict):
    type: Literal["task"]
    id: str                                   # the letter: a, b, c …
    skills: list[Skill]
    rubric: Bi
    points: Optional[int] = None
    body: list[BodyBlock] = Field(default_factory=list)
    notes: list[MarginNote] = Field(default_factory=list)
    audio: Optional[Audio] = None
    answer: Optional[Answer] = None
    words: list[str] = Field(default_factory=list)       # vocab ids that are new in this task
    explain: Optional[bool] = None            # force / suppress the explanation line

    @model_validator(mode="after")
    def _checks(self):
        if not self.skills:
            raise ValueError("task needs at least one skill icon")
        if not (len(self.id) == 1 and self.id.isalpha() and self.id.islower()):
            raise ValueError(f"task id must be one lowercase letter, got '{self.id}'")
        return self


class Boxed(Strict):
    """A stand-alone block between tasks (grammar box, mistake box, picture …) with optional notes."""
    type: Literal["box"]
    body: list[BodyBlock]
    notes: list[MarginNote] = Field(default_factory=list)
    words: list[str] = Field(default_factory=list)


TopBlock = Annotated[Union[Task, Boxed, PageBreak], Field(discriminator="type")]


class Teil(Strict):
    nr: int
    section: SectionId
    title: str
    subtitle: Loc
    blocks: list[TopBlock]


class CanDo(Strict):
    type: Literal["can_do"] = "can_do"
    de: str
    en: Optional[str] = None
    tr: Optional[str] = None
    ref: Optional[str] = None                 # where to look again: a Teil ("5.4") or task ("5.4c")
    model_config = ConfigDict(extra="allow")

    @model_validator(mode="after")
    def _complete(self):
        missing = [lang for lang in LANGS if not (getattr(self, lang, None) or (self.model_extra or {}).get(lang))]
        if missing:
            raise ValueError(f"missing translation ({', '.join(missing)})")
        return self

    def translation(self, lang: str) -> str:
        return getattr(self, lang, None) or (self.model_extra or {}).get(lang) or ""


class Uebersicht(Strict):
    grammar: list[BodyBlock]
    phrases: list[BodyBlock]


class Preview(Strict):
    title: str
    teaser: Bi
    points: list[Bi] = Field(default_factory=list)


class Chapter(Strict):
    type: Literal["chapter"]
    level: str
    number: int
    title: str
    subtitle: Loc
    goal: Bi
    can_do: list[CanDo]
    grammar: list[str]
    image: Image
    vocabulary: list[Vocab]
    teile: list[Teil]
    uebersicht: Uebersicht
    next: Optional[Preview] = None
    answers: list[Answer] = Field(default_factory=list)          # optional stand-alone answers
    transcripts: list[Transcript] = Field(default_factory=list)  # optional stand-alone transcripts

    @property
    def key(self) -> str:
        return str(self.number)


class StationTeil(Strict):
    nr: int
    title: str
    subtitle: Loc
    kind: Literal["review", "exam"] = "review"
    blocks: list[TopBlock]


class Station(Strict):
    """Zwischenstation: four pages of mixed revision plus a mini mock exam."""
    type: Literal["station"]
    level: str
    number: int
    title: str
    subtitle: Loc
    covers: list[int]
    intro: Bi
    vocabulary: list[Vocab] = Field(default_factory=list)
    teile: list[StationTeil]
    answers: list[Answer] = Field(default_factory=list)
    transcripts: list[Transcript] = Field(default_factory=list)

    @property
    def key(self) -> str:
        return f"Z{self.number}"


class OutlineChapter(Strict):
    number: int
    title: str
    subtitle: Loc
    grammar: list[str]


class OutlineStation(Strict):
    number: int
    subtitle: Loc


class Outline(Strict):
    """content/<level>/book.yaml — the plan of the whole book (used for the table of contents)."""
    level: str
    chapters: list[OutlineChapter]
    stations: list[OutlineStation]
