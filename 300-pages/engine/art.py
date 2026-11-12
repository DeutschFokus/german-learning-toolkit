"""Vector artwork drawn in code: the icon set, the character avatars, QR codes,
the logo and the illustration placeholders.

Everything is inline SVG with a <title>, so the tagged PDF carries alternative
text for every image and the file stays small and razor-sharp at any zoom.
"""
from __future__ import annotations

import html
from pathlib import Path
import io
from typing import Optional

import segno

# ── icons: 24 px grid, 1.6 stroke, round caps and joins ──────────────────────
ICON_PATHS = {
    # skills
    "hoeren": '<path d="M4.5 14.5v-2.2a7.5 7.5 0 0 1 15 0v2.2"/><rect x="3.2" y="13.2" width="4.3" height="7" rx="1.9"/><rect x="16.5" y="13.2" width="4.3" height="7" rx="1.9"/>',
    "lesen": '<path d="M12 6.6C10 5.2 7.3 4.7 3.8 5v13.2c3.5-.3 6.2.2 8.2 1.6 2-1.4 4.7-1.9 8.2-1.6V5c-3.5-.3-6.2.2-8.2 1.6z"/><path d="M12 6.6v13.2"/>',
    "schreiben": '<path d="M4.2 19.8l.9-4.3L16.4 4.2a2.05 2.05 0 0 1 2.9 0l.5.5a2.05 2.05 0 0 1 0 2.9L8.5 18.9z"/><path d="M14.3 6.3l3.4 3.4"/>',
    "sprechen": '<path d="M6.5 4.5h11A2.5 2.5 0 0 1 20 7v6.5a2.5 2.5 0 0 1-2.5 2.5h-6.3L7 19.8V16h-.5A2.5 2.5 0 0 1 4 13.5V7a2.5 2.5 0 0 1 2.5-2.5z"/>',
    "partner": '<circle cx="8.3" cy="8.2" r="3.1"/><path d="M2.8 19.5c.4-3.8 2.5-5.9 5.5-5.9s5.1 2.1 5.5 5.9"/><circle cx="16.8" cy="9.3" r="2.5"/><path d="M15.6 14c3.1-.3 5.1 1.7 5.6 5.1"/>',
    "grammatik": '<path d="M4.5 9.3h3.3a2.4 2.4 0 1 1 4.4 0h3.3v3.3a2.4 2.4 0 1 1 0 4.4v3H4.5z"/>',
    # margin notes
    "tipp": '<path d="M12 3.3a6.2 6.2 0 0 0-3.7 11.2c.7.5 1.1 1.3 1.1 2.1h5.2c0-.8.4-1.6 1.1-2.1A6.2 6.2 0 0 0 12 3.3z"/><path d="M9.8 19.3h4.4"/><path d="M10.8 21.3h2.4"/>',
    "wort": '<rect x="4.8" y="3.6" width="14.4" height="16.8" rx="2.2"/><path d="M8.6 3.6v16.8"/><path d="M11.6 9h4.6M11.6 12.3h4.6"/>',
    "landeskunde": '<path d="M12 21s6.4-5.5 6.4-10.4a6.4 6.4 0 1 0-12.8 0C5.6 15.5 12 21 12 21z"/><circle cx="12" cy="10.5" r="2.3"/>',
    "sogehts": '<path d="M3.8 19.7h4.3v-4.4h4.3v-4.4h4.3V6.5h3.5"/><path d="M17.9 4.2l2.4 2.3-2.4 2.3"/>',
    # interface
    "play": '<circle cx="12" cy="12" r="8.8"/><path d="M10.2 8.6v6.8l5.6-3.4z"/>',
    "check": '<path d="M5 12.6l4.4 4.4L19 7.4"/>',
    "cross": '<path d="M6.5 6.5l11 11M17.5 6.5l-11 11"/>',
    "ziel": '<circle cx="12" cy="12" r="8.6"/><circle cx="12" cy="12" r="4.6"/><circle cx="12" cy="12" r="1" fill="currentColor"/>',
    "bild": '<rect x="3.5" y="5" width="17" height="14" rx="2.2"/><circle cx="8.6" cy="9.8" r="1.6"/><path d="M4 17l4.8-4.6 3.4 3.2 3-2.8 4.8 4.4"/>',
    "arrow": '<path d="M4.5 12h14.5"/><path d="M13.5 6.5L19 12l-5.5 5.5"/>',
    "back": '<path d="M9 7L4.5 11.5 9 16"/><path d="M4.5 11.5h10a5 5 0 0 1 0 10H12"/>',
    "key": '<circle cx="8" cy="15.5" r="3.7"/><path d="M10.7 12.8L19 4.5"/><path d="M15.5 8l2.6 2.6"/><path d="M18 5.5l1.8 1.8"/>',
    "fehler": '<path d="M12 4.2l8.6 15H3.4z"/><path d="M12 10v4.3"/><circle cx="12" cy="16.9" r=".4" fill="currentColor"/>',
    "clock": '<circle cx="12" cy="12" r="8.6"/><path d="M12 7.3V12l3.2 2"/>',
    "stern": '<path d="M12 3.8l2.5 5.2 5.700.8-4.1 4 1 5.7-5.1-2.7-5.1 2.7 1-5.700-4.1-4 5.700-.8z"/>',
    "buch": '<path d="M6 4h11.5v13.5H6.7A1.7 1.7 0 0 0 5 19.200V5a1 1 0 0 1 1-1z"/><path d="M5 19.200c0 .9.800 1.5 1.700 1.5h10.800v-3.200"/>',
    "phrases": '<path d="M5.500 4.500h8A2.500 2.500 0 0 1 16 7v3.500a2.500 2.500 0 0 1-2.500 2.500H9l-3 2.600V13h-.5A2.500 2.500 0 0 1 3 10.500V7a2.500 2.500 0 0 1 2.500-2.500z"/><path d="M18.500 9.500A2.500 2.500 0 0 1 21 12v3a2.500 2.500 0 0 1-2.500 2.500H18v2.500l-3-2.500h-2.500"/>',
    "youtube": '<rect x="3" y="6" width="18" height="12" rx="3.500"/><path d="M10.300 9.300v5.400l4.600-2.700z"/>',
    "cart": '<path d="M3.500 5h2.300l2 9.500h9.700l1.800-6.800H7"/><circle cx="9.300" cy="18.300" r="1.300"/><circle cx="16.300" cy="18.300" r="1.300"/>',
    "pin": '<path d="M12 3.500v4"/><circle cx="12" cy="10" r="2.600"/><path d="M12 12.600V20"/>',
    "voice": '<path d="M4.500 10v4"/><path d="M8.300 7v10"/><path d="M12 4.500v15"/><path d="M15.700 7.500v9"/><path d="M19.500 10v4"/>',
}


def icon(name: str, size: str = "5mm", title: Optional[str] = None, sw: float = 1.6, cls: str = "") -> str:
    t = f"<title>{html.escape(title)}</title>" if title else f"<title>{name}</title>"
    return (f'<svg class="ic {cls}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{t}{ICON_PATHS[name]}</svg>')


# ── avatars: one flat construction, varied by hair, colour and details ───────
def avatar(key: str, cast: dict, size: str = "8.6mm", uid: str = "") -> str:
    c = cast[key]
    a = c.get("avatar", {})
    name = c.get("name", key)
    bg = a.get("bg", "#E7E9EE")
    cid = f"av-{key}-{uid}" if uid else f"av-{key}"
    portrait = Path(__file__).resolve().parent.parent / "assets" / "cast" / f"{key}.png"
    if portrait.exists():                          # a real portrait (cut from the character sheet) replaces the drawn one
        return (f'<svg class="av" width="{size}" height="{size}" viewBox="0 0 48 48"><title>{html.escape(name)}</title>'
                f'<defs><clipPath id="{cid}"><circle cx="24" cy="24" r="24"/></clipPath></defs>'
                f'<image href="{portrait.as_uri()}" x="0" y="0" width="48" height="48" clip-path="url(#{cid})"/></svg>')
    if a.get("style") == "voice":
        inner = (f'<circle cx="24" cy="24" r="24" fill="{bg}"/>'
                 '<g fill="none" stroke="#1B1E2F" stroke-width="2.6" stroke-linecap="round">'
                 '<path d="M14 21v6"/><path d="M19 17v14"/><path d="M24 13v22"/><path d="M29 18v12"/><path d="M34 21v6"/></g>')
        return (f'<svg class="av" width="{size}" height="{size}" viewBox="0 0 48 48"><title>{html.escape(name)}</title>{inner}</svg>')
    s, h, st, top = a.get("skin", "#E0A677"), a.get("hair", "#2B1D17"), a.get("style", "short"), a.get("top", "#5B6EE1")
    p = [f'<circle cx="24" cy="24" r="24" fill="{bg}"/>']
    if st == "long":
        p.append(f'<path d="M12.5 22c0-8.500 4.500-13.500 11.500-13.500S35.500 13.500 35.500 22v16h-23z" fill="{h}"/>')
    if st == "scarf":
        p.append(f'<path d="M11.500 23c0-9 5-14.500 12.500-14.500S36.500 14 36.500 23c0 7-2 12-4 16h-17c-2-4-4-9-4-16z" fill="{h}"/>')
    if st == "bun":
        p.append(f'<circle cx="24" cy="8.200" r="4.200" fill="{h}"/>')
    p.append(f'<path d="M5 48c.800-8.800 8-13 19-13s18.200 4.200 19 13z" fill="{top}"/>')
    p.append(f'<path d="M19.800 28h8.400v6.500a4.200 4.200 0 0 1-8.400 0z" fill="{s}"/>'
             '<path d="M19.800 30.500c2.600 1.600 5.800 1.600 8.400 0V28h-8.400z" fill="#000" fill-opacity=".12"/>')
    p.append(f'<ellipse cx="24" cy="20.500" rx="8.300" ry="9.300" fill="{s}"/>')
    if st == "short":
        p.append(f'<path d="M15.400 19.500c-.600-6.500 3-10.500 8.600-10.500s9.200 4 8.600 10.500c-1.200-3.300-3-5-5.100-5.500-2.300 1.300-6.400 1.600-9 .900-1.500.900-2.500 2.400-3.100 4.600z" fill="{h}"/>')
    if st == "curly":
        p.append(f'<path d="M15.200 19c-1.800-6 2.200-11.200 8.800-11.200S34.600 13 32.800 19c-.600-2.300-1.700-3.700-3.200-4.300-3.200 1.200-8 1.200-11.200 0-1.500.600-2.600 2-3.200 4.300z" fill="{h}"/>')
    if st == "bob":
        p.append(f'<path d="M14.200 27c-1.600-10.500 2.600-18.200 9.800-18.200s11.400 7.700 9.800 18.200h-2.600c.900-5.300.100-9.300-1.700-11.800-3.300 1.500-7.700 1.900-11.200.600-1.800 2.500-2.500 6.300-1.500 11.200z" fill="{h}"/>')
    if st in ("long", "bun"):
        p.append(f'<path d="M15.300 20.500c-.500-6.900 3.100-11.200 8.700-11.200s9.200 4.300 8.700 11.200c-1.300-3.400-3.200-5.300-5.600-5.700-2.900 1.400-6.300 1.300-8.300.300-1.700 1-2.900 2.900-3.500 5.400z" fill="{h}"/>')
    if st == "bald":
        p.append(f'<path d="M15.700 20.500c.200-1.700.700-3.200 1.500-4.300-.300 1.500-.200 3 .300 4.600zM32.300 20.500c-.200-1.700-.700-3.200-1.500-4.300.300 1.500.200 3-.300 4.600z" fill="{h}"/>')
    if st == "scarf":
        p.append(f'<path d="M15.300 21c-.500-7.200 3.100-11.700 8.700-11.700s9.200 4.500 8.700 11.700c-1.700-4.600-4.600-6.800-8.700-6.800s-7 2.200-8.700 6.800z" fill="{h}"/>'
                 f'<path d="M17 30.500c2 3.400 4.300 5 7 5s5-1.600 7-5c1 2 1 4-.300 6.200H17.300C16 34.500 16 32.500 17 30.500z" fill="{h}"/>')
    if a.get("beard"):
        p.append(f'<path d="M16.200 22.500c.600 5.200 3.600 7.900 7.800 7.900s7.200-2.700 7.800-7.900c-1.500 2.300-4 3.300-7.800 3.300s-6.300-1-7.800-3.300z" fill="{a["beard"]}"/>')
    p.append('<path d="M21 24.300c1.800 1.500 4.200 1.500 6 0" fill="none" stroke="#3A2A22" stroke-opacity=".75" stroke-width="1.100" stroke-linecap="round"/>')
    p.append('<circle cx="20.600" cy="20" r=".95" fill="#2A1E1A"/><circle cx="27.400" cy="20" r=".95" fill="#2A1E1A"/>')
    if a.get("moustache"):
        p.append(f'<path d="M19.600 23.300c1.300-1.500 3-1.300 4.400-.300 1.400-1 3.100-1.200 4.400.300-1.500.900-3 .900-4.400.200-1.400.700-2.900.700-4.400-.200z" fill="{a["moustache"]}"/>')
    if a.get("cap"):
        p.append(f'<path d="M15 17.500c0-5.500 3.800-9.300 9-9.300s9 3.800 9 9.300z" fill="{a["cap"]}"/><path d="M14 17.500h17.500c2.500 0 4.500.800 6 2.200H14z" fill="{a["cap"]}"/>')
    if a.get("band"):
        p.append(f'<path d="M15.400 15.600c2.300-2.600 5.200-3.900 8.600-3.900s6.300 1.300 8.600 3.900l-.900 2c-2.100-2.200-4.700-3.300-7.700-3.300s-5.600 1.100-7.700 3.300z" fill="{a["band"]}"/>')
    if a.get("glasses"):
        p.append('<g fill="none" stroke="#1A1D2E" stroke-width="1"><circle cx="20.600" cy="20" r="2.900"/><circle cx="27.400" cy="20" r="2.900"/><path d="M23.500 20h1"/></g>')
    return (f'<svg class="av" width="{size}" height="{size}" viewBox="0 0 48 48"><title>{html.escape(name)}</title>'
            f'<defs><clipPath id="{cid}"><circle cx="24" cy="24" r="24"/></clipPath></defs>'
            f'<g clip-path="url(#{cid})">{"".join(p)}</g></svg>')


# ── QR codes (vector) ────────────────────────────────────────────────────────
def qr_svg(url: str, title: str, dark: str = "#1B1E2F") -> str:
    q = segno.make(url, error="m", micro=False)
    buf = io.BytesIO()
    q.save(buf, kind="svg", border=0, dark=dark, xmldecl=False, svgns=True, nl=False, omitsize=True)
    svg = buf.getvalue().decode()
    head, sep, rest = svg.partition(">")
    return f'{head} class="qr"{sep}<title>{html.escape(title)}</title>{rest}'


# ── logo: a speech bubble with a focus point (language + focus) ────────────────────────────────────
def logo(color: str, size_mm: float = 6.2, wordmark: bool = True) -> str:
    mark = (f'<svg class="lg-mark" width="{size_mm}mm" height="{size_mm}mm" viewBox="0 0 24 24"><title>Deutsch Fokus</title>'
            f'<path fill="{color}" fill-rule="evenodd" d="M12 1.500a10.500 10.500 0 1 1-5.600 19.400L2 22.500l1.700-4.300A10.500 10.500 0 0 1 12 1.500z'
            f'M12 6.200a5.800 5.800 0 1 0 0 11.600a5.800 5.800 0 1 0 0-11.600zM12 9.300a2.700 2.700 0 1 1 0 5.400a2.700 2.700 0 1 1 0-5.400z"/></svg>')
    word = f'<span class="lg-word" style="color:{color}">Deutsch<b>Fokus</b></span>' if wordmark else ""
    return f'<span class="lg">{mark}{word}</span>'


# ── illustration placeholder ─────────────────────────────────────────────────
def placeholder_art(tokens: dict, title: str, variant: int = 0) -> str:
    """Abstract, calm scene in the chapter tints: looks finished, clearly not the final picture."""
    soft, hl, mid = tokens["soft"], tokens["hl"], tokens["mid"]
    scenes = [
        (f'<circle cx="158" cy="34" r="46" fill="{hl}" fill-opacity=".55"/>'
         f'<path d="M0 120V78c22-16 44-16 66 0s44 16 66 0 44-16 78 2v40z" fill="{mid}" fill-opacity=".28"/>'
         '<path d="M22 120V66a22 22 0 0 1 44 0v54z" fill="#fff" fill-opacity=".55"/>'
         '<rect x="86" y="58" width="38" height="62" rx="3" fill="#fff" fill-opacity=".4"/>'),
        (f'<circle cx="46" cy="44" r="38" fill="{hl}" fill-opacity=".5"/>'
         f'<path d="M0 120V92c30-14 60-14 90-2s70 12 120-6v36z" fill="{mid}" fill-opacity=".26"/>'
         '<rect x="118" y="38" width="30" height="82" rx="3" fill="#fff" fill-opacity=".45"/>'
         '<path d="M156 120V70a18 18 0 0 1 36 0v50z" fill="#fff" fill-opacity=".5"/>'),
        (f'<path d="M0 120V60c40-20 80 10 120-6s60-16 90-4v70z" fill="{mid}" fill-opacity=".22"/>'
         f'<circle cx="104" cy="40" r="30" fill="{hl}" fill-opacity=".55"/>'
         '<rect x="24" y="52" width="44" height="68" rx="3" fill="#fff" fill-opacity=".45"/>'
         '<rect x="150" y="66" width="36" height="54" rx="18" fill="#fff" fill-opacity=".5"/>'),
    ]
    return (f'<svg class="ph-art" viewBox="0 0 210 120" preserveAspectRatio="xMidYMid slice"><title>{html.escape(title)}</title>'
            f'<rect width="210" height="120" fill="{soft}"/>{scenes[variant % len(scenes)]}</svg>')
