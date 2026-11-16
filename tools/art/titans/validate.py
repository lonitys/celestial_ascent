"""Validate the titan assets against the contract the Java side depends on.

python validate.py        -> prints a report, exit code 1 on any error
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image

import geo_preview as gp

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.abspath(os.path.join(HERE, "..", "..", "..", "src", "main", "resources", "assets", "celestialascent"))

COMMON_ANIMS = {"idle": 3.0, "walk": 1.6, "death": 2.8, "phase": 2.0}
TITANS = {
    "frost_titan": {
        "hitbox": (2.0, 4.0), "legs": True,
        "anims": {"attack.slam": 1.5, "attack.ice_spikes": 1.5, "attack.frost_breath": 2.5, "attack.blizzard": 3.0},
    },
    "tide_titan": {
        "hitbox": (2.0, 4.2), "legs": True,
        "anims": {"attack.trident_throw": 1.5, "attack.tidal_wave": 2.0, "attack.whirlpool": 3.0, "attack.water_jet": 2.0},
    },
    "storm_titan": {
        "hitbox": (2.2, 4.5), "legs": False,
        "anims": {"attack.lightning_call": 2.0, "attack.wind_gust": 1.5, "attack.thunder_clap": 1.5, "attack.storm_dash": 1.2},
    },
    "magma_titan": {
        "hitbox": (2.4, 4.6), "legs": True,
        "anims": {"attack.meteor": 2.5, "attack.eruption": 1.8, "attack.flame_breath": 2.5, "attack.lava_pool": 1.5},
    },
}
LOOPING = {"idle", "walk"}


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []

    def err(self, m):
        self.errors.append(m)

    def warn(self, m):
        self.warnings.append(m)

    def note(self, m):
        self.info.append(m)


def is_vec3(v):
    return isinstance(v, list) and len(v) == 3 and all(isinstance(x, (int, float)) and math.isfinite(x) for x in v)


def check_titan(name, spec, R):
    paths = {
        "geo": os.path.join(ASSETS, "geo", "entity", f"{name}.geo.json"),
        "anim": os.path.join(ASSETS, "animations", "entity", f"{name}.animation.json"),
        "tex": os.path.join(ASSETS, "textures", "entity", f"{name}.png"),
        "glow": os.path.join(ASSETS, "textures", "entity", f"{name}_glowmask.png"),
    }
    for k, p in paths.items():
        if not os.path.isfile(p):
            R.err(f"{name}: missing {k} file {p}")
            return
    try:
        with open(paths["geo"], encoding="utf-8") as f:
            geo = json.load(f)
        with open(paths["anim"], encoding="utf-8") as f:
            anim = json.load(f)
    except Exception as e:  # noqa
        R.err(f"{name}: JSON parse error {e}")
        return

    # ---------------------------------------------------------------- geometry
    if geo.get("format_version") != "1.12.0":
        R.err(f"{name}: geo format_version {geo.get('format_version')}")
    geos = geo.get("minecraft:geometry", [])
    if len(geos) != 1:
        R.err(f"{name}: expected exactly one geometry, got {len(geos)}")
        return
    g = geos[0]
    desc = g["description"]
    if desc.get("identifier") != f"geometry.{name}":
        R.err(f"{name}: identifier {desc.get('identifier')}")
    tw, th = desc.get("texture_width"), desc.get("texture_height")
    bones = g.get("bones", [])
    names = [b["name"] for b in bones]
    if len(set(names)) != len(names):
        R.err(f"{name}: duplicate bone names")
    bmap = {b["name"]: b for b in bones}
    required = {"root", "body", "head", "right_arm", "left_arm"}
    required |= {"right_leg", "left_leg"} if spec["legs"] else {"vortex"}
    for r in sorted(required - set(names)):
        R.err(f"{name}: missing required bone '{r}'")
    root = bmap.get("root")
    if root:
        if root.get("parent"):
            R.err(f"{name}: root has a parent")
        if root.get("pivot", [0, 0, 0]) != [0, 0, 0]:
            R.err(f"{name}: root pivot is {root.get('pivot')}")
    for b in bones:
        if b["name"] == "root":
            continue
        seen = set()
        cur = b
        while cur.get("parent"):
            if cur["name"] in seen:
                R.err(f"{name}: parent cycle at {b['name']}")
                break
            seen.add(cur["name"])
            par = cur["parent"]
            if par not in bmap:
                R.err(f"{name}: bone {cur['name']} has unknown parent {par}")
                break
            cur = bmap[par]
        if cur["name"] != "root":
            R.err(f"{name}: bone {b['name']} does not descend from root")
    def in_stage(bone):
        """True for evolution parts: the bone or one of its parents is named stage2_* / stage3_*."""
        cur, guard = bone, 0
        while cur is not None and guard < 64:
            if cur["name"].startswith(("stage2_", "stage3_")):
                return True
            cur = bmap.get(cur.get("parent"))
            guard += 1
        return False

    ncubes = 0
    nstage = 0
    occupancy = np.zeros((th, tw), dtype=np.int16)
    for b in bones:
        staged = in_stage(b)
        for c in b.get("cubes", []):
            if staged:
                nstage += 1
            else:
                ncubes += 1
            if not (is_vec3(c.get("origin")) and is_vec3(c.get("size"))):
                R.err(f"{name}: bad cube in {b['name']}")
                continue
            if any(abs(s - round(s)) > 1e-6 for s in c["size"]):
                R.warn(f"{name}: non-integer cube size {c['size']} in {b['name']} (box UV floors it)")
            uv = c.get("uv")
            if isinstance(uv, list):
                rects = gp.box_uv_rects(uv, c["size"])
                for face, (u, v, w, h) in rects.items():
                    if u < 0 or v < 0 or u + w > tw or v + h > th:
                        R.err(f"{name}: UV of cube in {b['name']} ({face}) outside texture")
                    else:
                        occupancy[int(v):int(v + h), int(u):int(u + w)] += 1
    over = int((occupancy > 1).sum())
    if over:
        R.warn(f"{name}: {over} texture pixels shared by more than one face")
    if not (40 <= ncubes <= 120):
        R.err(f"{name}: {ncubes} base cubes (want 40-120)")
    if nstage > 70:
        R.err(f"{name}: {nstage} stage cubes (want at most 70)")
    head = bmap.get("head")
    if head and head.get("rotation") and any(head["rotation"]):
        R.warn(f"{name}: head bone has a rest rotation {head['rotation']} (look-at code may overwrite it)")

    # textures
    tex = Image.open(paths["tex"])
    glow = Image.open(paths["glow"])
    if tex.size != (tw * 2, th * 2):
        R.err(f"{name}: texture is {tex.size}, expected {(tw * 2, th * 2)} (2x of {tw}x{th})")
    if glow.size != tex.size:
        R.err(f"{name}: glowmask is {glow.size}, texture {tex.size}")
    ta = np.array(tex.convert("RGBA"))
    ga = np.array(glow.convert("RGBA"))
    if ga.shape == ta.shape:
        gl = ga[..., 3] > 0
        if (gl & (ta[..., 3] == 0)).any():
            R.err(f"{name}: glowmask has pixels where the texture is transparent")
        R.note(f"{name}: glow pixels {int(gl.sum())} ({100.0 * gl.sum() / gl.size:.1f}% of atlas)")
    # extents vs hitbox
    gg = gp.load_geo(geo)
    lo, hi = gp.model_extent(gg)
    hbw, hbh = spec["hitbox"]
    width = max(-lo[0], hi[0]) * 2
    R.note(f"{name}: {ncubes} cubes, {len(bones)} bones, texture {tw}x{th} (png {tex.size[0]}x{tex.size[1]}); "
           f"model x {lo[0]:.1f}..{hi[0]:.1f} (width {width:.1f} vs hitbox {hbw * 16:.0f}), "
           f"y {lo[1]:.1f}..{hi[1]:.1f} (hitbox {hbh * 16:.0f}), z {lo[2]:.1f}..{hi[2]:.1f}")
    if lo[1] < -0.5:
        R.warn(f"{name}: model extends below the feet (y min {lo[1]:.1f})")

    # ---------------------------------------------------------------- animations
    if anim.get("format_version") != "1.8.0":
        R.err(f"{name}: animation format_version {anim.get('format_version')}")
    anims = anim.get("animations", {})
    want = dict(COMMON_ANIMS)
    want.update(spec["anims"])
    for an, length in want.items():
        if an not in anims:
            R.err(f"{name}: missing animation '{an}'")
            continue
        a = anims[an]
        L = a.get("animation_length")
        if L is None or abs(L - length) > 0.051:
            R.err(f"{name}: {an} length {L}, expected ~{length}")
        loop = a.get("loop", False)
        if an in LOOPING and loop is not True:
            R.err(f"{name}: {an} should loop")
        if an.startswith("attack.") or an == "phase":
            if loop is True:
                R.err(f"{name}: {an} must not loop")
        if an == "death" and loop not in ("hold_on_last_frame", False):
            R.err(f"{name}: death loop is {loop}")
    for an, a in anims.items():
        L = a.get("animation_length", 0)
        for bn, bd in a.get("bones", {}).items():
            if bn not in bmap:
                R.err(f"{name}: {an} animates unknown bone '{bn}'")
            for chan, ch in bd.items():
                if chan not in ("rotation", "position", "scale"):
                    R.err(f"{name}: {an}/{bn} unknown channel {chan}")
                    continue
                if isinstance(ch, list):
                    if not is_vec3(ch):
                        R.err(f"{name}: {an}/{bn}/{chan} bad constant value")
                    continue
                for tk, v in ch.items():
                    try:
                        tt = float(tk)
                    except ValueError:
                        R.err(f"{name}: {an}/{bn}/{chan} bad time key {tk}")
                        continue
                    if tt < -1e-6 or tt > L + 1e-6:
                        R.err(f"{name}: {an}/{bn}/{chan} key {tk} outside 0..{L}")
                    if not is_vec3(v):
                        R.err(f"{name}: {an}/{bn}/{chan}@{tk} is not 3 numbers: {v}")
        # attacks/phase start and end near the idle (rest) pose
        if an.startswith("attack.") or an == "phase":
            worst = 0.0
            where = ""
            for bn, bd in a.get("bones", {}).items():
                for chan, ch in bd.items():
                    if not isinstance(ch, dict):
                        continue
                    ks = sorted(ch.items(), key=lambda kv: float(kv[0]))
                    for (tk, v) in (ks[0], ks[-1]):
                        base = 1.0 if chan == "scale" else 0.0
                        dev = [abs(x - base) for x in v]
                        if chan == "rotation" and bn.startswith("vortex_ring"):
                            dev = [min(d % 360, 360 - d % 360) for d in dev]
                        lim = 4.0 if chan == "rotation" else (0.6 if chan == "position" else 0.05)
                        d = max(dev) / lim
                        if d > worst:
                            worst, where = d, f"{bn}/{chan}@{tk}={v}"
            if worst > 1.0:
                R.err(f"{name}: {an} does not start/end near rest pose ({where})")
    R.note(f"{name}: animations {sorted(anims)}")


def main():
    R = Report()
    for name, spec in TITANS.items():
        check_titan(name, spec, R)
    for m in R.info:
        print("  info:", m)
    for m in R.warnings:
        print("  WARN:", m)
    for m in R.errors:
        print("  ERROR:", m)
    print(f"{len(R.errors)} errors, {len(R.warnings)} warnings")
    sys.exit(1 if R.errors else 0)


if __name__ == "__main__":
    main()
