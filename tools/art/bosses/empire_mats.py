"""Ender Empire materials shared by sentinel_construct and ender_colossus: purpur tiles, glossy
obsidian, engraved gold, violet ender glow, end rods and ender-eye teal."""
import math

import numpy as np

from bosslib import fbm, hash3, palette, ramp, vnoise, worley, polyline_dist
from bossfx import (bevel, border_coords, dither, dramp, edge_dist, filigree, runes, smoothstep, sramp, spec,
                    plane_xy, mix)

PURPUR = palette("#2e1d36", "#432a4d", "#5a3a66", "#714c80", "#8a5f99", "#a275b0", "#b98ec6", "#cfabd9", "#e3cbea")
PURPUR_D = palette("#1f1426", "#2d1d37", "#3d284a", "#4e345d", "#634273", "#7a558b", "#9270a3")
OBSID = palette("#050309", "#0b0713", "#120c1e", "#1a122b", "#241939", "#30224b", "#3f2e62", "#56428a", "#7a64b8")
GOLD = palette("#241002", "#3f2104", "#61360a", "#875013", "#ad6d1d", "#cf8f2b", "#e9b145", "#f9d475", "#fff1c4")
ENDER = palette("#1c0636", "#36105f", "#561c8f", "#7a2cc0", "#9d4ae8", "#bd78ff", "#d9a8ff", "#efd6ff", "#ffffff")
MAGENTA = palette("#3a0636", "#64105c", "#921c86", "#bf34b0", "#e05ad2", "#f490e8", "#ffc8f6", "#ffffff")
TEAL = palette("#031a16", "#073329", "#0e5240", "#18755a", "#279a74", "#3fbf8e", "#71dfae", "#b2f5d2", "#ecfff6")
ROD = palette("#6e6478", "#8f8698", "#b2abb9", "#d2ccd7", "#ebe7ef", "#ffffff")


def _tone(ctx):
    """Shared light terms: up faces brighter, down faces darker, AO."""
    n = ctx.nw
    return 0.06 * max(0.0, n[1]) - 0.12 * max(0.0, -n[1]) - ctx.ao * 0.55


def purpur(ctx, cracked=False, tile=8, glow_cracks=True, trim=None, worn=0.0):
    """Purpur tiles (tile = texels per tile). trim: None | 'gold' (gold border with filigree)."""
    p = ctx.p
    i, j = ctx.i, ctx.j
    # offset rows like masonry so the pattern reads as carved purpur
    row = np.floor(j / tile)
    ii = i + np.mod(row, 2) * (tile // 2)
    col = np.floor(ii / tile)
    fx = np.mod(ii, tile)
    fy = np.mod(j, tile)
    tid = hash3(col, row, np.full(ctx.N, ctx.index), 3)
    v = 0.56 + (tid - 0.5) * 0.12 + (fbm(p, 0.35, 3, 11) - 0.5) * 0.18
    # tile bevel: lit top-left lip, shaded bottom-right lip, dark grout
    v += np.where((fx == 1) | (fy == 1), 0.1, 0) + np.where((fx == tile - 2) | (fy == tile - 2), -0.08, 0)
    grout = (fx == 0) | (fy == 0)
    v -= grout * 0.26
    # inner panel of each tile (the purpur block's raised centre)
    inner = (fx >= 3) & (fx <= tile - 3) & (fy >= 3) & (fy <= tile - 3)
    v += inner * 0.05
    v += (vnoise(p, 1.3, 12) - 0.5) * 0.08
    if worn:
        v -= (fbm(p, 0.25, 3, 13) > 1 - worn) * 0.12
    v += bevel(ctx, 2.0, 0.14, 0.18) + _tone(ctx)
    glow = np.zeros(ctx.N, dtype=bool)
    rgb = dramp(PURPUR, v, ctx)
    if cracked:
        f1, f2, cid = worley(p * np.array([1.0, 0.7, 1.0]), 0.09, 21)
        e = f2 - f1
        gate = fbm(p, 0.05, 2, 23) > 0.44
        crack = (e < 0.035) & gate
        lip = (e < 0.075) & gate & ~crack
        rgb[lip] = rgb[lip] * 0.72
        if glow_cracks:
            hot = (e < 0.016) & gate
            rgb[crack] = ENDER[2]
            rgb[hot] = ENDER[6]
            glow = crack
        else:
            rgb[crack] = PURPUR[0]
    if trim == "gold":
        tb = gold_trim_mask(ctx)
        if tb.any():
            g, gl = gold_px(ctx, tb, engraved=False)
            rgb[tb] = g
    return rgb, glow


def gold_trim_mask(ctx, inset=1, corner=5):
    """Thin inlaid gold line inset from the face border plus filigree corner pieces."""
    d = edge_dist(ctx)
    line = d == inset
    if min(ctx.tw, ctx.th) < 8:
        return line
    i, j, tw, th = ctx.i, ctx.j, ctx.tw, ctx.th
    cx = np.minimum(i, tw - 1 - i)
    cy = np.minimum(j, th - 1 - j)
    k = corner
    # corner bracket: an L of width 2 plus a small curl
    brk = ((cx <= k) & (cy <= 2) & (cy >= 1)) | ((cy <= k) & (cx <= 2) & (cx >= 1))
    r = np.sqrt((cx - k * 0.75) ** 2 + (cy - k * 0.75) ** 2)
    curl = (np.abs(r - 1.3) < 0.6) & (cx <= k + 1) & (cy <= k + 1)
    stud = (cx <= 3) & (cy <= 3) & (cx >= 1) & (cy >= 1)
    return line | brk | curl | stud


def gold_px(ctx, sel, engraved=True):
    """Gold colours for the selected texels (used for trims on other materials)."""
    p = ctx.p
    v = 0.58 + (fbm(p, 0.4, 2, 31) - 0.5) * 0.14 + _tone(ctx) + 0.25 * spec(ctx, 8)
    if ctx.face not in ("up", "down"):
        v = v + (0.5 - ctx.t) * 0.3
    d = edge_dist(ctx)
    v = v + np.where(d == 0, 0.2, 0) - np.where(d == 2, 0.12, 0)
    return sramp(GOLD, (v + dither(ctx, 0.06))[sel]), None


def gold(ctx, filig=True, rivets=False, gem=None):
    """Polished gold with engraved filigree scroll-work."""
    p = ctx.p
    v = 0.5 + (fbm(p, 0.4, 2, 31) - 0.5) * 0.12
    if ctx.face not in ("up", "down"):
        # polished: bright upper band, dark reflected horizon, warm lower bounce
        t = ctx.t
        v += 0.26 * np.exp(-((t - 0.18) / 0.16) ** 2) - 0.16 * np.exp(-((t - 0.55) / 0.12) ** 2) + 0.05 * (t > 0.8)
    else:
        v += 0.12 if ctx.face == "up" else -0.1
    v += bevel(ctx, 2.2, 0.3, 0.26) + _tone(ctx) + 0.2 * spec(ctx, 8)
    glow = np.zeros(ctx.N, dtype=bool)
    if filig and min(ctx.tw, ctx.th) >= 10:
        line, curl = filigree(ctx, d0=1.5, width=min(6.0, min(ctx.tw, ctx.th) / 2 - 2), period=12)
        v -= (line | curl) * 0.34
    if rivets:
        d = edge_dist(ctx)
        a, _ = border_coords(ctx)
        riv = (np.abs(d - 1.5) < 0.9) & (np.mod(a, 10) < 1.6)
        v += riv * 0.3
    rgb = sramp(GOLD, v + dither(ctx, 0.05))
    return rgb, glow


def obsidian(ctx, runes_on=False, rune_cell=7.0, rune_density=0.34, glints=True, seed=0, rune_fill=0.55):
    p = ctx.p
    # glassy conchoidal facets: stretched noise with sharp ridges and cool sheen
    n1 = fbm(p * np.array([1.0, 2.2, 1.0]), 0.18, 3, 41 + seed)
    facet = np.abs(vnoise(p, 0.32, 43 + seed) - 0.5)
    v = 0.38 + (n1 - 0.5) * 0.34 + (facet < 0.05) * 0.18 - (facet > 0.4) * 0.05
    if ctx.face not in ("up", "down"):
        v += 0.1 * np.exp(-((ctx.t - 0.2) / 0.2) ** 2)
    v += bevel(ctx, 2.0, 0.24, 0.1) + _tone(ctx) + 0.18 * spec(ctx, 10)
    rgb = dramp(OBSID, v, ctx, 0.7)
    glow = np.zeros(ctx.N, dtype=bool)
    if glints:
        g = hash3(np.floor(p[:, 0] * 2 + .01), np.floor(p[:, 1] * 2 + .01), np.floor(p[:, 2] * 2 + .01), 47 + seed) > 0.985
        rgb[g] = OBSID[7]
    if runes_on:
        x = ctx.i.astype(float)
        y = ctx.j.astype(float)
        m, cid = runes(x + ctx.index * 13, y, cell=rune_cell, seed=5 + seed, density=rune_density, stroke=0.55)
        d = edge_dist(ctx)
        m &= (d >= 2) & (cid < rune_fill)
        if m.any():
            rgb[m] = ENDER[4]
            glow |= m
    return rgb, glow


def ender_glow(ctx, base=0.6, pal=ENDER):
    """Pure emissive energy surface with soft internal swirls."""
    p = ctx.p
    v = base + (fbm(p, 0.3, 3, 51) - 0.5) * 0.4 + (0.5 - np.abs(ctx.s - 0.5)) * 0.2
    return sramp(pal, v + dither(ctx, 0.04)), np.ones(ctx.N, dtype=bool)


def lens(ctx, pupil="slit"):
    """Violet eye-lens: concentric rings with a bright core; the north face is the iris."""
    if ctx.face != "north":
        v = 0.25 + (0.5 - ctx.t) * 0.2
        return dramp(ENDER, v, ctx), np.ones(ctx.N, dtype=bool)
    x, y = plane_xy(ctx)
    r = np.sqrt(x * x + y * y)
    ang = np.arctan2(y, x)
    v = 0.85 - r * 0.62
    v += 0.08 * np.cos(r * 18)                        # concentric grooves
    v += 0.06 * np.cos(ang * 12) * (r > 0.45)         # radial iris fibres
    rgb = sramp(ENDER, v + dither(ctx, 0.05))
    if pupil == "slit":
        sl = (np.abs(x) < 0.12 * (1 - np.abs(y) ** 2)) & (np.abs(y) < 0.7)
        rgb[sl] = ENDER[8]
    elif pupil == "dot":
        rgb[r < 0.22] = ENDER[8]
    rim = r > 0.92
    rgb[rim] = ENDER[3]
    hl = (np.sqrt((x + 0.35) ** 2 + (y - 0.38) ** 2) < 0.13)
    rgb[hl] = np.array([255, 255, 255])
    return rgb, np.ones(ctx.N, dtype=bool)


def end_rod(ctx, tip_frac=0.0):
    p = ctx.p
    v = 0.55 + bevel(ctx, 1.5, 0.2, 0.2) + (0.5 - np.abs(ctx.s - 0.5)) * 0.4 + _tone(ctx) * 0.5
    rgb = sramp(ROD, v)
    glow = np.zeros(ctx.N, dtype=bool)
    if tip_frac > 0 and ctx.face not in ("up", "down"):
        tip = ctx.t < tip_frac
        rgb[tip] = sramp(ENDER, 0.75 + (tip_frac - ctx.t[tip]) * 0.6)
        glow |= tip
    if ctx.face == "up":
        rgb[:] = ENDER[7]
        glow[:] = True
    return rgb, glow


def ender_eye(ctx):
    """Ender-eye core: teal iris with a dark slit pupil on the north face, glowing."""
    if ctx.face != "north":
        v = 0.45 + (fbm(ctx.p, 0.5, 2, 61) - 0.5) * 0.3
        return dramp(TEAL, v, ctx), np.ones(ctx.N, dtype=bool)
    x, y = plane_xy(ctx)
    r = np.sqrt(x * x + y * y)
    ang = np.arctan2(y, x)
    v = 0.86 - r * 0.55 + 0.07 * np.cos(ang * 14 + r * 6)
    rgb = sramp(TEAL, v + dither(ctx, 0.05))
    glow = np.ones(ctx.N, dtype=bool)
    pupil = (np.abs(x) < 0.16 * (1 - (y / 0.8) ** 2)) & (np.abs(y) < 0.8)
    rgb[pupil] = np.array([8, 30, 24])
    glow[pupil] = False
    ring = np.abs(r - 0.92) < 0.08
    rgb[ring] = TEAL[3]
    return rgb, glow
