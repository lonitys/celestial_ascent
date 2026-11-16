"""Materials for the Sun Herald: engraved sun-gold, ivory and saffron robes with embroidered hems,
the blazing sun-disc halo layers, the sun mask, the eclipse moon and the sun staff.

Every shader returns (rgb, alpha, glow). Glow is kept for the focal points: the sun disc and its
flame corona, the mask eyes, the gem/orb cores and a few hot ray tips."""
import math

import numpy as np

from bosslib import fbm, hash3, palette, vnoise
from bossfx import bevel, border_coords, dither, dramp, edge_dist, plane_xy, smoothstep, sramp, spec

TAU = 2 * math.pi

GOLD = palette("#1e0b02", "#3a1b04", "#5e3007", "#86470d", "#ad6316", "#cc801f", "#e49f2e", "#f3be48",
               "#fbdb80", "#fff3cc")
IVORY = palette("#3a2a22", "#5a4334", "#7d604b", "#a08064", "#bfa082", "#d8bea0", "#ead6bc", "#f6ead7",
                "#fdf7ec")
SAFFRON = palette("#3a0a06", "#5f1208", "#871f0b", "#ad320f", "#cf4c14", "#e86c1b", "#f59128", "#fbb540",
                  "#fdd673", "#fff0b0")
CRIMSON = palette("#160406", "#26070b", "#3b0b12", "#530f19", "#6e1520", "#8a2129", "#a63532", "#c0503f")
SUN = palette("#6a1c00", "#a83a00", "#e06200", "#ff8c0a", "#ffb120", "#ffd040", "#ffe877", "#fff6b8",
              "#fffdf0")
MOON = palette("#030206", "#07050c", "#0d0a15", "#151020", "#1e182d", "#2a223d")
BRONZE = palette("#140b05", "#24150a", "#382110", "#4f3018", "#684222", "#83582f")


def tone(ctx, ao=0.55):
    n = ctx.nw
    return 0.06 * max(0.0, n[1]) - 0.12 * max(0.0, -n[1]) - ctx.ao * ao


def side_face(ctx):
    return ctx.plane or ctx.face not in ("up", "down")


def face_units(ctx):
    """Face coordinates in model units, origin at the face centre, x right, y up."""
    return (ctx.s - 0.5) * ctx.tw / 2.0, (0.5 - ctx.t) * ctx.th / 2.0


# =============================================================================== gold

def gold_value(ctx, polish=1.0):
    p = ctx.p
    v = 0.5 + (fbm(p, 0.4, 2, 31) - 0.5) * 0.10
    if side_face(ctx):
        t = ctx.t
        v = v + polish * (0.24 * np.exp(-((t - 0.2) / 0.17) ** 2) - 0.13 * np.exp(-((t - 0.6) / 0.14) ** 2)
                          + 0.05 * (t > 0.84))
    else:
        v = v + (0.12 if ctx.face == "up" else -0.12)
    v = v + bevel(ctx, 2.2, 0.26, 0.22) + tone(ctx) + 0.18 * spec(ctx, 8)
    return v


def sunburst_mask(x, y, n=16, r0=1.2, width=0.16, ring=True):
    """Engraved sunburst lines in face units around (0, 0): n radial grooves outside r0 plus a ring."""
    r = np.sqrt(x * x + y * y) + 1e-6
    a = np.arctan2(y, x)
    q = np.abs(np.mod(a * n / TAU, 1.0) - 0.5)          # 0.5 at a groove
    dperp = (0.5 - q) * TAU / n * r                    # arc distance to the nearest groove
    m = (dperp < width) & (r > r0)
    if ring:
        m |= np.abs(r - r0) < width
    return m


def gold(ctx, engrave=None, hot=False, polish=1.0):
    """Polished sun-gold. engrave: None | 'sunburst' (radial grooves around the face centre)
    | 'bands' (horizontal engraved lines)."""
    v = gold_value(ctx, polish)
    glow = np.zeros(ctx.N, dtype=bool)
    if engrave == "sunburst" and side_face(ctx) and min(ctx.tw, ctx.th) >= 8:
        # raised sunburst: bold tapered rays (alternating long/short) out of a central boss
        x, y = face_units(ctx)
        y = y - ctx.params.get("burst_y", 0.0)
        r = np.sqrt(x * x + y * y) + 1e-6
        a = np.arctan2(y, x)
        n = ctx.params.get("burst_n", 8)
        u = a * n / TAU
        k = np.floor(u + 0.5)
        fq = u - k
        dperp = np.abs(fq) * TAU / n * r
        long = np.mod(k, 2) == 0
        r0 = ctx.params.get("burst_r", 1.6)
        r1 = np.where(long, ctx.params.get("burst_long", 4.4), ctx.params.get("burst_short", 3.0))
        prog = np.clip((r - r0) / (r1 - r0), 0, 1)
        w = 0.55 * (1 - prog) + 0.12
        ray = (r > r0) & (r < r1) & (dperp < w)
        outline = (r > r0 - 0.3) & (r < r1 + 0.35) & (dperp < w + 0.4) & ~ray
        v = v - outline * 0.2 + ray * (0.16 + 0.1 * (fq < 0))
        v = v - 0.2 * (np.abs(r - r0) < 0.25)
    elif engrave == "bands" and side_face(ctx):
        y = (1 - ctx.t) * ctx.th
        m = np.mod(y, 6) < 1
        v = v - m * 0.22 + (np.mod(y - 1, 6) < 1) * 0.1
    rgb = sramp(GOLD, v + dither(ctx, 0.05))
    if hot:
        # molten-hot lower lip on the leading edge
        pass
    return rgb, glow


def gold_rim(ctx):
    """Gold plate with a single thin raised rim line inset from the border (restrained trim).
    params boss=True puts a raised sun medallion on the up face (pauldrons)."""
    v = gold_value(ctx)
    d = edge_dist(ctx)
    if min(ctx.tw, ctx.th) >= 8:
        v = v + np.where(d == 2, 0.16, 0) - np.where(d == 3, 0.14, 0)
    if ctx.params.get("boss") and ctx.face == "up":
        x, y = face_units(ctx)
        r = np.sqrt(x * x + y * y) + 1e-6
        a = np.arctan2(y, x)
        disc = r < 1.7
        ring = (r >= 1.7) & (r < 2.15)
        q = np.abs(np.mod(a * 8 / TAU, 1.0) - 0.5)
        rays = (r >= 2.15) & (r < 3.6) & ((0.5 - q) * TAU / 8 * r < 0.42 * (1 - (r - 2.15) / 1.45) + 0.1)
        v = v + disc * (0.2 - 0.1 * (x > 0) + 0.08 * (y > 0)) - ring * 0.22 + rays * 0.14
        v = v - 0.12 * ((r > 3.6) & (r < 3.95))
    return sramp(GOLD, v + dither(ctx, 0.05)), np.zeros(ctx.N, dtype=bool)


def gauntlet(ctx):
    """Gold gauntlet: knuckle ridge across the upper third, finger grooves below."""
    v = gold_value(ctx, 0.5)
    if side_face(ctx):
        knuck = np.abs(ctx.t - 0.32) < 0.08
        v = v + knuck * 0.16 - (np.abs(ctx.t - 0.42) < 0.05) * 0.18
        if ctx.face in ("north", "south", "west", "east"):
            groove = (ctx.t > 0.45) & (np.mod(ctx.i, 2 if ctx.tw <= 8 else 3) == 0) & (ctx.i > 0) & (ctx.i < ctx.tw - 1)
            v = v - groove * 0.2
    return sramp(GOLD, v + dither(ctx, 0.05)), np.zeros(ctx.N, dtype=bool)


def gold_ray(ctx):
    """Flame fins / ray spikes: polished gold brightening to pale gold towards the tip."""
    prog = ctx.params.get("curve_prog0", 0.0)
    prog1 = ctx.params.get("curve_prog1", 1.0)
    pt = prog + (prog1 - prog) * (1 - ctx.t) if side_face(ctx) else prog1
    v = gold_value(ctx, 0.5) + (0.5 - np.abs(ctx.s - 0.5)) * 0.2 + 0.25 * pt
    return sramp(GOLD, v + dither(ctx, 0.05)), np.zeros(ctx.N, dtype=bool)


# =============================================================================== cloth

def folds(ctx, period=3.0, seed=0):
    """Hanging cloth folds across a plane (s) with a slow wave down it (t). Returns -1..1."""
    u = ctx.s * ctx.tw / 2.0
    w = ctx.t * ctx.th / 2.0
    ph = TAU * u / period + 0.9 * np.sin(w * 0.23 + seed) + 0.5 * np.sin(u * 0.37 + seed * 2.1)
    return np.sin(ph)


def hem_line(ctx, tongue_w=3.4, depth=2.4, shape="flame"):
    """t-limit of the cut hem (alpha = t < limit). Flame tongues with slightly curled tips."""
    W = ctx.tw / 2.0
    H = ctx.th / 2.0
    n = max(1, int(round(W / tongue_w)))
    u = ctx.s * n
    k = np.floor(u)
    f = u - k - 0.5                                         # -0.5..0.5 across a tongue
    lean = (hash3(k, k * 0 + 3, k * 0 + ctx.index, 7) - 0.5) * 0.25
    f = f - lean * (1 - 2 * np.abs(f))
    if shape == "flame":
        prof = np.clip(1 - np.abs(f) * 2, 0, 1) ** 1.6      # 1 at the tongue tip, 0 at the notch
    elif shape == "point":
        prof = np.clip(1 - np.abs(ctx.s - 0.5) * 2, 0, 1)
        return 1 - (depth / H) * (1 - prof)
    else:
        prof = np.sqrt(np.clip(1 - (f * 2) ** 2, 0, 1))      # scallops
    return 1 - (depth / H) * (1 - prof)


def trapezoid(ctx, taper):
    """Alpha mask narrowing the top of a hanging plane: top width = 1 - taper (fraction)."""
    x = (ctx.s - 0.5) * 2
    lim = 1 - taper * (1 - ctx.t) ** 1.3
    return np.abs(x) <= lim


def embroidery_band(ctx, d, d0=0.45, d1=1.85):
    """Gold-thread band following the hem at distance d (model units above the cut)."""
    band = (d > d0) & (d < d1)
    edge = band & ((d < d0 + 0.3) | (d > d1 - 0.3))
    u = ctx.s * ctx.tw / 2.0
    mid = (d0 + d1) / 2
    zig = np.abs((d - mid) - 0.45 * np.sin(u * TAU / 2.2)) < 0.22
    return band, edge, zig & band & ~edge


def robe(ctx):
    """Under-robe panel: saffron dye graded to deep orange-red at the hem by world height, soft
    folds, embroidered flame hem with ember dots. params: taper, tongue, depth, top_y."""
    prm = ctx.params
    fo = folds(ctx, prm.get("fold", 2.8), ctx.index * 1.7)
    y = ctx.pw[:, 1]
    g = np.clip((prm.get("top_y", 29.0) - y) / 26.0, 0, 1)
    v = 0.80 - 0.40 * g ** 1.1 + 0.075 * fo - 0.07 * (fo < -0.75) + tone(ctx, 0.45)
    v = v + (fbm(ctx.p, 0.6, 2, 5) - 0.5) * 0.06
    hl = hem_line(ctx, prm.get("tongue", 3.4), prm.get("depth", 2.4))
    alpha = (ctx.t < hl) & trapezoid(ctx, prm.get("taper", 0.0))
    d = (hl - ctx.t) * ctx.th / 2.0
    rgb = dramp(SAFFRON, v, ctx, 0.6)
    band, edge, zig = embroidery_band(ctx, d)
    gv = 0.62 + 0.08 * fo + tone(ctx, 0.3) + (edge * 0.12)
    rgb[band] = sramp(GOLD, gv[band] - 0.12 + 0.18 * zig[band])
    lip = d <= 0.45
    rgb[lip] = sramp(SAFFRON, v[lip] - 0.18)
    glow = np.zeros(ctx.N, dtype=bool)
    # tiny ember dots in the band
    u = ctx.s * ctx.tw / 2.0
    dots = band & ~edge & (np.abs(np.mod(u, 3.4) - 1.7) < 0.32) & (np.abs(d - 1.15) < 0.32)
    rgb[dots] = SUN[6]
    glow |= dots
    return rgb, np.where(alpha, 255, 0), glow


def emblem_sun(x, y, r_core=1.2, r_ring=1.8, n=12, r_ray=3.4, w=0.28):
    """Small embroidered sun emblem in units around (0, 0). Returns (core, ring, rays)."""
    r = np.sqrt(x * x + y * y) + 1e-6
    a = np.arctan2(y, x)
    core = r < r_core
    ring = np.abs(r - r_ring) < w
    q = np.abs(np.mod(a * n / TAU, 1.0) - 0.5)
    dperp = (0.5 - q) * TAU / n * r
    long = np.mod(np.floor(a * n / TAU + 0.5), 2) == 0
    lim = np.where(long, r_ray, r_ray * 0.72)
    taper = w * 1.5 * np.clip(1 - (r - r_ring) / (lim - r_ring + 1e-6), 0, 1)
    rays = (r > r_ring + w) & (r < lim) & (dperp < taper + 0.1)
    return core, ring, rays


def tabard(ctx):
    """Ivory over-tabard: warm folds, gold-thread border, embroidered sun, pointed hem."""
    prm = ctx.params
    fo = folds(ctx, 2.4, 3.0)
    y = ctx.pw[:, 1]
    g = np.clip((29.0 - y) / 24.0, 0, 1)
    v = 0.86 - 0.16 * g + 0.06 * fo - 0.06 * (fo < -0.75) + tone(ctx, 0.5)
    rgb = dramp(IVORY, v, ctx, 0.5)
    W, H = ctx.tw / 2.0, ctx.th / 2.0
    hl = hem_line(ctx, prm.get("tongue", W), prm.get("depth", 3.2), prm.get("hem", "point"))
    alpha = (ctx.t < hl) & trapezoid(ctx, prm.get("taper", 0.0))
    d = (hl - ctx.t) * H
    x = (ctx.s - 0.5) * W
    side = W / 2 - np.abs(x)                                  # distance to the side edges
    border = ((side < 1.0) & (side > 0.35)) | ((d < 1.3) & (d > 0.45))
    rgb[border] = sramp(GOLD, (0.66 + 0.06 * fo + tone(ctx, 0.3) - 0.04)[border])
    edge = (side <= 0.35) | (d <= 0.45)
    rgb[edge] = sramp(SAFFRON, 0.62 + 0.05 * fo[edge])
    glow = np.zeros(ctx.N, dtype=bool)
    if prm.get("emblem"):
        ey = prm.get("emblem_t", 0.3)
        yy = (ey - ctx.t) * H
        core, ring, rays = emblem_sun(x, yy, r_core=1.0, r_ring=1.6, n=12, r_ray=min(3.3, W / 2 - 1.1), w=0.25)
        rgb[ring | rays] = sramp(GOLD, 0.7 + 0.05 * fo[ring | rays] - 0.05)
        rgb[core] = SUN[5]
        glow |= core
    return rgb, np.where(alpha, 255, 0), glow


def fauld(ctx):
    """Short ivory side fauld with gold scalloped hem."""
    prm = dict(ctx.params)
    fo = folds(ctx, 2.2, 5.0)
    v = 0.82 + 0.06 * fo + tone(ctx, 0.5) - 0.06 * ctx.t
    rgb = dramp(IVORY, v, ctx, 0.5)
    H = ctx.th / 2.0
    hl = hem_line(ctx, 2.6, 1.3, "scallop")
    alpha = (ctx.t < hl) & trapezoid(ctx, prm.get("taper", 0.0))
    d = (hl - ctx.t) * H
    band = d < 1.4
    rgb[band] = sramp(GOLD, (0.64 + 0.06 * fo + tone(ctx, 0.3))[band])
    rgb[(d < 1.0) & (d > 0.65)] = GOLD[3]
    return rgb, np.where(alpha, 255, 0), np.zeros(ctx.N, dtype=bool)


def mantle(ctx):
    """Long back mantle: ivory at the shoulders melting into saffron and ember-red at the hem, with a
    gold border, a large embroidered sun on the upper back and a flame-cut hem."""
    prm = ctx.params
    fo = folds(ctx, 3.2, 9.0 + ctx.index)
    y = ctx.pw[:, 1]
    g = np.clip((40.0 - y) / 38.0, 0, 1)
    W, H = ctx.tw / 2.0, ctx.th / 2.0
    x = (ctx.s - 0.5) * W
    side = W / 2 - np.abs(x)
    v_iv = 0.84 + 0.06 * fo - 0.06 * (fo < -0.75) + tone(ctx, 0.5)
    v_sa = 0.86 - 0.42 * np.clip((g - 0.35) / 0.65, 0, 1) + 0.07 * fo - 0.06 * (fo < -0.75) + tone(ctx, 0.45)
    a = IVORY[np.clip(((v_iv + dither(ctx, 0.06)) * len(IVORY)).astype(int), 0, len(IVORY) - 1)]
    b = SAFFRON[np.clip(((v_sa + dither(ctx, 0.06)) * len(SAFFRON)).astype(int), 0, len(SAFFRON) - 1)]
    mixf = smoothstep(0.25, 0.6, g + (fbm(ctx.pw, 0.25, 2, 77) - 0.5) * 0.12 + dither(ctx, 0.08))
    rgb = a * (1 - mixf[:, None]) + b * mixf[:, None]
    hl = hem_line(ctx, 3.6, 2.8) if prm.get("hem") else np.ones(ctx.N) * 2
    alpha = (ctx.t < hl) & trapezoid(ctx, prm.get("taper", 0.0))
    d = (hl - ctx.t) * H
    border = (side < 1.25) & (side > 0.45)
    rgb[border] = sramp(GOLD, (0.64 + 0.06 * fo + tone(ctx, 0.3))[border])
    glow = np.zeros(ctx.N, dtype=bool)
    if prm.get("hem"):
        band, edge, zig = embroidery_band(ctx, d)
        rgb[band] = sramp(GOLD, 0.56 + 0.06 * fo[band] + 0.16 * zig[band] + 0.1 * edge[band])
        lip = d <= 0.45
        rgb[lip] = sramp(SAFFRON, v_sa[lip] - 0.2)
    if prm.get("emblem"):
        ey = prm["emblem"]                                    # world y of the emblem centre
        yy = y - ey
        core, ring, rays = emblem_sun(x, yy, r_core=2.0, r_ring=2.9, n=16, r_ray=6.6, w=0.32)
        m = ring | rays
        rgb[m] = sramp(GOLD, 0.66 + 0.06 * fo[m] - 0.02)
        rgb[core] = sramp(SUN, 0.62 + 0.25 * (1 - np.sqrt(x[core] ** 2 + yy[core] ** 2) / 2.0))
        glow |= core
    return rgb, np.where(alpha, 255, 0), glow


def cloth_dark(ctx):
    """Deep crimson under-cloth (hips, upper sleeves, thighs)."""
    p = ctx.p
    v = 0.5 + (fbm(p, 0.5, 3, 15) - 0.5) * 0.18
    if side_face(ctx):
        u = (ctx.s * ctx.tw)
        v = v + 0.06 * np.sin(u * TAU / 6 + np.sin(ctx.t * 4) * 0.8)
    v = v + bevel(ctx, 2.0, 0.08, 0.1) + tone(ctx, 0.5)
    return dramp(CRIMSON, v, ctx, 0.6), np.zeros(ctx.N, dtype=bool)


def sash(ctx):
    """Crimson waist sash with two thin gold-thread stripes and diagonal wrap folds."""
    v = 0.52 + (fbm(ctx.p, 0.5, 2, 17) - 0.5) * 0.14 + tone(ctx, 0.5)
    glow = np.zeros(ctx.N, dtype=bool)
    if side_face(ctx):
        diag = np.sin((ctx.i * 0.5 + ctx.j) * TAU / 7.0)
        v = v + 0.08 * diag
        rgb = dramp(CRIMSON, v, ctx, 0.6)
        stripe = (np.abs(ctx.t - 0.22) < 0.06) | (np.abs(ctx.t - 0.78) < 0.06)
        rgb[stripe] = sramp(GOLD, (0.6 + 0.05 * diag + tone(ctx, 0.3))[stripe])
        return rgb, glow
    return dramp(CRIMSON, v, ctx, 0.6), glow


def sleeve(ctx):
    """Ivory bell sleeve: deep folds darkening towards the cuff, a thin gold piping at the top."""
    if ctx.face in ("down", "up"):
        x, y = plane_xy(ctx)
        r = np.maximum(np.abs(x), np.abs(y))
        return dramp(CRIMSON, 0.2 + 0.25 * r, ctx, 0.5), np.zeros(ctx.N, dtype=bool)
    fo = np.sin(ctx.s * TAU * 2.2 + np.sin(ctx.t * 3 + ctx.index) * 0.9)
    v = 0.76 + 0.11 * fo - 0.07 * (fo < -0.7) - 0.12 * ctx.t + tone(ctx, 0.5) + bevel(ctx, 1.5, 0.05, 0.08)
    rgb = dramp(IVORY, v, ctx, 0.5)
    pip = ctx.t < 0.1
    rgb[pip] = sramp(GOLD, (0.62 + tone(ctx, 0.3))[pip])
    return rgb, np.zeros(ctx.N, dtype=bool)


def hood(ctx):
    """Ivory hood: deep soft folds, darker towards the back and bottom, a gold hem framing the face
    opening (north face) and a gold seam over the crown."""
    p = ctx.p
    if side_face(ctx):
        fo = np.sin(ctx.s * TAU * 1.7 + np.sin(ctx.t * 2.5 + ctx.index) * 0.9 + 0.3 * np.sin(ctx.t * 7))
    else:
        fo = np.sin(ctx.s * TAU * 1.2 + np.sin((1 - ctx.t) * 3.0) * 0.8)
    v = 0.7 + 0.12 * fo - 0.08 * (fo < -0.7) + tone(ctx, 0.5) + bevel(ctx, 2.0, 0.06, 0.1)
    v = v + (fbm(p, 0.7, 2, 3) - 0.5) * 0.05
    if side_face(ctx):
        v = v - 0.12 * ctx.t
    if ctx.face in ("east", "west"):
        v = v - 0.1 * (ctx.s if ctx.face == "west" else 1 - ctx.s) * 0 - 0.08 * (p[:, 2] - ctx.lo[2]) / max(1e-6, ctx.hi[2] - ctx.lo[2])
    rgb = dramp(IVORY, v, ctx, 0.5)
    glow = np.zeros(ctx.N, dtype=bool)
    if ctx.face == "north":
        x, y = face_units(ctx)
        e = (x / 3.9) ** 2 + ((y + 1.3) / 5.0) ** 2
        rgb[e < 1.0] = sramp(CRIMSON, 0.1 + 0.1 * np.clip(1 - e[e < 1.0], 0, 1))
        rim = (e >= 1.0) & (e < 1.5)
        rgb[rim] = sramp(GOLD, (0.64 - 0.2 * (e - 1.0) + tone(ctx, 0.3))[rim])
        d = edge_dist(ctx)
        hem = (d <= 1) & (ctx.j > 1)
        rgb[hem] = sramp(GOLD, (0.6 + 0.08 * (d == 0) + tone(ctx, 0.3))[hem])
    if ctx.face in ("east", "west"):
        front = ctx.s > 0.86 if ctx.face == "west" else ctx.s < 0.14
        rgb[front] = sramp(GOLD, (0.58 + tone(ctx, 0.3))[front])
    if ctx.face == "up":
        seam = np.abs(ctx.s - 0.5) < 0.07
        rgb[seam] = sramp(GOLD, (0.66 + tone(ctx, 0.3))[seam])
    return rgb, glow


def mask(ctx):
    """The sun mask (north face): an egg-shaped polished gold face, stern brow over deep sockets,
    narrow glowing eye slits with thin light-tears running down the cheeks, a long nose and closed
    lips. Corners outside the egg are the dark hood interior. Other faces: plain gold."""
    if ctx.face != "north":
        rgb, glow = gold(ctx, polish=0.6)
        return rgb, 255, glow
    x, y = plane_xy(ctx)
    X = x * 4.0
    Y = y * 5.0
    ry = np.where(Y > 0.6, 4.45, 5.5)
    e = (X / 3.95) ** 2 + ((Y - 0.6) / ry) ** 2
    egg = e < 1.0
    ax = np.abs(X)
    v = 0.56 - 0.2 * (X / 4.0) ** 2 + 0.07 * (-X / 4.0) + 0.04 * (Y / 5.0)
    v = v + 0.09 * (e > 0.8) * (e < 1.0)                                      # raised mask rim
    v = v + 0.13 * ((Y > 1.35) & (Y < 2.1) & (ax < 3.2))                       # brow
    socket = (Y > -0.15) & (Y < 1.3) & (ax > 0.65) & (ax < 3.3)
    v = v - 0.24 * socket
    nose = (ax < 0.55) & (Y < 1.3) & (Y > -1.5)
    v = v + nose * np.where(X < 0, 0.16, -0.06)
    v = v - 0.2 * ((ax < 1.0) & (np.abs(Y + 1.75) < 0.28))                    # under the nose
    v = v + 0.08 * ((ax > 1.6) & (ax < 3.0) & (Y > -1.1) & (Y < -0.3))         # cheekbones
    v = v - 0.08 * ((ax > 2.2) & (Y < -1.5) & (Y > -3.2))                      # cheek hollows
    lipline = (np.abs(Y + 2.75 + 0.1 * X ** 2) < 0.22) & (ax < 1.4)
    lower = (np.abs(Y + 3.25) < 0.25) & (ax < 1.0)
    v = v - lipline * 0.3 + lower * 0.12
    v = v + 0.1 * ((ax < 1.1) & (Y < -3.9) & (Y > -4.6))                       # chin
    v = v + 0.1 * spec(ctx, 6) + dither(ctx, 0.04) - ctx.ao * 0.3
    rgb = sramp(GOLD, v + 0.12)
    glow = np.zeros(ctx.N, dtype=bool)
    # eye slits angled up and out, white-hot cores
    ey = Y - 0.55 - 0.16 * (ax - 0.8)
    eye = (ax > 0.75) & (ax < 2.75) & (np.abs(ey) < 0.34)
    core = (ax > 1.05) & (ax < 2.4) & (np.abs(ey) < 0.2)
    rgb[eye] = SUN[5]
    rgb[core] = SUN[8]
    glow |= eye
    # light-tears: thin glowing channels from the eyes down the cheeks
    tear = (np.abs(ax - 1.75 - 0.08 * (Y + 0.0)) < 0.24) & (Y < 0.1) & (Y > -2.7)
    rgb[tear] = sramp(SUN, 0.42 + 0.25 * np.clip((Y[tear] + 2.7) / 2.8, 0, 1))
    glow |= tear
    # small sun mark on the brow
    sy = Y - 2.9
    sr = np.sqrt(X * X + sy * sy)
    mark = sr < 0.55
    rgb[mark] = SUN[6]
    glow |= mark
    out = ~egg
    rgb[out] = sramp(CRIMSON, 0.1 + 0.05 * dither(ctx, 1.0)[out])
    glow[out] = False
    return rgb, 255, glow


def mask_crown(ctx):
    """Ray crown framing the mask: 16 alternating gold rays from an oval rim (plane)."""
    x, y = plane_xy(ctx)
    W = ctx.tw / 4.0
    X, Y = x * W, y * W
    Yc = Y - ctx.params.get("cy", 0.0)
    ex = X / 1.0
    ey = Yc / 1.2
    r = np.sqrt(ex * ex + ey * ey) + 1e-6
    a = np.arctan2(ey, ex)
    n = 16
    k = np.floor(a * n / TAU + 0.5)
    q = a * n / TAU - k                                        # -0.5..0.5
    long = np.mod(k, 2) == 0
    r0 = ctx.params.get("r0", 4.3)
    r1 = np.where(long, ctx.params.get("r_long", 7.6), ctx.params.get("r_short", 6.2))
    width = 0.42 * np.clip((r1 - r) / (r1 - r0), 0, 1) ** 0.9
    ray = (r > r0 - 0.2) & (r < r1) & (np.abs(q) < width)
    rimr = (r > r0 - 0.6) & (r < r0 + 0.25)
    m = ray | rimr
    v = 0.62 + 0.18 * (q < 0) - 0.14 * (np.abs(q) > width * 0.6) + 0.1 * (1 - np.clip((r - r0) / 3, 0, 1))
    v = v + tone(ctx, 0.25) + dither(ctx, 0.05)
    rgb = sramp(GOLD, v)
    rgb[rimr] = sramp(GOLD, 0.5 + 0.2 * (Yc[rimr] > 0) + dither(ctx, 0.05)[rimr])
    glow = np.zeros(ctx.N, dtype=bool)
    tip = ray & long & (r > r1 - 1.1)
    rgb[tip] = sramp(SUN, 0.7 + 0.3 * (r[tip] - (r1[tip] - 1.1)))
    glow |= tip
    return rgb, np.where(m, 255, 0), glow


# =============================================================================== halo

def polar(ctx):
    x, y = plane_xy(ctx)
    R = ctx.tw / 4.0                                           # plane half-size in units
    X, Y = x * R, y * R
    return X, Y, np.sqrt(X * X + Y * Y) + 1e-6, np.arctan2(Y, X), R


def halo_disc(ctx):
    """Front halo layer: the blazing sun disc (white core, engraved rings), a gold rim with studs,
    and 24 wavy flame tongues. Everything is 15-degree symmetric so the spin loops cleanly, and the
    shading is radial only (a spinning layer must not carry a fixed highlight)."""
    X, Y, r, a, R = polar(ctx)
    rd = ctx.params.get("r_disc", 9.5)
    rr = ctx.params.get("r_rim", 10.8)
    rf = ctx.params.get("r_flame", 15.4)
    rgb = np.zeros((ctx.N, 3))
    glow = np.zeros(ctx.N, dtype=bool)
    disc = r < rd
    rim = (r >= rd) & (r < rr)
    # disc: white-hot heart, yellow body, molten orange limb; two engraved rings and radial grain
    f = r / rd
    v = 0.97 - 0.50 * f ** 1.8
    for rk, dv in ((0.36, 0.13), (0.62, 0.12), (0.86, 0.10)):
        v = v - dv * (np.abs(r - rd * rk) < 0.26) + 0.6 * dv * (np.abs(r - rd * rk - 0.42) < 0.18)
    q = np.abs(np.mod(a * 48 / TAU, 1.0) - 0.5)
    v = v - 0.07 * ((q > 0.36) & (r > rd * 0.64) & (r < rd * 0.84))
    q2 = np.abs(np.mod(a * 24 / TAU + 0.5, 1.0) - 0.5)
    tri = (q2 < 0.5 * np.clip((r - rd * 0.38) / (rd * 0.22), 0, 1)) & (r > rd * 0.38) & (r < rd * 0.6)
    v = v - 0.06 * tri
    rgb[disc] = sramp(SUN, (v + dither(ctx, 0.03))[disc])
    glow |= disc
    # rim: polished gold band (lit inner lip, dark outer groove) with 24 glowing studs
    stud = rim & (np.abs(np.mod(a * 24 / TAU, 1.0) - 0.5) > 0.36) & (np.abs(r - (rd + rr) / 2) < 0.36)
    fr = (r - rd) / (rr - rd)
    vr = 0.74 - 0.34 * fr + 0.12 * (fr < 0.22) - 0.14 * (fr > 0.8)
    rgb[rim] = sramp(GOLD, (vr + dither(ctx, 0.04))[rim])
    rgb[stud] = SUN[6]
    glow |= stud
    # flames: 24 wavy tongues, alternating long/short (30 deg) -> use equal length pairs mirrored
    n = 24
    wob = 0.15 * np.sin((r - rr) * 0.9)
    u = a * n / TAU + wob
    k = np.floor(u + 0.5)
    fq = u - k
    prog = np.clip((r - rr + 0.4) / (rf - rr + 0.4), 0, 1)
    width = 0.44 * np.clip(1 - prog, 0, 1) ** 0.7
    flame = (r >= rr - 0.1) & (np.abs(fq) < width) & (prog < 1)
    edge = np.abs(fq) / np.maximum(width, 1e-3)
    vf = 0.74 - 0.46 * prog - 0.14 * edge ** 2 + 0.05 * (fq < 0)
    rgb[flame] = sramp(SUN, (vf + dither(ctx, 0.04))[flame])
    glow |= flame & (edge < 0.72)
    rgb[flame & (edge >= 0.72)] = sramp(GOLD, (0.62 - 0.3 * prog + dither(ctx, 0.04))[flame & (edge >= 0.72)])
    m = disc | rim | flame
    return rgb, np.where(m, 255, 0), glow & m


def halo_rays(ctx):
    """Back halo layer: 16 long straight gold rays interleaved with 16 short ones (22.5 degree
    symmetry) joined by a thin ring, with glowing spines on the long rays and an opaque engraved
    back plate behind the disc (it hides the eclipse moon parked between the two layers)."""
    X, Y, r, a, R = polar(ctx)
    n = 32
    u = a * n / TAU
    k = np.floor(u + 0.5)
    fq = u - k
    dperp = np.abs(fq) * TAU / n * r
    longer = np.mod(k, 2) == 0
    r0 = ctx.params.get("r0", 9.0)
    r1 = np.where(longer, ctx.params.get("r_long", 20.5), ctx.params.get("r_short", 15.6))
    prog = np.clip((r - r0) / (r1 - r0), 0, 1)
    w = np.where(longer, 1.2, 0.85) * (1 - prog) ** 0.8 + 0.08
    ray = (r > r0) & (r < r1) & (dperp < w)
    ring_r = ctx.params.get("r_ring", 17.2)
    ring = np.abs(r - ring_r) < 0.4
    plate_r = ctx.params.get("r_plate", 10.4)
    plate = r < plate_r
    spine = ray & (dperp < np.maximum(w * 0.3, 0.22)) & longer & ~plate
    rgb = np.zeros((ctx.N, 3))
    v = 0.6 + 0.16 * (fq < 0) - 0.16 * (dperp > w * 0.68) - 0.12 * prog + dither(ctx, 0.04)
    rgb[:] = sramp(GOLD, v)
    fr = np.abs(r - ring_r) / 0.4
    rgb[ring] = sramp(GOLD, (0.66 - 0.2 * fr + dither(ctx, 0.04))[ring])
    rgb[spine] = sramp(SUN, 0.72 - 0.34 * prog[spine])
    # back plate: dark-to-bright engraved gold with a 32-fold sunburst and two rings
    pv = 0.5 + 0.12 * (r / plate_r) - 0.16 * (np.abs(r - plate_r * 0.55) < 0.3) - 0.14 * (r > plate_r - 0.6)
    qq = np.abs(np.mod(a * 32 / TAU, 1.0) - 0.5)
    pv = pv - 0.12 * ((qq > 0.4) & (r > plate_r * 0.6)) + 0.1 * (r < plate_r * 0.3)
    rgb[plate] = sramp(GOLD, (pv + dither(ctx, 0.04))[plate])
    glow = spine.copy()
    m = ray | ring | plate
    return rgb, np.where(m, 255, 0), glow & m


def moon(ctx):
    """Eclipse moon disc: near-black with faint craters and a pale glowing rim (plane)."""
    X, Y, r, a, R = polar(ctx)
    rm = ctx.params.get("r", 9.4)
    disc = r < rm
    v = 0.45 + (fbm(ctx.p, 0.45, 3, 91) - 0.5) * 0.5 - 0.3 * (r / rm) ** 2
    rgb = dramp(MOON, v, ctx, 0.6)
    rim = disc & (r > rm - 0.55)
    rgb[rim] = np.array([255, 236, 190])
    inner = disc & (r > rm - 1.0) & ~rim
    rgb[inner] = MOON[5]
    return rgb, np.where(disc, 255, 0), rim


def diadem(ctx):
    """Brow diadem (plane): a gold band with five rising rays, the centre one tallest, and a glowing
    sun stone at its base."""
    x, y = plane_xy(ctx)
    W, H = ctx.tw / 4.0, ctx.th / 4.0
    X, Y = x * W, (y + 1) * H                                  # Y = 0 at the bottom edge
    band = (Y < 1.3) & (np.abs(X) < W - 0.6 + 0.3 * (Y < 0.6))
    m = band.copy()
    v = 0.6 + 0.16 * (Y > 0.9) - 0.12 * (Y < 0.35) + dither(ctx, 0.04)
    for cx, hgt, wd in ((0.0, 2 * H - 0.2, 1.25), (-2.5, 2 * H * 0.74, 1.0), (2.5, 2 * H * 0.74, 1.0),
                        (-4.7, 2 * H * 0.5, 0.8), (4.7, 2 * H * 0.5, 0.8)):
        prog = np.clip((Y - 1.0) / (hgt - 1.0), 0, 1)
        ray = (Y >= 0.9) & (Y < hgt) & (np.abs(X - cx) < wd * (1 - prog) ** 0.9 + 0.12)
        m |= ray
        v = v + ray * (0.14 * (X < cx) - 0.06 * prog)
    rgb = sramp(GOLD, v)
    glow = np.zeros(ctx.N, dtype=bool)
    gem = (X / 0.85) ** 2 + ((Y - 0.75) / 0.6) ** 2 < 1.0
    rgb[gem] = SUN[6]
    glow |= gem
    return rgb, np.where(m, 255, 0), glow


# =============================================================================== gems, staff, belt

def sun_gem(ctx):
    """Glowing faceted sun gem / orb."""
    x, y = plane_xy(ctx)
    v = 0.92 - 0.35 * (np.abs(x) + np.abs(y)) * 0.6 + 0.12 * ((x < 0) & (y > 0))
    if ctx.face in ("down",):
        v = v - 0.2
    return sramp(SUN, v + dither(ctx, 0.04)), 255, np.ones(ctx.N, dtype=bool)


def buckle(ctx):
    """Belt buckle: gold sun disc with a glowing centre (north face)."""
    rgb, glow = gold(ctx)
    if ctx.face == "north":
        x, y = face_units(ctx)
        r = np.sqrt(x * x + y * y)
        core = r < 0.9
        ring = np.abs(r - 1.35) < 0.22
        rgb[ring] = GOLD[8]
        rgb[core] = sramp(SUN, 0.75 + 0.2 * (1 - r[core] / 0.9))
        glow = glow | core
    return rgb, 255, glow


def belt(ctx):
    """Broad gold belt with square sun plaques separated by dark gaps."""
    v = gold_value(ctx, 0.7)
    glow = np.zeros(ctx.N, dtype=bool)
    if side_face(ctx):
        u = ctx.i.astype(float)
        cell = np.mod(u, 10)
        gap = cell < 1
        v = v - gap * 0.35
        pc = np.abs(cell - 5.5)
        dot = (pc < 1.2) & (np.abs(ctx.t - 0.5) < 0.2)
        v = v + dot * 0.18
    return sramp(GOLD, v + dither(ctx, 0.05)), glow


def staff_shaft(ctx):
    """Staff shaft: polished gold with a dark spiral inlay; crimson grip wrap via params."""
    if ctx.params.get("grip"):
        v = 0.5 + 0.12 * np.sin((ctx.j + ctx.i * 0.6) * TAU / 4) + tone(ctx, 0.4)
        return dramp(CRIMSON, v, ctx, 0.5), 255, np.zeros(ctx.N, dtype=bool)
    v = 0.56 + (0.5 - np.abs(ctx.s - 0.5)) * 0.3 + tone(ctx, 0.4)
    y = ctx.pw[:, 1]
    sp = np.mod(y * 0.5 + ctx.s * 1.0 + (ctx.face in ("east", "south")) * 0.5, 2.0) < 0.35
    v = v - sp * 0.3
    if ctx.face in ("up", "down"):
        v = v * 0 + 0.55
    return sramp(GOLD, v + dither(ctx, 0.05)), 255, np.zeros(ctx.N, dtype=bool)


def staff_sun(ctx):
    """Staff finial (plane): gold ring and 12 tapered rays around a hollow centre."""
    x, y = plane_xy(ctx)
    R = ctx.tw / 4.0
    X, Y = x * R, y * R
    r = np.sqrt(X * X + Y * Y) + 1e-6
    a = np.arctan2(Y, X)
    r_in, r_out = ctx.params.get("r_in", 3.2), ctx.params.get("r_out", 4.4)
    ring = (r > r_in) & (r < r_out)
    n = 12
    u = a * n / TAU
    k = np.floor(u + 0.5)
    fq = u - k
    longer = np.mod(k, 2) == 0
    r1 = np.where(longer, R - 0.2, R * 0.74)
    prog = np.clip((r - r_out) / (r1 - r_out), 0, 1)
    w = 0.36 * (1 - prog) ** 0.8
    ray = (r >= r_out - 0.2) & (r < r1) & (np.abs(fq) < w)
    v = 0.62 + 0.18 * (fq < 0) - 0.12 * prog + 0.12 * np.cos(a - 2.2) * ring + dither(ctx, 0.04)
    v = v - 0.18 * (ring & (np.abs(r - (r_in + r_out) / 2) < 0.18))
    rgb = sramp(GOLD, v)
    glow = np.zeros(ctx.N, dtype=bool)
    tip = ray & longer & (prog > 0.72)
    rgb[tip] = sramp(SUN, 0.7 + 0.25 * prog[tip])
    glow |= tip
    m = ring | ray
    return rgb, np.where(m, 255, 0), glow


def bronze(ctx):
    v = 0.5 + (fbm(ctx.p, 0.5, 2, 21) - 0.5) * 0.2 + bevel(ctx, 1.5, 0.12, 0.12) + tone(ctx, 0.5)
    return dramp(BRONZE, v, ctx, 0.6), np.zeros(ctx.N, dtype=bool)


# =============================================================================== evolution stage parts

def tongues(r, a, r0, n, length, width, wob=0.18, offset=0.0, inward=False):
    """n flame tongues around a ring at radius r0 (outward, or inward towards the centre). The wobble
    depends on the radius only, so the pattern keeps its 360/n symmetry (spinning parts loop clean).
    Returns (mask, progress 0 base..1 tip, |offset| 0 centre..1 edge)."""
    d = (r0 - r) if inward else (r - r0)
    u = a * n / TAU + wob * np.sin(d * 0.85) + offset
    fq = u - np.floor(u + 0.5)
    prog = np.clip((d + 0.3) / (length + 0.3), 0, 1)
    w = width * np.clip(1 - prog, 0, 1) ** 0.7
    m = (d >= -0.3) & (np.abs(fq) < w) & (prog < 1)
    return m, prog, np.abs(fq) / np.maximum(w, 1e-3)


def fire_ring(ctx):
    """Stage 2 outer halo: a gold band with a white-hot seam, 24 long flame tongues licking outward
    with 24 short ones between them, and short licks curling inward. 15-degree symmetric, radial
    shading only (it spins with the flame disc)."""
    X, Y, r, a, R = polar(ctx)
    rb = ctx.params.get("r_band", 23.0)
    b0, b1 = rb - 0.95, rb + 0.95
    rgb = np.zeros((ctx.N, 3))
    glow = np.zeros(ctx.N, dtype=bool)
    m_out, p_out, e_out = tongues(r, a, b1, 24, 4.9, 0.44)
    m_mid, p_mid, e_mid = tongues(r, a, b1, 24, 2.9, 0.3, offset=0.5)
    m_in, p_in, e_in = tongues(r, a, b0, 24, 1.8, 0.3, inward=True, offset=0.5)
    for m, p, e in ((m_in, p_in, e_in), (m_mid, p_mid, e_mid), (m_out, p_out, e_out)):
        vf = 0.86 - 0.56 * p - 0.16 * e ** 2
        rgb[m] = sramp(SUN, (vf + dither(ctx, 0.04))[m])
        rim = m & (e > 0.74)
        rgb[rim] = sramp(SAFFRON, (0.62 - 0.25 * p + dither(ctx, 0.04))[rim])
        glow |= m & ~rim
    band = (r >= b0) & (r < b1)
    fr = (r - b0) / (b1 - b0)
    vb = 0.74 - 0.3 * fr + 0.14 * (fr < 0.22) - 0.16 * (fr > 0.82)
    rgb[band] = sramp(GOLD, (vb + dither(ctx, 0.04))[band])
    seam = band & (np.abs(fr - 0.5) < 0.17)
    rgb[seam] = SUN[7]
    stud = band & (np.abs(np.mod(a * 24 / TAU, 1.0) - 0.5) > 0.42) & (np.abs(fr - 0.5) < 0.34)
    rgb[stud] = SUN[8]
    glow |= seam | stud
    m = band | m_out | m_mid | m_in
    return rgb, np.where(m, 255, 0), glow & m


def sun_plate(ctx):
    """Shoulder sun plate (plane): an engraved gold disc with a glowing heart, a raised rim and 12
    alternating long/short rays whose long tips glow."""
    X, Y, r, a, R = polar(ctx)
    rd = ctx.params.get("r_disc", 3.4)
    disc = r < rd
    v = 0.66 - 0.12 * (r / rd) + 0.12 * (Y > 0) - 0.08 * (X > 0)
    v = v - 0.2 * (np.abs(r - rd * 0.62) < 0.22) + 0.18 * (r > rd - 0.45)
    n = 12
    u = a * n / TAU
    k = np.floor(u + 0.5)
    fq = u - k
    longer = np.mod(k, 2) == 0
    r1 = np.where(longer, R - 0.25, R * 0.74)
    prog = np.clip((r - rd) / (r1 - rd), 0, 1)
    w = 0.42 * (1 - prog) ** 0.8 + 0.03
    ray = (r >= rd - 0.2) & (r < r1) & (np.abs(fq) < w)
    vr = 0.64 + 0.16 * (fq < 0) - 0.14 * (np.abs(fq) > w * 0.62) - 0.1 * prog
    vv = np.where(disc, v, vr) + dither(ctx, 0.04)
    rgb = sramp(GOLD, vv)
    glow = np.zeros(ctx.N, dtype=bool)
    core = r < rd * 0.42
    rgb[core] = sramp(SUN, 0.92 - 0.3 * r[core] / (rd * 0.42))
    tip = ray & longer & (prog > 0.68)
    rgb[tip] = sramp(SUN, 0.62 + 0.3 * prog[tip])
    glow |= core | tip
    m = disc | ray
    return rgb, np.where(m, 255, 0), glow & m


def _feather(u, y, base, tip, width):
    """Pointed feather blade from base to tip: (inside, along 0..1, across |b| / half-width)."""
    bx, by = base
    dx, dy = tip[0] - bx, tip[1] - by
    L = math.hypot(dx, dy)
    dx, dy = dx / L, dy / L
    a = ((u - bx) * dx + (y - by) * dy) / L
    b = (u - bx) * (-dy) + (y - by) * dx
    ac = np.clip(a, 0, 1)
    hw = width / 2 * (ac ** 0.42 * (1 - ac) ** 0.62) / 0.52
    inside = (a >= 0) & (a <= 1) & (np.abs(b) <= hw)
    return inside, a, np.abs(b) / np.maximum(hw, 1e-3), b, L


def light_wing(ctx):
    """Stage 3 wing of light (plane): pointed feathers of white-gold light that burn to saffron at
    their tips, each with a bright quill and a thin darker rim so the layers read, coverts over the
    secondaries and a white-hot leading edge. params: side, u0, y_top, feathers, coverts, arm (all in
    wing coordinates: u outward from the root, y up)."""
    prm = ctx.params
    W, H = ctx.tw / 2.0, ctx.th / 2.0
    s = ctx.s if prm["side"] > 0 else 1 - ctx.s
    u = prm["u0"] + s * W
    y = prm["y_top"] - ctx.t * H
    rgb = np.zeros((ctx.N, 3))
    glow = np.zeros(ctx.N, dtype=bool)
    shape = np.zeros(ctx.N, dtype=bool)
    layers = [(f, 0.0) for f in prm.get("feathers", [])] + [(f, 0.08) for f in prm.get("coverts", [])]
    for k, ((base, tip, width), lift) in enumerate(layers):
        m, a, e, b, L = _feather(u, y, base, tip, width)
        if not m.any():
            continue
        a = np.clip(a, 0, 1)
        barb = 0.05 * np.sin((a * L - np.abs(b) * 1.3) * 2.4)
        v = 0.92 + lift - 0.06 * (k % 2) - 0.5 * a ** 1.2 - 0.12 * e ** 2 + barb + dither(ctx, 0.04)
        col = sramp(SUN, v)
        hot = a > 0.7
        col[hot] = sramp(SAFFRON, 0.86 - (a[hot] - 0.7) * 1.25 + barb[hot] + dither(ctx, 0.04)[hot])
        quill = (np.abs(b) < 0.22) & (a < 0.86)
        col[quill] = SUN[8]
        rim = e > 0.7
        col[rim] = sramp(GOLD, 0.4 + 0.18 * (1 - a[rim]) + dither(ctx, 0.04)[rim])
        rgb[m] = col[m]
        glow[m] = ~rim[m]
        shape |= m
    arm = prm.get("arm")
    if arm:
        from bosslib import polyline_dist
        d = polyline_dist(u, y, arm)
        edge = d < 1.25
        rgb[edge] = sramp(SUN, 0.95 - 0.3 * d[edge] / 1.25)
        rgb[edge & (d > 0.95)] = GOLD[6]
        glow |= edge & (d <= 0.95)
        shape |= edge
    return rgb, np.where(shape, 255, 0), glow & shape


def sun_spike(ctx):
    """Crown ray (stacked spike segments): polished sun-gold brightening outward, white-hot point."""
    pr = ctx.params
    prog = np.clip((ctx.p[:, 1] - pr["spike_base"][1]) / pr["spike_len"], 0, 1)
    v = gold_value(ctx, 0.6) + 0.22 * prog + (0.5 - np.abs(ctx.s - 0.5)) * 0.16
    rgb = sramp(GOLD, v + dither(ctx, 0.05))
    glow = np.zeros(ctx.N, dtype=bool)
    tip = prog > 0.8
    rgb[tip] = sramp(SUN, 0.62 + 0.36 * (prog[tip] - 0.8) / 0.2)
    glow |= tip
    return rgb, 255, glow


def _w(fn):
    def sh(ctx):
        rgb, glow = fn(ctx)
        return rgb, 255, glow
    return sh


SHADERS = {
    "gold": _w(lambda c: gold(c)),
    "gold_soft": _w(lambda c: gold(c, polish=0.55)),
    "gold_cuirass": _w(lambda c: gold(c, engrave="sunburst")),
    "gold_bands": _w(lambda c: gold(c, engrave="bands")),
    "gold_plate": _w(gold_rim),
    "gauntlet": _w(gauntlet),
    "cuff": _w(lambda c: gold(c, engrave="bands")),
    "gold_ray": _w(gold_ray),
    "belt": _w(belt),
    "buckle": buckle,
    "cloth_dark": _w(cloth_dark),
    "sash": _w(sash),
    "sleeve": _w(sleeve),
    "hood": _w(hood),
    "mask": mask,
    "mask_crown": mask_crown,
    "robe": robe,
    "tabard": tabard,
    "fauld": fauld,
    "mantle": mantle,
    "halo_disc": halo_disc,
    "halo_rays": halo_rays,
    "moon": moon,
    "diadem": diadem,
    "sun_gem": sun_gem,
    "staff_shaft": staff_shaft,
    "staff_sun": staff_sun,
    "bronze": _w(bronze),
    # evolution stage parts
    "fire_ring": fire_ring,
    "sun_plate": sun_plate,
    "light_wing": light_wing,
    "sun_spike": sun_spike,
}
