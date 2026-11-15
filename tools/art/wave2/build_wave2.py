"""Regenerate every wave-2 art asset and validate the results.

usage: python build_wave2.py            (from tools/art/wave2)
       python build_wave2.py --check    (validate only)
"""
import json
import os
import sys

import numpy as np
from PIL import Image

from w2common import ASSETS, sheet, inventory_strip
import w2model

ITEMS = ['imperial_plating', 'ender_gear', 'colossus_core', 'imperial_seal',
         'stardust', 'dormant_star_core', 'star_core', 'star_compass',
         'void_essence', 'void_heart', 'primordial_core', 'abyssal_beacon', 'ascension_pearl']
ITEMS += [f'{s}_{p}' for s in ('imperial', 'stellar', 'void', 'ascendant')
          for p in ('helmet', 'chestplate', 'leggings', 'boots')]
BLOCKS = ['starstone', 'starlit_starstone', 'starstone_bricks', 'stardust_ore', 'star_gate_frame',
          'void_essence_ore', 'abyssal_stone', 'abyssal_stone_crack1', 'abyssal_stone_crack2',
          'abyssal_stone_crack3', 'imperial_barrier', 'star_crystal']
MODELS = ['imperial_pylon', 'imperial_pylon_restored', 'empty_throne', 'imperial_forge',
          'star_gate_pedestal', 'star_gate_pedestal_head', 'star_portal',
          'seraph_altar', 'leviathan_altar', 'herald_altar',
          'sky_altar', 'void_infuser', 'ascension_altar', 'quest_board']
GUIS = {'imperial_forge': (176, 166), 'sky_altar': (176, 166), 'void_infuser': (176, 166),
        'ascension_altar': (176, 166), 'quest_board': (176, 186)}


def generate():
    import gen_items, gen_armor, gen_blocks, build_models, gen_guis, gen_entity
    gen_items.main()
    gen_armor.main()
    gen_blocks.main()
    build_models.main()
    gen_guis.main()
    gen_entity.main()


def png(rel, size):
    p = os.path.join(ASSETS, rel)
    assert os.path.exists(p), f'missing {rel}'
    with Image.open(p) as im:
        im.verify()
    im = Image.open(p)
    assert im.format == 'PNG', f'{rel} not PNG'
    assert im.size == size, f'{rel} is {im.size}, expected {size}'
    assert im.mode == 'RGBA', f'{rel} mode {im.mode}'
    return np.array(im)


def check():
    errs = []

    def guard(fn, *a):
        try:
            return fn(*a)
        except AssertionError as e:
            errs.append(str(e))

    for n in ITEMS:
        a = guard(png, f'textures/item/{n}.png', (16, 16))
        if a is not None and a[:, :, 3].max() == 0:
            errs.append(f'{n} is empty')
    for n in BLOCKS:
        a = guard(png, f'textures/block/{n}.png', (16, 16))
        if a is None:
            continue
        if n not in ('imperial_barrier', 'star_crystal') and (a[:, :, 3] != 255).any():
            errs.append(f'{n} has transparent pixels')
        if n == 'imperial_barrier':
            lo, hi = int(a[:, :, 3].min()), int(a[:, :, 3].max())
            if not (95 <= lo and hi <= 170):
                errs.append(f'imperial_barrier alpha {lo}-{hi}')
    a = guard(png, 'textures/block/star_portal.png', (16, 16 * 32))
    meta = os.path.join(ASSETS, 'textures', 'block', 'star_portal.png.mcmeta')
    try:
        with open(meta) as f:
            m = json.load(f)
        assert m == {'animation': {'frametime': 2}}, m
    except Exception as e:
        errs.append(f'mcmeta: {e}')
    for n in MODELS:
        p = os.path.join(ASSETS, 'models', 'block', n + '.json')
        try:
            with open(p) as f:
                json.load(f)
        except Exception as e:
            errs.append(f'model {n}: {e}')
            continue
        e = w2model.check_model(n)
        if n == 'star_portal':
            e = [x for x in e if 'faces' not in x]
        errs += [f'{n}: {x}' for x in e]
    with open(os.path.join(ASSETS, 'models', 'block', 'star_portal.json')) as f:
        sp = json.load(f)
    if sp.get('render_type') != 'minecraft:translucent':
        errs.append('star_portal render_type')
    for n, (w, h) in GUIS.items():
        a = guard(png, f'textures/gui/{n}.png', (256, 256))
        if a is not None and (a[:h, 2:w - 2, 3] == 0).any():
            errs.append(f'gui {n}: holes inside the image')
    guard(png, 'textures/entity/void_wraith.png', (32, 32))
    return errs


def overview():
    ims = [(n, Image.open(os.path.join(ASSETS, 'textures', 'item', n + '.png'))) for n in ITEMS]
    print(sheet(ims, 'overview_items.png', cols=8, scale=6))
    print(inventory_strip(ims, 'overview_items_scales.png', scales=(1, 2)))


if __name__ == '__main__':
    if '--check' not in sys.argv:
        generate()
    overview()
    errs = check()
    if errs:
        print('\n'.join('!! ' + e for e in errs))
        sys.exit(1)
    print(f'OK: {len(ITEMS)} items, {len(BLOCKS)} blocks + portal strip, {len(MODELS)} models, '
          f'{len(GUIS)} GUIs, 1 entity texture')
