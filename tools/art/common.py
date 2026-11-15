"""Shared helpers for the Celestial Ascent art generators.

Everything here is deterministic so the art is reproducible: colour/ramp
helpers, a small RGBA canvas wrapper, string-grid pixel maps, outlines,
tileable noise, ordered dithering and contact-sheet output.
"""
import colorsys
import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
ASSETS = os.path.join(ROOT, 'src', 'main', 'resources', 'assets', 'celestialascent')
PREVIEW = os.path.join(HERE, 'preview')

TRANSPARENT = (0, 0, 0, 0)


# --------------------------------------------------------------------------
# colour helpers
# --------------------------------------------------------------------------
def hexc(h, a=255):
    """'#rrggbb' -> (r, g, b, a)."""
    if isinstance(h, tuple):
        return h if len(h) == 4 else (h[0], h[1], h[2], a)
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def mix(c1, c2, t):
    c1, c2 = hexc(c1), hexc(c2)
    return tuple(int(round(c1[i] + (c2[i] - c1[i]) * t)) for i in range(4))


def scale(c, f):
    c = hexc(c)
    return (min(255, int(c[0] * f)), min(255, int(c[1] * f)), min(255, int(c[2] * f)), c[3])


def with_alpha(c, a):
    c = hexc(c)
    return (c[0], c[1], c[2], a)


def ramp(stops, n):
    """Interpolate a list of hex stops into n evenly spaced colours."""
    stops = [hexc(s) for s in stops]
    if n == 1:
        return [stops[0]]
    out = []
    for i in range(n):
        t = i / (n - 1) * (len(stops) - 1)
        k = min(int(t), len(stops) - 2)
        out.append(mix(stops[k], stops[k + 1], t - k))
    return out


def hsv_ramp(base, n=6, hue_shift=0.04, sat_gain=0.15, val_lo=0.25, val_hi=1.0):
    """Hue-shifted ramp around a base colour: shadows drift cooler, lights warmer."""
    r, g, b, _ = hexc(base)
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    out = []
    for i in range(n):
        t = i / (n - 1)          # 0 dark .. 1 light
        hh = (h + (0.5 - t) * hue_shift * 2) % 1.0
        ss = max(0.0, min(1.0, s + (0.5 - t) * sat_gain * 2))
        vv = val_lo + (val_hi - val_lo) * t
        rr, gg, bb = colorsys.hsv_to_rgb(hh, ss, vv)
        out.append((int(rr * 255), int(gg * 255), int(bb * 255), 255))
    return out


# --------------------------------------------------------------------------
# canvas
# --------------------------------------------------------------------------
class Canvas:
    def __init__(self, w=16, h=16, fill=TRANSPARENT):
        self.w, self.h = w, h
        self.a = np.zeros((h, w, 4), dtype=np.uint8)
        if fill != TRANSPARENT:
            self.a[:, :] = hexc(fill)

    # basic access ---------------------------------------------------------
    def inb(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h

    def put(self, x, y, c):
        if c is None:
            return
        if self.inb(x, y):
            self.a[y, x] = hexc(c)

    def blend(self, x, y, c, t=None):
        """Alpha-blend colour c (using its alpha, or t) over the pixel."""
        if not self.inb(x, y):
            return
        c = hexc(c)
        al = (c[3] / 255.0) if t is None else t
        old = self.a[y, x].astype(float)
        if old[3] == 0:
            self.a[y, x] = (c[0], c[1], c[2], int(255 * al))
            return
        new = old[:3] * (1 - al) + np.array(c[:3]) * al
        self.a[y, x, :3] = np.clip(new, 0, 255)

    def get(self, x, y):
        if not self.inb(x, y):
            return TRANSPARENT
        return tuple(int(v) for v in self.a[y, x])

    def opaque(self, x, y):
        return self.inb(x, y) and self.a[y, x, 3] > 0

    def rect(self, x0, y0, x1, y1, c):
        """Filled rectangle, inclusive coords."""
        c = hexc(c)
        x0, x1 = max(0, x0), min(self.w - 1, x1)
        y0, y1 = max(0, y0), min(self.h - 1, y1)
        if x0 > x1 or y0 > y1:
            return
        self.a[y0:y1 + 1, x0:x1 + 1] = c

    def hline(self, x0, x1, y, c):
        self.rect(x0, y, x1, y, c)

    def vline(self, x, y0, y1, c):
        self.rect(x, y0, x, y1, c)

    def frame(self, x0, y0, x1, y1, c):
        self.hline(x0, x1, y0, c)
        self.hline(x0, x1, y1, c)
        self.vline(x0, y0, y1, c)
        self.vline(x1, y0, y1, c)

    def grid(self, rows, pal, ox=0, oy=0):
        """Paint a string pixel map. Characters missing from pal (and '.'/' ')
        are skipped, so grids can be layered."""
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch in ('.', ' '):
                    continue
                if ch in pal and pal[ch] is not None:
                    self.put(ox + i, oy + j, pal[ch])

    def paste(self, other, ox, oy):
        """Composite another canvas (alpha over)."""
        for y in range(other.h):
            for x in range(other.w):
                c = other.get(x, y)
                if c[3] == 255:
                    self.put(ox + x, oy + y, c)
                elif c[3] > 0:
                    self.blend(ox + x, oy + y, c)

    def copy(self):
        c = Canvas(self.w, self.h)
        c.a = self.a.copy()
        return c

    def mask(self):
        return self.a[:, :, 3] > 0

    def pil(self):
        return Image.fromarray(self.a, 'RGBA')

    def save(self, rel_path):
        """Save relative to the mod assets dir (or absolute)."""
        path = rel_path if os.path.isabs(rel_path) else os.path.join(ASSETS, rel_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.pil().save(path)
        return path

    @staticmethod
    def load(path):
        im = Image.open(path).convert('RGBA')
        c = Canvas(im.width, im.height)
        c.a = np.array(im, dtype=np.uint8)
        return c


# --------------------------------------------------------------------------
# outlines / masks
# --------------------------------------------------------------------------
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
N8 = N4 + ((1, 1), (-1, -1), (1, -1), (-1, 1))


def outline(cv, tl, br=None, diag=False):
    """Add a 1px outline around opaque pixels.

    Outline pixels on the lower/right side of the shape get `br`, the rest `tl`.
    `tl`/`br` may be colours or callables taking the neighbouring colour.
    """
    br = br if br is not None else tl
    m = cv.mask()
    adds = []
    nb = N8 if diag else N4
    for y in range(cv.h):
        for x in range(cv.w):
            if m[y, x]:
                continue
            touching = [(x + dx, y + dy) for dx, dy in nb
                        if 0 <= x + dx < cv.w and 0 <= y + dy < cv.h and m[y + dy, x + dx]]
            if not touching:
                continue
            # shape lies up/left of this pixel -> it's on the bottom/right edge
            lower_right = (x > 0 and m[y, x - 1]) or (y > 0 and m[y - 1, x])
            upper_left = (x < cv.w - 1 and m[y, x + 1]) or (y < cv.h - 1 and m[y + 1, x])
            col = br if (lower_right and not upper_left) else tl
            if callable(col):
                nx, ny = touching[0]
                col = col(cv.get(nx, ny))
            adds.append((x, y, col))
    for x, y, c in adds:
        cv.put(x, y, c)


def boundary(mask):
    """Pixels of mask that have a 4-neighbour outside the mask (thin border)."""
    h, w = mask.shape
    pad = np.pad(mask, 1, constant_values=False)
    inner = pad[1:-1, 1:-1] & pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:]
    return mask & ~inner


def ring_depth(mask):
    """Erosion depth of each mask pixel (0 = border)."""
    depth = np.full(mask.shape, -1, dtype=int)
    m = mask.copy()
    d = 0
    while m.any():
        b = boundary(m)
        depth[b] = d
        m = m & ~b
        d += 1
    return depth


def disc_mask(w, h, cx, cy, r):
    ys, xs = np.mgrid[0:h, 0:w]
    return (xs - cx) ** 2 + (ys - cy) ** 2 <= r * r


def light_dot(dx, dy):
    """Dot of a 2D direction with a top-left light (screen coords, y down)."""
    d = math.hypot(dx, dy)
    if d == 0:
        return 1.0
    return (-dx - dy) / (math.sqrt(2) * d)


# --------------------------------------------------------------------------
# noise & dithering
# --------------------------------------------------------------------------
BAYER4 = np.array([[0, 8, 2, 10],
                   [12, 4, 14, 6],
                   [3, 11, 1, 9],
                   [15, 7, 13, 5]]) / 16.0


def rng(seed):
    return np.random.default_rng(seed)


def tile_noise(w, h, cells, seed, octaves=1, persistence=0.5):
    """Tileable value noise in [0,1], `cells` lattice cells across the image."""
    r = rng(seed)
    total = np.zeros((h, w))
    amp, norm = 1.0, 0.0
    for o in range(octaves):
        c = cells * (2 ** o)
        lat = r.random((c, c))
        ys, xs = np.mgrid[0:h, 0:w]
        fx = xs / w * c
        fy = ys / h * c
        x0 = np.floor(fx).astype(int)
        y0 = np.floor(fy).astype(int)
        tx = fx - x0
        ty = fy - y0
        tx = tx * tx * (3 - 2 * tx)
        ty = ty * ty * (3 - 2 * ty)
        x1 = (x0 + 1) % c
        y1 = (y0 + 1) % c
        x0 %= c
        y0 %= c
        a = lat[y0, x0] * (1 - tx) + lat[y0, x1] * tx
        b = lat[y1, x0] * (1 - tx) + lat[y1, x1] * tx
        total += (a * (1 - ty) + b * ty) * amp
        norm += amp
        amp *= persistence
    return total / norm


def quantize(values, pal, dither=0.0):
    """Map a float array in [0,1] onto a palette (list of colours) with
    optional Bayer dithering strength (0..1 of a step)."""
    h, w = values.shape
    n = len(pal)
    out = Canvas(w, h)
    for y in range(h):
        for x in range(w):
            v = values[y, x] * (n - 1)
            if dither:
                v += (BAYER4[y % 4, x % 4] - 0.5) * dither
            k = int(round(min(max(v, 0), n - 1)))
            out.put(x, y, pal[k])
    return out


# --------------------------------------------------------------------------
# JSON / file helpers
# --------------------------------------------------------------------------
def write_json(rel_path, data):
    path = rel_path if os.path.isabs(rel_path) else os.path.join(ASSETS, rel_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='\n') as f:
        json.dump(data, f, indent=2)
        f.write('\n')
    return path


# --------------------------------------------------------------------------
# contact sheets
# --------------------------------------------------------------------------
def _font(size=12):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def contact_sheet(items, out_name, scale=8, cols=6, bg=(118, 118, 118), label=True, pad=12):
    """items: list of (label, PIL.Image). Upscales nearest-neighbour onto grey."""
    ims = [(n, im.convert('RGBA').resize((im.width * scale, im.height * scale), Image.NEAREST))
           for n, im in items]
    cw = max(im.width for _, im in ims)
    ch = max(im.height for _, im in ims)
    lab = 18 if label else 0
    rows = (len(ims) + cols - 1) // cols
    cols = min(cols, len(ims))
    sheet = Image.new('RGBA', (cols * (cw + pad) + pad, rows * (ch + pad + lab) + pad), bg + (255,))
    d = ImageDraw.Draw(sheet)
    f = _font(13)
    for i, (n, im) in enumerate(ims):
        x = pad + (i % cols) * (cw + pad)
        y = pad + (i // cols) * (ch + pad + lab)
        sheet.alpha_composite(im, (x, y))
        if label:
            d.text((x, y + ch + 2), n, fill=(20, 20, 20, 255), font=f)
    os.makedirs(PREVIEW, exist_ok=True)
    path = os.path.join(PREVIEW, out_name)
    sheet.save(path)
    return path


def scale_strip(items, out_name, scales=(1, 2, 3, 4), bg=(139, 139, 139)):
    """Show each image at several scales side by side (for judging in-game read)."""
    rows = []
    for n, im in items:
        ims = [im.convert('RGBA').resize((im.width * s, im.height * s), Image.NEAREST) for s in scales]
        rows.append(ims)
    w = max(sum(i.width + 8 for i in r) for r in rows) + 8
    h = sum(max(i.height for i in r) + 8 for r in rows) + 8
    sheet = Image.new('RGBA', (w, h), bg + (255,))
    y = 8
    for r in rows:
        x = 8
        for i in r:
            sheet.alpha_composite(i, (x, y))
            x += i.width + 8
        y += max(i.height for i in r) + 8
    path = os.path.join(PREVIEW, out_name)
    sheet.save(path)
    return path
