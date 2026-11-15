"""First-person readability check: the chestplate's right arm raised forward, seen from behind the
shoulder (roughly where the camera sits).  python firstperson.py"""
import os

from PIL import Image

import armorkit as ak
import armorlib as al
import geo_preview as gp

SETS = ["titan", "imperial", "stellar", "void", "ascendant"]


def main():
    tiles = []
    for s in SETS:
        p = al.asset_paths(f"{s}_armor")
        geo, tex, glow = gp.load_geo(p["geo"]), gp.load_rgba(p["tex"]), gp.load_rgba(p["glow"])
        hid = ak.hidden_except(geo, ["chestplate"]) | ak.descendants(geo, ["armorBody", "armorLeftArm"])
        im = ak.render_worn(geo, tex, glow, ("fp", 155, -38), pose="reach", scale=11, frame=(30, 30),
                            center=(5.0, 19.0), hidden=hid, body=True)
        ak._label(im, s + " arm, first-person angle")
        tiles.append(im)
    W, H = tiles[0].size
    sheet = Image.new("RGB", (W * len(tiles), H), (20, 20, 26))
    for i, t in enumerate(tiles):
        sheet.paste(t, (i * W, 0))
    out = os.path.join(ak.PREVIEW, "first_person_arms.png")
    sheet.save(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
