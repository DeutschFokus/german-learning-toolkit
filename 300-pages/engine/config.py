"""Configuration: series.yaml + levels/<level>.yaml + i18n/<lang>.yaml → one Config object.

All design tokens (colours, sizes, page geometry) are derived here, so templates
never contain a literal colour or a magic number.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .colors import contrast, oklch

ROOT = Path(__file__).resolve().parent.parent
MM = 72 / 25.4          # points per millimetre
PX = 96 / 72            # CSS px per point (WeasyPrint reports anchors in px)


def load_yaml(path: Path) -> Any:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


class Strings:
    """Dot-access to a nested dict of UI strings with a readable error for missing keys."""

    def __init__(self, data: dict, name: str):
        self._d, self._n = data, name

    def __call__(self, key: str, **fmt) -> str:
        node: Any = self._d
        for part in key.split("."):
            if not isinstance(node, dict) or part not in node:
                raise KeyError(f"i18n/{self._n}.yaml: missing string '{key}'")
            node = node[part]
        return node.format(**fmt) if fmt and isinstance(node, str) else node

    def has(self, key: str) -> bool:
        try:
            self(key)
            return True
        except KeyError:
            return False


@dataclass
class Config:
    level: str
    lang: str
    series: dict
    lv: dict
    de: Strings
    ui: Strings
    root: Path = ROOT
    flags: dict = field(default_factory=dict)       # print / forms / sample / draft

    # ── basic facts ───────────────────────────────────────────────────────────
    @property
    def langs(self) -> list[str]:
        return self.series["languages"]

    @property
    def page(self) -> dict:
        return self.series["page"]

    @property
    def level_name(self) -> str:
        return self.lv["name"]

    @property
    def bl(self) -> float:
        """Baseline unit in points."""
        return float(self.lv["type"]["baseline"])

    @property
    def body_lines(self) -> int:
        return int(self.lv["type"]["body_lines"])

    @property
    def body_height_pt(self) -> float:
        return self.body_lines * self.bl

    @property
    def text_width_mm(self) -> float:
        p = self.page
        return p["width"] - p["inner"] - p["outer"]

    # ── structure ─────────────────────────────────────────────────────────────
    @property
    def sections(self) -> list[dict]:
        return self.series["structure"]["sections"]

    def section(self, sid: str) -> dict:
        return next(s for s in self.sections if s["id"] == sid)

    @property
    def chapter_pages(self) -> int:
        return sum(s["pages"] for s in self.sections)

    def chapter_start(self, n: int) -> int:
        """Folio of the first page of chapter n (1-based)."""
        st = self.series["structure"]
        stations_before = sum(1 for a in st["stations_after"] if a < n)
        return 1 + (n - 1) * self.chapter_pages + stations_before * st["station_pages"]

    def station_start(self, k: int) -> int:
        """Folio of the first page of review station k (1-based)."""
        st = self.series["structure"]
        after = st["stations_after"][k - 1]
        return 1 + after * self.chapter_pages + (k - 1) * st["station_pages"]

    def section_start(self, chapter: int, sid: str) -> int:
        folio = self.chapter_start(chapter)
        for s in self.sections:
            if s["id"] == sid:
                return folio
            folio += s["pages"]
        raise KeyError(sid)

    @property
    def total_pages(self) -> int:
        st = self.series["structure"]
        return st["chapters"] * self.chapter_pages + len(st["stations_after"]) * st["station_pages"]

    # ── colour tokens ─────────────────────────────────────────────────────────
    def level_hue(self, level: str | None = None) -> float:
        if level and level != self.level:
            return float(load_yaml(self.root / "levels" / f"{level}.yaml")["hue"])
        return float(self.lv["hue"])

    def chapter_hue(self, k: int, level: str | None = None) -> float:
        spread = self.series["colors"]["chapter"]["spread"]
        n = self.series["structure"]["chapters"]
        return (self.level_hue(level) + spread - (k - 0.5) * (2 * spread / n)) % 360

    def chapter_tokens(self, k: int, level: str | None = None) -> dict[str, str]:
        c = self.series["colors"]["chapter"]
        h = self.chapter_hue(k, level)
        m = c["mid"]
        l_mid = m["l"] + m["l_swing"] * math.cos(math.radians(h - m["l_peak_hue"]))
        return {
            "mid": oklch(l_mid, m["c"], h),
            "soft": oklch(c["soft"]["l"], c["soft"]["c"], h),
            "wash": oklch(c["wash"]["l"], c["wash"]["c"], h),
            "hl": oklch(c["hl"]["l"], c["hl"]["c"], h),
            "strong": oklch(c["strong"]["l"], c["strong"]["c"], h),
            "deep": oklch(c["deep"]["l"], c["deep"]["c"], h),
        }

    def station_tokens(self) -> dict[str, str]:
        """Review stations use the navy of the series instead of a chapter tint."""
        c = self.series["colors"]
        h = 268
        return {"mid": oklch(0.80, 0.07, h), "soft": oklch(0.94, 0.025, h), "wash": oklch(0.972, 0.012, h),
                "hl": oklch(0.87, 0.06, h), "strong": oklch(0.42, 0.10, h), "deep": c["navy"]}

    def level_tokens(self, level: str | None = None) -> dict[str, str]:
        lv = self.lv if not level or level == self.level else load_yaml(self.root / "levels" / f"{level}.yaml")
        L, C, h = lv["cover"]
        cream = self.series["colors"]["cream"]
        d = 0.05                                   # the lighter "sun": as light as it can be while the cream 300 keeps 3:1 on it
        while d > 0.01 and contrast(cream, oklch(L + d, C, h)) < 3.0:
            d -= 0.0025
        return {"cover": oklch(L, C, h), "cover_lite": oklch(L + d, C, h), "cover_deep": oklch(L - 0.07, C, h),
                "bright": oklch(min(0.80, L + 0.14), C, h)}

    @property
    def article_colors(self) -> dict[str, str]:
        return {k: oklch(*v) for k, v in self.series["colors"]["articles"].items()}

    @property
    def article_tints(self) -> dict[str, str]:
        t = self.series["colors"]["article_tint"]
        return {k: oklch(t["l"], t["c"], v[2]) for k, v in self.series["colors"]["articles"].items()}

    @property
    def note_colors(self) -> dict[str, str]:
        return {k: oklch(*v) for k, v in self.series["colors"]["notes"].items()}

    def base_tokens(self) -> dict[str, str]:
        c = self.series["colors"]
        out = {k: v for k, v in c.items() if isinstance(v, str)}
        out.update(self.article_colors)
        out.update({f"{k}_tint": v for k, v in self.article_tints.items()})
        out.update({f"n_{k}": v for k, v in self.note_colors.items()})
        return out

    # ── i18n helpers ──────────────────────────────────────────────────────────
    def t(self, loc: Any) -> str:
        """Pick the edition language out of a {en: …, tr: …} mapping (or pass strings through)."""
        if loc is None:
            return ""
        if isinstance(loc, str):
            return loc
        if hasattr(loc, "root"):
            loc = loc.root
        return loc[self.lang]

    def audio_url(self, track: str) -> str:
        return self.series["series"]["audio_url"].format(level=self.level, track=track)

    def edition_title(self) -> str:
        return self.ui("cover.title", level=self.level_name)

    def contrast_table(self) -> list[tuple[str, str, str, float, str]]:
        """Rows for the QA report: (name, fg, bg, ratio, requirement)."""
        base = self.base_tokens()
        rows = []
        for a in ("der", "die", "das", "pl"):
            rows.append((f"article {a} on paper", base[a], base["paper"], contrast(base[a], base["paper"]), "4.5"))
            rows.append((f"article {a} on its tint", base[a], base[f"{a}_tint"], contrast(base[a], base[f"{a}_tint"]), "4.5"))
        for n in ("tipp", "wort", "landeskunde", "sogehts"):
            rows.append((f"note {n} label on paper", base[f"n_{n}"], base["paper"], contrast(base[f"n_{n}"], base["paper"]), "4.5"))
        rows.append(("body ink on paper", base["ink"], base["paper"], contrast(base["ink"], base["paper"]), "4.5"))
        rows.append(("muted text on paper", base["mute"], base["paper"], contrast(base["mute"], base["paper"]), "4.5"))
        rows.append(("handwriting ink on paper", base["pen"], base["paper"], contrast(base["pen"], base["paper"]), "4.5"))
        for k in range(1, self.series["structure"]["chapters"] + 1):
            t = self.chapter_tokens(k)
            rows.append((f"chapter {k}: ink on mid (tab, chips)", base["ink"], t["mid"], contrast(base["ink"], t["mid"]), "4.5"))
            rows.append((f"chapter {k}: ink on wash (boxes)", base["ink"], t["wash"], contrast(base["ink"], t["wash"]), "4.5"))
            rows.append((f"chapter {k}: muted on wash", base["mute"], t["wash"], contrast(base["mute"], t["wash"]), "4.5"))
            rows.append((f"chapter {k}: ink on highlight", base["ink"], t["hl"], contrast(base["ink"], t["hl"]), "4.5"))
            rows.append((f"chapter {k}: deep on paper (labels)", t["deep"], base["paper"], contrast(t["deep"], base["paper"]), "4.5"))
            rows.append((f"chapter {k}: deep on soft (pointer)", t["deep"], t["soft"], contrast(t["deep"], t["soft"]), "4.5"))
        for lv in self.series["levels"]:                 # every cover of the series, not only this level
            lt = self.level_tokens(lv)
            rows.append((f"cover {lv.upper()}: cream on level field (large type)", base["cream"], lt["cover"], contrast(base["cream"], lt["cover"]), "3.0"))
            rows.append((f"cover {lv.upper()}: cream 300 on the lighter circle", base["cream"], lt["cover_lite"], contrast(base["cream"], lt["cover_lite"]), "3.0"))
        rows.append(("cover: navy on cream band", base["navy"], base["cream"], contrast(base["navy"], base["cream"]), "4.5"))
        rows.append(("cover: cream on navy badge", base["cream"], base["navy"], contrast(base["cream"], base["navy"]), "4.5"))
        return rows


def load_config(level: str, lang: str, **flags) -> Config:
    series = load_yaml(ROOT / "series.yaml")
    if level not in series["levels"]:
        raise SystemExit(f"Unknown level '{level}'. Known: {', '.join(series['levels'])}")
    if lang not in series["languages"]:
        raise SystemExit(f"Unknown language '{lang}'. Known: {', '.join(series['languages'])}")
    lv = load_yaml(ROOT / "levels" / f"{level}.yaml")
    de = Strings(load_yaml(ROOT / "i18n" / "de.yaml"), "de")
    ui = Strings(load_yaml(ROOT / "i18n" / f"{lang}.yaml"), lang)
    return Config(level=level, lang=lang, series=series, lv=lv, de=de, ui=ui, flags=flags)
