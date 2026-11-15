"""Shared animation helpers for the titan rigs (Bedrock rotation conventions):

  rot x > 0 : top of a bone tips forward (-Z); a hanging limb swings BACK; a jaw opens.
  rot x < 0 : hanging limb swings forward / up in front.
  rot z > 0 : tips towards +X (model's left). Right arm (at -X) rises outward with z > 0,
              left arm rises outward with z < 0.
  rot y > 0 : turns so the model's right shoulder moves back.
"""
import math

import numpy as np

from titanlib import ease, env, shake, Track

TAU = 2 * math.pi


def mirror(v):
    """Mirror a rotation for the opposite side (x, -y, -z)."""
    return (v[0], -v[1], -v[2])


def legs_for_drop(clip, drop_fn, thigh=9.0, shin=12.0, legs=(("right_leg", "right_shin"), ("left_leg", "left_shin")),
                  body="body", spread=0.0, feet=("right_foot", "left_foot")):
    """Bend knees so the feet stay planted (and flat) while the body drops by drop_fn(t) units (>0 = lower)."""
    L = thigh + shin

    def angle(t):
        d = max(0.0, min(drop_fn(t), L * 0.6))
        return math.degrees(math.acos(1 - d / L))

    for k, (leg, sh) in enumerate(legs):
        sgn = -1 if leg.startswith("right") else 1
        clip.f(leg, "rotation", lambda t, sgn=sgn: (-angle(t), 0, sgn * spread * angle(t) / 30.0))
        clip.f(leg, "position", lambda t: (0, -max(0.0, drop_fn(t)), 0))
        clip.f(sh, "rotation", lambda t: (2 * angle(t), 0, 0))
        if feet:
            clip.f(feet[k], "rotation", lambda t: (-angle(t), 0, 0))
    if body:
        clip.f(body, "position", lambda t: (0, -max(0.0, drop_fn(t)), 0))


def track(keys):
    return Track(keys)


def periodic(amp, period, phase=0.0, harmonic=1):
    return lambda t: amp * math.sin(TAU * harmonic * t / period + phase)
