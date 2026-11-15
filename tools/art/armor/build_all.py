"""Rebuild every armor set (geo, animation, textures, glowmasks), all previews, then validate.

python build_all.py            -> assets + previews + validation
python build_all.py --no-preview
"""
import subprocess
import sys

import ascendant_armor
import firstperson
import imperial_armor
import lineup
import stellar_armor
import titan_armor
import void_armor


def main():
    preview = "--no-preview" not in sys.argv
    for mod in (titan_armor, imperial_armor, stellar_armor, void_armor, ascendant_armor):
        mod.build(preview=preview)
    if preview:
        lineup.main()
        firstperson.main()
    r = subprocess.run([sys.executable, "validate.py"])
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
