"""OKLCH → sRGB with gamut mapping, plus WCAG contrast. No dependencies."""
from __future__ import annotations
import math


def _lin(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _gam(c: float) -> float:
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055


def _oklch_to_linear(L: float, C: float, h: float) -> tuple[float, float, float]:
    a = C * math.cos(math.radians(h))
    b = C * math.sin(math.radians(h))
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)


def _in_gamut(rgb, eps: float = 1e-4) -> bool:
    return all(-eps <= c <= 1 + eps for c in rgb)


def oklch(L: float, C: float, h: float) -> str:
    """Hex colour for an OKLCH triplet. Chroma is reduced until the colour fits sRGB."""
    lo, hi = 0.0, C
    if _in_gamut(_oklch_to_linear(L, C, h)):
        lo = C
    else:
        for _ in range(24):
            mid = (lo + hi) / 2
            if _in_gamut(_oklch_to_linear(L, mid, h)):
                lo = mid
            else:
                hi = mid
    r, g, b = (min(1.0, max(0.0, _gam(min(1.0, max(0.0, c))))) for c in _oklch_to_linear(L, lo, h))
    return "#%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))


def hex_to_rgb(hx: str) -> tuple[float, float, float]:
    hx = hx.lstrip("#")
    return tuple(int(hx[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def luminance(hx: str) -> float:
    r, g, b = (_lin(c) for c in hex_to_rgb(hx))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    """WCAG 2.x contrast ratio between two hex colours."""
    la, lb = luminance(a), luminance(b)
    if la < lb:
        la, lb = lb, la
    return (la + 0.05) / (lb + 0.05)


def mix(a: str, b: str, t: float) -> str:
    """Linear sRGB mix, t = share of b."""
    ra, rb = hex_to_rgb(a), hex_to_rgb(b)
    return "#%02X%02X%02X" % tuple(round((x * (1 - t) + y * t) * 255) for x, y in zip(ra, rb))
