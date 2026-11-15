"""Measure → paginate.

WeasyPrint lays out every unit once on a tall scratch page so we learn its exact
height. Pagination itself is done here in Python, which gives us things CSS
cannot: every block starts on the baseline grid, pages are filled to the last
line where possible, write-in areas grow into spare room, and each section is
checked against its page budget.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Optional

from weasyprint import HTML

from .config import MM, Config
from .render import Unit

PT_PER_PX = 0.75


def measure(cfg: Config, css: str, items: list[tuple[str, float]]) -> dict[str, tuple[float, float, float, float]]:
    """Lay out `items` [(html, width_mm)] one per scratch page; return the box of every element with an id (pt)."""
    pages = "".join(f'<div class="mpage"><div class="m" style="width:{w}mm">{h}</div></div>' for h, w in items)
    doc = (f'<html lang="de"><head><meta charset="utf-8"><style>{css}\n@page{{size:240mm 700mm;margin:0}}'
           f'.mpage{{padding:6mm}}</style></head><body>{pages}</body></html>')
    rendered = HTML(string=doc, base_url=str(cfg.root)).render()
    geom: dict[str, tuple[float, float, float, float]] = {}
    for page in rendered.pages:
        for name, box in page.anchors.items():
            geom[name] = tuple(v * PT_PER_PX for v in box)  # type: ignore[assignment]
    return geom


@dataclass
class Placed:
    unit: Unit
    top: float            # pt from the top of the text block


@dataclass
class FlowPage:
    placed: list[Placed] = field(default_factory=list)
    used: float = 0.0
    leftover: float = 0.0
    overflow: float = 0.0
    filled: bool = False  # True if the page could be justified to the last line
    natural: float = 0.0  # height used before elastic growth and gap opening


def _snap(y: float, step: float) -> float:
    return math.ceil((y - 0.05) / step) * step


def paginate(units: list[Unit], cap: float, bl: float, gap: float = 1.0) -> list[FlowPage]:
    """Fill pages top to bottom. Every unit starts on a half-baseline; a heading never ends a page."""
    half = bl / 2
    pages: list[FlowPage] = []
    cur = FlowPage()
    y = 0.0
    for i, u in enumerate(units):
        need = u.height
        if u.keep_next and i + 1 < len(units):
            need += gap * bl + units[i + 1].height
        top = _snap(y, half)
        if cur.placed and (u.break_before or top + need > cap + 0.6):
            pages.append(cur)
            cur, top = FlowPage(), 0.0
        cur.placed.append(Placed(u, top))
        y = top + u.height + gap * bl
    if cur.placed:
        pages.append(cur)
    for p in pages:
        _finish(p, cap)
        p.natural = p.used
    return pages


def paginate_fit(units: list[Unit], cap: float, bl: float, pages: int, elastic: dict[str, tuple[float, int]],
                 gap: float = 1.0, max_gap_steps: int = 2) -> tuple[Optional[list[FlowPage]], int]:
    """Break `units` into exactly `pages` pages – the way a typesetter would for a chapter with a fixed length.

    Of all the ways to do it, the one is chosen where the spare room is spread best: first it goes to
    elements that can grow (write-in lines, pictures), then to the gaps, and whatever is left counts
    heavily. The same rules as in paginate() hold: a heading never ends a page, units with
    break_before start one. Returns (pages, minimum number of pages); pages is None if the units do
    not fit into the wanted number of pages or cannot be spread over that many.
    """
    half = bl / 2
    n = len(units)
    inf = float("inf")
    cand: list[list[tuple[int, float, float]]] = [[] for _ in range(n)]   # start → [(end, used, growth capacity)]
    for i in range(n):
        y, cap_grow = 0.0, 0.0
        for j in range(i, n):
            u = units[j]
            if j > i and u.break_before:
                break
            used = _snap(y, half) + u.height
            if used > cap + 0.6 and j > i:
                break
            cap_grow += sum(elastic[g][0] * elastic[g][1] for g in u.grow_ids if g in elastic)
            y = used + gap * bl
            if not (u.keep_next and j + 1 < n and not units[j + 1].break_before):
                cand[i].append((j + 1, used, cap_grow))
            if used > cap + 0.6:
                break                                  # a single unit that is taller than the page stays alone

    def cost(i: int, j: int, used: float, cap_grow: float) -> float:
        left = max(0.0, cap - used)
        rest = max(0.0, left - cap_grow)                                   # elastic elements cannot take this
        rest2 = max(0.0, rest - (j - i - 1) * max_gap_steps * half)        # … and opening the gaps cannot either
        c = (left / cap) ** 2 + 6 * (rest / cap) ** 2 + 40 * (rest2 / cap) ** 2
        return c * (0.4 if j == n or units[j].break_before else 1.0)        # a section may end short

    best = [[inf] * (n + 1) for _ in range(pages + 1)]
    prev = [[-1] * (n + 1) for _ in range(pages + 1)]
    best[0][0] = 0.0
    for p in range(1, pages + 1):
        for i in range(n):
            b0 = best[p - 1][i]
            if b0 == inf:
                continue
            for j, used, cap_grow in cand[i]:
                c = b0 + cost(i, j, used, cap_grow)
                if c < best[p][j]:
                    best[p][j], prev[p][j] = c, i
    minimum = len(paginate(units, cap, bl, gap))
    if n == 0 or best[pages][n] == inf:
        return None, minimum
    cuts = [n]
    for p in range(pages, 0, -1):
        cuts.append(prev[p][cuts[-1]])
    cuts.reverse()
    out: list[FlowPage] = []
    for a, b in zip(cuts, cuts[1:]):
        fp, y = FlowPage(), 0.0
        for u in units[a:b]:
            top = _snap(y, half)
            fp.placed.append(Placed(u, top))
            y = top + u.height + gap * bl
        _finish(fp, cap)
        fp.natural = fp.used
        out.append(fp)
    return out, minimum


def _finish(p: FlowPage, cap: float) -> None:
    last = p.placed[-1]
    p.used = last.top + last.unit.height
    p.leftover = max(0.0, cap - p.used)
    p.overflow = max(0.0, p.used - cap)


def justify(p: FlowPage, cap: float, bl: float, elastic: dict[str, tuple[float, int]], grow: dict[str, int],
            max_gap_steps: int = 2, gap: float = 1.0) -> None:
    """Use spare room: first let elastic elements grow (write-in lines, illustration slots), then open
    the gaps evenly — but only if that fills the page exactly. Otherwise the natural rhythm is kept.

    elastic: id → (step in pt, maximum number of steps)
    """
    half = bl / 2

    def reflow() -> None:
        y = 0.0
        for pl in p.placed:
            pl.top = _snap(y, half)
            y = pl.top + pl.unit.height + gap * bl
        _finish(p, cap)

    growable = [(pl, gid) for pl in p.placed for gid in pl.unit.grow_ids if gid in elastic]
    progress = True
    while growable and progress:
        progress = False
        for pl, gid in growable:
            step, limit = elastic[gid]
            if grow.get(gid, 0) >= limit or p.leftover < step + 0.5:
                continue
            pl.unit.height += step
            grow[gid] = grow.get(gid, 0) + 1
            reflow()
            if p.overflow > 0.6:                  # snapping pushed us over: take the step back
                pl.unit.height -= step
                grow[gid] -= 1
                reflow()
                continue
            progress = True
    gaps = len(p.placed) - 1
    steps = int((p.leftover + 0.3) // half)
    if gaps <= 0 or steps <= 0:
        return
    room = [max_gap_steps * (2 if pl.unit.kind in ("blk", "teil", "head") else 1) for pl in p.placed[1:]]
    if steps > sum(room):
        return                                    # cannot fill the page: keep natural spacing
    extra = [0] * gaps
    todo = steps
    while todo > 0:                               # one half-line at a time, bottom-up, headings first
        order = sorted(range(gaps), key=lambda g: (extra[g] / room[g], -g))
        for g in order:
            if todo and extra[g] < room[g]:
                extra[g] += 1
                todo -= 1
                break
    shift = 0.0
    for idx, pl in enumerate(p.placed):
        if idx > 0:
            shift += extra[idx - 1] * half
        pl.top += shift
    _finish(p, cap)
    p.filled = p.leftover < half


@dataclass
class ColUnit:
    uid: str
    height: float
    keep_next: bool = False
    gap_after: float = 0.0


def flow_columns(units: list[ColUnit], cols: int, cap_of: Callable[[int], float]) -> list[list[list[tuple[str, float]]]]:
    """Flow units into `cols` columns per page. cap_of(page_index) → usable column height (pt).
    Returns pages → columns → [(uid, top)]."""
    pages: list[list[list[tuple[str, float]]]] = [[[] for _ in range(cols)]]
    pi, ci, y = 0, 0, 0.0
    for i, u in enumerate(units):
        need = u.height
        if u.keep_next and i + 1 < len(units):
            need += u.gap_after + units[i + 1].height
        if y > 0 and y + need > cap_of(pi) + 0.6:
            ci += 1
            y = 0.0
            if ci >= cols:
                pi += 1
                ci = 0
                pages.append([[] for _ in range(cols)])
        pages[pi][ci].append((u.uid, y))
        y += u.height + u.gap_after
    return pages
