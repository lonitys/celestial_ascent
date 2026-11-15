"""Regenerate all four titans (geo, animations, textures, glowmasks), their previews, the lineup and
run the validator.

python build_all.py [--no-preview]
"""
import importlib
import os
import subprocess
import sys

import titanlib as tl

NAMES = ["frost_titan", "tide_titan", "storm_titan", "magma_titan"]
FRAMES = {"frost_titan": (120, 84), "tide_titan": (120, 90), "storm_titan": (120, 92), "magma_titan": (130, 92)}


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    preview = "--no-preview" not in sys.argv
    for n in NAMES:
        mod = importlib.import_module(n)
        m = mod.build_model()
        geo, rgba, glow, anims = tl.build(n, m, mod.SHADERS, mod.clips(), visible=(5, 6, 2.5))
        if preview:
            for p in tl.previews(n, geo, rgba, glow, anims, mod.HITBOX, mod.POSES, frame=FRAMES[n]):
                print("  preview", p)
            print("  preview", tl.contact_sheet(n, geo, rgba, glow, anims, mod.POSES))
    if preview:
        subprocess.run([sys.executable, os.path.join(here, "lineup.py"), "--hitbox"], check=True, cwd=here)
    r = subprocess.run([sys.executable, os.path.join(here, "validate.py")], cwd=here)
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
