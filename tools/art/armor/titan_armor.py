"""Titan armor: massive dark-steel and carved stone plate with glowing elemental crystal inlays.

One geometry / UV layout, five textures: neutral, frost, tide, storm, magma.
Run: python titan_armor.py [--preview]
"""
import math
import os
import sys

import numpy as np

import armorkit as ak
import armorlib as al
import mats as M
from armorlib import Clip, fbm, hash3, worley
from common_geo import cube, sym, sym_spike, boxc, sym_boxc

NAME = "titan_armor"


# =============================================================================== geometry

def build_model():
    m = ak.new_model(NAME)
    H, B = m["armorHead"], m["armorBody"]
    RA, LA = m["armorRightArm"], m["armorLeftArm"]
    RL, LL = m["armorRightLeg"], m["armorLeftLeg"]
    RB, LB = m["armorRightBoot"], m["armorLeftBoot"]

    # ------------------------------------------------------------------ helmet
    cube(H, (-5, 23, -5), (10, 10, 10), "helm")                                  # great helm shell
    cube(H, (-5.5, 29.4, -5.7), (11, 2, 3), "steel", seams=False)                # heavy brow ridge
    cube(H, (-3, 23.4, -5.6), (6, 4, 1), "faceplate")                            # breathing guard
    sym(H, H, (-5.8, 22.6, -5.8), (3, 5, 5), "stone")                            # stone cheek guards
    sym(H, H, (-5.0, 23.6, -6.15), (1, 2, 1), "gem")                             # cheek crystal studs
    cube(H, (-1, 26.4, -6.2), (2, 5, 1), "crystal")                              # nasal crystal
    cube(H, (-2, 32.7, -4.4), (4, 1, 9), "stone")                                # stepped stone crest
    cube(H, (-1, 33.5, -3.6), (2, 1, 8), "stone")
    cube(H, (-5, 22.4, 4.6), (10, 3, 1), "steel", lames=True)                    # neck guard
    cube(H, (-1.5, 25.6, 4.7), (3, 6, 1), "stone", rune="nape")                  # nape rune plate
    sym(H, H, (-6.0, 25.8, -1.6), (1, 3, 3), "stone")                            # ear bosses
    sym(H, H, (-6.5, 26.8, -0.6), (1, 1, 1), "gem")                              # ear crystals
    crest = m.bone("helmCrystal", "armorHead", (0, 34, -3.6))
    crest.spike((0, 34.0, -3.6), (0, 1.0, -0.42), 5, 2, "crystal", segs=[0.62, 0.45], spin=45)
    tl_ = m.bone("helmHornR", "armorHead", (-5.2, 30.8, 0.6))
    tr_ = m.bone("helmHornL", "armorHead", (5.2, 30.8, 0.6))
    sym_spike(tl_, tr_, (-5.2, 30.8, 0.6), (-0.8, 1.0, 0.7), 4, 2, "crystal", segs=[0.62, 0.45])

    # ------------------------------------------------------------------ chestplate body
    cube(B, (-4.5, 11.5, -3), (9, 13, 6), "steel", seams=[16.5])                 # cuirass shell
    cube(B, (-5, 16.6, -4), (10, 7, 2), "steel", plate="breast")                 # breastplate
    cube(B, (-4.5, 15, -3.55), (9, 2, 1), "steel")                               # plackart lame
    cube(B, (-5, 13, -3.5), (10, 2, 7), "stone", rune="belt")                    # stone girdle
    cube(B, (-1, 13.4, -4.6), (2, 9, 1), "crystal")                              # crystal spine
    cube(B, (-3, 19.6, -4.55), (6, 2, 1), "crystal")                             # crystal cross arm
    cube(B, (-1.5, 18.9, -5.0), (3, 3, 1), "gem")                                # heart crystal
    sym(B, B, (-4.4, 12.4, -4.1), (1, 2, 1), "gem")                              # girdle studs
    cube(B, (-4.5, 15.8, 2.6), (9, 8, 2), "steel", plate="back")                 # back plate
    cube(B, (-2.5, 16.8, 4.3), (5, 5, 1), "stone", rune="core")                  # core housing
    cube(B, (-1.5, 17.8, 4.9), (3, 3, 1), "gem")                                 # back core crystal
    core = m.bone("backCrystals", "armorBody", (0, 22.6, 4.2))
    core.spike((0, 22.4, 4.0), (0, 1.0, 0.75), 6, 2, "crystal", segs=[0.62, 0.45])
    core.spike((-2.8, 21.8, 4.0), (-0.5, 1.0, 0.7), 5, 2, "crystal", segs=[0.62, 0.45])
    core.spike((2.8, 21.8, 4.0), (0.5, 1.0, 0.7), 5, 2, "crystal", segs=[0.62, 0.45])

    # ------------------------------------------------------------------ arms (chestplate)
    sym(RA, LA, (-8.5, 12, -2.5), (4, 12, 5), "steel", inflate=0.25, seams=[19.0])   # rerebrace sleeve
    sym(RA, LA, (-10.4, 20.8, -4.5), (6, 4, 9), "stone", rune="pauldron")         # massive pauldron
    sym(RA, LA, (-10.6, 19.4, -4.1), (6, 2, 8), "steel", rot=[0, 0, 10], pivot=[-7.6, 21.4, 0], rivets=True)
    sym(RA, LA, (-10.2, 24.7, -3.5), (5, 1, 7), "steel")                          # pauldron cap plate
    sym(RA, LA, (-9.25, 11.1, -3), (5, 6, 6), "steel", inflate=0.15)              # gauntlet
    sym(RA, LA, (-10.1, 16.0, -3.5), (6, 2, 7), "stone")                          # gauntlet cuff
    sym(RA, LA, (-10.0, 12.3, -1), (1, 3, 2), "crystal")                          # gauntlet crystal
    sym(RA, LA, (-9.0, 11.0, -3.6), (4, 2, 1), "steel")                           # knuckle guard
    pr = m.bone("pauldronCrystalsR", "armorRightArm", (-7.4, 25, 0))
    pl = m.bone("pauldronCrystalsL", "armorLeftArm", (7.4, 25, 0))
    sym_spike(pr, pl, (-7.8, 25.3, 0.8), (-0.35, 1.0, 0.25), 5, 3, "crystal", segs=[0.6, 0.45])
    sym_spike(pr, pl, (-9.3, 25.0, -1.4), (-0.9, 1.0, -0.2), 3, 2, "crystal", segs=[0.62, 0.5])

    # ------------------------------------------------------------------ leggings (belt lives in the legs)
    cube(RL, (-4.025, 0, -2.5), (4, 12, 5), "steel", inflate=0.375, seams=[4.0, 8.5], side=-1)  # cuisse + greave
    cube(LL, (-0.025, 0, -2.5), (4, 12, 5), "steel", inflate=0.425, seams=[4.0, 8.5], side=1)
    sym(RL, LL, (-5.0, 10.4, -3.5), (5, 2, 7), "stone", rune="legbelt")           # girdle half
    sym(RL, LL, (-1.0, 10.6, -3.95), (1, 2, 1), "crystal")                        # buckle crystal half
    sym(RL, LL, (-4.4, 6.4, -3.6), (4, 4, 1), "steel", rot=[-7, 0, 0], pivot=[-2.4, 10.4, -3.1], plate="tasset")
    sym(RL, LL, (-5.4, 5.6, -2.5), (1, 5, 5), "steel", rot=[0, 0, 7], pivot=[-4.9, 10.6, 0], plate="tasset")
    sym(RL, LL, (-4.3, 4.2, -3.4), (4, 3, 1), "steel")                            # knee cop
    sym(RL, LL, (-3.4, 4.7, -3.9), (2, 2, 1), "gem")                              # knee crystal
    sym(RL, LL, (-5.05, 0.8, -2.2), (1, 4, 4), "stone")                           # shin side guard

    # ------------------------------------------------------------------ boots
    cube(RB, (-4.75, -0.25, -3.0), (5, 6, 6), "steel", inflate=0.2, side=-1)       # sabaton shell
    cube(LB, (-0.25, -0.25, -3.0), (5, 6, 6), "steel", inflate=0.25, side=1)
    sym(RB, LB, (-5.0, -0.5, -4.4), (5, 3, 3), "stone")                           # stone toe cap
    sym(RB, LB, (-5.05, -0.6, -3.5), (5, 1, 7), "stone", inflate=0.05, sole=True)  # sole
    sym(RB, LB, (-5.1, 5.4, -3.5), (5, 2, 7), "stone", inflate=0.1)               # boot cuff
    sym(RB, LB, (-3.5, 2.0, -3.75), (2, 3, 1), "crystal")                         # shin crystal
    sym(RB, LB, (-4.0, 0.5, 2.9), (3, 2, 1), "steel", rivets=True)                # heel plate
    build_stage_parts(m)
    return m


# =============================================================================== stage parts
# Evolving armor: bones named "stage2_*" are shown when the piece is stage 2 or 3, "stage3_*" only at
# stage 3 (the renderer toggles them by that prefix). They are created after every base bone, so base
# cubes keep their cube index (texel hashes), and StagedPainter keeps them out of the base AO: with the
# stage bones hidden every piece renders exactly as it did before.

STAGE_PREFIXES = ("stage2_", "stage3_")


def stage_level(name):
    return 3 if name.startswith("stage3_") else 2 if name.startswith("stage2_") else 1


def stage_bone(m, name, parent, pivot):
    assert name.startswith(STAGE_PREFIXES), name
    return m.bone(name, parent, [round(float(x), 4) for x in pivot])


def stage_pair(m, name, limb, pivot_r):
    """Mirrored stage bones <name>R / <name>L under armorRight<limb> / armorLeft<limb>."""
    x, y, z = pivot_r
    return (stage_bone(m, name + "R", "armorRight" + limb, (x, y, z)),
            stage_bone(m, name + "L", "armorLeft" + limb, (-x, y, z)))


class StagedPainter(al.Painter):
    """AO that follows stage visibility: a cube only receives occlusion from cubes that are visible
    whenever it is (base <- base, stage 2 <- base + stage 2, stage 3 <- everything)."""

    def _ao(self, pw, nw, cm, face, ci, boxes):
        lvl = stage_level(boxes[ci][0].bone.name)
        far = (np.full(3, 1e9), np.full(3, -1e9))       # empty bounds: skipped by the AO loop
        boxes = [b if b[0] is None or stage_level(b[0].bone.name) <= lvl else b[:5] + far for b in boxes]
        return super()._ao(pw, nw, cm, face, ci, boxes)


def check_stage_bones(m):
    names = list(m.bones)
    first = next((i for i, n in enumerate(names) if stage_level(n) > 1), len(names))
    assert all(stage_level(n) > 1 for n in names[first:]), "stage bones must come after every base bone"
    for b in m.bones.values():
        if b.parent and stage_level(b.parent) > 1:
            assert stage_level(b.name) == stage_level(b.parent), f"{b.name} needs its parent's stage prefix"


def paint_staged(m, shaders, ao=0.85):
    check_stage_bones(m)
    return StagedPainter(m, shaders, ao_strength=ao, occluders=ak.BODY_BOXES).paint()


def tipped_spike(bone, base, d, L, w, tip_len=2, mat="steel", **params):
    """Steel spike with a glowing crystal tip continuing along the same axis."""
    d = al.unit(d)
    base = np.asarray(base, dtype=float)
    bone.spike(base, d, L, w, mat, segs=[1.0], **params)
    bone.spike(base + d * (L - 0.6), d, tip_len, max(1, w - 1), "crystal", segs=[1.0], **params)


def build_stage_parts(m):
    # ------------------------------------------------------------------ helmet
    # stage 2: crystal-tipped steel bull horns sweeping out of the brow corners, stone root collars
    for side in (-1, 1):
        s = "R" if side < 0 else "L"
        base = np.array([5.3 * side, 30.3, -2.4])
        hb = stage_bone(m, f"stage2_horn{s}", "armorHead", base)
        boxc(hb, base.tolist(), (2, 3, 3), "stone", side=side)                           # root collar
        d1, d2 = al.unit([side, 0.24, -0.2]), al.unit([0.5 * side, 1.0, -0.1])
        hb.curve_spike(base, [d1, d2], [4, 4], [3, 2], "steel", side=side, panel=False)
        tip = base + d1 * 3.3 + d2 * 3.3
        hb.spike(tip, (0.12 * side, 1.0, 0.3), 3, 2, "crystal", segs=[0.67, 0.5], side=side)

    # stage 3: carved crown - riveted steel band with gem studs and stone tines
    cr = stage_bone(m, "stage3_crown", "armorHead", (0, 31.5, 0))
    cube(cr, (-5.6, 31.5, -5.6), (11, 2, 1), "steel", panel=False, rivets=True)          # front band
    cube(cr, (-5.6, 31.5, 4.6), (11, 2, 1), "steel", panel=False, rivets=True)           # back band
    sym(cr, cr, (-5.6, 31.5, -4.6), (1, 2, 9), "steel", panel=False)                     # side bands
    for x in (-3.4, 0.0, 3.4):
        boxc(cr, (x, 32.5, -5.8), (1, 1, 1), "gem", inflate=0.12)                         # gem studs
    for (x, z, ax) in ((-3.0, -5.1, "x"), (3.0, -5.1, "x"), (-3.2, 5.1, "x"), (0.0, 5.1, "x"), (3.2, 5.1, "x"),
                       (-5.1, -2.2, "z"), (5.1, -2.2, "z")):
        for k, w in enumerate((3, 2, 1)):                                                # pixel-triangle tines
            sx, sz = (w, 1) if ax == "x" else (1, w)
            cr.boxb(x, 33.4 + k, z, sx, 1, sz, "stone")
    for x, z in ((-5.1, -5.1), (5.1, -5.1), (-5.1, 5.1), (5.1, 5.1)):
        cr.boxb(x, 33.4, z, 1, 3, 1, "steel", panel=False)                               # corner posts
        boxc(cr, (x, 37.0, z), (1, 1, 1), "gem", inflate=0.15)                           # crown jewels

    # ------------------------------------------------------------------ chestplate
    # stage 2: larger pauldrons - outer stone shield plate with its own rune, wider second lame, ridge
    pr, pl = stage_pair(m, "stage2_pauldron", "Arm", (-7.4, 24.8, 0))
    sym(pr, pl, (-11.6, 19.0, -5.0), (1, 7, 10), "stone", rune="pauldron", rot=[0, 0, 8], pivot=[-11.1, 26.0, 0])
    sym(pr, pl, (-11.2, 17.4, -4.6), (6, 2, 9), "steel", rot=[0, 0, 18], pivot=[-8.0, 19.4, 0], rivets=True)
    sym(pr, pl, (-11.4, 25.4, -4.0), (2, 1, 8), "steel", panel=False)                    # top ridge

    # stage 3: elemental core crystal on chest and back
    cf = stage_bone(m, "stage3_coreFront", "armorBody", (0, 20.2, -4.0))
    cube(cf, (-2.5, 17.7, -5.4), (5, 5, 1), "stone", rot=[0, 0, 45], pivot=[0, 20.2, -4.9])   # diamond setting
    boxc(cf, (0, 20.2, -6.0), (3, 3, 2), "gem", rot=[0, 0, 45])                               # the core
    for side in (-1, 1):
        cf.spike((2.4 * side, 20.2, -5.0), (side, 0.12, -0.3), 3, 2, "crystal", segs=[0.67, 0.5])
    cb = stage_bone(m, "stage3_coreBack", "armorBody", (0, 19.3, 5.3))
    cube(cb, (-2.5, 16.8, 5.3), (5, 5, 1), "stone", rot=[0, 0, 45], pivot=[0, 19.3, 5.8])
    boxc(cb, (0, 19.3, 6.9), (3, 3, 2), "gem", rot=[0, 0, 45])
    for side in (-1, 1):
        cb.spike((2.2 * side, 17.4, 5.8), (0.8 * side, -0.7, 0.45), 3, 2, "crystal", segs=[0.67, 0.5])

    # stage 3: gauntlet spikes along the outer stone cuff
    gr, gl = stage_pair(m, "stage3_gauntlet", "Arm", (-10.1, 17.0, 0))
    for z, dz in ((-2.0, -0.3), (0.2, 0.0), (2.4, 0.3)):
        for b, sd in ((gr, -1), (gl, 1)):
            tipped_spike(b, (10.0 * sd, 17.0, z), (sd, 0.35, dz), 3, 2, side=sd)

    # ------------------------------------------------------------------ leggings
    # stage 2: stone knee guards with a crystal and riveted side discs
    kr, kl = stage_pair(m, "stage2_knee", "Leg", (-2.3, 5.8, -3.4))
    sym(kr, kl, (-4.6, 4.2, -4.6), (5, 4, 1), "stone")                                   # poleyn
    sym(kr, kl, (-3.3, 5.2, -5.3), (2, 2, 1), "gem")                                     # knee gem
    sym(kr, kl, (-5.6, 4.4, -2.4), (1, 3, 3), "steel", rivets=True, panel=False)         # side disc
    # stage 3: crystal knee spikes and crystal slabs set into the front tassets
    sr3, sl3 = stage_pair(m, "stage3_legCrystals", "Leg", (-2.3, 6.4, -4.6))
    sym_spike(sr3, sl3, (-2.3, 6.4, -4.4), (0, 0.55, -1.0), 4, 2, "crystal", segs=[0.62, 0.45])
    sym(sr3, sl3, (-3.4, 7.4, -4.25), (2, 3, 1), "crystal", rot=[-7, 0, 0], pivot=[-2.4, 10.4, -3.1])

    # ------------------------------------------------------------------ boots
    # stage 2: crystal-rowel heel spurs and stone outer ankle guards
    br, bl = stage_pair(m, "stage2_spur", "Boot", (-2.4, 1.9, 3.3))
    sym(br, bl, (-2.9, 1.4, 3.3), (1, 1, 2), "steel")                                    # spur neck
    sym_boxc(br, bl, (-2.4, 1.9, 6.0), (1, 2, 2), "crystal", rot=[45, 0, 0], inflate=0.1)  # rowel
    sym(br, bl, (-5.6, 1.4, -1.6), (1, 3, 4), "stone")                                   # ankle guard
    # stage 3: crystal fins growing back out of the ankle guards
    ar3, al3 = stage_pair(m, "stage3_ankleCrystals", "Boot", (-5.6, 3.4, 1.4))
    sym_spike(ar3, al3, (-5.4, 3.0, 1.2), (-0.5, 0.4, 1.0), 4, 2, "crystal", segs=[0.62, 0.45])


# =============================================================================== themes

THEMES = {
    "": dict(
        steel=M.pal("#121519", "#191d23", "#21262e", "#2a3039", "#343b46", "#3f4754", "#4b5564", "#5a6577",
                    "#6c788b", "#8592a5", "#a6b2c3"),
        stone=M.pal("#3b342b", "#4b4337", "#5c5244", "#6e6352", "#817461", "#948670", "#a7997f", "#b9ab90",
                    "#cbbfa5", "#ddd3bc"),
        crys=M.pal("#0d4d6b", "#12698e", "#1886b0", "#22a4cc", "#3cc3e6", "#6ad9f4", "#9fecfb", "#d3f9ff",
                   "#ffffff"),
        eye=(160, 245, 255), slit=(8, 10, 14)),
    "_frost": dict(
        steel=M.pal("#11161f", "#171e29", "#1e2734", "#263141", "#2f3c4f", "#3a4960", "#475872", "#566a86",
                    "#6a7f9c", "#8399b6", "#a6bdd6"),
        stone=M.pal("#28303b", "#323c49", "#3d4858", "#495668", "#566578", "#647489", "#74859a", "#8698ad",
                    "#9eb0c4", "#bccbdc"),
        crys=M.pal("#0f3f9a", "#1557c0", "#1f74df", "#3394f2", "#55b4fb", "#84d0ff", "#b5e6ff", "#e2f6ff",
                   "#ffffff"),
        rime=M.pal("#8fb3d9", "#b2d0ee", "#d3e8fb", "#f0f9ff"),
        eye=(170, 225, 255), slit=(6, 10, 20)),
    "_tide": dict(
        steel=M.pal("#08131d", "#0c1a27", "#102233", "#152c41", "#1b3750", "#224461", "#2b5373", "#356386",
                    "#42759a", "#558bb0", "#72a6c9"),
        stone=M.pal("#10292a", "#163735", "#1c4542", "#245550", "#2e665e", "#3a776c", "#4a897b", "#5e9b8c",
                    "#77ad9f", "#96c3b6"),
        crys=M.pal("#064a4f", "#0a6469", "#108084", "#1a9d9c", "#2fbab3", "#52d4c6", "#85e9d8", "#bdf7ea",
                   "#f2fffb"),
        coral=M.pal("#6e1a2a", "#a02b38", "#d4454c", "#f86e62", "#ff9d80", "#ffcbb0"),
        eye=(120, 255, 230), slit=(4, 12, 16)),
    "_storm": dict(
        steel=M.pal("#111317", "#181b21", "#20242c", "#292e38", "#333945", "#3e4553", "#4a5262", "#586173",
                    "#697387", "#7f8a9e", "#9aa5b8"),
        stone=M.pal("#3a1a0f", "#532617", "#6d3321", "#88422c", "#a25239", "#b96446", "#cc7955", "#dd9168",
                    "#ebad80", "#f6cb9f"),
        patina=M.pal("#2f5f50", "#3e7a66", "#58a084", "#7cc0a2"),
        crys=M.pal("#6b4a05", "#8f660a", "#b48612", "#d6a61e", "#eec433", "#fbdc5a", "#fff08f", "#fffac8",
                   "#ffffff"),
        eye=(255, 245, 170), slit=(10, 10, 12)),
    "_magma": dict(
        steel=M.pal("#0c0b0d", "#121114", "#18171b", "#1f1d22", "#27242a", "#302c33", "#3a353d", "#464048",
                    "#534c55", "#635b64", "#766d76"),
        stone=M.pal("#1a1513", "#221c19", "#2b2420", "#352c27", "#40352e", "#4c3f36", "#5a4a3f", "#6a574a",
                    "#7c6656", "#8f7764"),
        crys=M.pal("#5a0a02", "#861404", "#b02208", "#d6380c", "#f05a12", "#ff7e1e", "#ffa53a", "#ffd06a",
                   "#fff3b0"),
        lava=M.pal("#a8280a", "#e04a0c", "#ff7a1a", "#ffb43c", "#ffe88a"),
        eye=(255, 170, 60), slit=(12, 6, 4)),
}

RUNES = [
    ["#.#.#", "#.#.#", ".###.", "..#..", "..#..", "..#..", "..#.."],     # algiz
    ["..#..", ".###.", "#.#.#", "..#..", "..#..", "..#..", "..#.."],     # tiwaz
    [".#...", ".##..", ".#.#.", ".#.#.", ".##..", ".#...", ".#..."],     # thurisaz
    ["..#..", ".#.#.", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"],     # othala
]


def rune_mask(ctx, which=0, cx=None, cy=None):
    g = RUNES[which % len(RUNES)]
    gh, gw = len(g), len(g[0])
    cx = ctx.tw // 2 if cx is None else cx
    cy = ctx.th // 2 if cy is None else cy
    x0 = cx - gw // 2
    y0 = cy - gh // 2
    m = np.zeros(ctx.N, dtype=bool)
    for r, row in enumerate(g):
        for c, ch in enumerate(row):
            if ch == "#":
                m |= (ctx.i == x0 + c) & (ctx.j == y0 + r)
    return m


def make_shaders(theme):
    T = THEMES[theme]
    STEEL, STONE, CRYS = T["steel"], T["stone"], T["crys"]

    def frost_rime(ctx, rgb, strength=1.0):
        if "rime" not in T:
            return
        up = max(0.0, ctx.nw[1])
        n = fbm(ctx.p, 0.5, 3, seed=41)
        side = M.side_face(ctx)
        top = (ctx.j < 2) if side else np.zeros(ctx.N, dtype=bool)
        top1 = (ctx.j < 1) if side else np.zeros(ctx.N, dtype=bool)
        r = (n * 0.6 + up * 0.5 + top * 0.2 + top1 * 0.2 - ctx.ao * 0.4) > (0.76 - 0.04 * strength)
        if side:
            # icicle drips hanging from the frosted top edge
            col = np.floor(ctx.p[:, 0] * 2 + ctx.p[:, 2] * 2 + 0.01)
            ln = np.floor(hash3(col, ctx.index, 0, 5) * 3)
            drip = (ctx.j < 1 + ln) & (hash3(col, ctx.index, 1, 6) > 0.7) & (n > 0.5)
            r |= drip
        rv = 0.55 + (fbm(ctx.p, 1.3, 2, 9) - 0.5) * 0.7 + M.bevel(ctx, 0.3, 0.1) - (ctx.j * 0.06 if side else 0)
        rgb[r] = M.ramp(T["rime"], rv[r])
        sp = (M.texel_hash(ctx, 91) > 0.985) & ~r
        rgb[sp] = T["rime"][2]

    def lava_cracks(ctx, rgb, glow, density=0.5, thr=0.06):
        if "lava" not in T:
            return
        f1, f2, _ = worley(ctx.p, 0.2, seed=17)
        gate = fbm(ctx.p, 0.16, 2, seed=5) > density
        d = f2 - f1
        crack = (d < thr) & gate
        core = (d < thr * 0.4) & gate
        halo = (d < thr * 2.4) & gate & ~crack
        rgb[halo] = rgb[halo] * 0.5 + np.array([140, 34, 8]) * 0.5
        rgb[crack] = T["lava"][1]
        rgb[core] = T["lava"][3]
        glow |= crack

    def storm_etch(ctx, rgb, glow):
        return

    def tide_barnacles(ctx, rgb):
        if theme != "_tide":
            return
        f1, f2, cid = worley(ctx.p, 0.9, seed=71)
        b = (f1 < 0.2) & (fbm(ctx.p, 0.25, 2, seed=3) > 0.64) & (cid > 0.4)
        rgb[b] = T["stone"][8]
        rgb[b & (f1 < 0.09)] = T["stone"][2]

    # -------------------------------------------------------------------------------- steel
    def steel(ctx):
        prm = ctx.params
        extra = np.zeros(ctx.N)
        y = ctx.p[:, 1]
        seams = prm.get("seams")
        if seams and M.side_face(ctx):
            for sy in seams:
                extra -= np.where(np.abs(y - sy) < 0.26, 0.26, 0)
                extra += np.where((y < sy - 0.26) & (y > sy - 0.76), 0.08, 0)
        if prm.get("lames") and M.side_face(ctx):
            band = ((ctx.th - 1 - ctx.j) % 4 == 0) & (ctx.j > 0)
            extra -= np.where(band, 0.16, 0)
        if prm.get("panel", True):
            extra += M.panel(ctx, inset=2, min_size=12)
        v, rgb = M.metal(ctx, STEEL, base=0.56, extra=extra)
        if prm.get("rivets"):
            hi, lo = M.rivets(ctx, inset=1, min_size=6)
            rgb[hi] = STEEL[-1]
            rgb[lo] = STEEL[2]
        glow = np.zeros(ctx.N, dtype=bool)
        plate = prm.get("plate")
        dl, dr, dt, db = M.edist(ctx)
        if plate == "breast" and ctx.face == "north":
            # chiselled pectoral ridges converging to the heart crystal
            x, yy = ctx.p[:, 0], ctx.p[:, 1]
            ridge = np.abs(np.abs(x) - (1.5 + (yy - 16.6) * 0.55)) < 0.28
            rgb[ridge & (yy > 17.2)] = STEEL[8]
            shadow = np.abs(np.abs(x) - (1.5 + (yy - 16.6) * 0.55) - 0.5) < 0.26
            rgb[shadow & (yy > 17.2)] = STEEL[2]
            # inlaid crystal veins
            vein = (np.abs(np.abs(x) - 3.6) < 0.26) & (yy > 18.0) & (yy < 22.6)
            rgb[vein] = CRYS[5]
            glow |= vein
        if plate == "back" and ctx.face == "south":
            x, yy = ctx.p[:, 0], ctx.p[:, 1]
            spine = (np.abs(x) < 0.26) & (yy < 17.6)
            rgb[spine] = CRYS[4]
            glow |= spine
        if plate == "tasset" and M.side_face(ctx):
            line = (db == 2) & (dl > 0) & (dr > 0)
            rgb[line] = STEEL[2]
        frost_rime(ctx, rgb)
        lava_cracks(ctx, rgb, glow, density=0.6)
        storm_etch(ctx, rgb, glow)
        return rgb, 255, glow

    def faceplate(ctx):
        v, rgb = M.metal(ctx, STEEL, base=0.52)
        glow = np.zeros(ctx.N, dtype=bool)
        if ctx.face == "north":
            grill = (ctx.i % 3 == 1) & (ctx.j > 1) & (ctx.j < ctx.th - 2) & (ctx.i > 1) & (ctx.i < ctx.tw - 2)
            rgb[grill] = T["slit"]
            rgb[grill & (ctx.j == 2)] = STEEL[1]
        frost_rime(ctx, rgb, 0.6)
        lava_cracks(ctx, rgb, glow, 0.62)
        return rgb, 255, glow

    def helm(ctx):
        v, rgb = M.metal(ctx, STEEL, base=0.56, extra=M.vgrad(ctx, 0.1) + M.panel(ctx, 2, 16))
        glow = np.zeros(ctx.N, dtype=bool)
        x, y, z = ctx.p[:, 0], ctx.p[:, 1], ctx.p[:, 2]
        if ctx.face == "north":
            slit = (y > 27.3) & (y < 29.5) & (np.abs(x) < 4.6)
            rgb[slit] = T["slit"]
            inner = slit & (y > 27.6) & (y < 29.2)
            rgb[inner] = np.array(T["slit"]) * 1.6 + 6
            eye = (np.abs(y - 28.25) < 0.3) & (np.abs(np.abs(x) - 2.4) < 1.1)
            rgb[eye] = T["eye"]
            glow |= eye
            core = eye & (np.abs(np.abs(x) - 2.4) < 0.4)
            rgb[core] = (255, 255, 255)
        if ctx.face == "up":
            # radial chisel grooves on the dome
            ang = np.arctan2(z, x)
            groove = (np.abs(np.sin(ang * 4)) < 0.12) & (np.hypot(x, z) > 2.5)
            rgb[groove] = STEEL[2]
        if M.side_face(ctx) and ctx.face != "north":
            band = np.abs(y - 29.0) < 0.26
            rgb[band] = STEEL[2]
            rgb[np.abs(y - 28.5) < 0.24] = STEEL[7]
        frost_rime(ctx, rgb)
        lava_cracks(ctx, rgb, glow, 0.6)
        storm_etch(ctx, rgb, glow)
        return rgb, 255, glow

    # -------------------------------------------------------------------------------- stone
    def stone(ctx):
        prm = ctx.params
        glow = np.zeros(ctx.N, dtype=bool)
        if theme == "_storm":
            # copper plate instead of stone
            v, rgb = M.metal(ctx, STONE, base=0.55, sheen_amt=0.18, noise=0.04)
            f = fbm(ctx.p, 0.35, 3, seed=12) + (1 - ctx.t) * 0.0
            pat = (f > 0.64) | ((ctx.ao > 0.25) & (f > 0.5))
            pv = 0.5 + (fbm(ctx.p, 1.0, 2, 4) - 0.5) * 0.8
            rgb[pat] = M.ramp(T["patina"], pv[pat])
            hi, lo = M.rivets(ctx, inset=1, min_size=8)
            rgb[hi] = STONE[-1]
            rgb[lo] = STONE[2]
        else:
            v, rgb = M.stone(ctx, STONE, base=0.62)
        rune = prm.get("rune")
        if rune and M.side_face(ctx) and ctx.tw >= 6 and ctx.th >= 6:
            side = ctx.params.get("side", 0)
            outer = "west" if side < 0 else "east"
            want = {"pauldron": (outer,), "core": (), "nape": ("south",), "belt": (), "legbelt": ()}.get(rune, ())
            if ctx.face in want:
                which = int(hash3(ctx.index, 1, 2, 3)[0] * 4)
                rm = rune_mask(ctx, which)
                rgb[rm] = CRYS[6]
                glow |= rm
                # carved groove around the rune
                halo = np.zeros(ctx.N, dtype=bool)
        if prm.get("sole"):
            rgb = rgb * 0.75
        if theme == "_tide":
            # coral growths on stone
            f1, f2, cid = worley(ctx.p, 0.3, seed=29)
            gate = fbm(ctx.p, 0.2, 2, seed=11) > 0.5
            branch = worley(ctx.p, 1.1, seed=30)
            cor = (f1 < 0.5) & gate & ((branch[1] - branch[0]) > 0.1)
            cv = 1.02 - f1 * 1.0 + (M.texel_hash(ctx, 5) - 0.5) * 0.12
            rgb[cor] = M.ramp(T["coral"], cv[cor])
            polyp = cor & (M.texel_hash(ctx, 12) > 0.86)
            rgb[polyp] = T["coral"][-1]
            tide_barnacles(ctx, rgb)
        frost_rime(ctx, rgb, 1.2)
        lava_cracks(ctx, rgb, glow, density=0.46, thr=0.065)
        return rgb, 255, glow

    def crystal(ctx):
        return M.crystal(ctx, CRYS)

    def gem(ctx):
        return M.gem(ctx, CRYS, shape="diamond")

    return {"steel": steel, "helm": helm, "faceplate": faceplate, "stone": stone, "crystal": crystal,
            "gem": gem}


# =============================================================================== animation

def build_clips():
    c = Clip("idle", 3.0, loop=True)
    T = 3.0
    w = 2 * math.pi / T

    def pulse(amp, ph):
        return lambda t: [1 + amp * math.sin(w * t + ph)] * 3

    c.f("backCrystals", "scale", pulse(0.06, 0.0))
    c.f("helmCrystal", "scale", pulse(0.07, 1.2))
    c.f("helmHornR", "scale", pulse(0.05, 2.0))
    c.f("helmHornL", "scale", pulse(0.05, 2.0))
    c.f("pauldronCrystalsR", "scale", pulse(0.06, 0.6))
    c.f("pauldronCrystalsL", "scale", pulse(0.06, 3.6))
    c.f("pauldronCrystalsR", "position", lambda t: [0, 0.25 + 0.25 * math.sin(w * t + 0.6), 0])
    c.f("pauldronCrystalsL", "position", lambda t: [0, 0.25 + 0.25 * math.sin(w * t + 3.6), 0])
    c.f("stage3_coreFront", "scale", pulse(0.05, 0.3))                  # elemental cores breathe
    c.f("stage3_coreBack", "scale", pulse(0.05, 0.3))
    return [c]


# =============================================================================== build

def build(preview=False):
    m = build_model()
    W, H = m.pack()
    paths = al.asset_paths(NAME)
    geo = ak.export_geo(m, paths["geo"])
    print(f"{NAME}: {m.cube_count()} cubes, uv {W}x{H}, png {W * 2}x{H * 2}")
    anims = al.export_anims(build_clips(), paths["anim"])
    out = {}
    for theme in THEMES:
        rgba, glow = paint_staged(m, make_shaders(theme))
        ak.save_textures(NAME, theme, rgba, glow)
        out[theme] = (rgba, glow)
    if preview:
        g = gp_geo(geo)
        os.makedirs(ak.PREVIEW, exist_ok=True)
        for theme, (rgba, glow) in out.items():
            tag = theme or "_neutral"
            ak.sheet_views(f"titan armor{theme}", g, rgba, glow).save(os.path.join(ak.PREVIEW, f"titan{tag}_views.png"))
        rgba, glow = out[""]
        ak.sheet_details("titan armor details", g, rgba, glow).save(os.path.join(ak.PREVIEW, "titan_details.png"))
        ak.texture_sheet(rgba, glow).save(os.path.join(ak.PREVIEW, "titan_texture.png"))
        ak.lineup([(f"titan{th or ' neutral'}", g, rg, gl) for th, (rg, gl) in out.items()],
                  os.path.join(ak.PREVIEW, "titan_variants.png"))
        import stage_preview
        stage_preview.stage_sheet("titan")
        stage_preview.variant_sheet("titan")
    return m, geo, out, anims


def gp_geo(geo):
    import geo_preview as gp
    return gp.load_geo(geo)


if __name__ == "__main__":
    build(preview="--preview" in sys.argv)
