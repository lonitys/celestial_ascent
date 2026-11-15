"""Wave-2 cube textures (seamlessly tiling, no outlines), the star crystal cross
sprite, the imperial barrier and the animated star portal strip."""
import math

from w2common import *


# ----------------------------------------------------------------- noise
def aniso_noise(cx, cy, seed, octaves=2, persistence=0.5, w=16, h=16):
    """Tileable value noise with separate lattice counts across/down."""
    r = rng(seed)
    total = np.zeros((h, w))
    amp, norm = 1.0, 0.0
    ys, xs = np.mgrid[0:h, 0:w]
    for o in range(octaves):
        nx, ny = cx * (2 ** o), cy * (2 ** o)
        lat = r.random((ny, nx))
        fx, fy = xs / w * nx, ys / h * ny
        x0, y0 = np.floor(fx).astype(int), np.floor(fy).astype(int)
        tx, ty = fx - x0, fy - y0
        tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
        x1, y1 = (x0 + 1) % nx, (y0 + 1) % ny
        x0, y0 = x0 % nx, y0 % ny
        a = lat[y0, x0] * (1 - tx) + lat[y0, x1] * tx
        b = lat[y1, x0] * (1 - tx) + lat[y1, x1] * tx
        total += (a * (1 - ty) + b * ty) * amp
        norm += amp
        amp *= persistence
    v = total / norm
    v = (v - v.min()) / max(1e-6, v.max() - v.min())
    return v


def stone(pal, seed, cuts, cx=4, cy=7, grain=0.18):
    """Vanilla-stone-like blotches: anisotropic noise plus per-pixel grain."""
    n = aniso_noise(cx, cy, seed, octaves=2)
    g = rng(seed + 99).random((16, 16))
    v = np.clip(n + (g - 0.5) * grain, 0, 1)
    cv = Canvas()
    for y in range(16):
        for x in range(16):
            k = 0
            while k < len(cuts) and v[y, x] > cuts[k]:
                k += 1
            cv.put(x, y, pal[k])
    return cv


def wrap_put(cv, x, y, c):
    cv.put(x % 16, y % 16, c)


def wrap_blend(cv, x, y, c, t):
    cv.blend(x % 16, y % 16, c, t)


# ================================================================= STARS
STAR_TONES = [NAVY[2], NAVY[3], NAVY[4], NAVY[5], NAVY[6]]
STAR_CUTS = [0.22, 0.42, 0.66, 0.86]


def starstone_base(seed=211):
    return stone(STAR_TONES, seed, STAR_CUTS)


def starstone():
    cv = starstone_base()
    # tiny star specks
    for (x, y, c) in ((3, 4, '#d8e6ff'), (11, 2, '#8fb4ee'), (13, 11, '#e8cc7a'), (6, 13, '#a8c4f4'),
                      (8, 8, '#5a6ea8')):
        cv.put(x, y, c)
    # one faint four-point twinkle
    cv.put(11, 2, '#c8dcff')
    for dx, dy in N4:
        cv.put(11 + dx, 2 + dy, NAVY[6])
    return cv


def starlit_starstone():
    """Starstone lit from within: lighter, with pools of pale-blue glow around
    brighter stars."""
    tones = [NAVY[3], NAVY[4], NAVY[5], NAVY[6], NAVY[7]]
    cv = stone(tones, 211, STAR_CUTS)
    glow = [(4, 4, 2.8), (12, 10, 3.2), (12, 2, 1.8), (3, 12, 2.2)]
    for gx, gy, rad in glow:
        for y in range(-4, 5):
            for x in range(-4, 5):
                d = math.hypot(x, y)
                if d < rad:
                    t = (1 - d / rad) ** 1.4 * 0.75
                    wrap_blend(cv, gx + x, gy + y, PALE[3], t)
    for (x, y, big) in ((4, 4, True), (12, 10, True), (12, 2, False), (3, 12, False), (8, 7, False),
                        (14, 14, False)):
        wrap_put(cv, x, y, '#ffffff')
        if big:
            for dx, dy in N4:
                wrap_put(cv, x + dx, y + dy, PALE[5])
    for (x, y) in ((8, 7), (14, 14), (9, 13)):
        wrap_put(cv, x, y, WGOLD[4])
    return cv


def starstone_bricks():
    """Stone-brick layout (16x8 bricks, offset by 8) in polished starstone with
    bevelled edges and a few embedded star specks."""
    cv = stone(STAR_TONES, 223, [0.2, 0.45, 0.72, 0.9], cx=4, cy=4, grain=0.14)
    mortar = NAVY[0]
    for course in range(2):
        y0 = course * 8
        seam = 0 if course == 0 else 8
        # mortar: bottom row of the course + head joint
        cv.hline(0, 15, y0 + 7, mortar)
        for y in range(y0, y0 + 7):
            cv.put(seam, y, mortar)
        # bevel: lit top row + left column, dark bottom row + right column
        for x in range(16):
            lx = (x - seam) % 16
            if lx == 0:
                continue
            cv.put(x, y0, NAVY[6] if lx < 13 else NAVY[5])
            cv.put(x, y0 + 6, NAVY[2] if lx > 2 else NAVY[3])
        for y in range(y0, y0 + 7):
            cv.put((seam + 1) % 16, y, NAVY[6] if y < y0 + 5 else NAVY[5])
            cv.put((seam + 15) % 16, y, NAVY[2])
        cv.put((seam + 1) % 16, y0 + 6, NAVY[4])
        cv.put((seam + 15) % 16, y0, NAVY[4])
    # chipped corner + star specks
    for (x, y, c) in ((5, 3, '#d8e6ff'), (12, 11, '#e8cc7a'), (11, 2, NAVY[7]), (3, 12, '#a8c4f4'),
                      (6, 10, NAVY[7])):
        cv.put(x, y, c)
    return cv


def ore_cluster(cv, pts, pal):
    """pal: (shadow, mid, light, bright). pts: list of (x, y, level 0-3)."""
    s = set((x, y) for x, y, _ in pts)
    for x, y, lv in pts:
        wrap_put(cv, x, y, pal[lv])
    for x, y, lv in pts:
        for dx, dy in ((1, 0), (0, 1), (1, 1)):
            if (x + dx, y + dy) not in s:
                q = cv.get((x + dx) % 16, (y + dy) % 16)
                if lum(q) < 120:
                    wrap_put(cv, x + dx, y + dy, NAVY[1])


def stardust_ore():
    cv = starstone_base()
    gold = (WGOLD[1], WGOLD[3], WGOLD[4], '#ffffff')
    blue = (PALE[1], PALE[3], PALE[4], '#ffffff')
    ore_cluster(cv, [(2, 2, 1), (3, 2, 2), (3, 3, 1), (4, 3, 3), (2, 3, 0)], gold)
    ore_cluster(cv, [(10, 3, 1), (11, 3, 2), (11, 4, 3), (12, 4, 1), (10, 4, 0), (12, 5, 1)], blue)
    ore_cluster(cv, [(6, 8, 2), (7, 8, 3), (7, 9, 1), (6, 9, 1), (8, 9, 0)], gold)
    ore_cluster(cv, [(13, 11, 2), (14, 11, 1), (13, 12, 1), (12, 12, 3)], gold)
    ore_cluster(cv, [(3, 11, 1), (4, 11, 3), (4, 12, 2), (5, 12, 1), (3, 12, 0), (4, 13, 1)], blue)
    ore_cluster(cv, [(9, 14, 2), (10, 14, 1), (9, 15, 1)], blue)
    # glitter
    for (x, y) in ((7, 5), (14, 7), (1, 8), (11, 15)):
        cv.put(x, y, '#e8f4ff')
    return cv


def star_gate_frame():
    """Black obsidian-like frame block with a white-gold star inlay."""
    tones = ['#05050c', '#0a0a17', '#101024', '#181833', '#222245']
    cv = stone(tones, 241, [0.25, 0.5, 0.75, 0.92], cx=4, cy=4, grain=0.25)
    # bevelled border
    for i in range(16):
        cv.put(i, 0, '#2a2a52')
        cv.put(0, i, '#2a2a52')
        cv.put(i, 15, '#030308')
        cv.put(15, i, '#030308')
    # thin white-gold inlay frame (inset 2)
    for i in range(3, 13):
        cv.put(i, 2, WGOLD[4])
        cv.put(2, i, WGOLD[4])
        cv.put(i, 13, WGOLD[2])
        cv.put(13, i, WGOLD[2])
    for (x, y, c) in ((2, 2, WGOLD[5]), (13, 2, WGOLD[3]), (2, 13, WGOLD[3]), (13, 13, WGOLD[1])):
        cv.put(x, y, c)
    star = [
        "....a....",
        "....a....",
        "...bWc...",
        "..bWWWc..",
        "aaWWWWWdd",
        "..eWWWf..",
        "...eWf...",
        "....d....",
        "....d....",
    ]
    cv.grid(star, {'a': WGOLD[4], 'b': WGOLD[5], 'c': WGOLD[3], 'd': WGOLD[2], 'e': WGOLD[3],
                   'f': WGOLD[2], 'W': '#fff6dc'}, 4, 4)
    cv.put(8, 8, '#ffffff')
    # tiny inlay stars in the corners
    for (x, y) in ((4, 4), (11, 4), (4, 11), (11, 11)):
        cv.put(x, y, PALE[3])
    return cv


def star_crystal():
    """Cross sprite: a pale-blue and white crystal cluster with star glints."""
    rows = [
        "................",
        ".......W........",
        "......LlM.......",
        "......LlMd......",
        ".....LlWMd......",
        ".....LllMd......",
        ".....LllMd......",
        ".L...LllMdd..d..",
        "LlM..LllMMd.dMd.",
        ".LlM.LllMMd.LMd.",
        ".LlMMLllMMdLlMd.",
        "..lMMLllMMdLlMd.",
        "..LlMLllMMdlMd..",
        "...lMLllMMdMMd..",
        "...LlMllMMMMd...",
        "...LLlMMMMdDd...",
    ]
    pal = {'W': '#ffffff', 'L': '#eaf6ff', 'l': '#b4d8fa', 'M': '#7eaee8', 'd': '#4f7cc8', 'D': '#3a5aa8'}
    cv = Canvas()
    cv.grid(rows, pal)
    # star glints
    for (x, y, c) in ((7, 4, '#ffffff'), (1, 8, '#ffffff'), (12, 9, '#ffffff'), (6, 10, '#fff2c8'),
                      (8, 12, '#d6ecff')):
        cv.put(x, y, c)
    return cv


# ================================================================= ABYSS
AB_TONES = [ABYSS[1], ABYSS[2], ABYSS[3], ABYSS[5], ABYSS[7]]


AB_CUTS = [0.2, 0.42, 0.66, 0.88]


def abyssal_base():
    cv = stone(AB_TONES, 307, AB_CUTS, cx=4, cy=6, grain=0.2)
    # faint violet motes, like dormant sculk
    for (x, y) in ((4, 3), (12, 6), (7, 12), (14, 14)):
        cv.put(x, y, SICK[0])
    return cv


def abyssal_stone():
    return abyssal_base()


# crack network, grown in three stages; each entry (x, y, stage, kind) with
# kind 'c' = glowing core, 'h' = hot centre
CRACK = [
    # stage 1: a short split near the centre
    (7, 6, 1, 'c'), (8, 7, 1, 'c'), (8, 8, 1, 'h'), (9, 9, 1, 'c'), (6, 5, 1, 'c'),
    # stage 2: it runs further and branches
    (5, 4, 2, 'c'), (5, 3, 2, 'c'), (4, 2, 2, 'c'), (10, 10, 2, 'c'), (10, 11, 2, 'c'), (11, 12, 2, 'c'),
    (7, 9, 2, 'c'), (6, 10, 2, 'c'), (5, 10, 2, 'c'), (9, 7, 2, 'c'), (10, 6, 2, 'c'),
    (8, 6, 2, 'h'), (9, 8, 2, 'h'),
    # stage 3: a wide glowing rift with long branches
    (3, 1, 3, 'c'), (3, 0, 3, 'c'), (12, 13, 3, 'c'), (12, 14, 3, 'c'), (13, 15, 3, 'c'),
    (4, 11, 3, 'c'), (3, 12, 3, 'c'), (2, 12, 3, 'c'), (11, 5, 3, 'c'), (12, 5, 3, 'c'), (13, 4, 3, 'c'),
    (14, 4, 3, 'c'), (2, 6, 3, 'c'), (3, 6, 3, 'c'), (4, 5, 3, 'c'), (1, 7, 3, 'c'),
    (11, 9, 3, 'c'), (12, 9, 3, 'c'), (13, 10, 3, 'c'),
    (7, 7, 3, 'h'), (6, 6, 3, 'h'), (9, 10, 3, 'h'), (7, 8, 3, 'h'), (8, 9, 3, 'h'), (5, 5, 3, 'c'),
    (6, 4, 3, 'c'), (10, 9, 3, 'c'), (11, 11, 3, 'c'),
]


def abyssal_crack(stage):
    cv = abyssal_base()
    pts = [(x, y, k) for (x, y, s, k) in CRACK if s <= stage]
    core = set((x, y) for x, y, _ in pts)
    # glow bleeding into the stone (stronger with larger cracks)
    bleed = {1: 0.0, 2: 0.22, 3: 0.4}[stage]
    if bleed:
        for x, y, _ in pts:
            for dx, dy in N8:
                q = (x + dx, y + dy)
                if q not in core:
                    wrap_blend(cv, q[0], q[1], MAGENTA[2], bleed * (0.6 if abs(dx) + abs(dy) == 2 else 1))
    # dark lip on the lower-right side of the crack (depth)
    for x, y, _ in pts:
        for dx, dy in ((1, 0), (0, 1)):
            q = (x + dx, y + dy)
            if q not in core:
                wrap_put(cv, q[0], q[1], ABYSS[0])
    hot_col = {1: MAGENTA[4], 2: MAGENTA[5], 3: MAGENTA[6]}[stage]
    core_col = {1: MAGENTA[2], 2: MAGENTA[3], 3: MAGENTA[4]}[stage]
    for x, y, k in pts:
        wrap_put(cv, x, y, hot_col if k == 'h' else core_col)
    if stage == 3:
        wrap_put(cv, 8, 8, '#ffffff')
        wrap_put(cv, 7, 7, '#ffffff')
    return cv


def void_essence_ore():
    """Abyssal stone with clusters of glowing violet void essence, threaded by
    faint veins."""
    cv = abyssal_base()
    pal = [SICK[1], SICK[2], SICK[3], SICK[4], '#f0dcff']
    veins = [(5, 4), (6, 5), (7, 6), (9, 10), (10, 11), (12, 3), (13, 2), (2, 9), (1, 10)]
    for x, y in veins:
        wrap_put(cv, x, y, SICK[1])
    clusters = [
        [(2, 2, 2), (3, 2, 3), (3, 3, 4), (4, 3, 2), (2, 3, 1), (3, 4, 1)],
        [(10, 4, 2), (11, 4, 3), (11, 5, 2), (10, 5, 1), (12, 5, 1)],
        [(7, 7, 2), (8, 7, 3), (8, 8, 4), (9, 8, 3), (7, 8, 1), (8, 9, 1), (9, 9, 2)],
        [(3, 11, 2), (4, 11, 3), (4, 12, 2), (3, 12, 1), (5, 12, 1)],
        [(12, 12, 2), (13, 12, 3), (13, 13, 4), (14, 13, 2), (12, 13, 1), (13, 14, 1)],
        [(14, 8, 2), (15, 8, 1), (14, 9, 1)],
    ]
    for cl in clusters:
        s = set((x, y) for x, y, _ in cl)
        for x, y, lv in cl:
            for dx, dy in N8:
                q = (x + dx, y + dy)
                if q not in s:
                    wrap_blend(cv, q[0], q[1], SICK[2], 0.3 if abs(dx) + abs(dy) == 1 else 0.15)
        for x, y, lv in cl:
            for dx, dy in ((1, 0), (0, 1)):
                q = (x + dx, y + dy)
                if q not in s:
                    wrap_put(cv, q[0], q[1], ABYSS[0])
        for x, y, lv in cl:
            wrap_put(cv, x, y, pal[lv])
    for (x, y) in ((3, 3), (8, 8), (13, 13)):
        wrap_put(cv, x, y, MAGENTA[5])
    return cv


def imperial_barrier():
    """Translucent magenta energy field: one crisp hexagon per block in a
    tiling honeycomb (alpha 100-160)."""
    line = set()
    for y, pairs in ((0, (6, 8)), (1, (4, 10)), (2, (2, 12)), (3, (0, 14))):
        for x0 in pairs:
            line.update({(x0, y), (x0 + 1, y)})
    for y in range(4, 8):
        line.update({(15, y), (0, y)})
    for y, pairs in ((8, (0, 14)), (9, (2, 12)), (10, (4, 10)), (11, (6, 8))):
        for x0 in pairs:
            line.update({(x0, y), (x0 + 1, y)})
    for y in range(12, 16):
        line.update({(7, y), (8, y)})
    nodes = {(7, 0), (8, 0), (15, 3), (0, 3), (15, 8), (0, 8), (7, 11), (8, 11), (7, 15), (8, 15),
             (15, 4), (0, 4), (15, 7), (0, 7), (7, 12), (8, 12)}

    def dist_to_line(x, y):
        best = 99
        for (lx, ly) in line:
            dx = min(abs(x - lx), 16 - abs(x - lx))
            dy = min(abs(y - ly), 16 - abs(y - ly))
            best = min(best, max(dx, dy))
        return best

    cv = Canvas()
    for y in range(16):
        for x in range(16):
            if (x, y) in line:
                c, a = ('#ffd6fb', 160) if (x, y) in nodes else ('#ff6ef0', 150)
            else:
                d = dist_to_line(x, y)
                if d == 1:
                    c, a = '#d23ad6', 128
                elif d == 2:
                    c, a = '#a826c0', 112
                else:
                    c, a = '#8418a8', 100
            cv.put(x, y, with_alpha(c, a))
    # a few sparks drifting in the field
    for (x, y) in ((4, 6), (11, 13), (12, 5)):
        cv.put(x, y, with_alpha('#ffb4f6', 140))
    return cv


PORTAL_FRAMES = 32


def periodic_field(x, y, t, terms):
    v = 0.0
    for a, kx, ky, kt, ph in terms:
        v += a * math.sin(2 * math.pi * (kx * x / 16 + ky * y / 16 + kt * t) + ph)
    return v


def star_portal():
    """Animated strip (16 x 16*N): luminous nebula filaments swirling through a
    starfield; tiles in space and loops in time."""
    N = PORTAL_FRAMES
    strip = Canvas(16, 16 * N)
    pal = ['#04051a', '#090c2c', '#121848', '#1e2a6e', '#34409a', '#5a5cc4', '#8c86e8', '#cfe0ff']
    terms = [(1.0, 1, 0, 0, 0.3), (0.9, 0, 1, 0, 1.7), (0.7, 1, 1, 0, 2.9), (0.6, 1, -1, 0, 0.4)]
    r = rng(401)
    stars = []
    for i in range(11):
        sx, sy = r.random() * 16, r.random() * 16
        vx, vy = [(1, 1), (1, 0), (0, 1), (1, -1), (-1, 1)][i % 5]
        stars.append((sx, sy, vx, vy, r.random(), i % 3 == 0))
    for k in range(N):
        t = k / N
        cv = Canvas()
        for y in range(16):
            for x in range(16):
                a1 = 2 * math.pi * t
                u = x + 3.0 * math.sin(2 * math.pi * y / 16 + a1) + 1.5 * math.sin(2 * math.pi * (x + y) / 16 - a1)
                v = y + 3.0 * math.sin(2 * math.pi * x / 16 - a1) + 1.5 * math.cos(2 * math.pi * (x - y) / 16 + a1)
                f = periodic_field(u, v, t, terms) / 3.2
                ridge = max(0.0, 1 - abs(f) * 2.2) ** 2.2
                glow = 0.25 + 0.25 * math.sin(2 * math.pi * (x / 16 + y / 16) + a1)
                val = ridge * 0.85 + glow * 0.3
                val += (BAYER4[y % 4, x % 4] - 0.5) * 0.1
                idx = int(max(0, min(6, val * 7)))
                cv.put(x, y, with_alpha(pal[idx], 240 if idx < 2 else 250))
        for sx, sy, vx, vy, ph, big in stars:
            x = int(math.floor(sx + vx * 16 * t)) % 16
            y = int(math.floor(sy + vy * 16 * t)) % 16
            tw = 0.5 + 0.5 * math.sin(2 * math.pi * (2 * t + ph))
            col = '#ffffff' if tw > 0.5 else '#c8dcff' if tw > 0.2 else '#8090e0'
            cv.put(x, y, col)
            if big and tw > 0.45:
                for dx, dy in N4:
                    wrap_put(cv, x + dx, y + dy, '#a8c0ff' if tw > 0.75 else '#5c68c8')
        strip.a[k * 16:(k + 1) * 16] = cv.a
    return strip


TEXTURES = {
    'starstone': starstone, 'starlit_starstone': starlit_starstone, 'starstone_bricks': starstone_bricks,
    'stardust_ore': stardust_ore, 'star_gate_frame': star_gate_frame,
    'abyssal_stone': abyssal_stone, 'abyssal_stone_crack1': lambda: abyssal_crack(1),
    'abyssal_stone_crack2': lambda: abyssal_crack(2), 'abyssal_stone_crack3': lambda: abyssal_crack(3),
    'void_essence_ore': void_essence_ore, 'imperial_barrier': imperial_barrier,
    'star_crystal': star_crystal,
}


def main():
    out, tiles = [], []
    for name, fn in TEXTURES.items():
        cv = fn()
        cv.save(f'textures/block/{name}.png')
        out.append((name, cv.pil()))
        if name != 'star_crystal':
            tiles.append((name, tiled(cv.pil(), 3)))
    print(sheet(out, 'blocks.png', cols=6))
    print(sheet(tiles, 'blocks_tiled.png', scale=3, cols=4))
    strip = star_portal()
    strip.save('textures/block/star_portal.png')
    with open(os.path.join(ASSETS, 'textures', 'block', 'star_portal.png.mcmeta'), 'w', newline='\n') as f:
        f.write('{\n  "animation": {\n    "frametime": 2\n  }\n}\n')
    frames = [(f'f{k}', strip.pil().crop((0, k * 16, 16, k * 16 + 16))) for k in range(0, PORTAL_FRAMES, 2)]
    print(sheet(frames, 'star_portal_frames.png', cols=8))
    print(sheet([(f'f{k}', tiled(strip.pil().crop((0, k * 16, 16, k * 16 + 16)), 3)) for k in (0, 8, 16)],
                'star_portal_tiled.png', scale=4, cols=3))


if __name__ == '__main__':
    main()
