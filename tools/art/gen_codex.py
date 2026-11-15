"""Celestial Codex textures: the book GUI (textures/gui/codex.png) and the item icon.

Book: night-blue leather cover with a gold trim (the same palette as the container
GUIs), two parchment pages with stacked page edges and a shaded fold. Sprites to the
right of the book (x >= 304) are the navigation buttons, slots, arrows and medallions;
their positions must match GuideScreen.
"""
from common import *

OUT = '#090a18'
GOLD_HI = '#F2D27A'
GOLD = '#C9A54C'
GOLD_MID = '#A8873A'
GOLD_SH = '#7A5C22'
LEATHER = ['#12162e', '#171c3a', '#1c2244', '#21284e', '#272e58']
SPECK = '#3a4174'
SPECK_HI = '#5d66a6'

PAPER = ['#b39867', '#c4ab78', '#d4bd8a', '#e0cc9e', '#e9d8ae', '#efe1bb', '#f3e7c7', '#f6ecd0']
EDGE_LIGHT = '#efe3c2'
EDGE_DARK = '#c7b083'
FOLD = '#a88d5c'
INK = '#3B2A1A'
INK_SOFT = '#7A6446'

BOOK_W, BOOK_H = 300, 200
L_PAGE = (8, 5, 149, 193)    # x0, y0, x1, y1 inclusive
R_PAGE = (150, 5, 291, 193)


def leather(cv):
    n = tile_noise(BOOK_W, BOOK_H, 24, seed=71, octaves=3, persistence=0.55)
    ys, xs = np.mgrid[0:BOOK_H, 0:BOOK_W]
    # darker toward the outer edge, a little lighter on the spine
    edge = np.minimum.reduce([xs, ys, BOOK_W - 1 - xs, BOOK_H - 1 - ys]) / 10.0
    v = n * 0.75 + np.clip(edge, 0, 1) * 0.35 - 0.1
    spine = np.exp(-((xs - 149.5) / 6.0) ** 2) * 0.25
    v = np.clip(v + spine, 0, 1)
    for y in range(BOOK_H):
        for x in range(BOOK_W):
            t = v[y, x] * (len(LEATHER) - 1) + (BAYER4[y % 4, x % 4] - 0.5) * 0.8
            cv.put(x, y, LEATHER[int(min(max(round(t), 0), len(LEATHER) - 1))])
    # cut corners + outline
    for x, y in ((0, 0), (1, 0), (0, 1), (BOOK_W - 1, 0), (BOOK_W - 2, 0), (BOOK_W - 1, 1),
                 (0, BOOK_H - 1), (1, BOOK_H - 1), (0, BOOK_H - 2),
                 (BOOK_W - 1, BOOK_H - 1), (BOOK_W - 2, BOOK_H - 1), (BOOK_W - 1, BOOK_H - 2)):
        cv.put(x, y, TRANSPARENT)
    cv.hline(2, BOOK_W - 3, 0, OUT)
    cv.hline(2, BOOK_W - 3, BOOK_H - 1, OUT)
    cv.vline(0, 2, BOOK_H - 3, OUT)
    cv.vline(BOOK_W - 1, 2, BOOK_H - 3, OUT)
    for x, y in ((1, 1), (BOOK_W - 2, 1), (1, BOOK_H - 2), (BOOK_W - 2, BOOK_H - 2)):
        cv.put(x, y, OUT)


def gold_trim(cv):
    """Gold line 3px inside the cover edge, lit from the top-left, with corner studs."""
    x0, y0, x1, y1 = 3, 2, BOOK_W - 4, BOOK_H - 3
    cv.hline(x0 + 1, x1 - 1, y0, GOLD_HI)
    cv.vline(x0, y0 + 1, y1 - 1, GOLD_HI)
    cv.hline(x0 + 1, x1 - 1, y1, GOLD_SH)
    cv.vline(x1, y0 + 1, y1 - 1, GOLD_SH)
    for (cx, cy) in ((x0 + 1, y0 + 1), (x1 - 1, y0 + 1), (x0 + 1, y1 - 1), (x1 - 1, y1 - 1)):
        for dx, dy, c in ((0, 0, GOLD_HI), (1, 0, GOLD), (0, 1, GOLD), (1, 1, GOLD_MID),
                          (-1, 0, GOLD_MID), (0, -1, GOLD_MID)):
            cv.put(cx + dx, cy + dy, c)


def specks(cv, seed):
    r = rng(seed)
    for _ in range(140):
        x, y = int(r.integers(1, BOOK_W - 1)), int(r.integers(1, BOOK_H - 1))
        inside = (L_PAGE[0] - 2 <= x <= R_PAGE[2] + 2) and (L_PAGE[1] - 2 <= y <= L_PAGE[3] + 2)
        if inside or cv.get(x, y)[3] == 0 or cv.get(x, y) in (hexc(GOLD_HI), hexc(GOLD_SH), hexc(OUT)):
            continue
        cv.put(x, y, SPECK_HI if r.random() < 0.25 else SPECK)


def page(cv, box, left_side, seed):
    x0, y0, x1, y1 = box
    w, h = x1 - x0 + 1, y1 - y0 + 1
    n = tile_noise(w, h, 18, seed=seed, octaves=3, persistence=0.6)
    ys, xs = np.mgrid[0:h, 0:w]
    outer = xs if left_side else (w - 1 - xs)          # distance from the outer edge
    fold = (w - 1 - xs) if left_side else xs           # distance from the fold
    v = 0.86 + (n - 0.5) * 0.18
    v -= np.clip(1 - outer / 8.0, 0, 1) ** 1.5 * 0.28  # outer edge darker
    v -= np.clip(1 - ys / 7.0, 0, 1) ** 1.5 * 0.18     # top edge
    v -= np.clip(1 - (h - 1 - ys) / 7.0, 0, 1) ** 1.5 * 0.2  # bottom edge
    v -= np.clip(1 - fold / 16.0, 0, 1) ** 1.8 * 0.78  # shadow into the fold
    v = np.clip(v, 0, 1)
    for y in range(h):
        for x in range(w):
            t = v[y, x] * (len(PAPER) - 1) + (BAYER4[(y + y0) % 4, (x + x0) % 4] - 0.5) * 0.7
            cv.put(x0 + x, y0 + y, PAPER[int(min(max(round(t), 0), len(PAPER) - 1))])
    # fibres: a few faint darker flecks away from the text area
    r = rng(seed + 5)
    for _ in range(70):
        fx, fy = int(r.integers(2, w - 2)), int(r.integers(2, h - 2))
        c = cv.get(x0 + fx, y0 + fy)
        cv.put(x0 + fx, y0 + fy, scale(c, 0.965))
    # stacked page edges on the outer side and bottom
    ex = x0 if left_side else x1
    step = 1 if left_side else -1
    for k in range(3):
        col = EDGE_DARK if k % 2 == 0 else EDGE_LIGHT
        cv.vline(ex + k * step, y0 + 2 + k, y1 - 1, col)
    for k in range(3):
        col = EDGE_DARK if k % 2 == 0 else EDGE_LIGHT
        if left_side:
            cv.hline(x0 + 3 - k, x1 - 1, y1 - k, col)
        else:
            cv.hline(x0 + 1, x1 - 3 + k, y1 - k, col)
    # fold line
    fx = x1 if left_side else x0
    cv.vline(fx, y0, y1 - 3, FOLD)
    # top-outer corner flourish
    cx = x0 + 6 if left_side else x1 - 6
    d = 1 if left_side else -1
    for i in range(6):
        cv.blend(cx + i * d, y0 + 4, GOLD_MID, 0.55)
        cv.blend(cx, y0 + 4 + i, GOLD_MID, 0.55)
    cv.blend(cx + d, y0 + 5, GOLD, 0.7)


def binding(cv):
    # stitched spine where the pages meet the cover, top and bottom
    for y in list(range(1, 5)) + list(range(194, 199)):
        for x in range(147, 153):
            cv.put(x, y, mix(LEATHER[0], OUT, 0.4))
        cv.put(149, y, GOLD_SH)
        cv.put(150, y, GOLD_MID)


# ------------------------------------------------------------------ sprites
def arrow(cv, ox, oy, hover, flip):
    body = GOLD_HI if hover else GOLD
    hi = '#FFF2B8' if hover else GOLD_HI
    rows = [
        "..........##......",
        "..........#B#.....",
        "##########BBB#....",
        "#HHHHHHHHHHHBB#...",
        "#BBBBBBBBBBBBBB#..",
        "#BBBBBBBBBBBBBB#..",
        "#SSSSSSSSSSSSS#...",
        "##########SSS#....",
        "..........#S#.....",
        "..........##......",
    ]
    pal = {'#': INK, 'B': body, 'H': hi, 'S': GOLD_MID if hover else GOLD_SH}
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch in pal:
                x = (17 - i) if flip else i
                cv.put(ox + x, oy + j, pal[ch])


def home_star(cv, ox, oy, hover):
    rows = [
        "......#......",
        ".....#H#.....",
        ".....#H#.....",
        "....#HBB#....",
        "..##HBBBS##..",
        "##HHBBBBBSS##",
        "#HBBBBWBBBBS#",
        "##BBBBBBBSS##",
        "..##BBBSS##..",
        "....#BBS#....",
        ".....#S#.....",
        ".....#S#.....",
        "......#......",
    ]
    pal = {'#': INK, 'H': '#FFF2B8' if hover else GOLD_HI, 'B': GOLD_HI if hover else GOLD,
           'S': GOLD if hover else GOLD_SH, 'W': '#FFFFFF' if hover else '#FFF2B8'}
    cv.grid(rows, pal, ox, oy)


def slot(cv, ox, oy):
    cv.rect(ox, oy, ox + 17, oy + 17, '#e3d2a8')
    cv.hline(ox, ox + 16, oy, '#a58e62')
    cv.vline(ox, oy, oy + 16, '#a58e62')
    cv.hline(ox + 1, ox + 17, oy + 17, '#fbf3dd')
    cv.vline(ox + 17, oy + 1, oy + 17, '#fbf3dd')
    cv.put(ox + 17, oy, '#cdb98f')
    cv.put(ox, oy + 17, '#cdb98f')
    cv.rect(ox + 1, oy + 1, ox + 16, oy + 1, '#d6c296')
    cv.rect(ox + 1, oy + 1, ox + 1, oy + 16, '#d6c296')


def big_arrow(cv, ox, oy):
    rows = [
        "..............#.......",
        "..............##......",
        "..............#F#.....",
        "..............#FF#....",
        "###############FFF#...",
        "#FFFFFFFFFFFFFFFFFF#..",
        "#FFFFFFFFFFFFFFFFFFF#.",
        "#FFFFFFFFFFFFFFFFFFFF#",
        "#FFFFFFFFFFFFFFFFFFF#.",
        "#FFFFFFFFFFFFFFFFFF#..",
        "###############FFF#...",
        "..............#FF#....",
        "..............#F#.....",
        "..............##......",
        "..............#.......",
    ]
    cv.grid(rows, {'#': INK_SOFT, 'F': '#c9b386'}, ox, oy)


def small_arrow(cv, ox, oy):
    rows = [
        "......#...",
        "......##..",
        "#######F#.",
        "#FFFFFFFF#",
        "#FFFFFFFFF",
        "#FFFFFFFF#",
        "#######F#.",
        "......##..",
        "......#...",
    ]
    cv.grid(rows, {'#': INK_SOFT, 'F': '#c9b386'}, ox, oy)


def plus(cv, ox, oy):
    cv.rect(ox + 3, oy, ox + 3, oy + 6, INK_SOFT)
    cv.rect(ox, oy + 3, ox + 6, oy + 3, INK_SOFT)


def check(cv, ox, oy):
    rows = [
        ".......##",
        "......#G#",
        ".....#GG#",
        "##..#GG#.",
        "#G##GG#..",
        "#GGGG#...",
        ".#GG#....",
        "..##.....",
        ".........",
    ]
    cv.grid(rows, {'#': '#16331a', 'G': '#5fd35f'}, ox, oy)
    cv.put(ox + 7, oy + 1, '#9af29a')
    cv.put(ox + 6, oy + 2, '#9af29a')


def ornament(cv, ox, oy):
    w = 100
    mid = w // 2
    for x in range(w):
        d = abs(x - mid) / mid
        a = max(0.0, 1 - d ** 1.4)
        if a <= 0.05:
            continue
        cv.blend(ox + x, oy + 2, GOLD_MID, min(1.0, a * 1.1))
    # centre diamond and side dots
    for dy, half in ((0, 0), (1, 1), (2, 2), (3, 1), (4, 0)):
        for dx in range(-half, half + 1):
            cv.put(ox + mid + dx, oy + dy, GOLD_HI if dx <= 0 and dy <= 2 else GOLD)
    for dx in (-8, 8):
        cv.put(ox + mid + dx, oy + 2, GOLD)
        cv.put(ox + mid + dx, oy + 1, GOLD_HI)
        cv.put(ox + mid + dx, oy + 3, GOLD_SH)
    for dx in (-15, 15):
        cv.put(ox + mid + dx, oy + 2, GOLD_HI)


def medal(cv, ox, oy, gold):
    ring_hi, ring, ring_sh = (GOLD_HI, GOLD, GOLD_SH) if gold else ('#cbb88f', '#a8936a', '#857049')
    inner = '#f6e9bf' if gold else '#e3d2a8'
    m = np.zeros((18, 18), bool)
    for y in range(18):
        for x in range(18):
            m[y, x] = abs(x - 8.5) + abs(y - 8.5) <= 12.5 and max(abs(x - 8.5), abs(y - 8.5)) <= 8.5
    for y in range(18):
        for x in range(18):
            if not m[y, x]:
                continue
            edge = not (0 < y < 17 and 0 < x < 17 and m[y - 1, x] and m[y + 1, x] and m[y, x - 1] and m[y, x + 1])
            if edge:
                cv.put(ox + x, oy + y, OUT if not gold else '#3b2a1a')
            else:
                cv.put(ox + x, oy + y, inner)
    # ring one pixel inside the outline
    for y in range(1, 17):
        for x in range(1, 17):
            if not m[y, x]:
                continue
            nb = [m[y - 1, x], m[y + 1, x], m[y, x - 1], m[y, x + 1]]
            if all(nb):
                inner_nb = [m[y - 2, x] if y > 1 else False, m[y + 2, x] if y < 16 else False,
                            m[y, x - 2] if x > 1 else False, m[y, x + 2] if x < 16 else False]
                if not all(inner_nb):
                    up_left = (x + y) < 17
                    cv.put(ox + x, oy + y, ring_hi if up_left else ring_sh)
    if gold:
        cv.put(ox + 4, oy + 4, '#fffbe6')
        cv.put(ox + 5, oy + 3, '#fff2b8')


def codex_gui():
    cv = Canvas(512, 256)
    leather(cv)
    gold_trim(cv)
    specks(cv, 9)
    binding(cv)
    page(cv, L_PAGE, True, 31)
    page(cv, R_PAGE, False, 37)
    arrow(cv, 304, 0, False, False)
    arrow(cv, 304, 10, True, False)
    arrow(cv, 322, 0, False, True)
    arrow(cv, 322, 10, True, True)
    home_star(cv, 340, 0, False)
    home_star(cv, 340, 13, True)
    slot(cv, 356, 0)
    big_arrow(cv, 376, 0)
    small_arrow(cv, 400, 0)
    plus(cv, 412, 0)
    check(cv, 420, 0)
    ornament(cv, 304, 24)
    medal(cv, 304, 32, False)
    medal(cv, 322, 32, True)
    return cv


def codex_item():
    """16x16 icon: indigo leather book with a gold-banded spine, a gold star and the page block showing."""
    rows = [
        "................",
        "..############..",
        "..#SshhhhhhhG#P.",
        "..#SshLLLLLLG#P.",
        "..#BBhLLLLLLG#P.",
        "..#SshLL*LLLG#P.",
        "..#SshL*W*LLG#P.",
        "..#Ssh*WWW*LG#P.",
        "..#SshL*W*LLG#P.",
        "..#SshLL*LLLG#P.",
        "..#BBhLLLLLLG#P.",
        "..#SshLLLLLLG#P.",
        "..#SsGGGGGGGG#P.",
        "..############p.",
        "...pppppppppppp.",
        "................",
    ]
    pal = {'#': OUT, 'S': LEATHER[0], 's': LEATHER[2], 'B': GOLD, 'h': GOLD_HI, 'G': GOLD_MID,
           'L': LEATHER[3], '*': GOLD, 'W': GOLD_HI, 'P': '#efe1bb', 'p': '#c7b083'}
    cv = Canvas(16, 16)
    cv.grid(rows, pal)
    # a soft highlight on the leather, upper left
    for x, y in ((7, 3), (8, 3), (7, 4)):
        cv.put(x, y, LEATHER[4])
    cv.put(4, 4, GOLD_HI)
    cv.put(4, 10, GOLD_HI)
    return cv


def main():
    gui = codex_gui()
    print('gui ->', gui.save('textures/gui/codex.png'))
    item = codex_item()
    print('item ->', item.save('textures/item/celestial_codex.png'))
    big = gui.pil().crop((0, 0, 440, 200)).resize((880, 400), Image.NEAREST)
    os.makedirs(PREVIEW, exist_ok=True)
    big.save(os.path.join(PREVIEW, 'codex_gui.png'))
    item.pil().resize((256, 256), Image.NEAREST).save(os.path.join(PREVIEW, 'codex_item.png'))


if __name__ == '__main__':
    main()
