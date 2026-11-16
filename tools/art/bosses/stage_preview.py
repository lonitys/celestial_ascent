"""Stage comparison sheet: renders a boss with its evolution bones hidden/shown the way BossRenderer
does it (a bone whose name starts with stage2_ shows from stage 2 on, stage3_ only in stage 3; hiding
a bone hides its children).

  python stage_preview.py BOSS [--anim idle --time 0.0] [--views front,3/4,back] [--before DIR]
                               [--out PATH] [--px 360] [--no-bloom]

Columns: stage 1 (all stage bones hidden), stage 2 (stage3_ hidden), stage 3 (everything).
--before DIR adds a first column rendered from an older copy of the asset files (DIR/<boss>.geo.json,
.png, _glowmask.png) and prints how far the new stage-1 render differs from it (should be 0).
All stage columns use the base texture (the per-stage textures are derived later by gen_stages.py).
"""
import argparse
import copy
import os

import numpy as np
from PIL import Image, ImageDraw

import bosslib as tl
import geo_preview as gp

VIEWS = {"front": (0, -6), "3/4": (35, -12), "side": (90, -6), "back": (180, -8), "3/4 back": (145, -12),
         "low 3/4": (-30, 14), "top": (20, -55)}
STAGE_HIDE = {1: ("stage2_", "stage3_"), 2: ("stage3_",), 3: ()}


def hidden_names(geo, prefixes):
    bones = {b["name"]: b for b in geo["bones"]}
    out = set()
    for n in bones:
        cur = n
        while cur:
            if any(cur.startswith(p) for p in prefixes):
                out.add(n)
                break
            cur = bones[cur].get("parent")
    return out


def stage_geo(geo, stage):
    g = copy.deepcopy(geo)
    hide = hidden_names(g, STAGE_HIDE[stage])
    g["bones"] = [b for b in g["bones"] if b["name"] not in hide]
    return g


def stage_bones(geo):
    return [b["name"] for b in geo["bones"] if b["name"].startswith(("stage2_", "stage3_"))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("boss")
    ap.add_argument("--anim", default=None)
    ap.add_argument("--time", type=float, default=0.0)
    ap.add_argument("--views", default="front,3/4,back")
    ap.add_argument("--before", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--px", type=int, default=360, help="tile height in pixels")
    ap.add_argument("--no-bloom", action="store_true", help="skip the preview bloom (closer to the in-game look)")
    a = ap.parse_args()

    p = tl.asset_paths(a.boss)
    geo = gp.load_geo(p["geo"])
    tex, glow = gp.load_rgba(p["tex"]), gp.load_rgba(p["glow"])
    pose = None
    if a.anim:
        pose = gp.sample_anim(gp.load_anims(p["anim"])[a.anim], a.time)
    cols = [(f"stage {s}", stage_geo(geo, s), tex, glow, pose) for s in (1, 2, 3)]
    if a.before:
        bg = gp.load_geo(os.path.join(a.before, f"{a.boss}.geo.json"))
        bt = gp.load_rgba(os.path.join(a.before, f"{a.boss}.png"))
        bw = gp.load_rgba(os.path.join(a.before, f"{a.boss}_glowmask.png"))
        bpose = None
        if a.anim:
            ba = os.path.join(a.before, f"{a.boss}.animation.json")
            bpose = gp.sample_anim(gp.load_anims(ba if os.path.isfile(ba) else p["anim"])[a.anim], a.time)
        cols.insert(0, ("before", bg, bt, bw, bpose))
    print("stage bones:", ", ".join(stage_bones(geo)) or "(none)")

    views = [v.strip() for v in a.views.split(",")]
    # frame on the full stage-3 model: widest projection over the requested views, centred on x = 0
    faces = gp.collect_faces(geo, pose)
    pts = np.concatenate([f[2] for f in faces] + [np.array([[-8, 0, -8], [8, 0, 8]], dtype=float)])
    lo, hi = pts.min(axis=0), pts.max(axis=0)
    half = max(float(np.abs((pts @ gp.view_matrix(*VIEWS[vn]).T)[:, 0]).max()) for vn in views)
    fh = (hi[1] - lo[1]) + 14
    fw = 2 * half + 10
    scale = a.px / fh
    W, H = int(fw * scale), int(fh * scale)
    cy = (hi[1] + lo[1]) / 2
    sheet = Image.new("RGB", (W * len(cols), H * len(views) + 18), (20, 20, 24))
    d = ImageDraw.Draw(sheet)
    title = f"{a.boss}" + (f"  {a.anim} @ {a.time:.2f}s" if a.anim else "  rest")
    d.text((6, 3), title, fill=(255, 255, 255))
    renders = {}
    for r, vn in enumerate(views):
        yaw, pitch = VIEWS[vn]
        for c, (label, g, t, gl, ps) in enumerate(cols):
            im = gp.render(g, t, gl, ps, yaw=yaw, pitch=pitch, scale=scale, size=(W, H), center=(0, cy),
                           bloom=not a.no_bloom)
            renders[(label, vn)] = np.asarray(im, dtype=int)
            ImageDraw.Draw(im).text((6, 4), f"{label}  {vn}", fill=(230, 230, 240))
            sheet.paste(im, (c * W, r * H + 18))
    if a.before:
        for vn in views:
            diff = np.abs(renders[("before", vn)] - renders[("stage 1", vn)])
            print(f"before vs stage 1 ({vn}): max diff {int(diff.max())}, differing px {int((diff.max(axis=2) > 0).sum())}")
    out = a.out or os.path.join(tl.PREVIEW, f"{a.boss}_stages" + (f"_{a.anim.replace('.', '_')}" if a.anim else "") + ".png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sheet.save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main()
