"""Content blocks → HTML fragments ("units").

A unit is the smallest thing the paginator moves around: a Teil header, a task,
a stand-alone box. While rendering, this module also collects everything that
is generated automatically: the answer key, line numbers, cross-references.
"""
from __future__ import annotations

import html
import math
import re
from dataclasses import dataclass, field
from typing import Optional

import jinja2

from . import art
from . import models as M
from .config import Config
from .loader import Book, TaskRef
from .markup import Inline, NNBSP

_TAGS = re.compile(r"<svg.*?</svg>|<[^>]+>", re.S)


def strip_tags(fragment: str) -> str:
    return html.unescape(_TAGS.sub(" ", fragment))


def esc(s: str) -> str:
    return html.escape(str(s), quote=False)


class View:
    """Attribute view of a dict for templates (so a key called `items` is not mistaken for dict.items)."""

    def __init__(self, data: dict):
        self.__dict__.update({k: to_view(v) for k, v in data.items()})


def to_view(obj):
    if isinstance(obj, dict):
        return View(obj)
    if isinstance(obj, list):
        return [to_view(x) for x in obj]
    return obj


class Macros:
    """Call Jinja macros with plain dicts: arguments are converted to views on the way in."""

    def __init__(self, module):
        self._m = module

    def __getattr__(self, name):
        macro = getattr(self._m, name)
        return lambda *args: str(macro(*[to_view(a) for a in args]))


@dataclass
class Unit:
    uid: str
    kind: str                       # teil | task | box | head | cando | total | next
    html: str
    part: str
    teil: int = 0
    section: str = ""
    words: list[str] = field(default_factory=list)
    address: str = ""
    grow_ids: list[str] = field(default_factory=list)
    keep_next: bool = False
    break_before: bool = False
    height: float = 0.0             # pt — set by the measure pass
    title: str = ""                 # bookmark text

    @property
    def text(self) -> str:
        return strip_tags(self.html)


@dataclass
class AnswerEntry:
    address: str
    anchor: str
    task_anchor: str
    part: str
    teil: int
    html: str


def make_env(cfg: Config) -> jinja2.Environment:
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(cfg.root / "engine" / "templates")),
        autoescape=False, trim_blocks=True, lstrip_blocks=True, undefined=jinja2.StrictUndefined)


class Renderer:
    def __init__(self, cfg: Config, book: Book):
        self.cfg, self.book = cfg, book
        self.forms = bool(cfg.flags.get("forms"))
        self.env = make_env(cfg)
        self.B = Macros(self.env.get_template("blocks.html.j2").module)
        self.inline = Inline(lang=cfg.lang, forms=self.forms, page_ref=self._page_ref, line_ref=self._line_ref,
                             de_page_abbr=cfg.de("page_abbr"), de_line_abbr=cfg.de("line_abbr"))
        self.cast = cfg.series["cast"]
        # registries filled by the layout passes -------------------------------
        self.page_of: dict[str, str] = {}             # anchor → folio label
        self.built: set[str] = set()                  # anchors that exist in this build
        self.line_of: dict[tuple[str, str], int] = {}
        self.text_geom: dict[str, list[tuple[float, int]]] = {}   # reading text → [(top pt, lines)]
        self.grow: dict[str, int] = {}                # elastic element id → steps it has grown
        self.elastic: dict[str, tuple[float, int]] = {}   # elastic element id → (step pt, max steps)
        self.model_rows: dict[str, int] = {}          # ruled area id → lines its handwritten model needs
        self.answers: dict[str, AnswerEntry] = {}
        self._ans: list[str] = []
        self._scope = "x"
        self._n = 0
        self._seen_types: set = set()
        self._grow_ids: list[str] = []

    # ── small helpers ────────────────────────────────────────────────────────
    def de(self, s) -> str:
        return self.inline.de(s)

    def ex(self, s) -> str:
        return self.inline.ex(self.cfg.t(s) if not isinstance(s, str) else s)

    def L(self, key: str) -> str:
        return esc(self.cfg.de(f"labels.{key}"))

    def icon(self, name: str, size: str = "5.2mm", title: Optional[str] = None, sw: float = 1.6) -> str:
        return art.icon(name, size, title or name, sw)

    def avatar(self, key: str, size: str = "8.6mm") -> str:
        self._n += 1
        return art.avatar(key, self.cast, size, uid=f"{self._scope}-{self._n}")

    def _fid(self, tag: str) -> str:
        self._n += 1
        return f"{self._scope}-{tag}{self._n}"

    def anchor_for(self, target: str) -> Optional[str]:
        """Resolve a reference target to a DOM anchor: 5.3a · 5.3 · 5.uebersicht · p120 · L:5.3a"""
        t = target.strip()
        if re.fullmatch(r"p?\d+", t):
            return "p-" + t.lstrip("p")
        m = re.fullmatch(r"(Z?\d+)\.(\d+)([a-z])", t)
        if m:
            return f"t-{m.group(1)}-{m.group(2)}-{m.group(3)}"
        m = re.fullmatch(r"(Z?\d+)\.(\d+)", t)
        if m:
            return f"teil-{m.group(1)}-{m.group(2)}"
        m = re.fullmatch(r"(Z?\d+)\.([a-z]+)", t)
        if m:
            return f"sec-{m.group(1)}-{m.group(2)}"
        m = re.fullmatch(r"(Z?\d+)", t)
        if m:
            return f"k-{m.group(1)}"
        return None

    def _page_ref(self, target: str):
        anchor = self.anchor_for(target)
        if not anchor or anchor not in self.page_of:
            return None
        return self.page_of[anchor], (f"#{anchor}" if anchor in self.built else "")

    def page_link(self, anchor: str, text: Optional[str] = None, cls: str = "xr") -> str:
        """'S. 104' as a live link (or plain text when the page is not part of this build)."""
        label = self.page_of.get(anchor)
        if label is None:
            return f'<span class="{cls}">{text or "…"}</span>'
        t = text if text is not None else f"{self.cfg.de('page_abbr')}{NNBSP}{label}"
        if anchor in self.built:
            return f'<a class="{cls}" href="#{anchor}">{t}</a>'
        return f'<span class="{cls}">{t}</span>'

    def _line_ref(self, scope: str, anchor: str):
        return self.line_of.get((scope, anchor))

    # ── vocabulary views ─────────────────────────────────────────────────────
    def word_view(self, v: M.Vocab, sep: bool = False) -> dict:
        article, head, suffix = v.notation()
        word = (v.sep if (sep and v.sep) else head)
        return {"id": v.id, "article": article, "cls": v.gender_class, "word": esc(word), "suffix": esc(suffix),
                "tr": esc(v.translation(self.cfg.lang))}

    # ── margin ───────────────────────────────────────────────────────────────
    def margin(self, notes: list[M.MarginNote], audio: Optional[M.Audio] = None) -> str:
        out = []
        if audio:
            url = self.cfg.audio_url(audio.track)
            out.append(self.B.audio({
                "href": esc(url), "qr": art.qr_svg(url, f"QR-Code: Track {audio.track}", self.cfg.series["colors"]["ink"]),
                "label": self.L("track"), "track": esc(audio.track), "duration": esc(audio.duration),
                "icon": self.icon("hoeren", "3.6mm", self.cfg.de("labels.skills.hoeren"))}))
        for n in notes:
            entries = []
            for wid in n.words:
                v = self.book.vocab.get(wid)
                if v is None:
                    continue
                article, head, suffix = v.notation()
                art_html = f'<span class="{v.gender_class}">{article}</span> ' if article else ""
                suf = esc(suffix) if v.is_noun else ""
                entries.append({"de": f"{art_html}{esc(head)}{suf}", "tr": esc(v.translation(self.cfg.lang))})
            for e in n.entries:
                entries.append({"de": self.de(e.de), "tr": self.inline.ex(e.translation(self.cfg.lang))})
            out.append(self.B.note({
                "kind": n.kind, "label": esc(self.cfg.de(f"labels.notes.{n.kind}")),
                "icon": self.icon(n.kind, "4.2mm", self.cfg.de(f"labels.notes.{n.kind}")),
                "text": self.ex(n.text) if n.text else "", "entries": entries, "lang": self.cfg.lang}))
        return "".join(str(x) for x in out)

    # ── body blocks ──────────────────────────────────────────────────────────
    def body(self, blocks: list) -> str:
        return "".join(self.block(b) for b in blocks)

    def block(self, b) -> str:
        fn = getattr(self, "_b_" + b.type)
        return str(fn(b))

    def _numbered(self, pairs: list[tuple[int, str]]) -> str:
        """Group inline answers by item number: 1 schließt · schreibe  2 ist · nehmen"""
        groups: dict[int, list[str]] = {}
        for n, a in pairs:
            groups.setdefault(n, []).append(esc(a))
        if list(groups) == [0]:
            return ' <span class="sep">·</span> '.join(groups[0])
        return " &nbsp; ".join(f'<b class="n">{n}</b> ' + ' <span class="sep">·</span> '.join(v) for n, v in groups.items())

    def _b_dialogue(self, b: M.Dialogue):
        return self.B.dialogue({"turns": [
            {"avatar": self.avatar(t.speaker), "name": esc(self.cast[t.speaker]["name"]), "text": self.de(t.text)}
            for t in b.turns]})

    def _b_reading_text(self, b: M.ReadingText):
        if b.genre == "chat" or b.turns:
            me = b.turns[1].speaker if len(b.turns) > 1 else None
            other = next((t.speaker for t in b.turns if t.speaker != me), b.turns[0].speaker)
            return self.B.chat({"contact": esc(self.cast[other]["name"]), "contact_avatar": self.avatar(other, "6.4mm"), "msgs": [
                {"avatar": self.avatar(t.speaker, "7mm"), "text": self.de(t.text), "me": t.speaker == me}
                for t in b.turns]})
        if b.parts:
            kind = "listing" if b.genre == "listing" else "notecards"
            n = 1 if (kind == "listing" or any(len(p.text) > 90 for p in b.parts)) else min(3, len(b.parts))
            return self.B.cards({"kind": kind, "n": n, "cards": [
                {"label": esc(p.label or ""), "title": self.de(p.title) if p.title else "", "text": self.de(p.text),
                 "author": self.de(p.author) if p.author else ""} for p in b.parts]})
        rid = f"rt-{self._scope}-{b.id or self._fid('r')}"
        if b.line_numbers:
            self.inline.text_scope = rid
        paras = []
        raw = [p.strip() for p in re.split(r"\n\s*\n", (b.text or "").strip()) if p.strip()]
        for i, p in enumerate(raw):
            lines = [self.de(x) for x in p.split("\n")]
            paras.append({"id": f"{rid}-p{i}", "html": "<br>".join(lines)})
        numbers = []
        if b.line_numbers and rid in self.text_geom:
            count = 0
            for top, n in self.text_geom[rid]:
                for k in range(n):
                    count += 1
                    if count % 5 == 0:
                        numbers.append((count, round(top + k * self.cfg.bl, 2)))
        meta = [(esc(self.cfg.de(f"labels.meta.{k}") if self.cfg.de.has(f"labels.meta.{k}") else k), self.de(v)) for k, v in b.meta.items()]
        return self.B.reading({"genre": b.genre, "nonum": not b.line_numbers, "meta": meta,
                               "title": self.de(b.title) if b.title else "", "kicker": self.de(b.kicker) if b.kicker else "",
                               "paras": paras, "rid": rid, "numbers": numbers})

    def _b_grammar_box(self, b: M.GrammarBox):
        before = len(self.inline.col.answers)
        v = {"title": self.de(b.title), "label": self.L("grammar"), "icon": self.icon("grammatik", "4.6mm", self.cfg.de("labels.grammar")),
             "head": [self.de(h) for h in b.head], "rows": [[self.de(c) for c in r] for r in b.rows],
             "first_col_head": b.first_col_head, "lines": [self.de(x) for x in b.lines],
             "note": self.de(b.note) if b.note else "", "rule": self.ex(b.rule) if b.rule else "", "lang": self.cfg.lang}
        new = self.inline.col.answers[before:]
        if new:
            self._ans.append(self._numbered([(0, a) for _, a in new]))
        return self.B.grammar(v)

    def _b_typical_mistake(self, b: M.TypicalMistake):
        return self.B.mistake({"label": self.L("typical_mistake"), "icon": self.icon("fehler", "4.4mm", self.cfg.de("labels.typical_mistake")),
                               "cross": self.icon("cross", "3mm", "falsch", 2.4), "check": self.icon("check", "3mm", "richtig", 2.6),
                               "wrong": self.de(b.wrong), "right": self.de(b.right), "why": self.ex(b.why), "lang": self.cfg.lang})

    def _b_gap_text(self, b: M.GapText):
        start = len(self.inline.col.answers)
        items = []
        for i, it in enumerate(b.items, 1):
            self.inline.item(i)
            items.append(self.de(it))
        text = ""
        if b.text:
            self.inline.item(0)
            text = self.de(b.text)
        self.inline.item(0)
        new = self.inline.col.answers[start:]
        bank = []
        if b.bank is True:
            words = sorted({a.split(" / ")[0] for _, a in new}, key=lambda w: (len(w) % 3, w.lower()))
            bank = [esc(w) for w in words]
        elif b.bank:
            bank = [self.de(w) for w in b.bank]
        example = ""
        if b.example:
            example = re.sub(r"\[\[(.*?)\]\]", lambda m: f'<span class="gap filled" style="width:{max(13, 8 + 2.15 * len(m.group(1)))}mm"><span class="hw">{esc(m.group(1))}</span></span>', esc(b.example))
        if new:
            self._ans.append(self._numbered(new))
        return self.B.gaptext({"bank": bank, "items": items, "text": text, "compact": b.compact, "example": example})

    def _b_true_false(self, b: M.TrueFalse):
        t, f = self.cfg.de("labels.true"), self.cfg.de("labels.false")
        self._ans.append(" &nbsp; ".join(f'<b class="n">{i}</b> {t if it.answer else f}' for i, it in enumerate(b.items, 1)))
        return self.B.truefalse({"t": t, "f": f, "forms": self.forms,
                                 "items": [{"text": self.de(it.text), "name": self._fid("tf")} for it in b.items]})

    def _b_multiple_choice(self, b: M.MultipleChoice):
        items = []
        for it in b.items:
            items.append({"q": self.de(it.q), "stack": any(len(self.inline.plain(o)) > 38 for o in it.options),
                          "opts": [("ABCD"[i], self.de(o), self._fid("mc")) for i, o in enumerate(it.options)]})
        if len(b.items) == 1:
            self._ans.append(b.items[0].answer)
        else:
            self._ans.append(" &nbsp; ".join(f'<b class="n">{i}</b> {it.answer}' for i, it in enumerate(b.items, 1)))
        return self.B.mc({"items": items, "forms": self.forms})

    def _b_matching(self, b: M.Matching):
        self._ans.append(" &nbsp; ".join(f'<b class="n">{i}</b> {a}' for i, a in enumerate(b.answer, 1)))
        return self.B.matching({"left": [{"text": self.de(x), "name": self._fid("m")} for x in b.left],
                                "right": [("ABCDEFGHIJ"[i], self.de(x)) for i, x in enumerate(b.right)], "forms": self.forms})

    def ruled(self, model: str = "", n: int = 1, grow: bool = False) -> str:
        """A ruled write-in area. `model` (already HTML) is shown in handwriting on the first lines."""
        wid = f"wl-{self._fid('w')}"
        if grow:
            self._grow_ids.append(wid)
            self.elastic[wid] = (float(self.cfg.lv["type"]["write_line"]) * self.cfg.bl, 3)
            n += self.grow.get(wid, 0)
        model_rows = 0
        if model:
            model_rows = self.model_rows.get(wid) or max(1, math.ceil(len(strip_tags(model)) / 50))
        return self.B.ruled({"id": wid, "model": model, "rows": model_rows + n, "n": n, "model_rows": model_rows, "forms": self.forms})

    def _b_write_lines(self, b: M.WriteLines):
        ruled = self.ruled(self.de(b.model) if b.model else "", b.lines, b.grow)
        return self.B.lines({"prompts": [self.de(p) for p in b.prompts], "model": bool(b.model),
                             "label": self.L("example"), "hint": esc(self.cfg.ui("labels.example_hint")), "lang": self.cfg.lang,
                             "ruled": ruled})

    def _b_sentence_build(self, b: M.SentenceBuild):
        self._ans.append(" &nbsp; ".join(f'<b class="n">{i}</b> {self.de(it.answer)}' for i, it in enumerate(b.items, 1)))
        ex = {"given": self.de(b.example.given), "ruled": self.ruled(self.de(b.example.answer), 0)} if b.example else None
        return self.B.sentences({"example": ex, "label": "Bsp.",
                                 "items": [{"given": self.de(it.given), "ruled": self.ruled("", 1)} for it in b.items]})

    def _b_table_fill(self, b: M.TableFill):
        start = len(self.inline.col.answers)
        rows = []
        for ri, r in enumerate(b.rows, 1):
            self.inline.item(ri)
            cells = []
            for c in r:
                has_gap = "[[" in c
                only_gap = bool(re.fullmatch(r"\s*\[\[.*?\]\]\s*", c))
                cells.append({"html": self.de(c), "cls": "g1" if only_gap else ("" if has_gap or len(r) == 2 and not only_gap and "[[" in "".join(r) and not b.head and False else ("lbl" if not b.head else ""))})
            rows.append(cells)
        self.inline.item(0)
        new = self.inline.col.answers[start:]
        if new:
            self._ans.append(self._numbered(new))
        return self.B.tablefill({"head": [self.de(h) for h in b.head], "rows": rows})

    def _b_odd_one_out(self, b: M.OddOneOut):
        self._ans.append(" &nbsp; ".join(f'<b class="n">{i}</b> {esc(it.answer)}' for i, it in enumerate(b.items, 1)))
        sep = ' <span style="color:var(--faint);margin:0 2.2mm">–</span> '
        return self.B.oddone({"items": [sep.join(esc(w) for w in it.words) for it in b.items]})

    def _b_sort_table(self, b: M.SortTable):
        self._ans.append(" &nbsp; ".join(f"<b>{esc(c)}:</b> " + ", ".join(esc(w) for w in ws) for c, ws in zip(b.columns, b.answer)))
        return self.B.sorttable({"words": [self.de(w) for w in b.words], "columns": [self.de(c) for c in b.columns],
                                 "rows": b.rows, "forms": self.forms, "name": self._fid("st")})

    def _b_phrases(self, b: M.Phrases):
        return self.B.phrases({"title": self.de(b.title) if b.title else "", "label": self.L("phrases"),
                               "icon": self.icon("phrases", "4.6mm", self.cfg.de("labels.phrases")), "lang": self.cfg.lang,
                               "groups": [{"title": self.de(g.title), "items": [(self.de(i.de), self.ex(i[self.cfg.lang])) for i in g.items]}
                                          for g in b.groups]})

    def _b_role_cards(self, b: M.RoleCards):
        return self.B.roles({"cards": [{"label": esc(c.label), "title": self.de(c.title), "points": [self.de(p) for p in c.points]} for c in b.cards]})

    def _b_bubbles(self, b: M.Bubbles):
        return self.B.bubbles({"items": [self.de(x) for x in b.items]})

    def _b_word_bank(self, b: M.WordBank):
        return self.B.bank([self.de(x) for x in b.items])

    def _b_game_grid(self, b: M.GameGrid):
        n = max(1, round(math.sqrt(len(b.cells))))
        cells = [self.de(c) for c in b.cells]
        return self.B.game({"rows": [cells[i:i + n] for i in range(0, len(cells), n)]})

    def _b_text(self, b: M.Paragraph):
        return self.B.para({"de": self.de(b.de) if b.de else "", "ex": self.ex(b.expl) if b.expl else "", "lang": self.cfg.lang})

    IMAGE_LINES = {"strip": 7, "wide": 11, "square": 12, "tall": 16}

    def image_view(self, im: M.Image, tokens: dict, fmt: Optional[str] = None, elastic: bool = True) -> dict:
        alt = self.cfg.t(im.alt) if im.alt else im.description
        src = ""
        if im.src and (self.cfg.root / im.src).exists():
            src = (self.cfg.root / im.src).as_uri()
        fmt = fmt or im.format
        iid = f"img-{im.id}"
        elastic = elastic and not im.markers          # pins are placed in per cent: a pinned picture keeps its shape
        style = ""
        if fmt in self.IMAGE_LINES:
            if elastic:
                self._grow_ids.append(iid)
                self.elastic[iid] = (self.cfg.bl / 2, 10)
            lines = self.IMAGE_LINES[fmt] + self.grow.get(iid, 0) * 0.5
            style = f"height:calc(var(--bl)*{lines:g})"
        variant = sum(ord(c) for c in im.id) % 3
        return {"id": iid, "format": fmt + (" nocap" if im.markers else ""), "src": src, "alt": html.escape(alt, quote=True), "style": style, "focus": im.focus,
                "art": art.placeholder_art(tokens, alt, variant), "icon": self.icon("bild", "4.6mm", self.cfg.de("labels.illustration")),
                "label": self.L("illustration"), "caption": esc(self.inline.plain(im.description)),
                "markers": [{"n": m.n, "x": m.x, "y": m.y} for m in im.markers]}

    def _b_image(self, b: M.Image):
        return self.B.image(self.image_view(b, self._tokens))

    def _b_picture_dictionary(self, b: M.PictureDictionary):
        items = []
        for i, wid in enumerate(b.items, 1):
            v = self.book.vocab[wid]
            article, head, suffix = v.notation()
            items.append({"n": i, "article": article, "cls": v.gender_class, "word": esc(head), "suffix": esc(suffix), "name": self._fid("pd")})
        return self.B.picdict({"image": self.image_view(b.image, self._tokens), "items": items, "forms": self.forms})

    def _b_self_eval(self, b: M.SelfEval):
        return self.B.selfeval({"lang": self.cfg.lang,
                                "items": [{"de": self.de(i.de), "ex": self.ex(i[self.cfg.lang]), "ruled": self.ruled("", 1)} for i in b.items]})

    # ── tasks and boxes ──────────────────────────────────────────────────────
    def _explain(self, task: M.Task, part_key: str) -> bool:
        if task.explain is not None:
            return task.explain
        if self.cfg.lv.get("explanation", "always") == "always":
            return True
        sig = (part_key, tuple(sorted(task.skills)), task.body[0].type if task.body else "")
        if sig in self._seen_types:
            return False
        self._seen_types.add(sig)
        return True

    def task_html(self, ref: TaskRef, tokens: dict, wu: bool = False) -> tuple[str, list[str]]:
        task = ref.task
        self._tokens = tokens
        self._scope = ref.address.replace(".", "-")
        self._n = 0
        self._ans = []
        self._grow_ids = []
        self.inline.begin(self._scope)
        prefix, letter = ref.address[:-1], ref.address[-1]
        icons = "".join(self.icon(s, "5.2mm", self.cfg.de(f"labels.skills.{s}")) for s in task.skills)
        rubric = self.de(task.rubric.de)
        expl = self.ex(task.rubric[self.cfg.lang]) if self._explain(task, ref.part_key) else ""
        body = self.body(task.body)
        margin = self.margin(task.notes, task.audio)
        self._answer(ref)
        l_anchor = "l-" + self._scope
        key = None
        if l_anchor in self.page_of:
            key = {"label": esc(self.page_of[l_anchor]), "href": f"#{l_anchor}" if l_anchor in self.built else ""}
        elif not self.page_of:
            key = {"label": "L 0", "href": ""}
        out = self.B.task({"anchor": ref.anchor, "prefix": esc(prefix), "letter": letter, "long": len(prefix) > 3, "icons": icons,
                           "rubric": rubric, "expl": expl, "lang": self.cfg.lang, "points": task.points, "key": key,
                           "body": body, "margin": margin, "wu": wu})
        return str(out), list(self._grow_ids)

    def _answer(self, ref: TaskRef) -> None:
        a = ref.answer
        parts = list(self._ans)
        bits = []
        if a and a.text:
            bits.append(self.de(a.text))
        bits += parts
        if a and a.open and not bits and not a.model:
            label = self.cfg.de("labels.listen_read") if (ref.task.audio and ref.task.audio.transcript_from_body) else self.cfg.de("labels.individual")
            bits.append(f'<span class="md">{esc(label)}</span>')
        if a and a.model:
            tag = f'<span class="tag">{self.L("model")}</span>'
            bits.append(f'{tag}<span class="md" lang="de">{self.de(a.model)}</span>')
        body = ' <span class="sep">|</span> '.join(bits)
        if a and a.note:
            body += f'<span class="nt" lang="{self.cfg.lang}">{self.ex(a.note)}</span>'
        anchor = "l-" + ref.address.replace(".", "-")
        back = self.page_link(ref.anchor, cls="bk")
        entry = (f'<div class="ak" id="{anchor}"><a class="aa" href="#{ref.anchor}">{esc(ref.address)}</a>'
                 f'<span class="ab" lang="de">{body} {back}</span></div>') if ref.anchor in self.built else \
                (f'<div class="ak" id="{anchor}"><span class="aa">{esc(ref.address)}</span>'
                 f'<span class="ab" lang="de">{body} {back}</span></div>')
        self.answers[ref.address] = AnswerEntry(ref.address, anchor, ref.anchor, ref.part_key, ref.teil, entry)

    def box_html(self, b: M.Boxed, uid: str, tokens: dict) -> tuple[str, list[str]]:
        self._tokens = tokens
        self._scope = uid
        self._n = 0
        self._ans = []
        self._grow_ids = []
        self.inline.begin(uid)
        out = self.B.boxed({"anchor": uid, "body": self.body(b.body), "margin": self.margin(b.notes)})
        return str(out), list(self._grow_ids)

    # ── units of a part ──────────────────────────────────────────────────────
    def teil_units(self, part, teil, tokens: dict, section: str) -> list[Unit]:
        key = part.key
        units: list[Unit] = []
        brk = False
        k = 0
        for b in teil.blocks:
            if isinstance(b, M.PageBreak):
                brk = True
                continue
            if isinstance(b, M.Boxed):
                k += 1
                uid = f"bx-{key}-{teil.nr}-{k}"
                h, grow = self.box_html(b, uid, tokens)
                units.append(Unit(uid, "box", h, key, teil.nr, section, list(b.words), grow_ids=grow, break_before=brk))
            else:
                ref = self.book.tasks[f"{key}.{teil.nr}{b.id}"]
                h, grow = self.task_html(ref, tokens)
                units.append(Unit(ref.anchor, "task", h, key, teil.nr, section, list(b.words), ref.address, grow,
                                  break_before=brk, title=self.inline.plain(b.rubric.de)))
            brk = False
        return units

    def teil_head(self, part, teil, section: str, no: Optional[str] = None) -> Unit:
        anchor = f"teil-{part.key}-{teil.nr}"
        h = self.B.teil_head({"anchor": anchor, "no": no if no is not None else str(teil.nr), "title": self.de(teil.title),
                              "sub": self.ex(teil.subtitle), "lang": self.cfg.lang})
        return Unit(anchor, "teil", str(h), part.key, teil.nr, section, keep_next=True, break_before=True, title=teil.title)

    def head_unit(self, uid: str, part_key: str, section: str, chip: str, title: str, sub: str) -> Unit:
        h = self.B.teil_head({"anchor": uid, "no": chip, "title": esc(title), "sub": sub, "lang": self.cfg.lang})
        return Unit(uid, "head", str(h), part_key, 0, section, keep_next=True, break_before=True, title=title)

    def total_unit(self, part, teil, section: str) -> Unit:
        """Score box at the end of a test: total points + what the result means."""
        total = sum((b.points or 0) for b in teil.blocks if isinstance(b, M.Task))
        rows = []
        if isinstance(part, M.Chapter):
            pages = self.page_link(f"sec-{part.key}-uebersicht")
            end = self.page_of.get(f"sec-{part.key}-uebersicht-2")
            if end and "<" in pages:
                pages = pages.replace("</", f"–{end}</", 1)
            scale, fmt = self.cfg.ui("test.scale"), {"pages": pages}
        else:
            scale, fmt = self.cfg.ui("station.scale"), {"a": part.covers[0], "b": part.covers[-1]}
        ref_total = scale[0][1]
        prev_lo = None
        for lo, hi, txt in scale:
            lo2 = round(lo * total / ref_total)
            hi2 = total if prev_lo is None else prev_lo - 1
            prev_lo = lo2
            rows.append(f"<li><b>{lo2}–{hi2}</b><span>{esc(txt).format(**fmt)}</span></li>")
        uid = f"total-{part.key}"
        h = (f'<div class="total"><div class="sum"><small lang="de">{self.L("total")}</small><span class="bx"></span>/ {total}</div>'
             f'<ul class="scale" lang="{self.cfg.lang}">{"".join(rows)}</ul></div>')
        return Unit("u-" + uid, "total", f'<article class="task boxu wide" id="u-{uid}"><div class="tk-l"></div><div class="tk-m">{h}</div></article>',
                    part.key, teil.nr, section)

    def cando_view(self, ch: M.Chapter, end: bool) -> str:
        heads = [self.cfg.de("labels.not_yet"), self.cfg.de("labels.almost"), self.cfg.de("labels.sure")]
        items = []
        for i, cd in enumerate(ch.can_do, 1):
            ref = ""
            if end and cd.ref:
                anchor = self.anchor_for(cd.ref)
                ref = self.page_link(anchor) if anchor else ""
            items.append({"de": self.de(cd.de), "ex": self.inline.ex(cd.translation(self.cfg.lang)), "ref": ref,
                          "name": f"cd-{ch.key}-{'e' if end else 's'}-{i}"})
        return str(self.B.cando({"title": esc(self.cfg.de("labels.can_do_end" if end else "labels.can_do_start")),
                                 "heads": [esc(h).replace(" ", "<br>") for h in heads], "items": items, "lang": self.cfg.lang,
                                 "forms": self.forms, "refs": end}))

    def next_unit(self, ch: M.Chapter) -> Optional[Unit]:
        if not ch.next:
            return None
        nmid = self.cfg.chapter_tokens(min(ch.number + 1, self.cfg.series["structure"]["chapters"]))["mid"]
        pts = "".join(f'<li><span lang="de">{self.de(p.de)}</span> <span class="ex" lang="{self.cfg.lang}">{self.ex(p[self.cfg.lang])}</span></li>' for p in ch.next.points)
        uid = f"next-{ch.key}"
        h = (f'<div class="nextc" id="{uid}" style="--nmid:{nmid}"><div><div class="lab" lang="de">{self.L("next_chapter")}</div>'
             f'<div class="nn">{ch.number + 1}</div></div><div><h3 lang="de">{self.de(ch.next.title)}</h3>'
             f'<p lang="de">{self.de(ch.next.teaser.de)}</p><p class="ex" lang="{self.cfg.lang}">{self.ex(ch.next.teaser[self.cfg.lang])}</p>'
             f'<ul class="pts">{pts}</ul></div></div>')
        return Unit("u-" + uid, "next", f'<div id="u-{uid}">{h}</div>', ch.key, 12, "rueckblick")
