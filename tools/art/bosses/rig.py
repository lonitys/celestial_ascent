"""Animation helpers for the boss rigs (Bedrock rotation conventions, see anim_helpers.py):

  rot x > 0 : top of a bone tips forward (-Z); a hanging limb swings BACK; a jaw opens.
  rot x < 0 : hanging limb swings forward / up in front.
  rot z > 0 : right arm (at -X) rises outward; left arm (at +X) rises outward with z < 0.
  rot y > 0 : turns so the model's right shoulder moves back.
"""
import math

import numpy as np

from bosslib import Clip, Track, ease, env, shake

TAU = 2 * math.pi


def mir(v):
    """Mirror a rotation for the opposite side (x, -y, -z)."""
    return (v[0], -v[1], -v[2])


def mirp(v):
    """Mirror a position for the opposite side (-x, y, z)."""
    return (-v[0], v[1], v[2])


def sides():
    return ((-1, "right"), (1, "left"))


def knee_bend(clip, drop_fn, thigh, shin, legs, feet=None, spread=0.0):
    """Rotation-only knee bend for legs parented to a body that drops by drop_fn(t) (>0 = lower),
    so the feet stay planted and flat. legs = [(thigh_bone, shin_bone), ...]."""
    L = thigh + shin

    def angle(t):
        d = max(0.0, min(drop_fn(t), L * 0.7))
        c = 1 - d / L
        return math.degrees(math.acos(max(-1.0, min(1.0, c))))

    for k, (lg, sh) in enumerate(legs):
        sgn = -1 if lg.startswith("right") else 1
        clip.f(lg, "rotation", lambda t, sgn=sgn: (-angle(t), 0, -sgn * spread * angle(t) / 30.0))
        clip.f(sh, "rotation", lambda t: (2 * angle(t), 0, 0))
        if feet:
            clip.f(feet[k], "rotation", lambda t: (-angle(t), 0, 0))


def keys(*pairs, e="io"):
    """keys((t, v), (t, v, ease)...) passthrough with a default ease."""
    out = []
    for p in pairs:
        out.append(p if len(p) > 2 else (p[0], p[1], e))
    return out


def wave(T, amp=1.0, phase=0.0, harmonic=1):
    return lambda t: amp * math.sin(TAU * harmonic * t / T + phase)


def tremor(t, t0, t1, t2, t3, amp, freq=22.0, seed=0):
    return shake(t, freq, amp, seed) * env(t, t0, t1, t2, t3)
