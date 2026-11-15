"""Armor icons for the Imperial, Stellar, Void and Ascendant sets.

Silhouettes are copied from the titan armor family (tools/art/gen_titan_items.py)
so the sets line up in the inventory; each set gets its own palette and a few
set-specific details (gold filigree, star specks, void veins, prismatic gems).
Roles in the grids: 1-6 main plate (dark->light), a-d trim (light->dark),
x/y/z/w gem inlay (deep->white), v dark interior.
"""
from w2common import *

HELMET = [
    "................",
    "................",
    ".....5aab4......",
    "....45abc43.....",
    "...4565bc4432...",
    "..4aabbzybccd2..",
    "..45vvvwyvvv32..",
    "..4544xyx44332..",
    "..354v3433v322..",
    "..3443....3221..",
    "..2aa2....2dd1..",
    "...bc......cd...",
    "................",
    "................",
    "................",
    "................",
]
CHESTPLATE = [
    "................",
    "..abbc....bccd..",
    ".abbbc5..4cccdd.",
    ".abccc5444cccdd.",
    ".2bcc65544ccd21.",
    ".234455zy443321.",
    ".2344zzwyx43321.",
    ".213445yx443211.",
    "...3445xy4332...",
    "...abbbbbcccd...",
    "...3454yx4332...",
    "...34544443321..",
    "....3x4334x2....",
    ".....233221.....",
    "................",
    "................",
]
LEGGINGS = [
    "................",
    "................",
    "...abbbzybccd...",
    "...4565444332...",
    "...4654544322...",
    "...4554334322...",
    "...4543..3432...",
    "...4zy3..3zy2...",
    "...3xw3..3xw2...",
    "...a443..344d...",
    "...ab43..34cd...",
    "...bc32..32dd...",
    "................",
    "................",
    "................",
    "................",
]
BOOTS = [
    "................",
    "................",
    "................",
    "...453...433....",
    "...4z3...4z3....",
    "...4y3...4y2....",
    "...453...432....",
    "..4543..44322...",
    "..aabbc.abbcd...",
    ".aabbcd.abccdd..",
    ".2333221.33221..",
    "................",
    "................",
    "................",
    "................",
    "................",
]
PIECES = {'helmet': HELMET, 'chestplate': CHESTPLATE, 'leggings': LEGGINGS, 'boots': BOOTS}

SETS = {
    'imperial': dict(
        main=['#2a1634', '#3e2248', '#56305e', '#704478', '#8e5e96', '#b084b6'],
        trim=['#ffe07a', '#efc140', '#c48c1c', '#8a5a0e'],
        gem=['#4a149a', '#9b55ff', '#d6b4ff', '#ffffff'],
        v='#12081a', outline=('#22102a', '#130818')),
    'stellar': dict(
        main=['#0f1632', '#18244a', '#223462', '#2e447e', '#40599c', '#5e78ba'],
        trim=['#fff4d0', '#f2d88a', '#d0aa52', '#94702c'],
        gem=['#2a5cb0', '#6aa8f0', '#c4e4ff', '#ffffff'],
        v='#060916', outline=('#0a1028', '#050818')),
    'void': dict(
        main=['#0c0812', '#150e1f', '#1f152d', '#2b1e3d', '#3a2a52', '#504070'],
        trim=['#5e4884', '#463463', '#33244b', '#231834'],
        gem=['#8a147a', '#e83cc4', '#ff9ae8', '#ffffff'],
        v='#040208', outline=('#08050c', '#040206')),
    'ascendant': dict(
        main=['#8a6418', '#b48a2e', '#d8b04e', '#eecf78', '#fae6ac', '#fffaf0'],
        trim=['#ffffff', '#f4ecdc', '#dccfb0', '#b0a07c'],
        gem=['#9a6aff', '#6fe8ff', '#ff9ae8', '#ffffff'],
        v='#3a2a10', outline=('#5a3c0c', '#3a2606')),
}

PRISM_CYCLE = ['#7ff0ff', '#a0a8ff', '#ff9ae8', '#fff27a', '#9affb8']


def base(set_name, piece):
    st = SETS[set_name]
    pal = {str(i + 1): c for i, c in enumerate(st['main'])}
    pal.update({k: c for k, c in zip('abcd', st['trim'])})
    pal.update({k: c for k, c in zip('xyzw', st['gem'])})
    pal['v'] = st['v']
    cv = Canvas()
    cv.grid(PIECES[piece], pal)
    return cv


def cells(piece, chars):
    return [(x, y) for y, r in enumerate(PIECES[piece]) for x, ch in enumerate(r) if ch in chars]


# ---------------------------------------------------------------- set details
def imperial(piece, cv):
    st = SETS['imperial']
    G = GOLD
    if piece == 'helmet':
        for x, y in ((5, 2), (6, 2)):
            cv.put(x, y, G[5])
        cv.put(7, 2, G[3])
        cv.put(4, 7, G[4])
        cv.put(11, 7, G[2])
    elif piece == 'chestplate':
        # gold collar lines and a sternum ridge
        for (x, y) in ((6, 2), (6, 3), (9, 3)):
            cv.put(x, y, G[4])
        for (x, y) in ((4, 11), (5, 11), (10, 11), (11, 11)):
            cv.put(x, y, G[3])
    elif piece == 'leggings':
        for y in (4, 5):
            cv.put(4, y, G[4])
            cv.put(11, y, G[2])
    elif piece == 'boots':
        cv.put(3, 6, G[4])
        cv.put(9, 6, G[3])
    return cv


def stellar(piece, cv):
    stars = {
        'helmet': [(4, 4, 'w'), (11, 8, 'g'), (3, 8, 'b')],
        'chestplate': [(3, 5, 'w'), (12, 6, 'g'), (5, 11, 'b'), (10, 10, 'w'), (2, 7, 'g')],
        'leggings': [(5, 4, 'w'), (10, 5, 'g'), (4, 10, 'b'), (11, 6, 'w')],
        'boots': [(4, 3, 'w'), (10, 7, 'g')],
    }[piece]
    cols = {'w': '#ffffff', 'g': WGOLD[4], 'b': PALE[4]}
    for x, y, k in stars:
        cv.put(x, y, cols[k])
    return cv


def void(piece, cv):
    veins = {
        'helmet': [(4, 3, 2), (3, 4, 3), (11, 4, 2), (12, 5, 3), (4, 8, 3)],
        'chestplate': [(3, 4, 2), (4, 5, 3), (4, 6, 2), (11, 5, 3), (12, 6, 2), (5, 10, 2), (10, 11, 3),
                       (9, 11, 2)],
        'leggings': [(4, 3, 3), (5, 4, 2), (10, 4, 3), (11, 5, 2), (4, 6, 2)],
        'boots': [(3, 7, 3), (10, 7, 2), (4, 6, 2)],
    }[piece]
    for x, y, k in veins:
        cv.put(x, y, MAGENTA[k])
    return cv


def ascendant(piece, cv):
    # prismatic gem: violet/cyan/pink facets around the white core, plus a gold glint
    hi = {'helmet': [(5, 4)], 'chestplate': [(5, 4), (10, 9)], 'leggings': [(4, 3)], 'boots': [(4, 3), (10, 3)]}
    for x, y in hi[piece]:
        cv.put(x, y, '#ffffff')
    return cv


DETAIL = {'imperial': imperial, 'stellar': stellar, 'void': void, 'ascendant': ascendant}


def make(set_name, piece):
    cv = base(set_name, piece)
    cv = DETAIL[set_name](piece, cv)
    outline(cv, *SETS[set_name]['outline'])
    if set_name == 'ascendant':
        glints = {'helmet': (13, 2), 'chestplate': (14, 0), 'leggings': (14, 1), 'boots': (13, 2)}
        gx, gy = glints[piece]
        for (x, y, c) in ((gx, gy, '#ffffff'), (gx - 1, gy, '#fff2c8'), (gx + 1, gy, '#fff2c8'),
                          (gx, gy - 1, '#fff2c8'), (gx, gy + 1, '#fff2c8')):
            put_if_empty(cv, x, y, c)
    return cv


def main():
    out = []
    for s in SETS:
        for p in PIECES:
            cv = make(s, p)
            name = f'{s}_{p}'
            cv.save(f'textures/item/{name}.png')
            out.append((name, cv.pil()))
    print(sheet(out, 'armor.png', cols=4))
    return out


if __name__ == '__main__':
    main()
