"""Imperial armor: purpur-violet and gold Ender Empire plate, crested helm, violet energy cape,
ender-eye gems.

Run: python imperial_armor.py [--preview]
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

NAME = "imperial_armor"

PURPUR = M.pal("#1f0f2a", "#2c1539", "#3a1c4a", "#4a245d", "#5b2d71", "#6d3785", "#804399", "#9452ab",
               "#a865bb", "#bb7cca", "#cd98d8", "#dfb8e6")
GOLD = M.pal("#3a1f04", "#5a3307", "#7c4a0c", "#9e6312", "#bf7d1a", "#db9a24", "#efb733", "#fad04e",
             "#ffe486", "#fff3c0")
DARK = M.pal("#0b0610", "#130b1b", "#1c1126", "#261833", "#311f40")
EYE = M.pal("#0a3328", "#11503c", "#1a7254", "#26946c", "#3ab685", "#5fd4a0", "#98ecc4", "#d6fff0")
CAPE = M.pal("#14072a", "#1f0b3c", "#2c1052", "#3b166a", "#4c1d84", "#5f259e", "#7430b8", "#8b40cf",
             "#a45ae2", "#bf7ff0", "#dcaafb", "#f3dcff")
LINING = M.pal("#0e0618", "#160a24", "#200f31", "#2b1540", "#371b50")
ECORE = M.pal("#5a1678", "#7f1f9e", "#a62cc0", "#c94adb", "#e478ee", "#f6aefa", "#ffe0ff")


# =============================================================================== geometry

def build_model():
    m = ak.new_model(NAME)
    H, B = m["armorHead"], m["armorBody"]
    RA, LA = m["armorRightArm"], m["armorLeftArm"]
    RL, LL = m["armorRightLeg"], m["armorLeftLeg"]
    RB, LB = m["armorRightBoot"], m["armorLeftBoot"]

    # ------------------------------------------------------------------ helmet
    cube(H, (-5, 23, -5), (10, 10, 10), "helm")                                  # crested helm shell
    cube(H, (-5.5, 29.2, -5.5), (11, 2, 11), "gold", band=True)                  # gold circlet
    cube(H, (-2, 28.7, -6.0), (4, 3, 1), "gold")                                 # brow setting
    cube(H, (-1, 29.2, -6.5), (2, 2, 1), "eye")                                  # brow ender eye
    sym(H, H, (-6.0, 23.0, -5.6), (1, 6, 6), "purpur", trim=("bottom", "left", "right"))  # cheek guards
    cube(H, (-2, 22.6, -5.8), (4, 1, 1), "gold")                                 # chin bar
    cube(H, (-5, 22.4, 4.5), (10, 3, 1), "purpur", trim=("bottom",), lames=True)  # neck guard
    cube(H, (-1, 32.6, -5.4), (2, 1, 11), "gold")                                # crest base
    crest = m.bone("crest", "armorHead", (0, 33.6, 0))
    cube(crest, (-1, 33.4, -4.6), (2, 2, 10), "plume", tier=0)
    cube(crest, (-1, 35.2, -2.2), (2, 2, 8), "plume", tier=1)
    cube(crest, (-1, 37.0, 1.4), (2, 1, 5), "plume", tier=2)
    cube(H, (-3, 32.8, -5.3), (6, 4, 1), "crown")                                # ender crown fan
    cube(H, (-1, 34.0, -5.75), (2, 2, 1), "eye")

    # ------------------------------------------------------------------ chestplate body
    cube(B, (-4.5, 11.5, -3), (9, 13, 6), "purpur", tiles=True)                  # cuirass shell
    cube(B, (-5, 16.8, -4), (10, 7, 2), "purpur", trim=("top", "bottom", "left", "right"), plate="breast")
    cube(B, (-2.5, 17.7, -4.7), (5, 5, 1), "gold", rot=[0, 0, 45], pivot=[0, 20.2, -4.2])   # diamond setting
    cube(B, (-1.5, 18.7, -5.25), (3, 3, 1), "eye")                               # heart ender eye
    cube(B, (-4.5, 15.0, -3.5), (9, 2, 1), "purpur", trim=("bottom",))           # abdominal lame
    cube(B, (-4.0, 13.2, -3.4), (8, 2, 1), "purpur", trim=("bottom",))
    cube(B, (-5, 12.2, -3.6), (10, 1, 7), "gold", band=True)                     # gold sash belt
    cube(B, (-1.5, 11.6, -4.0), (3, 2, 1), "gold")                               # belt plaque
    cube(B, (-4.5, 15.5, 2.6), (9, 8, 1), "purpur", trim=("left", "right"))      # back plate
    cube(B, (-4.5, 23.4, 2.4), (9, 3, 1), "purpur", trim=("top",))               # high back collar
    sym(B, B, (-4.9, 22.2, 3.3), (2, 2, 2), "gold")                              # cape clasps
    sym(B, B, (-4.4, 22.7, 5.1), (1, 1, 1), "eye")
    cape = m.bone("cape", "armorBody", (0, 24.0, 4.4), rotation=[7, 0, 0])
    cube(cape, (-5, 13.0, 4.35), (10, 11, 1), "cape", part=0)
    capel = m.bone("capeLower", "cape", (0, 13.0, 4.85), rotation=[3, 0, 0])
    cube(capel, (-5.5, 3.0, 4.35), (11, 10, 1), "cape", part=1)

    # ------------------------------------------------------------------ arms
    sym(RA, LA, (-8.5, 12, -2.5), (4, 12, 5), "purpur", inflate=0.25, seams=[18.0])
    sym(RA, LA, (-10.2, 22.0, -4.0), (6, 3, 8), "purpur", trim=("bottom",), plate="pauldron")  # pauldron dome
    sym(RA, LA, (-10.4, 21.0, -4.25), (6, 1, 9), "gold", band=True)              # gold rim
    sym(RA, LA, (-10.6, 19.2, -4.0), (6, 2, 8), "purpur", rot=[0, 0, 12], pivot=[-7.6, 21.2, 0], trim=("bottom",))
    sym(RA, LA, (-10.6, 22.6, -1.0), (1, 2, 2), "eye")                           # pauldron eye
    sym(RA, LA, (-9.25, 11.1, -3), (5, 6, 6), "purpur", inflate=0.15, trim=("top", "bottom"))  # vambrace
    sym(RA, LA, (-9.6, 16.4, -3.5), (5, 1, 7), "gold", band=True, inflate=0.05)  # cuff
    sym(RA, LA, (-10.0, 12.6, -1.0), (1, 2, 2), "eye")                           # vambrace eye
    sym(RA, LA, (-9.4, 18.0, -1.0), (1, 2, 2), "gold")                           # couter

    # ------------------------------------------------------------------ leggings
    cube(RL, (-4.025, 0, -2.5), (4, 12, 5), "purpur", inflate=0.375, seams=[5.0], side=-1)
    cube(LL, (-0.025, 0, -2.5), (4, 12, 5), "purpur", inflate=0.425, seams=[5.0], side=1)
    sym(RL, LL, (-5.0, 10.4, -3.5), (5, 2, 7), "gold", band=True)                # belt half
    sym(RL, LL, (-1.4, 10.6, -3.9), (2, 2, 1), "gold")                           # belt buckle half
    sym(RL, LL, (-4.4, 5.4, -3.6), (4, 5, 1), "purpur", rot=[-8, 0, 0], pivot=[-2.4, 10.4, -3.1],
        trim=("bottom",), plate="tasset")
    sym(RL, LL, (-5.4, 5.0, -2.5), (1, 5, 5), "purpur", rot=[0, 0, 8], pivot=[-4.9, 10.4, 0],
        trim=("bottom",), plate="tasset")
    sym(RL, LL, (-4.3, 3.8, -3.4), (4, 3, 1), "gold")                            # knee cop
    sym(RL, LL, (-3.4, 4.3, -3.9), (2, 2, 1), "eye")

    # ------------------------------------------------------------------ boots
    cube(RB, (-4.75, -0.25, -3.0), (5, 6, 6), "purpur", inflate=0.2, side=-1, trim=("top",))
    cube(LB, (-0.25, -0.25, -3.0), (5, 6, 6), "purpur", inflate=0.25, side=1, trim=("top",))
    sym(RB, LB, (-5.0, -0.55, -4.6), (5, 2, 3), "gold")                          # gold sabaton toe
    sym(RB, LB, (-4.6, 1.2, -4.1), (4, 1, 2), "purpur", trim=("top",))           # instep plate
    sym(RB, LB, (-5.05, -0.6, -3.5), (5, 1, 7), "dark", inflate=0.05)            # sole
    sym(RB, LB, (-5.1, 5.2, -3.5), (5, 1, 7), "gold", band=True, inflate=0.1)    # cuff
    sym(RB, LB, (-3.5, 2.2, -3.75), (2, 3, 1), "gold")                           # shin guard
    sym(RB, LB, (-3.0, 2.7, -4.15), (1, 2, 1), "eye")
    for k, (y, L, rx) in enumerate(((4.2, 4, 30), (3.3, 3, 44))):
        sym(RB, LB, (-5.6, y, -0.5), (1, 1, L), "gold", rot=[rx, -18, 0], pivot=[-5.1, y + 0.5, 0])  # heel wings
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


def sym_rows(br, bl, x0, rows, mats, width=1, rot=None, pivot=None, **params):
    """Mirrored pixel-stepped fin in the YZ plane: rows = [(y, z0, z1), ...] of 1 px tall bars spanning
    x0..x0+width on the right bone (mirrored onto the left one). mats: one per row, or a single name."""
    for k, (y, z0, z1) in enumerate(rows):
        mat = mats[k] if isinstance(mats, (list, tuple)) else mats
        sym(br, bl, (x0, y, z0), (width, 1, z1 - z0), mat, rot=rot, pivot=pivot, **params)


def ender_crystal(bone, center, core=2, cage=3, **params):
    """Small End crystal standing on a corner: glowing core inside a glass cage (edges only)."""
    R = al.axis_angle([0, 0, 1], 54.7356) @ al.axis_angle([0, 1, 0], 45)
    e = al.euler(R)
    boxc(bone, center, (core, core, core), "ecore", rot=e, **params)
    boxc(bone, center, (cage, cage, cage), "ecage", rot=e, **params)


def build_stage_parts(m):
    # ------------------------------------------------------------------ helmet
    # stage 2: fanned violet energy wing-fins at the temples + a short trailing plume behind the crest
    fr, fl = stage_bone(m, "stage2_helmFinR", "armorHead", (-5.9, 28.6, 0.4)),         stage_bone(m, "stage2_helmFinL", "armorHead", (5.9, 28.6, 0.4))
    for (y, L, rx, h) in ((28.6, 7, 10, 1), (29.3, 7, 28, 1), (30.0, 6, 48, 1)):
        sym(fr, fl, (-6.5, y - h / 2, 0.0), (1, h, L), "plume", rot=[rx, -16, 0], pivot=[-6.0, y, 0.4], tier=1,
            y0=y - 4.0)
    sym(fr, fl, (-6.6, 27.6, -0.6), (1, 2, 2), "gold")                                     # wing root boss
    tail = stage_bone(m, "stage2_plumeTail", "armorHead", (0, 35.4, 5.4))
    cube(tail, (-1, 34.4, 5.0), (2, 2, 3), "plume", rot=[-30, 0, 0], pivot=[0, 35.4, 5.0], tier=1, y0=31.0)
    cube(tail, (-1, 32.9, 7.0), (2, 1, 3), "plume", rot=[-52, 0, 0], pivot=[0, 33.4, 7.0], tier=2, y0=29.5)

    # stage 3: the crown closes - crown fans with ender eyes on both temples
    cr = stage_bone(m, "stage3_crown", "armorHead", (0, 32.8, 0))
    for side in (-1, 1):
        cube(cr, (5.3 * side - 3, 32.8, -1.5), (6, 4, 1), "crown", rot=[0, 90, 0], pivot=[5.3 * side, 34.8, -1.0])
        boxc(cr, (5.95 * side, 35.0, -1.0), (1, 2, 2), "eye")

    # ------------------------------------------------------------------ chestplate
    # stage 2: gold-edged purpur fins flaring up and out from the pauldron rims
    sr, sl = stage_pair(m, "stage2_shoulderFin", "Arm", (-10.0, 24.6, 0))
    sym(sr, sl, (-14.0, 24.2, -3.0), (4, 1, 6), "purpur", rot=[0, 0, 24], pivot=[-10.0, 24.6, 0],
        fin=True)
    sym(sr, sl, (-13.0, 25.4, -2.0), (3, 1, 4), "purpur", rot=[0, 0, 48], pivot=[-10.0, 25.6, 0],
        fin=True)
    sym(sr, sl, (-10.8, 23.8, -1.0), (1, 2, 2), "eye")                                    # fin root eye

    # stage 3: floating End crystals over the shoulders (body bone: they hover, the arms swing below)
    for side in (-1, 1):
        s = "R" if side < 0 else "L"
        c = (10.4 * side, 31.6, 0.8)
        ender_crystal(stage_bone(m, f"stage3_enderCrystal{s}", "armorBody", c), c, side=side)
    # stage 3: short rigid purpur mantle over the top of the cape
    mt = stage_bone(m, "stage3_mantle", "armorBody", (0, 24.4, 5.6))
    cube(mt, (-5, 24.4, 5.6), (10, 1, 1), "gold", band=True)                                # yoke
    cube(mt, (-5, 20.4, 5.6), (10, 4, 1), "purpur", rot=[10, 0, 0], pivot=[0, 24.4, 5.6],
         trim=("left", "right", "bottom"), plate="mantle")
    cube(mt, (-1, 21.3, 6.3), (2, 2, 1), "eye", rot=[10, 0, 0], pivot=[0, 24.4, 5.6])

    # ------------------------------------------------------------------ leggings
    # stage 2: violet wing-fins at the outer hips (kept below the hands)
    hr, hl = stage_pair(m, "stage2_hipFin", "Leg", (-5.9, 7.6, -0.4))
    for (y, L, rx) in ((7.6, 5, 12), (7.0, 5, 30), (6.4, 4, 50)):
        sym(hr, hl, (-6.4, y - 0.5, -0.4), (1, 1, L), "plume", rot=[rx, -14, 0], pivot=[-5.9, y, -0.4], tier=1,
            y0=y - 4.0)
    sym(hr, hl, (-6.5, 6.4, -1.4), (1, 2, 2), "gold")
    # stage 3: gold-framed ender eyes set into the front tassets
    er, el = stage_pair(m, "stage3_tassetEye", "Leg", (-2.4, 8.0, -4.2))
    sym(er, el, (-4.4, 5.5, -4.25), (4, 4, 1), "gold", rot=[-8, 0, 45], pivot=[-2.4, 7.5, -3.75])
    sym(er, el, (-3.4, 6.5, -4.75), (2, 2, 1), "eye", rot=[-8, 0, 0], pivot=[-2.4, 7.5, -3.75])

    # ------------------------------------------------------------------ boots
    # stage 2: the heel wings grow two violet energy feathers
    wr, wl = stage_pair(m, "stage2_heelWing", "Boot", (-5.1, 4.0, 0))
    for (y, L, rx) in ((5.0, 5, 16), (2.4, 3, 60)):
        sym(wr, wl, (-5.6, y, -0.5), (1, 1, L), "plume", rot=[rx, -18, 0], pivot=[-5.1, y + 0.5, 0], tier=1, y0=2.0)
    # stage 3: gold sabaton crest with an ender eye along the instep, gold + violet heel blades
    cr3, cl3 = stage_pair(m, "stage3_sabatonCrest", "Boot", (-2.4, 1.2, -3.0))
    sym_rows(cr3, cl3, -2.9, [(1.4, -5.0, -1.0), (2.4, -4.0, -1.0), (3.4, -3.0, -1.0)], "gold")
    sym(cr3, cl3, (-3.1, 1.6, -4.2), (1, 1, 1), "eye", inflate=0.12)
    sym(cr3, cl3, (-2.9, 1.0, 3.0), (1, 1, 4), "gold", rot=[22, 0, 0], pivot=[-2.4, 1.5, 3.0], feather=True)
    sym(cr3, cl3, (-2.9, 0.2, 3.0), (1, 1, 3), "plume", rot=[6, 0, 0], pivot=[-2.4, 0.7, 3.0], tier=1, y0=-2.0)


# =============================================================================== shaders

def make_shaders():
    def purpur(ctx):
        prm = ctx.params
        extra = np.zeros(ctx.N)
        y = ctx.p[:, 1]
        if prm.get("seams") and M.side_face(ctx):
            for sy in prm["seams"]:
                extra -= np.where(np.abs(y - sy) < 0.26, 0.24, 0)
                extra += np.where((y < sy - 0.26) & (y > sy - 0.76), 0.08, 0)
        if prm.get("lames") and M.side_face(ctx):
            extra -= np.where(((ctx.th - 1 - ctx.j) % 3 == 0) & (ctx.j > 0), 0.14, 0)
        if prm.get("tiles") and M.side_face(ctx):
            gxp = np.floor((ctx.p[:, 0] + ctx.p[:, 2]) * 2 + 0.01)
            gyp = np.floor(ctx.p[:, 1] * 2 + 0.01)
            line = ((gxp % 8) == 0) | ((gyp % 8) == 0)
            extra -= np.where(line, 0.08, 0)
        extra += M.panel(ctx, 2, 12, 0.14)
        v, rgb = M.metal(ctx, PURPUR, base=0.56, sheen_amt=0.14, extra=extra)
        glow = np.zeros(ctx.N, dtype=bool)
        trim = prm.get("trim")
        if trim:
            tm = M.trim_band(ctx, 2, trim) & M.side_face(ctx)
            if ctx.face == "up":
                tm |= M.emin(ctx) < 1
            gv, grgb = M.gold(ctx, GOLD, engrave=False)
            rgb[tm] = grgb[tm]
            dl, dr, dt, db = M.edist(ctx)
            inner = M.trim_band(ctx, 3, trim) & ~M.trim_band(ctx, 2, trim) & M.side_face(ctx)
            rgb[inner] = PURPUR[1]
        plate = prm.get("plate")
        x = ctx.p[:, 0]
        if plate == "breast" and ctx.face == "north":
            ax = np.abs(x)
            # gold chevrons converging on the heart eye
            for y0 in (17.6, 18.8):
                chev = (np.abs(y - (y0 + ax * 0.55)) < 0.26) & (ax > 2.2) & (ax < 4.4)
                gv, grgb = M.gold(ctx, GOLD, engrave=False)
                rgb[chev] = grgb[chev]
            # filigree scroll dots
            dots = (np.abs(ax - 3.7) < 0.26) & (np.abs(y - 22.2) < 0.26)
            rgb[dots] = GOLD[7]
            # ender sigil glow lines
            sig = (np.abs(ax - 1.0) < 0.26) & (y > 17.2) & (y < 18.0)
            rgb[sig] = CAPE[9]
            glow |= sig
        if plate == "pauldron" and ctx.face in ("west", "east", "up"):
            pass
        if plate == "tasset" and ctx.face in ("north", "west", "east"):
            mid = (np.abs(ctx.s - 0.5) * ctx.tw < 0.6) & (ctx.j > 2) & (ctx.j < ctx.th - 3)
            rgb[mid] = PURPUR[9]
        if prm.get("fin"):
            # flared shoulder fin: gold outer tip and rim, glowing ender filament along the top
            gv, grgb = M.gold(ctx, GOLD, engrave=False)
            reach = max(abs(ctx.lo[0]), abs(ctx.hi[0]))
            tipm = np.abs(x) > reach - 0.8
            rgb[tipm] = grgb[tipm]
            if ctx.face == "up":
                zc = (ctx.lo[2] + ctx.hi[2]) / 2
                fil = (np.abs(ctx.p[:, 2] - zc) < 0.26) & ~tipm
                rgb[fil] = CAPE[9]
                glow |= fil
                rim = (M.emin(ctx) < 1) & ~fil
                rgb[rim] = grgb[rim]
        if plate == "mantle" and ctx.face == "south":
            # gold chevron pointing down at the cape sigil + glowing ender filament
            ax = np.abs(x)
            chev = (np.abs(y - (20.9 + ax * 0.45)) < 0.26) & (ax > 1.4) & (ax < 4.2)
            gv, grgb = M.gold(ctx, GOLD, engrave=False)
            rgb[chev] = grgb[chev]
            fil = (np.abs(y - (21.7 + ax * 0.45)) < 0.24) & (ax > 1.6) & (ax < 4.0)
            rgb[fil] = CAPE[9]
            glow |= fil
        return rgb, 255, glow

    def gold(ctx):
        prm = ctx.params
        v, rgb = M.gold(ctx, GOLD, engrave=not prm.get("band"))
        if prm.get("band") and M.side_face(ctx):
            # engraved meander on bands
            k = (ctx.i % 6)
            meander = ((k == 0) & (ctx.j > 0) & (ctx.j < ctx.th - 1)) | ((ctx.j == 1) & (k < 3) & (ctx.th > 3))
            rgb[meander & (ctx.th >= 3)] = GOLD[3]
        return rgb, 255, np.zeros(ctx.N, dtype=bool)

    def eye(ctx):
        dx = (ctx.s - 0.5) * 2
        dy = (ctx.t - 0.5) * 2
        r = np.sqrt(dx * dx + dy * dy)
        v = 0.95 - r * 0.6
        rgb = M.ramp(EYE, v, ctx, 0.3)
        glow = np.ones(ctx.N, dtype=bool)
        if ctx.face in ("north", "south", "west", "east"):
            pupil = (np.abs(dx) * ctx.tw < 1.0) & (np.abs(dy) < 0.75)
            rgb[pupil] = (10, 26, 22)
            glow &= ~pupil
            ring = (r > 0.85)
            rgb[ring] = EYE[1]
            if ctx.tw >= 4:
                sp = (ctx.i == 1) & (ctx.j == 1)
                rgb[sp] = (235, 255, 248)
        return rgb, 255, glow

    def helm(ctx):
        x, y, z = ctx.p[:, 0], ctx.p[:, 1], ctx.p[:, 2]
        v, rgb = M.metal(ctx, PURPUR, base=0.56, sheen_amt=0.14, extra=M.panel(ctx, 2, 16, 0.12))
        glow = np.zeros(ctx.N, dtype=bool)
        if ctx.face == "north":
            ax = np.abs(x)
            tslot = ((y > 27.0) & (y < 28.6) & (ax < 4.2)) | ((ax < 1.0) & (y > 23.0) & (y < 28.6))
            frame = ((y > 26.5) & (y < 29.1) & (ax < 4.7)) | ((ax < 1.5) & (y > 23.0) & (y < 29.1))
            gv, grgb = M.gold(ctx, GOLD, engrave=False)
            rgb[frame] = grgb[frame]
            rgb[tslot] = DARK[1]
            rgb[tslot & (y > 27.2) & (y < 28.4)] = DARK[3]
            eyes = (np.abs(y - 27.8) < 0.3) & (np.abs(ax - 2.4) < 1.0)
            rgb[eyes] = (214, 140, 255)
            glow |= eyes
            rgb[eyes & (np.abs(ax - 2.4) < 0.35)] = (255, 236, 255)
        if ctx.face == "up":
            ridge = np.abs(x) < 1.5
            rgb[ridge] = rgb[ridge] * 0.85
        if ctx.face in ("west", "east"):
            # engraved gold swirl at the temple
            r = np.hypot(z - 0.5, y - 27.0)
            swirl = (np.abs(r - 1.8) < 0.26) & (z < 2.5)
            gv, grgb = M.gold(ctx, GOLD, engrave=False)
            rgb[swirl] = grgb[swirl]
        return rgb, 255, glow

    def plume(ctx):
        """Violet energy crest: streaks along the length, glowing crest edge."""
        tier = ctx.params.get("tier", 0)
        x, y, z = ctx.p[:, 0], ctx.p[:, 1], ctx.p[:, 2]
        streak = fbm(np.c_[z * 0.12, y * 2.4, x * 2.4], 1.0, 2, seed=8 + tier)
        v = 0.28 + (y - ctx.params.get("y0", 33.4)) * 0.05 + (streak - 0.5) * 0.5 + (z + 5) * 0.012
        rgb = M.ramp(CAPE, v, ctx, 0.6)
        dl, dr, dt, db = M.edist(ctx)
        glow = np.zeros(ctx.N, dtype=bool)
        if M.side_face(ctx):
            edge = dt == 0
            rgb[edge] = CAPE[10]
            fil = np.abs(streak - 0.5) < 0.03
            rgb[fil] = CAPE[9]
            glow |= edge | fil
            if tier == 0:
                base = db <= 1
                gv, grgb = M.gold(ctx, GOLD, engrave=False)
                rgb[base] = grgb[base]
                glow &= ~base
        else:
            if ctx.face == "up":
                rgb[:] = CAPE[6]
                mid = np.abs(ctx.s - 0.5) * ctx.tw < 1.0
                rgb[mid] = CAPE[10]
                glow |= mid
            else:
                rgb[:] = CAPE[3]
        return rgb, 255, glow

    def cape(ctx):
        part = ctx.params.get("part", 0)
        x, y, z = ctx.p[:, 0], ctx.p[:, 1], ctx.p[:, 2]
        alpha = np.full(ctx.N, 255)
        glow = np.zeros(ctx.N, dtype=bool)
        fold = np.sin(x * 1.25 + 0.6) * 0.5 + 0.5
        if ctx.face == "south":
            v = 0.34 + fold * 0.2 + (y - 3) * 0.012 + (fbm(np.c_[x * 1.5, y * 0.12, z], 1.0, 2, 4) - 0.5) * 0.18
            rgb = M.ramp(CAPE, v, ctx, 0.7)
            # energy filaments rising up the cape
            fil = fbm(np.c_[x * 0.9, y * 0.18, z * 0.0], 1.0, 3, 21)
            line = np.abs(fil - 0.5) < 0.025
            rgb[line] = CAPE[9]
            glow |= line
            # ender particle specks
            sp = (M.texel_hash(ctx, 17) > 0.988)
            rgb[sp] = CAPE[10]
            glow |= sp
            # gold embroidered border + eye sigil
            dl, dr, dt, db = M.edist(ctx)
            side_border = (dl < 1) | (dr < 1)
            gv, grgb = M.gold(ctx, GOLD, engrave=False)
            rgb[side_border] = grgb[side_border]
            if part == 0:
                top = dt < 2
                rgb[top] = grgb[top]
                ax = np.abs(x)
                r = np.hypot(x, (y - 19.0) * 1.5)
                sig = (np.abs(r - 2.2) < 0.28) | ((ax < 0.28) & (np.abs(y - 19.0) < 1.0))
                rgb[sig] = CAPE[10]
                glow |= sig
                dia = (np.abs(x) + np.abs(y - 19.0) * 0.8 < 3.6) & (np.abs(x) + np.abs(y - 19.0) * 0.8 > 3.2)
                rgb[dia] = GOLD[6]
                glow &= ~dia
            if part == 1:
                hem = (y < 5.0) & (y > 4.0)
                rgb[hem] = grgb[hem]
                zig = np.abs(np.abs(((x * 2) % 4) - 2) * 0.5 + 5.2 - y) < 0.3
                rgb[zig & (y > 5.0)] = GOLD[6]
                # dissolving energy hem: cut-out wisps with glowing tips
                col = np.floor(x * 2 + 0.01)
                ln = 1 + np.floor(hash3(col, 3, 1, 2) * 4)
                cut = (ctx.th - 1 - ctx.j) < ln - 1
                alpha[cut] = 0
                tip = ((ctx.th - 1 - ctx.j) == ln - 1) | ((ctx.th - 1 - ctx.j) == ln)
                rgb[tip & (y < 4.0)] = CAPE[10]
                glow |= tip & (y < 4.0)
        elif ctx.face == "north":
            v = 0.5 + fold * 0.3 - ctx.ao * 0.4
            rgb = M.ramp(LINING, v, ctx, 0.5)
            if part == 1:
                col = np.floor(-x * 2 + 0.01)
                ln = 1 + np.floor(hash3(-col - 1, 3, 1, 2) * 4)
                cut = (ctx.th - 1 - ctx.j) < ln - 1
                alpha[cut] = 0
        else:
            rgb = np.tile(CAPE[5], (ctx.N, 1)).astype(float)
            rgb[(ctx.j % 3) == 0] = CAPE[4]
            if ctx.face == "down" and part == 1:
                alpha[:] = 0
            if ctx.face in ("west", "east") and part == 1:
                alpha[(ctx.th - 1 - ctx.j) < 1] = 0
        return rgb, alpha, glow

    def dark(ctx):
        v = 0.5 + M.bevel(ctx, 0.2, 0.2) - ctx.ao * 0.4
        return M.ramp(DARK, v, ctx, 0.4), 255, np.zeros(ctx.N, dtype=bool)

    def crown(ctx):
        v, rgb = M.gold(ctx, GOLD, engrave=False)
        alpha = np.full(ctx.N, 255)
        glow = np.zeros(ctx.N, dtype=bool)
        if ctx.face in ("north", "south"):
            # crown points: cut a three-spired silhouette out of the top
            s = ctx.s if ctx.face == "north" else 1 - ctx.s
            u = (s - 0.5) * ctx.tw          # texels from centre
            h = ctx.th - ctx.j              # texels from bottom
            prof = np.where(np.abs(u) < 1.5, 8, np.where(np.abs(np.abs(u) - 4.5) < 1.5, 7, 4))
            alpha[h > prof] = 0
            rim = (h == prof) | (h == 1)
            rgb[rim] = GOLD[8]
            inner = (h > 1) & (h < prof - 1) & (np.abs(u) > 0.5) & ((np.abs(u) + h) % 4 == 0)
            rgb[inner] = GOLD[3]
        elif ctx.face == "up":
            alpha[:] = 0
        return rgb, alpha, glow

    def feather(ctx):
        v, rgb = M.gold(ctx, GOLD, engrave=False)
        if M.side_face(ctx):
            barb = (ctx.i % 2 == 0) & (ctx.j == ctx.th // 2)
            rgb[barb] = GOLD[3]
            rgb[ctx.j == 0] = GOLD[8]
        return rgb, 255, np.zeros(ctx.N, dtype=bool)

    def ecore(ctx):
        """End-crystal core: hot violet-pink cube, white heart."""
        dx = (ctx.s - 0.5) * 2
        dy = (ctx.t - 0.5) * 2
        r = np.maximum(np.abs(dx), np.abs(dy))
        v = 1.0 - r * 0.5 + (M.texel_hash(ctx, 3) - 0.5) * 0.12
        rgb = M.ramp(ECORE, v, ctx, 0.3)
        rgb[r < 0.3] = (255, 240, 255)
        return rgb, 255, np.ones(ctx.N, dtype=bool)

    def ecage(ctx):
        """End-crystal glass cage: only the face borders are solid, lit corners."""
        dl, dr, dt, db = M.edist(ctx)
        m = np.minimum(np.minimum(dl, dr), np.minimum(dt, db))
        edge = m < 1
        rgb = np.tile(np.array([226, 196, 255], dtype=float), (ctx.N, 1))
        corner = (np.minimum(dl, dr) == 0) & (np.minimum(dt, db) == 0)
        rgb[corner] = (255, 250, 255)
        mid = edge & ((dl == ctx.tw // 2) | (dt == ctx.th // 2))
        rgb[mid] = (186, 140, 240)
        return rgb, np.where(edge, 255, 0), edge

    return {"purpur": purpur, "gold": gold, "eye": eye, "helm": helm, "plume": plume, "cape": cape, "dark": dark,
            "crown": crown, "feather": feather, "ecore": ecore, "ecage": ecage}


# =============================================================================== animation

def build_clips():
    T = 3.2
    w = 2 * math.pi / T
    c = Clip("idle", T, loop=True)
    c.f("cape", "rotation", lambda t: [3.0 + 3.0 * math.sin(w * t), 1.2 * math.sin(w * t + 1.0), 1.0 * math.sin(w * t + 0.4)])
    c.f("capeLower", "rotation", lambda t: [2.5 + 4.0 * math.sin(w * t - 1.1), 0, 1.6 * math.sin(w * t - 0.6)])
    c.f("crest", "rotation", lambda t: [0, 0, 1.5 * math.sin(w * t + 2.0)])
    for side, s in ((-1, "R"), (1, "L")):                                # hovering End crystals spin and bob
        c.f(f"stage3_enderCrystal{s}", "rotation", lambda t, sd=side: [0, sd * 360.0 * t / T, 0])
        c.f(f"stage3_enderCrystal{s}", "position", lambda t, sd=side: [0, 0.3 * math.sin(w * t + (sd + 1) * 1.4), 0])
    c.f("stage2_plumeTail", "rotation", lambda t: [2.0 * math.sin(w * t + 1.2), 0, 1.5 * math.sin(w * t + 2.0)])
    return [c]


# =============================================================================== build

def build(preview=False):
    m = build_model()
    W, H = m.pack()
    paths = al.asset_paths(NAME)
    geo = ak.export_geo(m, paths["geo"])
    print(f"{NAME}: {m.cube_count()} cubes, uv {W}x{H}, png {W * 2}x{H * 2}")
    anims = al.export_anims(build_clips(), paths["anim"])
    rgba, glow = paint_staged(m, make_shaders())
    ak.save_textures(NAME, "", rgba, glow)
    if preview:
        import geo_preview as gp
        g = gp.load_geo(geo)
        ak.sheet_views("imperial armor", g, rgba, glow).save(os.path.join(ak.PREVIEW, "imperial_views.png"))
        ak.sheet_details("imperial armor details", g, rgba, glow).save(os.path.join(ak.PREVIEW, "imperial_details.png"))
        ak.texture_sheet(rgba, glow).save(os.path.join(ak.PREVIEW, "imperial_texture.png"))
        an = anims["animations"]["idle"]
        ak.sheet_anim("imperial idle", g, rgba, glow, an, [0, 0.8, 1.6, 2.4], view=("side", 100, -6)).save(
            os.path.join(ak.PREVIEW, "imperial_idle.png"))
        import stage_preview
        stage_preview.stage_sheet("imperial")
    return m, geo, (rgba, glow), anims


if __name__ == "__main__":
    build(preview="--preview" in sys.argv)
