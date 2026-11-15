"""Titan-step items: shard, elemental cores, sigils, titan armor, dragon heart."""
import math
from common import *


def finish(cv, tl, br=None):
    outline(cv, tl, br or tl)
    return cv


# ---------------------------------------------------------------- shard
def point_in_poly(x, y, poly):
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xi = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < xi:
                inside = not inside
    return inside


def raster_poly(poly):
    return {(x, y) for y in range(16) for x in range(16) if point_in_poly(x + 0.5, y + 0.5, poly)}


SHARD_POLY = [  # jagged shard pointing up-right, clockwise from the tip
    (15.4, 0.6), (14.9, 3.6), (13.6, 5.2), (14.3, 6.3), (11.6, 9.0), (10.4, 9.0),
    (8.0, 11.9), (6.0, 13.0), (4.4, 15.2), (1.3, 14.4), (1.0, 11.8), (3.2, 9.9),
    (3.9, 8.0), (5.2, 7.8), (8.6, 4.2), (10.2, 3.9), (11.4, 2.0),
]
SHARD_RIDGE = ((3.0, 14.6), (14.6, 1.6))


SHARD_SIL = [
    "................",
    "..............#.",
    ".............##.",
    "............###.",
    "..........#####.",
    ".........#####..",
    "........######..",
    ".......#######..",
    "......#######...",
    ".....#######....",
    "....#######.....",
    "....######......",
    "...#####........",
    "..#####.........",
    "..###...........",
    "................",
]


def titan_shard():
    """Jagged iridescent crystal shard on a stone stub, pointing up-right.
    Lit facet (upper-left of the ridge) runs cyan->indigo, shaded facet runs
    lilac->magenta->amber, and a white ridge separates them."""
    px = {(x, y) for y, r in enumerate(SHARD_SIL) for x, ch in enumerate(r) if ch == '#'}
    (ax, ay), (bx, by) = SHARD_RIDGE
    vx, vy = bx - ax, by - ay
    ln = math.hypot(vx, vy)
    lit = ramp(['#3a6fe0', '#3fa8f0', '#6fe0fa', '#b8fbff'], 6)        # base -> tip
    shd = ramp(['#b4401c', '#c23a72', '#8a44c8', '#5a5ad8', '#6f86ec'], 6)
    ridge = ramp(['#9fe9ff', '#e8fdff', '#ffffff'], 3)
    stone = {'hi': '#9a97a6', 'mid': '#6b6878', 'lo': '#45424f'}
    cv = Canvas()
    for (x, y) in px:
        cx, cy = x + 0.5 - ax, y + 0.5 - ay
        t = (cx * vx + cy * vy) / (ln * ln)          # 0 base .. 1 tip
        side = (vx * cy - vy * cx) / ln              # <0 upper-left of ridge
        if t < 0.17:
            c = stone['hi'] if side < -0.6 else stone['mid'] if side < 0.8 else stone['lo']
        elif abs(side) < 0.55:
            c = ridge[min(2, int(t * 3))]
        elif side < 0:
            c = lit[min(5, int(t * 6))]
        else:
            c = shd[min(5, int(t * 6))]
        cv.put(x, y, c)
    # secondary fracture line on the shaded facet + chips of light on the lit facet
    # fracture glints
    for x, y, c in ((11, 7, '#e08ae8'), (8, 7, '#d8fdff'), (5, 11, '#9fe8ff')):
        if cv.opaque(x, y):
            cv.put(x, y, c)
    outline(cv, '#1e1838', '#140e26')
    return cv


# ---------------------------------------------------------------- orbs
def orb_field(cx, cy, R, glow=0.55, light=(-0.55, -0.6, 0.58)):
    """Return dict (x,y)->value in [0,1] for a glowing sphere."""
    L = np.array(light)
    L = L / np.linalg.norm(L)
    vals = {}
    for y in range(16):
        for x in range(16):
            dx, dy = (x + 0.5 - cx) / R, (y + 0.5 - cy) / R
            r2 = dx * dx + dy * dy
            if r2 > 1.0:
                continue
            nz = math.sqrt(1 - r2)
            lam = max(0.0, dx * L[0] + dy * L[1] + nz * L[2])
            inner = (1 - math.sqrt(r2)) ** 1.2
            vals[(x, y)] = min(1.0, glow * inner + (1 - glow) * lam)
    return vals


def paint_orb(cv, vals, pal, cuts):
    """cuts: ascending thresholds len(pal)-1"""
    for (x, y), v in vals.items():
        k = 0
        while k < len(cuts) and v > cuts[k]:
            k += 1
        cv.put(x, y, pal[k])


def frost_core():
    cv = Canvas()
    vals = orb_field(7.5, 7.5, 5.3)
    pal = ['#1d4f8f', '#2f80c8', '#56b8ee', '#93e2ff', '#d4f7ff', '#ffffff']
    paint_orb(cv, vals, pal, [0.18, 0.34, 0.5, 0.66, 0.84])
    # ice spikes growing out of the orb on the diagonals (lit edge / shaded edge)
    spikes = [
        "................",
        ".W............W.",
        "..WL........LW..",
        "..LCc......cCL..",
        "...cc......cc...",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "...LC......Cc...",
        "..LCc......cCc..",
        "..Wc........cW..",
        ".W............W.",
        "................",
    ]
    cv.grid(spikes, {'W': '#ffffff', 'L': '#d8fbff', 'C': '#8fdcf8', 'c': '#4a9fd8'})
    flake = [
        "...w...",
        ".w.w.w.",
        "..www..",
        "wwwWwww",
        "..www..",
        ".w.w.w.",
        "...w...",
    ]
    cv.grid(flake, {'w': '#e8fdff', 'W': '#ffffff'}, 4, 4)
    cv.put(4, 4, '#ffffff')
    outline(cv, '#143c70', '#0b2148')
    return cv


def tide_core():
    cv = Canvas()
    cx, cy = 7.5, 7.5
    vals = orb_field(cx, cy, 5.4)
    pal = ['#06325a', '#0b5a86', '#1489a8', '#2ebfc4', '#7ef0de', '#e6fff8']
    paint_orb(cv, vals, pal, [0.16, 0.3, 0.46, 0.64, 0.86])
    swirl = [
        "..aaa...",
        ".a...b..",
        "a..cc.b.",
        "a.c..cb.",
        "a.c.c.b.",
        ".a.c.b..",
        "..abb...",
    ]
    cv.grid(swirl, {'a': '#a8fff2', 'b': '#2ad0d0', 'c': '#ffffff'}, 4, 4)
    orb = cv.mask().copy()
    # tilted gold ring, traced parametrically so it stays 1px thick
    ang = math.radians(-28)
    U = (math.cos(ang), math.sin(ang))
    V = (-math.sin(ang), math.cos(ang))
    ring = {}
    for i in range(720):
        th = i / 720 * 2 * math.pi
        a, b = 7.9 * math.cos(th), 2.7 * math.sin(th)
        x = int(math.floor(cx + a * U[0] + b * V[0]))
        y = int(math.floor(cy + a * U[1] + b * V[1]))
        if not (0 <= x < 16 and 0 <= y < 16):
            continue
        front = math.sin(th) > 0
        if orb[y, x] and not front:
            continue
        ring[(x, y)] = math.cos(th)
    for (x, y), u in ring.items():
        c = '#ffe680' if u < -0.45 else '#e8b830' if u < 0.5 else '#b07818'
        cv.put(x, y, c)
    outline(cv, '#05304a', '#021d30')
    return cv


def storm_core():
    cv = Canvas()
    vals = orb_field(7.5, 7.5, 6.2, glow=0.7)
    pal = ['#2a2350', '#433a7a', '#6a5ca8', '#a99ad8', '#f6f0b0', '#fffff0']
    paint_orb(cv, vals, pal, [0.18, 0.32, 0.46, 0.62, 0.8])
    bolt = [
        ".....yy.",
        "....yy..",
        "...yWy..",
        "..yWWyy.",
        ".yyyWWy.",
        "...yWy..",
        "..yWy...",
        "..yy....",
        ".y......",
    ]
    cv.grid(bolt, {'y': '#ffe14a', 'W': '#ffffff'}, 4, 3)
    outline(cv, '#1a1538', '#100c26')
    # crackling arcs outside the orb
    for x, y, c in ((14, 5, '#ffe14a'), (15, 4, '#fff7b0'), (1, 10, '#ffe14a'), (0, 11, '#fff7b0'),
                    (12, 14, '#ffe14a')):
        cv.put(x, y, c)
    return cv


def magma_core():
    cv = Canvas()
    vals = orb_field(7.5, 7.5, 6.3, glow=0.25)
    crust = ['#120c0c', '#1e1414', '#2e1f1c', '#463029', '#5e4237']
    paint_orb(cv, vals, crust, [0.2, 0.38, 0.56, 0.74])
    cracks = [
        "......l.....",
        "..m...lL....",
        "...mMLLyl...",
        "....yYYy..m.",
        "..lLYWWYym..",
        ".mLyYWWYyMm.",
        "...yYYYYl...",
        "..m..yYl....",
        ".m...Ll.m...",
        "....l..mm...",
        "............",
    ]
    cv.grid(cracks, {'m': '#8a2a0c', 'M': '#c2410c', 'l': '#c2410c', 'L': '#ff6a12',
                     'y': '#ff9a1f', 'Y': '#ffd23f', 'W': '#fff6c0'}, 2, 2)
    outline(cv, '#0b0606', '#060303')
    for x, y, c in ((13, 2, '#ff9a1f'), (14, 1, '#ffd23f'), (2, 14, '#c2410c')):
        cv.put(x, y, c)
    return cv


# ---------------------------------------------------------------- sigils
HEX = [  # 13x15 pointy-top hexagon, centre (7,7)
    ".......#.......",
    ".....#####.....",
    "...#########...",
    ".#############.",
    ".#############.",
    ".#############.",
    ".#############.",
    ".#############.",
    ".#############.",
    ".#############.",
    ".#############.",
    ".#############.",
    "...#########...",
    ".....#####.....",
    ".......#.......",
]
HEX_VERTS = [(7, 1), (2, 3), (12, 3), (2, 11), (12, 11), (7, 13)]

GLYPHS = {
    'frost': [
        "...#...",
        ".#.#.#.",
        "..###..",
        "###W###",
        "..###..",
        ".#.#.#.",
        "...#...",
    ],
    'tide': [
        "#..#..#",
        "#..#..#",
        "##.#.##",
        ".#####.",
        "...W...",
        "...#...",
        "...#...",
        "..###..",
    ],
    'storm': [
        "....##.",
        "...##..",
        "..##...",
        ".#####.",
        "...W#..",
        "..##...",
        ".##....",
        ".#.....",
    ],
    'magma': [
        "...#...",
        "...##..",
        "..###.#",
        ".##y##.",
        ".#yyy#.",
        "##yWy##",
        "##yyy##",
        ".##y##.",
        "..###..",
    ],
}

SIGIL_STYLE = {
    'frost': dict(outline=('#1a3466', '#0e1f44'), bevel=['#5a6f96', '#8fa6cc', '#c4d4ec', '#f2f8ff'],
                  field='#1d3a6a', field_sh='#142a52', glyph='#a8f2ff', core='#ffffff', halo='#2f5c92',
                  stud='#ffffff', y='#e0fbff'),
    'tide': dict(outline=('#06302f', '#031c1d'), bevel=['#8a5a0c', '#c8941e', '#ecc040', '#fff0a0'],
                 field='#0d4a50', field_sh='#08343a', glyph='#62f6e0', core='#eafffb', halo='#1a6e72',
                 stud='#7ffff0', y='#c8fff6'),
    'storm': dict(outline=('#1c1834', '#110e22'), bevel=['#7a3418', '#b25a2e', '#de8a52', '#ffc08a'],
                  field='#2c2a4c', field_sh='#201e3a', glyph='#ffe84a', core='#ffffff', halo='#4a446e',
                  stud='#fff27a', y='#fff8c0'),
    'magma': dict(outline=('#1a0f0d', '#0c0606'), bevel=['#2a1a18', '#463029', '#664540', '#8a6058'],
                  field='#1e1515', field_sh='#140e0e', glyph='#ff7a1a', core='#fff2b0', halo='#4a1c0e',
                  stud='#ff9a2a', y='#ffd040'),
}


def sigil(kind):
    st = SIGIL_STYLE[kind]
    cv = Canvas()
    mask = np.zeros((16, 16), bool)
    for y, r in enumerate(HEX):
        for x, ch in enumerate(r):
            if ch == '#':
                mask[y, x] = True
    depth = ring_depth(mask)
    bev = st['bevel']
    for y in range(16):
        for x in range(16):
            if not mask[y, x]:
                continue
            d = depth[y, x]
            dot = light_dot(x - 7, y - 7)
            if d == 0:
                c = st['outline'][0] if dot > 0.2 else st['outline'][1]
            elif d == 1:
                c = bev[3] if dot > 0.55 else bev[2] if dot > -0.1 else bev[1] if dot > -0.6 else bev[0]
            elif d == 2 and dot > 0.2:
                c = st['field_sh']
            else:
                c = st['field']
            cv.put(x, y, c)
    g = GLYPHS[kind]
    gh, gw = len(g), len(g[0])
    ox, oy = 7 - gw // 2, 7 - gh // 2
    pts = {(ox + i, oy + j) for j, r in enumerate(g) for i, ch in enumerate(r) if ch != '.'}
    # soft halo on the field around the glyph
    for (x, y) in pts:
        for dx, dy in N8:
            q = (x + dx, y + dy)
            if q not in pts and depth[q[1], q[0]] >= 2:
                cv.put(q[0], q[1], st['halo'])
    cv.grid(g, {'#': st['glyph'], 'W': st['core'], 'y': st['y']}, ox, oy)
    for x, y in HEX_VERTS:
        cv.put(x, y, st['stud'])
    return cv


def frost_sigil():
    return sigil('frost')


def tide_sigil():
    return sigil('tide')


def storm_sigil():
    return sigil('storm')


def magma_sigil():
    return sigil('magma')


# ---------------------------------------------------------------- titan armor
# 1-5 dark steel (dark->light), a-d stone plate (light->dark),
# x/y/z/w crystal inlay (deep->white), v dark interior
ARMOR_PAL = {
    '1': '#262a31', '2': '#363c45', '3': '#4b535e', '4': '#66707c', '5': '#8f99a4', '6': '#b9c2ca',
    'a': '#b0a898', 'b': '#8c8579', 'c': '#6b655b', 'd': '#4d4842',
    'x': '#1e8fb4', 'y': '#46cdea', 'z': '#a6f2ff', 'w': '#ffffff',
    'v': '#101217',
}
ARMOR_OUTLINE = ('#15171c', '#0b0c0f')

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
    "...456544432....",
    "...4654544322...",
    "...45543343322..",
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
# leggings rows 3-5 need trimming to a clean silhouette; fixed below
LEGGINGS[3] = "...4565444332..."
LEGGINGS[4] = "...4654544322..."
LEGGINGS[5] = "...4554334322..."

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


def armor(rows):
    cv = Canvas()
    cv.grid(rows, ARMOR_PAL)
    outline(cv, *ARMOR_OUTLINE)
    return cv


def titan_helmet():
    return armor(HELMET)


def titan_chestplate():
    return armor(CHESTPLATE)


def titan_leggings():
    return armor(LEGGINGS)


def titan_boots():
    return armor(BOOTS)


# ---------------------------------------------------------------- dragon heart
HEART_SIL = [
    "................",
    "...###...###....",
    "..#####.#####...",
    ".#############..",
    ".#############..",
    ".#############..",
    ".#############..",
    "..###########...",
    "..###########...",
    "...#########....",
    "....#######.....",
    ".....#####......",
    "......###.......",
    ".......#........",
    "................",
    "................",
]


def dragon_heart():
    """Dark purple heart: two shaded lobes, aorta stub, branching magenta
    veins around a glowing throb, and an ender sparkle."""
    cv = Canvas()
    body = ['#200a2e', '#2f1042', '#431858', '#5a2272', '#74308c', '#9448ac']
    L = np.array([-0.62, -0.6, 0.5])
    L /= np.linalg.norm(L)
    lobes = [((4.5, 4.4), 3.9), ((10.5, 4.4), 3.9), ((7.5, 6.8), 6.0)]
    for y, r in enumerate(HEART_SIL):
        for x, ch in enumerate(r):
            if ch != '#':
                continue
            px, py = x + 0.5, y + 0.5
            best = min(lobes, key=lambda l: math.hypot(px - l[0][0], py - l[0][1]) / l[1])
            (cx, cy), rr = best
            nx, ny = (px - cx) / rr, (py - cy) / rr
            nz = math.sqrt(max(0.04, 1 - min(1, nx * nx + ny * ny)))
            lam = max(0, nx * L[0] + ny * L[1] + nz * L[2])
            cv.put(x, y, body[min(5, int(lam * 5.4))])
    # magenta rim light along the lower-right edge (inner glow bleeding out)
    msk = cv.mask()
    for y in range(16):
        for x in range(16):
            if msk[y, x] and (x + 1 >= 16 or not msk[y, x + 1] or y + 1 >= 16 or not msk[y + 1, x]):
                if x + y > 13:
                    cv.put(x, y, '#5c1a66')
    # organic veins: dim branches, bright pulsing cores
    M, m = '#ff5ad6', '#a8248f'
    veins_m = [(7, 2), (7, 3), (6, 4), (4, 4), (3, 5), (5, 5), (5, 6), (5, 7), (6, 8), (6, 9), (7, 10),
               (9, 3), (10, 4), (10, 5), (11, 6), (9, 6), (9, 7), (10, 8), (8, 9), (4, 8)]
    veins_M = [(6, 5), (5, 6), (9, 5), (10, 5), (6, 9)]
    for x, y in veins_m:
        cv.put(x, y, m)
    for x, y in veins_M:
        cv.put(x, y, M)
    cv.put(5, 6, '#ffd0f4')     # throb
    # glossy highlight on the lit lobe
    cv.put(3, 2, '#c690dc')
    cv.put(2, 3, '#a86ac4')
    cv.put(4, 2, '#a86ac4')
    outline(cv, '#1c0628', '#0f0316')
    # ender sparkle (outside the outline)
    for x, y, c in ((14, 1, '#ffffff'), (13, 1, '#d070ff'), (15, 1, '#d070ff'), (14, 0, '#d070ff'),
                    (14, 2, '#d070ff'), (1, 12, '#c060f0')):
        if not cv.opaque(x, y):
            cv.put(x, y, c)
    return cv


ITEMS = [
    ('titan_shard', titan_shard),
    ('frost_core', frost_core), ('tide_core', tide_core),
    ('storm_core', storm_core), ('magma_core', magma_core),
    ('frost_sigil', frost_sigil), ('tide_sigil', tide_sigil),
    ('storm_sigil', storm_sigil), ('magma_sigil', magma_sigil),
    ('titan_helmet', titan_helmet), ('titan_chestplate', titan_chestplate),
    ('titan_leggings', titan_leggings), ('titan_boots', titan_boots),
    ('dragon_heart', dragon_heart),
]


def main():
    out = []
    for name, fn in ITEMS:
        cv = fn()
        cv.save(f'textures/item/{name}.png')
        out.append((name, cv.pil()))
    print(contact_sheet(out, 'titan_items.png', cols=5))


if __name__ == '__main__':
    main()
