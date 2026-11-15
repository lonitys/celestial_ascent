"""Frost Titan: a hunched giant of glacial ice over dark-blue frozen stone.

Run: python frost_titan.py [--preview]
"""
import math
import sys

import numpy as np

import titanlib as tl
from titanlib import (Clip, edge_term, env, fbm, hash3, palette, ramp, shake, vgrad, worley,
                      polyline_dist)
from anim_helpers import TAU, legs_for_drop, mirror

NAME = "frost_titan"
HITBOX = (2.0, 4.0)

# =============================================================================== geometry


def build_model():
    m = tl.Model(NAME)
    body = m.bone("body", "root", (0, 21, 0))
    body.boxb(0, 17, 0.5, 20, 9, 12, "stone")                                   # pelvis
    body.box((0, 14.5, -6.3), (10, 10, 2), "ice", rot=[-7, 0, 0])               # front tasset
    body.box((-8.5, 15.5, -5.2), (6, 8, 2), "ice", rot=[-6, 14, 6])             # side tassets
    body.box((8.5, 15.5, -5.2), (6, 8, 2), "ice", rot=[-6, -14, -6])
    body.box((0, 16, 7.0), (14, 9, 2), "ice", rot=[8, 0, 0])                    # rear tasset

    chest = m.bone("chest", "body", (0, 25, 0), rotation=[10, 0, 0])
    chest.boxb(0, 24, 0.5, 18, 10, 12, "stone")                                 # abdomen
    chest.boxb(0, 33, 0, 26, 16, 16, "stone")                                   # ribcage
    chest.boxb(0, 47, 1.5, 22, 5, 13, "stone")                                  # trapezius hump
    chest.box((-8.0, 42.5, -8.6), (9, 10, 3), "ice", rot=[-3, 12, 0])           # pec plates
    chest.box((8.0, 42.5, -8.6), (9, 10, 3), "ice", rot=[-3, -12, 0])
    chest.box((0, 42.0, -8.4), (8, 10, 2), "rune")                              # chest rune stone
    chest.box((0, 35.2, -8.3), (16, 4, 2), "ice", rot=[4, 0, 0])                # ab plates
    chest.box((0, 30.0, -6.5), (13, 4, 2), "ice", rot=[2, 0, 0])
    chest.box((0, 40.5, 8.5), (20, 12, 2), "ice")                               # back plate
    chest.spike((0, 46, 8), (0, 1.0, 0.75), 16, 5, "crystal")                   # back crystals
    chest.spike((-7, 45, 8), (-0.35, 1.0, 0.8), 12, 4, "crystal")
    chest.spike((7, 45, 8), (0.35, 1.0, 0.8), 12, 4, "crystal")
    chest.spike((0, 37, 9), (0, 0.55, 1.0), 8, 3, "crystal", segs=[0.6, 0.4])

    neck = m.bone("neck", "chest", (0, 48, -4), rotation=[-10, 0, 0])
    head = m.bone("head", "neck", (0, 50, -7))
    head.boxb(0, 48, -10.5, 12, 11, 11, "skull")                                # skull
    head.box((0, 56.6, -16.3), (14, 3, 4), "ice", rot=[14, 0, 0])               # brow ridge
    head.box((-5.6, 51.8, -15.6), (3, 4, 3), "ice", rot=[0, 10, 0])             # cheek plates
    head.box((5.6, 51.8, -15.6), (3, 4, 3), "ice", rot=[0, -10, 0])
    head.box((0, 53.2, -16.7), (2, 4, 2), "skull", rot=[8, 0, 0])               # nose ridge
    head.box((-3.1, 54.6, -16.15), (3, 1, 1), "eye", inflate=0.12)              # eyes
    head.box((3.1, 54.6, -16.15), (3, 1, 1), "eye", inflate=0.12)
    head.boxb(0, 57.6, -10.5, 13, 2, 12, "ice")                                 # circlet
    head.spike((0, 58.6, -15.5), (0, 1.0, -0.22), 14, 4, "crystal")             # crown
    head.spike((-4.2, 58.4, -14.6), (-0.42, 1.0, -0.28), 10, 3, "crystal", segs=[0.6, 0.4])
    head.spike((4.2, 58.4, -14.6), (0.42, 1.0, -0.28), 10, 3, "crystal", segs=[0.6, 0.4])
    head.spike((-6.0, 58.2, -10.0), (-0.85, 1.0, -0.05), 9, 3, "crystal", segs=[0.6, 0.4])
    head.spike((6.0, 58.2, -10.0), (0.85, 1.0, -0.05), 9, 3, "crystal", segs=[0.6, 0.4])
    head.spike((-4.0, 58.2, -5.6), (-0.5, 1.0, 0.55), 7, 3, "crystal", segs=[0.6, 0.4])
    head.spike((4.0, 58.2, -5.6), (0.5, 1.0, 0.55), 7, 3, "crystal", segs=[0.6, 0.4])

    jaw = m.bone("jaw", "head", (0, 50, -7))
    jaw.boxb(0, 45, -10.5, 11, 4, 10, "skull")
    beard = m.bone("beard", "jaw", (0, 46, -12))
    beard.spike((0, 46, -14.2), (0, -1.0, -0.14), 16, 4, "icicle")
    beard.spike((-2.6, 46, -14.0), (-0.12, -1.0, -0.12), 12, 3, "icicle", segs=[0.6, 0.4])
    beard.spike((2.6, 46, -14.0), (0.12, -1.0, -0.12), 12, 3, "icicle", segs=[0.6, 0.4])
    beard.spike((-4.6, 46, -12.6), (-0.25, -1.0, -0.08), 9, 3, "icicle", segs=[0.6, 0.4])
    beard.spike((4.6, 46, -12.6), (0.25, -1.0, -0.08), 9, 3, "icicle", segs=[0.6, 0.4])
    beard.spike((-5.2, 46.5, -8.6), (-0.3, -1.0, 0.1), 6, 2, "icicle", segs=[0.6, 0.4])
    beard.spike((5.2, 46.5, -8.6), (0.3, -1.0, 0.1), 6, 2, "icicle", segs=[0.6, 0.4])

    for side, nm in ((-1, "right"), (1, "left")):
        s = side
        arm = m.bone(f"{nm}_arm", "chest", (15 * s, 46, 0), rotation=[-10, 0, -6 * s])
        arm.boxb(18 * s, 35, 0, 9, 13, 10, "stone")                             # upper arm
        arm.box((19.6 * s, 47, 0), (13, 7, 15), "ice", rot=[0, 0, -12 * s])     # pauldron
        arm.box((20.2 * s, 44.2, 0), (14, 2, 16), "skull", rot=[0, 0, -12 * s])  # pauldron rim
        arm.spike((20 * s, 50, 0.5), (0.35 * s, 1.0, 0.05), 19, 5, "crystal")
        arm.spike((24 * s, 48.5, -4), (1.0 * s, 0.8, -0.3), 12, 4, "crystal")
        arm.spike((23 * s, 49, 4.5), (0.7 * s, 0.9, 0.6), 13, 4, "crystal")
        arm.spike((16 * s, 50.5, -5), (-0.1 * s, 1.0, -0.6), 7, 3, "crystal", segs=[0.6, 0.4])
        fore = m.bone(f"{nm}_forearm", f"{nm}_arm", (18 * s, 36, 0), rotation=[-8, 0, 0])
        fore.boxb(18 * s, 24, 0, 9, 13, 10, "stone")                            # forearm
        fore.boxb(18.5 * s, 26, 0, 11, 8, 12, "ice")                            # bracer
        fore.spike((23.5 * s, 31, -2), (1.0 * s, 0.35, 0), 6, 3, "crystal", segs=[0.6, 0.4])
        fore.spike((23.5 * s, 28, 2.5), (1.0 * s, 0.2, 0.35), 5, 3, "crystal", segs=[0.6, 0.4])
        fore.spike((18 * s, 35, 4.5), (0, 0.3, 1.0), 6, 3, "crystal", segs=[0.6, 0.4])
        fore.boxb(18.5 * s, 12, -0.5, 12, 12, 13, "fist")                       # ice fist
        fore.box((13.2 * s, 19, -5), (3, 6, 4), "fist")                         # thumb
        for k, x in enumerate((22.0, 18.5, 15.0)):
            fore.spike((x * s, 15.5, -6.5), (0, -0.35, -1.0), 5, 3, "crystal", segs=[0.6, 0.4])

        leg = m.bone(f"{nm}_leg", "root", (6.5 * s, 21, 0))
        leg.boxb(6.5 * s, 12, 0, 10, 10, 10, "stone")                           # thigh
        leg.box((6.8 * s, 17.5, -5.6), (9, 7, 2), "ice", rot=[-6, 0, 0])        # thigh plate
        leg.box((11.9 * s, 18.0, 0), (2, 7, 10), "ice", rot=[0, 0, -8 * s])     # hip guard
        shin = m.bone(f"{nm}_shin", f"{nm}_leg", (6.5 * s, 12, 0))
        shin.boxb(6.5 * s, 3, 0.5, 9, 10, 9, "stone")
        shin.box((6.5 * s, 11.6, -4.9), (8, 5, 3), "ice", rot=[-12, 0, 0])      # knee cap
        shin.box((6.5 * s, 6.5, -4.4), (8, 6, 2), "ice")                        # greave
        shin.spike((6.5 * s, 12.5, -5.8), (0, 0.55, -1.0), 5, 3, "crystal", segs=[0.6, 0.4])
        shin.boxb(6.5 * s, 0, -1.5, 11, 4, 14, "stone")                         # foot
        for x in (10.0, 6.5, 3.0):
            shin.box((x * s, 1.5, -9.4), (3, 3, 2), "ice")                      # toe claws
    return m

# =============================================================================== shaders


STONE = palette("#0e1326", "#151d36", "#1c2846", "#253357", "#2f4069", "#3b4f7d", "#4a6192", "#5b74a6")
CRACK = palette("#1846c8", "#2a6cf5", "#4f95ff", "#93ccff", "#d8f1ff")
FROST = palette("#6f8fbd", "#93b5de", "#bad7f3", "#e2f2ff")
ICE = palette("#24508f", "#3169ae", "#4386c8", "#5ca3dd", "#7dbdeb", "#a2d5f6", "#c7e9ff", "#e9f8ff")
CRYS = palette("#1a3f86", "#2257a8", "#2f74c6", "#4592dc", "#64afea", "#8acaf4", "#b4e1fb", "#e2f6ff", "#ffffff")
EYE = palette("#36e8ff", "#8ff6ff", "#e8ffff")
RUNE = palette("#1fb8ff", "#4fe0ff", "#a8f6ff", "#f0ffff")


def _crack_layer(ctx, rgb, freq=0.085, seed=11, thr=0.055, density=0.5):
    p = ctx.p
    g1, g2, _ = worley(p, freq, seed)
    gate = fbm(p, 0.1, 2, seed + 4) > density
    d = (g2 - g1)
    core = (d < thr * 0.45) & gate
    crack = (d < thr) & gate
    halo = (d < thr * 2.6) & gate & ~crack
    rgb[halo] = rgb[halo] * 0.7 + np.array([30, 70, 170]) * 0.3
    v = np.where(core, 0.85, 0.45) + (fbm(p, 0.4, 1, seed + 9) - 0.5) * 0.3
    rgb[crack] = ramp(CRACK, v[crack])
    return crack


def shade_stone(ctx, skull=False):
    p = ctx.p
    n1 = fbm(p, 0.16, 3, seed=1)
    f1, f2, cid = worley(p, 0.17, seed=3)
    v = 0.48 + (n1 - 0.5) * 0.55 + (cid - 0.5) * 0.16
    v -= ((f2 - f1) < 0.07) * 0.2                                       # block seams
    v += (hash3(np.floor(p[:, 0] * 2), np.floor(p[:, 1] * 2), np.floor(p[:, 2] * 2), 5) - 0.5) * 0.1
    v += edge_term(ctx, 0.12, 0.14, 0.05) + vgrad(ctx, 0.12) - ctx.ao * 0.55
    v += 0.08 * max(0, ctx.nw[1]) - 0.08 * max(0, -ctx.nw[1])
    rgb = ramp(STONE, v)
    # frost settles on up-facing surfaces and as rime patches
    rime = (fbm(p, 0.22, 3, seed=8) + max(0, ctx.nw[1]) * 0.35) > 0.72
    rgb[rime] = ramp(FROST, (fbm(p, 0.6, 2, 2)[rime] - 0.3) * 1.6 + edge_term(ctx)[rime])
    glow = _crack_layer(ctx, rgb, density=0.47 if not skull else 0.6)
    if skull and ctx.face == "north":
        # deep eye sockets with cyan glow spill
        x, y = p[:, 0], p[:, 1]
        for ex in (-3.1, 3.1):
            dx = np.abs(x - ex)
            sock = (dx < 2.6) & (np.abs(y - 54.6) < 1.4)
            rgb[sock] = np.array([8, 12, 26])
            spill = (dx < 3.4) & (np.abs(y - 54.4) < 2.3) & ~sock
            rgb[spill] = rgb[spill] * 0.55 + np.array([40, 200, 255]) * 0.45
        mouth = (np.abs(x) < 4.2) & (np.abs(y - 49.4) < 0.6)
        rgb[mouth] = np.array([6, 10, 22])
    return rgb, 255, glow


def shade_ice(ctx, fist=False):
    p = ctx.p
    de = np.minimum(np.minimum(ctx.i, ctx.tw - 1 - ctx.i), np.minimum(ctx.j, ctx.th - 1 - ctx.j)) / 2.0
    rim = np.clip(1 - de / 2.2, 0, 1)
    streak = np.sin((p[:, 0] * 0.8 + p[:, 1] * 1.2 - p[:, 2] * 0.6) * 0.62 + fbm(p, 0.2, 2, 7) * 4.0)
    v = 0.46 + rim * 0.22 + (streak > 0.8) * 0.18 + (fbm(p, 0.28, 3, 2) - 0.5) * 0.35
    v -= (fbm(p, 0.11, 2, 9) > 0.6) * 0.16                               # frozen depth pockets
    f1, f2, _ = worley(p, 0.19 if not fist else 0.26, 21)
    v += ((f2 - f1) < 0.045) * 0.28                                      # white fractures
    v += edge_term(ctx, 0.3, 0.12, 0.04) - ctx.ao * 0.5
    v += 0.1 * max(0, ctx.nw[1]) - 0.06 * max(0, -ctx.nw[1])
    rgb = ramp(ICE, v)
    sp = hash3(np.floor(p[:, 0] * 2), np.floor(p[:, 1] * 2), np.floor(p[:, 2] * 2), 77) > 0.985
    rgb[sp] = np.array([255, 255, 255])
    glow = np.zeros(ctx.N, dtype=bool)
    if fist:
        g1, g2, _ = worley(p, 0.11, 41)
        c = (g2 - g1) < 0.035
        rgb[c] = ramp(CRACK, np.full(c.sum(), 0.6))
        glow = c
    return rgb, 255, glow


def shade_crystal(ctx, icicle=False):
    p = ctx.p
    prm = ctx.params
    base = np.array(prm["spike_base"])
    prog = np.clip((p[:, 1] - base[1]) / prm["spike_len"], 0, 1)
    v = 0.18 + prog * 0.62
    if ctx.face not in ("up", "down"):
        facet = np.abs(ctx.s - 0.5) < 0.12
        v += facet * 0.14 - (ctx.s > 0.75) * 0.08
        v += (np.abs(ctx.s - 0.25 + prog * 0.1) < 0.06) * 0.1
    v += (fbm(p, 0.35, 2, 13) - 0.5) * 0.18
    v += edge_term(ctx, 0.18, 0.06, 0.06) - ctx.ao * 0.35
    if icicle:
        v = 0.25 + (1 - prog) * 0.25 + prog * 0.35 + (v - 0.18 - prog * 0.62) * 0.8
        v += (np.sin(p[:, 1] * 3.1 + p[:, 0] * 2) > 0.85) * 0.12
    rgb = ramp(CRYS, v)
    glow = np.zeros(ctx.N, dtype=bool)
    if not icicle:
        # faint inner light line along the crystal axis (glows)
        if ctx.face not in ("up", "down"):
            core = (np.abs(ctx.s - 0.5) < 0.07) & (prog < 0.75) & (prog > 0.08) & (ctx.params.get("seg", 0) == 0)
            rgb[core] = ramp(RUNE, np.full(core.sum(), 0.35))
            glow = core
    return rgb, 255, glow


RUNE_STROKES = [
    [(0, -0.86), (0, 0.86)],
    [(-0.62, 0.9), (0, 0.38), (0.62, 0.9)],
    [(-0.62, -0.9), (0, -0.38), (0.62, -0.9)],
    [(-0.62, 0.0), (0, 0.24), (0.62, 0.0), (0, -0.24), (-0.62, 0.0)],
]


def shade_rune(ctx):
    rgb, _, glow = shade_stone(ctx)
    rgb = rgb * 0.55
    glow = np.zeros(ctx.N, dtype=bool)
    if ctx.face == "north":
        x = (ctx.s - 0.5) * 2.0
        y = (0.5 - ctx.t) * 2.0
        d = np.full(ctx.N, 9.0)
        for st in RUNE_STROKES:
            d = np.minimum(d, polyline_dist(x, y * 1.0, st))
        core = d < 0.1
        line = d < 0.2
        halo = (d < 0.34) & ~line
        rgb[halo] = rgb[halo] * 0.4 + np.array([30, 150, 230]) * 0.6
        rgb[line] = ramp(RUNE, np.full(line.sum(), 0.4))
        rgb[core] = ramp(RUNE, np.full(core.sum(), 0.95))
        glow = line | halo
        # glowing frame
        fr = (ctx.i == 0) | (ctx.i == ctx.tw - 1) | (ctx.j == 0) | (ctx.j == ctx.th - 1)
        rgb[fr] = ramp(RUNE, np.full(fr.sum(), 0.1))
        glow |= fr
    return rgb, 255, glow


def shade_eye(ctx):
    v = 0.4 + (ctx.face == "north") * 0.4 - (np.abs(ctx.s - 0.5) > 0.35) * 0.3
    return ramp(EYE, v), 255, True


SHADERS = {
    "stone": shade_stone,
    "skull": lambda c: shade_stone(c, skull=True),
    "ice": shade_ice,
    "fist": lambda c: shade_ice(c, fist=True),
    "crystal": shade_crystal,
    "icicle": lambda c: shade_crystal(c, icicle=True),
    "rune": shade_rune,
    "eye": shade_eye,
}

# =============================================================================== animations

ARMS = ("right_arm", "left_arm")


def anim_idle():
    T = 3.0
    c = Clip("idle", T, loop=True)
    w = lambda t, ph=0.0, h=1: math.sin(TAU * h * t / T + ph)
    c.f("chest", "rotation", lambda t: (-1.6 * w(t), 0.8 * w(t, 1.0), 0))
    c.f("chest", "position", lambda t: (0, 0.35 * w(t), 0))
    c.f("body", "position", lambda t: (0, -0.25 * (1 - math.cos(TAU * t / T)) / 2, 0))
    c.f("right_arm", "rotation", lambda t: (2.0 * w(t, 0.7), 0, 1.6 * w(t, 0.3)))
    c.f("left_arm", "rotation", lambda t: (2.0 * w(t, 0.9), 0, -1.6 * w(t, 0.3)))
    c.f("right_forearm", "rotation", lambda t: (-2.5 * w(t, 1.3), 0, 0))
    c.f("left_forearm", "rotation", lambda t: (-2.5 * w(t, 1.5), 0, 0))
    c.f("neck", "rotation", lambda t: (1.3 * w(t, 0.9), 2.5 * w(t, 0.0), 0.8 * w(t, 2.0)))
    c.f("jaw", "rotation", lambda t: (1.5 + 1.5 * w(t, -0.4), 0, 0))
    c.f("beard", "rotation", lambda t: (2.5 * w(t, -0.9), 0, 1.5 * w(t, 1.2)))
    return c


def anim_walk():
    T = 1.6
    c = Clip("walk", T, loop=True)
    ph = lambda t: TAU * t / T
    c.f("right_leg", "rotation", lambda t: (-24 * math.sin(ph(t)), 0, 0))
    c.f("left_leg", "rotation", lambda t: (24 * math.sin(ph(t)), 0, 0))
    c.f("right_shin", "rotation", lambda t: (32 * max(0.0, math.cos(ph(t))) ** 1.4, 0, 0))
    c.f("left_shin", "rotation", lambda t: (32 * max(0.0, -math.cos(ph(t))) ** 1.4, 0, 0))
    # heavy stomp: drop sharply as each foot strikes (sin^2 peaks at the strikes)
    c.f("body", "position", lambda t: (0, 0.7 - 2.4 * math.sin(ph(t)) ** 4, 0))
    c.f("body", "rotation", lambda t: (0, 5 * math.sin(ph(t)), -3.5 * math.sin(ph(t))))
    c.f("chest", "rotation", lambda t: (4 + 2.5 * math.sin(ph(t)) ** 4, -7 * math.sin(ph(t)), 1.5 * math.sin(ph(t))))
    c.f("right_arm", "rotation", lambda t: (20 * math.sin(ph(t) - 0.25), 0, 2 + 2 * math.sin(ph(t)) ** 2))
    c.f("left_arm", "rotation", lambda t: (-20 * math.sin(ph(t) - 0.25), 0, -2 - 2 * math.sin(ph(t)) ** 2))
    c.f("right_forearm", "rotation", lambda t: (-8 - 8 * max(0.0, -math.sin(ph(t) - 0.6)), 0, 0))
    c.f("left_forearm", "rotation", lambda t: (-8 - 8 * max(0.0, math.sin(ph(t) - 0.6)), 0, 0))
    c.f("neck", "rotation", lambda t: (-2 - 2 * math.sin(ph(t)) ** 4, 3 * math.sin(ph(t)), 2.5 * math.sin(ph(t))))
    c.f("beard", "rotation", lambda t: (5 * math.sin(2 * ph(t) - 1.0), 0, 3 * math.sin(ph(t) - 0.8)))
    c.f("jaw", "rotation", lambda t: (1.5 + 1.5 * math.sin(2 * ph(t) - 0.5), 0, 0))
    return c


def anim_slam():
    c = Clip("attack.slam", 1.5)
    c.rot("right_arm", [(0, (0, 0, 0)), (0.5, (-168, 0, 14), "io"), (0.6, (-172, 0, 14), "lin"),
                        (0.9, (-42, 0, 4), "in3"), (1.12, (-40, 0, 4), "lin"), (1.5, (0, 0, 0), "io")])
    c.rot("right_forearm", [(0, (0, 0, 0)), (0.5, (-38, 0, 0)), (0.6, (-40, 0, 0), "lin"),
                            (0.9, (-4, 0, 0), "in3"), (1.12, (-6, 0, 0)), (1.5, (0, 0, 0))])
    c.rot("left_arm", [(0, (0, 0, 0)), (0.5, (-25, 0, -22)), (0.9, (20, 0, -10), "in"), (1.15, (18, 0, -10)),
                       (1.5, (0, 0, 0))])
    c.rot("left_forearm", [(0, (0, 0, 0)), (0.5, (-30, 0, 0)), (0.9, (-12, 0, 0), "in"), (1.5, (0, 0, 0))])
    c.rot("chest", [(0, (0, 0, 0)), (0.55, (-14, 18, -4)), (0.9, (36, -12, 4), "in3"), (1.12, (34, -10, 4)),
                    (1.5, (0, 0, 0))])
    c.rot("neck", [(0, (0, 0, 0)), (0.55, (-6, -8, 0)), (0.9, (-24, 6, 0), "in3"), (1.12, (-22, 6, 0)),
                   (1.5, (0, 0, 0))])
    c.rot("jaw", [(0, (0, 0, 0)), (0.5, (14, 0, 0)), (0.9, (24, 0, 0), "in"), (1.2, (10, 0, 0)), (1.5, (0, 0, 0))])
    c.f("chest", "rotation", lambda t: (shake(t, 22, 1.6) * env(t, 0.9, 0.92, 1.0, 1.2), 0, 0))
    c.rot("body", [(0, (0, 0, 0)), (0.55, (-4, 6, 0)), (0.9, (8, -6, 0), "in3"), (1.12, (8, -6, 0)),
                   (1.5, (0, 0, 0))])
    drop = tl.Track([(0, 0), (0.55, -1.0), (0.9, 5.0, "in3"), (1.12, 5.0), (1.5, 0, "io")])
    legs_for_drop(c, lambda t: float(drop(t)), thigh=9, shin=12)
    c.rot("beard", [(0, (0, 0, 0)), (0.6, (-8, 0, 0)), (0.9, (6, 0, 0), "in"), (1.0, (-14, 0, 0), "out"),
                    (1.25, (5, 0, 0)), (1.5, (0, 0, 0))])
    return c


def anim_ice_spikes():
    c = Clip("attack.ice_spikes", 1.5)
    c.rot("right_arm", [(0, (0, 0, 0)), (0.35, (32, 0, 16), "io"), (0.6, (-84, 0, -4), "snap"),
                        (0.95, (-80, 0, -4)), (1.5, (0, 0, 0), "io")])
    c.rot("right_forearm", [(0, (0, 0, 0)), (0.35, (-52, 0, 0)), (0.6, (2, 0, 0), "snap"), (0.95, (0, 0, 0)),
                            (1.5, (0, 0, 0))])
    c.rot("left_arm", [(0, (0, 0, 0)), (0.35, (-30, 0, -10)), (0.6, (24, 0, -18), "snap"), (0.95, (22, 0, -18)),
                       (1.5, (0, 0, 0))])
    c.rot("left_forearm", [(0, (0, 0, 0)), (0.35, (-35, 0, 0)), (0.6, (-15, 0, 0)), (1.5, (0, 0, 0))])
    c.rot("chest", [(0, (0, 0, 0)), (0.35, (-6, 24, 0)), (0.6, (14, -18, 0), "snap"), (0.95, (13, -16, 0)),
                    (1.5, (0, 0, 0))])
    c.f("right_arm", "rotation", lambda t: (shake(t, 16, 1.5), shake(t, 13, 1.2, 2), 0) if 0.6 < t < 0.95 else (0, 0, 0))
    c.rot("neck", [(0, (0, 0, 0)), (0.35, (-4, -14, 0)), (0.6, (-10, 12, 0), "snap"), (0.95, (-9, 10, 0)),
                   (1.5, (0, 0, 0))])
    c.rot("jaw", [(0, (0, 0, 0)), (0.35, (6, 0, 0)), (0.6, (22, 0, 0), "snap"), (0.95, (18, 0, 0)), (1.5, (0, 0, 0))])
    drop = tl.Track([(0, 0), (0.35, 1.0), (0.6, 3.0, "snap"), (0.95, 3.0), (1.5, 0)])
    legs_for_drop(c, lambda t: float(drop(t)))
    c.rot("right_leg", [(0, (0, 0, 0)), (0.6, (-16, 0, 0), "snap"), (0.95, (-16, 0, 0)), (1.5, (0, 0, 0))])
    c.rot("left_leg", [(0, (0, 0, 0)), (0.6, (12, 0, 0), "snap"), (0.95, (12, 0, 0)), (1.5, (0, 0, 0))])
    return c


def anim_frost_breath():
    c = Clip("attack.frost_breath", 2.5)
    c.rot("chest", [(0, (0, 0, 0)), (0.45, (-14, 0, 0), "io"), (0.6, (16, 0, 0), "snap"),
                    (1.0, (16, -8, 0)), (1.5, (16, 8, 0)), (2.0, (16, -4, 0)), (2.25, (14, 0, 0)), (2.5, (0, 0, 0))])
    c.rot("neck", [(0, (0, 0, 0)), (0.45, (-22, 0, 0), "io"), (0.6, (6, 0, 0), "snap"),
                   (1.0, (6, -18, 0)), (1.5, (6, 18, 0)), (2.0, (6, -8, 0)), (2.25, (4, 0, 0)), (2.5, (0, 0, 0))])
    c.pos("neck", [(0, (0, 0, 0)), (0.45, (0, 0.5, 1)), (0.6, (0, -0.5, -2.5), "snap"), (2.25, (0, -0.5, -2.5)),
                   (2.5, (0, 0, 0))])
    c.rot("jaw", [(0, (0, 0, 0)), (0.45, (10, 0, 0)), (0.55, (36, 0, 0), "snap"), (2.25, (34, 0, 0)),
                  (2.5, (0, 0, 0), "io")])
    c.f("jaw", "rotation", lambda t: (shake(t, 14, 2.0) * env(t, 0.55, 0.6, 2.15, 2.25), 0, 0))
    c.f("neck", "rotation", lambda t: (shake(t, 9, 0.8, 1) * env(t, 0.55, 0.6, 2.15, 2.25), 0, 0))
    for side, nm in ((-1, "right"), (1, "left")):
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.45, (12, 0, -18 * side)), (0.6, (-10, 0, -26 * side), "snap"),
                            (2.25, (-8, 0, -24 * side)), (2.5, (0, 0, 0))])
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.45, (-20, 0, 0)), (0.6, (-34, 0, 0)), (2.25, (-30, 0, 0)),
                                (2.5, (0, 0, 0))])
    c.rot("beard", [(0, (0, 0, 0)), (0.45, (8, 0, 0)), (0.6, (-18, 0, 0), "snap"), (2.25, (-16, 0, 0)),
                    (2.5, (0, 0, 0))])
    c.f("beard", "rotation", lambda t: (shake(t, 11, 3.0, 4) * env(t, 0.6, 0.7, 2.1, 2.25), 0, 0))
    drop = tl.Track([(0, 0), (0.45, -0.5), (0.6, 2.0, "snap"), (2.25, 2.0), (2.5, 0)])
    legs_for_drop(c, lambda t: float(drop(t)))
    return c


def anim_blizzard():
    c = Clip("attack.blizzard", 3.0)
    # arms thrown up into a V, then the torso whirls side to side while the arms circle overhead
    for side, nm in ((-1, "right"), (1, "left")):
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.55, (-20, 0, -150 * side), "io"), (2.55, (-20, 0, -150 * side)),
                            (3.0, (0, 0, 0), "io")])
        c.f(f"{nm}_arm", "rotation", lambda t, side=side: (
            22 * math.sin(TAU * 2 * (t - 0.55) / 2.0) * env(t, 0.55, 0.8, 2.3, 2.55),
            0,
            -12 * side * math.cos(TAU * 2 * (t - 0.55) / 2.0) * env(t, 0.55, 0.8, 2.3, 2.55)))
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.55, (-25, 0, 0)), (2.55, (-25, 0, 0)), (3.0, (0, 0, 0))])
    c.rot("chest", [(0, (0, 0, 0)), (0.3, (8, 0, 0)), (0.55, (-14, 0, 0), "out"), (2.55, (-14, 0, 0)),
                    (3.0, (0, 0, 0))])
    c.f("chest", "rotation", lambda t: (0, 55 * math.sin(TAU * (t - 0.55) / 1.0) * env(t, 0.55, 0.9, 2.2, 2.55), 0))
    c.f("body", "rotation", lambda t: (0, 20 * math.sin(TAU * (t - 0.62) / 1.0) * env(t, 0.55, 0.9, 2.2, 2.55), 0))
    c.rot("neck", [(0, (0, 0, 0)), (0.55, (-26, 0, 0)), (2.55, (-26, 0, 0)), (3.0, (0, 0, 0))])
    c.rot("jaw", [(0, (0, 0, 0)), (0.55, (28, 0, 0)), (2.55, (26, 0, 0)), (3.0, (0, 0, 0))])
    c.f("beard", "rotation", lambda t: (0, 0, 14 * math.sin(TAU * (t - 0.75) / 1.0) * env(t, 0.55, 0.9, 2.2, 2.6)))
    drop = tl.Track([(0, 0), (0.3, 2.0), (0.55, -0.5, "out"), (2.55, -0.5), (3.0, 0)])
    legs_for_drop(c, lambda t: max(0.0, float(drop(t))))
    c.f("body", "position", lambda t: (0, max(0.0, -float(drop(t))) + 0.6 * math.sin(TAU * 2 * t) * env(t, 0.6, 0.9, 2.2, 2.5), 0))
    return c


def anim_phase():
    c = Clip("phase", 2.0)
    c.rot("chest", [(0, (0, 0, 0)), (0.45, (22, 0, 0), "io"), (0.75, (-24, 0, 0), "snap"), (1.5, (-22, 0, 0)),
                    (2.0, (0, 0, 0), "io")])
    c.rot("neck", [(0, (0, 0, 0)), (0.45, (12, 0, 0)), (0.75, (-28, 0, 0), "snap"), (1.5, (-26, 0, 0)),
                   (2.0, (0, 0, 0))])
    c.rot("jaw", [(0, (0, 0, 0)), (0.45, (4, 0, 0)), (0.7, (40, 0, 0), "snap"), (1.55, (38, 0, 0)), (2.0, (0, 0, 0))])
    for side, nm in ((-1, "right"), (1, "left")):
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.45, (-30, 0, 12 * side), "io"), (0.75, (-30, 0, -75 * side), "snap"),
                            (1.5, (-28, 0, -72 * side)), (2.0, (0, 0, 0), "io")])
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.45, (-60, 0, 0)), (0.75, (-38, 0, 0), "snap"),
                                (1.5, (-40, 0, 0)), (2.0, (0, 0, 0))])
    trem = lambda t: env(t, 0.75, 0.8, 1.45, 1.6)
    c.f("chest", "rotation", lambda t: (shake(t, 20, 1.5) * trem(t), shake(t, 17, 1.2, 3) * trem(t), 0))
    c.f("neck", "rotation", lambda t: (shake(t, 23, 1.5, 5) * trem(t), 0, shake(t, 19, 1.2, 1) * trem(t)))
    c.rot("beard", [(0, (0, 0, 0)), (0.45, (10, 0, 0)), (0.75, (-20, 0, 0), "snap"), (1.5, (-14, 0, 0)), (2.0, (0, 0, 0))])
    drop = tl.Track([(0, 0), (0.45, 4.0), (0.75, 0.0, "snap"), (2.0, 0.0)])
    legs_for_drop(c, lambda t: float(drop(t)))
    return c


def anim_death():
    c = Clip("death", 2.8, loop="hold")
    c.rot("chest", [(0, (0, 0, 0)), (0.3, (-18, 0, 0), "out"), (1.1, (26, 0, 6), "io"), (1.7, (40, 0, 8), "in"),
                    (2.8, (40, 0, 8))])
    c.rot("neck", [(0, (0, 0, 0)), (0.3, (-26, 0, 0), "out"), (1.1, (10, 0, -8)), (1.7, (22, 0, -10), "in"),
                   (2.8, (22, 0, -10))])
    c.rot("jaw", [(0, (0, 0, 0)), (0.3, (36, 0, 0), "out"), (1.1, (18, 0, 0)), (1.7, (30, 0, 0)), (2.8, (30, 0, 0))])
    for side, nm in ((-1, "right"), (1, "left")):
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.3, (-40, 0, -50 * side), "out"), (1.1, (-10, 0, -14 * side)),
                            (1.7, (-35, 0, -20 * side), "in"), (2.8, (-35, 0, -20 * side))])
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.3, (-30, 0, 0)), (1.1, (-10, 0, 0)), (1.7, (-5, 0, 0)),
                                (2.8, (-5, 0, 0))])
    # kneel then topple forward
    drop = tl.Track([(0, 0), (0.3, -0.5, "out"), (1.1, 11.0, "io"), (2.8, 11.0)])
    legs_for_drop(c, lambda t: float(drop(t)), body=None)
    c.f("body", "position", lambda t: (0, -max(0.0, float(drop(t))), 0))
    c.rot("body", [(0, (0, 0, 0)), (1.1, (6, 0, 0)), (1.75, (34, 0, 0), "in"), (2.8, (34, 0, 0))])
    c.pos("body", [(0, (0, 0, 0)), (1.1, (0, 0, 0)), (1.75, (0, -3, -4), "in"), (2.8, (0, -3, -4))])
    # shatter: limbs and head burst apart and shrink into shards
    burst = lambda t: tl.ease("out", (t - 1.85) / 0.6) if t > 1.85 else 0.0
    gone = lambda t: 1 - tl.ease("in", (t - 2.15) / 0.6) if t > 2.15 else 1.0
    c.f("right_arm", "position", lambda t: (-7 * burst(t), -3 * burst(t), -2 * burst(t)))
    c.f("left_arm", "position", lambda t: (7 * burst(t), -3 * burst(t), -2 * burst(t)))
    c.f("head", "position", lambda t: (0, 2 * burst(t), -4 * burst(t)))
    for b in ("chest", "right_arm", "left_arm", "head", "right_leg", "left_leg", "body"):
        c.f(b, "scale", lambda t: (gone(t),) * 3)
    c.f("chest", "rotation", lambda t: (shake(t, 25, 2.0) * env(t, 1.7, 1.75, 2.0, 2.2), 0, 0))
    return c


def clips():
    return [anim_idle(), anim_walk(), anim_slam(), anim_ice_spikes(), anim_frost_breath(), anim_blizzard(),
            anim_phase(), anim_death()]


POSES = [
    ("idle", [0.0, 0.75, 1.5]),
    ("walk", [0.0, 0.4, 0.8, 1.2]),
    ("attack.slam", [0.3, 0.55, 0.9, 1.3]),
    ("attack.ice_spikes", [0.35, 0.6, 0.9]),
    ("attack.frost_breath", [0.45, 0.7, 1.5]),
    ("attack.blizzard", [0.55, 1.0, 1.8]),
    ("phase", [0.45, 0.8, 1.2]),
    ("death", [0.3, 1.1, 1.8, 2.4]),
]


def main():
    m = build_model()
    geo, rgba, glow, anims = tl.build(NAME, m, SHADERS, clips(), visible=(5, 6, 2.5))
    if "--preview" in sys.argv:
        sel = POSES if "--all" in sys.argv else POSES[:3]
        for p in tl.previews(NAME, geo, rgba, glow, anims, HITBOX, sel, frame=(120, 84)):
            print("preview", p)


if __name__ == "__main__":
    main()
