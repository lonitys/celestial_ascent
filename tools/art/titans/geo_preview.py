"""Software rasteriser for Bedrock/GeckoLib .geo.json models.

Replicates what GeckoLib 4 does when it renders a Bedrock model:
  * Bedrock space is mirrored on X relative to Minecraft render space. GeckoLib negates
    X of points/pivots/positions and negates the X and Y rotation angles. We keep everything
    in Bedrock coordinates and use the equivalent effective matrix
        R_b(rx, ry, rz) = Rz(-rz) . Ry(ry) . Rx(-rx)
    (standard right-handed matrices), then flip X for display.
  * bone transform: parent . T(anim_pos) . T(pivot) . R(rest + anim_rot) . S(anim_scale) . T(-pivot)
  * cube transform:  bone . T(cube_pivot) . R(cube_rot) . T(-cube_pivot)
  * inflate grows the box on every side; box UV uses floor(size) and the standard
    Minecraft skin layout (front = north = -Z, model right side = -X).

Usage:
  python geo_preview.py MODEL.geo.json TEXTURE.png [--glow GLOW.png] [--anim FILE --name ANIM
                       --time T] [--out OUT.png] [--scale 5]
"""
import argparse
import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw

# ----------------------------------------------------------------------------- math

def _rx(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], dtype=float)


def _ry(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], dtype=float)


def _rz(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=float)


def rot_b(rot):
    """Effective rotation matrix in Bedrock space for Bedrock euler angles (degrees)."""
    rx, ry, rz = (math.radians(v) for v in rot)
    return _rz(-rz) @ _ry(ry) @ _rx(-rx)


def euler_from_matrix(m):
    """Inverse of rot_b: find Bedrock euler degrees for an effective rotation matrix."""
    # m = Rz(a) Ry(b) Rx(c) with a=-rz, b=ry, c=-rx
    sb = -m[2, 0]
    sb = max(-1.0, min(1.0, sb))
    b = math.asin(sb)
    if abs(sb) < 0.999999:
        c = math.atan2(m[2, 1], m[2, 2])
        a = math.atan2(m[1, 0], m[0, 0])
    else:  # gimbal lock
        c = 0.0
        a = math.atan2(-m[0, 1], m[1, 1])
    return [-math.degrees(c), math.degrees(b), -math.degrees(a)]


def mat4(r=None, t=None):
    m = np.eye(4)
    if r is not None:
        m[:3, :3] = r
    if t is not None:
        m[:3, 3] = t
    return m


def trans(v):
    return mat4(t=np.asarray(v, dtype=float))


def scale4(s):
    m = np.eye(4)
    m[0, 0], m[1, 1], m[2, 2] = s
    return m

# ----------------------------------------------------------------------------- loading


def load_geo(path_or_dict):
    if isinstance(path_or_dict, dict):
        data = path_or_dict
    else:
        with open(path_or_dict, encoding="utf-8") as f:
            data = json.load(f)
    geo = data["minecraft:geometry"][0]
    desc = geo["description"]
    return {
        "identifier": desc.get("identifier"),
        "tw": desc.get("texture_width", 64),
        "th": desc.get("texture_height", 64),
        "bones": geo.get("bones", []),
    }


def load_anims(path_or_dict):
    if isinstance(path_or_dict, dict):
        data = path_or_dict
    else:
        with open(path_or_dict, encoding="utf-8") as f:
            data = json.load(f)
    return data["animations"]

# ----------------------------------------------------------------------------- animation sampling


def _kf_vals(v):
    """Return (pre, post) vectors of a keyframe value."""
    if isinstance(v, dict):
        post = v.get("post", v.get("vector", v.get("pre")))
        pre = v.get("pre", post)
        return _vec(pre), _vec(post)
    return _vec(v), _vec(v)


def _vec(v):
    if isinstance(v, (int, float)):
        return np.array([v, v, v], dtype=float)
    out = []
    for c in v:
        out.append(float(c) if isinstance(c, (int, float)) else 0.0)
    return np.array(out, dtype=float)


def sample_channel(ch, t):
    if ch is None:
        return None
    if isinstance(ch, (list, int, float)):
        return _vec(ch)
    if isinstance(ch, dict) and ("vector" in ch or "post" in ch):
        return _kf_vals(ch)[1]
    keys = sorted(((float(k), v) for k, v in ch.items()), key=lambda kv: kv[0])
    if t <= keys[0][0]:
        return _kf_vals(keys[0][1])[0]
    if t >= keys[-1][0]:
        return _kf_vals(keys[-1][1])[1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            a = _kf_vals(v0)[1]
            b = _kf_vals(v1)[0]
            f = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
            return a + (b - a) * f
    return _kf_vals(keys[-1][1])[1]


def sample_anim(anim, t):
    """Return {bone: {'rotation': v, 'position': v, 'scale': v}} at time t (seconds)."""
    length = float(anim.get("animation_length", 0) or 0)
    if anim.get("loop") is True and length > 0:
        t = t % length if t < length else (t % length if t > length else length)
    pose = {}
    for bname, bd in anim.get("bones", {}).items():
        p = {}
        for chan in ("rotation", "position", "scale"):
            if chan in bd:
                p[chan] = sample_channel(bd[chan], t)
        pose[bname] = p
    return pose

# ----------------------------------------------------------------------------- transforms


def bone_matrices(geo, pose=None):
    """World (model) matrices of all bones in Bedrock space, pose = sample_anim output."""
    pose = pose or {}
    bones = {b["name"]: b for b in geo["bones"]}
    cache = {}

    def get(name):
        if name in cache:
            return cache[name]
        b = bones[name]
        parent = b.get("parent")
        pm = get(parent) if parent in bones else np.eye(4)
        piv = np.array(b.get("pivot", [0, 0, 0]), dtype=float)
        rot = np.array(b.get("rotation", [0, 0, 0]), dtype=float)
        bp = pose.get(name, {})
        pos = np.zeros(3)
        scl = np.ones(3)
        if bp.get("rotation") is not None:
            rot = rot + bp["rotation"]
        if bp.get("position") is not None:
            pos = bp["position"]
        if bp.get("scale") is not None:
            scl = bp["scale"]
        m = pm @ trans(pos) @ trans(piv) @ mat4(rot_b(rot)) @ scale4(scl) @ trans(-piv)
        cache[name] = m
        return m

    for n in bones:
        get(n)
    return cache


def cube_matrix(bone_m, cube):
    if "rotation" in cube and any(cube["rotation"]):
        piv = np.array(cube.get("pivot", [0, 0, 0]), dtype=float)
        return bone_m @ trans(piv) @ mat4(rot_b(cube["rotation"])) @ trans(-piv)
    return bone_m


# face definitions: for face param (s, t) in [0,1]^2 (s across, t down in the UV rect)
# returns a point inside the [0,1]^3 unit box (x, y, z fractions) and the outward normal.
FACES = {
    #        corner(s,t) -> (fx, fy, fz)                     normal
    "north": (lambda s, t: (s, 1 - t, 0 * s), (0, 0, -1)),
    "south": (lambda s, t: (1 - s, 1 - t, 1 + 0 * s), (0, 0, 1)),
    "west": (lambda s, t: (0 * s, 1 - t, 1 - s), (-1, 0, 0)),   # minX = model's right side
    "east": (lambda s, t: (1 + 0 * s, 1 - t, s), (1, 0, 0)),    # maxX = model's left side
    "up": (lambda s, t: (s, 1 + 0 * s, 1 - t), (0, 1, 0)),
    "down": (lambda s, t: (s, 0 * s, 1 - t), (0, -1, 0)),
}


def box_uv_rects(uv, size):
    """Standard box-UV layout. Returns {face: (u, v, w, h)} in model texture pixels."""
    u, v = uv
    w, h, d = (math.floor(s + 1e-6) for s in size)
    return {
        "west": (u, v + d, d, h),
        "north": (u + d, v + d, w, h),
        "east": (u + d + w, v + d, d, h),
        "south": (u + d + w + d, v + d, w, h),
        "up": (u + d, v, w, d),
        "down": (u + d + w, v, w, d),
    }


def face_uv_rects(cube):
    uv = cube.get("uv", [0, 0])
    if isinstance(uv, dict):
        rects = {}
        for f, fd in uv.items():
            if f in FACES:
                (u, v), (w, h) = fd["uv"], fd.get("uv_size", [0, 0])
                rects[f] = (u, v, w, h)
        return rects
    return box_uv_rects(uv, cube["size"])


def cube_faces(cube, m):
    """Yield (face, world_corners(4,3), uv_corners(4,2), rect, normal_world)."""
    o = np.array(cube["origin"], dtype=float)
    s = np.array(cube["size"], dtype=float)
    inf = float(cube.get("inflate", 0.0))
    lo = o - inf
    ext = s + 2 * inf
    rects = face_uv_rects(cube)
    st = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    for face, (fn, nrm) in FACES.items():
        if face not in rects:
            continue
        u, v, w, h = rects[face]
        pts = []
        uvs = []
        for (ss, tt) in st:
            fx, fy, fz = fn(ss, tt)
            p = lo + ext * np.array([fx, fy, fz], dtype=float)
            pts.append(p)
            uvs.append((u + ss * w, v + tt * h))
        pts = np.array(pts)
        pw = (m @ np.c_[pts, np.ones(4)].T).T[:, :3]
        nw = m[:3, :3] @ np.array(nrm, dtype=float)
        ln = np.linalg.norm(nw)
        nw = nw / ln if ln > 1e-9 else nw
        yield face, pw, np.array(uvs, dtype=float), (u, v, w, h), nw


def collect_faces(geo, pose=None):
    mats = bone_matrices(geo, pose)
    out = []
    for b in geo["bones"]:
        bm = mats[b["name"]]
        for cube in b.get("cubes", []):
            cm = cube_matrix(bm, cube)
            for f in cube_faces(cube, cm):
                out.append((b["name"],) + f)
    return out

# ----------------------------------------------------------------------------- raster


def view_matrix(yaw_deg, pitch_deg):
    """Bedrock world -> view space (x right, y up, z into the screen).

    Bedrock -> Java render space is an X flip. A camera sitting at -Z (in front of the
    model) looking +Z has screen-right = -X_java = +X_bedrock. yaw rotates the model
    (positive yaw shows more of the model's right side), pitch tilts the top towards the
    camera."""
    f = np.diag([-1.0, 1.0, 1.0])            # Bedrock -> Java
    ry = _ry(math.radians(yaw_deg))           # Java-space yaw
    rx = _rx(math.radians(pitch_deg))
    to_screen = np.diag([-1.0, 1.0, 1.0])     # screen x = -X_java
    return to_screen @ rx @ ry @ f


def render(geo, tex, glow=None, pose=None, yaw=0.0, pitch=0.0, scale=5.0,
           size=None, center=None, light=True, bg=(38, 40, 48), hitbox=None, ground=True):
    """Render to a PIL image. tex/glow are RGBA numpy arrays (H, W, 4)."""
    faces = collect_faces(geo, pose)
    V = view_matrix(yaw, pitch)
    th_px, tw_px = tex.shape[0], tex.shape[1]
    sx = tw_px / geo["tw"]
    sy = th_px / geo["th"]

    allp = np.concatenate([f[2] for f in faces]) if faces else np.zeros((1, 3))
    vp = allp @ V.T
    if size is None:
        w = int((vp[:, 0].max() - vp[:, 0].min()) * scale + 40)
        h = int((vp[:, 1].max() - vp[:, 1].min()) * scale + 40)
        size = (w, h)
    W, H = size
    if center is None:
        cx = (vp[:, 0].max() + vp[:, 0].min()) / 2
        cy = (vp[:, 1].max() + vp[:, 1].min()) / 2
        center = (cx, cy)
    cx, cy = center

    def to_px(p):
        q = p @ V.T
        return np.c_[(q[:, 0] - cx) * scale + W / 2, H / 2 - (q[:, 1] - cy) * scale, q[:, 2]]

    img = np.zeros((H, W, 3), dtype=float)
    yy = np.linspace(0, 1, H)[:, None]
    img[:] = np.array(bg, dtype=float)[None, None, :] * (1.15 - 0.35 * yy[..., None])
    zbuf = np.full((H, W), np.inf)

    ldir = np.array([-0.35, 0.75, -0.55])
    ldir /= np.linalg.norm(ldir)
    ldir2 = np.array([0.6, 0.2, 0.4])
    ldir2 /= np.linalg.norm(ldir2)

    # ground grid + hitbox drawn after (overlay)
    for (bname, face, pw, uvs, rect, nw) in faces:
        if rect[2] <= 0 and rect[3] <= 0:
            continue
        P = to_px(pw)
        nv = V @ nw
        if light:
            # entity cutout no-cull: back faces visible -> use |n| facing camera
            if nv[2] > 0:
                nv = -nv
            sh = 0.42 + 0.50 * max(0.0, float(nv @ ldir)) + 0.18 * max(0.0, float(nv @ ldir2))
            sh = min(sh, 1.08)
        else:
            sh = 1.0
        u0, v0, rw, rh = rect
        tx0 = int(math.floor(u0 * sx + 1e-6))
        ty0 = int(math.floor(v0 * sy + 1e-6))
        tx1 = max(tx0, int(math.ceil((u0 + rw) * sx - 1e-6)) - 1)
        ty1 = max(ty0, int(math.ceil((v0 + rh) * sy - 1e-6)) - 1)
        for tri in ((0, 1, 2), (0, 2, 3)):
            a, b, c = P[list(tri)]
            ua, ub, uc = uvs[list(tri)]
            xmin = max(int(math.floor(min(a[0], b[0], c[0]))), 0)
            xmax = min(int(math.ceil(max(a[0], b[0], c[0]))), W - 1)
            ymin = max(int(math.floor(min(a[1], b[1], c[1]))), 0)
            ymax = min(int(math.ceil(max(a[1], b[1], c[1]))), H - 1)
            if xmin > xmax or ymin > ymax:
                continue
            area = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
            if abs(area) < 1e-9:
                continue
            xs = np.arange(xmin, xmax + 1) + 0.5
            ys = np.arange(ymin, ymax + 1) + 0.5
            X, Y = np.meshgrid(xs, ys)
            w0 = ((b[0] - X) * (c[1] - Y) - (b[1] - Y) * (c[0] - X)) / area
            w1 = ((c[0] - X) * (a[1] - Y) - (c[1] - Y) * (a[0] - X)) / area
            w2 = 1 - w0 - w1
            inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
            if not inside.any():
                continue
            Z = w0 * a[2] + w1 * b[2] + w2 * c[2]
            U = w0 * ua[0] + w1 * ub[0] + w2 * uc[0]
            Vv = w0 * ua[1] + w1 * ub[1] + w2 * uc[1]
            txi = np.clip(np.floor(U * sx).astype(int), tx0, tx1)
            tyi = np.clip(np.floor(Vv * sy).astype(int), ty0, ty1)
            txi = np.clip(txi, 0, tw_px - 1)
            tyi = np.clip(tyi, 0, th_px - 1)
            iy = (Y - 0.5).astype(int)
            ix = (X - 0.5).astype(int)
            col = tex[tyi, txi]
            ok = inside & (col[..., 3] >= 26) & (Z < zbuf[iy, ix])
            if not ok.any():
                continue
            rgb = col[..., :3].astype(float) * sh
            if glow is not None:
                g = glow[tyi, txi]
                gm = g[..., 3] > 0
                rgb = np.where(gm[..., None], np.maximum(col[..., :3].astype(float), g[..., :3].astype(float)), rgb)
            zbuf[iy[ok], ix[ok]] = Z[ok]
            img[iy[ok], ix[ok]] = rgb[ok]

    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(out)
    if ground:
        # ground plane line through y=0 (feet)
        g = to_px(np.array([[-40, 0, 0], [40, 0, 0], [0, 0, -40], [0, 0, 40]], dtype=float))
        d.line([tuple(g[0][:2]), tuple(g[1][:2])], fill=(90, 95, 110), width=1)
        d.line([tuple(g[2][:2]), tuple(g[3][:2])], fill=(90, 95, 110), width=1)
    if hitbox:
        hw, hh = hitbox[0] * 8, hitbox[1] * 16
        corners = np.array([[x, y, z] for x in (-hw, hw) for y in (0, hh) for z in (-hw, hw)], dtype=float)
        cp = to_px(corners)
        edges = [(0, 1), (2, 3), (4, 5), (6, 7), (0, 2), (1, 3), (4, 6), (5, 7), (0, 4), (1, 5), (2, 6), (3, 7)]
        for i, j in edges:
            d.line([tuple(cp[i][:2]), tuple(cp[j][:2])], fill=(255, 80, 80), width=1)
    return out


def load_rgba(path):
    return np.array(Image.open(path).convert("RGBA"))


VIEWS = [("front", 0, -8), ("3/4", 35, -14), ("side", 90, -6), ("back", 180, -10)]


def model_extent(geo, pose=None):
    faces = collect_faces(geo, pose)
    allp = np.concatenate([f[2] for f in faces])
    return allp.min(axis=0), allp.max(axis=0)


def render_sheet(geo, tex, glow=None, pose=None, scale=5.0, views=VIEWS, title=None,
                 hitbox=None, frame=(150, 92)):
    """Render several views side by side with a shared frame (units around the model)."""
    fw, fh = frame
    W, H = int(fw * scale), int(fh * scale)
    tiles = []
    for name, yaw, pitch in views:
        im = render(geo, tex, glow, pose, yaw=yaw, pitch=pitch, scale=scale, size=(W, H),
                    center=(0, fh / 2 - 12), hitbox=hitbox)
        d = ImageDraw.Draw(im)
        d.text((6, 4), name, fill=(220, 220, 230))
        tiles.append(im)
    sheet = Image.new("RGB", (W * len(tiles), H + (16 if title else 0)), (20, 20, 24))
    for i, im in enumerate(tiles):
        sheet.paste(im, (i * W, 16 if title else 0))
    if title:
        ImageDraw.Draw(sheet).text((6, 2), title, fill=(255, 255, 255))
    return sheet


def render_anim_strip(geo, tex, glow, anim, times, yaw=35, pitch=-12, scale=4.0, title=None,
                      hitbox=None, frame=(110, 96)):
    fw, fh = frame
    W, H = int(fw * scale), int(fh * scale)
    sheet = Image.new("RGB", (W * len(times), H + 16), (20, 20, 24))
    for i, t in enumerate(times):
        pose = sample_anim(anim, t)
        im = render(geo, tex, glow, pose, yaw=yaw, pitch=pitch, scale=scale, size=(W, H),
                    center=(0, fh / 2 - 12), hitbox=hitbox)
        ImageDraw.Draw(im).text((6, 4), f"t={t:.2f}", fill=(230, 230, 240))
        sheet.paste(im, (i * W, 16))
    if title:
        ImageDraw.Draw(sheet).text((6, 2), title, fill=(255, 255, 255))
    return sheet


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("geo")
    ap.add_argument("texture")
    ap.add_argument("--glow")
    ap.add_argument("--anim")
    ap.add_argument("--name")
    ap.add_argument("--time", type=float, default=None)
    ap.add_argument("--times", default=None, help="comma separated times for a strip")
    ap.add_argument("--yaw", type=float, default=35)
    ap.add_argument("--scale", type=float, default=4.0)
    ap.add_argument("--out", default="preview.png")
    args = ap.parse_args()
    geo = load_geo(args.geo)
    tex = load_rgba(args.texture)
    glow = load_rgba(args.glow) if args.glow else None
    if args.anim and args.name and args.times:
        anim = load_anims(args.anim)[args.name]
        times = [float(x) for x in args.times.split(",")]
        img = render_anim_strip(geo, tex, glow, anim, times, yaw=args.yaw, scale=args.scale,
                                title=f"{os.path.basename(args.geo)} {args.name}")
    else:
        pose = None
        if args.anim and args.name:
            pose = sample_anim(load_anims(args.anim)[args.name], args.time or 0.0)
        img = render_sheet(geo, tex, glow, pose, scale=args.scale,
                           title=os.path.basename(args.geo) + (f" {args.name}@{args.time}" if pose else ""))
    img.save(args.out)
    print("wrote", args.out, img.size)


if __name__ == "__main__":
    main()
