"""Render large single views of a built titan for close inspection.

python inspect_view.py NAME [--anim ANIM --time T] [--views front,3/4] [--scale 7] [--out PATH]
           [--crop x0,y0,x1,y1 (model units: left,bottom,right,top in the view)]
"""
import argparse
import os

from PIL import Image, ImageDraw

import geo_preview as gp
import titanlib as tl

VIEWS = {"front": (0, -8), "3/4": (35, -14), "side": (90, -6), "back": (180, -10), "3/4l": (-35, -14),
         "3/4b": (145, -14), "low": (25, 10)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--anim")
    ap.add_argument("--time", type=float, default=0.0)
    ap.add_argument("--views", default="front,3/4")
    ap.add_argument("--scale", type=float, default=7)
    ap.add_argument("--frame", default="90,90")
    ap.add_argument("--center", default=None)
    ap.add_argument("--out")
    a = ap.parse_args()
    p = tl.asset_paths(a.name)
    geo = gp.load_geo(p["geo"])
    tex = gp.load_rgba(p["tex"])
    glow = gp.load_rgba(p["glow"])
    pose = None
    if a.anim:
        pose = gp.sample_anim(gp.load_anims(p["anim"])[a.anim], a.time)
    fw, fh = (float(x) for x in a.frame.split(","))
    W, H = int(fw * a.scale), int(fh * a.scale)
    center = tuple(float(x) for x in a.center.split(",")) if a.center else (0, fh / 2 - 8)
    tiles = []
    for v in a.views.split(","):
        yaw, pitch = VIEWS[v]
        im = gp.render(geo, tex, glow, pose, yaw=yaw, pitch=pitch, scale=a.scale, size=(W, H), center=center)
        ImageDraw.Draw(im).text((6, 4), f"{v} {a.anim or ''} {a.time if a.anim else ''}", fill=(230, 230, 240))
        tiles.append(im)
    sheet = Image.new("RGB", (W * len(tiles), H))
    for i, t in enumerate(tiles):
        sheet.paste(t, (i * W, 0))
    out = a.out or os.path.join(os.environ.get("TEMP", "."), f"{a.name}_inspect.png")
    sheet.save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main()
