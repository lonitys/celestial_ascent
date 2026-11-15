"""Tide Titan: an ancient sea colossus with teal scales, coral growths, shell pauldrons,
a fin crest, glowing gills and a gold-and-coral trident.

Run: python tide_titan.py [--preview [--all]]
"""
import math
import sys

import numpy as np

import titanlib as tl
from titanlib import (Clip, edge_term, env, fbm, hash3, palette, ramp, shake, vgrad, worley, polyline_dist)
from anim_helpers import TAU, legs_for_drop

NAME = "tide_titan"
HITBOX = (2.0, 4.2)
THIGH, SHIN = 11.0, 15.0

# =============================================================================== geometry


def build_model():
    m = tl.Model(NAME)
    body = m.bone("body", "root", (0, 26, 0))
    body.boxb(0, 22, 0.5, 17, 7, 11, "scales")                                  # pelvis
    body.boxb(0, 26, 0.5, 18, 2, 12, "gold")                                    # gold belt
    body.box((0, 19.5, -5.9), (9, 10, 1), "kelp", rot=[-6, 0, 0])               # kelp loincloth
    body.box((-6.5, 20, -4.5), (5, 9, 1), "kelp", rot=[-4, 22, 4])
    body.box((6.5, 20, -4.5), (5, 9, 1), "kelp", rot=[-4, -22, -4])
    body.box((0, 20, 6.2), (12, 9, 1), "kelp", rot=[6, 0, 0])
    tail = m.bone("tail", "body", (0, 23, 5))
    tail.box((0, 20.5, 9.5), (7, 6, 10), "scales", rot=[28, 0, 0])
    tail.boxb(0, 18, 5.5, 5, 2, 2, "barnacle")
    tail_tip = m.bone("tail_tip", "tail", (0, 17.5, 13.5))
    tail_tip.box((0, 14.5, 17.5), (5, 5, 9), "scales", rot=[38, 0, 0])
    tail_tip.box((0, 9.5, 22.5), (1, 12, 9), "fin", rot=[38, 0, 0], inflate=-0.25, shape="tail")

    chest = m.bone("chest", "body", (0, 29, 0), rotation=[6, 0, 0])
    chest.boxb(0, 27, 0.5, 15, 9, 10, "belly_scales")                           # abdomen
    chest.boxb(0, 35, 0, 22, 16, 13, "scales", gills=True)                      # chest
    chest.boxb(0, 49, 1.0, 18, 4, 11, "scales")                                 # collar
    chest.box((-5.4, 45.0, -6.9), (9, 7, 2), "scales", rot=[-8, 10, 0])          # pectorals
    chest.box((5.4, 45.0, -6.9), (9, 7, 2), "scales", rot=[-8, -10, 0])
    chest.box((0, 41, 8.5), (1, 15, 5), "fin", rot=[-8, 0, 0], inflate=-0.2, shape="dorsal")           # dorsal ridge
    # coral reef growing out of the back
    chest.spike((-4, 46, 6.5), (-0.5, 1.0, 0.7), 13, 3, "coral_pink", segs=[0.45, 0.33, 0.22])
    chest.spike((-6.5, 51, 8.5), (-1.0, 0.7, 0.2), 6, 2, "coral_pink", segs=[1.0])
    chest.spike((3.5, 44, 6.5), (0.45, 1.0, 0.85), 11, 3, "coral_orange", segs=[0.45, 0.33, 0.22])
    chest.spike((6, 48, 9.5), (1.0, 0.8, 0.3), 5, 2, "coral_orange", segs=[1.0])
    chest.spike((0.5, 40, 7), (0.1, 0.5, 1.0), 7, 2, "coral_pink", segs=[0.6, 0.4])
    chest.box((-2, 37, 7.2), (5, 4, 3), "coral_lump")
    chest.box((5, 41, 7.0), (4, 3, 2), "coral_lump_o")
    chest.boxb(-6.5, 38, 6.9, 2, 2, 2, "barnacle")
    # antler-like side branches on the big reef growths
    chest.spike((-6.2, 49.5, 9.0), (-0.9, 0.9, 0.2), 6, 2, "coral_pink", segs=[1.0])
    chest.spike((-5.0, 52.5, 10.0), (0.2, 1.0, 0.9), 5, 2, "coral_pink", segs=[1.0])
    chest.spike((5.2, 48.0, 9.5), (0.2, 1.0, 1.0), 5, 2, "coral_orange", segs=[1.0])
    chest.spike((2.5, 46.5, 8.0), (-0.6, 1.0, 0.6), 4, 2, "coral_orange", segs=[1.0])

    neck = m.bone("neck", "chest", (0, 50, -2), rotation=[-6, 0, 0])
    neck.boxb(0, 48, -1.5, 9, 7, 8, "scales", gills=True)
    head = m.bone("head", "neck", (0, 54, -3))
    head.boxb(0, 52.5, -6.5, 12, 9, 13, "scales")                               # cranium
    head.boxb(0, 52.5, -15, 10, 5, 5, "scales")                                 # snout
    head.box((-3.6, 60.2, -12.0), (5, 2, 5), "scales", rot=[0, -10, -10])       # brow ridges
    head.box((3.6, 60.2, -12.0), (5, 2, 5), "scales", rot=[0, 10, 10])
    head.box((-3.6, 58.8, -13.25), (3, 1, 1), "eye", inflate=0.12)
    head.box((3.6, 58.8, -13.25), (3, 1, 1), "eye", inflate=0.12)
    head.box((0, 64.0, -5.5), (1, 12, 17), "fin", rot=[-8, 0, 0], inflate=-0.2, shape="crest")
    head.box((-6.6, 57.5, -2.5), (1, 9, 8), "fin", rot=[0, -25, -14], inflate=-0.2, shape="ear")
    head.box((6.6, 57.5, -2.5), (1, 9, 8), "fin", rot=[0, 25, 14], inflate=-0.2, shape="ear")
    jaw = m.bone("jaw", "head", (0, 53.5, -3))
    jaw.boxb(0, 50, -10, 11, 3, 15, "belly_scales")
    jaw.box((-3.0, 52.6, -16.8), (1, 2, 1), "tooth")
    jaw.box((3.0, 52.6, -16.8), (1, 2, 1), "tooth")
    jaw.box((0, 48.6, -9.0), (1, 4, 8), "fin", inflate=-0.2, shape="barbel")

    for side, nm in ((-1, "right"), (1, "left")):
        s = side
        arm = m.bone(f"{nm}_arm", "chest", (13 * s, 49, 0), rotation=[-6, 0, -5 * s])
        arm.boxb(16 * s, 37, 0, 7, 13, 8, "scales")                             # upper arm
        # scallop shell pauldron (three tiers) with coral growing from it
        arm.box((17.0 * s, 49.5, 0), (11, 5, 13), "shell", rot=[0, 0, -18 * s])
        arm.box((18.4 * s, 52.6, 0), (8, 3, 10), "shell", rot=[0, 0, -18 * s])
        arm.box((19.6 * s, 54.6, 0), (5, 2, 6), "shell", rot=[0, 0, -18 * s])
        arm.box((21.8 * s, 46.0, 0), (2, 3, 13), "shell", rot=[0, 0, -18 * s])  # rim
        if s < 0:
            arm.spike((16.5 * s, 54.5, 3), (-0.4, 1.0, 0.5), 9, 3, "coral_orange", segs=[0.6, 0.4])
            arm.spike((19 * s, 53.5, -3.5), (-0.6, 1.0, -0.3), 7, 2, "coral_pink", segs=[0.6, 0.4])
        else:
            arm.spike((16.5 * s, 54.5, 3), (0.45, 1.0, 0.5), 10, 3, "coral_pink", segs=[0.6, 0.4])
            arm.spike((19 * s, 53.5, -3.5), (0.6, 1.0, -0.3), 6, 2, "coral_orange", segs=[0.6, 0.4])
        arm.spike((17.5 * s, 57.5, 4.0), (0.9 * s, 0.8, 0.2), 4, 2, "coral_pink" if s < 0 else "coral_orange", segs=[1.0])
        fore = m.bone(f"{nm}_forearm", f"{nm}_arm", (16 * s, 37.5, 0), rotation=[-6, 0, 0])
        fore.boxb(16 * s, 26, -0.5, 7, 12, 8, "scales")                         # forearm
        fore.boxb(16 * s, 30, -0.5, 8, 5, 9, "gold", bracer=True)               # gold bracer
        fore.box((19.8 * s, 32, 3.5), (1, 9, 7), "fin", rot=[0, 0, -4 * s], inflate=-0.2, shape="arm")
        fore.boxb(16 * s, 19.5, -1, 7, 7, 8, "scales")                          # hand
        if s < 0:
            fore.boxb(16 * s, 21.5, -6.5, 5, 4, 4, "scales")                    # fingers round the shaft
            tri = m.bone("trident", f"{nm}_forearm", (16 * s, 23.5, -6.5), rotation=[-4, 0, -9])
            build_trident(tri, 16 * s, 23.5, -6.5)
        else:
            for k, x in enumerate((13.6, 16.0, 18.4)):
                fore.box((x * s, 17.5, -3.5), (2, 3, 2), "claw", rot=[-20, 0, 0])

        leg = m.bone(f"{nm}_leg", "root", (6 * s, 26, 0))
        leg.boxb(6 * s, 15, 0, 8, 12, 9, "scales")                              # thigh
        leg.box((6.2 * s, 21, -4.9), (7, 6, 1), "gold", rot=[-6, 0, 0], plate=True)  # thigh guard
        shin = m.bone(f"{nm}_shin", f"{nm}_leg", (6 * s, 15, 0))
        shin.boxb(6 * s, 4, 0.5, 7, 12, 7, "scales")
        shin.box((6 * s, 14.5, -3.6), (7, 4, 2), "shell", rot=[-10, 0, 0])      # knee shell
        shin.box((6 * s, 9.5, 5.4), (1, 10, 6), "fin", rot=[-12, 0, 0], inflate=-0.2, shape="calf")
        foot = m.bone(f"{nm}_foot", f"{nm}_shin", (6 * s, 4, 0.5))
        foot.boxb(6 * s, 0, -2, 9, 4, 12, "scales")
        foot.box((6 * s, 0.5, -9.0), (10, 1, 3), "fin", inflate=-0.05, shape="web", axis="y")
        for x in (3.0, 6.0, 9.0):
            foot.box((x * s, 1.0, -8.6), (2, 2, 2), "claw")
    return m


def build_trident(b, x, y, z):
    # shaft from the ground to above the head; grip at (x, y, z)
    b.box((x, 31.5, z), (2, 62, 2), "gold", shaft=True)
    b.box((x, 1.2, z), (3, 3, 3), "gold")                                       # pommel
    b.box((x, 62.5, z), (12, 2, 2), "gold")                                     # crossguard
    b.box((x, 62.5, z), (4, 4, 4), "gold", inflate=0.1)                         # collar
    b.box((x, 62.5, z - 2.1), (2, 2, 1), "pearl", inflate=0.2)                  # pearl
    b.box((x, 69.5, z), (2, 12, 2), "gold")                                     # centre prong
    b.spike((x, 75.0, z), (0, 1, 0), 4, 3, "gold", segs=[1.0], spin=45, tip=True)
    for sx in (-1, 1):
        b.box((x + 5 * sx, 67.0, z), (2, 8, 2), "gold")                         # side prongs
        b.spike((x + 5 * sx, 70.5, z), (0.45 * sx, 1, 0), 4, 2, "gold", segs=[1.0], tip=True)
        b.box((x + 6.6 * sx, 64.2, z), (2, 2, 2), "gold")                       # barb
    b.spike((x - 1.4, 58.0, z), (-0.8, 1, 0.3), 6, 2, "coral_pink", segs=[0.6, 0.4])
    b.spike((x + 1.4, 56.0, z), (0.9, 1, -0.2), 5, 2, "coral_orange", segs=[1.0])
    b.box((x, 54.5, z), (3, 3, 3), "coral_lump")

# =============================================================================== shaders


SCALE = palette("#0c2f30", "#103f3c", "#155247", "#1b6653", "#227b5f", "#2b926c", "#38a87a", "#4fbf8c", "#73d6a6")
BELLY = palette("#3c8d7c", "#4fa38c", "#66b99e", "#80ccb0", "#9fdcc3", "#c1ead7")
FIN = palette("#0d4d5e", "#11677a", "#178395", "#22a0ae", "#3dbcc3", "#67d6d4", "#9aeae2")
CORAL_P = palette("#5e1438", "#86204f", "#ad2e66", "#d2457f", "#ee6b9c", "#ff96bc", "#ffc4da")
CORAL_O = palette("#6a2509", "#953a12", "#c0541d", "#e2732b", "#f8963f", "#ffbb6b", "#ffdca3")
SHELL = palette("#4e2c26", "#79473a", "#a5664f", "#c98a6a", "#e2ae8c", "#f2cdb0", "#fde6d2", "#fff6ec")
GOLD = palette("#4a2d05", "#74490b", "#a06c14", "#c99222", "#e8b532", "#f9d553", "#fff08e", "#fffbd8")
BARN = palette("#2b2a27", "#4d4a44", "#77736a", "#a29d92", "#c9c4b8", "#ebe7dc")
KELP = palette("#16260d", "#213a12", "#2e5018", "#3f681f", "#548429", "#6c9f35")
GLOW = palette("#1fd8e8", "#5ff2ff", "#b8fdff", "#f2ffff")


def _th(ctx, seed):
    p = ctx.p
    return hash3(np.floor(p[:, 0] * 2 + 0.01), np.floor(p[:, 1] * 2 + 0.01), np.floor(p[:, 2] * 2 + 0.01), seed)


def _surface_uv(ctx):
    """A wrap-around 2D coordinate (u around the body, v up) in model units."""
    p = ctx.p
    f = ctx.face
    if f == "north":
        return p[:, 0], p[:, 1]
    if f == "south":
        return -p[:, 0] + 40, p[:, 1]
    if f == "west":
        return -p[:, 2] + 80, p[:, 1]
    if f == "east":
        return p[:, 2] + 120, p[:, 1]
    return p[:, 0], p[:, 2]


SCALE_TPL = np.array([
    [0.04, 0.20, 0.26, 0.20, 0.04, -0.06],
    [-0.02, 0.14, 0.18, 0.12, -0.02, -0.10],
    [-0.30, 0.04, 0.08, 0.02, -0.30, -0.04],
    [-0.06, -0.34, -0.34, -0.34, -0.06, 0.02],
])


def scale_pattern(ctx):
    """Pixel-template fish scales (6x4 texels, alternate rows offset by 3)."""
    u, v = _surface_uv(ctx)
    tu = np.floor(u * 2 + 1000).astype(int)
    tv = np.floor(-v * 2 + 1000).astype(int)           # rows counted downward
    row = tv // 4
    tu2 = tu + (row % 2) * 3
    col = tu2 // 6
    sv = SCALE_TPL[tv % 4, tu2 % 6]
    rim = (tv % 4) == 3
    cid = hash3(row, col, 0, 9)
    return sv, rim, cid


def shade_scales(ctx, belly=False):
    p = ctx.p
    sv, rim, cid = scale_pattern(ctx)
    v = 0.5 + sv * 1.1 + (cid - 0.5) * 0.1 + (fbm(p, 0.12, 3, 4) - 0.5) * 0.38
    v += edge_term(ctx, 0.12, 0.12, 0.04) + vgrad(ctx, 0.12) - ctx.ao * 0.55
    v += 0.06 * max(0, ctx.nw[1]) - 0.12 * max(0, -ctx.nw[1])
    v += -0.06 * max(0, ctx.nw[2]) + 0.03 * max(0, -ctx.nw[2])
    rgb = ramp(SCALE, v)
    glow = np.zeros(ctx.N, dtype=bool)
    if ctx.face == "north":
        half = 4.6 if not belly else 5.6
        bm = np.abs(p[:, 0]) < half - 0.6 * np.abs(np.sin(p[:, 1] * 0.35))
        seg = np.mod(p[:, 1] * 2, 6) < 1
        bv = 0.62 - seg * 0.3 + (fbm(p, 0.2, 2, 6) - 0.5) * 0.3 - ctx.ao * 0.5 + vgrad(ctx, 0.1)
        bv += (np.mod(p[:, 1] * 2, 6) == 5) * 0.1
        rgb[bm] = ramp(BELLY, bv[bm])
        edge = bm & ~(np.abs(p[:, 0]) < half - 0.5 - 0.6 * np.abs(np.sin(p[:, 1] * 0.35)))
        rgb[edge] = rgb[edge] * 0.7
    # mottled darker stripes across the back
    if ctx.face in ("south", "up"):
        st = (np.sin(p[:, 1] * 0.9 + fbm(p, 0.15, 2, 3) * 5) > 0.55)
        rgb[st] = rgb[st] * 0.72
    # algae / weathering patches
    alg = fbm(p, 0.2, 3, 21) > 0.7
    rgb[alg] = rgb[alg] * 0.6 + np.array([40, 70, 30]) * 0.4
    if ctx.params.get("gills") and ctx.face in ("west", "east"):
        # three glowing gill slits curving down the side, near the front
        zf = (p[:, 2] - ctx.lo[2]) / (ctx.hi[2] - ctx.lo[2])
        yf = (p[:, 1] - ctx.lo[1]) / (ctx.hi[1] - ctx.lo[1])
        g = np.zeros(ctx.N, bool)
        for k in range(3):
            x0 = 0.22 + k * 0.15
            curve = x0 + 0.08 * np.sin((yf - 0.2) * 3.0)
            g |= (np.abs(zf - curve) < 0.035) & (yf > 0.25) & (yf < 0.85)
        halo = np.zeros(ctx.N, bool)
        for k in range(3):
            x0 = 0.22 + k * 0.15
            curve = x0 + 0.08 * np.sin((yf - 0.2) * 3.0)
            halo |= (np.abs(zf - curve) < 0.075) & (yf > 0.22) & (yf < 0.88)
        halo &= ~g
        rgb[halo] = rgb[halo] * 0.4 + np.array([30, 170, 170]) * 0.6
        rgb[g] = GLOW[1]
        glow = g | halo
    return rgb, 255, glow


def fin_mask(shape, a, b):
    """a along the fin length (0 front/base .. 1 back/tip), b up (0 base .. 1 top)."""
    if shape == "crest":
        # rises toward the back with ray spikes along the top
        top = 0.35 + 0.6 * np.clip(a * 1.25, 0, 1) - 0.18 * np.abs(np.sin(a * math.pi * 4.5)) ** 0.6
        return (b < top) & (a > 0.02)
    if shape == "tail":
        # forked caudal fin; a = along the tail (base->tip), b = across
        lobe = np.abs(b - 0.5) * 2
        edge = 0.35 + 0.65 * lobe ** 1.4 - 0.12 * np.abs(np.sin(lobe * 6))
        return a < edge + 0.25 * (1 - lobe)
    if shape == "ear":
        top = 0.25 + 0.7 * a - 0.15 * np.abs(np.sin(a * math.pi * 3)) ** 0.6
        return (b < top + 0.1) & (b > 0.05)
    if shape == "arm" or shape == "calf":
        top = 1.0 - 0.75 * a - 0.12 * np.abs(np.sin(a * math.pi * 3.5)) ** 0.6
        return (b < top) | (a < 0.12)
    if shape == "barbel":
        return (b > 0.25 + 0.6 * a)
    if shape == "dorsal":
        # a = along z (spine -> back edge), b = up the spine; spiky trailing edge
        edge = 0.55 + 0.45 * np.abs(np.sin(b * math.pi * 3.0)) ** 0.5
        return a < edge
    if shape == "web":
        return np.ones_like(a, dtype=bool)
    if shape == "flap":
        return np.ones_like(a, dtype=bool)
    return np.ones_like(a, dtype=bool)


def shade_fin(ctx):
    p = ctx.p
    shape = ctx.params.get("shape", "flap")
    axis = ctx.params.get("axis", "z")
    lo, hi = ctx.lo, ctx.hi
    if axis == "z":
        a = (p[:, 2] - lo[2]) / (hi[2] - lo[2])
    elif axis == "x":
        a = (p[:, 0] - lo[0]) / (hi[0] - lo[0])
    else:
        a = (p[:, 2] - lo[2]) / (hi[2] - lo[2])
    b = (p[:, 1] - lo[1]) / (hi[1] - lo[1]) if axis != "y" else (p[:, 0] - lo[0]) / (hi[0] - lo[0])
    if shape == "tail":
        a, b = 1 - (p[:, 1] - lo[1]) / (hi[1] - lo[1]), (p[:, 2] - lo[2]) / (hi[2] - lo[2])
    if shape in ("barbel",):
        a, b = (p[:, 2] - lo[2]) / (hi[2] - lo[2]), 1 - (p[:, 1] - lo[1]) / (hi[1] - lo[1])
    if shape in ("arm", "calf"):
        a, b = (p[:, 2] - lo[2]) / (hi[2] - lo[2]), (p[:, 1] - lo[1]) / (hi[1] - lo[1])
    inside = fin_mask(shape, a, b)
    # membrane with darker rays fanning from the base
    ang = np.arctan2(b + 0.15, a + 0.25)
    rays = np.abs(np.sin(ang * 16)) < 0.22
    v = 0.45 + b * 0.25 + (fbm(p, 0.3, 2, 5) - 0.5) * 0.3
    v -= rays * 0.22
    v += edge_term(ctx, 0.15, 0.08, 0.0) - ctx.ao * 0.4
    rgb = ramp(FIN, v)
    # luminous edge along the silhouette (approximate with a band near the mask border)
    alpha = np.where(inside, 255, 0)
    glow = np.zeros(ctx.N, dtype=bool)
    if shape in ("crest", "tail", "ear"):
        # faint bioluminescent spots
        spots = (_th(ctx, 3) > 0.965) & inside
        rgb[spots] = GLOW[1]
        glow = spots
    return rgb, alpha, glow


def shade_coral(ctx, pal=CORAL_P, lump=False):
    p = ctx.p
    f1, f2, cid = worley(p, 0.9 if not lump else 0.7, 17)
    v = 0.5 + (fbm(p, 0.4, 2, 2) - 0.5) * 0.35
    pores = f1 < 0.22
    v -= pores * 0.3
    if lump:
        # brain-coral meanders
        mz = np.abs(np.sin(p[:, 0] * 1.7 + np.sin(p[:, 2] * 1.3 + p[:, 1]) * 2.0 + p[:, 1] * 0.9)) < 0.3
        v = 0.55 - mz * 0.3 + (fbm(p, 0.4, 2, 7) - 0.5) * 0.3
    else:
        prm = ctx.params
        if "spike_base" in prm:
            prog = np.clip((p[:, 1] - prm["spike_base"][1]) / prm["spike_len"], 0, 1)
            v += prog * 0.3 - 0.1
    v += edge_term(ctx, 0.15, 0.1, 0.04) - ctx.ao * 0.45
    rgb = ramp(pal, v)
    tips = (_th(ctx, 8) > 0.93)
    rgb[tips] = ramp(pal, np.full(tips.sum(), 0.92))
    return rgb, 255, False


def shade_shell(ctx):
    p = ctx.p
    hx = 23.0 * np.sign(np.mean(p[:, 0])) if abs(np.mean(p[:, 0])) > 8 else np.mean(p[:, 0])
    H = np.array([hx, 44.0, 0.0]) if abs(np.mean(p[:, 0])) > 8 else np.array([np.mean(p[:, 0]), np.min(p[:, 1]) - 2, 0])
    d = p - H
    ang = np.arctan2(d[:, 2], np.sqrt(d[:, 0] ** 2 + d[:, 1] ** 2) + 1e-6)
    ribs = np.sin(ang * 13.0)
    dist = np.sqrt((d ** 2).sum(1))
    rings = np.abs(np.sin(dist * 1.5)) < 0.18
    v = 0.52 + (ribs > 0.25) * 0.2 - (ribs < -0.55) * 0.16 - rings * 0.12 + (fbm(p, 0.25, 2, 3) - 0.5) * 0.25
    v += edge_term(ctx, 0.22, 0.18, 0.06) + vgrad(ctx, 0.1) - ctx.ao * 0.55
    v += 0.06 * max(0, ctx.nw[1])
    rgb = ramp(SHELL, v)
    band = np.mod(dist, 7.0) < 2.2
    rgb[band] = rgb[band] * 0.72 + np.array([240, 120, 120]) * 0.28
    band2 = (np.mod(dist, 7.0) > 4.6) & (np.mod(dist, 7.0) < 5.6)
    rgb[band2] = rgb[band2] * 0.75 + np.array([250, 150, 70]) * 0.25
    return rgb, 255, False


def shade_gold(ctx):
    p = ctx.p
    prm = ctx.params
    v = 0.55 + (fbm(p, 0.3, 2, 11) - 0.5) * 0.25 + vgrad(ctx, 0.2)
    if ctx.face not in ("up", "down"):
        v += np.where(ctx.s < 0.35, 0.18, np.where(ctx.s > 0.75, -0.15, 0.0))       # cylindrical sheen
    if prm.get("shaft"):
        wrap = (np.mod(p[:, 1], 6.0) < 1.0)
        v -= wrap * 0.25
        v += (np.mod(p[:, 1], 6.0) > 5.0) * 0.15
    if prm.get("plate"):
        v += ((ctx.j < 2) | (ctx.i < 2) | (ctx.i >= ctx.tw - 2)) * 0.15
        sp = (np.abs(ctx.s - 0.5) < 0.12) & (np.abs(ctx.t - 0.5) < 0.18)
        v -= sp * 0.25
    if prm.get("bracer"):
        band = (ctx.j < 2) | (ctx.j >= ctx.th - 2)
        v += band * 0.2
        wave = np.abs(np.sin(p[:, 0] * 1.4 + p[:, 2] * 1.4) * 1.2 - ((p[:, 1] - ctx.lo[1]) - 2.5)) < 0.35
        v -= wave * 0.3
    v += edge_term(ctx, 0.22, 0.18, 0.05) - ctx.ao * 0.5
    rgb = ramp(GOLD, v)
    sp = _th(ctx, 4) > 0.97
    rgb[sp] = GOLD[-1]
    if prm.get("tip"):
        prog = np.clip((p[:, 1] - prm["spike_base"][1]) / prm["spike_len"], 0, 1)
        rgb[prog > 0.6] = GOLD[-2]
    return rgb, 255, False


def shade_barnacle(ctx):
    p = ctx.p
    v = 0.55 + (fbm(p, 0.8, 2, 5) - 0.5) * 0.5 + edge_term(ctx, 0.2, 0.2, 0.1)
    rgb = ramp(BARN, v)
    if ctx.face == "up":
        cx = (ctx.s - 0.5)
        cy = (ctx.t - 0.5)
        hole = (np.abs(cx) < 0.2) & (np.abs(cy) < 0.2)
        rgb[hole] = np.array([22, 24, 26])
    else:
        ridges = (ctx.i % 2 == 0)
        rgb[ridges] = rgb[ridges] * 0.85
    return rgb, 255, False


def shade_kelp(ctx):
    p = ctx.p
    # vertical strands with a ragged, cut-out lower fringe
    strand = np.floor((p[:, 0] + p[:, 2]) * 1.0)
    h = hash3(strand, 0, 0, 13)
    yb = (p[:, 1] - ctx.lo[1]) / (ctx.hi[1] - ctx.lo[1])
    cut = yb < (0.05 + 0.35 * h)
    v = 0.4 + (h - 0.5) * 0.4 + yb * 0.25 + ((p[:, 0] * 2) % 2 < 1) * 0.08 - ctx.ao * 0.4
    rgb = ramp(KELP, v)
    alpha = np.where(cut & (ctx.face not in ("up",)), 0, 255)
    return rgb, alpha, False


def shade_eye(ctx):
    v = 0.45 + (ctx.face == "north") * 0.4 - (np.abs(ctx.s - 0.5) > 0.3) * 0.25
    return ramp(GLOW, v), 255, True


def shade_pearl(ctx):
    v = 0.5 + (ctx.s < 0.5) * 0.25 + (ctx.t < 0.5) * 0.2
    return ramp(GLOW, v), 255, True


def shade_claw(ctx):
    v = 0.6 - ctx.t * 0.4 + edge_term(ctx, 0.2)
    return ramp(BARN, v), 255, False


def shade_tooth(ctx):
    return ramp(BARN, np.full(ctx.N, 0.85) - ctx.t * 0.2), 255, False


SHADERS = {
    "scales": shade_scales,
    "belly_scales": lambda c: shade_scales(c, belly=True),
    "fin": shade_fin,
    "coral_pink": shade_coral,
    "coral_orange": lambda c: shade_coral(c, CORAL_O),
    "coral_lump": lambda c: shade_coral(c, CORAL_P, lump=True),
    "coral_lump_o": lambda c: shade_coral(c, CORAL_O, lump=True),
    "shell": shade_shell,
    "gold": shade_gold,
    "barnacle": shade_barnacle,
    "kelp": shade_kelp,
    "eye": shade_eye,
    "pearl": shade_pearl,
    "claw": shade_claw,
    "tooth": shade_tooth,
}

# =============================================================================== animations


def _breath(c, T):
    w = lambda t, ph=0.0: math.sin(TAU * t / T + ph)
    c.f("chest", "rotation", lambda t: (-1.4 * w(t), 0, 0.6 * w(t, 1.2)))
    c.f("chest", "position", lambda t: (0, 0.3 * w(t), 0))
    c.f("neck", "rotation", lambda t: (1.2 * w(t, 0.8), 2.0 * w(t, 0.2), 0))
    c.f("jaw", "rotation", lambda t: (2.0 + 2.0 * w(t, -0.5), 0, 0))
    c.f("tail", "rotation", lambda t: (2 * w(t, 0.5), 7 * w(t), 0))
    c.f("tail_tip", "rotation", lambda t: (3 * w(t, 1.0), 11 * w(t, -1.0), 0))
    return w


def anim_idle():
    T = 3.0
    c = Clip("idle", T, loop=True)
    w = _breath(c, T)
    c.f("right_arm", "rotation", lambda t: (1.5 * w(t, 0.6), 0, 1.2 * w(t, 0.3)))
    c.f("left_arm", "rotation", lambda t: (2.2 * w(t, 0.9), 0, -1.6 * w(t, 0.3)))
    c.f("left_forearm", "rotation", lambda t: (-3 * w(t, 1.4), 0, 0))
    c.f("trident", "rotation", lambda t: (0.8 * w(t, 1.0), 0, 0.8 * w(t, 2.0)))
    return c


def anim_walk():
    T = 1.6
    c = Clip("walk", T, loop=True)
    ph = lambda t: TAU * t / T
    sn = lambda t: math.sin(ph(t))
    c.f("right_leg", "rotation", lambda t: (-26 * sn(t), 0, 0))
    c.f("left_leg", "rotation", lambda t: (26 * sn(t), 0, 0))
    kr = lambda t: 34 * max(0.0, math.cos(ph(t))) ** 1.3
    kl = lambda t: 34 * max(0.0, -math.cos(ph(t))) ** 1.3
    c.f("right_shin", "rotation", lambda t: (kr(t), 0, 0))
    c.f("left_shin", "rotation", lambda t: (kl(t), 0, 0))
    c.f("right_foot", "rotation", lambda t: (26 * sn(t) - kr(t), 0, 0))
    c.f("left_foot", "rotation", lambda t: (-26 * sn(t) - kl(t), 0, 0))
    c.f("body", "position", lambda t: (0, 0.6 - 2.0 * sn(t) ** 4, 0))
    c.f("body", "rotation", lambda t: (0, 6 * sn(t), -3 * sn(t)))
    c.f("chest", "rotation", lambda t: (3 + 2 * sn(t) ** 4, -8 * sn(t), 2 * sn(t)))
    c.f("right_arm", "rotation", lambda t: (8 * sn(t - 0.25), 0, 2))               # trident arm: restrained
    c.f("left_arm", "rotation", lambda t: (-22 * sn(t - 0.25), 0, -2 - 2 * sn(t) ** 2))
    c.f("left_forearm", "rotation", lambda t: (-10 - 10 * max(0.0, math.sin(ph(t) - 0.6)), 0, 0))
    c.f("right_forearm", "rotation", lambda t: (-4 * sn(t), 0, 0))
    c.f("trident", "rotation", lambda t: (-6 * sn(t - 0.4), 0, 0))
    c.f("neck", "rotation", lambda t: (-2 - 2 * sn(t) ** 4, 4 * sn(t), 2 * sn(t)))
    c.f("tail", "rotation", lambda t: (3 * math.sin(2 * ph(t)), -14 * sn(t - 0.5), 0))
    c.f("tail_tip", "rotation", lambda t: (4 * math.sin(2 * ph(t) - 0.6), -20 * sn(t - 1.2), 0))
    c.f("jaw", "rotation", lambda t: (2 + 2 * math.sin(2 * ph(t)), 0, 0))
    return c


def anim_trident_throw():
    c = Clip("attack.trident_throw", 1.5)
    c.rot("right_arm", [(0, (0, 0, 0)), (0.55, (-158, 0, 18), "io"), (0.75, (-62, 0, 4), "snap"),
                        (0.95, (-40, 0, 0), "out"), (1.5, (0, 0, 0), "io")])
    c.rot("right_forearm", [(0, (0, 0, 0)), (0.55, (-34, 0, 0)), (0.75, (0, 0, 0), "snap"), (1.5, (0, 0, 0))])
    c.rot("trident", [(0, (0, 0, 0)), (0.55, (-54, 0, 9), "io"), (0.75, (-54, 0, 9)), (1.15, (0, 0, 0), "hold"),
                      (1.5, (0, 0, 0))])
    # vanishes on release, re-forms from water in the hand
    c.scl("trident", [(0, (1, 1, 1)), (0.74, (1, 1, 1)), (0.76, (0.01, 0.01, 0.01), "lin"), (1.12, (0.01, 0.01, 0.01)),
                      (1.38, (1.08, 1.08, 1.08), "out"), (1.5, (1, 1, 1))])
    c.rot("left_arm", [(0, (0, 0, 0)), (0.55, (-55, 0, -12)), (0.75, (30, 0, -20), "snap"), (1.0, (25, 0, -18)),
                       (1.5, (0, 0, 0))])
    c.rot("left_forearm", [(0, (0, 0, 0)), (0.55, (-30, 0, 0)), (0.75, (-10, 0, 0)), (1.5, (0, 0, 0))])
    c.rot("chest", [(0, (0, 0, 0)), (0.55, (-14, 26, -4), "io"), (0.75, (16, -22, 2), "snap"),
                    (1.0, (12, -16, 0)), (1.5, (0, 0, 0))])
    c.rot("body", [(0, (0, 0, 0)), (0.55, (-3, 10, 0)), (0.75, (5, -10, 0), "snap"), (1.5, (0, 0, 0))])
    c.rot("neck", [(0, (0, 0, 0)), (0.55, (-6, -14, 0)), (0.75, (-10, 14, 0), "snap"), (1.5, (0, 0, 0))])
    c.rot("jaw", [(0, (0, 0, 0)), (0.6, (8, 0, 0)), (0.75, (26, 0, 0), "snap"), (1.1, (8, 0, 0)), (1.5, (0, 0, 0))])
    c.rot("right_leg", [(0, (0, 0, 0)), (0.55, (8, 0, 0)), (0.75, (-22, 0, 0), "snap"), (1.0, (-20, 0, 0)), (1.5, (0, 0, 0))])
    c.rot("right_shin", [(0, (0, 0, 0)), (0.75, (14, 0, 0), "snap"), (1.0, (14, 0, 0)), (1.5, (0, 0, 0))])
    c.rot("right_foot", [(0, (0, 0, 0)), (0.55, (-8, 0, 0)), (0.75, (8, 0, 0), "snap"), (1.0, (6, 0, 0)), (1.5, (0, 0, 0))])
    c.rot("left_leg", [(0, (0, 0, 0)), (0.55, (-6, 0, 0)), (0.75, (14, 0, 0), "snap"), (1.0, (12, 0, 0)), (1.5, (0, 0, 0))])
    c.rot("left_foot", [(0, (0, 0, 0)), (0.55, (6, 0, 0)), (0.75, (-14, 0, 0), "snap"), (1.0, (-12, 0, 0)), (1.5, (0, 0, 0))])
    drop = tl.Track([(0, 0), (0.55, 1.0), (0.75, 3.0, "snap"), (1.0, 3.0), (1.5, 0)])
    c.f("body", "position", lambda t: (0, -float(drop(t)), 0))
    c.rot("tail", [(0, (0, 0, 0)), (0.55, (0, -18, 0)), (0.75, (8, 22, 0), "snap"), (1.5, (0, 0, 0))])
    c.rot("tail_tip", [(0, (0, 0, 0)), (0.6, (0, -24, 0)), (0.85, (6, 28, 0), "snap"), (1.5, (0, 0, 0))])
    return c


def anim_tidal_wave():
    c = Clip("attack.tidal_wave", 2.0)
    # gather both arms low on the right, then sweep them across and up (0.8 s)
    c.rot("right_arm", [(0, (0, 0, 0)), (0.5, (-30, 0, 30), "io"), (0.8, (-105, 0, -30), "snap"),
                        (1.2, (-100, 0, -28)), (2.0, (0, 0, 0), "io")])
    c.rot("left_arm", [(0, (0, 0, 0)), (0.5, (-40, 0, 40), "io"), (0.8, (-110, 0, -55), "snap"),
                       (1.2, (-104, 0, -52)), (2.0, (0, 0, 0), "io")])
    c.rot("right_forearm", [(0, (0, 0, 0)), (0.5, (-35, 0, 0)), (0.8, (-10, 0, 0), "snap"), (2.0, (0, 0, 0))])
    c.rot("left_forearm", [(0, (0, 0, 0)), (0.5, (-45, 0, 0)), (0.8, (-12, 0, 0), "snap"), (2.0, (0, 0, 0))])
    c.rot("trident", [(0, (0, 0, 0)), (0.5, (30, 0, 0)), (0.8, (60, 0, 0), "snap"), (1.2, (58, 0, 0)), (2.0, (0, 0, 0))])
    c.rot("chest", [(0, (0, 0, 0)), (0.5, (14, 38, 6), "io"), (0.8, (-12, -34, -4), "snap"), (1.2, (-10, -30, -4)),
                    (2.0, (0, 0, 0), "io")])
    c.rot("body", [(0, (0, 0, 0)), (0.5, (4, 14, 0)), (0.8, (-4, -14, 0), "snap"), (2.0, (0, 0, 0))])
    c.rot("neck", [(0, (0, 0, 0)), (0.5, (6, -16, 0)), (0.8, (-14, 12, 0), "snap"), (1.2, (-12, 10, 0)), (2.0, (0, 0, 0))])
    c.rot("jaw", [(0, (0, 0, 0)), (0.5, (6, 0, 0)), (0.8, (30, 0, 0), "snap"), (1.3, (22, 0, 0)), (2.0, (0, 0, 0))])
    drop = tl.Track([(0, 0), (0.5, 5.0, "io"), (0.8, -0.5, "snap"), (1.2, 0), (2.0, 0)])
    legs_for_drop(c, lambda t: max(0.0, float(drop(t))), thigh=THIGH, shin=SHIN)
    c.f("body", "position", lambda t: (0, max(0.0, -float(drop(t))), 0))
    c.rot("tail", [(0, (0, 0, 0)), (0.5, (0, 25, 0)), (0.8, (10, -30, 0), "snap"), (2.0, (0, 0, 0))])
    c.rot("tail_tip", [(0, (0, 0, 0)), (0.55, (0, 30, 0)), (0.9, (8, -35, 0), "snap"), (2.0, (0, 0, 0))])
    return c


def anim_whirlpool():
    c = Clip("attack.whirlpool", 3.0)
    e = lambda t: env(t, 0.0, 0.5, 2.5, 3.0)
    om = lambda t: TAU * 2 * (t - 0.5) / 2.0                       # two full circles over 2 s
    # arms reach forward and circle; trident stirs like a ladle
    c.f("right_arm", "rotation", lambda t: (-70 * e(t) + 28 * math.sin(om(t)) * e(t), 0, 22 * math.cos(om(t)) * e(t)))
    c.f("left_arm", "rotation", lambda t: (-70 * e(t) + 28 * math.sin(om(t) + math.pi) * e(t), 0,
                                           22 * math.cos(om(t) + math.pi) * e(t)))
    c.f("right_forearm", "rotation", lambda t: (-20 * e(t), 0, 0))
    c.f("left_forearm", "rotation", lambda t: (-20 * e(t), 0, 0))
    c.f("trident", "rotation", lambda t: (-118 * e(t), 0, 9 * e(t)))
    c.f("chest", "rotation", lambda t: (8 * e(t), 18 * math.sin(om(t)) * e(t), 4 * math.cos(om(t)) * e(t)))
    c.f("body", "rotation", lambda t: (0, 8 * math.sin(om(t) - 0.4) * e(t), 0))
    c.f("neck", "rotation", lambda t: (6 * e(t), -10 * math.sin(om(t)) * e(t), 0))
    c.f("jaw", "rotation", lambda t: (18 * e(t), 0, 0))
    c.f("tail", "rotation", lambda t: (0, -20 * math.sin(om(t) - 0.6) * e(t), 0))
    c.f("tail_tip", "rotation", lambda t: (0, -26 * math.sin(om(t) - 1.2) * e(t), 0))
    legs_for_drop(c, lambda t: 3.0 * e(t), thigh=THIGH, shin=SHIN, spread=0.0)
    return c


def anim_water_jet():
    c = Clip("attack.water_jet", 2.0)
    # flip the trident to point forward, brace with the left hand, fire 0.6-1.6
    c.rot("right_arm", [(0, (0, 0, 0)), (0.45, (-60, 0, 10), "io"), (0.6, (-88, 0, -6), "snap"), (1.6, (-86, 0, -6)),
                        (2.0, (0, 0, 0), "io")])
    c.rot("right_forearm", [(0, (0, 0, 0)), (0.45, (-40, 0, 0)), (0.6, (-2, 0, 0), "snap"), (1.6, (0, 0, 0)), (2.0, (0, 0, 0))])
    c.rot("trident", [(0, (0, 0, 0)), (0.45, (150, 0, 0), "io"), (0.6, (178, 0, -7), "snap"), (1.6, (178, 0, -7)),
                      (2.0, (0, 0, 0), "io")])
    c.rot("left_arm", [(0, (0, 0, 0)), (0.45, (-40, 0, 10)), (0.6, (-70, 0, 26), "snap"), (1.6, (-68, 0, 26)),
                       (2.0, (0, 0, 0))])
    c.rot("left_forearm", [(0, (0, 0, 0)), (0.45, (-30, 0, 0)), (0.6, (-28, 0, 0)), (2.0, (0, 0, 0))])
    c.rot("chest", [(0, (0, 0, 0)), (0.45, (-8, 16, 0)), (0.6, (10, 10, 0), "snap"), (1.6, (10, 10, 0)), (2.0, (0, 0, 0))])
    c.f("chest", "rotation", lambda t: (shake(t, 15, 1.2) * env(t, 0.6, 0.65, 1.5, 1.6), shake(t, 11, 1.0, 2) * env(t, 0.6, 0.65, 1.5, 1.6), 0))
    c.f("right_arm", "rotation", lambda t: (shake(t, 19, 1.5, 4) * env(t, 0.6, 0.65, 1.5, 1.6), 0, 0))
    c.rot("neck", [(0, (0, 0, 0)), (0.6, (-4, -10, 0), "snap"), (1.6, (-4, -10, 0)), (2.0, (0, 0, 0))])
    c.rot("jaw", [(0, (0, 0, 0)), (0.6, (16, 0, 0), "snap"), (1.6, (14, 0, 0)), (2.0, (0, 0, 0))])
    c.rot("right_leg", [(0, (0, 0, 0)), (0.6, (-18, 0, 0), "snap"), (1.6, (-18, 0, 0)), (2.0, (0, 0, 0))])
    c.rot("right_foot", [(0, (0, 0, 0)), (0.6, (18, 0, 0), "snap"), (1.6, (18, 0, 0)), (2.0, (0, 0, 0))])
    c.rot("left_leg", [(0, (0, 0, 0)), (0.6, (14, 0, 0), "snap"), (1.6, (14, 0, 0)), (2.0, (0, 0, 0))])
    c.rot("left_foot", [(0, (0, 0, 0)), (0.6, (-14, 0, 0), "snap"), (1.6, (-14, 0, 0)), (2.0, (0, 0, 0))])
    c.pos("body", [(0, (0, 0, 0)), (0.6, (0, -1.5, 0), "snap"), (1.6, (0, -1.5, 0)), (2.0, (0, 0, 0))])
    c.f("body", "position", lambda t: (0, 0, 0.8 * env(t, 0.6, 0.7, 1.5, 1.7)))           # recoil
    c.rot("tail", [(0, (0, 0, 0)), (0.6, (-10, 0, 0), "snap"), (1.6, (-8, 0, 0)), (2.0, (0, 0, 0))])
    return c


def anim_phase():
    c = Clip("phase", 2.0)
    c.rot("chest", [(0, (0, 0, 0)), (0.45, (20, 0, 0), "io"), (0.75, (-22, 0, 0), "snap"), (1.5, (-20, 0, 0)), (2.0, (0, 0, 0))])
    c.rot("neck", [(0, (0, 0, 0)), (0.45, (12, 0, 0)), (0.75, (-30, 0, 0), "snap"), (1.5, (-28, 0, 0)), (2.0, (0, 0, 0))])
    c.rot("jaw", [(0, (0, 0, 0)), (0.45, (4, 0, 0)), (0.7, (42, 0, 0), "snap"), (1.55, (40, 0, 0)), (2.0, (0, 0, 0))])
    # trident raised to the sky, free arm flung out
    c.rot("right_arm", [(0, (0, 0, 0)), (0.45, (-20, 0, 10)), (0.75, (-168, 0, 8), "snap"), (1.5, (-166, 0, 8)),
                        (2.0, (0, 0, 0), "io")])
    c.rot("right_forearm", [(0, (0, 0, 0)), (0.45, (-40, 0, 0)), (0.75, (-6, 0, 0), "snap"), (1.5, (-6, 0, 0)), (2.0, (0, 0, 0))])
    c.rot("trident", [(0, (0, 0, 0)), (0.45, (60, 0, 0)), (0.75, (172, 0, -6), "snap"), (1.5, (172, 0, -6)), (2.0, (0, 0, 0), "io")])
    c.rot("left_arm", [(0, (0, 0, 0)), (0.45, (-20, 0, 10)), (0.75, (-40, 0, -80), "snap"), (1.5, (-38, 0, -76)), (2.0, (0, 0, 0))])
    c.rot("left_forearm", [(0, (0, 0, 0)), (0.45, (-60, 0, 0)), (0.75, (-30, 0, 0), "snap"), (2.0, (0, 0, 0))])
    trem = lambda t: env(t, 0.75, 0.8, 1.45, 1.6)
    c.f("chest", "rotation", lambda t: (shake(t, 20, 1.4) * trem(t), shake(t, 17, 1.1, 3) * trem(t), 0))
    c.f("neck", "rotation", lambda t: (shake(t, 23, 1.4, 5) * trem(t), 0, shake(t, 19, 1.0, 1) * trem(t)))
    c.rot("tail", [(0, (0, 0, 0)), (0.45, (-10, 0, 0)), (0.75, (20, 0, 0), "snap"), (1.5, (18, 0, 0)), (2.0, (0, 0, 0))])
    c.f("tail_tip", "rotation", lambda t: (0, 20 * math.sin(TAU * 3 * t) * trem(t), 0))
    drop = tl.Track([(0, 0), (0.45, 4.0), (0.75, 0.0, "snap"), (2.0, 0.0)])
    legs_for_drop(c, lambda t: float(drop(t)), thigh=THIGH, shin=SHIN)
    return c


def anim_death():
    c = Clip("death", 2.8, loop="hold")
    # staggers, drops the trident, falls to its knees, topples backward and sinks away like water
    c.rot("chest", [(0, (0, 0, 0)), (0.35, (16, 0, 0), "out"), (1.1, (-8, 0, 6)), (1.8, (-28, 0, 10), "in"), (2.8, (-28, 0, 10))])
    c.rot("neck", [(0, (0, 0, 0)), (0.35, (18, 0, 0), "out"), (1.1, (-14, 0, 0)), (1.8, (-30, 0, -8), "in"), (2.8, (-30, 0, -8))])
    c.rot("jaw", [(0, (0, 0, 0)), (0.35, (30, 0, 0), "out"), (1.1, (20, 0, 0)), (1.8, (36, 0, 0)), (2.8, (36, 0, 0))])
    c.rot("right_arm", [(0, (0, 0, 0)), (0.35, (-30, 0, 20), "out"), (1.1, (10, 0, 30)), (1.8, (-20, 0, 50), "in"), (2.8, (-20, 0, 50))])
    c.rot("left_arm", [(0, (0, 0, 0)), (0.35, (-40, 0, -25), "out"), (1.1, (10, 0, -30)), (1.8, (-20, 0, -50), "in"), (2.8, (-20, 0, -50))])
    c.rot("trident", [(0, (0, 0, 0)), (0.35, (0, 0, -10)), (1.0, (-75, 0, -30), "in"), (2.8, (-75, 0, -30))])
    c.pos("trident", [(0, (0, 0, 0)), (0.35, (0, 0, 0)), (1.0, (-4, -16, -6), "in"), (2.8, (-4, -16, -6))])
    c.scl("trident", [(0, (1, 1, 1)), (0.95, (1, 1, 1)), (1.35, (0.01, 0.01, 0.01), "in"), (2.8, (0.01, 0.01, 0.01))])
    drop = tl.Track([(0, 0), (0.35, 1.0, "out"), (1.1, 11.0, "io"), (2.8, 11.0)])
    legs_for_drop(c, lambda t: float(drop(t)), thigh=THIGH, shin=SHIN)
    c.rot("body", [(0, (0, 0, 0)), (1.1, (-4, 0, 0)), (1.8, (-22, 0, 0), "in"), (2.8, (-22, 0, 0))])
    c.rot("tail", [(0, (0, 0, 0)), (1.0, (-20, 0, 0)), (1.8, (-30, 0, 0)), (2.8, (-30, 0, 0))])
    sink = lambda t: tl.ease("in", (t - 1.8) / 1.0) if t > 1.8 else 0.0
    c.f("root", "position", lambda t: (0, -22 * sink(t), 0))
    c.f("root", "scale", lambda t: (1 - 0.35 * sink(t), 1 - 0.6 * sink(t), 1 - 0.35 * sink(t)))
    return c


def clips():
    return [anim_idle(), anim_walk(), anim_trident_throw(), anim_tidal_wave(), anim_whirlpool(), anim_water_jet(),
            anim_phase(), anim_death()]


POSES = [
    ("idle", [0.0, 1.5]),
    ("walk", [0.0, 0.4, 0.8, 1.2]),
    ("attack.trident_throw", [0.55, 0.75, 1.0, 1.35]),
    ("attack.tidal_wave", [0.5, 0.8, 1.2]),
    ("attack.whirlpool", [0.75, 1.25, 1.75]),
    ("attack.water_jet", [0.45, 0.8, 1.4]),
    ("phase", [0.45, 0.8, 1.2]),
    ("death", [0.35, 1.1, 1.9, 2.5]),
]


def main():
    m = build_model()
    geo, rgba, glow, anims = tl.build(NAME, m, SHADERS, clips(), visible=(5, 6, 2.5))
    if "--preview" in sys.argv:
        sel = POSES if "--all" in sys.argv else POSES[:3]
        for p in tl.previews(NAME, geo, rgba, glow, anims, HITBOX, sel, frame=(120, 90)):
            print("preview", p)


if __name__ == "__main__":
    main()
