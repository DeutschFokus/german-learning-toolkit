"""Extended cut: a vocabulary moment (story sentences replayed on cards) and the outro.

Follows the channel format: Method 4 (contextual sentences, read once more, with
German explanations and small English glosses), then the standard call to action.
"""
import json
import os
import subprocess

import cv2
import numpy as np
import pyloudnorm as pyln
from PIL import Image, ImageDraw

from . import mix as mixmod
from . import music as musicmod
from . import render as rendermod
from . import sfx
from . import tts as ttsmod
from .common import FPS, H, SR, W, butter, db, place, read_wav, smoothstep, write_wav
from .music import BASS, OSTINATO, PAD, Part, n
from .text import _PUNCT, Captions, _blur_alpha, _font, font_path

GOLD = (246, 196, 112)
VIEW_PLATE = {"quote": "letter", "card": "letter", "vergeben": "photo", "photo": "photo", "cta": "window"}
WHITE = (250, 246, 238)
SOFT = (226, 220, 208)


# --------------------------------------------------------------------------- timeline


class ExtTimeline:
    def __init__(self, ext, story_timing, ext_timing, lead_in=1.0, tail=2.6):
        self.items = []
        t = lead_in
        card_no = 0
        for it in ext["items"]:
            if it["type"] == "say":
                d = ext_timing[it["id"]]["dur"]
                words = [dict(w, start=w["start"] + t, end=w["end"] + t) for w in ext_timing[it["id"]]["words"]]
                self.items.append(dict(it, start=t, end=t + d, a0=t, a1=t + d, words=words))
                t += d + it.get("pause", 0.6)
            else:
                card_no += 1
                pre = 0.7
                d = story_timing[it["replay"]]["dur"]
                words = [dict(w, start=w["start"] + t + pre, end=w["end"] + t + pre)
                         for w in story_timing[it["replay"]]["words"]]
                g = t + pre + d + 0.3
                self.items.append(dict(it, start=t, a0=t + pre, a1=t + pre + d, words=words, gloss_t=g,
                                       end=g + it.get("hold", 3.0), no=card_no))
                t = g + it.get("hold", 3.0) + 0.2
        self.n_cards = card_no
        self.duration = t + tail

    def speech_intervals(self):
        return [(i["a0"], i["a1"]) for i in self.items]


# --------------------------------------------------------------------------- audio


def compose_music(tl):
    for ch, pat, bass, pad in (("Bm", ["D3", "F#3", "B3", "D4", "F#4", "D4", "B3", "F#3"], "B1", ["D3", "B3", "F#4"]),
                               ("G", ["D3", "G3", "B3", "D4", "G4", "D4", "B3", "G3"], "G1", ["D3", "B3", "G4"])):
        OSTINATO.setdefault(ch, pat)
        BASS.setdefault(ch, bass)
        PAD.setdefault(ch, pad)
    rng = np.random.default_rng(5)
    piano, strings, cello = Part(0, "piano"), Part(49, "strings"), Part(42, "cello")
    bar = 60 / 66 * 4
    e8 = bar / 8
    prog = ["D", "Bm", "G", "A"]
    t = 0.4
    i = 0
    end = tl.duration - 3.2
    strings.cc(0, 11, 30)
    while t + bar <= end:
        ch = prog[i % 4]
        piano.cc(t - 0.03, 64, 0)
        piano.cc(t + 0.02, 64, 127)
        for k, p in enumerate(OSTINATO[ch]):
            piano.note(t + k * e8 + rng.normal(0, 0.008), e8 * 2.2, p, 32 + (5 if k == 4 else 0) + rng.integers(-3, 4))
        piano.note(t, bar * 1.05, BASS[ch], 36)
        for p in PAD[ch]:
            strings.note(t, bar * 1.02, p, 54)
        cello.note(t, bar * 1.02, n(BASS[ch]) + 12, 44)
        t += bar
        i += 1
    piano.cc(t - 0.03, 64, 0)
    piano.cc(t + 0.02, 64, 127)
    for p, v in (("D2", 46), ("D3", 40), ("A3", 38), ("F#4", 40), ("D5", 36)):
        piano.note(t, tl.duration - t, p, v)
    for p in PAD["D"]:
        strings.note(t, tl.duration - t, p, 52)
    strings.ramp(t, tl.duration - 0.2, 11, 30, 0)
    return {"piano": piano, "strings": strings, "cello": cello}


def build_audio(tl, story, ext_dir_tts, story_tts, work, target_lufs=-14.0):
    n_s = int(tl.duration * SR)
    vo = np.zeros((n_s + 3 * SR, 2), np.float32)
    for it in tl.items:
        if it["type"] == "say":
            x = read_wav(os.path.join(ext_dir_tts, f"{it['id']}.wav"))
            kind = story["voices"][it["voice"]].get("fx", "narrator")
        else:
            x = read_wav(os.path.join(story_tts, f"{it['replay']}.wav"))
            line = next(l for l in story["lines"] if l["id"] == it["replay"])
            kind = story["voices"][line["voice"]].get("fx", "narrator")
        m = np.abs(x) > 0.01
        x = x * (0.1 / (np.sqrt(np.mean(x[m] ** 2)) + 1e-9))
        place(vo, mixmod.process_voice(x, kind), it["a0"])
    vo = vo[:n_s]

    parts = compose_music(tl)
    stems = musicmod.render(parts, work, tl.duration + 2)
    hall = mixmod.make_ir(4.0, 3.0, 0.03, 6500, seed=7)
    mus = np.zeros((n_s, 2), np.float32)
    for name, x in stems.items():
        y = mixmod.convolve_reverb(butter(x, "high", 45, 2), hall, wet=0.38)[:n_s]
        mus += y * db({"piano": 0, "strings": -3, "cello": -5}[name])
    mus = mus / (np.abs(mus).max() + 1e-9) * 0.5

    t = np.arange(n_s) / SR
    amb = sfx.rain(tl.duration + 1, "interior", seed=31)[:n_s]
    amb *= (np.clip(t / 1.5, 0, 1) * np.clip((tl.duration - 10 - t) / 6, 0.15, 1))[:, None]
    fx = np.zeros((n_s, 2), np.float32)
    for it in tl.items:
        if it["type"] == "card":
            place(fx, butter(sfx.paper(0.55, seed=40 + it["no"]), "high", 900), it["start"] + 0.05, db(-20))
        if it.get("button"):
            tick = sfx.knock(0.6, seed=70)
            place(fx, butter(tick, "high", 1800), it["words"][0]["start"] + 0.12, db(-22))

    class _TL:  # minimal adaptor for mix.duck_env
        def __init__(self, iv):
            self._iv = iv

        def speech_intervals(self):
            return self._iv

    duck_tl = _TL(tl.speech_intervals())
    mix = vo + mus * db(-8.5) * mixmod.duck_env(duck_tl, n_s, -9.0)[:, None] \
        + amb * db(-19) * mixmod.duck_env(duck_tl, n_s, -6.0)[:, None] + fx * db(-3)
    mix = butter(mix, "high", 28, 2)
    mix *= (np.clip(t / 0.6, 0, 1) * np.clip((tl.duration - t) / 1.8, 0, 1))[:, None]
    meter = pyln.Meter(SR)
    loud = meter.integrated_loudness(mix.astype(np.float64))
    mix *= db(target_lufs - loud)
    mix = mixmod.limiter(mix, -1.5)
    path = os.path.join(work, "ext_mix.wav")
    write_wav(path, mix)
    return path


# --------------------------------------------------------------------------- visuals


def _plate(orig, cx, cy, z, sigma, dark, warm=0.0):
    h0, w0 = orig.shape[:2]
    s = (W / w0) * z
    ww, hh = W / s, H / s
    x0, y0 = cx * w0 - ww / 2, cy * h0 - hh / 2
    x0 = min(max(0, x0), w0 - ww)
    y0 = min(max(0, y0), h0 - hh)
    m = np.float32([[s * 1.1, 0, -x0 * s * 1.1], [0, s * 1.1, -y0 * s * 1.1]])
    pl = cv2.warpAffine(orig, m, (int(W * 1.1), int(H * 1.1)), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    pl = pl.astype(np.float32) / 255
    if sigma:
        pl = cv2.GaussianBlur(pl, (0, 0), sigma)
    pl *= dark
    if warm:
        pl *= np.array([1 + 0.08 * warm, 1.0, 1 - 0.08 * warm], np.float32)
    return pl


def _text_block(lines_spec, width=W):
    """lines_spec: list of (text, font, color, line_height). Returns RGBA float array."""
    hgt = sum(lh for _, _, _, lh in lines_spec) + 40
    layer = Image.new("RGBA", (width, hgt), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    y = 20
    for text, font, col, lh in lines_spec:
        if text:
            x = (width - font.getlength(text)) / 2
            d.text((x, y), text, font=font, fill=col)
        y += lh
    return np.array(layer).astype(np.float32) / 255


def _blit(frame, rgba, y, a=1.0, shadow=0.85):
    if a <= 0:
        return
    h = rgba.shape[0]
    y0, y1 = max(0, y), min(H, y + h)
    if y1 <= y0:
        return
    src = rgba[y0 - y:y1 - y]
    al = src[..., 3] * a
    sh = _blur_alpha(cv2.dilate(src[..., 3], np.ones((5, 5), np.uint8)), 5) * shadow * a
    reg = frame[y0:y1]
    reg *= (1 - sh[..., None])
    reg[:] = reg * (1 - al[..., None]) + src[..., :3] * al[..., None]


class ExtRenderer:
    def __init__(self, tl, ext, story, story_tl_lines, images, vocab):
        self.tl = tl
        self.ext = ext
        self.vocab = {v.lower() for v in vocab}
        self.tex = rendermod.Textures(seed=4)
        o1 = np.array(Image.open(images[1]).convert("RGB"))
        o2 = np.array(Image.open(images[2]).convert("RGB"))
        o3 = np.array(Image.open(images[3]).convert("RGB"))
        self.plates = {
            "letter": _plate(o3, 0.6, 0.72, 1.6, 9, 0.36, 0.6),
            "photo": _plate(o1, 0.65, 0.83, 2.0, 2.2, 0.5, 0.3),
            "window": _plate(o2, 0.55, 0.35, 1.25, 7, 0.4, 0.0),
        }
        self.f_head = _font(font_path("Inter-Medium.otf"), 28)
        self.f_sent = _font(font_path("InterDisplay-SemiBold.otf"), 56)
        self.f_en = _font(font_path("Inter-Italic.otf"), 32)
        self.f_gw = _font(font_path("InterDisplay-SemiBold.otf"), 46)
        self.f_gd = _font(font_path("Inter-Regular.otf"), 33)
        self.f_ge = _font(font_path("Inter-Italic.otf"), 29)
        self.f_quote = _font(font_path("CormorantGaramond[wght].ttf"), 92, 600)
        self.f_title = _font(font_path("CormorantGaramond[wght].ttf"), 86, 560)
        self.f_btn = _font(font_path("Inter-SemiBold.otf"), 40)
        self.f_mean = _font(font_path("Inter-Regular.otf"), 36)
        self.f_mean_b = _font(font_path("InterDisplay-SemiBold.otf"), 40)
        self.story_lines = {l["id"]: l for l in story["lines"]}
        # subtitles for narrated items: big centred style for quotes, standard below otherwise
        say = [i for i in tl.items if i["type"] == "say"]
        chunks_low, chunks_big = [], []
        for it in say:
            for ci, (de, en) in enumerate(it["chunks"]):
                ws = [w for w in it["words"] if w["chunk"] == ci]
                c = {"line": it["id"], "idx": ci, "de": de, "en": en, "start": ws[0]["start"],
                     "end": ws[-1]["end"], "words": ws, "voice": it["voice"], "handwriting": False}
                (chunks_big if it.get("view") in ("quote", "photo") else chunks_low).append(c)
        self.cap_low = Captions(chunks_low, vocab + ["vergeben", "verzeihen"])
        self.cap_big = Captions(chunks_big, vocab + ["vergeben"], y_top=820, de_size=64, en_size=34)
        self._card_cache = {}
        self._static = {}

    # ---- helpers
    def background(self, t):
        """Current plate, crossfading from the previous one when the view changes."""
        seq = []
        for it in self.tl.items:
            v = VIEW_PLATE[it.get("view", "card")]
            if not seq or seq[-1][1] != v:
                seq.append((it["start"] - 0.4, v))
        ci = 0
        for i, (ts, _) in enumerate(seq):
            if ts <= t:
                ci = i
        out = self._drift(self.plates[seq[ci][1]], t)
        if ci > 0:
            p = smoothstep(seq[ci][0], seq[ci][0] + 1.2, t)
            if p < 1:
                out = self._drift(self.plates[seq[ci - 1][1]], t) * (1 - p) + out * p
        return out

    def _drift(self, plate, t):
        k = 1.0 + 0.04 * (t / max(1.0, self.tl.duration))
        ph, pw = plate.shape[:2]
        m = np.float32([[k, 0, (W - pw * k) / 2], [0, k, (H - ph * k) / 2]])
        return cv2.warpAffine(plate, m, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

    def _card_layers(self, it):
        key = it["no"]
        if key in self._card_cache:
            return self._card_cache[key]
        line = self.story_lines[it["replay"]]
        de = " ".join(c[0] for c in line["chunks"])
        en = " ".join(c[1] for c in line["chunks"])
        head = _text_block([(f"{self.ext.get('header', 'Wortschatz').upper()}   ·   {it['no']} / {self.tl.n_cards}",
                             self.f_head, (226, 190, 140, 235), 40)])
        # sentence with word boxes (karaoke) and gold vocabulary
        words = de.split()
        lines, cur = [], []
        for w in words:
            if cur and self.f_sent.getlength(" ".join(cur + [w])) > 900:
                lines.append(cur)
                cur = [w]
            else:
                cur.append(w)
        lines.append(cur)
        lh = int(56 * 1.3)
        en_lines, cur = [], []
        for w in en.split():
            if cur and self.f_en.getlength(" ".join(cur + [w])) > 900:
                en_lines.append(cur)
                cur = [w]
            else:
                cur.append(w)
        en_lines.append(cur)
        hgt = len(lines) * lh + 24 + len(en_lines) * 44 + 40
        layer = Image.new("RGBA", (W, hgt), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        y = 20
        boxes, k = [], 0
        sp = self.f_sent.getlength(" ")
        for ln in lines:
            x = (W - self.f_sent.getlength(" ".join(ln))) / 2
            for w in ln:
                col = GOLD if _PUNCT.sub("", w).lower() in self.vocab else WHITE
                d.text((x, y), w, font=self.f_sent, fill=col + (255,))
                ww = self.f_sent.getlength(w)
                boxes.append((int(x) - 2, y - 4, int(x + ww) + 3, y + lh, k))
                x += ww + sp
                k += 1
            y += lh
        y += 24
        for ln in en_lines:
            s = " ".join(ln)
            d.text(((W - self.f_en.getlength(s)) / 2, y), s, font=self.f_en, fill=SOFT + (235,))
            y += 44
        sent = np.array(layer).astype(np.float32) / 255
        wid = np.full(sent.shape[:2], -1, np.int16)
        for x0, y0, x1, y1, kk in boxes:
            wid[max(0, y0):y1, max(0, x0):x1] = kk
        glosses = []
        for gw, gd, ge in it["gloss"]:
            glosses.append(_text_block([(gw, self.f_gw, GOLD + (255,), 58),
                                        ("= " + gd, self.f_gd, WHITE + (235,), 46),
                                        (ge, self.f_ge, (206, 200, 190, 220), 42)]))
        res = {"head": head, "sent": sent, "wid": wid, "gloss": glosses}
        self._card_cache[key] = res
        return res

    def _static_block(self, name, spec):
        if name not in self._static:
            self._static[name] = _text_block(spec)
        return self._static[name]

    def _button(self, pressed, scale):
        bw, bh = int(560 * scale), int(118 * scale)
        layer = Image.new("RGBA", (W, 200), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        x0, y0 = (W - bw) // 2, (200 - bh) // 2
        fill = (70, 66, 62, 245) if pressed else (204, 42, 40, 250)
        d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=bh // 2, fill=fill)
        label = "ABONNIERT  ✓" if pressed else "ABONNIEREN"
        f = _font(font_path("Inter-SemiBold.otf"), int(40 * scale))
        d.text(((W - f.getlength(label)) / 2, y0 + (bh - 40 * scale) / 2 - 4 * scale), label, font=f, fill=(255, 255, 255, 255))
        return np.array(layer).astype(np.float32) / 255

    # ---- frame
    def frame(self, fi):
        t = fi / FPS
        out = self.background(t)
        items = self.tl.items
        for idx, it in enumerate(items):
            nxt = items[idx + 1]["start"] if idx + 1 < len(items) else self.tl.duration
            if it["type"] == "card":
                a = smoothstep(it["start"], it["start"] + 0.35, t) * (1 - smoothstep(it["end"], it["end"] + 0.3, t))
                if a <= 0:
                    continue
                L = self._card_layers(it)
                _blit(out, L["head"], 250, a)
                prog = np.array([0.6 + 0.4 * smoothstep(w["start"] - 0.04, w["start"] + 0.1, t) for w in it["words"]] + [1.0],
                                np.float32)
                sent = L["sent"].copy()
                sent[..., 3] *= prog[L["wid"]]
                _blit(out, sent, 360, a)
                y = 360 + sent.shape[0] + 30
                ga = smoothstep(it["gloss_t"], it["gloss_t"] + 0.4, t) * a
                if ga > 0:
                    lw = 300
                    out[y:y + 2, (W - lw) // 2:(W + lw) // 2] = out[y:y + 2, (W - lw) // 2:(W + lw) // 2] * (1 - ga) + np.array(GOLD, np.float32) / 255 * ga
                    y += 30
                    for gi, g in enumerate(L["gloss"]):
                        gaa = smoothstep(it["gloss_t"] + 0.25 * gi, it["gloss_t"] + 0.25 * gi + 0.4, t) * a
                        rise = int((1 - gaa) * 14)
                        _blit(out, g, y + rise, gaa)
                        y += g.shape[0] + 8
            elif it.get("view") == "vergeben":
                a = smoothstep(it["start"] - 0.2, it["start"] + 0.3, t)
                end_v = max(i2["start"] for i2 in items if i2.get("view") == "photo") - 0.1
                a *= 1 - smoothstep(end_v - 0.4, end_v, t)
                if a <= 0 or idx != min(i for i, x in enumerate(items) if x.get("view") == "vergeben"):
                    continue
                first = it
                q = self._static_block("quote", [("„Sie war noch", self.f_quote, WHITE + (255,), 104),
                                                 ("vergeben.“", self.f_quote, GOLD + (255,), 104)])
                q0 = next(w["start"] for w in first["words"] if w["tok"].startswith("„"))
                qa = smoothstep(q0 - 0.1, q0 + 0.4, t) * a
                _blit(out, q, 330, qa)
                for r_no, spec in ((1, [("① vergeben = schon jemandem zugeteilt", self.f_mean_b, WHITE + (255,), 58),
                                        ("taken, assigned", self.f_ge, (206, 200, 190, 225), 44)]),
                                   (2, [("② vergeben = verzeihen", self.f_mean_b, GOLD + (255,), 58),
                                        ("to forgive", self.f_ge, (206, 200, 190, 225), 44)])):
                    src = next((x for x in items if x.get("reveal") == r_no), None)
                    if src is None:
                        continue
                    ra = smoothstep(src["start"], src["start"] + 0.5, t) * a
                    _blit(out, self._static_block(f"mean{r_no}", spec), 600 + (r_no - 1) * 150 + int((1 - ra) * 12), ra)
            elif it.get("view") == "cta":
                first_cta = min(i for i, x in enumerate(items) if x.get("view") == "cta")
                if idx != first_cta:
                    continue
                a = smoothstep(it["start"] - 0.2, it["start"] + 0.5, t) * (1 - smoothstep(self.tl.duration - 1.6, self.tl.duration - 0.4, t))
                if a <= 0:
                    continue
                ttl = self._static_block("thanks", [("Danke fürs Zuhören", self.f_title, WHITE + (255,), 100)])
                _blit(out, ttl, 430, a)
                btn_it = next((x for x in items if x.get("button")), None)
                if btn_it is not None:
                    tp = btn_it["words"][0]["start"] + 0.12
                    ba = smoothstep(it["start"] + 1.2, it["start"] + 1.8, t) * a
                    press = np.exp(-((t - tp) / 0.09) ** 2) if t > tp - 0.3 else 0.0
                    _blit(out, self._button(t >= tp + 0.05, 1.0 - 0.07 * press), 760, ba, shadow=0.6)
        # narrated subtitles
        for cap in (self.cap_big, self.cap_low):
            for ci, a in cap.visible(t):
                prof_y = cap.y_top + 110
                rows = np.arange(H, dtype=np.float32)
                out *= (1 - 0.4 * a * np.exp(-0.5 * ((rows - prof_y) / 170) ** 2))[:, None, None]
            cap.draw(out, t)
        out *= self.tex.vignette[..., None]
        out *= smoothstep(0, 0.8, t) * (1 - smoothstep(self.tl.duration - 1.2, self.tl.duration, t))
        lum = out.mean(axis=2, keepdims=True)
        out += self.tex.grain[fi % len(self.tex.grain)][..., None] * 0.011 * (1.1 - np.clip(lum, 0, 1))
        return np.clip(out, 0, 1)


# --------------------------------------------------------------------------- build


def build(story_dir, story, story_work, story_tl, story_mp4, images, out_path, workers=4):
    ext = json.load(open(os.path.join(story_dir, "extended.json"), encoding="utf-8"))
    work = os.path.join(story_work, "extended")
    os.makedirs(work, exist_ok=True)
    say = [it for it in ext["items"] if it["type"] == "say"]
    pseudo = {"voices": story["voices"], "lines": say}
    ext_timing = ttsmod.generate(pseudo, story_dir, work)
    story_timing = json.load(open(os.path.join(story_work, "tts_timing.json"), encoding="utf-8"))
    tl = ExtTimeline(ext, story_timing, ext_timing)
    audio = build_audio(tl, story, os.path.join(work, "tts"), os.path.join(story_work, "tts"), work)
    rend = ExtRenderer(tl, ext, story, None, images, story["vocab"])
    ext_mp4 = os.path.join(work, "extended_part.mp4")
    rendermod.render_video(rend, int(round(tl.duration * FPS)), ext_mp4, audio, work, workers=workers)
    lst = os.path.join(work, "concat.txt")
    with open(lst, "w") as f:
        f.write(f"file '{story_mp4}'\nfile '{ext_mp4}'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                    "-movflags", "+faststart", out_path], check=True)
    return out_path, tl, rend
