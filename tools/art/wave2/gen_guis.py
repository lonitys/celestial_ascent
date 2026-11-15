"""Wave-2 container GUIs (256x256 canvases, image at top-left).

The frame construction is copied from tools/art/gen_gui.py (titan_forge / bank):
cut-corner outline, 2px trim lit top-left, inner shadow line, corner brackets
with a gem, vanilla 18x18 slots, the 26x26 output frame, dithered panel
gradient and specks. Only the palette changes per theme.
"""
import math

from w2common import *
from w2common import _font

THEMES = {
    # titan/bank palette, kept for reference and the quest board
    'celestial': dict(
        outline='#090a18', hi='#F2D27A', gold='#C9A54C', mid='#A8873A', sh='#7A5C22',
        top='#2A2F55', midp='#252a4d', bot='#1B1F3B', inner_sh='#151830', inner_hi='#363c6c',
        slot_in='#0F1226', slot_dark='#060714', slot_light='#3d4476', slot_mid='#1a1e3c',
        speck='#3a4174', speck_hi='#5d66a6', ghost=('#1b2042', '#222850'), line=('#4a3d1e', '#6e5a2a'),
        divider='#3a3424', glow=['#0d1024', '#151a3a', '#1e2552'], inset='#161a33'),
    'imperial': dict(
        outline='#0e0716', hi='#F6D77E', gold='#CFA64A', mid='#AC8634', sh='#7C5A1E',
        top='#3a2456', midp='#30204a', bot='#22163a', inner_sh='#1a1030', inner_hi='#4a3270',
        slot_in='#170d26', slot_dark='#080410', slot_light='#4e3678', slot_mid='#24163a',
        speck='#4a3474', speck_hi='#8a62c8', ghost=('#261840', '#30204e'), line=('#4e3a1c', '#7a5c28'),
        divider='#3e3022', glow=['#120a22', '#1e1238', '#2c1a52'], inset='#1c1230'),
    'sky': dict(
        outline='#04050f', hi='#FFF2C8', gold='#E0C478', mid='#BC9E58', sh='#7E6632',
        top='#1a2148', midp='#141a3c', bot='#0c1028', inner_sh='#090c20', inner_hi='#2a3466',
        slot_in='#080b1c', slot_dark='#03040c', slot_light='#323e74', slot_mid='#121834',
        speck='#3a4a8a', speck_hi='#a8c8ff', ghost=('#141c40', '#1c264e'), line=('#3c3a4a', '#6a6a8a'),
        divider='#2e3044', glow=['#070a1c', '#101838', '#1a2858'], inset='#0e1330'),
    'void': dict(
        outline='#050208', hi='#E07AE8', gold='#A848B8', mid='#843496', sh='#4e1a5c',
        top='#221730', midp='#1b1228', bot='#120b1c', inner_sh='#0c0714', inner_hi='#34224a',
        slot_in='#0b0712', slot_dark='#030106', slot_light='#3c2852', slot_mid='#170f22',
        speck='#3a2250', speck_hi='#ff4ed6', ghost=('#1c1228', '#261834'), line=('#4a1a48', '#8a2a7a'),
        divider='#2e1a34', glow=['#0a0410', '#1a0a24', '#2e0f3a'], inset='#140c1e'),
    'ascension': dict(
        outline='#140f08', hi='#FFFFFF', gold='#FFE9A8', mid='#E2C46E', sh='#9C7A30',
        top='#4a3d2a', midp='#3a3022', bot='#2a221a', inner_sh='#1e1912', inner_hi='#54473a',
        slot_in='#1a1510', slot_dark='#0a0805', slot_light='#5a4c3a', slot_mid='#2a2219',
        speck='#5a4c34', speck_hi='#fff2c8', ghost=('#2c2419', '#362c1f'), line=('#6a5428', '#a88a44'),
        divider='#4a3e28', glow=['#1c160e', '#2c2416', '#403420'], inset='#221c14'),
}


class Gui:
    def __init__(self, w, h, theme):
        self.cv = Canvas(256, 256)
        self.w, self.h = w, h
        self.t = THEMES[theme]
        self.busy = np.zeros((256, 256), bool)

    def mark(self, x0, y0, x1, y1, pad=1):
        self.busy[max(0, y0 - pad):y1 + pad + 1, max(0, x0 - pad):x1 + pad + 1] = True

    def panel(self):
        w, h, cv, t = self.w, self.h, self.cv, self.t
        stops = ramp([t['top'], t['midp'], t['bot']], 5)
        for y in range(h):
            k = y / (h - 1) * (len(stops) - 1)
            for x in range(w):
                v = k + (BAYER4[y % 4, x % 4] - 0.5) * 0.9
                cv.put(x, y, stops[int(min(max(round(v), 0), len(stops) - 1))])
        O = t['outline']
        cv.hline(2, w - 3, 0, O)
        cv.hline(2, w - 3, h - 1, O)
        cv.vline(0, 2, h - 3, O)
        cv.vline(w - 1, 2, h - 3, O)
        for x, y in ((1, 1), (w - 2, 1), (1, h - 2), (w - 2, h - 2)):
            cv.put(x, y, O)
        for x, y in ((0, 0), (1, 0), (0, 1), (w - 1, 0), (w - 2, 0), (w - 1, 1),
                     (0, h - 1), (1, h - 1), (0, h - 2), (w - 1, h - 1), (w - 2, h - 1), (w - 1, h - 2)):
            cv.put(x, y, TRANSPARENT)
        HI, G, M, SH = t['hi'], t['gold'], t['mid'], t['sh']
        cv.hline(2, w - 3, 1, HI)
        cv.vline(1, 2, h - 3, HI)
        cv.hline(2, w - 4, 2, G)
        cv.vline(2, 2, h - 4, G)
        cv.hline(2, w - 3, h - 2, SH)
        cv.vline(w - 2, 2, h - 3, SH)
        cv.hline(3, w - 3, h - 3, M)
        cv.vline(w - 3, 3, h - 3, M)
        cv.put(3, 3, G)
        cv.put(w - 4, h - 4, M)
        cv.put(w - 3, 2, G)
        cv.put(2, h - 3, G)
        cv.put(w - 2, 1, G)
        cv.put(1, h - 2, G)
        cv.hline(4, w - 5, 3, t['inner_sh'])
        cv.vline(3, 4, h - 5, t['inner_sh'])
        cv.hline(4, w - 4, h - 4, t['inner_hi'])
        cv.vline(w - 4, 4, h - 5, t['inner_hi'])
        for (cx, cy, sx, sy) in ((4, 4, 1, 1), (w - 5, 4, -1, 1), (4, h - 5, 1, -1), (w - 5, h - 5, -1, -1)):
            for i in range(3):
                cv.put(cx + sx * i, cy, M)
                cv.put(cx, cy + sy * i, M)
            cv.put(cx + sx, cy + sy, self.gem_col(cx, cy))
        self.mark(0, 0, w - 1, 5, 0)
        self.mark(0, 0, 5, h - 1, 0)
        self.mark(0, h - 6, w - 1, h - 1, 0)
        self.mark(w - 6, 0, w - 1, h - 1, 0)

    def gem_col(self, x, y):
        return self.t['hi']

    def slot(self, x, y, ghost=None):
        cv, t = self.cv, self.t
        x0, y0 = x - 1, y - 1
        cv.rect(x0, y0, x0 + 17, y0 + 17, t['slot_in'])
        cv.hline(x0, x0 + 16, y0, t['slot_dark'])
        cv.vline(x0, y0, y0 + 16, t['slot_dark'])
        cv.hline(x0 + 1, x0 + 17, y0 + 17, t['slot_light'])
        cv.vline(x0 + 17, y0 + 1, y0 + 17, t['slot_light'])
        cv.put(x0 + 17, y0, t['slot_mid'])
        cv.put(x0, y0 + 17, t['slot_mid'])
        if ghost:
            cv.grid(ghost, {'#': t['ghost'][0], '+': t['ghost'][1]}, x, y)
        self.mark(x0, y0, x0 + 17, y0 + 17)

    def big_frame(self, x, y, gems=True):
        cv, t = self.cv, self.t
        x0, y0 = x - 5, y - 5
        x1, y1 = x0 + 25, y0 + 25
        HI, G, M, SH = t['hi'], t['gold'], t['mid'], t['sh']
        cv.rect(x0, y0, x1, y1, t['outline'])
        cv.hline(x0 + 1, x1 - 1, y0 + 1, HI)
        cv.vline(x0 + 1, y0 + 1, y1 - 1, HI)
        cv.hline(x0 + 1, x1 - 1, y1 - 1, SH)
        cv.vline(x1 - 1, y0 + 1, y1 - 1, SH)
        cv.hline(x0 + 2, x1 - 2, y0 + 2, G)
        cv.vline(x0 + 2, y0 + 2, y1 - 2, G)
        cv.hline(x0 + 2, x1 - 2, y1 - 2, M)
        cv.vline(x1 - 2, y0 + 2, y1 - 2, M)
        cv.put(x1 - 1, y0 + 1, G)
        cv.put(x0 + 1, y1 - 1, G)
        cx, cy = x + 7.5, y + 7.5
        glow = t['glow']
        for yy in range(y0 + 3, y1 - 2):
            for xx in range(x0 + 3, x1 - 2):
                d = math.hypot(xx + 0.5 - cx, yy + 0.5 - cy) / 10.5
                v = (1 - d) * 2.6 + (BAYER4[yy % 4, xx % 4] - 0.5) * 0.8
                cv.put(xx, yy, glow[int(min(max(round(v), 0), 2))])
        cv.hline(x0 + 3, x1 - 3, y0 + 3, t['slot_dark'])
        cv.vline(x0 + 3, y0 + 3, y1 - 3, t['slot_dark'])
        cv.hline(x0 + 4, x1 - 3, y1 - 3, t['slot_light'])
        cv.vline(x1 - 3, y0 + 4, y1 - 3, t['slot_light'])
        if gems:
            for gx, gy in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
                cv.put(gx, gy, self.gem_col(gx, gy))
            for gx, gy, c in ((x0 + 12, y0, HI), (x0 + 13, y0, HI), (x0 + 12, y1, SH), (x0 + 13, y1, SH)):
                cv.put(gx, gy, c)
        self.mark(x0 - 1, y0 - 1, x1 + 1, y1 + 1)

    def keep_clear(self, x0, y0, x1, y1):
        self.mark(x0, y0, x1, y1, 1)

    def glyph(self, rows, x, y, col, strength=0.24):
        c = mix(self.t['bot'], col, strength)
        self.cv.grid(rows, {'#': c, '*': mix(self.t['bot'], col, strength * 1.8)}, x, y)
        self.mark(x, y, x + len(rows[0]) - 1, y + len(rows) - 1, 2)

    def specks(self, seed, density=0.004, hi_chance=0.15):
        t = self.t
        r = rng(seed)
        n = int(self.w * self.h * density)
        placed = tries = 0
        while placed < n and tries < n * 30:
            tries += 1
            x, y = int(r.integers(6, self.w - 6)), int(r.integers(6, self.h - 6))
            if self.busy[max(0, y - 2):y + 3, max(0, x - 2):x + 3].any():
                continue
            if r.random() < hi_chance and not self.busy[max(0, y - 3):y + 4, max(0, x - 3):x + 4].any():
                self.cv.put(x, y, t['speck_hi'])
                for dx, dy in N4:
                    self.cv.put(x + dx, y + dy, t['speck'])
                self.mark(x - 1, y - 1, x + 1, y + 1, 3)
            else:
                self.cv.put(x, y, t['speck'])
                self.mark(x, y, x, y, 3)
            placed += 1

    def player_inventory(self, y_inv, y_hot, label_y):
        for row in range(3):
            for col in range(9):
                self.slot(8 + col * 18, y_inv + row * 18)
        for col in range(9):
            self.slot(8 + col * 18, y_hot)
        self.keep_clear(7, label_y - 1, 90, label_y + 9)
        yd = y_inv + 3 * 18 + 1
        for x in range(10, 166):
            if (x // 2) % 2 == 0:
                self.cv.put(x, yd, self.t['divider'])

    def save(self, name):
        return self.cv.save(f'textures/gui/{name}.png')


class PrismGui(Gui):
    """Ascension theme: corner gems cycle through prismatic colours."""
    def gem_col(self, x, y):
        return PRISM[(x * 3 + y) % len(PRISM)]


# ----------------------------------------------------------------- ghosts
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
]
GHOST_PLATE = [
    "................",
    "................",
    "..##########....",
    "..#++++++++##...",
    "..#+######+##...",
    "..#+#....#+##...",
    "..#+#.++.#+##...",
    "..#+#.++.#+##...",
    "..#+#....#+##...",
    "..#+######+##...",
    "..#++++++++##...",
    "..###########...",
    "...##########...",
]
GHOST_GEAR = [
    "................",
    "................",
    ".......##.......",
    "...##.####.##...",
    "...##########...",
    "....###++###....",
    "..####+..+####..",
    "..####+..+####..",
    "....###++###....",
    "...##########...",
    "...##.####.##...",
    ".......##.......",
]
GHOST_ORB = [
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
GHOST_STAR = [
    "................",
    "................",
    ".......#........",
    ".......#........",
    "......###.......",
    "......#+#.......",
    "..#####+#####...",
    "....##+++##.....",
    ".....##+##......",
    "....##...##.....",
    "...##.....##....",
]
GHOST_DUST = [
    "................",
    "................",
    "................",
    "................",
    "....+.....+.....",
    "................",
    ".........+......",
    ".......##.......",
    ".....######.....",
    "....########....",
    "...##########...",
    "..############..",
]
GHOST_DROP = [
    "................",
    "................",
    ".......#........",
    "......###.......",
    ".....#####......",
    "....###+###.....",
    "...###+++###....",
    "...##+++++##....",
    "...###+++###....",
    "....#######.....",
    ".....#####......",
]
GHOST_HEART = [
    "................",
    "................",
    "...###...###....",
    "..#####.#####...",
    "..###########...",
    "..#####+#####...",
    "...###+++###....",
    "....###+###.....",
    ".....#####......",
    "......###.......",
    ".......#........",
]

# ----------------------------------------------------------------- glyphs (7x7)
G_EYE = [".......", "..###..", ".#...#.", "#..*..#", ".#...#.", "..###..", "......."]
G_CROWN = [".......", "#..#..#", "##.#.##", "#######", "#.*.*.#", "#######", "......."]
G_STAR = ["...#...", "...#...", "..###..", "###*###", "..###..", "...#...", "...#..."]
G_MOON = ["..###..", ".##....", "##.....", "##.....", "##.....", ".##....", "..###.."]
G_SPIRAL = [".#####.", "#.....#", "#.###.#", "#.#*#.#", "#.#..#.", "#.###..", ".#....."]
G_RIFT = ["...#...", "..#.#..", ".#.*.#.", "#.*.*.#", ".#.*.#.", "..#.#..", "...#..."]
G_SUN = ["#..#..#", ".#.#.#.", "..###..", "###*###", "..###..", ".#.#.#.", "#..#..#"]
G_HALO = [".#####.", "#.....#", ".#####.", ".......", "...#...", "..###..", ".#####."]


def arrow_mask():
    m = np.zeros((16, 24), bool)
    for y in range(5, 11):
        m[y, 1:15] = True
    for i in range(8):
        y0, y1 = 1 + i, 14 - i
        m[y0:y1 + 1, 14 + i] = True
    return m


def station(theme, mats, ghosts, glyphs, arrow_stops, seed, gui_cls=Gui, extra=None):
    """Titan-forge layout: base (30,35), materials at x=66, output frame (124,35),
    empty arrow (90,35), filled arrow at u=176 v=0, inventory y=84, hotbar y=142."""
    g = gui_cls(176, 166, theme)
    g.panel()
    g.keep_clear(7, 5, 120, 14)
    cv, t = g.cv, g.t
    line, line_hi = t['line']
    # circuit: base -> spine -> material slots -> spine -> arrow
    ys = [y + 8 for (_, y) in mats]
    for x in range(48, 65):
        cv.put(x, 43, line)
    for x in range(83, 90):
        cv.put(x, 43, line)
    for sx in (56, 86):
        for y in range(min(ys), max(ys) + 1):
            cv.put(sx, y, line)
    for yy in ys:
        for x in range(56, 65):
            cv.put(x, yy, line)
        for x in range(83, 87):
            cv.put(x, yy, line)
    for (x, y) in ((56, 43), (86, 43), (48, 43)):
        cv.put(x, y, line_hi)
    g.slot(30, 35, ghosts[0])
    for (mx, my), gh in zip(mats, ghosts[1:]):
        g.slot(mx, my, gh)
    g.big_frame(124, 35)
    m = arrow_mask()
    ax, ay = 90, 35
    for y in range(16):
        for x in range(24):
            if m[y, x]:
                edge = not (m[y - 1, x] if y > 0 else False) or not (m[y, x - 1] if x > 0 else False)
                low = not (m[y + 1, x] if y < 15 else False) or not (m[y, x + 1] if x < 23 else False)
                cv.put(ax + x, ay + y, t['slot_dark'] if edge else t['slot_light'] if low else t['slot_in'])
    g.mark(ax, ay, ax + 23, ay + 15)
    grad = ramp(arrow_stops, 24)
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
    for (rows, x, y, col) in glyphs:
        g.glyph(rows, x, y, col)
    if extra:
        extra(g)
    g.keep_clear(7, 71, 90, 81)
    g.keep_clear(30, 60, 146, 70)          # condition text line (y=62)
    g.player_inventory(84, 142, 72)
    g.specks(seed)
    return g


# ----------------------------------------------------------------- screens
def imperial_forge():
    return station('imperial', [(66, 17), (66, 35), (66, 53)],
                   [GHOST_ARMOR, GHOST_PLATE, GHOST_GEAR, GHOST_ORB],
                   [(G_EYE, 10, 20, '#b88aff'), (G_CROWN, 10, 56, '#efc140'),
                    (G_CROWN, 156, 20, '#efc140'), (G_EYE, 156, 56, '#b88aff')],
                   ['#7429d8', '#9b55ff', '#d6a8ff', '#ffe07a', '#ffc040'], 11)


def sky_extra(g):
    """A faint constellation and crescent moon in the night panel."""
    cv = g.cv
    pts = [(14, 28), (20, 24), (24, 31), (18, 36)]
    for (a, b) in ((0, 1), (1, 2), (2, 3)):
        (x0, y0), (x1, y1) = pts[a], pts[b]
        n = max(abs(x1 - x0), abs(y1 - y0))
        for i in range(1, n, 2):
            cv.put(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), '#202a58')
    for (x, y) in pts:
        cv.put(x, y, '#8aa8f0')
    cv.put(20, 24, '#ffffff')
    g.keep_clear(12, 22, 26, 38)


def sky_altar():
    return station('sky', [(66, 17), (66, 53)],
                   [GHOST_ARMOR, GHOST_STAR, GHOST_DUST],
                   [(G_MOON, 156, 20, '#fff2c8'), (G_STAR, 10, 56, '#a8c8ff'), (G_STAR, 156, 56, '#fff2c8')],
                   ['#2a5cb0', '#4a88dc', '#a8d4ff', '#fff2c8', '#e0bd5a'], 12, extra=sky_extra)


def void_infuser():
    return station('void', [(66, 17), (66, 53)],
                   [GHOST_ARMOR, GHOST_DROP, GHOST_HEART],
                   [(G_RIFT, 10, 20, '#ff4ed6'), (G_SPIRAL, 10, 56, '#b67ae8'),
                    (G_SPIRAL, 156, 20, '#b67ae8'), (G_RIFT, 156, 56, '#ff4ed6')],
                   ['#4a1f74', '#9150cc', '#d82ab4', '#ff4ed6', '#ff96e8'], 13)


def ascension_extra(g):
    """Soft radiant halo and rays behind the output frame."""
    cv = g.cv
    cx, cy = 131.5, 42.5
    halo = ['#463a28', '#544530', '#64523a']
    for y in range(14, 72):
        for x in range(100, 166):
            if g.busy[y, x]:
                continue
            d = math.hypot(x + 0.5 - cx, (y + 0.5 - cy) * 1.1)
            v = (1 - d / 28) * 3.2 + (BAYER4[y % 4, x % 4] - 0.5) * 0.9
            k = int(round(v)) - 1
            if k >= 0:
                cv.put(x, y, halo[min(2, k)])
    for ang in range(0, 360, 45):
        a = math.radians(ang + 22.5)
        for rr in range(17, 25):
            x, y = int(cx + 0.5 + math.cos(a) * rr), int(cy + 0.5 + math.sin(a) * rr * 0.92)
            if rr % 2 == 0 and not g.busy[y, x]:
                cv.put(x, y, '#7a6646')
    g.keep_clear(104, 16, 162, 70)


def ascension_altar():
    return station('ascension', [(66, 17), (66, 35), (66, 53)],
                   [GHOST_ARMOR, GHOST_ORB, GHOST_STAR, GHOST_HEART],
                   [(G_HALO, 10, 20, '#fff2c8'), (G_SUN, 10, 56, '#ffe9a8'),
                    (G_SUN, 156, 20, '#ffe9a8'), (G_HALO, 156, 56, '#fff2c8')],
                   ['#ff9ae8', '#c09aff', '#7ff0ff', '#9affb8', '#fff27a', '#ffffff'], 14, gui_cls=PrismGui,
                   extra=ascension_extra)


PARCH = ['#2a241a', '#342c20', '#3c3326', '#443a2b', '#4e4331', '#5c4f3a']


def parchment_row(g, y):
    """Subtle aged-parchment strip for one quest row (y..y+19), darker icon well."""
    cv = g.cv
    x0, x1 = 7, 169
    y0, y1 = y - 1, y + 18
    r = rng(y * 13)
    for yy in range(y0, y1 + 1):
        for xx in range(x0, x1 + 1):
            v = r.random()
            c = PARCH[2] if v < 0.72 else PARCH[3] if v < 0.9 else PARCH[1]
            cv.put(xx, yy, c)
    # curled light top edge, shadowed bottom edge, ragged ends
    cv.hline(x0 + 1, x1 - 1, y0, PARCH[5])
    cv.hline(x0 + 1, x1 - 1, y0 + 1, PARCH[4])
    cv.hline(x0 + 1, x1 - 1, y1, PARCH[0])
    for yy in range(y0, y1 + 1):
        if (yy * 7) % 5 == 0:
            cv.put(x0, yy, TRANSPARENT)
            cv.put(x0, yy, g.t['bot'])
        else:
            cv.put(x0, yy, PARCH[3])
        cv.put(x1, yy, PARCH[1] if (yy * 3) % 4 else g.t['bot'])
    cv.put(x0, y0, g.t['bot'])
    cv.put(x1, y0, g.t['bot'])
    cv.put(x0, y1, g.t['bot'])
    cv.put(x1, y1, g.t['bot'])
    # recessed well behind the item icon at (10, y+1)
    wx0, wy0 = 9, y
    cv.rect(wx0, wy0, wx0 + 17, wy0 + 17, PARCH[1])
    cv.hline(wx0, wx0 + 16, wy0, PARCH[0])
    cv.vline(wx0, wy0, wy0 + 16, PARCH[0])
    cv.hline(wx0 + 1, wx0 + 17, wy0 + 17, PARCH[4])
    cv.vline(wx0 + 17, wy0 + 1, wy0 + 17, PARCH[4])
    # wax seal dot + faint ruled line under the reward text
    cv.put(28, y + 9, '#5a3a2a')
    for xx in range(30, 112):
        if xx % 3 != 2:
            cv.put(xx, y + 19 - 1, PARCH[1])
    g.mark(x0, y0, x1, y1, 2)


def quest_board():
    g = Gui(176, 186, 'celestial')
    g.panel()
    g.keep_clear(7, 5, 120, 14)
    for y in (20, 44, 68):
        parchment_row(g, y)
    # tiny gold star next to the title area's right end
    g.cv.grid(["..a..", ".aba.", "abWba", ".aba.", "..a.."], {'a': '#7A5C22', 'b': '#C9A54C', 'W': '#F2D27A'}, 160, 7)
    g.keep_clear(158, 5, 166, 13)
    g.player_inventory(104, 162, 92)
    g.specks(15)
    return g


GUIS = {'imperial_forge': (imperial_forge, (176, 166)), 'sky_altar': (sky_altar, (176, 166)),
        'void_infuser': (void_infuser, (176, 166)), 'ascension_altar': (ascension_altar, (176, 166)),
        'quest_board': (quest_board, (176, 186))}


def mock(img, name):
    from PIL import ImageDraw
    im = img.copy()
    d = ImageDraw.Draw(im)
    f = _font(8)
    titles = {'imperial_forge': 'Imperial Forge', 'sky_altar': 'Sky Altar', 'void_infuser': 'Void Infuser',
              'ascension_altar': 'Ascension Altar', 'quest_board': 'Quest Board'}
    d.text((8, 6), titles[name], fill='#F2E6C9', font=f)
    if name == 'quest_board':
        d.text((8, 92), 'Inventory', fill='#BFB49A', font=f)
        for i, y in enumerate((20, 44, 68)):
            d.text((30, y + 1), f'Deliver 16 Stardust', fill='#F2E6C9' if i else '#7A8F6A', font=f)
            d.text((30, y + 11), '120 Asters', fill='#FFD966', font=f)
            d.rectangle((118, y, 167, y + 17), fill='#6b6b6b', outline='#000000')
    else:
        d.text((8, 72), 'Inventory', fill='#BFB49A', font=f)
        if name == 'sky_altar':
            d.text((48, 62), 'Needs the night sky', fill='#FF8080', font=f)
    return im


def main():
    out, mocks = [], []
    for name, (fn, (w, h)) in GUIS.items():
        g = fn()
        g.save(name)
        im = g.cv.pil()
        out.append((name, im))
        mocks.append((name, mock(im.crop((0, 0, w, h)), name)))
    print(sheet(out, 'gui.png', scale=2, cols=3))
    print(sheet(mocks, 'gui_mock.png', scale=3, cols=2))


if __name__ == '__main__':
    main()
