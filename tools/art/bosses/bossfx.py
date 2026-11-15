"""Extra shading and preview helpers for the boss generators (used together with bosslib)."""
import math
import os

import numpy as np
from PIL import Image, ImageDraw

import geo_preview as gp
from bosslib import PREVIEW, hash3, ramp, seg_dist, unit, fbm, vnoise, worley, palette, hexcol

# ============================================================================ shading helpers

BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], dtype=float) / 16.0 - 0.47


def dither(ctx, amount=1.0):
    """Ordered-dither offset per texel in about [-0.5, 0.5] * amount."""
    return BAYER4[ctx.j % 4, ctx.i % 4] * amount


def dramp(pal, v, ctx, amt=0.9):
    """Quantised palette lookup with ordered dithering between neighbouring steps."""
    n = len(pal)
    return ramp(pal, np.asarray(v) + dither(ctx, amt / n))


def sramp(pal, v):
    """Smooth palette interpolation."""
    n = len(pal)
    x = np.clip(np.asarray(v, dtype=float), 0, 1) * (n - 1)
    i = np.clip(np.floor(x).astype(int), 0, n - 2)
    f = (x - i)[:, None]
    return pal[i] * (1 - f) + pal[i + 1] * f


def edge_dist(ctx):
    """Distance (texels) of each texel to the nearest border of its face."""
    return np.minimum(np.minimum(ctx.i, ctx.tw - 1 - ctx.i), np.minimum(ctx.j, ctx.th - 1 - ctx.j))


def bevel(ctx, width=2.5, hi=0.16, lo=0.16):
    """Soft bevel: lit top/left rims, shaded bottom/right rims (in texels)."""
    if getattr(ctx, "plane", False):
        return np.zeros(ctx.N)
    top = np.clip(1 - ctx.j / width, 0, 1)
    bot = np.clip(1 - (ctx.th - 1 - ctx.j) / width, 0, 1)
    lef = np.clip(1 - ctx.i / width, 0, 1)
    rig = np.clip(1 - (ctx.tw - 1 - ctx.i) / width, 0, 1)
    if ctx.face in ("up", "down"):
        return np.maximum.reduce([top, bot, lef, rig]) * hi * 0.7
    return top * hi + lef * hi * 0.35 - bot * lo - rig * lo * 0.45


def band(ctx, d0, d1):
    d = edge_dist(ctx)
    return (d >= d0) & (d < d1)


def border_coords(ctx):
    """(a, d): coordinate along the nearest border (texels, continuous around the face) and the
    distance into the face from that border."""
    i, j, tw, th = ctx.i, ctx.j, ctx.tw, ctx.th
    dl, dr, dt, db = i, tw - 1 - i, j, th - 1 - j
    d = np.minimum(np.minimum(dl, dr), np.minimum(dt, db))
    a = np.where(d == dt, i, np.where(d == dr, tw + j, np.where(d == db, tw + th + (tw - 1 - i), 2 * tw + th + (th - 1 - j))))
    return a.astype(float), d.astype(float)


def filigree(ctx, d0=2.0, width=5.0, period=14.0, line=0.75):
    """Gold scroll-work inside a border band: a wavy vine with curls at each crest, between two
    thin border lines. Returns (line_mask, curl_mask)."""
    a, d = border_coords(ctx)
    inband = (d >= d0) & (d < d0 + width)
    mid = d0 + width / 2
    amp = width * 0.3
    ph = a * 2 * math.pi / period
    wave = mid + amp * np.sin(ph)
    vine = np.abs(d - wave) < line
    k = np.round(a / period * 2 - 0.5)
    ca = (k + 0.5) * period / 2
    side = np.where(np.mod(k, 2) == 0, 1.0, -1.0)
    cd = mid - side * amp * 0.9
    r = np.sqrt((a - ca) ** 2 + (d - cd) ** 2)
    curl = (np.abs(r - width * 0.2) < line * 0.75) & inband
    edge = ((d >= d0 - 0.5) & (d < d0 + 0.5)) | ((d >= d0 + width - 0.5) & (d < d0 + width + 0.5))
    return (vine & inband) | edge, curl


RUNE_SEGS = [((0, 0), (1, 0)), ((1, 0), (2, 0)), ((0, 2), (1, 2)), ((1, 2), (2, 2)), ((0, 0), (0, 1)),
             ((0, 1), (0, 2)), ((2, 0), (2, 1)), ((2, 1), (2, 2)), ((1, 0), (1, 1)), ((1, 1), (1, 2)),
             ((0, 0), (1, 1)), ((2, 0), (1, 1)), ((0, 2), (1, 1)), ((2, 2), (1, 1)), ((0, 1), (1, 1)), ((1, 1), (2, 1))]


def runes(x, y, cell=6.0, seed=0, stroke=0.55, density=0.4, gap=0.2):
    """Rune glyph mask on a 2D grid (x, y in texels). Each cell holds a random glyph built from
    strokes on a 3x3 lattice. Returns (mask, per-cell hash)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    cx = np.floor(x / cell)
    cy = np.floor(y / cell)
    lx = (x / cell - cx - gap) / (1 - 2 * gap) * 2
    ly = (y / cell - cy - gap) / (1 - 2 * gap) * 2
    inside = (lx >= -0.2) & (lx <= 2.2) & (ly >= -0.2) & (ly <= 2.2)
    dmin = np.full(np.shape(x), 9.0)
    for k, ((ax, ay), (bx, by)) in enumerate(RUNE_SEGS):
        on = hash3(cx, cy, np.full(np.shape(x), k), seed) < density
        d = seg_dist(lx, ly, ax, ay, bx, by)
        dmin = np.where(on, np.minimum(dmin, d), dmin)
    sw = stroke * 2.0 / (cell * (1 - 2 * gap))
    return inside & (dmin < sw), hash3(cx, cy, cx * 0, seed + 99)


def stars(p, scale=1.4, density=0.025, seed=0):
    """Sparse star points in 3D (p in model units). Returns brightness 0..1 per point."""
    q = np.asarray(p, dtype=float) * scale
    i = np.floor(q)
    f = q - i
    h = hash3(i[:, 0], i[:, 1], i[:, 2], seed)
    on = h < density
    cx = hash3(i[:, 0], i[:, 1], i[:, 2], seed + 1) * 0.6 + 0.2
    cy = hash3(i[:, 0], i[:, 1], i[:, 2], seed + 2) * 0.6 + 0.2
    cz = hash3(i[:, 0], i[:, 1], i[:, 2], seed + 3) * 0.6 + 0.2
    d = np.sqrt((f[:, 0] - cx) ** 2 + (f[:, 1] - cy) ** 2 + (f[:, 2] - cz) ** 2)
    size = 0.16 + 0.28 * (h / max(density, 1e-6))
    return np.where(on, np.clip(1 - d / size, 0, 1), 0.0)


def mix(a, b, f):
    f = np.asarray(f, dtype=float)
    if f.ndim == 1:
        f = f[:, None]
    return a * (1 - f) + b * f


def col(hexstr, n):
    return np.broadcast_to(hexcol(hexstr), (n, 3)).astype(float)


def spec(ctx, power=6.0, ldir=(-0.35, 0.75, -0.55)):
    """Baked highlight term from the rest-pose world normal (0..1, constant per face)."""
    l = unit(np.array(ldir))
    h = unit(l + np.array([0, 0, -1.0]))
    return max(0.0, float(ctx.nw @ h)) ** power


def smoothstep(e0, e1, x):
    t = np.clip((np.asarray(x, dtype=float) - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def plane_xy(ctx):
    """Centred plane coordinates: x in [-1, 1] left->right, y in [-1, 1] bottom->top."""
    return (ctx.s - 0.5) * 2, (0.5 - ctx.t) * 2


def face_xy(ctx):
    """Face coordinates in model units from the face centre (x right, y up as seen on the texture)."""
    return (ctx.s - 0.5) * ctx.tw / 2.0, (0.5 - ctx.t) * ctx.th / 2.0


def cracks(p, freq=0.12, width=0.045, seed=0):
    """Worley-edge crack mask (bool) and the cell id."""
    f1, f2, cid = worley(p, freq, seed)
    return (f2 - f1) < width, cid, f2 - f1

# ============================================================================ previews


def _render_tiles(g, rgba, glow, pose, views, scale, W, H, cy, hitbox, label):
    tiles = []
    for vn, yaw, pitch in views:
        im = gp.render(g, rgba, glow, pose, yaw=yaw, pitch=pitch, scale=scale, size=(W, H), center=(0, cy),
                       hitbox=hitbox)
        ImageDraw.Draw(im).text((6, 4), f"{label} {vn}", fill=(230, 230, 240))
        tiles.append(im)
    return tiles


def _grid(tiles, cols, W, H, title=None):
    rows = (len(tiles) + cols - 1) // cols
    top = 16 if title else 0
    sheet = Image.new("RGB", (W * min(cols, len(tiles)), H * rows + top), (20, 20, 24))
    for k, im in enumerate(tiles):
        sheet.paste(im, ((k % cols) * W, (k // cols) * H + top))
    if title:
        ImageDraw.Draw(sheet).text((6, 2), title, fill=(255, 255, 255))
    return sheet


REST_VIEWS = [("front", 0, -6), ("3/4", 35, -12), ("side", 90, -6), ("back", 180, -8), ("3/4 back", 145, -12),
              ("low 3/4", -30, 14)]


def extent_over(g, anim, times):
    los, his = [], []
    for t in times:
        pose = gp.sample_anim(anim, t) if anim is not None else None
        lo, hi = gp.model_extent(g, pose)
        los.append(lo)
        his.append(hi)
    return np.min(los, axis=0), np.max(his, axis=0)


def preview_rest(name, geo, rgba, glow, hitbox, px_height=430, views=REST_VIEWS, tag="", cols=3):
    os.makedirs(PREVIEW, exist_ok=True)
    g = gp.load_geo(geo)
    lo, hi = gp.model_extent(g)
    lo = np.minimum(lo, [-hitbox[0] * 8, 0, -hitbox[0] * 8])
    hi = np.maximum(hi, [hitbox[0] * 8, hitbox[1] * 16, hitbox[0] * 8])
    span = max(hi[0] - lo[0], hi[2] - lo[2])
    fh = (hi[1] - lo[1]) + 16
    fw = span * 1.05 + 16
    scale = px_height / fh
    W, H = int(fw * scale), int(fh * scale)
    cy = (hi[1] + lo[1]) / 2
    tiles = _render_tiles(g, rgba, glow, None, views, scale, W, H, cy, hitbox, name)
    p = os.path.join(PREVIEW, f"{name}_rest{tag}.png")
    _grid(tiles, cols, W, H).save(p)
    return p


def preview_strip(name, geo, rgba, glow, anims, an, times, hitbox=None, yaw=35, pitch=-12, px_height=300, tag=""):
    os.makedirs(PREVIEW, exist_ok=True)
    g = gp.load_geo(geo)
    anim = anims["animations"][an]
    lo, hi = extent_over(g, anim, times)
    lo = np.minimum(lo, [-8, 0, -8])
    span = max(hi[0] - lo[0], hi[2] - lo[2])
    fh = (hi[1] - lo[1]) + 14
    fw = span * 0.95 + 14
    scale = px_height / fh
    W, H = int(fw * scale), int(fh * scale)
    cy = (hi[1] + lo[1]) / 2
    tiles = []
    for t in times:
        im = gp.render(g, rgba, glow, gp.sample_anim(anim, t), yaw=yaw, pitch=pitch, scale=scale, size=(W, H),
                       center=(0, cy), hitbox=hitbox)
        ImageDraw.Draw(im).text((6, 4), f"t={t:.2f}", fill=(230, 230, 240))
        tiles.append(im)
    p = os.path.join(PREVIEW, f"{name}_{an.replace('.', '_')}{tag}.png")
    _grid(tiles, len(tiles), W, H, title=f"{name} {an}").save(p)
    return p


def preview_pose(name, geo, rgba, glow, anims, an, t, views=None, px_height=430, tag=""):
    """One pose from several angles (the mid-attack hero shot)."""
    os.makedirs(PREVIEW, exist_ok=True)
    g = gp.load_geo(geo)
    pose = gp.sample_anim(anims["animations"][an], t)
    lo, hi = gp.model_extent(g, pose)
    lo = np.minimum(lo, [-8, 0, -8])
    span = max(hi[0] - lo[0], hi[2] - lo[2])
    fh = (hi[1] - lo[1]) + 16
    fw = span * 1.05 + 16
    scale = px_height / fh
    views = views or [("front", 0, -6), ("3/4", 35, -12), ("3/4 left", -40, -8)]
    W, H = int(fw * scale), int(fh * scale)
    cy = (hi[1] + lo[1]) / 2
    tiles = _render_tiles(g, rgba, glow, pose, views, scale, W, H, cy, None, "")
    p = os.path.join(PREVIEW, f"{name}_pose_{an.replace('.', '_')}{tag}.png")
    _grid(tiles, len(tiles), W, H, title=f"{name} {an} @ {t:.2f}s").save(p)
    return p


def inspect(name, geo, rgba, glow, yaw=25, pitch=-10, center=None, frame=40, px=700, pose=None, out=None):
    """Close-up render of a region (center = (x, y) in view units, frame = width in units)."""
    g = gp.load_geo(geo)
    scale = px / frame
    im = gp.render(g, rgba, glow, pose, yaw=yaw, pitch=pitch, scale=scale, size=(px, px), center=center)
    out = out or os.path.join(os.environ.get("TEMP", "."), f"{name}_inspect.png")
    im.save(out)
    return out
