"""Container GUI textures (256x256 canvases, image at top-left).

Night-blue panel, 2px gold trim in the vanilla 9-slice construction,
vanilla-style 18x18 slots, inset text panels and faint star specks.
"""
from common import *

OUTLINE = '#090a18'
GOLD_HI = '#F2D27A'
GOLD = '#C9A54C'
GOLD_MID = '#A8873A'
GOLD_SH = '#7A5C22'
PANEL_TOP = '#2A2F55'
PANEL_BOT = '#1B1F3B'
INNER_SH = '#151830'
INNER_HI = '#363c6c'
SLOT_IN = '#0F1226'
SLOT_DARK = '#060714'
SLOT_LIGHT = '#3d4476'
SLOT_MID = '#1a1e3c'
SPECK = '#3a4174'
SPECK_HI = '#5d66a6'
CREAM = '#F2E6C9'

ELEMENTS = {'frost': '#7fe6f5', 'tide': '#5c8cff', 'storm': '#ffe45c', 'magma': '#ff9a3c'}
GLYPHS = {
    'frost': ["...#...", ".#.#.#.", "..###..", "###.###", "..###..", ".#.#.#.", "...#..."],
    'tide': ["#..#..#", "#..#..#", "##.#.##", ".#####.", "...#...", "...#...", "..###.."],
    'storm': ["....##.", "...##..", "..##...", ".#####.", "...##..", "..##...", ".##...."],
    'magma': ["...#...", "...##..", "..###.#", ".##.##.", "##...##", "##...##", ".#####."],
}


class Gui:
    def __init__(self, w, h):
        self.cv = Canvas(256, 256)
        self.w, self.h = w, h
        self.busy = np.zeros((256, 256), bool)   # where specks must not go

    def mark(self, x0, y0, x1, y1, pad=1):
        self.busy[max(0, y0 - pad):y1 + pad + 1, max(0, x0 - pad):x1 + pad + 1] = True

    # ----------------------------------------------------------- panel
    def panel(self):
        w, h, cv = self.w, self.h, self.cv
        # gradient fill with ordered-dither transitions
        stops = ramp([PANEL_TOP, '#252a4d', PANEL_BOT], 5)
        for y in range(h):
            t = y / (h - 1) * (len(stops) - 1)
            for x in range(w):
                v = t + (BAYER4[y % 4, x % 4] - 0.5) * 0.9
                cv.put(x, y, stops[int(min(max(round(v), 0), len(stops) - 1))])
        # outline with vanilla-style cut corners
        cv.hline(2, w - 3, 0, OUTLINE)
        cv.hline(2, w - 3, h - 1, OUTLINE)
        cv.vline(0, 2, h - 3, OUTLINE)
        cv.vline(w - 1, 2, h - 3, OUTLINE)
        for x, y in ((1, 1), (w - 2, 1), (1, h - 2), (w - 2, h - 2)):
            cv.put(x, y, OUTLINE)
        for x, y in ((0, 0), (1, 0), (0, 1), (w - 1, 0), (w - 2, 0), (w - 1, 1),
                     (0, h - 1), (1, h - 1), (0, h - 2), (w - 1, h - 1), (w - 2, h - 1), (w - 1, h - 2)):
            cv.put(x, y, TRANSPARENT)
        # 2px gold trim: lit top/left, shaded bottom/right
        cv.hline(2, w - 3, 1, GOLD_HI)
        cv.vline(1, 2, h - 3, GOLD_HI)
        cv.hline(2, w - 4, 2, GOLD)
        cv.vline(2, 2, h - 4, GOLD)
        cv.hline(2, w - 3, h - 2, GOLD_SH)
        cv.vline(w - 2, 2, h - 3, GOLD_SH)
        cv.hline(3, w - 3, h - 3, GOLD_MID)
        cv.vline(w - 3, 3, h - 3, GOLD_MID)
        cv.put(3, 3, GOLD)                       # rounded inner corners
        cv.put(w - 4, h - 4, GOLD_MID)
        cv.put(w - 3, 2, GOLD)                   # mixed corners
        cv.put(2, h - 3, GOLD)
        cv.put(w - 2, 1, GOLD)
        cv.put(1, h - 2, GOLD)
        # thin inner shadow/highlight just inside the trim
        cv.hline(4, w - 5, 3, INNER_SH)
        cv.vline(3, 4, h - 5, INNER_SH)
        cv.hline(4, w - 4, h - 4, INNER_HI)
        cv.vline(w - 4, 4, h - 5, INNER_HI)
        # corner brackets with a gem
        for (cx, cy, sx, sy) in ((4, 4, 1, 1), (w - 5, 4, -1, 1), (4, h - 5, 1, -1), (w - 5, h - 5, -1, -1)):
            for i in range(3):
                cv.put(cx + sx * i, cy, GOLD_MID)
                cv.put(cx, cy + sy * i, GOLD_MID)
            cv.put(cx + sx, cy + sy, GOLD_HI)
        self.mark(0, 0, w - 1, 5, 0)
        self.mark(0, 0, 5, h - 1, 0)
        self.mark(0, h - 6, w - 1, h - 1, 0)
        self.mark(w - 6, 0, w - 1, h - 1, 0)

    # ----------------------------------------------------------- parts
    def slot(self, x, y, ghost=None):
        """Slot frame for an item drawn at (x,y)."""
        cv = self.cv
        x0, y0 = x - 1, y - 1
        cv.rect(x0, y0, x0 + 17, y0 + 17, SLOT_IN)
        cv.hline(x0, x0 + 16, y0, SLOT_DARK)
        cv.vline(x0, y0, y0 + 16, SLOT_DARK)
        cv.hline(x0 + 1, x0 + 17, y0 + 17, SLOT_LIGHT)
        cv.vline(x0 + 17, y0 + 1, y0 + 17, SLOT_LIGHT)
        cv.put(x0 + 17, y0, SLOT_MID)
        cv.put(x0, y0 + 17, SLOT_MID)
        if ghost:
            cv.grid(ghost, {'#': '#1b2042', '+': '#222850'}, x, y)
        self.mark(x0, y0, x0 + 17, y0 + 17)

    def inset(self, x0, y0, x1, y1, fill='#161a33', specks=False, gold_corners=True):
        """Recessed panel; coordinates inclusive."""
        cv = self.cv
        cv.rect(x0, y0, x1, y1, fill)
        cv.hline(x0, x1 - 1, y0, SLOT_DARK)
        cv.vline(x0, y0, y1 - 1, SLOT_DARK)
        cv.hline(x0 + 1, x1, y1, SLOT_LIGHT)
        cv.vline(x1, y0 + 1, y1, SLOT_LIGHT)
        cv.put(x1, y0, SLOT_MID)
        cv.put(x0, y1, SLOT_MID)
        if gold_corners:
            for x, y in ((x0 + 2, y0 + 2), (x1 - 2, y0 + 2), (x0 + 2, y1 - 2), (x1 - 2, y1 - 2)):
                cv.put(x, y, GOLD_SH)
        self.mark(x0, y0, x1, y1)
        if specks:
            r = rng(x0 * 7 + y0)
            n = (x1 - x0) * (y1 - y0) // 160
            for _ in range(n):
                sx, sy = int(r.integers(x0 + 3, x1 - 2)), int(r.integers(y0 + 3, y1 - 2))
                cv.put(sx, sy, '#262c52')

    def big_frame(self, x, y, gems=True):
        """26x26 gold-edged frame centred on the slot whose item sits at (x,y)."""
        cv = self.cv
        x0, y0 = x - 5, y - 5
        x1, y1 = x0 + 25, y0 + 25
        cv.rect(x0, y0, x1, y1, OUTLINE)
        cv.hline(x0 + 1, x1 - 1, y0 + 1, GOLD_HI)
        cv.vline(x0 + 1, y0 + 1, y1 - 1, GOLD_HI)
        cv.hline(x0 + 1, x1 - 1, y1 - 1, GOLD_SH)
        cv.vline(x1 - 1, y0 + 1, y1 - 1, GOLD_SH)
        cv.hline(x0 + 2, x1 - 2, y0 + 2, GOLD)
        cv.vline(x0 + 2, y0 + 2, y1 - 2, GOLD)
        cv.hline(x0 + 2, x1 - 2, y1 - 2, GOLD_MID)
        cv.vline(x1 - 2, y0 + 2, y1 - 2, GOLD_MID)
        cv.put(x1 - 1, y0 + 1, GOLD)
        cv.put(x0 + 1, y1 - 1, GOLD)
        # inner well with a soft radial glow
        cx, cy = x + 7.5, y + 7.5
        glow = ramp(['#0d1024', '#151a3a', '#1e2552'], 3)
        for yy in range(y0 + 3, y1 - 2):
            for xx in range(x0 + 3, x1 - 2):
                d = math.hypot(xx + 0.5 - cx, yy + 0.5 - cy) / 10.5
                v = (1 - d) * 2.6 + (BAYER4[yy % 4, xx % 4] - 0.5) * 0.8
                cv.put(xx, yy, glow[int(min(max(round(v), 0), 2))])
        cv.hline(x0 + 3, x1 - 3, y0 + 3, SLOT_DARK)
        cv.vline(x0 + 3, y0 + 3, y1 - 3, SLOT_DARK)
        cv.hline(x0 + 4, x1 - 3, y1 - 3, SLOT_LIGHT)
        cv.vline(x1 - 3, y0 + 4, y1 - 3, SLOT_LIGHT)
        if gems:
            for gx, gy in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
                cv.put(gx, gy, GOLD_HI)
            for gx, gy, c in ((x0 + 12, y0, GOLD_HI), (x0 + 13, y0, GOLD_HI), (x0 + 12, y1, GOLD_SH), (x0 + 13, y1, GOLD_SH)):
                cv.put(gx, gy, c)
        self.mark(x0 - 1, y0 - 1, x1 + 1, y1 + 1)
        return x0, y0, x1, y1

    def keep_clear(self, x0, y0, x1, y1):
        self.mark(x0, y0, x1, y1, 1)

    def glyph(self, kind, x, y, strength=0.22):
        col = mix(PANEL_BOT, ELEMENTS[kind], strength)
        self.cv.grid(GLYPHS[kind], {'#': col}, x, y)
        self.mark(x, y, x + 6, y + 6, 2)

    def specks(self, seed, density=0.004):
        r = rng(seed)
        n = int(self.w * self.h * density)
        placed = 0
        tries = 0
        while placed < n and tries < n * 30:
            tries += 1
            x, y = int(r.integers(6, self.w - 6)), int(r.integers(6, self.h - 6))
            if self.busy[max(0, y - 2):y + 3, max(0, x - 2):x + 3].any():
                continue
            if r.random() < 0.15 and not self.busy[max(0, y - 3):y + 4, max(0, x - 3):x + 4].any():
                self.cv.put(x, y, SPECK_HI)
                for dx, dy in N4:
                    self.cv.put(x + dx, y + dy, SPECK)
                self.mark(x - 1, y - 1, x + 1, y + 1, 3)
            else:
                self.cv.put(x, y, SPECK)
                self.mark(x, y, x, y, 3)
            placed += 1

    def player_inventory(self, y_inv, y_hot, label_y):
        for row in range(3):
            for col in range(9):
                self.slot(8 + col * 18, y_inv + row * 18)
        for col in range(9):
            self.slot(8 + col * 18, y_hot)
        self.keep_clear(7, label_y - 1, 90, label_y + 9)
        # faint gold divider between inventory and hotbar
        yd = y_inv + 3 * 18 + 1
        for x in range(10, 166):
            if (x // 2) % 2 == 0:
                self.cv.put(x, yd, '#3a3424')

    def save(self, name):
        return self.cv.save(f'textures/gui/{name}.png')


GHOST_ARMOR = [
    "................",
    "................",
    "...###....###...",
    "..####+..+####..",
    "..#####++#####..",
    "...##########...",
    "....########....",
    "....########....",
    "....########....",
    "....########....",
    ".....######.....",
    "................",
]
GHOST_CORE = [
    "................",
    "................",
    "................",
    "......####......",
    ".....######.....",
    "....###++###....",
    "....##++++##....",
    "....##++++##....",
    "....###++###....",
    ".....######.....",
    "......####......",
]
GHOST_SHARD = [
    "................",
    "................",
    "...........##...",
    "..........###...",
    ".........###....",
    "........####....",
    ".......####.....",
    "......####......",
    ".....####.......",
    "....####........",
    "....###.........",
    "....##..........",
]


# ======================================================================
def bank():
    g = Gui(176, 186)
    g.panel()
    g.keep_clear(7, 5, 120, 14)                  # title
    # balance display
    g.inset(7, 16, 169, 46, fill='#0f1226', specks=True)
    cv = g.cv
    for x in range(12, 165):                     # faint gold rules
        if x % 3 != 2:
            cv.put(x, 19, '#3a3220')
            cv.put(x, 43, '#3a3220')
    # tiny aster marks at the display's ends
    for cx in (10, 166):
        cv.put(cx, 31, GOLD_MID)
        for dx, dy in N4:
            cv.put(cx + dx, 31 + dy, GOLD_SH)
    g.keep_clear(6, 48, 170, 91)                 # button areas
    g.player_inventory(104, 162, 92)
    g.specks(1)
    return g


def shop_owner():
    g = Gui(176, 204)
    g.panel()
    g.keep_clear(7, 5, 120, 14)
    for r in range(3):
        for c in range(3):
            g.slot(8 + c * 18, 22 + r * 18)
    g.inset(68, 16, 170, 108, fill='#171b35')
    g.keep_clear(68, 16, 170, 108)
    # faint aster emblem under the stock grid
    cv = g.cv
    em = [
        "....#....",
        "....#....",
        "...###...",
        "..#####..",
        "#########",
        "..#####..",
        "...###...",
        "....#....",
        "....#....",
    ]
    cv.grid(em, {'#': '#2e2c3a'}, 30, 84)
    cv.put(34, 88, '#4a4230')
    g.keep_clear(26, 80, 44, 98)
    g.player_inventory(122, 180, 110)
    g.specks(2)
    return g


def shop_buyer():
    g = Gui(176, 204)
    g.panel()
    g.keep_clear(7, 5, 120, 14)
    cv = g.cv
    # glow halo behind the showcase
    cx, cy = 34, 48
    halo = ['#232852', '#2a3060', '#323a70']
    for y in range(20, 80):
        for x in range(6, 64):
            d = math.hypot(x + 0.5 - cx, (y + 0.5 - cy) * 1.1)
            v = (1 - d / 26) * 3.2 + (BAYER4[y % 4, x % 4] - 0.5) * 0.9
            k = int(round(v)) - 1
            if k >= 0:
                cv.put(x, y, halo[min(2, k)])
    # rays
    for ang in range(0, 360, 45):
        a = math.radians(ang + 22.5)
        for rr in range(16, 24):
            x, y = int(cx + 0.5 + math.cos(a) * rr), int(cy + 0.5 + math.sin(a) * rr * 0.92)
            if (rr % 2) == 0:
                cv.put(x, y, '#3d4680')
    g.big_frame(26, 40)
    # pedestal below the frame
    ped = [
        "..aaaaaaaaaaaa..",
        ".bbbbbbbbbbbbbb.",
        "...cccccccccc...",
        "...cddddddddc...",
        "..eeeeeeeeeeee..",
        ".ffffffffffffff.",
    ]
    cv.grid(ped, {'a': GOLD_HI, 'b': GOLD_SH, 'c': '#3a3f6e', 'd': '#2a2e55', 'e': GOLD, 'f': GOLD_SH}, 26, 62)
    g.keep_clear(20, 34, 48, 68)
    g.inset(66, 16, 170, 82, fill='#171b35')
    g.keep_clear(69, 85, 169, 104)               # buy button
    g.player_inventory(122, 180, 110)
    g.specks(3)
    return g


ARROW = [  # 24x16: shaft rows 5-10, head to the right
    "................",
]


def arrow_mask():
    m = np.zeros((16, 24), bool)
    for y in range(5, 11):
        m[y, 1:15] = True
    for i in range(8):
        y0, y1 = 1 + i, 14 - i
        x = 14 + i
        m[y0:y1 + 1, x] = True
    return m


def titan_forge():
    g = Gui(176, 166)
    g.panel()
    g.keep_clear(7, 5, 120, 14)
    cv = g.cv
    # circuit lines linking the inputs to the arrow
    line = '#4a3d1e'
    line_hi = '#6e5a2a'
    for x in range(48, 90):
        cv.put(x, 43, line)
    for y in range(35, 52):
        cv.put(75, y, line)
    for x in range(75, 90):
        cv.put(x, 43, line)
    cv.hline(66 + 8, 75, 34, line)
    cv.hline(66 + 8, 75, 52, line)
    for x, y in ((75, 43), (48, 43)):
        cv.put(x, y, line_hi)
    g.slot(30, 35, GHOST_ARMOR)
    g.slot(66, 17, GHOST_CORE)
    g.slot(66, 53, GHOST_SHARD)
    g.big_frame(124, 35)
    # empty arrow (recessed)
    m = arrow_mask()
    ax, ay = 90, 35
    for y in range(16):
        for x in range(24):
            if m[y, x]:
                edge = not (m[y - 1, x] if y > 0 else False) or not (m[y, x - 1] if x > 0 else False)
                low = not (m[y + 1, x] if y < 15 else False) or not (m[y, x + 1] if x < 23 else False)
                cv.put(ax + x, ay + y, SLOT_DARK if edge else SLOT_LIGHT if low else SLOT_IN)
    g.mark(ax, ay, ax + 23, ay + 15)
    # filled glowing arrow at (176,0): prismatic elemental gradient
    grad = ramp(['#7fe6f5', '#7aa6ff', '#ffe45c', '#ff9a3c'], 24)
    for y in range(16):
        for x in range(24):
            if not m[y, x]:
                continue
            c = grad[x]
            edge = not (m[y - 1, x] if y > 0 else False) or not (m[y, x - 1] if x > 0 else False)
            low = not (m[y + 1, x] if y < 15 else False) or not (m[y, x + 1] if x < 23 else False)
            if edge:
                c = mix(c, '#ffffff', 0.55)
            elif low:
                c = mix(c, '#000000', 0.35)
            elif 7 <= y <= 8 and x < 20:
                c = mix(c, '#ffffff', 0.7)
            cv.put(176 + x, y, c)
    # faint elemental glyphs in the free corners
    g.glyph('frost', 10, 20)
    g.glyph('tide', 10, 56)
    g.glyph('storm', 156, 20)
    g.glyph('magma', 156, 56)
    g.keep_clear(7, 71, 90, 81)
    g.player_inventory(84, 142, 72)
    g.specks(4)
    return g


GUIS = {'bank': (bank, (176, 186)), 'shop_owner': (shop_owner, (176, 204)),
        'shop_buyer': (shop_buyer, (176, 204)), 'titan_forge': (titan_forge, (176, 166))}


def mock_text(img, name):
    """Preview-only overlay: cream text blocks where code draws text."""
    from PIL import ImageDraw
    im = img.copy()
    d = ImageDraw.Draw(im)
    f = _font(8)
    spots = {
        'bank': [((8, 6), 'Bank of the Stars', '#F2E6C9'), ((12, 26), 'Balance: 1,204 Asters', '#F2E6C9'),
                 ((8, 92), 'Inventory', '#BFB49A')],
        'shop_owner': [((8, 6), 'Your Stall', '#F2E6C9'), ((70, 18), 'Price: 12', '#F2E6C9'),
                       ((70, 29), 'Stock: 9', '#BFB49A'), ((8, 110), 'Inventory', '#BFB49A')],
        'shop_buyer': [((8, 6), 'Market Stall', '#F2E6C9'), ((70, 20), 'Titan Shard', '#F2E6C9'),
                       ((70, 32), '12 Asters', '#BFB49A'), ((8, 110), 'Inventory', '#BFB49A')],
        'titan_forge': [((8, 6), 'Titan Forge', '#F2E6C9'), ((8, 72), 'Inventory', '#BFB49A')],
    }
    for (x, y), t, c in spots[name]:
        d.text((x, y), t, fill=c, font=f)
    return im


def main():
    from common import _font
    globals()['_font'] = _font
    out = []
    for name, (fn, (w, h)) in GUIS.items():
        g = fn()
        g.save(name)
        im = g.cv.pil()
        out.append((name, im.crop((0, 0, 256, 256))))
    print(contact_sheet(out, 'gui.png', scale=3, cols=2))
    # with mock text, at 3x, cropped to the image
    mocks = [(n, mock_text(im.crop((0, 0, GUIS[n][1][0], GUIS[n][1][1])), n)) for n, im in out]
    print(contact_sheet(mocks, 'gui_text_mock.png', scale=3, cols=2))


if __name__ == '__main__':
    main()
