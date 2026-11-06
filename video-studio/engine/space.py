"""Deep-space props: a Milky Way sky, a detailed 3D-projected Voyager, the
golden record, a 70 m Deep Space Network dish, an incandescent bulb, the
pale-blue-dot frame, brainwave (EEG) and heartbeat (EKG) traces.
"""
from __future__ import annotations

import math

import cairo
import cv2
import numpy as np

from .gfx import L, Canvas, W, H, clamp, lerp, mix


def _surf(rgb, a):
    h, w = a.shape
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    buf = np.ndarray((h, s.get_stride() // 4, 4), np.uint8, s.get_data())
    a = np.clip(a, 0, 1)
    pm = np.clip(rgb, 0, 1) * a[..., None]
    buf[:, :w, 0] = (pm[..., 2] * 255 + 0.5).astype(np.uint8)
    buf[:, :w, 1] = (pm[..., 1] * 255 + 0.5).astype(np.uint8)
    buf[:, :w, 2] = (pm[..., 0] * 255 + 0.5).astype(np.uint8)
    buf[:, :w, 3] = (a * 255 + 0.5).astype(np.uint8)
    s.mark_dirty()
    return s


def _noise(rng, h, w, scale, octaves=5):
    acc = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        sh, sw = max(2, int(h / scale * 2 ** o)), max(2, int(w / scale * 2 ** o))
        acc += amp * cv2.resize(rng.random((sh, sw)).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC)
        tot += amp
        amp *= 0.55
    acc /= tot
    return (acc - acc.min()) / (np.ptp(acc) + 1e-6)


# =========================================================================== the sky

class MilkyWay:
    """A large static sky texture: a tilted galactic band with dust lanes, glow and dense stars."""

    def __init__(self, w=1500, h=2400, seed=11, angle=-0.95):
        rng = np.random.default_rng(seed)
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        cx, cy = w / 2, h / 2
        u = (xx - cx) * math.cos(angle) + (yy - cy) * math.sin(angle)
        v = -(xx - cx) * math.sin(angle) + (yy - cy) * math.cos(angle)
        band = np.exp(-(v / (w * 0.20)) ** 2)
        n1 = _noise(rng, h, w, 220)
        n2 = _noise(rng, h, w, 60)
        dust = np.clip((n2 - 0.45) * 2.4, 0, 1) * np.exp(-(v / (w * 0.08)) ** 2)
        glow = band * (0.35 + 0.65 * n1) * (1 - 0.75 * dust)
        core = np.exp(-((u - w * 0.10) / (w * 0.55)) ** 2) * band
        col = np.zeros((h, w, 3), np.float32)
        col += np.array([0.10, 0.12, 0.22], np.float32) * glow[..., None] * 0.9
        col += np.array([0.55, 0.42, 0.30], np.float32) * (core * glow * 0.55)[..., None]
        neb = np.clip((n1 - 0.62) * 3.0, 0, 1) * band
        col += np.array([0.35, 0.10, 0.25], np.float32) * neb[..., None] * 0.35
        # stars: more inside the band
        st = np.zeros((h, w), np.float32)
        n_st = 26000
        ys = rng.integers(0, h, n_st)
        xs = rng.integers(0, w, n_st)
        keep = rng.random(n_st) < (0.25 + 0.75 * band[ys, xs])
        st[ys[keep], xs[keep]] = rng.uniform(0.25, 1.0, keep.sum()) ** 2.2
        st = cv2.GaussianBlur(st, (0, 0), 0.6) * 3.2
        tint = rng.random((h, w)).astype(np.float32)
        scol = np.where(tint[..., None] > 0.7, np.array([1.0, 0.85, 0.7]), np.array([0.8, 0.88, 1.0]))
        col += scol * st[..., None]
        self.surf = _surf(col, np.ones((h, w), np.float32))
        self.w, self.h = w, h
        # bright stars drawn per frame (twinkle, glow)
        self.bright = [(rng.uniform(0, w), rng.uniform(0, h), rng.uniform(1.4, 3.0), rng.uniform(0, 6.28),
                        int(rng.integers(3, 12))) for _ in range(60)]

    def draw(self, cv: Canvas, t, ox=0.0, oy=0.0, scale=1.0, alpha=1.0, loop=60.0):
        b = cv.b
        b.save()
        b.translate(W / 2 + ox, H / 2 + oy)
        b.scale(scale, scale)
        b.translate(-self.w / 2, -self.h / 2)
        b.set_source_surface(self.surf, 0, 0)
        b.paint_with_alpha(alpha)
        b.restore()
        for x, y, r, ph, cyc in self.bright:
            px = W / 2 + ox + (x - self.w / 2) * scale
            py = H / 2 + oy + (y - self.h / 2) * scale
            if -10 < px < W + 10 and -10 < py < H + 10:
                tw = 0.75 + 0.25 * math.sin(2 * math.pi * cyc * t / loop + ph)
                cv.circle(px, py, r * scale ** 0.5, (0.9, 0.93, 1.0), alpha=alpha * tw, glow=0.9 * tw)


# =========================================================================== Voyager

def _rot(yaw, pitch, roll):
    cy, sy = math.cos(yaw), math.sin(yaw)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cr, sr = math.cos(roll), math.sin(roll)
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]])
    Rz = np.array([[cr, -sr, 0], [sr, cr, 0], [0, 0, 1]])
    return Rz @ Rx @ Ry


def _circle3(c, n, r, k=48):
    """Points of a circle centred c with normal n, radius r."""
    n = np.asarray(n, float)
    n = n / np.linalg.norm(n)
    a = np.array([1.0, 0, 0]) if abs(n[0]) < 0.9 else np.array([0, 1.0, 0])
    u = np.cross(n, a)
    u /= np.linalg.norm(u)
    v = np.cross(n, u)
    th = np.linspace(0, 2 * np.pi, k, endpoint=False)
    return np.asarray(c, float) + r * (np.outer(np.cos(th), u) + np.outer(np.sin(th), v))


class Voyager3D:
    """Voyager spacecraft (approximate real proportions, metres). The dish looks along +Z."""

    GOLD = (0.86, 0.64, 0.26)
    WHITE = (0.90, 0.92, 0.95)
    GREY = (0.55, 0.58, 0.64)
    DARK = (0.18, 0.19, 0.22)

    def __init__(self):
        self.parts = []
        # dish (3.66 m), depth ~0.45 m; feed on struts
        self.dish_r, self.dish_depth = 1.83, 0.45
        bus_z = -0.70
        self.bus = [(math.cos(2 * math.pi * k / 10 + 0.31) * 0.95, math.sin(2 * math.pi * k / 10 + 0.31) * 0.95)
                    for k in range(10)]
        self.bus_z0, self.bus_z1 = bus_z - 0.24, bus_z + 0.24
        self.rtg_boom = (np.array([-0.95, -0.05, bus_z]), np.array([-3.25, -0.30, bus_z - 0.10]))
        self.rtgs = [np.array([-2.15 - 0.52 * k, -0.18 - 0.05 * k, bus_z - 0.05 - 0.02 * k]) for k in range(3)]
        self.sci_boom = (np.array([0.95, 0.05, bus_z]), np.array([2.55, 0.25, bus_z]))
        self.platform = np.array([2.75, 0.32, bus_z])
        d = np.array([-0.62, 0.42, -0.66])
        d /= np.linalg.norm(d)
        self.mag_boom = (np.array([-0.55, 0.55, bus_z - 0.20]), np.array([-0.55, 0.55, bus_z - 0.20]) + d * 13.0)
        self.pws = [(np.array([-0.30, -0.80, bus_z - 0.20]), np.array([-4.6, -8.6, bus_z + 1.2])),
                    (np.array([-0.10, -0.85, bus_z - 0.25]), np.array([-1.0, -9.8, bus_z - 2.6]))]
        # golden record on the bus side facing -X/+Z-ish
        a = 2 * math.pi * 6 / 10 + 0.31 + math.pi / 10
        self.record_c = np.array([math.cos(a) * 0.93, math.sin(a) * 0.93, bus_z])
        self.record_n = np.array([math.cos(a), math.sin(a), 0.0])

    def draw(self, cv: Canvas, x, y, scale, yaw=0.6, pitch=-0.35, roll=0.15, alpha=1.0, light=(0.55, 0.35, 0.75),
             record_glow=0.0, rim=(0.55, 0.75, 1.0), t=0.0, dist=14.0):
        """(x, y): screen position of the dish centre; scale: px per metre at that distance."""
        if alpha <= 0.003:
            return
        rim_color = rim
        R = _rot(yaw, pitch, roll)
        Lv = np.asarray(light, float)
        Lv = Lv / np.linalg.norm(Lv)

        def P(p):
            q = R @ np.asarray(p, float)
            k = dist / (dist - q[2])
            return (x + q[0] * scale * k, y - q[1] * scale * k), q[2]

        items = []

        def add(depth, fn):
            items.append((depth, fn))

        # ---- booms and antennas (thin)
        def seg(a, b, col, w, n_truss=0):
            (pa, za), (pb, zb) = P(a), P(b)

            def f():
                cv.line([pa, pb], col, width=w, alpha=alpha * 0.95)
                if n_truss:
                    for k in range(n_truss):
                        u0, u1 = k / n_truss, (k + 1) / n_truss
                        q0 = (lerp(pa[0], pb[0], u0) + 3, lerp(pa[1], pb[1], u0) + 3)
                        q1 = (lerp(pa[0], pb[0], u1) - 3, lerp(pa[1], pb[1], u1) - 3)
                        cv.line([q0, q1], col, width=max(0.8, w * 0.5), alpha=alpha * 0.6)
            add((za + zb) / 2, f)

        seg(*self.mag_boom, (0.78, 0.80, 0.86), 2.2, n_truss=26)
        for a_, b_ in self.pws:
            seg(a_, b_, (0.80, 0.82, 0.88), 1.4)
        seg(*self.rtg_boom, self.GREY, 4.5)
        seg(*self.sci_boom, self.GREY, 4.5)

        # ---- RTGs (finned cylinders along the boom)
        ax = self.rtg_boom[1] - self.rtg_boom[0]
        ax = ax / np.linalg.norm(ax)
        for c in self.rtgs:
            self._cyl(cv, add, P, R, Lv, c - ax * 0.22, c + ax * 0.22, 0.20, self.DARK, alpha, fins=6)

        # ---- science platform with cameras
        pc = self.platform
        self._box(cv, add, P, R, Lv, pc, (0.35, 0.30, 0.40), self.GREY, alpha)
        for off, rr, ln in (((0.05, 0.22, 0.10), 0.09, 0.55), ((-0.08, 0.18, -0.12), 0.06, 0.32)):
            c0 = pc + np.array(off)
            self._cyl(cv, add, P, R, Lv, c0, c0 + np.array([0.05, 0.12, ln]), rr, (0.70, 0.72, 0.78), alpha)

        # ---- bus: decagonal prism wrapped in gold blankets
        for k in range(10):
            p0, p1 = self.bus[k], self.bus[(k + 1) % 10]
            quad = [(p0[0], p0[1], self.bus_z0), (p1[0], p1[1], self.bus_z0), (p1[0], p1[1], self.bus_z1),
                    (p0[0], p0[1], self.bus_z1)]
            n = np.array([(p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, 0.0])
            n /= np.linalg.norm(n)
            nr = R @ n
            if nr[2] <= -0.05:
                continue
            pts = [P(q)[0] for q in quad]
            depth = float(np.mean([P(q)[1] for q in quad]))
            shade = 0.35 + 0.65 * max(0.0, float(nr @ Lv))
            col = tuple(c * shade for c in self.GOLD)

            def f(pts=pts, col=col, k=k, shade=shade):
                cv.poly(pts, col, alpha=alpha)
                # crinkled blanket highlights
                for j in range(3):
                    u = (j + 0.5) / 3
                    a_ = (lerp(pts[0][0], pts[1][0], u), lerp(pts[0][1], pts[1][1], u))
                    b_ = (lerp(pts[3][0], pts[2][0], u + 0.08), lerp(pts[3][1], pts[2][1], u + 0.08))
                    cv.line([a_, b_], (1.0, 0.85, 0.5), width=1.2, alpha=alpha * 0.35 * shade)
                cv.line(pts + [pts[0]], (0.35, 0.25, 0.10), width=1.0, alpha=alpha * 0.6)
            add(depth, f)
        # back cap of the bus
        cap = [(p[0], p[1], self.bus_z0) for p in self.bus]
        n_cap = R @ np.array([0, 0, -1.0])
        if n_cap[2] > 0:
            pts = [P(q)[0] for q in cap]
            add(float(np.mean([P(q)[1] for q in cap])) - 0.01, lambda pts=pts: cv.poly(pts, (0.30, 0.24, 0.12), alpha=alpha))

        # ---- the golden record on the bus
        rc = self.record_c
        rn = R @ self.record_n
        rec_rim = _circle3(rc + self.record_n * 0.01, self.record_n, 0.16, 36)
        rpts = [P(q)[0] for q in rec_rim]
        rdepth = float(np.mean([P(q)[1] for q in rec_rim])) + 0.02

        def frec(rpts=rpts, rn=rn):
            if rn[2] > 0:
                cv.poly(rpts, (0.95, 0.75, 0.30), alpha=alpha)
                cv.poly(rpts, (1.0, 0.85, 0.45), alpha=alpha * (0.3 + 0.7 * record_glow), glow=1.2 * record_glow + 0.2)
        add(rdepth, frec)

        # ---- the dish: paraboloid with ribs; feed horn on struts
        dish_rim = _circle3((0, 0, self.dish_depth), (0, 0, 1), self.dish_r, 64)
        dpts = [P(q)[0] for q in dish_rim]
        dn = R @ np.array([0, 0, 1.0])
        ddepth = float(np.mean([P(q)[1] for q in dish_rim]))
        front = dn[2] > 0
        cpos, _ = P((0, 0, 0.0))

        def fdish(dpts=dpts, front=front, cpos=cpos):
            xs = [p[0] for p in dpts]
            ys = [p[1] for p in dpts]
            mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
            rr = max(max(xs) - min(xs), max(ys) - min(ys)) / 2
            for ctx, gl in ((cv.b, False), (cv.g, True)):
                ctx.new_path()
                ctx.move_to(*dpts[0])
                for q in dpts[1:]:
                    ctx.line_to(*q)
                ctx.close_path()
                if not gl:
                    if front:
                        pat = cairo.RadialGradient(cpos[0], cpos[1], rr * 0.05, mx, my, rr * 1.05)
                        pat.add_color_stop_rgba(0, 0.55, 0.58, 0.64, alpha)
                        pat.add_color_stop_rgba(0.75, 0.86, 0.88, 0.92, alpha)
                        pat.add_color_stop_rgba(1, 0.97, 0.98, 1.0, alpha)
                    else:
                        pat = cairo.LinearGradient(mx - rr, my - rr, mx + rr, my + rr)
                        pat.add_color_stop_rgba(0, 0.70, 0.72, 0.78, alpha)
                        pat.add_color_stop_rgba(1, 0.30, 0.32, 0.38, alpha)
                    ctx.set_source(pat)
                    ctx.fill_preserve()
                    ctx.set_source_rgba(*rim_col, alpha * 0.9)
                    ctx.set_line_width(2.4)
                    ctx.stroke()
                else:
                    ctx.set_source_rgba(*rim_col, alpha * 0.25)
                    ctx.set_line_width(5)
                    ctx.stroke()
            if front:
                for k in range(16):
                    q = dpts[k * 4]
                    cv.line([cpos, q], (0.62, 0.66, 0.74), width=1.0, alpha=alpha * 0.45)
                for f_ in (0.35, 0.68):
                    ring = [(lerp(cpos[0], q[0], f_), lerp(cpos[1], q[1], f_)) for q in dpts]
                    cv.line(ring + [ring[0]], (0.62, 0.66, 0.74), width=1.0, alpha=alpha * 0.35)
        rim_col = rim_color
        add(ddepth, fdish)
        # feed: subreflector on four struts
        feed = np.array([0, 0, 1.25])
        fp, fz = P(feed)
        for k in range(4):
            a_ = k * math.pi / 2 + math.pi / 4
            base = (math.cos(a_) * 0.75, math.sin(a_) * 0.75, 0.75 ** 2 / (4 * 1.85))
            seg(base, feed, (0.80, 0.82, 0.88), 1.6)
        add(fz + 0.01, lambda: (cv.circle(fp[0], fp[1], 0.20 * scale, self.WHITE, alpha=alpha),
                                cv.circle(fp[0], fp[1], 0.20 * scale, self.GREY, alpha=alpha, fill=False, width=1.5)))
        for _, fn in sorted(items, key=lambda it: it[0]):
            fn()

    # --- primitives
    def _cyl(self, cv, add, P, R, Lv, a, b, r, col, alpha, fins=0):
        ax = np.asarray(b, float) - np.asarray(a, float)
        c0 = _circle3(a, ax, r, 20)
        c1 = _circle3(b, ax, r, 20)
        p0 = [P(q)[0] for q in c0]
        p1 = [P(q)[0] for q in c1]
        depth = float(np.mean([P(q)[1] for q in np.vstack([c0, c1])]))
        axr = R @ (ax / np.linalg.norm(ax))
        side = np.cross(axr, [0, 0, 1.0])
        shade = 0.45 + 0.55 * abs(float(np.dot(side / (np.linalg.norm(side) + 1e-9), Lv)))
        pts = np.array(p0 + p1)
        hull = cv2.convexHull(pts.astype(np.float32)).reshape(-1, 2)
        colr = tuple(c * shade for c in col)

        def f():
            cv.poly([tuple(p) for p in hull], colr, alpha=alpha)
            end = p1 if axr[2] > 0 else p0
            cv.poly(end, tuple(min(1, c * 1.25) for c in colr), alpha=alpha)
            cv.line([tuple(p) for p in hull] + [tuple(hull[0])], (0.12, 0.12, 0.14), width=1.0, alpha=alpha * 0.6)
            if fins:
                for k in range(fins):
                    th = 2 * math.pi * k / fins
                    for u in (0.2, 0.8):
                        cen = np.asarray(a) + ax * u
                        d = _circle3(cen, ax, r * 1.6, fins)[k]
                        q0 = P(_circle3(cen, ax, r, fins)[k])[0]
                        q1 = P(d)[0]
                        cv.line([q0, q1], (0.30, 0.31, 0.35), width=2.0, alpha=alpha * 0.8)
        add(depth, f)

    def _box(self, cv, add, P, R, Lv, c, size, col, alpha):
        sx, sy, sz = size
        corners = np.array([[dx, dy, dz] for dx in (-sx / 2, sx / 2) for dy in (-sy / 2, sy / 2)
                            for dz in (-sz / 2, sz / 2)]) + c
        faces = [((0, 1, 3, 2), (-1, 0, 0)), ((4, 5, 7, 6), (1, 0, 0)), ((0, 1, 5, 4), (0, -1, 0)),
                 ((2, 3, 7, 6), (0, 1, 0)), ((0, 2, 6, 4), (0, 0, -1)), ((1, 3, 7, 5), (0, 0, 1))]
        for idx, n in faces:
            nr = R @ np.array(n, float)
            if nr[2] <= 0:
                continue
            pts = [P(corners[i])[0] for i in idx]
            depth = float(np.mean([P(corners[i])[1] for i in idx]))
            shade = 0.4 + 0.6 * max(0.0, float(nr @ Lv))
            add(depth, lambda pts=pts, shade=shade: cv.poly(pts, tuple(v * shade for v in col), alpha=alpha))


# =========================================================================== golden record

class GoldenRecord:
    """A gold disc with grooves (numpy texture) and an engraved-cover variant."""

    def __init__(self, size=900, seed=3):
        rng = np.random.default_rng(seed)
        S = size
        yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
        dx, dy = xx - S / 2, yy - S / 2
        r = np.hypot(dx, dy) / (S / 2)
        th = np.arctan2(dy, dx)
        grooves = 0.5 + 0.5 * np.sin(r * 420 + rng.uniform(0, 1))
        bands = (np.sin(r * 38) > 0.92).astype(np.float32) * (r > 0.38) * (r < 0.95)
        aniso = 0.5 + 0.5 * np.cos(2 * (th - 0.7))
        gold = np.array([0.86, 0.66, 0.30], np.float32)
        col = gold * (0.55 + 0.25 * grooves[..., None] + 0.45 * (aniso[..., None] ** 6))
        col *= (1 - 0.25 * bands[..., None])
        label = (r < 0.34)
        col[label] = gold * 0.85
        col[r < 0.025] = (0.08, 0.06, 0.04)
        a = np.clip((1 - r) * S / 3, 0, 1)
        self.disc = _surf(col, a)
        self.size = S
        # engraved cover (the instructions): pulsar map, hydrogen, play diagram
        s = cairo.ImageSurface(cairo.FORMAT_ARGB32, S, S)
        c = cairo.Context(s)
        c.arc(S / 2, S / 2, S / 2, 0, 2 * math.pi)
        pat = cairo.RadialGradient(S * 0.35, S * 0.3, 0, S / 2, S / 2, S / 2)
        pat.add_color_stop_rgb(0, 0.95, 0.80, 0.45)
        pat.add_color_stop_rgb(1, 0.62, 0.45, 0.18)
        c.set_source(pat)
        c.fill()
        c.set_source_rgba(0.35, 0.22, 0.06, 0.9)
        c.set_line_width(2.0)
        # pulsar map: 14 lines from a centre with tick codes
        px, py = S * 0.30, S * 0.70
        for k in range(14):
            ang = rng.uniform(0, 2 * math.pi)
            ln = rng.uniform(0.10, 0.26) * S
            c.move_to(px, py)
            c.line_to(px + math.cos(ang) * ln, py + math.sin(ang) * ln)
            c.stroke()
            for j in range(8):
                u = 0.4 + j * 0.07
                if rng.random() < 0.5:
                    tx, ty = px + math.cos(ang) * ln * u, py + math.sin(ang) * ln * u
                    c.move_to(tx - math.sin(ang) * 5, ty + math.cos(ang) * 5)
                    c.line_to(tx + math.sin(ang) * 5, ty - math.cos(ang) * 5)
                    c.stroke()
        c.move_to(px + S * 0.03, py)
        c.line_to(px + S * 0.42, py)
        c.stroke()
        # hydrogen hyperfine transition: two circles joined
        hx, hy = S * 0.64, S * 0.76
        for k in (-1, 1):
            c.arc(hx + k * S * 0.05, hy, S * 0.035, 0, 2 * math.pi)
            c.stroke()
            c.arc(hx + k * S * 0.05, hy, S * 0.006, 0, 2 * math.pi)
            c.fill()
        c.move_to(hx - S * 0.015, hy)
        c.line_to(hx + S * 0.015, hy)
        c.stroke()
        # the record and stylus, seen from above and side
        rx, ry = S * 0.30, S * 0.30
        c.arc(rx, ry, S * 0.12, 0, 2 * math.pi)
        c.stroke()
        c.arc(rx, ry, S * 0.02, 0, 2 * math.pi)
        c.stroke()
        c.move_to(rx + S * 0.14, ry - S * 0.10)
        c.line_to(rx + S * 0.06, ry + S * 0.02)
        c.stroke()
        c.rectangle(rx - S * 0.12, ry + S * 0.17, S * 0.24, S * 0.02)
        c.stroke()
        # picture-scan diagrams
        for k in range(3):
            bx, by = S * 0.58 + k * S * 0.0, S * 0.22 + k * S * 0.12
            c.rectangle(bx, by, S * 0.22, S * 0.08)
            c.stroke()
            for j in range(9):
                c.move_to(bx + j * S * 0.024, by)
                c.line_to(bx + j * S * 0.024 + S * 0.012, by + S * 0.08)
            c.stroke()
        s.flush()
        self.cover = s

    def draw(self, cv: Canvas, x, y, r, rot=0.0, alpha=1.0, glow=0.3, cover=0.0, tilt=1.0):
        S = self.size
        for ctx, a in ((cv.b, alpha), (cv.g, alpha * glow)):
            if a <= 0.003:
                continue
            ctx.save()
            ctx.translate(x, y)
            ctx.scale(1.0, tilt)
            ctx.rotate(rot)
            ctx.scale(2 * r / S, 2 * r / S)
            ctx.translate(-S / 2, -S / 2)
            ctx.set_source_surface(self.disc, 0, 0)
            ctx.get_source().set_filter(cairo.FILTER_GOOD)
            ctx.paint_with_alpha(a * (1 - cover))
            if cover > 0:
                ctx.set_source_surface(self.cover, 0, 0)
                ctx.paint_with_alpha(a * cover)
            ctx.restore()
        # moving specular sweep (light catches the grooves)
        cv.radial(x + r * 0.35 * math.cos(rot * 0.7), y - r * 0.25 * tilt, r * 0.35, (1.0, 0.92, 0.7),
                  alpha=0.25 * alpha * (1 - cover), glow=0.4)


# =========================================================================== Earth-side hardware

def dsn_dish(cv: Canvas, x, y, s, alpha=1.0, glow=0.4, t=0.0):
    """70 m Deep Space Network antenna in silhouette, aimed up and to the left. (x, y) = ground centre."""
    if alpha <= 0.003:
        return
    col = (0.62, 0.68, 0.80)
    # pedestal and yoke
    cv.poly([(x - 140 * s, y), (x + 140 * s, y), (x + 80 * s, y - 230 * s), (x - 80 * s, y - 230 * s)], (0.10, 0.12, 0.18),
            alpha=alpha)
    cv.line([(x - 140 * s, y), (x - 80 * s, y - 230 * s), (x + 80 * s, y - 230 * s), (x + 140 * s, y)], col, width=2.5,
            alpha=alpha * 0.8)
    # dish: an ellipse tilted toward the sky
    b = cv.b
    cx, cy = x - 30 * s, y - 360 * s
    for ctx, gl in ((cv.b, False), (cv.g, True)):
        ctx.save()
        ctx.translate(cx, cy)
        ctx.rotate(-0.55)
        ctx.scale(260 * s, 120 * s)
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()
        if not gl:
            pat = cairo.LinearGradient(cx - 200 * s, cy - 200 * s, cx + 200 * s, cy + 200 * s)
            pat.add_color_stop_rgba(0, 0.80, 0.84, 0.92, alpha)
            pat.add_color_stop_rgba(1, 0.28, 0.32, 0.42, alpha)
            ctx.set_source(pat)
            ctx.fill_preserve()
            ctx.set_source_rgba(*col, alpha)
            ctx.set_line_width(3)
            ctx.stroke()
        else:
            ctx.set_source_rgba(*col, alpha * glow * 0.4)
            ctx.set_line_width(6)
            ctx.stroke()
    # ribs and feed tripod
    for k in range(9):
        a = -0.55 + (k - 4) * 0.33
        cv.line([(cx, cy), (cx + math.cos(a + 1.6) * 230 * s, cy + math.sin(a + 1.6) * 100 * s)], (0.4, 0.45, 0.55),
                width=1.0, alpha=alpha * 0.5)
    fx, fy = cx - 120 * s, cy - 190 * s
    for k in (-1, 0, 1):
        cv.line([(cx + k * 120 * s, cy + k * 40 * s), (fx, fy)], col, width=2.0, alpha=alpha * 0.85)
    cv.circle(fx, fy, 12 * s, col, alpha=alpha, glow=glow)
    return (fx, fy)


def bulb(cv: Canvas, x, y, s, alpha=1.0, glow=1.0, t=0.0):
    """An incandescent fridge bulb, screw base down, glowing filament."""
    if alpha <= 0.003:
        return
    flick = 0.95 + 0.05 * math.sin(t * 2 * math.pi * 3)
    cv.radial(x, y - 40 * s, 260 * s, (1.0, 0.82, 0.55), alpha=0.35 * alpha * glow * flick, glow=glow)
    b = cv.b
    for ctx, gl in ((cv.b, False), (cv.g, True)):
        ctx.save()
        ctx.translate(x, y - 40 * s)
        ctx.new_path()
        ctx.arc(0, -40 * s, 95 * s, math.radians(140), math.radians(40))
        ctx.curve_to(70 * s, 40 * s, 42 * s, 70 * s, 40 * s, 110 * s)
        ctx.line_to(-40 * s, 110 * s)
        ctx.curve_to(-42 * s, 70 * s, -70 * s, 40 * s, -72 * s, 18 * s)
        ctx.close_path()
        ctx.restore()
        if not gl:
            pat = cairo.RadialGradient(x - 20 * s, y - 100 * s, 5 * s, x, y - 70 * s, 110 * s)
            pat.add_color_stop_rgba(0, 1.0, 0.98, 0.90, 0.75 * alpha * glow)
            pat.add_color_stop_rgba(1, 1.0, 0.85, 0.55, 0.20 * alpha * glow)
            ctx.set_source(pat)
            ctx.fill_preserve()
            ctx.set_source_rgba(1.0, 0.95, 0.85, 0.7 * alpha)
            ctx.set_line_width(2.5)
            ctx.stroke()
        else:
            ctx.set_source_rgba(1.0, 0.85, 0.55, 0.5 * alpha * glow * flick)
            ctx.fill()
    # filament
    pts = [(x - 26 * s, y - 70 * s)]
    for k in range(9):
        pts.append((x - 26 * s + (k + 1) * 52 * s / 9, y - 76 * s + (6 if k % 2 else -6) * s))
    cv.line(pts, (1.0, 0.95, 0.70), width=3 * s, alpha=alpha * glow, glow=1.4 * glow * flick)
    cv.line([(x - 26 * s, y - 70 * s), (x - 18 * s, y + 20 * s)], (0.8, 0.8, 0.85), width=1.5, alpha=alpha)
    cv.line([(x + 26 * s, y - 72 * s), (x + 18 * s, y + 20 * s)], (0.8, 0.8, 0.85), width=1.5, alpha=alpha)
    # screw base
    for k in range(5):
        yy = y + 72 * s + k * 14 * s
        cv.rect(x - 40 * s, yy, 80 * s, 10 * s, (0.62, 0.62, 0.66), alpha=alpha, radius=4 * s)
    cv.rect(x - 22 * s, y + 142 * s, 44 * s, 16 * s, (0.25, 0.25, 0.28), alpha=alpha, radius=6 * s)


# =========================================================================== the pale blue dot

def pale_blue_dot(cv: Canvas, x0, y0, w, h, alpha=1.0, dot=(0.62, 0.66), t=0.0, zoom=1.0):
    """Voyager's 1990 view: dark field crossed by bands of scattered sunlight, Earth a speck in one band."""
    if alpha <= 0.003:
        return
    b = cv.b
    b.save()
    b.rectangle(x0, y0, w, h)
    b.clip()
    b.set_source_rgba(0.015, 0.012, 0.012, alpha)
    b.paint()
    rng = np.random.default_rng(2)
    bands = [(0.20, 0.10, (0.55, 0.30, 0.20)), (0.42, 0.05, (0.62, 0.42, 0.30)), (0.62, 0.09, (0.70, 0.52, 0.38)),
             (0.84, 0.06, (0.50, 0.36, 0.30))]
    for (u, wd, col) in bands:
        cxb = x0 + u * w
        pat = cairo.LinearGradient(cxb - wd * w, 0, cxb + wd * w, 0)
        pat.add_color_stop_rgba(0, *col, 0)
        pat.add_color_stop_rgba(0.5, *col, 0.35 * alpha)
        pat.add_color_stop_rgba(1, *col, 0)
        b.save()
        b.translate(cxb, y0 + h / 2)
        b.rotate(-0.10)
        b.translate(-cxb, -(y0 + h / 2))
        b.rectangle(cxb - wd * w, y0 - h * 0.2, 2 * wd * w, h * 1.4)
        b.set_source(pat)
        b.fill()
        b.restore()
    for _ in range(220):
        b.set_source_rgba(0.6, 0.55, 0.5, rng.uniform(0.04, 0.12) * alpha)
        b.rectangle(x0 + rng.uniform(0, w), y0 + rng.uniform(0, h), 1.5, 1.5)
        b.fill()
    dx, dy = x0 + dot[0] * w, y0 + dot[1] * h
    cv.circle(dx, dy, 2.2 * zoom, (0.75, 0.86, 1.0), alpha=alpha, glow=0.9)
    b.restore()
    return dx, dy


# =========================================================================== signals of life

def eeg(cv: Canvas, x0, y0, w, h, t, channels=6, alpha=1.0, color=(1.0, 0.45, 0.65), speed=60.0, seed=5):
    """Scrolling EEG traces (alpha rhythm ~10 Hz plus slower waves)."""
    if alpha <= 0.003:
        return
    rng = np.random.default_rng(seed)
    params = [(rng.uniform(8, 11), rng.uniform(1.5, 4), rng.uniform(0, 6.28), rng.uniform(0.4, 1.0)) for _ in range(channels)]
    for k, (fa, fs, ph, amp) in enumerate(params):
        yc = y0 + (k + 0.5) * h / channels
        pts = []
        for i in range(160):
            u = i / 159
            tt = t * 0.9 + u * w / speed
            v = amp * (0.55 * math.sin(2 * math.pi * fa * tt * 0.12 + ph) + 0.30 * math.sin(2 * math.pi * fs * tt * 0.25 + k)
                       + 0.15 * math.sin(2 * math.pi * 23 * tt * 0.1 + 3 * k))
            pts.append((x0 + u * w, yc + v * h / channels * 0.38))
        cv.line(pts, color, width=2.0, alpha=alpha * (0.55 + 0.45 * amp), glow=0.6)


def ekg(cv: Canvas, x0, x1, y, t, alpha=1.0, color=(1.0, 0.35, 0.40), bpm=62.0, amp=70.0, period_px=330.0):
    if alpha <= 0.003:
        return
    pts = []
    n = 220
    shift = (t * bpm / 60.0 * period_px) % period_px
    for i in range(n):
        x = x0 + (x1 - x0) * i / (n - 1)
        ph = ((x - x0 + shift) % period_px) / period_px
        v = 0.0
        v += 0.12 * math.exp(-((ph - 0.18) / 0.03) ** 2)
        v -= 0.15 * math.exp(-((ph - 0.30) / 0.008) ** 2)
        v += 1.00 * math.exp(-((ph - 0.32) / 0.010) ** 2)
        v -= 0.25 * math.exp(-((ph - 0.345) / 0.010) ** 2)
        v += 0.22 * math.exp(-((ph - 0.52) / 0.045) ** 2)
        pts.append((x, y - v * amp))
    cv.line(pts, color, width=3, alpha=alpha, glow=0.8)
