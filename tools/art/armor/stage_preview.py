"""Stage comparison sheets for the evolving armor pieces (reads the built assets).

Stage bones: names starting with "stage2_" are shown when the piece is stage 2 or 3, "stage3_" only
at stage 3 (the Java renderer toggles them per piece by that prefix).

python stage_preview.py [set ...] [--variant _frost]
  -> preview/<set>_stages.png: columns stage 1 (stage bones hidden) / stage 2 / stage 3,
     rows front 3/4, back 3/4, side, helm close-up, first-person arm.
python stage_preview.py titan --variants
  -> also preview/titan_stage3_variants.png (every titan element texture at stage 3).
"""
import os
import sys

from PIL import Image

import armorkit as ak
import armorlib as al
import geo_preview as gp

SETS = ["titan", "imperial", "stellar", "void", "ascendant"]
VARIANTS = {"titan": ["", "_frost", "_tide", "_storm", "_magma"]}
STAGE_LABEL = {1: "stage 1 (stage bones hidden)", 2: "stage 2", 3: "stage 3"}


def stage_bones(geo, prefix):
    return [b["name"] for b in geo["bones"] if b["name"].startswith(prefix)]


def stage_hidden(geo, stage):
    """Bones (incl. descendants) the renderer hides for a piece at `stage` (1..3)."""
    roots = []
    if stage < 2:
        roots += stage_bones(geo, "stage2_")
    if stage < 3:
        roots += stage_bones(geo, "stage3_")
    return ak.descendants(geo, roots)


def load_set(key, variant=""):
    p = al.asset_paths(f"{key}_armor", variant)
    return gp.load_geo(p["geo"]), gp.load_rgba(p["tex"]), gp.load_rgba(p["glow"])


def _tile(geo, tex, glow, row, stage):
    hid = stage_hidden(geo, stage)
    if row == "fp":
        hid = hid | ak.hidden_except(geo, ["chestplate"]) | ak.descendants(geo, ["armorBody", "armorLeftArm"])
        return ak.render_worn(geo, tex, glow, ("fp", 155, -38), pose="reach", scale=11.5, frame=(32.6, 30),
                              center=(5.0, 19.0), hidden=hid)
    if row == "helm":
        return ak.render_worn(geo, tex, glow, ("helm 3/4", 35, -12), scale=13.4, frame=(28, 25.75),
                              center=(0, 30.2), hidden=hid)
    view = {"front": ("front 3/4", 30, -10), "back": ("back 3/4", 210, -10), "side": ("side", 90, -6)}[row]
    return ak.render_worn(geo, tex, glow, view, scale=7.5, frame=(50, 46), center=(0, 19.5), hidden=hid)


ROWS = [("front", "front 3/4"), ("back", "back 3/4"), ("side", "side"), ("helm", "helm 3/4"),
        ("fp", "first-person arm")]


def stage_sheet(key, variant="", rows=ROWS, out=None):
    geo, tex, glow = load_set(key, variant)
    tiles = []
    for r, rlabel in rows:
        line = []
        for st in (1, 2, 3):
            im = _tile(geo, tex, glow, r, st)
            if im.size != (375, 345):
                im = im.resize((375, 345), Image.LANCZOS)
            ak._label(im, f"{STAGE_LABEL[st]} - {rlabel}")
            line.append(im)
        tiles.append(line)
    W, H = tiles[0][0].size
    sheet = Image.new("RGB", (W * 3, H * len(tiles) + 18), (22, 22, 28))
    for ri, line in enumerate(tiles):
        for ci, im in enumerate(line):
            sheet.paste(im, (ci * W, 18 + ri * H))
    s2 = stage_bones(geo, "stage2_")
    s3 = stage_bones(geo, "stage3_")
    ak._label(sheet, f"{key} armor{variant}: stage parts  ({len(s2)} stage2_ bones, {len(s3)} stage3_ bones)",
              (6, 3), (255, 255, 255))
    out = out or os.path.join(ak.PREVIEW, f"{key}{variant}_stages.png")
    sheet.save(out)
    print("wrote", out)
    return out


def variant_sheet(key):
    entries = []
    for v in VARIANTS.get(key, [""]):
        geo, tex, glow = load_set(key, v)
        entries.append((f"{key}{v or ' neutral'} stage 3", geo, tex, glow))
    out = os.path.join(ak.PREVIEW, f"{key}_stage3_variants.png")
    ak.lineup(entries, out, views=(("front 3/4", 30, -10), ("back 3/4", 210, -10)), scale=7.5, frame=(50, 46),
              center=(0, 19.5))
    print("wrote", out)
    return out


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    variant = ""
    if "--variant" in argv:
        variant = argv[argv.index("--variant") + 1]
        args = [a for a in args if a != variant]
    keys = args or SETS
    for k in keys:
        stage_sheet(k, variant)
        if "--variants" in argv and k in VARIANTS:
            variant_sheet(k)


if __name__ == "__main__":
    main(sys.argv[1:])
