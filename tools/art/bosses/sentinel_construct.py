"""Sentinel Construct: an Ender Empire war machine. A hulking purpur-and-obsidian golem with a
single violet eye-lens behind sliding visor plates, floating shoulder plates held up by rune
circles, gold filigree trims and two end-rod exhaust masts on its back.

Run: python sentinel_construct.py [--preview]
"""
import math
import sys

import numpy as np

import bosslib as tl
import bossfx as fx
import empire_mats as em
from bosslib import Clip, env, shake, hash3, fbm, palette
from rig import TAU, knee_bend, mir, sides, tremor

NAME = "sentinel_construct"
HITBOX = (1.6, 3.2)
THIGH, SHIN = 8.0, 9.0

# =============================================================================== geometry


def rod(bone, base, d, length, width, mat, **kw):
    R = tl.orient(d, 45)
    base = np.asarray(base, dtype=float)
    return bone.cube(base + np.array([-width / 2, 0, -width / 2]), (width, length, width), mat, 0.0, base,
                     tl.euler(R), **kw)


def build_model():
    m = tl.Model(NAME)
    body = m.bone("body", "root", (0, 19, 0))
    body.boxb(0, 15.5, 0.5, 13, 6, 9, "obsidian")                                  # pelvis
    body.boxb(0, 19.5, 0.5, 14, 2, 10, "gold_band")                                # belt
    body.box((0, 20.5, -4.75), (3, 3, 1), "gem", rot=[0, 0, 45])                   # buckle gem
    body.plane_from((0, 19.6, -5.2), 9, 9, "fauld", rot=[-14, 0, 0])               # front tasset
    body.plane_from((0, 19.6, 5.9), 11, 8, "fauld", rot=[14, 0, 0])                # rear tasset
    for s in (-1, 1):
        body.plane_from((7.3 * s, 19.6, 0.5), 8, 7, "fauld", rot=[-16, -90 * s, 0])

    torso = m.bone("torso", "body", (0, 21, 0), rotation=[5, 0, 0])
    torso.boxb(0, 20.5, 0.5, 10, 7, 8, "obsidian_runes")                           # waist
    torso.box((0, 24.0, -4.0), (8, 3, 2), "purpur")                                # ab plates
    torso.box((0, 27.0, -4.6), (11, 3, 2), "purpur")
    torso.boxb(0, 27, 0.5, 15, 8, 10, "obsidian")                                  # chest core
    torso.boxb(0, 32, 0, 22, 8, 13, "purpur_trim")                                 # broad upper chest
    for s in (-1, 1):
        torso.box((5.3 * s, 35.0, -6.9), (10, 7, 2), "purpur_trim", rot=[-12, -14 * s, 0])   # pectoral plates
        torso.box((10.6 * s, 29.0, 0.5), (2, 6, 9), "obsidian", rot=[0, 0, 8 * s])            # flank ribs
    torso.box((0, 30.2, -5.3), (7, 3, 1), "vent")                                  # chest vent
    torso.boxb(0, 39.5, 1.0, 12, 2, 9, "obsidian")                                 # gorget
    torso.box((0, 35.5, 6.9), (17, 9, 3), "purpur_trim", rot=[8, 0, 0])            # back hump
    torso.boxb(0, 25, 5.4, 5, 10, 2, "obsidian_runes")                             # spine
    masts = m.bone("masts", "torso", (0, 37, 7.5))
    for s in (-1, 1):
        rod(masts, (4.0 * s, 36.0, 8.0), (0.28 * s, 1.0, 0.5), 15, 2, "rod", tip=0.22)
        masts.box((4.0 * s, 37.0, 8.4), (4, 3, 4), "obsidian", rot=[25, 0, -15 * s])  # mast collars
        rod(masts, (7.0 * s, 37.5, 8.6), (0.6 * s, 1.0, 0.35), 8, 1, "rod", tip=0.35)

    head = m.bone("head", "torso", (0, 38.5, -3))
    head.boxb(0, 37, -4, 9, 8, 9, "purpur_helm")                                   # helm
    head.box((0, 41.0, -8.6), (9, 8, 1), "obsidian")                               # lens socket
    head.box((0, 45.4, -6.2), (11, 2, 6), "purpur_trim", rot=[16, 0, 0])           # brow hood
    head.box((0, 46.6, -2.5), (2, 4, 10), "gold_fin")                              # crest fin
    head.box((0, 47.6, 2.4), (2, 3, 5), "gold_fin", rot=[-28, 0, 0])
    for s in (-1, 1):
        head.box((5.3 * s, 40.0, -5.0), (2, 6, 7), "purpur", rot=[0, 12 * s, 0])  # cheek guards
        head.box((5.6 * s, 44.6, -1.0), (1, 4, 5), "gold_fin", rot=[-25, 0, 30 * s])  # temple fins
    head.box((0, 37.4, -7.9), (5, 2, 2), "obsidian")                               # chin
    eye = m.bone("eye", "head", (0, 41, -9.1))
    eye.box((0, 41.0, -9.3), (7, 7, 1), "lens", inflate=0.05)                      # the lens
    eye.plane((0, 41.0, -9.95), 9, 9, "lens_ring")                                 # glowing iris ring
    vt = m.bone("visor_top", "head", (0, 44.8, -9.4))
    vt.box((0, 45.2, -9.7), (10, 2, 1), "visor")
    vb = m.bone("visor_bottom", "head", (0, 37.2, -9.4))
    vb.box((0, 36.9, -9.7), (10, 2, 1), "visor")

    for s, nm in sides():
        arm = m.bone(f"{nm}_arm", "torso", (12.5 * s, 37, 0), rotation=[-5, 0, 0])
        arm.box((13 * s, 36.0, 0), (6, 6, 6), "orb")                                # shoulder energy orb
        arm.boxb(13.5 * s, 27, 0, 6, 9, 6, "obsidian")                              # upper arm
        arm.boxb(13.7 * s, 29, 0, 7, 5, 7, "purpur")                                # bicep sleeve
        fore = m.bone(f"{nm}_forearm", f"{nm}_arm", (13.5 * s, 27.5, 0))
        fore.box((13.5 * s, 27.0, 1.5), (5, 4, 4), "gold")                          # elbow cop
        fore.boxb(14 * s, 15.5, 0, 9, 11, 9, "purpur_trim")                        # gauntlet
        fore.boxb(14 * s, 24.5, 0, 10, 2, 10, "gold_band")                          # cuff band
        fore.boxb(14 * s, 14.5, 0, 10, 3, 10, "purpur")                             # wrist flare
        fore.box((18.9 * s, 21.0, 0.5), (1, 8, 6), "gold_fin")                      # forearm blade
        fore.box((19.5 * s, 24.0, 2.5), (1, 4, 4), "gold_fin", rot=[-30, 0, 0])
        fore.boxb(14 * s, 6, -0.5, 9, 8, 10, "obsidian")                            # fist
        fore.box((14 * s, 10.5, -5.7), (9, 3, 2), "gold")                           # knuckle guard
        fore.box((9.6 * s, 10.5, -3.0), (2, 4, 3), "obsidian", rot=[0, 0, -12 * s])  # thumb
        pa = m.bone(f"{nm}_pauldron", "torso", (15 * s, 44, 0))
        pa.box((15 * s, 44.0, 0), (12, 4, 14), "purpur_trim", rot=[0, 0, 20 * s])  # main plate
        pa.box((18.6 * s, 40.6, 0), (7, 3, 13), "purpur_trim", rot=[0, 0, 32 * s]) # lower lame
        pa.box((14.0 * s, 46.6, 0), (7, 2, 10), "gold", rot=[0, 0, 20 * s])        # gold cap
        pa.box((12.8 * s, 49.0, 0), (2, 4, 8), "gold_fin", rot=[0, 0, 28 * s])      # top fins
        pa.box((15.8 * s, 48.2, 0), (1, 3, 6), "gold_fin", rot=[0, 0, 40 * s])
        pa.plane((15 * s, 39.6, 0), 11, 11, "rune_circle", rot=[90, 0, 0])          # levitation circle

    for s, nm in sides():
        leg = m.bone(f"{nm}_leg", "body", (5.5 * s, 19, 0))
        leg.boxb(5.5 * s, 11, 0, 6, 8, 6, "obsidian")                               # thigh
        leg.boxb(5.8 * s, 12.5, -0.4, 7, 6, 7, "purpur")                            # thigh plate
        shin = m.bone(f"{nm}_shin", f"{nm}_leg", (5.5 * s, 11, 0))
        shin.boxb(5.5 * s, 2.5, 0, 7, 8, 7, "purpur_trim")                          # greave
        shin.box((5.5 * s, 10.8, -3.8), (5, 4, 2), "gold")                          # knee cop
        shin.box((5.5 * s, 6.5, -3.9), (3, 6, 1), "obsidian_runes")                 # shin ridge
        shin.box((9.0 * s, 6.5, 0), (1, 6, 5), "gold_fin")                          # calf fin
        foot = m.bone(f"{nm}_foot", f"{nm}_shin", (5.5 * s, 2, -0.5))
        foot.boxb(5.5 * s, 0, -1.5, 8, 3, 11, "obsidian")                           # foot
        foot.boxb(5.5 * s, 0, -7.0, 8, 2, 2, "gold")                                # toe cap
        foot.boxb(5.5 * s, 0, 4.6, 6, 2, 2, "obsidian")                             # heel spur
    return m


# =============================================================================== shaders


def _wrap(fn):
    def sh(ctx):
        rgb, glow = fn(ctx)
        return rgb, 255, glow
    return sh


def shade_fauld(ctx):
    """Hanging tasset plate (plane): purpur with gold rim, tapered cutout bottom."""
    x, y = fx.plane_xy(ctx)
    rgb, glow = em.purpur(ctx, tile=8)
    # cutout: pointed bottom
    shape = (y > -0.55 - (1 - np.abs(x)) * 0.45)
    edge = shape & ~((y > -0.55 - (1 - np.abs(x)) * 0.45 + 0.12) & (np.abs(x) < 0.86))
    rgb[edge] = fx.sramp(em.GOLD, 0.7 + 0.2 * (y[edge] + 1) / 2)
    return rgb, np.where(shape, 255, 0), glow


def shade_rune_circle(ctx):
    x, y = fx.plane_xy(ctx)
    r = np.sqrt(x * x + y * y)
    a = np.arctan2(y, x)
    ring1 = np.abs(r - 0.9) < 0.06
    ring2 = np.abs(r - 0.62) < 0.045
    ticks = (r > 0.66) & (r < 0.86) & (np.abs(np.mod(a * 8 / TAU, 1) - 0.5) < 0.07)
    tri = np.zeros(ctx.N, dtype=bool)
    for k in range(3):
        a0 = TAU * k / 3 + TAU / 4
        a1 = a0 + TAU / 3
        tri |= tl.seg_dist(x, y, 0.62 * math.cos(a0), 0.62 * math.sin(a0), 0.62 * math.cos(a1), 0.62 * math.sin(a1)) < 0.04
    m = ring1 | ring2 | ticks | tri
    rgb = np.zeros((ctx.N, 3)) + em.ENDER[5]
    rgb[ring1] = em.ENDER[6]
    return rgb, np.where(m, 255, 0), m


def shade_visor(ctx):
    rgb, glow = em.obsidian(ctx)
    if ctx.face in ("north",):
        d = fx.edge_dist(ctx)
        rgb[d == 0] = em.GOLD[6]
    return rgb, 255, glow


def shade_gem(ctx):
    x, y = fx.plane_xy(ctx)
    v = 0.62 - 0.3 * (np.abs(x) + np.abs(y)) + 0.25 * ((x < 0) & (y > 0))
    if ctx.face != "north":
        v = v * 0.7
    return fx.sramp(em.ENDER, v + fx.dither(ctx, 0.05)), 255, np.ones(ctx.N, dtype=bool)


def shade_vent(ctx):
    rgb, glow = em.obsidian(ctx)
    if ctx.face == "north":
        slot = (np.mod(ctx.j, 3) == 1) & (fx.edge_dist(ctx) >= 1)
        rgb[slot] = fx.sramp(em.ENDER, 0.45 + 0.3 * (1 - np.abs(ctx.s[slot] - 0.5) * 2))
        glow = glow | slot
    return rgb, 255, glow


def shade_lens_ring(ctx):
    x, y = fx.plane_xy(ctx)
    r = np.sqrt(x * x + y * y)
    a = np.arctan2(y, x)
    ring = (r > 0.8) & (r < 0.97)
    notch = np.abs(np.mod(a * 6 / TAU, 1) - 0.5) < 0.1
    m = ring & ~(notch & (r > 0.9))
    rgb = fx.sramp(em.ENDER, 0.55 + 0.35 * (r - 0.8) / 0.17)[:, :] * 1.0
    return rgb, np.where(m, 255, 0), m


def shade_orb(ctx):
    """Shoulder joint: dark glass orb banded by a glowing violet equator and rune ring."""
    rgb, glow = em.obsidian(ctx, glints=True)
    if ctx.face not in ("up", "down"):
        eq = np.abs(ctx.t - 0.5) < 0.12
        rgb[eq] = fx.sramp(em.ENDER, 0.62 + 0.25 * (1 - np.abs(ctx.t[eq] - 0.5) / 0.12))
        dots = (np.abs(ctx.t - 0.5) < 0.3) & ~eq & (np.mod(ctx.i, 4) == 1) & (np.abs(ctx.t - 0.5) > 0.2)
        rgb[dots] = em.ENDER[4]
        glow = glow | eq | dots
    else:
        x, y = fx.plane_xy(ctx)
        r = np.sqrt(x * x + y * y)
        ring = np.abs(r - 0.55) < 0.12
        rgb[ring] = em.ENDER[5]
        glow = glow | ring
    return rgb, 255, glow


def shade_helm(ctx):
    rgb, glow = em.purpur(ctx, tile=8, trim="gold")
    return rgb, 255, glow


def shade_rod(ctx):
    rgb, glow = em.end_rod(ctx, ctx.params.get("tip", 0.0))
    return rgb, 255, glow


SHADERS = {
    "purpur": _wrap(lambda c: em.purpur(c)),
    "purpur_trim": _wrap(lambda c: em.purpur(c, trim="gold")),
    "purpur_helm": shade_helm,
    "obsidian": _wrap(lambda c: em.obsidian(c)),
    "obsidian_runes": _wrap(lambda c: em.obsidian(c, runes_on=True, rune_cell=7.0)),
    "gold": _wrap(lambda c: em.gold(c)),
    "gold_band": _wrap(lambda c: em.gold(c, filig=False, rivets=True)),
    "gold_fin": _wrap(lambda c: em.gold(c, filig=False)),
    "gem": shade_gem,
    "lens": _wrap(lambda c: em.lens(c, "slit")),
    "visor": shade_visor,
    "rod": shade_rod,
    "fauld": shade_fauld,
    "vent": shade_vent,
    "orb": shade_orb,
    "lens_ring": shade_lens_ring,
    "rune_circle": shade_rune_circle,
}

# =============================================================================== animations
LEGS = [("right_leg", "right_shin"), ("left_leg", "left_shin")]
FEET = ["right_foot", "left_foot"]


def hover_pauldrons(c, T, amp=1.1, turns=0):
    for k, (s, nm) in enumerate(sides()):
        c.f(f"{nm}_pauldron", "position", lambda t, k=k: (0, amp * math.sin(TAU * t / T + k * 2.1), 0))
        c.f(f"{nm}_pauldron", "rotation", lambda t, k=k, s=s: (2.5 * math.sin(TAU * t / T + 1 + k), 360 * turns * t / T * -s,
                                                               3 * math.sin(TAU * t / T + k * 2.1 + 0.8) * s))


def anim_idle():
    T = 3.2
    c = Clip("idle", T, loop=True)
    w = lambda t, ph=0.0: math.sin(TAU * t / T + ph)
    hover_pauldrons(c, T)
    c.f("torso", "rotation", lambda t: (1.5 * w(t), 0, 0))
    c.f("torso", "position", lambda t: (0, 0.25 * w(t), 0))
    for s, nm in sides():
        c.f(f"{nm}_arm", "rotation", lambda t, s=s: (2 * w(t, 0.6), 0, (2.5 + 1.2 * w(t, 0.3)) * -s))
        c.f(f"{nm}_forearm", "rotation", lambda t: (-6 - 2 * w(t, 1.0), 0, 0))
    c.f("eye", "scale", lambda t: (1 + 0.06 * w(t * 2, 0.0),) * 3)
    c.f("visor_top", "position", lambda t: (0, 0.25 * w(t, 1.2), 0))
    c.f("visor_bottom", "position", lambda t: (0, -0.25 * w(t, 1.2), 0))
    c.f("masts", "rotation", lambda t: (1.2 * w(t, 2.0), 0, 0))
    return c


def anim_walk():
    T = 1.6
    c = Clip("walk", T, loop=True)
    ph = lambda t: TAU * t / T
    A = 24.0
    for s, nm in sides():
        sg = 1 if nm == "right" else -1
        c.f(f"{nm}_leg", "rotation", lambda t, sg=sg: (-A * sg * math.sin(ph(t)), 0, 0))
        c.f(f"{nm}_shin", "rotation", lambda t, sg=sg: (32 * max(0.0, sg * math.cos(ph(t))) ** 1.5, 0, 0))
        c.f(f"{nm}_foot", "rotation", lambda t, sg=sg: (A * sg * math.sin(ph(t)) * 0.6 - 18 * max(0.0, sg * math.cos(ph(t))) ** 1.5, 0, 0))
        c.f(f"{nm}_arm", "rotation", lambda t, sg=sg, s=s: (18 * sg * math.sin(ph(t)), 0, 3 * -s))
        c.f(f"{nm}_forearm", "rotation", lambda t, sg=sg: (-10 - 8 * max(0.0, -sg * math.sin(ph(t))), 0, 0))
    c.f("body", "position", lambda t: (0, -1.1 + 1.1 * math.cos(2 * ph(t)), 0))
    c.f("body", "rotation", lambda t: (0, 0, 2.2 * math.sin(ph(t))))
    c.f("torso", "rotation", lambda t: (5 + 1.5 * math.cos(2 * ph(t)), 6 * math.sin(ph(t)), -1.5 * math.sin(ph(t))))
    for k, (s, nm) in enumerate(sides()):
        c.f(f"{nm}_pauldron", "position", lambda t, k=k: (0, 0.9 * math.cos(2 * ph(t) - 1.2) + 0.6, 0.8))
        c.f(f"{nm}_pauldron", "rotation", lambda t, s=s: (4 * math.cos(2 * ph(t) - 1.2), 0, 3 * math.sin(ph(t) - 1.0)))
    c.f("eye", "scale", lambda t: (1.0, 1.0, 1.0))
    c.f("masts", "rotation", lambda t: (3 * math.cos(2 * ph(t) - 0.8), 0, 0))
    return c


def anim_laser():
    L = 1.8
    c = Clip("attack.laser", L)
    hover_pauldrons(c, L, amp=0.6)
    c.rot("torso", [(0, (0, 0, 0)), (0.42, (-12, 0, 0), "io"), (0.52, (9, 0, 0), "snap"), (1.55, (7, 0, 0)), (1.8, (0, 0, 0), "io")])
    c.f("torso", "rotation", lambda t: (tremor(t, 0.5, 0.56, 1.5, 1.6, 0.9, 26), tremor(t, 0.5, 0.56, 1.5, 1.6, 0.6, 21, 2), 0))
    c.pos("body", [(0, (0, 0, 0)), (0.42, (0, -1.0, 1.0)), (0.52, (0, -2.0, 0.5), "snap"), (1.55, (0, -2.0, 0.8)), (1.8, (0, 0, 0))])
    knee_bend(c, lambda t: 1.0 * env(t, 0, 0.42, 0.45, 0.52) + 2.0 * env(t, 0.45, 0.52, 1.55, 1.8), THIGH, SHIN, LEGS, FEET)
    for s, nm in sides():
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.42, (20, 0, -s * 28)), (0.52, (-18, 0, -s * 14), "snap"),
                            (1.55, (-16, 0, -s * 12)), (1.8, (0, 0, 0))])
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.42, (-50, 0, 0)), (0.52, (-24, 0, 0), "snap"), (1.55, (-26, 0, 0)), (1.8, (0, 0, 0))])
        c.pos(f"{nm}_pauldron", [(0, (0, 0, 0)), (0.42, (1.2 * s, 1.5, 0)), (0.52, (2.5 * s, 2.5, 1), "snap"), (1.55, (2.4 * s, 2.2, 1)),
                                 (1.8, (0, 0, 0))])
        c.rot(f"{nm}_pauldron", [(0, (0, 0, 0)), (0.52, (0, 0, -18 * s), "snap"), (1.55, (0, 0, -16 * s)), (1.8, (0, 0, 0))])
    c.scl("eye", [(0, (1, 1, 1)), (0.42, (1.3, 1.3, 1.3), "in"), (0.5, (1.0, 1.0, 1.0)), (0.56, (1.55, 1.55, 1.4), "snap"),
                  (1.55, (1.5, 1.5, 1.4)), (1.8, (1, 1, 1))])
    c.f("eye", "scale", lambda t: (1 + 0.06 * math.sin(t * 70) * env(t, 0.55, 0.6, 1.5, 1.55),) * 3)
    c.pos("visor_top", [(0, (0, 0, 0)), (0.42, (0, 1.6, 0)), (0.52, (0, 2.2, 0), "snap"), (1.55, (0, 2.2, 0)), (1.8, (0, 0, 0))])
    c.pos("visor_bottom", [(0, (0, 0, 0)), (0.42, (0, -1.4, 0)), (0.52, (0, -2.0, 0), "snap"), (1.55, (0, -2.0, 0)), (1.8, (0, 0, 0))])
    c.rot("masts", [(0, (0, 0, 0)), (0.42, (-8, 0, 0)), (0.52, (12, 0, 0), "snap"), (1.55, (10, 0, 0)), (1.8, (0, 0, 0))])
    return c


def anim_stomp():
    L = 1.4
    c = Clip("attack.stomp", L)
    hover_pauldrons(c, L, amp=0.5)
    c.rot("right_leg", [(0, (0, 0, 0)), (0.55, (-86, 0, 6), "out"), (0.68, (-88, 0, 6)), (0.8, (-22, 0, 2), "in3"),
                        (1.0, (-22, 0, 2)), (1.4, (0, 0, 0), "io")])
    c.rot("right_shin", [(0, (0, 0, 0)), (0.55, (84, 0, 0), "out"), (0.68, (80, 0, 0)), (0.8, (18, 0, 0), "in3"), (1.0, (18, 0, 0)),
                         (1.4, (0, 0, 0))])
    c.rot("right_foot", [(0, (0, 0, 0)), (0.55, (8, 0, 0)), (0.8, (4, 0, 0), "in3"), (1.4, (0, 0, 0))])
    c.pos("body", [(0, (0, 0, 0)), (0.55, (0, 1.2, 1.5), "out"), (0.68, (0, 1.4, 1.5)), (0.8, (0, -2.5, -1.0), "in3"),
                   (1.0, (0, -2.2, -1.0)), (1.4, (0, 0, 0), "io")])
    c.f("body", "position", lambda t: (0, tremor(t, 0.8, 0.82, 0.92, 1.05, 0.5, 30), 0))
    c.rot("body", [(0, (0, 0, 0)), (0.55, (0, 0, -5), "out"), (0.8, (0, 0, 1), "in3"), (1.4, (0, 0, 0))])
    c.rot("torso", [(0, (0, 0, 0)), (0.55, (-12, 0, 0), "out"), (0.68, (-14, 0, 0)), (0.8, (16, 0, 0), "in3"), (1.0, (14, 0, 0)),
                    (1.4, (0, 0, 0), "io")])
    # support leg keeps the planted foot under the body
    c.rot("left_leg", [(0, (0, 0, 0)), (0.55, (4, 0, -3), "out"), (0.8, (-14, 0, -2), "in3"), (1.0, (-14, 0, -2)), (1.4, (0, 0, 0))])
    c.rot("left_shin", [(0, (0, 0, 0)), (0.55, (0, 0, 0)), (0.8, (28, 0, 0), "in3"), (1.0, (26, 0, 0)), (1.4, (0, 0, 0))])
    c.rot("left_foot", [(0, (0, 0, 0)), (0.55, (-4, 0, 3)), (0.8, (-14, 0, 2), "in3"), (1.0, (-12, 0, 2)), (1.4, (0, 0, 0))])
    for s, nm in sides():
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.55, (-30, 0, -s * 38), "out"), (0.68, (-32, 0, -s * 40)),
                            (0.8, (14, 0, -s * 10), "in3"), (1.0, (12, 0, -s * 8)), (1.4, (0, 0, 0))])
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.55, (-55, 0, 0), "out"), (0.8, (-8, 0, 0), "in3"), (1.4, (0, 0, 0))])
        c.pos(f"{nm}_pauldron", [(0, (0, 0, 0)), (0.55, (0.5 * s, 2.0, 0)), (0.8, (0, -1.5, 0), "in3"), (0.95, (0, 1.0, 0), "out"),
                                 (1.4, (0, 0, 0))])
    c.scl("eye", [(0, (1, 1, 1)), (0.55, (1.15, 1.15, 1.15)), (0.8, (1.35, 1.35, 1.3), "snap"), (1.4, (1, 1, 1))])
    c.rot("masts", [(0, (0, 0, 0)), (0.55, (-6, 0, 0)), (0.8, (14, 0, 0), "in3"), (1.0, (-4, 0, 0)), (1.4, (0, 0, 0))])
    return c


def anim_charge():
    L = 1.3
    c = Clip("attack.charge", L)
    hover_pauldrons(c, L, amp=0.4)
    c.pos("body", [(0, (0, 0, 0)), (0.28, (0, -2.0, 2.5), "io"), (0.4, (0, -1.0, -9.0), "snap"), (0.75, (0, -1.4, -10.0)),
                   (1.3, (0, 0, 0), "io")])
    knee_bend(c, lambda t: 2.0 * env(t, 0.0, 0.28, 0.3, 0.42), THIGH, SHIN, LEGS, FEET)
    c.rot("torso", [(0, (0, 0, 0)), (0.28, (14, 0, 0)), (0.4, (28, 10, 0), "snap"), (0.75, (26, 8, 0)), (1.3, (0, 0, 0), "io")])
    c.rot("right_leg", [(0, (0, 0, 0)), (0.28, (0, 0, 0)), (0.4, (-34, 0, 0), "snap"), (0.75, (-30, 0, 0)), (1.3, (0, 0, 0))])
    c.rot("right_shin", [(0, (0, 0, 0)), (0.4, (22, 0, 0), "snap"), (0.75, (20, 0, 0)), (1.3, (0, 0, 0))])
    c.rot("right_foot", [(0, (0, 0, 0)), (0.4, (12, 0, 0), "snap"), (0.75, (10, 0, 0)), (1.3, (0, 0, 0))])
    c.rot("left_leg", [(0, (0, 0, 0)), (0.28, (0, 0, 0)), (0.4, (30, 0, 0), "snap"), (0.75, (28, 0, 0)), (1.3, (0, 0, 0))])
    c.rot("left_shin", [(0, (0, 0, 0)), (0.4, (14, 0, 0), "snap"), (0.75, (12, 0, 0)), (1.3, (0, 0, 0))])
    c.rot("left_foot", [(0, (0, 0, 0)), (0.4, (-36, 0, 0), "snap"), (0.75, (-34, 0, 0)), (1.3, (0, 0, 0))])
    # shoulder bash: right side leads, left arm pulls back
    c.rot("right_arm", [(0, (0, 0, 0)), (0.28, (30, 0, 8)), (0.4, (-62, 20, 14), "snap"), (0.75, (-58, 18, 12)), (1.3, (0, 0, 0))])
    c.rot("right_forearm", [(0, (0, 0, 0)), (0.28, (-40, 0, 0)), (0.4, (-20, 0, 0), "snap"), (1.3, (0, 0, 0))])
    c.rot("left_arm", [(0, (0, 0, 0)), (0.28, (34, 0, -10)), (0.4, (40, -10, -14), "snap"), (0.75, (38, -8, -12)), (1.3, (0, 0, 0))])
    c.rot("left_forearm", [(0, (0, 0, 0)), (0.28, (-50, 0, 0)), (0.4, (-30, 0, 0), "snap"), (1.3, (0, 0, 0))])
    c.pos("right_pauldron", [(0, (0, 0, 0)), (0.28, (0, 0, 2)), (0.4, (1, -1, -4), "snap"), (0.75, (1, -1, -3.5)), (1.3, (0, 0, 0))])
    c.rot("right_pauldron", [(0, (0, 0, 0)), (0.4, (22, 0, 8), "snap"), (0.75, (20, 0, 6)), (1.3, (0, 0, 0))])
    c.pos("left_pauldron", [(0, (0, 0, 0)), (0.4, (0, 1, 3), "snap"), (0.75, (0, 1, 3)), (1.3, (0, 0, 0))])
    c.scl("eye", [(0, (1, 1, 1)), (0.28, (1.2, 1.2, 1.2)), (0.4, (1.35, 1.35, 1.3), "snap"), (0.8, (1.25, 1.25, 1.2)), (1.3, (1, 1, 1))])
    c.rot("masts", [(0, (0, 0, 0)), (0.28, (-6, 0, 0)), (0.4, (22, 0, 0), "snap"), (0.75, (18, 0, 0)), (1.3, (0, 0, 0))])
    return c


def anim_phase():
    L = 2.0
    c = Clip("phase", L)
    c.rot("torso", [(0, (0, 0, 0)), (0.5, (22, 0, 0), "io"), (0.75, (-20, 0, 0), "snap"), (1.5, (-18, 0, 0)), (2.0, (0, 0, 0), "io")])
    c.f("torso", "rotation", lambda t: (tremor(t, 0.75, 0.8, 1.4, 1.55, 1.4, 24), tremor(t, 0.75, 0.8, 1.4, 1.55, 1.0, 19, 3), 0))
    c.pos("body", [(0, (0, 0, 0)), (0.5, (0, -2.5, 0)), (0.75, (0, 0.8, 0), "snap"), (1.5, (0, 0.6, 0)), (2.0, (0, 0, 0))])
    knee_bend(c, lambda t: 2.5 * env(t, 0.0, 0.5, 0.52, 0.75), THIGH, SHIN, LEGS, FEET, spread=0.5)
    for s, nm in sides():
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.5, (20, 0, 4 * s)), (0.75, (-26, 0, -s * 72), "snap"),
                            (1.5, (-24, 0, -s * 70)), (2.0, (0, 0, 0), "io")])
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.5, (-80, 0, 0)), (0.75, (-30, 0, 0), "snap"), (1.5, (-28, 0, 0)), (2.0, (0, 0, 0))])
        c.pos(f"{nm}_pauldron", [(0, (0, 0, 0)), (0.5, (-1.5 * s, -2.0, 0)), (0.75, (4.0 * s, 5.0, 0), "snap"), (1.5, (4.0 * s, 5.5, 0)),
                                 (2.0, (0, 0, 0), "io")])
        c.rot(f"{nm}_pauldron", [(0, (0, 0, 0)), (0.5, (0, 0, 0)), (1.6, (0, 360 * s, -20 * s), "io"), (2.0, (0, 360 * s, 0))])
    c.scl("eye", [(0, (1, 1, 1)), (0.5, (0.7, 0.7, 1)), (0.75, (1.7, 1.7, 1.5), "snap"), (1.5, (1.6, 1.6, 1.5)), (2.0, (1, 1, 1))])
    c.pos("visor_top", [(0, (0, 0, 0)), (0.5, (0, -1.0, 0)), (0.75, (0, 2.4, 0), "snap"), (1.5, (0, 2.4, 0)), (2.0, (0, 0, 0))])
    c.pos("visor_bottom", [(0, (0, 0, 0)), (0.5, (0, 1.0, 0)), (0.75, (0, -2.2, 0), "snap"), (1.5, (0, -2.2, 0)), (2.0, (0, 0, 0))])
    c.rot("masts", [(0, (0, 0, 0)), (0.5, (14, 0, 0)), (0.75, (-16, 0, 0), "snap"), (1.5, (-14, 0, 0)), (2.0, (0, 0, 0))])
    c.scl("masts", [(0, (1, 1, 1)), (0.75, (1.0, 1.2, 1.0), "snap"), (1.5, (1.0, 1.15, 1.0)), (2.0, (1, 1, 1))])
    return c


def anim_death():
    L = 2.8
    c = Clip("death", L, loop="hold")
    # jolt, shudder, knees buckle, kneels, slumps; the eye shutters closed and the pauldrons drop
    c.rot("torso", [(0, (0, 0, 0)), (0.25, (-16, 0, 0), "out"), (1.0, (-8, 0, 5)), (1.7, (24, 0, 6), "io"), (2.3, (38, 0, 8), "io"),
                    (2.8, (38, 0, 8))])
    c.f("torso", "rotation", lambda t: (tremor(t, 0.2, 0.3, 1.0, 1.3, 2.5, 20), tremor(t, 0.2, 0.3, 1.0, 1.3, 2.0, 17, 2), 0))
    drop = tl.Track([(0, 0.0), (1.1, 0.0), (1.75, 10.0, "in"), (1.9, 9.4, "out"), (2.05, 10.0, "in"), (2.8, 10.0)])
    c.f("body", "position", lambda t: (0, -float(drop(t)), -0.5 * float(drop(t)) / 10))
    kneel = lambda t: min(1.0, float(drop(t)) / 10.0)
    for s, nm in sides():
        sg = 1 if nm == "right" else -1
        c.f(f"{nm}_leg", "rotation", lambda t, sg=sg: (-12 * kneel(t) * (1 if sg > 0 else 0.4), 0, -4 * sg * kneel(t)))
        c.f(f"{nm}_shin", "rotation", lambda t, sg=sg: (92 * kneel(t), 0, 0))
        c.f(f"{nm}_foot", "rotation", lambda t: (-40 * kneel(t), 0, 0))
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.25, (-30, 0, -s * 30), "out"), (1.0, (-10, 0, -s * 10)),
                            (1.8, (-26, 0, -s * 6)), (2.3, (-40, 0, -s * 4)), (2.8, (-40, 0, -s * 4))])
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.25, (-40, 0, 0)), (1.0, (-10, 0, 0)), (2.3, (-6, 0, 0)), (2.8, (-6, 0, 0))])
        c.pos(f"{nm}_pauldron", [(0, (0, 0, 0)), (0.25, (1.5 * s, 2.0, 0), "out"), (0.9, (1.0 * s, 1.0, 0)),
                                 (1.6, (4.0 * s, -26.0, 4.0), "in"), (1.75, (4.0 * s, -24.5, 4.0), "out"), (1.9, (4.0 * s, -26.0, 4.0), "in"),
                                 (2.8, (4.0 * s, -26.0, 4.0))])
        c.rot(f"{nm}_pauldron", [(0, (0, 0, 0)), (0.9, (0, 0, 10 * s)), (1.6, (-30, 25 * s, 70 * s), "in"), (2.8, (-30, 25 * s, 70 * s))])
    c.f("eye", "scale", lambda t: ((1 + 0.25 * math.sin(t * 55) * env(t, 0.1, 0.2, 1.4, 1.8)) * (1 - 0.6 * tl.ease("io", (t - 1.6) / 1.0)),) * 3)
    c.pos("visor_top", [(0, (0, 0, 0)), (0.25, (0, 1.8, 0)), (1.4, (0, 1.0, 0)), (2.4, (0, -2.6, 0), "io"), (2.8, (0, -2.6, 0))])
    c.pos("visor_bottom", [(0, (0, 0, 0)), (0.25, (0, -1.6, 0)), (1.4, (0, -1.0, 0)), (2.4, (0, 2.2, 0), "io"), (2.8, (0, 2.2, 0))])
    c.rot("head", [(0, (0, 0, 0)), (1.6, (0, 0, 0)), (2.4, (0, 0, -14), "io"), (2.8, (0, 0, -14))])
    c.pos("head", [(0, (0, 0, 0)), (1.6, (0, 0, 0)), (2.4, (0, -1.5, -0.5), "io"), (2.8, (0, -1.5, -0.5))])
    c.rot("masts", [(0, (0, 0, 0)), (0.25, (-12, 0, 0)), (1.2, (6, 0, 0)), (2.3, (30, 0, 0), "io"), (2.8, (30, 0, 0))])
    return c


def clips():
    return [anim_idle(), anim_walk(), anim_laser(), anim_stomp(), anim_charge(), anim_phase(), anim_death()]


POSES = [
    ("idle", [0.0, 0.8, 1.6]),
    ("walk", [0.0, 0.4, 0.8, 1.2]),
    ("attack.laser", [0.3, 0.45, 0.8, 1.7]),
    ("attack.stomp", [0.3, 0.6, 0.8, 1.1]),
    ("attack.charge", [0.25, 0.4, 0.7, 1.1]),
    ("phase", [0.5, 0.8, 1.3]),
    ("death", [0.25, 1.2, 1.8, 2.8]),
]
HERO = ("attack.laser", 0.8)


def main():
    m = build_model()
    geo, rgba, glow, anims = tl.build(NAME, m, SHADERS, clips(), visible=(4, 4, 1.6))
    if "--preview" in sys.argv:
        print(fx.preview_rest(NAME, geo, rgba, glow, HITBOX))
        print(fx.preview_pose(NAME, geo, rgba, glow, anims, HERO[0], HERO[1]))
        if "--all" in sys.argv:
            for an, times in POSES:
                print(fx.preview_strip(NAME, geo, rgba, glow, anims, an, times, HITBOX))


if __name__ == "__main__":
    main()
