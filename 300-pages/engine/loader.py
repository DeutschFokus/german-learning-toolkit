"""Load content files and validate them before anything is rendered.

The build stops if validation reports an error:
missing article · missing plural · missing translation · duplicate task address ·
task without answer · answer without task · audio without transcript · …
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Optional, Union

from pydantic import ValidationError

from . import models as M
from .config import Config, load_yaml

_TRACK = re.compile(r"^(Z?\d+)\.(\d{2})$")
_AUTO_MARK = re.compile(r"\[\[.*?\]\]|\{\?[^{}]*\}")


@dataclass
class Issue:
    level: str          # "error" | "warning"
    where: str
    message: str

    def __str__(self) -> str:
        return f"{self.level.upper():7} {self.where}: {self.message}"


@dataclass
class TaskRef:
    address: str            # "5.2d"
    part_key: str           # "5" or "Z2"
    teil: int
    task: M.Task
    section: str
    answer: Optional[M.Answer] = None

    @property
    def anchor(self) -> str:
        return "t-" + self.address.replace(".", "-")


@dataclass
class Book:
    cfg: Config
    outline: M.Outline
    chapters: dict[int, M.Chapter] = field(default_factory=dict)
    stations: dict[int, M.Station] = field(default_factory=dict)
    issues: list[Issue] = field(default_factory=list)
    vocab: dict[str, M.Vocab] = field(default_factory=dict)
    vocab_owner: dict[str, str] = field(default_factory=dict)
    tasks: dict[str, TaskRef] = field(default_factory=dict)
    tracks: dict[str, tuple[TaskRef, M.Audio, M.Transcript]] = field(default_factory=dict)

    # -- iteration in book order ------------------------------------------------
    def parts(self) -> Iterator[Union[M.Chapter, M.Station]]:
        st = self.cfg.series["structure"]
        for n in range(1, st["chapters"] + 1):
            if n in self.chapters:
                yield self.chapters[n]
            if n in st["stations_after"]:
                k = st["stations_after"].index(n) + 1
                if k in self.stations:
                    yield self.stations[k]

    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.level == "error"]

    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.level == "warning"]

    def err(self, where: str, message: str) -> None:
        self.issues.append(Issue("error", where, message))

    def warn(self, where: str, message: str) -> None:
        self.issues.append(Issue("warning", where, message))


def _pydantic_issues(book: Book, path: Path, exc: ValidationError) -> None:
    for e in exc.errors():
        loc = ".".join(str(x) for x in e["loc"] if not (isinstance(x, str) and x in ("task", "box", "function-after")))
        msg = e["msg"].replace("Value error, ", "")
        if "translation" in msg:
            msg = msg  # already says "missing translation (tr)"
        book.err(f"{path.name} → {loc}", msg)


def content_dir(cfg: Config) -> Path:
    return cfg.root / "content" / cfg.level


def parse_selection(spec: Optional[str]) -> Optional[tuple[set[int], set[int]]]:
    """'5,Z2' or '1-4,z1' → ({5}, {2}). None = everything that exists."""
    if not spec:
        return None
    chapters: set[int] = set()
    stations: set[int] = set()
    for tok in spec.replace(" ", "").split(","):
        if not tok:
            continue
        if tok.lower().startswith("z"):
            stations.add(int(tok[1:]))
        elif "-" in tok:
            a, b = tok.split("-")
            chapters.update(range(int(a), int(b) + 1))
        else:
            chapters.add(int(tok))
    return chapters, stations


def load_book(cfg: Config, selection: Optional[str] = None) -> Book:
    M.LANGS[:] = cfg.langs
    cdir = content_dir(cfg)
    if not (cdir / "book.yaml").exists():
        raise SystemExit(f"No content for level {cfg.level}: {cdir / 'book.yaml'} is missing.")
    try:
        outline = M.Outline.model_validate(load_yaml(cdir / "book.yaml"))
    except ValidationError as exc:
        book = Book(cfg, M.Outline(level=cfg.level, chapters=[], stations=[]))
        _pydantic_issues(book, cdir / "book.yaml", exc)
        return book
    book = Book(cfg, outline)
    sel = parse_selection(selection)

    for path in sorted(cdir.glob("kapitel-*.yaml")):
        n = int(re.search(r"(\d+)", path.stem).group(1))
        if sel and n not in sel[0]:
            continue
        try:
            ch = M.Chapter.model_validate(load_yaml(path))
        except ValidationError as exc:
            _pydantic_issues(book, path, exc)
            continue
        if ch.number != n:
            book.err(path.name, f"file name says chapter {n}, content says {ch.number}")
        book.chapters[ch.number] = ch
    for path in sorted(cdir.glob("station-*.yaml")):
        n = int(re.search(r"(\d+)", path.stem).group(1))
        if sel and n not in sel[1]:
            continue
        try:
            st = M.Station.model_validate(load_yaml(path))
        except ValidationError as exc:
            _pydantic_issues(book, path, exc)
            continue
        book.stations[st.number] = st
    if sel:
        for n in sel[0] - set(book.chapters):
            if not any(i.where.startswith(f"kapitel-{n:02d}") for i in book.issues):
                book.err("selection", f"chapter {n} was requested but content/{cfg.level}/kapitel-{n:02d}.yaml does not exist")
        for n in sel[1] - set(book.stations):
            if not any(i.where.startswith(f"station-{n}") for i in book.issues):
                book.err("selection", f"station {n} was requested but content/{cfg.level}/station-{n}.yaml does not exist")
    validate(book)
    return book


# ── semantic validation ──────────────────────────────────────────────────────
def _strings(obj) -> Iterator[str]:
    """Every string inside a (nested) model — used to detect auto-answer markup."""
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, (list, tuple)):
        for x in obj:
            yield from _strings(x)
    elif isinstance(obj, dict):
        for x in obj.values():
            yield from _strings(x)
    elif hasattr(obj, "root"):
        yield from _strings(obj.root)
    elif hasattr(obj, "model_fields"):
        for name in type(obj).model_fields:
            yield from _strings(getattr(obj, name))


_AUTO_TYPES = (M.TrueFalse, M.MultipleChoice, M.Matching, M.SentenceBuild, M.OddOneOut, M.SortTable)


def has_auto_answer(task: M.Task) -> bool:
    for b in task.body:
        if isinstance(b, _AUTO_TYPES):
            return True
        if isinstance(b, (M.GapText, M.TableFill, M.GrammarBox, M.ReadingText)) and any(_AUTO_MARK.search(s) for s in _strings(b)):
            return True
    return False


def _speakers(obj) -> Iterator[str]:
    if isinstance(obj, M.Turn):
        yield obj.speaker
    elif isinstance(obj, (list, tuple)):
        for x in obj:
            yield from _speakers(x)
    elif hasattr(obj, "model_fields") and not hasattr(obj, "root"):
        for name in type(obj).model_fields:
            yield from _speakers(getattr(obj, name))


def _teile(part) -> list:
    return part.teile


def validate(book: Book) -> None:
    cfg = book.cfg
    cast = cfg.series["cast"]
    seq = [s["id"] for s in cfg.sections if s["id"] != "uebersicht"]

    for part in book.parts():
        key = part.key
        fname = f"kapitel-{part.number:02d}.yaml" if isinstance(part, M.Chapter) else f"station-{part.number}.yaml"
        if part.level != cfg.level:
            book.err(fname, f"level is '{part.level}' but the file lives in content/{cfg.level}/")

        # vocabulary ---------------------------------------------------------
        for v in part.vocabulary:
            where = f"{fname} → vocabulary '{v.id}'"
            if v.id in book.vocab:
                book.err(where, f"duplicate vocabulary id (also in part {book.vocab_owner[v.id]})")
                continue
            book.vocab[v.id] = v
            book.vocab_owner[v.id] = key
            looks_like_noun = v.pos is None and v.de[:1].isupper() and " " not in v.de.strip()
            if (v.is_noun or looks_like_noun) and v.pos in (None, "noun"):
                if not v.article:
                    book.err(where, f"missing article for noun '{v.de}'")
                if not v.plural:
                    book.err(where, f"missing plural for noun '{v.de}' (use '-', '¨-er', 'Pl.' or 'Sg.')")
            for lang in cfg.langs:
                if not v.translation(lang).strip():
                    book.err(where, f"missing translation ({lang}) for '{v.de}'")
            if v.sep and v.sep.replace("|", "") != v.de:
                book.err(where, f"sep '{v.sep}' does not spell '{v.de}'")

        # structure ----------------------------------------------------------
        teile = _teile(part)
        for i, t in enumerate(teile, 1):
            if t.nr != i:
                book.err(f"{fname} → Teil {t.nr}", f"Teile must be numbered 1, 2, 3 …; expected {i}")
        if isinstance(part, M.Chapter):
            order = [t.section for t in teile]
            dedup = [s for i, s in enumerate(order) if i == 0 or s != order[i - 1]]
            if dedup != seq:
                book.err(fname, f"sections must come in the order {' → '.join(seq)}; found {' → '.join(dedup)}")
            if len(part.can_do) < 3:
                book.warn(fname, "fewer than three can-do statements")
            for cd in part.can_do:
                if cd.ref and not re.fullmatch(rf"{part.number}\.\d+[a-z]?", cd.ref):
                    book.err(f"{fname} → can_do", f"ref '{cd.ref}' must look like '{part.number}.4' or '{part.number}.4c'")

        # tasks --------------------------------------------------------------
        standalone = {a.task: a for a in part.answers}
        for a in part.answers:
            if not a.task:
                book.err(f"{fname} → answers", "stand-alone answer without 'task' address")
        st_transcripts = {t.track: t for t in part.transcripts}
        seen_ids: set[str] = set()
        introduced: set[str] = set()
        for t in teile:
            section = getattr(t, "section", "station")
            for b in t.blocks:
                if isinstance(b, M.PageBreak):
                    continue
                for w in b.words:
                    if w not in {v.id for v in part.vocabulary}:
                        book.err(f"{fname} → Teil {t.nr}", f"word '{w}' is not in this file's vocabulary")
                    introduced.add(w)
                for sp in _speakers(b):
                    if sp not in cast:
                        book.err(f"{fname} → Teil {t.nr}", f"unknown speaker '{sp}' (not in series.yaml cast)")
                if isinstance(b, M.Boxed):
                    for n in b.notes:
                        for w in n.words:
                            if w not in {v.id for v in part.vocabulary}:
                                book.err(f"{fname} → Teil {t.nr}", f"margin note word '{w}' is not in the vocabulary")
                    continue
                task: M.Task = b
                address = f"{key}.{t.nr}{task.id}"
                where = f"{fname} → {address}"
                if address in book.tasks:
                    book.err(where, "duplicate task address")
                    continue
                ref = TaskRef(address, key, t.nr, task, section)
                book.tasks[address] = ref
                for n in task.notes:
                    for w in n.words:
                        if w not in {v.id for v in part.vocabulary}:
                            book.err(where, f"margin note word '{w}' is not in the vocabulary")
                # answer
                if task.answer and address in standalone:
                    book.err(where, "has both an inline answer and a stand-alone answer")
                ref.answer = task.answer or standalone.get(address)
                if ref.answer is None and not has_auto_answer(task):
                    book.err(where, "task without answer (add answer: {text|model|open} or use gaps/choices with solutions)")
                if ref.answer and not (ref.answer.text or ref.answer.model or ref.answer.open or has_auto_answer(task)):
                    book.err(where, "answer is empty (give text, model or open: true)")
                if section == "abschlusstest" and task.points is None:
                    book.err(where, "test tasks need points")
                # audio
                if task.audio:
                    au = task.audio
                    m = _TRACK.match(au.track)
                    if not m:
                        book.err(where, f"track '{au.track}' must look like '{key}.03'")
                    elif m.group(1) != key:
                        book.err(where, f"track '{au.track}' does not belong to part {key}")
                    if au.track in book.tracks:
                        book.err(where, f"duplicate track number {au.track}")
                    tr = au.transcript
                    if tr is None and au.transcript_from_body:
                        turns = [x for blk in task.body if isinstance(blk, M.Dialogue) for x in blk.turns]
                        if turns:
                            tr = M.Transcript(turns=turns)
                    if tr is None:
                        tr = st_transcripts.get(au.track)
                    if tr is None:
                        book.err(where, f"audio without transcript (track {au.track})")
                    else:
                        book.tracks[au.track] = (ref, au, tr)
                    if "hoeren" not in task.skills:
                        book.warn(where, "task has audio but no Hören icon")
                elif "hoeren" in task.skills:
                    book.warn(where, "Hören icon but no audio track")
        for addr in standalone:
            if addr and addr not in book.tasks:
                book.err(f"{fname} → answers", f"answer without task: '{addr}'")
        for track in st_transcripts:
            if track not in book.tracks:
                book.err(f"{fname} → transcripts", f"transcript without audio: track '{track}'")
        for v in part.vocabulary:
            if v.id not in introduced:
                book.warn(f"{fname} → vocabulary '{v.id}'", "word is never introduced by a task (it will not appear in a page footer)")

    # outline ----------------------------------------------------------------
    nums = [c.number for c in book.outline.chapters]
    if nums != list(range(1, cfg.series["structure"]["chapters"] + 1)):
        book.err("book.yaml", f"outline must list chapters 1–{cfg.series['structure']['chapters']} in order")
    for n, ch in book.chapters.items():
        oc = next((c for c in book.outline.chapters if c.number == n), None)
        if oc and oc.title != ch.title:
            book.err("book.yaml", f"chapter {n}: outline title '{oc.title}' ≠ content title '{ch.title}'")


def format_log(book: Book) -> str:
    errs, warns = book.errors(), book.warnings()
    lines = [f"Validation: {len(errs)} error(s), {len(warns)} warning(s)",
             f"  parts: {', '.join(p.key for p in book.parts()) or '–'} · tasks: {len(book.tasks)} · "
             f"vocabulary: {len(book.vocab)} · audio tracks: {len(book.tracks)}"]
    lines += [f"  {i}" for i in errs + warns]
    return "\n".join(lines)
