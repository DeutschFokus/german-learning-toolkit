"""AI narration with Kokoro-82M (Apache-2.0 open weights) through kokoro-onnx.

Runs fully offline once the two model files are cached. No paid API, no voice
cloning: the channel voice is a blend of Kokoro's stock male voices.
"""
from __future__ import annotations

import os
import urllib.request
from pathlib import Path

import numpy as np

MODEL_DIR = Path(os.environ.get("STUDIO_MODELS", Path.home() / ".cache" / "studio-models"))
_BASE = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
MODEL_FILES = {"kokoro-v1.0.onnx": _BASE + "kokoro-v1.0.onnx",
               "voices-v1.0.bin": _BASE + "voices-v1.0.bin"}


def ensure_models() -> Path:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    for name, url in MODEL_FILES.items():
        dest = MODEL_DIR / name
        if not dest.exists() or dest.stat().st_size < 1_000_000:
            print(f"[tts] downloading {name} ...")
            urllib.request.urlretrieve(url, dest)
    return MODEL_DIR


class Narrator:
    """Synthesises one phrase at a time so pauses stay under editorial control."""

    def __init__(self, blend: dict[str, float], speed: float = 1.0, lang: str = "en-us"):
        from kokoro_onnx import Kokoro
        d = ensure_models()
        self.k = Kokoro(str(d / "kokoro-v1.0.onnx"), str(d / "voices-v1.0.bin"))
        total = sum(blend.values())
        self.style = sum((w / total) * self.k.get_voice_style(v) for v, w in blend.items())
        self.speed = speed
        self.lang = lang
        self.sr = 24000

    def say(self, text: str, speed: float | None = None) -> np.ndarray:
        audio, sr = self.k.create(text, voice=self.style, speed=speed or self.speed,
                                  lang=self.lang, trim=True)
        self.sr = sr
        return trim_silence(np.asarray(audio, dtype=np.float32), sr)


def trim_silence(a: np.ndarray, sr: int, thresh_db: float = -45.0, pad: float = 0.03) -> np.ndarray:
    """Trim leading/trailing near-silence, keep a short pad so consonants survive."""
    if a.size == 0:
        return a
    win = int(sr * 0.01)
    env = np.sqrt(np.convolve(a ** 2, np.ones(win) / win, mode="same"))
    peak = env.max() or 1.0
    idx = np.where(env > peak * 10 ** (thresh_db / 20))[0]
    if idx.size == 0:
        return a
    p = int(pad * sr)
    return a[max(0, idx[0] - p): min(a.size, idx[-1] + p)]
