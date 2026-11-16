"""Ender Colossus: the Ender Empire's last colossus. A 6-block ancient king of cracked purpur over an
obsidian frame, with violet light bleeding from the cracks, a gold cutout crown, a carved obsidian
beard, a teal ender-eye core set in its chest, rune-carved obsidian, a long royal tabard and a
three-segment cape of violet energy.

Run: python ender_colossus.py [--preview [--all]]
"""
import math
import sys

import numpy as np

import bosslib as tl
import bossfx as fx
import empire_mats as em
import geo_preview as gp
from bosslib import Clip, env, fbm, hash3, vnoise
from rig import TAU, knee_bend, sides, tremor

NAME = "ender_colossus"
HITBOX = (3.0, 6.0)
THIGH, SHIN = 15.0, 20.0
CAPE = [(0, 26), (26, 24), (50, 22)]          # (top offset, height) of each cape segment
CAPE_TOTAL = 72.0
CAPE_W = 19                                    # width of each cape half

# =============================================================================== geometry


def build_model():
    m = tl.Model(NAME)
    body = m.bone("body", "root", (0, 40, 0))
    body.boxb(0, 34, 1, 22, 10, 15, "obsidian")                                    # pelvis
    body.boxb(0, 41, 1, 24, 3, 16, "gold_band")                                    # belt
    body.box((0, 42.5, -7.4), (5, 5, 1), "gem", rot=[0, 0, 45])                    # belt gem
    for s in (-1, 1):
        body.plane_from((12.3 * s, 42.0, 1.0), 13, 14, "tasset", rot=[-16, -90 * s, 0])   # hip tassets
        body.box((10.5 * s, 38.5, -7.2), (3, 3, 1), "gold")                        # belt studs
    body.plane_from((0, 42.0, 9.2), 18, 13, "tasset", rot=[14, 0, 0])              # rear tasset
    tab = m.bone("tabard", "body", (0, 42, -7.8))
    tab.plane_from((0, 42.0, -7.9), 14, 33, "tabard", rot=[-4, 0, 0])               # royal tabard

    for s, nm in sides():
        leg = m.bone(f"{nm}_leg", "body", (8 * s, 40, 0))
        leg.boxb(8 * s, 25, 0, 10, 15, 10, "obsidian")                              # thigh
        leg.boxb(8.6 * s, 28, -0.6, 12, 10, 12, "purpur_ct")                        # thigh plate
        shin = m.bone(f"{nm}_shin", f"{nm}_leg", (8 * s, 25, 0))
        shin.boxb(8 * s, 6, 0, 11, 18, 11, "purpur_ct")                             # greave
        shin.box((8 * s, 24.2, -6.2), (8, 7, 3), "gold")                            # knee cop
        shin.box((8 * s, 14.5, -6.0), (4, 14, 1), "obsidian_runes")                 # greave ridge
        shin.box((13.9 * s, 15.0, 0.5), (1, 12, 8), "gold_fin")                     # calf fin
        foot = m.bone(f"{nm}_foot", f"{nm}_shin", (8 * s, 5, -0.5))
        foot.boxb(8 * s, 0, -2, 13, 6, 18, "obsidian")                              # foot
        foot.boxb(8 * s, 0, -11.6, 13, 3, 3, "gold")                                # toe cap
        foot.boxb(8 * s, 5, 0, 12, 2, 12, "gold_band")                              # ankle band

    torso = m.bone("torso", "body", (0, 44, 0))
    torso.boxb(0, 43, 1, 18, 11, 13, "obsidian_runes")                             # waist
    torso.box((0, 47.5, -6.0), (14, 4, 2), "purpur_c")                             # ab plates
    torso.box((0, 51.8, -6.8), (17, 4, 2), "purpur_c")
    torso.boxb(0, 53, 1, 28, 12, 18, "obsidian")                                   # chest core
    torso.boxb(0, 60, 0, 36, 14, 21, "purpur_ct")                                  # broad upper chest
    for s in (-1, 1):
        torso.box((10.2 * s, 66.0, -11.4), (14, 12, 3), "purpur_ct", rot=[-8, -8 * s, 0])   # pectorals
        torso.box((16.8 * s, 55.0, 1.0), (3, 9, 14), "obsidian", rot=[0, 0, 8 * s])          # flank ribs
        torso.box((12.5 * s, 73.0, -9.6), (5, 5, 2), "clasp")                                  # cape clasps
    torso.box((0, 63.0, -14.0), (12, 12, 2), "obsidian_runes")                     # core frame
    torso.boxb(0, 73, 1.5, 20, 4, 15, "obsidian")                                  # gorget
    torso.box((0, 64.0, 11.2), (30, 16, 3), "purpur_ct", rot=[6, 0, 0])            # back plate
    torso.boxb(0, 45, 8.0, 8, 15, 2, "obsidian_runes")                             # spine
    core = m.bone("core", "torso", (0, 63, -15.3))
    core.box((0, 63.0, -15.3), (9, 9, 1), "eye_core", inflate=0.05)                # ender-eye core
    core.plane((0, 63.0, -15.95), 15, 15, "core_ring")                             # gold rune ring
    spires = m.bone("spires", "torso", (0, 70, 12))
    for s in (-1, 1):                                                              # End-city spires
        R = tl.orient((0.22 * s, 1.0, 0.32), 0)
        base = np.array([8.5 * s, 66.0, 12.5])
        e = tl.euler(R)
        spires.cube(base + [-3, 0, -3], (6, 22, 6), "purpur_c", 0.0, base, e)
        spires.cube(base + [-4, 18, -4], (8, 3, 8), "purpur_ct", 0.0, base, e)
        spires.cube(base + [-2.5, 21, -2.5], (5, 4, 5), "obsidian_runes", 0.0, base, e)
        spires.cube(base + [-1, 25, -1], (2, 9, 2), "rod", 0.0, base, e, tip=0.3)
        spires.cube(base + [-3.5, 6, -3.5], (7, 2, 7), "gold_band", 0.0, base, e)

    neck = m.bone("neck", "torso", (0, 74, 0))
    neck.boxb(0, 73, 0, 10, 5, 10, "obsidian")
    head = m.bone("head", "neck", (0, 77, -1))
    head.boxb(0, 76, -1.5, 14, 14, 14, "purpur_helm")                              # great helm
    head.box((0, 81.0, -8.9), (12, 10, 1), "obsidian")                             # face plate
    for s in (-1, 1):
        head.box((3.3 * s, 83.4, -9.55), (4, 1, 1), "eye_slit", rot=[0, 0, -10 * s], inflate=0.08)
        head.box((7.3 * s, 80.5, -3.5), (2, 10, 9), "purpur_c", rot=[0, 10 * s, 0])  # cheek guards
        head.box((7.6 * s, 87.5, 1.0), (1, 5, 7), "gold_fin", rot=[-20, 0, 18 * s])  # helm wings
    head.box((0, 81.3, -9.7), (2, 7, 1), "gold")                                   # nose guard
    head.box((0, 86.3, -8.9), (14, 2, 3), "purpur_ct", rot=[12, 0, 0])             # brow ridge
    head.box((0, 76.8, -8.6), (10, 3, 3), "obsidian")                              # jaw plate
    head.plane_from((0, 78.4, -9.6), 11, 11, "beard", rot=[-28, 0, 0])             # carved beard
    crown = m.bone("crown", "head", (0, 90, -1.5))
    crown.boxb(0, 89, -1.5, 16, 3, 16, "gold_band")                                # crown band
    for k, (dx, dz, ry) in enumerate(((0, -8.6, 0), (0, 5.6, 180), (-8.6, -1.5, 90), (8.6, -1.5, -90))):
        crown.plane_from((dx, 91.2, dz), 17, 13, "crown", rot=[-10, ry, 0], anchor_st=(0.5, 1.0), front=(k == 0))
    crown.box((0, 90.5, -9.8), (3, 3, 1), "gem", rot=[0, 0, 45])                   # front gem
    for s in (-1, 1):
        crown.box((5.2 * s, 90.5, -9.6), (2, 2, 1), "gem", rot=[0, 0, 45])

    for s, nm in sides():
        arm = m.bone(f"{nm}_arm", "torso", (20 * s, 71, 0))
        arm.box((21 * s, 70.0, 0), (9, 9, 9), "orb")                                # shoulder orb
        arm.boxb(22 * s, 55, 0, 9, 14, 9, "obsidian")                               # upper arm
        arm.boxb(22.3 * s, 58, 0, 10, 8, 10, "purpur_c")                            # bicep plate
        pa = m.bone(f"{nm}_pauldron", "torso", (20 * s, 71, 0))                    # follows the arm partly
        pa.box((23.0 * s, 75.5, 0), (17, 5, 20), "purpur_ct", rot=[0, 0, 20 * s])   # pauldron
        pa.box((28.8 * s, 70.2, 0), (9, 4, 19), "purpur_ct", rot=[0, 0, 34 * s])    # lame 1
        pa.box((31.4 * s, 65.6, 0), (6, 4, 17), "purpur_c", rot=[0, 0, 50 * s])     # lame 2
        pa.box((21.6 * s, 79.0, 0), (10, 2, 14), "gold", rot=[0, 0, 20 * s])        # pauldron cap
        pa.box((19.6 * s, 82.4, 0), (2, 6, 10), "gold_fin", rot=[0, 0, 26 * s])     # crest fins
        pa.box((23.6 * s, 81.2, 0), (2, 5, 8), "gold_fin", rot=[0, 0, 34 * s])
        fore = m.bone(f"{nm}_forearm", f"{nm}_arm", (22 * s, 55.5, 0))
        fore.box((22 * s, 55.0, 2.5), (7, 6, 6), "gold")                            # elbow cop
        fore.boxb(22.5 * s, 38, 0, 13, 16, 13, "purpur_ct")                        # gauntlet
        fore.boxb(22.5 * s, 51.0, 0, 14, 3, 14, "gold_band")                        # cuff
        fore.boxb(22.5 * s, 37, 0, 14, 4, 14, "purpur_c")                           # wrist flare
        fore.box((29.6 * s, 46.0, 1.0), (1, 12, 9), "gold_fin")                     # forearm blade
        hand = m.bone(f"{nm}_hand", f"{nm}_forearm", (22.5 * s, 37.5, 0))
        hand.boxb(22.5 * s, 26, -1, 13, 11, 14, "obsidian")                         # fist
        hand.box((22.5 * s, 32.0, -8.4), (13, 4, 3), "gold")                        # knuckle guard
        hand.box((16.4 * s, 32.0, -4.0), (3, 6, 4), "obsidian", rot=[0, 0, -12 * s])  # thumb
        hand.box((29.1 * s, 31.0, -1.0), (1, 7, 9), "rune_plate")                   # hand sigil

    # cape of violet energy: three chained segments, each a shallow V of two planes
    parent, top, z = "torso", 74.0, 12.4
    tilt = [7, 5, 3]
    for k, (off, h) in enumerate(CAPE):
        nm = ["cape_top", "cape_mid", "cape_low"][k]
        b = m.bone(nm, parent, (0, top, z))
        for s in (-1, 1):
            R = gp.rot_b([tilt[k], 0, 0]) @ gp.rot_b([0, 16 * s, 0])      # yaw first, then tilt: seams stay on x=0
            b.plane_from((0, top, z), CAPE_W, h, "cape", rot=R,
                         anchor_st=(1.0 if s < 0 else 0.0, 0.0), off=off, seg_h=h, half=s)
        a = math.radians(tilt[k])
        top, z = top - h * math.cos(a), z + h * math.sin(a)
        parent = nm
    build_stages(m)
    return m


# =============================================================================== evolution stages
# BossRenderer shows bones named stage2_* from stage 2 on and stage3_* only in stage 3 (hiding a
# bone hides its children) and scales them in from 0 at their pivot, so every pivot sits where the
# part attaches. Stage bones come after all base bones (base cube indices, which seed the tile and
# rune patterns, stay the same) and never occlude the base model in the baked AO, so the base
# texture is unchanged with them hidden. Budget: validate.py allows at most 140 cubes.


def stage_bone(m, name, parent, pivot):
    assert name.startswith(("stage2_", "stage3_")), name
    return m.bone(name, parent, pivot)


def shard(bone, base, d, length, width, mat, spin=45.0, **params):
    """One tapered crystal: a single box along d whose tip is cut to a point in the texture."""
    base = np.asarray(base, dtype=float)
    w = int(round(width))
    return bone.cube(base + np.array([-w / 2, 0, -w / 2]), (w, int(round(length)), w), mat, 0.0, base,
                     tl.euler(tl.orient(d, spin)), **params)


def pauldron_top(s, u):
    """Point on the sloped top face of the main pauldron plate, u units outward from its centre
    (plate: centre (23s, 75.5), 5 thick, rolled 20 deg outward-down)."""
    a = math.radians(20)
    c = np.array([23 * s + 2.5 * math.sin(a) * s, 75.5 + 2.5 * math.cos(a), 0.0])
    return c + u * np.array([math.cos(a) * s, -math.sin(a), 0.0])


def build_stages(m):
    # ---- stage 2: purpur crystals burst from the shoulders and the upper back, two more ender eyes
    for s, nm in sides():
        b = pauldron_top(s, 4.2) + np.array([0, -0.6, 4.5])
        cs = stage_bone(m, f"stage2_{nm}_shards", f"{nm}_pauldron", b)
        cs.spike(b, (0.55 * s, 1.0, 0.5), 19, 5, "crystal", segs=[0.6, 0.46], taper=0.6, overlap=1.0, tip=0.55)
        shard(cs, pauldron_top(s, 1.5) + np.array([0, -0.6, 8.0]), (0.25 * s, 1.0, 0.85), 10, 3, "crystal", tip=0.5)
    bs = stage_bone(m, "stage2_back_shards", "torso", (0, 74.5, 9.5))
    bs.spike((0, 74.0, 9.5), (0, 1.0, 0.36), 24, 6, "crystal", segs=[0.58, 0.48], taper=0.67, overlap=1.0, tip=0.5)
    for s in (-1, 1):
        shard(bs, (4.6 * s, 73.5, 10.0), (0.36 * s, 1.0, 0.32), 14, 4, "crystal", tip=0.45)
    for s, nm in sides():
        P = np.array([10.2 * s, 66.0, -11.4])                       # pectoral plate centre
        eye_c = P + gp.rot_b([-8, -8 * s, 0]) @ np.array([1.3 * s, 0.5, -1.5])   # on the plate's front face
        eye = stage_bone(m, f"stage2_{nm}_chest_eye", "torso", eye_c)
        eye.box(P + np.array([1.3 * s, 0.5, -1.95]), (8, 6, 1), "chest_eye", rot=[-8, -8 * s, 0], pivot=P)

    # ---- stage 3: a crown of floating obsidian spikes, end crystals set into the shoulders
    cr = stage_bone(m, "stage3_spike_crown", "crown", (0, 92, -1.5))
    for th, L in ((180, 19), (115, 16), (-115, 16), (55, 13), (-55, 13)):
        t = math.radians(th)
        out = np.array([math.sin(t), 0.0, -math.cos(t)])
        base = np.array([0, 97.0, -1.5]) + 13.5 * out
        shard(cr, base, out * 0.36 + np.array([0, 1.0, 0]), L, 3, "obsidian_spike", tip=0.5)
    for s, nm in sides():
        c = pauldron_top(s, 5.6) + np.array([0, 4.4, -5.0])
        ec = stage_bone(m, f"stage3_{nm}_end_crystal", f"{nm}_pauldron", c - np.array([0, 4.4, 0]))
        Ro = tl.axis_angle([0, 0, 1], 35.26 * s) @ tl.axis_angle([1, 0, 0], 45)   # stands on a corner
        ec.box(c, (6, 6, 6), "end_frame", rot=Ro)
        ec.box(c, (4, 4, 4), "end_core", rot=tl.axis_angle([0, 1, 0], 45) @ tl.axis_angle([1, 0, 0], 30))
    for b in m.bones.values():
        if b.name.startswith(("stage2_", "stage3_")):
            for c in b.cubes:
                c.params["no_ao"] = True        # never darkens the base model (it must look unchanged)

# =============================================================================== shaders


def _wrap(fn):
    def sh(ctx):
        rgb, glow = fn(ctx)
        return rgb, 255, glow
    return sh


def shade_gem(ctx):
    x, y = fx.plane_xy(ctx)
    v = 0.62 - 0.3 * (np.abs(x) + np.abs(y)) + 0.25 * ((x < 0) & (y > 0))
    if ctx.face != "north":
        v = v * 0.7
    return fx.sramp(em.ENDER, v + fx.dither(ctx, 0.05)), 255, np.ones(ctx.N, dtype=bool)


def shade_eye_slit(ctx):
    v = 0.78 + 0.18 * (1 - np.abs(ctx.s - 0.5) * 2)
    return fx.sramp(em.ENDER, v), 255, np.ones(ctx.N, dtype=bool)


def shade_orb(ctx):
    rgb, glow = em.obsidian(ctx, glints=True)
    if ctx.face not in ("up", "down"):
        eq = np.abs(ctx.t - 0.5) < 0.1
        rgb[eq] = fx.sramp(em.ENDER, 0.62 + 0.25 * (1 - np.abs(ctx.t[eq] - 0.5) / 0.1))
        runes_m, _ = fx.runes(ctx.i + ctx.index * 7.0, ctx.j - ctx.th * 0.18, cell=6.0, seed=13, density=0.38)
        band = (np.abs(ctx.t - 0.5) > 0.14) & (np.abs(ctx.t - 0.5) < 0.33) & runes_m
        rgb[band] = em.ENDER[4]
        glow = glow | eq | band
    else:
        x, y = fx.plane_xy(ctx)
        r = np.sqrt(x * x + y * y)
        ring = np.abs(r - 0.55) < 0.1
        rgb[ring] = em.ENDER[5]
        glow = glow | ring
    return rgb, 255, glow


def shade_clasp(ctx):
    rgb, glow = em.gold(ctx, filig=False)
    if ctx.face == "north":
        x, y = fx.plane_xy(ctx)
        r = np.sqrt(x * x + y * y)
        g = r < 0.45
        rgb[g] = fx.sramp(em.TEAL, 0.85 - r[g])
        glow = glow | g
    return rgb, 255, glow


def shade_rune_plate(ctx):
    rgb, glow = em.obsidian(ctx)
    if ctx.face in ("east", "west"):
        x, y = fx.plane_xy(ctx)
        r = np.sqrt(x * x + (y * ctx.th / ctx.tw) ** 2)
        ring = np.abs(r - 0.62) < 0.1
        m, _ = fx.runes(ctx.i.astype(float) + 3, ctx.j.astype(float) + 2, cell=6.0, seed=31, density=0.5)
        inner = m & (r < 0.48)
        rgb[ring | inner] = em.ENDER[5]
        glow = glow | ring | inner
    return rgb, 255, glow


def shade_core_ring(ctx):
    """Gold ring around the ender-eye core with glowing rune glyphs and four cardinal spikes."""
    x, y = fx.plane_xy(ctx)
    r = np.sqrt(x * x + y * y)
    a = np.arctan2(y, x)
    ring = (r > 0.66) & (r < 0.88)
    spikes = (np.abs(np.mod(a * 4 / TAU + 0.5, 1) - 0.5) < 0.1 * (1.05 - r)) & (r >= 0.88) & (r < 1.0)
    inner_lip = (r > 0.6) & (r <= 0.66)
    shape = ring | spikes | inner_lip
    v = 0.55 + 0.25 * np.cos((r - 0.77) * 14) + 0.2 * (y > 0) - 0.1 * (y < -0.4)
    rgb = fx.sramp(em.GOLD, v + fx.dither(ctx, 0.05))
    # rune glyphs around the band (polar-unwrapped)
    gx = (a / TAU + 0.5) * 44.0
    gy = (r - 0.66) / 0.22 * 5.0
    rm, cid = fx.runes(gx * 1.0, gy * 1.0, cell=5.0, seed=17, density=0.45, stroke=0.5)
    gly = ring & rm & (gy > 0.4) & (gy < 4.6)
    rgb[gly] = em.ENDER[5]
    rgb[inner_lip] = em.GOLD[2]
    return rgb, np.where(shape, 255, 0), gly


def shade_tasset(ctx):
    x, y = fx.plane_xy(ctx)
    rgb, glow = em.purpur(ctx, cracked=True, tile=8)
    shape = (y > -0.6 - (1 - np.abs(x)) * 0.4)
    inner = (y > -0.6 - (1 - np.abs(x)) * 0.4 + 0.1) & (np.abs(x) < 0.9) & (y < 0.92)
    edge = shape & ~inner
    rgb[edge] = fx.sramp(em.GOLD, 0.62 + 0.25 * (y[edge] + 1) / 2)
    glow = glow & inner
    return rgb, np.where(shape, 255, 0), glow


def shade_tabard(ctx):
    """Long royal tabard: deep violet cloth, gold border, ender-eye emblem in a gold lozenge, a
    column of runes and a ragged hem."""
    x, y = fx.plane_xy(ctx)
    p = ctx.p
    W, H = ctx.tw, ctx.th
    yy = (1 - ctx.t) * H / 2          # model units from the bottom
    # cloth folds: vertical sinusoidal pleats shaded across the width
    pleat = np.sin(x * 7.5 + fbm(p, 0.2, 2, 3) * 2.0)
    v = 0.42 + 0.1 * pleat + (fbm(p, 0.6, 3, 5) - 0.5) * 0.12 - 0.12 * ctx.t
    rgb = fx.dramp(em.PURPUR_D, v, ctx)
    glow = np.zeros(ctx.N, dtype=bool)
    # ragged hem
    hem_y = -0.9 + 0.05 * np.sin(x * 9) + (fbm(np.c_[x * 4, x * 0, x * 0], 1.0, 2, 9) - 0.5) * 0.12
    shape = y > hem_y
    # gold border
    d_side = 1 - np.abs(x)
    border = (d_side * W / 2 < 1.3) | ((y - hem_y) * H / 2 < 1.3)
    border_in = ((d_side * W / 2 >= 1.9) & (d_side * W / 2 < 2.4))
    rgb[border] = fx.sramp(em.GOLD, 0.65 + 0.2 * pleat[border])
    rgb[border_in] = em.GOLD[4]
    # emblem: gold lozenge with an ender eye, upper third
    ex, ey = x * W / 2, (y - 0.55) * H / 2
    loz = np.abs(ex) / 5.6 + np.abs(ey) / 5.6
    rgb[(loz < 1.0) & (loz > 0.82)] = em.GOLD[6]
    eye_r = np.sqrt((ex / 3.0) ** 2 + (ey / 2.0) ** 2)
    iris = eye_r < 1.0
    rgb[iris] = fx.sramp(em.TEAL, 0.9 - eye_r[iris] * 0.5)
    pupil = iris & (np.abs(ex) < 0.6 * (1 - (ey / 2.0) ** 2))
    rgb[pupil] = np.array([10, 26, 22])
    glow |= iris & ~pupil
    # rune column
    m, cid = fx.runes(ctx.i.astype(float) - W + 3.0, ctx.j.astype(float), cell=6.0, seed=23, density=0.42)
    col = m & (np.abs(x) * W / 2 < 2.5) & (y < 0.15) & (y > hem_y + 0.12)
    rgb[col] = em.ENDER[4]
    glow |= col
    return rgb, np.where(shape, 255, 0), glow & shape


def shade_beard(ctx):
    """Carved obsidian beard: braided strands with gold rings, split into three braid tips."""
    x, y = fx.plane_xy(ctx)
    p = ctx.p
    yy = (y + 1) / 2                 # 0 bottom .. 1 top
    width = 0.55 + 0.45 * yy ** 0.6
    braid_ix = np.round(x * 1.5)
    split = (yy < 0.38)
    in_braid = np.abs(x * 1.5 - braid_ix) < (0.36 + 0.5 * (yy / 0.38)) if True else True
    shape = (np.abs(x) < width) & (~split | (in_braid & (np.abs(braid_ix) <= 1)))
    tip = yy > 0.03 + 0.12 * np.abs(braid_ix) * 0.4
    shape &= tip
    strand = np.sin((x * 9 + y * 2.5 * np.sign(np.sin(y * 9))) * 3.0)
    v = 0.56 + 0.2 * strand + (fbm(p, 0.8, 2, 7) - 0.5) * 0.15 + 0.12 * yy
    rgb = fx.dramp(em.OBSID, v, ctx, 0.6)
    rings = (np.abs(yy - 0.44) < 0.045) | (np.abs(yy - 0.22) < 0.04)
    rgb[rings & shape] = fx.sramp(em.GOLD, 0.7 + 0.2 * np.cos(x[rings & shape] * 6))
    return rgb, np.where(shape, 255, 0), False


def shade_crown(ctx):
    """Crown wall (plane): low gold band with three bold points; the front wall's centre point
    is a tall spire crowned by a glowing ender pearl."""
    x, y = fx.plane_xy(ctx)
    W, H = ctx.tw, ctx.th
    yy = (y + 1) / 2                  # 0 bottom .. 1 top
    xx = (x + 1) / 2
    front = bool(ctx.params.get("front"))
    k = np.floor(xx * 3)
    fxp = xx * 3 - k - 0.5            # -0.5..0.5 within a point cell
    centre = k == 1
    peak = np.where(centre, 0.92 if front else 0.78, 0.62 if front else 0.55)
    base_h = 0.2
    band = yy < base_h
    wpt = 0.5 * np.clip(1 - (yy - base_h) / (peak - base_h), 0, 1) ** 0.8
    point = (yy >= base_h) & (yy < peak) & (np.abs(fxp) < wpt)
    orb_r = np.sqrt((fxp * W / 3 / 2) ** 2 + ((yy - peak - 0.03) * H / 2) ** 2)
    orb = orb_r < (1.1 if (front) else 0.85)
    orb &= ~band
    shape = band | point | orb
    # engraved centre groove on each point, bevelled band
    groove = point & (np.abs(fxp) < 0.05) & (yy > base_h + 0.06)
    v = 0.58 + 0.22 * (1 - np.abs(fxp) * 2) * point + 0.25 * np.exp(-((ctx.t - 0.25) / 0.2) ** 2)
    v += 0.2 * (band & (np.abs(yy - base_h * 0.5) < 0.03)) - 0.15 * groove
    rgb = fx.sramp(em.GOLD, v + fx.dither(ctx, 0.05))
    gem = band & centre & (np.abs(fxp) < 0.15) & (np.abs(yy - base_h * 0.5) < 0.08)
    rgb[gem] = fx.sramp(em.ENDER, 0.75 - np.abs(fxp[gem]) * 1.5)
    glow = gem.copy()
    if front:
        pearl = orb & centre
        rgb[pearl] = fx.sramp(em.TEAL, 0.95 - orb_r[pearl] * 0.25)
        glow |= pearl
    return rgb, np.where(shape, 255, 0), glow & shape


def shade_cape(ctx):
    """Cape of violet energy: deep violet field with flowing luminous filaments, star motes,
    glowing edges and a ragged, flame-like hem. Global coordinates keep it continuous across the
    two halves and three segments."""
    half = ctx.params["half"]
    off, h = ctx.params["off"], ctx.params["seg_h"]
    gy = (off + ctx.t * h) / CAPE_TOTAL                     # 0 top .. 1 bottom
    gx = (ctx.s - 1.0) if half < 0 else ctx.s               # -1 .. 1 across the whole cape
    q = np.c_[gx * CAPE_W, gy * CAPE_TOTAL, np.zeros(ctx.N)]
    warp = fbm(q, 0.05, 3, 71) - 0.5
    fil_n = vnoise(np.c_[gx * 4.5 + warp * 2.5, gy * 1.4, np.zeros(ctx.N)], 1.0, 73)
    ridge = np.abs(fil_n - 0.5)
    base = 0.18 + 0.22 * gy + (fbm(q, 0.12, 3, 75) - 0.5) * 0.18 + 0.06 * np.sin(gx * 9 + warp * 4)
    # soft fold shading (vertical folds)
    base += 0.07 * np.sin(gx * 13 + warp * 3)
    rgb = fx.dramp(em.ENDER, base, ctx, 0.7)
    fil = ridge < 0.03 + 0.015 * gy
    core_f = ridge < 0.012
    rgb[fil] = fx.sramp(em.ENDER, 0.6 + gy[fil] * 0.2)
    rgb[core_f] = em.ENDER[7]
    st = fx.stars(q, 0.9, 0.035, 77) > 0.25
    rgb[st] = em.ENDER[8]
    edge = np.abs(gx) > 0.955
    rgb[edge] = fx.sramp(em.ENDER, 0.72 + (np.abs(gx[edge]) - 0.955) * 4)
    # collar band at the top
    collar = gy < 0.025
    rgb[collar] = fx.sramp(em.GOLD, 0.7 - gy[collar] * 8)
    # ragged flame hem
    tongue = 0.05 * (np.sin(gx * 23) * 0.5 + 0.5) + (fbm(np.c_[gx * 6, gx * 0, gx * 0], 1.0, 2, 79) - 0.5) * 0.06
    hem = 1.0 - 0.07 - tongue
    shape = gy < hem
    rim = shape & (gy > hem - 0.018)
    rgb[rim] = em.ENDER[6]
    holes = (fbm(q, 0.22, 2, 81) > 0.74) & (gy > 0.55)
    shape &= ~holes
    hole_rim = (fbm(q, 0.22, 2, 81) > 0.70) & (gy > 0.55) & shape
    rgb[hole_rim] = em.ENDER[5]
    glow = fil | st | edge | rim | hole_rim
    return rgb, np.where(shape, 255, 0), glow & shape & ~collar


# ------------------------------------------------------------------------------- stage parts

FACE_SHADE = {"north": 0.06, "west": 0.1, "east": -0.04, "south": -0.08, "up": 0.12, "down": -0.14}


def spike_prog(ctx):
    """0 at the base .. 1 at the tip of a crystal (stacked spike segments or a single box)."""
    pr = ctx.params
    if "spike_base" in pr:
        return np.clip((ctx.p[:, 1] - pr["spike_base"][1]) / pr["spike_len"], 0, 1)
    return np.clip((ctx.p[:, 1] - ctx.lo[1]) / max(1e-6, ctx.hi[1] - ctx.lo[1]), 0, 1)


def taper_alpha(ctx, frac):
    """Chisel point cut into the texture: over the top `frac` of the box the north and east faces
    narrow to the edge they share and the south/west faces and the cap are cleared. All four faces
    meeting in one apex on that edge reads as a single crystal point from every side (a symmetric
    taper on each face would show a forked double tip from the diagonals). With the default 45 deg
    spin that edge faces the front. Returns (shape mask, 0..1 distance from the cut edge)."""
    full = np.ones(ctx.N, dtype=bool)
    if frac <= 0:
        return full, np.ones(ctx.N)
    if ctx.face == "up":
        return ~full, np.zeros(ctx.N)
    if ctx.face == "down":
        return full, np.ones(ctx.N)
    w = np.clip(ctx.t / frac, 0, 1) ** 0.85          # face width left at this height (1 = full)
    if ctx.face == "north":                          # apex at its +X end (s = 1)
        x = 1 - ctx.s
    elif ctx.face == "east":                         # apex at its -Z end (s = 0)
        x = ctx.s
    else:
        return ctx.t >= frac, np.ones(ctx.N)
    return x <= w + 0.5 / ctx.tw, np.clip(w - x, 0, 1)


def _tip_frac(ctx):
    pr = ctx.params
    if "nseg" in pr:                                  # stacked spike: only the last segment tapers
        return pr.get("tip", 0.5) if pr["seg"] == pr["nseg"] - 1 else 0.0
    return pr.get("tip", 0.0)


def shade_crystal(ctx):
    """Purpur crystal shard: pale lilac facets that brighten towards the point, bright lit edges, a
    glowing violet heart running up the middle and a glowing tip."""
    prog = spike_prog(ctx)
    shape, ed = taper_alpha(ctx, _tip_frac(ctx))
    x = np.abs(ctx.s - 0.5) * 2
    v = 0.42 + 0.34 * prog + FACE_SHADE.get(ctx.face, 0.0) + 0.18 * fx.spec(ctx, 4) - ctx.ao * 0.4
    v = v + 0.08 * np.sin(ctx.p[:, 1] * 0.9 + ctx.index) * (1 - prog)          # growth bands
    rgb = fx.dramp(em.PURPUR, v, ctx, 0.7)
    glow = np.zeros(ctx.N, dtype=bool)
    if ctx.face not in ("up", "down"):
        edge = (ed < 0.16) | (x > 0.84)
        rgb[edge] = fx.sramp(em.PURPUR, np.clip(v[edge] + 0.3, 0, 1))
        heart = (x < 0.2 + 0.1 * (1 - prog)) & (prog > 0.12)
        rgb[heart] = fx.sramp(em.ENDER, 0.52 + 0.3 * prog[heart])
        tip = prog > 0.86
        rgb[tip] = fx.sramp(em.ENDER, 0.7 + 0.25 * (prog[tip] - 0.86) / 0.14)
        glow = heart | tip
    elif ctx.face == "down":
        rgb[:] = em.PURPUR[1]
    return rgb, np.where(shape, 255, 0), glow & shape


def shade_obsidian_spike(ctx):
    """Floating obsidian spike: glossy black glass with a violet vein up its spine and a hot tip."""
    prog = spike_prog(ctx)
    shape, ed = taper_alpha(ctx, _tip_frac(ctx))
    rgb, glow = em.obsidian(ctx, glints=True, seed=7)
    if ctx.face not in ("up", "down"):
        x = np.abs(ctx.s - 0.5) * 2
        rim = ed < 0.18
        rgb[rim] = em.OBSID[6]
        wig = 0.12 * np.sin(ctx.t * 9 + ctx.index)
        vein = (np.abs((ctx.s - 0.5) * 2 - wig) < 0.17) & (prog > 0.05)
        rgb[vein] = fx.sramp(em.ENDER, 0.45 + 0.4 * prog[vein])
        tip = prog > 0.8
        rgb[tip] = fx.sramp(em.ENDER, 0.62 + 0.35 * (prog[tip] - 0.8) / 0.2)
        glow = glow | vein | tip
    return rgb, np.where(shape, 255, 0), glow & shape


def shade_end_frame(ctx):
    """End-crystal glass cage: a pale glowing frame with an inner hairline, glass otherwise clear."""
    d = fx.edge_dist(ctx)
    frame = d <= 1
    inner = d == 3
    glint = (np.abs(ctx.i - ctx.j) <= 0) & (d >= 3) & (d <= 4)
    m = frame | inner | glint
    rgb = np.zeros((ctx.N, 3)) + em.ENDER[7]
    rgb[d == 1] = em.ENDER[6]
    rgb[inner | glint] = em.ENDER[5]
    return rgb, np.where(m, 255, 0), m


def shade_end_core(ctx):
    """End-crystal heart: magenta-violet facets crossed by dark seams, fully glowing."""
    x, y = fx.plane_xy(ctx)
    v = 0.78 - 0.32 * np.maximum(np.abs(x), np.abs(y)) + 0.1 * ((x < 0) & (y > 0)) + FACE_SHADE.get(ctx.face, 0) * 0.5
    rgb = fx.mix(fx.sramp(em.MAGENTA, v), fx.sramp(em.ENDER, v + 0.05), 0.45)
    seam = (np.abs(np.abs(x) - np.abs(y)) < 0.13) & (np.maximum(np.abs(x), np.abs(y)) > 0.25)
    rgb[seam] = em.ENDER[1]
    glow = ~seam
    return rgb, 255, glow


def shade_chest_eye(ctx):
    """A newly opened ender eye on the pectoral: gold-lidded almond, violet sclera, teal iris with a
    slit pupil (front face); the edges are obsidian."""
    rgb, glow = em.obsidian(ctx, glints=False)
    if ctx.face != "north":
        return rgb, 255, glow
    x, y = fx.plane_xy(ctx)
    lid = np.abs(y) < 0.98 * (1 - x * x) ** 0.8
    eye = np.abs(y) < 0.72 * (1 - (x / 0.9) ** 2).clip(0) ** 0.8
    rgb[lid & ~eye] = fx.sramp(em.GOLD, 0.62 + 0.25 * y[lid & ~eye])
    rgb[eye] = fx.sramp(em.ENDER, 0.38 + 0.25 * (1 - np.abs(x[eye])))
    ix, iy = x * 1.45, y
    r = np.sqrt(ix * ix + iy * iy)
    iris = eye & (r < 0.62)
    rgb[iris] = fx.sramp(em.TEAL, 0.92 - r[iris] * 0.6)
    pupil = iris & (np.abs(ix) < 0.13 * (1 - (iy / 0.6) ** 2).clip(0) + 0.02) & (np.abs(iy) < 0.58)
    rgb[pupil] = np.array([10, 30, 24])
    glow = glow | (eye & ~pupil)
    return rgb, 255, glow


SHADERS = {
    "purpur_c": _wrap(lambda c: em.purpur(c, cracked=True)),
    "purpur_ct": _wrap(lambda c: em.purpur(c, cracked=True, trim="gold")),
    "purpur_helm": _wrap(lambda c: em.purpur(c, cracked=True, trim="gold", tile=8)),
    "obsidian": _wrap(lambda c: em.obsidian(c)),
    "obsidian_runes": _wrap(lambda c: em.obsidian(c, runes_on=True, rune_cell=7.0, rune_fill=0.6)),
    "gold": _wrap(lambda c: em.gold(c)),
    "gold_band": _wrap(lambda c: em.gold(c, filig=False, rivets=True)),
    "gold_fin": _wrap(lambda c: em.gold(c, filig=False)),
    "gem": shade_gem,
    "eye_core": _wrap(em.ender_eye),
    "core_ring": shade_core_ring,
    "eye_slit": shade_eye_slit,
    "orb": shade_orb,
    "clasp": shade_clasp,
    "rune_plate": shade_rune_plate,
    "tasset": shade_tasset,
    "tabard": shade_tabard,
    "beard": shade_beard,
    "crown": shade_crown,
    "cape": shade_cape,
    "rod": _wrap(lambda c: em.end_rod(c, c.params.get("tip", 0.0))),
    # evolution stage parts
    "crystal": shade_crystal,
    "obsidian_spike": shade_obsidian_spike,
    "end_frame": shade_end_frame,
    "end_core": shade_end_core,
    "chest_eye": shade_chest_eye,
}

# =============================================================================== animations
LEGS = [("right_leg", "right_shin"), ("left_leg", "left_shin")]
FEET = ["right_foot", "left_foot"]
CAPES = ["cape_top", "cape_mid", "cape_low"]


def ambient(c, T, cape_amp=1.0, core_amp=0.05, cape_bias=0.0):
    """Layers that every clip carries so nothing snaps when the attack controller takes over:
    cape ripple, core pulse and a faint tabard sway (whole periods of T)."""
    for k, nm in enumerate(CAPES):
        c.f(nm, "rotation", lambda t, k=k: (cape_bias * (1 + 0.5 * k) + cape_amp * (2.0 + k) * math.sin(TAU * t / T - k * 0.9),
                                             cape_amp * 1.5 * math.sin(TAU * t / T * 2 - k * 1.1), 0))
    c.f("core", "scale", lambda t: (1 + core_amp * math.sin(TAU * t / T * 2),) * 3)
    c.f("tabard", "rotation", lambda t: (cape_amp * 1.5 * math.sin(TAU * t / T - 0.6), 0, cape_amp * 1.0 * math.sin(TAU * t / T * 2)))


def anim_idle():
    T = 4.0
    c = Clip("idle", T, loop=True)
    w = lambda t, ph=0.0: math.sin(TAU * t / T + ph)
    ambient(c, T)
    c.f("torso", "rotation", lambda t: (1.2 * w(t), 0, 0))
    c.f("torso", "position", lambda t: (0, 0.35 * w(t), 0))
    c.f("neck", "rotation", lambda t: (-1.0 * w(t, 0.5), 0, 0))
    for s, nm in sides():
        c.f(f"{nm}_arm", "rotation", lambda t, s=s: (1.8 * w(t, 0.7), 0, (2.0 + 1.0 * w(t, 0.4)) * -s))
        c.f(f"{nm}_forearm", "rotation", lambda t: (-8 - 2 * w(t, 1.1), 0, 0))
    c.f("crown", "position", lambda t: (0, 0.15 * w(t, 1.5), 0))
    return c


def anim_walk():
    T = 2.4
    c = Clip("walk", T, loop=True)
    ph = lambda t: TAU * t / T
    ambient(c, T / 2, cape_amp=1.4, cape_bias=4.0)
    A = 20.0
    for s, nm in sides():
        sg = 1 if nm == "right" else -1
        c.f(f"{nm}_leg", "rotation", lambda t, sg=sg: (-A * sg * math.sin(ph(t)), 0, 0))
        c.f(f"{nm}_shin", "rotation", lambda t, sg=sg: (30 * max(0.0, sg * math.cos(ph(t))) ** 1.5, 0, 0))
        c.f(f"{nm}_foot", "rotation", lambda t, sg=sg: (A * sg * math.sin(ph(t)) * 0.6 - 16 * max(0.0, sg * math.cos(ph(t))) ** 1.5, 0, 0))
        c.f(f"{nm}_arm", "rotation", lambda t, sg=sg, s=s: (14 * sg * math.sin(ph(t)), 0, 2.5 * -s))
        c.f(f"{nm}_forearm", "rotation", lambda t, sg=sg: (-10 - 7 * max(0.0, -sg * math.sin(ph(t))), 0, 0))
    c.f("body", "position", lambda t: (0, -1.6 + 1.6 * math.cos(2 * ph(t)), 0))
    c.f("body", "rotation", lambda t: (0, 0, 2.0 * math.sin(ph(t))))
    c.f("torso", "rotation", lambda t: (3 + 1.2 * math.cos(2 * ph(t)), 5 * math.sin(ph(t)), -1.6 * math.sin(ph(t))))
    c.f("neck", "rotation", lambda t: (-3 - 1.0 * math.cos(2 * ph(t) - 0.6), -3 * math.sin(ph(t)), 0))
    c.f("tabard", "rotation", lambda t: (-6 + 4 * math.cos(2 * ph(t) - 0.8), 0, 0))
    c.f("crown", "position", lambda t: (0, 0.0, 0))
    return c


def anim_void_slam():
    L = 1.6
    c = Clip("attack.void_slam", L)
    ambient(c, L, cape_amp=0.6)
    imp = 0.9
    c.rot("torso", [(0, (0, 0, 0)), (0.6, (-16, 0, 0), "io"), (0.75, (-18, 0, 0)), (imp, (30, 0, 0), "in3"), (1.1, (27, 0, 0)),
                    (1.6, (0, 0, 0), "io")])
    c.f("torso", "rotation", lambda t: (tremor(t, imp, imp + 0.02, imp + 0.12, imp + 0.3, 1.6, 28), 0, tremor(t, imp, imp + 0.02, imp + 0.12, imp + 0.3, 1.2, 23, 2)))
    c.pos("body", [(0, (0, 0, 0)), (0.6, (0, 1.5, 2.0), "io"), (0.75, (0, 1.8, 2.0)), (imp, (0, -5.0, -3.0), "in3"), (1.1, (0, -4.6, -3.0)),
                   (1.6, (0, 0, 0), "io")])
    knee_bend(c, lambda t: 5.0 * env(t, 0.75, imp, 1.1, 1.6, "in3", "io"), THIGH, SHIN, LEGS, FEET, spread=0.4)
    for s, nm in sides():
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.6, (-168, 0, -s * 12), "io"), (0.75, (-172, 0, -s * 10)), (imp, (-52, 0, -s * 8), "in3"),
                            (1.1, (-50, 0, -s * 8)), (1.6, (0, 0, 0), "io")])
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.6, (-28, 0, 0)), (imp, (-12, 0, 0), "in3"), (1.6, (0, 0, 0))])
        c.rot(f"{nm}_hand", [(0, (0, 0, 0)), (0.6, (0, 0, -s * 14)), (imp, (0, 0, -s * 10), "in3"), (1.6, (0, 0, 0))])
    c.rot("neck", [(0, (0, 0, 0)), (0.6, (-10, 0, 0)), (imp, (8, 0, 0), "in3"), (1.6, (0, 0, 0))])
    c.scl("core", [(0, (1, 1, 1)), (0.75, (1.2, 1.2, 1.2)), (imp, (1.5, 1.5, 1.4), "snap"), (1.3, (1.0, 1.0, 1.0)), (1.6, (1, 1, 1))])
    c.rot("cape_top", [(0, (0, 0, 0)), (0.75, (-4, 0, 0)), (imp, (10, 0, 0), "in3"), (1.25, (4, 0, 0)), (1.6, (0, 0, 0))])
    c.rot("cape_mid", [(0, (0, 0, 0)), (0.8, (-4, 0, 0)), (imp + 0.05, (10, 0, 0), "in3"), (1.3, (3, 0, 0)), (1.6, (0, 0, 0))])
    c.rot("cape_low", [(0, (0, 0, 0)), (0.85, (-4, 0, 0)), (imp + 0.1, (12, 0, 0), "in3"), (1.35, (2, 0, 0)), (1.6, (0, 0, 0))])
    c.rot("tabard", [(0, (0, 0, 0)), (0.75, (6, 0, 0)), (imp, (-10, 0, 0), "in3"), (1.2, (-4, 0, 0)), (1.6, (0, 0, 0))])
    return c


def anim_ender_beam():
    L = 2.5
    c = Clip("attack.ender_beam", L)
    ambient(c, L / 2, cape_amp=0.7)
    sweep = tl.Track([(0, 0.0), (0.4, 0.0), (0.55, -32.0, "out"), (2.15, 32.0, "io"), (2.5, 0.0, "io")])
    c.f("torso", "rotation", lambda t: (0, float(sweep(t)) * 0.75, 0))
    c.f("neck", "rotation", lambda t: (0, float(sweep(t)) * 0.25, 0))
    c.rot("torso", [(0, (0, 0, 0)), (0.4, (-14, 0, 0), "io"), (0.55, (6, 0, 0), "snap"), (2.15, (5, 0, 0)), (2.5, (0, 0, 0), "io")])
    c.f("torso", "rotation", lambda t: (tremor(t, 0.5, 0.6, 2.05, 2.2, 0.8, 24), 0, tremor(t, 0.5, 0.6, 2.05, 2.2, 0.6, 19, 4)))
    c.rot("neck", [(0, (0, 0, 0)), (0.4, (-12, 0, 0)), (0.55, (4, 0, 0), "snap"), (2.15, (4, 0, 0)), (2.5, (0, 0, 0))])
    c.pos("body", [(0, (0, 0, 0)), (0.4, (0, -1.5, 1.5)), (0.55, (0, -2.5, 0), "snap"), (2.15, (0, -2.5, 0)), (2.5, (0, 0, 0))])
    knee_bend(c, lambda t: 1.5 * env(t, 0, 0.4, 0.42, 0.55) + 2.5 * env(t, 0.42, 0.55, 2.15, 2.5), THIGH, SHIN, LEGS, FEET, spread=0.6)
    for s, nm in sides():
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.4, (12, 0, -s * 40)), (0.55, (-10, 0, -s * 34), "snap"), (2.15, (-12, 0, -s * 32)),
                            (2.5, (0, 0, 0), "io")])
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.4, (-40, 0, 0)), (0.55, (-22, 0, 0), "snap"), (2.15, (-24, 0, 0)), (2.5, (0, 0, 0))])
        c.rot(f"{nm}_hand", [(0, (0, 0, 0)), (0.4, (0, 0, -s * 20)), (0.55, (0, 0, -s * 28), "snap"), (2.15, (0, 0, -s * 26)), (2.5, (0, 0, 0))])
    c.scl("core", [(0, (1, 1, 1)), (0.4, (1.25, 1.25, 1.2)), (0.55, (1.45, 1.45, 1.3), "snap"), (2.15, (1.4, 1.4, 1.3)), (2.5, (1, 1, 1))])
    c.pos("crown", [(0, (0, 0, 0)), (0.55, (0, 1.2, 0), "snap"), (2.15, (0, 1.2, 0)), (2.5, (0, 0, 0))])
    for k, nm in enumerate(CAPES):
        c.rot(nm, [(0, (0, 0, 0)), (0.4, (-3, 0, 0)), (0.6, (10 + 4 * k, 0, 0), "out"), (2.15, (8 + 3 * k, 0, 0)), (2.5, (0, 0, 0))])
    return c


def anim_rift_blink():
    L = 1.4
    c = Clip("attack.rift_blink", L)
    ambient(c, L, cape_amp=0.5)
    imp = 0.8
    drop = tl.Track([(0, 0.0), (0.45, 9.0, "io"), (0.6, 9.5), (0.68, 0.0, "snap"), (imp, -1.0, "out"), (imp + 0.02, 3.0, "snap"),
                     (1.0, 2.5), (1.4, 0.0, "io")])
    c.f("body", "position", lambda t: (0, -float(drop(t)), 0))
    knee_bend(c, lambda t: max(0.0, float(drop(t))), THIGH, SHIN, LEGS, FEET, spread=0.8)
    # warp squash as it blinks through the rift
    c.scl("body", [(0, (1, 1, 1)), (0.55, (1.0, 1.0, 1.0)), (0.62, (0.82, 1.18, 0.82), "snap"), (0.7, (1.12, 0.9, 1.12), "snap"),
                   (0.78, (1, 1, 1), "out"), (1.4, (1, 1, 1))])
    c.rot("torso", [(0, (0, 0, 0)), (0.45, (26, 0, 0), "io"), (0.6, (28, 0, 0)), (0.68, (-12, 0, 0), "snap"), (imp, (24, -16, 0), "in3"),
                    (1.0, (22, -14, 0)), (1.4, (0, 0, 0), "io")])
    # arms wrap in during the crouch, then the right fist hammers down
    c.rot("right_arm", [(0, (0, 0, 0)), (0.45, (-50, -30, -22)), (0.6, (-52, -30, -24)), (0.68, (-175, 0, 20), "snap"),
                        (imp, (-62, 0, 10), "in3"), (1.0, (-60, 0, 10)), (1.4, (0, 0, 0), "io")])
    c.rot("left_arm", [(0, (0, 0, 0)), (0.45, (-50, 30, 22)), (0.6, (-52, 30, 24)), (0.68, (-30, 0, -40), "snap"),
                       (imp, (10, 0, -30), "in3"), (1.0, (8, 0, -28)), (1.4, (0, 0, 0), "io")])
    for nm in ("right_forearm", "left_forearm"):
        c.rot(nm, [(0, (0, 0, 0)), (0.45, (-70, 0, 0)), (0.68, (-20, 0, 0), "snap"), (imp, (-6, 0, 0), "in3"), (1.4, (0, 0, 0))])
    c.rot("neck", [(0, (0, 0, 0)), (0.45, (-18, 0, 0)), (0.68, (-6, 0, 0), "snap"), (imp, (10, 0, 0)), (1.4, (0, 0, 0))])
    c.scl("core", [(0, (1, 1, 1)), (0.45, (0.7, 0.7, 0.9)), (0.68, (1.6, 1.6, 1.4), "snap"), (imp, (1.4, 1.4, 1.3)), (1.4, (1, 1, 1))])
    for k, nm in enumerate(CAPES):
        c.rot(nm, [(0, (0, 0, 0)), (0.45, (-6 - 3 * k, 0, 0)), (0.68, (12 + 5 * k, 0, 0), "snap"), (imp, (6, 0, 0)), (1.4, (0, 0, 0))])
    c.rot("tabard", [(0, (0, 0, 0)), (0.45, (-30, 0, 0)), (0.68, (20, 0, 0), "snap"), (imp, (-20, 0, 0)), (1.4, (0, 0, 0))])
    return c


def anim_shulker_barrage():
    L = 2.0
    c = Clip("attack.shulker_barrage", L)
    ambient(c, L, cape_amp=0.6)
    c.rot("torso", [(0, (0, 0, 0)), (0.45, (-14, 0, 0), "io"), (1.65, (-12, 0, 0)), (2.0, (0, 0, 0), "io")])
    c.rot("neck", [(0, (0, 0, 0)), (0.45, (-14, 0, 0)), (1.65, (-12, 0, 0)), (2.0, (0, 0, 0))])
    pulses = (0.6, 0.85, 1.1, 1.35, 1.6)
    jolt = lambda t: sum(math.exp(-((t - p) / 0.05) ** 2) for p in pulses)
    for s, nm in sides():
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.45, (-150, 0, -s * 30), "io"), (1.65, (-148, 0, -s * 30)), (2.0, (0, 0, 0), "io")])
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.45, (-20, 0, 0)), (1.65, (-20, 0, 0)), (2.0, (0, 0, 0))])
        c.rot(f"{nm}_hand", [(0, (0, 0, 0)), (0.45, (30, 0, 0)), (1.65, (30, 0, 0)), (2.0, (0, 0, 0))])
        c.f(f"{nm}_arm", "rotation", lambda t, s=s: (8 * jolt(t + (0.12 if s > 0 else 0)), 0, 0))
    c.f("torso", "rotation", lambda t: (-2.5 * jolt(t), 0, 0))
    c.f("core", "scale", lambda t: (1 + 0.35 * env(t, 0.3, 0.45, 1.65, 2.0) + 0.15 * jolt(t),) * 3)
    c.pos("body", [(0, (0, 0, 0)), (0.45, (0, 1.0, 0)), (1.65, (0, 1.0, 0)), (2.0, (0, 0, 0))])
    c.pos("crown", [(0, (0, 0, 0)), (0.45, (0, 1.5, 0)), (1.65, (0, 1.5, 0)), (2.0, (0, 0, 0))])
    for k, nm in enumerate(CAPES):
        c.f(nm, "rotation", lambda t, k=k: (6 * env(t, 0.3, 0.6, 1.6, 2.0) + 2.5 * jolt(t - 0.05 * k), 0, 0))
    return c


def anim_gravity_well():
    L = 2.5
    c = Clip("attack.gravity_well", L)
    ambient(c, L / 2, cape_amp=0.5)
    imp = 2.3
    gather = lambda t: env(t, 0.1, 0.6, 1.9, 2.05)
    circ = lambda t, s: (8 * math.sin(TAU * t * 1.6) * gather(t), 10 * s * math.cos(TAU * t * 1.6) * gather(t), 0)
    for s, nm in sides():
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.6, (-80, -s * 30, -s * 14), "io"), (1.9, (-84, -s * 26, -s * 14)),
                            (2.12, (-175, 0, -s * 8), "out"), (imp, (-40, 0, -s * 10), "in3"), (2.5, (0, 0, 0), "io")])
        c.f(f"{nm}_arm", "rotation", lambda t, s=s: circ(t, s))
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.6, (-30, 0, 0)), (1.9, (-34, 0, 0)), (2.12, (-14, 0, 0)), (imp, (-8, 0, 0), "in3"),
                                (2.5, (0, 0, 0))])
        c.rot(f"{nm}_hand", [(0, (0, 0, 0)), (0.6, (0, 0, -s * 40)), (1.9, (0, 0, -s * 40)), (2.12, (0, 0, 0)), (2.5, (0, 0, 0))])
    c.rot("torso", [(0, (0, 0, 0)), (0.6, (8, 0, 0)), (1.9, (10, 0, 0)), (2.12, (-14, 0, 0), "out"), (imp, (28, 0, 0), "in3"),
                    (2.5, (0, 0, 0), "io")])
    c.f("torso", "rotation", lambda t: (tremor(t, 0.6, 1.0, 1.85, 1.95, 0.8, 18), tremor(t, 0.6, 1.0, 1.85, 1.95, 0.6, 15, 1), 0))
    drop = tl.Track([(0, 0.0), (0.6, 2.5), (1.9, 3.5), (2.12, -0.5, "out"), (imp, 5.0, "in3"), (2.5, 0.0, "io")])
    c.f("body", "position", lambda t: (0, -float(drop(t)), 0))
    knee_bend(c, lambda t: max(0.0, float(drop(t))), THIGH, SHIN, LEGS, FEET, spread=0.6)
    c.f("core", "scale", lambda t: (1 + 0.6 * tl.ease("in", min(1.0, max(0.0, (t - 0.2) / 1.9))) * (1 - tl.ease("out", max(0.0, (t - imp) / 0.2))),) * 3)
    c.rot("neck", [(0, (0, 0, 0)), (0.6, (6, 0, 0)), (2.12, (-12, 0, 0)), (imp, (10, 0, 0), "in3"), (2.5, (0, 0, 0))])
    for k, nm in enumerate(CAPES):
        c.rot(nm, [(0, (0, 0, 0)), (0.6, (-6 - 2 * k, 0, 0)), (1.9, (-8 - 3 * k, 0, 0)), (2.12, (-6, 0, 0)),
                   (imp, (10 + 4 * k, 0, 0), "in3"), (2.5, (2, 0, 0), "out")])
    c.rot("tabard", [(0, (0, 0, 0)), (0.6, (-8, 0, 0)), (2.12, (6, 0, 0)), (imp, (-8, 0, 0), "in3"), (2.5, (-1, 0, 0), "out")])
    return c


def anim_phase():
    L = 2.0
    c = Clip("phase", L)
    ambient(c, L, cape_amp=0.4)
    c.rot("torso", [(0, (0, 0, 0)), (0.5, (20, 0, 0), "io"), (0.75, (-18, 0, 0), "snap"), (1.5, (-16, 0, 0)), (2.0, (0, 0, 0), "io")])
    c.f("torso", "rotation", lambda t: (tremor(t, 0.75, 0.8, 1.4, 1.55, 1.3, 22), tremor(t, 0.75, 0.8, 1.4, 1.55, 1.0, 18, 3), 0))
    c.rot("neck", [(0, (0, 0, 0)), (0.5, (14, 0, 0)), (0.75, (-24, 0, 0), "snap"), (1.5, (-22, 0, 0)), (2.0, (0, 0, 0))])
    c.pos("body", [(0, (0, 0, 0)), (0.5, (0, -4.0, 0)), (0.75, (0, 1.0, 0), "snap"), (1.5, (0, 0.8, 0)), (2.0, (0, 0, 0))])
    knee_bend(c, lambda t: 4.0 * env(t, 0.0, 0.5, 0.52, 0.75), THIGH, SHIN, LEGS, FEET, spread=0.6)
    for s, nm in sides():
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.5, (16, 0, s * 6)), (0.75, (-30, 0, -s * 76), "snap"), (1.5, (-28, 0, -s * 74)),
                            (2.0, (0, 0, 0), "io")])
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.5, (-84, 0, 0)), (0.75, (-26, 0, 0), "snap"), (1.5, (-24, 0, 0)), (2.0, (0, 0, 0))])
        c.rot(f"{nm}_hand", [(0, (0, 0, 0)), (0.75, (0, 0, -s * 24), "snap"), (1.5, (0, 0, -s * 22)), (2.0, (0, 0, 0))])
    c.pos("crown", [(0, (0, 0, 0)), (0.5, (0, -0.5, 0)), (0.75, (0, 5.0, 0), "snap"), (1.5, (0, 5.5, 0)), (2.0, (0, 0, 0), "io")])
    c.rot("crown", [(0, (0, 0, 0)), (0.6, (0, 0, 0)), (1.7, (0, 360, 0), "io"), (2.0, (0, 360, 0))])
    c.scl("core", [(0, (1, 1, 1)), (0.5, (0.7, 0.7, 0.9)), (0.75, (1.7, 1.7, 1.5), "snap"), (1.5, (1.6, 1.6, 1.5)), (2.0, (1, 1, 1))])
    for k, nm in enumerate(CAPES):
        c.rot(nm, [(0, (0, 0, 0)), (0.5, (-4, 0, 0)), (0.75, (14 + 7 * k, 0, 0), "snap"), (1.5, (10 + 6 * k, 0, 0)), (2.0, (0, 0, 0), "io")])
        c.f(nm, "rotation", lambda t, k=k: (tremor(t, 0.75, 0.8, 1.4, 1.6, 3.0, 13, k), 0, 0))
    c.rot("tabard", [(0, (0, 0, 0)), (0.5, (-20, 0, 0)), (0.75, (10, 0, 0), "snap"), (1.5, (8, 0, 0)), (2.0, (0, 0, 0))])
    return c


def anim_death():
    L = 2.8
    c = Clip("death", L, loop="hold")
    # the colossus reels, sinks to one knee, then slumps forward on its fists; the crown topples off
    c.rot("torso", [(0, (0, 0, 0)), (0.3, (-18, 6, 0), "out"), (1.0, (-6, 0, 6)), (1.7, (22, 0, 4), "io"), (2.4, (34, 0, 2), "io"),
                    (2.8, (34, 0, 2))])
    c.f("torso", "rotation", lambda t: (tremor(t, 0.2, 0.3, 1.0, 1.4, 2.2, 18), tremor(t, 0.2, 0.3, 1.0, 1.4, 1.8, 15, 2), 0))
    c.rot("neck", [(0, (0, 0, 0)), (0.3, (-22, 0, 0), "out"), (1.0, (-4, 0, 0)), (2.0, (16, 0, 0)), (2.8, (18, 0, 0))])
    drop = tl.Track([(0, 0.0), (1.0, 0.0), (1.7, 13.0, "in"), (1.85, 12.0, "out"), (2.0, 13.0, "in"), (2.8, 13.0)])
    kneel = lambda t: float(drop(t)) / 13.0
    c.f("body", "position", lambda t: (0, -float(drop(t)), -3 * kneel(t)))
    # right knee down, left foot planted forward
    c.f("right_leg", "rotation", lambda t: (8 * kneel(t), 0, 2 * kneel(t)))
    c.f("right_shin", "rotation", lambda t: (82 * kneel(t), 0, 0))
    c.f("right_foot", "rotation", lambda t: (-30 * kneel(t), 0, 0))
    c.f("left_leg", "rotation", lambda t: (-62 * kneel(t), 0, -4 * kneel(t)))
    c.f("left_shin", "rotation", lambda t: (70 * kneel(t), 0, 0))
    c.f("left_foot", "rotation", lambda t: (-8 * kneel(t), 0, 0))
    for s, nm in sides():
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.3, (-30, 0, -s * 34), "out"), (1.0, (-12, 0, -s * 12)), (1.8, (-30, 0, -s * 8)),
                            (2.4, (-44, 0, -s * 6)), (2.8, (-44, 0, -s * 6))])
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.3, (-40, 0, 0)), (1.0, (-12, 0, 0)), (2.4, (-4, 0, 0)), (2.8, (-4, 0, 0))])
    c.f("core", "scale", lambda t: ((1 + 0.3 * math.sin(t * 50) * env(t, 0.1, 0.2, 1.3, 1.7)) * (1 - 0.65 * tl.ease("io", (t - 1.5) / 1.1)),) * 3)
    # crown slips off the brow and falls to the floor in front
    c.pos("crown", [(0, (0, 0, 0)), (0.3, (0, 2.0, 1.0), "out"), (1.2, (0, 1.0, 0)), (1.7, (0, -2.0, -6.0), "in"),
                    (2.2, (0, -62.0, -24.0), "in"), (2.35, (0, -60.0, -25.0), "out"), (2.5, (0, -62.0, -26.0), "in"), (2.8, (0, -62.0, -26.0))])
    c.rot("crown", [(0, (0, 0, 0)), (1.2, (0, 0, 0)), (2.2, (-80, 30, 25), "in"), (2.8, (-84, 30, 25))])
    for k, nm in enumerate(CAPES):
        c.rot(nm, [(0, (0, 0, 0)), (0.3, (10 + 4 * k, 0, 0)), (1.0, (3, 0, 0)), (1.8, (6 + 14 * k, 0, 0)), (2.4, (8 + 22 * k, 0, 0)),
                   (2.8, (8 + 22 * k, 0, 0))])
    c.rot("tabard", [(0, (0, 0, 0)), (0.3, (-10, 0, 0)), (1.7, (-14, 0, 0)), (2.4, (-24, 0, 0)), (2.8, (-24, 0, 0))])
    return c


def _ev(c, bone, chan, t):
    v = c.eval(bone, chan, t)
    return np.zeros(3) if v is None else v


def secondary(c):
    """Derived motion added to every clip: the pauldrons follow a third of the arm swing (so a raised
    arm doesn't flip its plate under the shoulder) and the cape counters the torso lean so it keeps
    hanging under gravity instead of swinging up like a wing."""
    for s, nm in sides():
        arm = f"{nm}_arm"
        c.f(f"{nm}_pauldron", "rotation", lambda t, arm=arm: _ev(c, arm, "rotation", t) * np.array([0.32, 0.2, 0.4]))
        c.f(f"{nm}_pauldron", "position", lambda t, arm=arm: (0, 0.025 * max(0.0, -_ev(c, arm, "rotation", t)[0]), 0))
    torso_x = lambda t: float(_ev(c, "torso", "rotation", t)[0] + _ev(c, "body", "rotation", t)[0])
    c.f("cape_top", "rotation", lambda t: (-0.85 * torso_x(t), 0, 0))
    c.f("tabard", "rotation", lambda t: (-0.7 * torso_x(t), 0, 0))
    return c


def clips():
    cs = [anim_idle(), anim_walk(), anim_void_slam(), anim_ender_beam(), anim_rift_blink(), anim_shulker_barrage(),
          anim_gravity_well(), anim_phase(), anim_death()]
    return [secondary(c) for c in cs]


POSES = [
    ("idle", [0.0, 1.0, 2.0]),
    ("walk", [0.0, 0.6, 1.2, 1.8]),
    ("attack.void_slam", [0.6, 0.8, 0.9, 1.2]),
    ("attack.ender_beam", [0.4, 0.8, 1.6, 2.2]),
    ("attack.rift_blink", [0.45, 0.65, 0.8, 1.1]),
    ("attack.shulker_barrage", [0.45, 0.85, 1.6]),
    ("attack.gravity_well", [0.8, 1.6, 2.12, 2.3]),
    ("phase", [0.5, 0.8, 1.3]),
    ("death", [0.3, 1.3, 2.0, 2.8]),
]
HERO = ("attack.void_slam", 0.7)


def main():
    m = build_model()
    geo, rgba, glow, anims = tl.build(NAME, m, SHADERS, clips(), visible=(7, 7, 3.2))
    if "--preview" in sys.argv:
        print(fx.preview_rest(NAME, geo, rgba, glow, HITBOX))
        print(fx.preview_pose(NAME, geo, rgba, glow, anims, HERO[0], HERO[1]))
        if "--all" in sys.argv:
            for an, times in POSES:
                print(fx.preview_strip(NAME, geo, rgba, glow, anims, an, times, HITBOX))


if __name__ == "__main__":
    main()
