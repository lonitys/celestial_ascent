"""Promotional art for the CurseForge page and the in-game mod list.

  release/curseforge/logo.png      1024x1024 project logo (CurseForge shows it at 400x400)
  release/curseforge/banner.png    1920x600 header for the description
  src/main/resources/celestialascent_logo.png   mod list logo (inside the jar)

Bosses are rendered from the real models in their third stage (stage3 textures and glow masks)
with the boss preview renderer, cut out by difference matting (rendered on black and on white)
and laid over a generated nebula. The title uses an original blocky pixel font drawn here.
Run: python tools/art/gen_promo.py
"""
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'bosses'))
import bosslib as bl  # noqa: E402
import geo_preview as gp  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(ROOT, 'release', 'curseforge')
TEX = os.path.join(bl.ASSETS, 'textures', 'entity')

# ------------------------------------------------------------------ background


def noise(w, h, cells, seed, octaves=4):
    rng = np.random.default_rng(seed)
    total = np.zeros((h, w))
    amp, norm = 1.0, 0.0
    for o in range(octaves):
        c = cells * 2 ** o
        lat = rng.random((c + 1, c + 1))
        ys, xs = np.mgrid[0:h, 0:w]
        fx, fy = xs / w * c, ys / h * c
        x0, y0 = fx.astype(int), fy.astype(int)
        tx, ty = fx - x0, fy - y0
        tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
        a = lat[y0, x0] * (1 - tx) + lat[y0, x0 + 1] * tx
        b = lat[y0 + 1, x0] * (1 - tx) + lat[y0 + 1, x0 + 1] * tx
        total += (a * (1 - ty) + b * ty) * amp
        norm += amp
        amp *= 0.5
    return total / norm


def nebula(w, h, seed, glow_at=None, glow_r=0.4, glow_col=(255, 214, 140)):
    """Deep indigo sky with violet and blue nebula clouds, stars and an optional soft glow."""
    base = np.zeros((h, w, 3))
    base[:] = (8, 9, 26)
    n1 = noise(w, h, 3, seed)
    n2 = noise(w, h, 5, seed + 7)
    violet = np.clip((n1 - 0.45) * 2.2, 0, 1) ** 1.6
    blue = np.clip((n2 - 0.5) * 2.4, 0, 1) ** 1.8
    base += violet[..., None] * np.array((92, 38, 140)) + blue[..., None] * np.array((30, 60, 140))
    ys, xs = np.mgrid[0:h, 0:w]
    if glow_at is not None:
        gx, gy = glow_at
        d = np.sqrt(((xs - gx) / w) ** 2 + ((ys - gy) / h) ** 2 * (h / w) ** 2 * 0 + ((ys - gy) / w) ** 2)
        g = np.exp(-(d / glow_r) ** 2)
        base += g[..., None] * np.array(glow_col) * 0.55
    # vignette
    v = np.sqrt(((xs - w / 2) / (w / 2)) ** 2 + ((ys - h / 2) / (h / 2)) ** 2)
    base *= np.clip(1.15 - 0.45 * v ** 2, 0.35, 1)[..., None]
    img = np.clip(base, 0, 255)
    rng = np.random.default_rng(seed + 99)
    for _ in range(int(w * h / 2600)):
        x, y = int(rng.integers(0, w)), int(rng.integers(0, h))
        b = rng.random() ** 3
        col = np.array((255, 255, 255)) * (0.35 + 0.65 * b)
        if rng.random() < 0.2:
            col = col * np.array((1.0, 0.85, 0.6))
        size = 1 if b < 0.85 else 2
        img[y:y + size, x:x + size] = np.maximum(img[y:y + size, x:x + size], col)
        if b > 0.96:  # a few sparkles with a cross
            for k in range(1, 5):
                fade = col * (1 - k / 5)
                for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)):
                    if 0 <= x + dx < w and 0 <= y + dy < h:
                        img[y + dy, x + dx] = np.maximum(img[y + dy, x + dx], fade)
    return img

# ------------------------------------------------------------------ boss renders


def stage3_geo(name):
    return gp.load_geo(bl.asset_paths(name)['geo'])  # all stage bones visible = stage 3


def render_boss(name, scale, yaw=0.0, pitch=-4.0, anim=None, time=0.0, stage_texture=True):
    """Returns (rgb, alpha, glow): the boss with all stage-3 parts, cut out, plus its bloom.
    stage_texture=False keeps the base colours (for bosses whose stage-3 glow would wash out)."""
    geo = stage3_geo(name)
    suffix = '_stage3' if stage_texture else ''
    tex = gp.load_rgba(os.path.join(TEX, f'{name}{suffix}.png'))
    glow = gp.load_rgba(os.path.join(TEX, f'{name}{suffix}_glowmask.png'))
    pose = None
    if anim:
        pose = gp.sample_anim(gp.load_anims(bl.asset_paths(name)['anim'])[anim], time)
    kw = dict(pose=pose, yaw=yaw, pitch=pitch, scale=scale, ground=False, light=True)
    # Render on a canvas with a wide margin, so the bloom fades out instead of ending at a hard edge.
    nat = gp.render(geo, tex, glow, bg=(0, 0, 0), bloom=False, **kw).size
    margin = 180
    kw['size'] = (nat[0] + 2 * margin, nat[1] + 2 * margin)
    black = np.asarray(gp.render(geo, tex, glow, bg=(0, 0, 0), bloom=False, **kw)).astype(float)
    white = np.asarray(gp.render(geo, tex, glow, bg=(255, 255, 255), bloom=False, **kw)).astype(float)
    bloom = np.asarray(gp.render(geo, tex, glow, bg=(0, 0, 0), bloom=True, **kw)).astype(float)
    # The renderer's background is a vertical gradient, so each row's background difference is its
    # largest difference (every row has empty margins).
    diff = (white - black).mean(axis=2)
    bgdiff = np.maximum(diff.max(axis=1, keepdims=True), 1.0)
    alpha = np.clip(1 - diff / bgdiff, 0, 1)
    alpha[alpha < 0.02] = 0
    rgb = np.where(alpha[..., None] > 1e-3, black / np.maximum(alpha[..., None], 1e-3), 0)
    glow_layer = np.clip(bloom - black, 0, 255)
    return np.clip(rgb, 0, 255), alpha, glow_layer, margin


def place(canvas, layer, cx, bottom):
    """Composites a rendered boss with the bottom centre of the model (not of its margin) at (cx, bottom)."""
    rgb, alpha, glow, margin = layer
    h, w = alpha.shape
    x0, y0 = int(cx - w / 2), int(bottom - h + margin)
    H, W = canvas.shape[:2]
    sx0, sy0 = max(0, -x0), max(0, -y0)
    dx0, dy0 = max(0, x0), max(0, y0)
    dx1, dy1 = min(W, x0 + w), min(H, y0 + h)
    if dx1 <= dx0 or dy1 <= dy0:
        return
    sl = (slice(sy0, sy0 + dy1 - dy0), slice(sx0, sx0 + dx1 - dx0))
    region = canvas[dy0:dy1, dx0:dx1]
    a = alpha[sl][..., None]
    g = glow[sl]
    region[:] = region * (1 - a) + rgb[sl] * a
    region[:] = 255 - (255 - region) * (1 - g / 255.0)  # screen the bloom on top

# ------------------------------------------------------------------ title font (original)


GLYPHS = {
    'C': [" ##### ", "##   ##", "##     ", "##     ", "##     ", "##     ", "##     ", "##   ##", " ##### "],
    'E': ["#######", "##     ", "##     ", "##     ", "###### ", "##     ", "##     ", "##     ", "#######"],
    'L': ["##     ", "##     ", "##     ", "##     ", "##     ", "##     ", "##     ", "##     ", "#######"],
    'S': [" ##### ", "##   ##", "##     ", " ###   ", "  #### ", "    ## ", "     ##", "##   ##", " ##### "],
    'T': ["#######", "  ###  ", "  ###  ", "  ###  ", "  ###  ", "  ###  ", "  ###  ", "  ###  ", "  ###  "],
    'I': [" ##### ", "  ###  ", "  ###  ", "  ###  ", "  ###  ", "  ###  ", "  ###  ", "  ###  ", " ##### "],
    'A': ["  ###  ", " ## ## ", "##   ##", "##   ##", "#######", "##   ##", "##   ##", "##   ##", "##   ##"],
    'N': ["##   ##", "###  ##", "#### ##", "## ####", "##  ###", "##   ##", "##   ##", "##   ##", "##   ##"],
    ' ': ["   "] * 9,
}
GOLD = [(255, 246, 200), (255, 228, 150), (242, 204, 110), (214, 170, 72), (170, 124, 44), (128, 88, 30)]


def title_layer(text, cell):
    """Gold pixel lettering with a dark outline and drop shadow. Returns an RGBA float array."""
    rows = 9
    cols = sum(len(GLYPHS[ch][0]) + 1 for ch in text) - 1
    mask = np.zeros((rows, cols), bool)
    x = 0
    for ch in text:
        g = GLYPHS[ch]
        for j, row in enumerate(g):
            for i, c in enumerate(row):
                if c == '#':
                    mask[j, x + i] = True
        x += len(g[0]) + 1
    big = np.kron(mask, np.ones((cell, cell), bool))
    pad = cell
    h, w = big.shape[0] + 2 * pad + cell, big.shape[1] + 2 * pad + cell
    out = np.zeros((h, w, 4))
    m = np.zeros((h, w), bool)
    m[pad:pad + big.shape[0], pad:pad + big.shape[1]] = big
    # drop shadow
    sh = np.zeros_like(m)
    off = max(2, cell // 2)
    sh[off:, off:] = m[:-off, :-off]
    # outline: dilate
    ol = m.copy()
    r = max(2, cell // 3)
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                ol |= np.roll(np.roll(m, dy, 0), dx, 1)
    shol = np.roll(np.roll(ol, off, 0), off, 1)
    out[shol] = (0, 0, 0, 150)
    out[ol] = (24, 14, 40, 255)
    # gold, shaded per glyph row with a bright top edge on every stroke
    ys = np.arange(h)[:, None].repeat(w, 1)
    rel = np.clip((ys - pad) / max(1, big.shape[0]), 0, 0.999)
    idx = (rel * len(GOLD)).astype(int)
    col = np.array(GOLD)[idx]
    top = m & ~np.roll(m, cell // 2, 0)
    out[m, :3] = col[m]
    out[m, 3] = 255
    out[top, :3] = np.minimum(255, col[top] * 1.1 + 20)
    return out


def paste_rgba(canvas, layer, cx, cy):
    h, w = layer.shape[:2]
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    region = canvas[y0:y0 + h, x0:x0 + w]
    a = layer[..., 3:4] / 255.0
    region[:] = region * (1 - a) + layer[..., :3] * a


def glow_behind(canvas, layer, cx, cy, color, radius):
    """A soft coloured glow around the lettering (on a padded mask, so it never ends in a hard edge)."""
    pad = radius * 3
    mask = np.pad((layer[..., 3] > 0).astype(np.uint8) * 255, pad)
    m = Image.fromarray(mask).filter(ImageFilter.GaussianBlur(radius))
    a = np.asarray(m).astype(float)[..., None] / 255.0 * 0.6
    h, w = mask.shape
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    H, W = canvas.shape[:2]
    cx0, cy0, cx1, cy1 = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    a = a[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]
    region = canvas[cy0:cy1, cx0:cx1]
    region[:] = 255 - (255 - region) * (1 - a * np.array(color) / 255.0)

# ------------------------------------------------------------------ outputs


def save(arr, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(path)
    print(path)


def logo():
    S = 1024
    canvas = nebula(S, S, 11, glow_at=(S / 2, S * 0.36), glow_r=0.33)
    seraph = render_boss('astral_seraph', scale=8.6, yaw=0, pitch=-3, stage_texture=False)
    place(canvas, seraph, S / 2, S * 0.70)
    t1, t2 = title_layer('CELESTIAL', 10), title_layer('ASCENT', 14)
    glow_behind(canvas, t1, S / 2, S * 0.78, (255, 200, 110), 14)
    glow_behind(canvas, t2, S / 2, S * 0.895, (255, 200, 110), 18)
    paste_rgba(canvas, t1, S / 2, S * 0.78)
    paste_rgba(canvas, t2, S / 2, S * 0.895)
    save(canvas, os.path.join(OUT, 'logo.png'))
    small = Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8)).resize((256, 256), Image.LANCZOS)
    small.save(os.path.join(ROOT, 'src', 'main', 'resources', 'celestialascent_logo.png'))
    print('mod list logo written')


def banner():
    W, H = 1920, 600
    canvas = nebula(W, H, 23, glow_at=(W / 2, H * 0.55), glow_r=0.28, glow_col=(200, 170, 255))
    lineup = [('void_sovereign', 3.9, 20, -330), ('ender_colossus', 3.2, 10, -650), ('astral_seraph', 4.4, 0, 0),
              ('sun_herald', 4.7, -10, 650), ('frost_titan', 3.5, -20, 330)]
    order = [1, 3, 0, 4, 2]  # back to front: outer bosses first, the seraph last
    for k in order:
        name, sc, yaw, dx = lineup[k]
        layer = render_boss(name, scale=sc, yaw=yaw, pitch=-4, stage_texture=name != 'astral_seraph')
        place(canvas, layer, W / 2 + dx, H - 14)
    t = title_layer('CELESTIAL ASCENT', 9)
    glow_behind(canvas, t, W / 2, 92, (255, 200, 110), 16)
    paste_rgba(canvas, t, W / 2, 92)
    save(canvas, os.path.join(OUT, 'banner.png'))


if __name__ == '__main__':
    logo()
    banner()
