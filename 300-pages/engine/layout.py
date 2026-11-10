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
    if steps > gaps * max_gap_steps:
        return                                    # cannot fill the page: keep natural spacing
    extra = [steps // gaps] * gaps
    for j in range(steps - sum(extra)):
        extra[gaps - 1 - j] += 1                  # remainder goes to the lower gaps
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
