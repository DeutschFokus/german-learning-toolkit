"""Photo plates: turn a still (photo, stock, AI image) into a moving 2.5D camera shot.

Pipeline
  1. `DepthModel` estimates relative depth with Depth Anything V2 Small (Apache-2.0),
     run locally through onnxruntime. The weights download once (~99 MB) into
     ~/.cache/lumen/models and are checked against a SHA-256.
  2. `Plate` cover-fits the image to 9:16 with overscan, splits it into depth layers,
     fills what each nearer layer hides (smooth fill + mirrored texture), and caches it.
  3. `Plate.render(cam, inserts)` warps every layer with per-pixel parallax for a
     virtual camera (push-in, orbit, crane, roll, dolly-zoom) and composites them
     back to front. `inserts` slots RGBA overlays *between* layers, which is how a
     title can sit behind a foreground subject.
  4. `blit(cv, img)` writes the frame into the canvas base layer; `glow_from(cv, img)`
     feeds its highlights to the bloom/god-ray layer, so the usual LUMEN finish applies.

Depth is relative (near = 1, far = 0), so camera moves are expressed in screen pixels
of parallax, not metres.
"""
from __future__ import annotations

import hashlib
import os
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from .gfx import W, H, Canvas

MODEL_URL = ("https://github.com/fabio-sim/Depth-Anything-ONNX/releases/download/v2.0.0/"
             "depth_anything_v2_vits.onnx")
MODEL_SHA256 = "d2b11a11c1d4a12b47608fa65a17ee9a4c605b55ee1730c8e3b526304f2562be"
CACHE = Path(os.environ.get("LUMEN_CACHE", Path.home() / ".cache" / "lumen"))
_MEAN = np.array([0.485, 0.456, 0.406], np.float32)
_STD = np.array([0.229, 0.224, 0.225], np.float32)


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class DepthModel:
    """Depth Anything V2 Small (ViT-S, Apache-2.0) at a fixed 518x518 input."""

    N = 518

    def __init__(self, path: Path | None = None):
        import onnxruntime as ort
        path = Path(path) if path else CACHE / "models" / "depth_anything_v2_vits.onnx"
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(".part")
            urllib.request.urlretrieve(MODEL_URL, tmp)
            if _sha256(tmp) != MODEL_SHA256:
                tmp.unlink()
                raise RuntimeError("depth model checksum mismatch")
            tmp.rename(path)
        so = ort.SessionOptions()
        so.intra_op_num_threads = os.cpu_count() or 4
        self.sess = ort.InferenceSession(str(path), so, providers=["CPUExecutionProvider"])
        self.inp = self.sess.get_inputs()[0].name

    def _run(self, rgb: np.ndarray) -> np.ndarray:
        x = cv2.resize(rgb, (self.N, self.N), interpolation=cv2.INTER_CUBIC).astype(np.float32) / 255
        x = ((x - _MEAN) / _STD).transpose(2, 0, 1)[None]
        return self.sess.run(None, {self.inp: x})[0][0]

    def predict(self, rgb: np.ndarray) -> np.ndarray:
        """Relative inverse depth at the image's resolution, normalised to 0 (far) .. 1 (near).

        One squashed global pass fixes the overall layout; square tiles along the long side
        add undistorted detail and are affinely aligned to the global pass, then feathered.
        """
        h, w = rgb.shape[:2]
        glob = cv2.resize(self._run(rgb), (w, h), interpolation=cv2.INTER_CUBIC)
        s = min(h, w)
        n = int(np.ceil(max(h, w) / s * 1.35))
        if n <= 1:
            out = glob
        else:
            acc = np.zeros((h, w), np.float32)
            wsum = np.zeros((h, w), np.float32)
            for k in range(n):
                o = int(round(k * (max(h, w) - s) / (n - 1)))
                sl = (slice(o, o + s), slice(0, w)) if h > w else (slice(0, h), slice(o, o + s))
                tile = cv2.resize(self._run(rgb[sl]), (s, s), interpolation=cv2.INTER_CUBIC)
                g = glob[sl]
                A = np.stack([tile.ravel(), np.ones(tile.size, np.float32)], 1)
                a, b = np.linalg.lstsq(A[::7], g.ravel()[::7], rcond=None)[0]
                ramp = np.minimum(np.linspace(0, 1, s), np.linspace(1, 0, s)) * 2
                ramp = np.clip(ramp * 3, 0.02, 1).astype(np.float32)
                wt = ramp[:, None] * np.ones((1, s), np.float32) if h > w else \
                    np.ones((s, 1), np.float32) * ramp[None, :]
                acc[sl] += (a * tile + b) * wt
                wsum[sl] += wt
            out = acc / np.maximum(wsum, 1e-6)
        lo, hi = np.percentile(out, [0.5, 99.5])
        return np.clip((out - lo) / max(hi - lo, 1e-6), 0, 1).astype(np.float32)


# --------------------------------------------------------------------------- helpers
def _smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def snap_edges(d: np.ndarray, k=13, thr=0.12) -> np.ndarray:
    """Make depth silhouettes crisp: across a discontinuity the model blurs depth over a few
    pixels, and those in-between values would float as thin 'echo' outlines between layers.
    Near a jump each pixel takes the nearer of its neighbourhood's min or max."""
    ker = np.ones((k, k), np.uint8)
    lo, hi = cv2.erode(d, ker), cv2.dilate(d, ker)
    snapped = np.where(d - lo < hi - d, lo, hi)
    return np.where(hi - lo > thr, snapped, d).astype(np.float32)


def auto_cuts(d: np.ndarray, n: int, sep=0.14):
    """Depth thresholds that cut along discontinuities (silhouettes), not across
    continuous surfaces: for each candidate, the share of the cut's boundary that
    lies on a strong depth edge."""
    small = cv2.resize(d, (d.shape[1] // 4, d.shape[0] // 4), interpolation=cv2.INTER_AREA)
    gx = cv2.Sobel(small, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(small, cv2.CV_32F, 0, 1, ksize=3)
    g = np.sqrt(gx * gx + gy * gy)
    edge = g > np.percentile(g, 90)
    cands = []
    for t in np.linspace(0.10, 0.90, 41):
        m = (small >= t).astype(np.uint8)
        frac = m.mean()
        if frac < 0.03 or frac > 0.85:
            continue
        bd = cv2.morphologyEx(m, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)) > 0
        nb = bd.sum()
        if nb == 0:
            continue
        cands.append(((edge & bd).sum() / nb, t))
    cands.sort(reverse=True)
    cuts = []
    for score, t in cands:
        if all(abs(t - c) >= sep for c in cuts):
            cuts.append(t)
        if len(cuts) == n:
            break
    return sorted(cuts)


def fill(v: np.ndarray, known: np.ndarray, weight: np.ndarray | None = None) -> np.ndarray:
    """Push-pull hole filling: unknown pixels get a smooth blend of the known ones around
    them, from progressively coarser levels (depth or colour). `weight` biases which known
    pixels win, e.g. favouring the far background that a moving subject would reveal."""
    v = v.astype(np.float32)
    k = known.astype(np.float32)
    wk = k * (weight.astype(np.float32) if weight is not None else 1.0)
    ex = (lambda a: a[..., None]) if v.ndim == 3 else (lambda a: a)
    num, den, conf = v * ex(wk), wk, k
    levels = []
    while max(num.shape[:2]) > 1:
        levels.append((num, den, conf))
        size = (max(1, num.shape[1] // 2), max(1, num.shape[0] // 2))
        num = cv2.resize(num, size, interpolation=cv2.INTER_AREA)
        den = cv2.resize(den, size, interpolation=cv2.INTER_AREA)
        conf = cv2.resize(conf, size, interpolation=cv2.INTER_AREA)
        if num.ndim < v.ndim:
            num = num[..., None]
    # coarsest level: anything still empty takes the weighted mean of all known pixels
    mean = (v * ex(wk)).reshape(-1, *v.shape[2:]).sum(0) / max(float(wk.sum()), 1e-8)
    filled = np.where(ex(den) > 1e-8, num / ex(np.maximum(den, 1e-8)), mean)
    for n_, d_, c_ in reversed(levels):
        up = cv2.resize(filled, (n_.shape[1], n_.shape[0]), interpolation=cv2.INTER_LINEAR)
        w = ex(np.clip(c_ * 2.0, 0, 1) * (d_ > 1e-6))
        filled = n_ / ex(np.maximum(d_, 1e-8)) * w + up * (1 - w)
    return np.where(ex(k) > 0.5, v, filled)


def texture_fill(img: np.ndarray, known: np.ndarray, weight=None, reach=70.0) -> np.ndarray:
    """Colour fill with texture: the smooth push-pull fill plus fine detail mirrored across
    the hole's border, so foliage or clouds revealed behind a subject keep their grain
    instead of turning into a smudge. Detail fades out deeper than `reach` px."""
    from scipy.ndimage import distance_transform_edt
    base = fill(img, known, weight)
    hole = known == 0
    if not hole.any():
        return base
    dist, (iy, ix) = distance_transform_edt(hole, return_indices=True)
    h, w = known.shape
    yy, xx = np.mgrid[0:h, 0:w]
    my = np.clip(2 * iy - yy, 0, h - 1)
    mx = np.clip(2 * ix - xx, 0, w - 1)
    ok = (known[my, mx] > 0).astype(np.float32)
    hp = img - cv2.GaussianBlur(img, (0, 0), 2.2)
    fade = (np.clip(1 - dist / reach, 0, 1) * ok)[..., None]
    out = base + hp[my, mx] * fade
    return np.where(hole[..., None], np.clip(out, 0, 1), img).astype(np.float32)


# --------------------------------------------------------------------------- camera
@dataclass
class Cam:
    """A virtual camera move, in output pixels. Depth d: 0 far .. 1 near.

    push   dolly-in: a pixel at depth d is magnified by 1 + push * (bias + (1 - bias) * d)
    zoom   lens zoom (uniform); with push it gives the dolly-zoom ("vertigo") look
    orbit  (x, y) parallax at d = 1 relative to `focus`; far things move the other way
    pan    (x, y) uniform shift; roll in radians; center = optical centre on screen
    """
    push: float = 0.0
    zoom: float = 1.0
    orbit: tuple = (0.0, 0.0)
    pan: tuple = (0.0, 0.0)
    roll: float = 0.0
    focus: float = 0.5
    bias: float = 0.15
    center: tuple = (W / 2, H / 2)

    def mag(self, d):
        return self.zoom * (1 + self.push * (self.bias + (1 - self.bias) * d))

    def vertigo_zoom(self):
        """The zoom that keeps the focus depth the same size while pushing (dolly zoom)."""
        return 1 / (1 + self.push * (self.bias + (1 - self.bias) * self.focus))

    @staticmethod
    def lerp(a: "Cam", b: "Cam", x: float) -> "Cam":
        f = lambda u, v: u + (v - u) * x
        t2 = lambda u, v: (f(u[0], v[0]), f(u[1], v[1]))
        return Cam(f(a.push, b.push), f(a.zoom, b.zoom), t2(a.orbit, b.orbit), t2(a.pan, b.pan),
                   f(a.roll, b.roll), f(a.focus, b.focus), f(a.bias, b.bias), t2(a.center, b.center))


# --------------------------------------------------------------------------- plate
@dataclass
class _Layer:
    col: np.ndarray      # float32 BGR (Hp, Wp, 3), colours extended past the edge
    alpha: np.ndarray    # float32 (Hp, Wp)
    depth: np.ndarray    # float32 (Hp, Wp), hidden parts inpainted


class Plate:
    """A still prepared for 2.5D moves. Construct once per shot (it caches to disk)."""

    def __init__(self, path, fx=0.5, fy=0.5, overscan=1.14, cuts=None, layers=3,
                 model: DepthModel | None = None, cache=True, sharpen=0.35):
        path = Path(path)
        src = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if src is None:
            raise FileNotFoundError(path)
        self.Wp, self.Hp = int(round(W * overscan)), int(round(H * overscan))
        self.ox, self.oy = (self.Wp - W) / 2, (self.Hp - H) / 2
        # cover-fit crop at native resolution (depth runs here), anchored at (fx, fy)
        sh, sw = src.shape[:2]
        k = max(self.Wp / sw, self.Hp / sh)
        cw, ch = int(round(self.Wp / k)), int(round(self.Hp / k))
        x0 = int(round(np.clip(fx * sw - cw / 2, 0, sw - cw)))
        y0 = int(round(np.clip(fy * sh - ch / 2, 0, sh - ch)))
        crop = src[y0:y0 + ch, x0:x0 + cw]
        self.upscale = k
        self.crop = (x0, y0, k)          # source pixel (ix, iy) -> plate ((ix-x0)*k, (iy-y0)*k)
        key = hashlib.sha1(f"{_sha256(path)}|{fx}|{fy}|{overscan}|{cuts}|{layers}|v10".encode()).hexdigest()[:16]
        cdir = CACHE / "plates"
        cfile = cdir / f"{path.stem}_{key}.npz"
        if cache and cfile.exists():
            z = np.load(cfile)
            self.depth, self.cuts = z["depth"], list(z["cuts"])
            self.layers = [_Layer(z[f"c{i}"].astype(np.float32) / 255, z[f"a{i}"].astype(np.float32) / 255,
                                  z[f"d{i}"]) for i in range(int(z["n"]))]
            return
        model = model or DepthModel()
        d_small = model.predict(np.ascontiguousarray(crop[..., ::-1]))
        interp = cv2.INTER_LANCZOS4 if k > 1 else cv2.INTER_AREA
        img = cv2.resize(crop, (self.Wp, self.Hp), interpolation=interp).astype(np.float32) / 255
        if k > 1.05 and sharpen > 0:
            img = np.clip(img + sharpen * (img - cv2.GaussianBlur(img, (0, 0), 1.2 * k)), 0, 1)
        d = cv2.resize(d_small, (self.Wp, self.Hp), interpolation=cv2.INTER_CUBIC)
        self.depth = snap_edges(np.clip(d, 0, 1).astype(np.float32))
        self.cuts = sorted(cuts) if cuts is not None else auto_cuts(self.depth, layers - 1)
        self.layers = self._build(img, self.depth, self.cuts)
        if cache:
            cdir.mkdir(parents=True, exist_ok=True)
            arrs = {"depth": self.depth, "cuts": np.array(self.cuts, np.float32), "n": len(self.layers)}
            for i, ly in enumerate(self.layers):
                arrs[f"c{i}"] = (ly.col * 255 + 0.5).astype(np.uint8)
                arrs[f"a{i}"] = (ly.alpha * 255 + 0.5).astype(np.uint8)
                arrs[f"d{i}"] = ly.depth
            np.savez_compressed(cfile, **arrs)

    @staticmethod
    def _build(img, d, cuts, reach_px=48):
        img8 = (img * 255 + 0.5).astype(np.uint8)
        bounds = [-1.0] + list(cuts) + [2.0]
        out = []
        for i in range(len(bounds) - 1):
            lo, hi = bounds[i], bounds[i + 1]
            last = i == len(bounds) - 2
            # alpha: everything at least as near as this layer (its own pixels plus what the
            # nearer layers hide); depth edges from the model are already tight
            if i == 0:
                a = np.ones_like(d)
            else:
                a = cv2.GaussianBlur(_smoothstep(lo - 0.015, lo + 0.015, d), (0, 0), 0.8)
                if not last:
                    # a middle layer only extends behind nearer things close to its own pixels;
                    # where a subject stands straight against the far background this layer
                    # must not exist, or its edge would trail the subject as a ghost outline
                    own = ((d >= lo) & (d < hi)).astype(np.uint8)
                    reach = cv2.dilate(own, np.ones((2 * reach_px + 1, 2 * reach_px + 1), np.uint8))
                    a = a * cv2.GaussianBlur(reach.astype(np.float32), (0, 0), 6)
            col, dep = img.copy(), d.copy()
            if not last:
                # what nearer layers cover is filled from this layer and the ones behind it
                # (a generous margin: photos carry halos and soft edges just outside the
                # silhouette, which would otherwise stay behind as "echo" outlines)
                known = (d < hi - 0.01).astype(np.uint8)
                known = cv2.erode(known, np.ones((25, 25), np.uint8))
                hm = cv2.GaussianBlur(1.0 - known.astype(np.float32), (0, 0), 3.5)
                # what a moving subject reveals is usually the *local* background: weight known
                # pixels by how close they are to the farthest depth in their neighbourhood
                dk = np.where(known > 0, d, 1.0).astype(np.float32)
                local_far = cv2.erode(dk, np.ones((41, 41), np.uint8))
                far = np.exp(-np.clip(d - local_far, 0, None) / 0.06) + 1e-3
                col = col * (1 - hm[..., None]) + texture_fill(img, known, far) * hm[..., None]
                dep = dep * (1 - hm) + fill(d, known, far) * hm
            if i > 0:
                # extend this layer's colours a few px outward so its soft edge never shows
                # the background it was cut from
                inside = (a > 0.5).astype(np.uint8)
                band = cv2.dilate(inside, np.ones((13, 13), np.uint8)) - inside
                c8 = (np.clip(col, 0, 1) * 255 + 0.5).astype(np.uint8)
                ext = cv2.inpaint(c8, band, 5, cv2.INPAINT_TELEA).astype(np.float32) / 255
                col = np.where(band[..., None] > 0, ext, col)
                # and extend its depth smoothly over *everything* outside it: the inverse warp
                # is a fixed-point search, and a depth cliff at the silhouette makes it flip
                # between the two sides and print detached slivers of the subject
                dep = np.where(inside > 0, dep, fill(dep, inside))
            out.append(_Layer(col.astype(np.float32), a.astype(np.float32), dep.astype(np.float32)))
        return out

    # ------------------------------------------------------------------ rendering
    def _maps(self, cam: Cam, depth, iters=4):
        if not hasattr(self, "_grid"):
            qy, qx = np.mgrid[0:H, 0:W].astype(np.float32)
            self._grid = (qx, qy)
        qx, qy = self._grid
        cx, cy = cam.center
        c, s = np.cos(-cam.roll), np.sin(-cam.roll)
        ox, oy = cam.orbit
        d = np.full((H, W), cam.focus, np.float32)
        for _ in range(iters):
            m = cam.mag(d)
            ux = qx - cx - cam.pan[0] - ox * (d - cam.focus)
            uy = qy - cy - cam.pan[1] - oy * (d - cam.focus)
            rx, ry = c * ux - s * uy, s * ux + c * uy
            px = (rx / m + cx + self.ox).astype(np.float32)
            py = (ry / m + cy + self.oy).astype(np.float32)
            d = cv2.remap(depth, px, py, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        return px, py

    def render(self, cam: Cam, inserts=(), fog=None):
        """Composite the layers for `cam`. inserts: [(layer_index, rgba)] where rgba is a
        premultiplied float32 BGRA (H, W, 4) drawn *behind* layer `layer_index`.
        fog: (bgr, amount, power) haze that grows with distance. Returns float32 BGR."""
        out = np.zeros((H, W, 3), np.float32)
        ins = sorted(inserts, key=lambda x: x[0])
        for i, ly in enumerate(self.layers):
            for j, rgba in ins:
                if j == i:
                    out = out * (1 - rgba[..., 3:4]) + rgba[..., :3]
            px, py = self._maps(cam, ly.depth)
            col = cv2.remap(ly.col, px, py, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            if fog is not None:
                fc, fa, fp = fog
                dd = cv2.remap(ly.depth, px, py, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
                f = (fa * (1 - dd) ** fp)[..., None]
                col = col * (1 - f) + np.array(fc, np.float32) * f
            if i == 0:
                out = col
            else:
                a = cv2.remap(ly.alpha, px, py, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)[..., None]
                out = out * (1 - a) + col * a
        for j, rgba in ins:
            if j >= len(self.layers):
                out = out * (1 - rgba[..., 3:4]) + rgba[..., :3]
        return out

    def screen_point(self, cam: Cam, ix, iy):
        """Where source-image pixel (ix, iy) lands on screen for `cam` (for labels that stick
        to things in the picture)."""
        x0, y0, k = self.crop
        px, py = (ix - x0) * k, (iy - y0) * k
        d = float(self.depth[int(np.clip(py, 0, self.Hp - 1)), int(np.clip(px, 0, self.Wp - 1))])
        m = cam.mag(d)
        cx, cy = cam.center
        rx, ry = (px - self.ox - cx) * m, (py - self.oy - cy) * m
        c, s = np.cos(cam.roll), np.sin(cam.roll)
        return (cx + cam.pan[0] + cam.orbit[0] * (d - cam.focus) + c * rx - s * ry,
                cy + cam.pan[1] + cam.orbit[1] * (d - cam.focus) + s * rx + c * ry)

    def depth_view(self, cam: Cam):
        """The warped depth map for `cam` (for wipes / look-dev)."""
        px, py = self._maps(cam, self.layers[0].depth)
        return cv2.remap(self.depth, px, py, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


# --------------------------------------------------------------------------- canvas glue
def blit(cv: Canvas, img: np.ndarray):
    """Write a float32 BGR frame into the canvas base layer (draw overlays after this)."""
    cv.base_s.flush()
    buf = np.ndarray((H, W, 4), np.uint8, cv.base_s.get_data())
    buf[..., :3] = (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)
    buf[..., 3] = 255
    cv.base_s.mark_dirty()


def glow_from(cv: Canvas, img: np.ndarray, thresh=0.78, gain=1.2, tint=(1.0, 1.0, 1.0)):
    """Feed a frame's highlights to the half-res glow layer (bloom, and god rays via cv.rays)."""
    small = cv2.resize(img, (W // 2, H // 2), interpolation=cv2.INTER_AREA)
    lum = small.max(axis=2, keepdims=True)
    g = np.clip((lum - thresh) / (1 - thresh), 0, 1) ** 1.5 * small * gain * np.array(tint, np.float32)
    cv.glow_s.flush()
    buf = np.ndarray((H // 2, W // 2, 4), np.uint8, cv.glow_s.get_data())
    cur = buf[..., :3].astype(np.float32) / 255
    buf[..., :3] = (np.clip(np.maximum(cur, g), 0, 1) * 255 + 0.5).astype(np.uint8)
    buf[..., 3] = np.maximum(buf[..., 3], (np.clip(g.max(axis=2), 0, 1) * 255).astype(np.uint8))
    cv.glow_s.mark_dirty()


def rgba_layer(draw_fn):
    """Draw with cairo (draw_fn(ctx)) into a transparent full frame; returns premultiplied
    float32 BGRA (H, W, 4) for Plate.render inserts."""
    import cairo
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(s)
    draw_fn(ctx)
    s.flush()
    return np.ndarray((H, W, 4), np.uint8, s.get_data()).astype(np.float32) / 255


# --------------------------------------------------------------------------- preview CLI
_PV = None


def _pv_frame(i):
    plate, cam_at, post, fps = _PV
    from .gfx import Canvas as _Canvas
    cv = _Canvas()
    img = plate.render(cam_at(i / fps))
    blit(cv, img)
    glow_from(cv, img, thresh=0.86, gain=0.55)
    return post.finish(cv, i)


def preview(path, out=None, seconds=5.0, fx=0.5, fy=0.5, cuts=None, layers=3, push=0.09, orbit=22.0,
            focus=0.55, workers=4):
    """Render a quick look-dev move for one image plus a sheet (photo | depth | layers), so a
    new image can be judged before it goes into an episode."""
    global _PV
    import multiprocessing as mp
    import subprocess
    from .gfx import ease_in_out
    from .postfx import Post
    from .render import encode_cmd
    path = Path(path)
    out = Path(out) if out else path.with_name(path.stem + "_plate_preview.mp4")
    plate = Plate(path, fx=fx, fy=fy, cuts=cuts, layers=layers)
    fps, n = 30, int(round(seconds * 30))

    def cam_at(t):
        x = ease_in_out(t / seconds)
        return Cam(push=push * x, orbit=(orbit * (1 - 2 * x), -orbit * 0.22 * (1 - 2 * x)), focus=focus)

    _PV = (plate, cam_at, Post(seed=5, grain=0.010), fps)
    cmd = encode_cmd(out, fps, None, 18)
    cmd[cmd.index("-t") + 1] = "%.3f" % (n / fps)
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with mp.get_context("fork").Pool(workers) as pool:
        for buf in pool.imap(_pv_frame, range(n), chunksize=2):
            proc.stdin.write(buf)
    proc.stdin.close()
    if proc.wait():
        raise SystemExit("ffmpeg failed")
    # sheet: the frame at rest, the depth map, then each layer over a checkerboard
    tw, th = 270, 480
    chk = ((np.indices((th, tw)).sum(0) // 12) % 2 * 0.25 + 0.4).astype(np.float32)[..., None]
    rest = plate.render(Cam(focus=focus))
    tiles = [cv2.resize(rest, (tw, th)),
             cv2.applyColorMap((cv2.resize(plate.depth, (tw, th)) * 255).astype(np.uint8),
                               cv2.COLORMAP_INFERNO).astype(np.float32) / 255]
    for ly in plate.layers:
        a = cv2.resize(ly.alpha, (tw, th))[..., None]
        tiles.append(cv2.resize(ly.col, (tw, th)) * a + chk * (1 - a))
    sheet = out.with_suffix(".png")
    cv2.imwrite(str(sheet), (np.clip(np.hstack(tiles), 0, 1) * 255).astype(np.uint8))
    print(f"[plates] {out}  {sheet}  cuts={[round(float(c), 3) for c in plate.cuts]}")
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Preview an image as a 2.5D camera move.")
    ap.add_argument("cmd", choices=["preview"])
    ap.add_argument("image")
    ap.add_argument("--out")
    ap.add_argument("--seconds", type=float, default=5.0)
    ap.add_argument("--fx", type=float, default=0.5, help="horizontal crop anchor 0..1")
    ap.add_argument("--fy", type=float, default=0.5, help="vertical crop anchor 0..1")
    ap.add_argument("--cuts", help="depth cuts, e.g. 0.3,0.45 (default: automatic)")
    ap.add_argument("--layers", type=int, default=3)
    ap.add_argument("--push", type=float, default=0.09)
    ap.add_argument("--orbit", type=float, default=22.0)
    ap.add_argument("--focus", type=float, default=0.55)
    a = ap.parse_args()
    preview(a.image, a.out, a.seconds, a.fx, a.fy,
            [float(c) for c in a.cuts.split(",")] if a.cuts else None, a.layers, a.push, a.orbit, a.focus)
