"""Wave-2 items: Lost Ender Empire, Fallen Stars and Abyss materials.

Vanilla-plus 16x16: 1px outline in a dark shade of the item colour, top-left
light, 4-5 tone ramps and crisp highlights. Procedural base shading, then
hand-placed pixels where it reads better.
"""
import math

from w2common import *


def poly_mask(poly, w=16, h=16):
    m = np.zeros((h, w), bool)
    n = len(poly)
    for y in range(h):
        for x in range(w):
            px, py = x + 0.5, y + 0.5
            inside = False
            for i in range(n):
                x1, y1 = poly[i]
                x2, y2 = poly[(i + 1) % n]
                if (y1 > py) != (y2 > py):
                    xi = x1 + (py - y1) * (x2 - x1) / (y2 - y1)
                    if px < xi:
                        inside = not inside
            m[y, x] = inside
    return m


# ===================================================================== EMPIRE
def imperial_plating():
    """A thick purpur armour plate seen face-on: metallic diagonal sheen, gold corner
    guards and edge rivets, a violet gem in a gold setting, and its edge thickness
    showing along the bottom and right."""
    cv = Canvas()
    P = PURPUR
    x0, y0, x1, y1 = 1, 1, 12, 12          # face
    # thickness (drawn first so the face overlaps it)
    for y in range(y0 + 1, y1 + 3):
        for x in (x1 + 1, x1 + 2):
            if y - y0 >= x - x1:
                cv.put(x, y, P[2] if x == x1 + 1 else P[1])
    for x in range(x0 + 1, x1 + 3):
        for y in (y1 + 1, y1 + 2):
            if x - x0 >= y - y1:
                cv.put(x, y, P[1] if y == y1 + 1 else P[0])
    # gold band along the plate edge (thickness)
    for y in range(y0 + 2, y1 + 2):
        cv.put(x1 + 1, y, GOLD[2] if y % 4 else GOLD[3])
    for x in range(x0 + 2, x1 + 2):
        cv.put(x, y1 + 1, GOLD[1] if x % 4 else GOLD[2])
    # face with a metallic diagonal sheen
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            s = (x - x0) + (y - y0)
            if s in (6, 7):
                c = P[6]
            elif s in (5, 8):
                c = P[5]
            elif s < 5:
                c = P[4]
            elif s < 12:
                c = P[4]
            elif s < 17:
                c = P[3]
            else:
                c = P[2]
            cv.put(x, y, c)
    # engraved inner border (recessed: dark top/left, light bottom/right)
    cv.hline(x0 + 2, x1 - 2, y0 + 2, P[2])
    cv.vline(x0 + 2, y0 + 2, y1 - 2, P[2])
    cv.hline(x0 + 3, x1 - 2, y1 - 2, P[5])
    cv.vline(x1 - 2, y0 + 3, y1 - 2, P[5])
    # thin bevel: lit top/left edge, dark bottom/right edge
    cv.hline(x0, x1, y0, P[7])
    cv.vline(x0, y0, y1, P[6])
    cv.hline(x0, x1, y1, P[2])
    cv.vline(x1, y0, y1, P[2])
    # gold corner guards
    guard = {
        (x0, y0): [(0, 0, 6), (1, 0, 5), (2, 0, 5), (3, 0, 4), (0, 1, 5), (0, 2, 5), (0, 3, 4), (1, 1, 4)],
        (x1, y0): [(0, 0, 4), (-1, 0, 5), (-2, 0, 5), (-3, 0, 4), (0, 1, 3), (0, 2, 3), (0, 3, 2), (-1, 1, 3)],
        (x0, y1): [(0, 0, 4), (1, 0, 3), (2, 0, 3), (3, 0, 2), (0, -1, 5), (0, -2, 5), (0, -3, 4), (1, -1, 3)],
        (x1, y1): [(0, 0, 2), (-1, 0, 2), (-2, 0, 3), (-3, 0, 2), (0, -1, 2), (0, -2, 3), (0, -3, 2), (-1, -1, 2)],
    }
    for (cx, cy), pts in guard.items():
        for dx, dy, k in pts:
            cv.put(cx + dx, cy + dy, GOLD[k])
    # rivets mid-edge
    for (x, y, k) in ((6, y0, 5), (x0, 6, 5), (6, y1, 2), (x1, 6, 3)):
        cv.put(x, y, GOLD[k])
    # gem in a gold setting at the centre of the face
    gem = [
        "..aa..",
        ".aVvb.",
        "avvuub",
        "buuwwc",
        ".bwwc.",
        "..cc..",
    ]
    cv.grid(gem, {'a': GOLD[5], 'b': GOLD[3], 'c': GOLD[2], 'V': '#ffffff', 'v': VIOLET[4],
                  'u': VIOLET[3], 'w': VIOLET[1]}, 4, 4)
    outline(cv, '#2a1232', '#170a1c')
    return cv


def ender_gear():
    """Eight-tooth obsidian cog with an ender pearl set in a violet-lit hub."""
    cv = Canvas()
    cx = cy = 7.5
    O = OBSID
    for y in range(16):
        for x in range(16):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            r = math.hypot(dx, dy)
            a = math.degrees(math.atan2(dy, dx)) % 45
            ang = min(a, 45 - a)
            if r <= 5.3 or (r <= 7.45 and ang <= 11.5):
                cv.put(x, y, O[4])
    m = cv.mask()
    for y in range(16):
        for x in range(16):
            if not m[y, x]:
                continue
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            r = math.hypot(dx, dy)
            up = (y == 0 or not m[y - 1, x]) or (x == 0 or not m[y, x - 1])
            dn = (y == 15 or not m[y + 1, x]) or (x == 15 or not m[y, x + 1])
            t = -(dx + dy) / 14.0
            if up and not dn:
                c = O[7] if t > -0.1 else O[6]
            elif dn and not up:
                c = O[2]
            elif up and dn:
                c = O[5]
            else:
                c = O[5] if t > 0.3 else O[4] if t > -0.25 else O[3]
            if not (up or dn) and 3.7 < r < 4.6:
                c = O[2] if t > 0 else O[3]
            cv.put(x, y, c)
    for (x, y, c) in ((4, 5, O[7]), (5, 4, O[6]), (10, 11, O[2]), (11, 10, O[2])):
        cv.put(x, y, c)
    for y in range(16):
        for x in range(16):
            r = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if 2.9 < r <= 3.7:
                dot = light_dot(x + 0.5 - cx, y + 0.5 - cy)
                cv.put(x, y, VIOLET[4] if dot < -0.4 else VIOLET[3] if dot < 0.3 else VIOLET[2])
    vals = sphere(cx, cy, 2.95, glow=0.1)
    paint_levels(cv, vals, [PEARL[1], PEARL[2], PEARL[3], PEARL[4], PEARL[5]], [0.25, 0.45, 0.62, 0.8])
    cv.put(6, 6, PEARL[6])
    cv.put(9, 8, PEARL[2])
    outline(cv, '#160c26', '#0a0514')
    return cv


def colossus_core():
    """Big glowing violet core held in a gold cage with crown and foot caps."""
    cv = Canvas()
    cx, cy, R = 7.5, 7.5, 5.9
    vals = sphere(cx, cy, R, glow=0.62, light=(-0.5, -0.6, 0.62))
    pal = [VIOLET[0], VIOLET[1], VIOLET[2], VIOLET[3], VIOLET[4], VIOLET[5], VIOLET[6]]
    paint_levels(cv, vals, pal, [0.14, 0.26, 0.4, 0.56, 0.72, 0.88])
    orb = cv.mask().copy()
    # swirling energy streaks
    for (x, y, c) in ((5, 9, VIOLET[4]), (4, 8, VIOLET[3]), (10, 5, VIOLET[4]), (11, 6, VIOLET[3]),
                      (9, 10, VIOLET[5]), (10, 9, VIOLET[4])):
        cv.put(x, y, c)
    # cage: equator + two meridians (gold, lit TL)
    def gold_at(x, y, front=True):
        dot = light_dot(x + 0.5 - cx, y + 0.5 - cy)
        if not front:
            return GOLD[1]
        return GOLD[5] if dot > 0.45 else GOLD[4] if dot > -0.1 else GOLD[3] if dot > -0.6 else GOLD[2]
    for x in range(2, 14):
        y = 7 if x in (2, 13) else 8 if x in (3, 12) else 8
        cv.put(x, 8, gold_at(x, 8))
    for x in (2, 13):
        cv.put(x, 7, gold_at(x, 7))
    for y in range(2, 14):
        dy = (y + 0.5 - cy) / R
        off = 2.6 * math.sqrt(max(0, 1 - dy * dy))
        for sx in (-1, 1):
            x = int(round(cx - 0.5 + sx * off))
            if orb[y, x]:
                cv.put(x, y, gold_at(x, y))
    # crown cap (top) and foot (bottom)
    cap = [
        "..a.aa.a..",
        "..abaabb..",
        "...abbb...",
    ]
    cv.grid(cap, {'a': GOLD[5], 'b': GOLD[3]}, 3, 0)
    foot = [
        "...abbc...",
        "..abbbcc..",
        "..a.cc.c..",
    ]
    cv.grid(foot, {'a': GOLD[4], 'b': GOLD[3], 'c': GOLD[2]}, 3, 13)
    cv.put(7, 0, GOLD[6])
    # hot white core + specular
    cv.put(7, 7, '#ffffff')
    cv.put(8, 7, VIOLET[6])
    cv.put(7, 6, VIOLET[6])
    cv.put(5, 4, '#ffffff')
    outline(cv, '#22093e', '#14052a')
    for x, y in ((14, 2), (1, 12)):
        sparkle(cv, x, y, '#ffffff', VIOLET[4], only_empty=True)
    return cv


def imperial_seal():
    """Gold signet medallion with a beaded rim, an ender eye on a violet field and
    two hanging ribbons."""
    cv = Canvas()
    cx, cy = 7.5, 6.5
    rib = [
        ".....AB...AB....",
        "....ABC...ABC...",
        "....ABC....ABC..",
        "...ABC.....ABC..",
        "...AD.......DC..",
    ]
    cv.grid(rib, {'A': VIOLET[4], 'B': VIOLET[3], 'C': VIOLET[1], 'D': VIOLET[2]}, 0, 11)
    for y in range(16):
        for x in range(16):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            r = math.hypot(dx, dy)
            if r > 6.3:
                continue
            dot = light_dot(dx, dy)
            a = math.atan2(dy, dx)
            if r > 5.2:
                bead = math.cos(a * 8) > -0.2
                if bead:
                    c = GOLD[6] if dot > 0.6 else GOLD[5] if dot > 0.1 else GOLD[4] if dot > -0.5 else GOLD[3]
                else:
                    c = GOLD[3] if dot > 0 else GOLD[2]
            elif r > 4.3:
                c = GOLD[4] if dot > 0.3 else GOLD[3] if dot > -0.4 else GOLD[2]
            elif r > 3.5:
                c = GOLD[1] if dot > 0 else GOLD[4]
            else:
                c = VIOLET[1] if dot > -0.2 else VIOLET[2]
            cv.put(x, y, c)
    eye = [
        ".ggg.",
        "gGLGg",
        "GLkLG",
        "gGkGg",
        ".ggg.",
    ]
    cv.grid(eye, {'g': '#1f6a50', 'G': '#3fb487', 'L': '#9ff0c4', 'k': '#061410'}, 5, 4)
    cv.put(6, 5, '#e8fff2')
    outline(cv, '#3a2008', '#241204')
    return cv


def stardust():
    """Heap of glittering pale-blue dust with gold flecks and rising motes."""
    cv = Canvas()
    heap = [
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        ".......##.......",
        ".....######.....",
        "....########....",
        "...##########...",
        "..############..",
        ".##############.",
        ".##############.",
        "................",
    ]
    m = mask_from(heap)
    r = rng(7)
    for y in range(16):
        for x in range(16):
            if not m[y, x]:
                continue
            # light from top-left over a rounded mound
            nx = (x + 0.5 - 8) / 7.5
            ny = (y + 0.5 - 15) / 7.0
            v = 0.55 - 0.55 * nx - 0.35 * (y - 8) / 7 + (r.random() - 0.5) * 0.45
            k = int(round(v * 4))
            cv.put(x, y, PALE[max(1, min(5, k + 1))])
    # grains: dither the top edge into individual specks
    for (x, y) in ((6, 8), (10, 9), (4, 10), (12, 11), (2, 12), (14, 13)):
        cv.put(x, y, TRANSPARENT)
    for (x, y) in ((5, 7), (11, 8), (3, 9), (13, 10), (9, 6)):
        cv.put(x, y, PALE[4])
    # gold flecks and white glitter on the heap
    for (x, y) in ((7, 9), (4, 12), (10, 11), (12, 13), (6, 13), (9, 14)):
        cv.put(x, y, WGOLD[4])
    for (x, y) in ((8, 9), (5, 11), (11, 12), (3, 13)):
        cv.put(x, y, '#ffffff')
    outline(cv, '#122454', '#0a1638')
    # rising motes and twinkles
    sparkle(cv, 4, 3, '#ffffff', PALE[4], only_empty=True)
    sparkle(cv, 11, 2, '#ffffff', WGOLD[4], only_empty=True)
    for (x, y, c) in ((8, 4, WGOLD[5]), (13, 6, PALE[5]), (2, 6, PALE[4]), (7, 1, PALE[5])):
        put_if_empty(cv, x, y, c)
    return cv


def facet_sphere(cv, cx, cy, R, pal, seed, light=(-0.6, -0.65, 0.5), n_facets=9, glow=0.0):
    """Sphere split into flat facets (Voronoi on the disc), each facet shaded flat."""
    r = rng(seed)
    centers = []
    for i in range(n_facets):
        a = r.random() * 2 * math.pi
        rr = math.sqrt(r.random()) * 0.95
        centers.append((math.cos(a) * rr, math.sin(a) * rr))
    centers.append((0.0, 0.0))
    L = np.array(light)
    L = L / np.linalg.norm(L)
    owner = {}
    for y in range(16):
        for x in range(16):
            dx, dy = (x + 0.5 - cx) / R, (y + 0.5 - cy) / R
            if dx * dx + dy * dy > 1:
                continue
            k = min(range(len(centers)), key=lambda i: (dx - centers[i][0]) ** 2 + (dy - centers[i][1]) ** 2)
            fx, fy = centers[k]
            nz = math.sqrt(max(0.05, 1 - fx * fx - fy * fy))
            lam = max(0, fx * L[0] + fy * L[1] + nz * L[2])
            inner = (1 - math.sqrt(dx * dx + dy * dy)) ** 1.3
            v = (1 - glow) * lam + glow * inner
            owner[(x, y)] = k
            idx = int(round(v * (len(pal) - 1)))
            cv.put(x, y, pal[max(0, min(len(pal) - 1, idx))])
    return owner


def dormant_star_core():
    """Dim grey-blue crystal sphere: flat facets, faint hairline cracks and a
    barely-there ember of starlight."""
    cv = Canvas()
    pal = ['#1f2533', '#2b3345', '#3a4459', '#4d5870', '#646f88', '#8590a6']
    owner = facet_sphere(cv, 7.5, 7.5, 6.3, pal, seed=31, n_facets=10)
    # facet edges slightly darker on the lower-right side of each boundary
    for (x, y), k in owner.items():
        for dx, dy in ((1, 0), (0, 1)):
            q = (x + dx, y + dy)
            if q in owner and owner[q] != k:
                c = cv.get(x, y)
                cv.put(x, y, scale(c, 0.82))
    # faint cracks
    crack = [(5, 3), (6, 4), (6, 5), (7, 6), (8, 7), (8, 8), (9, 9), (10, 9), (11, 10), (7, 9), (6, 10), (5, 11)]
    for x, y in crack:
        cv.put(x, y, '#8e9ab2')
    for x, y in ((6, 5), (8, 8)):
        cv.put(x, y, '#aab4c8')
    # dim inner ember
    cv.put(8, 7, '#b8c6dc')
    # cold specular
    cv.put(4, 4, '#b0bacb')
    cv.put(5, 3, '#8e9ab2')
    outline(cv, '#141824', '#0b0e16')
    return cv


def star_core():
    """Blazing white-gold star inside a clear pale-blue crystal sphere."""
    cv = Canvas()
    pal = ['#1d3c7a', '#2a5cae', '#3f80d2', '#62a6ea', '#90c8fa', '#c4e4ff']
    owner = facet_sphere(cv, 7.5, 7.5, 6.3, pal, seed=33, n_facets=9, glow=0.35)
    for (x, y), k in owner.items():
        for dx, dy in ((1, 0), (0, 1)):
            q = (x + dx, y + dy)
            if q in owner and owner[q] != k:
                cv.put(x, y, scale(cv.get(x, y), 0.85))
    # golden glow halo inside the crystal
    for (x, y) in owner:
        d = math.hypot(x + 0.5 - 8, y + 0.5 - 8)
        if d < 3.6:
            cv.put(x, y, mix(cv.get(x, y), WGOLD[4], 0.55 if d > 2.4 else 0.8))
    star = [
        ".......a.......",
        ".......a.......",
        ".......b.......",
        "......aba......",
        "......bWb......",
        ".....bWWWb.....",
        "..ab.bWWWb.ba..",
        "aabbWWWWWWWbbaa",
        "..ab.bWWWb.ba..",
        ".....bWWWb.....",
        "......bWb......",
        "......aba......",
        ".......b.......",
        ".......a.......",
        ".......a.......",
    ]
    star = [
        "......a......",
        "......b......",
        ".....aba.....",
        ".....bWb.....",
        "....bWWWb....",
        "abbbWWWWWbbba",
        "....bWWWb....",
        ".....bWb.....",
        ".....aba.....",
        "......b......",
        "......a......",
    ]
    cv.grid(star, {'a': WGOLD[3], 'b': WGOLD[5], 'W': '#ffffff'}, 2, 2)
    cv.put(8, 7, '#ffffff')
    # crystal specular
    cv.put(4, 3, '#ffffff')
    cv.put(3, 4, PALE[5])
    outline(cv, '#0e2050', '#081436')
    # flare tips beyond the sphere
    for (x, y, c) in ((8, 0, WGOLD[4]), (8, 15, WGOLD[3]), (0, 7, WGOLD[4]), (15, 7, WGOLD[3])):
        cv.put(x, y, c)
    for (x, y) in ((14, 1), (1, 14)):
        put_if_empty(cv, x, y, WGOLD[5])
    return cv


def star_compass():
    """Gold-rimmed compass with a starry navy face and a glowing needle."""
    cv = Canvas()
    cx, cy = 7.5, 8.5
    for y in range(16):
        for x in range(16):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            r = math.hypot(dx, dy)
            if r > 6.6:
                continue
            dot = light_dot(dx, dy)
            if r > 5.5:
                c = WGOLD[5] if dot > 0.5 else WGOLD[4] if dot > 0 else WGOLD[3] if dot > -0.5 else WGOLD[2]
            elif r > 4.8:
                c = WGOLD[1] if dot > 0 else WGOLD[3]
            else:
                t = (dx + dy) / 9 + 0.5
                c = NAVY[5] if t < 0.25 else NAVY[4] if t < 0.6 else NAVY[3]
            cv.put(x, y, c)
    # bail ring at the top
    cv.grid([".aa.", "a..b", ".bb."], {'a': WGOLD[5], 'b': WGOLD[3]}, 6, 0)
    # tick marks N/E/S/W
    for (x, y) in ((7, 4), (8, 4), (3, 8), (12, 8), (7, 13), (8, 13)):
        pass
    for (x, y) in ((7, 3), (3, 8), (12, 9), (8, 13)):
        cv.put(x, y, WGOLD[4])
    # stars on the face
    for (x, y, c) in ((5, 6, PALE[5]), (10, 11, PALE[4]), (11, 6, '#ffffff'), (4, 10, WGOLD[4]), (6, 12, PALE[3])):
        cv.put(x, y, c)
    # needle: glowing north half (pale blue/white) to the upper right, dark south half
    north = [(8, 8), (9, 7), (9, 6), (10, 6), (10, 5), (11, 5)]
    south = [(7, 9), (6, 10), (6, 11), (5, 11)]
    for x, y in south:
        cv.put(x, y, WGOLD[2])
    cv.put(7, 10, WGOLD[1])
    for x, y in north:
        cv.put(x, y, PALE[4])
    for x, y in ((9, 6), (10, 5), (11, 5)):
        cv.put(x, y, PALE[6])
    cv.put(8, 7, PALE[3])
    cv.put(11, 4, '#ffffff')
    # pivot
    cv.put(7, 8, WGOLD[5])
    cv.put(8, 8, '#ffffff')
    outline(cv, '#1c1c3a', '#0e0e24')
    # glow beyond the tip
    put_if_empty(cv, 13, 2, PALE[5])
    return cv


# ===================================================================== ABYSS
def void_essence():
    """Violet-black droplet holding a slow magenta spiral, glassy rim light."""
    cv = Canvas()
    rows = [
        ".......#........",
        ".......#........",
        "......###.......",
        "......###.......",
        ".....#####......",
        "....#######.....",
        "...#########....",
        "...#########....",
        "..###########...",
        "..###########...",
        "..###########...",
        "..###########...",
        "...#########....",
        "....#######.....",
        "................",
        "................",
    ]
    m = mask_from(rows)
    cx, cy = 7.5, 9.6
    for y in range(16):
        for x in range(16):
            if not m[y, x]:
                continue
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            r = math.hypot(dx, dy)
            v = 0.45 + 0.3 * light_dot(dx, dy) * min(1, r / 4) - 0.05 * r
            pal = [ABYSS[1], ABYSS[3], ABYSS[5], ABYSS[7], SICK[1]]
            k = int(round(max(0, min(1, v)) * 4))
            cv.put(x, y, pal[k])
    arm = []
    for i in range(80):
        th = i / 80 * 3.4 * math.pi
        rr = 0.35 + 0.42 * th
        x = int(math.floor(cx + rr * math.cos(th + 0.4)))
        y = int(math.floor(cy + rr * math.sin(th + 0.4) * 0.95))
        arm.append((x, y, i / 80))
    for x, y, t in arm:
        if 0 <= x < 16 and 0 <= y < 16 and m[y, x]:
            c = MAGENTA[5] if t < 0.12 else MAGENTA[4] if t < 0.3 else MAGENTA[3] if t < 0.55 else SICK[3] if t < 0.8 else SICK[2]
            cv.put(x, y, c)
    cv.put(7, 9, '#ffffff')
    shade_edges(cv, ABYSS[0])
    for (x, y, c) in ((4, 6, SICK[4]), (3, 8, SICK[4]), (3, 9, SICK[3]), (5, 5, SICK[3]), (6, 3, SICK[2]),
                      (4, 7, '#efe0ff')):
        cv.put(x, y, c)
    outline(cv, '#16071f', '#0a0310')
    put_if_empty(cv, 9, 1, SICK[3])
    put_if_empty(cv, 10, 0, MAGENTA[3])
    return cv


HEART = [
    "................",
    "..####...####...",
    ".######.######..",
    "##############..",
    "###############.",
    "###############.",
    "###############.",
    ".#############..",
    ".#############..",
    "..###########...",
    "...#########....",
    "....#######.....",
    ".....#####......",
    "......###.......",
    ".......#........",
    "................",
]


def void_heart():
    """Near-black heart split by glowing magenta void cracks around a white star."""
    cv = Canvas()
    rows = [
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
    m = mask_from(rows)
    body = [ABYSS[1], ABYSS[2], ABYSS[3], ABYSS[5], ABYSS[7], '#5a4478']
    L = np.array([-0.62, -0.6, 0.5])
    L /= np.linalg.norm(L)
    lobes = [((4.5, 4.4), 3.9), ((10.5, 4.4), 3.9), ((7.5, 6.8), 6.0)]
    for y in range(16):
        for x in range(16):
            if not m[y, x]:
                continue
            px, py = x + 0.5, y + 0.5
            (lx, ly), rr = min(lobes, key=lambda l: math.hypot(px - l[0][0], py - l[0][1]) / l[1])
            nx, ny = (px - lx) / rr, (py - ly) / rr
            nz = math.sqrt(max(0.04, 1 - min(1, nx * nx + ny * ny)))
            lam = max(0, nx * L[0] + ny * L[1] + nz * L[2])
            cv.put(x, y, body[min(5, int(lam * 5.6))])
    # magenta cracks radiating from the core (7,7)
    dim, mid, hot = MAGENTA[2], MAGENTA[3], MAGENTA[4]
    cracks = {
        hot: [(6, 6), (8, 6), (6, 8), (8, 8)],
        mid: [(5, 5), (9, 5), (5, 9), (9, 9), (7, 4), (7, 10), (4, 7), (10, 7)],
        dim: [(4, 4), (3, 3), (10, 4), (11, 3), (4, 10), (10, 10), (11, 11), (7, 11), (2, 7), (11, 7),
              (12, 6), (3, 5), (8, 3), (6, 12), (8, 12)],
    }
    for c, pts in cracks.items():
        for x, y in pts:
            if m[y, x]:
                cv.put(x, y, c)
    star = [
        "..a..",
        ".aWa.",
        "aWWWa",
        ".aWa.",
        "..a..",
    ]
    cv.grid(star, {'a': MAGENTA[5], 'W': '#ffffff'}, 5, 5)
    cv.put(7, 7, '#ffffff')
    # rim light (magenta bleeding out on the lower right) + gloss
    for y in range(16):
        for x in range(16):
            if m[y, x] and (x + 1 >= 16 or not m[y, x + 1] or not m[min(15, y + 1), x]) and x + y > 15:
                cv.put(x, y, MAGENTA[1])
    cv.put(3, 2, '#7a64a0')
    cv.put(2, 3, '#5a4478')
    cv.put(4, 2, '#5a4478')
    outline(cv, '#12061c', '#08020e')
    for (x, y, c) in ((14, 1, '#ffffff'), (13, 1, MAGENTA[4]), (15, 1, MAGENTA[4]), (14, 0, MAGENTA[4]),
                      (14, 2, MAGENTA[4])):
        put_if_empty(cv, x, y, c)
    return cv


ELEM = {
    'frost': ['#1a5c78', '#2f98b8', '#5fd2ea', '#a8f2ff', '#ffffff'],
    'tide': ['#1a2c8a', '#2c4fd0', '#4f7cf2', '#8aaaff', '#d8e4ff'],
    'storm': ['#8a5a0a', '#c8920e', '#f0c428', '#ffe86a', '#fffbd0'],
    'magma': ['#7a2208', '#b8420f', '#e86a1a', '#ff9c42', '#ffd8a0'],
}


def primordial_core():
    """Four elemental arms (frost, storm, magma, tide) spiralling into a violet heart."""
    cv = Canvas()
    cx, cy, R = 7.5, 7.5, 6.5
    vals = sphere(cx, cy, R, glow=0.25)
    order = ['tide', 'frost', 'storm', 'magma']
    for (x, y), v in vals.items():
        dx, dy = x + 0.5 - cx, y + 0.5 - cy
        r = math.hypot(dx, dy) / R
        a = math.atan2(dy, dx)
        a2 = (a + math.pi - r * 2.1 + 0.15) % (2 * math.pi)
        q = int(a2 / (math.pi / 2)) % 4
        pal = ELEM[order[q]]
        k = 1 + int(round(v * 3.1))
        cv.put(x, y, pal[max(0, min(4, k))])
    for (x, y), v in vals.items():
        if math.hypot(x + 0.5 - cx, y + 0.5 - cy) > R - 1 and x + y > 15:
            cv.put(x, y, scale(cv.get(x, y), 0.72))
    heart = [
        ".aba.",
        "abVba",
        "bVWVb",
        "abVba",
        ".aba.",
    ]
    cv.grid(heart, {'a': VIOLET[1], 'b': VIOLET[3], 'V': VIOLET[5], 'W': '#ffffff'}, 5, 5)
    cv.put(4, 3, '#ffffff')
    cv.put(3, 4, '#e8fcff')
    outline(cv, '#1c1234', '#100a22')
    return cv


def abyssal_beacon():
    """Black-violet lantern beacon with a spired cap and a magenta void flame."""
    cv = Canvas()
    rows = [
        "......4.4.......",
        "......4.4.......",
        ".....45532......",
        "....4553332.....",
        "...455333332....",
        "...3gGGGGGg1....",
        "...3gGfFfGg1....",
        "...3gfFWFfg1....",
        "...3gfFWFfg1....",
        "...3ggfFfgg1....",
        "...3gggfggg1....",
        "..45533333321...",
        "...322222221....",
        "....2111111.....",
        "................",
        "................",
    ]
    pal = {'1': ABYSS[2], '2': ABYSS[4], '3': ABYSS[6], '4': '#4c3a68', '5': '#6c5694',
           'g': MAGENTA[0], 'G': MAGENTA[1], 'f': MAGENTA[3], 'F': MAGENTA[5], 'W': '#ffffff'}
    cv.grid(rows, pal, 0, 1)
    cv.put(7, 0, '#6c5694')
    cv.put(7, 4, MAGENTA[4])
    cv.put(6, 6, MAGENTA[2])
    outline(cv, '#120a1c', '#07030c')
    for (x, y, c) in ((13, 6, MAGENTA[4]), (14, 9, MAGENTA[3]), (1, 8, MAGENTA[3])):
        put_if_empty(cv, x, y, c)
    return cv


def ascension_pearl():
    """A radiant pearl of white-gold light: glowing core, gold-shadowed rim,
    prismatic sheen and a ring of short light rays."""
    cv = Canvas()
    cx, cy, R = 7.5, 7.5, 5.0
    vals = sphere(cx, cy, R, glow=0.5, light=(-0.55, -0.65, 0.55))
    pal = ['#c09440', '#e2c070', '#f6e2a6', '#fff4d4', '#fffbee', '#ffffff']
    paint_levels(cv, vals, pal, [0.12, 0.27, 0.43, 0.6, 0.78])
    prism = ['#ffc6ec', '#e0bcff', '#b8d4ff', '#a8f4ff', '#c4ffd8']
    for (x, y) in vals:
        dx, dy = x + 0.5 - cx, y + 0.5 - cy
        if math.hypot(dx, dy) > R - 1.0 and dx + dy > 2.5:
            a = math.atan2(dy, dx)
            k = int((a + 0.6) / 2.8 * len(prism))
            cv.put(x, y, prism[max(0, min(len(prism) - 1, k))])
    for (x, y) in ((5, 5), (6, 5), (5, 6)):
        cv.put(x, y, '#ffffff')
    outline(cv, '#7a5414', '#5a3c0c')
    # radiant rays (outside the outline)
    rays = {
        (7, 0): '#fff6dc', (7, 1): '#f6dc8e',
        (7, 14): '#e8c868', (7, 15): '#c89e3e',
        (0, 7): '#fff6dc', (1, 7): '#f6dc8e',
        (14, 7): '#e8c868', (15, 7): '#c89e3e',
        (2, 2): '#fff6dc', (12, 12): '#e0bcff', (12, 2): '#f6dc8e', (2, 12): '#f6dc8e',
    }
    for (x, y), c in rays.items():
        put_if_empty(cv, x, y, c)
    cv.put(13, 1, '#ffffff')
    return cv


ITEMS = [
    ('imperial_plating', imperial_plating), ('ender_gear', ender_gear), ('colossus_core', colossus_core),
    ('imperial_seal', imperial_seal),
    ('stardust', stardust), ('dormant_star_core', dormant_star_core), ('star_core', star_core),
    ('star_compass', star_compass),
    ('void_essence', void_essence), ('void_heart', void_heart), ('primordial_core', primordial_core),
    ('abyssal_beacon', abyssal_beacon), ('ascension_pearl', ascension_pearl),
]


def main():
    out = []
    for name, fn in ITEMS:
        cv = fn()
        cv.save(f'textures/item/{name}.png')
        out.append((name, cv.pil()))
    print(sheet(out, 'items.png', cols=5))
    print(inventory_strip(out, 'items_scales.png'))
    return out


if __name__ == '__main__':
    main()
