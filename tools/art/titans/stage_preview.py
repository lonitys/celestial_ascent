"""Compare a titan's boss stages: bones named stage2_* are shown from stage 2 on, stage3_* only in
stage 3 (a hidden bone hides its children), exactly like the Java renderer.

python stage_preview.py NAME [--views front,3/4,back,side] [--scale 4] [--anim ANIM --time T]
                        [--grow 0.5] [--frame 120,92] [--center X,Y] [--stages 1,2,3] [--out PATH]

One column per stage, one row per view. --grow renders each stage's own new bones at that scale
(the renderer scales them 0 -> 1 when they appear) to check that the pivots sit at the attachment.
"""
import argparse
import os

import numpy as np
from PIL import Image, ImageDraw

import geo_preview as gp
import titanlib as tl

VIEWS = {"front": (0, -6), "3/4": (35, -12), "side": (90, -6), "back": (180, -10), "3/4b": (145, -12),
         "3/4l": (-35, -12), "top": (20, -55)}
PREFIXES = (("stage2_", 2), ("stage3_", 3))


def bone_stage(bmap, name):
    """Stage from which a bone is visible (max over itself and its ancestors)."""
    st = 1
    cur = bmap.get(name)
    while cur is not None:
        for pre, s in PREFIXES:
            if cur["name"].startswith(pre):
                st = max(st, s)
        cur = bmap.get(cur.get("parent"))
    return st


def stage_geo(geo, stage):
    bmap = {b["name"]: b for b in geo["bones"]}
    g = dict(geo)
    g["bones"] = [b for b in geo["bones"] if bone_stage(bmap, b["name"]) <= stage]
    return g


def grow_pose(geo, stage, factor, pose=None):
    pose = {k: dict(v) for k, v in (pose or {}).items()}
    for b in geo["bones"]:
        for pre, s in PREFIXES:
            if s == stage and b["name"].startswith(pre):
                p = pose.setdefault(b["name"], {})
                p["scale"] = np.array([factor] * 3) * (p.get("scale") if p.get("scale") is not None else 1.0)
    return pose


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--views", default="front,3/4,back")
    ap.add_argument("--scale", type=float, default=4.0)
    ap.add_argument("--frame", default="120,92")
    ap.add_argument("--anim")
    ap.add_argument("--time", type=float, default=0.0)
    ap.add_argument("--grow", type=float, default=None)
    ap.add_argument("--stages", default="1,2,3")
    ap.add_argument("--center", default=None, help="view-space centre x,y (default 0,frame_h/2-10)")
    ap.add_argument("--out")
    a = ap.parse_args()
    p = tl.asset_paths(a.name)
    geo = gp.load_geo(p["geo"])
    tex = gp.load_rgba(p["tex"])
    glow = gp.load_rgba(p["glow"])
    pose = gp.sample_anim(gp.load_anims(p["anim"])[a.anim], a.time) if a.anim else None
    fw, fh = (float(x) for x in a.frame.split(","))
    W, H = int(fw * a.scale), int(fh * a.scale)
    stages = [int(s) for s in a.stages.split(",")]
    center = tuple(float(x) for x in a.center.split(",")) if a.center else (0, fh / 2 - 10)
    views = a.views.split(",")
    top = 18
    sheet = Image.new("RGB", (W * len(stages), H * len(views) + top), (20, 20, 24))
    d = ImageDraw.Draw(sheet)
    title = f"{a.name} stages" + (f"  {a.anim}@{a.time}" if a.anim else "") + (f"  grow {a.grow}" if a.grow else "")
    d.text((6, 3), title, fill=(255, 255, 255))
    for c, st in enumerate(stages):
        g = stage_geo(geo, st)
        ps = grow_pose(g, st, a.grow, pose) if a.grow is not None else pose
        n_cubes = sum(len(b.get("cubes", [])) for b in g["bones"])
        for r, v in enumerate(views):
            yaw, pitch = VIEWS[v]
            im = gp.render(g, tex, glow, ps, yaw=yaw, pitch=pitch, scale=a.scale, size=(W, H),
                           center=center)
            ImageDraw.Draw(im).text((6, 4), f"stage {st} ({v})  {n_cubes} cubes", fill=(230, 230, 240))
            sheet.paste(im, (c * W, top + r * H))
    out = a.out or os.path.join(tl.PREVIEW, f"{a.name}_stages{'_' + a.anim.replace('.', '_') if a.anim else ''}"
                                             f"{'_grow' if a.grow is not None else ''}.png")
    sheet.save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main()
