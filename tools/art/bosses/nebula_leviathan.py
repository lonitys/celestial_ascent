"""Nebula Leviathan: a cosmic star-serpent. A long tapering body of overlapping purple-and-blue nebula
scales with pale ventral scutes, a continuous star-speckled dorsal sail with a thin edge light, broad
pectoral fins, a forked tail fan, swept horns, fan-shaped cheek frills, trailing whiskers, icy glowing
eyes and a glowing magenta maw and throat.

Rig: root -> body (front torso, over the hitbox) -> neck -> head -> jaw; body -> seg1 -> ... -> seg8 ->
tail -> fan (each parented to the previous). The rest pose carries a gentle S-curve (segment rest
rotations); every clip authors absolute joint angles and subtracts the rest rotation.

Run: python nebula_leviathan.py [--preview] [--all]
"""
import math
import sys

import numpy as np

import bosslib as tl
import geo_preview as gp
import nebula_leviathan_mats as nm
import nebula_leviathan_view as nv
from bosslib import Clip, Track, ease, env, shake
from rig import TAU, tremor

NAME = "nebula_leviathan"
HITBOX = (2.6, 2.0)
YC = 15.0       # body centre line height
ZOFF = 8.0      # whole model shifted back so the head/neck/body sit over the hitbox

# (bone, z_front, length, width, height, sail height, scale size)
BODY = ("body", -6, 16, 14, 13, 4, 4.0)
SEGS = [
    ("seg1", 10, 11, 13, 12, 6, 3.8),
    ("seg2", 21, 10, 12, 11, 6, 3.7),
    ("seg3", 31, 10, 11, 10, 5, 3.5),
    ("seg4", 41, 9, 10, 9, 5, 3.3),
    ("seg5", 50, 9, 9, 8, 4, 3.1),
    ("seg6", 59, 8, 8, 7, 4, 2.9),
    ("seg7", 67, 8, 7, 6, 3, 2.6),
    ("seg8", 75, 7, 6, 5, 3, 2.4),
    ("tail", 82, 7, 4, 4, 2, 2.1),
]
CHAIN = ["body"] + [s[0] for s in SEGS]
NCH = len(CHAIN)
NECK_PIVOT = np.array([0.0, 16.0, -5.0])
NECK_TILT = -16.0
HEAD_LIFT = 1.5

# =============================================================================== chain motion model
PHI_Y = TAU * 1.15 / (NCH - 1)       # spatial phase step of the lateral wave per segment
PHI_P = TAU * 0.7 / (NCH - 1)       # vertical wave
# absolute pitch heading of each chain element (deg, + = rising towards the tail): a slow vertical S
STATIC_P = [0, -9, -15, -10, 3, 13, 15, 6, -4, 6]
IDLE_T = 4.0
IDLE_YA = (3.0, 27.0)
IDLE_PA = (0.0, 7.0)


def heading(k, ph, a0, a1, phi, off=0.0, power=0.85):
    if k < 0:
        return 0.0
    f = k / (NCH - 1)
    return (a0 + (a1 - a0) * f ** power) * math.sin(ph - k * phi + off)


def wave_joint(k, ph, ya, pa):
    """Joint rotation (x, y, z) of chain element k for a travelling wave at phase ph (radians)."""
    yaw = heading(k, ph, ya[0], ya[1], PHI_Y) - heading(k - 1, ph, ya[0], ya[1], PHI_Y)
    pit = heading(k, ph, pa[0], pa[1], PHI_P, 1.4) - heading(k - 1, ph, pa[0], pa[1], PHI_P, 1.4)
    roll = -0.25 * (heading(k, ph, ya[0], ya[1], PHI_Y) - heading(k - 1, ph, ya[0], ya[1], PHI_Y)) if k else 0.0
    return np.array([pit, yaw, roll])


def static_joint(k):
    return np.array([STATIC_P[k] - (STATIC_P[k - 1] if k else 0.0), 0.0, 0.0])


REST = [np.zeros(3)] + [np.round(wave_joint(k, 0.0, IDLE_YA, IDLE_PA) + static_joint(k), 3) for k in range(1, NCH)]

# =============================================================================== geometry


def frame(A, B):
    """Rotation taking plane-local +X to A and plane-local -Y (texture down) to B."""
    A = tl.unit(A)
    B = np.asarray(B, dtype=float)
    B = tl.unit(B - A * float(A @ B))
    ex, ey = A, -B
    return np.column_stack([ex, ey, np.cross(ex, ey)])


def neck_pt(p):
    R = gp.rot_b([NECK_TILT, 0, 0])
    return NECK_PIVOT + R @ (np.asarray(p, dtype=float) - NECK_PIVOT)


def segment(b, z0, L, W, H, sail0, sail1, P, ov=3.5, ridge=True):
    """One body segment along +Z from its pivot at z0. The core reaches ov units back inside the
    (strictly larger) previous segment to hide the joint when it bends; belly, ridge and sail pieces
    butt against their neighbours instead of overlapping, so nothing is ever coplanar (no z-fighting
    when a joint passes through zero)."""
    zc = z0 + (L + 0.5 - ov) / 2
    b.box((0, YC, zc), (W, H, L + 0.5 + ov), "scales", P=P)
    if ridge:
        b.box((0, YC + H / 2 + 0.2, z0 + L / 2), (max(2, int(round(W * 0.5))), 1, L), "ridge", P=P * 0.8)
    bw = max(2, int(round(W * 0.66)))
    b.box((0, YC - H / 2 - 0.4, z0 + L / 2 + 0.25), (bw, 2, L), "belly", Pb=max(1.2, P * 0.68))
    sh = max(sail0, sail1)
    if sh > 0:
        b.plane_from((0, YC + H / 2 + 0.5, z0), L, sh, "fin", rot=[0, -90, 0], anchor_st=(0, 1),
                     kind="dorsal", h0=sail0, h1=sail1, sp=max(2.2, P * 1.1), xoff=z0)


def build_model():
    m = tl.Model(NAME)
    # ---------------------------------------------------------------- body (front torso)
    _, z0, L, W, H, sail, P = BODY
    body = m.bone("body", "root", (0, YC, 2))
    segment(body, z0, L, W, H, sail, SEGS[0][5], P, ov=0.0)
    body.box((0, YC - 2.0, -5.5), (11, 8, 2), "scales_plain", P=3.4)            # chest under the neck
    for s, nm_ in ((-1, "right"), (1, "left")):
        fb = m.bone(f"fin_{nm_}", "body", (6.8 * s, YC - 3, -2))
        fb.plane_from((6.8 * s, YC - 3, -2), 28, 15, "fin", rot=frame((1.0 * s, -0.16, 0.3), (-0.1 * s, -0.12, 1)),
                      anchor_st=(0, 0), kind="pectoral")

    # ---------------------------------------------------------------- neck
    neck = m.bone("neck", "body", tuple(NECK_PIVOT))
    tilt = [NECK_TILT, 0, 0]
    piv = tuple(NECK_PIVOT)
    neck.box((0, 17.0, -10.5), (12, 11, 13), "scales", rot=tilt, pivot=piv, P=3.4)
    neck.box((0, 22.7, -10.5), (6, 1, 13), "ridge", rot=tilt, pivot=piv, P=2.8)
    neck.box((0, 11.2, -10.5), (8, 2, 12), "throat", rot=tilt, pivot=piv, Pb=1.5)
    # neck sail ends where the body sail begins (both lie in x = 0, so they must not overlap)
    neck.plane_from(neck_pt((0, 23.0, -16.6)), 7, 4, "fin", rot=gp.rot_b(tilt) @ gp.rot_b([0, -90, 0]),
                    anchor_st=(0, 1), kind="dorsal", h0=2.5, h1=4, sp=2.8, xoff=-17.5)

    # ---------------------------------------------------------------- head (zero rest rotation!)
    head = m.bone("head", "neck", (0, 20, -16))
    mz = (-43, -17)
    head.box((0, 24, -22), (15, 8, 12), "head", palate=True, maw_z=mz)               # cranium
    head.box((0, 28.4, -21.5), (5, 1, 9), "head")                                    # crest plate
    head.box((0, 22.5, -32), (12, 5, 8), "head", palate=True, maw_z=mz)              # snout base
    head.box((0, 22, -39.5), (10, 4, 7), "head", palate=True, maw_z=mz)              # nose
    head.box((0, 25.5, -31.5), (8, 2, 10), "head", rot=[11, 0, 0])                   # nasal bridge
    head.box((0, 17.8, -16.6), (9, 4, 2), "maw_deep")                                # glowing throat
    head.plane((0, 18.5, -43.1), 10, 3, "teeth", down=True, fangs=[1.3, 8.7], only_fangs=True, fang_w=1.2)
    for s in (-1, 1):
        head.box((2.4 * s, 24.3, -41.2), (2, 1, 3), "head")                                  # nostril ridge
        head.box((7.4 * s, 22.8, -20.5), (3, 7, 10), "head", scaled=True, rot=[0, 14 * s, 0])  # cheek plate
        head.box((5.0 * s, 28.2, -27.5), (6, 2, 9), "head", rot=[10, 14 * s, -12 * s])       # brow ridge
        head.box((7.0 * s, 25.2, -28.8), (1, 3, 6), "eye", rot=[0, 30 * s, 0], side=s)        # eye
        head.box((6.6 * s, 18.5, -21.5), (2, 5, 9), "head", scaled=True)                      # jowl
        head.curve_spike((4.4 * s, 27.8, -20), [(0.25 * s, 0.8, 0.5), (0.3 * s, 0.32, 1.0), (0.18 * s, 0.2, 1.0)],
                         [7, 8, 8], [4, 3, 1.6], "horn")                                      # main horn
        head.curve_spike((7.8 * s, 18.5, -17.5), [(0.7 * s, -0.25, 0.7), (0.35 * s, 0.0, 1.0)], [5, 5], [2.2, 1.2],
                         "horn")                                                              # cheek spike
        head.plane_from((4.85 * s, 20, -42.8), 12, 2, "teeth", rot=[0, -90, 0], anchor_st=(0, 0), down=True,
                        fangs=[1.8], tw=1.5)                                                  # upper side teeth

    jaw = m.bone("jaw", "head", (0, 19.5, -18.5))
    tz = (-42, -18)
    jaw.box((0, 18, -24), (11, 4, 12), "jaw", tongue_z=tz)                              # jaw back
    jaw.box((0, 18, -36), (9, 4, 12), "jaw", tongue_z=tz)                               # jaw front
    jaw.box((0, 15.5, -37), (7, 1, 8), "head", scaled=True)                             # chin
    jaw.curve_spike((0, 15.5, -38.5), [(0, -0.75, 0.6), (0, -0.2, 1.0)], [4, 4], [2.2, 1.2], "horn")  # beard spike
    jaw.box((0, 15.6, -25), (8, 1, 13), "throat", Pb=1.4)                               # gular plates
    jaw.plane((0, 21, -41.6), 8, 2, "teeth", down=False, fangs=[1.1, 6.9], tw=1.2)
    for s in (-1, 1):
        jaw.plane_from((4.0 * s, 20, -41), 10, 2, "teeth", rot=[0, -90, 0], anchor_st=(0, 1), down=False, tw=1.4)
        jaw.curve_spike((5.3 * s, 16.5, -21), [(0.45 * s, -0.55, 0.7)], [5], [2], "horn")

    for s, nm_ in ((-1, "right"), (1, "left")):
        fr = m.bone(f"frill_{nm_}", "head", (8.0 * s, 21.8, -17.5))
        fr.plane_from((8.0 * s, 21.8, -17.5), 15, 24, "fin", rot=frame((0.9 * s, 0.12, 0.42), (0, -1, 0.15)),
                      anchor_st=(0, 0.5), kind="frill")
        wh = m.bone(f"whisker_{nm_}", "head", (5.0 * s, 21.5, -40))
        A = np.array([0.32 * s, -0.42, 1.0])
        B1 = np.array([0.7 * s, -0.7, 0.0])
        B2 = np.cross(tl.unit(A), tl.unit(B1))
        for B in (B1, B2):
            wh.plane_from((5.0 * s, 21.5, -40), 28, 9, "fin", rot=frame(A, B), anchor_st=(0, 0.5), kind="whisker",
                          amp=2.2)

    # ---------------------------------------------------------------- tail chain
    parent = "body"
    for k, (name, z0, L, W, H, sail, P) in enumerate(SEGS):
        nxt = SEGS[k + 1][5] if k + 1 < len(SEGS) else 2
        b = m.bone(name, parent, (0, YC, z0), rotation=list(REST[k + 1]))
        segment(b, z0, L, W, H, sail, nxt, P, ridge=W >= 7)
        if name == "seg3":
            sc = 1.0
            for s in (-1, 1):
                b.plane_from((W / 2 * s, YC - H / 2 + 2.5, z0 + 1.5), int(16 * sc), int(9 * sc), "fin",
                             rot=frame((1.0 * s, -0.55, 0.35), (0, -0.1, 1)), anchor_st=(0, 0), kind="pectoral",
                             figure=False)
        parent = name
    tail = m["tail"]
    tail.box((0, YC, 90.5), (3, 3, 4), "scales_plain", P=2.0)                         # tail tip
    fan = m.bone("fan", "tail", (0, YC, 88.5))
    fan.plane_from((0, YC, 88), 27, 42, "fin", rot=frame((0, 0, 1), (1, 0, 0)), anchor_st=(0, 0.5), kind="fluke")
    fan.plane_from((0, YC + 0.5, 87.5), 13, 20, "fin", rot=frame((0, 0.25, 1), (0, -1, 0.25)), anchor_st=(0, 0.5),
                   kind="fan")

    build_stages(m)
    m.shift_bones(["head", "jaw", "frill_right", "frill_left", "whisker_right", "whisker_left"] + STAGE_HEAD_BONES,
                  (0, HEAD_LIFT, 0))
    m.shift_bones(list(m.bones.keys())[1:], (0, 0, ZOFF))
    return m


# =============================================================================== evolution stages
# BossRenderer hides bones named stage2_* below stage 2 and stage3_* below stage 3 (with their children)
# and grows them from scale 0 about their pivot. Stage bones are created after every base bone (base cube
# order seeds the shaders' noise) and their cubes are no_ao, so with them hidden the model is unchanged.
# Each stage bone hangs off the chain element it sits on, so it rides the travelling body wave.
#   stage 2: a row of tall glowing crystal spines rising through the dorsal sail along the back;
#   stage 3: a crown of five glowing spikes on the head, an extra pair of tail fins and glowing nebula
#            orbs set into the flanks.
# (segment, spine length, base width)
DORSAL_SPINES = [("body", 15, 3), ("seg1", 15, 3), ("seg2", 14, 3), ("seg3", 12, 3), ("seg4", 11, 3),
                 ("seg5", 9, 2), ("seg6", 8, 2), ("seg7", 6, 2), ("seg8", 5, 2)]
# (x, y, z) base on the head (pre-shift head space), segment directions, lengths, widths
CROWN = [((0.0, 28.6, -25.2), [(0, 1, 0.1), (0, 1, 0.42), (0, 0.8, 0.8)], [5, 5, 4], [3, 2, 1.2]),
         ((2.7, 28.4, -27.4), [(0.22, 1, -0.12), (0.3, 1, 0.3)], [5, 4], [2.4, 1.3]),
         ((5.6, 29.0, -28.6), [(0.5, 1, -0.2), (0.6, 1, 0.25)], [4, 4], [2.2, 1.1])]
ORBS = [("seg1", 4), ("seg2", 4), ("seg4", 3), ("seg5", 3)]
TAIL_FIN_SEG = "seg7"
STAGE_HEAD_BONES = ["stage3_crown"]


def _seg(name):
    return BODY if name == "body" else next(s for s in SEGS if s[0] == name)


def build_stages(m):
    # ---------------------------------------------------------------- stage 2: dorsal spines
    for name, ln, wd in DORSAL_SPINES:
        _, z0, L, W, H, _, _ = _seg(name)
        base = np.array([0.0, YC + H / 2 + 0.3, z0 + L * 0.42])
        b = m.bone(f"stage2_spines_{name}", name, tuple(base))
        segs = [0.44, 0.36, 0.3] if ln >= 10 else ([0.58, 0.52] if ln >= 7 else [1.0])
        b.spike(base, (0, 1, 0.55), ln, wd, "spine", segs=segs, spin=45, taper=0.62)
    # ---------------------------------------------------------------- stage 3: crown, tail fins, orbs
    cr = m.bone("stage3_crown", "head", (0, 28.4, -25.5))
    for (x, y, z), dirs, lens, wids in CROWN:
        for s in ((-1, 1) if x else (1,)):
            dd = [(dx * s, dy, dz) for dx, dy, dz in dirs]
            cr.curve_spike((x * s, y, z), dd, lens, wids, "spine", crown=True)
    _, z0, L, W, H, _, _ = _seg(TAIL_FIN_SEG)
    for s, nm_ in ((-1, "right"), (1, "left")):
        tf = m.bone(f"stage3_tail_fin_{nm_}", TAIL_FIN_SEG, (W / 2 * s, YC - 0.5, z0 + 1.5))
        tf.plane_from((W / 2 * s, YC - 0.5, z0 + 1.5), 17, 10, "fin", rot=frame((1.0 * s, -0.35, 0.55), (0, -0.1, 1)),
                      anchor_st=(0, 0), kind="pectoral", figure=False)
    for name, sz in ORBS:
        _, z0, L, W, H, _, _ = _seg(name)
        for s, nm_ in ((-1, "right"), (1, "left")):
            c = np.array([(W / 2 - sz * 0.3) * s, YC + 1.2, z0 + L * 0.5])
            ob = m.bone(f"stage3_orb_{name}_{nm_}", name, tuple(c))
            ob.box(c, (sz, sz, sz), "orb", inflate=0.3, side=s)
    for b in m.bones.values():
        if b.name.startswith(("stage2_", "stage3_")):
            for cb in b.cubes:
                cb.params["no_ao"] = True


# =============================================================================== animation helpers
SIDES = ((-1, "right"), (1, "left"))


def begin(c):
    """Cancel the rest rotations once per clip (all chain contributions are absolute joint angles)."""
    for k, b in enumerate(CHAIN):
        if k and np.any(np.abs(REST[k]) > 1e-6):
            c.f(b, "rotation", lambda t, k=k: -REST[k])
    return c


def add_wave(c, ya, pa, period, amp=None, t0=0.0, static=1.0):
    """Travelling wave through the chain (absolute joint angles) plus the static vertical S."""
    amp = amp or (lambda t: 1.0)
    for k, b in enumerate(CHAIN):
        c.f(b, "rotation", lambda t, k=k: wave_joint(k, TAU * (t + t0) / period, ya, pa) * amp(t)
            + static_joint(k) * (static(t) if callable(static) else static))
    # the neck counter-turns against the body so the head stays aimed
    c.f("neck", "rotation", lambda t: (0, -0.85 * heading(0, TAU * (t + t0) / period, ya[0], ya[1], PHI_Y) * amp(t), 0))


def joints_from_headings(H):
    """Absolute headings per chain element -> joint angles (each relative to its parent)."""
    return [H[0]] + [H[k] - H[k - 1] for k in range(1, len(H))]


def chain_keys(c, keys_per_bone):
    for b, keys in keys_per_bone.items():
        c.rot(b, keys)


def side_keys(c, prefix, keys):
    """keys: [(t, (pitch, sweep, raise), ease?)] mirrored onto both sides as (pitch, -s*sweep, -s*raise)."""
    for s, nm_ in SIDES:
        ks = []
        for k in keys:
            p, sw, r = k[1]
            ks.append((k[0], (p, -s * sw, -s * r)) + tuple(k[2:]))
        c.rot(f"{prefix}_{nm_}", ks)


def side_fn(c, prefix, fn):
    """fn(t) -> (pitch, sweep, raise), mirrored onto both sides."""
    for s, nm_ in SIDES:
        c.f(f"{prefix}_{nm_}", "rotation", lambda t, s=s: (lambda v: (v[0], -s * v[1], -s * v[2]))(fn(t)))


def ambient(c, period, k=1.0, fin_sweep=8.0, fin_flap=6.0, frill=4.0, whisk=5.0, jaw=(3.0, 2.0), hover=1.2,
            fan=6.0, harm=1):
    """Secondary motion every clip needs: hover, jaw breathing, frills, fins, whiskers, tail fan, head tilt."""
    w = lambda t, h=1, o=0.0: math.sin(TAU * h * harm * t / period + o)
    c.f("root", "position", lambda t: (0, hover * w(t) * k, 0))
    c.f("jaw", "rotation", lambda t: (jaw[0] + jaw[1] * w(t, 2, 0.3) * k, 0, 0))
    c.f("head", "rotation", lambda t: (0, 0, 2.0 * w(t, 1, 1.0) * k))
    side_fn(c, "frill", lambda t: (0, frill * w(t, 2, 0.4) * k, 1.5 * w(t, 2, 1.2) * k))
    side_fn(c, "fin", lambda t: (2 * w(t, 2, 0.4) * k, fin_sweep + 3 * w(t, 2, 1.0) * k, fin_flap * w(t, 2, 0.0) * k))
    side_fn(c, "whisker", lambda t: (3 * w(t, 2, -1.2) * k, whisk * w(t, 2, -0.8) * k, 2 * w(t, 2, -1.6) * k))
    c.f("fan", "rotation", lambda t: (3 * w(t, 1, -0.4) * k, fan * w(t, 1, -(NCH - 1) * PHI_Y - 0.8) * k, 0))


# =============================================================================== animations


def anim_idle():
    T = IDLE_T
    c = begin(Clip("idle", T, loop=True))
    add_wave(c, IDLE_YA, IDLE_PA, T)
    ambient(c, T)
    w = lambda t, o=0.0: math.sin(TAU * t / T + o)
    c.f("body", "rotation", lambda t: (1.2 * w(t, 2.0), 0, 1.5 * w(t, 0.5)))
    c.f("neck", "rotation", lambda t: (-1.5 * w(t, 2.4), 0, 0))
    return c


def anim_fly():
    T = 2.0
    c = begin(Clip("fly", T, loop=True))
    add_wave(c, (5.0, 36.0), (1.5, 10.0), T)
    ambient(c, T, fin_sweep=24, fin_flap=10, frill=3, whisk=4, jaw=(2.0, 1.5), hover=0.8, fan=10)
    w = lambda t, h=1, o=0.0: math.sin(TAU * h * t / T + o)
    c.f("body", "rotation", lambda t: (4 + 1.5 * w(t, 2, 0.6), 0, 2.5 * w(t, 1, 0.4)))
    c.f("neck", "rotation", lambda t: (-4 - 1.5 * w(t, 2, 1.4), 0, 0))
    side_fn(c, "frill", lambda t: (0, 16, 0))
    side_fn(c, "whisker", lambda t: (0, 12, 2))
    return c


def anim_void_bite():
    L = 1.3
    c = begin(Clip("attack.void_bite", L))
    damp = lambda t: 1 - 0.65 * env(t, 0.05, 0.3, 0.5, 1.1)
    add_wave(c, IDLE_YA, IDLE_PA, L, amp=damp)      # period = clip length: ends on idle's first frame
    ambient(c, 2.0, k=0.6)
    # wind-up: the front body folds into a snake-strike S (a coiled spring), then whips straight
    zz = joints_from_headings([0, 42, 58, 12, -44, -56, -20, 26, 42, 22])
    for k, b in enumerate(CHAIN[1:], 1):
        c.rot(b, [(0, (0, 0, 0)), (0.32, (0, zz[k], 0), "io"), (0.42, (0, -0.3 * zz[k], 0), "snap"),
                  (0.75, (0, -0.1 * zz[k], 0)), (1.3, (0, 0, 0), "io")])
    c.rot("body", [(0, (0, 0, 0)), (0.32, (-10, 0, 0), "io"), (0.42, (5, 0, 0), "snap"), (0.7, (4, 0, 0)),
                   (1.3, (0, 0, 0), "io")])
    c.pos("body", [(0, (0, 0, 0)), (0.32, (0, 1.0, 5), "io"), (0.42, (0, -1.0, -9), "snap"), (0.7, (0, -1.0, -7.5)),
                   (1.3, (0, 0, 0), "io")])
    c.rot("neck", [(0, (0, 0, 0)), (0.32, (-20, 0, 0), "io"), (0.42, (12, 0, 0), "snap"), (0.62, (9, 0, 0)),
                   (1.3, (0, 0, 0), "io")])
    c.pos("neck", [(0, (0, 0, 0)), (0.32, (0, 1.0, 1.5), "io"), (0.42, (0, -0.5, -2), "snap"), (0.65, (0, -0.5, -1.5)),
                   (1.3, (0, 0, 0), "io")])
    c.f("neck", "rotation", lambda t: (tremor(t, 0.42, 0.45, 0.55, 0.75, 1.5, 24), tremor(t, 0.42, 0.45, 0.55, 0.75, 1.0, 19, 2), 0))
    c.rot("jaw", [(0, (0, 0, 0)), (0.1, (0, 0, 0)), (0.3, (36, 0, 0), "out"), (0.4, (40, 0, 0)),
                  (0.45, (-3, 0, 0), "snap"), (0.7, (2, 0, 0)), (1.3, (0, 0, 0), "io")])
    c.f("head", "position", lambda t: (0, tremor(t, 0.44, 0.46, 0.55, 0.7, 0.5, 30), 0))
    side_keys(c, "frill", [(0, (0, 0, 0)), (0.32, (0, -28, 6), "io"), (0.42, (0, -30, 6)), (0.6, (0, 12, 0), "out"),
                           (1.3, (0, 0, 0), "io")])
    side_keys(c, "fin", [(0, (0, 0, 0)), (0.32, (0, -10, 14), "io"), (0.42, (0, 30, -6), "snap"), (0.8, (0, 18, 0)),
                         (1.3, (0, 0, 0), "io")])
    side_keys(c, "whisker", [(0, (0, 0, 0)), (0.32, (-6, -8, 0)), (0.5, (8, 24, 0), "out"), (0.8, (0, 10, 0)),
                             (1.3, (0, 0, 0), "io")])
    c.rot("fan", [(0, (0, 0, 0)), (0.32, (0, -12, 0)), (0.46, (0, 20, 0), "snap"), (0.8, (0, -8, 0)), (1.3, (0, 0, 0))])
    return c


def anim_nebula_breath():
    L = 2.5
    c = begin(Clip("attack.nebula_breath", L))
    damp = lambda t: 1 - 0.5 * env(t, 0.3, 0.6, 2.0, 2.45)
    add_wave(c, IDLE_YA, IDLE_PA, 2.4, amp=damp)
    ambient(c, 2.5, k=0.5, jaw=(0, 0))
    c.rot("neck", [(0, (0, 0, 0)), (0.45, (-18, 0, 0), "io"), (0.58, (-6, 0, 0), "snap"), (2.15, (-8, 0, 0)),
                   (2.5, (0, 0, 0), "io")])
    c.f("neck", "rotation", lambda t: (0, 9 * math.sin(TAU * (t - 0.6) / 1.6) * env(t, 0.6, 0.85, 1.95, 2.2), 0))
    c.pos("neck", [(0, (0, 0, 0)), (0.45, (0, 1, 3), "io"), (0.58, (0, -0.5, -3), "snap"), (2.15, (0, -0.5, -2.5)),
                   (2.5, (0, 0, 0), "io")])
    c.scl("neck", [(0, (1, 1, 1)), (0.45, (1.06, 1.1, 1.0), "io"), (0.58, (1, 1, 1), "snap"), (2.5, (1, 1, 1))])
    c.rot("body", [(0, (0, 0, 0)), (0.45, (-6, 0, 0)), (0.58, (1, 0, 0), "snap"), (2.15, (0, 0, 0)),
                   (2.5, (0, 0, 0), "io")])
    c.pos("body", [(0, (0, 0, 0)), (0.45, (0, 0, 2)), (0.58, (0, 0, -1.5), "snap"), (2.15, (0, 0, -1)),
                   (2.5, (0, 0, 0), "io")])
    c.rot("jaw", [(0, (2, 0, 0)), (0.3, (7, 0, 0)), (0.45, (10, 0, 0)), (0.58, (40, 0, 0), "snap"),
                  (2.15, (36, 0, 0)), (2.4, (0, 0, 0), "in"), (2.5, (2, 0, 0))])
    c.f("jaw", "rotation", lambda t: (tremor(t, 0.6, 0.7, 2.0, 2.15, 1.6, 17), 0, 0))
    c.f("head", "position", lambda t: (tremor(t, 0.6, 0.7, 2.0, 2.15, 0.25, 23, 1), tremor(t, 0.6, 0.7, 2.0, 2.15, 0.3, 29), 0))
    side_keys(c, "frill", [(0, (0, 0, 0)), (0.45, (0, 18, -4), "io"), (0.58, (0, -32, 8), "snap"),
                           (2.15, (0, -28, 6)), (2.5, (0, 0, 0), "io")])
    side_fn(c, "frill", lambda t: (0, 3 * math.sin(t * 95) * env(t, 0.6, 0.7, 2.0, 2.15), 0))
    side_keys(c, "fin", [(0, (0, 0, 0)), (0.45, (0, 4, 6)), (0.58, (0, -8, 12), "snap"), (2.15, (0, -6, 10)),
                         (2.5, (0, 0, 0), "io")])
    side_keys(c, "whisker", [(0, (0, 0, 0)), (0.45, (-4, -6, 0)), (0.62, (6, 22, 4), "out"), (2.15, (4, 18, 3)),
                             (2.5, (0, 0, 0), "io")])
    return c


def anim_coil():
    L = 3.0
    c = begin(Clip("attack.coil", L))
    curl = lambda t: env(t, 0.0, 0.7, 2.4, 3.0, "io", "io")
    pulse = lambda t: max(0.0, math.sin(TAU * (t - 0.6) / 0.5)) ** 3 * env(t, 0.6, 0.75, 2.35, 2.5)
    add_wave(c, IDLE_YA, IDLE_PA, L / 2, amp=lambda t: 1 - 0.8 * curl(t), static=lambda t: 1 - curl(t))
    ambient(c, 3.0, k=0.5, jaw=(0, 0))
    for k, b in enumerate(CHAIN[1:], 1):
        yaw = 30 + 10 * k / 9
        c.f(b, "rotation", lambda t, k=k, yaw=yaw: (-4.0 * curl(t),
                                                    yaw * curl(t) * (1 + 0.1 * pulse(t)) + 4 * math.sin(TAU * 1.5 * t - k * 0.9) * curl(t),
                                                    -6 * curl(t)))
    c.f("body", "rotation", lambda t: (6 * curl(t), -24 * curl(t), 8 * curl(t)))
    c.f("neck", "rotation", lambda t: (8 * curl(t), 30 * curl(t), 0))
    c.f("root", "position", lambda t: (6 * curl(t), 2 * curl(t), 0))
    c.rot("jaw", [(0, (2, 0, 0)), (0.6, (18, 0, 0)), (1.0, (26, 0, 0)), (1.12, (4, 0, 0), "snap"), (1.6, (22, 0, 0)),
                  (1.72, (4, 0, 0), "snap"), (2.2, (22, 0, 0)), (2.32, (4, 0, 0), "snap"), (3.0, (2, 0, 0), "io")])
    side_keys(c, "frill", [(0, (0, 0, 0)), (0.6, (0, -26, 6)), (2.4, (0, -24, 6)), (3.0, (0, 0, 0), "io")])
    side_keys(c, "fin", [(0, (0, 0, 0)), (0.6, (0, 32, -10)), (2.4, (0, 30, -8)), (3.0, (0, 0, 0), "io")])
    side_keys(c, "whisker", [(0, (0, 0, 0)), (0.7, (4, 18, 0)), (2.4, (4, 16, 0)), (3.0, (0, 0, 0), "io")])
    c.f("fan", "rotation", lambda t: (0, 14 * math.sin(TAU * 2 * t) * curl(t), 0))
    return c


def anim_star_rain():
    L = 2.5
    c = begin(Clip("attack.star_rain", L))
    rear = lambda t: env(t, 0.0, 0.45, 2.0, 2.5)
    add_wave(c, IDLE_YA, IDLE_PA, 2.5, amp=lambda t: 1 - 0.5 * rear(t))
    ambient(c, 2.5, k=0.5, jaw=(0, 0), hover=0.6)
    lash = lambda t: env(t, 0.5, 0.7, 1.9, 2.3)
    for k, b in enumerate(CHAIN[1:], 1):
        c.f(b, "rotation", lambda t, k=k: (0, 11 * (k / 9) * math.sin(TAU * 2.0 * t - k * 0.9) * lash(t), 0))
    c.rot("body", [(0, (0, 0, 0)), (0.45, (-30, 0, 0), "io"), (0.55, (-34, 0, 0)), (2.0, (-30, 0, 0)),
                   (2.5, (0, 0, 0), "io")])
    c.rot("seg1", [(0, (0, 0, 0)), (0.45, (20, 0, 0), "io"), (2.0, (18, 0, 0)), (2.5, (0, 0, 0), "io")])
    c.rot("seg2", [(0, (0, 0, 0)), (0.45, (10, 0, 0), "io"), (2.0, (10, 0, 0)), (2.5, (0, 0, 0), "io")])
    c.rot("neck", [(0, (0, 0, 0)), (0.45, (-24, 0, 0), "io"), (0.55, (-28, 0, 0)), (2.0, (-24, 0, 0)),
                   (2.5, (0, 0, 0), "io")])
    c.f("neck", "rotation", lambda t: (tremor(t, 0.55, 0.65, 1.8, 2.0, 1.4, 21), tremor(t, 0.55, 0.65, 1.8, 2.0, 1.0, 17, 3), 0))
    c.pos("root", [(0, (0, 0, 0)), (0.45, (0, 4, 2), "io"), (2.0, (0, 4, 2)), (2.5, (0, 0, 0), "io")])
    c.rot("jaw", [(0, (2, 0, 0)), (0.35, (8, 0, 0)), (0.55, (46, 0, 0), "snap"), (1.9, (40, 0, 0)), (2.3, (2, 0, 0), "io"),
                  (2.5, (2, 0, 0))])
    c.f("jaw", "rotation", lambda t: (tremor(t, 0.6, 0.7, 1.8, 1.95, 2.0, 15), 0, 0))
    c.f("head", "rotation", lambda t: (0, 0, tremor(t, 0.55, 0.65, 1.8, 2.0, 2.5, 13, 5)))
    side_keys(c, "frill", [(0, (0, 0, 0)), (0.4, (0, 10, 0)), (0.55, (0, -36, 12), "snap"), (2.0, (0, -32, 10)),
                           (2.5, (0, 0, 0), "io")])
    side_fn(c, "frill", lambda t: (0, 3 * math.sin(t * 80) * env(t, 0.6, 0.7, 1.8, 2.0), 0))
    side_keys(c, "fin", [(0, (0, 0, 0)), (0.45, (0, -12, 26), "io"), (2.0, (0, -10, 22)), (2.5, (0, 0, 0), "io")])
    side_fn(c, "fin", lambda t: (0, 0, 6 * math.sin(TAU * 3 * t) * env(t, 0.5, 0.7, 1.8, 2.0)))
    side_keys(c, "whisker", [(0, (0, 0, 0)), (0.5, (-12, -6, 10), "io"), (2.0, (-10, -4, 8)), (2.5, (0, 0, 0), "io")])
    return c


def anim_phase():
    L = 2.0
    c = begin(Clip("phase", L))
    con = lambda t: env(t, 0.0, 0.5, 0.52, 0.66, "io", "snap")
    burst = lambda t: env(t, 0.55, 0.68, 1.45, 2.0, "snap", "io")
    add_wave(c, IDLE_YA, IDLE_PA, 2.0, amp=lambda t: 1 - 0.7 * con(t) - 0.4 * burst(t))
    ambient(c, 2.0, k=0.4, jaw=(0, 0))
    zz = joints_from_headings([0, -36, -50, -12, 38, 50, 18, -24, -38, -18])
    for k, b in enumerate(CHAIN[1:], 1):
        c.f(b, "rotation", lambda t, k=k: (-4 * con(t) + (5 - 0.8 * k) * burst(t), zz[k] * con(t)
                                           + 10 * (k / 9) * math.sin(TAU * 2.4 * t - k) * burst(t), 0))
    c.f("body", "rotation", lambda t: (10 * con(t) - 22 * burst(t) + tremor(t, 0.66, 0.72, 1.35, 1.5, 1.5, 22), 0, 0))
    c.f("neck", "rotation", lambda t: (16 * con(t) - 26 * burst(t) + tremor(t, 0.66, 0.72, 1.35, 1.5, 2.0, 25, 1),
                                       tremor(t, 0.66, 0.72, 1.35, 1.5, 1.5, 19, 4), 0))
    c.f("root", "position", lambda t: (0, -2 * con(t) + 3 * burst(t), 0))
    c.f("jaw", "rotation", lambda t: (2 + 46 * burst(t) + tremor(t, 0.7, 0.8, 1.35, 1.5, 2.5, 16), 0, 0))
    side_fn(c, "frill", lambda t: (0, 30 * con(t) - 40 * burst(t) + 3 * math.sin(t * 90) * burst(t), 14 * burst(t)))
    c.f("frill_right", "scale", lambda t: (1 + 0.25 * burst(t),) * 3)
    c.f("frill_left", "scale", lambda t: (1 + 0.25 * burst(t),) * 3)
    side_fn(c, "fin", lambda t: (0, 36 * con(t) - 16 * burst(t), -10 * con(t) + 30 * burst(t)))
    side_fn(c, "whisker", lambda t: (6 * con(t) - 12 * burst(t), 18 * con(t) - 8 * burst(t), 10 * burst(t)))
    c.f("fan", "rotation", lambda t: (0, 18 * math.sin(TAU * 2.4 * t - 9) * burst(t), 0))
    c.f("fan", "scale", lambda t: (1, 1 + 0.15 * burst(t), 1 + 0.1 * burst(t)))
    return c


def anim_death():
    L = 2.8
    c = begin(Clip("death", L, loop="hold"))
    live = lambda t: 1 - ease("io", (t - 0.2) / 1.3)
    fall = lambda t: ease("in", (t - 1.15) / 1.1)
    limp = lambda t: ease("io", (t - 1.0) / 1.3)
    add_wave(c, IDLE_YA, IDLE_PA, 2.0, amp=live, static=lambda t: 1 - limp(t))
    ambient(c, 2.0, k=0.4, jaw=(0, 0), hover=0.0)
    lazy = joints_from_headings([0, 8, 14, 10, -2, -12, -14, -6, 6, 12])
    jolts = joints_from_headings([0, -14, -20, -4, 16, 20, 6, -12, -16, -8])
    for k, b in enumerate(CHAIN[1:], 1):
        c.f(b, "rotation", lambda t, k=k: (
            (2.5 - 0.4 * k) * limp(t) + 2.5 * shake(t, 9 + k, 1.0, k) * env(t, 0.25, 0.35, 1.0, 1.3),
            jolts[k] * env(t, 0.0, 0.25, 0.4, 1.0) + lazy[k] * limp(t), 0))
    c.f("body", "rotation", lambda t: (-14 * env(t, 0.0, 0.25, 0.45, 1.2) + tremor(t, 0.25, 0.35, 1.0, 1.3, 2.5, 18),
                                       0, 34 * limp(t)))
    c.f("neck", "rotation", lambda t: (-30 * env(t, 0.0, 0.25, 0.5, 1.2) + 16 * limp(t)
                                       + tremor(t, 0.25, 0.35, 1.0, 1.3, 3.0, 21, 1), tremor(t, 0.25, 0.35, 1.0, 1.3, 2.0, 16, 3), 0))
    bounce = Track([(0, 0.0), (1.15, 0.0), (2.25, -9.0, "in"), (2.4, -8.0, "out"), (2.55, -9.0, "in"), (2.8, -9.0)])
    c.f("root", "position", lambda t: (0, float(bounce(t)), 0))
    c.f("jaw", "rotation", lambda t: (44 * env(t, 0.0, 0.2, 0.5, 1.2, "snap") + 24 * limp(t)
                                      + tremor(t, 0.25, 0.35, 1.0, 1.3, 3.0, 14), 0, 0))
    c.f("head", "rotation", lambda t: (0, 0, -18 * limp(t)))
    side_fn(c, "frill", lambda t: (0, -30 * env(t, 0.0, 0.2, 0.5, 1.2) + 26 * limp(t), -12 * limp(t)))
    side_fn(c, "fin", lambda t: (0, -8 * env(t, 0.0, 0.2, 0.5, 1.2) + 20 * limp(t), 20 * env(t, 0.0, 0.2, 0.5, 1.2) - 24 * limp(t)))
    side_fn(c, "whisker", lambda t: (10 * limp(t), 8 * limp(t), -14 * limp(t)))
    c.f("fan", "rotation", lambda t: (8 * limp(t), 6 * limp(t), 0))
    return c


def clips():
    return [anim_idle(), anim_fly(), anim_void_bite(), anim_nebula_breath(), anim_coil(), anim_star_rain(),
            anim_phase(), anim_death()]


POSES = [
    ("idle", [0.0, 1.0, 2.0, 3.0]),
    ("fly", [0.0, 0.5, 1.0, 1.5]),
    ("attack.void_bite", [0.2, 0.32, 0.42, 0.8]),
    ("attack.nebula_breath", [0.3, 0.45, 0.9, 2.3]),
    ("attack.coil", [0.3, 0.8, 1.6, 2.7]),
    ("attack.star_rain", [0.3, 0.6, 1.4, 2.3]),
    ("phase", [0.4, 0.62, 1.0, 1.8]),
    ("death", [0.2, 0.9, 1.8, 2.8]),
]
HERO = ("attack.void_bite", 0.3)


# =============================================================================== checks + main


def sanity(geo, anims, rgba):
    desc = geo["minecraft:geometry"][0]["description"]
    bones = {b["name"]: b for b in geo["minecraft:geometry"][0]["bones"]}
    for req in ("root", "body", "head"):
        assert req in bones, req
    assert bones["root"]["pivot"] == [0, 0, 0] and "parent" not in bones["root"]
    assert "rotation" not in bones["head"], "head must have zero rest rotation"
    for an, a in anims["animations"].items():
        for b in a["bones"]:
            assert b in bones, (an, b)
    assert rgba.shape[1] == desc["texture_width"] * 2 and rgba.shape[0] == desc["texture_height"] * 2
    need = {"idle", "fly", "death", "phase", "attack.void_bite", "attack.nebula_breath", "attack.coil", "attack.star_rain"}
    assert need <= set(anims["animations"]), need - set(anims["animations"])
    # chain depth
    depth, b = 0, "tail"
    while b != "body":
        b = bones[b]["parent"]
        depth += 1
    print(f"sanity ok: {len(bones)} bones, chain body->tail {depth + 1} bones, "
          f"texture {desc['texture_width']}x{desc['texture_height']} (png {rgba.shape[1]}x{rgba.shape[0]})")
    g = gp.load_geo(geo)
    lo, hi = gp.model_extent(g)
    print(f"rest extent x {lo[0]:.1f}..{hi[0]:.1f}  y {lo[1]:.1f}..{hi[1]:.1f}  z {lo[2]:.1f}..{hi[2]:.1f}")


def main():
    m = build_model()
    geo, rgba, glow, anims = tl.build(NAME, m, nm.SHADERS, clips(), visible=(12, 5, 1.0))
    sanity(geo, anims, rgba)
    if "--preview" in sys.argv:
        print(nv.rest_sheet(NAME, geo, rgba, glow, HITBOX))
        print(nv.pose_sheet(NAME, geo, rgba, glow, anims, HERO[0], HERO[1]))
        head = np.array([0, 23, -30 + ZOFF])
        bite = gp.sample_anim(anims["animations"]["attack.void_bite"], 0.36)
        print(nv.closeup(NAME, geo, rgba, glow, head, [("head front", 0, -6), ("head 3/4", 35, -12),
                                                         ("head side", 90, -4), ("open maw", 25, -10, bite)],
                         frame=50, px=440))
        print(nv.closeup(NAME, geo, rgba, glow, np.array([0, 18, 20]), [("body side", 90, -4), ("body top", 90, -70)],
                         frame=34, px=520, tag="_body"))
        print(nv.closeup(NAME, geo, rgba, glow, np.array([0, 14, 2]), [("pectoral fins (top)", 90, -80)],
                         frame=70, px=520, tag="_fins"))
        print(nv.closeup(NAME, geo, rgba, glow, np.array([0, 14, 100]), [("tail fluke (top)", 90, -80)],
                         frame=50, px=520, tag="_fluke"))
        if "--all" in sys.argv:
            print(nv.pose_sheet(NAME, geo, rgba, glow, anims, "attack.coil", 1.6))
            for an, times in POSES:
                print(nv.strip(NAME, geo, rgba, glow, anims, an, times))


if __name__ == "__main__":
    main()
