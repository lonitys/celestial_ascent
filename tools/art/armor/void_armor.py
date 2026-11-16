"""Void armor: jagged black-violet crystalline plate with magenta void cracks, floating shard pauldrons
and a shadowy hood with a crystal crest.

Run: python void_armor.py [--preview]
"""
import math
import os
import sys

import numpy as np

import armorkit as ak
import armorlib as al
import mats as M
from armorlib import Clip, fbm, hash3, worley
from common_geo import cube, sym, sym_spike, boxc, sym_boxc, cross_sprite, sym_cross_sprite

NAME = "void_armor"

VOIDP = M.pal("#040207", "#08050d", "#0d0814", "#130b1c", "#190e25", "#20122f", "#28173a", "#311c46", "#3b2254",
              "#472a63", "#553374", "#663e88")
CRACK = M.pal("#7a0c68", "#b0168f", "#e41fb8", "#ff4fd6", "#ff9cec", "#ffe0fa")
SHARD = M.pal("#0e0518", "#190a29", "#26103b", "#36164f", "#481c66", "#5e247f", "#782f9b", "#9640b8", "#b65ad2",
              "#d77fe8", "#f2b4fb")
HOOD = M.pal("#040306", "#08060c", "#0e0a14", "#150f1d", "#1c1427", "#241a32", "#2e223f")
EYE = (255, 90, 220)


# =============================================================================== geometry

def build_model():
    m = ak.new_model(NAME)
    H, B = m["armorHead"], m["armorBody"]
    RA, LA = m["armorRightArm"], m["armorLeftArm"]
    RL, LL = m["armorRightLeg"], m["armorLeftLeg"]
    RB, LB = m["armorRightBoot"], m["armorLeftBoot"]

    # ------------------------------------------------------------------ helmet: shadow hood
    cube(H, (-5, 23, -5), (10, 10, 10), "hood", shell=True)
    cube(H, (-5.5, 31.0, -6.0), (11, 2, 3), "hood", brim=True)                    # overhanging brim
    sym(H, H, (-6.0, 23.0, -6.0), (2, 9, 3), "hood", flap=True)                   # side flaps framing the face
    cube(H, (-2, 32.0, -6.4), (4, 2, 3), "hood", rot=[18, 0, 0], pivot=[0, 33, -4.9])   # front peak
    cube(H, (-5.5, 21.6, 3.6), (11, 4, 2), "hood", drape=True)                    # drape over the shoulders
    cube(H, (-3, 24.0, -5.3), (6, 3, 1), "vplate", mask=True)                     # void mask
    crest = m.bone("voidCrest", "armorHead", (0, 33.0, 0.5))
    cross_sprite(crest, (0, 32.4, -0.8), (0, 1.0, 0.45), 6, 4, "sshard")
    cross_sprite(crest, (-2.6, 32.2, 0.4), (-0.55, 1.0, 0.6), 6, 3, "sshard")
    cross_sprite(crest, (2.6, 32.2, 0.4), (0.55, 1.0, 0.6), 6, 3, "sshard")
    cross_sprite(crest, (0, 32.0, 2.6), (0, 0.55, 1.0), 5, 3, "sshard")

    # ------------------------------------------------------------------ chestplate body
    cube(B, (-4.5, 11.5, -3), (9, 13, 6), "vplate")
    cube(B, (-5.2, 17.2, -4.2), (5, 6, 2), "vplate", rot=[4, 14, 6], pivot=[-2.7, 20.2, -3.2], facet=1)   # pec shards
    cube(B, (0.2, 17.2, -4.2), (5, 6, 2), "vplate", rot=[4, -14, -6], pivot=[2.7, 20.2, -3.2], facet=2)
    cube(B, (-1.5, 18.4, -5.1), (3, 3, 1), "core", rot=[0, 0, 45], pivot=[0, 19.9, -4.6])  # void core
    cube(B, (-4.4, 13.4, -3.8), (4, 3, 1), "vplate", rot=[0, 8, -10], pivot=[-2.4, 14.9, -3.3], facet=3)
    cube(B, (0.4, 13.4, -3.8), (4, 3, 1), "vplate", rot=[0, -8, 10], pivot=[2.4, 14.9, -3.3], facet=4)
    cube(B, (-5, 12.0, -3.5), (10, 1, 7), "hood", belt=True)
    cube(B, (-4.5, 15.5, 2.6), (9, 8, 1), "vplate", facet=5)
    spines = m.bone("backSpines", "armorBody", (0, 19, 3.4))
    cross_sprite(spines, (0, 22.0, 3.0), (0, 0.8, 1.0), 6, 4, "sshard")
    cross_sprite(spines, (-2.6, 19.6, 3.0), (-0.4, 0.6, 1.0), 5, 3, "sshard")
    cross_sprite(spines, (2.6, 19.6, 3.0), (0.4, 0.6, 1.0), 5, 3, "sshard")
    cross_sprite(spines, (0, 16.4, 3.0), (0, 0.35, 1.0), 4, 3, "sshard")

    # ------------------------------------------------------------------ arms: floating shard pauldrons
    sym(RA, LA, (-8.5, 12, -2.5), (4, 12, 5), "vplate", inflate=0.25)
    sym(RA, LA, (-9.8, 21.4, -3.6), (5, 3, 7), "vplate", rot=[0, 0, 10], pivot=[-7.3, 22.9, 0], facet=6)
    sym(RA, LA, (-9.25, 11.1, -3), (5, 6, 6), "vplate", inflate=0.15, facet=7)
    sym_cross_sprite(RA, LA, (-9.0, 14.6, 0.6), (-0.5, 1.0, 0.4), 5, 3, "sshard")             # forearm fin
    for side, nm, arm in ((-1, "R", RA), (1, "L", LA)):
        sh = m.bone(f"shards{nm}", "armorRightArm" if side < 0 else "armorLeftArm", (6.8 * side, 23.0, 0))
        cx = 6.8 * side
        for k, (ang, r0, L, w, dz) in enumerate(((92, 3.0, 8, 4, 0.2), (58, 3.4, 7, 4, -1.6), (30, 3.2, 5, 3, 1.4),
                                                  (122, 3.2, 5, 3, -0.6))):
            a = math.radians(ang)
            d = np.array([math.cos(a) * side, math.sin(a), dz * 0.15])
            base = np.array([cx, 23.0, dz]) + d * r0
            cross_sprite(sh, base.tolist(), d.tolist(), L, w, "sshard", spin=20 * k, side=side)

    # ------------------------------------------------------------------ leggings
    cube(RL, (-4.025, 0, -2.5), (4, 12, 5), "vplate", inflate=0.375, side=-1)
    cube(LL, (-0.025, 0, -2.5), (4, 12, 5), "vplate", inflate=0.425, side=1)
    sym(RL, LL, (-5.0, 10.6, -3.5), (5, 1, 7), "hood", belt=True)
    sym(RL, LL, (-4.4, 5.6, -3.6), (4, 5, 1), "vplate", rot=[-9, 0, 6], pivot=[-2.4, 10.6, -3.1], facet=8)
    sym(RL, LL, (-5.4, 4.8, -2.5), (1, 6, 5), "vplate", rot=[0, 0, 9], pivot=[-4.9, 10.6, 0], facet=9)
    sym(RL, LL, (-4.3, 3.8, -3.5), (4, 3, 1), "vplate", rot=[0, 0, 45 / 3], pivot=[-2.3, 5.3, -3.0], facet=10)
    sym_cross_sprite(RL, LL, (-2.3, 5.4, -3.4), (0, 0.45, -1.0), 4, 3, "sshard")      # knee spike

    # ------------------------------------------------------------------ boots
    cube(RB, (-4.75, -0.25, -3.0), (5, 6, 6), "vplate", inflate=0.2, side=-1)
    cube(LB, (-0.25, -0.25, -3.0), (5, 6, 6), "vplate", inflate=0.25, side=1)
    sym(RB, LB, (-5.05, -0.6, -3.5), (5, 1, 7), "hood", inflate=0.05, sole=True)
    sym(RB, LB, (-4.8, 4.6, -3.6), (5, 2, 7), "vplate", rot=[0, 0, 0], facet=11)   # jagged cuff
    sym_cross_sprite(RB, LB, (-2.4, 0.4, -3.0), (0, 0.15, -1.0), 4, 3, "sshard")       # toe spike
    sym_cross_sprite(RB, LB, (-2.4, 1.2, 3.0), (0, 0.55, 1.0), 4, 3, "sshard")         # heel spur
    sym_cross_sprite(RB, LB, (-4.9, 4.4, 0.0), (-0.8, 1.0, 0.35), 4, 3, "sshard")      # ankle shard
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


def sym_horn(br, bl, base, dirs, lengths, widths, mat="shard", **params):
    """Mirrored curved horn (curve_spike) on a right/left bone pair (or the same bone twice)."""
    br.curve_spike(base, dirs, lengths, widths, mat, side=-1, **params)
    bl.curve_spike([-base[0], base[1], base[2]], [(-d[0], d[1], d[2]) for d in dirs], lengths, widths, mat,
                   side=1, **params)


def build_stage_parts(m):
    # ------------------------------------------------------------------ helmet
    # stage 2: solid obsidian void spikes along the hood brim
    hs = stage_bone(m, "stage2_hoodSpikes", "armorHead", (0, 33.0, -5.0))
    for side in (-1, 1):
        hs.spike((4.3 * side, 32.8, -4.6), (0.35 * side, 1.0, -0.3), 4, 2, "shard", segs=[0.62, 0.45], side=side)
        hs.spike((2.5 * side, 32.8, -5.0), (0.1 * side, 1.0, -0.45), 3, 2, "shard", segs=[0.67, 0.5], side=side)
    # stage 3: curved void horns sweeping out of the temples and back
    hr, hl = stage_bone(m, "stage3_hornR", "armorHead", (-5.6, 30.4, -1.2)),         stage_bone(m, "stage3_hornL", "armorHead", (5.6, 30.4, -1.2))
    sym_horn(hr, hl, (-5.6, 30.4, -1.2), [(-1.0, 0.3, 0.05), (-0.45, 1.0, 0.25), (-0.12, 0.55, 1.0),
                                         (0.0, -0.25, 1.0)], [3, 4, 3, 3], [3, 2, 2, 1], horn=True)

    # ------------------------------------------------------------------ chestplate
    # stage 2: void spikes jutting out of the pauldrons and a spike on each elbow
    sr, sl = stage_pair(m, "stage2_shoulderSpikes", "Arm", (-9.8, 22.2, 0))
    sym_spike(sr, sl, (-9.6, 22.4, -1.6), (-1.0, -0.12, -0.35), 4, 2, "shard", segs=[0.62, 0.45])
    sym_spike(sr, sl, (-9.6, 22.0, 1.7), (-1.0, -0.05, 0.4), 3, 2, "shard", segs=[0.67, 0.5])
    sym_spike(sr, sl, (-7.0, 17.6, 2.8), (-0.25, -0.35, 1.0), 4, 2, "shard", segs=[0.62, 0.45])
    # stage 3: spectral shoulder plates - ghostly layered shields hovering off the pauldrons
    gr, gl = stage_pair(m, "stage3_spectralPauldron", "Arm", (-10.4, 22.0, 0))
    sym(gr, gl, (-11.6, 20.2, -3.5), (1, 5, 7), "spectral", rot=[0, 0, 10], pivot=[-11.1, 25.2, 0])
    sym(gr, gl, (-12.9, 21.0, -2.5), (1, 3, 5), "spectral", rot=[0, 0, 18], pivot=[-12.4, 24.0, 0])

    # ------------------------------------------------------------------ leggings
    # stage 2: void spikes raking back from the outer thighs
    tr, tl = stage_pair(m, "stage2_thighSpike", "Leg", (-5.2, 8.0, 1.0))
    sym_spike(tr, tl, (-5.0, 8.2, 1.0), (-0.7, -0.25, 1.0), 4, 2, "shard", segs=[0.62, 0.45])
    # stage 3: spectral tassets hovering in front of the thighs
    fr, fl = stage_pair(m, "stage3_spectralTasset", "Leg", (-2.3, 10.4, -4.4))
    sym(fr, fl, (-4.4, 7.4, -5.2), (4, 3, 1), "spectral", rot=[-14, 0, 6], pivot=[-2.4, 10.4, -4.7])

    # ------------------------------------------------------------------ boots
    # stage 2: low void spikes along the outer sabaton
    br, bl = stage_pair(m, "stage2_bootSpikes", "Boot", (-5.0, 1.5, 0))
    sym_spike(br, bl, (-4.9, 1.4, 0.9), (-1.0, 0.2, 0.6), 3, 2, "shard", segs=[0.67, 0.5])
    sym_spike(br, bl, (-4.9, 1.5, -1.5), (-1.0, 0.3, -0.25), 3, 2, "shard", segs=[0.67, 0.5])
    # stage 3: spectral ankle guards hovering off the outer side
    ar, alb = stage_pair(m, "stage3_spectralGreave", "Boot", (-5.6, 2.6, 0))
    sym(ar, alb, (-6.6, 0.6, -2.4), (1, 4, 5), "spectral", rot=[0, 0, 6], pivot=[-6.1, 4.6, 0])


# =============================================================================== shaders

def facets(ctx, n=3, seed=0, amt=0.13):
    """Angular facet regions: random half-plane cuts across the face, each side lighter/darker."""
    v = np.zeros(ctx.N)
    edge = np.zeros(ctx.N, dtype=bool)
    for k in range(n):
        h = hash3(ctx.index, k, seed, 7 + M.FACE_ID[ctx.face])
        ang = h[0] * math.pi
        cx = hash3(ctx.index, k, seed, 11)[0] * ctx.tw
        cy = hash3(ctx.index, k, seed, 13)[0] * ctx.th
        d = (ctx.i - cx) * math.cos(ang) + (ctx.j - cy) * math.sin(ang)
        v += np.where(d > 0, amt, -amt) * (0.6 + 0.4 * hash3(ctx.index, k, seed, 17)[0])
        edge |= np.abs(d) < 0.5
    return v, edge


def make_shaders():
    def cracks(ctx, rgb, glow, density=0.55, thr=0.05, freq=0.24):
        f1, f2, _ = worley(ctx.p, freq, seed=91)
        gate = fbm(ctx.p, 0.075, 2, seed=33) > density
        d = f2 - f1
        crack = (d < thr) & gate
        core = (d < thr * 0.4) & gate
        halo = (d < thr * 2.6) & gate & ~crack
        rgb[halo] = rgb[halo] * 0.55 + CRACK[0] * 0.45
        rgb[crack] = CRACK[2]
        rgb[core] = CRACK[4]
        glow |= crack

    def glassy(ctx, base=0.42, grad=0.34):
        """Polished obsidian-crystal face: diagonal light-to-dark sweep, sharp rim light, reflection band."""
        sx = ctx.i / max(ctx.tw - 1, 1)
        sy = ctx.j / max(ctx.th - 1, 1)
        flip = hash3(ctx.index, M.FACE_ID[ctx.face], 3, 9)[0] > 0.5
        diag = (sx + sy) * 0.5 if not flip else ((1 - sx) + sy) * 0.5
        val = base + (0.5 - diag) * grad + M.face_tone(ctx, 0.12, -0.28)
        dl, dr, dt, db = M.edist(ctx)
        val += np.where(dt == 0, 0.26, 0) + np.where((dl == 0) & (dt > 0), 0.12, 0)
        val -= np.where(db == 0, 0.18, 0) + np.where((dr == 0) & (db > 0), 0.1, 0)
        band = np.abs((ctx.i + ctx.j * (1 if not flip else -1)) - (ctx.tw * 0.35 + (0 if not flip else ctx.th))) < 0.8
        val += np.where(band & (diag < 0.6), 0.16, 0)
        val += (fbm(ctx.p, 0.5, 2, 3) - 0.5) * 0.06
        val -= ctx.ao * 0.5
        return val

    def vplate(ctx):
        prm = ctx.params
        val = glassy(ctx)
        rgb = M.ramp(VOIDP, val, ctx, 0.6)
        glow = np.zeros(ctx.N, dtype=bool)
        if not prm.get("mask"):
            cracks(ctx, rgb, glow, 0.47, thr=0.055, freq=0.12)
        else:
            rgb[:] = rgb * 0.6
        return rgb, 255, glow

    def hood(ctx):
        prm = ctx.params
        x, y, z = ctx.p[:, 0], ctx.p[:, 1], ctx.p[:, 2]
        folds = np.sin(x * 1.6 + np.sin(y * 0.7) * 0.8) * 0.5 + 0.5 if ctx.face in ("north", "south") else \
            np.sin(z * 1.6 + np.sin(y * 0.7) * 0.8) * 0.5 + 0.5
        v = 0.42 + folds * 0.2 + M.vgrad(ctx, 0.2) + M.bevel(ctx, 0.16, 0.2) + M.face_tone(ctx, 0.1, -0.25)
        v += (fbm(ctx.p, 0.8, 2, 5) - 0.5) * 0.12 - ctx.ao * 0.5
        rgb = M.ramp(HOOD, v, ctx, 0.7)
        glow = np.zeros(ctx.N, dtype=bool)
        dl, dr, dt, db = M.edist(ctx)
        if prm.get("shell") and ctx.face == "north":
            # the face is lost in shadow: near-black void with two burning slanted eyes
            rgb[:] = M.ramp(HOOD, 0.08 + (y - 23) * 0.012, ctx, 0.6)
            ax = np.abs(x)
            eye = (np.abs(y - (28.0 + (ax - 1.2) * 0.35)) < 0.3) & (ax > 1.0) & (ax < 3.4)
            rgb[eye] = EYE
            glow |= eye
            hot = eye & (ax > 1.6) & (ax < 2.6)
            rgb[hot] = (255, 220, 250)
            haze = (np.abs(y - (28.0 + (ax - 1.2) * 0.35)) < 0.8) & (ax > 0.6) & (ax < 3.9) & ~eye
            rgb[haze] = rgb[haze] * 0.4 + np.array([120, 20, 110]) * 0.6
        if prm.get("brim") and ctx.face == "north":
            hem = (db == 0) & (np.abs(x) < 4.2)
            rgb[hem] = CRACK[1]
            glow |= hem
        if (prm.get("brim") or prm.get("flap")) and ctx.face == "down":
            rgb[:] = HOOD[0]
        if prm.get("drape") and ctx.face == "south":
            tatter = (db < 2) & (hash3(np.floor(x * 2), 1, 2, 3) > 0.5)
            rgb[tatter] = HOOD[1]
        if prm.get("belt") and M.side_face(ctx):
            stud = (ctx.i % 6 == 3) & (ctx.th >= 2)
            rgb[stud] = CRACK[3]
            glow |= stud
        if prm.get("sole"):
            rgb *= 0.8
        return rgb, 255, glow

    def shard(ctx):
        prm = ctx.params
        base = np.array(prm.get("spike_base", ctx.lo))
        L = max(prm.get("spike_len", 1.0), 1e-6)
        prog = np.clip((ctx.p[:, 1] - base[1]) / L, 0, 1)
        if prm.get("horn"):          # curved horn: progress along the whole horn, not per segment
            prog = prm["curve_prog0"] + prog * (prm["curve_prog1"] - prm["curve_prog0"])
        val = glassy(ctx, base=0.38 + prog * 0.25, grad=0.4)
        rgb = M.ramp(SHARD[:9], val, ctx, 0.6)
        glow = np.zeros(ctx.N, dtype=bool)
        if M.side_face(ctx) and ctx.face in ("north", "east") and ctx.tw >= 3:
            core = (ctx.i == ctx.tw // 2) & (prog > 0.2) & (prog < 0.85)
            rgb[core] = CRACK[2]
            glow |= core
        tip = (prog > 0.92) & (ctx.face != "down")
        rgb[tip] = CRACK[3]
        glow |= tip
        return rgb, 255, glow

    def core(ctx):
        dx = (ctx.s - 0.5) * 2
        dy = (ctx.t - 0.5) * 2
        r = np.maximum(np.abs(dx), np.abs(dy))
        rgb = M.ramp(CRACK, 1.0 - r * 0.7, ctx, 0.3)
        glow = np.ones(ctx.N, dtype=bool)
        if ctx.face == "north":
            pupil = r < 0.36
            rgb[pupil] = (8, 2, 12)
            glow &= ~pupil
            ring = (r > 0.36) & (r < 0.55)
            rgb[ring] = CRACK[5]
        return rgb, 255, glow

    def sshard(ctx):
        """Crossed-plane crystal shard: pointed faceted silhouette, magenta core ridge, glowing tip."""
        keep = ctx.params.get("plane")
        if ctx.face != keep:
            return np.zeros((ctx.N, 3)), np.zeros(ctx.N), np.zeros(ctx.N, dtype=bool)
        prm = ctx.params
        L = prm["spike_len"]
        base = np.array(prm["spike_base"])
        t = np.clip((ctx.p[:, 1] - base[1]) / L, 0, 1)
        u = (ctx.s - 0.5) * 2                       # -1..1 across
        half = np.where(t < 0.12, 0.55 + t / 0.12 * 0.45, 1.0 - np.clip((t - 0.12) / 0.88, 0, 1) ** 1.25)
        inside = np.abs(u) <= half + 1e-6
        left = u < 0
        val = 0.34 + t * 0.32 + np.where(left, 0.14, -0.06) - np.abs(u) * 0.1
        rgb = M.ramp(SHARD, val, ctx, 0.5)
        tw = ctx.tw
        edge = inside & (np.abs(u) > half - 2.0 / tw)
        rgb[edge & left] = SHARD[9]
        rgb[edge & ~left] = SHARD[3]
        ridge = inside & (np.abs(u) < 1.0 / tw + 1e-6) & (t > 0.15)
        rgb[ridge] = CRACK[2]
        tip = inside & (t > 0.86)
        rgb[tip] = CRACK[4]
        glow = ridge | tip
        return rgb, np.where(inside, 255, 0), glow

    def spectral(ctx):
        """Ghost plate: thin glowing rim, otherwise see-through but for faint violet facet lines."""
        dl, dr, dt, db = M.edist(ctx)
        m = np.minimum(np.minimum(dl, dr), np.minimum(dt, db))
        rim = m < 1
        f1, f2, _ = worley(ctx.p, 0.32, seed=57)
        vein = ((f2 - f1) < 0.05) & ~rim & (fbm(ctx.p, 0.3, 2, 9) > 0.42)
        rgb = np.tile(SHARD[6], (ctx.N, 1)).astype(float)
        rgb[rim] = CRACK[2]
        corner = (np.minimum(dl, dr) == 0) & (np.minimum(dt, db) == 0)
        rgb[corner] = CRACK[4]
        rgb[vein] = SHARD[8]
        speck = (M.texel_hash(ctx, 23) > 0.975) & ~rim & ~vein
        rgb[speck] = CRACK[4]
        solid = rim | vein | speck
        return rgb, np.where(solid, 255, 0), solid

    return {"vplate": vplate, "hood": hood, "shard": shard, "core": core, "sshard": sshard, "spectral": spectral}


# =============================================================================== animation

def build_clips():
    T = 3.0
    w = 2 * math.pi / T
    c = Clip("idle", T, loop=True)
    c.f("shardsR", "position", lambda t: [0, 0.6 + 0.6 * math.sin(w * t), 0])
    c.f("shardsL", "position", lambda t: [0, 0.6 + 0.6 * math.sin(w * t + math.pi), 0])
    c.f("shardsR", "rotation", lambda t: [2.5 * math.sin(w * t + 0.5), 0, 3.0 * math.sin(w * t)])
    c.f("shardsL", "rotation", lambda t: [2.5 * math.sin(w * t + 0.5 + math.pi), 0, -3.0 * math.sin(w * t + math.pi)])
    c.f("voidCrest", "scale", lambda t: [1 + 0.05 * math.sin(w * 2 * t)] * 3)
    c.f("backSpines", "position", lambda t: [0, 0, 0.25 + 0.25 * math.sin(w * t + 1.0)])
    for side, s in ((-1, "R"), (1, "L")):                      # spectral plates drift in and out
        for bone, ph in (("stage3_spectralPauldron", 0.0), ("stage3_spectralGreave", 1.6)):
            c.f(f"{bone}{s}", "position", lambda t, sd=side, p=ph: [sd * (0.35 + 0.35 * math.sin(w * t + p)), 0, 0])
        c.f(f"stage3_spectralTasset{s}", "position", lambda t: [0, 0, -0.3 - 0.3 * math.sin(w * t + 0.8)])
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
        ak.sheet_views("void armor", g, rgba, glow).save(os.path.join(ak.PREVIEW, "void_views.png"))
        ak.sheet_details("void armor details", g, rgba, glow).save(os.path.join(ak.PREVIEW, "void_details.png"))
        ak.texture_sheet(rgba, glow).save(os.path.join(ak.PREVIEW, "void_texture.png"))
        an = anims["animations"]["idle"]
        ak.sheet_anim("void idle", g, rgba, glow, an, [0, 0.75, 1.5, 2.25], view=("front", 20, -8)).save(
            os.path.join(ak.PREVIEW, "void_idle.png"))
        import stage_preview
        stage_preview.stage_sheet("void")
    return m, geo, (rgba, glow), anims


if __name__ == "__main__":
    build(preview="--preview" in sys.argv)
