"""Helpers for authoring JSON block models (north-facing)."""
from common import write_json

DIRS = ('down', 'up', 'north', 'south', 'west', 'east')


def auto_uv(d, f, t):
    """Vanilla's world-locked default uv for a face."""
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


def el(f, t, faces, rotation=None, name=None, shade=None):
    """faces: {dir: '#tex' | ('#tex', uv) | ('#tex', uv, rot) | dict}. 'all' key
    applies to every direction not given; '-dir' entries remove faces."""
    out_faces = {}
    spec = dict(faces)
    base = spec.pop('all', None)
    for d in DIRS:
        s = spec.get(d, base)
        if s is None or spec.get('-' + d):
            continue
        if isinstance(s, str):
            tex, uv, rot = s, None, 0
        elif isinstance(s, dict):
            out_faces[d] = s
            continue
        else:
            tex = s[0]
            uv = s[1] if len(s) > 1 else None
            rot = s[2] if len(s) > 2 else 0
        if uv is None:
            uv = auto_uv(d, f, t)
            uv = [min(16, max(0, u)) for u in uv]
        face = {'uv': [_clean(u) for u in uv], 'texture': tex}
        if rot:
            face['rotation'] = rot
        out_faces[d] = face
    e = {}
    if name:
        e['name'] = name
    e['from'] = [_clean(v) for v in f]
    e['to'] = [_clean(v) for v in t]
    if rotation:
        e['rotation'] = rotation
    if shade is not None:
        e['shade'] = shade
    e['faces'] = out_faces
    return e


def rot(axis, angle, origin, rescale=False):
    r = {'angle': angle, 'axis': axis, 'origin': [_clean(v) for v in origin]}
    if rescale:
        r['rescale'] = True
    return r


def emissive(face_dict):
    """Mark a face fully bright (NeoForge per-face extra data)."""
    face_dict = dict(face_dict)
    face_dict['neoforge_data'] = {'block_light': 15, 'sky_light': 15}
    return face_dict


def model(name, textures, elements, render_type=None, ao=None):
    m = {'parent': 'block/block'}
    if render_type:
        m['render_type'] = render_type
    if ao is not None:
        m['ambientocclusion'] = ao
    m['textures'] = {k: v for k, v in textures.items()}
    m['elements'] = elements
    write_json(f'models/block/{name}.json', m)
    return m


def T(name):
    return f'celestialascent:block/{name}'
