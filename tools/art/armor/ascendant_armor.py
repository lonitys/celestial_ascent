"""Ascendant armor: the ultimate set. Radiant white-gold and pearl plate, prismatic gems in all four
elemental colours, a spinning floating halo crown and two pairs of fluttering angelic light wings.

Run: python ascendant_armor.py [--preview]
"""
import math
import os
import sys

import numpy as np

import armorkit as ak
import armorlib as al
import mats as M
from armorlib import Clip, fbm, hash3, worley
from common_geo import cube, sym, boxc, sym_boxc, cross_sprite, sym_cross_sprite

NAME = "ascendant_armor"

PEARL = M.pal("#77708a", "#8c85a0", "#a19bb4", "#b5b0c6", "#c8c4d6", "#d8d5e3", "#e5e3ee", "#efeef6", "#f7f6fb",
              "#fcfcfe", "#ffffff")
GOLD = M.pal("#4a2805", "#6c3f09", "#91590f", "#b47616", "#d4941f", "#ecb22c", "#fbcd45", "#ffe274", "#fff2ab",
             "#fffbe2")
GEMS = {
    "frost": M.pal("#0a3f7e", "#1264b0", "#2393e0", "#4cc0f8", "#92e4ff", "#d8f8ff", "#ffffff"),
    "tide": M.pal("#053f55", "#086478", "#0f8e94", "#22b8ad", "#62e0cc", "#c4fff2", "#ffffff"),
    "storm": M.pal("#6a4003", "#9c6a08", "#d09d14", "#f8cc32", "#fff082", "#fffbe0", "#ffffff"),
    "magma": M.pal("#5e1003", "#9a2406", "#d8480e", "#ff7a1e", "#ffb452", "#ffeec0", "#ffffff"),
    "prism": M.pal("#8a7db0", "#b2a6d8", "#d6ccf4", "#efe8ff", "#fffaff", "#ffffff", "#ffffff"),
}
ELEMENT_RGB = {"frost": (110, 210, 255), "tide": (70, 230, 200), "storm": (255, 226, 80), "magma": (255, 130, 40)}
LIGHT = M.pal("#b08a3a", "#d2ae5a", "#ebcd82", "#f8e3a8", "#fff1cc", "#fff9e8", "#ffffff")
IRIDESCENT = [np.array([255, 214, 236]), np.array([206, 236, 255]), np.array([255, 240, 206])]
LUMEN = M.pal("#6f8fe0", "#93b2f2", "#b8cefa", "#d8e6ff", "#eef4ff", "#ffffff")   # luminous light wings


# =============================================================================== geometry

def gem(bone, center, size, element, rot=(0, 0, 45), **params):
    return boxc(bone, center, size, "gem", rot=list(rot), element=element, **params)


def build_model():
    m = ak.new_model(NAME)
    H, B = m["armorHead"], m["armorBody"]
    RA, LA = m["armorRightArm"], m["armorLeftArm"]
    RL, LL = m["armorRightLeg"], m["armorLeftLeg"]
    RB, LB = m["armorRightBoot"], m["armorLeftBoot"]

    # ------------------------------------------------------------------ helmet
    cube(H, (-5, 23, -5), (10, 10, 10), "helm")
    cube(H, (-3, 23.3, -5.6), (6, 2, 1), "mask")                                  # gold mouth guard
    cube(H, (-0.5, 25.2, -5.5), (1, 3, 1), "gold")                                # nasal ridge
    cube(H, (-5.5, 29.0, -5.8), (11, 2, 2), "gold", band=True)                    # diadem
    cube(H, (-2, 28.4, -6.3), (4, 3, 1), "gold")                                  # diadem plate
    gem(H, (0, 29.9, -6.6), (2, 2, 1), "prism")                                   # prismatic brow gem
    sym(H, H, (-5.9, 23.4, -4.6), (1, 5, 6), "pearl", trim=("bottom", "left", "right"))   # cheek guards
    cube(H, (-1, 32.7, -4.2), (2, 1, 8), "gold")                                  # crest line
    cube(H, (-5, 22.4, 4.6), (10, 3, 1), "pearl", trim=("bottom",), lames=True)
    for side in (-1, 1):                                                          # feathered temple wings
        wb = m.bone(f"helmWing{'R' if side < 0 else 'L'}", "armorHead", (5.4 * side, 28.5, -1.0),
                    rotation=[0, 28 * side, 0])
        cube(wb, (5.4 * side, 27.0, -1.0), (0, 7, 7), "hwing", side=side)

    halo = m.bone("halo", "armorHead", (0, 36.2, 0))
    R = 5.4
    for k in range(16):
        a = k * 22.5
        cx, cz = R * math.sin(math.radians(a)), -R * math.cos(math.radians(a))
        cube(halo, (cx - 1.5, 35.7, cz - 0.5), (3, 1, 1), "halo", rot=[0, -a, 0], pivot=[cx, 36.2, cz])
    for k, el in enumerate(("storm", "frost", "magma", "tide")):              # four elemental gems on the halo
        a = math.radians(k * 90)
        gem(halo, ((R + 0.45) * math.sin(a), 36.2, -(R + 0.45) * math.cos(a)), (2, 2, 1), el, rot=(0, -k * 90, 45))
    for k in range(4):                                                         # radiant crown rays
        a = math.radians(k * 90 + 45)
        cross_sprite(halo, (R * math.sin(a), 36.0, -R * math.cos(a)), (0, 1, 0), 3, 3, "ray", spin=k * 90 + 45)

    # ------------------------------------------------------------------ chestplate body
    cube(B, (-4.5, 11.5, -3), (9, 13, 6), "pearl")
    cube(B, (-5, 16.8, -4), (10, 7, 2), "pearl", trim=("top", "left", "right", "bottom"), plate="breast")
    cube(B, (-2.5, 17.8, -4.6), (5, 5, 1), "gold", rot=[0, 0, 45], pivot=[0, 20.3, -4.1])   # sun setting
    gem(B, (0, 20.3, -5.05), (3, 3, 1), "prism")                                 # central prism
    gem(B, (0, 22.75, -4.8), (2, 2, 1), "storm")
    gem(B, (0, 17.85, -4.8), (2, 2, 1), "magma")
    gem(B, (2.45, 20.3, -4.8), (2, 2, 1), "frost")
    gem(B, (-2.45, 20.3, -4.8), (2, 2, 1), "tide")
    cube(B, (-4.5, 15.0, -3.5), (9, 2, 1), "pearl", trim=("bottom",))
    cube(B, (-4.0, 13.3, -3.4), (8, 2, 1), "pearl", trim=("bottom",))
    cube(B, (-5, 12.2, -3.6), (10, 1, 7), "gold", band=True)
    cube(B, (-4.5, 15.5, 2.6), (9, 8, 1), "pearl", trim=("left", "right", "top"), plate="back")
    sym(B, B, (-3.6, 19.5, 3.2), (3, 4, 1), "gold")                               # wing mounts
    gem(B, (0, 21.0, 3.75), (2, 2, 1), "prism")
    for side in (-1, 1):
        s = "R" if side < 0 else "L"
        up = m.bone(f"wingUpper{s}", "armorBody", (2.2 * side, 22.5, 4.0), rotation=[0, -24 * side, -6 * side])
        x0 = 2.2 if side > 0 else -2.2 - 16
        cube(up, (x0, 17.5, 4.0), (16, 15, 0), "wing", side=side, tier=0)
        lo = m.bone(f"wingLower{s}", "armorBody", (2.0 * side, 18.5, 3.8), rotation=[0, -34 * side, 8 * side])
        x0 = 2.0 if side > 0 else -2.0 - 12
        cube(lo, (x0, 9.5, 3.8), (12, 10, 0), "wing", side=side, tier=1)

    # ------------------------------------------------------------------ arms
    for side, arm, el_p, el_v in ((-1, RA, "magma", "storm"), (1, LA, "frost", "tide")):
        def X(x0, w):
            return x0 if side < 0 else -(x0 + w)
        cube(arm, (X(-8.5, 4), 12, -2.5), (4, 12, 5), "pearl", inflate=0.25, side=side)
        cube(arm, (X(-10.2, 6), 22.0, -4.0), (6, 3, 8), "pearl", trim=("bottom",), plate="pauldron", side=side)
        cube(arm, (X(-10.4, 6), 21.0, -4.25), (6, 1, 9), "gold", band=True)
        cube(arm, (X(-10.6, 6), 19.2, -4.0), (6, 2, 8), "pearl", rot=[0, 0, 12 * -side],
             pivot=[7.6 * side, 21.2, 0], trim=("bottom",))
        gem(arm, (10.55 * side, 23.5, 0), (1, 2, 2), el_p, rot=(45, 0, 0))
        # feathered flare rising from the pauldron
        fw = m.bone(f"pauldronWing{'R' if side < 0 else 'L'}", "armorRightArm" if side < 0 else "armorLeftArm",
                    (9.0 * side, 24.0, 1.5), rotation=[0, 0, -30 * side])
        cube(fw, (9.0 * side, 23.0, -2.5), (0, 6, 6), "hwing", side=side, flare=True)
        cube(arm, (X(-9.25, 5), 11.1, -3), (5, 6, 6), "pearl", inflate=0.15, trim=("top", "bottom"), side=side)
        cube(arm, (X(-9.6, 5), 16.4, -3.5), (5, 1, 7), "gold", band=True, inflate=0.05)
        gem(arm, (9.6 * side, 14.0, 0), (1, 2, 2), el_v, rot=(45, 0, 0))

    # ------------------------------------------------------------------ leggings
    cube(RL, (-4.025, 0, -2.5), (4, 12, 5), "pearl", inflate=0.375, side=-1)
    cube(LL, (-0.025, 0, -2.5), (4, 12, 5), "pearl", inflate=0.425, side=1)
    sym(RL, LL, (-5.0, 10.4, -3.5), (5, 2, 7), "gold", band=True)
    sym(RL, LL, (-4.4, 5.4, -3.6), (4, 5, 1), "pearl", rot=[-8, 0, 0], pivot=[-2.4, 10.4, -3.1],
        trim=("bottom", "left", "right"), plate="tasset")
    sym(RL, LL, (-5.4, 5.0, -2.5), (1, 5, 5), "pearl", rot=[0, 0, 8], pivot=[-4.9, 10.4, 0], trim=("bottom",))
    sym(RL, LL, (-4.3, 3.8, -3.4), (4, 3, 1), "gold")
    gem(RL, (-2.3, 5.3, -4.25), (2, 2, 1), "tide")
    gem(LL, (2.3, 5.3, -4.25), (2, 2, 1), "storm")
    gem(RL, (-0.9, 11.4, -3.95), (1, 1, 1), "prism")
    gem(LL, (0.9, 11.4, -3.95), (1, 1, 1), "prism")

    # ------------------------------------------------------------------ boots
    cube(RB, (-4.75, -0.25, -3.0), (5, 6, 6), "pearl", inflate=0.2, side=-1, trim=("top",))
    cube(LB, (-0.25, -0.25, -3.0), (5, 6, 6), "pearl", inflate=0.25, side=1, trim=("top",))
    sym(RB, LB, (-5.0, -0.55, -4.6), (5, 2, 3), "gold")
    sym(RB, LB, (-5.05, -0.6, -3.5), (5, 1, 7), "gold", inflate=0.05, sole=True)
    sym(RB, LB, (-5.1, 5.2, -3.5), (5, 1, 7), "gold", band=True, inflate=0.1)
    sym(RB, LB, (-3.5, 1.6, -3.75), (2, 3, 1), "gold")
    gem(RB, (-2.5, 3.1, -4.2), (1, 1, 1), "frost", inflate=0.1)
    gem(LB, (2.5, 3.1, -4.2), (1, 1, 1), "magma", inflate=0.1)
    for side, bb in ((-1, RB), (1, LB)):                                          # ankle wings
        wb = m.bone(f"ankleWing{'R' if side < 0 else 'L'}", "armorRightBoot" if side < 0 else "armorLeftBoot",
                    (5.0 * side, 3.5, 0.5), rotation=[0, 24 * side, 0])
        cube(wb, (5.0 * side, 2.0, 0.5), (0, 5, 5), "hwing", side=side, small=True)
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


def build_stage_parts(m):
    # ------------------------------------------------------------------ helmet
    # stage 2: radiant halo - an outer, counter-rotating ring of light rays around the halo
    hr = stage_bone(m, "stage2_haloRays", "armorHead", (0, 36.2, 0))
    for k in range(8):
        a = math.radians(k * 45 + 22.5)
        sa, ca = math.sin(a), math.cos(a)
        cross_sprite(hr, (round(6.6 * sa, 3), 35.6, round(-6.6 * ca, 3)), (0.75 * sa, 0.66, -0.75 * ca), 3, 2, "ray",
                     spin=k * 45 + 22.5)
    # stage 3: gold crown - jeweled band round the temples and back, stepped spires, prism-set centre spire
    cr = stage_bone(m, "stage3_crown", "armorHead", (0, 30.0, 0))
    sym(cr, cr, (-6.4, 30.0, -4.4), (1, 2, 10), "gold", band=True)                       # side bands
    cube(cr, (-6.4, 30.0, 5.6), (13, 2, 1), "gold", band=True)                           # back band
    for k, w in enumerate((3, 2, 1)):                                                    # centre spire
        cr.boxb(0, 31.4 + k, -5.8, w, 1, 1, "gold")
    boxc(cr, (0, 32.9, -6.45), (1, 1, 1), "gem", rot=[0, 0, 45], element="prism", inflate=0.1)
    for x in (-3.3, 3.3):                                                                # front side spires
        for k, w in enumerate((2, 1)):
            cr.boxb(x, 31.0 + k, -5.3, w, 1, 1, "gold")
    for side in (-1, 1):                                                                 # side spires
        for z in (-2.0, 2.6):
            for k, d in enumerate((2, 1)):
                cr.boxb(5.9 * side, 32.0 + k, z, 1, 1, d, "gold")
    for x in (-3.2, 0.0, 3.2):                                                           # back spires
        for k, w in enumerate((2, 1)):
            cr.boxb(x, 32.0 + k, 6.1, w, 1, 1, "gold")
    for (x, z, el) in ((-5.9, -4.4, "magma"), (5.9, -4.4, "frost"), (-5.9, 5.6, "tide"), (5.9, 5.6, "storm")):
        gem(cr, (x, 32.6, z), (1, 1, 1), el, rot=(0, 45, 0), inflate=0.12)               # corner jewels

    # ------------------------------------------------------------------ chestplate
    # stage 2: ornate pauldrons - jeweled gold cap, extra gold-trimmed lame, pearl and gold star medallion
    pr, pl = stage_pair(m, "stage2_pauldron", "Arm", (-7.4, 25.0, 0))
    sym(pr, pl, (-10.4, 25.0, -3.5), (6, 1, 7), "gold", band=True)
    sym(pr, pl, (-11.0, 17.4, -4.0), (6, 2, 8), "pearl", rot=[0, 0, 20], pivot=[-7.8, 19.4, 0], trim=("bottom",))
    sym_boxc(pr, pl, (-10.95, 22.6, 0.0), (1, 3, 3), "gold")
    sym_boxc(pr, pl, (-10.75, 22.6, 0.0), (1, 3, 3), "pearl", rot=[45, 0, 0], trim=("left", "right", "top", "bottom"))
    gem(pr, (-11.55, 22.6, 0.0), (1, 2, 2), "magma", rot=(45, 0, 0))
    gem(pl, (11.55, 22.6, 0.0), (1, 2, 2), "frost", rot=(45, 0, 0))
    # stage 3: the third pair of wings - luminous light wings folded upright behind the shoulders
    for side in (-1, 1):
        s = "R" if side < 0 else "L"
        lw = stage_bone(m, f"stage3_lightWing{s}", "armorBody", (1.8 * side, 22.5, 5.0))
        lw.rotation = [-8.0, -28.0 * side, 10.0 * side]
        x0 = 1.8 if side > 0 else -1.8 - 10
        cube(lw, (x0, 21.7, 5.0), (10, 13, 0), "lwing", side=side)

    # ------------------------------------------------------------------ leggings
    # stage 2: gold diamond knee medallions with their element gem
    kr, kl = stage_pair(m, "stage2_kneeMedallion", "Leg", (-2.3, 5.3, -3.6))
    sym_boxc(kr, kl, (-2.3, 5.3, -4.1), (3, 3, 1), "gold", rot=[0, 0, 45])
    gem(kr, (-2.3, 5.3, -4.75), (2, 2, 1), "tide")
    gem(kl, (2.3, 5.3, -4.75), (2, 2, 1), "storm")
    # stage 3: feathered gold wings at the outer hips (below the hands)
    for side in (-1, 1):
        s = "R" if side < 0 else "L"
        hb = stage_bone(m, f"stage3_hipWing{s}", "armorRightLeg" if side < 0 else "armorLeftLeg",
                        (5.5 * side, 9.0, -0.6))
        hb.rotation = [0.0, 24.0 * side, 0.0]
        cube(hb, (5.5 * side, 6.4, -0.6), (0, 4, 5), "hwing", side=side, small=True)

    # ------------------------------------------------------------------ boots
    # stage 2: the ankle wings grow (a larger feather layer behind the original)
    for side in (-1, 1):
        s = "R" if side < 0 else "L"
        wb = stage_bone(m, f"stage2_ankleWing{s}", "armorRightBoot" if side < 0 else "armorLeftBoot",
                        (5.15 * side, 3.5, 0.3))
        wb.rotation = [0.0, 24.0 * side, 0.0]
        cube(wb, (5.15 * side, 1.3, 0.3), (0, 6, 7), "hwing", side=side, small=True)
    # stage 3: light spurs - gold neck, prism gem and a ray of light streaming back from each heel
    sr, sl = stage_pair(m, "stage3_lightSpur", "Boot", (-2.4, 1.9, 3.2))
    sym(sr, sl, (-2.9, 1.4, 3.1), (1, 1, 2), "gold")
    gem(sr, (-2.4, 1.9, 5.3), (1, 1, 1), "prism", rot=(0, 0, 45), inflate=0.15)
    gem(sl, (2.4, 1.9, 5.3), (1, 1, 1), "prism", rot=(0, 0, 45), inflate=0.15)
    sym_cross_sprite(sr, sl, (-2.4, 1.9, 5.6), (0, 0.2, 1.0), 3, 2, "ray")


# =============================================================================== shaders

def arm_curve(uu, W, Hh, tier):
    uu = np.asarray(uu, dtype=float)
    if tier == 0:
        return Hh * 0.52 * np.sin(np.clip(uu / W, 0, 1) * math.pi * 0.62) + uu * 0.04
    return Hh * 0.18 * np.sin(np.clip(uu / W, 0, 1) * math.pi * 0.7) - uu * 0.06


def wing_layers(u, v, W, Hh, tier, nf):
    """Procedural angel wing in plane units (u: 0 root .. W tip, v: height above the root).

    Layers bottom->top: primaries, two rows of coverts, the leading-edge arm. Returns per-texel
    kind (0 empty, 1 primary, 2 covert, 3 arm), shade value, outline mask, shaft mask, feather index
    and along-feather progress."""
    N = len(u)
    kind = np.zeros(N, dtype=int)
    val = np.zeros(N)
    outline = np.zeros(N, dtype=bool)
    shaft = np.zeros(N, dtype=bool)
    fidx = np.full(N, -1)
    prog = np.zeros(N)

    def fdir(f):
        a = math.radians(-100 + f * 80) if tier == 0 else math.radians(-112 + f * 70)
        return math.cos(a), math.sin(a)

    for k in range(nf):                                        # primaries
        f = (k + 0.5) / nf
        ru = f * W * 0.92
        rv = float(arm_curve(ru, W, Hh, tier)) - 0.6
        dx, dy = fdir(f)
        L = (Hh * 0.6 + f * W * 0.34) if tier == 0 else (Hh * 0.6 + f * W * 0.24)
        wdt = 1.35 + 0.3 * (1 - abs(f - 0.6))
        tt = (u - ru) * dx + (v - rv) * dy
        nn = -(u - ru) * dy + (v - rv) * dx
        p = tt / L
        half = wdt * np.where(p < 0.8, 1.0, np.sqrt(np.clip((1 - p) / 0.2, 0, 1)))
        ins = (p >= -0.05) & (p <= 1) & (np.abs(nn) <= half)
        shade = 0.96 - np.abs(nn) / np.maximum(half, 1e-3) * 0.3 - np.clip(p, 0, 1) * 0.16
        ol = ins & ((nn < -(half - 0.55)) | (p > 1 - 0.5 / L))
        sh = ins & (np.abs(nn) < 0.25) & (p > 0.06) & (p < 0.86)
        kind = np.where(ins, 1, kind)
        val = np.where(ins, shade, val)
        outline = np.where(ins, ol, outline)
        shaft = np.where(ins, sh, shaft)
        fidx = np.where(ins, k, fidx)
        prog = np.where(ins, p, prog)
    for row in (0,):                                           # one row of rounded coverts
        n = nf + 1
        Lc = 3.6 * (1.0 if tier == 0 else 0.8)
        for k in range(n):
            f = (k + 0.5) / n
            ru = f * W * 0.9
            rv = float(arm_curve(ru, W, Hh, tier)) - 0.4
            dx, dy = fdir(f)
            wdt = 1.25
            tt = (u - ru) * dx + (v - rv) * dy
            nn = -(u - ru) * dy + (v - rv) * dx
            r = np.sqrt(((tt - Lc / 2) / (Lc / 2)) ** 2 + (nn / wdt) ** 2)
            ins = r <= 1.0
            kind = np.where(ins, 2, kind)
            val = np.where(ins, 0.98 - r * 0.22 - row * 0.04, val)
            outline = np.where(ins, (r > 0.74) & (tt > Lc * 0.45), outline)
            shaft = np.where(ins, False, shaft)
    ay = arm_curve(u, W, Hh, tier)                             # leading-edge arm
    arm = (u >= -0.2) & (u <= W * 0.95) & (v <= ay + 0.7) & (v >= ay - 1.0)
    kind = np.where(arm, 3, kind)
    val = np.where(arm, 1.0, val)
    outline = np.where(arm, v > ay + 0.25, outline)
    shaft = np.where(arm, False, shaft)
    return kind, val, outline, shaft, fidx, prog


def make_shaders():
    def iridescence(ctx, rgb, amt=0.22):
        n1 = fbm(ctx.p, 0.18, 2, seed=61)
        n2 = fbm(ctx.p, 0.22, 2, seed=67)
        tint = IRIDESCENT[0] * (1 - n1)[:, None] + IRIDESCENT[1] * n1[:, None]
        tint = tint * (1 - np.clip(n2 - 0.4, 0, 1))[:, None] + IRIDESCENT[2] * np.clip(n2 - 0.4, 0, 1)[:, None]
        rgb[:] = rgb * (1 - amt) + tint * amt * (rgb / 255.0) * 1.15

    def pearl(ctx):
        prm = ctx.params
        extra = M.panel(ctx, 2, 12, 0.10)
        y = ctx.p[:, 1]
        if prm.get("lames") and M.side_face(ctx):
            extra -= np.where(((ctx.th - 1 - ctx.j) % 3 == 0) & (ctx.j > 0), 0.12, 0)
        v, rgb = M.metal(ctx, PEARL, base=0.76, sheen_amt=0.12, noise=0.015, brush=0.015, extra=extra, grad=0.18)
        iridescence(ctx, rgb)
        glow = np.zeros(ctx.N, dtype=bool)
        trim = prm.get("trim")
        gv, grgb = M.gold(ctx, GOLD, engrave=False, base=0.7)
        if trim:
            tm = M.trim_band(ctx, 2, trim) & M.side_face(ctx)
            if ctx.face == "up":
                tm |= M.emin(ctx) < 1
            rgb[tm] = grgb[tm]
        x = ctx.p[:, 0]
        plate = prm.get("plate")
        if plate == "breast" and ctx.face == "north":
            # radiant sunburst inlaid in gold behind the gem cluster
            ang = np.arctan2(y - 20.3, x)
            r = np.hypot(x, (y - 20.3))
            rays = (np.abs(((ang / (math.pi / 8)) % 1.0) - 0.5) > 0.42) & (r > 3.6)
            rgb[rays] = grgb[rays]
            sparkle = rays & (M.texel_hash(ctx, 5) > 0.9)
            rgb[sparkle] = GOLD[9]
            glow |= sparkle
        if plate == "back" and ctx.face == "south":
            ang = np.arctan2(y - 21.0, x)
            r = np.hypot(x, y - 21.0)
            rays = (np.abs(((ang / (math.pi / 6)) % 1.0) - 0.5) > 0.43) & (r > 2.0)
            rgb[rays] = grgb[rays]
        if plate == "tasset" and ctx.face == "north":
            # engraved feather motif
            cxp = (ctx.s - 0.5) * ctx.tw
            fe = (np.abs(cxp) < 0.6) & (ctx.j > 1) & (ctx.j < ctx.th - 3)
            barb = (np.abs(np.abs(cxp) - (ctx.j % 3) * 0.6 - 0.6) < 0.5) & (ctx.j > 1) & (ctx.j < ctx.th - 3) & (
                np.abs(cxp) < 2.5)
            rgb[fe | barb] = grgb[fe | barb]
        if plate == "pauldron" and ctx.face == "up":
            sp = M.texel_hash(ctx, 8) > 0.97
            rgb[sp] = GOLD[8]
        return rgb, 255, glow

    def gold(ctx):
        prm = ctx.params
        v, rgb = M.gold(ctx, GOLD, engrave=not prm.get("band") and not prm.get("feather"), base=0.7)
        glow = np.zeros(ctx.N, dtype=bool)
        if prm.get("band") and M.side_face(ctx) and ctx.th >= 2:
            k = ctx.i % 6
            jewel = (k == 3) & (ctx.j == ctx.th // 2)
            cols = np.array([ELEMENT_RGB[e] for e in ("frost", "tide", "storm", "magma")])
            idx = ((ctx.i // 6) % 4).astype(int)
            rgb[jewel] = cols[idx[jewel]]
            glow |= jewel
        if prm.get("feather") and M.side_face(ctx):
            rgb[ctx.j == 0] = GOLD[9]
            glow |= ctx.j == 0
        if prm.get("sole"):
            rgb *= 0.8
        return rgb, 255, glow

    def helm(ctx):
        v, rgb = M.metal(ctx, PEARL, base=0.76, sheen_amt=0.12, noise=0.015, brush=0.015,
                         extra=M.panel(ctx, 2, 16, 0.10), grad=0.18)
        iridescence(ctx, rgb)
        x, y, z = ctx.p[:, 0], ctx.p[:, 1], ctx.p[:, 2]
        glow = np.zeros(ctx.N, dtype=bool)
        gv, grgb = M.gold(ctx, GOLD, engrave=False, base=0.7)
        if ctx.face == "up":
            ang = np.arctan2(z, x)
            r = np.hypot(x, z)
            rays = (np.abs(((ang / (math.pi / 6)) % 1.0) - 0.5) > 0.44) & (r > 1.6) & (r < 4.6)
            rgb[rays] = grgb[rays]
        if ctx.face in ("west", "east", "south"):
            band = np.abs(y - 28.3) < 0.26
            rgb[band] = grgb[band]
        if ctx.face == "north":
            ax = np.abs(x)
            slit = (np.abs(y - 27.6) < 0.55) & (ax < 4.0) & (ax > 0.5)
            frame = (np.abs(y - 27.6) < 1.1) & (ax < 4.5) & ~slit
            rgb[frame] = grgb[frame]
            rgb[slit] = (255, 248, 224)
            glow |= slit
            hot = slit & (np.abs(y - 27.6) < 0.3) & (np.abs(ax - 2.2) < 1.0)
            rgb[hot] = (255, 255, 255)
            # filigree: feathered gold sweeps under the eyes
            sweep = (np.abs(y - (25.8 - (ax - 1.0) * 0.45)) < 0.26) & (ax > 1.0) & (ax < 4.2)
            rgb[sweep] = grgb[sweep]
        return rgb, 255, glow

    def mask(ctx):
        v, rgb = M.gold(ctx, GOLD, engrave=False, base=0.7)
        glow = np.zeros(ctx.N, dtype=bool)
        x, y = ctx.p[:, 0], ctx.p[:, 1]
        if ctx.face == "north":
            ax = np.abs(x)
            # sculpted seraph face: brow arcs, nose ridge, cheek feathers
            nose = (ax < 0.5) & (y > 25.0)
            rgb[nose] = GOLD[8]
            cheek = (np.abs(y - (25.6 - (ax - 1.2) * 0.5)) < 0.26) & (ax > 1.2) & (ax < 3.8)
            rgb[cheek] = GOLD[3]
            cheek2 = (np.abs(y - (24.6 - (ax - 1.6) * 0.5)) < 0.26) & (ax > 1.6) & (ax < 3.8)
            rgb[cheek2] = GOLD[3]
            mouth = (np.abs(y - 24.0) < 0.24) & (ax < 1.0)
            rgb[mouth] = GOLD[2]
        return rgb, 255, glow

    def gemsh(ctx):
        el = ctx.params.get("element", "prism")
        p = GEMS[el]
        rgb, a, g = M.gem(ctx, p, shape="diamond", base=1.02, falloff=0.7)
        if el == "prism":
            # prismatic: each quadrant refracts a different element colour
            dx = ctx.s - 0.5
            dy = ctx.t - 0.5
            q = np.where(dy < 0, np.where(dx < 0, 0, 1), np.where(dx < 0, 2, 3))
            cols = np.array([ELEMENT_RGB[e] for e in ("frost", "storm", "tide", "magma")], dtype=float)
            r = np.abs(dx) + np.abs(dy)
            mix = np.clip((r - 0.1) * 1.6, 0, 0.7)[:, None]
            rgb[:] = rgb * (1 - mix) + cols[q] * mix
            core = r < 0.18
            rgb[core] = (255, 255, 255)
        return rgb, 255, np.ones(ctx.N, dtype=bool)

    def halo(ctx):
        v, rgb = M.gold(ctx, GOLD, engrave=False, base=0.7)
        glow = np.ones(ctx.N, dtype=bool)
        rgb = np.clip(rgb * 1.05 + 10, 0, 255)
        if ctx.face in ("north", "south", "up", "down"):
            line = ctx.j == ctx.th // 2
            rgb[line] = (255, 253, 236)
        return rgb, 255, glow

    def ray(ctx):
        keep = ctx.params.get("plane")
        if ctx.face != keep:
            return np.zeros((ctx.N, 3)), np.zeros(ctx.N), np.zeros(ctx.N, dtype=bool)
        t = 1 - ctx.t
        u = np.abs(ctx.s - 0.5) * 2
        inside = u <= (1 - t) ** 0.9 + 0.05
        v = 0.95 - t * 0.2 - u * 0.4
        rgb = M.ramp(LIGHT, v, ctx, 0.3)
        return rgb, np.where(inside, 255, 0), inside

    def wing(ctx):
        """Angelic light wing on a single-face plane (south face painted, north face transparent)."""
        side = ctx.params.get("side", -1)
        tier = ctx.params.get("tier", 0)
        if ctx.face != "south":
            return np.zeros((ctx.N, 3)), np.zeros(ctx.N), np.zeros(ctx.N, dtype=bool)
        x, y = ctx.p[:, 0], ctx.p[:, 1]
        lo, hi = ctx.lo, ctx.hi
        W = hi[0] - lo[0]
        u = (hi[0] - x) if side < 0 else (x - lo[0])
        root_y = 22.5 if tier == 0 else 18.5
        v = y - root_y
        Hh = hi[1] - lo[1]
        kind, val, outline, shaft, fidx, prog = wing_layers(u, v, W, Hh, tier, 7 if tier == 0 else 5)
        inside = kind > 0
        rgb = M.ramp(LIGHT, val)
        rgb[outline] = LIGHT[2]
        rgb[outline & (kind == 3)] = GOLD[7]
        rgb[shaft] = (255, 255, 255)
        cols = np.array([ELEMENT_RGB[e] for e in ("frost", "tide", "storm", "magma")], dtype=float)
        tipm = (kind == 1) & (prog > 0.8) & ~outline
        ci = np.clip(fidx, 0, 6) % 4
        rgb[tipm] = rgb[tipm] * 0.72 + cols[ci[tipm]] * 0.28
        return rgb, np.where(inside, 255, 0), inside

    def hwing(ctx):
        """Small feathered wing ornament (helm temples / ankles) on a single-face YZ plane (east face)."""
        side = ctx.params.get("side", -1)
        if ctx.face != "east":
            return np.zeros((ctx.N, 3)), np.zeros(ctx.N), np.zeros(ctx.N, dtype=bool)
        z, y = ctx.p[:, 2], ctx.p[:, 1]
        lo, hi = ctx.lo, ctx.hi
        u = (z - lo[2]) / max(hi[2] - lo[2], 1e-6)         # 0 front -> 1 back
        w = (y - lo[1]) / max(hi[1] - lo[1], 1e-6)         # 0 bottom -> 1 top
        inside = np.zeros(ctx.N, dtype=bool)
        fe = np.full(ctx.N, -1)
        for k in range(4):
            a = math.radians(18 + k * 16)
            base_u, base_w = 0.05, 0.25 + k * 0.08
            dx, dy = math.cos(a), math.sin(a)
            L = 0.95 - k * 0.12
            tt = (u - base_u) * dx + (w - base_w) * dy
            nn = -(u - base_u) * dy + (w - base_w) * dx
            p = tt / L
            half = 0.11 * np.where(p < 0.8, 1.0, np.sqrt(np.clip((1 - p) / 0.2, 0, 1)))
            ins = (p >= 0) & (p <= 1) & (np.abs(nn) <= half)
            fe = np.where(ins & (fe < 0), k, fe)
            inside |= ins
        v = 0.62 + (w - 0.5) * 0.2 + u * 0.3
        rgb = M.ramp(GOLD, v, ctx, 0.4)
        rgb[(fe % 2) == 1] = GOLD[6]
        tips = inside & (u > 0.55)
        rgb[tips] = M.ramp(LIGHT, 0.5 + u[tips] * 0.5)
        return rgb, np.where(inside, 255, 0), tips

    def lwing(ctx):
        """Luminous light wing folded upright (single-face plane, south face painted): a fan of glowing
        primaries rising from the root with element-tinted tips, a few coverts over the root."""
        if ctx.face != "south":
            return np.zeros((ctx.N, 3)), np.zeros(ctx.N), np.zeros(ctx.N, dtype=bool)
        x, y = ctx.p[:, 0], ctx.p[:, 1]
        u = np.abs(x) - 1.8                       # outward from the root
        v = y - 22.5                              # up from the root
        N = ctx.N
        kind = np.zeros(N, dtype=int)
        val = np.zeros(N)
        outline = np.zeros(N, dtype=bool)
        shaft = np.zeros(N, dtype=bool)
        fid = np.full(N, -1)
        prog = np.zeros(N)
        for k, (ang, L) in enumerate(((54, 7.4), (45, 8.8), (36, 10.0), (27, 11.0), (18, 11.8), (10, 12.3), (3, 12.4))):
            a = math.radians(ang)
            tt = u * math.sin(a) + v * math.cos(a)
            nn = u * math.cos(a) - v * math.sin(a)
            p = tt / L
            half = 1.25 * np.where(p < 0.15, 0.55 + p / 0.15 * 0.45,
                                   np.where(p < 0.78, 1.0, np.sqrt(np.clip((1 - p) / 0.22, 0, 1))))
            ins = (p >= -0.02) & (p <= 1) & (np.abs(nn) <= half)
            kind = np.where(ins, 1, kind)
            val = np.where(ins, 0.98 - np.abs(nn) / np.maximum(half, 1e-3) * 0.28 - np.clip(p, 0, 1) * 0.1, val)
            outline = np.where(ins, (nn > half - 0.5) | (p > 1 - 0.45 / L), outline)
            shaft = np.where(ins, (np.abs(nn) < 0.25) & (p > 0.08) & (p < 0.85), shaft)
            fid = np.where(ins, k, fid)
            prog = np.where(ins, p, prog)
        for k in range(5):                         # rounded coverts over the root
            a = math.radians(8 + k * 11)
            cu, cv = 0.5 + k * 1.0, 1.7 + k * 0.1
            tt = (u - cu) * math.sin(a) + (v - cv) * math.cos(a)
            nn = (u - cu) * math.cos(a) - (v - cv) * math.sin(a)
            r = np.sqrt((tt / 2.4) ** 2 + (nn / 1.1) ** 2)
            ins = r <= 1.0
            kind = np.where(ins, 2, kind)
            val = np.where(ins, 1.0 - r * 0.2, val)
            outline = np.where(ins, (r > 0.78) & (tt > 0.6), outline)
            shaft = np.where(ins, False, shaft)
        inside = kind > 0
        rgb = M.ramp(LUMEN, val, ctx, 0.3)
        rgb[outline] = LUMEN[1]
        rgb[shaft] = (255, 255, 255)
        cols = np.array([ELEMENT_RGB[e] for e in ("frost", "tide", "storm", "magma")], dtype=float)
        tipm = (kind == 1) & (prog > 0.72)
        ci = np.clip(fid, 0, 6) % 4
        mix = np.clip((prog - 0.72) / 0.28, 0, 1)[:, None] * 0.55
        rgb[tipm] = rgb[tipm] * (1 - mix[tipm]) + cols[ci[tipm]] * mix[tipm]
        sp = inside & (M.texel_hash(ctx, 29) > 0.96)
        rgb[sp] = (255, 255, 255)
        return rgb, np.where(inside, 255, 0), inside

    return {"pearl": pearl, "gold": gold, "helm": helm, "mask": mask, "gem": gemsh, "halo": halo, "ray": ray,
            "wing": wing, "hwing": hwing, "lwing": lwing}


# =============================================================================== animation

def build_clips():
    T = 4.0
    w = 2 * math.pi / T
    c = Clip("idle", T, loop=True)
    c.f("halo", "rotation", lambda t: [0, -360.0 * t / T, 0])
    c.f("halo", "position", lambda t: [0, 0.35 * math.sin(w * t), 0])
    for side, s in ((-1, "R"), (1, "L")):
        c.f(f"wingUpper{s}", "rotation",
            lambda t, sd=side: [0, sd * -9.0 * (0.5 + 0.5 * math.sin(w * 2 * t)), sd * 4.0 * math.sin(w * 2 * t + 0.4)])
        c.f(f"wingLower{s}", "rotation",
            lambda t, sd=side: [0, sd * -8.0 * (0.5 + 0.5 * math.sin(w * 2 * t - 0.9)), sd * -3.0 * math.sin(w * 2 * t - 0.5)])
        c.f(f"helmWing{s}", "rotation", lambda t, sd=side: [0, sd * 4.0 * math.sin(w * 2 * t), 0])
        c.f(f"ankleWing{s}", "rotation", lambda t, sd=side: [0, sd * 6.0 * math.sin(w * 2 * t + 1.0), 0])
        c.f(f"pauldronWing{s}", "rotation", lambda t, sd=side: [0, 0, sd * -3.0 * math.sin(w * 2 * t + 0.6)])
        c.f(f"stage2_ankleWing{s}", "rotation", lambda t, sd=side: [0, sd * 6.0 * math.sin(w * 2 * t + 1.0), 0])
        c.f(f"stage3_lightWing{s}", "rotation",
            lambda t, sd=side: [1.5 * math.sin(w * 2 * t + 0.2), sd * -6.0 * (0.5 + 0.5 * math.sin(w * 2 * t + 0.2)), 0])
        c.f(f"stage3_hipWing{s}", "rotation", lambda t, sd=side: [0, sd * 5.0 * math.sin(w * 2 * t + 1.6), 0])
    c.f("stage2_haloRays", "rotation", lambda t: [0, 180.0 * t / T, 0])      # 8-fold: seamless counter-spin
    c.f("stage2_haloRays", "position", lambda t: [0, 0.35 * math.sin(w * t), 0])
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
        ak.sheet_views("ascendant armor", g, rgba, glow, frame=(52, 46), scale=8.5, center=(0, 19.5)).save(
            os.path.join(ak.PREVIEW, "ascendant_views.png"))
        ak.sheet_details("ascendant armor details", g, rgba, glow).save(os.path.join(ak.PREVIEW, "ascendant_details.png"))
        ak.texture_sheet(rgba, glow).save(os.path.join(ak.PREVIEW, "ascendant_texture.png"))
        an = anims["animations"]["idle"]
        ak.sheet_anim("ascendant idle", g, rgba, glow, an, [0, 0.5, 1.0, 1.5], view=("3/4 back", 205, -12)).save(
            os.path.join(ak.PREVIEW, "ascendant_idle.png"))
        import stage_preview
        stage_preview.stage_sheet("ascendant")
    return m, geo, (rgba, glow), anims


if __name__ == "__main__":
    build(preview="--preview" in sys.argv)
