"""Shared toolkit for the Celestial Ascent boss generators (extended copy of tools/art/titans/titanlib.py).

Additions over the titan toolkit:
  * per-face-UV cubes and zero-thickness "planes" (only the north face is mapped; GeckoLib renders
    entities no-cull, so a single quad is visible from both sides) for cutout feathers, capes, halos;
  * item-based skyline packer up to 1024x1024 model px;
  * extra shading helpers (smooth dithered ramps, bevels, filigree, runes, stars, nebula);
  * animation bake refuses head rotation x/y (GeckoLib's turnsHead overwrites them).


* Model / Bone / Cube builder in Bedrock coordinates (16 units = 1 block, y up,
  front = -Z, model right side = -X) with helpers for oriented boxes, spikes and crystals.
* Skyline UV packer for box UV (integer cube sizes; GeckoLib floors box-UV sizes).
* Procedural painter: every texel of every face is mapped back to its 3D point, so
  materials are evaluated in 3D (continuous across faces) at 2x texel density.
  Includes baked ambient occlusion from the other cubes.
* Animation clips built from eased key tracks and procedural functions, baked to dense
  linear keyframes and simplified.
"""
import json
import math
import os
from collections import OrderedDict, defaultdict

import numpy as np
from PIL import Image

import geo_preview as gp

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ASSETS = os.path.join(ROOT, "src", "main", "resources", "assets", "celestialascent")
PREVIEW = os.path.join(HERE, "preview")
TEX_SCALE = 2  # HD: texels per model pixel

# ============================================================================ vectors / rotation


def v3(*a):
    if len(a) == 1:
        return np.array(a[0], dtype=float)
    return np.array(a, dtype=float)


def unit(v):
    v = np.asarray(v, dtype=float)
    n = np.linalg.norm(v)
    return v / n if n > 1e-12 else v


def axis_angle(axis, deg):
    a = unit(axis)
    th = math.radians(deg)
    c, s = math.cos(th), math.sin(th)
    x, y, z = a
    C = 1 - c
    return np.array([
        [c + x * x * C, x * y * C - z * s, x * z * C + y * s],
        [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
        [z * x * C - y * s, z * y * C + x * s, c + z * z * C]])


def align_y(d):
    """Rotation matrix taking +Y onto direction d."""
    d = unit(d)
    y = np.array([0.0, 1.0, 0.0])
    c = float(np.dot(y, d))
    if c > 0.999999:
        return np.eye(3)
    if c < -0.999999:
        return axis_angle([1, 0, 0], 180)
    ax = np.cross(y, d)
    return axis_angle(ax, math.degrees(math.acos(c)))


def orient(d, spin=0.0):
    """+Y -> d, with a spin about the local Y axis applied first."""
    return align_y(d) @ axis_angle([0, 1, 0], spin)


def euler(R):
    return [round(x, 4) for x in gp.euler_from_matrix(R)]


def mirror_euler(e):
    return [e[0], -e[1], -e[2]]

# ============================================================================ model


FACE_DIMS = {"north": (0, 1), "south": (0, 1), "east": (2, 1), "west": (2, 1), "up": (0, 2), "down": (0, 2)}


class Cube:
    def __init__(self, bone, origin, size, mat, inflate=0.0, pivot=None, rotation=None, params=None, faces=None):
        size = [int(round(s)) for s in size]
        if faces:
            assert all(s >= 0 for s in size) and sum(s > 0 for s in size) >= 2, (bone.name, size)
        else:
            assert all(s >= 1 for s in size), (bone.name, size)
        self.faces = list(faces) if faces else None   # per-face uv: list of mapped faces
        self.face_uv = {}
        self.bone = bone
        self.origin = [float(x) for x in origin]
        self.size = size
        self.mat = mat
        self.inflate = float(inflate)
        self.pivot = [float(x) for x in pivot] if pivot is not None else None
        self.rotation = [float(x) for x in rotation] if rotation is not None else None
        self.params = params or {}
        self.uv = None

    def footprint(self):
        w, h, d = self.size
        return 2 * (d + w), d + h

    def face_rect_size(self, face):
        a, b = FACE_DIMS[face]
        return max(1, int(math.ceil(self.size[a]))), max(1, int(math.ceil(self.size[b])))

    def pack_items(self):
        """[(key, w, h)] rectangles this cube needs in the atlas."""
        if self.faces:
            return [(f, *self.face_rect_size(f)) for f in self.faces]
        return [("box", *self.footprint())]

    def uv_rects(self):
        """{face: (u, v, w, h)} in model px (same convention as geo_preview.face_uv_rects)."""
        if self.faces:
            out = {}
            for f in self.faces:
                (u, v), (w, h) = self.face_uv[f]
                out[f] = (u, v, w, h)
            return out
        return gp.box_uv_rects(self.uv, self.size)

    def to_json(self):
        c = OrderedDict()
        c["origin"] = [round(x, 4) for x in self.origin]
        c["size"] = list(self.size)
        if self.inflate:
            c["inflate"] = round(self.inflate, 4)
        if self.rotation and any(abs(r) > 1e-6 for r in self.rotation):
            c["pivot"] = [round(x, 4) for x in (self.pivot or self.center())]
            c["rotation"] = [round(x, 4) for x in self.rotation]
        if self.faces:
            c["uv"] = OrderedDict((f, OrderedDict([("uv", list(self.face_uv[f][0])), ("uv_size", list(self.face_uv[f][1]))]))
                                  for f in self.faces)
        else:
            c["uv"] = list(self.uv)
        return c

    def center(self):
        return [o + s / 2 for o, s in zip(self.origin, self.size)]


class Bone:
    def __init__(self, model, name, parent, pivot, rotation=None):
        self.model = model
        self.name = name
        self.parent = parent
        self.pivot = [float(x) for x in pivot]
        self.rotation = [float(x) for x in rotation] if rotation else None
        self.cubes = []

    # raw cube
    def cube(self, origin, size, mat, inflate=0.0, pivot=None, rotation=None, faces=None, **params):
        c = Cube(self, origin, size, mat, inflate, pivot, rotation, params, faces=faces)
        self.cubes.append(c)
        return c

    def plane(self, center, w, h, mat, rot=None, pivot=None, **params):
        """Zero-thickness double-sided plane (XY plane before rotation, facing -Z), centred at
        center. rot = euler list or 3x3 matrix about pivot (default: centre). Only the north face
        is mapped; texel (s,t) runs min X -> max X and top -> bottom."""
        c = np.asarray(center, dtype=float)
        w, h = int(round(w)), int(round(h))
        origin = c - np.array([w / 2, h / 2, 0.0])
        rotation = None
        if rot is not None:
            rotation = euler(rot) if isinstance(rot, np.ndarray) and rot.shape == (3, 3) else list(rot)
        return self.cube(origin, (w, h, 0), mat, 0.0, pivot if pivot is not None else (c if rotation else None),
                         rotation, faces=["north"], **params)

    def plane_from(self, anchor, w, h, mat, rot=None, anchor_st=(0.5, 0.0), **params):
        """Plane pivoting at an anchor given in face coords (s across, t down):
        anchor_st=(0.5, 0) hangs the plane from the middle of its top edge."""
        a = np.asarray(anchor, dtype=float)
        w, h = int(round(w)), int(round(h))
        s, t = anchor_st
        origin = a - np.array([s * w, (1 - t) * h, 0.0])
        rotation = None
        if rot is not None:
            rotation = euler(rot) if isinstance(rot, np.ndarray) and rot.shape == (3, 3) else list(rot)
        return self.cube(origin, (w, h, 0), mat, 0.0, a if rotation else None, rotation, faces=["north"], **params)

    def box(self, center, size, mat, rot=None, pivot=None, inflate=0.0, **params):
        """Box by centre. rot = euler list or 3x3 matrix; rotates about pivot (default centre)."""
        c = np.asarray(center, dtype=float)
        s = np.asarray([int(round(x)) for x in size], dtype=float)
        origin = c - s / 2
        rotation = None
        if rot is not None:
            rotation = euler(rot) if isinstance(rot, np.ndarray) and rot.shape == (3, 3) else list(rot)
        return self.cube(origin, s, mat, inflate, pivot if pivot is not None else (c if rotation else None),
                         rotation, **params)

    def boxb(self, cx, y0, cz, sx, sy, sz, mat, **kw):
        """Box with x/z centre and bottom at y0."""
        return self.box((cx, y0 + int(round(sy)) / 2, cz), (sx, sy, sz), mat, **kw)

    def spike(self, base, direction, length, width, mat, segs=None, taper=0.58, spin=45.0,
              inflate=0.0, overlap=0.6, min_w=1, **params):
        """Tapered crystal/spike: stacked boxes along +Y, rotated so +Y points along direction,
        all pivoting at base. Returns the cubes."""
        base = np.asarray(base, dtype=float)
        R = orient(direction, spin)
        e = euler(R)
        if segs is None:
            segs = [0.46, 0.32, 0.22] if length >= 9 else [0.6, 0.4]
        lens = [max(1, int(round(length * f))) for f in segs]
        out = []
        y = 0.0
        w = float(width)
        n = len(lens)
        for k, L in enumerate(lens):
            wi = max(min_w, int(round(w)))
            origin = base + np.array([-wi / 2, y, -wi / 2])
            p = dict(params)
            p.update(seg=k, nseg=n, spike_len=length, spike_y0=y, spike_base=base.tolist())
            out.append(self.cube(origin, (wi, L, wi), mat, inflate, base, e, **p))
            y += L - overlap
            w = w * taper
        return out


    def curve_spike(self, base, dirs, lengths, widths, mat, spin=45.0, inflate=0.0, overlap=0.7, **params):
        """Curved horn/flame: one box per segment, each along its own direction, chained tip to base."""
        p0 = np.asarray(base, dtype=float)
        total = float(sum(lengths))
        acc = 0.0
        out = []
        n = len(lengths)
        for k, (d, L, w) in enumerate(zip(dirs, lengths, widths)):
            d = unit(d)
            R = orient(d, spin)
            e = euler(R)
            wi = max(1, int(round(w)))
            origin = p0 + np.array([-wi / 2, 0, -wi / 2])
            p = dict(params)
            p.update(seg=k, nseg=n, spike_len=L, spike_y0=0.0, spike_base=p0.tolist(),
                     curve_prog0=acc / total, curve_prog1=(acc + L) / total)
            out.append(self.cube(origin, (wi, int(L), wi), mat, inflate, p0, e, **p))
            p0 = p0 + d * (L - overlap)
            acc += L
        return out


class Model:
    def __init__(self, name):
        self.name = name
        self.bones = OrderedDict()
        self.tw = self.th = None
        self.bone("root", None, (0, 0, 0))

    def bone(self, name, parent="root", pivot=(0, 0, 0), rotation=None):
        assert name not in self.bones, name
        b = Bone(self, name, parent, pivot, rotation)
        self.bones[name] = b
        return b

    def __getitem__(self, k):
        return self.bones[k]

    def cubes(self):
        for b in self.bones.values():
            for c in b.cubes:
                yield c

    # -------------------------------------------------------------- uv packing
    def pack(self, sizes=((128, 128), (256, 128), (256, 256), (512, 256), (512, 512), (1024, 512), (1024, 1024))):
        from numpy.lib.stride_tricks import sliding_window_view
        items = []
        for c in self.cubes():
            for key, w, h in c.pack_items():
                items.append((c, key, w, h))
        order = sorted(items, key=lambda it: (it[3], it[2]), reverse=True)
        for (W, H) in sizes:
            sky = np.zeros(W, dtype=int)
            ok = True
            place = []
            for (c, key, fw, fh) in order:
                if fw > W:
                    ok = False
                    break
                win = sliding_window_view(sky, fw).max(axis=1)
                x = int(np.argmin(win))
                y = int(win[x])
                if y + fh > H:
                    ok = False
                    break
                place.append((c, key, x, y, fw, fh))
                sky[x:x + fw] = y + fh
            if ok:
                for (c, key, x, y, fw, fh) in place:
                    if key == "box":
                        c.uv = (x, y)
                    else:
                        c.face_uv[key] = ((x, y), (fw, fh))
                self.tw, self.th = W, H
                return W, H
        raise RuntimeError("UV packing failed: too much surface")

    # -------------------------------------------------------------- export
    def to_json(self, visible=(5, 6, 2.5)):
        bones = []
        for b in self.bones.values():
            d = OrderedDict()
            d["name"] = b.name
            if b.parent:
                d["parent"] = b.parent
            d["pivot"] = [round(x, 4) for x in b.pivot]
            if b.rotation and any(abs(r) > 1e-6 for r in b.rotation):
                d["rotation"] = [round(x, 4) for x in b.rotation]
            if b.cubes:
                d["cubes"] = [c.to_json() for c in b.cubes]
            bones.append(d)
        return OrderedDict([
            ("format_version", "1.12.0"),
            ("minecraft:geometry", [OrderedDict([
                ("description", OrderedDict([
                    ("identifier", f"geometry.{self.name}"),
                    ("texture_width", self.tw),
                    ("texture_height", self.th),
                    ("visible_bounds_width", visible[0]),
                    ("visible_bounds_height", visible[1]),
                    ("visible_bounds_offset", [0, visible[2], 0]),
                ])),
                ("bones", bones),
            ])]),
        ])

    def shift_bones(self, names, dv):
        """Translate bones (pivots, cubes, cube pivots) by dv in model space."""
        dv = np.asarray(dv, dtype=float)
        for n in names:
            b = self.bones[n]
            b.pivot = list(np.asarray(b.pivot) + dv)
            for c in b.cubes:
                c.origin = list(np.asarray(c.origin) + dv)
                if c.pivot is not None:
                    c.pivot = list(np.asarray(c.pivot) + dv)
                if "spike_base" in c.params:
                    c.params["spike_base"] = list(np.asarray(c.params["spike_base"]) + dv)

    def cube_count(self):
        return sum(len(b.cubes) for b in self.bones.values())

# ============================================================================ noise


def _u32(a):
    return (np.asarray(a).astype(np.int64) & 0xFFFFFFFF).astype(np.uint32)


def hash3(ix, iy, iz, seed=0):
    with np.errstate(over="ignore"):
        return _hash3(np.atleast_1d(ix), np.atleast_1d(iy), np.atleast_1d(iz), seed)


def _hash3(ix, iy, iz, seed=0):
    h = _u32(ix) * np.uint32(0x8DA6B343) ^ _u32(iy) * np.uint32(0xD8163841) ^ _u32(iz) * np.uint32(0xCB1AB31F)
    h = h ^ np.uint32((seed * 0x9E3779B1) & 0xFFFFFFFF)
    h ^= h >> np.uint32(15)
    h = h * np.uint32(0x2C1B3C6D)
    h ^= h >> np.uint32(12)
    h = h * np.uint32(0x297A2D39)
    h ^= h >> np.uint32(15)
    return (h & np.uint32(0xFFFFFF)).astype(np.float64) / float(0x1000000)


def vnoise(p, freq=1.0, seed=0):
    """3D value noise in [0,1]. p: (N,3)."""
    q = np.asarray(p, dtype=float) * freq
    i = np.floor(q).astype(np.int64)
    f = q - i
    u = f * f * (3 - 2 * f)
    out = 0.0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (u[:, 0] if dx else 1 - u[:, 0]) * (u[:, 1] if dy else 1 - u[:, 1]) * (u[:, 2] if dz else 1 - u[:, 2])
                out = out + w * hash3(i[:, 0] + dx, i[:, 1] + dy, i[:, 2] + dz, seed)
    return out


def fbm(p, freq=1.0, octaves=4, seed=0, gain=0.5):
    tot = 0.0
    amp = 1.0
    norm = 0.0
    for o in range(octaves):
        tot = tot + amp * vnoise(p, freq * (2 ** o), seed + 101 * o)
        norm += amp
        amp *= gain
    return tot / norm


def worley(p, freq=1.0, seed=0, jitter=0.9):
    """Returns F1, F2 (distances in cell units) and the id hash of the nearest cell."""
    q = np.asarray(p, dtype=float) * freq
    i = np.floor(q).astype(np.int64)
    f1 = np.full(len(q), 9.0)
    f2 = np.full(len(q), 9.0)
    cid = np.zeros(len(q))
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                cx, cy, cz = i[:, 0] + dx, i[:, 1] + dy, i[:, 2] + dz
                fx = cx + 0.5 + (hash3(cx, cy, cz, seed) - 0.5) * jitter
                fy = cy + 0.5 + (hash3(cx, cy, cz, seed + 7) - 0.5) * jitter
                fz = cz + 0.5 + (hash3(cx, cy, cz, seed + 13) - 0.5) * jitter
                d = np.sqrt((q[:, 0] - fx) ** 2 + (q[:, 1] - fy) ** 2 + (q[:, 2] - fz) ** 2)
                closer = d < f1
                f2 = np.where(closer, f1, np.minimum(f2, d))
                cid = np.where(closer, hash3(cx, cy, cz, seed + 31), cid)
                f1 = np.where(closer, d, f1)
    return f1, f2, cid


def hexcol(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=float)


def palette(*hexes):
    return np.array([hexcol(h) for h in hexes])


def ramp(pal, v):
    """Quantised palette lookup: v in [0,1] -> pal entries (dark to light)."""
    n = len(pal)
    idx = np.clip(np.floor(np.asarray(v) * n), 0, n - 1).astype(int)
    return pal[idx]


def ramp_smooth(pal, v):
    n = len(pal)
    x = np.clip(np.asarray(v), 0, 1) * (n - 1)
    i = np.clip(np.floor(x).astype(int), 0, n - 2)
    f = (x - i)[:, None]
    return pal[i] * (1 - f) + pal[i + 1] * f


def seg_dist(px, py, ax, ay, bx, by):
    """Distance from points to 2D segment."""
    vx, vy = bx - ax, by - ay
    wx, wy = px - ax, py - ay
    L = vx * vx + vy * vy
    t = np.clip((wx * vx + wy * vy) / L if L > 0 else 0, 0, 1)
    dx, dy = wx - t * vx, wy - t * vy
    return np.sqrt(dx * dx + dy * dy)


def polyline_dist(px, py, pts):
    d = np.full(np.shape(px), 1e9)
    for (a, b) in zip(pts, pts[1:]):
        d = np.minimum(d, seg_dist(px, py, a[0], a[1], b[0], b[1]))
    return d

# ============================================================================ painter


class Ctx:
    """Per-face shading context (arrays are per texel)."""
    pass


FACE_TANGENTS = {
    "north": ((1, 0, 0), (0, 1, 0)), "south": ((1, 0, 0), (0, 1, 0)),
    "west": ((0, 0, 1), (0, 1, 0)), "east": ((0, 0, 1), (0, 1, 0)),
    "up": ((1, 0, 0), (0, 0, 1)), "down": ((1, 0, 0), (0, 0, 1)),
}


class Painter:
    def __init__(self, model, shaders, ao_strength=1.0, ao_dist=(0.7, 1.8, 3.6)):
        self.model = model
        self.shaders = shaders
        self.ao_strength = ao_strength
        self.ao_dist = ao_dist

    def paint(self):
        m = self.model
        geo = gp.load_geo(m.to_json())
        mats = gp.bone_matrices(geo)
        S = TEX_SCALE
        W, H = m.tw * S, m.th * S
        rgba = np.zeros((H, W, 4), dtype=np.uint8)
        glow = np.zeros((H, W, 4), dtype=np.uint8)
        cubes = list(m.cubes())
        # world boxes for AO
        boxes = []
        for c in cubes:
            cj = c.to_json()
            cm = gp.cube_matrix(mats[c.bone.name], cj)
            lo = np.array(c.origin) - c.inflate
            hi = np.array(c.origin) + np.array(c.size) + c.inflate
            inv = np.linalg.inv(cm)
            corners = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
            wc = (cm @ np.c_[corners, np.ones(8)].T).T[:, :3]
            boxes.append((c, cm, inv, lo, hi, wc.min(0), wc.max(0)))
        for ci, (c, cm, inv, lo, hi, _, _) in enumerate(boxes):
            shader = self.shaders[c.mat]
            ext = hi - lo
            rects = c.uv_rects()
            for face, (fn, nrm) in gp.FACES.items():
                if face not in rects:
                    continue
                u, v, w, h = rects[face]
                if w <= 0 or h <= 0:
                    continue
                tw, th = int(w * S), int(h * S)
                I, J = np.meshgrid(np.arange(tw), np.arange(th))
                I = I.ravel()
                J = J.ravel()
                s = (I + 0.5) / tw
                t = (J + 0.5) / th
                fx, fy, fz = fn(s, t)
                pl = lo[None, :] + ext[None, :] * np.stack([fx, fy, fz], axis=1)
                pw = (cm @ np.c_[pl, np.ones(len(pl))].T).T[:, :3]
                nl = np.array(nrm, dtype=float)
                nw = unit(cm[:3, :3] @ nl)
                ctx = Ctx()
                ctx.cube, ctx.face, ctx.index = c, face, ci
                ctx.p, ctx.pw, ctx.n, ctx.nw = pl, pw, nl, nw
                ctx.s, ctx.t, ctx.i, ctx.j, ctx.tw, ctx.th = s, t, I, J, tw, th
                ctx.lo, ctx.hi = lo, hi
                ctx.bone = c.bone.name
                ctx.plane = bool(c.faces) and min(c.size) == 0
                ctx.params = c.params
                ctx.N = len(pl)
                ctx.ao, ctx.buried = self._ao(pw, nw, cm, face, ci, boxes)
                rgb, alpha, gl = shader(ctx)
                rgb = np.clip(np.asarray(rgb, dtype=float), 0, 255)
                alpha = np.broadcast_to(np.asarray(alpha), (ctx.N,))
                gl = np.broadcast_to(np.asarray(gl, dtype=bool), (ctx.N,))
                ys = int(v * S) + J
                xs = int(u * S) + I
                rgba[ys, xs, :3] = rgb.astype(np.uint8)
                rgba[ys, xs, 3] = alpha.astype(np.uint8)
                gsel = gl & (alpha > 0)
                if gsel.any():
                    g = np.clip(rgb[gsel] * 1.08 + 8, 0, 255)
                    glow[ys[gsel], xs[gsel], :3] = g.astype(np.uint8)
                    glow[ys[gsel], xs[gsel], 3] = 255
        return rgba, glow

    def _ao(self, pw, nw, cm, face, ci, boxes):
        N = len(pw)
        if self.ao_strength <= 0:
            return np.zeros(N), np.zeros(N, dtype=bool)
        tu, tv = FACE_TANGENTS[face]
        tu = unit(cm[:3, :3] @ np.array(tu, dtype=float))
        tv = unit(cm[:3, :3] @ np.array(tv, dtype=float))
        dirs = [nw, unit(nw + 0.7 * tu), unit(nw - 0.7 * tu), unit(nw + 0.7 * tv), unit(nw - 0.7 * tv)]
        samples = []
        for d in self.ao_dist:
            for k, dr in enumerate(dirs):
                if d == self.ao_dist[-1] and k > 0:
                    continue
                samples.append(dr * d)
        pmin = pw.min(0) - max(self.ao_dist) - 0.1
        pmax = pw.max(0) + max(self.ao_dist) + 0.1
        occ = np.zeros(N)
        buried = np.zeros(N, dtype=bool)
        probe = pw + nw * 0.08
        for bj, (c2, cm2, inv2, lo2, hi2, bmin, bmax) in enumerate(boxes):
            if bj == ci or (c2.faces and min(c2.size) == 0) or c2.params.get("no_ao"):
                continue
            if np.any(bmax < pmin) or np.any(bmin > pmax):
                continue
            A = inv2[:3, :3]
            b = inv2[:3, 3]
            q = probe @ A.T + b
            buried |= np.all((q > lo2 + 0.02) & (q < hi2 - 0.02), axis=1)
            for off in samples:
                q = (pw + off) @ A.T + b
                inside = np.all((q > lo2) & (q < hi2), axis=1)
                occ += inside
        occ = np.minimum(occ / len(samples), 1.0)
        return occ * self.ao_strength, buried


# --------------------------------------------------------------------------- shading helpers

def edge_term(ctx, light=0.10, dark=0.12, side=0.05, width=1):
    """Bevel: lighter top edge, darker bottom edge and slightly darker sides (in texels)."""
    e = np.zeros(ctx.N)
    top = ctx.j < width
    bot = ctx.j >= ctx.th - width
    lef = ctx.i < width
    rig = ctx.i >= ctx.tw - width
    if ctx.face in ("up", "down"):
        e += np.where(top | bot | lef | rig, light * 0.6, 0)
    else:
        e += np.where(top, light, 0)
        e -= np.where(bot, dark, 0)
        e -= np.where((lef | rig) & ~top, side, 0)
    return e


def face_light(ctx, up=0.06, down=-0.10):
    """Small constant per-face variation so faces read in pixel art style."""
    n = ctx.nw
    return up * max(0.0, n[1]) + (-down) * min(0.0, n[1])


def vgrad(ctx, amount=0.12):
    """Darker towards the bottom of side faces (t=1)."""
    if ctx.face in ("up", "down"):
        return np.zeros(ctx.N)
    return (0.5 - ctx.t) * amount


def write_png(arr, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Image.fromarray(arr, "RGBA").save(path, optimize=True)

# ============================================================================ animation


def ease(kind, f):
    f = min(max(f, 0.0), 1.0)
    if kind in (None, "lin"):
        return f
    if kind == "in":
        return f * f
    if kind == "in3":
        return f * f * f
    if kind == "out":
        return 1 - (1 - f) ** 2
    if kind == "out3":
        return 1 - (1 - f) ** 3
    if kind == "snap":
        return 1 - (1 - f) ** 5
    if kind == "io":
        return f * f * (3 - 2 * f)
    if kind == "io3":
        return 4 * f ** 3 if f < 0.5 else 1 - (-2 * f + 2) ** 3 / 2
    if kind == "back":
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * (f - 1) ** 3 + c1 * (f - 1) ** 2
    if kind == "hold":
        return 0.0 if f < 1 else 1.0
    raise ValueError(kind)


class Track:
    def __init__(self, keys):
        ks = []
        for k in keys:
            t, val = k[0], k[1]
            e = k[2] if len(k) > 2 else "io"
            ks.append((float(t), np.array(val, dtype=float), e))
        ks.sort(key=lambda x: x[0])
        self.keys = ks

    def __call__(self, t):
        ks = self.keys
        if t <= ks[0][0]:
            return ks[0][1]
        if t >= ks[-1][0]:
            return ks[-1][1]
        for (t0, a, _), (t1, b, e) in zip(ks, ks[1:]):
            if t0 <= t <= t1:
                f = 0 if t1 == t0 else (t - t0) / (t1 - t0)
                return a + (b - a) * ease(e, f)
        return ks[-1][1]


def env(t, t0, t1, t2, t3, e_in="io", e_out="io"):
    """Trapezoid envelope 0->1 (t0..t1), hold, 1->0 (t2..t3)."""
    if t <= t0 or t >= t3:
        return 0.0
    if t < t1:
        return ease(e_in, (t - t0) / (t1 - t0))
    if t <= t2:
        return 1.0
    return 1 - ease(e_out, (t - t2) / (t3 - t2))


def shake(t, freq=18.0, amp=1.0, seed=0):
    """Deterministic jitter in [-amp, amp]."""
    return amp * (math.sin(t * freq * 6.283 + seed) * 0.6 + math.sin(t * freq * 1.7 * 6.283 + seed * 3.1) * 0.4)


class Clip:
    def __init__(self, name, length, loop=False):
        self.name = name
        self.length = float(length)
        self.loop = loop
        self.parts = defaultdict(list)

    def k(self, bone, chan, keys):
        self.parts[(bone, chan)].append(Track(keys))
        return self

    def f(self, bone, chan, fn):
        self.parts[(bone, chan)].append(fn)
        return self

    def rot(self, bone, keys):
        return self.k(bone, "rotation", keys)

    def pos(self, bone, keys):
        return self.k(bone, "position", keys)

    def scl(self, bone, keys):
        return self.k(bone, "scale", keys)

    def eval(self, bone, chan, t):
        fns = self.parts.get((bone, chan))
        if not fns:
            return None
        if chan == "scale":
            v = np.ones(3)
            for fn in fns:
                v = v * np.asarray(fn(t), dtype=float)
        else:
            v = np.zeros(3)
            for fn in fns:
                v = v + np.asarray(fn(t), dtype=float)
        return v

    def bake(self, dt=0.05, tol=None):
        tol = tol or {"rotation": 0.35, "position": 0.04, "scale": 0.006}
        n = int(round(self.length / dt))
        times = [round(i * self.length / n, 4) for i in range(n + 1)]
        bones = OrderedDict()
        for (bone, chan) in sorted(self.parts.keys()):
            vals = np.array([self.eval(bone, chan, t) for t in times])
            if bone == "head" and chan == "rotation":
                assert np.all(np.abs(vals[:, :2]) < 1e-6), f"{self.name}: head rot x/y is overwritten by GeckoLib look"
            base = 1.0 if chan == "scale" else 0.0
            if np.all(np.abs(vals - base) < 1e-4):
                continue
            keep = _simplify(times, vals, tol[chan])
            ch = OrderedDict()
            for i in keep:
                ch[_tkey(times[i])] = [_num(x) for x in vals[i]]
            bones.setdefault(bone, OrderedDict())[chan] = ch
        out = OrderedDict()
        if self.loop == "hold":
            out["loop"] = "hold_on_last_frame"
        else:
            out["loop"] = bool(self.loop)
        out["animation_length"] = self.length
        out["bones"] = bones
        return out


def _num(x):
    r = round(float(x), 3)
    if r == 0:
        r = 0.0
    if r == int(r):
        return int(r) if abs(r) < 1e9 else r
    return r


def _tkey(t):
    s = repr(round(t, 4))
    return s


def _simplify(times, vals, tol):
    n = len(times)
    keep = {0, n - 1}
    T = np.array(times)

    def rec(a, b):
        if b - a < 2:
            return
        f = ((T[a + 1:b] - T[a]) / (T[b] - T[a]))[:, None]
        interp = vals[a] + (vals[b] - vals[a]) * f
        err = np.abs(vals[a + 1:b] - interp).max(axis=1)
        k = int(np.argmax(err))
        if err[k] > tol:
            m = a + 1 + k
            keep.add(m)
            rec(a, m)
            rec(m, b)

    rec(0, n - 1)
    return sorted(keep)


# Spinning parts: (bone, axis, symmetry step in degrees). GeckoLib blends between clips by lerping raw
# Euler angles, so a halo that ends an attack at 157.5 deg would visibly spin back to the next clip's 0.
# wrap_spins keeps each listed angle inside [-step/2, step/2) by inserting invisible 0.1 ms micro-steps
# of exactly one symmetry step. That's exact for single-axis spins, and a 360 step is exact for any bone.
SPIN_WRAP = {
    "sentinel_construct": [("right_pauldron", 1, 360.0), ("left_pauldron", 1, 360.0)],
    "ender_colossus": [("crown", 1, 360.0)],
    "astral_seraph": [("halo", 2, 30.0), ("halo_inner", 2, 45.0)],
    "sun_herald": [("halo", 2, 15.0), ("halo_rays", 2, 22.5), ("staff", 0, 360.0), ("staff", 2, 360.0)],
    "void_sovereign": [("chest_star", 2, 180.0), ("halo", 2, 60.0)],
}
_SPIN_EPS = 0.0001


def _wrap_channel(ch, axis, step):
    keys = sorted(((float(t), list(v)) for t, v in ch.items()), key=lambda kv: kv[0])
    if not keys or not all(isinstance(v, list) and len(v) == 3 for _, v in keys):
        return ch
    kidx = lambda a: math.floor((a + step / 2) / step + 1e-9)
    out = []
    for n, (t, v) in enumerate(keys):
        if n > 0:
            (t0, v0), a0, a1 = keys[n - 1], keys[n - 1][1][axis], v[axis]
            k0, k1 = kidx(a0), kidx(a1)
            if k0 != k1 and abs(a1 - a0) > 1e-9:
                rng = range(k0, k1) if k1 > k0 else range(k0 - 1, k1 - 1, -1)
                for kb in rng:
                    b = (kb + 0.5) * step                       # boundary value crossed
                    f = (b - a0) / (a1 - a0)
                    tc = t0 + f * (t - t0)
                    base = [v0[i] + (v[i] - v0[i]) * f for i in range(3)]
                    before, after = (kb, kb + 1) if k1 > k0 else (kb + 1, kb)
                    pa, pb = list(base), list(base)
                    pa[axis] = b - before * step
                    pb[axis] = b - after * step
                    ta, tb = tc, tc + _SPIN_EPS
                    if tb >= t - 1e-9:
                        ta, tb = tc - _SPIN_EPS, tc
                    out.append((ta, pa))
                    out.append((tb, pb))
        w = list(v)
        w[axis] = v[axis] - kidx(v[axis]) * step
        out.append((t, w))
    res = OrderedDict()
    for t, v in out:
        res[repr(round(t, 5))] = [_num(x) for x in v]
    return res


def wrap_spins(data, spinners):
    for an, a in data["animations"].items():
        for bone, axis, step in spinners:
            ch = a.get("bones", {}).get(bone, {}).get("rotation")
            if isinstance(ch, dict) and not any(k in ch for k in ("vector", "pre", "post")):
                a["bones"][bone]["rotation"] = _wrap_channel(ch, axis, step)
    return data


def export_anims(clips, path, name=None):
    data = OrderedDict([("format_version", "1.8.0"), ("animations", OrderedDict())])
    for c in clips:
        data["animations"][c.name] = c.bake()
    if name in SPIN_WRAP:
        wrap_spins(data, SPIN_WRAP[name])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
    return data


def export_geo(model, path, visible=(5, 6, 2.5)):
    data = model.to_json(visible)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
    return data

# ============================================================================ build + preview


def asset_paths(name):
    return {
        "geo": os.path.join(ASSETS, "geo", "entity", f"{name}.geo.json"),
        "anim": os.path.join(ASSETS, "animations", "entity", f"{name}.animation.json"),
        "tex": os.path.join(ASSETS, "textures", "entity", f"{name}.png"),
        "glow": os.path.join(ASSETS, "textures", "entity", f"{name}_glowmask.png"),
    }


def build(name, model, shaders, clips, painter_kw=None, visible=(5, 6, 2.5)):
    paths = asset_paths(name)
    W, H = model.pack()
    print(f"{name}: {model.cube_count()} cubes, texture {W}x{H} (png {W * TEX_SCALE}x{H * TEX_SCALE})")
    geo = export_geo(model, paths["geo"], visible)
    rgba, glow = Painter(model, shaders, **(painter_kw or {})).paint()
    write_png(rgba, paths["tex"])
    write_png(glow, paths["glow"])
    anims = export_anims(clips, paths["anim"], name)
    return geo, rgba, glow, anims


def contact_sheet(name, geo, rgba, glow, anims, poses, frame=(100, 112), scale=2.2, yaw=35, pitch=-12, path=None):
    """One row per animation, one column per sampled time (3/4 view)."""
    from PIL import ImageDraw
    g = gp.load_geo(geo)
    ncol = max(len(t) for _, t in poses)
    W, H = int(frame[0] * scale), int(frame[1] * scale)
    sheet = Image.new("RGB", (W * ncol + 120, H * len(poses)), (18, 18, 22))
    d = ImageDraw.Draw(sheet)
    for r, (an, times) in enumerate(poses):
        d.text((6, r * H + H // 2 - 6), an, fill=(235, 235, 240))
        for c, t in enumerate(times):
            pose = gp.sample_anim(anims["animations"][an], t)
            im = gp.render(g, rgba, glow, pose, yaw=yaw, pitch=pitch, scale=scale, size=(W, H),
                           center=(0, frame[1] / 2 - 8))
            ImageDraw.Draw(im).text((4, 3), f"t={t:.2f}", fill=(210, 210, 220))
            sheet.paste(im, (120 + c * W, r * H))
    path = path or os.path.join(PREVIEW, f"{name}_animations.png")
    sheet.save(path)
    return path


def previews(name, geo, rgba, glow, anims, hitbox, poses, frame=(150, 92), scale=4.0, tag=""):
    """poses: list of (anim_name, [times]) strips to render."""
    os.makedirs(PREVIEW, exist_ok=True)
    g = gp.load_geo(geo)
    out = []
    sheet = gp.render_sheet(g, rgba, glow, None, scale=scale, title=f"{name} rest", hitbox=hitbox, frame=frame)
    p = os.path.join(PREVIEW, f"{name}_rest{tag}.png")
    sheet.save(p)
    out.append(p)
    for an, times in poses:
        strip = gp.render_anim_strip(g, rgba, glow, anims["animations"][an], times, scale=scale * 0.8,
                                     title=f"{name} {an}", hitbox=hitbox, frame=(frame[0] * 0.75, frame[1]))
        p = os.path.join(PREVIEW, f"{name}_{an.replace('.', '_')}{tag}.png")
        strip.save(p)
        out.append(p)
    return out
