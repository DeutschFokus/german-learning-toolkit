"""The build pipeline: units → measure → paginate → compose pages → one HTML document.

Layout is a small fixed-point iteration: page numbers appear inside the text
("S. 104", "L 2", line numbers), and the text decides the pagination. Two or
three rounds are enough for everything to settle.
"""
from __future__ import annotations

import datetime as _dt
import html
import re
from dataclasses import dataclass, field
from typing import Optional

from . import art
from . import models as M
from .config import MM, Config
from .layout import ColUnit, FlowPage, Placed, flow_columns, justify, measure, paginate
from .loader import Book
from .markup import NNBSP, german_sort_key, plural_form
from .render import Macros, Renderer, Unit, esc, strip_tags

ROMAN = ["", "i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi", "xii"]


PW_WIDTH, PW_GAP = 160.0, 3.0      # "words on this page" footer: line width and gap between entries (mm)


def stylesheet(cfg: Config, env, print_: bool = False) -> str:
    """The complete stylesheet of one edition: tokens from series.yaml and levels/<level>.yaml, rules from book.css.j2."""
    from .colors import oklch
    pg = cfg.page
    fdir = cfg.root / cfg.series["fonts"]["dir"]
    fonts = [{"family": f["family"], "url": (fdir / f["file"]).as_uri(), "weight": f["weight"], "style": f.get("style", "normal")}
             for f in cfg.series["fonts"]["faces"]]
    palettes = {f"c{k}": cfg.chapter_tokens(k) for k in range(1, cfg.series["structure"]["chapters"] + 1)}
    palettes["cz"] = cfg.station_tokens()
    lt = cfg.level_tokens()
    h = cfg.level_hue()
    palettes["cn"] = {"mid": oklch(0.86, 0.06, h), "soft": oklch(0.94, 0.03, h), "wash": oklch(0.972, 0.014, h),
                      "hl": oklch(0.88, 0.08, h), "strong": lt["cover_deep"], "deep": oklch(0.40, 0.10, h)}
    body = float(cfg.lv["type"]["body"])
    sheet_w = pg["width"] + (2 * (pg["bleed"] + pg["slug"]) if print_ else 0)
    sheet_h = pg["height"] + (2 * (pg["bleed"] + pg["slug"]) if print_ else 0)
    return env.get_template("book.css.j2").render(
        fonts=fonts, t=cfg.base_tokens(), lv=lt, palettes=palettes, pg=pg, tw=cfg.text_width_mm,
        content_w=round(pg["main"] - pg["label_col"], 3), body_h=cfg.body_height_pt, bl=cfg.bl, fs=body,
        fs_ex=body - 1, fs_note=round(body * 0.786, 2), fs_read=round(body - 0.3, 2), hw=cfg.lv["type"]["hand"],
        wl=float(cfg.lv["type"]["write_line"]) * cfg.bl, sheet_w=sheet_w, sheet_h=sheet_h, pw_w=PW_WIDTH, pw_h=15, pw_gap=PW_GAP)


def cover_view(cfg: Config, sample: bool = False) -> dict:
    """Everything the cover template needs. Each text element is passed (and printed) exactly once."""
    rest = esc(cfg.ui("cover.title_rest")).replace("{level}", f'<span class="lvw">{cfg.level_name}</span>').replace("|", "<br>")
    return {"lang": cfg.lang, "level": cfg.level_name, "niveau": esc(cfg.de("labels.level")), "rest": rest,
            "expl": esc(cfg.ui("cover.explanations")), "features": [esc(f) for f in cfg.ui("cover.features")],
            "logo": art.logo(cfg.series["colors"]["navy"]),
            "sample": esc(cfg.ui("labels.free_sample")) if sample else ""}


@dataclass
class PageSpec:
    pid: str                      # DOM id of the page: p-101, p-L1, p-cover
    kind: str                     # cover | front | opener | flow | appendix | sales
    group: str                    # front | learn | answers | transcripts | wordlist | back
    label: str                    # PDF page label
    folio: str                    # printed folio ("" = none)
    side: str                     # recto | verso
    palette: str
    inner: str = ""
    cls: str = ""
    anchors: list[str] = field(default_factory=list)
    outline: list[tuple[int, str, str]] = field(default_factory=list)   # (level, title, anchor)
    meta: dict = field(default_factory=dict)
    flow: Optional[FlowPage] = None


@dataclass
class Result:
    html: str
    pages: list[PageSpec]
    css: str
    rounds: int
    title: str
    stats: dict


class Builder:
    def __init__(self, cfg: Config, book: Book):
        self.cfg, self.book = cfg, book
        self.r = Renderer(cfg, book)
        self.P = Macros(self.r.env.get_template("pages.html.j2").module)
        self.print = bool(cfg.flags.get("print"))
        self.sample = bool(cfg.flags.get("sample"))
        self.css = self._css()
        self.cap = cfg.body_height_pt
        self.bl = cfg.bl
        self.wl_pt = float(cfg.lv["type"]["write_line"]) * cfg.bl
        self.grow: dict[str, int] = {}
        self.word_intro: dict[str, str] = {}           # vocab id → page label
        self.word_pages: dict[str, list[str]] = {}
        self.pw_width: dict[str, float] = {}
        self.geom: dict = {}
        self.goal_pad: dict[str, float] = {}           # chapter key → pt that round the goal box up to the grid

    # ── stylesheet ───────────────────────────────────────────────────────────
    def _css(self) -> str:
        self.pw_w, self.pw_gap = PW_WIDTH, PW_GAP
        return stylesheet(self.cfg, self.r.env, self.print)

    # ── helpers ──────────────────────────────────────────────────────────────
    def goalbox(self, ch, pad: float) -> str:
        """Chapter goal and its translation; `pad` (pt) rounds the box up to a multiple of half a baseline."""
        r, cfg = self.r, self.cfg
        style = f' style="padding-bottom:{pad}pt"' if pad else ""
        return (f'<div class="goalbox" id="goalbox-{ch.key}"{style}><p class="goal" lang="de">{r.de(ch.goal.de)}</p>'
                f'<p class="goal-tr" lang="{cfg.lang}">{r.ex(ch.goal[cfg.lang])}</p></div>')

    def palette(self, part) -> tuple[str, dict]:
        if isinstance(part, M.Chapter):
            return f"c{part.number}", self.cfg.chapter_tokens(part.number)
        return "cz", self.cfg.station_tokens()

    def part_start(self, part) -> int:
        return self.cfg.chapter_start(part.number) if isinstance(part, M.Chapter) else self.cfg.station_start(part.number)

    def full_unit(self, uid: str, inner: str, part_key: str, section: str, teil: int = 0, words=None) -> Unit:
        return Unit(uid, "full", f'<div class="full" id="{uid}">{inner}</div>', part_key, teil, section, list(words or []))

    # ── build the flow units of every part ───────────────────────────────────
    def part_units(self, part) -> tuple[list[Unit], list[Unit]]:
        """Returns (opener task units, flow units)."""
        r, cfg = self.r, self.cfg
        pal, tokens = self.palette(part)
        opener_units: list[Unit] = []
        flow: list[Unit] = []
        if isinstance(part, M.Station):
            first = True
            for teil in part.teile:
                if first:
                    covers = cfg.de("labels.station_covers", a=part.covers[0], b=part.covers[-1])
                    h = r.B.station_head({"anchor": f"k-{part.key}", "no": part.number, "kicker": esc(covers),
                                          "title": r.de(part.title), "intro": r.de(part.intro.de),
                                          "sub": r.ex(part.intro[cfg.lang]), "lang": cfg.lang})
                    flow.append(Unit(f"k-{part.key}", "head", str(h), part.key, 0, "station", break_before=True, title=part.title))
                head = r.teil_head(part, teil, "station")
                head.break_before = not first
                flow.append(head)
                flow += r.teil_units(part, teil, tokens, "station")
                if teil.kind == "exam":
                    flow.append(r.total_unit(part, teil, "station"))
                first = False
            return opener_units, flow
        ch: M.Chapter = part
        for teil in ch.teile:
            sec = teil.section
            if sec == "auftakt":
                for b in teil.blocks:
                    if isinstance(b, M.Task):
                        ref = self.book.tasks[f"{ch.key}.{teil.nr}{b.id}"]
                        h, _ = r.task_html(ref, tokens, wu=True)
                        opener_units.append(Unit(ref.anchor, "task", h, ch.key, teil.nr, sec, list(b.words), ref.address,
                                                 title=r.inline.plain(b.rubric.de)))
                continue
            if sec == "abschlusstest" and not any(u.section == "uebersicht" for u in flow):
                flow += self.overview_units(ch, tokens)
            head = r.teil_head(ch, teil, sec)
            flow.append(head)
            if sec == "rueckblick":
                lead = f'<p class="rvlead" lang="{cfg.lang}">{esc(cfg.ui("review.lead")).format(page=r.page_link(f"k-{ch.key}"))}</p>'
                test_total = sum((b.points or 0) for t in ch.teile if t.section == "abschlusstest" for b in t.blocks if isinstance(b, M.Task))
                res = (f'<p class="rvres" lang="de">{r.L("test_result")}: <span class="gap" style="width:16mm"></span> / {test_total}'
                       f' &nbsp; {r.page_link(f"teil-{ch.key}-{teil.nr - 1}")}</p>') if test_total else ""
                uid = f"cando-{ch.key}"
                inner = (f'<article class="task boxu" id="{uid}"><div class="tk-l"></div><div class="tk-m">{lead}{r.cando_view(ch, True)}{res}</div>'
                         f'<aside class="mn"></aside></article>')
                flow.append(Unit(uid, "cando", inner, ch.key, teil.nr, sec))
            flow += r.teil_units(ch, teil, tokens, sec)
            if sec == "abschlusstest":
                flow.append(r.total_unit(ch, teil, sec))
            if sec == "rueckblick":
                nx = r.next_unit(ch)
                if nx:
                    flow.append(nx)
        return opener_units, flow

    def overview_units(self, ch: M.Chapter, tokens: dict) -> list[Unit]:
        r, cfg = self.r, self.cfg
        out = []
        r._tokens = tokens
        for idx, (key, blocks, icon_name) in enumerate((("grammar", ch.uebersicht.grammar, "grammatik"), ("phrases", ch.uebersicht.phrases, "phrases")), 1):
            anchor = f"sec-{ch.key}-uebersicht" + ("" if idx == 1 else "-2")
            chip = r.icon(icon_name, "7mm", cfg.de(f"labels.overview_{key}"))
            out.append(r.head_unit(anchor, ch.key, "uebersicht", chip, cfg.de(f"labels.overview_{key}"), esc(cfg.ui(f"overview.{key}"))))
            for j, b in enumerate(blocks, 1):
                r._scope = f"ov-{ch.key}-{idx}-{j}"
                r._n = 0
                r.inline.begin(r._scope)
                inner = r.block(b)
                if key == "phrases":
                    inner = inner.replace('class="phr"', 'class="phr two"', 1)
                out.append(self.full_unit(f"ov-{ch.key}-{idx}-{j}", inner, ch.key, "uebersicht"))
        return out

    # ── appendix content ─────────────────────────────────────────────────────
    def answer_units(self) -> list[tuple[ColUnit, str]]:
        r, cfg = self.r, self.cfg
        out: list[tuple[ColUnit, str]] = []
        order = {p.key: i for i, p in enumerate(self.book.parts())}
        entries = sorted(r.answers.values(), key=lambda a: (order[a.part], a.teil, a.address))
        cur = None
        for a in entries:
            if a.part != cur:
                cur = a.part
                part = next(p for p in self.book.parts() if p.key == cur)
                color = self.palette(part)[1]["mid"] if isinstance(part, M.Chapter) else cfg.series["colors"]["navy"]
                title = f'{cfg.de("chapter")} {part.number} · {esc(part.title)}' if isinstance(part, M.Chapter) else f'{cfg.de("station")} {part.number}'
                uid = f"akh-{cur}"
                out.append((ColUnit(uid, 0, keep_next=True, gap_after=self.bl * 0.4),
                            f'<div class="akh" id="{uid}" style="--cm:{color}" lang="de">{title}</div>'))
            out.append((ColUnit(a.anchor, 0, gap_after=self.bl * 0.4), a.html))
        return out

    def transcript_units(self) -> list[tuple[ColUnit, str]]:
        r, cfg = self.r, self.cfg
        out = []
        cast = cfg.series["cast"]
        for track in sorted(self.book.tracks):
            ref, au, tr = self.book.tracks[track]
            uid = "tr-" + track.replace(".", "-")
            back = r.page_link(ref.anchor, f'{esc(ref.address)}, {cfg.de("page_abbr")}{NNBSP}{r.page_of.get(ref.anchor, "…")}', cls="bk")
            head = (f'<div class="th"><span class="tn">{esc(track)}</span><span class="tt" lang="de">{esc(au.title)}'
                    f'<span>{esc(au.duration)} Min. · {back}</span></span></div>')
            body = ""
            if tr.turns:
                for t in tr.turns:
                    body += f'<div class="tl2"><span class="who">{esc(cast[t.speaker]["name"])}</span><span lang="de">{r.de(t.text)}</span></div>'
            if tr.text:
                body += f'<div class="tl2"><span class="who"></span><span lang="de">{r.de(tr.text)}</span></div>'
            out.append((ColUnit(uid, 0, gap_after=self.bl * 0.8), f'<div class="trs" id="{uid}">{head}{body}</div>'))
        return out

    def wordlist_units(self) -> list[tuple[ColUnit, str]]:
        r, cfg = self.r, self.cfg
        out = []
        vocab = sorted(self.book.vocab.values(), key=lambda v: (german_sort_key(v.de), v.de))
        letter = None
        for v in vocab:
            first = german_sort_key(v.de)[:1].upper()
            if first != letter:
                letter = first
                uid = f"wlh-{letter}"
                out.append((ColUnit(uid, 0, keep_next=True), f'<div class="wlh" id="{uid}">{letter}</div>'))
            w = r.word_view(v, sep=True)
            a = f'<span class="{w["cls"]}">{w["article"]}</span> ' if w["article"] else ""
            pages = []
            intro = self.word_intro.get(v.id)
            for lab in self.word_pages.get(v.id, []):
                anchor = "p-" + lab.replace(" ", "")
                txt = f"<b>{lab}</b>" if lab == intro else lab
                pages.append(f'<a href="#{anchor}">{txt}</a>' if anchor in r.built else txt)
            uid = f"w-{v.id}"
            out.append((ColUnit(uid, 0), f'<div class="wle" id="{uid}" lang="de">{a}<b>{w["word"]}</b><span class="sx">{w["suffix"]}</span> '
                                         f'<span class="tr2" lang="{cfg.lang}">{w["tr"]}</span> <span class="pgs">{", ".join(pages)}</span></div>'))
        return out

    # ── one layout round ─────────────────────────────────────────────────────
    def layout_round(self, final: bool = False) -> dict:
        r, cfg, book = self.r, self.cfg, self.book
        r.grow = dict(self.grow)
        r._seen_types = set()
        r.answers = {}
        parts = list(book.parts())
        units: dict[str, tuple[list[Unit], list[Unit]]] = {p.key: self.part_units(p) for p in parts}
        tw = cfg.text_width_mm
        items: list[tuple[str, float]] = []
        for key, (op, flow) in units.items():
            items += [(u.html, tw) for u in op + flow]
        for p in parts:                                     # chapter goals: measured so the opener stays on the grid
            if isinstance(p, M.Chapter):
                items.append((f'<div class="op op-{cfg.series["design"]["opener"]}">{self.goalbox(p, 0.0)}</div>', 122.0))
        ans = self.answer_units()
        trs = self.transcript_units()
        colw2 = round((tw - 8) / 2, 3)
        items += [(f'<div class="axc" style="position:static;width:{colw2}mm">{h}</div>', colw2) for _, h in ans + trs]
        pw_items = []
        for v in book.vocab.values():
            w = r.word_view(v)
            a = f'<span class="{w["cls"]}">{w["article"]}</span> ' if w["article"] else ""
            pw_items.append(f'<span class="w" id="pwm-{v.id}">{a}<b>{w["word"]}</b>{w["suffix"]} <em>{w["tr"]}</em></span>')
        items.append(('<div class="pw" style="position:static;width:auto;height:auto;border:0;overflow:visible">' + "<br>".join(pw_items) + "</div>", 200))
        geom = measure(cfg, self.css, items)
        self.geom = geom
        self.pw_width = {v.id: geom[f"pwm-{v.id}"][2] - geom[f"pwm-{v.id}"][0] for v in book.vocab.values() if f"pwm-{v.id}" in geom}

        half = self.bl / 2
        self.goal_pad = {}
        for p in parts:
            g = geom.get(f"goalbox-{p.key}")
            if g is not None:
                pad = (-(g[3] - g[1])) % half
                self.goal_pad[p.key] = 0.0 if pad < 0.05 or half - pad < 0.05 else round(pad, 2)

        # heights (without the lines that were grown in the previous round)
        missing = []
        for key, (op, flow) in units.items():
            for u in op + flow:
                g = geom.get(u.uid) or geom.get("u-" + u.uid)
                if g is None:
                    missing.append(u.uid)
                    continue
                u.height = (g[3] - g[1]) - sum(self.grow.get(i, 0) * r.elastic[i][0] for i in u.grow_ids if i in r.elastic)
        if missing:
            raise RuntimeError(f"measure pass lost units: {missing[:5]}")

        # reading texts: line geometry and line anchors
        text_geom: dict[str, list[tuple[float, int]]] = {}
        line_of: dict[tuple[str, str], int] = {}
        for name, g in geom.items():
            if name.startswith("rt-") and re.search(r"-p\d+$", name) is None:
                paras = sorted((k for k in geom if k.startswith(name + "-p")), key=lambda k: int(k.rsplit("-p", 1)[1]))
                rows = [(geom[p][1] - g[1], max(1, round((geom[p][3] - geom[p][1]) / self.bl))) for p in paras]
                text_geom[name] = rows
        for name, g in geom.items():
            if name.startswith("la-"):
                rest = name[3:]
                rid = next((t for t in sorted(text_geom, key=len, reverse=True) if rest.startswith(t + "-")), None)
                if rid is None:
                    continue
                anchor = rest[len(rid) + 1:]
                base = geom[rid][1]
                y = (g[1] + g[3]) / 2 - base
                n = 0
                for top, lines in text_geom[rid]:
                    if y >= top + lines * self.bl:
                        n += lines
                    else:
                        n += max(0, int((y - top) // self.bl)) + 1
                        break
                line_of[(rid, anchor)] = n

        # paginate the learning parts
        page_of: dict[str, str] = {}
        new_grow: dict[str, int] = {}
        learn: list[PageSpec] = []
        issues = []
        for part in parts:
            pal, tokens = self.palette(part)
            op, flow = units[part.key]
            start = self.part_start(part)
            folio = start
            if isinstance(part, M.Chapter):
                spec = PageSpec(f"p-{folio}", "opener", "learn", str(folio), str(folio), "recto" if folio % 2 else "verso", pal,
                                meta={"part": part.key, "section": "auftakt", "units": op})
                spec.anchors = [f"k-{part.key}", f"sec-{part.key}-auftakt", f"teil-{part.key}-1"] + [u.uid for u in op]
                learn.append(spec)
                folio += 1
            pages = paginate(flow, self.cap, self.bl)
            for fp in pages:
                justify(fp, self.cap, self.bl, r.elastic, new_grow)
                first = fp.placed[0].unit
                spec = PageSpec(f"p-{folio}", "flow", "learn", str(folio), str(folio), "recto" if folio % 2 else "verso", pal, flow=fp,
                                meta={"part": part.key, "section": first.section, "teil": first.teil})
                spec.anchors = [pl.unit.uid for pl in fp.placed]
                learn.append(spec)
                folio += 1
            # budgets
            if isinstance(part, M.Chapter):
                got: dict[str, int] = {"auftakt": 1}
                for s in learn:
                    if s.meta.get("part") == part.key and s.kind == "flow":
                        got[s.meta["section"]] = got.get(s.meta["section"], 0) + 1
                for s in cfg.sections:
                    if got.get(s["id"], 0) != s["pages"]:
                        issues.append(("error", f"Kapitel {part.number} · {s['de']}",
                                       f"uses {got.get(s['id'], 0)} page(s), budget is {s['pages']}"))
            else:
                n = folio - start
                if n != cfg.series["structure"]["station_pages"]:
                    issues.append(("error", f"Zwischenstation {part.number}", f"uses {n} page(s), budget is {cfg.series['structure']['station_pages']}"))
        for s in learn:
            for a in s.anchors:
                page_of.setdefault(a, s.label)
            page_of[s.pid] = s.label
            if s.kind == "flow":
                sec_anchor = f"sec-{s.meta['part']}-{s.meta['section']}"
                page_of.setdefault(sec_anchor, s.label)
                s.anchors.append(sec_anchor)
            fp = s.flow
            if fp and fp.overflow > 0.6:
                issues.append(("error", f"S. {s.label}", f"content overflows the page by {fp.overflow / MM:.1f} mm"))

        # appendix: answers and transcripts (two columns)
        head_h = self.bl * 6.5
        appendix: list[PageSpec] = []

        def columns(group: str, prefix: str, cunits: list[tuple[ColUnit, str]], cols: int, colw: float, cls: str, title_key: str, anchor: str, tab: str):
            for cu, _ in cunits:
                g = geom.get(cu.uid)
                cu.height = (g[3] - g[1]) if g else self.bl
            pages = flow_columns([cu for cu, _ in cunits], cols, lambda pi: self.cap - (head_h if pi == 0 else 0))
            htmls = {cu.uid: h for cu, h in cunits}
            for pi, cols_ in enumerate(pages):
                label = f"{prefix} {pi + 1}"
                spec = PageSpec("p-" + label.replace(" ", ""), "appendix", group, label, label, "", "cn",
                                meta={"cols": cols_, "htmls": htmls, "colw": colw, "ncols": cols, "cls": cls, "title_key": title_key,
                                      "first": pi == 0, "head_h": head_h, "anchor": anchor, "tab": tab, "tabslot": {"L": 1, "T": 2, "W": 3}[prefix]})
                spec.anchors = [uid for col in cols_ for uid, _ in col] + ([anchor] if pi == 0 else [])
                appendix.append(spec)

        if ans:
            columns("answers", "L", ans, 2, colw2, "", "answers", "ax-answers", "L")
        if trs:
            columns("transcripts", "T", trs, 2, colw2, "", "transcripts", "ax-transcripts", "T")
        for s in appendix:
            for a in s.anchors:
                page_of.setdefault(a, s.label)
            page_of[s.pid] = s.label

        # words: where is each word introduced, where else does it occur?
        word_intro: dict[str, str] = {}
        page_text: dict[str, str] = {}
        for s in learn:
            us = s.meta.get("units") if s.kind == "opener" else [pl.unit for pl in s.flow.placed]
            words = []
            for u in us:
                for w in u.words:
                    if w not in word_intro:
                        word_intro[w] = s.label
                        words.append(w)
            s.meta["words"] = words
            page_text[s.label] = " ".join(u.text for u in us)
        word_pages: dict[str, list[str]] = {}
        for v in book.vocab.values():
            forms = {v.de, *v.forms}
            pf = v.plural_form or (plural_form(v.de, v.plural or "") if v.is_noun else None)
            if pf:
                forms.add(pf)
            if v.perfekt:
                forms.add(v.perfekt.split()[-1])
            rx = re.compile(r"(?<![A-Za-zÄÖÜäöüß])(?:" + "|".join(re.escape(f) for f in sorted(forms, key=len, reverse=True)) + r")(?![A-Za-zÄÖÜäöüß])",
                            re.I if not v.is_noun else 0)
            pages = [lab for lab, txt in page_text.items() if rx.search(txt)]
            if v.id in word_intro and word_intro[v.id] not in pages:
                pages.append(word_intro[v.id])
            word_pages[v.id] = sorted(pages, key=lambda x: int(x))
        self.word_intro, self.word_pages = word_intro, word_pages

        model_rows = {name[:-2]: max(1, round((g[3] - g[1]) / self.wl_pt)) for name, g in geom.items()
                      if name.startswith("wl-") and name.endswith("-m")}
        state = {"page_of": page_of, "line_of": line_of, "text_geom": text_geom, "grow": new_grow, "model_rows": model_rows}
        self._round = {"learn": learn, "appendix": appendix, "issues": issues, "units": units, "ans": ans, "trs": trs, "colw2": colw2}
        return state

    # ── words-on-this-page footer ────────────────────────────────────────────
    def words_footer(self, words: list[str], pid: str) -> str:
        cfg, r = self.cfg, self.r
        if not words:
            return ""
        width = self.pw_w * MM
        gap = self.pw_gap * MM + 1.9
        lines, x, kept, dropped = 1, 0.0, [], 0
        more_reserve = 52 * MM
        for i, w in enumerate(words):
            ww = self.pw_width.get(w, 60.0)
            if x > 0 and x + ww > width:
                lines += 1
                x = 0.0
            limit = width - (more_reserve if lines == 3 and i < len(words) - 1 else 0)
            if lines > 3 or (lines == 3 and x + ww > limit and i < len(words) - 1):
                dropped = len(words) - i
                break
            kept.append(w)
            x += ww + gap
        more = ""
        if dropped:
            more = esc(cfg.ui("labels.more_words", n=dropped))
            self._round["issues"].append(("warning", pid, f"{dropped} word(s) did not fit into the footer; they are in the word list only"))
        return str(r.B.words_footer({"label": r.L("words_on_page"), "sub": esc(cfg.ui("labels.words_on_page")), "lang": cfg.lang,
                                     "words": [r.word_view(self.book.vocab[w]) for w in kept], "more": more}))

    # ── page composition ─────────────────────────────────────────────────────
    def tab(self, part) -> str:
        pg = self.cfg.page["tab"]
        if isinstance(part, M.Chapter):
            return f'<div class="tab" style="top:{pg["first"] + (part.number - 1) * pg["step"]:.1f}mm">{part.number}</div>'
        return f'<div class="tab st" style="top:{pg["first"] + 12 * pg["step"]:.1f}mm;font-size:9pt">Z{part.number}</div>'

    def running(self, part, section: str, teil_title: str = "") -> str:
        cfg = self.cfg
        if isinstance(part, M.Chapter):
            prog = [(s["pages"] * 1.25, "on" if s["id"] == section else "") for s in cfg.sections]
            return str(self.P.running({"prog": prog, "left": f'{cfg.de("chapter")} {part.number}', "mid": esc(part.title),
                                       "right": esc(cfg.section(section)["de"])}))
        covers = cfg.de("labels.station_covers", a=part.covers[0], b=part.covers[-1])
        return str(self.P.running({"prog": [], "left": f'{cfg.de("station")} {part.number}', "mid": esc(covers), "right": esc(teil_title)}))

    def compose_learning(self, spec: PageSpec) -> None:
        cfg, r = self.cfg, self.r
        part = next(p for p in self.book.parts() if p.key == spec.meta["part"])
        pal, tokens = self.palette(part)
        folio = f'<div class="folio">{spec.folio}</div>'
        footer = self.words_footer(spec.meta.get("words", []), spec.pid)
        if spec.kind == "opener":
            ch: M.Chapter = part
            style = cfg.series["design"]["opener"]
            r._tokens = tokens
            toc = ""
            for s in cfg.sections[1:]:
                anchor = f"sec-{ch.key}-{s['id']}"
                toc += f'<li><b>{esc(s["de"])}</b>{r.page_link(anchor, r.page_of.get(anchor, "…"), cls="pg")}</li>'
            im = r.image_view(ch.image, tokens, "banner", elastic=False)
            o = {"style": style, "no": str(ch.number), "kicker": f'{cfg.de("chapter")} {ch.number}' if style == "buehne" else f'{cfg.level_name} · {cfg.de("chapter")} {ch.number}',
                 "title": r.de(ch.title), "long": len(ch.title) > 12, "sub": r.ex(ch.subtitle), "lang": cfg.lang, "anchor": f"k-{ch.key}",
                 "goalbox": self.goalbox(ch, getattr(self, "goal_pad", {}).get(ch.key, 0.0)), "goal_label": r.L("goal"),
                 "goal_icon": r.icon("ziel", "4.6mm", cfg.de("labels.goal")), "cando": r.cando_view(ch, False),
                 "toc_label": r.L("in_this_chapter"), "toc": toc, "gram_label": r.L("grammar"),
                 "gram_icon": r.icon("grammatik", "4.6mm", cfg.de("labels.grammar")), "grammar": [esc(g) for g in ch.grammar],
                 "warmup": "".join(u.html for u in spec.meta["units"]), "image": str(r.B.image(im)), "end": f"end-{spec.pid}",
                 "tab_top": cfg.page["tab"]["first"] + (ch.number - 1) * cfg.page["tab"]["step"]}
            spec.cls = f"op op-{style}"
            spec.inner = str(self.P.opener(o)) + footer + folio
            spec.outline = [(1, f'{cfg.de("chapter")} {ch.number} · {ch.title}', f"k-{ch.key}")] + \
                           [(3, f"{u.address} {u.title}", u.uid) for u in spec.meta["units"]]
            return
        fp = spec.flow
        teil_title = ""
        if isinstance(part, M.Station):
            t = next((t for t in part.teile if t.nr == spec.meta.get("teil")), None) or part.teile[0]
            teil_title = t.title
        body = "".join(f'<div class="u" style="top:{pl.top:.2f}pt">{pl.unit.html}</div>' for pl in fp.placed)
        spec.inner = (self.running(part, spec.meta["section"], teil_title) + self.tab(part)
                      + f'<div class="body">{body}</div>' + footer + folio)
        for pl in fp.placed:
            u = pl.unit
            if u.kind == "teil":
                spec.outline.append((2, f"{u.part}.{u.teil} {u.title}", u.uid))
            elif u.kind == "head":
                if u.uid.startswith("k-"):
                    spec.outline.append((1, f'{cfg.de("station")} {part.number}', u.uid))
                else:
                    spec.outline.append((2, f'{cfg.section("uebersicht")["de"]} · {u.title}', u.uid))
            elif u.kind == "task":
                spec.outline.append((3, f"{u.address} {u.title}", u.uid))

    def compose_appendix(self, spec: PageSpec) -> None:
        cfg, r = self.cfg, self.r
        m = spec.meta
        key = m["title_key"]
        head = ""
        top0 = 0.0
        if m["first"]:
            head = (f'<div class="axh"><h1 lang="de" id="{m["anchor"]}">{esc(cfg.de("labels.wordlist_long" if key == "wordlist" else "labels." + key))}</h1>'
                    f'<p class="lead" lang="{cfg.lang}">{esc(cfg.ui(key + ".lead"))}</p></div>')
            top0 = m["head_h"]
            spec.outline = [(1, cfg.de("labels.wordlist_long" if key == "wordlist" else "labels." + key), m["anchor"])]
        gapw = (cfg.text_width_mm - m["ncols"] * m["colw"]) / max(1, m["ncols"] - 1) if m["ncols"] > 1 else 0
        cols = ""
        for ci, col in enumerate(m["cols"]):
            left = ci * (m["colw"] + gapw)
            inner = "".join(f'<div class="axu" style="top:{top:.2f}pt">{m["htmls"][uid]}</div>' for uid, top in col)
            cols += f'<div class="axc {m["cls"]}" style="left:{left:.3f}mm;width:{m["colw"]}mm;top:{top0:.2f}pt">{inner}</div>'
        pg = cfg.page["tab"]
        tab = f'<div class="tab" style="top:{pg["first"] + (m["tabslot"] - 1) * pg["step"]:.1f}mm">{m["tab"]}</div>'
        run = str(self.P.running({"prog": [], "left": cfg.de("labels.appendix"), "mid": "", "right": esc(cfg.de("labels." + key))}))
        spec.inner = run + tab + f'<div class="ax">{head}{cols}</div><div class="folio">{spec.folio}</div>'

    # ── front and back matter ────────────────────────────────────────────────
    def front_pages(self) -> list[PageSpec]:
        cfg, r = self.cfg, self.r
        S = cfg.series["series"]
        pages: list[PageSpec] = []
        # cover
        cover = self.P.cover(cover_view(cfg, self.sample))
        pages.append(PageSpec("p-cover", "cover", "front", "Cover", "", "recto", "cn", str(cover), "cover", ["p-cover"],
                              [(1, cfg.edition_title(), "p-cover")]))
        # imprint
        today = _dt.date.today().isoformat()
        imp = self.P.imprint({"lang": cfg.lang, "logo": art.logo(cfg.series["colors"]["ink"]), "title": esc(cfg.edition_title()),
                              "expl": esc(cfg.ui("cover.explanations")),
                              "copyright": esc(cfg.ui("imprint.copyright", year=S["year"], publisher=S["publisher"])),
                              "version": esc(cfg.ui("imprint.version", version=S["version"], date=today)),
                              "licence_title": esc(cfg.ui("imprint.licence_title")), "licence": esc(cfg.ui("imprint.licence")),
                              "audio_title": esc(cfg.ui("imprint.audio_title")),
                              "audio": esc(cfg.ui("imprint.audio")).format(url=f'<a href="{S["website"]}/audio">{S["website"].split("//")[1]}/audio</a>'),
                              "fonts_title": esc(cfg.ui("imprint.fonts_title")), "fonts": esc(cfg.ui("imprint.fonts")),
                              "credits": esc(" · ".join(cfg.series["fonts"]["credits"])),
                              "characters": esc(cfg.ui("imprint.characters")),
                              "contact": esc(cfg.ui("imprint.contact")).format(contact=f'<a href="mailto:{S["contact"]}">{S["contact"]}</a>')})
        pages.append(PageSpec("p-ii", "front", "front", "ii", "ii", "verso", "cn", str(imp) + '<div class="folio">ii</div>', "", ["p-ii"],
                              [(1, cfg.de("labels.imprint"), "p-ii")]))
        # contents
        rows = []
        st = cfg.series["structure"]
        for oc in self.book.outline.chapters:
            built = oc.number in self.book.chapters
            anchor = f"k-{oc.number}"
            start = cfg.chapter_start(oc.number)
            link = f'<a href="#{anchor}"><b lang="de">{esc(oc.title)}</b></a>' if anchor in r.built else f'<b lang="de">{esc(oc.title)}</b>'
            rows.append({"kind": "chapter", "no": oc.number, "built": built, "color": cfg.chapter_tokens(oc.number)["mid"], "link": link,
                         "sub": r.ex(oc.subtitle), "grammar": esc(" · ".join(oc.grammar)),
                         "page": f'<a href="#{anchor}">{start}</a>' if anchor in r.built else str(start)})
            if oc.number in st["stations_after"]:
                k = st["stations_after"].index(oc.number) + 1
                os_ = next((s for s in self.book.outline.stations if s.number == k), None)
                anchor = f"k-Z{k}"
                start = cfg.station_start(k)
                title = f'{cfg.de("station")} {k}'
                link = f'<a href="#{anchor}"><b lang="de">{title}</b></a>' if anchor in r.built else f'<b lang="de">{title}</b>'
                rows.append({"kind": "station", "no": k, "built": k in self.book.stations, "link": link, "sub": r.ex(os_.subtitle) if os_ else "",
                             "page": f'<a href="#{anchor}">{start}</a>' if anchor in r.built else str(start)})
        front_rows = [{"link": f'<a href="#how"><b lang="de">{esc(cfg.de("labels.how"))}</b></a> <span lang="{cfg.lang}">{esc(cfg.ui("toc.how"))}</span>', "page": '<a href="#how">iv</a>'},
                      {"link": f'<a href="#cast"><b lang="de">{esc(cfg.de("labels.cast"))}</b></a> <span lang="{cfg.lang}">{esc(cfg.ui("toc.cast"))}</span>', "page": '<a href="#cast">vi</a>'}]
        back_rows = []
        for key, anchor in (("answers", "ax-answers"), ("transcripts", "ax-transcripts"), ("wordlist", "ax-wordlist")):
            lab = r.page_of.get(anchor, "")
            built = anchor in r.built
            name = f'<b lang="de">{esc(cfg.de("labels.wordlist_long" if key == "wordlist" else "labels." + key))}</b> <span lang="{cfg.lang}">{esc(cfg.ui("toc." + key))}</span>'
            back_rows.append({"built": bool(lab), "link": f'<a href="#{anchor}">{name}</a>' if built else name,
                              "page": (f'<a href="#{anchor}">{lab}</a>' if built else lab)})
        toc = self.P.toc({"title": esc(cfg.de("labels.contents")), "lang": cfg.lang, "intro": esc(cfg.ui("toc.intro", level=cfg.level_name)),
                          "front": esc(cfg.ui("toc.front")), "front_rows": front_rows, "chapters_label": f'{cfg.total_pages} {esc(cfg.de("labels.pages"))} · 12 {esc(cfg.de("chapter"))}',
                          "rows": rows, "appendix": esc(cfg.ui("toc.appendix")), "back_rows": back_rows})
        pages.append(PageSpec("p-iii", "front", "front", "iii", "iii", "recto", "cn", str(toc) + '<div class="folio">iii</div>', "", ["p-iii", "toc"],
                              [(1, cfg.de("labels.contents"), "toc")]))
        # how this book works (spread)
        demo_tokens = cfg.chapter_tokens(5)
        sample_task = (f'<article class="task"><div class="tk-l"><span class="addr"><i>5.2</i><b>d</b></span><span class="skills">'
                       f'{r.icon("lesen", "5.2mm", cfg.de("labels.skills.lesen"))}{r.icon("schreiben", "5.2mm", cfg.de("labels.skills.schreiben"))}</span></div>'
                       f'<div class="tk-m"><div class="rub"><span class="de" lang="de">{esc(cfg.de("how.sample_rubric"))}</span><span class="meta">'
                       f'<span class="score">/ 6</span><span class="lkey">L 3</span></span></div>'
                       f'<p class="ex" lang="{cfg.lang}">{esc(cfg.ui("how.task_points")[2])}</p></div><aside class="mn"></aside></article>')
        how1 = self.P.how1({"title": esc(cfg.de("labels.how")), "lang": cfg.lang, "lead": esc(cfg.ui("how.lead")),
                            "path_title": esc(cfg.de("how.path_title")),
                            "path": [{"pages": s["pages"], "name": esc(s["de"]), "text": esc(cfg.ui(f"how.path.{s['id']}"))} for s in cfg.sections],
                            "task_title": esc(cfg.de("how.task_title")), "task": esc(cfg.ui("how.task")), "sample_task": sample_task,
                            "task_points": [esc(x) for x in cfg.ui("how.task_points")],
                            "icons_title": esc(cfg.de("how.icons_title")), "icons": esc(cfg.ui("how.icons")),
                            "icon_list": [(r.icon(s, "7mm", cfg.de(f"labels.skills.{s}")), esc(cfg.de(f"labels.skills.{s}")))
                                          for s in ("hoeren", "lesen", "schreiben", "sprechen", "partner", "grammatik")],
                            "colors_title": esc(cfg.de("how.colors_title")), "colors": esc(cfg.ui("how.colors")),
                            "margin_title": esc(cfg.de("how.margin_title")), "margin": esc(cfg.ui("how.margin")),
                            "margin_items": [{"kind": k, "icon": r.icon(k, "4.2mm", cfg.de(f"labels.notes.{k}")), "label": esc(cfg.de(f"labels.notes.{k}")),
                                              "text": esc(cfg.ui(f"how.margin_items.{k}"))} for k in ("tipp", "wort", "landeskunde", "sogehts")]})
        pages.append(PageSpec("p-iv", "front", "front", "iv", "iv", "verso", "c5", str(how1) + '<div class="folio">iv</div>', "", ["p-iv", "how"],
                              [(1, cfg.de("labels.how"), "how")]))
        url = cfg.audio_url("5.01")
        sample_audio = str(r.B.audio({"href": esc(url), "qr": art.qr_svg(url, "QR-Code: Track 5.01", cfg.series["colors"]["ink"]), "label": r.L("track"),
                                      "track": "5.01", "duration": "0:48", "icon": r.icon("hoeren", "3.6mm", cfg.de("labels.skills.hoeren"))}))
        sample_mistake = str(r.B.mistake({"label": r.L("typical_mistake"), "icon": r.icon("fehler", "4.4mm", cfg.de("labels.typical_mistake")),
                                          "cross": r.icon("cross", "3mm", "falsch", 2.4), "check": r.icon("check", "3mm", "richtig", 2.6),
                                          "wrong": esc(cfg.de("how.sample_wrong")), "right": r.de(cfg.de("how.sample_right")),
                                          "why": "", "lang": cfg.lang})).replace('<div class="why" lang="%s"></div>' % cfg.lang, "")
        sample_lines = f'<div class="lines"><span class="hw" lang="de">{esc(cfg.de("how.sample_hand"))}</span><span class="hl"></span><span class="hl"></span></div>'
        heads = [cfg.de("labels.not_yet"), cfg.de("labels.almost"), cfg.de("labels.sure")]
        sample_cando = str(r.B.cando({"title": esc(cfg.de("labels.can_do_start")), "heads": [esc(h).replace(" ", "<br>") for h in heads], "lang": cfg.lang,
                                      "items": [{"de": esc(cfg.de("how.sample_cando")), "ex": "", "ref": "", "name": "how-cd"}], "forms": False, "refs": False}))
        demo_words = [self.book.vocab[w] for w in list(self.book.vocab)[3:6]] if len(self.book.vocab) >= 6 else list(self.book.vocab.values())[:3]
        sample_words = str(r.B.words_footer({"label": r.L("words_on_page"), "sub": esc(cfg.ui("labels.words_on_page")), "lang": cfg.lang,
                                             "words": [r.word_view(v) for v in demo_words], "more": ""})).replace('class="pw"', 'class="pw pwdemo"')
        how2 = self.P.how2({"lang": cfg.lang,
                            "audio_title": esc(cfg.de("how.audio_title")), "audio": esc(cfg.ui("how.audio")), "sample_audio": sample_audio,
                            "mistake_title": esc(cfg.de("how.mistake_title")), "mistake": esc(cfg.ui("how.mistake")), "sample_mistake": sample_mistake,
                            "hand_title": esc(cfg.de("how.hand_title")), "hand": esc(cfg.ui("how.hand")), "sample_lines": sample_lines,
                            "check_title": esc(cfg.de("how.check_title")), "check": esc(cfg.ui("how.check")), "sample_cando": sample_cando,
                            "words_title": esc(cfg.de("how.words_title")), "words": esc(cfg.ui("how.words")), "sample_words": sample_words,
                            "tips_title": esc(cfg.ui("how.tips_title")), "tips": [esc(t) for t in cfg.ui("how.tips")]})
        pages.append(PageSpec("p-v", "front", "front", "v", "v", "recto", "c5", str(how2) + '<div class="folio">v</div>', "", ["p-v"]))
        # cast
        bios = cfg.series.get("bios", {})
        people = [{"avatar": art.avatar(k, cfg.series["cast"], "24mm", uid="cast"), "name": esc(cfg.series["cast"][k]["full"]),
                   "bio": r.de(b["de"]), "bio_tr": r.inline.ex(b[cfg.lang])} for k, b in bios.items()]
        cast = self.P.cast({"title": esc(cfg.de("labels.cast")), "lang": cfg.lang, "lead": esc(cfg.ui("cast.lead")), "people": people})
        pages.append(PageSpec("p-vi", "front", "front", "vi", "vi", "verso", "cn", str(cast) + '<div class="folio">vi</div>', "", ["p-vi", "cast"],
                              [(1, cfg.de("labels.cast"), "cast")]))
        return pages

    def sales_page(self, side: str) -> PageSpec:
        """Last page. Sample and partial builds sell the full book; a complete book points to the next level."""
        cfg, r = self.cfg, self.r
        S = cfg.series["series"]
        levels = cfg.series["levels"]
        complete = not self.sample and len(self.book.chapters) == cfg.series["structure"]["chapters"]
        nxt = levels[levels.index(cfg.level) + 1] if cfg.level != levels[-1] else None
        if not complete:
            kicker = cfg.ui("sales.kicker") if self.sample else cfg.edition_title()
            title, body, button = cfg.ui("sales.title"), cfg.ui("sales.body", level=cfg.level_name), cfg.ui("sales.button")
            points = cfg.ui("sales.points")
        else:
            kicker, points = cfg.ui("sales.kicker_full", level=cfg.level_name), []
            key = "full" if nxt else "last"
            nx = nxt.upper() if nxt else ""
            title = cfg.ui(f"sales.title_{key}", level=cfg.level_name, next=nx)
            body = cfg.ui(f"sales.body_{key}", level=cfg.level_name, next=nx)
            button = cfg.ui(f"sales.button_{key}", level=cfg.level_name, next=nx)
        minis = []
        for lv in levels:
            lt = cfg.level_tokens(lv)
            minis.append({"name": lv.upper(), "color": lt["cover"], "lite": lt["cover_lite"], "url": esc(S["shop_url"]),
                          "current": lv == (nxt if complete and nxt else cfg.level)})
        title_html = re.sub(r"\b300\b", "<b>300</b>", esc(title)).replace("|", "<br>")
        s = self.P.sales({"lang": cfg.lang, "kicker": esc(kicker), "title": title_html, "body": esc(body),
                          "points": [esc(p) for p in points], "check": r.icon("check", "5mm", "✓", 2.4),
                          "button": esc(button), "arrow": r.icon("arrow", "6mm", "→", 2.2), "shop_url": esc(S["shop_url"]),
                          "shop_text": esc(S["shop_url"].split("//")[1]), "youtube_url": esc(S["youtube_url"]),
                          "yt_icon": r.icon("youtube", "6mm", "YouTube", 1.8), "youtube": esc(cfg.ui("sales.youtube")),
                          "youtube_text": esc(S["youtube_url"].split("//")[1].replace("www.", "")), "series": esc(cfg.ui("sales.series")),
                          "minis": minis, "logo": art.logo(cfg.series["colors"]["navy"])})
        return PageSpec("p-info", "sales", "back", "Info", "", side, "cn", str(s), "sales", ["p-info", "sales"],
                        [(1, strip_tags(title_html.replace("<br>", " ")), "sales")])

    # ── the whole document ───────────────────────────────────────────────────
    def build(self) -> Result:
        cfg, r, book = self.cfg, self.r, self.book
        state = None
        rounds = 0
        for rounds in range(1, 6):
            new = self.layout_round()
            # everything that exists in the build is a valid link target while we iterate
            r.page_of = dict(new["page_of"])
            r.page_of.update({"toc": "iii", "how": "iv", "cast": "vi"})
            r.line_of, r.text_geom = new["line_of"], new["text_geom"]
            r.model_rows = new["model_rows"]
            self.grow = new["grow"]
            r.built = set(r.page_of)
            if new == state:
                break
            state = new
        learn: list[PageSpec] = self._round["learn"]
        appendix: list[PageSpec] = self._round["appendix"]
        issues = list(self._round["issues"])

        # word list (needs the final page numbers)
        wl = self.wordlist_units()
        tw = cfg.text_width_mm
        colw3 = round((tw - 12) / 3, 3)
        if wl:
            geom = measure(cfg, self.css, [(f'<div class="axc wl3" style="position:static;width:{colw3}mm">{h}</div>', colw3) for _, h in wl])
            for cu, _ in wl:
                g = geom.get(cu.uid)
                cu.height = (g[3] - g[1]) if g else self.bl * 0.8
            head_h = self.bl * 8
            pages = flow_columns([cu for cu, _ in wl], 3, lambda pi: self.cap - (head_h if pi == 0 else 0))
            htmls = {cu.uid: h for cu, h in wl}
            for pi, cols_ in enumerate(pages):
                label = f"W {pi + 1}"
                spec = PageSpec("p-" + label.replace(" ", ""), "appendix", "wordlist", label, label, "", "cn",
                                meta={"cols": cols_, "htmls": htmls, "colw": colw3, "ncols": 3, "cls": "wl3", "title_key": "wordlist",
                                      "first": pi == 0, "head_h": head_h, "anchor": "ax-wordlist", "tab": "W", "tabslot": 3})
                spec.anchors = [uid for col in cols_ for uid, _ in col] + (["ax-wordlist"] if pi == 0 else [])
                appendix.append(spec)
                for a in spec.anchors:
                    r.page_of.setdefault(a, label)
                r.page_of[spec.pid] = label

        # choose the pages of this edition
        keep: set[str] = set()
        if self.sample:
            keep = {str(x) for x in cfg.lv.get("sample", {}).get("pages", [])}
            keep_ax = set(cfg.lv.get("sample", {}).get("appendix", []))
            learn = [s for s in learn if s.label in keep]
            appendix = [s for s in appendix if s.label in keep_ax]
        # anchors that exist → live links
        r.built = {"toc", "how", "cast", "p-cover", "p-ii", "p-iii", "p-iv", "p-v", "p-vi", "sales", "p-info"}
        for s in learn + appendix:
            r.built.update(s.anchors)
            r.built.add(s.pid)
        # final render of all units with the definitive registries
        self.final_units()
        learn_final = [s for s in self._round["learn"] if (not self.sample or s.label in keep)]
        for s in learn_final:
            self.compose_learning(s)
        # appendix htmls were rendered in final_units (answers) – refresh them
        ans_html = {cu.uid: h for cu, h in self.answer_units()}
        trs_html = {cu.uid: h for cu, h in self.transcript_units()}
        wl_html = {cu.uid: h for cu, h in self.wordlist_units()}
        side = "recto"
        seq: list[PageSpec] = []
        fronts = self.front_pages()
        seq += fronts
        seq += learn_final
        prev_side = seq[-1].side if seq else "verso"
        for s in appendix:
            s.side = "verso" if prev_side == "recto" else "recto"
            prev_side = s.side
            src = {"answers": ans_html, "transcripts": trs_html, "wordlist": wl_html}[s.group]
            s.meta["htmls"] = src
            self.compose_appendix(s)
            seq.append(s)
        seq.append(self.sales_page("verso" if prev_side == "recto" else "recto"))
        if r.inline.unresolved:
            for u in sorted(set(r.inline.unresolved)):
                issues.append(("error", "cross-reference", f"cannot resolve {u}"))
        for lvl, where, msg in issues:
            (book.err if lvl == "error" else book.warn)(where, msg)

        body = "".join(str(self.P.shell({"print": self.print, "marks": self.marks(s), "side": s.side, "palette": s.palette, "cls": s.cls,
                                         "id": s.pid, "inner": s.inner})) for s in seq)
        S = cfg.series["series"]
        title = f'{cfg.edition_title()} – {cfg.ui("cover.explanations")}'
        if self.sample:
            title += f' ({cfg.ui("labels.free_sample")})'
        head = (f'<meta charset="utf-8"><title>{esc(title)}</title><meta name="author" content="{esc(S["author"])}">'
                f'<meta name="description" content="{esc(cfg.ui("toc.intro", level=cfg.level_name))}">'
                f'<meta name="keywords" content="Deutsch, German, {cfg.level_name}, Kursbuch, Deutsch Fokus, 300">'
                f'<meta name="generator" content="300 Pages engine {S["version"]}">'
                f'<meta name="dcterms.created" content="{_dt.date.today().isoformat()}">')
        doc = f'<!DOCTYPE html><html lang="de-DE"><head>{head}<style>{self.css}</style></head><body class="{"print" if self.print else "digital"}">{body}</body></html>'
        stats = {"learning_pages": len(learn_final), "pages": len(seq), "tasks": len(book.tasks), "vocab": len(book.vocab),
                 "tracks": len(book.tracks), "rounds": rounds}
        return Result(doc, seq, self.css, rounds, title, stats)

    def final_units(self) -> None:
        """Re-render every unit with final page numbers / links and put the fresh HTML into the placed units."""
        r = self.r
        r.grow = dict(self.grow)
        r._seen_types = set()
        r.answers = {}
        r.inline.unresolved = []
        fresh: dict[str, Unit] = {}
        for p in self.book.parts():
            op, flow = self.part_units(p)
            for u in op + flow:
                fresh[u.uid] = u
        for s in self._round["learn"]:
            if s.kind == "opener":
                s.meta["units"] = [fresh[u.uid] for u in s.meta["units"]]
            else:
                for pl in s.flow.placed:
                    h = pl.unit.height
                    pl.unit = fresh[pl.unit.uid]
                    pl.unit.height = h

    def marks(self, s: PageSpec) -> str:
        if not self.print:
            return ""
        pg = self.cfg.page
        o = pg["slug"] + pg["bleed"]                     # trim offset
        W, H = pg["width"], pg["height"]
        L = 5.0                                          # mark length
        g = pg["slug"] - L - 0.5
        out = []
        for x in (o, o + W):
            out.append(f'<div class="crop" style="left:{x - 0.044:.3f}mm;top:{g:.2f}mm;width:.088mm;height:{L}mm"></div>')
            out.append(f'<div class="crop" style="left:{x - 0.044:.3f}mm;top:{o + H + pg["bleed"] + 0.5:.2f}mm;width:.088mm;height:{L}mm"></div>')
        for y in (o, o + H):
            out.append(f'<div class="crop" style="top:{y - 0.044:.3f}mm;left:{g:.2f}mm;height:.088mm;width:{L}mm"></div>')
            out.append(f'<div class="crop" style="top:{y - 0.044:.3f}mm;left:{o + W + pg["bleed"] + 0.5:.2f}mm;height:.088mm;width:{L}mm"></div>')
        slug = f'<div class="slugline">{self.cfg.level_name}-{self.cfg.lang.upper()} · {s.label} · {_dt.date.today().isoformat()}</div>'
        return "".join(out) + slug
