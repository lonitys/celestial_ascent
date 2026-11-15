"""Summon altars for the Fallen Stars bosses (same layout as frost_altar.json):
seraph (white quartz + wings), leviathan (amethyst/purpur + serpent coil) and
herald (gold/orange + sun disc)."""
import math

from w2common import *
from w2model import T, el, model, rot
from gen_models import noise_fill, glow_faces

TEX = {}


def tex(name):
    def deco(fn):
        TEX[name] = fn
        return fn
    return deco


QUARTZ = ['#b8b0a6', '#cdc6bc', '#ddd8d0', '#ebe7e0', '#f6f4ef', '#ffffff']
AMETH = ['#3c2470', '#55369a', '#7050b8', '#8c68d2', '#a886ea', '#c8a8fa', '#ead6ff']
ORANGE = ['#6a2a0c', '#963c10', '#c25618', '#e07424', '#f49a3a', '#ffc070']


def step_trims(cv, hi, lo):
    """Rows 12-13 upper-step side, rows 14-15 lower-step side."""
    for y in (12, 14):
        for x in range(16):
            cv.put(x, y, hi[1] if x % 4 else hi[0])
        cv.hline(0, 15, y + 1, lo)


def pillar_edges(cv, lit, dark):
    for y in range(16):
        cv.put(3, y, lit)
        cv.put(12, y, dark)


# ===================================================================== SERAPH
@tex('seraph_altar_base')
def seraph_base():
    cv = Canvas()
    noise_fill(cv, QUARTZ[1:5], 601, [0.25, 0.55, 0.85], grain=0.2)
    # quartz tile seams
    for i in range(16):
        if i % 8 == 0:
            cv.vline(i, 0, 11, QUARTZ[1])
            cv.hline(0, 15, i, QUARTZ[1])
    step_trims(cv, (WGOLD[5], WGOLD[4]), WGOLD[2])
    return cv


@tex('seraph_altar_pillar')
def seraph_pillar():
    cv = Canvas()
    for y in range(16):
        for x in range(16):
            cv.put(x, y, QUARTZ[[4, 3, 3, 2][x % 4]] if 4 <= x <= 11 else QUARTZ[3])
    pillar_edges(cv, QUARTZ[5], QUARTZ[1])
    # carved wings around a small white-gold star
    wing = [
        "a........a",
        ".a......a.",
        ".aa.bb.aa.",
        "..aabbaa..",
        "...a..a...",
    ]
    cv.grid(wing, {'a': WGOLD[4], 'b': WGOLD[5]}, 3, 6)
    cv.put(7, 6, '#ffffff')
    for x in range(16):
        cv.put(x, 4, WGOLD[5] if x % 3 else WGOLD[6])
        cv.put(x, 11, WGOLD[2])
    return cv


@tex('seraph_altar_dish')
def seraph_dish():
    cv = Canvas()
    noise_fill(cv, QUARTZ[2:6], 603, [0.3, 0.6, 0.85], grain=0.2)
    for x in range(16):
        cv.put(x, 1, WGOLD[5] if x % 4 else WGOLD[6])
        cv.put(x, 2, WGOLD[3])
    cv.hline(0, 15, 3, QUARTZ[1])
    return cv


@tex('seraph_altar_inner')
def seraph_inner():
    cv = Canvas()
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            k = 5 if d < 1.6 else 4 if d < 3.2 else 3 if d < 4.8 else 2
            cv.put(x, y, ['#c8a85a', '#e0c478', '#f2dc9a', '#fff0c8', '#fffae8', '#ffffff'][k])
    for a in range(8):
        ang = a * math.pi / 4
        for rr in (5.5, 6.5):
            cv.put(int(7.5 + math.cos(ang) * rr + 0.5), int(7.5 + math.sin(ang) * rr + 0.5), '#fff6dc')
    return cv


@tex('seraph_altar_wing')
def seraph_wing():
    """Cutout feathers in rows 6-15. Left half: a raised wing with its root on the
    right (tip up-left); right half: its mirror. Rows 1-5 stay transparent (used by
    the thin edge faces so the planes have no visible frame)."""
    half = [
        "W.......",
        "WW......",
        "LWW.....",
        "LLWW....",
        "LLLWWW..",
        "MLLLLLWY",
        "MMLLLLLY",
        ".MMMLLLL",
        "..M.MMLL",
        "....M.MM",
    ]
    pal = {'W': '#ffffff', 'L': '#e8edf6', 'M': '#bcc8e0', 'Y': '#fff2c8'}
    cv = Canvas()
    for j, row in enumerate(half):
        for i, ch in enumerate(row):
            if ch in pal:
                cv.put(i, 6 + j, pal[ch])
                cv.put(15 - i, 6 + j, pal[ch])
    cv.hline(0, 15, 0, '#d4dcec')
    return cv


@tex('seraph_altar_orb')
def seraph_orb():
    cv = Canvas()
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5) / 8
            cv.put(x, y, mix('#ffffff', '#ffe9a8', min(1, d * 1.3)))
    for i in range(16):
        cv.put(i, 15, WGOLD[4])
    return cv


def seraph_emblem():
    E = []
    w = '#wing'
    clear = (w, [0, 2, 0.5, 3])
    for (x0, x1, ang, ox) in ((8.25, 15.75, -22.5, 8.25), (0.25, 7.75, 22.5, 7.75)):
        E.append(el((x0, 15.5, 7.75), (x1, 25.5, 8.25), {
            'north': (w, [16 - x1, 6, 16 - x0, 16]), 'south': (w, [x0, 6, x1, 16]),
            'west': clear, 'east': clear, 'up': clear, 'down': clear},
            rotation=rot('y', ang, (ox, 20, 8)), name='wing'))
    E.append(el((7, 18, 7), (9, 20, 9), {'all': ('#orb', [4, 4, 6, 6])}, name='orb', light=15))
    E.append(el((7.5, 17.25, 7.5), (8.5, 20.75, 8.5), {'all': ('#orb', [6, 2, 7, 5.5])}, name='orb_flare', light=15))
    for f, t in (((6, 22.5, 6), (10, 23, 6.75)), ((6, 22.5, 9.25), (10, 23, 10)),
                 ((6, 22.5, 6.75), (6.75, 23, 9.25)), ((9.25, 22.5, 6.75), (10, 23, 9.25))):
        E.append(el(f, t, {'all': ('#orb', [0, 15, 4, 16])}, name='halo', light=15))
    return E


# ===================================================================== LEVIATHAN
@tex('leviathan_altar_base')
def leviathan_base():
    cv = Canvas()
    noise_fill(cv, PURPUR[2:6], 611, [0.25, 0.55, 0.85], grain=0.22)
    for y in range(16):
        for x in range(16):
            if x % 8 == 7 or y % 8 == 7:
                cv.put(x, y, PURPUR[2])
            elif x % 8 == 0 or y % 8 == 0:
                cv.put(x, y, PURPUR[6])
    step_trims(cv, (AMETH[6], AMETH[5]), AMETH[1])
    return cv


@tex('leviathan_altar_pillar')
def leviathan_pillar():
    """Polished amethyst between purpur bands with a coiled serpent inlay."""
    cv = Canvas()
    noise_fill(cv, AMETH[3:6], 613, [0.4, 0.75], cx=3, cy=6, grain=0.15)
    for x in range(4, 12):
        cv.put(x, 5, AMETH[5])
    pillar_edges(cv, AMETH[6], AMETH[1])
    for y in (4, 11):
        cv.hline(0, 15, y, PURPUR[6] if y == 4 else PURPUR[2])
    coil = [
        "..sss...",
        ".s...s..",
        ".s.ss.h.",
        "..s..s..",
        "...ss...",
    ]
    cv.grid(coil, {'s': '#f4dcff', 'h': MAGENTA[4]}, 4, 5)
    return cv


@tex('leviathan_altar_dish')
def leviathan_dish():
    cv = Canvas()
    noise_fill(cv, PURPUR[2:6], 615, [0.3, 0.6, 0.85], grain=0.2)
    for x in range(16):
        cv.put(x, 1, AMETH[6] if x % 4 else '#ffffff')
        cv.put(x, 2, AMETH[4])
    cv.hline(0, 15, 3, PURPUR[1])
    return cv


@tex('leviathan_altar_inner')
def leviathan_inner():
    cv = Canvas()
    for y in range(16):
        for x in range(16):
            a = math.atan2(y - 7.5, x - 7.5)
            r = math.hypot(x - 7.5, y - 7.5)
            v = math.sin(a * 2 - r * 0.8)
            cv.put(x, y, '#9a6ae8' if v > 0.5 else '#6a3cc0' if v > -0.2 else '#3e1c88')
    for (x, y) in ((7, 7), (8, 8), (4, 10), (11, 4), (10, 11)):
        cv.put(x, y, '#ffd6f4')
    return cv


@tex('leviathan_altar_scales')
def leviathan_scales():
    """Serpent body: amethyst scales (rows 0-9), pale belly (10-11), glowing orb
    (12-13), eyes (14-15)."""
    cv = Canvas()
    for y in range(10):
        for x in range(16):
            lx = (x + (1 if (y // 2) % 2 else 0)) % 2
            cv.put(x, y, AMETH[5] if (lx == 0 and y % 2 == 0) else AMETH[4] if y % 2 == 0 else AMETH[3])
    cv.hline(0, 15, 10, '#f0d8ff')
    cv.hline(0, 15, 11, '#d0aaf4')
    for x in range(16):
        cv.put(x, 12, '#ffffff' if x % 5 == 2 else '#e8c8ff')
        cv.put(x, 13, '#c89aff')
    cv.hline(0, 15, 14, MAGENTA[5])
    cv.hline(0, 15, 15, MAGENTA[3])
    return cv


def leviathan_emblem():
    """A serpent coiled around a glowing amethyst orb, rising to a raised head
    that faces north."""
    E = []
    s = '#scales'
    E.append(el((7, 16.25, 7), (9, 18.25, 9), {'all': (s, [2, 12, 4, 14])}, name='orb', light=15))
    E.append(el((7.5, 15.75, 7.5), (8.5, 18.75, 8.5), {'all': (s, [6, 12, 7, 14])}, name='orb_flare', light=15))
    n, R, turns = 20, 3.7, 1.3
    th_end = -math.pi / 2
    th0 = th_end - turns * 2 * math.pi
    last = None
    for i in range(n):
        t = i / (n - 1)
        th = th0 + t * (th_end - th0)
        x, z = 8 + R * math.cos(th), 8 + R * math.sin(th)
        y = 15.2 + t * 4.2
        Tk = 0.6 + 0.6 * min(1, t * 2.5)
        phi = math.degrees(th) + 90
        E.append(_seg(x, y, z, phi, 1.9, Tk, s, (i * 3) % 12))
        last = (x, y, z, Tk)
    x, y, z, Tk = last
    # neck rising forward, then the head
    E.append(el((x - 0.6, y + 0.4, z - 1.6), (x + 0.6, y + 1.8, z - 0.2), {
        'all': (s, [3, 0, 4.2, 1.4]), 'up': (s, [3, 2, 4.2, 3.4]), 'down': (s, [3, 10, 4.2, 11.4]),
        'west': (s, [5, 0, 6.4, 1.4]), 'east': (s, [5, 0, 6.4, 1.4])}, name='neck'))
    hy = y + 1.4
    E.append(el((x - 1.1, hy, z - 4.2), (x + 1.1, hy + 1.6, z - 1.2), {
        'all': (s, [4, 4, 6.2, 5.6]), 'down': (s, [0, 10, 2.2, 11.6]),
        'up': (s, [4, 2, 6.2, 5]), 'west': (s, [2, 4, 5, 5.6]), 'east': (s, [2, 4, 5, 5.6])},
        name='head'))
    E.append(el((x - 0.8, hy - 0.45, z - 3.9), (x + 0.8, hy, z - 1.5), {
        'all': (s, [8, 4, 9.6, 4.45]), 'up': (s, [0, 15, 1.6, 16]), 'down': (s, [0, 10, 1.6, 12.4]),
        'west': (s, [8, 4, 10.4, 4.45]), 'east': (s, [8, 4, 10.4, 4.45])}, name='jaw'))
    for x0 in (x - 1.2, x + 1.1):
        E.append(el((x0, hy + 0.8, z - 3.4), (x0 + 0.1, hy + 1.3, z - 2.5), {'all': (s, [0, 14, 0.9, 14.5])},
                    name='eye', light=15))
    for dz, h in ((-2.4, 0.8), (-1.4, 1.1)):
        E.append(el((x - 0.12, hy + 1.6, z + dz), (x + 0.12, hy + 1.6 + h, z + dz + 0.9), {
            'all': (s, [8, 0, 9, 1])}, name='fin'))
    return E


# ===================================================================== HERALD
@tex('herald_altar_base')
def herald_base():
    cv = Canvas()
    noise_fill(cv, ORANGE[1:5], 621, [0.25, 0.55, 0.85], grain=0.22)
    for y in range(0, 12, 4):
        cv.hline(0, 15, y + 3, ORANGE[0])
        for x in range(0 if (y // 4) % 2 == 0 else 4, 16, 8):
            cv.vline(x, y, y + 2, ORANGE[0])
    step_trims(cv, (GOLD[6], GOLD[5]), GOLD[2])
    return cv


@tex('herald_altar_pillar')
def herald_pillar():
    cv = Canvas()
    noise_fill(cv, [GOLD[2], GOLD[3], GOLD[4], GOLD[5]], 623, [0.3, 0.55, 0.8], cx=3, cy=6, grain=0.25)
    pillar_edges(cv, GOLD[6], GOLD[1])
    for y in (4, 11):
        cv.hline(0, 15, y, ORANGE[4] if y == 4 else ORANGE[1])
    sun = [
        "..o.o..",
        ".o.y.o.",
        "o.yYy.o",
        ".yYWYy.",
        "o.yYy.o",
        ".o.y.o.",
        "..o.o..",
    ]
    cv.grid(sun, {'o': ORANGE[3], 'y': ORANGE[5], 'Y': '#fff2b0', 'W': '#ffffff'}, 5, 5)
    return cv


@tex('herald_altar_dish')
def herald_dish():
    cv = Canvas()
    noise_fill(cv, ORANGE[1:5], 625, [0.3, 0.6, 0.85], grain=0.2)
    for x in range(16):
        cv.put(x, 1, GOLD[5] if x % 4 else GOLD[6])
        cv.put(x, 2, GOLD[3])
    cv.hline(0, 15, 3, ORANGE[0])
    return cv


@tex('herald_altar_inner')
def herald_inner():
    cv = Canvas()
    for y in range(16):
        for x in range(16):
            v = math.sin(x * 0.8 + math.sin(y * 0.7) * 2) + math.cos(y * 0.9 - x * 0.3)
            cv.put(x, y, '#fff6c0' if v > 1.2 else '#ffd24a' if v > 0.4 else '#ffa82a' if v > -0.6 else '#f07a1a')
    return cv


@tex('herald_altar_sun')
def herald_sun():
    """Cutout sun disc (10x10 at u/v 3..13) with flame rays; row 15 holds a solid
    rim colour and the corners stay transparent for the thin edge faces."""
    cv = Canvas()
    for y in range(3, 13):
        for x in range(3, 13):
            dx, dy = x + 0.5 - 8, y + 0.5 - 8
            r = math.hypot(dx, dy)
            a = math.atan2(dy, dx)
            ray = 3.9 + 1.3 * max(0, math.cos(a * 8)) ** 3
            if r <= 3.0:
                c = '#ffffff' if r < 1.1 else '#fff2b0' if r < 2.0 else '#ffd24a'
            elif r <= ray:
                c = '#f07a1a' if r > ray - 0.9 else '#ffb43a'
            else:
                continue
            cv.put(x, y, c)
    cv.hline(0, 15, 15, '#ffa82a')
    return cv


def herald_emblem():
    E = []
    clear = ('#sun', [0, 0, 0.5, 0.5])
    E.append(el((3, 15.5, 7.75), (13, 25.5, 8.25), {
        'north': ('#sun', [3, 3, 13, 13]), 'south': ('#sun', [3, 3, 13, 13]),
        'west': clear, 'east': clear, 'up': clear, 'down': clear}, name='sun_disc', light=15))
    return E


# ===================================================================== shared layout
def altar_model(name, emblem, extra, render_type=None, inner_glow=True):
    tx = {'particle': T(f'{name}_pillar'), 'base': T(f'{name}_base'), 'pillar': T(f'{name}_pillar'),
          'dish': T(f'{name}_dish'), 'inner': T(f'{name}_inner')}
    tx.update({k: T(f'{name}_{k}') for k in extra})
    E = []
    # step tops sample rows 0-10 so the side trims (rows 12-15) never show on top
    E.append(el((0, 0, 0), (16, 2, 16), {
        'all': ('#base', [0, 14, 16, 16]), 'up': ('#base', [0, 0, 16, 11]), 'down': ('#base', [0, 0, 16, 11])},
        name='step_lower'))
    E.append(el((1, 2, 1), (15, 4, 15), {
        'all': ('#base', [1, 12, 15, 14]), 'up': ('#base', [1, 0, 15, 11]), 'down': ('#base', [1, 0, 15, 11])},
        name='step_upper'))
    E.append(el((3, 4, 3), (13, 12, 13), {
        'all': ('#pillar', [3, 4, 13, 12]), 'up': ('#pillar', [3, 3, 13, 13]), 'down': ('#pillar', [3, 3, 13, 13])},
        name='pillar'))
    E.append(el((1, 12, 1), (15, 13, 15), {
        'all': ('#dish', [1, 3, 15, 4]), 'down': ('#dish', [1, 1, 15, 15]), 'up': ('#inner', [1, 1, 15, 15])},
        name='dish_floor'))
    if inner_glow:
        glow_faces(E[-1], ['up'])
    rim = [((1, 13, 1), (15, 15, 3)), ((1, 13, 13), (15, 15, 15)), ((1, 13, 3), (3, 15, 13)), ((13, 13, 3), (15, 15, 13))]
    for f, t in rim:
        E.append(el(f, t, {
            'up': ('#dish', [f[0], f[2], t[0], t[2]]), 'down': ('#dish', [f[0], f[2], t[0], t[2]]),
            'north': ('#dish', [16 - t[0], 1, 16 - f[0], 3]), 'south': ('#dish', [f[0], 1, t[0], 3]),
            'west': ('#dish', [f[2], 1, t[2], 3]), 'east': ('#dish', [16 - t[2], 1, 16 - f[2], 3])}, name='dish_rim'))
    E.extend(emblem())
    model(name, tx, E, render_type=render_type)


def _seg(x, y, z, phi_deg, L, Tk, tex_ref, u, name='coil'):
    """Box of length L along direction phi (degrees, atan2(dz, dx)), snapped to the
    allowed 22.5-degree element rotations."""
    d = phi_deg % 180
    if d <= 45:
        axis, a = 'x', -d
    elif d >= 135:
        axis, a = 'x', 180 - d
    else:
        axis, a = 'z', 90 - d
    a = max(-45, min(45, round(a / 22.5) * 22.5))
    if axis == 'x':
        f, t = (x - L / 2, y, z - Tk / 2), (x + L / 2, y + Tk, z + Tk / 2)
        lw, ld = L, Tk
    else:
        f, t = (x - Tk / 2, y, z - L / 2), (x + Tk / 2, y + Tk, z + L / 2)
        lw, ld = Tk, L
    faces = {
        'north': (tex_ref, [u, 0, u + lw, Tk]), 'south': (tex_ref, [u, 0, u + lw, Tk]),
        'west': (tex_ref, [u, 0, u + ld, Tk]), 'east': (tex_ref, [u, 0, u + ld, Tk]),
        'up': (tex_ref, [u, 2, u + lw, 2 + ld]), 'down': (tex_ref, [u, 10, u + lw, 10 + min(ld, 2)])}
    return el(f, t, faces, rotation=rot('y', a, (x, y, z)) if a else None, name=name)


MODELS = {
    'seraph_altar': lambda: altar_model('seraph_altar', seraph_emblem, ['wing', 'orb'], render_type='minecraft:cutout'),
    'leviathan_altar': lambda: altar_model('leviathan_altar', leviathan_emblem, ['scales']),
    'herald_altar': lambda: altar_model('herald_altar', herald_emblem, ['sun'], render_type='minecraft:cutout'),
}
