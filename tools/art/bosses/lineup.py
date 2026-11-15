"""Render all six bosses side by side at the same scale (front and 3/4 rows) on a shared ground line.

python lineup.py [--out PATH] [--scale 3] [--anim idle --time 0.5]
"""
import argparse
import os

import numpy as np
from PIL import Image, ImageDraw

import geo_preview as gp
import bosslib as tl

NAMES = ["sentinel_construct", "ender_colossus", "astral_seraph", "nebula_leviathan", "sun_herald", "void_sovereign"]
VIEWS = [("front", 0, -4), ("3/4", 35, -10)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(tl.PREVIEW, "bosses_lineup.png"))
    ap.add_argument("--scale", type=float, default=3.2)
    ap.add_argument("--anim", default=None)
    ap.add_argument("--time", type=float, default=0.0)
    a = ap.parse_args()
    loaded = []
    for n in NAMES:
        p = tl.asset_paths(n)
        g = gp.load_geo(p["geo"])
        pose = None
        if a.anim:
            anims = gp.load_anims(p["anim"])
            if a.anim in anims:
                pose = gp.sample_anim(anims[a.anim], a.time)
        loaded.append((n, g, gp.load_rgba(p["tex"]), gp.load_rgba(p["glow"]), pose))
    top = max(gp.model_extent(g, pose)[1][1] for _, g, _, _, pose in loaded) + 6
    H = int(top * a.scale) + 30
    rows = []
    for vn, yaw, pitch in VIEWS:
        tiles = []
        for n, g, tex, glow, pose in loaded:
            lo, hi = gp.model_extent(g, pose)
            V = gp.view_matrix(yaw, pitch)
            corners = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
            vx = corners @ V.T
            w = (vx[:, 0].max() - vx[:, 0].min()) * a.scale + 30
            cx = (vx[:, 0].max() + vx[:, 0].min()) / 2
            W = int(max(w, 40 * a.scale))
            cy = (top - 6) / 2 - 2
            im = gp.render(g, tex, glow, pose, yaw=yaw, pitch=pitch, scale=a.scale, size=(W, H), center=(cx, cy))
            ImageDraw.Draw(im).text((6, 4), f"{n} ({vn})", fill=(230, 230, 240))
            tiles.append(im)
        row = Image.new("RGB", (sum(t.size[0] for t in tiles), H), (20, 20, 24))
        x = 0
        for t in tiles:
            row.paste(t, (x, 0))
            x += t.size[0]
        rows.append(row)
    sheet = Image.new("RGB", (max(r.size[0] for r in rows), H * len(rows)), (20, 20, 24))
    for k, r in enumerate(rows):
        sheet.paste(r, (0, k * H))
    sheet.save(a.out)
    print(a.out, sheet.size)


if __name__ == "__main__":
    main()
