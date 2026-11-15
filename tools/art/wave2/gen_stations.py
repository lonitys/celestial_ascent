"""Crafting stations (sky altar, void infuser, ascension altar) and the quest board."""
import math

from w2common import *
from w2model import T, el, model, rot
from gen_models import noise_fill, glow_faces, crystal_tex
from gen_blocks import starstone_base, abyssal_base

TEX = {}


def tex(name):
    def deco(fn):
        TEX[name] = fn
        return fn
    return deco


AMETH = ['#3c2470', '#55369a', '#7050b8', '#8c68d2', '#a886ea', '#c8a8fa', '#ead6ff']


def box_faces(t, side_uv, top_uv, bottom_uv=None):
    return {'all': (t, side_uv), 'up': (t, top_uv), 'down': (t, bottom_uv or top_uv)}


# ===================================================================== SKY ALTAR
@tex('sky_altar_base')
def sky_base():
    """Starstone; rows 13-15 are the plinth sides (white-gold lip)."""
    cv = starstone_base(701)
    for x in range(16):
        cv.put(x, 13, WGOLD[4] if x % 4 else WGOLD[5])
    cv.hline(0, 15, 14, NAVY[2])
    cv.hline(0, 15, 15, NAVY[0])
    for x in (2, 7, 12):
        cv.put(x, 14, PALE[3])
    return cv


@tex('sky_altar_body')
def sky_body():
    """Polished amethyst panel between starstone posts, with a constellation inlay.
    The body uses rows 5-13."""
    cv = Canvas()
    noise_fill(cv, AMETH[2:6], 703, [0.3, 0.55, 0.8], cx=3, cy=5, grain=0.2)
    for y in range(16):
        for x in (1, 2, 13, 14):
            cv.put(x, y, NAVY[4] if x in (1, 13) else NAVY[3])
        cv.put(0, y, NAVY[5])
        cv.put(15, y, NAVY[1])
        cv.put(3, y, AMETH[6])
        cv.put(12, y, AMETH[1])
    # bevel on the amethyst panel
    cv.hline(3, 12, 5, AMETH[6])
    cv.hline(3, 12, 12, AMETH[1])
    # constellation: white-gold stars joined by faint lines
    stars = [(5, 7), (8, 6), (10, 8), (7, 10), (9, 11)]
    for (a, b) in ((0, 1), (1, 2), (1, 3), (3, 4)):
        (x0, y0), (x1, y1) = stars[a], stars[b]
        n = max(abs(x1 - x0), abs(y1 - y0))
        for i in range(1, n):
            cv.put(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), AMETH[5])
    for i, (x, y) in enumerate(stars):
        cv.put(x, y, '#ffffff' if i == 1 else WGOLD[5])
    for y in (5, 12):
        for x in (1, 14):
            cv.put(x, y, WGOLD[4])
    return cv


@tex('sky_altar_top')
def sky_top():
    """Top slab: rows 0-1 are its sides; the top is a star chart in a gold ring."""
    cv = starstone_base(705)
    for x in range(16):
        cv.put(x, 0, WGOLD[5] if x % 4 == 1 else WGOLD[4])
        cv.put(x, 1, NAVY[2])
    for y in range(2, 16):
        for x in range(16):
            r = math.hypot(x + 0.5 - 8, y + 0.5 - 8)
            if 5.6 < r < 6.6:
                cv.put(x, y, WGOLD[4] if (x + y) < 16 else WGOLD[2])
            elif r <= 5.6:
                cv.put(x, y, NAVY[2] if r > 4 else NAVY[3])
    for (x, y, c) in ((6, 6, '#ffffff'), (9, 5, PALE[4]), (10, 9, WGOLD[5]), (5, 10, PALE[3]), (8, 8, PALE[5])):
        cv.put(x, y, c)
    return cv


@tex('sky_altar_crystal')
def sky_crystal():
    pal = ['#3a6ac8', '#5a90e8', '#8cbcf8', '#c4e0ff', '#eef8ff', '#ffffff']
    return crystal_tex(pal)


def sky_altar_model():
    tx = {'particle': T('sky_altar_body'), 'base': T('sky_altar_base'), 'body': T('sky_altar_body'),
          'top': T('sky_altar_top'), 'crystal': T('sky_altar_crystal')}
    E = []
    E.append(el((0, 0, 0), (16, 3, 16), box_faces('#base', [0, 13, 16, 16], [0, 0, 16, 16]), name='plinth'))
    E.append(el((1, 3, 1), (15, 11, 15), box_faces('#body', [1, 5, 15, 13], [1, 1, 15, 15]), name='body'))
    E.append(el((0, 11, 0), (16, 13, 16), box_faces('#top', [0, 0, 16, 2], [0, 0, 16, 16]), name='top'))
    # crystal cluster growing from the slab
    E.append(el((5.5, 13, 7), (7, 15.5, 8.5), box_faces('#crystal', [0, 2, 1.5, 4.5], [0, 0, 1.5, 1.5]),
                rotation=rot('z', 22.5, (6.25, 13, 7.75)), name='bud'))
    E.append(el((9, 13, 7.5), (10.5, 15, 9), box_faces('#crystal', [4, 3, 5.5, 5], [0, 0, 1.5, 1.5]),
                rotation=rot('z', -22.5, (9.75, 13, 8.25)), name='bud'))
    E.append(el((7.25, 13, 7.25), (8.75, 15, 8.75), box_faces('#crystal', [8, 3, 9.5, 5], [0, 0, 1.5, 1.5]),
                name='stem'))
    # floating six-pointed star
    c = (8, 18.5, 8)
    E.append(el((7.4, 14.75, 7.4), (8.6, 22.25, 8.6), box_faces('#crystal', [1, 0, 2.2, 7.5], [1, 1, 2.2, 2.2]),
                name='star_v', light=15))
    E.append(el((4.25, 17.9, 7.4), (11.75, 19.1, 8.6), box_faces('#crystal', [0, 2, 7.5, 3.2], [0, 2, 7.5, 3.2]),
                name='star_x', light=15))
    E.append(el((7.4, 17.9, 4.25), (8.6, 19.1, 11.75), box_faces('#crystal', [4, 2, 5.2, 3.2], [4, 0, 5.2, 7.5]),
                name='star_z', light=15))
    E.append(el((6.75, 17.25, 6.75), (9.25, 19.75, 9.25), box_faces('#crystal', [12, 0, 14.5, 2.5], [12, 0, 14.5, 2.5]),
                rotation=rot('y', 45, c), name='star_core', light=15))
    model('sky_altar', tx, E)


# ===================================================================== VOID INFUSER
@tex('void_infuser_base')
def void_base():
    cv = abyssal_base()
    for x in range(16):
        cv.put(x, 13, MAGENTA[2] if x % 5 else MAGENTA[3])
    cv.hline(0, 15, 14, ABYSS[3])
    cv.hline(0, 15, 15, ABYSS[0])
    return cv


@tex('void_infuser_body')
def void_body():
    """Sculk-like black-violet growth with glowing magenta pores; uses rows 6-13."""
    cv = Canvas()
    S = ['#0a0612', '#120a1e', '#1a1029', '#231636', '#2e1e46']
    noise_fill(cv, S, 711, [0.2, 0.45, 0.75, 0.93], cx=3, cy=3, grain=0.18)
    pores = [(3, 8), (11, 8), (7, 11), (13, 12), (4, 12), (9, 7)]
    for i, (x, y) in enumerate(pores):
        cv.put(x, y, MAGENTA[5] if i % 2 == 0 else MAGENTA[3])
        for dx, dy in N4:
            cv.put(x + dx, y + dy, '#3a1240')
    for (x, y) in ((5, 9), (6, 10), (9, 9), (10, 10), (12, 10)):
        cv.put(x, y, MAGENTA[1])
    cv.hline(0, 15, 6, S[4])
    cv.hline(0, 15, 13, S[0])
    return cv


@tex('void_infuser_top')
def void_top():
    """Top slab: rows 0-1 are its sides; the top carries a magenta ritual ring."""
    cv = abyssal_base()
    for x in range(16):
        cv.put(x, 0, ABYSS[6])
        cv.put(x, 1, MAGENTA[1] if x % 3 else MAGENTA[2])
    for y in range(2, 16):
        for x in range(16):
            r = math.hypot(x + 0.5 - 8, y + 0.5 - 8)
            if 4.6 < r < 5.6:
                cv.put(x, y, MAGENTA[3] if (x + y) % 3 else MAGENTA[4])
            elif r < 2.4:
                cv.put(x, y, MAGENTA[1])
    return cv


@tex('void_infuser_prong')
def void_prong():
    """Pale violet bone prongs (like a shrieker's), darker toward the base."""
    cv = Canvas()
    B = ['#3a2c4a', '#52426a', '#6e5c88', '#8e7ca8', '#b4a4cc']
    for y in range(16):
        for x in range(16):
            k = 4 - min(4, y // 4) + (0 if x % 4 < 2 else -1)
            cv.put(x, y, B[max(0, k)])
    for y in (5, 10):
        cv.hline(0, 15, y, B[0])
    return cv


@tex('void_infuser_orb')
def void_orb():
    """Glowing magenta void orb with dark swirling rifts and a white heart."""
    cv = Canvas()
    for y in range(16):
        for x in range(16):
            a = math.atan2(y - 7.5, x - 7.5)
            r = math.hypot(x - 7.5, y - 7.5)
            v = math.sin(a * 2 + r * 1.2)
            c = MAGENTA[5] if v > 0.55 else MAGENTA[4] if v > -0.1 else MAGENTA[3] if v > -0.7 else '#3a0a3a'
            if r < 1.6:
                c = '#ffffff'
            elif r < 2.6:
                c = MAGENTA[6]
            cv.put(x, y, c)
    return cv


def void_infuser_model():
    tx = {'particle': T('void_infuser_body'), 'base': T('void_infuser_base'), 'body': T('void_infuser_body'),
          'top': T('void_infuser_top'), 'prong': T('void_infuser_prong'), 'orb': T('void_infuser_orb')}
    E = []
    E.append(el((0, 0, 0), (16, 3, 16), box_faces('#base', [0, 13, 16, 16], [0, 0, 16, 16]), name='plinth'))
    E.append(el((2, 3, 2), (14, 10, 14), box_faces('#body', [2, 6, 14, 13], [2, 2, 14, 14]), name='body'))
    E.append(el((1, 10, 1), (15, 12, 15), box_faces('#top', [1, 0, 15, 2], [1, 1, 15, 15]), name='top'))
    glow_faces(E[-1], ['up'])
    for (x, z, ang) in ((2, 2, -22.5), (12, 2, 22.5), (2, 12, -22.5), (12, 12, 22.5)):
        E.append(el((x, 12, z), (x + 2, 16.5, z + 2), box_faces('#prong', [0, 0, 2, 4.5], [0, 0, 2, 2]),
                    rotation=rot('z', ang, (x + 1, 12, z + 1)), name='prong'))
        E.append(el((x + 0.5, 16.5, z + 0.5), (x + 1.5, 18, z + 1.5), box_faces('#prong', [0, 0, 1, 1.5], [0, 0, 1, 1]),
                    rotation=rot('z', ang, (x + 1, 12, z + 1)), name='prong_tip'))
    # voxel void orb: three crossed boxes, faces sampled around (not on) the white heart
    for f, t, o in (((5.5, 15.5, 6.5), (10.5, 18.5, 9.5), 0), ((6.5, 15.5, 5.5), (9.5, 18.5, 10.5), 9),
                    ((6.5, 14.5, 6.5), (9.5, 19.5, 9.5), 4)):
        w, h, d = t[0] - f[0], t[1] - f[1], t[2] - f[2]
        E.append(el(f, t, {
            'north': ('#orb', [o, 0, o + w, h]), 'south': ('#orb', [11 - w, 11, 11, 11 + h]),
            'west': ('#orb', [0, o, d, o + h]), 'east': ('#orb', [16 - d, 11 - h, 16, 11]),
            'up': ('#orb', [o, 11, o + w, 11 + d]), 'down': ('#orb', [11, o, 11 + w, o + d])},
            name='void_orb', light=15))
    E.append(el((7.25, 16.25, 7.25), (8.75, 17.75, 8.75), {'all': ('#orb', [7, 7, 8.5, 8.5])}, name='orb_core',
                light=15))
    model('void_infuser', tx, E)


# ===================================================================== ASCENSION ALTAR
MARB = ['#b4afa8', '#cbc7c0', '#ddd9d3', '#e9e6e1', '#f3f1ed', '#fcfbf8']


def marble(seed):
    cv = Canvas()
    noise_fill(cv, MARB[3:6], seed, [0.35, 0.75], cx=3, cy=3, grain=0.08)
    r = rng(seed + 1)
    x, y = int(r.integers(0, 16)), 0
    while y < 16:
        cv.put(x % 16, y, MARB[1])
        if y % 6 == 3:
            cv.put((x + 1) % 16, y, MARB[2])
        x += int(r.integers(-1, 2))
        y += 1
    return cv


@tex('ascension_altar_marble')
def asc_marble():
    """Steps: rows 12-13 upper step side, rows 14-15 lower step side (gold banded)."""
    cv = marble(721)
    for y in (12, 14):
        for x in range(16):
            cv.put(x, y, RADIANT[5] if x % 4 == 1 else RADIANT[4])
        cv.hline(0, 15, y + 1, RADIANT[2])
    return cv


@tex('ascension_altar_body')
def asc_body():
    """Body (rows 5-12): marble with gold corner trim and a prismatic gem inlay."""
    cv = marble(723)
    for y in range(16):
        cv.put(3, y, RADIANT[4])
        cv.put(4, y, MARB[5])
        cv.put(12, y, RADIANT[2])
        cv.put(11, y, MARB[1])
    cv.hline(3, 12, 5, RADIANT[5])
    cv.hline(3, 12, 11, RADIANT[2])
    gem = [
        "..g..",
        ".gcg.",
        "gpWyg",
        ".gvg.",
        "..g..",
    ]
    cv.grid(gem, {'g': RADIANT[4], 'c': PRISM[0], 'p': PRISM[2], 'y': PRISM[3], 'v': PRISM[1], 'W': '#ffffff'}, 6, 6)
    return cv


@tex('ascension_altar_top')
def asc_top():
    """Top slab: rows 0-1 are its sides (gold band); the top has a gold ring."""
    cv = marble(725)
    for x in range(16):
        cv.put(x, 0, RADIANT[5] if x % 4 == 1 else RADIANT[4])
        cv.put(x, 1, RADIANT[2])
    for y in range(2, 16):
        for x in range(16):
            r = math.hypot(x + 0.5 - 8, y + 0.5 - 8)
            if 4.6 < r < 5.6:
                cv.put(x, y, RADIANT[4] if x + y < 16 else RADIANT[3])
            elif 5.6 <= r < 6.1 and x + y >= 16:
                cv.put(x, y, MARB[2])
    return cv


@tex('ascension_altar_halo')
def asc_halo():
    """Prismatic light strip: a hue sweep across u, white-hot centre rows."""
    cv = Canvas()
    hues = ['#ff9ae8', '#c09aff', '#8ab4ff', '#7ff0ff', '#9affb8', '#fff27a', '#ffc27a', '#ff9ae8']
    for x in range(16):
        c = hues[int(x / 16 * (len(hues) - 1) + 0.5)]
        for y in range(16):
            if y in (7, 8):
                cv.put(x, y, mix(c, '#ffffff', 0.7))
            else:
                cv.put(x, y, mix(c, '#ffffff', 0.25 if 4 <= y <= 11 else 0.0))
    return cv


@tex('ascension_altar_gold')
def asc_gold():
    cv = Canvas()
    noise_fill(cv, RADIANT[1:5], 727, grain=0.3)
    cv.hline(0, 15, 0, RADIANT[5])
    return cv


def ascension_altar_model():
    tx = {'particle': T('ascension_altar_body'), 'marble': T('ascension_altar_marble'),
          'body': T('ascension_altar_body'), 'top': T('ascension_altar_top'),
          'halo': T('ascension_altar_halo'), 'gold': T('ascension_altar_gold')}
    E = []
    E.append(el((0, 0, 0), (16, 2, 16), box_faces('#marble', [0, 14, 16, 16], [0, 0, 16, 11]), name='step_lower'))
    E.append(el((1, 2, 1), (15, 4, 15), box_faces('#marble', [1, 12, 15, 14], [1, 0, 15, 11]), name='step_upper'))
    E.append(el((3, 4, 3), (13, 11, 13), box_faces('#body', [3, 5, 13, 12], [3, 3, 13, 13]), name='body'))
    E.append(el((1, 11, 1), (15, 13, 15), box_faces('#top', [1, 0, 15, 2], [1, 1, 15, 15]), name='top'))
    # floating prismatic gem cradled by four gold spires
    E.append(el((6.75, 14.25, 6.75), (9.25, 17.75, 9.25), {
        'north': ('#halo', [2, 4, 4.5, 7.5]), 'west': ('#halo', [5, 4, 7.5, 7.5]),
        'south': ('#halo', [9, 4, 11.5, 7.5]), 'east': ('#halo', [12, 4, 14.5, 7.5]),
        'up': ('#halo', [6, 6, 8.5, 8.5]), 'down': ('#halo', [6, 6, 8.5, 8.5])},
        rotation=rot('y', 45, (8, 16, 8)), name='gem', light=15))
    E.append(el((7.4, 13.5, 7.4), (8.6, 18.5, 8.6), box_faces('#halo', [7, 2, 8.2, 7], [7, 7, 8.2, 8.2]),
                rotation=rot('y', 45, (8, 16, 8)), name='gem_spire', light=15))
    for (x, z) in ((5.5, 5.5), (9.5, 5.5), (5.5, 9.5), (9.5, 9.5)):
        E.append(el((x, 13, z), (x + 1, 15, z + 1), box_faces('#gold', [4, 4, 5, 6], [4, 4, 5, 5]), name='spire'))
        E.append(el((x + 0.25, 15, z + 0.25), (x + 0.75, 15.75, z + 0.75), box_faces('#gold', [2, 0, 2.5, 0.75],
                                                                                     [2, 0, 2.5, 0.5]),
                    name='spire_tip'))
    a = 4.25
    s = 2 * a * math.tan(math.radians(22.5))
    y0, y1 = 19, 19.75
    bars = [((8 - s / 2, y0, 8 - a - 0.5), (8 + s / 2, y1, 8 - a + 0.5), None, 0),
            ((8 - s / 2, y0, 8 + a - 0.5), (8 + s / 2, y1, 8 + a + 0.5), None, 8),
            ((8 - a - 0.5, y0, 8 - s / 2), (8 - a + 0.5, y1, 8 + s / 2), None, 12),
            ((8 + a - 0.5, y0, 8 - s / 2), (8 + a + 0.5, y1, 8 + s / 2), None, 4)]
    dd = a / math.sqrt(2)
    for (sx, sz, ang, u) in ((-1, -1, 45, 14), (1, -1, -45, 2), (-1, 1, -45, 10), (1, 1, 45, 6)):
        cx, cz = 8 + sx * dd, 8 + sz * dd
        bars.append(((cx - s / 2, y0, cz - 0.5), (cx + s / 2, y1, cz + 0.5), rot('y', ang, (cx, 19.4, cz)), u))
    for f, t, r, u in bars:
        u = min(u, 16 - 4)
        E.append(el(f, t, box_faces('#halo', [u, 6, u + 3.5, 6.75], [u, 6, u + 3.5, 7]), rotation=r,
                    name='halo', light=15))
    model('ascension_altar', tx, E)


# ===================================================================== QUEST BOARD
WOOD = ['#2a1a0e', '#3a2414', '#4a301a', '#5c3c22', '#6e4a2a', '#825a34', '#966a3e']
CORK = ['#7a5430', '#8e643a', '#a27446', '#b48452', '#c29460']


@tex('quest_board_wood')
def qb_wood():
    cv = Canvas()
    for x in range(16):
        base = 3 + (x // 4) % 2
        for y in range(16):
            cv.put(x, y, WOOD[base])
    r = rng(731)
    for _ in range(14):
        x, y = int(r.integers(0, 16)), int(r.integers(0, 16))
        for i in range(int(r.integers(2, 5))):
            cv.put(x, (y + i) % 16, WOOD[2] if r.random() < 0.6 else WOOD[5])
    for x in range(0, 16, 4):
        cv.vline(x, 0, 15, WOOD[1])
    cv.hline(0, 15, 0, WOOD[6])
    return cv


@tex('quest_board_cork')
def qb_cork():
    """Board face: cork in a dark wood frame (the frame is the outer 1px of 2..14)."""
    cv = Canvas()
    noise_fill(cv, CORK, 733, [0.2, 0.45, 0.7, 0.9], cx=6, cy=6, grain=0.5)
    r = rng(735)
    for _ in range(18):
        cv.put(int(r.integers(0, 16)), int(r.integers(0, 16)), CORK[0] if r.random() < 0.5 else CORK[4])
    for i in range(16):
        cv.put(i, 1, WOOD[5])
        cv.put(2, i, WOOD[5])
        cv.put(i, 14, WOOD[1])
        cv.put(13, i, WOOD[1])
    return cv


@tex('quest_board_paper')
def qb_paper():
    """Three notes side by side: u0-5 (wanted poster), u5-10 (list), u10-16 (map scrap)."""
    cv = Canvas()
    P = ['#b8a882', '#d6c8a2', '#ece0bc', '#f8f0d8']
    for y in range(16):
        for x in range(16):
            cv.put(x, y, P[2] if (x * 7 + y * 3) % 11 else P[1])
    for x in range(16):
        cv.put(x, 15, P[0])
    # note 1: red seal and title bar
    cv.hline(1, 3, 2, '#5a3a2a')
    for y in (5, 7, 9):
        cv.hline(1, 3, y, '#7a6a5a')
    cv.put(2, 11, '#b02a2a')
    cv.put(3, 11, '#d84a3a')
    cv.put(2, 12, '#8a1a1a')
    # note 2: checklist
    for y in (2, 5, 8, 11):
        cv.put(6, y, '#5a3a2a')
        cv.hline(7, 8, y, '#7a6a5a')
    cv.put(6, 2, '#3a8a3a')
    # note 3: a little star map
    for (x, y) in ((11, 3), (13, 5), (12, 8), (14, 10), (11, 11)):
        cv.put(x, y, '#3a4a8a')
    cv.put(13, 5, '#c89a2a')
    for i in range(10, 16):
        cv.put(i, 0, P[3])
    return cv


@tex('quest_board_star')
def qb_star():
    """Cutout gold star; row 15 holds a solid edge colour."""
    cv = Canvas()
    star = [
        ".......a.......",
        "......aba......",
        "......aba......",
        ".....abWba.....",
        "aaaaabWWWbbbbbc",
        ".abbbWWWWWbbbc.",
        "..abbbWWWbbbc..",
        "...abbbWbbbc...",
        "...abbbbbbbc...",
        "..abbbcccbbbc..",
        "..abbc...cbbc..",
        ".abc.......cbc.",
        ".ac.........cc.",
    ]
    cv.grid(star, {'a': GOLD[5], 'b': GOLD[4], 'c': GOLD[2], 'W': GOLD[6]}, 0, 1)
    cv.hline(0, 15, 15, GOLD[3])
    return cv


@tex('quest_board_pin')
def qb_pin():
    cv = Canvas()
    for y in range(16):
        for x in range(16):
            cv.put(x, y, ['#c83a3a', '#3a6ac8', '#e8b838', '#3a9a5a'][x // 4])
    return cv


def quest_board_model():
    tx = {'particle': T('quest_board_wood'), 'wood': T('quest_board_wood'), 'cork': T('quest_board_cork'),
          'paper': T('quest_board_paper'), 'star': T('quest_board_star'), 'pin': T('quest_board_pin')}
    E = []
    for x0 in (0, 14):
        E.append(el((x0, 0, 13), (x0 + 2, 15, 16), box_faces('#wood', [x0, 1, x0 + 2, 16], [x0, 0, x0 + 2, 3]),
                    name='post'))
    E.append(el((0, 15, 12.5), (16, 16, 16), box_faces('#wood', [0, 0, 16, 1], [0, 0, 16, 3.5]), name='top_beam'))
    E.append(el((2, 1, 13.5), (14, 2, 15.5), box_faces('#wood', [2, 0, 14, 1], [2, 0, 14, 2]), name='bottom_rail'))
    E.append(el((2, 2, 14), (14, 15, 15.5), {
        'north': ('#cork', [2, 1, 14, 14]), 'south': ('#wood', [2, 1, 14, 14]),
        'west': ('#wood', [0, 1, 1.5, 14]), 'east': ('#wood', [0, 1, 1.5, 14]),
        'up': ('#wood', [2, 0, 14, 1.5]), 'down': ('#wood', [2, 0, 14, 1.5])}, name='board'))
    notes = [((3, 8, 13.8), (7.5, 13.5, 14), [0, 1, 4.5, 6.5]),
             ((8, 6.5, 13.8), (12.5, 13, 14), [5, 1, 9.5, 7.5]),
             ((3.5, 3, 13.8), (8, 7, 14), [10.5, 4, 15, 8]),
             ((9, 2.5, 13.8), (12.5, 5.5, 14), [11.5, 9, 15, 12])]
    for f, t, uv in notes:
        w = t[0] - f[0]
        h = t[1] - f[1]
        E.append(el(f, t, {
            'north': ('#paper', uv), 'south': ('#paper', uv),
            'west': ('#paper', [0, 15, 0.2, 15 + 1]), 'east': ('#paper', [0, 15, 0.2, 16]),
            'up': ('#paper', [0, 15, w, 15.2]), 'down': ('#paper', [0, 15, w, 15.2])}, name='note'))
    for (x, y, u) in ((5, 12.75, 0), (10, 12.25, 4), (5.5, 6.25, 8), (10.5, 4.75, 12)):
        E.append(el((x, y, 13.6), (x + 0.6, y + 0.6, 13.8), box_faces('#pin', [u, 0, u + 0.6, 0.6], [u, 0, u + 0.6, 0.6]),
                    name='pin'))
    E.append(el((6.5, 12, 12.3), (9.5, 15, 12.5), {
        'north': ('#star', [0, 1, 15, 14]), 'south': ('#star', [0, 1, 15, 14]),
        'west': ('#star', [0, 0, 0.2, 0.2]), 'east': ('#star', [0, 0, 0.2, 0.2]),
        'up': ('#star', [0, 0, 0.2, 0.2]), 'down': ('#star', [0, 0, 0.2, 0.2])}, name='gold_star'))
    model('quest_board', tx, E, render_type='minecraft:cutout')


MODELS = {'sky_altar': sky_altar_model, 'void_infuser': void_infuser_model,
          'ascension_altar': ascension_altar_model, 'quest_board': quest_board_model}
