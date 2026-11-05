"""Interface-style props: instruction chips, editor timeline, film strip,
analog clock, gaze reticle. Built for "the brain as an editor" but generic.
"""
from __future__ import annotations

import math

from .gfx import L, Canvas, clamp, ease_out_back, ease_out_cubic, lerp, mix, prog, text_width


def chip(cv: Canvas, x, y, w, h, num, text, alpha=1.0, icon=None, color=L.CYAN, pop=0.0):
    """Rounded instruction chip: numbered bubble + mono text (+ optional icon callback)."""
    if alpha <= 0.003:
        return
    s = 1.0 + 0.08 * pop
    with cv.transform(s=s, cx=x + w / 2, cy=y + h / 2):
        cv.rect(x, y, w, h, (0.04, 0.08, 0.16), alpha=0.85 * alpha, radius=h / 2)
        cv.rect(x, y, w, h, color, alpha=0.55 * alpha, fill=False, width=2, radius=h / 2, glow=0.3)
        cv.circle(x + h / 2, y + h / 2, h * 0.34, color, alpha=alpha, glow=0.5)
        cv.text(str(num), x + h / 2, y + h / 2, h * 0.40, font=L.MONO_XB, color=(0.02, 0.05, 0.1), alpha=alpha)
        tx = x + h + 14
        if icon:
            icon(cv, tx + h * 0.45, y + h / 2, h * 0.8, alpha)
            tx += h + 4
        cv.text(text, tx, y + h / 2, h * 0.36, font=L.MONO_XB, anchor="left", color=L.WHITE, alpha=alpha,
                tracking=0.08)


def gaze_reticle(cv: Canvas, x, y, r=34, alpha=1.0, color=L.CYAN):
    if alpha <= 0.003:
        return
    cv.circle(x, y, r, color, alpha=alpha, fill=False, width=3, glow=0.8)
    for a in range(4):
        ang = a * math.pi / 2
        cv.line([(x + math.cos(ang) * r * 0.55, y + math.sin(ang) * r * 0.55),
                 (x + math.cos(ang) * r * 1.35, y + math.sin(ang) * r * 1.35)], color, width=3, alpha=alpha, glow=0.6)
    cv.circle(x, y, 4, L.WHITE, alpha=alpha, glow=0.8)


def analog_clock(cv: Canvas, x, y, r, sec, minute=10.0, hour=10.2, alpha=1.0, accent=L.AMBER, numerals=True):
    """sec in [0, 60): second-hand position (fractional allowed). minute/hour in their own units."""
    if alpha <= 0.003:
        return
    cv.circle(x, y, r * 1.04, (0.03, 0.05, 0.11), alpha=0.92 * alpha)
    cv.circle(x, y, r * 1.04, (0.8, 0.9, 1.0), alpha=0.9 * alpha, fill=False, width=6, glow=0.4)
    for k in range(60):
        a = k / 60 * 2 * math.pi - math.pi / 2
        big = k % 5 == 0
        r0 = r * (0.86 if big else 0.92)
        cv.line([(x + math.cos(a) * r0, y + math.sin(a) * r0), (x + math.cos(a) * r * 0.97, y + math.sin(a) * r * 0.97)],
                L.WHITE, width=5 if big else 2, alpha=alpha * (0.95 if big else 0.55))
    if numerals:
        for k in range(1, 13):
            a = k / 12 * 2 * math.pi - math.pi / 2
            cv.text(str(k), x + math.cos(a) * r * 0.72, y + math.sin(a) * r * 0.72, r * 0.15, font=L.DISPLAY_XB,
                    color=L.WHITE, alpha=alpha * 0.85)
    ha = (hour % 12) / 12 * 2 * math.pi - math.pi / 2
    ma = (minute % 60) / 60 * 2 * math.pi - math.pi / 2
    cv.line([(x, y), (x + math.cos(ha) * r * 0.48, y + math.sin(ha) * r * 0.48)], L.WHITE, width=r * 0.05, alpha=alpha)
    cv.line([(x, y), (x + math.cos(ma) * r * 0.72, y + math.sin(ma) * r * 0.72)], L.WHITE, width=r * 0.035, alpha=alpha)
    sa = (sec % 60) / 60 * 2 * math.pi - math.pi / 2
    cv.line([(x - math.cos(sa) * r * 0.18, y - math.sin(sa) * r * 0.18), (x + math.cos(sa) * r * 0.86,
             y + math.sin(sa) * r * 0.86)], accent, width=r * 0.018 + 2, alpha=alpha, glow=0.8)
    cv.circle(x, y, r * 0.045, accent, alpha=alpha, glow=0.6)
    cv.circle(x, y, r * 0.02, L.WHITE, alpha=alpha)


def film_strip(cv: Canvas, x, y, frame_w, frame_h, frames, alpha=1.0, gap=10, draw_frame=None, scroll=0.0):
    """frames: list of dicts {w: width multiplier, kind: 'clear'|'blur'|'gap'|'stretch', a: alpha}.

    draw_frame(cv, fx, fy, fw, fh, frame) draws frame content; defaults to abstract bars.
    """
    if alpha <= 0.003:
        return
    total = sum(f.get("w", 1.0) * frame_w + gap for f in frames)
    x0 = x - scroll
    band_h = frame_h + 56
    cv.rect(x0 - 16, y - band_h / 2, total + 22, band_h, (0.05, 0.06, 0.09), alpha=0.95 * alpha, radius=10)
    for side in (-1, 1):
        yy = y + side * (frame_h / 2 + 15)
        hx = x0 - 6
        while hx < x0 + total:
            cv.rect(hx, yy - 7, 14, 14, (0.0, 0.0, 0.0), alpha=alpha, radius=3)
            cv.rect(hx, yy - 7, 14, 14, (0.3, 0.35, 0.45), alpha=0.6 * alpha, fill=False, width=1, radius=3)
            hx += 28
    fx = x0
    for f in frames:
        fw = f.get("w", 1.0) * frame_w
        fa = alpha * f.get("a", 1.0)
        kind = f.get("kind", "clear")
        if kind != "gap" and fa > 0.003:
            col = {"clear": (0.12, 0.2, 0.36), "blur": (0.3, 0.08, 0.16), "stretch": (0.36, 0.24, 0.08)}.get(kind)
            cv.rect(fx, y - frame_h / 2, fw, frame_h, col, alpha=fa, radius=6)
            if draw_frame:
                draw_frame(cv, fx, y - frame_h / 2, fw, frame_h, f, fa)
            border = {"clear": L.CYAN, "blur": L.MAGENTA, "stretch": L.AMBER}[kind]
            cv.rect(fx, y - frame_h / 2, fw, frame_h, border, alpha=0.8 * fa, fill=False, width=2.5, radius=6,
                    glow=0.4 if kind != "clear" else 0)
        elif kind == "gap" and fa > 0.003:
            cv.rect(fx, y - frame_h / 2, fw, frame_h, L.MAGENTA, alpha=0.5 * fa, fill=False, width=2, radius=6)
        f["_x"], f["_w"] = fx, fw
        fx += fw + gap
    return total


def editor_timeline(cv: Canvas, x, y, w, h, tracks, t_view=(0.0, 6.0), playhead=None, alpha=1.0, title="",
                    live_badge=None, fs=1.0):
    """A video-editor style timeline.

    tracks: list of (label, clips) where clips are dicts {t0, t1, text, color, a, kind}.
    """
    if alpha <= 0.003:
        return
    cv.rect(x, y, w, h, (0.03, 0.05, 0.10), alpha=0.92 * alpha, radius=16)
    cv.rect(x, y, w, h, L.FAINT, alpha=alpha, fill=False, width=2, radius=16)
    head_h = 54
    cv.rect(x, y, w, head_h, (0.06, 0.09, 0.16), alpha=alpha, radius=16)
    cv.circle(x + 26, y + head_h / 2, 7, L.MAGENTA, alpha=alpha)
    cv.circle(x + 48, y + head_h / 2, 7, L.AMBER, alpha=alpha)
    cv.circle(x + 70, y + head_h / 2, 7, L.MINT, alpha=alpha)
    if title:
        cv.text(title, x + 96, y + head_h / 2, 22 * fs, font=L.MONO_XB, anchor="left", color=L.WHITE, alpha=alpha,
                tracking=0.12)
    if live_badge:
        live_badge(cv, x + w - 20, y + head_h / 2, alpha)
    # ruler
    ry = y + head_h + 26
    label_w = 150 * fs
    tx0, tx1 = x + label_w, x + w - 20
    v0, v1 = t_view
    sec = math.floor(v0)
    while sec <= v1:
        px = lerp(tx0, tx1, (sec - v0) / (v1 - v0))
        if tx0 - 1 <= px <= tx1 + 1:
            cv.line([(px, ry - 12), (px, ry + 4)], L.DIM, width=2, alpha=alpha * 0.8)
            cv.text(f"{int(sec)}s", px + 5, ry - 6, 16 * fs, font=L.MONO, anchor="left", color=L.DIM,
                    alpha=alpha * 0.8)
        for q in range(1, 4):
            qx = lerp(tx0, tx1, (sec + q / 4 - v0) / (v1 - v0))
            if tx0 <= qx <= tx1:
                cv.line([(qx, ry - 5), (qx, ry + 2)], L.DIM, width=1, alpha=alpha * 0.5)
        sec += 1
    track_h = (h - head_h - 52) / max(1, len(tracks))
    for i, (label, clips) in enumerate(tracks):
        ty = ry + 16 + i * track_h
        cv.line([(x + 12, ty + track_h - 4), (x + w - 12, ty + track_h - 4)], L.FAINT, width=1, alpha=alpha * 0.6)
        cv.text(label, x + 20, ty + track_h / 2, 18 * fs, font=L.MONO_XB, anchor="left", color=L.DIM, alpha=alpha,
                tracking=0.1)
        for cl in clips:
            ca = alpha * cl.get("a", 1.0)
            if ca <= 0.003:
                continue
            a0 = clamp((cl["t0"] - v0) / (v1 - v0))
            a1 = clamp((cl["t1"] - v0) / (v1 - v0))
            if a1 <= a0:
                continue
            cx0, cx1 = lerp(tx0, tx1, a0), lerp(tx0, tx1, a1)
            col = cl.get("color", L.CYAN)
            cv.rect(cx0, ty + 6, cx1 - cx0, track_h - 16, col, alpha=0.30 * ca, radius=6)
            cv.rect(cx0, ty + 6, cx1 - cx0, track_h - 16, col, alpha=0.9 * ca, fill=False, width=2, radius=6,
                    glow=0.3)
            fill = cl.get("fill")
            if fill is not None:
                cv.rect(cx0 + 2, ty + 8, cx1 - cx0 - 4, track_h - 20, fill, alpha=0.95 * ca, radius=5)
            if cl.get("text") and cx1 - cx0 > 60:
                cv.text(cl["text"], cx0 + 10, ty + track_h / 2 - 4, 17 * fs, font=L.MONO_XB, anchor="left",
                        color=L.WHITE, alpha=ca, tracking=0.05)
            if cl.get("cross"):
                k = cl["cross"]
                cv.line([(cx0, ty + 6), (lerp(cx0, cx1, k), lerp(ty + 6, ty + track_h - 10, k))], L.MAGENTA,
                        width=3, alpha=ca)
    if playhead is not None:
        pa = clamp((playhead - v0) / (v1 - v0))
        px = lerp(tx0, tx1, pa)
        cv.line([(px, ry - 14), (px, y + h - 10)], L.WHITE, width=2.5, alpha=alpha, glow=0.6)
        cv.poly([(px - 9, ry - 22), (px + 9, ry - 22), (px, ry - 10)], L.WHITE, alpha=alpha)
    return {"tx0": tx0, "tx1": tx1, "ry": ry}
