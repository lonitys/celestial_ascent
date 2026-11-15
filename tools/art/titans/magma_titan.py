"""Magma Titan: a hunched, gorilla-like colossus of cracked black basalt plates over molten lava
flesh, with smoldering shoulder vents, a crown of flame-shaped obsidian spikes, huge fists and a
glowing chest furnace.

Run: python magma_titan.py [--preview [--all]]
"""
import math
import sys

import numpy as np

import titanlib as tl
from titanlib import (Clip, edge_term, env, fbm, hash3, palette, ramp, shake, vgrad, worley, vnoise)
from anim_helpers import TAU, legs_for_drop

NAME = "magma_titan"
HITBOX = (2.4, 4.6)
THIGH, SHIN = 10.0, 12.0

# =============================================================================== geometry


def build_model():
    m = tl.Model(NAME)
    body = m.bone("body", "root", (0, 22, 1))
    body.boxb(0, 18, 1, 22, 10, 15, "basalt")                                    # pelvis
    body.box((0, 15.5, -6.9), (12, 8, 2), "plate", rot=[-8, 0, 0])              # front fauld
    body.box((-10.5, 17, -0.5), (2, 8, 12), "plate", rot=[0, 0, 10])            # hip plates
    body.box((10.5, 17, -0.5), (2, 8, 12), "plate", rot=[0, 0, -10])

    chest = m.bone("chest", "body", (0, 27, 1), rotation=[18, 0, 0])
    chest.boxb(0, 25, 0.5, 22, 11, 16, "lava")                                   # molten belly
    chest.box((-5.5, 30.5, -7.8), (9, 4, 2), "plate", rot=[4, 8, 0])            # belly plates
    chest.box((5.5, 30.5, -7.8), (9, 4, 2), "plate", rot=[4, -8, 0])
    chest.box((0, 26.6, -7.6), (12, 3, 2), "plate", rot=[6, 0, 0])
    chest.boxb(0, 35, 1, 30, 20, 20, "basalt")                                   # massive chest
    chest.box((0, 45.0, -9.2), (12, 10, 2), "furnace")                          # furnace mouth
    for x in (-3.6, 0.0, 3.6):
        chest.box((x, 45.0, -10.0), (2, 11, 1), "obsidian", inflate=0.1)        # grate bars
    chest.box((0, 50.6, -10.2), (14, 2, 2), "obsidian")                         # furnace lintel
    chest.box((0, 39.4, -10.2), (14, 2, 2), "obsidian")
    chest.box((-10.6, 47.5, -9.4), (9, 9, 3), "plate", rot=[-8, 16, 0])         # pec plates
    chest.box((10.6, 47.5, -9.4), (9, 9, 3), "plate", rot=[-8, -16, 0])
    chest.boxb(0, 53, 5.0, 24, 8, 15, "basalt")                                 # back hump
    # volcanic vents on the hump
    for x, z, s in ((-6.5, 8.5, 1.0), (6.0, 9.5, 0.85)):
        chest.boxb(x, 60, z, round(8 * s), 4, round(8 * s), "vent")
        chest.boxb(x, 63.5, z, round(5 * s), 3, round(5 * s), "vent", crater=True)
    chest.box((0, 42, 11.5), (18, 14, 2), "plate")                               # back plate

    neck = m.bone("neck", "chest", (0, 52, -6), rotation=[-18, 0, 0])
    head = m.bone("head", "neck", (0, 52, -9))
    head.boxb(0, 49, -13, 14, 10, 12, "basalt")                                  # wide flat skull
    head.box((0, 56.6, -19.4), (16, 3, 4), "obsidian", rot=[16, 0, 0])          # heavy brow
    head.box((-3.7, 54.6, -19.2), (3, 1, 1), "eye", inflate=0.12)
    head.box((3.7, 54.6, -19.2), (3, 1, 1), "eye", inflate=0.12)
    head.box((0, 52.5, -19.4), (4, 3, 2), "plate")                              # snout plate
    # crown of flame-shaped obsidian spikes curling back
    crown = [((0, 58.6, -15.5), [(0, 1, -0.15), (0, 1, 0.25), (0, 1, 0.8)], [6, 5, 4], [4, 3, 2]),
             ((-4.6, 58.4, -14.0), [(-0.2, 1, -0.1), (-0.35, 1, 0.35), (-0.4, 0.9, 0.9)], [5, 4, 3], [3, 3, 2]),
             ((4.6, 58.4, -14.0), [(0.2, 1, -0.1), (0.35, 1, 0.35), (0.4, 0.9, 0.9)], [5, 4, 3], [3, 3, 2]),
             ((-6.2, 58.0, -9.0), [(-0.6, 1, 0.1), (-0.7, 0.9, 0.6)], [5, 4], [3, 2]),
             ((6.2, 58.0, -9.0), [(0.6, 1, 0.1), (0.7, 0.9, 0.6)], [5, 4], [3, 2])]
    for base, dirs, lens, ws in crown:
        head.curve_spike(base, dirs, lens, ws, "flame")
    jaw = m.bone("jaw", "head", (0, 51, -9))
    jaw.boxb(0, 45.0, -13.5, 13, 4, 11, "basalt")
    jaw.box((0, 47.6, -18.6), (11, 2, 1), "lava")                               # molten maw
    jaw.spike((-4.2, 48.5, -18.2), (-0.1, 1, -0.2), 4, 2, "obsidian", segs=[1.0])  # tusks
    jaw.spike((4.2, 48.5, -18.2), (0.1, 1, -0.2), 4, 2, "obsidian", segs=[1.0])

    for side, nm in ((-1, "right"), (1, "left")):
        s = side
        arm = m.bone(f"{nm}_arm", "chest", (16 * s, 50, 1), rotation=[-18, 0, -6 * s])
        arm.boxb(20 * s, 34, 1, 11, 15, 12, "basalt")                           # upper arm
        arm.box((20.5 * s, 50.5, 1), (14, 11, 15), "ember", rot=[0, 0, -10 * s])  # smoldering shoulder boulder
        arm.boxb(21.5 * s, 56, 1, 8, 4, 8, "vent")                              # shoulder vent
        arm.boxb(21.8 * s, 59.5, 1, 5, 3, 5, "vent", crater=True)
        arm.box((26.8 * s, 47.5, 1), (3, 7, 13), "plate", rot=[0, 0, -18 * s])  # outer plate
        fore = m.bone(f"{nm}_forearm", f"{nm}_arm", (20 * s, 35, 1), rotation=[-10, 0, 0])
        fore.boxb(20.5 * s, 20, 0.5, 12, 15, 13, "basalt")                      # forearm
        fore.box((26.8 * s, 27.5, 0.5), (2, 10, 11), "plate", rot=[0, 0, -4 * s])
        fore.spike((26.5 * s, 31, 0.5), (1.0 * s, 0.5, 0), 5, 3, "obsidian", segs=[1.0])
        fore.spike((26.5 * s, 25, 2.5), (1.0 * s, 0.3, 0.3), 4, 2, "obsidian", segs=[1.0])
        fore.boxb(21 * s, 4, 0, 15, 14, 15, "fist")                             # huge fist
        fore.box((21 * s, 9.5, -7.9), (14, 6, 2), "obsidian")                   # knuckle guard
        for x in (16.5, 21.0, 25.5):
            fore.spike((x * s, 9.5, -8.6), (0, 0.15, -1.0), 4, 3, "obsidian", segs=[1.0])
        fore.box((13.0 * s, 12.5, -4.0), (3, 6, 5), "fist")                     # thumb

        leg = m.bone(f"{nm}_leg", "root", (8 * s, 22, 1))
        leg.boxb(8 * s, 12, 1, 12, 11, 12, "basalt")                            # thigh
        leg.box((8.2 * s, 18.5, -5.5), (10, 6, 2), "plate", rot=[-8, 0, 0])
        shin = m.bone(f"{nm}_shin", f"{nm}_leg", (8 * s, 12, 1))
        shin.boxb(8 * s, 3, 1.5, 11, 10, 11, "lava_limb")
        shin.box((8 * s, 11.5, -5.2), (10, 6, 3), "plate", rot=[-12, 0, 0])     # knee plate
        shin.box((8 * s, 6.5, -4.8), (9, 6, 2), "plate")                        # greave
        shin.box((13.6 * s, 7.0, 1.5), (2, 8, 9), "plate")                      # outer greave
        foot = m.bone(f"{nm}_foot", f"{nm}_shin", (8 * s, 3.5, 1.5))
        foot.boxb(8 * s, 0, -1, 14, 4, 15, "basalt")
        for x in (4.0, 8.0, 12.0):
            foot.box((x * s, 1.5, -9.2), (3, 3, 3), "obsidian")                 # toe claws
    return m

# =============================================================================== shaders


BASALT = palette("#0b0909", "#121010", "#1a1716", "#231f1d", "#2d2826", "#383230", "#463e3b", "#574d48")
LAVA = palette("#5c0a00", "#8a1500", "#bb2400", "#e23b00", "#ff5800", "#ff7d0a", "#ffa224", "#ffc847", "#ffe98a")
OBSID = palette("#07040b", "#0e0816", "#160d22", "#1f1330", "#2a1a41", "#382456", "#4b316f", "#62438c")
ASH = palette("#3a3533", "#504945", "#6a625c", "#867c74")
EYE = palette("#ff8a00", "#ffc23a", "#fff09a")


def _th(ctx, seed):
    p = ctx.p
    return hash3(np.floor(p[:, 0] * 2 + 0.01), np.floor(p[:, 1] * 2 + 0.01), np.floor(p[:, 2] * 2 + 0.01), seed)


def lava_rgb(ctx, heat=0.0):
    p = ctx.p
    flow = fbm(p + np.array([0, 0, 0]), 0.16, 3, 51)
    v = 0.45 + (flow - 0.5) * 0.9 + heat
    v += (np.sin(p[:, 1] * 0.9 + flow * 7) > 0.6) * 0.12
    return ramp(LAVA, v), v


def shade_basalt(ctx, seams=0.07, plate=False, fist=False):
    p = ctx.p
    f1, f2, cid = worley(p, 0.13 if not fist else 0.17, 23)
    # each cell is a basalt plate; plates bevel lighter at their upper edge
    d = f2 - f1
    v = 0.42 + (cid - 0.5) * 0.25 + (fbm(p, 0.2, 3, 3) - 0.5) * 0.3
    v += np.clip(d, 0, 0.3) * 0.5                                         # raised plate centres
    v += (np.sin((p[:, 0] + p[:, 2]) * 1.6 + cid * 9) > 0.92) * 0.08       # columnar striations
    v += (_th(ctx, 2) - 0.5) * 0.06
    v += edge_term(ctx, 0.16 if plate else 0.1, 0.14, 0.05) + vgrad(ctx, 0.1) - ctx.ao * 0.5
    v += 0.1 * max(0, ctx.nw[1]) - 0.08 * max(0, -ctx.nw[1])
    rgb = ramp(BASALT, v)
    # glowing lava seams between the plates (wider low on the body / fists)
    gate = fbm(p, 0.09, 2, 29) > (0.42 if not plate else 0.62)
    seam = (d < seams) & gate
    hot = (d < seams * 0.45) & gate
    halo = (d < seams * 2.2) & gate & ~seam
    rgb[halo] = rgb[halo] * 0.6 + np.array([150, 35, 0]) * 0.4
    lr, _ = lava_rgb(ctx, 0.0)
    rgb[seam] = lr[seam]
    lh, _ = lava_rgb(ctx, 0.3)
    rgb[hot] = lh[hot]
    # hairline cracks
    g1, g2, _ = worley(p, 0.35, 61)
    crack = ((g2 - g1) < 0.035) & (fbm(p, 0.3, 2, 62) > 0.6) & ~seam
    rgb[crack] = LAVA[3]
    return rgb, 255, seam | crack


def shade_lava(ctx, limb=False):
    p = ctx.p
    rgb, v = lava_rgb(ctx, 0.05)
    # cooling crust islands floating on the molten flesh
    f1, f2, cid = worley(p, 0.22 if not limb else 0.16, 81)
    crust = (f1 < (0.32 if not limb else 0.45)) & (cid > 0.3)
    cv = 0.35 + (cid - 0.5) * 0.3 + edge_term(ctx, 0.1, 0.1) - ctx.ao * 0.4 + (fbm(p, 0.4, 2, 5) - 0.5) * 0.3
    rgb[crust] = ramp(BASALT, cv[crust])
    rim = (f1 >= (0.32 if not limb else 0.45)) & (f1 < (0.38 if not limb else 0.52)) & (cid > 0.3)
    rgb[rim] = LAVA[2]
    glow = ~crust
    return rgb, 255, glow


def shade_obsidian(ctx, flame=False):
    p = ctx.p
    v = 0.4 + (fbm(p, 0.3, 2, 9) - 0.5) * 0.3
    if ctx.face not in ("up", "down"):
        v += np.where(ctx.s < 0.4, 0.14, -0.06) + (np.abs(ctx.s - 0.4) < 0.06) * 0.2   # glassy facet ridge
    v += edge_term(ctx, 0.3, 0.1, 0.08) - ctx.ao * 0.4
    rgb = ramp(OBSID, v)
    sheen = (_th(ctx, 12) > 0.975)
    rgb[sheen] = OBSID[-1]
    glow = np.zeros(ctx.N, dtype=bool)
    if flame:
        prm = ctx.params
        # heat rises through the flame: hot glowing core near the tip, embers along the edge
        prog = prm["curve_prog0"] + (prm["curve_prog1"] - prm["curve_prog0"]) * (1 - ctx.t)
        if ctx.face in ("up",):
            prog = np.full(ctx.N, prm["curve_prog1"])
        if ctx.face in ("down",):
            prog = np.full(ctx.N, prm["curve_prog0"])
        hot = prog > 0.62
        lv = 0.35 + (prog - 0.62) * 2.0 + (fbm(p, 0.5, 2, 4) - 0.5) * 0.3
        rgb[hot] = ramp(LAVA, lv[hot])
        edge = (ctx.i == 0) | (ctx.i == ctx.tw - 1)
        lick = edge & (prog > 0.35) & ~hot
        rgb[lick] = LAVA[4]
        glow = hot | lick
    return rgb, 255, glow


def shade_furnace(ctx):
    p = ctx.p
    if ctx.face != "north":
        return shade_obsidian(ctx)
    x = (ctx.s - 0.5) * 2
    y = (0.5 - ctx.t) * 2
    r = np.sqrt(x * x * 0.8 + y * y)
    v = 0.95 - r * 0.45 + (fbm(p, 0.6, 2, 7) - 0.5) * 0.25
    rgb = ramp(LAVA, v)
    hot = r < 0.45
    rgb[hot] = ramp(LAVA, 0.88 + 0 * r[hot])
    rgb[r < 0.22] = np.array([255, 250, 210])
    return rgb, 255, True


def shade_vent(ctx):
    rgb, a, glow = shade_basalt(ctx, seams=0.05)
    if ctx.params.get("crater") and ctx.face == "up":
        x = (ctx.s - 0.5) * 2
        y = (ctx.t - 0.5) * 2
        r = np.maximum(np.abs(x), np.abs(y))
        pit = r < 0.72
        lv = 0.95 - r * 0.6
        rgb[pit] = ramp(LAVA, lv[pit])
        glow = glow | pit
    elif ctx.face not in ("up", "down"):
        # lava dribbling down the sides from the rim
        p = ctx.p
        col = hash3(np.floor((p[:, 0] + p[:, 2]) * 1.5), 0, 0, 5)
        drip = (ctx.t < 0.15 + col * (0.85 if ctx.params.get("crater") else 0.5)) & (col > 0.55)
        lr, _ = lava_rgb(ctx, 0.1)
        rgb[drip] = lr[drip]
        glow = glow | drip
    return rgb, 255, glow


def shade_ember(ctx):
    rgb, a, glow = shade_basalt(ctx, seams=0.06)
    p = ctx.p
    ash = (fbm(p, 0.25, 3, 41) > 0.6) & ~glow
    av = 0.4 + (fbm(p, 0.7, 2, 3) - 0.5) * 0.6 + edge_term(ctx, 0.15)
    rgb[ash] = ramp(ASH, av[ash])
    em = (_th(ctx, 45) > 0.95) & (max(0, ctx.nw[1]) > 0.2) | ((_th(ctx, 46) > 0.982) & ~glow)
    rgb[em] = np.where(_th(ctx, 47)[em, None] > 0.5, LAVA[6], LAVA[4])
    return rgb, 255, glow | em


def shade_eye(ctx):
    v = 0.45 + (ctx.face == "north") * 0.4 - (np.abs(ctx.s - 0.5) > 0.32) * 0.25
    return ramp(EYE, v), 255, True


SHADERS = {
    "basalt": shade_basalt,
    "plate": lambda c: shade_basalt(c, seams=0.04, plate=True),
    "fist": lambda c: shade_basalt(c, seams=0.09, fist=True),
    "lava": shade_lava,
    "lava_limb": lambda c: shade_lava(c, limb=True),
    "obsidian": shade_obsidian,
    "flame": lambda c: shade_obsidian(c, flame=True),
    "furnace": shade_furnace,
    "vent": shade_vent,
    "ember": shade_ember,
    "eye": shade_eye,
}

# =============================================================================== animations


def anim_idle():
    T = 3.0
    c = Clip("idle", T, loop=True)
    w = lambda t, ph=0.0: math.sin(TAU * t / T + ph)
    c.f("chest", "rotation", lambda t: (-2.0 * w(t), 0, 0.8 * w(t, 1.3)))
    c.f("chest", "position", lambda t: (0, 0.45 * w(t), 0))
    c.f("body", "position", lambda t: (0, -0.3 * (1 - math.cos(TAU * t / T)) / 2, 0))
    c.f("right_arm", "rotation", lambda t: (2.0 * w(t, 0.8), 0, 1.5 * w(t, 0.3)))
    c.f("left_arm", "rotation", lambda t: (2.0 * w(t, 1.0), 0, -1.5 * w(t, 0.3)))
    c.f("right_forearm", "rotation", lambda t: (-3.0 * w(t, 1.3), 0, 0))
    c.f("left_forearm", "rotation", lambda t: (-3.0 * w(t, 1.5), 0, 0))
    c.f("neck", "rotation", lambda t: (1.6 * w(t, 0.9), 3.0 * w(t, 0.1), 0))
    c.f("jaw", "rotation", lambda t: (2.5 + 2.5 * w(t, -0.4), 0, 0))
    return c


def anim_walk():
    T = 1.6
    c = Clip("walk", T, loop=True)
    ph = lambda t: TAU * t / T
    sn = lambda t: math.sin(ph(t))
    c.f("right_leg", "rotation", lambda t: (-22 * sn(t), 0, 0))
    c.f("left_leg", "rotation", lambda t: (22 * sn(t), 0, 0))
    kr = lambda t: 30 * max(0.0, math.cos(ph(t))) ** 1.3
    kl = lambda t: 30 * max(0.0, -math.cos(ph(t))) ** 1.3
    c.f("right_shin", "rotation", lambda t: (kr(t), 0, 0))
    c.f("left_shin", "rotation", lambda t: (kl(t), 0, 0))
    c.f("right_foot", "rotation", lambda t: (22 * sn(t) - kr(t), 0, 0))
    c.f("left_foot", "rotation", lambda t: (-22 * sn(t) - kl(t), 0, 0))
    c.f("body", "position", lambda t: (0, 0.8 - 2.8 * sn(t) ** 4, 0))
    c.f("body", "rotation", lambda t: (0, 6 * sn(t), -5 * sn(t)))
    c.f("chest", "rotation", lambda t: (3 + 3 * sn(t) ** 4, -9 * sn(t), 3 * sn(t)))
    # gorilla arm swing: big, heavy, slightly lagging
    c.f("right_arm", "rotation", lambda t: (24 * math.sin(ph(t) - 0.35), 0, 3 + 3 * sn(t) ** 2))
    c.f("left_arm", "rotation", lambda t: (-24 * math.sin(ph(t) - 0.35), 0, -3 - 3 * sn(t) ** 2))
    c.f("right_forearm", "rotation", lambda t: (-6 - 10 * max(0.0, -math.sin(ph(t) - 0.8)), 0, 0))
    c.f("left_forearm", "rotation", lambda t: (-6 - 10 * max(0.0, math.sin(ph(t) - 0.8)), 0, 0))
    c.f("neck", "rotation", lambda t: (-2 - 3 * sn(t) ** 4, 4 * sn(t), 4 * sn(t)))
    c.f("jaw", "rotation", lambda t: (3 + 3 * math.sin(2 * ph(t) - 0.6), 0, 0))
    return c


def anim_meteor():
    c = Clip("attack.meteor", 2.5)
    for side, nm in ((-1, "right"), (1, "left")):
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.4, (20, 0, -14 * side), "io"), (0.75, (-172, 0, -16 * side), "snap"),
                            (1.45, (-168, 0, -14 * side)), (2.5, (0, 0, 0), "io")])
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.4, (-40, 0, 0)), (0.75, (-6, 0, 0), "snap"), (1.45, (-8, 0, 0)),
                                (2.5, (0, 0, 0))])
    trem = lambda t: env(t, 0.75, 0.85, 1.35, 1.5)
    for b in ("right_arm", "left_arm"):
        c.f(b, "rotation", lambda t, b=b: (shake(t, 21, 2.5, len(b)) * trem(t), 0, shake(t, 18, 2.0, 3 + len(b)) * trem(t)))
    c.rot("chest", [(0, (0, 0, 0)), (0.4, (14, 0, 0)), (0.75, (-26, 0, 0), "snap"), (1.45, (-24, 0, 0)), (2.5, (0, 0, 0))])
    c.rot("neck", [(0, (0, 0, 0)), (0.4, (8, 0, 0)), (0.75, (-36, 0, 0), "snap"), (1.45, (-34, 0, 0)), (2.5, (0, 0, 0))])
    c.rot("jaw", [(0, (0, 0, 0)), (0.4, (6, 0, 0)), (0.75, (38, 0, 0), "snap"), (1.45, (36, 0, 0)), (2.5, (0, 0, 0))])
    drop = tl.Track([(0, 0), (0.4, 6.0, "io"), (0.75, -1.0, "snap"), (1.45, -1.0), (2.5, 0, "io")])
    legs_for_drop(c, lambda t: max(0.0, float(drop(t))), thigh=THIGH, shin=SHIN)
    c.f("body", "position", lambda t: (0, max(0.0, -float(drop(t))), 0))
    return c


def anim_eruption():
    c = Clip("attack.eruption", 1.8)
    for side, nm in ((-1, "right"), (1, "left")):
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.7, (-175, 0, 8 * side), "io"), (1.0, (-50, 0, 2 * side), "in3"),
                            (1.25, (-48, 0, 2 * side)), (1.8, (0, 0, 0), "io")])
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.7, (-30, 0, 0)), (1.0, (0, 0, 0), "in3"), (1.25, (0, 0, 0)), (1.8, (0, 0, 0))])
    c.rot("chest", [(0, (0, 0, 0)), (0.7, (-22, 0, 0), "io"), (1.0, (26, 0, 0), "in3"), (1.25, (25, 0, 0)), (1.8, (0, 0, 0))])
    c.f("chest", "rotation", lambda t: (shake(t, 24, 2.0) * env(t, 1.0, 1.02, 1.12, 1.3), shake(t, 19, 1.5, 2) * env(t, 1.0, 1.02, 1.12, 1.3), 0))
    c.rot("neck", [(0, (0, 0, 0)), (0.7, (-14, 0, 0)), (1.0, (-22, 0, 0), "in3"), (1.25, (-20, 0, 0)), (1.8, (0, 0, 0))])
    c.rot("jaw", [(0, (0, 0, 0)), (0.7, (24, 0, 0)), (1.0, (34, 0, 0), "in"), (1.3, (14, 0, 0)), (1.8, (0, 0, 0))])
    drop = tl.Track([(0, 0), (0.7, -1.5, "io"), (1.0, 9.0, "in3"), (1.25, 9.0), (1.8, 0, "io")])
    legs_for_drop(c, lambda t: max(0.0, float(drop(t))), thigh=THIGH, shin=SHIN, spread=1.0)
    c.f("body", "position", lambda t: (0, max(0.0, -float(drop(t))), 0))
    return c


def anim_flame_breath():
    c = Clip("attack.flame_breath", 2.5)
    c.rot("chest", [(0, (0, 0, 0)), (0.5, (-12, 0, 0), "io"), (0.62, (12, 0, 0), "snap"),
                    (1.1, (12, -12, 0)), (1.6, (12, 12, 0)), (2.05, (12, -4, 0)), (2.25, (10, 0, 0)), (2.5, (0, 0, 0))])
    c.rot("neck", [(0, (0, 0, 0)), (0.5, (-26, 0, 0), "io"), (0.62, (8, 0, 0), "snap"),
                   (1.1, (8, -20, 0)), (1.6, (8, 20, 0)), (2.05, (8, -8, 0)), (2.25, (6, 0, 0)), (2.5, (0, 0, 0))])
    c.pos("neck", [(0, (0, 0, 0)), (0.5, (0, 0.5, 1.5)), (0.62, (0, -0.5, -2.5), "snap"), (2.25, (0, -0.5, -2.5)), (2.5, (0, 0, 0))])
    c.rot("jaw", [(0, (0, 0, 0)), (0.5, (12, 0, 0)), (0.6, (40, 0, 0), "snap"), (2.25, (38, 0, 0)), (2.5, (0, 0, 0))])
    c.f("jaw", "rotation", lambda t: (shake(t, 13, 2.2) * env(t, 0.6, 0.65, 2.15, 2.25), 0, 0))
    # brace on the knuckles
    for side, nm in ((-1, "right"), (1, "left")):
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.5, (14, 0, -14 * side)), (0.62, (-26, 0, -12 * side), "snap"),
                            (2.25, (-24, 0, -12 * side)), (2.5, (0, 0, 0))])
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.5, (-24, 0, 0)), (0.62, (6, 0, 0)), (2.25, (6, 0, 0)), (2.5, (0, 0, 0))])
    drop = tl.Track([(0, 0), (0.5, -0.5), (0.62, 3.5, "snap"), (2.25, 3.5), (2.5, 0)])
    legs_for_drop(c, lambda t: max(0.0, float(drop(t))), thigh=THIGH, shin=SHIN)
    return c


def anim_lava_pool():
    c = Clip("attack.lava_pool", 1.5)
    # lift the right foot high, shift weight left, then stomp at 0.8
    c.rot("right_leg", [(0, (0, 0, 0)), (0.55, (-58, 0, 6), "io"), (0.8, (-4, 0, 0), "in3"), (1.05, (-4, 0, 0)), (1.5, (0, 0, 0))])
    c.rot("right_shin", [(0, (0, 0, 0)), (0.55, (62, 0, 0), "io"), (0.8, (10, 0, 0), "in3"), (1.05, (10, 0, 0)), (1.5, (0, 0, 0))])
    c.rot("right_foot", [(0, (0, 0, 0)), (0.55, (-10, 0, 0)), (0.8, (-6, 0, 0), "in3"), (1.5, (0, 0, 0))])
    c.pos("right_leg", [(0, (0, 0, 0)), (0.55, (0, 2.5, 0)), (0.8, (0, -1.5, 0), "in3"), (1.05, (0, -1.5, 0)), (1.5, (0, 0, 0))])
    c.rot("left_leg", [(0, (0, 0, 0)), (0.55, (-6, 0, -4)), (0.8, (-14, 0, 0), "in3"), (1.05, (-14, 0, 0)), (1.5, (0, 0, 0))])
    c.rot("left_shin", [(0, (0, 0, 0)), (0.55, (10, 0, 0)), (0.8, (28, 0, 0), "in3"), (1.05, (28, 0, 0)), (1.5, (0, 0, 0))])
    c.rot("left_foot", [(0, (0, 0, 0)), (0.55, (-4, 0, 0)), (0.8, (-14, 0, 0), "in3"), (1.05, (-14, 0, 0)), (1.5, (0, 0, 0))])
    c.pos("left_leg", [(0, (0, 0, 0)), (0.8, (0, -1.5, 0), "in3"), (1.05, (0, -1.5, 0)), (1.5, (0, 0, 0))])
    c.rot("body", [(0, (0, 0, 0)), (0.55, (-6, 0, 9), "io"), (0.8, (8, 0, -3), "in3"), (1.05, (7, 0, -2)), (1.5, (0, 0, 0))])
    c.pos("body", [(0, (0, 0, 0)), (0.55, (1.5, 1.5, 0)), (0.8, (0, -2.5, 0), "in3"), (1.05, (0, -2.5, 0)), (1.5, (0, 0, 0))])
    c.f("chest", "rotation", lambda t: (shake(t, 24, 2.2) * env(t, 0.8, 0.82, 0.95, 1.15), 0, shake(t, 20, 1.8, 2) * env(t, 0.8, 0.82, 0.95, 1.15)))
    c.rot("chest", [(0, (0, 0, 0)), (0.55, (-10, 0, 4)), (0.8, (12, 0, 0), "in3"), (1.05, (10, 0, 0)), (1.5, (0, 0, 0))])
    for side, nm in ((-1, "right"), (1, "left")):
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.55, (-30, 0, -40 * side)), (0.8, (-10, 0, -14 * side), "in3"), (1.05, (-10, 0, -14 * side)),
                            (1.5, (0, 0, 0))])
    c.rot("neck", [(0, (0, 0, 0)), (0.55, (-12, 0, 0)), (0.8, (-20, 0, 0), "in3"), (1.5, (0, 0, 0))])
    c.rot("jaw", [(0, (0, 0, 0)), (0.55, (10, 0, 0)), (0.8, (32, 0, 0), "in3"), (1.1, (14, 0, 0)), (1.5, (0, 0, 0))])
    return c


def anim_phase():
    c = Clip("phase", 2.0)
    # rears up and pounds its chest (four beats) then roars
    c.rot("chest", [(0, (0, 0, 0)), (0.35, (-20, 0, 0), "io"), (1.45, (-22, 0, 0)), (1.6, (-28, 0, 0), "snap"), (2.0, (0, 0, 0), "io")])
    c.rot("neck", [(0, (0, 0, 0)), (0.35, (-10, 0, 0)), (1.45, (-12, 0, 0)), (1.6, (-34, 0, 0), "snap"), (2.0, (0, 0, 0))])
    c.rot("jaw", [(0, (0, 0, 0)), (0.35, (20, 0, 0)), (1.4, (16, 0, 0)), (1.55, (44, 0, 0), "snap"), (1.85, (40, 0, 0)), (2.0, (0, 0, 0))])
    beats = [0.5, 0.75, 1.0, 1.25]
    for k, (side, nm) in enumerate(((-1, "right"), (1, "left"))):
        keys = [(0, (0, 0, 0)), (0.35, (-60, 30 * side, -10 * side), "io")]
        for i, tb in enumerate(beats):
            mine = (i % 2) == k
            if mine:
                keys += [(tb - 0.1, (-85, 55 * side, -30 * side), "out"), (tb, (-78, -10 * side, -4 * side), "in")]
            else:
                keys += [(tb, (-70, 40 * side, -20 * side), "io")]
        keys += [(1.45, (-60, 30 * side, -10 * side)), (1.6, (-30, 0, -70 * side), "snap"), (1.85, (-28, 0, -66 * side)), (2.0, (0, 0, 0), "io")]
        c.rot(f"{nm}_arm", keys)
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.35, (-70, 0, 0)), (1.45, (-70, 0, 0)), (1.6, (-30, 0, 0), "snap"), (2.0, (0, 0, 0))])
    c.f("chest", "rotation", lambda t: (sum(2.5 * env(t, tb - 0.01, tb, tb + 0.02, tb + 0.12) for tb in beats), 0, 0))
    trem = lambda t: env(t, 1.6, 1.65, 1.85, 1.95)
    c.f("neck", "rotation", lambda t: (shake(t, 23, 1.5, 5) * trem(t), 0, shake(t, 19, 1.2, 1) * trem(t)))
    drop = tl.Track([(0, 0), (0.35, -1.0), (1.45, -1.0), (1.6, 2.0, "snap"), (2.0, 0)])
    legs_for_drop(c, lambda t: max(0.0, float(drop(t))), thigh=THIGH, shin=SHIN)
    c.f("body", "position", lambda t: (0, max(0.0, -float(drop(t))), 0))
    return c


def anim_death():
    c = Clip("death", 2.8, loop="hold")
    # roars, knees buckle, slumps onto its fists, then crumbles and sinks into molten rock
    c.rot("chest", [(0, (0, 0, 0)), (0.3, (-20, 0, 0), "out"), (1.1, (14, 0, -6)), (1.7, (26, 0, -8), "in"), (2.8, (30, 0, -8))])
    c.rot("neck", [(0, (0, 0, 0)), (0.3, (-30, 0, 0), "out"), (1.1, (6, 0, 6)), (1.7, (20, 0, 10), "in"), (2.8, (24, 0, 10))])
    c.rot("jaw", [(0, (0, 0, 0)), (0.3, (42, 0, 0), "out"), (1.1, (20, 0, 0)), (1.7, (30, 0, 0)), (2.8, (30, 0, 0))])
    for side, nm in ((-1, "right"), (1, "left")):
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.3, (-40, 0, -45 * side), "out"), (1.1, (-14, 0, -8 * side)),
                            (1.7, (-30, 0, -6 * side), "in"), (2.8, (-30, 0, -6 * side))])
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.3, (-30, 0, 0)), (1.1, (-6, 0, 0)), (1.7, (6, 0, 0)), (2.8, (6, 0, 0))])
    drop = tl.Track([(0, 0), (0.3, -0.5, "out"), (1.1, 9.0, "io"), (2.8, 9.0)])
    legs_for_drop(c, lambda t: float(drop(t)), thigh=THIGH, shin=SHIN)
    c.rot("body", [(0, (0, 0, 0)), (1.1, (4, 0, 0)), (1.75, (16, 0, 0), "in"), (2.8, (16, 0, 0))])
    c.f("chest", "rotation", lambda t: (shake(t, 25, 1.6) * env(t, 1.7, 1.75, 2.4, 2.6), 0, shake(t, 21, 1.2, 2) * env(t, 1.7, 1.75, 2.4, 2.6)))
    sink = lambda t: tl.ease("in", (t - 1.8) / 1.0) if t > 1.8 else 0.0
    c.f("root", "position", lambda t: (0, -16 * sink(t), 0))
    c.f("root", "scale", lambda t: (1 + 0.15 * sink(t), 1 - 0.55 * sink(t), 1 + 0.15 * sink(t)))
    return c


def clips():
    return [anim_idle(), anim_walk(), anim_meteor(), anim_eruption(), anim_flame_breath(), anim_lava_pool(),
            anim_phase(), anim_death()]


POSES = [
    ("idle", [0.0, 1.5]),
    ("walk", [0.0, 0.4, 0.8, 1.2]),
    ("attack.meteor", [0.4, 0.75, 1.2]),
    ("attack.eruption", [0.7, 1.0, 1.4]),
    ("attack.flame_breath", [0.5, 0.8, 1.6]),
    ("attack.lava_pool", [0.55, 0.8, 1.1]),
    ("phase", [0.4, 0.75, 1.0, 1.6]),
    ("death", [0.3, 1.1, 1.8, 2.4]),
]


def main():
    m = build_model()
    geo, rgba, glow, anims = tl.build(NAME, m, SHADERS, clips(), visible=(5, 6, 2.5))
    if "--preview" in sys.argv:
        sel = POSES if "--all" in sys.argv else POSES[:3]
        for p in tl.previews(NAME, geo, rgba, glow, anims, HITBOX, sel, frame=(130, 92)):
            print("preview", p)


if __name__ == "__main__":
    main()
