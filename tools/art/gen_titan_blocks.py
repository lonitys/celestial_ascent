"""Titan Forge and the four shrine altars (frost, tide, storm, magma).

Models are authored facing NORTH (front = -Z).
"""
from common import *
from materials import *
from blockmodel import el, rot, model, T, emissive

S = STEEL


def glow(spec):
    """Turn ('#tex', uv) into an emissive face dict."""
    tex, uv = spec[0], spec[1]
    return emissive({'uv': uv, 'texture': tex})


# ======================================================================
# TITAN FORGE
# ======================================================================
FORGE_STONE = ['#16171c', '#1e2026', '#272930', '#30333b', '#3a3d46', '#464a54', '#565b66']


def forge_bricks(cv, y0, y1, seed):
    """Dark forge-stone bricks (8x4 running bond) between rows y0..y1."""
    r = rng(seed)
    for y in range(y0, y1 + 1):
        for x in range(16):
            cv.put(x, y, FORGE_STONE[3])
    for y in range(y0, y1 + 1):
        row = (y - y0) // 4
        off = 0 if row % 2 == 0 else 4
        ly = (y - y0) % 4
        for x in range(16):
            lx = (x + off) % 8
            if ly == 3 or lx == 7:
                cv.put(x, y, FORGE_STONE[1])
            elif ly == 0 or lx == 0:
                cv.put(x, y, FORGE_STONE[4])
            elif r.random() < 0.12:
                cv.put(x, y, FORGE_STONE[2])


def gem_row(cv, x, y):
    """Four tiny element gems set in a gold strip (8 px wide)."""
    cols = [('#9ff4ff', '#2aa9c4'), ('#7aa6ff', '#2c4fd0'), ('#fff07a', '#c08a12'), ('#ffb05a', '#b8420f')]
    cv.hline(x, x + 8, y, GOLD[3])
    cv.hline(x, x + 8, y + 1, GOLD[2])
    for i, (hi, lo) in enumerate(cols):
        cv.put(x + 1 + i * 2, y, hi)
        cv.put(x + 1 + i * 2, y + 1, lo)


def forge_front():
    """Front face. Opening is u4..12 v7..13 (x4-12, y3-9)."""
    cv = Canvas()
    forge_bricks(cv, 0, 15, 61)
    # steel pillars either side of the mouth
    for x0 in (0, 12):
        cv.rect(x0, 3, x0 + 3, 15, S[3])
        cv.vline(x0, 3, 15, S[5])
        cv.vline(x0 + 3, 3, 15, S[1])
        for y in (5, 9, 13):
            cv.put(x0 + 1, y, S[7])
            cv.put(x0 + 2, y + 1, S[0])
    # lintel with element gems
    cv.rect(3, 3, 12, 6, S[2])
    cv.hline(3, 12, 3, S[5])
    gem_row(cv, 4, 4)
    # gold rim around the mouth
    cv.hline(3, 12, 6, GOLD[4])
    cv.hline(3, 12, 13, GOLD[2])
    cv.vline(3, 6, 13, GOLD[4])
    cv.vline(12, 6, 13, GOLD[2])
    cv.put(3, 6, GOLD[5])
    # mouth (only seen in the particle / item view)
    for y in range(7, 13):
        for x in range(4, 12):
            d = abs(x - 7.5) + abs(y - 10.5) * 1.2
            cv.put(x, y, LAVA[6] if d < 1.5 else LAVA[5] if d < 3 else LAVA[4] if d < 4.5 else LAVA[3])
    # plinth
    cv.rect(0, 13, 15, 15, S[2])
    cv.hline(0, 15, 13, GOLD[3])
    cv.hline(0, 15, 15, S[0])
    for x in (1, 5, 10, 14):
        cv.put(x, 14, S[6])
    # top band (y13-16 not used by the body, used by deck sides)
    cv.rect(0, 0, 15, 2, S[3])
    cv.hline(0, 15, 0, S[5])
    cv.hline(0, 15, 2, S[1])
    return cv


def forge_side():
    cv = Canvas()
    forge_bricks(cv, 0, 15, 63)
    # steel band with rivets and a glowing vent
    cv.rect(0, 7, 15, 10, S[3])
    cv.hline(0, 15, 7, S[5])
    cv.hline(0, 15, 10, S[1])
    for x in range(5, 11):
        cv.put(x, 8, '#1a0c06')
        cv.put(x, 9, LAVA[3] if x % 2 else LAVA[2])
    for x in (1, 14):
        cv.put(x, 8, S[7])
        cv.put(x, 9, S[1])
    # corner steel posts
    cv.vline(0, 3, 15, S[4])
    cv.vline(15, 3, 15, S[1])
    # gold cap line + plinth
    cv.hline(0, 15, 3, GOLD[3])
    cv.rect(0, 13, 15, 15, S[2])
    cv.hline(0, 15, 13, S[4])
    cv.hline(0, 15, 15, S[0])
    cv.rect(0, 0, 15, 2, S[3])
    cv.hline(0, 15, 0, S[5])
    cv.hline(0, 15, 2, S[1])
    return cv


def forge_top():
    cv = Canvas()
    cv.rect(0, 0, 15, 15, S[3])
    for i in range(16):
        cv.put(i, 0, S[5])
        cv.put(0, i, S[5])
        cv.put(i, 15, S[1])
        cv.put(15, i, S[1])
    for x, y in ((1, 1), (14, 1), (1, 14), (14, 14), (7, 1), (1, 7)):
        cv.put(x, y, S[6])
    return cv


def forge_deck():
    """Deck top: steel grate over the furnace glow (uv 2..14), deck sides on rows 0-1."""
    cv = Canvas()
    cv.rect(0, 0, 15, 15, S[4])
    bevel(cv, 2, 2, 13, 13, S[6], S[1])
    for y in range(3, 13):
        for x in range(3, 13):
            if y % 2 == 0:
                cv.put(x, y, S[2])
            else:
                d = abs(x - 7.5) + abs(y - 7.5)
                cv.put(x, y, LAVA[5] if d < 3 else LAVA[4] if d < 5 else LAVA[3])
    for x in (3, 12):
        cv.vline(x, 3, 12, S[3])
    gem_row(cv, 4, 0)
    return cv


def forge_crucible():
    """Glowing interior: back wall (rows 0-7), molten pool (rows 8-11), heated lip (rows 12-15)."""
    cv = Canvas()
    for y in range(8):
        for x in range(16):
            d = abs(x - 7.5) / 8 + (7 - y) / 10
            k = 6 if d < 0.25 else 5 if d < 0.45 else 4 if d < 0.65 else 3
            cv.put(x, y, LAVA[k])
    for x, y in ((3, 5), (11, 4), (6, 2), (12, 6)):
        cv.put(x, y, LAVA[6])
    for y in range(8, 12):
        for x in range(16):
            cv.put(x, y, LAVA[5] if (x + y * 3) % 5 else LAVA[6])
    for y in range(12, 16):
        for x in range(16):
            cv.put(x, y, mix(S[3], LAVA[3], 0.35 + 0.15 * (y - 12)))
    return cv


def forge_crystals():
    """Four 4px bands: frost, tide, storm, magma (light edge -> dark edge)."""
    cv = Canvas()
    bands = [
        ['#e8ffff', '#9ff0ff', '#4fc6e8', '#2a86b0'],
        ['#c8dcff', '#7aa6ff', '#3f6ae0', '#2a3fa8'],
        ['#fffbd0', '#ffe45c', '#e0b020', '#a07010'],
        ['#ffe0a0', '#ffa040', '#e0601a', '#a0300c'],
    ]
    for b, pal in enumerate(bands):
        for y in range(16):
            for i in range(4):
                t = i if y > 3 else max(0, i - 1)
                cv.put(b * 4 + i, y, pal[t])
        cv.put(b * 4, 1, '#ffffff')
    return cv


def forge_gold():
    cv = Canvas()
    noise_region(cv, 0, 0, 15, 15, GOLD[2:6], 65, cells=4, contrast=1.2)
    for i in range(16):
        cv.put(i, 0, GOLD[5])
        cv.put(i, 15, GOLD[1])
    for x, y in ((2, 2), (9, 5), (5, 11)):
        cv.put(x, y, GOLD[6])
    return cv


def titan_forge_model():
    tex = {'particle': T('titan_forge_front'), 'front': T('titan_forge_front'), 'side': T('titan_forge_side'),
           'top': T('titan_forge_top'), 'deck': T('titan_forge_deck'), 'crucible': T('titan_forge_crucible'),
           'crystal': T('titan_forge_crystals'), 'gold': T('titan_forge_gold')}
    E = []
    # main body (its north face is the glowing back wall of the mouth)
    E.append(el((0, 0, 2), (16, 13, 16), {
        'down': ('#top', [0, 0, 16, 14]), 'up': ('#top', [0, 2, 16, 16]),
        'north': glow(('#crucible', [0, 0, 16, 8])),
        'south': ('#side', [0, 3, 16, 16]), 'west': ('#side', [2, 3, 16, 16]), 'east': ('#side', [0, 3, 14, 16]),
    }, name='body'))
    # front frame around the mouth (z0-2)
    lip = ('#crucible', [0, 12, 2, 16])
    E.append(el((0, 0, 0), (4, 13, 2), {
        'north': '#front', 'west': ('#side', [0, 3, 2, 16]), 'up': '#top', 'down': '#top',
        'east': ('#crucible', [0, 12, 2, 15]),
    }, name='frame_left'))
    E.append(el((12, 0, 0), (16, 13, 2), {
        'north': '#front', 'east': ('#side', [14, 3, 16, 16]), 'up': '#top', 'down': '#top',
        'west': ('#crucible', [0, 12, 2, 15]),
    }, name='frame_right'))
    E.append(el((4, 0, 0), (12, 3, 2), {
        'north': '#front', 'down': '#top',
        'up': glow(('#crucible', [4, 8, 12, 10])),
    }, name='frame_sill'))
    E.append(el((4, 9, 0), (12, 13, 2), {
        'north': '#front', 'up': '#top',
        'down': ('#crucible', [4, 12, 12, 14]),
    }, name='frame_lintel'))
    # raised deck with furnace grate
    E.append(el((2, 13, 2), (14, 15, 14), {
        'up': glow(('#deck', [2, 2, 14, 14])),
        'north': ('#front', [2, 0, 14, 2]), 'south': ('#side', [2, 0, 14, 2]),
        'west': ('#side', [2, 0, 14, 2]), 'east': ('#side', [2, 0, 14, 2]),
    }, name='deck'))
    # gold sockets + element crystals on the four top corners
    corners = [((0, 0), 0), ((13, 0), 8), ((0, 13), 4), ((13, 13), 12)]  # frost, storm, tide, magma
    for (x0, z0), band in corners:
        E.append(el((x0, 13, z0), (x0 + 3, 14, z0 + 3), {
            'up': ('#gold', [0, 0, 3, 3]), 'north': ('#gold', [0, 0, 3, 1]), 'south': ('#gold', [3, 0, 6, 1]),
            'west': ('#gold', [6, 0, 9, 1]), 'east': ('#gold', [9, 0, 12, 1])}, name='socket'))
        cx, cz = x0 + 1.5, z0 + 1.5
        b = band
        tilt = 22.5 if x0 < 8 else -22.5          # lean away from the block centre
        cr = rot('z', tilt, (cx, 14, cz))
        E.append(el((cx - 1, 14, cz - 1), (cx + 1, 18.5, cz + 1), {
            'west': glow(('#crystal', [b, 0, b + 2, 16])),
            'north': glow(('#crystal', [b + 1, 0, b + 3, 16])),
            'east': glow(('#crystal', [b + 2, 0, b + 4, 16])),
            'south': glow(('#crystal', [b + 1, 0, b + 3, 16])),
            'up': glow(('#crystal', [b, 0, b + 2, 2]))}, rotation=cr, name='crystal'))
    model('titan_forge', tex, E)


# ======================================================================
# ALTARS
# ======================================================================
def ice_tex(pal, seed, cracks=True):
    cv = Canvas()
    noise_region(cv, 0, 0, 15, 15, pal[1:6], seed, cells=2, octaves=2, contrast=1.1)
    if cracks:
        r = rng(seed + 1)
        for _ in range(3):
            x, y = int(r.integers(0, 16)), int(r.integers(0, 16))
            for i in range(4):
                cv.put((x + i) % 16, (y + i // 2) % 16, pal[6])
    return cv


def stepped_base_tex(fill_fn, trim_hi, trim_lo, top_rows=(12, 14)):
    """Base atlas: rows 12-13 upper step side, rows 14-15 lower step side; whole
    texture doubles as the step tops."""
    cv = fill_fn()
    for y in top_rows:
        cv.hline(0, 15, y, trim_hi)
        cv.hline(0, 15, y + 1, trim_lo)
    return cv


ALTARS = {}


def altar(name):
    def deco(fn):
        ALTARS[name] = fn
        return fn
    return deco


# ---------------------------------------------------------------- frost
@altar('frost_altar')
def frost_textures():
    t = {}
    base = ice_tex(PACKED_ICE, 71)
    for y, (hi, lo) in ((12, (PACKED_ICE[6], PACKED_ICE[2])), (14, (PACKED_ICE[5], PACKED_ICE[1]))):
        cv = base
        cv.hline(0, 15, y, hi)
        cv.hline(0, 15, y + 1, lo)
        cv.hline(0, 15, y + 1, lo)
    for x in range(0, 16, 4):
        base.put(x + 1, 15, PACKED_ICE[0])
    t['base'] = base
    # pillar: blue ice with a carved snowflake
    p = ice_tex(BLUE_ICE, 73, cracks=False)
    for y in range(16):
        p.put(3, y, BLUE_ICE[5])
        p.put(12, y, BLUE_ICE[1])
    flake = ["..w..", "w.w.w", ".www.", "wwWww", ".www.", "w.w.w", "..w.."]
    p.grid(flake, {'w': '#e0f4ff', 'W': '#ffffff'}, 6, 5)
    p.hline(0, 15, 4, BLUE_ICE[6])
    p.hline(0, 15, 11, BLUE_ICE[1])
    t['pillar'] = p
    # dish: packed ice with a frosty white rim
    d = ice_tex(PACKED_ICE, 75)
    d.hline(0, 15, 1, '#f4fbff')
    d.hline(0, 15, 2, PACKED_ICE[3])
    d.hline(0, 15, 3, PACKED_ICE[1])
    t['dish'] = d
    # inner: frozen surface with radial cracks
    i = Canvas(fill=PACKED_ICE[5])
    noise_region(i, 3, 3, 12, 12, ['#cfe4ff', '#e2efff', '#f4f9ff'], 77, cells=2)
    for x, y in ((7, 7), (8, 8), (6, 6), (5, 5), (9, 7), (10, 6), (8, 9), (8, 10), (6, 9), (5, 10)):
        i.put(x, y, '#9fc4f4')
    i.put(7, 8, '#ffffff')
    t['inner'] = i
    # crystal
    c = Canvas()
    pal = ['#2f7fd0', '#56b4ee', '#9fe2ff', '#dcfaff', '#ffffff']
    for y in range(16):
        for x in range(16):
            k = 3 - x // 4 + (1 if y < 3 else 0)
            c.put(x, y, pal[max(0, min(4, k))])
        c.put(1, y, '#ffffff' if y < 10 else pal[3])
    t['crystal'] = c
    return t


# ---------------------------------------------------------------- tide
@altar('tide_altar')
def tide_textures():
    t = {}
    b = Canvas()
    noise_region(b, 0, 0, 15, 15, DARK_PRISMARINE[1:6], 81, cells=4, contrast=1.2)
    for y in (12, 14):
        for x in range(16):
            b.put(x, y, GOLD[4] if x % 4 else GOLD[5])
        b.hline(0, 15, y + 1, DARK_PRISMARINE[0])
    t['base'] = b
    p = Canvas()
    noise_region(p, 0, 0, 15, 15, PRISMARINE[1:6], 83, cells=4, octaves=2, contrast=1.3)
    for y in range(16):
        p.put(3, y, PRISMARINE[6])
        p.put(12, y, PRISMARINE[0])
    for x in range(16):
        p.put(x, 7, GOLD[5] if x % 3 == 0 else GOLD[4])
        p.put(x, 8, GOLD[2])
    # trident inlay below the band
    p.grid(["g.g.g", "ggggg", "..g.."], {'g': GOLD[4]}, 6, 3)
    p.hline(0, 15, 4, PRISMARINE[6])
    p.hline(0, 15, 11, PRISMARINE[0])
    t['pillar'] = p
    d = Canvas()
    # prismarine bricks
    noise_region(d, 0, 0, 15, 15, PRISMARINE[2:6], 85, cells=4, contrast=1.1)
    for y in range(0, 16, 4):
        d.hline(0, 15, y, PRISMARINE[0])
        off = 0 if (y // 4) % 2 == 0 else 4
        for x in range(off, 16, 8):
            d.vline(x, y, y + 3, PRISMARINE[0])
    d.hline(0, 15, 1, GOLD[5])
    d.hline(0, 15, 2, GOLD[3])
    d.hline(0, 15, 3, PRISMARINE[1])
    t['dish'] = d
    i = Canvas(fill='#1f5fb8')
    for y in range(16):
        for x in range(16):
            w = math.sin((x + y * 0.5) * 0.9) + math.sin(y * 1.3 - x * 0.4)
            i.put(x, y, '#3a8ae0' if w > 1.0 else '#2a74d0' if w > 0 else '#1f5fb8')
    for x, y in ((5, 6), (6, 6), (9, 9), (10, 9), (7, 11)):
        i.put(x, y, '#a8e8ff')
    t['inner'] = i
    c = Canvas()
    pal = ['#0b5a86', '#1489a8', '#2ebfc4', '#7ef0de', '#e6fff8']
    for y in range(16):
        for x in range(16):
            k = 3 - x // 4 + (1 if y < 4 else 0)
            c.put(x, y, pal[max(0, min(4, k))])
    for x, y in ((1, 1), (2, 1), (1, 2), (5, 6), (9, 3), (13, 10)):
        c.put(x, y, '#ffffff')
    for x, y in ((6, 9), (7, 10), (10, 7), (3, 12)):
        c.put(x, y, '#c8fff4')
    t['crystal'] = c
    return t


# ---------------------------------------------------------------- storm
@altar('storm_altar')
def storm_textures():
    t = {}
    b = Canvas()
    # deepslate tiles
    noise_region(b, 0, 0, 15, 15, DEEPSLATE[1:5], 91, cells=4, contrast=1.1)
    for y in range(0, 16, 4):
        b.hline(0, 15, y + 3, DEEPSLATE[0])
        for x in range(0 if (y // 4) % 2 == 0 else 4, 16, 8):
            b.vline(x, y, y + 3, DEEPSLATE[0])
    for y in (12, 14):
        for x in range(16):
            b.put(x, y, COPPER[4] if x % 4 else COPPER[5])
        b.hline(0, 15, y + 1, DEEPSLATE[0])
    t['base'] = b
    p = Canvas()
    noise_region(p, 0, 0, 15, 15, CALCITE[2:6], 93, cells=4, octaves=2, contrast=1.1)
    for y in range(16):
        p.put(3, y, CALCITE[6])
        p.put(12, y, CALCITE[1])
    # copper lightning inlay
    bolt = ["...cc", "..cc.", ".cccc", "..cc.", ".cc..", ".c..."]
    p.grid(bolt, {'c': COPPER[4]}, 6, 5)
    p.put(9, 5, COPPER[6])
    p.put(7, 10, '#3e7a66')     # a fleck of verdigris
    for x in range(16):
        p.put(x, 4, COPPER[5] if x % 3 else COPPER[6])
        p.put(x, 11, COPPER[2])
    t['pillar'] = p
    d = Canvas()
    noise_region(d, 0, 0, 15, 15, CALCITE[2:6], 95, cells=4, contrast=1.1)
    for x in range(16):
        d.put(x, 1, COPPER[5] if x % 4 else COPPER[6])
        d.put(x, 2, COPPER[3])
    d.hline(0, 15, 3, CALCITE[1])
    for x in (4, 11):
        d.put(x, 2, VERDIGRIS[1])
    t['dish'] = d
    i = Canvas(fill='#3a3658')
    for y in range(16):
        for x in range(16):
            a = math.atan2(y - 7.5, x - 7.5)
            r = math.hypot(x - 7.5, y - 7.5)
            v = math.sin(a * 2 + r * 0.9)
            i.put(x, y, '#5a5480' if v > 0.4 else '#46406a' if v > -0.3 else '#2e2a48')
    for x, y in ((7, 6), (8, 7), (7, 8), (8, 9), (10, 5), (5, 10)):
        i.put(x, y, '#ffe45c')
    i.put(8, 7, '#ffffff')
    t['inner'] = i
    c = Canvas()
    pal = ['#a07010', '#e0b020', '#ffe45c', '#fff6b0', '#ffffff']
    for y in range(16):
        for x in range(16):
            k = 3 - x // 4 + (1 if y < 4 else 0)
            c.put(x, y, pal[max(0, min(4, k))])
    for b in range(4):
        for y, dx in ((2, 2), (3, 1), (4, 1), (5, 2), (6, 2), (7, 1), (8, 2), (9, 2), (10, 1), (11, 1), (12, 2)):
            c.put(b * 4 + dx, y, '#ffffff' if b < 2 else '#fff6b0')
    t['crystal'] = c
    cu = Canvas()
    for y in range(16):
        for x in range(16):
            cu.put(x, y, COPPER[[5, 4, 3, 2][x % 4]])
    for y in range(0, 16, 5):
        cu.put(1, y, COPPER[6])
    cu.put(2, 9, VERDIGRIS[1])
    t['copper'] = cu
    return t


# ---------------------------------------------------------------- magma
@altar('magma_altar')
def magma_textures():
    t = {}
    b = Canvas()
    # basalt: vertical columnar streaks
    for y in range(16):
        for x in range(16):
            col = [3, 4, 2, 3, 5, 3, 2, 4][(x // 2) % 8]
            b.put(x, y, BASALT[col])
    noise = tile_noise(16, 16, 4, 101)
    for y in range(16):
        for x in range(16):
            if noise[y, x] > 0.68:
                b.put(x, y, BASALT[1])
    for y in (12, 14):
        b.hline(0, 15, y, BASALT[6])
        b.hline(0, 15, y + 1, BASALT[0])
    crack_line(b, [(3, 12), (4, 13), (4, 14)], LAVA[3])
    crack_line(b, [(11, 14), (12, 15)], LAVA[3])
    t['base'] = b
    p = Canvas()
    noise_region(p, 0, 0, 15, 15, BLACKSTONE[1:6], 103, cells=4, octaves=2, contrast=1.3)
    for y in range(16):
        p.put(3, y, BLACKSTONE[5])
        p.put(12, y, BLACKSTONE[0])
    crack = [(7, 4), (7, 5), (8, 6), (8, 7), (7, 8), (6, 9), (6, 10), (9, 8), (10, 9), (5, 6)]
    for x, y in crack:
        p.put(x, y, LAVA[4])
    for x, y in ((8, 6), (8, 7), (7, 8)):
        p.put(x, y, LAVA[6])
    for x, y in crack:
        if p.get(x + 1, y)[0] < 100:
            p.put(x + 1, y, LAVA[1])
    p.hline(0, 15, 4, BLACKSTONE[5])
    p.hline(0, 15, 11, BLACKSTONE[0])
    t['pillar'] = p
    d = Canvas()
    noise_region(d, 0, 0, 15, 15, BLACKSTONE[1:5], 105, cells=4, contrast=1.3)
    d.hline(0, 15, 1, BLACKSTONE[5])
    d.hline(0, 15, 2, BLACKSTONE[2])
    d.hline(0, 15, 3, LAVA[1])
    for x in (3, 4, 10):
        d.put(x, 2, LAVA[3])
    t['dish'] = d
    i = Canvas()
    for y in range(16):
        for x in range(16):
            v = math.sin(x * 0.8 + math.sin(y * 0.7) * 2) + math.cos(y * 0.9 - x * 0.3)
            i.put(x, y, LAVA[6] if v > 1.2 else LAVA[5] if v > 0.4 else LAVA[4] if v > -0.6 else LAVA[3])
    for x, y in ((5, 5), (10, 9), (7, 11)):
        i.put(x, y, LAVA[1])
    t['inner'] = i
    c = Canvas()
    noise_region(c, 0, 0, 15, 15, BLACKSTONE[1:5], 107, cells=4, contrast=1.4)
    r = rng(109)
    for _ in range(7):
        x, y = int(r.integers(0, 16)), int(r.integers(0, 16))
        for i in range(6):
            c.put(x % 16, y % 16, LAVA[5] if i % 3 else LAVA[6])
            if c.inb((x + 1) % 16, y % 16):
                c.put((x + 1) % 16, y % 16, LAVA[3])
            x += int(r.integers(0, 2))
            y += 1
    t['crystal'] = c
    return t


def altar_model(name, emblem):
    tex = {'particle': T(f'{name}_pillar'), 'base': T(f'{name}_base'), 'pillar': T(f'{name}_pillar'),
           'dish': T(f'{name}_dish'), 'inner': T(f'{name}_inner'), 'crystal': T(f'{name}_crystal')}
    if name == 'storm_altar':
        tex['copper'] = T(f'{name}_copper')
    E = []
    E.append(el((0, 0, 0), (16, 2, 16), {
        'down': '#base', 'up': '#base',
        'north': ('#base', [0, 14, 16, 16]), 'south': ('#base', [0, 14, 16, 16]),
        'west': ('#base', [0, 14, 16, 16]), 'east': ('#base', [0, 14, 16, 16])}, name='step_lower'))
    E.append(el((1, 2, 1), (15, 4, 15), {
        'up': '#base',
        'north': ('#base', [1, 12, 15, 14]), 'south': ('#base', [1, 12, 15, 14]),
        'west': ('#base', [1, 12, 15, 14]), 'east': ('#base', [1, 12, 15, 14])}, name='step_upper'))
    E.append(el((3, 4, 3), (13, 12, 13), {
        'north': ('#pillar', [3, 4, 13, 12]), 'south': ('#pillar', [3, 4, 13, 12]),
        'west': ('#pillar', [3, 4, 13, 12]), 'east': ('#pillar', [3, 4, 13, 12])}, name='pillar'))
    inner_face = ('#inner', [3, 3, 13, 13])
    if name == 'magma_altar':
        inner_face = glow(inner_face)
    E.append(el((1, 12, 1), (15, 13, 15), {
        'down': ('#dish', [1, 1, 15, 15]), 'up': inner_face,
        'north': ('#dish', [1, 3, 15, 4]), 'south': ('#dish', [1, 3, 15, 4]),
        'west': ('#dish', [1, 3, 15, 4]), 'east': ('#dish', [1, 3, 15, 4])}, name='dish_floor'))
    rim = [((1, 13, 1), (15, 15, 3)), ((1, 13, 13), (15, 15, 15)), ((1, 13, 3), (3, 15, 13)), ((13, 13, 3), (15, 15, 13))]
    for f, t in rim:
        E.append(el(f, t, {
            'up': '#dish',
            'north': ('#dish', [16 - t[0], 1, 16 - f[0], 3]), 'south': ('#dish', [f[0], 1, t[0], 3]),
            'west': ('#dish', [f[2], 1, t[2], 3]), 'east': ('#dish', [16 - t[2], 1, 16 - f[2], 3])}, name='dish_rim'))
    E.extend(emblem())
    model(name, tex, E)


def frost_emblem():
    E = []
    c = rot('y', 45, (8, 19, 8))
    E.append(el((7, 15.5, 7), (9, 23.5, 9), {
        'up': glow(('#crystal', [0, 0, 2, 2])),
        'west': glow(('#crystal', [0, 0, 2, 16])), 'north': glow(('#crystal', [4, 0, 6, 16])),
        'east': glow(('#crystal', [8, 0, 10, 16])), 'south': glow(('#crystal', [12, 0, 14, 16])),
        'down': ('#crystal', [12, 14, 14, 16])}, rotation=c, name='ice_spire'))
    for x0, ang in ((5.2, 22.5), (9.6, -22.5)):
        E.append(el((x0, 16, 7.4), (x0 + 1.2, 20, 8.6), {
            'up': ('#crystal', [0, 0, 1.2, 1.2]),
            'west': ('#crystal', [0, 2, 1.2, 10]), 'north': ('#crystal', [4, 2, 5.2, 10]),
            'east': ('#crystal', [8, 2, 9.2, 10]), 'south': ('#crystal', [12, 2, 13.2, 10]),
            'down': ('#crystal', [12, 14, 13.2, 15.2])},
            rotation=rot('z', ang, (x0 + 0.6, 16, 8)), name='ice_shard'))
    return E


def tide_emblem():
    """Voxel sphere from three crossed boxes."""
    E = []
    boxes = [((5.5, 17, 6.5), (10.5, 22, 9.5)), ((6.5, 17, 5.5), (9.5, 22, 10.5)), ((6.5, 16, 6.5), (9.5, 23, 9.5))]
    for f, t in boxes:
        w = t[0] - f[0]
        d = t[2] - f[2]
        h = t[1] - f[1]
        E.append(el(f, t, {
            'up': glow(('#crystal', [1, 1, 1 + w, 1 + d])), 'down': ('#crystal', [10, 10, 10 + w, 10 + d]),
            'north': glow(('#crystal', [2, 3, 2 + w, 3 + h])), 'west': glow(('#crystal', [0, 3, d, 3 + h])),
            'south': ('#crystal', [10, 6, 10 + w, 6 + h]), 'east': ('#crystal', [10, 6, 10 + d, 6 + h])},
            name='water_orb'))
    return E


def storm_emblem():
    E = []
    for x, z in ((1.5, 1.5), (13.5, 1.5), (1.5, 13.5), (13.5, 13.5)):
        E.append(el((x, 15, z), (x + 1, 19, z + 1), {
            'up': ('#copper', [0, 0, 1, 1]), 'north': ('#copper', [0, 0, 1, 4]), 'south': ('#copper', [1, 0, 2, 4]),
            'west': ('#copper', [0, 4, 1, 8]), 'east': ('#copper', [2, 4, 3, 8])}, name='lightning_rod'))
        E.append(el((x - 0.25, 19, z - 0.25), (x + 1.25, 20, z + 1.25), {
            'up': ('#copper', [0, 0, 1.5, 1.5]), 'down': ('#copper', [2, 2, 3.5, 3.5]),
            'north': ('#copper', [0, 8, 1.5, 9]), 'south': ('#copper', [1, 8, 2.5, 9]),
            'west': ('#copper', [0, 9, 1.5, 10]), 'east': ('#copper', [2, 9, 3.5, 10])}, name='rod_tip'))
    cr = rot('y', 45, (8, 19, 8))
    E.append(el((6.75, 16, 6.75), (9.25, 22.5, 9.25), {
        'up': glow(('#crystal', [0, 0, 2.5, 2.5])), 'down': ('#crystal', [12, 13, 14.5, 15.5]),
        'west': glow(('#crystal', [0, 0, 2.5, 16])), 'north': glow(('#crystal', [4, 0, 6.5, 16])),
        'east': glow(('#crystal', [8, 0, 10.5, 16])), 'south': glow(('#crystal', [12, 0, 14.5, 16]))},
        rotation=cr, name='spark_spire'))
    for (x, y, z) in ((4.8, 19.5, 8), (11.2, 17.5, 7.5), (8.5, 22, 4.8), (7.5, 18, 11.4)):
        E.append(el((x - 0.5, y - 0.5, z - 0.5), (x + 0.5, y + 0.5, z + 0.5), {
            'all': glow(('#crystal', [1, 1, 2, 2]))}, rotation=rot('z', 45, (x, y, z)), name='spark'))
    return E


def magma_emblem():
    E = []
    f = lambda o: {
        'up': glow(('#crystal', [o, o, o + 5, o + 5])), 'down': glow(('#crystal', [10, 10, 15, 15])),
        'west': glow(('#crystal', [0, o, 5, o + 5])), 'north': glow(('#crystal', [5, o, 10, o + 5])),
        'east': glow(('#crystal', [10, o, 15, o + 5])), 'south': glow(('#crystal', [o, 10, o + 5, 15]))}
    E.append(el((5.5, 16, 5.5), (10.5, 20.5, 10.5), f(0), rotation=rot('y', 22.5, (8, 18, 8)), name='rock_a'))
    E.append(el((6.5, 18, 6.5), (9.5, 22, 9.5), f(3), rotation=rot('x', 22.5, (8, 20, 8)), name='rock_b'))
    return E


# ======================================================================
FORGE_TEX = {
    'titan_forge_front': forge_front, 'titan_forge_side': forge_side, 'titan_forge_top': forge_top,
    'titan_forge_deck': forge_deck, 'titan_forge_crucible': forge_crucible,
    'titan_forge_crystals': forge_crystals, 'titan_forge_gold': forge_gold,
}
EMBLEMS = {'frost_altar': frost_emblem, 'tide_altar': tide_emblem, 'storm_altar': storm_emblem,
           'magma_altar': magma_emblem}
MODEL_NAMES = ['titan_forge', 'frost_altar', 'tide_altar', 'storm_altar', 'magma_altar']


def main():
    out = []
    for name, fn in FORGE_TEX.items():
        cv = fn()
        cv.save(f'textures/block/{name}.png')
        out.append((name, cv.pil()))
    titan_forge_model()
    for name, fn in ALTARS.items():
        for part, cv in fn().items():
            cv.save(f'textures/block/{name}_{part}.png')
            out.append((f'{name}_{part}', cv.pil()))
        altar_model(name, EMBLEMS[name])
    print(contact_sheet(out, 'titan_block_textures.png', cols=7))
    from model_preview import model_sheet
    print(model_sheet(MODEL_NAMES, 'titan_block_models.png', S=11))


if __name__ == '__main__':
    main()
