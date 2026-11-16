"""City blocks: the Celestial Crystal (a floating, turning crystal over a small quartz socket).

The model holds socket, gem and ring; tools/split_floating.py splits gem and ring off so
FloatingRenderer can animate them. Run: python tools/art/gen_city_blocks.py && python tools/split_floating.py
"""
from common import *
from materials import *
from blockmodel import el, rot, model, T, emissive

SKY = ['#1f3f8a', '#2c5cc0', '#3f7fe6', '#62a2ff', '#8cc2ff', '#bfe0ff', '#f2fbff']
QUARTZ = CALCITE


def socket_side():
    """Rows 0-3: quartz with a gold band (rows 1-2) over a dark lapis foot (row 3)."""
    cv = Canvas()
    noise = tile_noise(16, 16, 4, 71)
    for y in range(16):
        for x in range(16):
            cv.put(x, y, QUARTZ[5] if noise[y, x] < 0.6 else QUARTZ[4])
    cv.hline(0, 15, 0, QUARTZ[6])
    for x in range(16):
        cv.put(x, 1, GOLD[5] if x % 4 in (1, 2) else GOLD[4])
        cv.put(x, 2, GOLD[2])
    cv.hline(0, 15, 3, SKY[0])
    for y in range(4, 16):
        for x in range(16):
            cv.put(x, y, QUARTZ[4] if (x + y) % 7 else QUARTZ[3])
    return cv


def socket_top():
    """Quartz disc with a gold octagon ring and a glowing sky-blue centre."""
    cv = Canvas()
    for y in range(16):
        for x in range(16):
            cv.put(x, y, QUARTZ[5] if (x * 3 + y) % 11 else QUARTZ[4])
    bevel(cv, 2, 2, 13, 13, QUARTZ[6], QUARTZ[3])
    ring = [(6, 4), (7, 4), (8, 4), (9, 4), (5, 5), (10, 5), (4, 6), (11, 6), (4, 7), (11, 7), (4, 8), (11, 8),
            (4, 9), (11, 9), (5, 10), (10, 10), (6, 11), (7, 11), (8, 11), (9, 11)]
    for x, y in ring:
        cv.put(x, y, GOLD[5] if x + y < 15 else GOLD[3])
    cv.rect(6, 6, 9, 9, SKY[4])
    cv.rect(7, 7, 8, 8, SKY[6])
    return cv


def gem():
    """Facets as vertical bands, brighter toward the tip, with white glints."""
    cv = Canvas()
    bands = [(6, 5, 4), (5, 4, 3), (4, 3, 2), (5, 4, 3)]
    for y in range(16):
        for x in range(16):
            hi, md, lo = bands[x // 4]
            t = hi if y < 5 else md if y < 11 else lo
            cv.put(x, y, SKY[t])
        cv.put(0, y, SKY[6])
        cv.put(15, y, SKY[1])
    for x, y in ((5, 2), (6, 7), (9, 3), (13, 5), (2, 12), (10, 13)):
        cv.put(x, y, '#ffffff')
    return cv


def ring():
    cv = Canvas()
    for y in range(16):
        for x in range(16):
            cv.put(x, y, GOLD[5] if (x + y) % 5 == 0 else GOLD[4] if y % 2 == 0 else GOLD[3])
    return cv


def celestial_crystal_model():
    tex = {'particle': T('celestial_crystal_socket'), 'socket': T('celestial_crystal_socket'),
           'top': T('celestial_crystal_top'), 'gem': T('celestial_crystal_gem'), 'ring': T('celestial_crystal_ring')}
    E = []
    side = ('#socket', [2, 0, 14, 4])
    E.append(el((2, 0, 2), (14, 3, 14), {
        'down': ('#socket', [2, 2, 14, 14]), 'up': ('#top', [2, 2, 14, 14]),
        'north': side, 'south': side, 'west': side, 'east': side}, name='socket'))

    def prism(f, t, name, uv_y=(0, 16)):
        y0, y1 = uv_y
        w = t[0] - f[0]
        g = lambda uv: emissive({'uv': uv, 'texture': '#gem'})
        faces = {'up': g([0, 0, w, w]), 'down': g([8, 8, 8 + w, 8 + w]),
                 'north': g([0, y0, w, y1]), 'east': g([4, y0, 4 + w, y1]),
                 'south': g([8, y0, 8 + w, y1]), 'west': g([12 - w, y0, 12, y1])}
        return el(f, t, faces, rotation=rot('y', 45, (8, 8, 8)), name=name)

    # octahedral gem from stacked prisms: lower tip, girdle, upper tip
    for (w, y0, y1, uv) in ((2, 3, 5, (14, 16)), (4, 5, 8, (11, 14)), (6, 8, 11, (8, 11)), (8, 11, 18, (3, 10)),
                             (6, 18, 21, (2, 5)), (4, 21, 24, (1, 4)), (2, 24, 27, (0, 3))):
        a, b = 8 - w / 2, 8 + w / 2
        E.append(prism((a, y0, a), (b, y1, b), 'gem', uv))
    # gold ring around the girdle (four bars, turning the other way)
    bar = lambda f, t: el(f, t, {k: ('#ring', [0, 0, 16, 1]) for k in ('north', 'south', 'east', 'west', 'up', 'down')},
                          name='ring')
    E.append(bar((1, 14, 1), (15, 15, 2)))
    E.append(bar((1, 14, 14), (15, 15, 15)))
    E.append(bar((1, 14, 2), (2, 15, 14)))
    E.append(bar((14, 14, 2), (15, 15, 14)))
    m = model('celestial_crystal', tex, E)
    # the full model is also the item model: shrink it so the tall gem fits a slot
    m['display'] = {
        'gui': {'rotation': [30, 225, 0], 'translation': [0, -2.5, 0], 'scale': [0.42, 0.42, 0.42]},
        'ground': {'rotation': [0, 0, 0], 'translation': [0, 2, 0], 'scale': [0.25, 0.25, 0.25]},
        'fixed': {'rotation': [0, 0, 0], 'translation': [0, -2, 0], 'scale': [0.45, 0.45, 0.45]},
        'thirdperson_righthand': {'rotation': [75, 45, 0], 'translation': [0, 2.5, 0], 'scale': [0.3, 0.3, 0.3]},
        'firstperson_righthand': {'rotation': [0, 45, 0], 'translation': [0, 0, 0], 'scale': [0.3, 0.3, 0.3]},
        'firstperson_lefthand': {'rotation': [0, 225, 0], 'translation': [0, 0, 0], 'scale': [0.3, 0.3, 0.3]},
    }
    write_json('models/block/celestial_crystal.json', m)


TEXTURES = {'celestial_crystal_socket': socket_side, 'celestial_crystal_top': socket_top,
            'celestial_crystal_gem': gem, 'celestial_crystal_ring': ring}


def main():
    out = []
    for name, fn in TEXTURES.items():
        cv = fn()
        cv.save(f'textures/block/{name}.png')
        out.append((name, cv.pil()))
    celestial_crystal_model()
    print(contact_sheet(out, 'city_block_textures.png', cols=4))
    from model_preview import model_sheet
    print(model_sheet(['celestial_crystal'], 'city_block_models.png', S=12))


if __name__ == '__main__':
    main()
