"""Reusable block-material builders (vanilla-style, tileable, no outlines)."""
from common import *

# --------------------------------------------------------------- palettes
DARK_WOOD = ['#24160a', '#2f1d0d', '#3a2411', '#462d15', '#53381a', '#61431f', '#704f26']
OAK = ['#5a4424', '#6f5430', '#86663a', '#9a7845', '#ad8a52', '#bf9b5e', '#cfae70']
SPRUCE = ['#3e2a16', '#4f3820', '#5f4628', '#6f5230', '#7d5e38', '#8b6a40']
GOLD = ['#5c3a06', '#8a5a0c', '#b8801a', '#dca528', '#f2c63c', '#ffe27a', '#fff6c4']
BRASS = ['#4a3410', '#76561c', '#a07a2a', '#c49a3a', '#e0bc5a', '#f6dc8a']
STEEL = ['#1b1e23', '#24282e', '#2e333a', '#393f47', '#454c55', '#545c66', '#6a737e', '#8994a0']
STONE_DARK = ['#1f2026', '#2a2b32', '#34363e', '#40424a', '#4c4e57', '#5a5c65']
OBSIDIAN = ['#06030b', '#0f0a1a', '#181026', '#221733', '#2e1f44', '#3e2a58', '#58407a']
PURPUR = ['#7a5279', '#906590', '#a072a0', '#ac7bac', '#b98bb9', '#c7a2c7', '#d8bcd8']
AMETHYST = ['#3c2470', '#5d3a9a', '#7a5bb5', '#9a72dc', '#b88af0', '#d8a8f8', '#fde0f2']
PACKED_ICE = ['#6f97e6', '#7ca5f4', '#88b0f8', '#96bcfe', '#a8c8ff', '#bcd6ff', '#d6e6ff']
BLUE_ICE = ['#4f80e8', '#5f91f4', '#6b9dfb', '#78aafe', '#8eb8fe', '#a9c8ff', '#c8dcff']
PRISMARINE = ['#2f6a58', '#41816a', '#4c9180', '#5ea496', '#72b4a8', '#8cc4b8', '#a8d6cc']
DARK_PRISMARINE = ['#1e322b', '#273e36', '#2f4c40', '#36584a', '#3f6656', '#4a7766', '#5a8a78']
CALCITE = ['#9e9e9c', '#b3b3b1', '#c6c6c1', '#d6d8d3', '#e4e5df', '#f0f2ee', '#ffffff']
DEEPSLATE = ['#25252c', '#2f2f37', '#3a3a41', '#46464b', '#515155', '#606062', '#737373']
COPPER = ['#6a3220', '#8a442c', '#a2563a', '#b86446', '#cc7454', '#df8668', '#f0a488']
VERDIGRIS = ['#3e7a66', '#58a084', '#7cc0a2']
BLACKSTONE = ['#120c0e', '#1a1216', '#23191e', '#2c2329', '#363039', '#423d48', '#524d58']
BASALT = ['#181f28', '#22262f', '#2c2e38', '#363844', '#42434e', '#504f57', '#626168']
LAVA = ['#6a1404', '#a8280a', '#d24a0c', '#f0701a', '#ff9a2a', '#ffc44a', '#fff09a']
RED_CLOTH = ['#5e1416', '#7e1c1e', '#9a2422', '#b22e28', '#c83c32', '#dc5444']
CREAM_CLOTH = ['#a89878', '#c4b490', '#d8caa6', '#e8dcbc', '#f4ecd2', '#fffaea']


# --------------------------------------------------------------- primitives
def noise_region(cv, x0, y0, x1, y1, pal, seed, cells=4, octaves=2, dither=0.0, bias=0.0, contrast=1.0,
                 tile=16):
    """Fill an inclusive rect with quantized tileable noise from pal."""
    n = tile_noise(tile, tile, cells, seed, octaves)
    n = np.clip((n - 0.5) * contrast + 0.5 + bias, 0, 1)
    k = len(pal)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            v = n[y % tile, x % tile] * (k - 1)
            if dither:
                v += (BAYER4[y % 4, x % 4] - 0.5) * dither
            cv.put(x, y, pal[int(round(min(max(v, 0), k - 1)))])


def speckle(cv, pts_or_count, col, seed=0, region=(0, 0, 15, 15), avoid=None):
    if isinstance(pts_or_count, int):
        r = rng(seed)
        x0, y0, x1, y1 = region
        pts = [(int(r.integers(x0, x1 + 1)), int(r.integers(y0, y1 + 1))) for _ in range(pts_or_count)]
    else:
        pts = pts_or_count
    for x, y in pts:
        if avoid and avoid(x, y):
            continue
        cv.put(x, y, col)


def bevel(cv, x0, y0, x1, y1, hi, lo, corner=None):
    """1px light top/left edge, dark bottom/right edge (inclusive rect)."""
    cv.hline(x0, x1, y0, hi)
    cv.vline(x0, y0, y1, hi)
    cv.hline(x0, x1, y1, lo)
    cv.vline(x1, y0, y1, lo)
    if corner:
        cv.put(x1, y0, corner)
        cv.put(x0, y1, corner)


def inset(cv, x0, y0, x1, y1, hi, lo, corner=None):
    """Recessed: dark top/left, light bottom/right."""
    bevel(cv, x0, y0, x1, y1, lo, hi, corner)


def planks(pal, seed, w=16, h=16, plank_h=4, offsets=(0, 8, 4, 12), seam=0, grain=True, polish=False):
    """Vanilla-like horizontal planks. pal dark->light; pal[seam] is the seam."""
    cv = Canvas(w, h)
    r = rng(seed)
    nplanks = h // plank_h
    for p in range(nplanks):
        y0 = p * plank_h
        base = 3 + (p % 2)  # alternate plank tone
        base = min(base, len(pal) - 2)
        for y in range(y0, y0 + plank_h):
            for x in range(w):
                cv.put(x, y, pal[base])
        # grain streaks
        if grain:
            for _ in range(3):
                gy = y0 + 1 + int(r.integers(0, plank_h - 1))
                gx = int(r.integers(0, w))
                ln = int(r.integers(3, 7))
                tone = pal[base - 1] if r.random() < 0.6 else pal[base + 1]
                for i in range(ln):
                    cv.put((gx + i) % w, gy, tone)
        # seam at the bottom row of the plank + end joint
        cv.hline(0, w - 1, y0 + plank_h - 1, pal[seam + 1])
        jx = offsets[p % len(offsets)] % w
        cv.vline(jx, y0, y0 + plank_h - 2, pal[seam + 1])
        # top-edge light catch
        if polish:
            for x in range(w):
                if (x + p * 5) % 7 in (0, 1, 2):
                    cv.put(x, y0, pal[base + 1])
            cv.put((jx + 1) % w, y0, pal[min(len(pal) - 1, base + 2)])
    return cv


def vgrain_planks(pal, seed, w=16, h=16, plank_w=4, offsets=(0, 6, 11, 3)):
    """Vertical planks (rotate of planks)."""
    p = planks(pal, seed, w=h, h=w, plank_h=plank_w, offsets=offsets)
    cv = Canvas(w, h)
    cv.a = np.transpose(p.a, (1, 0, 2)).copy()
    return cv


def crack_line(cv, pts, core, edge=None):
    """Draw a polyline of pixels (list of (x,y)); optional darker edge right/below."""
    for x, y in pts:
        cv.put(x, y, core)
    if edge:
        s = set(pts)
        for x, y in pts:
            for dx, dy in ((1, 0), (0, 1)):
                if (x + dx, y + dy) not in s and cv.inb(x + dx, y + dy):
                    cv.put(x + dx, y + dy, edge)


def star4(cv, cx, cy, pal, big=False):
    """Small embossed 4-point star (odd centre). pal: (shadow, mid, light, bright)."""
    if big:
        g = [
            "...a...",
            "...a...",
            "..LaM..",
            "aaaWbbb",
            "..MbD..",
            "...b...",
            "...b...",
        ]
    else:
        g = [
            "..a..",
            ".LaM.",
            "aaWbb",
            ".MbD.",
            "..b..",
        ]
    sh, mid, lt, br = pal
    n = len(g)
    cv.grid(g, {'a': br, 'L': lt, 'M': mid, 'b': mid, 'D': sh, 'W': '#ffffff'}, cx - n // 2, cy - n // 2)
