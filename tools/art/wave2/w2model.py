"""Block-model authoring + preview renderer for wave 2.

Adapted from tools/art/blockmodel.py and tools/art/model_preview.py (copied, not
modified) with: mandatory six faces per element, element `light_emission` plus
NeoForge per-face `neoforge_data` for glowing parts, a translucent pass and
animated-strip support in the preview, and the 1.21.1 rotation-angle check.
"""
import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw

from w2common import ASSETS, PREVIEW, _font, write_json

DIRS = ('down', 'up', 'north', 'south', 'west', 'east')
ANGLES = (-45, -22.5, 0, 22.5, 45)


def auto_uv(d, f, t):
    x0, y0, z0 = f
    x1, y1, z1 = t
    return {
        'down': [x0, 16 - z1, x1, 16 - z0],
        'up': [x0, z0, x1, z1],
        'north': [16 - x1, 16 - y1, 16 - x0, 16 - y0],
        'south': [x0, 16 - y1, x1, 16 - y0],
        'west': [z0, 16 - y1, z1, 16 - y0],
        'east': [16 - z1, 16 - y1, 16 - z0, 16 - y0],
    }[d]


def _clean(v):
    v = round(v, 4)
    return int(v) if float(v).is_integer() else v


def el(f, t, faces, rotation=None, name=None, light=None, shade=None):
    """faces: {dir: '#tex' | ('#tex', uv) | ('#tex', uv, rot)}; 'all' fills the rest.
    Every one of the six faces must end up with a texture. Auto uvs wrap world
    coordinates into 0..16 for parts that stick out above the block."""
    spec = dict(faces)
    base = spec.pop('all', None)
    out_faces = {}
    for d in DIRS:
        s = spec.get(d, base)
        if s is None:
            raise ValueError(f'element {name}: face {d} has no texture')
        if isinstance(s, str):
            tex, uv, r = s, None, 0
        else:
            tex = s[0]
            uv = s[1] if len(s) > 1 else None
            r = s[2] if len(s) > 2 else 0
        if uv is None:
            uv = auto_uv(d, f, t)
            lo = min(uv)
            if lo < 0 or max(uv) > 16:
                # shift vertically/horizontally into range keeping size
                u0, v0, u1, v1 = uv
                du = -16 * math.floor(min(u0, u1) / 16)
                dv = -16 * math.floor(min(v0, v1) / 16)
                uv = [u0 + du, v0 + dv, u1 + du, v1 + dv]
                uv = [min(16, max(0, x)) for x in uv]
        face = {'uv': [_clean(u) for u in uv], 'texture': tex}
        if r:
            face['rotation'] = r
        if light:
            face['neoforge_data'] = {'block_light': light, 'sky_light': light}
        out_faces[d] = face
    e = {}
    if name:
        e['name'] = name
    e['from'] = [_clean(v) for v in f]
    e['to'] = [_clean(v) for v in t]
    if rotation:
        assert rotation['angle'] in ANGLES, rotation
        e['rotation'] = rotation
    if shade is not None:
        e['shade'] = shade
    if light:
        e['light_emission'] = light
    e['faces'] = out_faces
    return e


def rot(axis, angle, origin, rescale=False):
    r = {'angle': angle, 'axis': axis, 'origin': [_clean(v) for v in origin]}
    if rescale:
        r['rescale'] = True
    return r


def box(f, t, tex, name=None, light=None, rotation=None, uvs=None):
    """Element with one texture on every face (auto uvs), optional uv overrides."""
    faces = {'all': tex}
    if uvs:
        for d, uv in uvs.items():
            faces[d] = (tex, uv) if not isinstance(uv, tuple) else uv
    return el(f, t, faces, rotation=rotation, name=name, light=light)


def model(name, textures, elements, render_type=None, ao=None):
    m = {'parent': 'block/block'}
    if render_type:
        m['render_type'] = render_type
    if ao is not None:
        m['ambientocclusion'] = ao
    m['textures'] = dict(textures)
    m['elements'] = elements
    write_json(f'models/block/{name}.json', m)
    return m


def T(name):
    return f'celestialascent:block/{name}'


# ======================================================================
# preview renderer
# ======================================================================
SHADE = {'up': 1.0, 'down': 0.5, 'north': 0.8, 'south': 0.8, 'east': 0.6, 'west': 0.6}
NORMALS = {'up': (0, 1, 0), 'down': (0, -1, 0), 'north': (0, 0, -1), 'south': (0, 0, 1),
           'west': (-1, 0, 0), 'east': (1, 0, 0)}


def face_verts(f, t, d):
    x0, y0, z0 = f
    x1, y1, z1 = t
    return {
        'down': [(x0, y0, z1), (x0, y0, z0), (x1, y0, z0), (x1, y0, z1)],
        'up': [(x0, y1, z0), (x0, y1, z1), (x1, y1, z1), (x1, y1, z0)],
        'north': [(x1, y1, z0), (x1, y0, z0), (x0, y0, z0), (x0, y1, z0)],
        'south': [(x0, y1, z1), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1)],
        'west': [(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)],
        'east': [(x1, y1, z1), (x1, y0, z1), (x1, y0, z0), (x1, y1, z0)],
    }[d]


def uv_corners(uv, r):
    u1, v1, u2, v2 = uv
    corners = [(u1, v1), (u1, v2), (u2, v2), (u2, v1)]
    k = (r // 90) % 4
    return [corners[(i + k) % 4] for i in range(4)]


def rotate_point(p, r):
    if not r:
        return p
    ox, oy, oz = r.get('origin', [8, 8, 8])
    a = math.radians(r['angle'])
    c, s = math.cos(a), math.sin(a)
    x, y, z = p[0] - ox, p[1] - oy, p[2] - oz
    ax = r['axis']
    if ax == 'x':
        y, z = y * c - z * s, y * s + z * c
    elif ax == 'y':
        x, z = x * c + z * s, -x * s + z * c
    else:
        x, y = x * c - y * s, x * s + y * c
    if r.get('rescale'):
        k = 1.0 / math.cos(a) if abs(math.cos(a)) > 1e-6 else 1.0
        if ax == 'x':
            y, z = y * k, z * k
        elif ax == 'y':
            x, z = x * k, z * k
        else:
            x, y = x * k, y * k
    return (x + ox, y + oy, z + oz)


def rotate_vec(v, r):
    if not r:
        return v
    o = r.get('origin', [8, 8, 8])
    p = rotate_point((o[0] + v[0], o[1] + v[1], o[2] + v[2]), dict(r, rescale=False))
    return (p[0] - o[0], p[1] - o[1], p[2] - o[2])


def tex_file(ref, textures):
    depth = 0
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


_cache = {}


def load_tex(path, frame=0):
    key = (path, frame)
    if key not in _cache:
        if path is None or not os.path.exists(path):
            im = np.zeros((16, 16, 4), np.uint8)
            im[:, :] = (255, 0, 255, 255)
            im[::2, ::2] = (0, 0, 0, 255)
        else:
            im = np.array(Image.open(path).convert('RGBA'))
            w = im.shape[1]
            if im.shape[0] > w and im.shape[0] % w == 0:          # animated strip
                n = im.shape[0] // w
                k = frame % n
                im = im[k * w:(k + 1) * w]
        _cache[key] = im
    return _cache[key]


def view_basis(yaw_deg, pitch_deg):
    th, ph = math.radians(yaw_deg), math.radians(pitch_deg)
    d = (math.sin(th), 0.0, math.cos(th))
    right = np.array([-d[2], 0.0, d[0]])
    fwd = np.array([d[0] * math.cos(ph), -math.sin(ph), d[2] * math.cos(ph)])
    up = np.array([d[0] * math.sin(ph), math.cos(ph), d[2] * math.sin(ph)])
    return right, up, fwd


def render_model(m, yaw=45, pitch=30, S=12, center=(8, 10, 8), frame=0, size=None, crop=True):
    right, up, fwd = view_basis(yaw, pitch)
    W = H = size or int(S * 44)
    color = np.zeros((H, W, 4), np.float32)
    zbuf = np.full((H, W), np.inf, np.float32)
    textures = m.get('textures', {})
    c0 = np.array(center, float)

    def proj(p):
        q = np.array(p, float) - c0
        return (W / 2 + q.dot(right) * S, H / 2 - q.dot(up) * S, q.dot(fwd))

    for pass_ in ('opaque', 'translucent'):
        for e in m.get('elements', []):
            r = e.get('rotation')
            emissive = e.get('light_emission', 0) > 0
            for d, face in e.get('faces', {}).items():
                n = rotate_vec(NORMALS[d], r)
                if np.dot(n, fwd) >= -1e-6:
                    continue
                verts = [rotate_point(v, r) for v in face_verts(e['from'], e['to'], d)]
                uvs = uv_corners(face.get('uv', [0, 0, 16, 16]), face.get('rotation', 0))
                tex = load_tex(tex_file(face['texture'], textures), frame)
                th, tw = tex.shape[:2]
                P = [proj(v) for v in verts]
                sh = 1.0 if (emissive or 'neoforge_data' in face or e.get('shade') is False) else SHADE[d]
                for tri in ((0, 1, 2), (0, 2, 3)):
                    (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = [P[i] for i in tri]
                    (u0, v0), (u1, v1), (u2, v2) = [uvs[i] for i in tri]
                    minx = int(max(0, math.floor(min(x0, x1, x2))))
                    maxx = int(min(W - 1, math.ceil(max(x0, x1, x2))))
                    miny = int(max(0, math.floor(min(y0, y1, y2))))
                    maxy = int(min(H - 1, math.ceil(max(y0, y1, y2))))
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
                    texel = tex[ty, tx].astype(np.float32)
                    zb = zbuf[miny:maxy + 1, minx:maxx + 1]
                    cb = color[miny:maxy + 1, minx:maxx + 1]
                    al = texel[..., 3]
                    rgb = texel[..., :3] * sh
                    if pass_ == 'opaque':
                        ok = inside & (al >= 250) & (z < zb - 1e-4)
                        zb[ok] = z[ok]
                        cb[ok, :3] = rgb[ok]
                        cb[ok, 3] = 255
                    else:
                        ok = inside & (al > 0) & (al < 250) & (z < zb - 1e-4)
                        if not ok.any():
                            continue
                        t = (al / 255.0)[..., None]
                        old = cb[..., :3]
                        olda = cb[..., 3:4] / 255.0
                        new = rgb * t + old * (1 - t) * olda / np.maximum(1e-6, (t + olda * (1 - t)))
                        na = (t + olda * (1 - t)) * 255
                        cb[ok, :3] = new[ok]
                        cb[ok, 3] = na[ok, 0]
    img = Image.fromarray(np.clip(color, 0, 255).astype(np.uint8), 'RGBA')
    if crop:
        bb = img.getbbox()
        return img.crop(bb) if bb else img
    return img


def load_model(name):
    with open(os.path.join(ASSETS, 'models', 'block', name + '.json')) as f:
        return json.load(f)


VIEWS = [(45, 30), (-45, 30), (225, 30)]


def model_sheet(names, out_name, S=11, bg=(118, 118, 118), views=VIEWS, dark=False):
    rows = []
    for n in names:
        m = load_model(n)
        rows.append((n, [render_model(m, yw, pt, S) for yw, pt in views]))
    cell = max(max(i.width, i.height) for _, r in rows for i in r) + 16
    lab = 18
    out = Image.new('RGBA', (len(views) * cell + 20, len(rows) * (cell + lab) + 20), tuple(bg) + (255,))
    d = ImageDraw.Draw(out)
    f = _font(14)
    for j, (n, ims) in enumerate(rows):
        y = 10 + j * (cell + lab)
        d.text((14, y), n, fill=(15, 15, 15, 255) if not dark else (220, 220, 220, 255), font=f)
        for i, im in enumerate(ims):
            x = 10 + i * cell + (cell - im.width) // 2
            out.alpha_composite(im, (x, y + lab + (cell - im.height) // 2))
    path = os.path.join(PREVIEW, out_name)
    out.save(path)
    return path


def check_model(name):
    """Validate: parent, particle, textures exist, six faces each, ranges, angles."""
    m = load_model(name)
    errs = []
    if m.get('parent') != 'block/block':
        errs.append('parent')
    tex = m.get('textures', {})
    if 'particle' not in tex:
        errs.append('no particle')
    for k, v in tex.items():
        p = tex_file(v, tex)
        if not p or not os.path.exists(p):
            errs.append(f'texture {k} -> {v} missing')
    for i, e in enumerate(m['elements']):
        for v in e['from'] + e['to']:
            if not -16 <= v <= 32:
                errs.append(f'el {i} out of range')
        for a, b in zip(e['from'], e['to']):
            if a > b:
                errs.append(f'el {i} from>to')
        if 'rotation' in e and e['rotation']['angle'] not in ANGLES:
            errs.append(f'el {i} bad angle')
        if set(e['faces']) != set(DIRS):
            errs.append(f'el {i} ({e.get("name")}) faces {sorted(e["faces"])}')
        for d, fc in e['faces'].items():
            ref = fc['texture']
            if not ref.startswith('#') or ref[1:] not in tex:
                errs.append(f'el {i} face {d} texture {ref} undefined')
            for u in fc['uv']:
                if not 0 <= u <= 16:
                    errs.append(f'el {i} face {d} uv {fc["uv"]}')
    return errs
