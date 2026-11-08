"""Text overlays: karaoke subtitles (German + English), title card, handwritten note."""
import os
import re

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .common import H, W, smoothstep

INTER = "/usr/share/fonts/opentype/inter"
FONT_DIR = os.environ.get("STORYVID_FONTS", os.path.join(os.path.dirname(__file__), "..", "fonts"))

_PUNCT = re.compile(r"[^\wäöüÄÖÜß-]+")


def _font(path, size, weight=None):
    f = ImageFont.truetype(path, size)
    if weight is not None:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def font_path(name):
    for d in (FONT_DIR, INTER, "/usr/share/fonts/truetype"):
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(name)


def _blur_alpha(a, sigma):
    return cv2.GaussianBlur(a, (0, 0), sigma)


class Captions:
    """German subtitle with per-word karaoke progress, vocabulary in gold, English below."""

    def __init__(self, chunks, vocab, y_top=1200, max_w=860, de_size=60, en_size=33,
                 top_lines=(), y_top_alt=230):
        self.chunks = [c for c in chunks if not c["handwriting"]]
        chunks = self.chunks
        self.top_lines = set(top_lines)
        self.y_top_alt = y_top_alt
        self.vocab = {v.lower() for v in vocab}
        self.y_top = y_top
        self.max_w = max_w
        self.f_de = _font(font_path("InterDisplay-SemiBold.otf"), de_size)
        self.f_en = _font(font_path("Inter-Italic.otf"), en_size)
        self.de_lh = int(de_size * 1.28)
        self.en_lh = int(en_size * 1.35)
        self.white = (250, 246, 238)
        self.gold = (246, 196, 112)
        self.en_col = (226, 220, 208)
        self._cache = {}
        # visibility windows
        # Visibility windows. Chunks share one screen position, so two must never be
        # visible at once: back-to-back chunks hand over at a single instant.
        for c in chunks:
            c["show"], c["fin"] = c["start"] - 0.14, 0.14
        for i, c in enumerate(chunks):
            nxt = chunks[i + 1] if i + 1 < len(chunks) else None
            c["fout"] = 0.12
            c["hide"] = c["end"] + 1.0
            if nxt is None:
                continue
            gap = nxt["start"] - c["end"]
            if gap < 0.45:
                b = min(nxt["start"], max(nxt["start"] - 0.14, c["end"] + gap / 2))
                c["fout"] = 0.07
                c["hide"] = b - 0.07
                nxt["show"], nxt["fin"] = b, 0.09
            else:
                c["hide"] = min(c["end"] + 1.0, nxt["start"] - 0.28)

    def _wrap(self, words, font, max_w):
        lines, cur = [], []
        for w in words:
            test = " ".join(cur + [w])
            if cur and font.getlength(test) > max_w:
                lines.append(cur)
                cur = [w]
            else:
                cur.append(w)
        if cur:
            lines.append(cur)
        return lines

    def _layout(self, idx):
        if idx in self._cache:
            return self._cache[idx]
        c = self.chunks[idx]
        words = c["de"].split()
        lines = self._wrap(words, self.f_de, self.max_w)
        en_lines = self._wrap(c["en"].split(), self.f_en, self.max_w + 40)
        h_de = len(lines) * self.de_lh
        h_en = len(en_lines) * self.en_lh
        gap = 14
        block_h = (0 if c["handwriting"] else h_de) + gap + h_en
        pad = 40
        layer = Image.new("RGBA", (W, block_h + 2 * pad), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        boxes = []
        y = pad
        space = self.f_de.getlength(" ")
        k = 0
        if not c["handwriting"]:
            for ln in lines:
                lw = self.f_de.getlength(" ".join(ln))
                x = (W - lw) / 2
                for w in ln:
                    is_vocab = _PUNCT.sub("", w).lower() in self.vocab
                    col = self.gold if is_vocab else self.white
                    d.text((x, y), w, font=self.f_de, fill=col + (255,))
                    ww = self.f_de.getlength(w)
                    boxes.append((int(x) - 2, y - 4, int(x + ww) + 3, y + self.de_lh, k))
                    x += ww + space
                    k += 1
                y += self.de_lh
            y += gap
        else:
            k = len(words)
        en_y = y
        for ln in en_lines:
            s = " ".join(ln)
            lw = self.f_en.getlength(s)
            d.text(((W - lw) / 2, y), s, font=self.f_en, fill=self.en_col + (235,))
            y += self.en_lh
        arr = np.array(layer).astype(np.float32) / 255.0
        alpha = arr[..., 3]
        outline = cv2.dilate(alpha, np.ones((5, 5), np.uint8))
        shadow = np.clip(_blur_alpha(outline, 4) * 1.1 + _blur_alpha(alpha, 14) * 0.45, 0, 1)
        shadow = np.roll(shadow, 3, axis=0)
        # per-pixel word index map for karaoke (-1 = not a German word, e.g. English)
        wid = np.full(alpha.shape, -1, np.int16)
        for (x0, y0, x1, y1, kk) in boxes:
            wid[max(0, y0):y1, max(0, x0):x1] = kk
        lay = {"rgb": arr[..., :3], "alpha": alpha, "shadow": shadow, "wid": wid,
               "h": arr.shape[0], "pad": pad, "en_y": en_y, "block_h": block_h}
        self._cache[idx] = lay
        return lay

    def visible(self, t):
        out = []
        for i, c in enumerate(self.chunks):
            if c["show"] <= t <= c["hide"] + c["fout"]:
                a = smoothstep(c["show"], c["show"] + c["fin"], t) * (1 - smoothstep(c["hide"], c["hide"] + c["fout"], t))
                if a > 0.001:
                    out.append((i, a))
        return out

    def scrim(self, t):
        """0..1 strength of the dark band behind the subtitles."""
        v = self.visible(t)
        return max((a for _, a in v), default=0.0)

    def draw(self, frame, t):
        """Composite onto float RGB frame (H, W, 3) in place."""
        for idx, a in self.visible(t):
            c = self.chunks[idx]
            lay = self._layout(idx)
            words = c["words"]
            prog = np.array([0.66 + 0.34 * smoothstep(w["start"] - 0.04, w["start"] + 0.10, t) for w in words]
                            + [1.0], np.float32)
            mult = prog[lay["wid"]]          # -1 -> last element (1.0) for English / gaps
            rise = (1 - smoothstep(c["show"], c["show"] + 0.3, t)) * 8
            ytop = self.y_top_alt if c["line"] in self.top_lines else self.y_top
            y0 = int(ytop - lay["pad"] + rise)
            hgt = lay["h"]
            y1 = min(H, y0 + hgt)
            sl = slice(y0, y1)
            al = (lay["alpha"] * mult)[: y1 - y0] * a
            sh = lay["shadow"][: y1 - y0] * a
            reg = frame[sl]
            reg *= (1 - sh[..., None] * 0.92)
            reg[:] = reg * (1 - al[..., None]) + lay["rgb"][: y1 - y0] * al[..., None]


class TitleCard:
    def __init__(self, title, subtitle, y=880):
        self.f_t = _font(font_path("CormorantGaramond[wght].ttf"), 128, 560)
        self.f_s = _font(font_path("Inter-Medium.otf"), 27)
        self.title = title.upper()
        self.subtitle = subtitle.upper()
        self.y = y
        self._base = None

    def _render(self, track):
        layer = Image.new("RGBA", (W, 420), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)

        def spaced(text, font, y, spacing, fill):
            widths = [font.getlength(ch) for ch in text]
            total = sum(widths) + spacing * (len(text) - 1)
            x = (W - total) / 2
            for ch, wch in zip(text, widths):
                d.text((x, y), ch, font=font, fill=fill)
                x += wch + spacing
            return total

        tw = spaced(self.title, self.f_t, 90, 18 + track * 10, (244, 236, 222, 255))
        sw = spaced(self.subtitle, self.f_s, 262, 7 + track * 3, (226, 200, 160, 230))
        lw = max(tw, sw) * 0.36
        d.line([((W - lw) / 2, 240), ((W + lw) / 2, 240)], fill=(226, 190, 140, 170), width=2)
        arr = np.array(layer).astype(np.float32) / 255
        glow = _blur_alpha(arr[..., 3], 14) * 0.55
        return arr, glow

    def draw(self, frame, t, t0, t1):
        if not (t0 <= t <= t1):
            return
        a = smoothstep(t0, t0 + 0.9, t) * (1 - smoothstep(t1 - 0.8, t1, t))
        track = (t - t0) / (t1 - t0)
        arr, glow = self._render(track)
        y0 = self.y - 210
        reg = frame[y0:y0 + arr.shape[0]]
        reg *= (1 - glow[..., None] * 0.6 * a)
        al = arr[..., 3:4] * a
        reg[:] = reg * (1 - al) + arr[..., :3] * al


class Handwriting:
    """Non-diegetic handwritten note, revealed word by word in sync with the narration."""

    def __init__(self, text_lines, words, en=None, y=600, size=128, max_w=930):
        probe = _font(font_path("LaBelleAurore.ttf"), 100)
        widest = max(probe.getbbox(ln, stroke_width=2)[2] - probe.getbbox(ln, stroke_width=2)[0] for ln in text_lines)
        size = int(min(size, 100 * max_w / widest))
        self.f = _font(font_path("LaBelleAurore.ttf"), size)
        self.f_en = _font(font_path("Inter-Italic.otf"), 33)
        self.words = words
        self.y = y
        self.h = 520
        canvas = Image.new("L", (W * 2, self.h), 0)
        d = ImageDraw.Draw(canvas)
        word_x = []
        yy = 70
        for li, ln in enumerate(text_lines):
            lw = self.f.getlength(ln)
            x = (W * 2 - lw) / 2 + (-25 if li == 0 else 70)
            d.text((x, yy), ln, font=self.f, fill=255, stroke_width=2, stroke_fill=255)
            cx = x
            for w in ln.split(" "):
                ww = self.f.getlength(w)
                word_x.append([cx, cx + ww, yy])
                cx += ww + self.f.getlength(" ")
            yy += int(size * 1.0)
        a = np.array(canvas).astype(np.float32) / 255
        cols = np.where(a.max(axis=0) > 0.05)[0]
        shift = (cols[0] + cols[-1]) / 2 - W / 2 - (W * 2 - W) / 2 * 0  # centre the ink
        off = int(round((cols[0] + cols[-1]) / 2 - W))
        a = np.roll(a, -off, axis=1)[:, W // 2: W // 2 + W]
        for wx in word_x:
            wx[0] -= off + W // 2
            wx[1] -= off + W // 2
        self.word_x = word_x
        a = cv2.GaussianBlur(a, (0, 0), 0.8)
        self.rot = cv2.getRotationMatrix2D((W / 2, self.h / 2), 2.5, 1.0)
        self.alpha = cv2.warpAffine(a, self.rot, (W, self.h))
        self.glow = _blur_alpha(self.alpha, 12)
        self.en = None
        if en:
            lay = Image.new("RGBA", (W, 70), (0, 0, 0, 0))
            dd = ImageDraw.Draw(lay)
            dd.text(((W - self.f_en.getlength(en)) / 2, 10), en, font=self.f_en, fill=(226, 220, 208, 235))
            e = np.array(lay).astype(np.float32) / 255
            self.en = (e, _blur_alpha(cv2.dilate(e[..., 3], np.ones((5, 5), np.uint8)), 4))

    def draw(self, frame, t, fade_out_start, fade_out_end):
        if t < self.words[0]["start"] - 0.2 or t > fade_out_end:
            return
        xs = np.arange(W, dtype=np.float32)
        band = np.zeros((self.h, W), np.float32)
        for (x0, x1, yy), w in zip(self.word_x, self.words):
            p = np.clip((t - w["start"] + 0.05) / max(0.25, (w["end"] - w["start"]) * 0.9), 0, 1)
            if p <= 0:
                continue
            edge = x0 + (x1 - x0 + 30) * p
            col = np.clip((edge - xs) / 18.0, 0, 1) * (xs >= x0 - 14)
            r0, r1 = max(0, yy - 40), min(self.h, yy + 190)
            band[r0:r1] = np.maximum(band[r0:r1], col[None, :])
        band = cv2.warpAffine(band, self.rot, (W, self.h))
        a = 1 - smoothstep(fade_out_start, fade_out_end, t)
        y0 = self.y - self.h // 2
        reg = frame[y0:y0 + self.h]
        g = self.glow * band * a
        reg *= (1 - g[..., None] * 0.6)
        ink = np.array([0.96, 0.91, 0.82], np.float32)
        al = (self.alpha * band * a)[..., None]
        reg[:] = reg * (1 - al) + ink * al
        if self.en is not None:
            e, sh = self.en
            ea = smoothstep(self.words[0]["start"], self.words[0]["start"] + 0.4, t) * a
            ey = y0 + self.h - 40
            r = frame[ey:ey + e.shape[0]]
            r *= (1 - sh[..., None] * 0.85 * ea)
            al2 = e[..., 3:4] * ea
            r[:] = r * (1 - al2) + e[..., :3] * al2
