"""Render all four titans side by side at the same scale (front and 3/4 rows), optionally posed.

python lineup.py [--out PATH] [--scale 4] [--pose idle:1.5]
"""
import argparse
import os

from PIL import Image, ImageDraw

import geo_preview as gp
import titanlib as tl

NAMES = ["frost_titan", "tide_titan", "storm_titan", "magma_titan"]
HITBOX = {"frost_titan": (2.0, 4.0), "tide_titan": (2.0, 4.2), "storm_titan": (2.2, 4.5), "magma_titan": (2.4, 4.6)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(tl.PREVIEW, "titans_lineup.png"))
    ap.add_argument("--scale", type=float, default=4.0)
    ap.add_argument("--views", default="front:0:-6,3/4:35:-12")
    ap.add_argument("--hitbox", action="store_true")
    a = ap.parse_args()
    views = [(v.split(":")[0], float(v.split(":")[1]), float(v.split(":")[2])) for v in a.views.split(",")]
    fw, fh = 84, 90
    W, H = int(fw * a.scale), int(fh * a.scale)
    sheet = Image.new("RGB", (W * len(NAMES), H * len(views)), (20, 20, 24))
    for i, n in enumerate(NAMES):
        p = tl.asset_paths(n)
        geo = gp.load_geo(p["geo"])
        tex = gp.load_rgba(p["tex"])
        glow = gp.load_rgba(p["glow"])
        for j, (vn, yaw, pitch) in enumerate(views):
            im = gp.render(geo, tex, glow, None, yaw=yaw, pitch=pitch, scale=a.scale, size=(W, H),
                           center=(0, fh / 2 - 6), hitbox=HITBOX[n] if a.hitbox else None)
            ImageDraw.Draw(im).text((6, 4), f"{n} ({vn})", fill=(230, 230, 240))
            sheet.paste(im, (i * W, j * H))
    sheet.save(a.out)
    print(a.out, sheet.size)


if __name__ == "__main__":
    main()
