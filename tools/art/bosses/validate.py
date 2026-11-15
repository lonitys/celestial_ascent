"""Validate the six boss asset sets against the contract the Java side depends on.

  python validate.py            -> report; exit code 1 on any error

Checks per boss: the 4 files exist and parse; geo format/identifier; PNG + glowmask are exactly 2x
the declared texture size; glowmask is transparent except emissive pixels; bone tree is sound
(root at 0,0,0 is the ancestor of everything, unique names, known parents); required bones; head has
no rest rotation; cube count 40-140; UVs inside the atlas; every animation exists with the right
length/loop mode, references only existing bones, has finite keys inside its length, and never keys
head rotation x/y (GeckoLib's look control overwrites it); attacks start and end near the rest pose;
loops are seamless; the leviathan has a chain of 8+ bones.
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.abspath(os.path.join(HERE, "..", "..", "..", "src", "main", "resources", "assets", "celestialascent"))

SPEC = {
    "sentinel_construct": {"hitbox": (1.6, 3.2), "move": "walk",
                           "attacks": {"laser": 1.8, "stomp": 1.4, "charge": 1.3}},
    "ender_colossus": {"hitbox": (3.0, 6.0), "move": "walk",
                       "attacks": {"void_slam": 1.6, "ender_beam": 2.5, "rift_blink": 1.4, "shulker_barrage": 2.0,
                                   "gravity_well": 2.5}},
    "astral_seraph": {"hitbox": (2.0, 3.2), "move": "fly",
                      "attacks": {"light_lances": 2.0, "wing_gust": 1.5, "dive": 1.5, "radiant_nova": 2.5}},
    "nebula_leviathan": {"hitbox": (2.6, 2.0), "move": "fly", "chain": 8,
                         "attacks": {"void_bite": 1.3, "nebula_breath": 2.5, "coil": 3.0, "star_rain": 2.5}},
    "sun_herald": {"hitbox": (1.8, 4.0), "move": "walk",
                   "attacks": {"solar_flare": 2.0, "sunburst": 1.6, "corona_ring": 3.0, "eclipse": 3.0, "supernova": 4.0}},
    "void_sovereign": {"hitbox": (2.6, 5.4), "move": "walk",
                       "attacks": {"void_cleave": 1.4, "void_meteors": 2.5, "black_hole": 3.0, "abyssal_rend": 2.0,
                                   "wraith_call": 1.5, "collapse": 2.0, "unmaking": 3.0}},
}
REQUIRED_BONES = ("root", "body", "head")
CUBES = (40, 140)
NEAR_REST_DEG = 12.0      # attacks must start/end within this of the rest pose (rotation)
NEAR_REST_POS = 2.0       # ... and within this many units (position)


class Report:
    def __init__(self):
        self.errors, self.warnings, self.notes = [], [], []

    def err(self, m):
        self.errors.append(m)

    def warn(self, m):
        self.warnings.append(m)

    def note(self, m):
        self.notes.append(m)


def vec3_ok(v):
    return isinstance(v, list) and len(v) == 3 and all(isinstance(x, (int, float)) and math.isfinite(x) for x in v)


def kf_vectors(v):
    if isinstance(v, dict):
        out = [v[k] for k in ("pre", "post", "vector") if k in v]
        return out
    return [v]


def channel_keys(ch):
    """[(time, vec)] for a channel (static vector or keyframe dict)."""
    if isinstance(ch, list) or (isinstance(ch, dict) and any(k in ch for k in ("vector", "pre", "post"))):
        vs = kf_vectors(ch)
        return [(0.0, vs[-1])], vs
    keys = []
    allv = []
    for t, v in ch.items():
        vs = kf_vectors(v)
        allv += vs
        keys.append((float(t), vs[-1]))
    keys.sort(key=lambda kv: kv[0])
    return keys, allv


def sample(keys, t):
    if t <= keys[0][0]:
        return np.array(keys[0][1], dtype=float)
    if t >= keys[-1][0]:
        return np.array(keys[-1][1], dtype=float)
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            f = 0 if t1 == t0 else (t - t0) / (t1 - t0)
            return np.array(a, dtype=float) + (np.array(b, dtype=float) - np.array(a, dtype=float)) * f
    return np.array(keys[-1][1], dtype=float)


def check_png_sizes(name, paths, tw, th, R):
    try:
        tex = Image.open(paths["tex"])
        glow = Image.open(paths["glow"])
    except Exception as e:  # noqa: BLE001
        R.err(f"{name}: PNG load failed: {e}")
        return
    want = (tw * 2, th * 2)
    if tex.size != want:
        R.err(f"{name}: texture is {tex.size}, expected 2x declared {tw}x{th} = {want}")
    if glow.size != want:
        R.err(f"{name}: glowmask is {glow.size}, expected {want}")
    g = np.asarray(glow.convert("RGBA"))
    a = g[..., 3]
    lit = int((a > 0).sum())
    if lit == 0:
        R.err(f"{name}: glowmask has no emissive pixels")
    frac = lit / a.size
    if frac > 0.35:
        R.warn(f"{name}: glowmask covers {frac:.0%} of the atlas (should be mostly transparent)")
    t = np.asarray(tex.convert("RGBA"))
    if ((a > 0) & (t[..., 3] == 0)).any():
        R.warn(f"{name}: some glowmask pixels sit on transparent base texels")
    R.note(f"{name}: texture {tex.size[0]}x{tex.size[1]} (declared {tw}x{th}), glow {frac:.1%} of atlas")


def check_geo(name, spec, geo, R):
    if geo.get("format_version") != "1.12.0":
        R.err(f"{name}: geo format_version {geo.get('format_version')}")
    gs = geo.get("minecraft:geometry", [])
    if len(gs) != 1:
        R.err(f"{name}: expected one geometry, found {len(gs)}")
        return None
    g = gs[0]
    d = g.get("description", {})
    if d.get("identifier") != f"geometry.{name}":
        R.err(f"{name}: identifier {d.get('identifier')}")
    tw, th = d.get("texture_width"), d.get("texture_height")
    if not (isinstance(tw, int) and isinstance(th, int) and tw > 0 and th > 0):
        R.err(f"{name}: bad texture size {tw}x{th}")
        return None
    bones = g.get("bones", [])
    names = [b.get("name") for b in bones]
    if len(set(names)) != len(names):
        R.err(f"{name}: duplicate bone names")
    bmap = {b["name"]: b for b in bones}
    for r in REQUIRED_BONES:
        if r not in bmap:
            R.err(f"{name}: missing required bone '{r}'")
    root = bmap.get("root")
    if root is not None:
        if root.get("parent"):
            R.err(f"{name}: root has a parent")
        if [float(x) for x in root.get("pivot", [0, 0, 0])] != [0.0, 0.0, 0.0]:
            R.err(f"{name}: root pivot {root.get('pivot')}")
    depth = {}
    for b in bones:
        chain, cur, seen = 0, b, set()
        while cur.get("parent"):
            if cur["name"] in seen:
                R.err(f"{name}: parent cycle at {b['name']}")
                break
            seen.add(cur["name"])
            p = cur["parent"]
            if p not in bmap:
                R.err(f"{name}: bone {cur['name']} has unknown parent {p}")
                break
            cur = bmap[p]
            chain += 1
        if cur["name"] != "root":
            R.err(f"{name}: bone {b['name']} does not descend from root")
        depth[b["name"]] = chain
        if not vec3_ok([float(x) for x in b.get("pivot", [0, 0, 0])]):
            R.err(f"{name}: bone {b['name']} bad pivot")
    head = bmap.get("head")
    if head is not None and any(abs(float(x)) > 1e-6 for x in head.get("rotation", [0, 0, 0])[:2]):
        R.err(f"{name}: head has a rest rotation x/y (GeckoLib's look control overwrites it)")
    ncubes = 0
    for b in bones:
        for c in b.get("cubes", []):
            ncubes += 1
            size = c.get("size")
            if not vec3_ok(c.get("origin")) or not vec3_ok(size) or any(s < 0 for s in size):
                R.err(f"{name}: bad cube in {b['name']}")
                continue
            uv = c.get("uv")
            if isinstance(uv, list):
                w, h, dd = (math.floor(s + 1e-6) for s in size)
                u, v = uv
                if u < 0 or v < 0 or u + 2 * (dd + w) > tw or v + dd + h > th:
                    R.err(f"{name}: box UV of a cube in {b['name']} leaves the atlas")
            elif isinstance(uv, dict):
                for f, fd in uv.items():
                    (u, v), (w, h) = fd["uv"], fd["uv_size"]
                    us, vs = sorted((u, u + w)), sorted((v, v + h))
                    if us[0] < 0 or vs[0] < 0 or us[1] > tw or vs[1] > th:
                        R.err(f"{name}: face UV {f} of a cube in {b['name']} leaves the atlas")
            else:
                R.err(f"{name}: cube without uv in {b['name']}")
    if not CUBES[0] <= ncubes <= CUBES[1]:
        R.err(f"{name}: {ncubes} cubes (allowed {CUBES[0]}-{CUBES[1]})")
    if spec.get("chain"):
        longest = max(depth.values())
        # longest root-to-leaf path minus root itself
        if longest < spec["chain"]:
            R.err(f"{name}: longest bone chain {longest} < {spec['chain']}")
        R.note(f"{name}: longest parent chain {longest} bones below root")
    R.note(f"{name}: {len(bones)} bones, {ncubes} cubes")
    return {"tw": tw, "th": th, "bones": set(names)}


def check_anims(name, spec, anim, geo_info, R):
    if anim.get("format_version") != "1.8.0":
        R.err(f"{name}: animation format_version {anim.get('format_version')}")
    A = anim.get("animations", {})
    move = spec["move"]
    want = {"idle": (None, "loop"), move: (None, "loop"), "death": (2.8, "hold"), "phase": (2.0, "once")}
    for aid, L in spec["attacks"].items():
        want[f"attack.{aid}"] = (L, "once")
    for an, (L, mode) in want.items():
        if an not in A:
            R.err(f"{name}: missing animation '{an}'")
            continue
        a = A[an]
        loop = a.get("loop", False)
        length = float(a.get("animation_length", 0) or 0)
        if L is not None and abs(length - L) > 1e-3:
            R.err(f"{name}: {an} length {length} != {L}")
        if mode == "loop" and loop is not True:
            R.err(f"{name}: {an} must loop")
        if mode == "hold" and loop != "hold_on_last_frame":
            R.err(f"{name}: {an} must hold on the last frame (loop={loop})")
        if mode == "once" and loop not in (False, None):
            R.err(f"{name}: {an} must not loop (loop={loop})")
    if move == "fly" and "walk" in A:
        R.warn(f"{name}: flying boss also has a walk animation (unused)")
    idle0 = {}
    for bn, chans in A.get("idle", {}).get("bones", {}).items():
        for ch, data in chans.items():
            idle0[(bn, ch)] = sample(channel_keys(data)[0], 0.0)
    for an, a in A.items():
        length = float(a.get("animation_length", 0) or 0)
        bones = a.get("bones", {})
        if not bones:
            R.warn(f"{name}: {an} animates no bones")
        for bn, chans in bones.items():
            if bn not in geo_info["bones"]:
                R.err(f"{name}: {an} references missing bone '{bn}'")
                continue
            for ch, data in chans.items():
                if ch not in ("rotation", "position", "scale"):
                    R.warn(f"{name}: {an}/{bn} unknown channel {ch}")
                    continue
                keys, allv = channel_keys(data)
                for v in allv:
                    if not vec3_ok(v):
                        R.err(f"{name}: {an}/{bn}/{ch} has a non-numeric key {v}")
                        break
                for t, _ in keys:
                    if t < -1e-6 or t > length + 1e-6:
                        R.err(f"{name}: {an}/{bn}/{ch} key at {t} outside 0..{length}")
                        break
                if bn == "head" and ch == "rotation":
                    if any(abs(float(v[0])) > 1e-6 or abs(float(v[1])) > 1e-6 for v in allv if vec3_ok(v)):
                        R.err(f"{name}: {an} keys head rotation x/y (overwritten by GeckoLib look control)")
        # attacks/phase start and end near the idle pose (idle at t=0 is the reference)
        if an.startswith("attack.") or an == "phase":
            for t in (0.0, length):
                worst_r = worst_p = 0.0
                chans_all = set((bn, ch) for bn, chans in bones.items() for ch in chans) | set(idle0)
                for (bn, ch) in chans_all:
                    if ch == "scale":
                        continue
                    data = bones.get(bn, {}).get(ch)
                    v = sample(channel_keys(data)[0], t) if data is not None else np.zeros(3)
                    ref = idle0.get((bn, ch), np.zeros(3))
                    d = v - ref
                    if ch == "rotation":
                        worst_r = max(worst_r, float(np.abs((d + 180) % 360 - 180).max()))
                    else:
                        worst_p = max(worst_p, float(np.abs(d).max()))
                if worst_r > NEAR_REST_DEG or worst_p > NEAR_REST_POS:
                    R.warn(f"{name}: {an} at t={t:.2f} is {worst_r:.1f} deg / {worst_p:.1f} u away from the idle pose")
        # loops are seamless
        if a.get("loop") is True:
            worst = 0.0
            for bn, chans in bones.items():
                for ch, data in chans.items():
                    keys, _ = channel_keys(data)
                    d = sample(keys, 0.0) - sample(keys, length)
                    if ch == "rotation":
                        d = (d + 180) % 360 - 180
                    worst = max(worst, float(np.abs(d).max()))
            if worst > 1.0:
                R.warn(f"{name}: loop {an} differs by {worst:.2f} between first and last frame "
                       "(fine only if it is a whole symmetry step of a spinning part)")
    R.note(f"{name}: {len(A)} animations")


def check_boss(name, spec, R):
    paths = {
        "geo": os.path.join(ASSETS, "geo", "entity", f"{name}.geo.json"),
        "anim": os.path.join(ASSETS, "animations", "entity", f"{name}.animation.json"),
        "tex": os.path.join(ASSETS, "textures", "entity", f"{name}.png"),
        "glow": os.path.join(ASSETS, "textures", "entity", f"{name}_glowmask.png"),
    }
    missing = [k for k, p in paths.items() if not os.path.isfile(p)]
    for k in missing:
        R.err(f"{name}: missing {k} file {paths[k]}")
    if missing:
        return
    try:
        geo = json.load(open(paths["geo"], encoding="utf-8"))
        anim = json.load(open(paths["anim"], encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        R.err(f"{name}: JSON parse error: {e}")
        return
    info = check_geo(name, spec, geo, R)
    if info is None:
        return
    check_png_sizes(name, paths, info["tw"], info["th"], R)
    check_anims(name, spec, anim, info, R)


def main():
    R = Report()
    for name, spec in SPEC.items():
        check_boss(name, spec, R)
    for n in R.notes:
        print("  ", n)
    for w in R.warnings:
        print("WARN ", w)
    for e in R.errors:
        print("ERROR", e)
    nfiles = 4 * len(SPEC)
    print(f"\n{len(SPEC)} bosses, {nfiles} files checked: {len(R.errors)} errors, {len(R.warnings)} warnings")
    sys.exit(1 if R.errors else 0)


if __name__ == "__main__":
    main()
