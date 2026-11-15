"""Shared procedural material building blocks for the armor painters.

Every shader receives an armorlib Ctx (per-face texel arrays) and returns (rgb[N,3], alpha, glow[N]).
Values `v` are in [0,1] and get quantised through hue-shifted palettes, optionally with a 2x2
ordered dither for smooth HD gradients.
"""
import math

import numpy as np

from armorlib import fbm, hash3, hexcol, palette, vnoise, worley

FACE_ID = {"north": 0, "south": 1, "west": 2, "east": 3, "up": 4, "down": 5}
BAYER2 = np.array([[0.0, 0.5], [0.75, 0.25]])
BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0


def pal(*hexes):
    return palette(*hexes)


def lerp_pal(a, b, f):
    return a * (1 - f) + b * f


def tint_pal(p, rgb, f):
    return p * (1 - f) + np.asarray(rgb, dtype=float) * f


def ramp(p, v, ctx=None, dither=0.0):
    n = len(p)
    v = np.asarray(v, dtype=float)
    if ctx is not None and dither:
        v = v + (BAYER2[ctx.j % 2, ctx.i % 2] - 0.375) * dither / n
    idx = np.clip(np.floor(v * n), 0, n - 1).astype(int)
    return p[idx].astype(float)


# ----------------------------------------------------------------------------- face geometry

def side_face(ctx):
    return ctx.face not in ("up", "down")


def edist(ctx):
    """dl, dr, dt, db: texel distance to the left/right/top/bottom border of the face."""
    return ctx.i, ctx.tw - 1 - ctx.i, ctx.j, ctx.th - 1 - ctx.j


def emin(ctx):
    dl, dr, dt, db = edist(ctx)
    return np.minimum(np.minimum(dl, dr), np.minimum(dt, db))


def texel_hash(ctx, seed=0):
    p = ctx.p
    return hash3(np.floor(p[:, 0] * 2 + 0.013), np.floor(p[:, 1] * 2 + 0.013), np.floor(p[:, 2] * 2 + 0.013), seed)


def bevel(ctx, hi=0.22, lo=0.20, side=0.05, inner=0.45, rim=True):
    """Pixel bevel: lit top edge, shaded bottom edge, mild sides, second ring weaker."""
    dl, dr, dt, db = edist(ctx)
    e = np.zeros(ctx.N)
    if side_face(ctx):
        e += np.where(dt == 0, hi, 0) + np.where(dt == 1, hi * inner * 0.6, 0)
        e -= np.where(db == 0, lo, 0) + np.where(db == 1, lo * inner * 0.5, 0)
        e += np.where((dl == 0) & (dt > 0), side, 0)
        e -= np.where((dr == 0) & (dt > 0), side * 1.4, 0)
    elif ctx.face == "up":
        m = np.minimum(np.minimum(dl, dr), np.minimum(dt, db))
        e += np.where(m == 0, hi * 0.8, 0) + np.where(m == 1, hi * 0.25, 0)
    else:
        m = np.minimum(np.minimum(dl, dr), np.minimum(dt, db))
        e -= np.where(m == 0, lo * 0.5, 0)
    return e


def face_tone(ctx, up=0.10, down=-0.22):
    n = ctx.nw
    return up * max(0.0, n[1]) + down * max(0.0, -n[1])


def vgrad(ctx, amount=0.14):
    if not side_face(ctx):
        return np.zeros(ctx.N)
    return (0.5 - ctx.t) * amount


def sheen(ctx, amt=0.13, period=None, phase=0.33):
    """Diagonal polished-metal glint band across side faces (texel space)."""
    if not side_face(ctx) or ctx.tw < 4 or ctx.th < 4:
        return np.zeros(ctx.N)
    d = ctx.i + ctx.j * 0.7
    c = (ctx.tw + ctx.th * 0.7) * phase + hash3(ctx.index, 3, 1, 9)[0] * 3
    band = np.abs(d - c)
    return np.where(band < 1.0, amt, 0) + np.where((band >= 2.0) & (band < 2.8), amt * 0.5, 0)


def rivets(ctx, inset=2, min_size=10, every=None):
    """Mask of rivet heads (2x2 texels) near the corners of big side faces + their highlight."""
    hi = np.zeros(ctx.N, dtype=bool)
    lo = np.zeros(ctx.N, dtype=bool)
    if not side_face(ctx) or ctx.tw < min_size or ctx.th < min_size:
        return hi, lo
    xs = [inset, ctx.tw - inset - 2]
    ys = [inset, ctx.th - inset - 2]
    for x0 in xs:
        for y0 in ys:
            hi |= (ctx.i == x0) & (ctx.j == y0)
            lo |= ((ctx.i == x0 + 1) & (ctx.j == y0 + 1)) | ((ctx.i == x0 + 1) & (ctx.j == y0)) | (
                (ctx.i == x0) & (ctx.j == y0 + 1))
    return hi, lo


def gx(ctx):
    """World-ish coordinates of the texel centre: x, y, z (cube-local before cube rotation)."""
    return ctx.p[:, 0], ctx.p[:, 1], ctx.p[:, 2]


# ----------------------------------------------------------------------------- generic materials

def brushed(ctx, amt=0.05, axis=1):
    """Anisotropic streak noise (brushed metal) along `axis`."""
    k = np.array([2.2, 2.2, 2.2])
    k[axis] = 0.18
    return (fbm(ctx.p * k, 1.0, 2, seed=55) - 0.5) * 2 * amt


def metal(ctx, p, base=0.52, noise=0.025, nfreq=0.45, hi=0.26, lo=0.24, sheen_amt=0.12, ao=0.6, dither=0.7,
          grad=0.18, extra=None, brush=0.05):
    v = base + face_tone(ctx) + vgrad(ctx, grad) + bevel(ctx, hi, lo)
    v += (fbm(ctx.p, nfreq, 2, seed=5) - 0.5) * noise * 2
    v += (texel_hash(ctx, 7) - 0.5) * noise * 0.5
    v += brushed(ctx, brush)
    v += sheen(ctx, sheen_amt)
    v -= ctx.ao * ao
    if extra is not None:
        v = v + extra
    return v, ramp(p, v, ctx, dither)


def gem(ctx, p, shape="diamond", glow=True, sparkle=(255, 255, 255), base=0.95, falloff=0.62):
    """Faceted gem: bright core, darker rim, top-left sparkle."""
    dx = (ctx.s - 0.5) * 2
    dy = (ctx.t - 0.5) * 2
    if shape == "diamond":
        r = (np.abs(dx) + np.abs(dy)) * 0.75
    elif shape == "round":
        r = np.sqrt(dx * dx + dy * dy) * 0.85
    else:
        r = np.maximum(np.abs(dx), np.abs(dy))
    v = base - r * falloff
    v += np.where((dx < -0.05) & (dy < -0.05) & (r > 0.25) & (r < 0.75), 0.18, 0)
    v -= np.where((dx > 0.1) & (dy > 0.1) & (r > 0.4), 0.12, 0)
    if ctx.face == "down":
        v -= 0.15
    rgb = ramp(p, v, ctx, 0.3)
    if ctx.tw >= 3 and ctx.th >= 3:
        sp = (ctx.i == 1) & (ctx.j == 1)
        rgb[sp] = sparkle
    g = np.ones(ctx.N, dtype=bool) if glow else np.zeros(ctx.N, dtype=bool)
    return rgb, 255, g


def crystal(ctx, p, glow=True, facet=True):
    """Elongated crystal (spike segments or upright boxes): brighter toward the tip, faceted faces."""
    prm = ctx.params
    if "spike_base" in prm:
        base = np.array(prm["spike_base"])
        prog = np.clip((ctx.p[:, 1] - base[1]) / max(prm["spike_len"], 1e-6), 0, 1)
    else:
        prog = np.clip((ctx.p[:, 1] - ctx.lo[1]) / max(ctx.hi[1] - ctx.lo[1], 1e-6), 0, 1)
    v = 0.30 + prog * 0.45
    fo = {"north": 0.06, "east": 0.16, "west": -0.10, "south": -0.04, "up": 0.30, "down": -0.18}
    v += fo[ctx.face] if facet else 0
    dl, dr, dt, db = edist(ctx)
    if side_face(ctx):
        v += np.where(dl == 0, 0.22, 0) + np.where(dl == 1, 0.08, 0)
        v -= np.where(dr == 0, 0.14, 0)
        stripe = (ctx.i == max(1, ctx.tw // 2)) & (ctx.tw >= 3)
        v += np.where(stripe, 0.12, 0)
    v += (fbm(ctx.p, 0.6, 2, 31) - 0.5) * 0.18
    v -= ctx.ao * 0.3
    rgb = ramp(p, v, ctx, 0.5)
    tip = (prog > 0.9) & (texel_hash(ctx, 3) > 0.5)
    rgb[tip] = p[-1]
    g = np.ones(ctx.N, dtype=bool) if glow else np.zeros(ctx.N, dtype=bool)
    return rgb, 255, g


def stone(ctx, p, base=0.56, cells=0.2, ao=0.6, dither=0.35, seed=3, grain=0.03, cracks=0.55):
    """Carved stone: broad tonal slabs, a few crisp cracks with lit lips, chipped edges, low noise."""
    f1, f2, cid = worley(ctx.p, cells, seed=seed)
    v = base + (cid - 0.5) * 0.12 + (fbm(ctx.p, 0.3, 2, seed + 1) - 0.5) * 0.10
    c1, c2, _ = worley(ctx.p, 0.34, seed=seed + 9)
    gate = fbm(ctx.p, 0.25, 2, seed + 4) > cracks
    crack = ((c2 - c1) < 0.05) & gate
    lip = ((c2 - c1) >= 0.05) & ((c2 - c1) < 0.11) & gate
    v -= np.where(crack, 0.3, 0)
    v += np.where(lip, 0.06, 0)
    v += (texel_hash(ctx, seed + 5) - 0.5) * grain
    dl, dr, dt, db = edist(ctx)
    chip = (np.minimum(np.minimum(dl, dr), np.minimum(dt, db)) <= 1) & (texel_hash(ctx, seed + 8) > 0.8)
    v -= np.where(chip, 0.18, 0)
    v += bevel(ctx, 0.30, 0.26, 0.07) + face_tone(ctx, 0.14, -0.25) + vgrad(ctx, 0.14)
    v -= ctx.ao * ao
    return v, ramp(p, v, ctx, dither)


def panel(ctx, inset=2, min_size=10, depth=0.16):
    """Recessed-panel groove for large side faces: dark line at `inset`, lit line just inside it."""
    out = np.zeros(ctx.N)
    if not side_face(ctx) or ctx.tw < min_size or ctx.th < min_size:
        return out
    dl, dr, dt, db = edist(ctx)
    m = np.minimum(np.minimum(dl, dr), np.minimum(dt, db))
    groove = m == inset
    out -= np.where(groove & ((dt == inset) | (dl == inset)), depth, 0)
    out += np.where(groove & ((db == inset) | (dr == inset)), depth * 0.5, 0)
    inner = m == inset + 1
    out += np.where(inner & ((dt == inset + 1) | (dl == inset + 1)), depth * 0.6, 0)
    return out


def trim_band(ctx, width=2, edges=("top", "bottom", "left", "right"), faces=None):
    """Mask of a border band of `width` texels along the selected edges (side faces + up rim)."""
    if faces is not None and ctx.face not in faces:
        return np.zeros(ctx.N, dtype=bool)
    dl, dr, dt, db = edist(ctx)
    m = np.zeros(ctx.N, dtype=bool)
    if "top" in edges:
        m |= dt < width
    if "bottom" in edges:
        m |= db < width
    if "left" in edges:
        m |= dl < width
    if "right" in edges:
        m |= dr < width
    return m


def gold(ctx, p, mask=None, base=0.62, engrave=True, dither=0.4):
    """Polished gold trim colour: strong bevel + engraved dots."""
    dl, dr, dt, db = edist(ctx)
    v = base + face_tone(ctx, 0.10, -0.25) + vgrad(ctx, 0.18) + bevel(ctx, 0.22, 0.26, 0.06)
    v += (fbm(ctx.p, 0.9, 2, 77) - 0.5) * 0.10
    v += sheen(ctx, 0.2, phase=0.4)
    v -= ctx.ao * 0.5
    if engrave and side_face(ctx):
        dots = ((ctx.i + ctx.j) % 4 == 0) & (dt > 1) & (db > 1) & (dl > 1) & (dr > 1)
        v -= np.where(dots, 0.12, 0)
    return v, ramp(p, v, ctx, dither)


def glow_line(mask, rgb, glowarr, color):
    rgb[mask] = color
    glowarr |= mask


def spot(x, y, cx, cy, r):
    return (x - cx) ** 2 + (y - cy) ** 2 < r * r


def plane_alpha(ctx, keep_face):
    """For zero-thickness planes: only one face is painted, the twin face is transparent."""
    return 255 if ctx.face == keep_face else 0
