"""Generate every wave-2 block model + texture, validate, and render previews.

usage: python build_models.py [names...]
"""
import sys

from w2common import sheet
import w2model
import gen_models
import gen_altars
import gen_stations

MODELS = {
    'imperial_pylon': gen_models.imperial_pylon_model,
    'imperial_pylon_restored': gen_models.imperial_pylon_restored_model,
    'empty_throne': gen_models.empty_throne_model,
    'imperial_forge': gen_models.imperial_forge_model,
    'star_gate_pedestal': gen_models.star_gate_pedestal_model,
    'star_gate_pedestal_head': gen_models.star_gate_pedestal_head_model,
    'star_portal': gen_models.star_portal_model,
}
MODELS.update(gen_altars.MODELS)
MODELS.update(gen_stations.MODELS)
TEXTURES = {}
for mod in (gen_models, gen_altars, gen_stations):
    TEXTURES.update(mod.TEX)

GROUPS = {
    'models_empire.png': ['imperial_pylon', 'imperial_pylon_restored', 'empty_throne', 'imperial_forge'],
    'models_stars.png': ['star_gate_pedestal', 'star_gate_pedestal_head', 'star_portal', 'sky_altar'],
    'models_altars.png': ['seraph_altar', 'leviathan_altar', 'herald_altar'],
    'models_stations.png': ['void_infuser', 'ascension_altar', 'quest_board'],
}


def main(only=None):
    out = []
    for name, fn in TEXTURES.items():
        cv = fn()
        cv.save(f'textures/block/{name}.png')
        out.append((name, cv.pil()))
    for name, fn in MODELS.items():
        fn()
    print(sheet(out, 'model_textures.png', cols=8, scale=6))
    bad = False
    for name in MODELS:
        errs = w2model.check_model(name)
        if name == 'star_portal':
            errs = [e for e in errs if 'faces' not in e]
        if errs:
            bad = True
            print('!!', name, errs)
    for fname, names in GROUPS.items():
        if only and not any(n in only for n in names):
            continue
        print(w2model.model_sheet(names, fname, S=11))
    return not bad


if __name__ == '__main__':
    main(sys.argv[1:] or None)
