"""Offline forced alignment (pocketsphinx 5, bundled US-English model).

Given audio and the words that were said, returns per-word start/end times.
Used for the AI narration (word-accurate captions) and for a creator's own
recording, where it also recovers where every script line starts and ends.
"""
from __future__ import annotations

import numpy as np
from scipy.signal import resample_poly


def _pcm16k(audio: np.ndarray, sr: int) -> bytes:
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    a = resample_poly(audio.astype(np.float64), 16000, sr) if sr != 16000 else audio
    peak = np.abs(a).max() or 1.0
    a = a / peak * 0.9
    return (np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes()


def align(audio: np.ndarray, sr: int, words: list[str], lexicon: dict | None = None) -> list[dict]:
    """Returns [{'word', 'start', 'end'}] for each requested word, in order.

    Pocketsphinx reports silences and alternate pronunciations ("the(2)");
    those are folded back onto the requested word list.
    """
    from pocketsphinx import Decoder
    dec = Decoder(bestpath=False, loglevel="FATAL")
    for w, phones in (lexicon or {}).items():      # script-supplied pronunciations (ARPAbet)
        if dec.lookup_word(w.lower()) is None:
            dec.add_word(w.lower(), phones, True)
    for w in words:
        if dec.lookup_word(w) is None:
            raise ValueError(f"word not in aligner dictionary: {w!r} — add it to the script's "
                             f'"lexicon" (ARPAbet, e.g. "B R IH S AH L K OW N") or respell it as {{display|spoken}}')
    dec.set_align_text(" ".join(words))
    dec.start_utt()
    dec.process_raw(_pcm16k(audio, sr), full_utt=True)
    dec.end_utt()
    segs = [s for s in dec.seg() if not s.word.startswith("<") and s.word not in ("[NOISE]",)]
    out = []
    for s in segs:
        w = s.word.split("(")[0]
        out.append({"word": w, "start": s.start_frame / 100.0, "end": (s.end_frame + 1) / 100.0})
    if [o["word"] for o in out] != words:
        got = [o["word"] for o in out]
        raise RuntimeError(f"alignment mismatch: expected {len(words)} words, got {len(got)}: "
                           f"{got[:12]}...")
    return out
