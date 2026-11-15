"""Shared helpers for the wave-2 art (Lost Ender Empire, Fallen Stars, Abyss, Ascendant).

Builds on tools/art/common.py (imported, never modified) and adds the wave-2
palettes, preview output into tools/art/wave2/preview, sphere shading and a few
pixel-art primitives.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..')))

import numpy as np                     # noqa: E402
from PIL import Image, ImageDraw       # noqa: E402

from common import (ASSETS, BAYER4, N4, N8, TRANSPARENT, Canvas, _font, boundary,  # noqa: E402,F401
                    disc_mask, hexc, light_dot, mix, outline, quantize, ramp, ring_depth,
                    rng, scale, tile_noise, with_alpha, write_json)

PREVIEW = os.path.join(HERE, 'preview')
os.makedirs(PREVIEW, exist_ok=True)

# ----------------------------------------------------------------- palettes
# Lost Ender Empire
PURPUR = ['#3e2442', '#563260', '#70447a', '#8a5a92', '#a676aa', '#bf94c2', '#d8b6da', '#eed8ee']
OBSID = ['#06030b', '#0d0817', '#150d23', '#1e1430', '#291b40', '#372553', '#4a336c', '#634a8c']
GOLD = ['#4a2e06', '#7a520e', '#a8761a', '#d29e2a', '#efc140', '#ffe07a', '#fff4c4']
VIOLET = ['#2a0a52', '#4a149a', '#7429d8', '#9b55ff', '#bd8cff', '#dcc0ff', '#f6ecff']
PEARL = ['#06261f', '#0b4a3e', '#127060', '#22977e', '#4cc4a6', '#9ae8d2', '#e0fff4']
# Fallen Stars
NAVY = ['#070a1a', '#0c1128', '#121a38', '#19234a', '#212e5c', '#2b3a70', '#384a86', '#4a5e9e']
WGOLD = ['#5a4012', '#8c6a22', '#bb9436', '#e0bd5a', '#f4dc8e', '#fff2c8', '#ffffff']
PALE = ['#1b3a7a', '#2a5cb0', '#4a88dc', '#78b2f2', '#a8d4ff', '#d4ecff', '#f4fbff']
# Abyss
ABYSS = ['#050308', '#0b0711', '#110b1a', '#171024', '#1f162f', '#291d3c', '#34264b', '#41305c']
MAGENTA = ['#3e0834', '#6e0f5c', '#a3188a', '#d82ab4', '#ff4ed6', '#ff96e8', '#ffd8f6']
SICK = ['#2c1048', '#4a1f74', '#6c32a0', '#9150cc', '#b67ae8', '#d8b0ff']
# Ascendant
RADIANT = ['#6a4a14', '#9a7424', '#c89e3e', '#e8c868', '#f8e4a2', '#fff6dc', '#ffffff']
MARBLE = ['#8e8578', '#aaa196', '#c2bab0', '#d6d0c8', '#e6e2dc', '#f2f0ec', '#fcfbf8']
PRISM = ['#7ff0ff', '#9aa8ff', '#ff9ae8', '#fff27a', '#9affb8']

STARLIGHT = '#fff6dc'


# ----------------------------------------------------------------- sheets
def sheet(items, out_name, scale=8, cols=6, bg=(118, 118, 118), label=True, pad=12):
    """items: list of (label, PIL.Image). Nearest-neighbour upscaled contact sheet."""
    ims = [(n, im.convert('RGBA').resize((im.width * scale, im.height * scale), Image.NEAREST))
           for n, im in items]
    cw = max(im.width for _, im in ims)
    ch = max(im.height for _, im in ims)
    lab = 18 if label else 0
    cols = min(cols, len(ims))
    rows = (len(ims) + cols - 1) // cols
    out = Image.new('RGBA', (cols * (cw + pad) + pad, rows * (ch + pad + lab) + pad), tuple(bg) + (255,))
    d = ImageDraw.Draw(out)
    f = _font(13)
    for i, (n, im) in enumerate(ims):
        x = pad + (i % cols) * (cw + pad)
        y = pad + (i // cols) * (ch + pad + lab)
        out.alpha_composite(im, (x, y))
        if label:
            d.text((x, y + ch + 2), n, fill=(20, 20, 20, 255), font=f)
    path = os.path.join(PREVIEW, out_name)
    out.save(path)
    return path


def tiled(im, n=3):
    """n x n repeat of a texture (seam check)."""
    t = Image.new('RGBA', (im.width * n, im.height * n))
    for j in range(n):
        for i in range(n):
            t.paste(im, (i * im.width, j * im.height))
    return t


def inventory_strip(items, out_name, scales=(1, 2, 3), bg=(139, 139, 139)):
    """Items on vanilla slot grey at small scales to judge the in-game read."""
    rows = []
    for n, im in items:
        rows.append([im.convert('RGBA').resize((im.width * s, im.height * s), Image.NEAREST) for s in scales])
    w = sum(i.width + 6 for i in rows[0]) + 6
    per = len(rows)
    cols = 4
    nrow = (per + cols - 1) // cols
    cell_w = w
    cell_h = max(i.height for r in rows for i in r) + 6
    out = Image.new('RGBA', (cols * cell_w + 6, nrow * cell_h + 6), bg + (255,))
    for k, r in enumerate(rows):
        x = 6 + (k % cols) * cell_w
        y = 6 + (k // cols) * cell_h
        for i in r:
            out.alpha_composite(i, (x, y))
            x += i.width + 6
    path = os.path.join(PREVIEW, out_name)
    out.save(path)
    return path


# ----------------------------------------------------------------- shading
def sphere(cx, cy, R, light=(-0.6, -0.65, 0.5), glow=0.0, w=16, h=16, squash=1.0):
    """{(x,y): value in [0,1]} lambert + optional inner glow, for a disc."""
    L = np.array(light, float)
    L /= np.linalg.norm(L)
    out = {}
    for y in range(h):
        for x in range(w):
            dx, dy = (x + 0.5 - cx) / R, (y + 0.5 - cy) / (R * squash)
            r2 = dx * dx + dy * dy
            if r2 > 1.0:
                continue
            nz = math.sqrt(1 - r2)
            lam = max(0.0, dx * L[0] + dy * L[1] + nz * L[2])
            inner = (1 - math.sqrt(r2)) ** 1.2
            out[(x, y)] = min(1.0, glow * inner + (1 - glow) * lam)
    return out


def paint_levels(cv, vals, pal, cuts):
    for (x, y), v in vals.items():
        k = 0
        while k < len(cuts) and v > cuts[k]:
            k += 1
        cv.put(x, y, pal[k])


def even_cuts(n, lo=0.12, hi=0.9):
    return [lo + (hi - lo) * i / (n - 2) for i in range(n - 1)] if n > 1 else []


def mask_from(rows, ch='#'):
    m = np.zeros((len(rows), len(rows[0])), bool)
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c in ch:
                m[y, x] = True
    return m


def sparkle(cv, x, y, core='#ffffff', arm='#fff2c8', size=1, only_empty=False):
    """Plus-shaped glint. size 1 = 3x3 plus, 2 = longer arms."""
    pts = [(x, y, core)]
    for dx, dy in N4:
        pts.append((x + dx, y + dy, arm))
        if size >= 2:
            pts.append((x + 2 * dx, y + 2 * dy, with_alpha(arm, 255)))
    for px, py, c in pts:
        if only_empty and cv.opaque(px, py) and (px, py) != (x, y):
            continue
        cv.put(px, py, c)


def put_if_empty(cv, x, y, c):
    if not cv.opaque(x, y):
        cv.put(x, y, c)


def shade_edges(cv, lo, hi=None, only=None):
    """Darken pixels on the lower/right boundary of the opaque shape (inner rim),
    optionally brighten the upper/left boundary."""
    m = cv.mask()
    pts = []
    for y in range(cv.h):
        for x in range(cv.w):
            if not m[y, x]:
                continue
            if only is not None and not only(x, y):
                continue
            br = (x + 1 >= cv.w or not m[y, x + 1]) or (y + 1 >= cv.h or not m[y + 1, x])
            tl = (x - 1 < 0 or not m[y, x - 1]) or (y - 1 < 0 or not m[y - 1, x])
            if br and not tl and lo:
                pts.append((x, y, lo))
            elif tl and not br and hi:
                pts.append((x, y, hi))
    for x, y, c in pts:
        cv.put(x, y, c)


def recolor(cv, mapping):
    """Replace exact colours: mapping {hex: hex}."""
    for src, dst in mapping.items():
        s = np.array(hexc(src))
        sel = (cv.a == s).all(axis=2)
        cv.a[sel] = hexc(dst)


def lum(c):
    c = hexc(c)
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
