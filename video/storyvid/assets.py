"""Per-image analysis: super-resolution, depth (Depth Anything V2), window and lamp masks."""
import os

import cv2
import numpy as np
from PIL import Image

MEAN = np.array([0.485, 0.456, 0.406], np.float32)
STD = np.array([0.229, 0.224, 0.225], np.float32)


def load_rgb(path):
    return np.array(Image.open(path).convert("RGB"))


def super_resolve(rgb, model_path, scale=3, tile=200, pad=12):
    sr = cv2.dnn_superres.DnnSuperResImpl_create()
    sr.readModel(model_path)
    sr.setModel("edsr", scale)
    im = rgb[:, :, ::-1].copy()
    h, w = im.shape[:2]
    padded = cv2.copyMakeBorder(im, pad, pad, pad, pad, cv2.BORDER_REFLECT_101)
    out = np.zeros((h * scale, w * scale, 3), np.uint8)
    for y in range(0, h, tile):
        for x in range(0, w, tile):
            th, tw = min(tile, h - y), min(tile, w - x)
            up = sr.upsample(padded[y:y + th + 2 * pad, x:x + tw + 2 * pad])
            out[y * scale:(y + th) * scale, x * scale:(x + tw) * scale] = \
                up[pad * scale:(pad + th) * scale, pad * scale:(pad + tw) * scale]
    return out[:, :, ::-1]


class DepthModel:
    def __init__(self, onnx_path):
        import onnxruntime as ort
        so = ort.SessionOptions()
        so.intra_op_num_threads = 4
        self.s = ort.InferenceSession(onnx_path, so, providers=["CPUExecutionProvider"])
        self.inp = self.s.get_inputs()[0].name

    def _run(self, rgb):
        x = cv2.resize(rgb, (518, 518), interpolation=cv2.INTER_CUBIC).astype(np.float32) / 255.0
        x = ((x - MEAN) / STD).transpose(2, 0, 1)[None]
        return self.s.run(None, {self.inp: x})[0][0]

    def predict(self, rgb):
        """Relative inverse depth (1 = near, 0 = far) at the image's resolution.

        The model takes a fixed 518x518 input, so portrait images are processed as a
        squashed global pass plus aspect-correct square tiles, each tile aligned to
        the global pass by a least-squares scale/shift and feather-blended.
        """
        h, w = rgb.shape[:2]
        g = cv2.resize(self._run(rgb), (w, h), interpolation=cv2.INTER_CUBIC)
        side = min(h, w)
        acc = g * 0.15
        wsum = np.full((h, w), 0.15, np.float32)
        n_t = max(2, int(np.ceil((max(h, w) - side) / (side * 0.5))) + 1)
        offs = np.linspace(0, max(h, w) - side, n_t).astype(int)
        for o in offs:
            if h >= w:
                crop = rgb[o:o + side, :]
            else:
                crop = rgb[:, o:o + side]
            d = cv2.resize(self._run(crop), (crop.shape[1], crop.shape[0]), interpolation=cv2.INTER_CUBIC)
            ref = g[o:o + side, :] if h >= w else g[:, o:o + side]
            A = np.stack([d.ravel(), np.ones(d.size)], 1)
            a, b = np.linalg.lstsq(A, ref.ravel(), rcond=None)[0]
            d = a * d + b
            ramp = np.sin(np.linspace(0, np.pi, side)) ** 2 + 0.02
            wt = (ramp[:, None] * np.ones((1, side))) if h >= w else (np.ones((side, 1)) * ramp[None, :])
            if h >= w:
                acc[o:o + side, :] += d * wt
                wsum[o:o + side, :] += wt
            else:
                acc[:, o:o + side] += d * wt
                wsum[:, o:o + side] += wt
        d = acc / wsum
        lo, hi = np.percentile(d, 1), np.percentile(d, 99.5)
        d = np.clip((d - lo) / (hi - lo + 1e-9), 0, 1).astype(np.float32)
        try:
            guide = rgb.astype(np.float32) / 255.0
            d = cv2.ximgproc.guidedFilter(guide, d, 6, 1e-3)
        except Exception:
            d = cv2.bilateralFilter(d, 9, 0.1, 6)
        return np.clip(d, 0, 1).astype(np.float32)


def window_mask(rgb, depth):
    """Soft mask of rain-streaked window glass: cool blue, not too dark, far away."""
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV).astype(np.float32)
    h, s, v = hsv[..., 0], hsv[..., 1] / 255, hsv[..., 2] / 255
    blue = np.clip(1 - np.abs(h - 103) / 18, 0, 1) * np.clip((s - 0.25) / 0.25, 0, 1) * np.clip((v - 0.18) / 0.2, 0, 1)
    far = np.clip((0.55 - depth) / 0.25, 0, 1)
    m = blue * far
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, k)
    m = cv2.GaussianBlur(m, (0, 0), 3)
    return np.clip(m * 1.3, 0, 1).astype(np.float32)


def warm_mask(rgb):
    """Bright warm light sources (lamp bulbs, lantern glow) for flicker and bloom."""
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV).astype(np.float32)
    h, s, v = hsv[..., 0], hsv[..., 1] / 255, hsv[..., 2] / 255
    warm = np.clip(1 - np.abs(h - 20) / 14, 0, 1) * np.clip((v - 0.62) / 0.25, 0, 1) * np.clip((s - 0.15) / 0.2, 0, 1)
    core = cv2.GaussianBlur(warm, (0, 0), 4)
    glow = cv2.GaussianBlur(warm, (0, 0), 40)
    return np.clip(core * 0.6 + glow * 2.2, 0, 1).astype(np.float32)


def prepare(images, work, models, log=print, do_sr=True):
    """images: {id: path}. Writes depth/mask .npy and SR png into work/assets."""
    adir = os.path.join(work, "assets")
    os.makedirs(adir, exist_ok=True)
    dm = None
    for iid, path in images.items():
        rgb = load_rgb(path)
        dpath = os.path.join(adir, f"{iid}_depth.npy")
        if not os.path.exists(dpath):
            dm = dm or DepthModel(models["depth"])
            depth = dm.predict(rgb)
            np.save(dpath, depth)
            log(f"  depth {iid}")
        depth = np.load(dpath)
        for name, fn in (("window", lambda: window_mask(rgb, depth)), ("warm", lambda: warm_mask(rgb))):
            p = os.path.join(adir, f"{iid}_{name}.npy")
            if not os.path.exists(p):
                np.save(p, fn())
        srp = os.path.join(adir, f"{iid}_sr.png")
        if not os.path.exists(srp):
            ext = os.path.join(work, "sr", f"{iid}.png")   # allow precomputed upscales
            if os.path.exists(ext):
                os.link(ext, srp) if not os.path.exists(srp) else None
            elif do_sr:
                up = super_resolve(rgb, models["sr"])
                Image.fromarray(up).save(srp)
                log(f"  upscaled {iid}")
    return adir
