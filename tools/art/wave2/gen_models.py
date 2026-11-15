"""Wave-2 custom block models (authored facing NORTH) and their textures.

Every element carries all six faces; glowing parts use element `light_emission`
plus NeoForge per-face `neoforge_data` so they glow on 1.21.1 either way.
"""
import math

from w2common import *
from w2model import T, el, model, rot, model_sheet, check_model, auto_uv
from gen_blocks import stone, starstone_base, abyssal_base, aniso_noise, STAR_TONES, AB_TONES

TEX = {}


def glow_faces(e, dirs):
    """Fullbright individual faces (NeoForge per-face data) without lighting the whole element."""
    for d in dirs:
        e['faces'][d]['neoforge_data'] = {'block_light': 15, 'sky_light': 15}
    return e


def tex(name):
    def deco(fn):
        TEX[name] = fn
        return fn
    return deco


def noise_fill(cv, pal, seed, cuts=None, cx=4, cy=4, grain=0.2, x0=0, y0=0, x1=15, y1=15):
    n = aniso_noise(cx, cy, seed, octaves=2)
    g = rng(seed + 7).random((16, 16))
    v = np.clip(n + (g - 0.5) * grain, 0, 1)
    k = len(pal)
    cuts = cuts or [(i + 1) / k for i in range(k - 1)]
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            i = 0
            while i < len(cuts) and v[y, x] > cuts[i]:
                i += 1
            cv.put(x, y, pal[i])


def gold_band(cv, y, lit=True, pal=GOLD):
    for x in range(16):
        cv.put(x, y, pal[5] if (x % 5 == 1 and lit) else pal[4] if lit else pal[2])


# ----------------------------------------------------------------- materials
OBS = [OBSID[1], OBSID[2], OBSID[3], OBSID[4], OBSID[5]]
PUR = [PURPUR[2], PURPUR[3], PURPUR[4], PURPUR[5], PURPUR[6]]


def obsidian(seed):
    cv = Canvas()
    noise_fill(cv, OBS, seed, [0.25, 0.5, 0.72, 0.9], grain=0.3)
    for (x, y) in ((3, 4), (11, 9), (6, 13)):
        cv.put(x, y, VIOLET[1])
    return cv


def purpur(seed, tiles=True):
    """Vanilla-like purpur: soft noise with a 2x2 tile grid of bevelled squares."""
    cv = Canvas()
    noise_fill(cv, PUR, seed, [0.22, 0.48, 0.74, 0.92], grain=0.22)
    if tiles:
        for y in range(16):
            for x in range(16):
                lx, ly = x % 8, y % 8
                if lx == 7 or ly == 7:
                    cv.put(x, y, PURPUR[2])
                elif lx == 0 or ly == 0:
                    cv.put(x, y, PURPUR[6])
    return cv


# ===================================================================== PYLON
@tex('imperial_pylon_base')
def pylon_base():
    """Obsidian slab; rows 14-15 are the slab sides (gold lip over dark obsidian)."""
    cv = obsidian(501)
    gold_band(cv, 14)
    cv.hline(0, 15, 15, OBSID[1])
    for x in (2, 7, 12):
        cv.put(x, 15, OBSID[4])
    return cv


@tex('imperial_pylon_step')
def pylon_step():
    """Purpur step: rows 0-1 are its sides, the 3..13 square is its top with a gold ring."""
    cv = purpur(503, tiles=False)
    gold_band(cv, 0)
    cv.hline(0, 15, 1, PURPUR[3])
    for i in range(4, 12):
        cv.put(i, 4, GOLD[4])
        cv.put(4, i, GOLD[4])
        cv.put(i, 11, GOLD[2])
        cv.put(11, i, GOLD[2])
    for (x, y) in ((4, 4), (11, 4), (4, 11), (11, 11)):
        cv.put(x, y, GOLD[5])
    return cv


@tex('imperial_pylon_claw')
def pylon_claw():
    cv = Canvas()
    for y in range(16):
        for x in range(16):
            cv.put(x, y, GOLD[[4, 3, 3, 2][x % 4]])
    for x in range(16):
        cv.put(x, 0, GOLD[6] if x % 4 == 0 else GOLD[5])
    for y in range(0, 16, 3):
        cv.put(0, y, GOLD[6])
    return cv


def crystal_tex(pal, cracks=False, glints=True, seed=0):
    """Prism facets: 4px bands lit->shaded, a bright edge line on each band, a
    vertical gradient (brighter toward the top) and internal light streaks."""
    cv = Canvas()
    n = len(pal) - 1
    for y in range(16):
        for x in range(16):
            band = x // 4
            k = [3, 2, 1, 2][band]
            if y < 3:
                k += 1
            elif y > 12:
                k -= 1
            cv.put(x, y, pal[max(0, min(n, k))])
        for b in range(4):
            cv.put(b * 4, y, pal[max(0, min(n, [4, 3, 2, 3][b] + (1 if y < 3 else 0)))])
    if glints:
        for (x, y) in ((1, 2), (5, 7), (9, 4), (13, 10), (2, 12), (6, 1)):
            cv.put(x, y, pal[-1])
        for x in (2, 6):
            for y in range(4, 11):
                if (y + x) % 3:
                    cv.put(x, y, pal[min(n, 4)])
    if cracks:
        r = rng(seed)
        for (sx, sy) in ((2, 3), (9, 6), (6, 11), (13, 2)):
            x, y = sx, sy
            for i in range(5):
                cv.put(x % 16, y % 16, pal[0])
                if i == 2:
                    cv.put((x + 1) % 16, y % 16, '#7a4ad0')
                x += int(r.integers(-1, 2))
                y += 1
    return cv


@tex('imperial_pylon_crystal')
def pylon_crystal():
    pal = ['#6a2cc8', '#9050f4', '#b88aff', '#d8c0ff', '#f0e6ff', '#ffffff']
    return crystal_tex(pal)


@tex('imperial_pylon_crystal_dim')
def pylon_crystal_dim():
    pal = ['#160e24', '#2a2040', '#3c3058', '#4e406e', '#625484', '#7a6c9c']
    cv = crystal_tex(pal, cracks=True, glints=False, seed=7)
    for (x, y) in ((1, 1), (5, 2), (9, 1)):
        cv.put(x, y, pal[5])
    return cv


def pylon_common():
    E = []
    E.append(el((2, 0, 2), (14, 2, 14), {
        'all': ('#base', [2, 14, 14, 16]), 'up': ('#base', [2, 1, 14, 13]), 'down': ('#base', [2, 1, 14, 13])},
        name='slab'))
    E.append(el((3, 2, 3), (13, 4, 13), {
        'all': ('#step', [3, 0, 13, 2]), 'up': ('#step', [3, 3, 13, 13]), 'down': ('#step', [3, 3, 13, 13])},
        name='step'))
    for (x, z, ang) in ((4, 4, -22.5), (10.5, 4, 22.5), (4, 10.5, -22.5), (10.5, 10.5, 22.5)):
        r = rot('z', ang, (x + 0.75, 4, z + 0.75))
        E.append(el((x, 4, z), (x + 1.5, 7, z + 1.5), {
            'all': ('#claw', [0, 0, 1.5, 3]), 'up': ('#claw', [0, 0, 1.5, 1.5]), 'down': ('#claw', [0, 0, 1.5, 1.5])},
            rotation=r, name='claw'))
        E.append(el((x + 0.25, 7, z + 0.25), (x + 1.25, 8.5, z + 1.25), {
            'all': ('#claw', [4, 0, 5, 1.5]), 'up': ('#claw', [0, 0, 1, 1]), 'down': ('#claw', [0, 0, 1, 1])},
            rotation=r, name='claw_tip'))
    return E


def crystal_box(f, t, tex_ref, light=None, name='crystal', rotation=None):
    w = t[0] - f[0]
    h = t[1] - f[1]
    d = t[2] - f[2]
    return el(f, t, {
        'north': (tex_ref, [4, 16 - h, 4 + w, 16]), 'south': (tex_ref, [12 - w, 16 - h, 12, 16]),
        'west': (tex_ref, [0, 16 - h, d, 16]), 'east': (tex_ref, [8, 16 - h, 8 + d, 16]),
        'up': (tex_ref, [0, 0, w, d]), 'down': (tex_ref, [8, 8, 8 + w, 8 + d])},
        rotation=rotation or rot('y', 45, (8, 8, 8)), name=name, light=light)


def imperial_pylon_model():
    tx = {'particle': T('imperial_pylon_base'), 'base': T('imperial_pylon_base'),
          'step': T('imperial_pylon_step'), 'claw': T('imperial_pylon_claw'),
          'crystal': T('imperial_pylon_crystal_dim')}
    E = pylon_common()
    E.append(crystal_box((5.5, 4, 5.5), (10.5, 10, 10.5), '#crystal', name='crystal_stump'))
    E.append(crystal_box((5.8, 10, 5.8), (8.6, 13.5, 8.6), '#crystal', name='jag_a',
                         rotation=rot('y', 45, (8, 10, 8))))
    E.append(crystal_box((8.2, 10, 7.2), (10.2, 11.75, 9.2), '#crystal', name='jag_b',
                         rotation=rot('y', 45, (8, 10, 8))))
    E.append(el((5.2, 7, 5.2), (10.8, 7.75, 10.8), {
        'all': ('#claw', [0, 2, 5.6, 2.75]), 'up': ('#claw', [0, 0, 5.6, 5.6]), 'down': ('#claw', [0, 0, 5.6, 5.6])},
        rotation=rot('y', 45, (8, 7, 8)), name='band'))
    E.append(el((8.5, 4, 3.4), (13, 5.4, 4.8), {
        'all': ('#crystal', [0, 10, 4.5, 11.4]), 'up': ('#crystal', [4, 2, 8.5, 3.4]),
        'down': ('#crystal', [4, 2, 8.5, 3.4]), 'west': ('#crystal', [0, 10, 1.4, 11.4]),
        'east': ('#crystal', [8, 10, 9.4, 11.4])},
        rotation=rot('y', -22.5, (10.75, 4, 4.1)), name='fallen_shard'))
    model('imperial_pylon', tx, E)


def imperial_pylon_restored_model():
    tx = {'particle': T('imperial_pylon_base'), 'base': T('imperial_pylon_base'),
          'step': T('imperial_pylon_step'), 'claw': T('imperial_pylon_claw'),
          'crystal': T('imperial_pylon_crystal')}
    E = pylon_common()
    E.append(crystal_box((5.5, 4, 5.5), (10.5, 14, 10.5), '#crystal', light=15, name='crystal'))
    E.append(crystal_box((6.4, 14, 6.4), (9.6, 15.25, 9.6), '#crystal', light=15, name='crystal_cap'))
    E.append(crystal_box((7.2, 15.25, 7.2), (8.8, 16, 8.8), '#crystal', light=15, name='crystal_tip'))
    for y in (7, 11.5):
        E.append(el((5.2, y, 5.2), (10.8, y + 0.75, 10.8), {
            'all': ('#claw', [0, 2, 5.6, 2.75]), 'up': ('#claw', [0, 0, 5.6, 5.6]),
            'down': ('#claw', [0, 0, 5.6, 5.6])},
            rotation=rot('y', 45, (8, y, 8)), name='band'))
    model('imperial_pylon_restored', tx, E)


@tex('empty_throne_purpur')
def throne_purpur():
    """Seat sides (rows 10-15): gold lip, carved purpur panel, obsidian plinth."""
    cv = purpur(511, tiles=False)
    gold_band(cv, 10)
    cv.hline(0, 15, 11, GOLD[2])
    for y in (12, 13, 14):
        for x in range(16):
            lx = x % 8
            if lx in (0, 7):
                cv.put(x, y, PURPUR[2] if lx == 7 else PURPUR[6])
            elif y == 12:
                cv.put(x, y, PURPUR[3])
    for x in range(16):
        cv.put(x, 15, OBSID[2] if x % 3 else OBSID[4])
    for x in (3, 4, 11, 12):
        cv.put(x, 13, GOLD[3])
    return cv


@tex('empty_throne_obsidian')
def throne_obsidian():
    """Backrest: obsidian with a gold rim (top row + edges) and a gold crest stud."""
    cv = obsidian(513)
    gold_band(cv, 0)
    cv.hline(0, 15, 1, GOLD[2])
    for y in range(16):
        cv.put(0, y, GOLD[4])
        cv.put(15, y, GOLD[2])
    cv.put(7, 0, GOLD[6])
    cv.put(8, 0, GOLD[6])
    return cv


@tex('empty_throne_cushion')
def throne_cushion():
    """Violet tufted velvet with gold buttons; rows 0-1 are a gold-piped edge."""
    cv = Canvas()
    V = ['#3a1470', '#4e1c92', '#6428b4', '#7a3cce', '#9458e2']
    for y in range(16):
        for x in range(16):
            lx, ly = (x + (4 if (y // 4) % 2 else 0)) % 8, y % 4
            d = abs(lx - 3.5) / 4 + abs(ly - 1.5) / 2
            k = 4 if d < 0.4 else 3 if d < 0.8 else 2 if d < 1.15 else 1
            cv.put(x, y, V[k])
    for y in range(0, 16, 4):
        for x in range(16):
            if (x + (4 if (y // 4) % 2 else 0)) % 8 == 7:
                cv.put(x, y + 3, GOLD[4])
    cv.hline(0, 15, 0, GOLD[4])
    cv.hline(0, 15, 1, V[0])
    return cv


@tex('empty_throne_gold')
def throne_gold():
    cv = Canvas()
    noise_fill(cv, [GOLD[2], GOLD[3], GOLD[4], GOLD[5]], 517, grain=0.3)
    cv.hline(0, 15, 0, GOLD[6])
    cv.hline(0, 15, 15, GOLD[1])
    return cv


def empty_throne_model():
    tx = {'particle': T('empty_throne_purpur'), 'purpur': T('empty_throne_purpur'),
          'obsidian': T('empty_throne_obsidian'), 'cushion': T('empty_throne_cushion'),
          'gold': T('empty_throne_gold')}
    E = []
    E.append(el((0, 0, 0), (16, 6, 16), {
        'all': ('#purpur', None), 'north': ('#purpur', [0, 10, 16, 16]), 'south': ('#purpur', [0, 10, 16, 16]),
        'west': ('#purpur', [0, 10, 16, 16]), 'east': ('#purpur', [0, 10, 16, 16]),
        'up': ('#purpur', [0, 0, 16, 16]), 'down': ('#purpur', [0, 0, 16, 16])}, name='seat_base'))
    for x0 in (0, 14):
        E.append(el((x0, 6, 0), (x0 + 2, 9, 12), {
            'all': ('#gold', None), 'north': ('#gold', [0, 0, 2, 3]), 'south': ('#gold', [0, 0, 2, 3]),
            'west': ('#gold', [0, 0, 12, 3]), 'east': ('#gold', [0, 0, 12, 3]),
            'up': ('#gold', [x0, 0, x0 + 2, 12]), 'down': ('#gold', [x0, 0, x0 + 2, 12])}, name='armrest'))
        E.append(el((x0 + 0.5, 9, 0.5), (x0 + 1.5, 10, 1.5), {
            'all': ('#gold', [0, 0, 1, 1])}, name='arm_finial'))
    E.append(el((2, 6, 0.5), (14, 8, 12), {
        'all': ('#cushion', None), 'north': ('#cushion', [2, 0, 14, 2]), 'south': ('#cushion', [2, 0, 14, 2]),
        'west': ('#cushion', [0, 0, 11.5, 2]), 'east': ('#cushion', [0, 0, 11.5, 2]),
        'up': ('#cushion', [2, 2, 14, 13.5]), 'down': ('#cushion', [2, 2, 14, 13.5])}, name='seat_cushion'))
    E.append(el((0, 6, 12), (16, 16, 16), {
        'all': ('#obsidian', None), 'north': ('#obsidian', [0, 0, 16, 10]), 'south': ('#obsidian', [0, 0, 16, 10]),
        'west': ('#obsidian', [12, 0, 16, 10]), 'east': ('#obsidian', [0, 0, 4, 10]),
        'up': ('#obsidian', [0, 0, 16, 4]), 'down': ('#obsidian', [0, 12, 16, 16])}, name='backrest'))
    E.append(el((2, 8, 11), (14, 15, 12), {
        'all': ('#cushion', None), 'north': ('#cushion', [2, 2, 14, 9]), 'south': ('#cushion', [2, 2, 14, 9]),
        'west': ('#cushion', [0, 0, 1, 7]), 'east': ('#cushion', [0, 0, 1, 7]),
        'up': ('#cushion', [2, 0, 14, 1]), 'down': ('#cushion', [2, 1, 14, 2])}, name='back_cushion'))
    # gold crest on top of the backrest (stays inside the block)
    E.append(el((6, 15, 11.5), (10, 16, 12), {'all': ('#gold', [6, 0, 10, 1])}, name='crest'))
    E.append(el((7, 14, 11.25), (9, 16, 11.5), {'all': ('#gold', [7, 0, 9, 2])}, name='crest_gem'))
    model('empty_throne', tx, E)


# ===================================================================== FORGE
@tex('imperial_forge_front')
def forge_front():
    """Front: purpur bricks, obsidian pilasters, gold-framed mouth (x4-12, y7-13
    in texture space), lintel with a violet gem."""
    cv = purpur(521, tiles=False)
    for y in range(16):
        row = y // 4
        off = 0 if row % 2 == 0 else 4
        for x in range(16):
            if y % 4 == 3 or (x + off) % 8 == 7:
                cv.put(x, y, PURPUR[2])
            elif y % 4 == 0:
                cv.put(x, y, PURPUR[6])
    for x0 in (0, 12):
        cv.rect(x0, 3, x0 + 3, 15, OBSID[3])
        cv.vline(x0, 3, 15, OBSID[5])
        cv.vline(x0 + 3, 3, 15, OBSID[1])
        for y in (5, 9, 13):
            cv.put(x0 + 1, y, GOLD[4])
    cv.rect(3, 3, 12, 6, OBSID[2])
    cv.hline(3, 12, 3, OBSID[5])
    cv.put(7, 4, VIOLET[5])
    cv.put(8, 4, VIOLET[3])
    cv.put(7, 5, VIOLET[3])
    cv.put(8, 5, VIOLET[1])
    for x in (5, 10):
        cv.put(x, 4, GOLD[4])
    cv.hline(3, 12, 6, GOLD[5])
    cv.hline(3, 12, 13, GOLD[2])
    cv.vline(3, 6, 13, GOLD[4])
    cv.vline(12, 6, 13, GOLD[2])
    for y in range(7, 13):
        for x in range(4, 12):
            d = abs(x - 7.5) + abs(y - 10.5) * 1.2
            cv.put(x, y, VIOLET[6] if d < 1.5 else VIOLET[4] if d < 3 else VIOLET[3] if d < 4.5 else VIOLET[2])
    cv.rect(0, 13, 15, 15, OBSID[2])
    cv.hline(0, 15, 13, GOLD[4])
    cv.hline(0, 15, 15, OBSID[0])
    cv.rect(0, 0, 15, 2, OBSID[3])
    cv.hline(0, 15, 0, OBSID[5])
    cv.hline(0, 15, 2, GOLD[3])
    return cv


@tex('imperial_forge_side')
def forge_side():
    cv = purpur(523, tiles=False)
    for y in range(16):
        row = y // 4
        off = 0 if row % 2 == 0 else 4
        for x in range(16):
            if y % 4 == 3 or (x + off) % 8 == 7:
                cv.put(x, y, PURPUR[2])
            elif y % 4 == 0:
                cv.put(x, y, PURPUR[6])
    # gold band with a glowing violet vent
    cv.rect(0, 7, 15, 10, OBSID[3])
    cv.hline(0, 15, 7, GOLD[4])
    cv.hline(0, 15, 10, GOLD[2])
    for x in range(5, 11):
        cv.put(x, 8, OBSID[0])
        cv.put(x, 9, VIOLET[3] if x % 2 else VIOLET[2])
    for x in (1, 14):
        cv.put(x, 8, GOLD[5])
    cv.vline(0, 3, 15, OBSID[4])
    cv.vline(15, 3, 15, OBSID[1])
    cv.rect(0, 13, 15, 15, OBSID[2])
    cv.hline(0, 15, 13, GOLD[4])
    cv.hline(0, 15, 15, OBSID[0])
    cv.rect(0, 0, 15, 2, OBSID[3])
    cv.hline(0, 15, 0, OBSID[5])
    cv.hline(0, 15, 2, GOLD[3])
    return cv


@tex('imperial_forge_top')
def forge_top():
    """Deck: obsidian with a gold rim; the 3..13 square is the glowing violet grate."""
    cv = obsidian(525)
    for i in range(16):
        cv.put(i, 0, GOLD[5])
        cv.put(0, i, GOLD[5])
        cv.put(i, 15, GOLD[2])
        cv.put(15, i, GOLD[2])
    for y in range(3, 13):
        for x in range(3, 13):
            if y % 2 == 1:
                cv.put(x, y, OBSID[4] if y < 12 else OBSID[3])
            else:
                d = abs(x - 7.5) + abs(y - 7.5)
                cv.put(x, y, VIOLET[5] if d < 3 else VIOLET[4] if d < 5 else VIOLET[3])
    for i in range(3, 13):
        cv.put(i, 2, GOLD[4])
        cv.put(2, i, GOLD[4])
        cv.put(i, 13, GOLD[2])
        cv.put(13, i, GOLD[2])
    return cv


@tex('imperial_forge_inner')
def forge_inner():
    """Glowing interior: violet flame back wall (rows 0-7), ember bed (8-11), lip (12-15)."""
    cv = Canvas()
    for y in range(8):
        for x in range(16):
            d = abs(x - 7.5) / 8 + (7 - y) / 10
            k = 6 if d < 0.25 else 5 if d < 0.45 else 4 if d < 0.65 else 3
            cv.put(x, y, VIOLET[k])
    for x, y in ((3, 5), (11, 4), (6, 2), (12, 6)):
        cv.put(x, y, '#ffffff')
    for y in range(8, 12):
        for x in range(16):
            cv.put(x, y, VIOLET[5] if (x + y * 3) % 5 else '#ffffff')
    for y in range(12, 16):
        for x in range(16):
            cv.put(x, y, mix(OBSID[3], VIOLET[3], 0.35 + 0.15 * (y - 12)))
    return cv


@tex('imperial_forge_gold')
def forge_gold():
    cv = Canvas()
    noise_fill(cv, [GOLD[2], GOLD[3], GOLD[4], GOLD[5]], 527, grain=0.3)
    cv.hline(0, 15, 0, GOLD[6])
    return cv


def imperial_forge_model():
    tx = {'particle': T('imperial_forge_front'), 'front': T('imperial_forge_front'),
          'side': T('imperial_forge_side'), 'top': T('imperial_forge_top'),
          'inner': T('imperial_forge_inner'), 'gold': T('imperial_forge_gold')}
    E = []
    E.append(el((0, 0, 2), (16, 13, 16), {
        'down': ('#top', [0, 0, 16, 14]), 'up': ('#top', [0, 2, 16, 16]),
        'north': ('#inner', [0, 0, 16, 8]),
        'south': ('#side', [0, 3, 16, 16]), 'west': ('#side', [2, 3, 16, 16]), 'east': ('#side', [0, 3, 14, 16]),
    }, name='body'))
    glow_faces(E[-1], ['north'])
    E.append(el((0, 0, 0), (4, 13, 2), {
        'north': '#front', 'west': ('#side', [0, 3, 2, 16]), 'up': '#top', 'down': '#top',
        'east': ('#inner', [0, 12, 2, 15]), 'south': ('#side', [0, 3, 4, 16])}, name='frame_left'))
    E.append(el((12, 0, 0), (16, 13, 2), {
        'north': '#front', 'east': ('#side', [14, 3, 16, 16]), 'up': '#top', 'down': '#top',
        'west': ('#inner', [0, 12, 2, 15]), 'south': ('#side', [0, 3, 4, 16])}, name='frame_right'))
    E.append(el((4, 0, 0), (12, 3, 2), {
        'north': '#front', 'down': '#top', 'up': ('#inner', [4, 8, 12, 10]),
        'south': ('#side', [4, 13, 12, 16]), 'west': ('#side', [0, 13, 2, 16]), 'east': ('#side', [0, 13, 2, 16])},
        name='frame_sill'))
    glow_faces(E[-1], ['up'])
    E.append(el((4, 9, 0), (12, 13, 2), {
        'north': '#front', 'up': '#top', 'down': ('#inner', [4, 12, 12, 14]),
        'south': ('#side', [4, 3, 12, 7]), 'west': ('#side', [0, 3, 2, 7]), 'east': ('#side', [0, 3, 2, 7])},
        name='frame_lintel'))
    # gold-rimmed deck with a glowing grate
    E.append(el((1, 13, 1), (15, 14, 15), {
        'all': ('#gold', None), 'up': ('#top', [1, 1, 15, 15]), 'down': ('#top', [1, 1, 15, 15]),
        'north': ('#gold', [1, 0, 15, 1]), 'south': ('#gold', [1, 0, 15, 1]),
        'west': ('#gold', [1, 0, 15, 1]), 'east': ('#gold', [1, 0, 15, 1])}, name='deck'))
    E.append(el((3, 14, 3), (13, 15, 13), {
        'all': ('#top', [3, 3, 13, 4]), 'up': ('#top', [3, 3, 13, 13]), 'down': ('#top', [3, 3, 13, 13])},
        name='grate', light=15))
    # obsidian corner finials with gold caps
    for (x, z) in ((0, 0), (13, 0), (0, 13), (13, 13)):
        E.append(el((x, 13, z), (x + 3, 15, z + 3), {
            'all': ('#side', [0, 0, 3, 2]), 'up': ('#gold', [0, 0, 3, 3]), 'down': ('#gold', [0, 0, 3, 3])},
            name='finial'))
        E.append(el((x + 0.75, 15, z + 0.75), (x + 2.25, 16, z + 2.25), {
            'all': ('#gold', [0, 0, 1.5, 1]), 'up': ('#gold', [0, 0, 1.5, 1.5]), 'down': ('#gold', [0, 0, 1.5, 1.5])},
            name='finial_cap'))
    model('imperial_forge', tx, E)


# ===================================================================== STAR GATE PEDESTAL
GATE_OBS = ['#05050c', '#0a0a17', '#101024', '#181833', '#222245']


@tex('star_gate_pedestal_base')
def gate_base():
    """Black frame stone; rows 12-15: base sides (white-gold lip + dark plinth)."""
    cv = Canvas()
    noise_fill(cv, GATE_OBS, 531, [0.25, 0.5, 0.75, 0.92], grain=0.25)
    for x in range(16):
        cv.put(x, 12, WGOLD[4] if x % 4 else WGOLD[5])
    cv.hline(0, 15, 13, WGOLD[2])
    for x in range(16):
        cv.put(x, 15, '#030308')
    for x in (3, 8, 13):
        cv.put(x, 14, PALE[2])
    return cv


@tex('star_gate_pedestal_column')
def gate_column():
    """Starstone column with a white-gold inlaid star and pale-blue rune ticks."""
    cv = starstone_base(533)
    for y in range(16):
        cv.put(4, y, NAVY[6])
        cv.put(11, y, NAVY[1])
    star = [
        "...a...",
        "...a...",
        "..aWa..",
        "aaWWWaa",
        "..aWa..",
        "...a...",
        "...a...",
    ]
    cv.grid(star, {'a': WGOLD[4], 'W': '#fff6dc'}, 5, 4)
    cv.put(8, 7, '#ffffff')
    for (x, y) in ((6, 1), (9, 1), (6, 13), (9, 13), (7, 14), (8, 2)):
        cv.put(x, y, PALE[3])
    cv.hline(4, 11, 0, WGOLD[3])
    cv.hline(4, 11, 15, WGOLD[2])
    return cv


@tex('star_gate_pedestal_top')
def gate_top():
    """Top slab: rows 0-1 are its sides; the 2..14 square is the top with a star socket."""
    cv = Canvas()
    noise_fill(cv, GATE_OBS, 535, [0.25, 0.5, 0.75, 0.92], grain=0.25)
    for x in range(16):
        cv.put(x, 0, WGOLD[5] if x % 4 == 1 else WGOLD[4])
        cv.put(x, 1, GATE_OBS[1])
    for i in range(3, 13):
        cv.put(i, 3, WGOLD[4])
        cv.put(3, i, WGOLD[4])
        cv.put(i, 12, WGOLD[2])
        cv.put(12, i, WGOLD[2])
    socket = [
        "..aba..",
        ".aPPPb.",
        "aPpWpPb",
        "bPWWWPc",
        "bPpWpPc",
        ".bPPPc.",
        "..bcc..",
    ]
    cv.grid(socket, {'a': WGOLD[5], 'b': WGOLD[3], 'c': WGOLD[1], 'P': PALE[1], 'p': PALE[3], 'W': PALE[5]}, 5, 5)
    return cv


@tex('star_gate_pedestal_dragon')
def gate_dragon():
    """Dark dragon scales with grey-violet highlights; row 12 mouth interior,
    rows 14-15 eye glow."""
    cv = Canvas()
    S = ['#121120', '#1c1a2e', '#282540', '#383454', '#4a4570', '#625c8c']
    for y in range(12):
        for x in range(16):
            lx = (x + (2 if (y // 3) % 2 else 0)) % 4
            ly = y % 3
            k = 4 if ly == 0 and lx in (1, 2) else 3 if ly == 0 else 2 if ly == 1 else 1
            if lx == 0 and ly == 2:
                k = 0
            cv.put(x, y, S[k])
    for (x, y) in ((3, 3), (10, 6), (6, 9), (13, 0)):
        cv.put(x, y, S[5])
    cv.hline(0, 15, 12, '#3a0c2c')
    cv.hline(0, 15, 13, '#5a1440')
    for x in range(16):
        cv.put(x, 14, '#f0c8ff' if x % 4 in (1, 2) else VIOLET[4])
        cv.put(x, 15, VIOLET[3])
    return cv


def pedestal_common():
    E = []
    E.append(el((2, 0, 2), (14, 4, 14), {
        'all': ('#base', [2, 12, 14, 16]), 'up': ('#base', [2, 0, 14, 11]), 'down': ('#base', [2, 0, 14, 11])},
        name='base'))
    E.append(el((4, 4, 4), (12, 14, 12), {
        'all': ('#column', [4, 3, 12, 13]), 'up': ('#column', [4, 4, 12, 12]), 'down': ('#column', [4, 4, 12, 12])},
        name='column'))
    E.append(el((2, 14, 2), (14, 16, 14), {
        'all': ('#top', [2, 0, 14, 2]), 'up': ('#top', [2, 2, 14, 14]), 'down': ('#top', [2, 2, 14, 14])},
        name='top'))
    return E


def pedestal_textures():
    return {'particle': T('star_gate_pedestal_base'), 'base': T('star_gate_pedestal_base'),
            'column': T('star_gate_pedestal_column'), 'top': T('star_gate_pedestal_top')}


def star_gate_pedestal_model():
    model('star_gate_pedestal', pedestal_textures(), pedestal_common())


def star_gate_pedestal_head_model():
    """Pedestal crowned with an ender-dragon head sculpture (facing north)."""
    tx = pedestal_textures()
    tx['dragon'] = T('star_gate_pedestal_dragon')
    E = pedestal_common()
    d = '#dragon'

    def sc(u, v, w, h):
        return (d, [u, v, u + w, v + h])

    # skull
    E.append(el((5, 16, 7), (11, 21, 13), {
        'all': sc(0, 0, 6, 5), 'west': sc(4, 0, 6, 5), 'east': sc(4, 0, 6, 5),
        'up': sc(0, 3, 6, 6), 'down': sc(0, 3, 6, 6)}, name='skull'))
    # upper jaw / snout, raised over a slightly open lower jaw
    E.append(el((5.5, 18, 2), (10.5, 20.25, 7), {
        'all': sc(8, 0, 5, 2.25), 'west': sc(8, 2, 5, 2.25), 'east': sc(8, 2, 5, 2.25),
        'up': sc(8, 4, 5, 5), 'down': (d, [0, 12, 5, 13])}, name='snout'))
    E.append(el((6, 16, 2.5), (10, 17.5, 7), {
        'all': sc(2, 6, 4, 1.5), 'west': sc(2, 6, 4.5, 1.5), 'east': sc(2, 6, 4.5, 1.5),
        'up': (d, [0, 12, 4, 13]), 'down': sc(2, 6, 4, 4.5)}, name='jaw'))
    for x in (6, 9):
        E.append(el((x, 20.25, 2.5), (x + 1, 20.85, 3.75), {
            'all': sc(12, 8, 1, 0.6), 'up': sc(12, 8, 1, 1.25), 'down': sc(12, 8, 1, 1.25),
            'west': sc(12, 8, 1.25, 0.6), 'east': sc(12, 8, 1.25, 0.6)}, name='nostril'))
    # glowing eyes on the sides and front corners of the skull
    for x0, x1 in ((4.9, 5), (11, 11.1)):
        E.append(el((x0, 19, 7.5), (x1, 20, 9.75), {'all': (d, [4, 14, 6.25, 15])}, name='eye', light=15))
    for x in (5.25, 9.25):
        E.append(el((x, 19.25, 6.9), (x + 1.5, 20, 7), {'all': (d, [1, 14, 2.5, 14.75])}, name='eye_front',
                    light=15))
    # horns sweeping back + a crest of spines
    for x in (5.5, 9.25):
        E.append(el((x, 20.5, 10), (x + 1.25, 24, 11.25), {
            'all': sc(13, 0, 1.25, 3.5), 'up': sc(13, 0, 1.25, 1.25), 'down': sc(13, 0, 1.25, 1.25)},
            rotation=rot('x', -22.5, (x + 0.6, 20.5, 10.6)), name='horn'))
    for z, h in ((8.5, 1.25), (10.5, 1.75)):
        E.append(el((7.5, 21, z), (8.5, 21 + h, z + 1.25), {
            'all': sc(14, 4, 1, h), 'up': sc(14, 4, 1, 1.25), 'down': sc(14, 4, 1, 1.25),
            'west': sc(14, 4, 1.25, h), 'east': sc(14, 4, 1.25, h)}, name='spine'))
    model('star_gate_pedestal_head', tx, E)


def star_portal_model():
    m = {'parent': 'block/block', 'render_type': 'minecraft:translucent',
         'textures': {'particle': T('star_portal'), 'portal': T('star_portal')},
         'elements': [{
             'name': 'portal_surface', 'from': [0, 12, 0], 'to': [16, 12, 16], 'shade': False,
             'light_emission': 15,
             'faces': {
                 'up': {'uv': [0, 0, 16, 16], 'texture': '#portal',
                        'neoforge_data': {'block_light': 15, 'sky_light': 15}},
                 'down': {'uv': [0, 0, 16, 16], 'texture': '#portal',
                          'neoforge_data': {'block_light': 15, 'sky_light': 15}},
             }}]}
    write_json('models/block/star_portal.json', m)
