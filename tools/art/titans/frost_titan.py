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
    chest.box((-7.5, 43.0, -8.6), (10, 9, 3), "ice", rot=[-3, 12, 0])           # pec plates
    chest.box((7.5, 43.0, -8.6), (10, 9, 3), "ice", rot=[-3, -12, 0])
    chest.box((0, 34.5, -8.6), (9, 10, 2), "rune")                              # solar-plexus rune
    chest.box((-8.2, 35.0, -8.5), (6, 7, 2), "ice", rot=[0, 14, 0])             # flank plates
    chest.box((8.2, 35.0, -8.5), (6, 7, 2), "ice", rot=[0, -14, 0])
    chest.box((0, 27.6, -6.7), (14, 4, 2), "ice", rot=[2, 0, 0])                # ab plate
    chest.box((0, 40.5, 8.5), (20, 12, 2), "ice")                               # back plate
    chest.spike((0, 46, 8), (0, 1.0, 0.75), 16, 5, "crystal")                   # back crystals
    chest.spike((-7, 45, 8), (-0.35, 1.0, 0.8), 11, 4, "crystal", segs=[0.6, 0.4])
    chest.spike((7, 45, 8), (0.35, 1.0, 0.8), 11, 4, "crystal", segs=[0.6, 0.4])

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
    head.spike((-4.4, 58.4, -14.2), (-0.45, 1.0, -0.28), 10, 3, "crystal", segs=[0.6, 0.4])
    head.spike((4.4, 58.4, -14.2), (0.45, 1.0, -0.28), 10, 3, "crystal", segs=[0.6, 0.4])
    head.spike((-6.0, 58.2, -8.5), (-0.85, 1.0, 0.15), 8, 3, "crystal", segs=[0.6, 0.4])
    head.spike((6.0, 58.2, -8.5), (0.85, 1.0, 0.15), 8, 3, "crystal", segs=[0.6, 0.4])

    jaw = m.bone("jaw", "head", (0, 50, -7))
    jaw.boxb(0, 45, -10.5, 11, 4, 10, "skull")
    beard = m.bone("beard", "jaw", (0, 46, -12))
    beard.spike((0, 46, -14.2), (0, -1.0, -0.16), 11, 4, "icicle", segs=[0.6, 0.4])
    beard.spike((-2.8, 46, -14.0), (-0.14, -1.0, -0.12), 8, 3, "icicle", segs=[0.6, 0.4])
    beard.spike((2.8, 46, -14.0), (0.14, -1.0, -0.12), 8, 3, "icicle", segs=[0.6, 0.4])
    beard.spike((-4.8, 46, -12.2), (-0.3, -1.0, -0.06), 6, 2, "icicle", segs=[0.6, 0.4])
    beard.spike((4.8, 46, -12.2), (0.3, -1.0, -0.06), 6, 2, "icicle", segs=[0.6, 0.4])

    for side, nm in ((-1, "right"), (1, "left")):
        s = side
        arm = m.bone(f"{nm}_arm", "chest", (15 * s, 46, 0), rotation=[-10, 0, -6 * s])
        arm.boxb(18 * s, 35, 0, 9, 13, 10, "stone")                             # upper arm
        arm.box((19.6 * s, 47, 0), (13, 7, 15), "ice", rot=[0, 0, -12 * s])     # pauldron
        arm.box((20.2 * s, 44.2, 0), (14, 2, 16), "skull", rot=[0, 0, -12 * s])  # pauldron rim
        arm.spike((20 * s, 50, 0.5), (0.35 * s, 1.0, 0.05), 19, 5, "crystal")
        arm.spike((24 * s, 48.5, -4), (1.0 * s, 0.8, -0.3), 12, 4, "crystal", segs=[0.6, 0.4])
        arm.spike((23 * s, 49, 4.5), (0.7 * s, 0.9, 0.6), 13, 4, "crystal", segs=[0.6, 0.4])
        arm.spike((16 * s, 50.5, -5), (-0.1 * s, 1.0, -0.6), 7, 3, "crystal", segs=[0.6, 0.4])
        arm.spike((24.5 * s, 42.0, -3.5), (0.15 * s, -1.0, -0.1), 5, 2, "icicle", segs=[1.0])  # rim icicles
        arm.spike((25.0 * s, 42.0, 3.0), (0.2 * s, -1.0, 0.1), 4, 2, "icicle", segs=[1.0])
        fore = m.bone(f"{nm}_forearm", f"{nm}_arm", (18 * s, 36, 0), rotation=[-8, 0, 0])
        fore.boxb(18 * s, 24, 0, 9, 13, 10, "stone")                            # forearm
        fore.boxb(18.5 * s, 26, 0, 11, 8, 12, "ice")                            # bracer
        fore.spike((23.5 * s, 30, -1), (1.0 * s, 0.3, 0.1), 6, 3, "crystal", segs=[1.0])
        fore.spike((18 * s, 35, 4.5), (0, 0.3, 1.0), 6, 3, "crystal", segs=[1.0])
        fore.boxb(18.5 * s, 12, -0.5, 12, 12, 13, "stone")                      # stone fist
        fore.box((19.3 * s, 19.5, -0.5), (12, 6, 14), "fist", rot=[0, 0, 0])    # ice gauntlet shell
        fore.box((13.0 * s, 17, -5), (3, 6, 4), "stone")                        # thumb
        for x in (22.0, 18.5, 15.0):
            fore.spike((x * s, 14.5, -6.2), (0, -0.3, -1.0), 4, 3, "crystal", segs=[1.0])

        leg = m.bone(f"{nm}_leg", "root", (6.5 * s, 21, 0))
        leg.boxb(6.5 * s, 12, 0, 10, 10, 10, "stone")                           # thigh
        leg.box((11.9 * s, 18.0, 0), (2, 7, 10), "ice", rot=[0, 0, -8 * s])     # hip guard
        shin = m.bone(f"{nm}_shin", f"{nm}_leg", (6.5 * s, 12, 0))
        shin.boxb(6.5 * s, 3, 0.5, 9, 10, 9, "stone")
        shin.box((6.5 * s, 11.6, -4.9), (8, 5, 3), "ice", rot=[-12, 0, 0])      # knee cap
        shin.box((6.5 * s, 6.5, -4.4), (8, 6, 2), "ice")                        # greave
        foot = m.bone(f"{nm}_foot", f"{nm}_shin", (6.5 * s, 3.5, 0.5))
        foot.boxb(6.5 * s, 0, -1.5, 11, 4, 14, "stone")                         # foot
        foot.box((6.5 * s, 1.5, -9.2), (10, 3, 2), "ice")                       # ice toe cap
    build_stages(m)
    return m

# =============================================================================== boss stages
# Bones named stage2_* are shown from boss stage 2 on, stage3_* only in stage 3; the renderer hides them
# by name prefix and scales them in from 0 about their pivot. They are created after every base bone so
# the base cubes keep their order (shaders hash ctx.index), and _install_stage_ao keeps them out of the
# base cubes' baked AO, so with all stage bones hidden the model looks exactly as before.

STAGE_PREFIXES = ("stage2_", "stage3_")


def is_stage_bone(bone):
    while bone is not None:
        if bone.name.startswith(STAGE_PREFIXES):
            return True
        bone = bone.model.bones.get(bone.parent) if bone.parent else None
    return False


def _install_stage_ao():
    """Stage parts are hidden in stage 1, so they must not darken the always-visible cubes. Wraps the
    shared painter's AO (a no-op for models without stage bones; installed once per process)."""
    if getattr(tl.Painter, "_stage_ao", False):
        return
    base_ao = tl.Painter._ao
    far = np.full(3, np.inf)

    def _ao(self, pw, nw, cm, face, ci, boxes):
        if not is_stage_bone(boxes[ci][0].bone):
            boxes = [b if not is_stage_bone(b[0].bone) else b[:5] + (far, far) for b in boxes]
        return base_ao(self, pw, nw, cm, face, ci, boxes)

    tl.Painter._ao = _ao
    tl.Painter._stage_ao = True


_install_stage_ao()


def box_point(center, size, rot, f):
    """Point of a box given like Bone.box(center, size, rot) at fractions f (-1..1 of each half size)."""
    R = tl.gp.rot_b(rot)
    return np.asarray(center, float) + R @ (np.asarray(size, float) / 2 * np.asarray(f, float))


def build_stages(m):
    # ---- stage 2 "Glacial Wrath": a towering ice crown and icicle-fringed pauldrons
    crown = m.bone("stage2_crown", "head", (0, 58.6, -10))
    crown.spike((0, 58.4, -7.0), (0, 1.0, 0.3), 19, 5, "glacier")                         # tall back spire
    for s in (-1, 1):
        crown.spike((4.0 * s, 58.4, -6.6), (0.45 * s, 1.0, 0.4), 15, 4, "glacier", segs=[0.6, 0.4])
        crown.spike((5.0 * s, 55.0, -11.5), (1.0 * s, 0.75, -0.05), 15, 4, "glacier", segs=[0.6, 0.4])  # temple horns
    for s, nm in ((-1, "right"), (1, "left")):
        rim = ((20.2 * s, 44.2, 0), (14, 2, 16), (0, 0, -12 * s))                         # the pauldron rim cube
        pd = m.bone(f"stage2_{nm}_pauldron", f"{nm}_arm", tuple(box_point(*rim, (0.2 * s, -1, 0))))
        for fx, fz, L, w in ((0.0, -0.8, 9, 3), (0.55, -0.75, 11, 4), (0.9, -0.15, 14, 4), (0.85, 0.55, 11, 3)):
            base = box_point(*rim, (fx * s, -0.55, fz))
            pd.spike(base, (0.12 * s, -1.0, 0.1 * fz), L, w, "glacier", segs=[0.55, 0.45], icicle=True)
    # ---- stage 3 "Absolute Zero": glacier spikes burst from the back, frozen claws, a blazing core
    gl = m.bone("stage3_glacier", "chest", (0, 40, 8.5))
    gl.spike((0, 36.5, 8.0), (0, 0.6, 1.0), 20, 7, "glacier")                             # straight back
    for s in (-1, 1):                                                                     # towering side spires
        gl.spike((7.0 * s, 40.0, 8.0), (0.5 * s, 1.0, 0.32), 32, 9, "glacier", segs=[0.42, 0.33, 0.25])
    # the solar-plexus rune cracks open into a blazing core (the only chest spot clear of the beard)
    core = m.bone("stage3_core", "chest", (0, 34.5, -9.6))
    core.box((0, 34.5, -10.0), (9, 9, 2), "core_frame", rot=[0, 0, 45])
    core.box((0, 34.5, -10.9), (6, 6, 2), "core", rot=[0, 0, 45], inflate=0.1)
    for s, nm in ((-1, "right"), (1, "left")):                                            # hooked ice talons
        cl = m.bone(f"stage3_{nm}_claws", f"{nm}_forearm", (18.5 * s, 13.0, -5.5))
        for x in (22.0, 18.5, 15.0):
            cl.curve_spike((x * s, 13.6, -5.4), [(0, -0.35, -1.0), (0, -1.0, -0.2)], [6, 8], [3, 2], "claw")

# =============================================================================== shaders


STONE = palette("#0d1124", "#131a32", "#1a2442", "#222f53", "#2b3b65", "#364978", "#43588b", "#52699e")
CRACK = palette("#1238b0", "#1f58e6", "#3a82ff", "#7cbcff", "#cfeaff")
FROST = palette("#5f7fae", "#86a8d4", "#aecdee", "#d9eeff")
ICE = palette("#1d5fb6", "#2777cf", "#3190e2", "#40a7f0", "#55bcf8", "#70cefc", "#90dcfe", "#b8ebff", "#e4f8ff")
CRYS = palette("#1a4aa3", "#1f62c2", "#2a7edc", "#389aee", "#4db4f8", "#6cc9fc", "#94dbfe", "#c4eeff", "#f4fdff")
EYE = palette("#36e8ff", "#8ff6ff", "#e8ffff")
RUNE = palette("#1aa8ff", "#45d8ff", "#9ff3ff", "#f0ffff")


def _texel_hash(ctx, seed):
    p = ctx.p
    return hash3(np.floor(p[:, 0] * 2 + 0.01), np.floor(p[:, 1] * 2 + 0.01), np.floor(p[:, 2] * 2 + 0.01), seed)


def _crack_layer(ctx, rgb, freq=0.075, seed=11, thr=0.05, density=0.6):
    p = ctx.p
    g1, g2, _ = worley(p, freq, seed)
    gate = fbm(p, 0.09, 2, seed + 4) > density
    d = (g2 - g1)
    crack = (d < thr) & gate
    core = (d < thr * 0.4) & gate
    halo = (d < thr * 2.4) & gate & ~crack
    rgb[halo] = rgb[halo] * 0.62 + np.array([24, 60, 170]) * 0.38
    rgb[crack] = CRACK[1]
    rgb[core] = CRACK[3]
    return crack


def shade_stone(ctx, skull=False):
    p = ctx.p
    n1 = fbm(p, 0.13, 3, seed=1)
    f1, f2, cid = worley(p, 0.15, seed=3)
    v = 0.5 + (n1 - 0.5) * 0.45 + (cid - 0.5) * 0.22
    seam = (f2 - f1) < 0.06
    v -= seam * 0.22
    v += (_texel_hash(ctx, 5) - 0.5) * 0.07
    v += edge_term(ctx, 0.16, 0.16, 0.05) + vgrad(ctx, 0.14) - ctx.ao * 0.6
    v += 0.1 * max(0, ctx.nw[1]) - 0.1 * max(0, -ctx.nw[1])
    rgb = ramp(STONE, v)
    # rime frost on up-facing surfaces and in patches
    rime = (fbm(p, 0.2, 3, seed=8) + max(0, ctx.nw[1]) * 0.4 - ctx.ao * 0.3) > 0.74
    rv = 0.35 + (fbm(p, 0.5, 2, 2) - 0.5) * 0.8 + edge_term(ctx, 0.3)
    rgb[rime] = ramp(FROST, rv[rime])
    glow = _crack_layer(ctx, rgb, density=0.6 if not skull else 0.7)
    if skull and ctx.face == "north":
        x, y = p[:, 0], p[:, 1]
        for ex in (-3.1, 3.1):
            dx = np.abs(x - ex)
            spill = (dx < 3.3) & (np.abs(y - 54.5) < 2.0)
            rgb[spill] = rgb[spill] * 0.5 + np.array([40, 190, 255]) * 0.5
            sock = (dx < 2.4) & (np.abs(y - 54.6) < 1.2)
            rgb[sock] = np.array([6, 10, 24])
        mouth = (np.abs(x) < 4.2) & (np.abs(y - 49.4) < 0.6)
        rgb[mouth] = np.array([6, 10, 22])
    return rgb, 255, glow


def shade_ice(ctx, fist=False):
    p = ctx.p
    side = ctx.face not in ("up", "down")
    # glassy body: lighter at the top of each face, deeper toward the bottom
    v = 0.66 - (ctx.t * 0.3 if side else 0.0) + (0.12 if ctx.face == "up" else 0.0)
    v += (fbm(p, 0.16, 3, 2) - 0.5) * 0.34
    v -= (fbm(p, 0.1, 2, 9) > 0.63) * 0.14                                   # frozen depth pockets
    # diagonal glints across the face (crisp pixel bands)
    dg = (ctx.i + ctx.j * 0.8 + (hash3(ctx.index, 0, 0, 3)[0] * 20)) % 17
    v += ((dg < 2.0) * 0.26 + ((dg >= 3) & (dg < 4)) * 0.12) * (ctx.t < 0.75)
    # rim light (fake translucency): bright top/left rim, soft inner rim
    de = np.minimum(np.minimum(ctx.i, ctx.tw - 1 - ctx.i), np.minimum(ctx.j, ctx.th - 1 - ctx.j))
    v += (de == 1) * 0.08
    v += edge_term(ctx, 0.34, 0.16, 0.03)
    f1, f2, _ = worley(p, 0.17, 21)
    frac = ((f2 - f1) < 0.04) & (fbm(p, 0.15, 2, 17) > 0.5)
    v += frac * 0.22                                                         # pale fracture lines
    v -= ctx.ao * 0.5
    rgb = ramp(ICE, v)
    sp = _texel_hash(ctx, 77) > 0.988
    rgb[sp] = np.array([255, 255, 255])
    glow = np.zeros(ctx.N, dtype=bool)
    if fist:
        g1, g2, _ = worley(p, 0.12, 41)
        c = ((g2 - g1) < 0.032) & (fbm(p, 0.2, 2, 3) > 0.42)
        rgb[c] = CRACK[2]
        glow = c
    return rgb, 255, glow


def shade_crystal(ctx, icicle=False):
    p = ctx.p
    prm = ctx.params
    base = np.array(prm["spike_base"])
    prog = np.clip((p[:, 1] - base[1]) / prm["spike_len"], 0, 1)
    v = 0.2 + prog * 0.62
    if ctx.face in ("up", "down"):
        v += 0.12
    else:
        # two-tone prism facets: left half lit, right half shaded, bright ridge between
        v += np.where(ctx.s < 0.5, 0.1, -0.06)
        v += (np.abs(ctx.s - 0.5) < 0.09) * 0.16
        v += (ctx.face in ("north", "west")) * 0.05
    v += (fbm(p, 0.3, 2, 13) - 0.5) * 0.14
    v += edge_term(ctx, 0.22, 0.05, 0.08) - ctx.ao * 0.4
    if icicle:
        v = v - prog * 0.25 + 0.12 + (np.sin(p[:, 1] * 2.6 + p[:, 0] * 2) > 0.8) * 0.1
    rgb = ramp(CRYS, v)
    tip = (prm.get("seg", 0) == prm.get("nseg", 1) - 1) & (ctx.t < 0.25) if not icicle else np.zeros(ctx.N, bool)
    rgb[tip] = ramp(CRYS, np.minimum(v[tip] + 0.25, 0.99))
    return rgb, 255, np.zeros(ctx.N, dtype=bool)


RUNE_STROKES = [
    [(0, -0.86), (0, 0.86)],
    [(-0.62, 0.9), (0, 0.4), (0.62, 0.9)],
    [(-0.62, -0.9), (0, -0.4), (0.62, -0.9)],
    [(-0.66, 0.0), (0, 0.26), (0.66, 0.0), (0, -0.26), (-0.66, 0.0)],
]


def shade_rune(ctx):
    rgb, _, _ = shade_stone(ctx)
    rgb = rgb * 0.5
    glow = np.zeros(ctx.N, dtype=bool)
    if ctx.face == "north":
        x = (ctx.s - 0.5) * 2.0
        y = (0.5 - ctx.t) * 2.0
        d = np.full(ctx.N, 9.0)
        for st in RUNE_STROKES:
            d = np.minimum(d, polyline_dist(x * 1.05, y * 1.05, st))
        core = d < 0.09
        line = d < 0.19
        halo = (d < 0.33) & ~line
        rgb[halo] = rgb[halo] * 0.35 + np.array([20, 130, 220]) * 0.65
        rgb[line] = RUNE[1]
        rgb[core] = RUNE[3]
        glow = line | halo
        fr = (ctx.i == 0) | (ctx.i == ctx.tw - 1) | (ctx.j == 0) | (ctx.j == ctx.th - 1)
        rgb[fr] = RUNE[0]
        glow |= fr
    else:
        fr = ctx.j == 0
        rgb[fr] = RUNE[0]
        glow = fr
    return rgb, 255, glow


def shade_eye(ctx):
    v = 0.4 + (ctx.face == "north") * 0.4 - (np.abs(ctx.s - 0.5) > 0.35) * 0.3
    return ramp(EYE, v), 255, True


def _spike_prog(ctx):
    """0 at the base .. 1 at the tip of a spike / curve_spike (per texel)."""
    prm = ctx.params
    seg_prog = np.clip((ctx.p[:, 1] - prm["spike_base"][1]) / prm["spike_len"], 0, 1)
    if "curve_prog0" in prm:
        return prm["curve_prog0"] + (prm["curve_prog1"] - prm["curve_prog0"]) * seg_prog
    return seg_prog


def shade_glacier(ctx):
    """Stage crystals: the faceted crystal look with a glowing cyan heart vein up the ridge and a
    blazing tip, plus faint glowing fractures in the body."""
    rgb, _, _ = shade_crystal(ctx, icicle=ctx.params.get("icicle", False))
    prm = ctx.params
    prog = _spike_prog(ctx)
    last = prm.get("seg", 0) == prm.get("nseg", 1) - 1
    side = ctx.face not in ("up", "down")
    vein = side & (np.abs(ctx.s - 0.5) < 0.11) & (prog > 0.18)
    core = vein & (np.abs(ctx.s - 0.5) < 0.05)
    g1, g2, _ = worley(ctx.p, 0.3, 57)
    frac = side & ((g2 - g1) < 0.05) & (prog < 0.75) & ~vein & (fbm(ctx.p, 0.25, 2, 58) > 0.45)
    rgb[frac] = rgb[frac] * 0.45 + CRACK[2] * 0.55
    rgb[vein] = CRACK[3]
    rgb[core] = RUNE[3]
    tip = np.zeros(ctx.N, dtype=bool)
    if last:                                    # the local +Y end of the last segment is the point
        tip = (prog > 0.84) if side else np.full(ctx.N, ctx.face == "up")
        rgb[tip] = RUNE[3] if prm.get("icicle") else RUNE[2]
    return rgb, 255, vein | frac | tip


def shade_claw(ctx):
    """Frozen talons: pale hard ice with a glowing cyan cutting edge, hottest at the point."""
    p = ctx.p
    prog = _spike_prog(ctx)
    v = 0.5 - prog * 0.12 + np.where(ctx.s < 0.5, 0.08, -0.08) + (fbm(p, 0.4, 2, 23) - 0.5) * 0.12
    v += edge_term(ctx, 0.2, 0.05, 0.08) - ctx.ao * 0.4
    rgb = ramp(CRYS, v)
    side = ctx.face not in ("up", "down")
    edge = side & (np.abs(ctx.s - 0.5) < 0.14) & (prog > 0.3)
    rgb[edge] = CRACK[3]
    point = side & (prog > 0.82)
    rgb[point] = RUNE[3]
    return rgb, 255, edge | point


def shade_core(ctx):
    """The exposed heart of absolute zero: concentric rings of blazing cyan light."""
    x = (ctx.s - 0.5) * 2
    y = (0.5 - ctx.t) * 2
    r = np.maximum(np.abs(x), np.abs(y)) if ctx.face == "north" else np.abs(x) * 0.6 + 0.4
    v = 1.0 - r * 0.75 + (_texel_hash(ctx, 91) - 0.5) * 0.08
    rgb = ramp(RUNE, v)
    ring = (np.abs(r - 0.62) < 0.07) if ctx.face == "north" else np.zeros(ctx.N, bool)
    rgb[ring] = CRACK[2]
    if ctx.face == "north":
        rgb[r < 0.22] = np.array([250, 255, 255])
    return rgb, 255, True


def shade_core_frame(ctx):
    rgb, _, _ = shade_ice(ctx)
    de = np.minimum(np.minimum(ctx.i, ctx.tw - 1 - ctx.i), np.minimum(ctx.j, ctx.th - 1 - ctx.j))
    glow = np.zeros(ctx.N, dtype=bool)
    if ctx.face == "north":
        x = (ctx.s - 0.5) * 2
        y = (0.5 - ctx.t) * 2
        r = np.maximum(np.abs(x), np.abs(y))
        halo = (r > 0.62) & (r < 0.86)
        rgb[halo] = rgb[halo] * 0.35 + CRACK[3] * 0.65
        glow = halo
    rgb[de == 0] = rgb[de == 0] * 0.8
    return rgb, 255, glow


SHADERS = {
    "stone": shade_stone,
    "skull": lambda c: shade_stone(c, skull=True),
    "ice": shade_ice,
    "fist": lambda c: shade_ice(c, fist=True),
    "crystal": shade_crystal,
    "icicle": lambda c: shade_crystal(c, icicle=True),
    "rune": shade_rune,
    "eye": shade_eye,
    # boss-stage parts
    "glacier": shade_glacier,
    "claw": shade_claw,
    "core": shade_core,
    "core_frame": shade_core_frame,
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
    c.f("right_foot", "rotation", lambda t: (24 * math.sin(ph(t)) - 32 * max(0.0, math.cos(ph(t))) ** 1.4, 0, 0))
    c.f("left_foot", "rotation", lambda t: (-24 * math.sin(ph(t)) - 32 * max(0.0, -math.cos(ph(t))) ** 1.4, 0, 0))
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
                        (0.9, (-30, 0, 4), "in3"), (1.12, (-28, 0, 4), "lin"), (1.5, (0, 0, 0), "io")])
    c.rot("right_forearm", [(0, (0, 0, 0)), (0.5, (-38, 0, 0)), (0.6, (-40, 0, 0), "lin"),
                            (0.9, (4, 0, 0), "in3"), (1.12, (2, 0, 0)), (1.5, (0, 0, 0))])
    c.rot("left_arm", [(0, (0, 0, 0)), (0.5, (-25, 0, -22)), (0.9, (-6, 0, -16), "in"), (1.15, (-6, 0, -16)),
                       (1.5, (0, 0, 0))])
    c.rot("left_forearm", [(0, (0, 0, 0)), (0.5, (-30, 0, 0)), (0.9, (-20, 0, 0), "in"), (1.5, (0, 0, 0))])
    c.rot("chest", [(0, (0, 0, 0)), (0.55, (-14, 18, -4)), (0.9, (20, -14, 4), "in3"), (1.12, (19, -12, 4)),
                    (1.5, (0, 0, 0))])
    c.rot("neck", [(0, (0, 0, 0)), (0.55, (-6, -8, 0)), (0.9, (-18, 8, 0), "in3"), (1.12, (-16, 8, 0)),
                   (1.5, (0, 0, 0))])
    c.rot("jaw", [(0, (0, 0, 0)), (0.5, (14, 0, 0)), (0.9, (26, 0, 0), "in"), (1.2, (10, 0, 0)), (1.5, (0, 0, 0))])
    c.f("chest", "rotation", lambda t: (shake(t, 22, 1.6) * env(t, 0.9, 0.92, 1.0, 1.2), 0, 0))
    c.rot("body", [(0, (0, 0, 0)), (0.55, (-4, 8, 0)), (0.9, (6, -8, 0), "in3"), (1.12, (6, -8, 0)),
                   (1.5, (0, 0, 0))])
    drop = tl.Track([(0, 0), (0.55, -1.0), (0.9, 9.0, "in3"), (1.12, 9.0), (1.5, 0, "io")])
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
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.55, (6, 0, -148 * side), "io"), (2.55, (6, 0, -148 * side)),
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
    c.rot("chest", [(0, (0, 0, 0)), (0.3, (-18, 0, 0), "out"), (1.1, (20, 0, 6), "io"), (1.7, (30, 0, 8), "in"),
                    (2.8, (30, 0, 8))])
    c.rot("neck", [(0, (0, 0, 0)), (0.3, (-26, 0, 0), "out"), (1.1, (10, 0, -8)), (1.7, (24, 0, -12), "in"),
                   (2.8, (24, 0, -12))])
    c.rot("jaw", [(0, (0, 0, 0)), (0.3, (36, 0, 0), "out"), (1.1, (18, 0, 0)), (1.7, (30, 0, 0)), (2.8, (30, 0, 0))])
    for side, nm in ((-1, "right"), (1, "left")):
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.3, (-40, 0, -50 * side), "out"), (1.1, (-14, 0, -12 * side)),
                            (1.7, (-38, 0, -8 * side), "in"), (2.8, (-38, 0, -8 * side))])
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.3, (-30, 0, 0)), (1.1, (-10, 0, 0)), (1.7, (6, 0, 0)),
                                (2.8, (6, 0, 0))])
    # knees give way, then it pitches forward onto its fists
    drop = tl.Track([(0, 0), (0.3, -0.5, "out"), (1.1, 10.0, "io"), (2.8, 10.0)])
    legs_for_drop(c, lambda t: float(drop(t)))
    c.rot("body", [(0, (0, 0, 0)), (1.1, (4, 0, 0)), (1.75, (22, 0, 0), "in"), (2.8, (22, 0, 0))])
    # shatter: limbs and head burst apart and shrink into shards
    burst = lambda t: tl.ease("out", (t - 1.9) / 0.6) if t > 1.9 else 0.0
    gone = lambda t: 1 - tl.ease("in", (t - 2.1) / 0.65) if t > 2.1 else 1.0
    c.f("right_arm", "position", lambda t: (-6 * burst(t), -2 * burst(t), -2 * burst(t)))
    c.f("left_arm", "position", lambda t: (6 * burst(t), -2 * burst(t), -2 * burst(t)))
    c.f("head", "position", lambda t: (0, 3 * burst(t), -4 * burst(t)))
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
