"""Split the decorative tops off altar and pedestal models so they can float.

For every entry in SPLITS the authored model (models/block/<model>.json) stays untouched:
it is still the item model. This script writes, next to it,
  models/block/<model>_base.json            the model without the floating parts (used by the blockstate)
  models/block/floating/<model>[_<g>].json  one model per floating group (rendered by FloatingRenderer)

Elements are picked by their "name"; "name@y" only picks elements of that name whose "from"
y is at least y (the pylon has two bands and only the upper one floats). Re-run after
regenerating the art (tools/art/*): python tools/split_floating.py
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MODELS = os.path.join(ROOT, 'src', 'main', 'resources', 'assets', 'celestialascent', 'models', 'block')

# model -> {group: names}; group "" means models/block/floating/<model>.json
SPLITS = {
    'frost_altar': {'': {'ice_spire', 'ice_shard'}},
    'tide_altar': {'': {'water_orb'}},
    'storm_altar': {'': {'spark_spire', 'spark'}},
    'magma_altar': {'': {'rock_a', 'rock_b'}},
    'seraph_altar': {'': {'wing', 'orb', 'orb_flare', 'halo'}},
    'leviathan_altar': {'': {'orb', 'orb_flare', 'coil', 'neck', 'head', 'jaw', 'eye', 'fin'}},
    'herald_altar': {'': {'sun_disc'}},
    'sky_altar': {'': {'star_v', 'star_x', 'star_z', 'star_core'}},
    'void_infuser': {'': {'void_orb', 'orb_core'}},
    'ascension_altar': {'gem': {'gem', 'gem_spire'}, 'halo': {'halo'}},
    'imperial_pylon_restored': {'': {'crystal', 'crystal_cap', 'crystal_tip', 'band@11'}},
    'relic_pedestal': {'': {'crystal_spire', 'crystal_shard'}},
    'celestial_crystal': {'gem': {'gem'}, 'ring': {'ring'}},
    'star_gate_pedestal_head': {'': {'skull', 'snout', 'jaw', 'nostril', 'eye', 'eye_front', 'horn', 'spine'}},
}


def picks(element, names):
    for n in names:
        name, _, min_y = n.partition('@')
        if element.get('name') == name and (not min_y or element['from'][1] >= float(min_y)):
            return True
    return False


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='\n') as f:
        json.dump(data, f, indent=2)
        f.write('\n')


def split(model, groups):
    with open(os.path.join(MODELS, model + '.json')) as f:
        src = json.load(f)
    elements = src['elements']
    taken = set()
    for group, names in groups.items():
        part = [e for e in elements if picks(e, names)]
        if not part:
            raise SystemExit(f'{model}: group {group!r} matched no elements')
        taken.update(i for i, e in enumerate(elements) if picks(e, names))
        out = {k: v for k, v in src.items() if k not in ('elements', 'display')}
        out['parent'] = 'minecraft:block/block'
        out['ambientocclusion'] = False
        out['elements'] = part
        write(os.path.join(MODELS, 'floating', model + (('_' + group) if group else '') + '.json'), out)
    base = {k: v for k, v in src.items() if k != 'elements'}
    base['elements'] = [e for i, e in enumerate(elements) if i not in taken]
    write(os.path.join(MODELS, model + '_base.json'), base)
    print(f'{model}: {len(taken)} floating of {len(elements)} elements')


if __name__ == '__main__':
    for m, g in SPLITS.items():
        split(m, g)
