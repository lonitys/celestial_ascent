"""Void Sovereign: the final boss. A towering monarch of black-violet void crystal: asymmetric
crystal spikes jutting from the shoulders and back, magenta void fractures, a crown of floating
shards orbiting above a horned skull-helm, a hollow chest rift holding a swirling star,
long clawed arms and a tattered cloak that dissolves into the starry void.

Run: python void_sovereign.py [--preview [--all]]
"""
import math
import os
import sys

import numpy as np

import bosslib as tl
import bossfx as fx
import geo_preview as gp
import void_sovereign_mats as vm
from bosslib import Clip, env, ease
from rig import TAU, knee_bend, sides, tremor

NAME = "void_sovereign"
HITBOX = (2.6, 5.4)
THIGH, SHIN = 15.0, 17.0
CAV = (0.0, 59.5, -1.5)                 # chest star centre (torso space, before the torso lean)
SHARD_ANG = [math.radians(30 + 60 * i) for i in range(6)]   # i=4 sits at the front (270 deg)
SHARDS = [f"shard_{i}" for i in range(6)]
CLOAK = [("cloak_right", "cloak_right_low"), ("cloak_mid", "cloak_mid_low"), ("cloak_left", "cloak_left_low")]
LEGS = [("right_leg", "right_shin"), ("left_leg", "left_shin")]
FEET = ["right_foot", "left_foot"]
CROWN_C = (0.0, 88.0, -1.5)
CROWN_R = 6.2

# =============================================================================== geometry


def build_model():
    m = tl.Model(NAME)
    # ------------------------------------------------------------------ pelvis + legs
    body = m.bone("body", "root", (0, 36, 0.5))
    body.boxb(0, 32, 0.5, 13, 7, 9, "crystal")                                     # pelvis
    body.boxb(0, 37.5, 0.5, 14, 3, 10, "belt")                                     # rune belt
    for s in (-1, 1):
        body.spike((10.4 * s, 39.0, 0.8), (0.34 * s, -1, 0.08), 12, 4, "shard", segs=[0.6, 0.48])   # hip shards
    tab = m.bone("tabard", "body", (0, 39.0, -5.4))
    tab.plane_from((0, 39.0, -5.4), 9, 24, "tabard", pid=3, v0=0.0, v1=1.0, total=24.0)

    for s, nm in sides():
        leg = m.bone(f"{nm}_leg", "body", (6 * s, 35.5, 0.5))
        leg.boxb(6 * s, 20.5, 0.5, 7, 15, 7, "crystal_cracked")                     # thigh
        leg.box((9.9 * s, 28.0, 0.5), (2, 11, 7), "crystal", rot=[0, 0, -9 * s], pivot=(9.9 * s, 33.5, 0.5))   # outer tasset
        shin = m.bone(f"{nm}_shin", f"{nm}_leg", (6.2 * s, 20.5, 0.5))
        shin.box((6.2 * s, 20.8, -1.4), (6, 5, 5), "crystal")                      # knee cop
        shin.spike((6.2 * s, 21.6, -3.4), (0, 0.6, -1), 6, 3, "shard", segs=[0.62, 0.5])   # knee spike
        shin.boxb(6.2 * s, 3.5, 0.8, 6, 17, 6, "crystal")                          # greave
        shin.box((6.2 * s, 11.5, -2.3), (2, 13, 2), "crystal", rot=[-3, 0, 0])     # shin ridge
        foot = m.bone(f"{nm}_foot", f"{nm}_shin", (6.3 * s, 3.5, 0.5))
        foot.boxb(6.3 * s, 0, -1.2, 6, 4, 10, "crystal")                           # sabaton
        foot.spike((6.3 * s, 1.7, -5.6), (0, -0.06, -1), 6, 3, "claw", segs=[0.55, 0.55])   # toe talon

    # ------------------------------------------------------------------ torso + chest cavity
    torso = m.bone("torso", "body", (0, 40, 1), rotation=[8, 0, 0])
    torso.boxb(0, 39.5, 1, 11, 9, 8, "crystal")                                    # waist
    torso.boxb(0, 48, 1, 18, 5, 11, "crystal_cracked")                             # lower ribcage
    for s in (-1, 1):
        torso.box((9.0 * s, 59.5, 0.5), (8, 13, 12), "frame")                      # chest halves (x 5..13)
    torso.box((0, 66.0, 0.5), (10, 2, 12), "frame")                                # sternum bridge
    torso.box((0, 53.0, 0.5), (10, 2, 12), "frame")                                # lower bridge
    torso.box((0, 59.5, 4.5), (10, 11, 4), "void_wall")                            # cavity back wall
    for s in (-1, 1):
        torso.box((9.6 * s, 60.5, -6.1), (8, 10, 2), "crystal_cracked_hi", rot=[-8, -14 * s, 5 * s])   # pectoral slabs
    torso.boxb(0, 65.5, 1.5, 26, 3, 11, "crystal")                                 # shoulder yoke
    for s in (-1, 1):
        torso.box((4.6 * s, 72.5, 4.2), (6, 10, 1), "crystal_cracked", rot=[-16, 0, 24 * s], pivot=(3.0 * s, 67.5, 4.2))   # standing collar
    torso.box((0, 57.5, 7.2), (15, 15, 2), "crystal_cracked")                      # back plate
    for s in (-1, 1):   # slanted lips turn the opening into a rift that narrows downward
        torso.box((4.6 * s, 59.5, -3.5), (2, 12, 5), "frame", rot=[0, 0, 7 * s])

    star = m.bone("chest_star", "torso", CAV)
    star.plane(CAV, 12, 12, "swirl")
    star.plane((CAV[0], CAV[1], CAV[2] - 0.35), 13, 13, "flare", rot=[0, 0, 45])
    star.plane(CAV, 10, 10, "flare", rot=[0, 90, 0])
    star.box(CAV, (2, 2, 2), "core", rot=[45, 0, 45])

    sp = m.bone("spines", "torso", (0, 61, 7.5))
    sp.spike((-5.0, 63.0, 7.2), (-0.55, 1, 0.75), 24, 5, "shard_cracked")
    sp.spike((4.5, 64.0, 7.2), (0.45, 1, 0.85), 19, 4.5, "shard_cracked")
    sp.spike((-2.0, 56.5, 7.6), (-0.25, 0.5, 1), 12, 3.5, "shard", segs=[0.6, 0.5])
    sp.spike((6.5, 57.5, 7.6), (0.9, 0.5, 0.8), 11, 3, "shard", segs=[0.6, 0.5])

    # ------------------------------------------------------------------ floating pauldron clusters (asymmetric)
    rp = m.bone("right_pauldron", "torso", (-16, 69.5, 1))
    rp.box((-16.5, 69.5, 1.0), (10, 4, 11), "crystal_cracked", rot=[0, 0, -16])
    rp.spike((-18.0, 70.5, 1.5), (-0.42, 1, 0.15), 23, 6, "shard_cracked", segs=[0.44, 0.33, 0.27])
    rp.spike((-20.5, 69.0, 3.5), (-1, 0.55, 0.5), 12, 3.5, "shard", segs=[0.6, 0.5])
    lp = m.bone("left_pauldron", "torso", (16, 69.5, 1))
    lp.box((16.5, 69.5, 1.0), (10, 4, 11), "crystal_cracked", rot=[0, 0, 16])
    lp.spike((18.0, 70.5, 2.5), (0.5, 1, 0.6), 16, 5, "shard", segs=[0.46, 0.33, 0.27])
    lp.spike((20.5, 69.0, -1.0), (1, 0.38, -0.3), 10, 3.5, "shard", segs=[0.6, 0.5])

    # ------------------------------------------------------------------ long clawed arms
    for s, nm in sides():
        arm = m.bone(f"{nm}_arm", "torso", (16 * s, 64, 1), rotation=[-8, 0, -12 * s])
        arm.box((16 * s, 63.5, 1), (7, 7, 7), "crystal")                           # shoulder ball
        arm.boxb(16.5 * s, 51, 1, 5, 12, 5, "crystal_cracked")                      # upper arm
        fore = m.bone(f"{nm}_forearm", f"{nm}_arm", (16.5 * s, 51.5, 1), rotation=[-20, 0, 4 * s])
        fore.spike((16.5 * s, 51.5, 3.0), (0.1 * s, -0.25, 1), 6, 3, "shard", segs=[0.6, 0.5])  # elbow spike
        fore.boxb(16.7 * s, 38.5, 1, 6, 13, 6, "bracer")                            # bracer
        fore.spike((19.6 * s, 40.0, 1.0), (0.3 * s, 1, 0.25), 13, 2.5, "shard", segs=[0.6, 0.5])  # forearm blade
        hand = m.bone(f"{nm}_hand", f"{nm}_forearm", (16.7 * s, 38.5, 0.8))
        hand.box((16.7 * s, 36.0, 0.8), (5, 5, 5), "crystal")                       # palm
        for dz, fz in ((-1.6, -0.35), (0.3, 0.0), (2.0, 0.3)):
            hand.curve_spike((16.7 * s - 0.6 * s, 34.0, 0.8 + dz), [(-0.12 * s, -1, fz), (-0.55 * s, -1, fz - 0.25)],
                             [5, 6], [2, 1], "claw")
        hand.curve_spike((16.7 * s - 2.2 * s, 35.0, -1.2), [(-0.6 * s, -0.6, -0.6), (-0.35 * s, -1, -0.45)],
                         [4, 4], [2, 1], "claw")                                     # thumb talon

    # ------------------------------------------------------------------ neck, skull-helm, floating crown
    neck = m.bone("neck", "torso", (0, 66.5, 0), rotation=[-6, 0, 0])
    neck.boxb(0, 65.5, 0, 5, 7, 5, "crystal")
    head = m.bone("head", "neck", (0, 70.5, -1))
    head.box((0, 76.5, -1.5), (9, 10, 8), "head")                                  # cranium (71.5..81.5)
    head.box((0, 71.5, -2.2), (6, 3, 6), "crystal")                                # narrower jaw
    head.spike((0, 71.2, -4.2), (0, -1, -0.6), 5, 4, "shard_dark", segs=[0.55, 0.6])     # pointed chin
    for s in (-1, 1):
        head.box((2.5 * s, 79.7, -5.7), (5, 2, 2), "crystal", rot=[8, 0, -17 * s])  # angry V brow
        head.curve_spike((4.0 * s, 80.0, -1.5), [(0.85 * s, 0.55, 0.25), (0.45 * s, 0.45, 1.0), (0.1 * s, 0.3, 1.0)],
                         [6, 6, 5], [3, 2, 1], "shard")                              # swept horns
    crown = m.bone("crown", "head", CROWN_C)
    halo = m.bone("halo", "crown", CROWN_C)
    halo.plane((CROWN_C[0], CROWN_C[1] - 1.8, CROWN_C[2]), 17, 17, "halo", rot=[90, 0, 0])
    for i, a in enumerate(SHARD_ANG):
        tall = i % 2 == 0
        bx, bz = CROWN_R * math.cos(a), CROWN_C[2] + CROWN_R * math.sin(a)
        by = CROWN_C[1] - (1.0 if tall else 0.0)
        sh = m.bone(SHARDS[i], "crown", (bx, by, bz))
        if tall:
            sh.spike((bx, by, bz), (0.2 * math.cos(a), 1, 0.2 * math.sin(a)), 11, 3, "crown", segs=[0.42, 0.36, 0.32])
        else:
            sh.spike((bx, by, bz), (0.24 * math.cos(a), 1, 0.24 * math.sin(a)), 7, 2, "crown", segs=[0.6, 0.55])

    # ------------------------------------------------------------------ tattered cloak (double-sided planes)
    cm = m.bone("cloak_mid", "torso", (0, 65.5, 8.8), rotation=[4, 0, 0])
    cm.plane_from((0, 65.5, 8.8), 14, 30, "cloak", pid=0, v0=0.0, v1=0.52)
    cml = m.bone("cloak_mid_low", "cloak_mid", (0, 35.5, 8.8), rotation=[-2, 0, 0])
    cml.plane_from((0, 35.5, 8.8), 14, 28, "cloak", pid=0, v0=0.52, v1=1.0)
    for s, nm in sides():
        cs = m.bone(f"cloak_{nm}", "torso", (11.0 * s, 65.5, 7.0), rotation=[4, 25 * s, -8 * s])
        cs.plane_from((11.0 * s, 65.5, 7.0), 12, 30, "cloak", pid=1 if s < 0 else 2, v0=0.0, v1=0.54, taper=1)
        csl = m.bone(f"cloak_{nm}_low", f"cloak_{nm}", (11.0 * s, 35.5, 7.0), rotation=[-2, 0, 0])
        csl.plane_from((11.0 * s, 35.5, 7.0), 12, 26, "cloak", pid=1 if s < 0 else 2, v0=0.54, v1=1.0)
    return m


# =============================================================================== animation helpers


def ambient(c, L, crown_turn=None, star_turn=None, bob=0.7, star_pulse=0.06, cloak=1.0, pauld=0.6,
            radial=None, lift=None, star_scale=None):
    """Bones that idle keeps moving; every clip drives them (the attack controller stops 'main').
    The crown is 3-fold symmetric (tall/short alternating) so a 120 deg orbit loops seamlessly;
    the star is 2-fold symmetric so 180 deg loops."""
    m = max(1, int(round(L / 2.0)))
    ct = crown_turn or (lambda t: t / L)
    st = star_turn or (lambda t: t / L)
    c.f("crown", "rotation", lambda t: (0, -120.0 * ct(t), 0))
    c.f("crown", "position", lambda t: (0, 0.45 * math.sin(TAU * m * t / L), 0))
    for i, nm in enumerate(SHARDS):
        ph = 0.0 if i % 2 == 0 else math.pi
        a = SHARD_ANG[i]

        def fn(t, ph=ph, a=a):
            r = radial(t) if radial else 0.0
            h = lift(t) if lift else 0.0
            return (r * math.cos(a), h + bob * math.sin(TAU * m * t / L + ph), r * math.sin(a))
        c.f(nm, "position", fn)
        c.f(nm, "rotation", lambda t, ph=ph, a=a: (4 * math.sin(TAU * m * t / L + ph) * math.sin(a), 0,
                                                  -4 * math.sin(TAU * m * t / L + ph) * math.cos(a)))
    c.f("chest_star", "rotation", lambda t: (0, 0, -180.0 * st(t)))
    c.f("chest_star", "scale", lambda t: (1 + star_pulse * math.sin(TAU * 2 * m * t / L),) * 3)
    if star_scale:
        c.f("chest_star", "scale", lambda t: (star_scale(t),) * 3)
    for k, (s, nm) in enumerate(sides()):
        c.f(f"{nm}_pauldron", "position", lambda t, k=k: (0, pauld * (0.6 + math.sin(TAU * m * t / L + k * 2.2)), 0))
        c.f(f"{nm}_pauldron", "rotation", lambda t, k=k, s=s: (1.5 * math.sin(TAU * m * t / L + 1 + k), 0,
                                                                1.5 * math.sin(TAU * m * t / L + k * 2.2 + 0.8) * s))
    for k, (up, low) in enumerate(CLOAK):
        c.f(up, "rotation", lambda t, k=k: (cloak * 1.8 * math.sin(TAU * m * t / L + k * 1.3), 0,
                                            cloak * 1.2 * math.sin(TAU * m * t / L + k * 2.1 + 0.5)))
        c.f(low, "rotation", lambda t, k=k: (cloak * 3.0 * math.sin(TAU * m * t / L + k * 1.3 - 0.9), 0,
                                             cloak * 2.0 * math.sin(TAU * m * t / L + k * 2.1 - 0.4)))
    c.f("tabard", "rotation", lambda t: (cloak * 1.5 * math.sin(TAU * m * t / L + 0.7), 0, 0))


def crouch(c, drop_fn, spread=0.0):
    """Knee bend with planted feet + matching body drop."""
    knee_bend(c, drop_fn, THIGH, SHIN, LEGS, FEET, spread=spread)
    c.f("body", "position", lambda t: (0, -drop_fn(t), 0))


def cloak_keys(c, keys_up, keys_low=None, side_flare=None):
    """Extra cloak motion (added to ambient): keys_up/low = [(t, x_rot)], side_flare = [(t, outward deg)]."""
    for up, low in CLOAK:
        c.rot(up, [(k[0], (k[1], 0, 0)) + tuple(k[2:]) for k in keys_up])
        if keys_low:
            c.rot(low, [(k[0], (k[1], 0, 0)) + tuple(k[2:]) for k in keys_low])
    if side_flare:
        for s, nm in sides():
            c.rot(f"cloak_{nm}", [(k[0], (0, 0, -s * k[1])) + tuple(k[2:]) for k in side_flare])


def tr(keys):
    return tl.Track(keys)

# =============================================================================== animations


def anim_idle():
    T = 4.0
    c = Clip("idle", T, loop=True)
    w = lambda t, k=1, ph=0.0: math.sin(TAU * k * t / T + ph)
    ambient(c, T)
    c.f("torso", "rotation", lambda t: (1.4 * w(t), 0.8 * w(t, 1, 1.3), 0))
    c.f("torso", "position", lambda t: (0, 0.3 * w(t, 1, -0.4), 0))
    c.f("neck", "rotation", lambda t: (-1.2 * w(t, 1, 0.5), 1.2 * w(t, 1, 2.0), 0.8 * w(t, 1, 0.9)))
    c.f("spines", "rotation", lambda t: (-0.8 * w(t, 1, 0.4), 0, 0))
    for s, nm in sides():
        c.f(f"{nm}_arm", "rotation", lambda t, s=s: (2.0 * w(t, 1, 0.6 + s * 0.4), 0, -s * (1.5 + 1.2 * w(t, 1, 0.3))))
        c.f(f"{nm}_forearm", "rotation", lambda t, s=s: (-3 - 2.5 * w(t, 1, 1.1 + s * 0.4), 0, 0))
        c.f(f"{nm}_hand", "rotation", lambda t, s=s: (5 * w(t, 2, 2 + s), 0, -s * 3 * w(t, 1, 1)))
    return c


def anim_walk():
    T = 2.4                                    # two strides per loop
    c = Clip("walk", T, loop=True)
    ph = lambda t: TAU * 2 * t / T
    A = 20.0
    ambient(c, T, cloak=0.6)
    for s, nm in sides():
        sg = 1 if nm == "right" else -1
        c.f(f"{nm}_leg", "rotation", lambda t, sg=sg: (-A * sg * math.sin(ph(t)) - 12 * max(0.0, sg * math.cos(ph(t))) ** 2, 0, 0))
        c.f(f"{nm}_shin", "rotation", lambda t, sg=sg: (46 * max(0.0, sg * math.cos(ph(t))) ** 1.5, 0, 0))
        c.f(f"{nm}_foot", "rotation", lambda t, sg=sg: (A * sg * math.sin(ph(t)) * 0.55 - 30 * max(0.0, sg * math.cos(ph(t))) ** 1.5, 0, 0))
        c.f(f"{nm}_arm", "rotation", lambda t, sg=sg, s=s: (13 * sg * math.sin(ph(t)), 0, -s * 2))
        c.f(f"{nm}_forearm", "rotation", lambda t, sg=sg: (-6 - 8 * max(0.0, -sg * math.sin(ph(t))), 0, 0))
        c.f(f"{nm}_hand", "rotation", lambda t, sg=sg: (7 * sg * math.sin(ph(t) - 0.7), 0, 0))
    c.f("body", "position", lambda t: (0, -1.2 + 1.2 * math.cos(2 * ph(t)), 0))
    c.f("body", "rotation", lambda t: (0, -3 * math.sin(ph(t)), 2.0 * math.sin(ph(t))))
    c.f("torso", "rotation", lambda t: (3 + 1.2 * math.cos(2 * ph(t)), 6 * math.sin(ph(t)), -1.6 * math.sin(ph(t))))
    c.f("neck", "rotation", lambda t: (-3 - 1.0 * math.cos(2 * ph(t) - 0.5), -3 * math.sin(ph(t)), 1.2 * math.sin(ph(t))))
    c.f("tabard", "rotation", lambda t: (-(A + 8) * abs(math.sin(ph(t))) - 4, 0, 0))
    for k, (up, low) in enumerate(CLOAK):
        c.f(up, "rotation", lambda t, k=k: (3 + 1.5 * math.cos(2 * ph(t) - 0.8), 0, 0))
        c.f(low, "rotation", lambda t, k=k: (3 + 3 * math.cos(2 * ph(t) - 1.4 + k * 0.5), 0, 2.5 * math.sin(ph(t) - 1.0 + k)))
    return c


def anim_void_cleave():
    """Right-handed horizontal sweep from behind the right shoulder across to the left (hit 0.8)."""
    L = 1.4
    c = Clip("attack.void_cleave", L)
    ambient(c, L, crown_turn=lambda t: float(tr([(0, 0), (0.55, 0.15), (0.85, 0.8, "out"), (1.4, 1.0)])(t)),
            radial=lambda t: float(tr([(0, 0), (0.6, -0.8), (0.8, 2.5, "snap"), (1.4, 0)])(t)),
            star_scale=lambda t: float(tr([(0, 1), (0.6, 1.25), (0.8, 1.6, "snap"), (1.4, 1)])(t)))
    c.rot("torso", [(0, (0, 0, 0)), (0.55, (-6, 36, 4), "io"), (0.7, (0, 14, 0), "in"), (0.8, (8, -34, -4), "lin"),
                    (0.95, (10, -42, -5), "out"), (1.4, (0, 0, 0), "io")])
    c.f("torso", "rotation", lambda t: (tremor(t, 0.8, 0.84, 0.95, 1.1, 1.2, 24), 0, 0))
    crouch(c, lambda t: float(tr([(0, 0), (0.55, 2.0), (0.8, 3.5, "snap"), (1.0, 3.2), (1.4, 0)])(t)), spread=0.5)
    c.rot("body", [(0, (0, 0, 0)), (0.55, (0, 8, 0)), (0.8, (0, -8, 0), "snap"), (1.4, (0, 0, 0))])
    c.rot("neck", [(0, (0, 0, 0)), (0.55, (4, -22, 0)), (0.8, (-4, 24, 0), "snap"), (0.95, (-2, 26, 0)), (1.4, (0, 0, 0))])
    c.rot("right_arm", [(0, (0, 0, 0)), (0.25, (-40, 40, 20)), (0.55, (-80, 115, 0), "io"), (0.7, (-88, 60, 0), "in"),
                        (0.8, (-88, -25, 0), "lin"), (0.95, (-74, -55, 0), "out"), (1.4, (0, 0, 0), "io")])
    c.rot("right_forearm", [(0, (0, 0, 0)), (0.55, (-38, 0, 0)), (0.7, (-14, 0, 0)), (0.8, (-4, 0, 0)), (0.95, (-10, 0, 0)),
                            (1.4, (0, 0, 0))])
    c.rot("right_hand", [(0, (0, 0, 0)), (0.55, (-20, 0, 25)), (0.8, (10, 0, -10), "snap"), (1.4, (0, 0, 0))])
    c.rot("left_arm", [(0, (0, 0, 0)), (0.55, (-34, 0, -12)), (0.8, (30, 0, -28), "snap"), (0.95, (32, 0, -30)),
                       (1.4, (0, 0, 0))])
    c.rot("left_forearm", [(0, (0, 0, 0)), (0.55, (-40, 0, 0)), (0.8, (-18, 0, 0)), (1.4, (0, 0, 0))])
    c.rot("left_hand", [(0, (0, 0, 0)), (0.8, (0, 0, -20), "snap"), (1.4, (0, 0, 0))])
    c.rot("spines", [(0, (0, 0, 0)), (0.55, (-4, 0, 0)), (0.8, (5, 0, 0), "snap"), (1.4, (0, 0, 0))])
    cloak_keys(c, [(0, 0), (0.55, -3), (0.8, 8, "snap"), (1.4, 0)], [(0, 0), (0.6, -4), (0.85, 12, "snap"), (1.4, 0)],
               [(0, 0), (0.8, 10, "snap"), (1.4, 0)])
    return c


def anim_void_meteors():
    """Both arms raised to the sky, then alternating claw-thrusts pull a meteor down each 0.3 s."""
    L = 2.5
    c = Clip("attack.void_meteors", L)
    up = lambda t: env(t, 0.0, 0.55, 2.1, 2.5)
    ambient(c, L, crown_turn=lambda t: float(tr([(0, 0), (0.6, 0.2), (2.1, 0.9), (2.5, 1.0)])(t)), bob=1.2,
            lift=lambda t: 6.0 * up(t), radial=lambda t: 2.5 * up(t),
            star_scale=lambda t: 1 + 0.35 * up(t))
    pulses = [0.6, 0.9, 1.2, 1.5, 1.8, 2.1]
    pulse = lambda t, k: math.exp(-((t - k - 0.04) / 0.06) ** 2)
    c.rot("torso", [(0, (0, 0, 0)), (0.55, (-12, 0, 0), "io"), (2.1, (-10, 0, 0)), (2.5, (0, 0, 0), "io")])
    c.f("torso", "rotation", lambda t: (sum(5 * pulse(t, k) for k in pulses), sum((-1) ** i * 4 * pulse(t, k) for i, k in enumerate(pulses)), 0))
    c.rot("neck", [(0, (0, 0, 0)), (0.55, (-14, 0, 0)), (2.1, (-12, 0, 0)), (2.5, (0, 0, 0))])
    crouch(c, lambda t: 1.5 * up(t) + sum(0.8 * pulse(t, k) for k in pulses))
    for s, nm in sides():
        mine = [k for i, k in enumerate(pulses) if (i % 2 == 0) == (s < 0)]
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.3, (-90, 0, -s * 10)), (0.55, (-165, 0, -s * 24), "out"), (2.1, (-160, 0, -s * 26)),
                            (2.5, (0, 0, 0), "io")])
        c.f(f"{nm}_arm", "rotation", lambda t, mine=mine: (sum(70 * pulse(t, k) for k in mine), 0, 0))
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.55, (-12, 0, 0)), (2.1, (-12, 0, 0)), (2.5, (0, 0, 0))])
        c.f(f"{nm}_forearm", "rotation", lambda t, mine=mine: (sum(-25 * pulse(t, k) for k in mine), 0, 0))
        c.rot(f"{nm}_hand", [(0, (0, 0, 0)), (0.55, (-20, 0, -s * 15)), (2.1, (-20, 0, -s * 15)), (2.5, (0, 0, 0))])
    c.rot("spines", [(0, (0, 0, 0)), (0.55, (-5, 0, 0)), (2.1, (-5, 0, 0)), (2.5, (0, 0, 0))])
    cloak_keys(c, [(0, 0), (0.55, 4), (2.1, 4), (2.5, 0)], [(0, 0), (0.55, 6), (2.1, 6), (2.5, 0)],
               [(0, 0), (0.55, 8), (2.1, 8), (2.5, 0)])
    return c


def anim_black_hole():
    """Cups a singularity at the chest, thrusts it out (0.85) and holds the pull, straining."""
    L = 3.0
    c = Clip("attack.black_hole", L)
    hold = lambda t: env(t, 0.75, 0.9, 2.55, 2.95)
    gather = lambda t: env(t, 0.0, 0.7, 0.75, 0.9)
    ambient(c, L, crown_turn=lambda t: float(tr([(0, 0), (0.8, 0.2), (2.6, 0.92, "lin"), (3.0, 1.0)])(t)),
            radial=lambda t: -1.5 * gather(t) - 3.0 * hold(t), lift=lambda t: -1.5 * hold(t), bob=0.4,
            star_turn=lambda t: float(tr([(0, 0), (0.75, 0.6, "in"), (0.9, 0.7), (3.0, 1.0)])(t)),
            star_scale=lambda t: float(tr([(0, 1), (0.7, 1.9, "in"), (0.85, 0.5, "snap"), (1.1, 1.15), (2.6, 1.15), (3.0, 1)])(t)))
    c.rot("torso", [(0, (0, 0, 0)), (0.7, (12, 0, 0), "io"), (0.88, (-6, 0, 0), "snap"), (2.55, (-4, 0, 0)), (3.0, (0, 0, 0), "io")])
    c.f("torso", "rotation", lambda t: (tremor(t, 0.9, 1.0, 2.5, 2.7, 1.0, 21), tremor(t, 0.9, 1.0, 2.5, 2.7, 0.8, 17, 2), 0))
    c.rot("neck", [(0, (0, 0, 0)), (0.7, (8, 0, 0)), (0.88, (-6, 0, 0), "snap"), (2.55, (-4, 0, 0)), (3.0, (0, 0, 0))])
    crouch(c, lambda t: 2.0 * gather(t) + 2.5 * hold(t), spread=0.6)
    for s, nm in sides():
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.7, (-55, s * 30, 0), "io"), (0.88, (-86, s * 12, 0), "snap"), (2.55, (-84, s * 14, 0)),
                            (3.0, (0, 0, 0), "io")])
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.7, (-62, 0, 0)), (0.88, (-6, 0, 0), "snap"), (2.55, (-8, 0, 0)), (3.0, (0, 0, 0))])
        c.rot(f"{nm}_hand", [(0, (0, 0, 0)), (0.7, (-20, 0, s * 30)), (0.88, (-60, 0, -s * 20), "snap"), (2.55, (-58, 0, -s * 22)),
                             (3.0, (0, 0, 0))])
        c.f(f"{nm}_hand", "rotation", lambda t, s=s: (tremor(t, 0.9, 1.0, 2.5, 2.7, 3, 26, 1 + s), 0, 0))
    cloak_keys(c, [(0, 0), (0.7, -2), (0.88, -6, "snap"), (2.55, -5), (3.0, 0)], [(0, 0), (0.88, -8, "snap"), (2.55, -7), (3.0, 0)],
               [(0, 0), (0.88, -6, "snap"), (2.55, -6), (3.0, 0)])
    c.rot("spines", [(0, (0, 0, 0)), (0.7, (4, 0, 0)), (0.88, (-4, 0, 0), "snap"), (3.0, (0, 0, 0))])
    return c


def anim_abyssal_rend():
    """Both claws raised crossed overhead, then a violent downward X-rake (impact 1.0)."""
    L = 2.0
    c = Clip("attack.abyssal_rend", L)
    ambient(c, L, crown_turn=lambda t: float(tr([(0, 0), (0.8, 0.25), (1.05, 0.75, "snap"), (2.0, 1.0)])(t)),
            lift=lambda t: float(tr([(0, 0), (0.8, 2.5), (1.0, -1.0, "snap"), (1.4, -0.5), (2.0, 0)])(t)),
            radial=lambda t: float(tr([(0, 0), (0.8, -1.0), (1.0, 3.0, "snap"), (1.4, 2.5), (2.0, 0)])(t)),
            star_scale=lambda t: float(tr([(0, 1), (0.8, 1.3), (1.0, 1.75, "snap"), (1.4, 1.5), (2.0, 1)])(t)))
    c.rot("torso", [(0, (0, 0, 0)), (0.8, (-20, 0, 0), "io"), (1.0, (24, 0, 0), "snap"), (1.4, (22, 0, 0)), (2.0, (0, 0, 0), "io")])
    c.f("torso", "rotation", lambda t: (tremor(t, 1.0, 1.04, 1.3, 1.5, 1.4, 23), tremor(t, 1.0, 1.04, 1.3, 1.5, 1.0, 19, 2), 0))
    c.rot("neck", [(0, (0, 0, 0)), (0.8, (-12, 0, 0)), (1.0, (-16, 0, 0), "snap"), (1.4, (-14, 0, 0)), (2.0, (0, 0, 0))])
    crouch(c, lambda t: float(tr([(0, 0), (0.8, 1.5), (1.0, 5.0, "snap"), (1.4, 4.6), (2.0, 0)])(t)), spread=0.8)
    for s, nm in sides():
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.4, (-100, 0, -s * 20)), (0.8, (-172, s * 8, s * 14), "out"),
                            (0.9, (-130, s * 18, 0), "in"), (1.0, (-80, s * 28, 0), "lin"), (1.4, (-76, s * 26, -s * 2)),
                            (2.0, (0, 0, 0), "io")])
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.8, (-30, 0, 0)), (1.0, (-6, 0, 0), "snap"), (1.4, (-8, 0, 0)), (2.0, (0, 0, 0))])
        c.rot(f"{nm}_hand", [(0, (0, 0, 0)), (0.8, (-35, 0, 0)), (1.0, (25, 0, 0), "snap"), (1.4, (22, 0, 0)), (2.0, (0, 0, 0))])
    c.rot("spines", [(0, (0, 0, 0)), (0.8, (-6, 0, 0)), (1.0, (8, 0, 0), "snap"), (2.0, (0, 0, 0))])
    cloak_keys(c, [(0, 0), (0.8, -4), (1.0, 6, "snap"), (1.4, 5), (2.0, 0)], [(0, 0), (0.85, -5), (1.05, 8, "snap"), (2.0, 0)],
               [(0, 0), (1.0, 5, "snap"), (1.4, 4), (2.0, 0)])
    return c


def anim_wraith_call():
    """Left claw raised to beckon, right flung low and wide; the cloak billows as wraiths tear free (0.75)."""
    L = 1.5
    c = Clip("attack.wraith_call", L)
    ambient(c, L, crown_turn=lambda t: float(tr([(0, 0), (0.75, 0.6, "io"), (1.5, 1.0)])(t)),
            lift=lambda t: float(tr([(0, 0), (0.6, 1.5), (0.75, 4.0, "snap"), (1.5, 0)])(t)),
            star_scale=lambda t: float(tr([(0, 1), (0.6, 1.2), (0.75, 1.55, "snap"), (1.5, 1)])(t)))
    c.rot("torso", [(0, (0, 0, 0)), (0.6, (6, -12, 4), "io"), (0.75, (-12, 10, -3), "snap"), (1.05, (-10, 8, -2)), (1.5, (0, 0, 0), "io")])
    c.rot("neck", [(0, (0, 0, 0)), (0.6, (8, 0, 0)), (0.75, (-24, 0, 6), "snap"), (1.05, (-22, 0, 5)), (1.5, (0, 0, 0))])
    crouch(c, lambda t: float(tr([(0, 0), (0.6, 2.5), (0.75, 0.5, "snap"), (1.5, 0)])(t)))
    c.rot("left_arm", [(0, (0, 0, 0)), (0.6, (-60, 0, 10)), (0.75, (-172, 0, -18), "snap"), (1.05, (-168, 0, -20)), (1.5, (0, 0, 0), "io")])
    c.rot("left_forearm", [(0, (0, 0, 0)), (0.6, (-70, 0, 0)), (0.75, (-15, 0, 0), "snap"), (1.05, (-18, 0, 0)), (1.5, (0, 0, 0))])
    c.rot("left_hand", [(0, (0, 0, 0)), (0.6, (30, 0, 0)), (0.75, (-30, 0, -20), "snap"), (1.5, (0, 0, 0))])
    c.rot("right_arm", [(0, (0, 0, 0)), (0.6, (20, 0, 10)), (0.75, (-10, 0, 58), "snap"), (1.05, (-8, 0, 55)), (1.5, (0, 0, 0), "io")])
    c.rot("right_forearm", [(0, (0, 0, 0)), (0.6, (-40, 0, 0)), (0.75, (-8, 0, 0), "snap"), (1.5, (0, 0, 0))])
    c.rot("right_hand", [(0, (0, 0, 0)), (0.75, (0, 0, 25), "snap"), (1.5, (0, 0, 0))])
    c.rot("spines", [(0, (0, 0, 0)), (0.6, (4, 0, 0)), (0.75, (-8, 0, 0), "snap"), (1.5, (0, 0, 0))])
    cloak_keys(c, [(0, 0), (0.6, -2), (0.75, 16, "snap"), (1.05, 14), (1.5, 0)], [(0, 0), (0.65, -4), (0.8, 22, "snap"), (1.1, 18), (1.5, 0)],
               [(0, 0), (0.6, -3), (0.75, 26, "snap"), (1.05, 22), (1.5, 0)])
    return c


def anim_collapse():
    """Claws raised, then driven into the ground in a deep crouch (0.5): the floor breaks."""
    L = 2.0
    c = Clip("attack.collapse", L)
    ambient(c, L, crown_turn=lambda t: float(tr([(0, 0), (0.5, 0.45, "in"), (2.0, 1.0)])(t)),
            lift=lambda t: float(tr([(0, 0), (0.35, 2.0), (0.5, -2.0, "snap"), (1.2, -1.5), (2.0, 0)])(t)),
            radial=lambda t: float(tr([(0, 0), (0.35, -1.0), (0.5, 3.5, "snap"), (1.2, 3.0), (2.0, 0)])(t)),
            star_scale=lambda t: float(tr([(0, 1), (0.35, 1.25), (0.5, 1.6, "snap"), (1.2, 1.4), (2.0, 1)])(t)))
    c.rot("torso", [(0, (0, 0, 0)), (0.35, (-14, 0, 0), "io"), (0.5, (54, 0, 0), "in3"), (1.2, (52, 0, 0)), (2.0, (0, 0, 0), "io")])
    c.f("torso", "rotation", lambda t: (tremor(t, 0.5, 0.53, 1.0, 1.25, 1.5, 24), tremor(t, 0.5, 0.53, 1.0, 1.25, 1.0, 20, 3), 0))
    c.rot("neck", [(0, (0, 0, 0)), (0.35, (-10, 0, 0)), (0.5, (-36, 0, 0), "in3"), (1.2, (-34, 0, 0)), (2.0, (0, 0, 0))])
    crouch(c, lambda t: float(tr([(0, 0), (0.35, 2.5), (0.5, 14.0, "in3"), (1.2, 13.5), (2.0, 0, "io")])(t)), spread=1.2)
    c.f("body", "position", lambda t: (0, tremor(t, 0.5, 0.52, 0.9, 1.1, 0.4, 30), 0))
    for s, nm in sides():
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.35, (-150, 0, -s * 16), "out"), (0.5, (-60, 0, -s * 14), "in3"), (1.2, (-58, 0, -s * 14)),
                            (2.0, (0, 0, 0), "io")])
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.35, (-30, 0, 0)), (0.5, (-6, 0, 0), "in3"), (1.2, (-6, 0, 0)), (2.0, (0, 0, 0))])
        c.rot(f"{nm}_hand", [(0, (0, 0, 0)), (0.35, (-30, 0, 0)), (0.5, (30, 0, 0), "in3"), (1.2, (28, 0, 0)), (2.0, (0, 0, 0))])
    c.rot("spines", [(0, (0, 0, 0)), (0.35, (-5, 0, 0)), (0.5, (8, 0, 0), "in3"), (1.2, (6, 0, 0)), (2.0, (0, 0, 0))])
    cloak_keys(c, [(0, 0), (0.35, 2), (0.5, -26, "in3"), (1.2, -24), (2.0, 0)], [(0, 0), (0.5, -18, "in3"), (1.2, -16), (2.0, 0)],
               [(0, 0), (0.5, 10, "in3"), (1.2, 9), (2.0, 0)])
    c.rot("tabard", [(0, (0, 0, 0)), (0.5, (-40, 0, 0), "in3"), (1.2, (-38, 0, 0)), (2.0, (0, 0, 0))])
    return c


def anim_unmaking():
    """Rises off the ground arms spread, the crown flung wide; it warps (teleports at 0.2/1.1/2.0)
    and pulses a blast at 0.6/1.5/2.4."""
    L = 3.0
    c = Clip("attack.unmaking", L)
    up = lambda t: env(t, 0.0, 0.35, 2.6, 3.0)
    blasts = [0.6, 1.5, 2.4]
    warps = [0.2, 1.1, 2.0]
    bl = lambda t: sum(math.exp(-((t - k) / 0.07) ** 2) for k in blasts)
    pre = lambda t: sum(math.exp(-((t - k + 0.13) / 0.07) ** 2) for k in blasts)
    wp = lambda t: sum(math.exp(-((t - k) / 0.05) ** 2) for k in warps)
    ambient(c, L, crown_turn=lambda t: float(tr([(0, 0), (0.4, 0.1), (2.6, 0.9, "lin"), (3.0, 1.0)])(t)),
            radial=lambda t: 4.0 * up(t) + 2.0 * bl(t) - 2.0 * pre(t), lift=lambda t: 2.0 * up(t), bob=1.0, cloak=1.5,
            star_scale=lambda t: 1 + 0.4 * up(t) + 0.6 * bl(t) - 0.3 * pre(t))
    c.f("body", "position", lambda t: (0, 3.5 * up(t) + 0.8 * math.sin(TAU * t / 1.5) * up(t), 0))
    c.f("body", "scale", lambda t: (1 - 0.18 * wp(t), 1 + 0.22 * wp(t), 1 - 0.18 * wp(t)))
    c.f("halo", "scale", lambda t: (1 + 0.5 * up(t) + 0.3 * bl(t), 1, 1 + 0.5 * up(t) + 0.3 * bl(t)))
    c.f("torso", "rotation", lambda t: (-8 * up(t) + 10 * pre(t) - 6 * bl(t), 0, 0))
    c.f("neck", "rotation", lambda t: (-14 * up(t) + 8 * pre(t) - 8 * bl(t), 0, 0))
    for s, nm in sides():
        sg = 1 if nm == "right" else -1
        c.f(f"{nm}_leg", "rotation", lambda t, sg=sg: ((8 + 4 * sg) * up(t), 0, -sg * 3 * up(t)))
        c.f(f"{nm}_shin", "rotation", lambda t, sg=sg: ((14 + 8 * sg) * up(t), 0, 0))
        c.f(f"{nm}_foot", "rotation", lambda t: (30 * up(t), 0, 0))
        c.f(f"{nm}_arm", "rotation", lambda t, s=s: (-10 * up(t) - 55 * pre(t), s * 20 * pre(t), -s * (72 * up(t) - 50 * pre(t) + 12 * bl(t))))
        c.f(f"{nm}_forearm", "rotation", lambda t: (-12 * up(t) - 40 * pre(t), 0, 0))
        c.f(f"{nm}_hand", "rotation", lambda t, s=s: (-15 * up(t), 0, -s * (25 * up(t) + 20 * bl(t))))
    c.f("spines", "rotation", lambda t: (-6 * up(t) - 4 * bl(t), 0, 0))
    for k, (u, lo) in enumerate(CLOAK):
        c.f(u, "rotation", lambda t: (12 * up(t) + 6 * bl(t), 0, 0))
        c.f(lo, "rotation", lambda t, k=k: (10 * up(t) + 3 * math.sin(TAU * 2 * t / L + k) * up(t), 0, 0))
    for s, nm in sides():
        c.f(f"cloak_{nm}", "rotation", lambda t, s=s: (0, 0, -s * (14 * up(t) + 8 * bl(t))))
    c.f("tabard", "rotation", lambda t: (-12 * up(t), 0, 0))
    return c


def anim_phase():
    """Power-up roar: hunch with arms crossed over the chest, then explode outward (0.75)."""
    L = 2.0
    c = Clip("phase", L)
    ambient(c, L, crown_turn=lambda t: float(tr([(0, 0), (0.5, 0.05), (0.9, 0.7, "out"), (2.0, 1.0)])(t)),
            radial=lambda t: float(tr([(0, 0), (0.5, -2.0), (0.75, 6.0, "snap"), (1.5, 5.0), (2.0, 0, "io")])(t)),
            lift=lambda t: float(tr([(0, 0), (0.5, -1.5), (0.75, 4.0, "snap"), (1.5, 3.5), (2.0, 0, "io")])(t)),
            star_turn=lambda t: float(tr([(0, 0), (0.5, 0.1), (0.8, 0.7, "out"), (2.0, 1.0)])(t)),
            star_scale=lambda t: float(tr([(0, 1), (0.5, 0.55), (0.75, 2.1, "snap"), (1.5, 1.8), (2.0, 1, "io")])(t)), cloak=1.4)
    c.rot("torso", [(0, (0, 0, 0)), (0.5, (18, 0, 0), "io"), (0.75, (-22, 0, 0), "snap"), (1.5, (-20, 0, 0)), (2.0, (0, 0, 0), "io")])
    c.f("torso", "rotation", lambda t: (tremor(t, 0.75, 0.8, 1.4, 1.55, 1.5, 24), tremor(t, 0.75, 0.8, 1.4, 1.55, 1.1, 19, 3), 0))
    c.rot("neck", [(0, (0, 0, 0)), (0.5, (16, 0, 0)), (0.75, (-26, 0, 0), "snap"), (1.5, (-24, 0, 0)), (2.0, (0, 0, 0))])
    crouch(c, lambda t: float(tr([(0, 0), (0.5, 3.5), (0.75, 0.0, "snap"), (2.0, 0)])(t)), spread=0.5)
    for s, nm in sides():
        c.rot(f"{nm}_arm", [(0, (0, 0, 0)), (0.5, (-62, s * 48, 0), "io"), (0.75, (-22, 0, -s * 108), "snap"),
                            (1.5, (-20, 0, -s * 104)), (2.0, (0, 0, 0), "io")])
        c.rot(f"{nm}_forearm", [(0, (0, 0, 0)), (0.5, (-90, 0, 0)), (0.75, (-18, 0, 0), "snap"), (1.5, (-20, 0, 0)), (2.0, (0, 0, 0))])
        c.rot(f"{nm}_hand", [(0, (0, 0, 0)), (0.5, (20, 0, 0)), (0.75, (-20, 0, -s * 30), "snap"), (1.5, (-18, 0, -s * 28)), (2.0, (0, 0, 0))])
        c.pos(f"{nm}_pauldron", [(0, (0, 0, 0)), (0.5, (-0.5 * s, -1.0, 0)), (0.75, (3.0 * s, 4.0, 0), "snap"), (1.5, (2.8 * s, 3.6, 0)),
                                 (2.0, (0, 0, 0), "io")])
        c.rot(f"{nm}_pauldron", [(0, (0, 0, 0)), (0.75, (0, 0, -s * 14), "snap"), (1.5, (0, 0, -s * 12)), (2.0, (0, 0, 0))])
    c.rot("spines", [(0, (0, 0, 0)), (0.5, (6, 0, 0)), (0.75, (-10, 0, 0), "snap"), (1.5, (-9, 0, 0)), (2.0, (0, 0, 0))])
    c.scl("halo", [(0, (1, 1, 1)), (0.5, (0.7, 1, 0.7)), (0.75, (1.6, 1, 1.6), "snap"), (1.5, (1.5, 1, 1.5)), (2.0, (1, 1, 1), "io")])
    c.scl("spines", [(0, (1, 1, 1)), (0.75, (1.08, 1.12, 1.08), "snap"), (1.5, (1.06, 1.1, 1.06)), (2.0, (1, 1, 1))])
    cloak_keys(c, [(0, 0), (0.5, -4), (0.75, 22, "snap"), (1.5, 18), (2.0, 0)], [(0, 0), (0.55, -6), (0.85, 26, "snap"), (1.5, 20), (2.0, 0)],
               [(0, 0), (0.5, -4), (0.75, 24, "snap"), (1.5, 20), (2.0, 0)])
    return c


def anim_death(m):
    """Jolts as the star gutters, clutches the cavity, staggers and falls to its knees, then slumps.
    The crown shards fall and land flat on the floor around it; the star shrinks to nothing."""
    L = 2.8
    c = Clip("death", L, loop="hold")
    c.rot("torso", [(0, (0, 0, 0)), (0.22, (-18, 0, -4), "out"), (0.7, (-6, 10, 4)), (1.2, (8, -4, 6)), (1.75, (22, 0, 8), "io"),
                    (2.35, (40, 0, 8), "io"), (2.8, (40, 0, 8))])
    c.f("torso", "rotation", lambda t: (tremor(t, 0.18, 0.28, 1.0, 1.3, 2.5, 20), tremor(t, 0.18, 0.28, 1.0, 1.3, 2.0, 17, 2), 0))
    drop = tr([(0, 0.0), (1.2, 0.0), (1.75, 17.0, "in"), (1.9, 16.2, "out"), (2.05, 17.0, "in"), (2.8, 17.0)])
    c.f("body", "position", lambda t: (0, -float(drop(t)), -1.0 * float(drop(t)) / 17))
    kneel = lambda t: min(1.0, float(drop(t)) / 17.0)
    for s, nm in sides():
        sg = 1 if nm == "right" else -1
        c.f(f"{nm}_leg", "rotation", lambda t, sg=sg: (-12 * kneel(t) * (1 if sg > 0 else 0.5), 0, -5 * sg * kneel(t)))
        c.f(f"{nm}_shin", "rotation", lambda t: (95 * kneel(t), 0, 0))
        c.f(f"{nm}_foot", "rotation", lambda t: (80 * kneel(t), 0, 0))
    c.rot("right_arm", [(0, (0, 0, 0)), (0.22, (-30, 0, 36), "out"), (0.7, (-30, -45, 0)), (1.2, (-28, -40, 4)), (1.75, (-20, 0, 12)),
                        (2.35, (-44, 0, 6), "io"), (2.8, (-44, 0, 6))])
    c.rot("right_forearm", [(0, (0, 0, 0)), (0.22, (-30, 0, 0)), (0.7, (-80, 0, 0)), (1.2, (-76, 0, 0)), (1.75, (-20, 0, 0)), (2.35, (-6, 0, 0)),
                            (2.8, (-6, 0, 0))])
    c.rot("left_arm", [(0, (0, 0, 0)), (0.22, (-30, 0, -36), "out"), (0.7, (-14, 0, -30)), (1.2, (-24, 0, -22)), (1.75, (-10, 0, -10)),
                       (2.35, (-40, 0, -8), "io"), (2.8, (-40, 0, -8))])
    c.rot("left_forearm", [(0, (0, 0, 0)), (0.22, (-40, 0, 0)), (0.7, (-20, 0, 0)), (1.75, (-10, 0, 0)), (2.35, (-4, 0, 0)), (2.8, (-4, 0, 0))])
    c.rot("right_hand", [(0, (0, 0, 0)), (0.22, (-30, 0, 30), "out"), (0.7, (55, 0, 0)), (1.2, (50, 0, 0)), (1.75, (0, 0, 0)), (2.35, (20, 0, 0)),
                         (2.8, (20, 0, 0))])
    c.rot("left_hand", [(0, (0, 0, 0)), (0.22, (-30, 0, -30), "out"), (1.2, (-10, 0, -10)), (2.35, (20, 0, 0)), (2.8, (20, 0, 0))])
    for s, nm in sides():
        c.pos(f"{nm}_pauldron", [(0, (0, 0.36, 0)), (0.22, (1.0 * s, 2.0, 0), "out"), (0.9, (0.5 * s, 1.0, 0)), (1.1, (0, -0.6, 0), "in"),
                                 (1.2, (0, -0.2, 0), "out"), (1.3, (0, -0.6, 0), "in"), (2.8, (0, -0.6, 0))])
        c.rot(f"{nm}_pauldron", [(0, (0, 0, 0)), (1.1, (0, 0, -s * 6), "in"), (2.8, (0, 0, -s * 6))])
    c.rot("neck", [(0, (0, 0, 0)), (0.22, (-20, 0, 0), "out"), (0.7, (-8, 10, 0)), (1.75, (10, 0, 0)), (2.35, (26, 0, 0), "io"), (2.8, (26, 0, 0))])
    c.rot("head", [(0, (0, 0, 0)), (1.75, (0, 0, 0)), (2.4, (0, 0, -12), "io"), (2.8, (0, 0, -12))])
    c.rot("spines", [(0, (0, 0, 0)), (0.22, (-8, 0, 0), "out"), (1.2, (2, 0, 0)), (2.35, (10, 0, 0), "io"), (2.8, (10, 0, 0))])
    # the star gutters: flare, violent flicker, collapse to nothing
    c.f("chest_star", "rotation", lambda t: (0, 0, -180 * ease("out", t / 2.2)))
    c.f("chest_star", "scale", lambda t: (max(0.01, float(tr([(0, 1), (0.22, 1.8, "out"), (0.9, 1.1), (2.1, 0.0, "in")])(t))
                                              * (1 + 0.35 * math.sin(t * 61) * env(t, 0.25, 0.4, 1.6, 2.0))),) * 3)
    c.f("crown", "rotation", lambda t: (0, -50 * ease("out", t / 0.9), 0))
    c.scl("halo", [(0, (1, 1, 1)), (0.22, (1.25, 1, 1.25), "out"), (0.85, (1.1, 1, 1.1)), (1.3, (0.01, 0.01, 0.01), "in"), (2.8, (0.01, 0.01, 0.01))])
    # cloak sags back into a drape; tabard settles over the thighs
    for k, (up, low) in enumerate(CLOAK):
        c.rot(up, [(0, (0, 0, 0)), (0.22, (-8, 0, 0), "out"), (1.2, (2, 0, 0)), (1.8, (-12, 0, 0)), (2.35, (-30, 0, 0), "io"), (2.8, (-30, 0, 0))])
        c.rot(low, [(0, (0, 0, 0)), (0.3, (-10, 0, 0), "out"), (1.2, (4, 0, 0)), (1.9, (20, 0, 0)), (2.4, (34 + 4 * k, 0, 0), "io"),
                    (2.8, (34 + 4 * k, 0, 0))])
    c.rot("tabard", [(0, (0, 0, 0)), (1.2, (0, 0, 0)), (1.8, (-36, 0, 0), "io"), (2.8, (-36, 0, 0))])
    falling_shards(c, m, L)
    return c


def falling_shards(c, m, L, t0=0.85):
    """Crown shards drop (gravity ease) from where they hover at t0 to land flat on the floor in a
    ring around the kneeling body. Positions/rotations are solved in each shard's (moving) parent
    frame so the landed shards stay put while the body keeps slumping."""
    geo = gp.load_geo(m.to_json())
    exclude = set(SHARDS)
    times = np.linspace(0, L, int(L / 0.005) + 1)

    def pose_at(t):
        pose = {}
        for (bone, chan) in list(c.parts.keys()):
            if bone in exclude:
                continue
            pose.setdefault(bone, {})[chan] = c.eval(bone, chan, t)
        return pose

    mats = [gp.bone_matrices(geo, pose_at(t)) for t in times]
    bones = {b["name"]: b for b in geo["bones"]}
    order = [4, 1, 3, 0, 5, 2]
    out = {}
    for i, nm in enumerate(SHARDS):
        piv = np.array(bones[nm]["pivot"], dtype=float)
        a = SHARD_ANG[i]
        d_loc = tl.unit(np.array([0.22 * math.cos(a), 1.0, 0.22 * math.sin(a)]))
        bob0 = np.array([0.0, 0.7 * math.sin(TAU * 1 * t0 / L + (0 if i % 2 == 0 else math.pi)), 0.0])
        k0 = int(round(t0 / 0.005))
        M0 = mats[k0]["crown"]
        P0 = M0[:3, :3] @ (piv + bob0) + M0[:3, 3]
        W0 = M0[:3, :3]
        C0 = M0[:3, :3] @ np.array(CROWN_C) + M0[:3, 3]
        rad = P0 - C0
        rad[1] = 0
        rad = tl.unit(rad)
        jit = (i * 0.37) % 1 - 0.5
        land_r = 14.0 + 3.0 * ((i * 0.61) % 1)
        P1 = np.array([C0[0] + rad[0] * land_r, 1.5 if i % 2 == 0 else 1.0,C0[2] + rad[2] * land_r - 2.0])
        d_tgt = tl.unit(tl.axis_angle([0, 1, 0], jit * 50) @ np.array([rad[0], -0.04, rad[2]]))
        W1 = tl.align_y(d_tgt) @ np.linalg.inv(tl.align_y(d_loc))
        Rd = W1 @ W0.T
        ang = math.degrees(math.acos(max(-1.0, min(1.0, (np.trace(Rd) - 1) / 2))))
        axis = np.array([Rd[2, 1] - Rd[1, 2], Rd[0, 2] - Rd[2, 0], Rd[1, 0] - Rd[0, 1]])
        axis = tl.unit(axis) if np.linalg.norm(axis) > 1e-9 else np.array([1.0, 0, 0])
        t1 = 1.55 + 0.07 * order.index(i)
        pos = np.zeros((len(times), 3))
        rot = np.zeros((len(times), 3))
        for k, t in enumerate(times):
            M = mats[k]["crown"]
            R, T = M[:3, :3], M[:3, 3]
            if t < t0:
                pos[k] = [0, 0.7 * math.sin(TAU * t / L + (0 if i % 2 == 0 else math.pi)), 0]
                continue
            f = min(1.0, (t - t0) / (t1 - t0))
            fy = f * f
            bounce = 0.0
            if t > t1:
                bounce = 1.6 * max(0.0, math.sin(min(1.0, (t - t1) / 0.22) * math.pi)) * (1 - min(1.0, (t - t1) / 0.22))
            P = np.array([P0[0] + (P1[0] - P0[0]) * f, P0[1] + (P1[1] - P0[1]) * fy + bounce, P0[2] + (P1[2] - P0[2]) * f])
            W = tl.axis_angle(axis, ang * ease("io", f)) @ W0
            pos[k] = R.T @ (P - T) - piv
            rot[k] = gp.euler_from_matrix(R.T @ W)
        rot = np.degrees(np.unwrap(np.radians(rot), axis=0))
        out[nm] = (pos, rot)
    for nm, (pos, rot) in out.items():
        c.f(nm, "position", lambda t, pos=pos: tuple(np.interp(t, times, pos[:, j]) for j in range(3)))
        c.f(nm, "rotation", lambda t, rot=rot: tuple(np.interp(t, times, rot[:, j]) for j in range(3)))


def clips(m):
    return [anim_idle(), anim_walk(), anim_void_cleave(), anim_void_meteors(), anim_black_hole(), anim_abyssal_rend(),
            anim_wraith_call(), anim_collapse(), anim_unmaking(), anim_phase(), anim_death(m)]


POSES = [
    ("idle", [0.0, 1.0, 2.0, 3.0]),
    ("walk", [0.0, 0.3, 0.6, 0.9]),
    ("attack.void_cleave", [0.3, 0.55, 0.8, 0.95, 1.3]),
    ("attack.void_meteors", [0.3, 0.6, 0.66, 1.5, 2.3]),
    ("attack.black_hole", [0.4, 0.7, 0.9, 2.0, 2.8]),
    ("attack.abyssal_rend", [0.4, 0.8, 0.9, 1.0, 1.6]),
    ("attack.wraith_call", [0.3, 0.6, 0.75, 1.0, 1.4]),
    ("attack.collapse", [0.2, 0.35, 0.5, 1.0, 1.6]),
    ("attack.unmaking", [0.2, 0.47, 0.6, 1.3, 2.8]),
    ("phase", [0.3, 0.5, 0.75, 1.2, 1.9]),
    ("death", [0.22, 0.7, 1.4, 1.9, 2.8]),
]
HERO = ("attack.abyssal_rend", 1.0)


def validate(geo, anims):
    names = {b["name"] for b in geo["minecraft:geometry"][0]["bones"]}
    for req in ("root", "body", "head"):
        assert req in names, req
    req_anims = {"idle": None, "walk": None, "death": 2.8, "phase": 2.0, "attack.void_cleave": 1.4, "attack.void_meteors": 2.5,
                 "attack.black_hole": 3.0, "attack.abyssal_rend": 2.0, "attack.wraith_call": 1.5, "attack.collapse": 2.0,
                 "attack.unmaking": 3.0}
    for an, ln in req_anims.items():
        a = anims["animations"][an]
        if ln:
            assert abs(a["animation_length"] - ln) < 1e-6, (an, a["animation_length"])
        for b in a["bones"]:
            assert b in names, (an, b)
    for b in geo["minecraft:geometry"][0]["bones"]:
        if b["name"] == "head":
            assert "rotation" not in b
    desc = geo["minecraft:geometry"][0]["description"]
    from PIL import Image
    paths = tl.asset_paths(NAME)
    for k in ("tex", "glow"):
        im = Image.open(paths[k])
        assert im.size == (desc["texture_width"] * 2, desc["texture_height"] * 2), (k, im.size)
    print("validate ok:", len(names), "bones;", sorted(anims["animations"].keys()))


def main():
    m = build_model()
    m.pack()            # to_json needs UVs (tl.build packs again, deterministically)
    # rest-pose world position of the star, for the cavity light in the frame shader
    mats = gp.bone_matrices(gp.load_geo(m.to_json()))
    vm.CAVITY["c"] = (mats["torso"] @ np.array([*CAV, 1.0]))[:3]
    geo, rgba, glow, anims = tl.build(NAME, m, vm.SHADERS, clips(m), visible=(8, 8, 3.0))
    validate(geo, anims)
    if "--preview" in sys.argv:
        print(fx.preview_rest(NAME, geo, rgba, glow, HITBOX))
        print(fx.preview_pose(NAME, geo, rgba, glow, anims, HERO[0], HERO[1]))
        if "--all" in sys.argv:
            print(fx.preview_pose(NAME, geo, rgba, glow, anims, "attack.void_cleave", 0.8))
            for an, times in POSES:
                print(fx.preview_strip(NAME, geo, rgba, glow, anims, an, times, HITBOX))
            print(fx.preview_strip(NAME, geo, rgba, glow, anims, "walk", [0.0, 0.15, 0.3, 0.45, 0.6, 0.75], HITBOX, yaw=90,
                                   tag="_side"))
            print(fx.preview_strip(NAME, geo, rgba, glow, anims, "death", [1.4, 1.9, 2.8], HITBOX, yaw=90, tag="_side"))
    if "--inspect" in sys.argv:
        out = os.path.join(os.environ.get("TEMP", "."), "vs_inspect")
        os.makedirs(out, exist_ok=True)
        g = geo
        print(fx.inspect(NAME, g, rgba, glow, yaw=15, pitch=-6, center=(0, 66), frame=34, out=os.path.join(out, "chest.png")))
        print(fx.inspect(NAME, g, rgba, glow, yaw=25, pitch=-6, center=(0, 80), frame=26, out=os.path.join(out, "head.png")))
        print(fx.inspect(NAME, g, rgba, glow, yaw=150, pitch=-8, center=(0, 40), frame=60, out=os.path.join(out, "cloak.png")))
        print(fx.inspect(NAME, g, rgba, glow, yaw=40, pitch=-6, center=(-14, 34), frame=28, out=os.path.join(out, "hand.png")))


if __name__ == "__main__":
    main()
