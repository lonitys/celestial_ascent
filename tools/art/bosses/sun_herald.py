"""Sun Herald: a tall herald of the sun. Engraved sun-gold armour over a layered saffron and ivory
robe, a serene golden sun mask framed by a ray crown, a two-layer blazing sunburst halo that spins
behind the head (with an eclipse moon parked behind it), and a tall sun staff.

Run: python sun_herald.py [--preview] [--all]
"""
import math
import os
import sys

import numpy as np

import bosslib as tl
import bossfx as fx
import geo_preview as gp
from bosslib import Clip, env
from rig import TAU, knee_bend, sides, tremor
from sun_herald_mats import SHADERS

NAME = "sun_herald"
HITBOX = (1.8, 4.0)
THIGH, SHIN = 12.0, 11.5
HALO_C = (0.0, 55.0, 8.0)          # halo centre (model units)

# robe panels: (bone, theta deg (0 = front, +90 = model's left), width, height, flare deg, taper)
ROBE = [
    ("robe_front", 0, 11, 24.5, 10, 0.42),
    ("robe_fl", 45, 10, 26.0, 13, 0.45),
    ("robe_l", 90, 10, 26.0, 14, 0.40),
    ("robe_bl", 135, 10, 26.8, 15, 0.45),
    ("robe_back", 180, 12, 28.0, 15, 0.42),
    ("robe_br", -135, 10, 26.8, 15, 0.45),
    ("robe_r", -90, 10, 26.0, 14, 0.40),
    ("robe_fr", -45, 10, 26.0, 13, 0.45),
]
ROBE_TOP = 28.4
ROBE_RX, ROBE_RZ, ROBE_CZ = 6.9, 4.9, 0.3

# =============================================================================== geometry


def bone_world(m):
    bones = [{"name": b.name, "parent": b.parent, "pivot": b.pivot, "rotation": b.rotation or [0, 0, 0]}
             for b in m.bones.values()]
    return gp.bone_matrices({"bones": bones})


def held_bone(m, name, parent, grip, build_fn):
    """Create a bone held by `parent` whose cubes are authored upright in WORLD (rest) space.
    The bone pivots at the grip and gets the rest rotation that cancels its parents' rotation."""
    mats = bone_world(m)
    M = mats[parent]
    G0 = np.asarray(grip, dtype=float)
    Gw = (M @ np.r_[G0, 1.0])[:3]
    b = m.bone(name, parent, G0, rotation=tl.euler(M[:3, :3].T))
    build_fn(b, Gw)
    d = G0 - Gw
    for c in b.cubes:
        c.origin = list(np.asarray(c.origin) + d)
        if c.pivot is not None:
            c.pivot = list(np.asarray(c.pivot) + d)
    return b


def build_model():
    m = tl.Model(NAME)
    body = m.bone("body", "root", (0, 27, 0))
    body.boxb(0, 22, 0.3, 12, 7, 9, "cloth_dark")                                   # hips under the robe
    body.boxb(0, 27, 0.3, 15, 3, 11, "belt")                                        # broad gold belt
    body.box((0, 28.5, -5.45), (4, 4, 1), "buckle")                                 # sun buckle

    # ---- layered robe: eight flared under-robe panels, ivory tabard and side faulds over them
    for nm, th, w, h, fl, tp in ROBE:
        st = math.sin(math.radians(th))
        ct = math.cos(math.radians(th))
        anchor = (ROBE_RX * st, ROBE_TOP, ROBE_CZ - ROBE_RZ * ct)
        b = m.bone(nm, "body", anchor)
        b.plane_from(anchor, w, h, "robe", rot=[-fl, -th, 0], taper=tp, top_y=ROBE_TOP)
        if nm == "robe_front":
            a2 = (0, ROBE_TOP + 0.4, ROBE_CZ - ROBE_RZ - 0.55)
            b.plane_from(a2, 7, 22, "tabard", rot=[-fl - 1.5, 0, 0], taper=0.25, emblem=True, emblem_t=0.34)
        if nm in ("robe_l", "robe_r"):
            s = 1 if th > 0 else -1
            a2 = (s * (ROBE_RX + 0.6), ROBE_TOP + 0.4, ROBE_CZ)
            b.plane_from(a2, 9, 12, "fauld", rot=[-fl - 6, -th, 0], taper=0.3)

    # ---- torso
    torso = m.bone("torso", "body", (0, 30, 0), rotation=[-2, 0, 0])
    torso.boxb(0, 29.5, 0.3, 11, 5, 8, "sash")                                       # waist sash
    torso.boxb(0, 33.5, 0.3, 13, 4, 9, "gold_bands")                                 # lower cuirass
    torso.boxb(0, 37, 0.3, 16, 6, 10, "gold_plate")                                   # upper cuirass
    torso.box((0, 38.0, -4.95), (9, 7, 1), "gold_cuirass", burst_y=0.0, burst_n=8, burst_r=1.7)  # sun plate
    torso.box((0, 38.0, -5.65), (3, 3, 1), "sun_gem", rot=[0, 0, 45])               # chest sun gem
    torso.boxb(0, 42.5, 0.3, 11, 3, 9, "gold_soft")                                  # gorget
    torso.boxb(0, 32.5, 4.7, 7, 10, 1, "gold_bands")                                 # spine plate

    neck = m.bone("neck", "torso", (0, 44.5, 0.3))
    neck.boxb(0, 43.5, 0.3, 5, 3, 5, "cloth_dark")
    neck.box((0, 45.0, 0.6), (9, 2, 8), "gold_soft")                                 # collar ring

    head = m.bone("head", "neck", (0, 46.5, 0.3))
    head.boxb(0, 45.5, 0.8, 10, 12, 10, "hood")                                      # hood
    head.box((0, 58.0, 1.3), (8, 1, 8), "hood", no_ao=True)                          # rounded crown
    head.box((0, 50.5, -5.0), (8, 10, 2), "mask")                                    # sun mask
    head.plane_from((0, 54.6, -6.15), 12, 6, "diadem", rot=[-20, 0, 0], anchor_st=(0.5, 1.0))

    # ---- halo (behind the head, on the torso, so it can spin and never follows the look)
    hm = m.bone("halo_mount", "torso", HALO_C)
    halo = m.bone("halo", "halo_mount", HALO_C)
    halo.plane(HALO_C, 32, 32, "halo_disc", r_disc=9.5, r_rim=10.8, r_flame=15.4)
    ecl = m.bone("eclipse", "halo_mount", HALO_C)
    ecl.plane((HALO_C[0], HALO_C[1], HALO_C[2] + 0.4), 20, 20, "moon", r=9.4)
    rays = m.bone("halo_rays", "halo_mount", HALO_C)
    rays.plane((HALO_C[0], HALO_C[1], HALO_C[2] + 0.8), 42, 42, "halo_rays", r_plate=10.4)

    # ---- mantle (two bones so it can ripple)
    mant = m.bone("mantle", "torso", (0, 43, 5.6))
    mant.plane_from((0, 43, 5.6), 17, 22, "mantle", rot=[-7, 180, 0], taper=0.0, emblem=31.0)
    a = (0, 43 - 22 * math.cos(math.radians(7)), 5.6 + 22 * math.sin(math.radians(7)))
    ml = m.bone("mantle_low", "mantle", a)
    ml.plane_from(a, 19, 17, "mantle", rot=[-4, 180, 0], taper=0.0, hem=True)

    # ---- arms
    for s, nm in sides():
        rest = [-6, 0, -9 * s]
        arm = m.bone(f"{nm}_arm", "torso", (10.5 * s, 41.5, 0.3), rotation=rest)
        arm.boxb(11.5 * s, 33, 0.3, 4, 9, 4, "cloth_dark")                         # upper sleeve
        arm.boxb(11.6 * s, 34.5, 0.3, 5, 4, 5, "gold_soft")                         # rerebrace
        # pauldron: three cascading sun-gold lames, a ridge cap and one swept flame fin
        arm.box((11.8 * s, 42.6, 0.3), (9, 4, 11), "gold_plate", rot=[0, 0, 22 * s], boss=True)
        arm.box((14.3 * s, 40.0, 0.3), (6, 3, 10), "gold_plate", rot=[0, 0, 36 * s])
        arm.box((15.7 * s, 37.6, 0.3), (4, 3, 9), "gold_plate", rot=[0, 0, 50 * s])
        arm.box((10.6 * s, 45.0, 0.3), (5, 2, 8), "gold", rot=[0, 0, 22 * s])
        arm.curve_spike((12.6 * s, 44.6, 2.0), [(0.45 * s, 1, 0.25), (0.75 * s, 1, 0.75), (1.0 * s, 0.5, 1.2)],
                        [5, 4, 4], [2, 2, 1], "gold_ray")
        fore_rest = [-38, 0, 0] if nm == "right" else [-24, 0, 0]
        fore = m.bone(f"{nm}_forearm", f"{nm}_arm", (11.5 * s, 33.5, 0.3), rotation=fore_rest)
        fore.boxb(11.5 * s, 28.4, 0.3, 6, 6, 6, "sleeve")                            # bell sleeve
        fore.boxb(11.5 * s, 26.6, 0.3, 7, 2, 7, "cuff")                              # flared gold cuff
        fore.boxb(11.5 * s, 23.5, 0.3, 4, 4, 4, "gold_bands")                        # vambrace
        fore.boxb(11.5 * s, 20, 0.0, 4, 4, 4, "gauntlet")                            # gauntlet
        fore.box((9.6 * s, 22.0, -1.2), (1, 3, 2), "gold_soft")                      # thumb

    # ---- staff (authored upright in world space, held in the right hand)
    def build_staff(b, G):
        gx, gz = G[0], G[2]
        b.box((gx, 1.5, gz), (3, 3, 3), "gold_soft")                                 # foot cap
        b.boxb(gx, 2.5, gz, 2, 54, 2, "staff_shaft")                                 # shaft
        b.box((gx, G[1], gz), (2, 6, 2), "staff_shaft", inflate=0.3, grip=True)      # grip wrap
        b.box((gx, 31.5, gz), (3, 2, 3), "gold_soft")                                # collar
        b.box((gx, 55.5, gz), (4, 3, 4), "gold_soft")                                # finial cup
        b.box((gx, 58.0, gz), (2, 3, 2), "gold_soft")                                # neck
        b.plane((gx, 64.5, gz), 14, 14, "staff_sun")                                 # sun finial (front)
        b.plane((gx, 64.5, gz), 14, 14, "staff_sun", rot=[0, 90, 0])                 # sun finial (side)
        b.box((gx, 64.5, gz), (3, 3, 3), "sun_gem", rot=[45, 0, 45])                 # sun orb
    st = held_bone(m, "staff", "right_forearm", (-11.5, 21.5, -0.2), build_staff)
    foot = st.cubes[0]
    lo, sz = np.asarray(foot.origin), np.asarray(foot.size, dtype=float)
    m.staff_foot = np.array([lo + sz * np.array([i, 0, k]) for i in (0, 1) for k in (0, 1)])

    # ---- legs (mostly under the robe; gold sabatons poke out at the hem)
    for s, nm in sides():
        leg = m.bone(f"{nm}_leg", "body", (3.6 * s, 26, 0.3))
        leg.boxb(3.6 * s, 14, 0.3, 5, 12, 5, "cloth_dark")
        shin = m.bone(f"{nm}_shin", f"{nm}_leg", (3.6 * s, 14, 0.3))
        shin.boxb(3.6 * s, 3, 0.3, 5, 11, 5, "gold_bands")
        shin.box((3.6 * s, 13.6, -2.2), (4, 4, 2), "gold_soft")                      # knee cop
        foot = m.bone(f"{nm}_foot", f"{nm}_shin", (3.6 * s, 2.5, 0.3))
        foot.boxb(3.6 * s, 0, -1.2, 5, 3, 8, "gold_soft")                            # sabaton
        foot.box((3.6 * s, 1.0, -5.6), (3, 2, 3), "gold_soft", rot=[0, 45, 0])       # pointed toe
    build_stages(m)
    return m


# =============================================================================== evolution stages
# BossRenderer shows bones named stage2_* from stage 2 on and stage3_* only in stage 3 (hiding a
# bone hides its children) and scales them in from 0 at their pivot, so every pivot sits where the
# part attaches. Stage bones come after all base bones (base cube indices, which seed the cloth
# folds and hems, stay the same) and never occlude the base model in the baked AO, so the base
# texture is unchanged with them hidden.
FIRE_R = 23.0                      # stage 2 ring of fire: band radius (outside the 20.5 long rays)
WING_ROOT = (4.0, 43.0, 6.0)       # stage 3 wing root (left wing; mirrored), on the upper back
WING_SPLIT, WING_WRIST = 16.0, (16.0, 13.0)
WING_A = dict(w=16, h=37, top=15.0, yaw=25.0)     # inner wing: arm, coverts, secondaries
WING_B = dict(w=24, h=42, top=3.0, yaw=48.0)      # outer wing: primaries fanning from the wrist

# feathers in wing coordinates (u outward from the root, y up from it): (base, tip, width)
SECONDARIES = [((1.0 + 14.0 * f, 0.6 + 11.0 * f), (min(15.0, 2.6 + 13.4 * f), -21.0 + 4.0 * f), 5.6)
               for f in np.linspace(0, 1, 6)]
COVERTS = [((16.0 * f, 13.0 * f - 0.4), (16.0 * f + 1.4, 13.0 * f - 7.6), 3.8) for f in (np.arange(7) + 0.45) / 7]
PRIMARIES = [((16.6, 12.4), (22.0, -22.5), 5.6), ((18.0, 12.4), (27.0, -19.5), 5.6), ((19.5, 12.2), (31.5, -14.5), 5.4),
             ((21.0, 12.0), (35.0, -9.0), 5.2), ((22.5, 11.8), (37.6, -3.0), 4.8), ((24.0, 11.5), (39.2, 3.0), 4.2),
             ((25.0, 11.0), (39.4, 8.6), 3.4)]
ARM = [(0.0, 0.0), WING_WRIST, (25.5, 10.8)]


def stage_bone(m, name, parent, pivot):
    assert name.startswith(("stage2_", "stage3_")), name
    return m.bone(name, parent, pivot)


def build_stages(m):
    # ---- stage 2: a second, larger ring of fire around the halo and sun plates on the shoulders
    fire = stage_bone(m, "stage2_halo_fire", "halo", HALO_C)          # spins with the flame disc
    fire.plane((HALO_C[0], HALO_C[1], HALO_C[2] + 1.4), 58, 58, "fire_ring", r_band=FIRE_R)
    for s, nm in sides():
        c = np.array([17.0 * s, 44.5, -0.5])
        R = tl.axis_angle([0, 1, 0], -40 * s) @ tl.axis_angle([1, 0, 0], -10)   # faces out, front and a bit down
        sp = stage_bone(m, f"stage2_{nm}_sun_plate", f"{nm}_arm", (15.0 * s, 42.5, 0.3))
        sp.plane(c, 16, 16, "sun_plate", rot=R, r_disc=3.9)

    # ---- stage 3: wings of light from the shoulder blades and a crown of sun rays on the head
    for s, nm in sides():
        root = np.array([WING_ROOT[0] * s, WING_ROOT[1], WING_ROOT[2]])
        wb = stage_bone(m, f"stage3_{nm}_wing", "torso", root)
        Ra = tl.axis_angle([0, 1, 0], -WING_A["yaw"] * s)
        wb.plane_from(root, WING_A["w"], WING_A["h"], "light_wing", rot=Ra,
                      anchor_st=(0.0 if s > 0 else 1.0, WING_A["top"] / WING_A["h"]),
                      side=s, u0=0.0, y_top=WING_A["top"], feathers=SECONDARIES, coverts=COVERTS, arm=ARM[:2])
        wrist = root + Ra @ np.array([WING_WRIST[0] * s, WING_WRIST[1], 0.0])
        Rb = tl.axis_angle([0, 1, 0], -WING_B["yaw"] * s)
        wb.plane_from(wrist, WING_B["w"], WING_B["h"], "light_wing", rot=Rb,
                      anchor_st=(0.0 if s > 0 else 1.0, WING_B["top"] / WING_B["h"]),
                      side=s, u0=WING_SPLIT, y_top=WING_WRIST[1] + WING_B["top"], feathers=PRIMARIES[::-1], arm=ARM[1:])
    cr = stage_bone(m, "stage3_sun_crown", "head", (0, 57.5, 1.6))
    for a_deg, L, w in ((0, 14, 3), (24, 12, 3), (-24, 12, 3), (48, 10, 2), (-48, 10, 2), (70, 8, 2), (-70, 8, 2)):
        a = math.radians(a_deg)
        back = abs(a_deg) / 70.0                                   # outer rays wrap back around the hood
        base = np.array([6.0 * math.sin(a), 52.0 + 6.0 * math.cos(a), 1.6 + 1.6 * back])
        cr.spike(base, (math.sin(a), math.cos(a), 0.15 + 0.6 * back), L, w, "sun_spike", segs=[0.56, 0.52], taper=0.6,
                 overlap=0.8)
    for b in m.bones.values():
        if b.name.startswith(("stage2_", "stage3_")):
            for c in b.cubes:
                c.params["no_ao"] = True        # never darkens the base model (it must look unchanged)


# =============================================================================== animation helpers
LEGS = [("right_leg", "right_shin"), ("left_leg", "left_shin")]
FEET = ["right_foot", "left_foot"]
FLAME_STEP, RAY_STEP = 15.0, 22.5
MODEL = build_model()            # rest rotations for the staff solver
STAFF_CHAIN = ["body", "torso", "right_arm", "right_forearm"]
K = tl.Track                     # eased key track usable inside procedural functions


def rest_rot(name):
    return np.array(MODEL.bones[name].rotation or [0, 0, 0], dtype=float)


def staff_world(c, tilt_keys, spin_keys=None):
    """Key the staff so that its WORLD orientation follows tilt_keys (Bedrock euler, 0 = upright)
    plus a spin about its own shaft, whatever the body, torso and right arm are doing."""
    tilt = K(tilt_keys)
    spin = K(spin_keys or [(0, 0.0)])
    rest_s = rest_rot("staff")
    state = {"t": None, "prev": None}

    def fn(t):
        R = np.eye(3)
        for b in STAFF_CHAIN:
            a = c.eval(b, "rotation", t)
            R = R @ gp.rot_b(rest_rot(b) + (a if a is not None else 0.0))
        Rd = gp.rot_b(np.asarray(tilt(t), dtype=float)) @ gp.rot_b((0.0, float(spin(t)), 0.0))
        e = np.array(gp.euler_from_matrix(R.T @ Rd)) - rest_s
        if state["prev"] is not None and t >= state["t"]:
            e = state["prev"] + (e - state["prev"] + 180.0) % 360.0 - 180.0
        state["t"], state["prev"] = t, e
        return e
    c.f("staff", "rotation", fn)


def clip_matrix(c, bone, t, skip=()):
    """World matrix of `bone` at time t of clip c (rest pivots/rotations + the clip's channels)."""
    chain = []
    b = bone
    while b is not None:
        chain.append(b)
        b = MODEL.bones[b].parent
    M = np.eye(4)
    for name in reversed(chain):
        rot = rest_rot(name)
        r = None if (name, "rotation") in skip else c.eval(name, "rotation", t)
        p = None if (name, "position") in skip else c.eval(name, "position", t)
        sc = None if (name, "scale") in skip else c.eval(name, "scale", t)
        piv = np.asarray(MODEL.bones[name].pivot, dtype=float)
        M = (M @ gp.trans(p if p is not None else np.zeros(3)) @ gp.trans(piv)
             @ gp.mat4(gp.rot_b(rot + (r if r is not None else 0.0)))
             @ gp.scale4(sc if sc is not None else np.ones(3)) @ gp.trans(-piv))
    return M


def staff_ground(c, margin=0.35):
    """Slide the staff up through the hand whenever its foot would dip below the ground."""
    corners = np.c_[MODEL.staff_foot, np.ones(len(MODEL.staff_foot))]

    def fn(t):
        M = clip_matrix(c, "staff", t, skip={("staff", "position")})
        low = float((M @ corners.T)[1].min())
        dy = max(0.0, margin - low)
        if dy <= 0:
            return (0.0, 0.0, 0.0)
        Rp = clip_matrix(c, "right_forearm", t)[:3, :3]
        return tuple(np.linalg.solve(Rp, np.array([0.0, dy, 0.0])))
    c.f("staff", "position", fn)


def leg_ik(dz, dy, l1=THIGH, l2=SHIN):
    """2-link sagittal leg IK. (dz, dy) = ankle relative to hip (dz < 0 forward, dy < 0 below).
    Returns (thigh_rot_x, shin_rot_x, shin_abs_x) in Bedrock degrees (x < 0 swings forward)."""
    D = min(math.hypot(dz, dy), l1 + l2 - 1e-4)
    phi = math.atan2(-dz, -dy)
    cosa = (l1 * l1 + D * D - l2 * l2) / (2 * l1 * D)
    a = phi + math.acos(max(-1.0, min(1.0, cosa)))
    kz, ky = -l1 * math.sin(a), -l1 * math.cos(a)
    psi = math.atan2(-(dz - kz), -(dy - ky))
    return -math.degrees(a), math.degrees(a - psi), -math.degrees(psi)


def legs_ik(c, targets, hip_offset):
    """Drive both legs from ankle targets. targets(side, t) -> (z_world, y_world, foot_abs_deg);
    hip_offset(t) -> (dy, dz) of the body. Keys thigh, shin and foot rotations."""
    for s, nm in sides():
        hip = np.array([0.3, 26.0])                     # (z, y) of the hip pivot at rest

        def solve(t, nm=nm):
            zt, yt, F = targets(nm, t)
            dyb, dzb = hip_offset(t)
            th, sh, sa = leg_ik(zt - (hip[0] + dzb), yt - (hip[1] + dyb))
            return th, sh, F - sa
        c.f(f"{nm}_leg", "rotation", lambda t, f=solve: (f(t)[0], 0, 0))
        c.f(f"{nm}_shin", "rotation", lambda t, f=solve: (f(t)[1], 0, 0))
        c.f(f"{nm}_foot", "rotation", lambda t, f=solve: (f(t)[2], 0, 0))


def robe_guard(c, drop, k_scale=0.7, k_flare=3.0):
    """When the body drops by drop(t), shorten the robe panels and flare them so the hem stays
    above the ground. Returns the extra flare function for robe_sway."""
    for nm, *_ in ROBE:
        c.f(nm, "scale", lambda t: (1.0, 1.0 - k_scale * max(0.0, float(drop(t))) / 26.0, 1.0))
    return lambda t: k_flare * max(0.0, float(drop(t)))


def halo_spin(c, L, flame_total=15.0, ray_total=22.5, extra_flame=None, extra_ray=None):
    """Constant halo spin (flames +z, rays -z) whose totals are whole symmetry steps (15 / 22.5 deg)
    so loops are seamless and attacks end where idle begins; plus optional extra spin keys."""
    assert abs(flame_total / FLAME_STEP - round(flame_total / FLAME_STEP)) < 1e-6
    assert abs(ray_total / RAY_STEP - round(ray_total / RAY_STEP)) < 1e-6
    c.f("halo", "rotation", lambda t: (0, 0, flame_total * t / L))
    c.f("halo_rays", "rotation", lambda t: (0, 0, -ray_total * t / L))
    for bone, keys, step in (("halo", extra_flame, FLAME_STEP), ("halo_rays", extra_ray, RAY_STEP)):
        if keys:
            end = keys[-1][1]
            end = end[2] if isinstance(end, (tuple, list)) else end
            assert abs(end / step - round(end / step)) < 1e-6, (c.name, bone, end)
            c.rot(bone, [(k[0], (0, 0, k[1])) + tuple(k[2:]) for k in keys])


def flare_rot(theta, alpha):
    """Rotation swinging a hanging panel at angle theta outward by alpha degrees."""
    th = math.radians(theta)
    return (-alpha * math.cos(th), 0.0, -alpha * math.sin(th))


def robe_sway(c, L, amp=1.4, cycles=1, flare=None, drag=None, extra=None, drop=None):
    """Ripple running around the robe hem (whole cycles per clip) + optional outward flare F(t),
    backward drag D(t) (deg, +x swings the hem back), a per-panel extra(theta, t) and a ground
    guard for body drops (drop(t) > 0 = lower)."""
    if drop is not None:
        guard = robe_guard(c, drop)
        user = flare
        flare = (lambda t: guard(t) + user(t)) if user else guard
    for nm, th, *_ in ROBE:
        ph = math.radians(th)

        def fn(t, th=th, ph=ph):
            a = amp * math.sin(TAU * cycles * t / L + ph)
            if flare:
                a += flare(t)
            r = list(flare_rot(th, a))
            r[0] += 0.5 * amp * math.sin(TAU * cycles * t / L + ph + 1.3)
            if drag:
                r[0] += drag(t)
            if extra:
                e = extra(th, t)
                r = [r[0] + e[0], r[1] + e[1], r[2] + e[2]]
            return tuple(r)
        c.f(nm, "rotation", fn)


def mantle_sway(c, L, amp=1.4, cycles=1, lift=None):
    """Two-segment mantle ripple; lift(t) -> (upper_deg, lower_deg) swings it back."""
    w = lambda t, ph: math.sin(TAU * cycles * t / L + ph)
    c.f("mantle", "rotation", lambda t: (amp * w(t, 0.4) + (lift(t)[0] if lift else 0), 0, 0.5 * amp * w(t, 1.9)))
    c.f("mantle_low", "rotation", lambda t: (1.6 * amp * w(t, -0.6) + (lift(t)[1] if lift else 0), 0,
                                             0.8 * amp * w(t, 0.9)))


def flutter(t, amp, freq=5.0, ph=0.0):
    return amp * math.sin(TAU * freq * t + ph)


# =============================================================================== animations


def anim_idle():
    T = 4.0
    c = Clip("idle", T, loop=True)
    w = lambda t, ph=0.0, k=1: math.sin(TAU * k * t / T + ph)
    halo_spin(c, T, 15.0, 22.5)
    c.f("halo_mount", "position", lambda t: (0, 0.4 * w(t, 0.8), 0))
    c.f("halo_mount", "rotation", lambda t: (0, 0, 0.8 * w(t, 2.0)))
    c.f("body", "position", lambda t: (0, 0.12 * w(t, 0, 2), 0))
    c.f("torso", "rotation", lambda t: (1.3 * w(t), 0.8 * w(t, 1.2), 0))
    c.f("torso", "position", lambda t: (0, 0.22 * w(t), 0))
    c.f("neck", "rotation", lambda t: (-1.2 * w(t, 0.5), 0, 0.6 * w(t, 2.3)))
    for s, nm in sides():
        c.f(f"{nm}_arm", "rotation", lambda t, s=s: (1.5 * w(t, 0.6 + s), 0, -1.4 * s * w(t, 0.3)))
        c.f(f"{nm}_forearm", "rotation", lambda t, s=s: (-2.5 * w(t, 1.0 + s * 0.4), 0, 0))
    staff_world(c, [(0, (0, 0, 0))])
    staff_ground(c)
    robe_sway(c, T, 1.5)
    mantle_sway(c, T, 1.5)
    return c


WALK_T, STRIDE, LIFT, DUTY = 1.6, 14.0, 3.4, 0.6
TOE, HEEL = 8.0, 2.5                     # toe / heel distance from the ankle pivot (foot box)


def foot_lift_for(F):
    """Ankle lift that keeps the sole above ground when the foot is pitched by F degrees."""
    r = math.radians(F)
    if F >= 0:
        return TOE * math.sin(r) + 2.5 * (math.cos(r) - 1)
    return HEEL * math.sin(-r) + 2.5 * (math.cos(r) - 1)


def walk_foot(u):
    """Foot path relative to the hip for phase u in [0, 1): stance front -> back on the ground
    (heel lifting at the end), swing back -> front on an arc. Returns (dz, lift, foot_abs_deg)."""
    u = u % 1.0
    if u < DUTY:
        f = u / DUTY
        z = -STRIDE / 2 + STRIDE * f
        F = 16.0 * fx.smoothstep(0.72, 1.0, f)
        return z, foot_lift_for(F), F
    f = (u - DUTY) / (1 - DUTY)
    z = STRIDE / 2 - STRIDE * tl.ease("io", f)
    F = 32.0 * math.sin(math.pi * f) * (0.55 - f) * 2 + 16.0 * (1 - fx.smoothstep(0.0, 0.25, f))
    return z, max(LIFT * math.sin(math.pi * f), foot_lift_for(F)) + 0.0, F


def walk_hip(t):
    u = (t / WALK_T) % 1.0
    return -0.75 - 0.55 * (1 - math.cos(4 * math.pi * (u - 0.3))) / 2


def anim_walk():
    T = WALK_T
    c = Clip("walk", T, loop=True)
    ph = lambda t: TAU * t / T
    phase = {"right": 0.0, "left": 0.5}

    def targets(nm, t):
        dz, lift, F = walk_foot(t / T + phase[nm])
        return 0.3 + dz, 2.5 + lift, F
    c.f("body", "position", lambda t: (0, walk_hip(t), 0))
    legs_ik(c, targets, lambda t: (walk_hip(t), 0.0))
    # right foot is forward (heel strike) at u = 0, so the right hip leads around u = 0
    c.f("body", "rotation", lambda t: (0, -3.5 * math.cos(ph(t)), 1.3 * math.sin(ph(t))))
    c.f("torso", "rotation", lambda t: (3 + 1.0 * math.cos(4 * math.pi * t / T - 0.5), 5.5 * math.cos(ph(t)),
                                        -1.1 * math.sin(ph(t))))
    c.f("neck", "rotation", lambda t: (-2 - 1.0 * math.cos(4 * math.pi * t / T - 0.8), -2.0 * math.cos(ph(t)), 0))
    c.f("left_arm", "rotation", lambda t: (-15 * math.cos(ph(t)), 0, 2.5))
    c.f("left_forearm", "rotation", lambda t: (-8 - 8 * max(0.0, math.cos(ph(t))), 0, 0))
    c.f("right_arm", "rotation", lambda t: (6 * math.cos(ph(t)), 0, 0))
    c.f("right_forearm", "rotation", lambda t: (-3 * math.cos(ph(t)), 0, 0))
    staff_world(c, [(0, (0, 0, 0))])
    c.f("staff", "rotation", lambda t: (4 * math.cos(ph(t) - 0.6), 0, 0))
    staff_ground(c)
    halo_spin(c, T, 15.0, 22.5)
    c.f("halo_mount", "position", lambda t: (0, 0.5 * math.cos(4 * math.pi * t / T - 1.0) - 0.2, 0.3))
    c.f("halo_mount", "rotation", lambda t: (1.0 * math.cos(4 * math.pi * t / T - 1.0), 0, 1.6 * math.sin(ph(t) - 0.7)))

    def thigh(nm, t):
        zt, yt, F = targets(nm, t)
        return leg_ik(zt - 0.3, yt - (26.0 + walk_hip(t)))[0]

    def walk_robe(th, t):
        r, l = thigh("right", t), thigh("left", t)
        if th == 0:
            return (0.6 * min(r, l, 0.0) - 2.0, 0, 0)
        if abs(th) == 45:
            g = r if th < 0 else l
            return (0.7 * min(g, 0.0) + 0.25 * max(g, 0.0), 0, 0)
        if abs(th) == 90:
            g = r if th < 0 else l
            return (0.45 * g, 0, 0)
        if abs(th) == 135:
            g = r if th < 0 else l
            return (0.6 * max(g, 0.0) + 0.15 * min(g, 0.0) + 2.5, 0, 0)
        return (0.5 * max(r, l, 0.0) + 4.0, 0, 0)
    robe_sway(c, T, 1.8, 2, extra=walk_robe)
    mantle_sway(c, T, 1.6, 2, lift=lambda t: (5 + 1.5 * math.cos(2 * ph(t)), 4 + 2.5 * math.cos(2 * ph(t) - 0.8)))
    return c


def anim_solar_flare():
    L = 2.0
    c = Clip("attack.solar_flare", L)
    A, S, H, R = 0.55, 0.72, 1.25, 2.0        # anticipation, strike, hold end, recovered
    c.rot("torso", [(0, (0, 0, 0)), (A, (-10, -20, 0), "io"), (S, (12, 16, 0), "snap"), (H, (10, 13, 0)),
                    (R, (0, 0, 0), "io")])
    c.f("torso", "rotation", lambda t: (tremor(t, S, S + 0.05, H - 0.1, H, 0.8, 24), tremor(t, S, S + 0.05, H - 0.1, H, 0.6, 19, 2), 0))
    drop = K([(0, 0.0), (A, 1.2), (S, 2.2, "snap"), (H, 2.0), (R, 0.0)])
    c.f("body", "position", lambda t: (0, -float(drop(t)), 0))
    c.pos("body", [(0, (0, 0, 0)), (A, (0, 0, 1.4)), (S, (0, 0, -1.6), "snap"), (H, (0, 0, -1.3)), (R, (0, 0, 0))])
    knee_bend(c, lambda t: float(drop(t)), THIGH, SHIN, LEGS, FEET)
    c.rot("left_arm", [(0, (0, 0, 0)), (A, (26, 0, -34)), (S, (-86, -6, 14), "snap"), (H, (-82, -4, 12)), (R, (0, 0, 0), "io")])
    c.rot("left_forearm", [(0, (0, 0, 0)), (A, (-62, 0, 0)), (S, (21, 0, 0), "snap"), (H, (18, 0, 0)), (R, (0, 0, 0))])
    c.rot("right_arm", [(0, (0, 0, 0)), (A, (-22, 0, 8)), (S, (8, 0, 4), "snap"), (H, (6, 0, 4)), (R, (0, 0, 0))])
    c.rot("right_forearm", [(0, (0, 0, 0)), (A, (-10, 0, 0)), (S, (6, 0, 0), "snap"), (R, (0, 0, 0))])
    staff_world(c, [(0, (0, 0, 0)), (A, (-8, 0, 4)), (S, (9, 0, -5), "snap"), (H, (7, 0, -4)), (R, (0, 0, 0))])
    staff_ground(c)
    c.rot("neck", [(0, (0, 0, 0)), (A, (-7, -6, 0)), (S, (7, 4, 0), "snap"), (H, (5, 3, 0)), (R, (0, 0, 0))])
    c.pos("halo_mount", [(0, (0, 0, 0)), (A, (0, 1.0, 1.5)), (S, (0, -0.4, -2.5), "snap"), (H, (0, -0.3, -2.0)), (R, (0, 0, 0))])
    c.f("halo_mount", "position", lambda t: (tremor(t, S, S + 0.05, H - 0.1, H, 0.25, 26), tremor(t, S, S + 0.05, H - 0.1, H, 0.25, 21, 1), 0))
    c.scl("halo_mount", [(0, (1, 1, 1)), (A, (0.9, 0.9, 0.9)), (S, (1.18, 1.18, 1.18), "snap"), (H, (1.12, 1.12, 1.12)),
                         (R, (1, 1, 1))])
    halo_spin(c, L, 15.0, 22.5, extra_flame=[(0, 0), (A, 15, "in"), (H, 90, "out"), (R, 90)],
              extra_ray=[(0, 0), (A, -22.5, "in"), (H, -67.5, "out"), (R, -67.5)])
    robe_sway(c, L, 1.3, drop=drop, flare=lambda t: 7 * env(t, S - 0.05, S + 0.08, H - 0.2, R - 0.3, "out", "io"),
              drag=lambda t: -3 * env(t, 0.1, A, A, S) + 9 * env(t, S - 0.04, S + 0.1, S + 0.25, R - 0.3, "out", "io"))
    mantle_sway(c, L, 1.3, lift=lambda t: (10 * env(t, S - 0.04, S + 0.1, H - 0.3, R - 0.2, "out"),
                                           14 * env(t, S, S + 0.16, H - 0.2, R - 0.1, "out")))
    return c


def anim_sunburst():
    L = 1.6
    c = Clip("attack.sunburst", L)
    G, B, P, R = 0.8, 0.9, 1.05, 1.6          # gathered, burst, peak, recovered
    c.rot("torso", [(0, (0, 0, 0)), (G, (15, 0, 0), "io"), (B, (-14, 0, 0), "snap"), (P, (-12, 0, 0)), (R, (0, 0, 0), "io")])
    c.f("torso", "rotation", lambda t: (tremor(t, 0.4, G, G, B, 0.7, 22), 0, tremor(t, 0.4, G, G, B, 0.5, 18, 3)))
    drop = K([(0, 0.0), (G, 2.6, "io"), (B, -0.6, "snap"), (P, -0.5), (R, 0.0, "io")])
    c.f("body", "position", lambda t: (0, -float(drop(t)), 0))
    knee_bend(c, lambda t: float(drop(t)), THIGH, SHIN, LEGS, FEET, spread=0.4)
    c.rot("left_arm", [(0, (0, 0, 0)), (G, (-52, -12, 30)), (B, (-24, 0, -82), "snap"), (P, (-22, 0, -80)), (R, (0, 0, 0), "io")])
    c.rot("left_forearm", [(0, (0, 0, 0)), (G, (-72, 0, 0)), (B, (22, 0, 0), "snap"), (P, (20, 0, 0)), (R, (0, 0, 0))])
    c.rot("right_arm", [(0, (0, 0, 0)), (G, (-48, 12, -26)), (B, (-24, 0, 72), "snap"), (P, (-22, 0, 70)), (R, (0, 0, 0), "io")])
    c.rot("right_forearm", [(0, (0, 0, 0)), (G, (-30, 0, 0)), (B, (32, 0, 0), "snap"), (P, (30, 0, 0)), (R, (0, 0, 0))])
    staff_world(c, [(0, (0, 0, 0)), (G, (-6, 0, 6)), (B, (-4, 0, -22), "snap"), (P, (-4, 0, -20)), (R, (0, 0, 0))])
    staff_ground(c)
    c.rot("neck", [(0, (0, 0, 0)), (G, (12, 0, 0)), (B, (-14, 0, 0), "snap"), (P, (-12, 0, 0)), (R, (0, 0, 0))])
    c.pos("halo_mount", [(0, (0, 0, 0)), (G, (0, -1.2, 0.5)), (B, (0, 1.6, 0), "snap"), (P, (0, 1.4, 0)), (R, (0, 0, 0))])
    c.scl("halo_mount", [(0, (1, 1, 1)), (G, (0.8, 0.8, 0.8), "in"), (B, (1.4, 1.4, 1.4), "snap"), (P, (1.32, 1.32, 1.32)),
                         (R, (1, 1, 1), "io")])
    halo_spin(c, L, 15.0, 22.5, extra_flame=[(0, 0), (G, -15), (B + 0.3, 60, "out"), (R, 60)],
              extra_ray=[(0, 0), (G, 22.5), (B + 0.3, -45, "out"), (R, -45)])
    robe_sway(c, L, 1.2, drop=drop, flare=lambda t: -3 * env(t, 0.2, G, G, B) + 22 * env(t, G + 0.03, B + 0.05, P, R - 0.05, "snap", "io"))
    mantle_sway(c, L, 1.2, lift=lambda t: (20 * env(t, G + 0.03, B + 0.06, P, R, "snap"), 18 * env(t, G + 0.05, B + 0.1, P, R, "snap")))
    return c


def anim_corona_ring():
    L = 3.0
    c = Clip("attack.corona_ring", L)
    U, SP, D, I, H, R = 0.7, 1.5, 1.62, 1.78, 2.3, 3.0     # up, spin done, drive, impact, hold, recovered
    c.rot("torso", [(0, (0, 0, 0)), (U, (-8, 6, 0), "io"), (SP, (-10, 6, 0)), (D, (-12, 4, 0)), (I, (16, -4, 0), "in3"),
                    (H, (14, -4, 0)), (R, (0, 0, 0), "io")])
    c.f("torso", "rotation", lambda t: (tremor(t, U, U + 0.2, SP, D, 0.6, 20), tremor(t, I, I + 0.04, I + 0.3, H, 1.0, 26, 2), 0))
    drop = K([(0, 0.0), (U, -0.6), (SP, -0.8), (D, -0.8), (I, 3.4, "in3"), (H, 3.0), (R, 0.0, "io")])
    c.f("body", "position", lambda t: (0, -float(drop(t)), 0))
    knee_bend(c, lambda t: max(0.0, float(drop(t))), THIGH, SHIN, LEGS, FEET, spread=0.5)
    c.rot("right_arm", [(0, (0, 0, 0)), (U, (-150, 0, -4), "io"), (SP, (-152, 0, -4)), (D, (-160, 0, -4)),
                        (I, (-42, 0, 6), "in3"), (H, (-40, 0, 6)), (R, (0, 0, 0), "io")])
    c.rot("right_forearm", [(0, (0, 0, 0)), (U, (30, 0, 0)), (SP, (30, 0, 0)), (I, (-4, 0, 0), "in3"), (H, (-4, 0, 0)), (R, (0, 0, 0))])
    staff_world(c, [(0, (0, 0, 0)), (U, (0, 0, 0)), (D, (-8, 0, 0)), (I, (2, 0, 0), "in3"), (H, (2, 0, 0)), (R, (0, 0, 0))],
                [(0, 0.0), (U, 0.0), (SP, 720.0, "io"), (R, 720.0)])
    staff_ground(c)
    c.rot("left_arm", [(0, (0, 0, 0)), (U, (-128, 0, -24), "io"), (SP, (-130, 0, -26)), (D, (-136, 0, -24)),
                       (I, (-12, 0, -46), "in3"), (H, (-10, 0, -44)), (R, (0, 0, 0), "io")])
    c.rot("left_forearm", [(0, (0, 0, 0)), (U, (14, 0, 0)), (I, (12, 0, 0)), (R, (0, 0, 0))])
    c.rot("neck", [(0, (0, 0, 0)), (U, (-12, 0, 0)), (D, (-14, 0, 0)), (I, (10, 0, 0), "in3"), (H, (8, 0, 0)), (R, (0, 0, 0))])
    c.pos("halo_mount", [(0, (0, 0, 0)), (U, (0, 4.0, 1.0), "io"), (SP, (0, 4.5, 1.0)), (D, (0, 5.0, 1.0)), (I, (0, -0.5, 0), "in3"),
                         (H, (0, 0, 0)), (R, (0, 0, 0))])
    c.scl("halo_mount", [(0, (1, 1, 1)), (U, (1.3, 1.3, 1.3), "io"), (SP, (1.36, 1.36, 1.36)), (I, (0.92, 0.92, 0.92), "in3"),
                         (I + 0.14, (1.32, 1.32, 1.32), "snap"), (H + 0.2, (1.0, 1.0, 1.0), "io"), (R, (1, 1, 1))])
    halo_spin(c, L, 15.0, 22.5, extra_flame=[(0, 0), (0.3, 0), (SP, 180, "io"), (I + 0.3, 240, "out"), (R, 240)],
              extra_ray=[(0, 0), (0.3, 0), (SP, -135, "io"), (I + 0.3, -180, "out"), (R, -180)])
    robe_sway(c, L, 1.4, 2, drop=drop, flare=lambda t: 4 * env(t, 0.2, U, SP, D) + 24 * env(t, I - 0.04, I + 0.08, I + 0.2, H + 0.4, "snap", "io"),
              drag=lambda t: flutter(t, 2.5 * env(t, U, U + 0.3, SP, D), 4.0))
    mantle_sway(c, L, 1.4, 2, lift=lambda t: (4 * env(t, 0.2, U, SP, D) + 18 * env(t, I - 0.02, I + 0.1, I + 0.25, H + 0.4, "snap"),
                                              6 * env(t, 0.2, U, SP, D) + 16 * env(t, I, I + 0.14, I + 0.3, H + 0.5, "snap")))
    return c


def anim_eclipse():
    L = 3.0
    c = Clip("attack.eclipse", L)
    RAISE, TOP, FRONT, COVER, CL, HOLD, LEAVE = 0.5, 0.85, 1.0, 1.45, 1.6, 2.25, 2.55
    c.rot("left_arm", [(0, (0, 0, 0)), (RAISE, (-22, 0, -108), "io"), (COVER - 0.05, (-26, 0, -114)), (CL, (-38, 0, -42), "snap"),
                       (HOLD, (-36, 0, -40)), (L, (0, 0, 0), "io")])
    c.rot("left_forearm", [(0, (0, 0, 0)), (RAISE, (12, 0, 0)), (COVER - 0.05, (14, 0, 0)), (CL, (-46, 0, 0), "snap"), (HOLD, (-44, 0, 0)),
                           (L, (0, 0, 0))])
    c.rot("right_arm", [(0, (0, 0, 0)), (RAISE, (-22, 0, 100), "io"), (COVER - 0.05, (-24, 0, 104)), (CL, (-34, 0, 36), "snap"),
                        (HOLD, (-32, 0, 34)), (L, (0, 0, 0), "io")])
    c.rot("right_forearm", [(0, (0, 0, 0)), (RAISE, (24, 0, 0)), (CL, (-20, 0, 0), "snap"), (HOLD, (-18, 0, 0)), (L, (0, 0, 0))])
    staff_world(c, [(0, (0, 0, 0)), (RAISE, (0, 0, -14)), (COVER - 0.05, (0, 0, -16)), (CL, (6, 0, -4), "snap"), (HOLD, (5, 0, -3)),
                    (L, (0, 0, 0))])
    staff_ground(c)
    c.rot("torso", [(0, (0, 0, 0)), (RAISE, (-9, 0, 0)), (COVER - 0.05, (-11, 0, 0)), (CL, (12, 0, 0), "snap"), (HOLD, (10, 0, 0)),
                    (L, (0, 0, 0), "io")])
    c.f("torso", "rotation", lambda t: (tremor(t, CL, CL + 0.05, HOLD - 0.2, HOLD, 0.7, 23), tremor(t, CL, CL + 0.05, HOLD - 0.2, HOLD, 0.5, 17, 1), 0))
    c.rot("neck", [(0, (0, 0, 0)), (RAISE, (-15, 0, 0)), (COVER - 0.05, (-16, 0, 0)), (CL, (8, 0, 0), "snap"), (HOLD, (7, 0, 0)),
                   (L, (0, 0, 0))])
    drop = K([(0, 0.0), (COVER - 0.05, 0.0), (CL, 2.2, "snap"), (HOLD, 2.0), (L, 0.0)])
    c.f("body", "position", lambda t: (0, -float(drop(t)), 0))
    knee_bend(c, lambda t: float(drop(t)), THIGH, SHIN, LEGS, FEET, spread=0.4)
    # the eclipse moon rises out from between the halo layers, comes forward and falls over the sun
    c.pos("eclipse", [(0, (0, 0, 0)), (0.35, (0, 0, 0)), (TOP, (0, 30, 0), "io"), (FRONT, (0, 30, -1.6), "io"), (COVER, (0, 0, -1.6), "in"),
                      (HOLD, (0, 0, -1.6)), (LEAVE, (0, 30, -1.6), "out"), (LEAVE + 0.12, (0, 30, 0)), (L - 0.05, (0, 0, 0), "io"),
                      (L, (0, 0, 0))])
    c.scl("halo_mount", [(0, (1, 1, 1)), (RAISE, (1.1, 1.1, 1.1)), (COVER, (1.1, 1.1, 1.1)), (CL, (1.3, 1.3, 1.3), "snap"),
                         (HOLD, (1.18, 1.18, 1.18)), (L, (1, 1, 1), "io")])
    c.pos("halo_mount", [(0, (0, 0, 0)), (RAISE, (0, 1.0, 0)), (COVER, (0, 1.0, 0)), (CL, (0, 0.2, 0), "snap"), (L, (0, 0, 0))])
    halo_spin(c, L, 15.0, 22.5, extra_flame=[(0, 0), (RAISE, 15), (COVER, 30), (HOLD, 120, "io"), (L, 135, "out")],
              extra_ray=[(0, 0), (RAISE, -22.5), (COVER, -45), (HOLD, -225, "io"), (L, -247.5, "out")])
    robe_sway(c, L, 1.4, 2, drop=drop, flare=lambda t: 2 * env(t, 0.1, RAISE, COVER, CL) + 15 * env(t, COVER, CL + 0.05, CL + 0.2, HOLD + 0.3, "snap", "io"))
    mantle_sway(c, L, 1.4, 2, lift=lambda t: (12 * env(t, COVER, CL + 0.06, CL + 0.2, HOLD + 0.3, "snap"),
                                              12 * env(t, COVER + 0.02, CL + 0.1, CL + 0.25, HOLD + 0.4, "snap")))
    return c


def anim_supernova():
    L = 4.0
    c = Clip("attack.supernova", L)
    W0, CH, REL, IMP, R = 0.6, 3.0, 3.0, 3.18, 4.0
    charge = lambda t: tl.ease("io", (t - W0) / (CH - W0))          # 0..1 over the charge
    grow = lambda t: tl.ease("in", (t - W0) / (CH - W0))
    lev = K([(0, 0.0), (W0, 0.0), (2.4, 4.5, "io"), (CH, 4.8), (IMP, -2.6, "in3"), (IMP + 0.35, -2.0), (R, 0.0, "io")])
    c.f("body", "position", lambda t: (0, float(lev(t)), 0))
    knee_bend(c, lambda t: max(0.0, -float(lev(t))), THIGH, SHIN, LEGS, FEET, spread=0.5)
    dangle = lambda t: float(fx.smoothstep(1.2, 4.5, float(lev(t))))
    for s, nm in sides():
        c.f(f"{nm}_leg", "rotation", lambda t, s=s: (7 * dangle(t), 0, 3 * s * dangle(t)))
        c.f(f"{nm}_shin", "rotation", lambda t: (16 * dangle(t), 0, 0))
        c.f(f"{nm}_foot", "rotation", lambda t: (26 * dangle(t), 0, 0))
    c.rot("torso", [(0, (0, 0, 0)), (W0, (7, 0, 0)), (2.4, (-12, 0, 0), "io"), (CH, (-15, 0, 0)), (IMP, (20, 0, 0), "in3"),
                    (IMP + 0.35, (17, 0, 0)), (R, (0, 0, 0), "io")])
    c.f("torso", "rotation", lambda t: (shake_up(t, W0, CH, 1.6, 23), shake_up(t, W0, CH, 1.2, 19, 2), shake_up(t, W0, CH, 0.8, 29, 5)))
    c.rot("neck", [(0, (0, 0, 0)), (W0, (6, 0, 0)), (2.4, (-15, 0, 0)), (CH, (-18, 0, 0)), (IMP, (12, 0, 0), "in3"), (R, (0, 0, 0), "io")])
    c.rot("left_arm", [(0, (0, 0, 0)), (W0, (-34, 0, 12)), (2.4, (-30, 0, -98), "io"), (CH, (-34, 0, -104)), (IMP, (-62, 0, -18), "in3"),
                       (IMP + 0.35, (-58, 0, -16)), (R, (0, 0, 0), "io")])
    c.rot("left_forearm", [(0, (0, 0, 0)), (W0, (-52, 0, 0)), (2.4, (16, 0, 0)), (IMP, (22, 0, 0), "in3"), (IMP + 0.35, (20, 0, 0)), (R, (0, 0, 0))])
    c.rot("right_arm", [(0, (0, 0, 0)), (W0, (-28, 0, -8)), (2.4, (-30, 0, 90), "io"), (CH, (-34, 0, 96)), (IMP, (-48, 0, 12), "in3"),
                        (IMP + 0.35, (-46, 0, 10)), (R, (0, 0, 0), "io")])
    c.rot("right_forearm", [(0, (0, 0, 0)), (W0, (-14, 0, 0)), (2.4, (26, 0, 0)), (IMP, (8, 0, 0), "in3"), (R, (0, 0, 0))])
    staff_world(c, [(0, (0, 0, 0)), (W0, (0, 0, 0)), (2.4, (0, 0, -12)), (CH, (0, 0, -14)), (IMP, (16, 0, 0), "in3"),
                    (IMP + 0.35, (14, 0, 0)), (R, (0, 0, 0), "io")])
    staff_ground(c)
    c.f("halo_mount", "scale", lambda t: (sn_scale(t),) * 3)
    c.pos("halo_mount", [(0, (0, 0, 0)), (W0, (0, 0, 0)), (CH, (0, 3.0, 1.5), "io"), (IMP, (0, -0.5, 0.5), "in3"), (R, (0, 0, 0), "io")])
    c.f("halo_mount", "position", lambda t: (shake_up(t, W0, CH, 0.55, 31), shake_up(t, W0, CH, 0.55, 27, 3), 0))
    c.f("halo_mount", "rotation", lambda t: (0, 0, shake_up(t, W0, CH, 2.0, 13, 7)))
    halo_spin(c, L, 15.0, 22.5, extra_flame=[(0, 0), (W0, 0), (CH, 600, "in"), (CH + 0.3, 660, "out"), (L, 660)],
              extra_ray=[(0, 0), (W0, 0), (CH, -540, "in"), (CH + 0.3, -585, "out"), (L, -585)])
    robe_sway(c, L, 1.4, 4, drop=lambda t: -float(lev(t)), flare=lambda t: 16 * charge(t) * (t < CH) + flutter(t, 3.5 * grow(t) * (t < CH), 7.0)
              + (16 * (1 - tl.ease("in3", (t - CH) / (IMP - CH))) if CH <= t < IMP else 0)
              + 26 * env(t, IMP - 0.04, IMP + 0.04, IMP + 0.15, R - 0.15, "snap", "io"))
    mantle_sway(c, L, 1.4, 4, lift=lambda t: (24 * charge(t) * (t < CH) + flutter(t, 4 * grow(t) * (t < CH), 6.0, 0.5)
                                              + 20 * env(t, IMP - 0.04, IMP + 0.08, IMP + 0.2, R - 0.1, "snap"),
                                              16 * charge(t) * (t < CH) + flutter(t, 6 * grow(t) * (t < CH), 6.0, 1.4)
                                              + 18 * env(t, IMP, IMP + 0.12, IMP + 0.25, R, "snap")))
    return c


def shake_up(t, t0, t1, amp, freq, seed=0):
    """Tremor that grows from 0 at t0 to amp at t1, then stops."""
    if t <= t0 or t >= t1:
        return 0.0
    return tl.shake(t, freq, amp * ((t - t0) / (t1 - t0)) ** 1.6, seed)


SN_SCALE = K([(0, 1.0), (0.6, 1.0), (3.0, 1.5, "in"), (3.12, 1.85, "snap"), (3.6, 1.0, "io"), (4.0, 1.0)])


def sn_scale(t):
    return float(SN_SCALE(t)) + (0.04 * math.sin(TAU * 9 * t) * ((t - 0.6) / 2.4) if 0.6 < t < 3.0 else 0.0)


def anim_phase():
    L = 2.0
    c = Clip("phase", L)
    CR, RO, HO, R = 0.5, 0.75, 1.5, 2.0
    c.rot("torso", [(0, (0, 0, 0)), (CR, (18, 0, 0), "io"), (RO, (-18, 0, 0), "snap"), (HO, (-16, 0, 0)), (R, (0, 0, 0), "io")])
    c.f("torso", "rotation", lambda t: (tremor(t, RO, RO + 0.05, HO - 0.15, HO, 1.3, 24), tremor(t, RO, RO + 0.05, HO - 0.15, HO, 1.0, 19, 3), 0))
    drop = K([(0, 0.0), (CR, 3.0, "io"), (RO, -0.8, "snap"), (HO, -0.6), (R, 0.0, "io")])
    c.f("body", "position", lambda t: (0, -float(drop(t)), 0))
    knee_bend(c, lambda t: max(0.0, float(drop(t))), THIGH, SHIN, LEGS, FEET, spread=0.5)
    c.rot("neck", [(0, (0, 0, 0)), (CR, (12, 0, 0)), (RO, (-24, 0, 0), "snap"), (HO, (-22, 0, 0)), (R, (0, 0, 0), "io")])
    c.f("head", "rotation", lambda t: (0, 0, tremor(t, RO, RO + 0.05, HO - 0.15, HO, 2.0, 21, 4)))
    c.rot("left_arm", [(0, (0, 0, 0)), (CR, (-22, 0, 16)), (RO, (-36, 0, -86), "snap"), (HO, (-34, 0, -84)), (R, (0, 0, 0), "io")])
    c.rot("left_forearm", [(0, (0, 0, 0)), (CR, (-62, 0, 0)), (RO, (20, 0, 0), "snap"), (HO, (18, 0, 0)), (R, (0, 0, 0))])
    c.rot("right_arm", [(0, (0, 0, 0)), (CR, (-20, 0, -12)), (RO, (-36, 0, 80), "snap"), (HO, (-34, 0, 78)), (R, (0, 0, 0), "io")])
    c.rot("right_forearm", [(0, (0, 0, 0)), (CR, (-28, 0, 0)), (RO, (28, 0, 0), "snap"), (HO, (26, 0, 0)), (R, (0, 0, 0))])
    staff_world(c, [(0, (0, 0, 0)), (CR, (-4, 0, 4)), (RO, (-6, 0, -18), "snap"), (HO, (-5, 0, -16)), (R, (0, 0, 0))])
    staff_ground(c)
    c.pos("halo_mount", [(0, (0, 0, 0)), (CR, (0, -1.2, 0)), (RO, (0, 2.2, 0.5), "snap"), (HO, (0, 2.0, 0.5)), (R, (0, 0, 0), "io")])
    c.scl("halo_mount", [(0, (1, 1, 1)), (CR, (0.84, 0.84, 0.84)), (RO, (1.45, 1.45, 1.45), "snap"), (HO, (1.38, 1.38, 1.38)),
                         (R, (1, 1, 1), "io")])
    c.f("halo_mount", "position", lambda t: (tremor(t, RO, RO + 0.05, HO - 0.15, HO, 0.3, 27), tremor(t, RO, RO + 0.05, HO - 0.15, HO, 0.3, 23, 2), 0))
    halo_spin(c, L, 15.0, 22.5, extra_flame=[(0, 0), (CR, -15), (HO, 120, "out"), (R, 120)],
              extra_ray=[(0, 0), (CR, 22.5), (HO, -90, "out"), (R, -90)])
    robe_sway(c, L, 1.3, drop=drop, flare=lambda t: -3 * env(t, 0.1, CR, CR, RO) + 20 * env(t, CR + 0.05, RO + 0.05, HO - 0.2, R - 0.1, "snap", "io")
              + flutter(t, 3 * env(t, RO, RO + 0.1, HO - 0.2, HO), 6.0))
    mantle_sway(c, L, 1.3, lift=lambda t: (20 * env(t, CR + 0.05, RO + 0.08, HO - 0.2, R, "snap"), 18 * env(t, CR + 0.1, RO + 0.12, HO - 0.1, R, "snap")))
    return c


def anim_death():
    L = 2.8
    c = Clip("death", L, loop="hold")
    KD = 11.1                                  # kneeling drop: knees on the ground, shins back
    drop = K([(0, 0.0), (0.25, -0.5, "out"), (0.9, 0.5), (1.65, KD, "in"), (1.8, KD - 0.6, "out"), (1.95, KD, "in"), (L, KD)])
    kneel = lambda t: min(1.0, max(0.0, float(drop(t)) / KD))
    c.f("body", "position", lambda t: (0, -float(drop(t)), 0))
    c.rot("body", [(0, (0, 0, 0)), (0.25, (0, 0, 3)), (1.0, (0, 0, -2)), (1.8, (0, 0, 0)), (L, (0, 0, 0))])

    def kneel_targets(nm, t):
        k = kneel(t)
        lag = 0.85 if nm == "right" else 1.0
        kk = min(1.0, k / lag)
        return 0.3 + 8.4 * kk, 2.5 + 0.8 * kk + 1.2 * math.sin(math.pi * kk), -150.0 * fx.smoothstep(0.35, 1.0, kk)
    legs_ik(c, kneel_targets, lambda t: (-float(drop(t)), 0.0))
    c.rot("torso", [(0, (0, 0, 0)), (0.25, (-16, 0, 4), "out"), (1.0, (-6, 0, 3)), (1.8, (14, 0, 4), "io"), (2.4, (20, 0, 5), "io"),
                    (L, (20, 0, 5))])
    c.f("torso", "rotation", lambda t: (tremor(t, 0.15, 0.25, 1.0, 1.4, 2.2, 20), tremor(t, 0.15, 0.25, 1.0, 1.4, 1.8, 17, 2), 0))
    c.rot("neck", [(0, (0, 0, 0)), (0.25, (-12, 0, 0), "out"), (1.2, (-4, 0, 0)), (2.4, (30, 0, 0), "io"), (L, (30, 0, 0))])
    c.rot("head", [(0, (0, 0, 0)), (1.6, (0, 0, 0)), (2.4, (0, 0, -9), "io"), (L, (0, 0, -9))])
    # right hand keeps the staff and leans on it as he sinks to his knees
    c.rot("right_arm", [(0, (0, 0, 0)), (0.25, (-18, 0, 10), "out"), (1.0, (-10, 0, 4)), (1.8, (-56, 0, 2), "io"), (2.4, (-58, 0, 2)),
                        (L, (-58, 0, 2))])
    c.rot("right_forearm", [(0, (0, 0, 0)), (0.25, (-10, 0, 0)), (1.8, (-20, 0, 0)), (L, (-20, 0, 0))])
    staff_world(c, [(0, (0, 0, 0)), (0.25, (-6, 0, 5), "out"), (1.0, (3, 0, -2)), (1.8, (8, 0, 2), "io"), (L, (8, 0, 2))])
    staff_ground(c)
    c.rot("left_arm", [(0, (0, 0, 0)), (0.25, (-26, 0, -34), "out"), (1.0, (-8, 0, -12)), (1.9, (12, 0, 0), "io"), (L, (12, 0, 0))])
    c.rot("left_forearm", [(0, (0, 0, 0)), (0.25, (-30, 0, 0)), (1.9, (12, 0, 0)), (L, (12, 0, 0))])
    # the sun dies: the moon covers it, the halo falters, sinks and tilts
    c.pos("eclipse", [(0, (0, 0, 0)), (0.5, (0, 0, 0)), (1.0, (0, 30, 0), "io"), (1.15, (0, 30, -1.6), "io"), (1.9, (0, 0, -1.6), "in"),
                      (L, (0, 0, -1.6))])
    c.pos("halo_mount", [(0, (0, 0, 0)), (0.25, (0, 1.0, 0)), (1.9, (0, -1.0, 0.3)), (2.5, (0, -3.0, 0.6), "io"), (L, (0, -3.0, 0.6))])
    # counter the torso lean so the dying halo stays nearly upright (only a slight droop)
    c.rot("halo_mount", [(0, (0, 0, 0)), (0.25, (12, 0, 4), "out"), (1.0, (4, 0, -3)), (1.8, (-11, 0, -4), "io"), (2.5, (-15, 0, -7), "io"),
                         (L, (-15, 0, -7))])
    c.f("halo_mount", "rotation", lambda t: (0, 0, tremor(t, 0.1, 0.2, 1.0, 1.5, 3.0, 11)))
    c.scl("halo_mount", [(0, (1, 1, 1)), (0.25, (1.12, 1.12, 1.12), "out"), (1.0, (1.0, 1.0, 1.0)), (2.5, (0.9, 0.9, 0.9), "io"),
                         (L, (0.9, 0.9, 0.9))])
    c.rot("halo", [(0, (0, 0, 0)), (0.3, (0, 0, 40), "out"), (0.45, (0, 0, 28)), (1.2, (0, 0, 75), "out"), (2.2, (0, 0, 84), "out"),
                   (L, (0, 0, 84))])
    c.rot("halo_rays", [(0, (0, 0, 0)), (0.3, (0, 0, -30), "out"), (0.5, (0, 0, -20)), (1.2, (0, 0, -55), "out"), (2.2, (0, 0, -62), "out"),
                        (L, (0, 0, -62))])
    # robe pools as he kneels: panels flare and shorten so the hem stays on the ground
    pool = lambda th: 14.0 if abs(th) <= 45 else (4.0 if abs(th) == 90 else 10.0)
    robe_sway(c, L, 1.2, flare=lambda t: 3 * env(t, 0.0, 0.25, 0.3, 0.9),
              drag=lambda t: -2 * env(t, 0.0, 0.25, 0.3, 0.9),
              extra=lambda th, t: flare_rot(th, pool(th) * kneel(t)))
    for nm, *_ in ROBE:
        c.f(nm, "scale", lambda t: (1.0, 1.0 - 0.4 * kneel(t), 1.0))
    # upper mantle hangs plumb despite the forward lean; the lower half folds back onto the ground
    mantle_sway(c, L, 1.2, lift=lambda t: (6 * env(t, 0, 0.25, 0.3, 0.9) - 17 * kneel(t), 54 * kneel(t)))
    return c


def clips():
    return [anim_idle(), anim_walk(), anim_solar_flare(), anim_sunburst(), anim_corona_ring(), anim_eclipse(),
            anim_supernova(), anim_phase(), anim_death()]


POSES = [
    ("idle", [0.0, 1.0, 2.0, 3.0]),
    ("walk", [0.0, 0.4, 0.8, 1.2]),
    ("attack.solar_flare", [0.3, 0.55, 0.8, 1.6]),
    ("attack.sunburst", [0.5, 0.8, 0.95, 1.3]),
    ("attack.corona_ring", [0.7, 1.2, 1.8, 2.5]),
    ("attack.eclipse", [0.6, 0.9, 1.3, 1.8, 2.6]),
    ("attack.supernova", [0.6, 1.8, 2.9, 3.15, 3.6]),
    ("phase", [0.5, 0.8, 1.3]),
    ("death", [0.25, 1.2, 1.8, 2.8]),
]
HERO = ("attack.supernova", 2.9)


def main():
    m = build_model()
    geo, rgba, glow, anims = tl.build(NAME, m, SHADERS, clips(), visible=(6, 7, 3.0))
    if "--preview" in sys.argv:
        print(fx.preview_rest(NAME, geo, rgba, glow, HITBOX))
        if "--hero" in sys.argv or "--all" in sys.argv:
            print(fx.preview_pose(NAME, geo, rgba, glow, anims, HERO[0], HERO[1]))
        if "--all" in sys.argv:
            for an, times in POSES:
                print(fx.preview_strip(NAME, geo, rgba, glow, anims, an, times, HITBOX))
            print(fx.preview_strip(NAME, geo, rgba, glow, anims, "walk", [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4],
                                   HITBOX, yaw=90, pitch=-4, tag="_side"))
    return m, geo, rgba, glow, anims


if __name__ == "__main__":
    main()
