"""Hand-drawn vector illustrations in the house style: flat shapes, no outlines, chapter palette.

Small building blocks (person, plant, box) so scenes stay consistent with the cast in series.yaml.
    python -m engine.illustrate        # writes assets/images/a2/*.svg
"""
from __future__ import annotations

from pathlib import Path

NAVY = "#1B1E2F"


def person(x: float, ground: float, h: float, skin: str, hair: str, top: str, legs: str = NAVY, style: str = "long",
           beard: str | None = None, moustache: str | None = None, pose: str = "stand", flip: bool = False, glasses: bool = False) -> str:
    """A figure standing on `ground`, centred on x, total height h. pose: stand | carry | offer | wave."""
    u = h / 100.0                                   # 100 units tall
    hr = 8.6 * u                                    # head radius
    hy = ground - h + hr
    sh_y = hy + hr + 2.5 * u                        # shoulder line
    hip = ground - 44 * u
    tw = 15 * u                                     # half torso width
    o = []
    # legs and shoes
    for dx in (-6.2, 6.2):
        o.append(f'<rect x="{x + dx * u - 4.4 * u:.1f}" y="{hip - 2 * u:.1f}" width="{8.8 * u:.1f}" height="{44 * u:.1f}" rx="{4.2 * u:.1f}" fill="{legs}"/>')
        o.append(f'<path d="M{x + dx * u - 5.2 * u:.1f} {ground:.1f}h{13 * u:.1f}a{5 * u:.1f} {5 * u:.1f} 0 0 0 -{5 * u:.1f} -{5 * u:.1f}h-{8 * u:.1f}z" fill="{NAVY}"/>')
    # back hair
    if style == "long":
        o.append(f'<path d="M{x - hr * 1.15:.1f} {hy:.1f}a{hr * 1.15:.1f} {hr * 1.15:.1f} 0 0 1 {hr * 2.3:.1f} 0v{22 * u:.1f}q-{hr * 1.15:.1f} {6 * u:.1f} -{hr * 2.3:.1f} 0z" fill="{hair}"/>')
    if style == "scarf":
        o.append(f'<path d="M{x - hr * 1.2:.1f} {hy:.1f}a{hr * 1.2:.1f} {hr * 1.2:.1f} 0 0 1 {hr * 2.4:.1f} 0v{hr * 1.9:.1f}h-{hr * 2.4:.1f}z" fill="{hair}"/>')
    # torso
    o.append(f'<path d="M{x - tw:.1f} {hip + 3 * u:.1f}v-{(hip - sh_y) - 6 * u:.1f}a{9 * u:.1f} {9 * u:.1f} 0 0 1 {9 * u:.1f} -{9 * u:.1f}h{2 * tw - 18 * u:.1f}a{9 * u:.1f} {9 * u:.1f} 0 0 1 {9 * u:.1f} {9 * u:.1f}v{(hip - sh_y) - 6 * u:.1f}z" fill="{top}"/>')
    # neck and head
    o.append(f'<rect x="{x - 3.4 * u:.1f}" y="{hy + hr - 2 * u:.1f}" width="{6.8 * u:.1f}" height="{7 * u:.1f}" fill="{skin}"/>')
    o.append(f'<circle cx="{x:.1f}" cy="{hy:.1f}" r="{hr:.1f}" fill="{skin}"/>')
    # front hair
    if style in ("long", "short"):
        o.append(f'<path d="M{x - hr * 1.02:.1f} {hy - 1 * u:.1f}a{hr * 1.02:.1f} {hr * 1.02:.1f} 0 0 1 {hr * 2.04:.1f} 0q-{hr * .5:.1f} -{hr * .75:.1f} -{hr * 1.3:.1f} -{hr * .55:.1f}q-{hr * .5:.1f} {hr * .1:.1f} -{hr * .74:.1f} {hr * .55:.1f}z" fill="{hair}"/>')
    if style == "scarf":                           # the scarf frames the face and covers the neck
        o.append(f'<path d="M{x - hr * 1.05:.1f} {hy + hr * .1:.1f}a{hr * 1.05:.1f} {hr * 1.05:.1f} 0 0 1 {hr * 2.1:.1f} 0q-{hr * .25:.1f} -{hr * .95:.1f} -{hr * 1.05:.1f} -{hr * .95:.1f}q-{hr * .8:.1f} 0 -{hr * 1.05:.1f} {hr * .95:.1f}z" fill="{hair}"/>')
        o.append(f'<path d="M{x - hr * .95:.1f} {hy + hr * .55:.1f}q{hr * .95:.1f} {hr * .9:.1f} {hr * 1.9:.1f} 0l{hr * .2:.1f} {hr * 1.05:.1f}h-{hr * 2.3:.1f}z" fill="{hair}"/>')
    if moustache:
        o.append(f'<path d="M{x - hr * .42:.1f} {hy + hr * .34:.1f}q{hr * .21:.1f} -{hr * .2:.1f} {hr * .42:.1f} 0q{hr * .21:.1f} -{hr * .2:.1f} {hr * .42:.1f} 0q-{hr * .21:.1f} {hr * .2:.1f} -{hr * .42:.1f} {hr * .06:.1f}q-{hr * .21:.1f} {hr * .14:.1f} -{hr * .42:.1f} -{hr * .06:.1f}z" fill="{moustache}"/>')
    if beard:
        o.append(f'<path d="M{x - hr * .86:.1f} {hy + hr * .2:.1f}q{hr * .86:.1f} {hr * 1.5:.1f} {hr * 1.72:.1f} 0q0 {hr * .95:.1f} -{hr * .86:.1f} {hr * .98:.1f}q-{hr * .86:.1f} -{hr * .03:.1f} -{hr * .86:.1f} -{hr * .98:.1f}z" fill="{beard}"/>')
    # face
    ex = hr * .36
    for s in (-1, 1):
        o.append(f'<circle cx="{x + s * ex:.1f}" cy="{hy + hr * .08:.1f}" r="{hr * .095:.1f}" fill="{NAVY}"/>')
    o.append(f'<path d="M{x - hr * .26:.1f} {hy + hr * .42:.1f}q{hr * .26:.1f} {hr * .26:.1f} {hr * .52:.1f} 0" fill="none" stroke="{NAVY if not beard else "#fff"}" stroke-width="{hr * .09:.1f}" stroke-linecap="round"/>')
    if glasses:
        for s in (-1, 1):
            o.append(f'<circle cx="{x + s * ex:.1f}" cy="{hy + hr * .08:.1f}" r="{hr * .27:.1f}" fill="none" stroke="{NAVY}" stroke-width="{hr * .07:.1f}"/>')
    # arms
    aw = 7.6 * u
    def arm(x0, y0, x1, y1, col):
        return (f'<path d="M{x0:.1f} {y0:.1f}L{x1:.1f} {y1:.1f}" stroke="{col}" stroke-width="{aw:.1f}" stroke-linecap="round" fill="none"/>'
                f'<circle cx="{x1:.1f}" cy="{y1:.1f}" r="{aw * .56:.1f}" fill="{skin}"/>')
    sy = sh_y + 5 * u
    if pose == "stand":
        o.append(arm(x - tw + 2 * u, sy, x - tw - 2 * u, hip - 2 * u, top)); o.append(arm(x + tw - 2 * u, sy, x + tw + 2 * u, hip - 2 * u, top))
    elif pose == "carry":                           # both hands under a box in front of the body
        o.append(arm(x - tw + 2 * u, sy, x - tw - 1 * u, hip - 14 * u, top)); o.append(arm(x + tw - 2 * u, sy, x + tw + 1 * u, hip - 14 * u, top))
    elif pose == "offer":                           # one arm forward holding something, other relaxed
        d = -1 if flip else 1
        o.append(arm(x - d * (tw - 2 * u), sy, x - d * (tw + 2 * u), hip - 2 * u, top))
        o.append(arm(x + d * (tw - 2 * u), sy, x + d * (tw + 13 * u), sy + 13 * u, top))
    return "".join(o)


def box(x: float, y: float, w: float, h: float, col: str, dark: str) -> str:
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{w * .04:.1f}" fill="{col}"/>'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h * .2:.1f}" rx="{w * .04:.1f}" fill="{dark}"/>'
            f'<rect x="{x + w * .44:.1f}" y="{y:.1f}" width="{w * .12:.1f}" height="{h * .42:.1f}" fill="#fff" fill-opacity=".55"/>')


def plant(x: float, y: float, s: float, pot: str, leaf: str, leaf2: str) -> str:
    """Pot centred on x with its top edge at y."""
    o = []
    for ang, col, ln in ((-38, leaf, 1.0), (0, leaf2, 1.25), (36, leaf, 1.05), (-70, leaf2, .75), (68, leaf2, .8)):
        o.append(f'<ellipse cx="{x:.1f}" cy="{y - s * .62 * ln:.1f}" rx="{s * .2:.1f}" ry="{s * .62 * ln:.1f}" fill="{col}" transform="rotate({ang} {x:.1f} {y:.1f})"/>')
    o.append(f'<path d="M{x - s * .42:.1f} {y:.1f}h{s * .84:.1f}l-{s * .1:.1f} {s * .7:.1f}h-{s * .64:.1f}z" fill="{pot}"/>')
    return "".join(o)


def k5_auftakt(t: dict) -> str:
    """Elif with a moving box in her empty living room; Herr Berger at the door with a plant. 2160 × 960."""
    W, H = 2160, 960
    shade = "#F7B77F"                               # the one darker tone
    g = 800                                         # floor line
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
         f'<rect width="{W}" height="{H}" fill="{t["soft"]}"/>',
         f'<rect y="{g}" width="{W}" height="{H - g}" fill="{t["hl"]}"/>',
         # window: arch with evening sky, sun and rooftops
         f'<rect x="796" y="96" width="548" height="704" rx="14" fill="#fff"/>',
         f'<rect x="820" y="120" width="500" height="680" fill="{t["wash"]}"/>',
         f'<circle cx="1150" cy="330" r="140" fill="{t["mid"]}"/>',
         f'<path d="M820 800V560l90-70 90 70v-90h80v-60l110 70v120l130-90v290z" fill="{shade}"/>',
         f'<path d="M820 800V660l130-80 110 80 60-40 200 110v70z" fill="{t["hl"]}"/>',
         f'<rect x="1062" y="120" width="16" height="680" fill="#fff"/><rect x="820" y="452" width="500" height="16" fill="#fff"/>',
         # light on the floor
         f'<path d="M800 800h540l190 160H560z" fill="{t["wash"]}" fill-opacity=".7"/>',
         # doorway on the right
         f'<path d="M1720 800V300a170 170 0 0 1 340 0v500z" fill="{shade}"/>',
         f'<path d="M1750 800V306a140 140 0 0 1 280 0v494z" fill="{t["wash"]}"/>',
         # boxes on the floor
         box(1420, 660, 190, 140, t["mid"], "#E08400"), box(1450, 548, 140, 112, t["hl"], shade),
         # Herr Berger, the caretaker, in the doorway, holding the plant towards Elif
         person(1900, 812, 500, "#D9A074", "#1E1512", "#F07F13", legs=NAVY, style="short", moustache="#1E1512", pose="offer", flip=True),
         plant(1752, 548, 96, t["deep"], "#3F7D6A", "#5FA28D"),
         # Elif with a box
         person(1180, 836, 520, "#F2C9A6", "#12827B", "#12827B", legs="#12827B", style="scarf", pose="carry"),
         box(1085, 560, 190, 130, t["mid"], "#E08400"),
         '</svg>']
    return "".join(o)


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from engine.config import load_config
    cfg = load_config("a2", "en")
    out = cfg.root / "assets" / "images" / "a2"
    out.mkdir(parents=True, exist_ok=True)
    (out / "k5-auftakt.svg").write_text(k5_auftakt(cfg.chapter_tokens(5)), encoding="utf-8")
    print("written", out / "k5-auftakt.svg")
