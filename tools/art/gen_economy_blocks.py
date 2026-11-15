"""Economy blocks: bank_counter, shop_stall, titan_anvil, relic_pedestal.

Models are authored facing NORTH (front = -Z). Textures use the vanilla
world-locked uv convention unless an explicit atlas region is given.
"""
from common import *
from materials import *
from blockmodel import el, rot, model, T, emissive

W = DARK_WOOD


# ======================================================================
# BANK COUNTER
# ======================================================================
def polished_wood_rows(cv, y0, y1, seed, pal=W, base=4):
    """Polished single-board wood with long horizontal grain."""
    r = rng(seed)
    for y in range(y0, y1 + 1):
        t = base if (y // 2) % 2 == 0 else base - 1
        for x in range(16):
            cv.put(x, y, pal[t])
    for _ in range((y1 - y0 + 1) * 2):
        y = int(r.integers(y0, y1 + 1))
        x = int(r.integers(0, 16))
        ln = int(r.integers(3, 9))
        tone = pal[base + 1] if r.random() < 0.45 else pal[base - 2]
        for i in range(ln):
            cv.put((x + i) % 16, y, tone)


def bank_top():
    cv = Canvas()
    polished_wood_rows(cv, 0, 15, 11)
    # board seams every 5 rows (boards run along X so counters join seamlessly)
    for y in (5, 10):
        cv.hline(0, 15, y, W[1])
        for x in range(0, 16, 5):
            cv.put((x + y) % 16, y - 1, W[5])
    # front + back: wood lip highlight and gold inlay line
    cv.hline(0, 15, 0, W[6])
    cv.hline(0, 15, 1, GOLD[3])
    for x in range(0, 16, 4):
        cv.put(x, 1, GOLD[5])
    cv.hline(0, 15, 14, GOLD[2])
    cv.hline(0, 15, 15, W[2])
    # polish sheen streaks
    for x, y in ((3, 3), (4, 3), (5, 3), (10, 7), (11, 7), (6, 12), (7, 12)):
        cv.put(x, y, W[6])
    return cv


def bank_trim():
    """Atlas: rows 0-1 gold edge band of the countertop; rows 2-15 dark wood underside."""
    cv = Canvas()
    for x in range(16):
        cv.put(x, 0, GOLD[5] if x % 4 in (1, 2) else GOLD[4])
        cv.put(x, 1, GOLD[2] if x % 4 != 3 else GOLD[1])
    cv.put(2, 0, GOLD[6])
    cv.put(10, 0, GOLD[6])
    for y in range(2, 16):
        for x in range(16):
            cv.put(x, y, W[1] if (x + y * 3) % 9 else W[2])
    return cv


EMBLEM = [  # 8x8 embossed star with a 2px centre (cols 4..11)
    "...hm...",
    "...hm...",
    "..hhmm..",
    "hhhWmmmm",
    "mmmmdddd",
    "..mmdd..",
    "...md...",
    "...md...",
]


def wood_panel_bg(cv, x0, y0, x1, y1, seed):
    """Recessed panel with faint vertical grain."""
    r = rng(seed)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, W[2] if (x * 7 + y // 3) % 5 else W[1])
    for _ in range(4):
        x = int(r.integers(x0, x1 + 1))
        y = int(r.integers(y0, y1 - 1))
        cv.vline(x, y, min(y1, y + 2), W[3])


def bank_front():
    """North face of the lower counter (uv rows 2..15 = y14..y0)."""
    cv = Canvas()
    cv.rect(0, 0, 15, 15, W[3])
    cv.hline(0, 15, 2, W[0])                     # shadow under the overhang
    cv.hline(0, 15, 3, W[4])                     # top rail
    for x in range(16):                          # gold trim strip
        cv.put(x, 4, GOLD[4] if x % 5 else GOLD[5])
    cv.hline(0, 15, 5, W[2])
    # stiles
    for y in range(6, 14):
        cv.put(0, y, W[5])
        cv.put(1, y, W[4])
        cv.put(14, y, W[3])
        cv.put(15, y, W[2])
    # recessed panel
    wood_panel_bg(cv, 3, 7, 12, 12, 3)
    inset(cv, 2, 6, 13, 13, W[5], W[0])
    # embossed gold Aster star
    pal = {'h': GOLD[5], 'm': GOLD[3], 'd': GOLD[2], 'W': '#fffbe0'}
    pts = set()
    for j, row in enumerate(EMBLEM):
        for i, ch in enumerate(row):
            if ch != '.':
                pts.add((4 + i, 6 + j))
    for (x, y) in pts:                           # drop shadow
        q = (x + 1, y + 1)
        if q not in pts and 3 <= q[0] <= 12 and 7 <= q[1] <= 13:
            cv.put(q[0], q[1], W[0])
    cv.grid(EMBLEM, pal, 4, 6)
    # plinth
    for x in range(16):
        cv.put(x, 14, GOLD[3] if x % 5 else GOLD[4])
    cv.hline(0, 15, 15, W[1])
    return cv


def bank_side():
    """East/west faces of the lower counter; front edge at col 2."""
    cv = Canvas()
    cv.rect(0, 0, 15, 15, W[3])
    cv.hline(0, 15, 2, W[0])
    cv.hline(0, 15, 3, W[4])
    for x in range(16):
        cv.put(x, 4, GOLD[4] if x % 5 else GOLD[5])
    cv.hline(0, 15, 5, W[2])
    for y in range(6, 14):
        cv.put(2, y, W[5])
        cv.put(3, y, W[4])
        cv.put(14, y, W[3])
        cv.put(15, y, W[2])
    wood_panel_bg(cv, 5, 7, 12, 12, 5)
    inset(cv, 4, 6, 13, 13, W[5], W[0])
    # small gold diamond stud
    cv.grid([".a.", "abc", ".c."], {'a': GOLD[5], 'b': GOLD[6], 'c': GOLD[2]}, 8, 8)
    for x in range(16):
        cv.put(x, 14, GOLD[3] if x % 5 else GOLD[4])
    cv.hline(0, 15, 15, W[1])
    return cv


def bank_back():
    """South (teller) face: drawers with gold pulls over a cubby of ledgers."""
    cv = Canvas()
    cv.rect(0, 0, 15, 15, W[3])
    cv.hline(0, 15, 2, W[5])
    cv.hline(0, 15, 3, W[2])
    for x0, x1 in ((1, 7), (8, 14)):
        cv.rect(x0, 4, x1, 8, W[4])
        bevel(cv, x0, 4, x1, 8, W[5], W[1])
        mx = (x0 + x1) // 2
        cv.put(mx, 6, GOLD[5])
        cv.put(mx + 1, 6, GOLD[3])
    cv.hline(0, 15, 9, W[2])
    # cubby
    cv.rect(1, 10, 14, 13, W[0])
    cv.hline(1, 14, 10, '#140c05')
    spines = [(2, '#6b1e1e', '#8e2a26'), (3, '#1e4a2e', '#2a6a40'), (4, '#6b1e1e', '#8e2a26'),
              (5, '#22305e', '#33468a')]
    for x, d, l in spines:
        cv.vline(x, 11, 13, d)
        cv.put(x, 11, l)
        cv.put(x, 12, GOLD[3])
    # coin sacks
    cv.grid([".cc.", "cCCc", "cCcc"], {'c': '#6e5a3a', 'C': '#8e7650'}, 9, 11)
    cv.put(10, 10, GOLD[5])
    cv.put(13, 13, GOLD[4])
    cv.put(12, 13, GOLD[3])
    cv.vline(0, 10, 13, W[4])
    cv.vline(15, 10, 13, W[2])
    for x in range(16):
        cv.put(x, 14, GOLD[3] if x % 5 else GOLD[4])
    cv.hline(0, 15, 15, W[1])
    return cv


def bank_bottom():
    return planks(W, 21, polish=False)


def bank_details():
    """Atlas: brass (0-7,0-7), ledger pages (8-15,0-7), ledger cover (0-7,8-15),
    brass pan top (8-15,8-15)."""
    cv = Canvas()
    # brass block
    for y in range(8):
        for x in range(8):
            t = 4 if (x + y) < 5 else 3 if (x + y) < 10 else 2
            cv.put(x, y, BRASS[t])
    for x, y in ((1, 1), (2, 1), (1, 2)):
        cv.put(x, y, BRASS[5])
    # ledger pages: two pages with ruled lines, spine down the middle
    cv.rect(8, 0, 15, 7, '#efe4c4')
    cv.vline(11, 0, 7, '#bfae86')
    cv.vline(12, 0, 7, '#d8c9a2')
    for y in (1, 3, 5):
        cv.hline(8, 10, y, '#8a7a5a')
        cv.hline(13, 15, y, '#8a7a5a')
    cv.put(9, 5, '#a8402e')        # red ink tally
    cv.put(14, 3, GOLD[3])
    cv.hline(8, 15, 7, '#cdbd94')
    # ledger cover: green leather with gold corner
    cv.rect(0, 8, 7, 15, '#1f4a2c')
    cv.hline(0, 7, 8, '#2e6a40')
    cv.hline(0, 7, 15, '#14301c')
    cv.put(0, 9, GOLD[4])
    cv.put(7, 14, GOLD[3])
    # pan top: shallow brass dish
    cv.rect(8, 8, 15, 15, BRASS[3])
    bevel(cv, 8, 8, 15, 15, BRASS[5], BRASS[1])
    cv.rect(10, 10, 13, 13, BRASS[2])
    cv.put(10, 10, BRASS[1])
    cv.put(13, 13, BRASS[4])
    return cv


def bank_counter_model():
    tex = {'particle': T('bank_counter_front'), 'top': T('bank_counter_top'), 'trim': T('bank_counter_trim'),
           'front': T('bank_counter_front'), 'side': T('bank_counter_side'), 'back': T('bank_counter_back'),
           'bottom': T('bank_counter_bottom'), 'detail': T('bank_counter_details')}
    E = []
    # lower counter x0-16 y0-14 z2-16
    E.append(el((0, 0, 2), (16, 14, 16), {
        'down': ('#bottom', [0, 0, 16, 14]),
        'north': ('#front', [0, 2, 16, 16]),
        'south': ('#back', [0, 2, 16, 16]),
        'west': ('#side', [2, 2, 16, 16]),
        'east': ('#side', [16, 2, 2, 16]),
    }, name='counter'))
    # countertop slab x0-16 y14-16 z0-16
    E.append(el((0, 14, 0), (16, 16, 16), {
        'up': ('#top', [0, 0, 16, 16]),
        'down': ('#trim', [0, 2, 16, 16]),
        'north': ('#trim', [0, 0, 16, 2]),
        'south': ('#trim', [0, 0, 16, 2]),
        'west': ('#trim', [0, 0, 16, 2]),
        'east': ('#trim', [0, 0, 16, 2]),
    }, name='countertop'))
    # brass balance scale (y16-20)
    brass = ('#detail', [0, 0, 4, 4])
    E.append(el((10, 16, 9.5), (14, 16.5, 12.5), {
        'up': ('#detail', [0, 0, 4, 3]), 'north': ('#detail', [0, 3, 4, 3.5]), 'south': ('#detail', [0, 5, 4, 5.5]),
        'west': ('#detail', [0, 4, 3, 4.5]), 'east': ('#detail', [0, 6, 3, 6.5]),
        'down': ('#detail', [0, 0, 4, 3])}, name='scale_base'))
    E.append(el((11.5, 16.5, 10.5), (12.5, 19.5, 11.5), {
        'north': ('#detail', [1, 1, 2, 4]), 'south': ('#detail', [3, 3, 4, 6]), 'west': ('#detail', [2, 1, 3, 4]),
        'east': ('#detail', [4, 3, 5, 6]), 'up': ('#detail', [1, 1, 2, 2])}, name='scale_post'))
    E.append(el((8.5, 19.5, 10.5), (15.5, 20, 11.5), {
        'up': ('#detail', [0, 1, 7, 2]), 'down': ('#detail', [0, 5, 7, 6]), 'north': ('#detail', [0, 1, 7, 1.5]),
        'south': ('#detail', [0, 5, 7, 5.5]), 'west': ('#detail', [0, 1, 1, 1.5]), 'east': ('#detail', [6, 6, 7, 6.5])},
        name='scale_beam'))
    for x in (9.25, 14.5):
        E.append(el((x, 18, 10.9), (x + 0.25, 19.5, 11.1), {
            'north': ('#detail', [2, 2, 2.25, 3.5]), 'south': ('#detail', [5, 5, 5.25, 6.5]),
            'west': ('#detail', [2, 2, 2.25, 3.5]), 'east': ('#detail', [5, 5, 5.25, 6.5])}, name='scale_hanger'))
    for x0 in (8.4, 13.6):
        E.append(el((x0, 17.5, 10), (x0 + 2, 18, 12), {
            'up': ('#detail', [8, 8, 16, 16]), 'down': ('#detail', [4, 4, 6, 6]),
            'north': ('#detail', [1, 2, 3, 2.5]), 'south': ('#detail', [4, 5, 6, 5.5]),
            'west': ('#detail', [1, 2, 3, 2.5]), 'east': ('#detail', [4, 5, 6, 5.5])}, name='scale_pan'))
    # open ledger, turned a little
    r = rot('y', 22.5, (5, 16, 7))
    E.append(el((2, 16, 4), (8, 16.25, 10), {
        'up': ('#detail', [0, 8, 8, 16]), 'down': ('#detail', [0, 8, 8, 16]),
        'north': ('#detail', [0, 8, 8, 8.5]), 'south': ('#detail', [0, 15, 8, 15.5]),
        'west': ('#detail', [0, 8, 8, 8.5]), 'east': ('#detail', [0, 15, 8, 15.5])}, rotation=r, name='ledger_cover'))
    E.append(el((2.4, 16.25, 4.4), (7.6, 16.75, 9.6), {
        'up': ('#detail', [8, 0, 16, 8]),
        'north': ('#detail', [8, 7, 16, 7.5]), 'south': ('#detail', [8, 7, 16, 7.5]),
        'west': ('#detail', [8, 7, 16, 7.5]), 'east': ('#detail', [8, 7, 16, 7.5])}, rotation=r, name='ledger_pages'))
    model('bank_counter', tex, E)


# ======================================================================
# SHOP STALL
# ======================================================================
def stall_top():
    cv = planks(OAK, 31, polish=True)
    # rim boards at front edge
    cv.hline(0, 15, 0, OAK[6])
    cv.hline(0, 15, 1, OAK[4])
    return cv


def stripe_col(x, w=2):
    return (x // w) % 2 == 0


def stall_front():
    """North face of the counter (rows 4..15 = y12..y0): plank lip, striped cloth
    with fold shading and scalloped hem, shadowed base below."""
    cv = Canvas()
    cv.rect(0, 0, 15, 15, OAK[3])
    cv.hline(0, 15, 4, OAK[6])
    cv.hline(0, 15, 5, OAK[3])
    for x in range(0, 16, 8):
        cv.put(x + 3, 5, OAK[1])        # nail heads
    for y in range(6, 15):
        for x in range(16):
            red = stripe_col(x)
            pal = RED_CLOTH if red else CREAM_CLOTH
            left = x % 2 == 0
            t = 3 if left else 2
            if y == 6:
                t -= 1                   # shadow under the lip
            cv.put(x, y, pal[max(0, min(len(pal) - 1, t + (1 if y in (8, 9) and left else 0)))])
    # scalloped hem: each stripe ends in a rounded tip; gaps show the dark base
    for x in range(16):
        cv.put(x, 15, OAK[0])
        if x % 2 == 1:
            cv.put(x, 14, OAK[1])
    return cv


def stall_side():
    """East/west faces: framed vertical planks with a cross brace."""
    cv = vgrain_planks(OAK, 33, plank_w=4)
    cv.hline(0, 15, 4, OAK[6])
    cv.hline(0, 15, 5, OAK[2])
    cv.hline(0, 15, 15, OAK[0])
    cv.vline(0, 4, 15, OAK[5])
    cv.vline(15, 4, 15, OAK[1])
    for i in range(9):
        x, y = 1 + int(i * 1.6), 6 + i
        if y <= 14:
            cv.put(x, y, OAK[6])
            cv.put(x + 1, y, OAK[5])
            cv.put(x + 2, y, OAK[1])
    return cv


def stall_back():
    """South face (merchant side): a shelf with jars and a coin box."""
    cv = vgrain_planks(OAK, 35, plank_w=4)
    cv.rect(1, 6, 14, 13, OAK[0])
    cv.hline(1, 14, 6, '#2e2414')
    cv.hline(1, 14, 10, OAK[5])
    cv.hline(1, 14, 11, OAK[2])
    jars = [(2, '#5aa0c8', '#a8e0f0'), (4, '#7cc07a', '#c0f0b0'), (6, '#c8a040', '#f0e08a')]
    for x, d, l in jars:
        cv.vline(x, 8, 9, d)
        cv.vline(x + 1, 8, 9, d)
        cv.put(x, 8, l)
        cv.put(x, 7, '#8a6a40')
        cv.put(x + 1, 7, '#8a6a40')
    cv.grid(["GgG", "ggg"], {'G': GOLD[5], 'g': GOLD[3]}, 10, 8)
    cv.grid(["bbbb", "BbbB"], {'b': '#5a3a1a', 'B': '#3e2810'}, 2, 12)
    cv.put(9, 13, GOLD[4])
    cv.hline(0, 15, 4, OAK[6])
    cv.hline(0, 15, 5, OAK[2])
    cv.hline(0, 15, 15, OAK[0])
    return cv


def stall_board():
    """Atlas: rows 0-3 sign face (north), rows 4-7 plank (top/back), rows 8-11 end grain."""
    cv = Canvas()
    # sign face: dark spruce board with a gold coin and 'price' marks
    for y in range(4):
        for x in range(16):
            cv.put(x, y, SPRUCE[3] if y in (1, 2) else SPRUCE[2])
    cv.hline(0, 15, 0, SPRUCE[5])
    cv.hline(0, 15, 3, SPRUCE[0])
    cv.grid([".ab.", "abbc", ".bc."], {'a': GOLD[5], 'b': GOLD[4], 'c': GOLD[2]}, 6, 0)
    cv.put(7, 1, '#fff6c4')
    for x in (2, 3, 12, 13):
        cv.put(x, 1, CREAM_CLOTH[3])
    cv.put(3, 2, CREAM_CLOTH[2])
    cv.put(12, 2, CREAM_CLOTH[2])
    # plank strip
    p = planks(SPRUCE, 37)
    cv.a[4:8] = p.a[0:4]
    # end grain
    for y in range(8, 12):
        for x in range(16):
            cv.put(x, y, SPRUCE[4] if (x + y) % 3 else SPRUCE[3])
        cv.put(y % 16, y, SPRUCE[1])
    cv.a[12:16] = p.a[8:12]
    return cv


def stall_awning():
    """Rows 0-7: awning top (stripes along z), rows 8-15: underside (shaded)."""
    cv = Canvas()
    for y in range(16):
        for x in range(16):
            red = stripe_col(x, 2)
            pal = RED_CLOTH if red else CREAM_CLOTH
            t = 4 if y < 8 else 2
            if y < 8 and x % 2 == 1:
                t -= 1
            if y in (0, 8):
                t += 1 if y == 0 else 0
            cv.put(x, y, pal[t])
    return cv


def shop_stall_model():
    tex = {'particle': T('shop_stall_front'), 'top': T('shop_stall_top'), 'front': T('shop_stall_front'),
           'side': T('shop_stall_side'), 'back': T('shop_stall_back'), 'board': T('shop_stall_board'),
           'awning': T('shop_stall_awning')}
    E = []
    E.append(el((0, 0, 0), (16, 12, 16), {
        'up': ('#top', [0, 0, 16, 16]),
        'down': ('#board', [0, 4, 16, 8]),
        'north': ('#front', [0, 4, 16, 16]),
        'south': ('#back', [0, 4, 16, 16]),
        'west': ('#side', [0, 4, 16, 16]),
        'east': ('#side', [0, 4, 16, 16]),
    }, name='counter'))
    E.append(el((0, 12, 12), (16, 16, 16), {
        'up': ('#board', [0, 4, 16, 8]),
        'north': ('#board', [0, 0, 16, 4]),
        'south': ('#board', [0, 4, 16, 8]),
        'west': ('#board', [0, 8, 4, 12]),
        'east': ('#board', [12, 8, 16, 12]),
    }, name='back_board'))
    # awning lip, tilted down toward the customer
    r = rot('x', -22.5, (8, 16, 16))
    E.append(el((0, 16, 10.5), (16, 17, 16), {
        'up': ('#awning', [0, 0, 16, 5.5]),
        'down': ('#awning', [0, 8, 16, 13.5]),
        'north': ('#awning', [0, 0, 16, 1]),
        'south': ('#awning', [0, 8, 16, 9]),
        'west': ('#awning', [0, 0, 5.5, 1]),
        'east': ('#awning', [0, 0, 5.5, 1]),
    }, rotation=r, name='awning'))
    model('shop_stall', tex, E)


# ======================================================================
# TITAN ANVIL
# ======================================================================
S = STEEL
RUNE_COL = {'frost': ('#3f8ea0', '#7fe6f5'), 'tide': ('#2f5aa8', '#6f9cff'),
            'storm': ('#9a8a30', '#ffe45c'), 'magma': ('#a0502a', '#ff9a4a')}
RUNES = {
    'frost': ["#.#", ".#.", "#.#"],
    'tide': ["#.#", "###", ".#."],
    'storm': [".##", ".#.", "##."],
    'magma': [".#.", "#.#", "###"],
}


def steel_fill(cv, x0, y0, x1, y1, seed, lo=2, hi=4):
    """Brushed dark steel: per-row base tone with long horizontal streaks."""
    r = rng(seed)
    tones = S[lo:hi + 1]
    mid = len(tones) // 2
    for y in range(y0, y1 + 1):
        base = mid if r.random() < 0.7 else max(0, mid - 1)
        for x in range(x0, x1 + 1):
            cv.put(x, y, tones[base])
        for _ in range(2):
            sx = int(r.integers(x0, x1 + 1))
            ln = int(r.integers(2, 7))
            t = tones[min(len(tones) - 1, base + 1)] if r.random() < 0.5 else tones[max(0, base - 1)]
            for i in range(ln):
                if sx + i <= x1:
                    cv.put(sx + i, y, t)


def engrave(cv, ox, oy, rune, kind, glow=False):
    """Engraved rune groove: dark cut with a faint elemental tint (brighter if glow)."""
    dark, light = RUNE_COL[kind]
    tint = mix(S[1], light if glow else dark, 0.55 if glow else 0.4)
    for j, r in enumerate(RUNES[rune]):
        for i, ch in enumerate(r):
            if ch == '#':
                cv.put(ox + i, oy + j, tint)
    # the centre-most groove pixel catches a little more colour
    if glow:
        cv.put(ox + 1, oy + 1, mix(S[2], light, 0.75)) if RUNES[rune][1][1] == '#' else None


def anvil_top():
    """Top face of the anvil head (uv rows 3..12)."""
    cv = Canvas()
    cv.rect(0, 0, 15, 15, S[4])
    for x, y, l in ((2, 6, 4), (9, 8, 5), (5, 10, 3), (11, 5, 3)):
        cv.hline(x, x + l, y, S[3])
    # worn polished striking face in the middle
    cv.rect(4, 6, 11, 9, S[5])
    cv.hline(4, 11, 6, S[6])
    cv.vline(4, 6, 9, S[6])
    cv.hline(5, 11, 9, S[4])
    for x, y in ((6, 7), (7, 7), (9, 8)):
        cv.put(x, y, S[7])
    cv.hline(0, 15, 3, S[6])
    cv.hline(0, 15, 12, S[1])
    cv.vline(0, 3, 12, S[5])
    cv.vline(15, 3, 12, S[1])
    # faint rune grooves at the four corners
    engrave(cv, 1, 4, 'frost', 'frost')
    engrave(cv, 12, 4, 'tide', 'tide')
    engrave(cv, 1, 9, 'storm', 'storm')
    engrave(cv, 12, 9, 'magma', 'magma')
    # groove line linking them
    for x in range(5, 11):
        cv.put(x, 4, S[2])
        cv.put(x, 11, S[2])
    for x, y in ((6, 7), (7, 6), (9, 8)):
        cv.put(x, y, S[7])
    return cv


def anvil_side():
    """Atlas: rows 0-5 head front/back (16x6), rows 6-11 head ends (cols 3..12),
    rows 12-15 base sides."""
    cv = Canvas()
    steel_fill(cv, 0, 0, 15, 15, 43)
    # head front: bevel + rune band
    cv.hline(0, 15, 0, S[6])
    cv.hline(0, 15, 1, S[4])
    cv.hline(0, 15, 5, S[1])
    cv.hline(1, 14, 2, S[2])
    cv.hline(1, 14, 4, S[3])
    for i, k in enumerate(('frost', 'tide', 'storm', 'magma')):
        ox = 1 + i * 4
        engrave(cv, ox, 2, k, k, glow=True)
        cv.put(ox + 3, 3, S[1])
    # head ends
    cv.hline(0, 15, 6, S[6])
    cv.hline(0, 15, 11, S[1])
    engrave(cv, 6, 8, 'storm', 'storm', glow=True)
    # base sides: heavy plate with rivets
    cv.hline(0, 15, 12, S[5])
    cv.hline(0, 15, 15, S[0])
    for x in (3, 8, 12):
        cv.put(x, 13, S[7])
        cv.put(x, 14, S[1])
    return cv


def anvil_body():
    """Waist sides (vertical grooves) and base top."""
    cv = Canvas()
    steel_fill(cv, 0, 0, 15, 15, 45, 1, 3)
    for x in range(0, 16, 3):
        cv.vline(x, 0, 15, S[1])
        cv.vline(x + 1, 0, 15, S[4])
    for y in (0, 15):
        cv.hline(0, 15, y, S[0])
    return cv


def anvil_base_top():
    cv = Canvas()
    steel_fill(cv, 0, 0, 15, 15, 47, 2, 4)
    bevel(cv, 2, 2, 13, 13, S[6], S[1])
    for x, y in ((3, 3), (12, 3), (3, 12), (12, 12)):
        cv.put(x, y, S[7])
    return cv


def titan_anvil_model():
    tex = {'particle': T('titan_anvil_side'), 'top': T('titan_anvil_top'), 'side': T('titan_anvil_side'),
           'body': T('titan_anvil_body'), 'base': T('titan_anvil_base')}
    E = []
    E.append(el((2, 0, 2), (14, 4, 14), {
        'down': ('#base', [2, 2, 14, 14]), 'up': ('#base', [2, 2, 14, 14]),
        'north': ('#side', [2, 12, 14, 16]), 'south': ('#side', [2, 12, 14, 16]),
        'west': ('#side', [2, 12, 14, 16]), 'east': ('#side', [2, 12, 14, 16])}, name='base'))
    E.append(el((4, 4, 5), (12, 10, 11), {
        'north': ('#body', [4, 5, 12, 11]), 'south': ('#body', [4, 5, 12, 11]),
        'west': ('#body', [5, 5, 11, 11]), 'east': ('#body', [5, 5, 11, 11])}, name='waist'))
    E.append(el((0, 10, 3), (16, 16, 13), {
        'up': ('#top', [0, 3, 16, 13]), 'down': ('#body', [0, 3, 16, 13]),
        'north': ('#side', [0, 0, 16, 6]), 'south': ('#side', [0, 0, 16, 6]),
        'west': ('#side', [3, 6, 13, 12]), 'east': ('#side', [3, 6, 13, 12])}, name='head'))
    model('titan_anvil', tex, E)


# ======================================================================
# RELIC PEDESTAL
# ======================================================================
O = OBSIDIAN


def obsidian_tex(seed=51):
    cv = Canvas()
    noise_region(cv, 0, 0, 15, 15, O[1:5], seed, cells=4, octaves=2, contrast=1.4)
    # polished sheen: short diagonal light streaks
    for sx, sy in ((2, 3), (9, 1), (11, 9), (4, 11)):
        cv.put(sx, sy, O[5])
        cv.put(sx + 1, sy - 1, O[6])
    for x, y in ((6, 6), (13, 13), (1, 14)):
        cv.put(x, y, O[0])
    return cv


def pedestal_slab():
    """Slab sides: obsidian with a gold trim line on the top row of each band.
    Base sides use rows 13-15, top-slab sides rows 2-3."""
    cv = obsidian_tex(53)
    for y in (2, 13):
        for x in range(16):
            cv.put(x, y, GOLD[4] if x % 4 else GOLD[5])
    cv.hline(0, 15, 3, O[2])
    cv.hline(0, 15, 15, O[0])
    return cv


def pedestal_top():
    """Top face of the top slab (uv 2..14): obsidian with a gold ring inlay and
    a purpur rosette under the floating crystal."""
    cv = obsidian_tex(55)
    bevel(cv, 2, 2, 13, 13, O[6], O[0])
    # gold ring (octagon)
    ring = [(6, 4), (7, 4), (8, 4), (9, 4), (5, 5), (10, 5), (4, 6), (11, 6), (4, 7), (11, 7), (4, 8), (11, 8),
            (4, 9), (11, 9), (5, 10), (10, 10), (6, 11), (7, 11), (8, 11), (9, 11)]
    for x, y in ring:
        cv.put(x, y, GOLD[5] if x + y < 15 else GOLD[3])
    cv.rect(6, 6, 9, 9, PURPUR[3])
    cv.rect(5, 7, 10, 8, PURPUR[3])
    cv.rect(7, 5, 8, 10, PURPUR[3])
    for x, y in ((6, 6), (7, 5), (5, 7)):
        cv.put(x, y, PURPUR[5])
    for x, y in ((9, 9), (8, 10), (10, 8)):
        cv.put(x, y, PURPUR[1])
    cv.put(7, 7, AMETHYST[5])
    cv.put(8, 8, AMETHYST[3])
    cv.put(8, 7, AMETHYST[4])
    cv.put(7, 8, AMETHYST[4])
    return cv


def pedestal_column():
    """Purpur column (uv cols 4..12, rows 4..13): fluting + gold band."""
    cv = Canvas()
    for y in range(16):
        for x in range(16):
            f = (x - 4) % 3
            cv.put(x, y, PURPUR[5] if f == 0 else PURPUR[3] if f == 1 else PURPUR[1])
    # subtle stone variation
    noise = tile_noise(16, 16, 4, 57)
    for y in range(16):
        for x in range(16):
            if noise[y, x] > 0.7 and (x - 4) % 3 == 1:
                cv.put(x, y, PURPUR[4])
    cv.hline(0, 15, 4, PURPUR[6])        # capital
    cv.hline(0, 15, 5, PURPUR[2])
    cv.hline(0, 15, 12, PURPUR[4])       # foot
    cv.hline(0, 15, 13, PURPUR[0])
    # gold band at y7..y8 (rows 8-9)
    for x in range(16):
        cv.put(x, 8, GOLD[5] if x % 3 == 1 else GOLD[4])
        cv.put(x, 9, GOLD[2])
    cv.put(7, 8, '#fff6c4')
    return cv


def pedestal_crystal():
    """Amethyst facets as vertical bands: cols 0-3 lit, 4-7 light, 8-11 mid,
    12-15 deep; rows get brighter toward the tip (top)."""
    cv = Canvas()
    bands = [(6, 5, 4), (5, 4, 3), (4, 3, 2), (3, 2, 1)]
    for y in range(16):
        for x in range(16):
            hi, md, lo = bands[x // 4]
            t = hi if y < 4 else md if y < 11 else lo
            cv.put(x, y, AMETHYST[t])
        cv.put(1, y, AMETHYST[6] if y < 9 else AMETHYST[5])     # edge highlight
        cv.put(15, y, AMETHYST[0])
    for x, y in ((5, 2), (6, 6), (9, 3), (13, 5), (2, 12)):
        cv.put(x, y, '#ffffff' if y < 4 else AMETHYST[6])
    return cv


def relic_pedestal_model():
    tex = {'particle': T('relic_pedestal_slab'), 'slab': T('relic_pedestal_slab'), 'top': T('relic_pedestal_top'),
           'column': T('relic_pedestal_column'), 'crystal': T('relic_pedestal_crystal')}
    E = []
    E.append(el((2, 0, 2), (14, 3, 14), {
        'down': ('#slab', [2, 2, 14, 14]), 'up': ('#slab', [2, 4, 14, 12]),
        'north': ('#slab', [2, 13, 14, 16]), 'south': ('#slab', [2, 13, 14, 16]),
        'west': ('#slab', [2, 13, 14, 16]), 'east': ('#slab', [2, 13, 14, 16])}, name='base'))
    E.append(el((4, 3, 4), (12, 12, 12), {
        'north': ('#column', [4, 4, 12, 13]), 'south': ('#column', [4, 4, 12, 13]),
        'west': ('#column', [4, 4, 12, 13]), 'east': ('#column', [4, 4, 12, 13])}, name='column'))
    E.append(el((2, 12, 2), (14, 14, 14), {
        'down': ('#slab', [2, 4, 14, 12]), 'up': ('#top', [2, 2, 14, 14]),
        'north': ('#slab', [2, 2, 14, 4]), 'south': ('#slab', [2, 2, 14, 4]),
        'west': ('#slab', [2, 2, 14, 4]), 'east': ('#slab', [2, 2, 14, 4])}, name='top'))
    # floating amethyst crystal: a tall rotated prism with a wider girdle
    cr = rot('y', 45, (8, 17, 8))
    E.append(el((7, 15, 7), (9, 20, 9), {
        'up': ('#crystal', [0, 0, 2, 2]), 'down': ('#crystal', [12, 14, 14, 16]),
        'west': ('#crystal', [0, 0, 2, 16]), 'north': ('#crystal', [4, 0, 6, 16]),
        'east': ('#crystal', [8, 0, 10, 16]), 'south': ('#crystal', [12, 0, 14, 16])},
        rotation=cr, name='crystal_spire'))
    E.append(el((8.6, 15.2, 7.3), (10, 18.4, 8.7), {
        'up': ('#crystal', [0, 0, 1.4, 1.4]), 'down': ('#crystal', [12, 14, 13.4, 15.4]),
        'west': ('#crystal', [0, 3, 1.4, 13]), 'north': ('#crystal', [4, 3, 5.4, 13]),
        'east': ('#crystal', [8, 3, 9.4, 13]), 'south': ('#crystal', [12, 3, 13.4, 13])},
        rotation=rot('z', -22.5, (9.3, 15.2, 8)), name='crystal_shard'))
    model('relic_pedestal', tex, E)


# ======================================================================
TEXTURES = {
    'bank_counter_top': bank_top, 'bank_counter_trim': bank_trim, 'bank_counter_front': bank_front,
    'bank_counter_side': bank_side, 'bank_counter_back': bank_back, 'bank_counter_bottom': bank_bottom,
    'bank_counter_details': bank_details,
    'shop_stall_top': stall_top, 'shop_stall_front': stall_front, 'shop_stall_side': stall_side,
    'shop_stall_back': stall_back, 'shop_stall_board': stall_board, 'shop_stall_awning': stall_awning,
    'titan_anvil_top': anvil_top, 'titan_anvil_side': anvil_side, 'titan_anvil_body': anvil_body,
    'titan_anvil_base': anvil_base_top,
    'relic_pedestal_slab': pedestal_slab, 'relic_pedestal_top': pedestal_top,
    'relic_pedestal_column': pedestal_column, 'relic_pedestal_crystal': pedestal_crystal,
}
MODELS = [bank_counter_model, shop_stall_model, titan_anvil_model, relic_pedestal_model]
MODEL_NAMES = ['bank_counter', 'shop_stall', 'titan_anvil', 'relic_pedestal']


def main():
    out = []
    for name, fn in TEXTURES.items():
        cv = fn()
        cv.save(f'textures/block/{name}.png')
        out.append((name, cv.pil()))
    for m in MODELS:
        m()
    print(contact_sheet(out, 'economy_block_textures.png', cols=7))
    from model_preview import model_sheet
    print(model_sheet(MODEL_NAMES, 'economy_block_models.png', S=12))


if __name__ == '__main__':
    main()
