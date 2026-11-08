"""Voiceover generation with Microsoft Edge neural voices (edge-tts).

Each story line is synthesized separately so pauses can be placed by hand.
Word boundaries from the TTS service are mapped onto the subtitle tokens, which
gives word-accurate timing for karaoke subtitles.
"""
import asyncio
import hashlib
import json
import os
import re
import subprocess

import numpy as np
import edge_tts

from .common import SR, read_wav, write_wav

_PUNCT = re.compile(r"[^\wäöüÄÖÜß'-]+")


def norm_token(tok):
    return _PUNCT.sub("", tok).lower()


def line_caption_text(line):
    return " ".join(c[0] for c in line["chunks"])


def line_tts_text(line):
    if line.get("tts"):
        return line["tts"]
    # German quotes are fine for the service, but drop them so nothing is read oddly.
    return line_caption_text(line).replace("„", "").replace("“", "")


async def _synth(text, voice, rate, pitch, mp3_path):
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    com = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch,
                               boundary="WordBoundary", proxy=proxy)
    words = []
    with open(mp3_path, "wb") as f:
        async for ch in com.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append({"text": ch["text"], "start": ch["offset"] / 1e7,
                              "dur": ch["duration"] / 1e7})
    return words


def _trim(x, thresh_db=-48.0, pre=0.03, post=0.09):
    """Return (start_sample, end_sample) of the voiced part."""
    win = int(0.01 * SR)
    env = np.sqrt(np.convolve(x ** 2, np.ones(win) / win, mode="same") + 1e-12)
    voiced = np.where(20 * np.log10(env) > thresh_db)[0]
    if len(voiced) == 0:
        return 0, len(x)
    a = max(0, voiced[0] - int(pre * SR))
    b = min(len(x), voiced[-1] + int(post * SR))
    return a, b


def _align(tokens, words):
    """Map caption tokens to TTS word boundaries (same order, mostly 1:1)."""
    out = []
    wi = 0
    for tok in tokens:
        n = norm_token(tok)
        if not n:  # pure punctuation token, e.g. a dash
            prev = out[-1] if out else {"start": 0.0, "end": 0.0}
            out.append({"tok": tok, "start": prev["end"], "end": prev["end"]})
            continue
        # advance until a matching boundary word (tolerate split/merged words)
        j = wi
        while j < len(words) and norm_token(words[j]["text"]) not in (n, ) \
                and not n.startswith(norm_token(words[j]["text"]) or "#"):
            j += 1
        if j >= len(words):
            j = min(wi, len(words) - 1)
        w = words[j]
        start, end = w["start"], w["start"] + w["dur"]
        # merged token spanning several boundaries ("im Sterben" never merges, but be safe)
        acc = norm_token(w["text"])
        k = j
        while acc != n and k + 1 < len(words) and n.startswith(acc + norm_token(words[k + 1]["text"])):
            k += 1
            acc += norm_token(words[k]["text"])
            end = words[k]["start"] + words[k]["dur"]
        out.append({"tok": tok, "start": start, "end": end})
        wi = k + 1
    return out


def generate(story, story_dir, work):
    tts_dir = os.path.join(work, "tts")
    os.makedirs(tts_dir, exist_ok=True)
    jobs = []
    for line in story["lines"]:
        v = dict(story["voices"][line["voice"]])
        rate = line.get("rate", v["rate"])
        pitch = line.get("pitch", v["pitch"])
        text = line_tts_text(line)
        key = hashlib.sha1(f"{text}|{v['voice']}|{rate}|{pitch}".encode()).hexdigest()[:12]
        jobs.append((line, v["voice"], rate, pitch, text, key))

    async def run_all():
        sem = asyncio.Semaphore(4)

        async def one(job):
            line, voice, rate, pitch, text, key = job
            mp3 = os.path.join(tts_dir, f"{line['id']}_{key}.mp3")
            meta = mp3 + ".json"
            if os.path.exists(meta):
                return
            async with sem:
                for attempt in range(4):
                    try:
                        words = await _synth(text, voice, rate, pitch, mp3)
                        break
                    except Exception:
                        if attempt == 3:
                            raise
                        await asyncio.sleep(2 ** attempt)
            with open(meta, "w") as f:
                json.dump(words, f)

        await asyncio.gather(*(one(j) for j in jobs))

    asyncio.run(run_all())

    timing = {}
    for line, voice, rate, pitch, text, key in jobs:
        mp3 = os.path.join(tts_dir, f"{line['id']}_{key}.mp3")
        wav = os.path.join(tts_dir, f"{line['id']}.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp3, "-ac", "1", "-ar", str(SR),
                        "-c:a", "pcm_f32le", wav], check=True)
        x = read_wav(wav)
        a, b = _trim(x)
        x = x[a:b]
        write_wav(wav, x)
        with open(mp3 + ".json") as f:
            words = json.load(f)
        off = a / SR
        for w in words:
            w["start"] = max(0.0, w["start"] - off)
        tokens = line_caption_text(line).split()
        aligned = _align(tokens, words)
        # never let a word end after the audio does
        dur = len(x) / SR
        for w in aligned:
            w["end"] = min(w["end"], dur)
        # chunk index for every token
        ci = []
        for k, c in enumerate(line["chunks"]):
            ci += [k] * len(c[0].split())
        for w, k in zip(aligned, ci):
            w["chunk"] = k
        timing[line["id"]] = {"dur": dur, "words": aligned, "n_tts_words": len(words)}
        if len(words) != len([t for t in tokens if norm_token(t)]):
            print(f"  note {line['id']}: {len(words)} TTS words vs {len(tokens)} tokens")
    with open(os.path.join(work, "tts_timing.json"), "w") as f:
        json.dump(timing, f, ensure_ascii=False, indent=1)
    return timing
