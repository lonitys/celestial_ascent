"""Astral Seraph: a six-winged celestial. A floating white-gold robe with a midnight stole, a
faceless radiant mask under a cowl, a great spinning halo, and three pairs of layered wings whose
feathers fade from ivory through pale gold into a starry astral blue with luminous edges.

Run: python astral_seraph.py [--preview] [--all]
"""
import math
import sys

import numpy as np

import bosslib as tl
import bossfx as fx
import geo_preview as gp
from bosslib import Clip, env, hash3, fbm, vnoise, palette
from rig import TAU, sides, tremor

NAME = "astral_seraph"
HITBOX = (2.0, 3.2)

# =============================================================================== palettes
IVORY = palette("#2b2536", "#423a50", "#5c536a", "#787087", "#968ea4", "#b4adc0", "#d0cad8", "#e6e1ea",
                "#f5f1f2", "#fffcf6")
GOLD = palette("#2a1707", "#47290b", "#6b4211", "#916019", "#b58024", "#d4a035", "#ebbf52", "#f9dc84", "#fff4cc")
ASTRAL = palette("#04051a", "#0a0d2d", "#121846", "#1b2462", "#26347f", "#35499e", "#4b66bd", "#7390d8",
                 "#aac2f2")
PEARL = palette("#363243", "#504a61", "#6d6781", "#8e88a2", "#b0abc2", "#cfcbdd", "#e8e5f1", "#fbfaff")
RADIANT = palette("#c98a2a", "#e6b24a", "#f6d47a", "#fde9ad", "#fff6dc", "#ffffff")
STAR = np.array([236.0, 244.0, 255.0])
EDGE = np.array([178.0, 210.0, 250.0])
WARM = np.array([246.0, 226.0, 170.0])

# =============================================================================== wing layout
# a = distance along the wing arm from the root (outward), b = distance below the arm.
# phi = feather angle from hanging straight down towards the wing tip (degrees).
WINGS = {
    "upper": dict(y=35.5, z=6.0, L1=10, L2=11, fan=40, sweep=14, bend=(10, 6), sec=15.0, sec_phi=(4, 22),
                  prim=(15, 17, 18.5, 19.5, 18.5), prim_phi=(32, 48, 63, 77, 90)),
    "middle": dict(y=32.5, z=7.0, L1=11, L2=12, fan=6, sweep=18, bend=(7, 8), sec=16.0, sec_phi=(6, 24),
                   prim=(16, 18, 20, 21.5, 20.5), prim_phi=(34, 50, 64, 78, 92)),
    "lower": dict(y=29.5, z=8.0, L1=9, L2=10, fan=-30, sweep=22, bend=(6, 8), sec=12.5, sec_phi=(22, 38),
                  prim=(13, 15, 16.5, 17.5, 16.5), prim_phi=(48, 62, 75, 88, 100)),
}
WPOS = ("upper", "middle", "lower")
WING_X = 2.0

# =============================================================================== geometry helpers


def canon_pt(cfg, s, a, b, dz=0.0):
    """Canonical (pre bone-rotation) model point of wing coords (a, b)."""
    return np.array([WING_X * s + s * a, cfg["y"] - b, cfg["z"] + dz])


def feather_outline(f, n=10):
    a0, b0, phi, L, W = f
    ph = math.radians(phi)
    da, db = math.sin(ph), math.cos(ph)
    pts = []
    for k in range(n + 1):
        u = k / n
        for sgn in (-1, 1):
            hw = W / 2
            pts.append((a0 + da * u * L + sgn * db * hw, b0 + db * u * L - sgn * da * hw))
    return np.array(pts)


def band_plane(bone, cfg, s, feathers, mat, dz, tilt=0.0, margin=0.6, **params):
    """Axis-aligned hanging plane (canonical frame) covering all feathers of a band."""
    pts = np.concatenate([feather_outline(f) for f in feathers])
    amin, bmin = pts.min(0) - margin
    amax, bmax = pts.max(0) + margin
    w = int(math.ceil(amax - amin))
    h = int(math.ceil(bmax - bmin))
    ac = (amin + amax) / 2
    top = canon_pt(cfg, s, ac, bmin, dz)            # middle of the top edge
    origin = top - np.array([w / 2, h, 0.0])
    rot = None
    if tilt:
        rot = tl.euler(tl.axis_angle([1, 0, 0], -tilt))  # trailing edge swings back (+Z)
    return bone.cube(origin, (w, h, 0), mat, 0.0, top if rot else None, rot, faces=["north"],
                     side=s, x_root=WING_X * s, y_root=cfg["y"], feathers=list(feathers), **params)


def feather_plane(bone, cfg, s, f, mat, dz, **params):
    """One feather as its own plane, based at (a0, b0), pointing along phi."""
    a0, b0, phi, L, W = f
    base = canon_pt(cfg, s, a0, b0, dz)
    ph = math.radians(phi)
    d2 = (s * math.sin(ph), -math.cos(ph))
    alpha = math.degrees(math.atan2(-d2[0], d2[1]))   # +Y -> d2 about Z
    R = tl.axis_angle([0, 0, 1], alpha)
    w = int(math.ceil(W + 1))
    h = int(math.ceil(L + 0.5))
    origin = base - np.array([w / 2, 0.0, 0.0])
    return bone.cube(origin, (w, h, 0), mat, 0.0, base, tl.euler(R), faces=["north"],
                     side=s, x_root=WING_X * s, y_root=cfg["y"], feathers=[f], **params)


def build_wing(m, pos, s, nm):
    cfg = WINGS[pos]
    L1, L2 = cfg["L1"], cfg["L2"]
    rest = (0, -s * cfg["sweep"], -s * cfg["fan"])
    w = m.bone(f"wing_{pos}_{nm}", "torso", canon_pt(cfg, s, 0, 0), rotation=rest)
    # arm (leading edge with marginal coverts)
    w.box(canon_pt(cfg, s, L1 / 2 - 0.5, 0), (L1 + 1, 3, 3), "wing_arm", side=s, x_root=WING_X * s,
          band_a=L1 - 0.6)
    # secondaries: one plane, feathers lean progressively towards the tip
    n = 5 if L1 < 10 else 6
    secs = []
    for k in range(n):
        f = k / (n - 1)
        phi = cfg["sec_phi"][0] + f * (cfg["sec_phi"][1] - cfg["sec_phi"][0])
        secs.append((0.6 + f * (L1 - 1.0), 0.4, phi, cfg["sec"] * (0.80 + 0.2 * f), 6.4))
    band_plane(w, cfg, s, secs, "feather", dz=0.8, tilt=6, ast=0.5, kind="sec")
    # coverts: two staggered rows of short feathers in front
    covs = []
    nc = 4 if L1 < 10 else 5
    for k in range(nc):
        f = k / (nc - 1)
        phi = cfg["sec_phi"][0] + 4 + f * (cfg["sec_phi"][1] - cfg["sec_phi"][0])
        covs.append((0.8 + f * (L1 - 1.2), 3.0, phi, 6.4 + 1.2 * f, 4.8))
    for k in range(nc - 1):
        f = (k + 0.5) / (nc - 1)
        phi = cfg["sec_phi"][0] + 6 + f * (cfg["sec_phi"][1] - cfg["sec_phi"][0])
        covs.append((0.8 + f * (L1 - 1.2), 0.2, phi, 4.8 + 0.8 * f, 4.2))
    band_plane(w, cfg, s, covs, "covert", dz=-0.55, tilt=3, ast=9.0, kind="cov")

    bz, by = cfg["bend"]
    tip = m.bone(f"wing_{pos}_{nm}_tip", w.name, canon_pt(cfg, s, L1, 0), rotation=(0, -s * by, -s * bz))
    tip.box(canon_pt(cfg, s, L1 + L2 / 2, 0), (L2 + 1, 2, 2), "wing_arm", side=s, x_root=WING_X * s,
            band_a=L1 + 0.4)
    # primaries: individual planes fanning out from the tip arm
    prims = []
    for k in range(5):
        f = k / 4
        prims.append((L1 + 0.8 + f * (L2 - 1.4), 0.3, cfg["prim_phi"][k], cfg["prim"][k], 7.4))
    for k, f in enumerate(prims):
        feather_plane(tip, cfg, s, f, "primary", dz=0.15 + 0.17 * k, ast=0.44, kind="prim", k=k)
    # primary coverts in front of the primaries
    pc = []
    for k in range(5):
        f = k / 4
        pc.append((L1 + 0.2 + f * (L2 - 1.0), 0.6, cfg["prim_phi"][0] - 6 + f * 40, 7.0 + 1.5 * f, 4.8))
    band_plane(tip, cfg, s, pc, "covert", dz=-0.45, tilt=3, ast=9.0, kind="pcov")


def skirt_plate(bone, yaw, ax, az, y_top, size, tilt, mat, **params):
    """Robe plate hanging from the waist ellipse, facing direction yaw, flared outward by tilt."""
    by = math.radians(yaw)
    n = np.array([-math.sin(by), 0.0, -math.cos(by)])
    anchor = np.array([ax * n[0], y_top, 0.5 + az * n[2]])
    R = tl.axis_angle([0, 1, 0], yaw) @ tl.axis_angle([1, 0, 0], tilt)
    w, h, d = size
    bone.box(anchor + np.array([0, -h / 2, 0]), size, mat, rot=R, pivot=anchor, **params)
    bottom = anchor + R @ np.array([0.0, -h + 0.6, 0.0])
    return anchor, bottom


def hem_plane(bone, bottom, yaw, tilt, w, h, mat, **params):
    R = tl.axis_angle([0, 1, 0], yaw) @ tl.axis_angle([1, 0, 0], tilt)
    origin = bottom - np.array([w / 2, h, 0.0])
    return bone.cube(origin, (w, h, 0), mat, 0.0, bottom, tl.euler(R), faces=["north"], **params)


# =============================================================================== model


ROBE = [  # name, yaw, plate size, plate tilt, hem (w, h), hem tilt, tails
    ("front", 0, (11, 14, 2), 12, (11, 9), 17, 2),
    ("back", 180, (11, 15, 2), 13, (11, 10), 20, 3),
    ("right", 90, (8, 13, 2), 13, (8, 9), 19, 2),
    ("left", -90, (8, 13, 2), 13, (8, 9), 19, 2),
]
ROBE_CORNERS = [45, -45, 135, -135]
WAIST = (5.4, 4.4, 24.5)


def build_model():
    m = tl.Model(NAME)
    body = m.bone("body", "root", (0, 24, 0))
    robe = m.bone("robe", "body", (0, 24.5, 0))
    robe.boxb(0, 12, 0.5, 9, 13, 7, "robe_core")
    robe.boxb(0, 23.5, 0.5, 12, 2, 9, "belt")
    ax, az, ytop = WAIST
    for yaw in ROBE_CORNERS:
        _, bot = skirt_plate(robe, yaw, ax - 0.3, az - 0.3, ytop - 0.5, (6, 13, 2), 14, "robe")
        hem_plane(robe, bot, yaw, 20, 6, 8, "hem", tails=1, seed=yaw)
    for nm, yaw, size, tilt, (hw, hh), htilt, tails in ROBE:
        by = math.radians(yaw)
        anchor = np.array([ax * -math.sin(by), ytop, 0.5 + az * -math.cos(by)])
        b = m.bone(f"robe_{nm}", "robe", anchor)
        stole = nm == "front"
        _, bot = skirt_plate(b, yaw, ax, az, ytop, size, tilt, "robe", stole=stole)
        hem_plane(b, bot, yaw, htilt, hw, hh, "hem", tails=tails, stole=stole, seed=yaw + 7)

    torso = m.bone("torso", "body", (0, 26, 0))
    torso.boxb(0, 25, 0.5, 9, 4, 7, "robe")                                         # waist
    torso.boxb(0, 28, 0.5, 11, 8, 8, "robe")                                        # chest
    torso.box((0, 32.2, -3.8), (9, 7, 1), "breastplate", rot=[-5, 0, 0])            # breastplate
    torso.box((0, 32.0, 5.6), (6, 10, 3), "pearl")                                 # wing mount
    torso.box((0, 37.6, 4.0), (9, 5, 2), "collar", rot=[-16, 0, 0])                 # standing collar
    for s, nm in sides():
        torso.box((4.4 * s, 37.4, 0.8), (2, 4, 7), "collar", rot=[0, 0, 14 * s])
        for dx, y, w, d, ang in ((6.0, 36.3, 6, 9, 18), (7.5, 34.8, 5, 9, 30), (8.8, 33.2, 4, 8, 42)):
            torso.box((dx * s, y, 0.5), (w, 2, d), "pauldron", rot=[0, 0, ang * s])  # layered pauldron

    neck = m.bone("neck", "torso", (0, 36.5, 0.5))
    neck.boxb(0, 35.5, 0.6, 4, 4, 4, "robe")
    head = m.bone("head", "neck", (0, 38, 0))
    head.boxb(0, 37.5, 0.9, 8, 9, 8, "hood")                                        # hood
    head.boxb(0, 46.5, 1.4, 6, 1, 7, "hood")                                        # rounded crown
    head.box((0, 46.4, -3.3), (10, 2, 2), "hood_rim")                               # cowl brim
    for s, nm in sides():
        head.box((4.0 * s, 41.6, -3.3), (2, 8, 2), "hood_rim")                      # cowl lappets
    head.box((0, 42.5, -3.6), (6, 6, 2), "mask")                                    # mask
    head.box((0, 38.5, -3.6), (4, 2, 2), "mask", lower=True)                        # mask chin
    halo = m.bone("halo", "head", (0, 43.0, 5.2))
    halo.plane((0, 43.0, 5.2), 28, 28, "halo")
    halo_in = m.bone("halo_inner", "head", (0, 43.0, 5.0))
    halo_in.plane((0, 43.0, 5.0), 15, 15, "halo_inner")

    for s, nm in sides():
        arm = m.bone(f"{nm}_arm", "torso", (6.8 * s, 34.5, 0.5), rotation=[0, 0, -7 * s])
        arm.boxb(7.4 * s, 27, 0.5, 4, 8, 4, "robe")                                 # upper sleeve
        fore = m.bone(f"{nm}_forearm", f"{nm}_arm", (7.4 * s, 28, 0.5), rotation=[-38, 0, 0])
        fore.boxb(7.4 * s, 22.5, 0.5, 3, 6, 3, "robe")                              # forearm
        fore.boxb(7.4 * s, 20, 0.5, 5, 4, 5, "cuff")                                # bell cuff
        fore.box((7.4 * s, 18.6, 0.3), (3, 3, 2), "gauntlet")                       # hand
        fore.plane_from((7.4 * s, 20.4, 2.9), 5, 12, "sleeve", rot=[46, 0, 0])      # hanging sleeve

    for pos in WPOS:
        for s, nm in sides():
            build_wing(m, pos, s, nm)
    return m


# =============================================================================== shading helpers


def tone(ctx, ao=0.5):
    n = ctx.nw
    return 0.06 * max(0.0, n[1]) - 0.10 * max(0.0, -n[1]) - ctx.ao * ao


def canon_xy(ctx):
    """Plane/box point in the bone's canonical frame (cube rotation applied)."""
    c = ctx.cube
    P = ctx.p
    if c.rotation and any(abs(r) > 1e-6 for r in c.rotation):
        R = gp.rot_b(c.rotation)
        piv = np.array(c.pivot if c.pivot is not None else c.center())
        P = (P - piv) @ R.T + piv
    return P


def cloth_value(ctx, base=0.70, fold=0.09, seed=0):
    p = ctx.pw
    ang = np.arctan2(p[:, 0], p[:, 2] - 0.5)
    warp = (fbm(p * np.array([1.0, 0.22, 1.0]), 0.14, 2, seed + 3) - 0.5) * 3.0
    f = np.sin(ang * 9 + warp + p[:, 1] * 0.04)
    v = base + fold * f + 0.035 * np.sin(ang * 23 + warp * 1.7)
    v += (fbm(p, 0.3, 3, seed + 7) - 0.5) * 0.07
    v += (p[:, 1] - 22) * 0.003
    v += (hash3(ctx.i, ctx.j, np.full(ctx.N, ctx.index), seed + 11) - 0.5) * 0.025
    v += fx.bevel(ctx, 2.0, 0.05, 0.07) + tone(ctx, 0.55)
    return v


def astral_cloth(ctx, v0=0.42, seed=0, star_density=0.03):
    p = ctx.pw
    v = v0 + (fbm(p, 0.25, 3, seed + 21) - 0.5) * 0.2 + tone(ctx, 0.4)
    rgb = fx.sramp(ASTRAL, v + fx.dither(ctx, 0.04))
    st = hash3(ctx.i, ctx.j, np.full(ctx.N, ctx.index), seed + 23) < star_density
    rgb[st] = STAR
    return rgb, st


def gold_value(ctx, seed=0):
    v = 0.52 + (fbm(ctx.p, 0.4, 2, 31 + seed) - 0.5) * 0.12
    if ctx.face not in ("up", "down") and not ctx.plane:
        t = ctx.t
        v = v + 0.26 * np.exp(-((t - 0.2) / 0.16) ** 2) - 0.14 * np.exp(-((t - 0.58) / 0.13) ** 2)
    else:
        v = v + (0.12 if ctx.nw[1] > 0.5 else -0.05)
    return v + fx.bevel(ctx, 2.0, 0.28, 0.24) + tone(ctx) + 0.2 * fx.spec(ctx, 8)


def pearl_value(ctx, seed=0):
    p = ctx.pw
    v = 0.58 + (fbm(p, 0.25, 2, 5 + seed) - 0.5) * 0.1
    if ctx.face not in ("up", "down"):
        v = v + 0.18 * np.exp(-((ctx.t - 0.25) / 0.2) ** 2) - 0.08 * np.exp(-((ctx.t - 0.65) / 0.14) ** 2)
    return v + fx.bevel(ctx, 2.2, 0.22, 0.2) + tone(ctx) + 0.22 * fx.spec(ctx, 6)


def pearl_rgb(ctx, v):
    rgb = fx.sramp(PEARL, v + fx.dither(ctx, 0.04))
    p = ctx.pw
    irid = 0.5 + 0.5 * np.sin(p[:, 0] * 0.35 + p[:, 1] * 0.22 + ctx.nw[0] * 2.0 + ctx.nw[2] * 1.3)
    tint = fx.mix(np.array([0.97, 0.97, 1.05]), np.array([1.05, 1.0, 0.92]), irid)
    return rgb * tint


def gold_line(ctx, inset=2):
    return fx.edge_dist(ctx) == inset


# =============================================================================== shaders


def shade_robe(ctx):
    v = cloth_value(ctx)
    rgb = fx.sramp(IVORY, v + fx.dither(ctx, 0.03))
    glow = np.zeros(ctx.N, dtype=bool)
    if ctx.params.get("stole") and ctx.nw[2] < -0.5:
        x = ctx.pw[:, 0]
        st = np.abs(x) < 2.0
        if st.any():
            a, sg = astral_cloth(ctx)
            rgb[st] = a[st]
            glow |= st & sg
            edge = (np.abs(x) >= 2.0) & (np.abs(x) < 2.55)
            rgb[edge] = fx.sramp(GOLD, 0.62 + 0.15 * fx.spec(ctx, 4) + fx.dither(ctx, 0.05))[edge]
    return rgb, 255, glow


def shade_robe_core(ctx):
    v = cloth_value(ctx, base=0.55)
    if ctx.face == "down":
        v = v - 0.18
    return fx.sramp(IVORY, v + fx.dither(ctx, 0.03)), 255, False


def shade_hem(ctx):
    """Hanging hem tail (plane): flowing pointed tails with an embroidered gold border."""
    s, t = ctx.s, ctx.t
    tails = ctx.params.get("tails", 2)
    seed = ctx.params.get("seed", 0)
    w = np.mod(s * tails, 1.0)
    k = np.floor(s * tails)
    tri = np.abs(w - 0.5) * 2
    jit = (hash3(k, k * 0 + 1, k * 0 + 3, seed) - 0.5) * 0.1
    bound = 1.0 - (0.42 + jit) * tri ** 1.2 - 0.03 * np.sin(s * 23 + seed)
    inside = t <= bound
    # distance (texels) to the cut boundary along t
    dpx = (bound - t) * ctx.th
    v = cloth_value(ctx, base=0.68)
    v -= 0.08 * fx.smoothstep(0.4, 1.0, t)
    rgb = fx.sramp(IVORY, v + fx.dither(ctx, 0.03))
    glow = np.zeros(ctx.N, dtype=bool)
    if ctx.params.get("stole"):
        x = ctx.pw[:, 0]
        st = np.abs(x) < 2.0 * (1 - 0.5 * fx.smoothstep(0.6, 1.0, t))
        a, sg = astral_cloth(ctx)
        rgb[st] = a[st]
        glow |= st & sg
    border = (dpx >= 0.0) & (dpx < 2.0)
    inner = (dpx >= 3.2) & (dpx < 4.0)
    g = fx.sramp(GOLD, 0.68 - 0.12 * (dpx < 1.0) + fx.dither(ctx, 0.04))
    rgb[border] = g[border]
    rgb[inner] = g[inner] * 0.9
    return rgb, np.where(inside, 255, 0), glow


def shade_belt(ctx):
    v = gold_value(ctx)
    rgb = fx.sramp(GOLD, v + fx.dither(ctx, 0.05))
    glow = np.zeros(ctx.N, dtype=bool)
    if ctx.face in ("north", "south", "east", "west"):
        mid = (ctx.j >= 1) & (ctx.j <= ctx.th - 2)
        a = ctx.i.astype(float)
        m, _ = fx.runes(a + ctx.index * 7, (ctx.j - 1).astype(float), cell=3.2, seed=4, density=0.45, stroke=0.45)
        inset = mid & (fx.edge_dist(ctx) >= 1)
        rgb[inset] = fx.sramp(ASTRAL, 0.3 + fx.dither(ctx, 0.05))[inset]
        r = inset & m
        rgb[r] = np.array([255, 236, 180.0])
        glow |= r
    return rgb, 255, glow


def shade_pearl(ctx):
    v = pearl_value(ctx)
    rgb = pearl_rgb(ctx, v)
    gl = gold_line(ctx, 2) if min(ctx.tw, ctx.th) >= 8 else np.zeros(ctx.N, dtype=bool)
    rgb[gl] = fx.sramp(GOLD, 0.7 + fx.dither(ctx, 0.05))[gl]
    return rgb, 255, False


def shade_breastplate(ctx):
    v = pearl_value(ctx)
    rgb = pearl_rgb(ctx, v)
    if ctx.face == "north":
        x, y = fx.plane_xy(ctx)
        y = y - 0.05
        r = np.sqrt((x * 1.25) ** 2 + y ** 2)
        a = np.arctan2(y, x)
        ring = np.abs(r - 0.36) < 0.08
        ray_w = 0.16 * (1 - (r - 0.46) / 0.5)
        rays = (r > 0.46) & (r < 0.96) & (np.abs(np.mod(a * 8 / TAU + 0.5, 1) - 0.5) < ray_w)
        core = r < 0.24
        gm = ring | rays
        rgb[gm] = fx.sramp(GOLD, 0.74 - 0.18 * r + fx.dither(ctx, 0.05))[gm]
        rgb[core] = fx.sramp(RADIANT, 0.85 - r * 1.6 + fx.dither(ctx, 0.05))[core]
        return rgb, 255, core
    return rgb, 255, False


def shade_hood_rim(ctx):
    """Cowl edge framing the mask: ivory cloth with a gold piped edge on the mask side."""
    v = cloth_value(ctx, base=0.74, fold=0.04, seed=6)
    rgb = fx.sramp(IVORY, v + fx.dither(ctx, 0.03))
    if ctx.face == "north":
        d = fx.edge_dist(ctx)
        pipe = d == 0
        rgb[pipe] = fx.sramp(GOLD, gold_value(ctx) + fx.dither(ctx, 0.05))[pipe]
    elif ctx.face == "south":
        rgb = rgb * 0.7
    return rgb, 255, False


def shade_collar(ctx):
    v = pearl_value(ctx)
    rgb = pearl_rgb(ctx, v)
    d = fx.edge_dist(ctx)
    rim = d <= 1
    rgb[rim] = fx.sramp(GOLD, gold_value(ctx) + fx.dither(ctx, 0.05))[rim]
    return rgb, 255, False


def shade_pauldron(ctx):
    v = pearl_value(ctx)
    rgb = pearl_rgb(ctx, v)
    if ctx.face == "up":
        # overlapping scale-plates (feather-like) on the top face
        q = ctx.j + (np.mod(np.floor(ctx.i / 4), 2) * 2)
        cres = np.mod(q, 4) == 3
        rgb[cres] = rgb[cres] * 0.86
        return rgb, 255, False
    if ctx.face == "down":
        rim = np.ones(ctx.N, dtype=bool)
    else:
        rim = ctx.j >= ctx.th - 1                  # gold piping only on the lower edge of each lame
    rgb[rim] = fx.sramp(GOLD, 0.6 + 0.2 * fx.spec(ctx, 4) + fx.dither(ctx, 0.05))[rim]
    return rgb, 255, False


def shade_gauntlet(ctx):
    """Pearl glove with a gold band at the wrist and gold knuckle studs."""
    v = pearl_value(ctx) + 0.04
    rgb = pearl_rgb(ctx, v)
    if ctx.face not in ("up", "down"):
        band = ctx.t < 0.3
        rgb[band] = fx.sramp(GOLD, gold_value(ctx) + fx.dither(ctx, 0.05))[band]
        stud = (np.abs(ctx.t - 0.62) < 0.1) & (np.mod(ctx.i, 3) == 1)
        rgb[stud] = GOLD[6]
    elif ctx.face == "up":
        rgb = fx.sramp(GOLD, gold_value(ctx) + fx.dither(ctx, 0.05))
    return rgb, 255, False


def shade_cuff(ctx):
    v = cloth_value(ctx, base=0.70)
    rgb = fx.sramp(IVORY, v + fx.dither(ctx, 0.03))
    glow = np.zeros(ctx.N, dtype=bool)
    if ctx.face == "down":
        a, sg = astral_cloth(ctx, 0.3)
        rgb = a
        glow = sg
    elif ctx.face != "up":
        g = ctx.t > 0.72
        rgb[g] = fx.sramp(GOLD, 0.6 + 0.2 * (1 - ctx.t) + fx.dither(ctx, 0.05))[g]
    return rgb, 255, glow


def shade_sleeve(ctx):
    """Hanging bell sleeve (plane): tapered tail, ivory outside with astral lining showing at the edge."""
    x, y = fx.plane_xy(ctx)
    t = ctx.t
    half = 1.0 - 0.75 * fx.smoothstep(0.35, 1.0, t)
    inside = np.abs(x) <= half
    v = cloth_value(ctx, base=0.66) - 0.06 * t
    rgb = fx.sramp(IVORY, v + fx.dither(ctx, 0.03))
    dpx = (half - np.abs(x)) * ctx.tw / 2
    edge = dpx < 1.0
    rgb[edge] = fx.sramp(GOLD, 0.64 + fx.dither(ctx, 0.05))[edge]
    return rgb, np.where(inside, 255, 0), False


def shade_hood(ctx):
    v = cloth_value(ctx, base=0.72, fold=0.05, seed=4)
    rgb = fx.sramp(IVORY, v + fx.dither(ctx, 0.03))
    if ctx.face == "north":
        rgb = rgb * 0.62          # the inside of the cowl, in shadow behind the mask
    elif ctx.face in ("east", "west", "south"):
        p = ctx.pw
        hem = (p[:, 1] < 38.6) & (p[:, 1] > 37.7)                     # gold hem where the hood meets the collar
        seam = (ctx.face == "south") & (np.abs(p[:, 0]) < 0.3)       # centre seam down the back
        g = fx.sramp(GOLD, 0.62 + 0.18 * fx.spec(ctx, 4) + fx.dither(ctx, 0.05))
        rgb[hem] = g[hem]
        rgb[seam] = fx.mix(rgb[seam], g[seam], 0.7)
    return rgb, 255, False


def shade_mask(ctx):
    if ctx.face != "north":
        v = pearl_value(ctx) + 0.05
        return pearl_rgb(ctx, v), 255, False
    # one continuous oval across the main plate and the chin plate (world-space coordinates)
    x = ctx.pw[:, 0] / 3.0
    y = (ctx.pw[:, 1] - 42.0) / 4.2
    r = np.sqrt((x * 1.05) ** 2 + (y - 0.08) ** 2)
    # faceless: a smooth convex oval, white-hot at the centre, cooling to gold at the rim,
    # with only a fine centre seam and a brow star
    v = 1.0 - 0.62 * np.clip(r, 0, 1.3) ** 1.6
    seam = (np.abs(x) < 0.045) & (y < 0.3) & (y > -0.8)
    v = np.where(seam, v - 0.2, v)
    rgb = fx.sramp(RADIANT, v + fx.dither(ctx, 0.04))
    sx, sy = x, y - 0.52
    star = (np.abs(sx) * 3.4 + np.abs(sy) < 0.3) | (np.abs(sx) + np.abs(sy) * 3.4 < 0.3)
    rgb[star] = np.array([255, 255, 255.0])
    glow = v > 0.5
    cool = ~glow
    rgb[cool] = fx.sramp(GOLD, 0.62 + 0.4 * (v[cool] - 0.3) + fx.dither(ctx, 0.04)[cool])
    return rgb, 255, glow


def shade_halo(ctx):
    x, y = fx.plane_xy(ctx)
    r = np.sqrt(x * x + y * y)
    a = np.mod(np.arctan2(y, x), TAU)
    R = ctx.tw / 2.0                                 # radius in texels
    sec = TAU / 12
    la = np.mod(a, sec) / sec                        # 0..1 inside each 30 degree sector
    dmaj = np.minimum(la, 1 - la) * sec * r * R      # texel distance (arc) to the nearest major ray axis
    dmin = np.abs(la - 0.5) * sec * r * R            # ... to the nearest minor ray axis
    ring = (r > 0.70) & (r < 0.80)
    # 12 long sun rays on the sector edges, 12 short ones between them (12-fold symmetric)
    major = (r >= 0.76) & (r < 1.0) & (dmaj < 2.4 * (1.0 - (r - 0.76) / 0.24))
    minor = (r >= 0.76) & (r < 0.9) & (dmin < 1.6 * (1.0 - (r - 0.76) / 0.14))
    band_lo, band_hi = 0.46, 0.60
    band = (r >= band_lo) & (r <= band_hi)
    lip = band & ((r < band_lo + 0.035) | (r > band_hi - 0.035))
    # glyph band: a radial bar on every ray axis and a lozenge between (24 marks)
    rb = (r - band_lo) / (band_hi - band_lo)
    bar = band & ~lip & (dmaj < 0.75) & (rb > 0.22) & (rb < 0.78)
    loz = band & ~lip & (dmin / 1.6 + np.abs(rb - 0.5) / 0.3 < 1.0)
    spokes = (r > band_hi) & (r < 0.71) & (dmaj < 0.7)
    shape = ring | major | minor | band | spokes
    v = 0.62 + 0.3 * (1 - np.abs(r - 0.75) / 0.06).clip(0, 1)
    v = v + 0.22 * (major | minor) * (1 - (r - 0.76) / 0.24).clip(0, 1)
    rgb = fx.sramp(RADIANT, v + fx.dither(ctx, 0.04))
    inner = band & ~lip
    rgb[inner] = fx.sramp(GOLD, 0.4 + fx.dither(ctx, 0.04))[inner]
    rgb[lip] = RADIANT[3]
    rgb[bar | loz] = np.array([255, 250, 230.0])
    return rgb, np.where(shape, 255, 0), shape


def shade_halo_inner(ctx):
    x, y = fx.plane_xy(ctx)
    r = np.sqrt(x * x + y * y)
    a = np.mod(np.arctan2(y, x), TAU)
    R = ctx.tw / 2.0
    sec = TAU / 8
    la = np.mod(a + sec / 2, sec) / sec
    dn = np.abs(la - 0.5) * sec * r * R        # texel arc distance to the 8 node axes
    ring = (r > 0.8) & (r < 0.9)
    dia = (np.abs(r - 0.85) * R / 2.6 + dn / 2.2) < 1.0
    shape = ring | dia
    rgb = fx.sramp(RADIANT, 0.66 + 0.34 * dia + fx.dither(ctx, 0.04))
    return rgb, np.where(shape, 255, 0), shape


def shade_wing_arm(ctx):
    """Leading edge: small overlapping marginal coverts with a gold band at the wrist."""
    s = ctx.params["side"]
    P = canon_xy(ctx)
    a = (P[:, 0] - ctx.params["x_root"]) * s
    yy = P[:, 1]
    row = np.floor(yy * 1.6)
    q = a * 1.4 + np.mod(row, 2) * 0.5
    fu = np.mod(q, 1.0)
    fv = np.mod(yy * 1.6, 1.0)
    scale = np.sqrt((fu - 0.5) ** 2 + (fv - 0.15) ** 2 * 0.6)
    v = 0.80 - 0.16 * fx.smoothstep(0.3, 0.55, scale) + (fbm(P, 0.6, 2, 61) - 0.5) * 0.06
    v += tone(ctx, 0.45) + fx.bevel(ctx, 1.5, 0.06, 0.06)
    if ctx.face == "down":
        v = v - 0.12
    rgb = fx.sramp(IVORY, v + fx.dither(ctx, 0.03))
    band = np.abs(a - ctx.params["band_a"]) < 0.75
    rgb[band] = fx.sramp(GOLD, gold_value(ctx) + fx.dither(ctx, 0.05))[band]
    return rgb, 255, False


def _profile(u, kind):
    rise = np.clip(u / 0.12, 0, 1) ** 0.6
    if kind == "prim":
        tt = np.clip((u - 0.56) / 0.44, 0, 1)
        tip = np.clip(1 - tt ** 2.0, 0, 1) ** 0.62
    elif kind in ("cov", "pcov"):
        tt = np.clip((u - 0.5) / 0.5, 0, 1)
        tip = np.sqrt(np.clip(1 - tt ** 2, 0, 1))
    else:
        tt = np.clip((u - 0.6) / 0.4, 0, 1)
        tip = np.clip(1 - tt ** 2.4, 0, 1) ** 0.55
    return (0.3 + 0.7 * rise) * tip


def shade_feathers(ctx):
    """Cutout feathers painted in the wing's canonical frame. Each feather fades from ivory through
    pale gold into a starry astral blue with a luminous edge."""
    pr = ctx.params
    s = pr["side"]
    kind = pr["kind"]
    P = canon_xy(ctx)
    a = (P[:, 0] - pr["x_root"]) * s
    b = pr["y_root"] - P[:, 1]
    N = ctx.N
    top = np.full(N, -1)
    U = np.zeros(N)
    V = np.zeros(N)
    HW = np.ones(N)
    LK = np.ones(N)
    rec = []
    feathers = pr["feathers"]
    nf = len(feathers)
    for k, (a0, b0, phi, L, W) in enumerate(feathers):
        ph = math.radians(phi)
        da, db = math.sin(ph), math.cos(ph)
        qa, qb = a - a0, b - b0
        u = (qa * da + qb * db) / L
        v = qa * db - qb * da                       # > 0 towards the leading (outer) side
        hw = 0.5 * W * _profile(u, kind)
        hw = np.where(v > 0, hw * (0.78 if kind == "prim" else 0.92), hw)
        inside = (u >= 0) & (u <= 1) & (np.abs(v) <= hw)
        top = np.where(inside, k, top)
        U = np.where(inside, u, U)
        V = np.where(inside, v, V)
        HW = np.where(inside, hw, HW)
        LK = np.where(inside, L, LK)
        rec.append((u, v, hw))
    has = top >= 0
    shadow = np.zeros(N, dtype=bool)
    for k, (u, v, hw) in enumerate(rec):
        shadow |= has & (top < k) & (u > 0.0) & (u < 1.02) & (np.abs(v) > hw) & (np.abs(v) < hw + 1.0)
    vn = np.abs(V) / np.maximum(HW, 1e-3)
    ed = np.minimum(HW - np.abs(V), (1 - U) * LK * 0.7)
    fid = np.where(has, top, 0) + ctx.index * 17
    jit = hash3(fid, fid * 0 + 5, fid * 0 + 9, 77) - 0.5
    # barbs (chevrons pointing to the tip) and vane splits
    barb_ph = U * LK - np.abs(V) * 1.5
    barb = np.cos(TAU * barb_ph / 1.25)
    split = np.zeros(N, dtype=bool)
    if kind in ("sec", "prim"):
        for kk in range(2):
            hs = hash3(fid, fid * 0 + 11 + kk, fid * 0, 79)
            us = (0.42 + 0.4 * hash3(fid, fid * 0 + 13 + kk, fid * 0, 81)) * LK
            sgn = np.where(hash3(fid, fid * 0 + 17 + kk, fid * 0, 83) < 0.5, -1.0, 1.0)
            split |= (hs < 0.55) & (np.abs(barb_ph - us) < 0.3) & (vn > 0.45) & (np.sign(V) == sgn)
    # vane: lit leading half, softly shaded trailing half (a crease along the shaft, no hard line)
    crease = np.where(V > 0, 0.05 * (1 - vn), -0.06 * (1 - vn) ** 2)
    val = 0.86 + 0.07 * (1 - vn ** 2) + crease + 0.025 * barb + jit * 0.05
    val -= 0.2 * (1 - fx.smoothstep(0.0, 0.3, U)) * (kind in ("sec", "prim"))
    val -= 0.14 * shadow
    val -= 0.11 * (ed < 0.5)
    val += tone(ctx, 0.6)
    if kind in ("cov", "pcov"):
        val += 0.0 - 0.08 * fx.smoothstep(0.55, 1.0, U) * (1 - vn)
    ivory = fx.sramp(IVORY, val + fx.dither(ctx, 0.03))
    u0 = pr.get("ast", 9.0) + jit * 0.1
    ta = fx.smoothstep(u0, u0 + 0.42, U)
    glow = np.zeros(N, dtype=bool)
    rgb = ivory
    if (ta > 0).any():
        warm = fx.mix(ivory, ivory * (WARM / 245.0), fx.smoothstep(0.0, 0.25, ta) * 0.6)
        av = 0.52 + 0.2 * (1 - vn ** 2) + crease - 0.3 * fx.smoothstep(u0 + 0.25, 1.0, U) + 0.03 * barb + jit * 0.08
        av -= 0.15 * shadow + ctx.ao * 0.3
        ast = fx.sramp(ASTRAL, av + fx.dither(ctx, 0.05))
        shade = (val - 0.86)[:, None]
        lil = np.array([206, 196, 240.0]) * (1.0 + shade)
        peri = np.array([128, 146, 222.0]) * (1.0 + shade)
        k1 = fx.smoothstep(0.12, 0.4, ta)
        k2 = fx.smoothstep(0.32, 0.6, ta)
        k3 = fx.smoothstep(0.5, 0.88, ta)
        rgb = fx.mix(fx.mix(fx.mix(warm, lil, k1), peri, k2), ast, k3)
        deep = ta > 0.6
        st = deep & (ed > 0.7) & (hash3(ctx.i, ctx.j, np.full(N, ctx.index), 91) < 0.026)
        rgb[st] = STAR
        rim = (ed < 0.5) & (ta > 0.66) & has
        rgb[rim] = EDGE
        glow = st | rim
    # faint warm shaft: a tint, not a stripe
    rach = (np.abs(V) < 0.24) & (U < 0.9) & has
    rgb[rach] = fx.mix(rgb[rach], fx.sramp(GOLD, 0.82 - 0.1 * ta[rach]), 0.45)
    alpha = np.where(has & ~split, 255, 0)
    return rgb, alpha, glow & has


SHADERS = {
    "robe": shade_robe,
    "robe_core": shade_robe_core,
    "hem": shade_hem,
    "belt": shade_belt,
    "pearl": shade_pearl,
    "breastplate": shade_breastplate,
    "collar": shade_collar,
    "pauldron": shade_pauldron,
    "gauntlet": shade_gauntlet,
    "cuff": shade_cuff,
    "sleeve": shade_sleeve,
    "hood": shade_hood,
    "hood_rim": shade_hood_rim,
    "mask": shade_mask,
    "halo": shade_halo,
    "halo_inner": shade_halo_inner,
    "wing_arm": shade_wing_arm,
    "feather": shade_feathers,
    "covert": shade_feathers,
    "primary": shade_feathers,
}

# =============================================================================== animations
# Wing rotations are written in right-wing semantics (twist, back, up):
#   twist > 0 pitches the trailing edge back, back > 0 sweeps the wing back, up > 0 raises it.


def mw(v, s):
    return (v[0], -s * v[1], -s * v[2])


def wing_f(c, pos, fn, tip_fn=None):
    for s, nm in sides():
        c.f(f"wing_{pos}_{nm}", "rotation", lambda t, s=s: mw(fn(t), s))
        if tip_fn is not None:
            c.f(f"wing_{pos}_{nm}_tip", "rotation", lambda t, s=s: mw(tip_fn(t), s))


def wing_k(c, pos, keys, tip_keys=None):
    for s, nm in sides():
        c.rot(f"wing_{pos}_{nm}", [(k[0], mw(k[1], s)) + tuple(k[2:]) for k in keys])
        if tip_keys:
            c.rot(f"wing_{pos}_{nm}_tip", [(k[0], mw(k[1], s)) + tuple(k[2:]) for k in tip_keys])


def halo_spin(c, L, outer_deg, inner_deg, e="lin"):
    """outer_deg must be a multiple of 30 (12-fold halo), inner_deg of 45 (8-fold ring)."""
    c.rot("halo", [(0, (0, 0, 0)), (L, (0, 0, outer_deg), e)])
    c.rot("halo_inner", [(0, (0, 0, 0)), (L, (0, 0, inner_deg), e)])


def breath(c, L, n_breath=1, amp=1.0, bob=1.0, n_bob=None):
    """Gentle hover + wing breathing that any clip can layer (whole periods over L)."""
    w = TAU * n_breath / L
    nb = n_bob or n_breath * 2
    wb = TAU * nb / L
    c.f("body", "position", lambda t: (0, bob * math.sin(wb * t), 0))
    for k, pos in enumerate(WPOS):
        ph = -0.55 * k
        wing_f(c, pos, lambda t, ph=ph: (0, -5 * amp * math.sin(w * t + ph + 0.8), 4 * amp * math.sin(w * t + ph)),
               lambda t, ph=ph: (0, -3 * amp * math.sin(w * t + ph), 3 * amp * math.sin(w * t + ph - 0.7)))
    for k, nm in enumerate(("front", "right", "back", "left")):
        c.f(f"robe_{nm}", "rotation", lambda t, k=k: (2.0 * amp * math.sin(wb * t + k * 1.3 + 0.6), 0,
                                                       1.2 * amp * math.sin(wb * t + k * 1.7)))


def anim_idle():
    T = 4.0
    c = Clip("idle", T, loop=True)
    w = TAU / T
    breath(c, T, 1, 1.0, 1.0)
    c.f("body", "rotation", lambda t: (1.2 * math.sin(w * t + 0.4), 0, 0.8 * math.sin(w * t)))
    c.f("torso", "rotation", lambda t: (1.0 * math.sin(w * t + 1.2), 0, 0))
    c.f("neck", "rotation", lambda t: (-1.0 * math.sin(w * t + 1.6), 0, 0))
    for s, nm in sides():
        c.f(f"{nm}_arm", "rotation", lambda t, s=s: (2.0 * math.sin(w * t + 0.8), 0, -s * 1.8 * math.sin(w * t + 0.3)))
        c.f(f"{nm}_forearm", "rotation", lambda t: (-3.0 * math.sin(w * t + 1.1), 0, 0))
    c.f("halo", "position", lambda t: (0, 0.35 * math.sin(w * t + 1.0), 0))
    halo_spin(c, T, 30, -45)
    return c


def anim_fly():
    T = 1.4
    c = Clip("fly", T, loop=True)
    w = TAU / T
    for k, pos in enumerate(WPOS):
        ph = -0.75 * k
        A = (22, 20, 16)[k]
        B = (16, 15, 12)[k]
        wing_f(c, pos, lambda t, ph=ph, A=A, B=B: (9 * math.sin(w * t + ph), 6 - B * math.sin(w * t + ph),
                                                   4 + A * math.cos(w * t + ph)),
               lambda t, ph=ph, A=A: (0, -10 * math.sin(w * t + ph - 0.8), 0.6 * A * math.cos(w * t + ph - 0.8)))
    c.f("body", "position", lambda t: (0, -1.4 * math.cos(w * t - 0.75), 0.6 * math.sin(w * t)))
    c.f("body", "rotation", lambda t: (11 + 2.0 * math.sin(w * t - 0.4), 0, 0))
    c.f("torso", "rotation", lambda t: (3 + 1.5 * math.sin(w * t - 1.0), 0, 0))
    c.f("neck", "rotation", lambda t: (-9 - 1.5 * math.sin(w * t - 1.2), 0, 0))
    for s, nm in sides():
        c.f(f"{nm}_arm", "rotation", lambda t, s=s: (26 + 4 * math.sin(w * t - 1.0), 0, -s * (6 + 2 * math.sin(w * t))))
        c.f(f"{nm}_forearm", "rotation", lambda t: (18 + 5 * math.sin(w * t - 1.4), 0, 0))
    trail = {"front": 6, "right": 14, "back": 26, "left": 14}
    for k, nm in enumerate(("front", "right", "back", "left")):
        c.f(f"robe_{nm}", "rotation", lambda t, k=k, nm=nm: (trail[nm] + 4 * math.sin(2 * w * t + k * 1.1), 0,
                                                             2 * math.sin(2 * w * t + k * 1.7)))
    c.f("halo", "position", lambda t: (0, 0.3 * math.sin(w * t), 0.4))
    halo_spin(c, T, 30, -45)
    return c


def anim_light_lances():
    L = 2.0
    c = Clip("attack.light_lances", L)
    breath(c, L, 1, 0.4, 0.5)
    c.pos("body", [(0, (0, 0, 0)), (0.65, (0, 2.0, 1.0), "io"), (0.8, (0, 0.6, -1.2), "snap"), (1.4, (0, 0.5, -0.8)),
                   (2.0, (0, 0, 0), "io")])
    c.rot("body", [(0, (0, 0, 0)), (0.65, (-9, 0, 0), "io"), (0.8, (12, 0, 0), "snap"), (1.4, (9, 0, 0)), (2.0, (0, 0, 0), "io")])
    c.rot("neck", [(0, (0, 0, 0)), (0.65, (-12, 0, 0)), (0.8, (6, 0, 0), "snap"), (1.4, (4, 0, 0)), (2.0, (0, 0, 0))])
    for s, nm in sides():
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.65, (-140, 0, s * 34), "io"), (0.8, (-78, 0, -s * 10), "snap"),
                            (1.4, (-72, 0, -s * 12)), (2.0, (0, 0, 0), "io")])
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.65, (14, 0, 0)), (0.8, (34, 0, 0), "snap"), (1.4, (30, 0, 0)), (2.0, (0, 0, 0))])
    c.f("right_arm", "rotation", lambda t: (tremor(t, 0.8, 0.85, 1.3, 1.45, 1.2, 24), 0, 0))
    c.f("left_arm", "rotation", lambda t: (tremor(t, 0.8, 0.85, 1.3, 1.45, 1.2, 22, 2), 0, 0))
    for k, pos in enumerate(WPOS):
        up = (16, 12, 8)[k]
        d = 0.03 * k
        wing_k(c, pos, [(0, (0, 0, 0)), (0.62 + d, (-6, 14, up), "io"), (0.8 + d, (8, -18, -8), "snap"),
                        (1.4, (4, -10, -4)), (2.0, (0, 0, 0), "io")],
               [(0, (0, 0, 0)), (0.66 + d, (0, 12, 10)), (0.86 + d, (0, -16, -10), "snap"), (1.4, (0, -6, -2)),
                (2.0, (0, 0, 0), "io")])
    c.scl("halo", [(0, (1, 1, 1)), (0.65, (1.14, 1.14, 1)), (0.8, (1.3, 1.3, 1), "snap"), (1.1, (1.1, 1.1, 1)),
                   (2.0, (1, 1, 1), "io")])
    halo_spin(c, L, 120, -135, "io")
    return c


def anim_wing_gust():
    L = 1.5
    c = Clip("attack.wing_gust", L)
    breath(c, L, 1, 0.3, 0.4)
    c.pos("body", [(0, (0, 0, 0)), (0.55, (0, 2.2, 2.2), "io"), (0.72, (0, 0.4, -2.0), "in3"), (1.0, (0, 0.6, -1.4)),
                   (1.5, (0, 0, 0), "io")])
    c.rot("body", [(0, (0, 0, 0)), (0.55, (-10, 0, 0), "io"), (0.72, (14, 0, 0), "in3"), (1.0, (10, 0, 0)), (1.5, (0, 0, 0), "io")])
    c.rot("neck", [(0, (0, 0, 0)), (0.55, (-8, 0, 0)), (0.72, (8, 0, 0), "in3"), (1.5, (0, 0, 0))])
    for s, nm in sides():
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.55, (24, 0, -s * 34), "io"), (0.72, (-30, 0, -s * 20), "in3"),
                            (1.0, (-24, 0, -s * 16)), (1.5, (0, 0, 0), "io")])
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.55, (10, 0, 0)), (0.72, (-10, 0, 0), "in3"), (1.5, (0, 0, 0))])
    for k, pos in enumerate(WPOS):
        up = (18, 12, 6)[k]
        d = 0.025 * k
        wing_k(c, pos, [(0, (0, 0, 0)), (0.55 + d, (-10, 38, up), "io"), (0.7 + d, (14, -46, -12), "in3"),
                        (1.0, (8, -30, -6)), (1.5, (0, 0, 0), "io")],
               [(0, (0, 0, 0)), (0.6 + d, (0, 28, 8), "io"), (0.76 + d, (0, -36, -8), "in3"), (1.05, (0, -16, -4)),
                (1.5, (0, 0, 0), "io")])
    for nm, amt in (("front", -10), ("back", 22), ("right", 12), ("left", 12)):
        c.rot(f"robe_{nm}", [(0, (0, 0, 0)), (0.55, (-amt * 0.5, 0, 0)), (0.72, (amt, 0, 0), "in3"), (1.1, (amt * 0.4, 0, 0)),
                             (1.5, (0, 0, 0), "io")])
    c.f("body", "position", lambda t: (0, tremor(t, 0.7, 0.74, 0.9, 1.05, 0.35, 26), 0))
    halo_spin(c, L, 60, -90, "io")
    return c


def anim_dive():
    L = 1.5
    c = Clip("attack.dive", L)
    c.pos("body", [(0, (0, 0, 0)), (0.4, (0, 3.0, 2.0), "io"), (0.5, (0, 3.2, 2.2)), (0.66, (0, -4.0, -9.0), "in3"),
                   (1.0, (0, -4.5, -10.0)), (1.5, (0, 0, 0), "io")])
    c.rot("body", [(0, (0, 0, 0)), (0.4, (-10, 0, 0), "io"), (0.5, (-12, 0, 0)), (0.66, (52, 0, 0), "in3"),
                   (1.0, (48, 0, 0)), (1.5, (0, 0, 0), "io")])
    c.f("body", "rotation", lambda t: (tremor(t, 0.66, 0.7, 0.95, 1.05, 1.2, 20), 0, tremor(t, 0.66, 0.7, 0.95, 1.05, 1.0, 17, 3)))
    c.rot("neck", [(0, (0, 0, 0)), (0.4, (8, 0, 0)), (0.66, (-28, 0, 0), "in3"), (1.0, (-26, 0, 0)), (1.5, (0, 0, 0))])
    for s, nm in sides():
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.4, (-28, 0, s * 18), "io"), (0.66, (40, 0, -s * 8), "in3"),
                            (1.0, (38, 0, -s * 8)), (1.5, (0, 0, 0), "io")])
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.4, (-50, 0, 0)), (0.66, (20, 0, 0), "in3"), (1.0, (18, 0, 0)),
                                (1.5, (0, 0, 0))])
    for k, pos in enumerate(WPOS):
        fold_up = (-28, -8, 18)[k]
        dive_up = (-34, -10, 22)[k]
        d = 0.02 * k
        wing_k(c, pos, [(0, (0, 0, 0)), (0.4 + d, (12, 62, fold_up), "io"), (0.5, (12, 66, fold_up)),
                        (0.66 + d, (16, 78, dive_up), "in3"), (1.0, (14, 74, dive_up)), (1.2, (-4, -14, 8), "out"),
                        (1.5, (0, 0, 0), "io")],
               [(0, (0, 0, 0)), (0.42 + d, (0, 36, -6), "io"), (0.66 + d, (0, 44, -8), "in3"), (1.0, (0, 40, -6)),
                (1.22, (0, -12, 6), "out"), (1.5, (0, 0, 0), "io")])
    for nm, amt in (("front", 12), ("back", 40), ("right", 24), ("left", 24)):
        c.rot(f"robe_{nm}", [(0, (0, 0, 0)), (0.4, (-amt * 0.3, 0, 0)), (0.66, (amt, 0, 0), "in3"), (1.0, (amt, 0, 0)),
                             (1.5, (0, 0, 0), "io")])
    c.pos("halo", [(0, (0, 0, 0)), (0.66, (0, -0.5, 1.5), "in3"), (1.0, (0, -0.5, 1.5)), (1.5, (0, 0, 0))])
    halo_spin(c, L, 60, -90, "io")
    return c


def anim_radiant_nova():
    L = 2.5
    c = Clip("attack.radiant_nova", L)
    c.pos("body", [(0, (0, 0, 0)), (0.9, (0, -1.5, 0), "io"), (1.1, (0, 2.5, 0.5), "snap"), (1.9, (0, 2.8, 0.5)),
                   (2.5, (0, 0, 0), "io")])
    c.rot("body", [(0, (0, 0, 0)), (0.9, (12, 0, 0), "io"), (1.1, (-12, 0, 0), "snap"), (1.9, (-10, 0, 0)), (2.5, (0, 0, 0), "io")])
    c.f("body", "rotation", lambda t: (tremor(t, 1.1, 1.2, 1.8, 1.95, 1.0, 22), 0, tremor(t, 1.1, 1.2, 1.8, 1.95, 0.8, 19, 2)))
    c.rot("neck", [(0, (0, 0, 0)), (0.9, (16, 0, 0)), (1.1, (-6, 0, 0), "snap"), (1.9, (-5, 0, 0)), (2.5, (0, 0, 0))])
    c.pos("halo", [(0, (0, 0, 0)), (0.9, (0, 0, 0)), (1.1, (0, 0, -2.6), "snap"), (1.9, (0, 0, -2.4)), (2.5, (0, 0, 0), "io")])
    for s, nm in sides():
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.9, (-62, s * 30, s * 24), "io"), (1.1, (-34, 0, -s * 82), "snap"),
                            (1.9, (-30, 0, -s * 78)), (2.5, (0, 0, 0), "io")])
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.9, (-62, 0, 0)), (1.1, (28, 0, 0), "snap"), (1.9, (26, 0, 0)), (2.5, (0, 0, 0))])
    spread = {"upper": 22, "middle": 6, "lower": -14}
    for k, pos in enumerate(WPOS):
        d = 0.03 * k
        wing_k(c, pos, [(0, (0, 0, 0)), (0.9, (-6, -48, -6 if k < 2 else 10), "io"),
                        (1.1 + d, (0, -10, spread[pos]), "snap"), (1.9, (0, -8, spread[pos] - 2)), (2.5, (0, 0, 0), "io")],
               [(0, (0, 0, 0)), (0.9, (0, -34, -12)), (1.14 + d, (0, -4, -6), "snap"), (1.9, (0, -4, -6)),
                (2.5, (0, 0, 0), "io")])
        wing_f(c, pos, lambda t, k=k: (0, 0, tremor(t, 1.15, 1.25, 1.8, 1.95, 1.4, 21, k)))
    for nm, amt in (("front", -6), ("back", 14), ("right", 10), ("left", 10)):
        c.rot(f"robe_{nm}", [(0, (0, 0, 0)), (0.9, (-amt * 0.3, 0, 0)), (1.1, (amt, 0, 0), "snap"), (1.9, (amt * 0.8, 0, 0)),
                             (2.5, (0, 0, 0), "io")])
    c.scl("halo", [(0, (1, 1, 1)), (0.9, (0.82, 0.82, 1), "io"), (1.1, (1.55, 1.55, 1), "snap"), (1.9, (1.45, 1.45, 1)),
                   (2.5, (1, 1, 1), "io")])
    c.scl("halo_inner", [(0, (1, 1, 1)), (0.9, (0.8, 0.8, 1), "io"), (1.12, (1.9, 1.9, 1), "snap"), (1.9, (1.7, 1.7, 1)),
                         (2.5, (1, 1, 1), "io")])
    halo_spin(c, L, 240, -270, "io")
    return c


def anim_phase():
    L = 2.0
    c = Clip("phase", L)
    c.pos("body", [(0, (0, 0, 0)), (0.6, (0, -2.0, 0), "io"), (0.8, (0, 3.0, 0), "snap"), (1.5, (0, 3.2, 0)), (2.0, (0, 0, 0), "io")])
    c.rot("body", [(0, (0, 0, 0)), (0.6, (14, 0, 0), "io"), (0.8, (-14, 0, 0), "snap"), (1.5, (-12, 0, 0)), (2.0, (0, 0, 0), "io")])
    c.f("body", "rotation", lambda t: (tremor(t, 0.8, 0.85, 1.4, 1.55, 1.3, 24), tremor(t, 0.8, 0.85, 1.4, 1.55, 0.9, 19, 3), 0))
    c.rot("torso", [(0, (0, 0, 0)), (0.6, (8, 0, 0)), (0.8, (-8, 0, 0), "snap"), (1.5, (-6, 0, 0)), (2.0, (0, 0, 0))])
    c.rot("neck", [(0, (0, 0, 0)), (0.6, (18, 0, 0), "io"), (0.8, (-20, 0, 0), "snap"), (1.5, (-17, 0, 0)), (2.0, (0, 0, 0), "io")])
    c.pos("halo", [(0, (0, 0, 0)), (0.6, (0, 0, 0)), (0.8, (0, 0, -3.0), "snap"), (1.5, (0, 0, -2.8)), (2.0, (0, 0, 0), "io")])
    for s, nm in sides():
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.6, (-40, s * 20, s * 14), "io"), (0.8, (-50, 0, -s * 70), "snap"),
                            (1.5, (-46, 0, -s * 66)), (2.0, (0, 0, 0), "io")])
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.6, (-60, 0, 0)), (0.8, (10, 0, 0), "snap"), (1.5, (6, 0, 0)), (2.0, (0, 0, 0))])
    spread = {"upper": 26, "middle": 8, "lower": -16}
    for k, pos in enumerate(WPOS):
        d = 0.03 * k
        wing_k(c, pos, [(0, (0, 0, 0)), (0.6, (4, 26, -14 if k < 2 else 12), "io"), (0.8 + d, (-4, -8, spread[pos]), "snap"),
                        (1.5, (-2, -6, spread[pos] - 2)), (2.0, (0, 0, 0), "io")],
               [(0, (0, 0, 0)), (0.6, (0, 20, -10)), (0.84 + d, (0, -6, 4), "snap"), (1.5, (0, -4, 2)), (2.0, (0, 0, 0), "io")])
        wing_f(c, pos, lambda t, k=k: (0, tremor(t, 0.85, 0.9, 1.4, 1.55, 1.2, 23, k + 4), tremor(t, 0.85, 0.9, 1.4, 1.55, 1.6, 20, k)))
    for nm, amt in (("front", -8), ("back", 16), ("right", 12), ("left", 12)):
        c.rot(f"robe_{nm}", [(0, (0, 0, 0)), (0.6, (-amt * 0.3, 0, 0)), (0.8, (amt, 0, 0), "snap"), (1.5, (amt * 0.8, 0, 0)),
                             (2.0, (0, 0, 0), "io")])
    c.scl("halo", [(0, (1, 1, 1)), (0.6, (0.85, 0.85, 1), "io"), (0.8, (1.6, 1.6, 1), "snap"), (1.5, (1.5, 1.5, 1)),
                   (2.0, (1, 1, 1), "io")])
    c.scl("halo_inner", [(0, (1, 1, 1)), (0.6, (0.8, 0.8, 1)), (0.82, (1.7, 1.7, 1), "snap"), (1.5, (1.6, 1.6, 1)),
                         (2.0, (1, 1, 1), "io")])
    halo_spin(c, L, 360, -360, "io")
    return c


def anim_death():
    L = 2.8
    c = Clip("death", L, loop="hold")
    c.pos("body", [(0, (0, 0, 0)), (0.3, (0, 1.5, 0.5), "out"), (1.2, (0, 0.5, 0.5)), (2.0, (0, -4.6, 1.0), "in"),
                   (2.15, (0, -4.0, 1.0), "out"), (2.3, (0, -4.6, 1.0), "in"), (2.8, (0, -4.6, 1.0))])
    c.rot("body", [(0, (0, 0, 0)), (0.3, (-14, 0, 0), "out"), (1.2, (-6, 0, 3)), (2.0, (6, 0, 4), "in"), (2.8, (7, 0, 4))])
    c.f("body", "rotation", lambda t: (tremor(t, 0.2, 0.3, 1.0, 1.3, 2.2, 20), tremor(t, 0.2, 0.3, 1.0, 1.3, 1.6, 17, 2), 0))
    c.rot("torso", [(0, (0, 0, 0)), (0.3, (-6, 0, 0)), (1.2, (4, 0, 0)), (2.2, (18, 0, 3), "io"), (2.8, (20, 0, 3))])
    c.rot("neck", [(0, (0, 0, 0)), (0.3, (-22, 0, 0), "out"), (1.2, (-10, 0, 0)), (2.3, (30, 0, 0), "io"), (2.8, (32, 0, 0))])
    c.rot("head", [(0, (0, 0, 0)), (1.4, (0, 0, 0)), (2.4, (0, 0, -12), "io"), (2.8, (0, 0, -12))])
    c.scl("robe", [(0, (1, 1, 1)), (1.6, (1, 1, 1)), (2.1, (1.08, 0.82, 1.08), "in"), (2.8, (1.08, 0.82, 1.08))])
    for s, nm in sides():
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.3, (-40, 0, -s * 40), "out"), (1.2, (-14, 0, -s * 12)), (2.2, (-10, 0, -s * 4), "io"),
                            (2.8, (-10, 0, -s * 4))])
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.3, (20, 0, 0)), (1.2, (8, 0, 0)), (2.2, (24, 0, 0)), (2.8, (24, 0, 0))])
    # the upper and middle pairs fall forward and drape down; the lower pair splays back along the ground
    droop = {"upper": ((8, -26, -74), (0, 6, -22)), "middle": ((8, -14, -44), (0, 8, -20)),
             "lower": ((4, 4, 4), (0, 6, -6))}
    for k, pos in enumerate(WPOS):
        (tx, tb, tu), tip_end = droop[pos]
        d = 0.06 * k
        wing_k(c, pos, [(0, (0, 0, 0)), (0.3, (-6, -10, 16), "out"), (0.8, (0, -14, 6)), (1.2, (4, 6, -6)),
                        (2.1 + d, (tx, tb, tu), "in"), (2.3 + d, (tx, tb, tu + 5), "out"), (2.5 + d, (tx, tb, tu), "in"),
                        (2.8, (tx, tb, tu))],
               [(0, (0, 0, 0)), (0.35, (0, -8, 10)), (0.9, (0, -10, 4)), (1.3, (0, 6, -8)), (2.25 + d, tip_end, "in"),
                (2.8, tip_end)])
        wing_f(c, pos, lambda t, k=k: (0, 0, tremor(t, 0.25, 0.35, 1.0, 1.3, 3.0, 19, k)))
    for nm, amt in (("front", -10), ("back", -6), ("right", -8), ("left", -8)):
        c.rot(f"robe_{nm}", [(0, (0, 0, 0)), (0.3, (6, 0, 0)), (1.6, (0, 0, 0)), (2.2, (amt, 0, 0), "in"), (2.8, (amt, 0, 0))])
    c.scl("halo", [(0, (1, 1, 1)), (0.3, (1.25, 1.25, 1), "out"), (1.4, (1.0, 1.0, 1)), (2.2, (0.6, 0.6, 1), "io"),
                   (2.7, (0.01, 0.01, 0.01), "in"), (2.8, (0.01, 0.01, 0.01))])
    c.scl("halo_inner", [(0, (1, 1, 1)), (1.4, (1, 1, 1)), (2.5, (0.01, 0.01, 0.01), "in"), (2.8, (0.01, 0.01, 0.01))])
    c.rot("halo", [(0, (0, 0, 0)), (0.3, (0, 0, 30), "out"), (2.7, (0, 0, 150), "out"), (2.8, (0, 0, 150))])
    c.pos("halo", [(0, (0, 0, 0)), (1.4, (0, 0, 0)), (2.7, (0, -3.0, 0), "in"), (2.8, (0, -3.0, 0))])
    return c


def clips():
    return [anim_idle(), anim_fly(), anim_light_lances(), anim_wing_gust(), anim_dive(), anim_radiant_nova(),
            anim_phase(), anim_death()]


POSES = [
    ("idle", [0.0, 1.0, 2.0, 3.0]),
    ("fly", [0.0, 0.35, 0.7, 1.05]),
    ("attack.light_lances", [0.35, 0.65, 0.85, 1.6]),
    ("attack.wing_gust", [0.3, 0.55, 0.72, 1.1]),
    ("attack.dive", [0.3, 0.45, 0.7, 1.2]),
    ("attack.radiant_nova", [0.5, 0.9, 1.3, 2.2]),
    ("phase", [0.5, 0.65, 1.0, 1.8]),
    ("death", [0.3, 1.2, 2.0, 2.8]),
]
HERO = ("attack.radiant_nova", 1.4)


# =============================================================================== validation


def validate(geo, anims, rgba):
    from PIL import Image
    g = geo["minecraft:geometry"][0]
    names = {b["name"] for b in g["bones"]}
    for req in ("root", "body", "head"):
        assert req in names, req
    roots = [b for b in g["bones"] if b["name"] == "root"]
    assert roots[0]["pivot"] == [0, 0, 0] and "parent" not in roots[0]
    for b in g["bones"]:
        if b["name"] != "root":
            assert b.get("parent") in names, b["name"]
    head = [b for b in g["bones"] if b["name"] == "head"][0]
    assert not any(head.get("rotation", [0, 0, 0])), "head must have zero rest rotation"
    for an, a in anims["animations"].items():
        for bn, ch in a["bones"].items():
            assert bn in names, (an, bn)
            if bn == "head" and "rotation" in ch:
                for k, v in ch["rotation"].items():
                    assert abs(v[0]) < 1e-6 and abs(v[1]) < 1e-6, (an, k, v)
    req = {"idle": True, "fly": True, "death": "hold_on_last_frame", "phase": False}
    for an, lp in req.items():
        assert an in anims["animations"], an
        assert anims["animations"][an]["loop"] == lp, (an, anims["animations"][an]["loop"])
    lens = {"death": 2.8, "phase": 2.0, "attack.light_lances": 2.0, "attack.wing_gust": 1.5, "attack.dive": 1.5,
            "attack.radiant_nova": 2.5}
    for an, ln in lens.items():
        assert abs(anims["animations"][an]["animation_length"] - ln) < 1e-6, an
    tw, th = g["description"]["texture_width"], g["description"]["texture_height"]
    p = tl.asset_paths(NAME)
    for key in ("tex", "glow"):
        im = Image.open(p[key])
        assert im.size == (tw * 2, th * 2), (key, im.size, tw, th)
    ncubes = sum(len(b.get("cubes", [])) for b in g["bones"])
    assert 40 <= ncubes <= 140, ncubes
    print(f"validate ok: {len(names)} bones, {ncubes} cubes, texture {tw}x{th} -> png {tw * 2}x{th * 2}")


def main():
    m = build_model()
    geo, rgba, glow, anims = tl.build(NAME, m, SHADERS, clips(), visible=(6, 5, 2.0))
    validate(geo, anims, rgba)
    if "--preview" in sys.argv:
        print(fx.preview_rest(NAME, geo, rgba, glow, HITBOX))
        print(fx.preview_pose(NAME, geo, rgba, glow, anims, HERO[0], HERO[1]))
        if "--all" in sys.argv:
            for an, times in POSES:
                print(fx.preview_strip(NAME, geo, rgba, glow, anims, an, times, HITBOX))
            print(fx.preview_strip(NAME, geo, rgba, glow, anims, "fly", [0.0, 0.35, 0.7, 1.05], HITBOX, yaw=0,
                                   pitch=-4, tag="_front"))
            print(fx.preview_strip(NAME, geo, rgba, glow, anims, "attack.dive", [0.3, 0.45, 0.7, 1.2], HITBOX, yaw=90,
                                   pitch=-4, tag="_side"))
            print(fx.preview_strip(NAME, geo, rgba, glow, anims, "attack.wing_gust", [0.3, 0.55, 0.72, 1.1], HITBOX,
                                   yaw=90, pitch=-20, tag="_side"))
            extra = [("fly", [0.0, 0.35, 0.7, 1.05], 90, -8, "_side"),
                     ("attack.dive", [0.2, 0.45, 0.6, 0.8, 1.25], -30, -8, "_34"),
                     ("attack.light_lances", [0.35, 0.65, 0.85, 1.6], 0, -8, "_front"),
                     ("attack.radiant_nova", [0.5, 0.9, 1.15, 2.2], 0, -8, "_front"),
                     ("phase", [0.5, 0.8, 1.2, 1.8], 0, -8, "_front"),
                     ("death", [0.8, 1.6, 2.2, 2.8], 0, -10, "_front")]
            for an, times, yaw, pitch, tag in extra:
                print(fx.preview_strip(NAME, geo, rgba, glow, anims, an, times, HITBOX, yaw=yaw, pitch=pitch, tag=tag))


if __name__ == "__main__":
    main()
