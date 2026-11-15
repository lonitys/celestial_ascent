"""Validate the 3D armor assets against the GeckoLib GeoArmorRenderer contract.

python validate.py      -> report; exit code 1 on any error

Checks per set: every file exists; PNG = 2x the declared texture size; glowmask same size as its
texture, fully opaque-or-transparent texels (GeckoLib cuts glow texels out of the base texture);
the 8 armor bones exist at top level with exact pivots and no rest rotation; every cube-carrying bone
descends from an armor bone; limb cubes sit in their limb's region; decorations stay within the
allowed distance of the body; box-UV footprints are inside the texture and do not overlap; the
"idle" animation exists, loops, lasts 2-4 s and only animates existing, non-main bones.
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

MAIN = {
    "armorHead": [0, 24, 0], "armorBody": [0, 24, 0],
    "armorRightArm": [-5, 22, 0], "armorLeftArm": [5, 22, 0],
    "armorRightLeg": [-1.9, 12, 0], "armorLeftLeg": [1.9, 12, 0],
    "armorRightBoot": [-1.9, 12, 0], "armorLeftBoot": [1.9, 12, 0],
}
# vanilla body part boxes the armor bones wrap (world space, rest pose)
BODY = {
    "armorHead": ((-4, 24, -4), (4, 32, 4)), "armorBody": ((-4, 12, -2), (4, 24, 2)),
    "armorRightArm": ((-8, 12, -2), (-4, 24, 2)), "armorLeftArm": ((4, 12, -2), (8, 24, 2)),
    "armorRightLeg": ((-3.9, 0, -2), (0.1, 12, 2)), "armorLeftLeg": ((-0.1, 0, -2), (3.9, 12, 2)),
    "armorRightBoot": ((-3.9, 0, -2), (0.1, 12, 2)), "armorLeftBoot": ((-0.1, 0, -2), (3.9, 12, 2)),
}
PLAYER = (np.array([-8.0, 0.0, -4.0]), np.array([8.0, 32.0, 4.0]))   # vanilla player model AABB
MARGIN = 7.5            # "about 6 px" from the body, measured from the 1 px-inflated armor shell
WING_MARGIN_X = 15.0    # ascendant wings: up to ~14 px out from the torso sides

SETS = {
    "titan": ["", "_frost", "_tide", "_storm", "_magma"],
    "imperial": [""],
    "stellar": [""],
    "void": [""],
    "ascendant": [""],
}


class Report:
    def __init__(self):
        self.errors, self.warnings, self.info = [], [], []

    def err(self, m):
        self.errors.append(m)

    def warn(self, m):
        self.warnings.append(m)

    def note(self, m):
        self.info.append(m)


def finite_vec(v, n=3):
    return isinstance(v, list) and len(v) == n and all(isinstance(x, (int, float)) and math.isfinite(x) for x in v)


def check_set(key, variants, R):
    name = f"{key}_armor"
    geo_p = os.path.join(ASSETS, "geo", "item", "armor", f"{name}.geo.json")
    anim_p = os.path.join(ASSETS, "animations", "item", "armor", f"{name}.animation.json")
    tex_ps = [(v, os.path.join(ASSETS, "textures", "item", "armor", f"{name}{v}.png"),
               os.path.join(ASSETS, "textures", "item", "armor", f"{name}{v}_glowmask.png")) for v in variants]
    missing = [p for p in [geo_p, anim_p] + [x for _, a, b in tex_ps for x in (a, b)] if not os.path.isfile(p)]
    for p in missing:
        R.err(f"{key}: missing file {os.path.relpath(p, ASSETS)}")
    if not os.path.isfile(geo_p) or not os.path.isfile(anim_p):
        return
    try:
        with open(geo_p, encoding="utf-8") as f:
            gj = json.load(f)
        with open(anim_p, encoding="utf-8") as f:
            aj = json.load(f)
    except Exception as e:  # noqa
        R.err(f"{key}: JSON parse error: {e}")
        return

    # ------------------------------------------------------------------ geometry
    try:
        g0 = gj["minecraft:geometry"][0]
        desc = g0["description"]
        tw, th = int(desc["texture_width"]), int(desc["texture_height"])
        bones = g0["bones"]
    except Exception as e:  # noqa
        R.err(f"{key}: malformed geometry: {e}")
        return
    byname = {}
    for b in bones:
        if b["name"] in byname:
            R.err(f"{key}: duplicate bone {b['name']}")
        byname[b["name"]] = b
    for mb, piv in MAIN.items():
        b = byname.get(mb)
        if b is None:
            R.err(f"{key}: required bone {mb} missing")
            continue
        if [float(x) for x in b.get("pivot", [0, 0, 0])] != [float(x) for x in piv]:
            R.err(f"{key}: {mb} pivot {b.get('pivot')} != {piv}")
        if b.get("rotation") and any(abs(x) > 1e-9 for x in b["rotation"]):
            R.err(f"{key}: {mb} has a rest rotation (GeckoLib overwrites it with the limb rotation)")
        par = b.get("parent")
        if par is not None:
            pb = byname.get(par)
            ok = pb is not None and pb.get("parent") is None and not pb.get("cubes") and \
                not any(abs(x) > 1e-9 for x in pb.get("pivot", [0, 0, 0])) and not any(pb.get("rotation", [0, 0, 0]))
            if not ok:
                R.err(f"{key}: {mb} must be top level or under a neutral root (parent={par})")

    def main_of(bn, depth=0):
        if bn in MAIN:
            return bn
        b = byname.get(bn)
        if b is None or depth > 64:
            return None
        p = b.get("parent")
        return main_of(p, depth + 1) if p else None

    for b in bones:
        p = b.get("parent")
        if p is not None and p not in byname:
            R.err(f"{key}: bone {b['name']} has unknown parent {p}")
        if not finite_vec(b.get("pivot", [0, 0, 0])):
            R.err(f"{key}: bone {b['name']} bad pivot")
        if b.get("cubes") and main_of(b["name"]) is None:
            R.err(f"{key}: bone {b['name']} has cubes but is not under an armor bone (would render for every piece)")

    geo = gp.load_geo(gj)
    mats = gp.bone_matrices(geo)
    occ = np.zeros((th * 2, tw * 2), dtype=np.int32)
    ncubes = 0
    reach = [np.full(3, -99.0)]
    for b in bones:
        mb = main_of(b["name"])
        for ci, c in enumerate(b.get("cubes", [])):
            ncubes += 1
            tag = f"{key}:{b['name']}#{ci}"
            if not finite_vec(c.get("origin")) or not finite_vec(c.get("size")):
                R.err(f"{tag}: bad origin/size")
                continue
            if any(s < 0 for s in c["size"]):
                R.err(f"{tag}: negative size")
            uv = c.get("uv")
            if not (isinstance(uv, list) and len(uv) == 2):
                R.err(f"{tag}: expected box uv [u, v]")
                continue
            w, h, d = (math.floor(s + 1e-6) for s in c["size"])
            u0, v0 = uv
            fw, fh = 2 * (d + w), d + h
            if u0 < 0 or v0 < 0 or u0 + fw > tw or v0 + fh > th:
                R.err(f"{tag}: uv footprint {u0},{v0} {fw}x{fh} outside {tw}x{th}")
            else:
                for face, (fu, fv, fww, fhh) in gp.box_uv_rects(uv, c["size"]).items():
                    if fww <= 0 or fhh <= 0:
                        continue
                    occ[int(fv * 2):int((fv + fhh) * 2), int(fu * 2):int((fu + fww) * 2)] += 1
            # world-space AABB at rest
            o = np.array(c["origin"], dtype=float)
            s = np.array(c["size"], dtype=float)
            inf = float(c.get("inflate", 0.0))
            lo, hi = o - inf, o + s + inf
            corners = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
            cm = gp.cube_matrix(mats[b["name"]], c)
            wc = (cm @ np.c_[corners, np.ones(8)].T).T[:, :3]
            wlo, whi = wc.min(0), wc.max(0)
            if mb is None:
                continue
            blo, bhi = (np.array(x, dtype=float) for x in BODY[mb])
            ctr = (wlo + whi) / 2
            # limb membership: the cube must sit on its limb's side / height band
            if mb in ("armorRightArm", "armorRightLeg", "armorRightBoot") and ctr[0] > 0.6:
                R.err(f"{tag}: cube centre x={ctr[0]:.2f} not on the right (-X) side of {mb}")
            if mb in ("armorLeftArm", "armorLeftLeg", "armorLeftBoot") and ctr[0] < -0.6:
                R.err(f"{tag}: cube centre x={ctr[0]:.2f} not on the left (+X) side of {mb}")
            if mb in ("armorRightLeg", "armorLeftLeg", "armorRightBoot", "armorLeftBoot") and ctr[1] > 13.5:
                R.err(f"{tag}: leg/boot cube centre y={ctr[1]:.2f} above the hip")
            if mb in ("armorRightBoot", "armorLeftBoot") and ctr[1] > 8.5:
                R.err(f"{tag}: boot cube centre y={ctr[1]:.2f} too high")
            if mb == "armorHead" and ctr[1] < 21.5:
                R.err(f"{tag}: head cube centre y={ctr[1]:.2f} below the neck")
            if mb in ("armorRightArm", "armorLeftArm") and abs(ctr[0]) < 3.5:
                R.err(f"{tag}: arm cube centre x={ctr[0]:.2f} inside the torso")
            # decoration reach, measured from the whole player body box (what clips walls / the camera)
            is_wing = b["name"].lower().startswith("wing")
            mx = np.maximum(PLAYER[0] - wlo, whi - PLAYER[1])
            lim = np.array([MARGIN, MARGIN, MARGIN])
            if is_wing:
                # wings: up to ~14 px out from the torso sides (x = +-4), may sweep back a little further
                mx[0] = max(abs(wlo[0]), abs(whi[0])) - 4.0
                lim = np.array([WING_MARGIN_X, MARGIN, MARGIN + 2.0])
            if np.any(mx > lim + 1e-6):
                R.warn(f"{tag}: reaches {np.round(mx, 2).tolist()} px beyond the body (limit {lim.tolist()})")
            reach[0] = np.maximum(reach[0], mx if not is_wing else reach[0])
    over = int((occ > 1).sum())
    if over:
        R.err(f"{key}: {over} texels claimed by more than one cube face (UV overlap)")

    # ------------------------------------------------------------------ textures
    for v, tp, gpth in tex_ps:
        if not (os.path.isfile(tp) and os.path.isfile(gpth)):
            continue
        ti = Image.open(tp)
        gi = Image.open(gpth)
        if ti.size != (tw * 2, th * 2):
            R.err(f"{key}{v}: texture {ti.size} != 2x declared {tw}x{th}")
        if gi.size != ti.size:
            R.err(f"{key}{v}: glowmask {gi.size} != texture {ti.size}")
        ga = np.array(gi.convert("RGBA"))[..., 3]
        partial = int(((ga > 0) & (ga < 255)).sum())
        if partial:
            R.err(f"{key}{v}: glowmask has {partial} semi-transparent texels")
        lit = int((ga == 255).sum())
        if lit == 0:
            R.err(f"{key}{v}: glowmask is empty")
        ta = np.array(ti.convert("RGBA"))[..., 3]
        used = occ > 0
        coverage = float((ta[used] > 0).mean()) if used.any() else 0.0
        R.note(f"{key}{v}: {ti.size[0]}x{ti.size[1]} png, {lit} glow texels, {coverage * 100:.1f}% of face texels opaque")

    # ------------------------------------------------------------------ animation
    anims = aj.get("animations", {})
    idle = anims.get("idle")
    if idle is None:
        R.err(f"{key}: no 'idle' animation")
    else:
        if idle.get("loop") is not True:
            R.err(f"{key}: idle must loop (loop=true)")
        L = float(idle.get("animation_length", 0))
        if not (2.0 <= L <= 4.0):
            R.err(f"{key}: idle length {L} not within 2-4 s")
        for bn, bd in idle.get("bones", {}).items():
            if bn in MAIN:
                R.err(f"{key}: idle animates main armor bone {bn}")
            if bn not in byname:
                R.err(f"{key}: idle references unknown bone {bn}")
            for chan, ch in bd.items():
                if chan not in ("rotation", "position", "scale"):
                    R.err(f"{key}: idle {bn} unknown channel {chan}")
                    continue
                frames = ch.values() if isinstance(ch, dict) else [ch]
                for fr in frames:
                    vec = fr if isinstance(fr, list) else (fr.get("post") or fr.get("vector") if isinstance(fr, dict) else None)
                    if not finite_vec(vec):
                        R.err(f"{key}: idle {bn}.{chan} bad keyframe {fr}")
                if isinstance(ch, dict):
                    for tk in ch:
                        tf = float(tk)
                        if tf < -1e-6 or tf > L + 1e-6:
                            R.err(f"{key}: idle {bn}.{chan} key time {tk} outside 0..{L}")
        R.note(f"{key}: {ncubes} cubes, {len(bones)} bones, idle {L}s animates {sorted(idle.get('bones', {}))}")
    R.note(f"{key}: max non-wing reach beyond the body box (x, y, z) = {np.round(reach[0], 2).tolist()} px")


def main():
    R = Report()
    for key, variants in SETS.items():
        check_set(key, variants, R)
    for m in R.info:
        print("  info  ", m)
    for m in R.warnings:
        print("  WARN  ", m)
    for m in R.errors:
        print("  ERROR ", m)
    print(f"\n{len(R.errors)} error(s), {len(R.warnings)} warning(s)")
    sys.exit(1 if R.errors else 0)


if __name__ == "__main__":
    main()
