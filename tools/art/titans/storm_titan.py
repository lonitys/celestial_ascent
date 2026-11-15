"""Storm Titan: a floating slate storm-stone colossus with a wild cloud mane, glowing lightning
veins, copper bracers and a spinning vortex of cloud rings instead of legs.

Run: python storm_titan.py [--preview [--all]]
"""
import math
import sys

import numpy as np

import titanlib as tl
from titanlib import (Clip, edge_term, env, fbm, hash3, palette, ramp, shake, vgrad, worley, vnoise)
from anim_helpers import TAU

NAME = "storm_titan"
HITBOX = (2.2, 4.5)
RINGS = [  # (bone, pivot y, radius, puffs, puff size, tilt)
    ("vortex_ring1", 24.0, 10.5, 8, (10, 5, 5), 6),
    ("vortex_ring2", 17.0, 7.8, 7, (8, 4, 4), -5),
    ("vortex_ring3", 10.5, 5.2, 6, (6, 3, 4), 7),
    ("vortex_ring4", 5.0, 3.2, 4, (5, 3, 3), -6),
]

# =============================================================================== geometry


def build_model():
    m = tl.Model(NAME)
    body = m.bone("body", "root", (0, 30, 0))
    body.boxb(0, 25, 0, 14, 9, 10, "stone")                                      # waist
    body.box((0, 27.5, -5.3), (8, 5, 1), "core_plate")                          # belt sigil

    vortex = m.bone("vortex", "body", (0, 28, 0))
    vortex.boxb(0, 18, 0, 10, 9, 10, "cloud_dark")                              # funnel core
    vortex.boxb(0, 10, 0, 7, 9, 7, "cloud_dark")
    vortex.boxb(0, 4, 0, 4, 7, 4, "cloud_dark")
    vortex.boxb(0, 0.5, 0, 2, 4, 2, "cloud_dark")
    for (nm, y, R, n, size, tilt) in RINGS:
        ring = m.bone(nm, "vortex", (0, y, 0), rotation=[tilt, 0, tilt * 0.6])
        for k in range(n):
            th = 360.0 * k / n + (17 if nm.endswith("2") else 0) + (33 if nm.endswith("4") else 0)
            x = R * math.cos(math.radians(th))
            z = R * math.sin(math.radians(th))
            yy = y + (0.8 if k % 2 else -0.4)
            ring.box((x, yy, z), size, "cloud", rot=[(-8 if k % 2 else 6), -th + 90, 0], ring=nm)

    chest = m.bone("chest", "body", (0, 33, 0), rotation=[8, 0, 0])
    chest.boxb(0, 32, 0, 16, 8, 11, "stone")                                    # abdomen
    chest.boxb(0, 39, 0, 26, 14, 15, "stone")                                   # broad chest
    chest.box((-6.2, 47.0, -7.9), (10, 8, 2), "plate", rot=[-10, 12, 0])        # pectoral plates
    chest.box((6.2, 47.0, -7.9), (10, 8, 2), "plate", rot=[-10, -12, 0])
    chest.box((0, 44.5, -8.0), (5, 7, 2), "core")                               # storm core
    chest.box((0, 36.0, -6.1), (12, 3, 2), "plate", rot=[4, 0, 0])              # ab plates
    chest.box((0, 33.0, -6.0), (10, 2, 2), "plate", rot=[2, 0, 0])
    for k, (x, y, d, L) in enumerate(((0, 50, (0, 0.9, 1.0), 9), (-6, 47, (-0.4, 0.8, 1.0), 7), (6, 47, (0.4, 0.8, 1.0), 7))):
        chest.spike((x, y, 7.0), d, L, 3, "plate", segs=[0.6, 0.4])             # jagged back ridges
    # cloud mane over the shoulders and back of the neck
    chest.box((0, 53.5, 5.5), (16, 8, 8), "cloud", mane=True)
    chest.box((-8.5, 52.5, 3.0), (8, 7, 9), "cloud", mane=True, rot=[0, 10, 12])
    chest.box((8.5, 52.5, 3.0), (8, 7, 9), "cloud", mane=True, rot=[0, -10, -12])
    chest.box((0, 47.0, 9.0), (12, 9, 5), "cloud", mane=True, rot=[-14, 0, 0])

    shard_r = m.bone("shard_right", "chest", (-16, 60, 8))
    shard_r.spike((-16, 57, 8), (-0.2, 1.0, 0.1), 8, 3, "plate", segs=[0.6, 0.4], vein=True)
    shard_l = m.bone("shard_left", "chest", (16, 62, 7))
    shard_l.spike((16, 59, 7), (0.25, 1.0, -0.1), 7, 3, "plate", segs=[0.6, 0.4], vein=True)

    neck = m.bone("neck", "chest", (0, 52, -2), rotation=[-8, 0, 0])
    head = m.bone("head", "neck", (0, 53, -3))
    head.boxb(0, 53, -4, 10, 10, 10, "stone")                                   # skull
    head.box((0, 60.4, -8.9), (12, 2, 3), "plate", rot=[16, 0, 0])              # brow
    head.box((-4.6, 55.5, -8.6), (2, 4, 2), "plate", rot=[0, 0, 8])             # cheek blades
    head.box((4.6, 55.5, -8.6), (2, 4, 2), "plate", rot=[0, 0, -8])
    head.box((-2.6, 58.4, -9.1), (3, 1, 1), "eye", inflate=0.12)
    head.box((2.6, 58.4, -9.1), (3, 1, 1), "eye", inflate=0.12)
    # lightning-bolt horns sweeping back (zig-zag)
    for s in (-1, 1):
        head.box((5.6 * s, 62.0, -4.0), (2, 5, 2), "horn", rot=[-30, 0, -30 * s])
        head.box((7.6 * s, 65.0, -2.4), (2, 4, 2), "horn", rot=[-10, 0, 25 * s])
        head.box((9.0 * s, 68.0, -1.6), (1, 4, 1), "horn", rot=[-35, 0, -20 * s], tip=True)
    # wild mane: big puffs crowning and trailing behind the head
    head.box((0, 61.5, 3.5), (12, 8, 6), "cloud", mane=True, rot=[-20, 0, 0])
    head.box((-4.0, 66.0, 2.5), (5, 7, 5), "cloud", mane=True, rot=[-25, 8, 22])
    head.box((4.0, 66.0, 2.5), (5, 7, 5), "cloud", mane=True, rot=[-25, -8, -22])
    head.box((0, 67.5, 4.5), (6, 8, 5), "cloud", mane=True, rot=[-38, 0, 0])
    head.box((-6.8, 58.5, -1.0), (4, 8, 8), "cloud", mane=True, rot=[0, 0, 14])
    head.box((6.8, 58.5, -1.0), (4, 8, 8), "cloud", mane=True, rot=[0, 0, -14])
    head.box((0, 56.5, 6.5), (11, 7, 5), "cloud", mane=True, rot=[-30, 0, 0])
    head.box((0, 63.4, -2.5), (9, 2, 7), "cloud", mane=True, rot=[8, 0, 0])
    head.box((0, 64.5, 9.5), (5, 4, 9), "cloud", mane=True, rot=[-28, 0, 0])            # wisps streaming back
    head.box((-5.0, 62.0, 8.5), (4, 4, 8), "cloud", mane=True, rot=[-18, -16, 10])
    head.box((5.0, 62.0, 8.5), (4, 4, 8), "cloud", mane=True, rot=[-18, 16, -10])
    jaw = m.bone("jaw", "head", (0, 54, -3))
    jaw.boxb(0, 50.5, -4.5, 9, 3, 9, "stone")
    jaw.box((0, 49.5, -6.5), (7, 3, 4), "cloud", mane=True)                     # cloud beard

    for side, nm in ((-1, "right"), (1, "left")):
        s = side
        arm = m.bone(f"{nm}_arm", "chest", (14 * s, 50, 0), rotation=[-8, 0, -4 * s])
        arm.boxb(17 * s, 38, 0, 8, 14, 8, "stone")                              # upper arm
        arm.box((17.5 * s, 51.5, 0), (11, 6, 13), "plate", rot=[0, 0, -16 * s])  # angular pauldron
        arm.box((19.5 * s, 49.0, 0), (3, 4, 14), "plate", rot=[0, 0, -16 * s])
        arm.spike((21 * s, 52, 0), (0.9 * s, 0.8, 0), 7, 3, "plate", segs=[0.6, 0.4])
        arm.box((17.0 * s, 56.5, 2.0), (10, 5, 10), "cloud", mane=True)         # thunderhead on shoulder
        arm.box((19.5 * s, 58.5, 6.5), (4, 4, 7), "cloud", mane=True, rot=[-25, 12 * s, -18 * s])
        fore = m.bone(f"{nm}_forearm", f"{nm}_arm", (17 * s, 38.5, 0), rotation=[-10, 0, 0])
        fore.boxb(17 * s, 25, 0, 7, 14, 7, "stone")                             # forearm
        fore.boxb(17 * s, 26, 0, 9, 9, 9, "copper")                             # copper bracer
        fore.boxb(17 * s, 35.5, 0, 9, 1, 9, "copper", inflate=0.2, ring=True)   # upper ring
        fore.spike((17 * s, 37, 3.5), (0, 0.2, 1.0), 5, 3, "plate", segs=[1.0])  # elbow spike
        fore.boxb(17 * s, 18, -0.5, 8, 7, 9, "stone")                           # hand
        for x, z in ((14.6, -4.0), (17.0, -4.3), (19.4, -4.0)):
            fore.box((x * s, 16.6, z), (2, 5, 2), "claw", rot=[-18, 0, 0])
        fore.box((13.0 * s, 20.0, -2.5), (2, 4, 2), "claw", rot=[0, 0, 20 * s])  # thumb
    return m

# =============================================================================== shaders


STONE = palette("#15181f", "#1d2129", "#262b35", "#30363f", "#3c434e", "#49515d", "#58616e", "#6a7482", "#808a98")
PLATE = palette("#1f2430", "#2a303d", "#363e4d", "#444d5e", "#535d70", "#657084", "#7a869b", "#929db0")
VEIN = palette("#f0b020", "#ffd848", "#fff08a", "#fffbd8", "#ffffff")
CLOUD = palette("#6c768c", "#8690a5", "#a1aabc", "#bbc2d0", "#d1d7e1", "#e3e7ee", "#f1f4f8", "#ffffff")
CLOUD_D = palette("#454c5c", "#565e6f", "#697183", "#7f8798", "#979fae", "#b1b8c4", "#cbd0d9", "#e2e5eb")
COPPER = palette("#4a200c", "#6e3216", "#934520", "#b85b2a", "#d77538", "#ee944c", "#fbb56c", "#ffd59a")
VERD = palette("#2b6e62", "#3e8d7d", "#58ab98", "#7fcab4")
EYE = palette("#ffe14a", "#fff59a", "#ffffe8")


def _th(ctx, seed):
    p = ctx.p
    return hash3(np.floor(p[:, 0] * 2 + 0.01), np.floor(p[:, 1] * 2 + 0.01), np.floor(p[:, 2] * 2 + 0.01), seed)


def vein_layer(ctx, rgb, density=0.0, width=0.022):
    """Branching lightning veins from ridged noise; returns glow mask."""
    p = ctx.p
    n = vnoise(p, 0.11, 71) * 0.65 + vnoise(p, 0.27, 72) * 0.35
    ridge = np.abs(n - 0.5)
    gate = fbm(p, 0.07, 2, 73) > 0.46 - density
    line = (ridge < width) & gate
    core = (ridge < width * 0.4) & gate
    halo = (ridge < width * 2.6) & gate & ~line
    rgb[halo] = rgb[halo] * 0.55 + np.array([200, 160, 60]) * 0.45
    rgb[line] = VEIN[1]
    rgb[core] = VEIN[3]
    return line | core


def shade_stone(ctx, plate=False):
    p = ctx.p
    f1, f2, cid = worley(p, 0.14, 5)
    v = 0.5 + (fbm(p, 0.14, 3, 1) - 0.5) * 0.4 + (cid - 0.5) * 0.18
    v -= ((f2 - f1) < 0.05) * 0.18
    # chiselled strata
    v += (np.sin(p[:, 1] * 1.3 + fbm(p, 0.1, 2, 3) * 4) > 0.85) * 0.08
    v += (_th(ctx, 7) - 0.5) * 0.06
    v += edge_term(ctx, 0.18 if plate else 0.12, 0.15, 0.05) + vgrad(ctx, 0.12) - ctx.ao * 0.55
    v += 0.08 * max(0, ctx.nw[1]) - 0.1 * max(0, -ctx.nw[1])
    rgb = ramp(PLATE if plate else STONE, v)
    glow = vein_layer(ctx, rgb, density=0.0 if not plate else -0.08)
    if ctx.params.get("vein"):
        glow |= vein_layer(ctx, rgb, density=0.2, width=0.03)
    return rgb, 255, glow


def shade_cloud(ctx, dark=False):
    p = ctx.p
    # cauliflower billows: each Worley cell is a puff lit from above, shaded below, with soft outlines
    f1, f2, near = tl.worley_pts(p, 0.15, 9)
    rel = (p - near) * 0.15                                  # in cell units
    up = rel[:, 1] / (np.sqrt((rel ** 2).sum(1)) + 1e-6)     # -1 bottom .. 1 top of the puff
    v = 0.64 + up * 0.17 + (1 - np.clip(f1 * 1.4, 0, 1)) * 0.06
    v -= ((f2 - f1) < 0.06) * (up < 0.2) * 0.08              # soft shadow under each billow
    v += (fbm(p, 0.2, 2, 4) - 0.5) * 0.1
    side = ctx.face not in ("up", "down")
    v += (0.18 if ctx.face == "up" else 0) - (0.3 if ctx.face == "down" else 0)
    if side:
        v += (0.5 - ctx.t) * 0.3
    if ctx.params.get("ring") or dark:
        streak = np.mod(ctx.i + ctx.j * 2.2 + hash3(ctx.index, 1, 1, 2)[0] * 30, 11) < 1.5
        v += streak * 0.12
    v += edge_term(ctx, 0.14, 0.04, 0.0) - ctx.ao * 0.45
    rgb = ramp(CLOUD_D if dark else CLOUD, v)
    # ragged, fluffy borders (cutout)
    de = np.minimum(np.minimum(ctx.i, ctx.tw - 1 - ctx.i), np.minimum(ctx.j, ctx.th - 1 - ctx.j))
    nz = fbm(p, 0.7, 2, 15)
    ragged = ((de == 0) & (nz > 0.44)) | ((de == 1) & (nz > 0.64))
    ragged &= side & (ctx.j > 0)
    alpha = np.where(ragged, 0, 255)
    glow = np.zeros(ctx.N, dtype=bool)
    if dark or ctx.params.get("ring"):
        g = (_th(ctx, 41) > 0.988) & ~ragged
        rgb[g] = VEIN[2]
        glow = g
    return rgb, alpha, glow


def shade_copper(ctx):
    p = ctx.p
    v = 0.52 + (fbm(p, 0.25, 3, 2) - 0.5) * 0.3 + vgrad(ctx, 0.18)
    if ctx.face not in ("up", "down"):
        v += np.where(ctx.s < 0.3, 0.15, np.where(ctx.s > 0.78, -0.14, 0.0))
    band = (ctx.j < 2) | (ctx.j >= ctx.th - 2)
    v += band * 0.16
    rivet = (np.mod(ctx.i, 6) == 3) & ((ctx.j == 3) | (ctx.j == ctx.th - 4))
    v += rivet * 0.3
    # engraved zigzag (lightning) band
    if not ctx.params.get("ring") and ctx.face not in ("up", "down"):
        zz = np.abs(np.mod(ctx.i, 8) - 4) * 0.75
        line = np.abs(ctx.j - (ctx.th / 2 - 2 + zz)) < 0.8
        v -= line * 0.35
    v += edge_term(ctx, 0.2, 0.18, 0.05) - ctx.ao * 0.5
    rgb = ramp(COPPER, v)
    verd = (fbm(p, 0.3, 3, 31) > 0.6) | ((fbm(p, 0.5, 2, 32) > 0.55) & band)
    vv = 0.45 + (fbm(p, 0.8, 2, 5) - 0.5) * 0.6
    rgb[verd] = ramp(VERD, vv[verd])
    if not ctx.params.get("ring") and ctx.face not in ("up", "down"):
        zz = np.abs(np.mod(ctx.i, 8) - 4) * 0.75
        line = np.abs(ctx.j - (ctx.th / 2 - 2 + zz)) < 0.7
        rgb[line] = VEIN[1]
        return rgb, 255, line
    return rgb, 255, False


def shade_core(ctx):
    rgb, _, _ = shade_stone(ctx, plate=True)
    rgb = rgb * 0.5
    glow = np.zeros(ctx.N, dtype=bool)
    if ctx.face == "north":
        x = (ctx.s - 0.5) * 2
        y = (0.5 - ctx.t) * 2
        bolt = tl.polyline_dist(x, y, [(0.35, 0.95), (-0.3, 0.1), (0.25, 0.05), (-0.35, -0.95)])
        line = bolt < 0.2
        core = bolt < 0.09
        halo = (bolt < 0.36) & ~line
        rgb[halo] = rgb[halo] * 0.4 + np.array([255, 200, 60]) * 0.6
        rgb[line] = VEIN[2]
        rgb[core] = VEIN[4]
        fr = (ctx.i == 0) | (ctx.i == ctx.tw - 1) | (ctx.j == 0) | (ctx.j == ctx.th - 1)
        rgb[fr] = VEIN[0]
        glow = line | halo | fr
    return rgb, 255, glow


def shade_core_plate(ctx):
    rgb, _, glow = shade_stone(ctx, plate=True)
    if ctx.face == "north":
        x = (ctx.s - 0.5) * 2
        y = (0.5 - ctx.t) * 2
        d = tl.polyline_dist(x, y, [(-0.9, 0), (-0.4, 0.5), (0, -0.4), (0.4, 0.5), (0.9, 0)])
        line = d < 0.16
        rgb[line] = VEIN[1]
        glow = glow | line
    return rgb, 255, glow


def shade_horn(ctx):
    rgb, _, glow = shade_stone(ctx, plate=True)
    if ctx.params.get("tip"):
        tip = ctx.t < 0.6
        rgb[tip] = ramp(VEIN, 0.3 + (0.6 - ctx.t[tip]))
        glow = glow | tip
    return rgb, 255, glow


def shade_eye(ctx):
    v = 0.45 + (ctx.face == "north") * 0.4 - (np.abs(ctx.s - 0.5) > 0.32) * 0.25
    return ramp(EYE, v), 255, True


def shade_claw(ctx):
    v = 0.65 - ctx.t * 0.45 + edge_term(ctx, 0.2)
    return ramp(PLATE, v), 255, False


SHADERS = {
    "stone": shade_stone,
    "plate": lambda c: shade_stone(c, plate=True),
    "cloud": shade_cloud,
    "cloud_dark": lambda c: shade_cloud(c, dark=True),
    "copper": shade_copper,
    "core": shade_core,
    "core_plate": shade_core_plate,
    "horn": shade_horn,
    "eye": shade_eye,
    "claw": shade_claw,
}

# =============================================================================== animations
RING_TURNS = {"vortex_ring1": 1, "vortex_ring2": -2, "vortex_ring3": 3, "vortex_ring4": -4}


def spin_rings(c, length, factor=1):
    """Whole turns over the clip so loops are seamless."""
    for nm, turns in RING_TURNS.items():
        tot = 360.0 * turns * factor
        c.f(nm, "rotation", lambda t, tot=tot: (0, tot * t / length, 0))


def float_bob(c, T, amp=1.4):
    c.f("body", "position", lambda t: (0, amp * math.sin(TAU * t / T), 0))
    c.f("vortex", "rotation", lambda t: (2.5 * math.sin(TAU * t / T + 1.0), 0, 2.0 * math.sin(TAU * t / T)))


def mane_breath(c, T, amp=0.04):
    pass


def anim_idle():
    T = 3.0
    c = Clip("idle", T, loop=True)
    w = lambda t, ph=0.0: math.sin(TAU * t / T + ph)
    spin_rings(c, T)
    float_bob(c, T)
    c.f("chest", "rotation", lambda t: (-1.5 * w(t, 0.6), 0, 1.0 * w(t, 2.0)))
    c.f("right_arm", "rotation", lambda t: (3 * w(t, 0.9), 0, 3 + 2.5 * w(t, 0.4)))
    c.f("left_arm", "rotation", lambda t: (3 * w(t, 1.2), 0, -3 - 2.5 * w(t, 0.4)))
    c.f("right_forearm", "rotation", lambda t: (-4 * w(t, 1.5), 0, 0))
    c.f("left_forearm", "rotation", lambda t: (-4 * w(t, 1.8), 0, 0))
    c.f("neck", "rotation", lambda t: (1.5 * w(t, 1.0), 3 * w(t, 0.2), 0))
    c.f("jaw", "rotation", lambda t: (2 + 2 * w(t), 0, 0))
    c.f("shard_right", "position", lambda t: (0, 1.4 * w(t, 0.0), 0))
    c.f("shard_right", "rotation", lambda t: (0, 120 * t / T, 0))
    c.f("shard_left", "position", lambda t: (0, 1.4 * w(t, 2.2), 0))
    c.f("shard_left", "rotation", lambda t: (0, -120 * t / T, 0))
    return c


def anim_walk():
    T = 1.6
    c = Clip("walk", T, loop=True)
    w = lambda t, ph=0.0: math.sin(TAU * t / T + ph)
    spin_rings(c, T, 1)
    c.f("body", "position", lambda t: (0, 1.0 * w(t), 0))
    c.f("body", "rotation", lambda t: (10 + 2 * w(t, 1.0), 4 * w(t), -3 * w(t)))
    c.f("vortex", "rotation", lambda t: (-14 + 3 * w(t, 0.6), -4 * w(t), 4 * w(t, 0.5)))
    c.f("chest", "rotation", lambda t: (2, -6 * w(t), 2 * w(t)))
    c.f("right_arm", "rotation", lambda t: (16 + 10 * w(t, 0.3), 0, 8 + 3 * w(t)))
    c.f("left_arm", "rotation", lambda t: (16 - 10 * w(t, 0.3), 0, -8 - 3 * w(t)))
    c.f("right_forearm", "rotation", lambda t: (-12 + 6 * w(t, 0.9), 0, 0))
    c.f("left_forearm", "rotation", lambda t: (-12 - 6 * w(t, 0.9), 0, 0))
    c.f("neck", "rotation", lambda t: (-10, 4 * w(t), 0))
    c.f("shard_right", "position", lambda t: (0, 1.2 * w(t), 1.5))
    c.f("shard_right", "rotation", lambda t: (0, 360 * t / T, 0))
    c.f("shard_left", "position", lambda t: (0, 1.2 * w(t, 2.0), 1.5))
    c.f("shard_left", "rotation", lambda t: (0, -360 * t / T, 0))
    return c


def anim_lightning_call():
    c = Clip("attack.lightning_call", 2.0)
    spin_rings(c, 2.0, 1)
    for side, nm in ((-1, "right"), (1, "left")):
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.9, (14, 0, -150 * side), "io"), (1.18, (12, 0, -142 * side)),
                            (1.25, (24, 0, -170 * side), "snap"), (1.6, (22, 0, -166 * side)), (2.0, (0, 0, 0), "io")])
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.9, (-14, 0, 0)), (1.25, (8, 0, 0), "snap"), (1.6, (6, 0, 0)), (2.0, (0, 0, 0))])
    trem = lambda t: env(t, 0.75, 0.95, 1.2, 1.25)
    for b in ("right_arm", "left_arm"):
        c.f(b, "rotation", lambda t, b=b: (shake(t, 24, 3.0, len(b)) * trem(t), 0, shake(t, 21, 3.0, 2 + len(b)) * trem(t)))
    c.rot("chest", [(0, (0, 0, 0)), (0.9, (-16, 0, 0)), (1.18, (-18, 0, 0)), (1.25, (6, 0, 0), "snap"),
                    (1.6, (2, 0, 0)), (2.0, (0, 0, 0))])
    c.rot("neck", [(0, (0, 0, 0)), (0.9, (-30, 0, 0)), (1.25, (-8, 0, 0), "snap"), (2.0, (0, 0, 0))])
    c.rot("jaw", [(0, (0, 0, 0)), (0.9, (16, 0, 0)), (1.25, (34, 0, 0), "snap"), (1.6, (20, 0, 0)), (2.0, (0, 0, 0))])
    c.pos("body", [(0, (0, 0, 0)), (0.9, (0, 4, 0)), (1.18, (0, 5, 0)), (1.25, (0, 1, 0), "snap"), (2.0, (0, 0, 0))])
    c.rot("vortex", [(0, (0, 0, 0)), (0.9, (8, 0, 0)), (1.25, (-6, 0, 0), "snap"), (2.0, (0, 0, 0))])
    c.scl("vortex", [(0, (1, 1, 1)), (0.9, (1.15, 0.9, 1.15)), (1.25, (1.3, 0.85, 1.3), "snap"), (2.0, (1, 1, 1))])
    return c


def anim_wind_gust():
    c = Clip("attack.wind_gust", 1.5)
    spin_rings(c, 1.5, 1)
    for side, nm in ((-1, "right"), (1, "left")):
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.5, (40, 18 * side, -20 * side), "io"), (0.7, (-86, -10 * side, 6 * side), "snap"),
                            (0.95, (-82, -8 * side, 6 * side)), (1.5, (0, 0, 0), "io")])
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.5, (-60, 0, 0)), (0.7, (-4, 0, 0), "snap"), (0.95, (-6, 0, 0)), (1.5, (0, 0, 0))])
    c.rot("chest", [(0, (0, 0, 0)), (0.5, (-16, 0, 0)), (0.7, (18, 0, 0), "snap"), (0.95, (15, 0, 0)), (1.5, (0, 0, 0))])
    c.rot("neck", [(0, (0, 0, 0)), (0.5, (-8, 0, 0)), (0.7, (-14, 0, 0), "snap"), (1.5, (0, 0, 0))])
    c.rot("jaw", [(0, (0, 0, 0)), (0.5, (10, 0, 0)), (0.7, (30, 0, 0), "snap"), (1.0, (18, 0, 0)), (1.5, (0, 0, 0))])
    c.pos("body", [(0, (0, 0, 0)), (0.5, (0, 1, 3)), (0.7, (0, -1, -3), "snap"), (0.95, (0, -1, -2.5)), (1.5, (0, 0, 0))])
    c.rot("vortex", [(0, (0, 0, 0)), (0.5, (12, 0, 0)), (0.7, (-16, 0, 0), "snap"), (1.5, (0, 0, 0))])
    return c


def anim_thunder_clap():
    c = Clip("attack.thunder_clap", 1.5)
    spin_rings(c, 1.5, 1)
    c.rot("right_arm", [(0, (0, 0, 0)), (0.55, (-72, 55, 0), "io"), (0.8, (-78, -30, 0), "snap"), (1.0, (-76, -28, 0)),
                        (1.5, (0, 0, 0), "io")])
    c.rot("left_arm", [(0, (0, 0, 0)), (0.55, (-72, -55, 0), "io"), (0.8, (-78, 30, 0), "snap"), (1.0, (-76, 28, 0)),
                       (1.5, (0, 0, 0), "io")])
    for nm in ("right_forearm", "left_forearm"):
        c.rot(nm, [(0, (0, 0, 0)), (0.55, (-25, 0, 0)), (0.8, (-6, 0, 0), "snap"), (1.0, (-8, 0, 0)), (1.5, (0, 0, 0))])
    c.rot("chest", [(0, (0, 0, 0)), (0.55, (-14, 0, 0)), (0.8, (12, 0, 0), "snap"), (1.0, (10, 0, 0)), (1.5, (0, 0, 0))])
    c.f("chest", "rotation", lambda t: (shake(t, 26, 2.0) * env(t, 0.8, 0.82, 0.95, 1.1), 0, shake(t, 22, 1.5, 3) * env(t, 0.8, 0.82, 0.95, 1.1)))
    c.rot("neck", [(0, (0, 0, 0)), (0.55, (-10, 0, 0)), (0.8, (-4, 0, 0), "snap"), (1.5, (0, 0, 0))])
    c.rot("jaw", [(0, (0, 0, 0)), (0.55, (20, 0, 0)), (0.8, (8, 0, 0), "snap"), (1.5, (0, 0, 0))])
    c.pos("body", [(0, (0, 0, 0)), (0.55, (0, 3, 0)), (0.8, (0, -1.5, 0), "snap"), (1.0, (0, -1, 0)), (1.5, (0, 0, 0))])
    c.scl("vortex", [(0, (1, 1, 1)), (0.78, (1, 1, 1)), (0.85, (1.25, 0.9, 1.25), "snap"), (1.5, (1, 1, 1))])
    return c


def anim_storm_dash():
    c = Clip("attack.storm_dash", 1.2)
    spin_rings(c, 1.2, 1)
    c.pos("body", [(0, (0, 0, 0)), (0.35, (0, 1.5, 4), "io"), (0.55, (0, -1, -8), "snap"), (0.8, (0, -1, -7)), (1.2, (0, 0, 0), "io")])
    c.rot("body", [(0, (0, 0, 0)), (0.35, (-10, 0, 0)), (0.55, (26, 0, 0), "snap"), (0.8, (24, 0, 0)), (1.2, (0, 0, 0))])
    c.rot("vortex", [(0, (0, 0, 0)), (0.35, (14, 0, 0)), (0.55, (-38, 0, 0), "snap"), (0.8, (-34, 0, 0)), (1.2, (0, 0, 0))])
    for side, nm in ((-1, "right"), (1, "left")):
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.35, (30, 0, -25 * side)), (0.55, (-70, 20 * side, -30 * side), "snap"),
                            (0.8, (-66, 18 * side, -28 * side)), (1.2, (0, 0, 0), "io")])
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.35, (-50, 0, 0)), (0.55, (-25, 0, 0), "snap"), (1.2, (0, 0, 0))])
    c.rot("neck", [(0, (0, 0, 0)), (0.35, (4, 0, 0)), (0.55, (-26, 0, 0), "snap"), (0.8, (-24, 0, 0)), (1.2, (0, 0, 0))])
    c.rot("jaw", [(0, (0, 0, 0)), (0.55, (32, 0, 0), "snap"), (0.85, (24, 0, 0)), (1.2, (0, 0, 0))])
    return c


def anim_phase():
    c = Clip("phase", 2.0)
    spin_rings(c, 2.0, 1)
    c.rot("chest", [(0, (0, 0, 0)), (0.45, (20, 0, 0), "io"), (0.75, (-24, 0, 0), "snap"), (1.5, (-22, 0, 0)), (2.0, (0, 0, 0))])
    c.rot("neck", [(0, (0, 0, 0)), (0.45, (14, 0, 0)), (0.75, (-30, 0, 0), "snap"), (1.5, (-28, 0, 0)), (2.0, (0, 0, 0))])
    c.rot("jaw", [(0, (0, 0, 0)), (0.45, (4, 0, 0)), (0.7, (40, 0, 0), "snap"), (1.55, (38, 0, 0)), (2.0, (0, 0, 0))])
    for side, nm in ((-1, "right"), (1, "left")):
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.45, (-30, 0, 10 * side)), (0.75, (-20, 0, -100 * side), "snap"),
                            (1.5, (-18, 0, -96 * side)), (2.0, (0, 0, 0), "io")])
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.45, (-70, 0, 0)), (0.75, (-30, 0, 0), "snap"), (2.0, (0, 0, 0))])
    trem = lambda t: env(t, 0.75, 0.8, 1.45, 1.6)
    c.f("chest", "rotation", lambda t: (shake(t, 20, 1.5) * trem(t), shake(t, 17, 1.2, 3) * trem(t), 0))
    c.f("neck", "rotation", lambda t: (shake(t, 23, 1.5, 5) * trem(t), 0, shake(t, 19, 1.2, 1) * trem(t)))
    c.pos("body", [(0, (0, 0, 0)), (0.45, (0, -2, 0)), (0.75, (0, 5, 0), "snap"), (1.5, (0, 4, 0)), (2.0, (0, 0, 0))])
    c.scl("vortex", [(0, (1, 1, 1)), (0.45, (0.9, 1.0, 0.9)), (0.75, (1.4, 1.1, 1.4), "snap"), (1.5, (1.35, 1.1, 1.35)), (2.0, (1, 1, 1))])
    for b in ("shard_right", "shard_left"):
        c.pos(b, [(0, (0, 0, 0)), (0.75, (0, 6, 2), "snap"), (1.5, (0, 6, 2)), (2.0, (0, 0, 0))])
    return c


def anim_death():
    c = Clip("death", 2.8, loop="hold")
    spin_rings(c, 2.8, 1)
    # convulses, rises, the vortex blows apart and the body dissipates into the wind
    c.rot("chest", [(0, (0, 0, 0)), (0.3, (-20, 0, 0), "out"), (1.2, (18, 0, 8)), (2.0, (26, 0, 10)), (2.8, (26, 0, 10))])
    c.rot("neck", [(0, (0, 0, 0)), (0.3, (-28, 0, 0), "out"), (1.2, (20, 0, 0)), (2.0, (30, 0, 6)), (2.8, (30, 0, 6))])
    c.rot("jaw", [(0, (0, 0, 0)), (0.3, (38, 0, 0)), (1.2, (20, 0, 0)), (2.0, (34, 0, 0)), (2.8, (34, 0, 0))])
    for side, nm in ((-1, "right"), (1, "left")):
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.3, (-50, 0, -60 * side), "out"), (1.2, (10, 0, -20 * side)),
                            (2.0, (20, 0, -10 * side)), (2.8, (20, 0, -10 * side))])
    c.f("chest", "rotation", lambda t: (shake(t, 22, 3.0) * env(t, 0.2, 0.3, 1.0, 1.3), shake(t, 18, 2.0, 2) * env(t, 0.2, 0.3, 1.0, 1.3), 0))
    c.pos("body", [(0, (0, 0, 0)), (0.3, (0, 3, 0), "out"), (1.2, (0, -4, 0), "io"), (2.0, (0, -10, 0), "in"), (2.8, (0, -12, 0))])
    burst = lambda t: tl.ease("out", (t - 1.4) / 1.0) if t > 1.4 else 0.0
    gone = lambda t: 1 - tl.ease("in", (t - 1.9) / 0.85) if t > 1.9 else 1.0
    for i, (nm, *_rest) in enumerate(RINGS):
        c.f(nm, "scale", lambda t, i=i: (1 + (1.6 - 0.2 * i) * burst(t), 1 - 0.5 * burst(t), 1 + (1.6 - 0.2 * i) * burst(t)))
        c.f(nm, "position", lambda t, i=i: (0, -2 * i * burst(t), 0))
    c.f("vortex", "scale", lambda t: (gone(t),) * 3)
    c.f("right_arm", "position", lambda t: (-6 * burst(t), 2 * burst(t), 0))
    c.f("left_arm", "position", lambda t: (6 * burst(t), 2 * burst(t), 0))
    c.f("head", "position", lambda t: (0, 4 * burst(t), -2 * burst(t)))
    for b in ("chest", "right_arm", "left_arm", "head"):
        c.f(b, "scale", lambda t: (gone(t),) * 3)
    for b in ("shard_right", "shard_left"):
        c.pos(b, [(0, (0, 0, 0)), (0.3, (0, 4, 0)), (1.5, (0, -20, 4), "in"), (2.8, (0, -20, 4))])
    return c


def clips():
    return [anim_idle(), anim_walk(), anim_lightning_call(), anim_wind_gust(), anim_thunder_clap(), anim_storm_dash(),
            anim_phase(), anim_death()]


POSES = [
    ("idle", [0.0, 1.5]),
    ("walk", [0.0, 0.8]),
    ("attack.lightning_call", [0.9, 1.25, 1.6]),
    ("attack.wind_gust", [0.5, 0.7, 1.0]),
    ("attack.thunder_clap", [0.55, 0.8, 1.1]),
    ("attack.storm_dash", [0.35, 0.55, 0.9]),
    ("phase", [0.45, 0.8, 1.2]),
    ("death", [0.3, 1.2, 1.9, 2.4]),
]


def main():
    m = build_model()
    geo, rgba, glow, anims = tl.build(NAME, m, SHADERS, clips(), visible=(5, 6, 2.5))
    if "--preview" in sys.argv:
        sel = POSES if "--all" in sys.argv else POSES[:3]
        for p in tl.previews(NAME, geo, rgba, glow, anims, HITBOX, sel, frame=(120, 92)):
            print("preview", p)


if __name__ == "__main__":
    main()
