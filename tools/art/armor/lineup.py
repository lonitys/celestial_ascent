"""All five sets side by side (reads the built assets).  python lineup.py"""
import os
import sys

import armorkit as ak
import armorlib as al
import geo_preview as gp

SETS = ["titan", "imperial", "stellar", "void", "ascendant"]


def main():
    entries = []
    for s in SETS:
        p = al.asset_paths(f"{s}_armor")
        entries.append((s, gp.load_geo(p["geo"]), gp.load_rgba(p["tex"]), gp.load_rgba(p["glow"])))
    out = os.path.join(ak.PREVIEW, "lineup_all_sets.png")
    ak.lineup(entries, out, views=(("front 3/4", 30, -10), ("back 3/4", 210, -10)), scale=7.5, frame=(50, 46),
              center=(0, 19.5))
    print("wrote", out)


if __name__ == "__main__":
    main()
