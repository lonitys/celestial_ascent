"""Stellar armor: midnight-navy plate scattered with tiny glowing stars, white-gold trims, a floating
star crown over the helm and small star-wings on the back.

Run: python stellar_armor.py [--preview]
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

NAME = "stellar_armor"

NAVY = M.pal("#060917", "#0a0f22", "#0e152f", "#131b3c", "#18224a", "#1e2a59", "#253468", "#2d3f78", "#374b89",
             "#43589a", "#5467ac", "#6a7cbd")
WGOLD = M.pal("#5e4618", "#7f6224", "#a08036", "#c19f4c", "#dbbd68", "#ecd58c", "#f7e8b6", "#fdf5dc", "#ffffff")
STAR = np.array([255, 248, 222])
STAR_C = np.array([214, 236, 255])
NEB_V = np.array([92, 52, 160])
NEB_T = np.array([30, 110, 150])
BLADE = M.pal("#0b1640", "#122161", "#1a3182", "#2546a3", "#3561c0", "#4f80da", "#74a2ee", "#a3c6fa", "#d6e8ff",
              "#ffffff")
VISOR = M.pal("#03050d", "#070b1c", "#0c1430", "#132049", "#1d3166")


# =============================================================================== geometry

def star_point(bone, c, r, mat="star", depth=True):
    """3D jack-shaped star: three crossed bars (reads as a 4-point star from every side)."""
    x, y, z = c
    cube(bone, (x - 0.5, y - r, z - 0.5), (1, 2 * r, 1), mat, ray=1)
    cube(bone, (x - r, y - 0.5, z - 0.5), (2 * r, 1, 1), mat, inflate=0.06, ray=1)
    if depth:
        cube(bone, (x - 0.5, y - 0.5, z - r + 0.5), (1, 1, 2 * r - 1), mat, inflate=0.12, ray=1)


def sprite_star(bone, c, size, mat="sprite", **params):
    """Two crossed zero-thickness planes carrying a 4-point star sprite (reads from every angle)."""
    x, y, z = c
    h = size / 2
    cube(bone, (x - h, y - h, z), (size, size, 0), mat, plane="north", **params)
    cube(bone, (x, y - h, z - h), (0, size, size), mat, plane="east", **params)


def build_model():
    m = ak.new_model(NAME)
    H, B = m["armorHead"], m["armorBody"]
    RA, LA = m["armorRightArm"], m["armorLeftArm"]
    RL, LL = m["armorRightLeg"], m["armorLeftLeg"]
    RB, LB = m["armorRightBoot"], m["armorLeftBoot"]

    # ------------------------------------------------------------------ helmet
    cube(H, (-5, 23, -5), (10, 10, 10), "helm")
    cube(H, (-4.5, 26.4, -5.5), (9, 3, 1), "visor")                               # starglass visor
    cube(H, (-5.4, 29.3, -5.8), (11, 1, 2), "wgold")                              # brow trim
    cube(H, (-1, 29.6, -6.3), (2, 2, 1), "gem", rot=[0, 0, 45], pivot=[0, 30.6, -5.8])  # brow star gem
    sym(H, H, (-5.9, 23.4, -4.4), (1, 6, 7), "navy", trim=("left", "right", "bottom"), cheek=True)   # cheek plates
    cube(H, (-1, 32.7, -4.6), (2, 1, 9), "wgold")                                 # crest line
    cube(H, (-5, 22.4, 4.6), (10, 3, 1), "navy", trim=("bottom",))                # neck guard
    crown = m.bone("starCrown", "armorHead", (0, 35.5, 0))
    R = 4.7
    for k in range(12):                                   # floating white-gold circlet
        a = k * 30.0
        cx, cz = R * math.sin(math.radians(a)), -R * math.cos(math.radians(a))
        cube(crown, (cx - 1.5, 35.0, cz - 0.5), (3, 1, 1), "ring", rot=[0, -a, 0], pivot=[cx, 35.5, cz])
    for k in range(6):                                    # star points riding the circlet
        a = math.radians(k * 60 + 30)
        sprite_star(crown, (round(R * math.sin(a), 3), 37.0, round(-R * math.cos(a), 3)), 3, tier=1)
    mainstar = m.bone("crownStar", "armorHead", (0, 37.2, -4.7))
    sprite_star(mainstar, (0, 37.2, -4.7), 4, tier=0)
    cube(mainstar, (-0.5, 36.7, -5.2), (1, 1, 1), "gem", rot=[45, 0, 45], pivot=[0, 37.2, -4.7], inflate=0.1)

    # ------------------------------------------------------------------ chestplate body
    cube(B, (-4.5, 11.5, -3), (9, 13, 6), "navy")
    cube(B, (-5, 16.8, -4), (10, 7, 2), "navy", trim=("top", "left", "right"), plate="breast")
    cube(B, (-1.0, 18.8, -4.7), (2, 2, 1), "gem", rot=[0, 0, 45], pivot=[0, 19.8, -4.2])  # heart star
    cube(B, (-0.5, 16.8, -4.35), (1, 6, 1), "ray")                                # star rays
    cube(B, (-3.0, 19.3, -4.35), (6, 1, 1), "ray")
    cube(B, (-4.5, 15.0, -3.5), (9, 2, 1), "navy", trim=("bottom",))
    cube(B, (-4.0, 13.3, -3.4), (8, 2, 1), "navy", trim=("bottom",))
    cube(B, (-5, 12.3, -3.6), (10, 1, 7), "wgold", band=True)                     # belt
    cube(B, (-4.5, 15.5, 2.6), (9, 8, 1), "navy", trim=("left", "right", "top"), plate="back")
    cube(B, (-1.5, 20.0, 3.3), (3, 3, 1), "wgold")                                # wing mount
    for side, nm in ((-1, "R"), (1, "L")):
        wb = m.bone(f"wing{nm}", "armorBody", (1.5 * side, 22.0, 4.6), rotation=[0, -22 * side, 0])
        x0 = 1.5 if side > 0 else -10.5
        cube(wb, (x0, 20.0, 4.6), (9, 11, 0), "wingplane", side=side)

    # ------------------------------------------------------------------ arms
    sym(RA, LA, (-8.5, 12, -2.5), (4, 12, 5), "navy", inflate=0.25)
    sym(RA, LA, (-10.0, 21.8, -4.0), (6, 3, 8), "navy", trim=("bottom", "top"), plate="pauldron")
    sym(RA, LA, (-10.4, 19.8, -4.0), (6, 2, 8), "navy", rot=[0, 0, 12], pivot=[-7.4, 21.8, 0], trim=("bottom",))
    sym(RA, LA, (-8.0, 24.8, -3.5), (1, 1, 7), "wgold", fin=True)                  # pauldron ridge
    sym(RA, LA, (-10.5, 22.3, -1.0), (1, 2, 2), "gem", rot=[45, 0, 0], pivot=[-10.0, 23.3, 0])
    sym(RA, LA, (-9.25, 11.1, -3), (5, 6, 6), "navy", inflate=0.15, trim=("top", "bottom"))
    sym(RA, LA, (-9.6, 16.4, -3.5), (5, 1, 7), "wgold", band=True, inflate=0.05)
    sym(RA, LA, (-10.0, 13.0, -1.0), (1, 2, 2), "gem", rot=[45, 0, 0], pivot=[-9.5, 14.0, 0])

    # ------------------------------------------------------------------ leggings
    cube(RL, (-4.025, 0, -2.5), (4, 12, 5), "navy", inflate=0.375, side=-1)
    cube(LL, (-0.025, 0, -2.5), (4, 12, 5), "navy", inflate=0.425, side=1)
    sym(RL, LL, (-5.0, 10.4, -3.5), (5, 2, 7), "wgold", band=True)
    sym(RL, LL, (-4.4, 5.4, -3.6), (4, 5, 1), "navy", rot=[-8, 0, 0], pivot=[-2.4, 10.4, -3.1], trim=("bottom",),
        plate="tasset")
    sym(RL, LL, (-5.4, 5.0, -2.5), (1, 5, 5), "navy", rot=[0, 0, 8], pivot=[-4.9, 10.4, 0], trim=("bottom",))
    sym(RL, LL, (-4.3, 3.8, -3.4), (4, 3, 1), "wgold")
    sym(RL, LL, (-3.0, 4.3, -4.25), (2, 2, 1), "gem", rot=[0, 0, 45], pivot=[-2.0, 5.3, -3.75])

    # ------------------------------------------------------------------ boots
    cube(RB, (-4.75, -0.25, -3.0), (5, 6, 6), "navy", inflate=0.2, side=-1)
    cube(LB, (-0.25, -0.25, -3.0), (5, 6, 6), "navy", inflate=0.25, side=1)
    sym(RB, LB, (-5.0, -0.55, -4.6), (5, 2, 3), "wgold")
    sym(RB, LB, (-5.05, -0.6, -3.5), (5, 1, 7), "navy", inflate=0.05, sole=True)
    sym(RB, LB, (-5.1, 5.2, -3.5), (5, 1, 7), "wgold", band=True, inflate=0.1)
    sym(RB, LB, (-3.5, 1.6, -3.75), (2, 3, 1), "navy", trim=("left", "right", "top"))
    sym(RB, LB, (-3.0, 2.4, -4.2), (1, 1, 1), "gem", rot=[0, 0, 45], pivot=[-2.5, 2.9, -3.7])
    for k, (y, L, ang) in enumerate(((4.0, 4, 26), (3.0, 3, 8))):
        sym(RB, LB, (-5.5, y, -0.3), (1, 1, L), "blade", rot=[ang, -16, 0], pivot=[-5.0, y + 0.5, -0.3], blade=3)
    return m


# =============================================================================== shaders

def starfield(ctx, rgb, glow, density=1.0):
    """Tiny glowing stars + soft nebula tint on navy plates (texel space, deterministic)."""
    p = ctx.p
    neb = fbm(p, 0.12, 3, seed=19)
    neb2 = fbm(p, 0.1, 2, seed=23)
    tv = np.clip((neb - 0.55) * 2.2, 0, 1)[:, None]
    tt = np.clip((neb2 - 0.58) * 2.2, 0, 1)[:, None]
    rgb[:] = rgb * (1 - 0.32 * tv) + NEB_V * 0.32 * tv
    rgb[:] = rgb * (1 - 0.25 * tt) + NEB_T * 0.25 * tt
    h = M.texel_hash(ctx, 101)
    dim = h > 1 - 0.022 * density
    rgb[dim] = rgb[dim] * 0.4 + STAR_C * 0.6
    bright = h > 1 - 0.008 * density
    rgb[bright] = STAR
    glow |= bright
    # a few 4-point sparkle stars per face (6x6 texel cells)
    if ctx.tw >= 5 and ctx.th >= 5:
        bi, bj = ctx.i // 6, ctx.j // 6
        hb = hash3(bi + ctx.index * 31, bj, 7 + M.FACE_ID[ctx.face], 77)
        ci = bi * 6 + 1 + np.floor(hash3(bi, bj, ctx.index, 3) * 4)
        cj = bj * 6 + 1 + np.floor(hash3(bi, bj, ctx.index, 4) * 4)
        on = hb > 1 - 0.32 * density
        core = on & (ctx.i == ci) & (ctx.j == cj)
        arm = on & ((np.abs(ctx.i - ci) + np.abs(ctx.j - cj)) == 1)
        rgb[arm] = rgb[arm] * 0.35 + STAR * 0.65
        rgb[core] = (255, 255, 255)
        glow |= core | arm


def make_shaders():
    def navy(ctx):
        prm = ctx.params
        extra = M.panel(ctx, 2, 12, 0.10)
        v, rgb = M.metal(ctx, NAVY, base=0.5, sheen_amt=0.1, noise=0.015, brush=0.02, extra=extra)
        glow = np.zeros(ctx.N, dtype=bool)
        starfield(ctx, rgb, glow, 0.9 if not prm.get("sole") else 0.3)
        trim = prm.get("trim")
        if trim:
            tm = M.trim_band(ctx, 2, trim) & M.side_face(ctx)
            if ctx.face == "up":
                tm |= M.emin(ctx) < 1
            gv, grgb = M.gold(ctx, WGOLD, engrave=False)
            rgb[tm] = grgb[tm]
            glow &= ~tm
        plate = prm.get("plate")
        x, y = ctx.p[:, 0], ctx.p[:, 1]
        if plate == "breast" and ctx.face == "north":
            # crescent moon inlay embracing the heart star
            r1 = np.hypot(x, y - 19.8)
            r2 = np.hypot(x - 0.9, y - 20.4)
            cres = (r1 < 3.4) & (r1 > 2.7) & (r2 > 2.9)
            gv, grgb = M.gold(ctx, WGOLD, engrave=False)
            rgb[cres] = WGOLD[7]
            glow |= cres
            orbit = (np.abs(r1 - 4.3) < 0.24) & (y > 18.0)
            rgb[orbit] = WGOLD[5]
            glow &= ~orbit | cres
        if plate == "back" and ctx.face == "south":
            # constellation: dotted lines between a few stars
            pts = [(-3.0, 22.5), (-1.4, 20.6), (0.8, 21.7), (2.6, 19.2), (1.2, 17.0), (-2.2, 17.6)]
            line = np.zeros(ctx.N, dtype=bool)
            for (ax, ay), (bx, by) in zip(pts, pts[1:]):
                d = al.seg_dist(x, y, ax, ay, bx, by)
                line |= d < 0.2
            rgb[line] = rgb[line] * 0.4 + np.array([150, 170, 230]) * 0.6
            for (ax, ay) in pts:
                s = (np.abs(x - ax) < 0.3) & (np.abs(y - ay) < 0.3)
                rgb[s] = STAR
                glow |= s
        if plate == "tasset" and ctx.face == "north":
            pass
        if prm.get("cheek") and ctx.face in ("west", "east"):
            r = np.hypot(ctx.p[:, 2] + 1.0, y - 26.4)
            ring = (np.abs(r - 2.0) < 0.26)
            rgb[ring] = WGOLD[5]
        return rgb, 255, glow

    def helm(ctx):
        v, rgb = M.metal(ctx, NAVY, base=0.5, sheen_amt=0.1, noise=0.015, brush=0.02, extra=M.panel(ctx, 2, 16, 0.1))
        glow = np.zeros(ctx.N, dtype=bool)
        starfield(ctx, rgb, glow, 0.9)
        x, y, z = ctx.p[:, 0], ctx.p[:, 1], ctx.p[:, 2]
        if ctx.face == "up":
            # white-gold star compass engraved on the dome
            ang = np.arctan2(z, x)
            r = np.hypot(x, z)
            ray = (np.abs(np.sin(ang * 2)) < 0.07 * (5 - r)) & (r < 4.2) & (r > 1.0)
            rgb[ray] = WGOLD[6]
        if M.side_face(ctx) and ctx.face != "north":
            band = np.abs(y - 29.8) < 0.26
            rgb[band] = WGOLD[5]
        return rgb, 255, glow

    def visor(ctx):
        x, y = ctx.p[:, 0], ctx.p[:, 1]
        v = 0.55 - ctx.t * 0.35 + M.bevel(ctx, 0.25, 0.1)
        rgb = M.ramp(VISOR, v, ctx, 0.6)
        glow = np.zeros(ctx.N, dtype=bool)
        if ctx.face == "north":
            # reflected galaxy streak + glowing eye line
            streak = np.abs((x * 0.35 + (y - 27.9)) ) < 0.22
            rgb[streak] = VISOR[4]
            eyes = (np.abs(y - 27.9) < 0.26) & (np.abs(np.abs(x) - 2.2) < 1.3)
            rgb[eyes] = (190, 225, 255)
            core = eyes & (np.abs(np.abs(x) - 2.2) < 0.5)
            rgb[core] = (255, 255, 255)
            glow |= eyes
            sp = M.texel_hash(ctx, 44) > 0.94
            rgb[sp & ~eyes] = (150, 170, 230)
            dl, dr, dt, db = M.edist(ctx)
            fr = (dt == 0) | (db == 0) | (dl == 0) | (dr == 0)
            rgb[fr] = WGOLD[5]
            glow &= ~fr
        return rgb, 255, glow

    def wgold(ctx):
        prm = ctx.params
        v, rgb = M.gold(ctx, WGOLD, engrave=False)
        glow = np.zeros(ctx.N, dtype=bool)
        if prm.get("band") and M.side_face(ctx) and ctx.th >= 2:
            dots = (ctx.i % 5 == 2) & (ctx.j == ctx.th // 2)
            rgb[dots] = (255, 255, 255)
            glow |= dots
        if prm.get("fin") and M.side_face(ctx):
            edge = ctx.j == 0
            rgb[edge] = WGOLD[8]
        return rgb, 255, glow

    def gem(ctx):
        return M.gem(ctx, M.pal("#4a5fb0", "#7d93dc", "#b6c8f6", "#e4ecff", "#fffaf0", "#ffffff"), shape="square",
                     base=1.0, falloff=0.5)

    def star(ctx):
        v = 0.7 + M.bevel(ctx, 0.2, 0.15)
        rgb = M.ramp(M.pal("#c9a650", "#ead18a", "#fbefc6", "#fffdf5"), v, ctx, 0.3)
        dl, dr, dt, db = M.edist(ctx)
        tip = (np.minimum(dl, dr) == 0) & ((dt == 0) | (db == 0))
        return rgb, 255, np.ones(ctx.N, dtype=bool)

    def ray(ctx):
        v = 0.75 - np.abs(ctx.s - 0.5) * 0.6 - np.abs(ctx.t - 0.5) * 0.6
        rgb = M.ramp(WGOLD, v + 0.15, ctx, 0.4)
        return rgb, 255, np.ones(ctx.N, dtype=bool)

    def blade(ctx):
        """Star-wing blade: deep blue root to white tip, cut to a pointed silhouette, glowing edges."""
        prm = ctx.params
        k = prm.get("blade", 0)
        lo, hi = ctx.lo, ctx.hi
        alpha = np.full(ctx.N, 255)
        glow = np.zeros(ctx.N, dtype=bool)
        L = hi[0] - lo[0]
        if k == 3:  # boot heel blade (along z)
            prog = (ctx.p[:, 2] - lo[2]) / max(hi[2] - lo[2], 1e-6)
        else:
            side = prm.get("side", -1)
            prog = (ctx.p[:, 0] - lo[0]) / max(L, 1e-6)
            if side < 0:
                prog = 1 - prog     # right wing grows toward -X
        prog = np.clip(prog, 0, 1)
        v = 0.25 + prog * 0.62
        rgb = M.ramp(BLADE, v, ctx, 0.6)
        if ctx.face in ("north", "south") and k != 3:
            # taper: the blade narrows to a point (cut-out above/below)
            yc = (ctx.p[:, 1] - lo[1]) / max(hi[1] - lo[1], 1e-6)
            half = 0.5 * (1 - prog ** 1.6) + 0.06
            out = np.abs(yc - 0.5) > half
            alpha[out] = 0
            edge = (np.abs(yc - 0.5) > half - 0.26) & ~out
            rgb[edge] = BLADE[8]
            glow |= edge
            core = (np.abs(yc - 0.5) < 0.2) & (prog > 0.25)
            rgb[core] = BLADE[min(9, 6 + int(2))]
            glow |= core & (prog > 0.6)
            sp = M.texel_hash(ctx, 9) > 0.93
            rgb[sp & ~out] = (255, 255, 255)
            glow |= sp & ~out
        elif ctx.face in ("up", "down", "west", "east") and k != 3:
            # thin edges: keep only near the root so the silhouette stays pointed
            alpha[prog > 0.7] = 0
            rgb[:] = BLADE[7]
            glow |= prog > 0.4
        else:
            glow |= prog > 0.55
            rgb[prog > 0.85] = BLADE[9]
        return rgb, alpha, glow

    def sprite(ctx):
        """4-point star sprite on one face of a zero-thickness plane; twin face transparent."""
        keep = ctx.params.get("plane")
        alpha = np.zeros(ctx.N)
        rgb = np.zeros((ctx.N, 3))
        glow = np.zeros(ctx.N, dtype=bool)
        if ctx.face != keep:
            return rgb, alpha, glow
        ox = np.abs(ctx.i - (ctx.tw - 1) / 2)
        oy = np.abs(ctx.j - (ctx.th - 1) / 2)
        rad = ctx.tw * 0.3
        inside = (ox <= 0.5) | (oy <= 0.5) | (ox + oy <= rad)
        dx = ox / (ctx.tw / 2)
        dy = oy / (ctx.th / 2)
        v = 1.05 - (dx + dy) * 0.6
        rgb = M.ramp(M.pal("#b48a3c", "#dcbd6c", "#f6e3a6", "#fff7dc", "#ffffff"), v, ctx, 0.3)
        core = (ox <= 0.5) & (oy <= 0.5)
        rgb[core] = (255, 255, 255)
        alpha = np.where(inside, 255, 0)
        glow = inside.copy()
        return rgb, alpha, glow

    def wingplane(ctx):
        """Star-wing on a single-face plane: three faceted blades fanning from the root."""
        side = ctx.params.get("side", -1)
        alpha = np.zeros(ctx.N)
        rgb = np.zeros((ctx.N, 3))
        glow = np.zeros(ctx.N, dtype=bool)
        if ctx.face != "south":
            return rgb, alpha, glow
        x, y = ctx.p[:, 0], ctx.p[:, 1]
        u = np.abs(x) - 1.5                      # distance out from the root
        w_ = y - 22.0                            # height relative to the root
        best_d = np.full(ctx.N, 9.0)
        best_t = np.zeros(ctx.N)
        inside = np.zeros(ctx.N, dtype=bool)
        edge = np.zeros(ctx.N, dtype=bool)
        spine = np.zeros(ctx.N, dtype=bool)
        for ang, L, W in ((72, 8.8, 1.8), (42, 10.2, 2.2), (12, 7.4, 1.8)):
            a = math.radians(ang)
            dx, dy = math.cos(a), math.sin(a)
            tt = u * dx + w_ * dy                # along the blade
            nn = -u * dy + w_ * dx               # across the blade
            prog = tt / L
            half = W * np.where(prog < 0.18, 0.45 + prog / 0.18 * 0.55, (1 - prog) / 0.82)
            ins = (prog >= 0) & (prog <= 1) & (np.abs(nn) <= half)
            e = ins & (np.abs(nn) > half - 0.55)
            sp = ins & (np.abs(nn) < 0.26) & (prog > 0.1)
            better = ins & (np.abs(nn) / np.maximum(half, 1e-3) < best_d)
            best_d = np.where(better, np.abs(nn) / np.maximum(half, 1e-3), best_d)
            best_t = np.where(better, prog, best_t)
            inside |= ins
            edge |= e
            spine |= sp
        v = 0.22 + best_t * 0.45 + (1 - best_d) * 0.12
        rgb = M.ramp(BLADE, v, ctx, 0.6)
        rgb[edge] = BLADE[7]
        rgb[spine] = WGOLD[7]
        glow = edge | spine | (inside & (best_t > 0.82))
        rgb[inside & (best_t > 0.82)] = BLADE[9]
        sp = inside & (M.texel_hash(ctx, 13) > 0.9) & ~edge
        rgb[sp] = STAR
        glow |= sp
        # root gem socket
        root = (u < 1.2) & (np.abs(w_) < 1.2)
        rgb[root & inside] = WGOLD[6]
        alpha = np.where(inside | root, 255, 0)
        glow &= alpha > 0
        return rgb, alpha, glow

    def ring(ctx):
        v, rgb = M.gold(ctx, WGOLD, engrave=False)
        glow = np.zeros(ctx.N, dtype=bool)
        if ctx.face in ("north", "south", "up"):
            line = (ctx.j == ctx.th // 2) if ctx.face != "up" else (ctx.j == ctx.th // 2)
            rgb[line] = (255, 252, 236)
            glow |= line
        return rgb, 255, glow

    return {"navy": navy, "helm": helm, "visor": visor, "wgold": wgold, "gem": gem, "star": star, "ray": ray,
            "blade": blade, "sprite": sprite, "ring": ring, "wingplane": wingplane}


# =============================================================================== animation

def build_clips():
    T = 4.0
    w = 2 * math.pi / T
    c = Clip("idle", T, loop=True)
    c.f("starCrown", "rotation", lambda t: [0, -60.0 * t / T, 0])            # 6-fold crown: seamless loop
    c.f("starCrown", "position", lambda t: [0, 0.35 * math.sin(w * t), 0])
    c.f("crownStar", "position", lambda t: [0, 0.4 * math.sin(w * t + 1.3), 0])
    c.f("crownStar", "rotation", lambda t: [0, 360.0 * t / T, 0])
    c.f("wingR", "rotation", lambda t: [0, 9.0 * (0.5 + 0.5 * math.sin(w * 2 * t)), 2.5 * math.sin(w * 2 * t + 0.5)])
    c.f("wingL", "rotation", lambda t: [0, -9.0 * (0.5 + 0.5 * math.sin(w * 2 * t)), -2.5 * math.sin(w * 2 * t + 0.5)])
    return [c]


# =============================================================================== build

def build(preview=False):
    m = build_model()
    W, H = m.pack()
    paths = al.asset_paths(NAME)
    geo = ak.export_geo(m, paths["geo"])
    print(f"{NAME}: {m.cube_count()} cubes, uv {W}x{H}, png {W * 2}x{H * 2}")
    anims = al.export_anims(build_clips(), paths["anim"])
    rgba, glow = ak.paint(m, make_shaders())
    ak.save_textures(NAME, "", rgba, glow)
    if preview:
        import geo_preview as gp
        g = gp.load_geo(geo)
        ak.sheet_views("stellar armor", g, rgba, glow).save(os.path.join(ak.PREVIEW, "stellar_views.png"))
        ak.sheet_details("stellar armor details", g, rgba, glow).save(os.path.join(ak.PREVIEW, "stellar_details.png"))
        ak.texture_sheet(rgba, glow).save(os.path.join(ak.PREVIEW, "stellar_texture.png"))
        an = anims["animations"]["idle"]
        ak.sheet_anim("stellar idle", g, rgba, glow, an, [0, 1.0, 2.0, 3.0], view=("3/4 back", 210, -14)).save(
            os.path.join(ak.PREVIEW, "stellar_idle.png"))
    return m, geo, (rgba, glow), anims


if __name__ == "__main__":
    build(preview="--preview" in sys.argv)
