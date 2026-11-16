"""Evolution stage textures for every boss.

From textures/entity/<boss>.png and <boss>_glowmask.png this writes
  <boss>_stage2.png / <boss>_stage2_glowmask.png   "awakened": glowing veins in the boss's colour,
                                                      the existing glow spreads a little
  <boss>_stage3.png / <boss>_stage3_glowmask.png   "unleashed": dense veins, the body takes on
                                                      the colour, the glow spreads further

Veins come from ridged value noise, so they read as organic cracks on every face of the
model instead of random lines across UV seams. BossRenderer picks the texture by stage.
Run: python tools/art/bosses/gen_stages.py
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from common import ASSETS, PREVIEW, tile_noise  # noqa: E402

TEX = os.path.join(ASSETS, 'textures', 'entity')

# boss -> accent colour of its element
ACCENT = {
    'frost_titan': (127, 230, 245),
    'tide_titan': (92, 160, 255),
    'storm_titan': (255, 228, 92),
    'magma_titan': (255, 130, 40),
    'sentinel_construct': (199, 125, 255),
    'ender_colossus': (142, 107, 255),
    'astral_seraph': (255, 236, 170),
    'nebula_leviathan': (200, 110, 255),
    'sun_herald': (255, 190, 50),
    'void_sovereign': (150, 60, 255),
}

STAGES = {
    # share of the body covered by veins, glow growth (px), tint toward the accent, body darkening, halo alpha
    2: dict(cover=0.065, grow=2, tint=0.10, dark=0.12, halo=140),
    3: dict(cover=0.13, grow=3, tint=0.22, dark=0.32, halo=190),
}


def ridged(h, w, seed, scale):
    cells = max(4, int(w / scale))
    n = tile_noise(w, h, cells, seed, octaves=2, persistence=0.55)
    return 1 - np.abs(2 * n - 1)


def dilate(mask, steps):
    m = mask.copy()
    for _ in range(steps):
        g = m.copy()
        g[1:, :] |= m[:-1, :]
        g[:-1, :] |= m[1:, :]
        g[:, 1:] |= m[:, :-1]
        g[:, :-1] |= m[:, 1:]
        m = g
    return m


def stage(boss, n):
    base = np.array(Image.open(os.path.join(TEX, boss + '.png')).convert('RGBA')).astype(float)
    glow = np.array(Image.open(os.path.join(TEX, boss + '_glowmask.png')).convert('RGBA')).astype(float)
    h, w = base.shape[:2]
    acc = np.array(ACCENT[boss], float)
    cfg = STAGES[n]
    solid = base[:, :, 3] > 0
    glowing = glow[:, :, 3] > 0
    body = solid & ~glowing

    out = base.copy()
    out_glow = glow.copy()

    # 1. tint the body toward the element colour, keeping its shading
    lum = (base[:, :, :3] @ np.array([0.299, 0.587, 0.114]))[:, :, None] / 255.0
    tinted = base[:, :, :3] * (1 - cfg['tint']) + (acc * (0.35 + 0.65 * lum)) * cfg['tint']
    tinted = tinted * (1 - cfg['dark'])  # a darker body makes the glowing veins stand out
    out[:, :, :3] = np.where(body[:, :, None], tinted, base[:, :, :3])

    # 2. veins: two noise scales so big cracks branch into fine ones; the threshold is picked so a
    #    fixed share of the body is covered, which keeps the cracks thin on every texture size
    v = np.maximum(ridged(h, w, 1000 + n * 17 + len(boss), w / 16), ridged(h, w, 2000 + n * 31 + len(boss), w / 34) * 0.99)
    t = np.quantile(v[body], 1 - cfg['cover']) if body.any() else 1.0
    veins = (v >= t) & body
    tc = np.quantile(v[veins], 0.6) if veins.any() else 1.0
    core = (v >= tc) & veins
    hot = np.clip(acc * 0.6 + 255 * 0.4, 0, 255)
    out[veins, :3] = acc * 0.8
    out[core, :3] = hot
    out_glow[veins] = np.append(acc, 210)
    out_glow[core] = np.append(hot, 255)
    # dark rims beside the veins make them read as cracks
    rim = dilate(veins, 1) & body & ~veins
    out[rim, :3] = out[rim, :3] * 0.55

    # 3. the existing glow spreads: a soft halo around emissive parts
    halo = dilate(glowing, cfg['grow']) & solid & ~glowing & ~veins
    out_glow[halo] = np.append(acc, cfg['halo'])
    # brighten the original glow toward white-hot
    g = glowing
    out_glow[g, :3] = np.clip(glow[g, :3] * 0.8 + 255 * 0.2 * (n - 1), 0, 255)

    Image.fromarray(out.astype(np.uint8), 'RGBA').save(os.path.join(TEX, f'{boss}_stage{n}.png'))
    Image.fromarray(out_glow.astype(np.uint8), 'RGBA').save(os.path.join(TEX, f'{boss}_stage{n}_glowmask.png'))
    return out.astype(np.uint8), out_glow.astype(np.uint8)


def preview(boss, imgs):
    """Side by side: stage 1, 2, 3 with their glow added on top (as the game shows it)."""
    tiles = []
    for b, g in imgs:
        a = b.astype(float)
        ga = g[:, :, 3:4].astype(float) / 255
        a[:, :, :3] = np.clip(a[:, :, :3] * (1 - ga * 0.6) + g[:, :, :3] * ga, 0, 255)
        tiles.append(Image.fromarray(a.astype(np.uint8), 'RGBA'))
    w, h = tiles[0].size
    sheet = Image.new('RGBA', (w * 3 + 16, h), (40, 40, 48, 255))
    for i, t in enumerate(tiles):
        sheet.alpha_composite(t, (i * (w + 8), 0))
    os.makedirs(PREVIEW, exist_ok=True)
    sheet.save(os.path.join(PREVIEW, f'stages_{boss}.png'))


def main():
    for boss in ACCENT:
        b1 = np.array(Image.open(os.path.join(TEX, boss + '.png')).convert('RGBA'))
        g1 = np.array(Image.open(os.path.join(TEX, boss + '_glowmask.png')).convert('RGBA'))
        imgs = [(b1, g1), stage(boss, 2), stage(boss, 3)]
        preview(boss, imgs)
        print(boss, 'stages written')


if __name__ == '__main__':
    main()
