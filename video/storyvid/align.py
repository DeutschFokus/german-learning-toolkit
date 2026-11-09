"""Align a human narration to the script.

The synthetic lines (edge-tts) have exact word timings. Both the synthetic reference and
the human recording are turned into speaker-normalised MFCC sequences and matched with
subsequence DTW, so the narrator can speak at any pace, pause anywhere and even leave
some talk before or after the take. Every word boundary of the reference is mapped onto
the recording, which gives the same timing format the TTS step produces; the rest of the
pipeline (subtitles, music cues, sound effects, camera) then simply follows the human voice.
"""
import json
import os
import subprocess

import numpy as np
from scipy import fft as sfft
from scipy import signal

from .common import SR, read_wav, write_wav

FR = 16000          # analysis rate
HOP = 320           # 20 ms frames
NFFT = 512


def load_any(path, sr=FR):
    """Decode any audio file (m4a, mp3, wav, ...) to mono float32."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def _mel_fb(n_mels=40, fmin=60.0, fmax=7600.0):
    def hz2mel(f):
        return 2595 * np.log10(1 + f / 700)

    def mel2hz(m):
        return 700 * (10 ** (m / 2595) - 1)

    pts = mel2hz(np.linspace(hz2mel(fmin), hz2mel(fmax), n_mels + 2))
    bins = np.fft.rfftfreq(NFFT, 1 / FR)
    fb = np.zeros((n_mels, len(bins)), np.float32)
    for m in range(n_mels):
        lo, ce, hi = pts[m], pts[m + 1], pts[m + 2]
        fb[m] = np.clip(np.minimum((bins - lo) / (ce - lo), (hi - bins) / (hi - ce)), 0, None)
    return fb


_FB = _mel_fb()


def _power(y):
    y = y - y.mean()
    y = np.append(y[0], y[1:] - 0.97 * y[:-1])      # pre-emphasis
    _, _, Z = signal.stft(y, fs=FR, window="hann", nperseg=NFFT, noverlap=NFFT - HOP,
                          boundary=None, padded=False)
    return (np.abs(Z) ** 2).astype(np.float32)


def features(y):
    """Speaker-normalised MFCC 1-13 + deltas, plus a speech/silence channel."""
    P = _power(y)
    logmel = np.log(_FB @ P + 1e-8)
    cep = sfft.dct(logmel, type=2, axis=0, norm="ortho")[1:14]
    f = np.vstack([cep, np.gradient(cep, axis=1)])
    f = (f - f.mean(1, keepdims=True)) / (f.std(1, keepdims=True) + 1e-6)   # CMVN
    return np.vstack([f, 3.0 * voicing(P)[None]]).astype(np.float32)


def voicing(P):
    """0..1 speech-likeness per frame from log energy, robust to the recording level."""
    le = np.log(P.sum(0) + 1e-10)
    lo, hi = np.percentile(le, 8), np.percentile(le, 97)
    return np.clip((le - lo) / (hi - lo + 1e-9), 0, 1)


def _cost_row(X, Y, x2, y2, i, j0=0, j1=None):
    return np.sqrt(np.maximum(x2[i] + y2[j0:j1] - 2 * X[:, i] @ Y[:, j0:j1], 0)).astype(np.float64)


def _dtw_matrix(X, Y, skip=None):
    """Accumulated cost with the symmetric step pattern (diagonal steps weigh 2), which has no
    bias towards short paths. Rows are vectorised: D[i] = C + prefix_min(A - C).
    With `skip`, the path may also begin and end anywhere in Y, paying `skip` per skipped frame
    (so extra talk around the take is dropped, but real script never is)."""
    n, m = X.shape[1], Y.shape[1]
    x2, y2 = (X ** 2).sum(0), (Y ** 2).sum(0)
    D = np.empty((n, m))
    c = _cost_row(X, Y, x2, y2, 0)
    C = np.cumsum(c)
    if skip is None:
        D[0] = C + c[0]
    else:
        start = skip * np.arange(m) + 2 * c
        D[0] = C + np.minimum.accumulate(start - C)
    for i in range(1, n):
        c = _cost_row(X, Y, x2, y2, i)
        prev = D[i - 1]
        a = np.empty(m)
        a[0] = prev[0] + c[0]
        a[1:] = np.minimum(prev[:-1] + 2 * c[1:], prev[1:] + c[1:])
        C = np.cumsum(c)
        D[i] = C + np.minimum.accumulate(a - C)
    return D, x2, y2


def _backtrack(D, X, Y, x2, y2, i, j, skip=None):
    path = [(i, j)]
    while i > 0 or j > 0:
        if i == 0:
            if skip is not None:
                c0 = float(np.sqrt(max(x2[0] + y2[j] - 2 * X[:, 0] @ Y[:, j], 0)))
                if abs(D[0, j] - (skip * j + 2 * c0)) < 1e-6 * max(1.0, D[0, j]):
                    break                                   # the path starts here
            j -= 1
        elif j == 0:
            i -= 1
        else:
            cij = float(np.sqrt(max(x2[i] + y2[j] - 2 * X[:, i] @ Y[:, j], 0)))
            _, i, j = min((D[i - 1, j - 1] + 2 * cij, i - 1, j - 1), (D[i - 1, j] + cij, i - 1, j),
                          (D[i, j - 1] + cij, i, j - 1))
        path.append((i, j))
    return np.array(path[::-1])


def dtw(X, Y):
    D, x2, y2 = _dtw_matrix(X, Y)
    return _backtrack(D, X, Y, x2, y2, X.shape[1] - 1, Y.shape[1] - 1)


def _shift(row, k, fill=np.inf):
    out = np.full_like(row, fill)
    out[k:] = row[:-k]
    return out


def dtw_slope(X, Y, skip=None):
    """DTW with steps (1,1), (1,2), (2,1): local tempo ratio stays within 0.5x-2x, so the path
    can never collapse into long horizontal or vertical runs. Weights follow step length
    (2, 3, 3), so there is no bias towards short paths. Each row only depends on the two
    previous rows, which makes the recursion fully vectorised.
    With `skip`, the path may begin and end anywhere in Y at `skip` per skipped frame."""
    n, m = X.shape[1], Y.shape[1]
    x2, y2 = (X ** 2).sum(0), (Y ** 2).sum(0)
    D = np.full((n, m), np.inf)
    c = _cost_row(X, Y, x2, y2, 0)
    if skip is None:
        D[0, 0] = 2 * c[0]
    else:
        D[0] = skip * np.arange(m) + 2 * c
    for i in range(1, n):
        c = _cost_row(X, Y, x2, y2, i)
        best = np.minimum(_shift(D[i - 1], 1) + 2 * c, _shift(D[i - 1], 2) + 3 * c)
        if i >= 2:
            best = np.minimum(best, _shift(D[i - 2], 1) + 3 * c)
        D[i] = best
    if skip is None:
        j = m - 1
    else:
        j = int(np.argmin(D[-1] + skip * (m - 1 - np.arange(m))))
    i = n - 1
    if not np.isfinite(D[i, j]):
        raise ValueError("recording and script are too different in length to align")
    path = [(i, j)]
    while i > 0:
        cij = float(np.sqrt(max(x2[i] + y2[j] - 2 * X[:, i] @ Y[:, j], 0)))
        opts = []
        if j >= 1:
            opts.append((D[i - 1, j - 1] + 2 * cij, i - 1, j - 1))
        if j >= 2:
            opts.append((D[i - 1, j - 2] + 3 * cij, i - 1, j - 2))
        if i >= 2 and j >= 1:
            opts.append((D[i - 2, j - 1] + 3 * cij, i - 2, j - 1))
        _, ni, nj = min(opts)
        if nj == j - 2:
            path.append((i, j - 1))              # fill the skipped cell so every frame is mapped
        if ni == i - 2:
            path.append((i - 1, j))
        i, j = ni, nj
        path.append((i, j))
    return np.array(path[::-1]), float(D[-1, path[-1][1]] if False else D[n - 1, j if False else path[-1][1]])


def _open_end_cost(X, Y):
    """Best length-normalised cost of matching all of X to some prefix of Y (slope-limited)."""
    n, m = X.shape[1], Y.shape[1]
    x2, y2 = (X ** 2).sum(0), (Y ** 2).sum(0)
    D = np.full((n, m), np.inf)
    D[0, 0] = 2 * _cost_row(X, Y, x2, y2, 0)[0]
    for i in range(1, n):
        c = _cost_row(X, Y, x2, y2, i)
        best = np.minimum(_shift(D[i - 1], 1) + 2 * c, _shift(D[i - 1], 2) + 3 * c)
        if i >= 2:
            best = np.minimum(best, _shift(D[i - 2], 1) + 3 * c)
        D[i] = best
    norm = D[-1] / (n + np.arange(1, m + 1))
    return float(np.min(norm))


def _locate_story(X, Y, onsets, offsets, span=600):
    """Where in the recording do the first and the last ~12 s of the script start/end?
    Candidates are speech onsets/offsets; the best match (slope-limited DTW) wins."""
    n = X.shape[1]
    k = min(span, n // 2)
    head, tail = X[:, :k], X[:, -k:][:, ::-1]
    best_s = (np.inf, 0)
    for o in onsets:
        w = Y[:, o:o + int(2.2 * k)]
        if w.shape[1] >= k // 2 + 2:
            best_s = min(best_s, (_open_end_cost(head, w), o))
    Yr = Y[:, ::-1]
    m = Y.shape[1]
    best_e = (np.inf, m - 1)
    for e in offsets:
        r = m - 1 - e
        w = Yr[:, r:r + int(2.2 * k)]
        if w.shape[1] >= k // 2 + 2:
            best_e = min(best_e, (_open_end_cost(tail, w), e))
    return best_s[1], best_e[1]


def squeeze_pauses(v, keep=15, thr=0.15):
    """Indices of frames kept when every pause is shortened to at most `keep` frames."""
    on = np.convolve(v, np.ones(3) / 3, mode="same") > thr
    idx, i, n = [], 0, len(v)
    while i < n:
        if on[i]:
            idx.append(i)
            i += 1
            continue
        j = i
        while j < n and not on[j]:
            j += 1
        L = j - i
        if L <= keep:
            idx.extend(range(i, j))
        else:
            h = keep // 2
            idx.extend(range(i, i + h))
            idx.extend(range(j - (keep - h), j))
        i = j
    return np.array(idx, dtype=np.int64)


def speech_segments(rec, min_gap=0.25):
    """(start, end) frame ranges of speech, from a level-independent energy threshold."""
    v = voicing(_power(rec))
    v = np.convolve(v, np.ones(5) / 5, mode="same")
    on = v > 0.42
    segs, i, n = [], 0, len(on)
    gap = int(min_gap * FR / HOP)
    while i < n:
        if on[i]:
            j = i
            while j < n and (on[j] or (j + gap < n and on[j:j + gap].any())):
                j += 1
            segs.append((i, j))
            i = j
        else:
            i += 1
    return segs, v


def _reference(lines, tts_dir, timing, gap=0.6, pad=0.15):
    """Concatenate the synthetic lines with short gaps; return audio and word times in it."""
    g = np.zeros(int(gap * FR), np.float32)
    parts, words, t = [np.zeros(int(pad * FR), np.float32)], [], pad
    for line in lines:
        lid = line["id"]
        x = read_wav(os.path.join(tts_dir, f"{lid}.wav"))
        x = signal.resample_poly(x, FR, SR).astype(np.float32)
        parts += [x, g]
        for k, w in enumerate(timing[lid]["words"]):
            words.append((lid, k, t + w["start"], t + w["end"]))
        t += len(x) / FR + gap
    parts[-1] = np.zeros(int(pad * FR), np.float32)
    return np.concatenate(parts), words


def align(lines, tts_dir, tts_timing, recording, log=print):
    """Map every word of `lines` onto `recording` (path). Returns ({lid: {start, end, words}} in
    recording seconds, mean match cost per frame, decoded recording)."""
    ref, rwords = _reference(lines, tts_dir, tts_timing)
    rec = load_any(recording)
    if len(rec) < FR:
        raise ValueError("recording is shorter than a second")
    segs, v = speech_segments(rec)
    if not segs:
        raise ValueError("no speech found in the recording")
    margin = int(0.3 * FR / HOP)
    j0 = max(0, segs[0][0] - margin)
    j1 = min(len(v), segs[-1][1] + margin)
    seg = rec[j0 * HOP: j1 * HOP + NFFT]
    Xf, Yf = features(ref), features(seg)
    vref = voicing(_power(ref))
    ir = squeeze_pauses(vref)                     # reference frames kept
    iy = squeeze_pauses(v[j0:j1][:Yf.shape[1]])   # recording frames kept
    X, Y = Xf[:, ir], Yf[:, iy]
    n, m = X.shape[1], Y.shape[1]
    log(f"    aligning {n * HOP / FR:.0f}s of script speech against {m * HOP / FR:.0f}s of recorded speech")
    # find where the story starts and ends (there may be talk around it), then align globally
    on = np.convolve(v[j0:j1][iy] if len(iy) else v[j0:j1], np.ones(3) / 3, mode="same") > 0.15
    edges = np.flatnonzero(np.diff(on.astype(np.int8)))
    onsets = [0] + [int(e) + 1 for e in edges if not on[e]]
    offsets = [int(e) for e in edges if on[e]] + [m - 1]
    onsets = [o for o in onsets if o < m * 0.5][:10]
    offsets = [o for o in offsets if o > m * 0.5][-10:]
    a_, b_ = _locate_story(X, Y, onsets, offsets)
    if b_ - a_ < n // 2:
        a_, b_ = 0, m - 1
    # only drop talk that is clearly separate from the story (a real pause, >= 0.8 s)
    vv = v[j0:j1]
    def gap_before(k):
        o = iy[k]; g = 0
        while o - g - 1 >= 0 and vv[o - g - 1] < 0.15: g += 1
        return g * HOP / FR
    def gap_after(k):
        o = iy[k]; g = 0
        while o + g + 1 < len(vv) and vv[o + g + 1] < 0.15: g += 1
        return g * HOP / FR
    if a_ > 0 and gap_before(a_) < 0.8:
        a_ = 0
    if b_ < m - 1 and gap_after(b_) < 0.8:
        b_ = m - 1
    if a_ > 0 or b_ < m - 1:
        log(f"    ignoring {a_ * HOP / FR:.1f}s before and {(m - 1 - b_) * HOP / FR:.1f}s after the story")
    path, _ = dtw_slope(X, Y[:, a_:b_ + 1])
    path[:, 1] += a_
    step = max(1, len(path) // 3000)
    mu = float(np.mean([np.linalg.norm(X[:, i] - Y[:, j]) for i, j in path[::step]]))
    # back to un-squeezed frame numbers
    path = np.stack([ir[path[:, 0]], iy[path[:, 1]]], axis=1)
    n = Xf.shape[1]
    jmin = np.full(n, np.iinfo(np.int64).max)
    jmax = np.full(n, -1)
    np.minimum.at(jmin, path[:, 0], path[:, 1])
    np.maximum.at(jmax, path[:, 0], path[:, 1])
    off = NFFT / 2 / FR
    vs = v[j0:j1]

    def fr(t):
        return int(np.clip(round(max(0.0, t - off) * FR / HOP), 0, n - 1))

    out = {line["id"]: {"words": []} for line in lines}
    for lid, k, ts, te in rwords:
        a = int(jmin[fr(ts)])
        b = int(jmax[max(fr(ts), fr(te) - 1)]) + 1
        # snap onto actual speech: a word never starts or ends inside a pause
        # (a low threshold keeps soft attacks such as "f", "s" or "h" inside the word)
        moved = False
        while a < b - 2 and a < len(vs) and vs[a] < 0.12:
            a += 1
            moved = True
        if moved:                      # word after a pause: keep the soft attack
            a = max(0, a - 4)
        while b > a + 2 and b - 1 < len(vs) and vs[b - 1] < 0.12:
            b -= 1
        out[lid]["words"].append({"k": k, "start": (j0 + a) * HOP / FR + off,
                                  "end": (j0 + b) * HOP / FR + off})
    flat = [w for line in lines for w in out[line["id"]]["words"]]
    for x, y in zip(flat, flat[1:]):
        if y["start"] < x["start"]:
            y["start"] = x["start"]
        if x["end"] > y["start"]:
            x["end"] = max(x["start"] + 0.04, y["start"])
    for line in lines:
        ws = out[line["id"]]["words"]
        out[line["id"]]["start"], out[line["id"]]["end"] = ws[0]["start"], ws[-1]["end"]
    return out, float(mu), rec


PRE, POST = 0.06, 0.22      # audio kept before the first and after the last word of a line


def to_timing(lines, aligned, tts_timing, pre=PRE):
    """Convert aligned absolute times to the per-line timing format (words relative to the start
    of the line's audio, which begins `pre` seconds before the first word)."""
    timing = {}
    for line in lines:
        lid = line["id"]
        a = aligned[lid]
        s = a["start"] - pre
        words = []
        for w, ref in zip(a["words"], tts_timing[lid]["words"]):
            words.append(dict(ref, start=w["start"] - s, end=w["end"] - s))
        timing[lid] = {"dur": a["end"] - s, "words": words, "n_tts_words": tts_timing[lid].get("n_tts_words")}
    return timing


def clean_voice(path, out_path):
    """Gentle clean-up for a home recording: rumble filter, broadband denoise, de-esser."""
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-ac", "1", "-ar", str(SR),
                    "-af", "highpass=f=70,afftdn=nr=10:nf=-50:tn=1,deesser=i=0.35",
                    "-c:a", "pcm_f32le", out_path], check=True)
    return out_path


def slice_lines(lines, aligned, voice48, out_dir, pre=PRE, post=POST):
    """Write one WAV per line (cut from the cleaned recording) for re-use, e.g. vocabulary replays."""
    os.makedirs(out_dir, exist_ok=True)
    x = read_wav(voice48)
    for line in lines:
        a = aligned[line["id"]]
        i0 = max(0, int((a["start"] - pre) * SR))
        i1 = min(len(x), int((a["end"] + post) * SR))
        seg = x[i0:i1].copy()
        r = int(0.01 * SR)
        seg[:r] *= np.linspace(0, 1, r)
        seg[-r:] *= np.linspace(1, 0, r)
        write_wav(os.path.join(out_dir, f"{line['id']}.wav"), seg)
    return out_dir


def align_story(lines, tts_dir, tts_timing, recording, work, log=print):
    """Full step: align, clean, slice. Returns (timing, starts_in_recording, voice48_path, cost)."""
    os.makedirs(work, exist_ok=True)
    aligned, cost, _ = align(lines, tts_dir, tts_timing, recording, log=log)
    with open(os.path.join(work, "alignment.json"), "w") as f:
        json.dump({"cost": cost, "lines": aligned}, f, indent=1)
    voice48 = clean_voice(recording, os.path.join(work, "voice_clean.wav"))
    slice_lines(lines, aligned, voice48, os.path.join(work, "lines"))
    starts = {line["id"]: aligned[line["id"]]["start"] - PRE for line in lines}
    # lines squeezed or stretched to the limit usually mean a skipped, repeated or misread line
    odd = []
    for line in lines:
        a = aligned[line["id"]]
        ref = tts_timing[line["id"]]["words"]
        r = (a["end"] - a["start"]) / max(0.2, ref[-1]["end"] - ref[0]["start"])
        if r < 0.5 or r > 2.4:
            odd.append(f"{line['id']} ({r:.1f}x)")
    if odd:
        log("    check these lines in the result (unusual length vs. the script): " + ", ".join(odd))
    return to_timing(lines, aligned, tts_timing), starts, voice48, cost
