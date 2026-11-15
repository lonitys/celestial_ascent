"""Aster coins: copper, silver, gold, titan, ender, star, void.

Each coin is a 15px disc centred on (7,7): outline ring, raised rim
(lit top-left), recessed inner wall (shadowed top-left), and a flat field
carrying an embossed 4-point star whose arms are split into a lit and a
shaded half (nether-star style). Tier motifs are hand placed on top.

Ring depth map of the disc (0 outline, 1 rim, 2 inner wall, 3+ field):
    .....00000......
    ...001111100....
    ..01122222110...
    .0122333332210..
    .0123444443210..
    012345555543210.
    012345666543210.
    012345676543210.
"""
from common import *

CX, CY = 7, 7

# tone indices: 0 outline-dark, 1 outline-lit, 2 dark, 3 mid-dark, 4 mid, 5 light, 6 bright, 7 glint
PALETTES = {
    'copper': ['#3b1609', '#62290f', '#8a3d1a', '#b0582a', '#cf773d', '#eb9c5e', '#ffcf9c', '#fff1dc'],
    'silver': ['#20232e', '#3f4657', '#5f687e', '#8690a6', '#aab3c5', '#d0d7e4', '#eff3f9', '#ffffff'],
    'gold':   ['#4a2803', '#7c4a05', '#ae730f', '#d49a18', '#ecbd2c', '#fadd60', '#fff4ae', '#ffffff'],
    'titan':  ['#0b1b20', '#1c3a41', '#2a5860', '#3b767c', '#589896', '#80bdb6', '#bde8dd', '#f2fffa'],
    'ender':  ['#07030c', '#1d0c2b', '#2a1240', '#3c1c59', '#542d78', '#73479a', '#9f76c6', '#e6d6ff'],
    'star':   ['#6e4c14', '#a8802e', '#cfa04a', '#e6c06a', '#f5dc98', '#fff1c8', '#fffbec', '#ffffff'],
    'void':   ['#020104', '#08030f', '#10071c', '#180b29', '#221236', '#2f1a4a', '#432667', '#ffffff'],
}

STAR = [  # 11x11, centre (5,5)
    ".....#.....",
    ".....#.....",
    "....###....",
    "....###....",
    "..#######..",
    "###########",
    "..#######..",
    "....###....",
    "....###....",
    ".....#.....",
    ".....#.....",
]
STAR_PTS = {(i - 5, j - 5) for j, row in enumerate(STAR) for i, ch in enumerate(row) if ch == '#'}
DIAG = [(-3, -3), (3, -3), (-3, 3), (3, 3)]


def star_tone(dx, dy):
    """Tone for a star pixel: each arm has a lit half and a shaded half."""
    if dx == 0 and dy == 0:
        return 7
    if abs(dy) >= abs(dx):            # vertical arm
        if dy < 0:
            return 6 if dx <= 0 else 5
        return 5 if dx < 0 else 4
    if dx < 0:                        # horizontal arm
        return 6 if dy <= 0 else 5
    return 5 if dy < 0 else 4


def quad_tone(dx, dy):
    """Tone for a stud in a given diagonal quadrant."""
    if dx < 0 and dy < 0:
        return 6
    if dx > 0 and dy > 0:
        return 4
    return 5


class Coin:
    def __init__(self, pal, rim=None, field=3):
        self.p = [hexc(c) for c in pal]
        self.rp = [hexc(c) for c in rim] if rim else self.p
        self.field = field
        self.cv = Canvas()
        self.mask = disc_mask(16, 16, CX, CY, 7.4)
        self.depth = ring_depth(self.mask)
        self.raised = set()
        self._body()

    def _body(self):
        p, rp = self.p, self.rp
        for y in range(16):
            for x in range(16):
                if not self.mask[y, x]:
                    continue
                d = self.depth[y, x]
                dot = light_dot(x - CX, y - CY)
                if d == 0:
                    c = rp[1] if dot > 0.35 else rp[0]
                elif d == 1:
                    c = rp[6] if dot > 0.6 else rp[5] if dot > 0.1 else rp[4] if dot > -0.5 else rp[3]
                elif d == 2:
                    c = p[2] if dot > 0.3 else p[5] if dot < -0.4 else p[3]
                else:
                    c = p[self.field]
                self.cv.put(x, y, c)

    def raise_px(self, dx, dy, c):
        self.cv.put(CX + dx, CY + dy, c)
        self.raised.add((dx, dy))

    def star(self, tones=None):
        t = tones or self.p
        for dx, dy in STAR_PTS:
            self.raise_px(dx, dy, t[star_tone(dx, dy)])

    def studs(self, tones=None):
        t = tones or self.p
        for dx, dy in DIAG:
            self.raise_px(dx, dy, t[quad_tone(dx, dy)])

    def shadows(self, tone=None):
        """Cast a 1px shadow from raised pixels onto the field, lower right."""
        c = self.p[self.field - 1] if tone is None else tone
        for dx, dy in list(self.raised):
            q = (dx + 1, dy + 1)
            if q in self.raised:
                continue
            x, y = CX + q[0], CY + q[1]
            if self.depth[y, x] >= 3:
                self.cv.put(x, y, c)

    def glint(self, tone=7):
        for x, y in ((3, 2), (2, 3)):
            self.cv.put(x, y, self.rp[tone])


# ---------------------------------------------------------------- tiers
def copper():
    c = Coin(PALETTES['copper'])
    c.star()
    c.shadows()
    c.glint(6)
    return c.cv


def silver():
    c = Coin(PALETTES['silver'])
    c.star()
    c.studs()
    c.shadows()
    c.glint()
    return c.cv


def gold():
    c = Coin(PALETTES['gold'])
    c.star()
    c.studs()
    c.shadows()
    # shine sparkle straddling the lit rim
    c.cv.put(3, 3, '#ffffff')
    for x, y in ((3, 2), (2, 3), (4, 3), (3, 4)):
        c.cv.put(x, y, '#fff6c0')
    c.cv.put(3, 1, '#fde58a')
    c.cv.put(1, 3, '#fde58a')
    return c.cv


def titan():
    c = Coin(PALETTES['titan'])
    c.star()
    c.shadows()
    gems = {(-3, -3): ('#9ffcff', '#2fb6d6'), (3, -3): ('#7aa6ff', '#2c4fd0'),
            (-3, 3): ('#fff07a', '#d39a12'), (3, 3): ('#ffb05a', '#c4480e')}
    for (dx, dy), (hi, lo) in gems.items():
        c.cv.put(CX + dx, CY + dy, hi)
    c.glint()
    return c.cv


def ender():
    c = Coin(PALETTES['ender'])
    c.star()
    c.shadows()
    eye = [".g.", "gpg", ".G."]
    c.cv.grid(eye, {'g': '#42d68e', 'p': '#06281a', 'G': '#1f8a58'}, CX - 1, CY - 1)
    c.cv.put(CX - 1, CY - 1, '#c4ffe0')
    c.glint(6)
    return c.cv


def star():
    c = Coin(PALETTES['star'], field=2)
    white = [hexc(x) for x in ['#000000', '#000000', '#000000', '#000000', '#fbe7b0', '#fff6dc', '#ffffff', '#ffffff']]
    c.star(white)
    # radiant: arm tips reach through the inner wall
    for dx, dy, t in ((0, -6, 6), (-6, 0, 6), (6, 0, 5), (0, 6, 5)):
        c.cv.put(CX + dx, CY + dy, white[t])
    c.studs(white)
    c.shadows()
    c.glint()
    # sparkles outside the rim (plus shapes: bright core, soft arms)
    core, arm = hexc('#ffffff'), hexc('#ffe9a8')
    for sx, sy in ((14, 1), (1, 14)):
        c.cv.put(sx, sy, core)
        for ex, ey in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            c.cv.put(sx + ex, sy + ey, arm)
    c.cv.put(14, 13, hexc('#fff3c4'))
    return c.cv


def void():
    rim = ['#22031c', '#4a0a3d', '#7a1466', '#a8208a', '#cf38ad', '#f05fd0', '#ff9be8', '#ffffff']
    c = Coin(PALETTES['void'], rim=rim, field=2)
    vt = [hexc(x) for x in ['#000000', '#000000', '#000000', '#000000', '#5a2c8c', '#8a48c0', '#d070f0', '#ffffff']]
    c.star(vt)
    c.shadows(hexc('#04020a'))
    for x, y in ((4, 9), (10, 4), (9, 10)):
        c.cv.put(x, y, '#cfd8ff')
    c.glint(6)
    return c.cv


TIERS = [('copper_aster', copper), ('silver_aster', silver), ('gold_aster', gold),
         ('titan_aster', titan), ('ender_aster', ender), ('star_aster', star), ('void_aster', void)]


def main():
    out = []
    for name, fn in TIERS:
        cv = fn()
        cv.save(f'textures/item/{name}.png')
        out.append((name, cv.pil()))
    print(contact_sheet(out, 'coins.png', cols=7))


if __name__ == '__main__':
    main()
