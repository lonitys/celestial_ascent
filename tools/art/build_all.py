"""Regenerate every Celestial Ascent art asset and validate the results.

usage: python build_all.py            (from tools/art)
"""
import json
import os
import sys

from PIL import Image

from common import ASSETS, PREVIEW, contact_sheet, scale_strip

ITEMS = ['copper_aster', 'silver_aster', 'gold_aster', 'titan_aster', 'ender_aster', 'star_aster', 'void_aster',
         'titan_shard', 'frost_core', 'tide_core', 'storm_core', 'magma_core',
         'frost_sigil', 'tide_sigil', 'storm_sigil', 'magma_sigil',
         'titan_helmet', 'titan_chestplate', 'titan_leggings', 'titan_boots', 'dragon_heart']
MODELS = ['bank_counter', 'shop_stall', 'titan_anvil', 'relic_pedestal', 'titan_forge',
          'frost_altar', 'tide_altar', 'storm_altar', 'magma_altar']
GUIS = ['bank', 'shop_owner', 'shop_buyer', 'titan_forge']
VILLAGERS = ['banker', 'titansmith', 'relic_dealer']
ANGLES = {-45, -22.5, 0, 22.5, 45}


def generate():
    import gen_coins, gen_titan_items, gen_economy_blocks, gen_titan_blocks, gen_gui, gen_villagers
    for m in (gen_coins, gen_titan_items, gen_economy_blocks, gen_titan_blocks, gen_gui, gen_villagers):
        m.main()


def check_png(rel, size):
    p = os.path.join(ASSETS, rel)
    assert os.path.exists(p), f'missing {rel}'
    im = Image.open(p)
    im.verify()
    im = Image.open(p)
    assert im.size == size, f'{rel} is {im.size}, expected {size}'
    assert im.mode == 'RGBA', f'{rel} mode {im.mode}'
    return im


def tex_path(ref):
    ns, path = ref.split(':', 1)
    assert ns == 'celestialascent', ref
    return os.path.join(ASSETS, 'textures', path + '.png')


def check_model(name):
    p = os.path.join(ASSETS, 'models', 'block', name + '.json')
    with open(p) as f:
        m = json.load(f)
    assert m.get('parent') == 'block/block', name
    tex = m['textures']
    assert 'particle' in tex, f'{name}: no particle'
    for k, v in tex.items():
        assert os.path.exists(tex_path(v)), f'{name}: texture {k} -> {v} missing'
    assert m['elements'], name
    for i, e in enumerate(m['elements']):
        for v in e['from'] + e['to']:
            assert -16 <= v <= 32, f'{name} element {i} out of range: {e["from"]} {e["to"]}'
        for a, b in zip(e['from'], e['to']):
            assert a <= b, f'{name} element {i} inverted'
        r = e.get('rotation')
        if r:
            assert r['axis'] in 'xyz' and r['angle'] in ANGLES, f'{name} element {i} bad rotation {r}'
        assert e['faces'], f'{name} element {i} has no faces'
        for d, face in e['faces'].items():
            assert d in ('down', 'up', 'north', 'south', 'west', 'east'), d
            t = face.get('texture')
            assert t and t.startswith('#') and t[1:] in tex, f'{name} element {i} face {d} texture {t}'
            uv = face.get('uv')
            assert uv and len(uv) == 4 and all(0 <= u <= 16 for u in uv), f'{name} element {i} face {d} uv {uv}'
    return m


def validate():
    errors = []

    def run(fn, *a):
        try:
            return fn(*a)
        except AssertionError as ex:
            errors.append(str(ex))

    for n in ITEMS:
        run(check_png, f'textures/item/{n}.png', (16, 16))
    for n in MODELS:
        run(check_model, n)
    for n in ('frost_altar', 'tide_altar', 'storm_altar', 'magma_altar'):
        d = os.path.join(ASSETS, 'textures', 'block')
        if not any(f.startswith(n + '_') and f.endswith('.png') for f in os.listdir(d)):
            errors.append(f'no textures/block/{n}_*.png')
    for f in os.listdir(os.path.join(ASSETS, 'textures', 'block')):
        if f.endswith('.png'):
            run(check_png, f'textures/block/{f}', (16, 16))
    for n in GUIS:
        run(check_png, f'textures/gui/{n}.png', (256, 256))
    import gen_villagers
    valid = gen_villagers.valid_mask()
    import numpy as np
    for n in VILLAGERS:
        im = run(check_png, f'textures/entity/villager/profession/{n}.png', (64, 64))
        if im is not None:
            a = np.array(im)[:, :, 3] > 0
            if (a & ~valid).any():
                errors.append(f'{n}: pixels outside villager UV regions')
        mp = os.path.join(ASSETS, 'textures', 'entity', 'villager', 'profession', n + '.png.mcmeta')
        if os.path.exists(mp):
            json.load(open(mp))
    return errors


def overview():
    """Final contact sheets for review."""
    items = [(n, Image.open(os.path.join(ASSETS, 'textures', 'item', n + '.png'))) for n in ITEMS]
    contact_sheet(items, 'all_items.png', cols=7)
    scale_strip([(n, im) for n, im in items[:7]], 'coins_scales.png', scales=(1, 2, 3, 4))
    scale_strip([(n, im) for n, im in items[7:]], 'titan_items_scales.png', scales=(1, 2, 3, 4))
    from model_preview import model_sheet
    model_sheet(MODELS, 'all_block_models.png', S=10)


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    if '--validate-only' not in sys.argv:
        generate()
    errs = validate()
    overview()
    if errs:
        print('VALIDATION FAILED:')
        for e in errs:
            print('  -', e)
        sys.exit(1)
    print(f'OK: {len(ITEMS)} items, {len(MODELS)} models, {len(GUIS)} GUIs, {len(VILLAGERS)} villager overlays validated')
