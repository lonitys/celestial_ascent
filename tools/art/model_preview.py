"""Tiny software renderer for Minecraft JSON block models (preview only).

Follows vanilla FaceBakery conventions: per-face vertex order, uv corner
assignment, face uv rotation, element rotation (with rescale), and the
vanilla directional shade (up 1.0, down 0.5, north/south 0.8, east/west 0.6).
Orthographic projection, z-buffer, alpha cutout.
"""
import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw

from common import ASSETS, PREVIEW, _font

SHADE = {'up': 1.0, 'down': 0.5, 'north': 0.8, 'south': 0.8, 'east': 0.6, 'west': 0.6}
NORMALS = {'up': (0, 1, 0), 'down': (0, -1, 0), 'north': (0, 0, -1), 'south': (0, 0, 1),
           'west': (-1, 0, 0), 'east': (1, 0, 0)}


def face_verts(f, t, d):
    x0, y0, z0 = f
    x1, y1, z1 = t
    return {
        'down':  [(x0, y0, z1), (x0, y0, z0), (x1, y0, z0), (x1, y0, z1)],
        'up':    [(x0, y1, z0), (x0, y1, z1), (x1, y1, z1), (x1, y1, z0)],
        'north': [(x1, y1, z0), (x1, y0, z0), (x0, y0, z0), (x0, y1, z0)],
        'south': [(x0, y1, z1), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1)],
        'west':  [(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)],
        'east':  [(x1, y1, z1), (x1, y0, z1), (x1, y0, z0), (x1, y1, z0)],
    }[d]


def uv_corners(uv, rot):
    u1, v1, u2, v2 = uv
    corners = [(u1, v1), (u1, v2), (u2, v2), (u2, v1)]
    k = (rot // 90) % 4
    return [corners[(i + k) % 4] for i in range(4)]


def rotate_point(p, rot):
    if not rot:
        return p
    ox, oy, oz = rot.get('origin', [8, 8, 8])
    a = math.radians(rot['angle'])
    c, s = math.cos(a), math.sin(a)
    x, y, z = p[0] - ox, p[1] - oy, p[2] - oz
    ax = rot['axis']
    if ax == 'x':
        y, z = y * c - z * s, y * s + z * c
    elif ax == 'y':
        x, z = x * c + z * s, -x * s + z * c
    else:
        x, y = x * c - y * s, x * s + y * c
    if rot.get('rescale'):
        k = 1.0 / math.cos(a) if abs(math.cos(a)) > 1e-6 else 1.0
        if ax == 'x':
            y, z = y * k, z * k
        elif ax == 'y':
            x, z = x * k, z * k
        else:
            x, y = x * k, y * k
    return (x + ox, y + oy, z + oz)


def rotate_vec(v, rot):
    if not rot:
        return v
    o = rot.get('origin', [8, 8, 8])
    p = rotate_point((o[0] + v[0], o[1] + v[1], o[2] + v[2]), dict(rot, rescale=False))
    return (p[0] - o[0], p[1] - o[1], p[2] - o[2])


def resolve_tex(ref, textures, depth=0):
    while ref.startswith('#') and depth < 10:
        ref = textures.get(ref[1:], ref)
        depth += 1
    if ':' in ref:
        ns, path = ref.split(':', 1)
    else:
        ns, path = 'minecraft', ref
    if ns == 'celestialascent':
        return os.path.join(ASSETS, 'textures', path + '.png')
    return None


_tex_cache = {}


def load_tex(path):
    if path not in _tex_cache:
        if path is None or not os.path.exists(path):
            im = np.zeros((16, 16, 4), np.uint8)
            im[:, :] = (255, 0, 255, 255)
            im[::2, ::2] = (0, 0, 0, 255)
        else:
            im = np.array(Image.open(path).convert('RGBA'))
        _tex_cache[path] = im
    return _tex_cache[path]


def view_basis(yaw_deg, pitch_deg):
    th, ph = math.radians(yaw_deg), math.radians(pitch_deg)
    d = (math.sin(th), 0.0, math.cos(th))
    right = np.array([-d[2], 0.0, d[0]])
    fwd = np.array([d[0] * math.cos(ph), -math.sin(ph), d[2] * math.cos(ph)])
    up = np.array([d[0] * math.sin(ph), math.cos(ph), d[2] * math.sin(ph)])
    return right, up, fwd


def render_model(model, yaw=45, pitch=30, S=12, size=None, center=(8, 10, 8)):
    """Return a PIL image of the model from the given view direction.
    yaw 45 looks toward +x+z (shows north+west), yaw -45 shows north+east,
    yaw 225 shows south+east."""
    right, up, fwd = view_basis(yaw, pitch)
    W = H = size or int(S * 40)
    color = np.zeros((H, W, 4), np.float32)
    zbuf = np.full((H, W), np.inf, np.float32)
    textures = model.get('textures', {})
    cxyz = np.array(center, float)

    def proj(p):
        q = np.array(p, float) - cxyz
        return (W / 2 + q.dot(right) * S, H / 2 - q.dot(up) * S, q.dot(fwd))

    for el in model.get('elements', []):
        rot = el.get('rotation')
        for d, face in el.get('faces', {}).items():
            n = rotate_vec(NORMALS[d], rot)
            if np.dot(n, fwd) >= -1e-6:
                continue
            verts = [rotate_point(v, rot) for v in face_verts(el['from'], el['to'], d)]
            uvs = uv_corners(face.get('uv', [0, 0, 16, 16]), face.get('rotation', 0))
            tex = load_tex(resolve_tex(face['texture'], textures))
            th, tw = tex.shape[:2]
            P = [proj(v) for v in verts]
            shade = SHADE[d]
            for tri in ((0, 1, 2), (0, 2, 3)):
                (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = [P[i] for i in tri]
                (u0, v0), (u1, v1), (u2, v2) = [uvs[i] for i in tri]
                minx, maxx = int(max(0, math.floor(min(x0, x1, x2)))), int(min(W - 1, math.ceil(max(x0, x1, x2))))
                miny, maxy = int(max(0, math.floor(min(y0, y1, y2)))), int(min(H - 1, math.ceil(max(y0, y1, y2))))
                if minx > maxx or miny > maxy:
                    continue
                den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
                if abs(den) < 1e-9:
                    continue
                ys, xs = np.mgrid[miny:maxy + 1, minx:maxx + 1]
                px, py = xs + 0.5, ys + 0.5
                a = ((y1 - y2) * (px - x2) + (x2 - x1) * (py - y2)) / den
                b = ((y2 - y0) * (px - x2) + (x0 - x2) * (py - y2)) / den
                c = 1 - a - b
                inside = (a >= -1e-4) & (b >= -1e-4) & (c >= -1e-4)
                if not inside.any():
                    continue
                z = a * z0 + b * z1 + c * z2
                u = a * u0 + b * u1 + c * u2
                v = a * v0 + b * v1 + c * v2
                tx = np.clip((u / 16.0 * tw).astype(int), 0, tw - 1)
                ty = np.clip((v / 16.0 * th).astype(int), 0, th - 1)
                # nudge so texel sampling at exact upper edges stays in range
                texel = tex[ty, tx].astype(np.float32)
                ok = inside & (texel[..., 3] > 0) & (z < zbuf[miny:maxy + 1, minx:maxx + 1] - 1e-4)
                if not ok.any():
                    continue
                zb = zbuf[miny:maxy + 1, minx:maxx + 1]
                cb = color[miny:maxy + 1, minx:maxx + 1]
                zb[ok] = z[ok]
                rgb = texel[..., :3] * shade
                cb[ok, :3] = rgb[ok]
                cb[ok, 3] = 255
    img = Image.fromarray(np.clip(color, 0, 255).astype(np.uint8), 'RGBA')
    bbox = img.getbbox()
    return img.crop(bbox) if bbox else img


def load_model(name):
    with open(os.path.join(ASSETS, 'models', 'block', name + '.json')) as f:
        return json.load(f)


def model_sheet(names, out_name, S=12, bg=(118, 118, 118)):
    """For each model render three views (NW, NE, SE) in a row."""
    views = [(45, 30, 'front-left (N+W)'), (-45, 30, 'front-right (N+E)'), (225, 30, 'back (S+E)')]
    rows = []
    for n in names:
        m = load_model(n)
        rows.append((n, [render_model(m, yaw, pitch, S) for yaw, pitch, _ in views]))
    cell = max(max(i.width, i.height) for _, r in rows for i in r) + 20
    lab = 20
    sheet = Image.new('RGBA', (len(views) * cell + 20, len(rows) * (cell + lab) + 20), bg + (255,))
    d = ImageDraw.Draw(sheet)
    f = _font(14)
    for j, (n, ims) in enumerate(rows):
        y = 10 + j * (cell + lab)
        d.text((14, y), n, fill=(15, 15, 15, 255), font=f)
        for i, im in enumerate(ims):
            x = 10 + i * cell + (cell - im.width) // 2
            sheet.alpha_composite(im, (x, y + lab + (cell - im.height) // 2))
    path = os.path.join(PREVIEW, out_name)
    sheet.save(path)
    return path
