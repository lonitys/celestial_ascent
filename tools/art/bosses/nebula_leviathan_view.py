"""Preview helpers for nebula_leviathan. The shared previews frame tiles from the model's y extent,
which crops a long horizontal serpent in top-down and 3/4 views, so these frame every view from its
projected screen-space bounds instead."""
import os

import numpy as np
from PIL import Image, ImageDraw

import geo_preview as gp
from bosslib import PREVIEW

BG = (20, 20, 24)


def _points(g, pose):
    faces = gp.collect_faces(g, pose)
    return np.concatenate([f[2] for f in faces])


def bounds(pts, yaw, pitch):
    q = pts @ gp.view_matrix(yaw, pitch).T
    return q[:, 0].min(), q[:, 0].max(), q[:, 1].min(), q[:, 1].max()


def fit(bb, W, H, pad=0.05):
    x0, x1, y0, y1 = bb
    s = min(W * (1 - 2 * pad) / max(x1 - x0, 1e-3), H * (1 - 2 * pad) / max(y1 - y0, 1e-3))
    return s, ((x0 + x1) / 2, (y0 + y1) / 2)


def tile(g, rgba, glow, pose, yaw, pitch, W, H, label=None, hitbox=None, scale=None, center=None):
    if scale is None or center is None:
        s, c = fit(bounds(_points(g, pose), yaw, pitch), W, H)
        scale = scale or s
        center = center or c
    im = gp.render(g, rgba, glow, pose, yaw=yaw, pitch=pitch, scale=scale, size=(W, H), center=center,
                   hitbox=hitbox)
    if label:
        ImageDraw.Draw(im).text((6, 4), label, fill=(230, 230, 240))
    return im


def grid(rows, title=None):
    """rows = [[img, img, ...], ...] (images in a row share a height)."""
    top = 16 if title else 0
    W = max(sum(im.size[0] for im in r) for r in rows)
    H = sum(r[0].size[1] for r in rows) + top
    sheet = Image.new("RGB", (W, H), BG)
    y = top
    for r in rows:
        x = 0
        for im in r:
            sheet.paste(im, (x, y))
            x += im.size[0]
        y += r[0].size[1]
    if title:
        ImageDraw.Draw(sheet).text((6, 2), title, fill=(255, 255, 255))
    return sheet


def rest_sheet(name, geo, rgba, glow, hitbox, pose=None, tag="", title=None):
    g = gp.load_geo(geo)
    wide = [("side", 90, -6), ("top (pitch -75)", 90, -75)]
    small = [("front", 0, -6), ("3/4", 35, -14), ("3/4 back", 150, -16), ("low 3/4", -35, 14)]
    r1 = [tile(g, rgba, glow, pose, y, p, 760, 300, f"{name} {n}", hitbox) for n, y, p in wide]
    r2 = [tile(g, rgba, glow, pose, y, p, 380, 300, f"{name} {n}", hitbox) for n, y, p in small]
    p = os.path.join(PREVIEW, f"{name}_rest{tag}.png")
    grid([r1, r2], title).save(p)
    return p


def strip(name, geo, rgba, glow, anims, an, times, views=(("3/4", 35, -14), ("top", 90, -75)), W=400, H=250,
          tag="", hitbox=None):
    """Columns = times, rows = views; each row uses one scale/centre for all times."""
    g = gp.load_geo(geo)
    anim = anims["animations"][an]
    poses = [gp.sample_anim(anim, t) for t in times]
    pts = [_points(g, ps) for ps in poses]
    rows = []
    for vn, yaw, pitch in views:
        bbs = np.array([bounds(p, yaw, pitch) for p in pts])
        bb = (bbs[:, 0].min(), bbs[:, 1].max(), bbs[:, 2].min(), bbs[:, 3].max())
        s, c = fit(bb, W, H, 0.04)
        row = []
        for t, ps in zip(times, poses):
            row.append(tile(g, rgba, glow, ps, yaw, pitch, W, H, f"{vn} t={t:.2f}", hitbox, s, c))
        rows.append(row)
    p = os.path.join(PREVIEW, f"{name}_{an.replace('.', '_')}{tag}.png")
    grid(rows, f"{name} {an} ({anim['animation_length']}s)").save(p)
    return p


def pose_sheet(name, geo, rgba, glow, anims, an, t, tag="", hitbox=None):
    g = gp.load_geo(geo)
    pose = gp.sample_anim(anims["animations"][an], t)
    views = [("front", 0, -6), ("3/4", 35, -12), ("3/4 left", -40, -8)]
    r1 = [tile(g, rgba, glow, pose, y, p, 520, 420, n, hitbox) for n, y, p in views]
    r2 = [tile(g, rgba, glow, pose, 90, -6, 780, 300, "side", hitbox),
          tile(g, rgba, glow, pose, 90, -75, 780, 300, "top", hitbox)]
    p = os.path.join(PREVIEW, f"{name}_pose_{an.replace('.', '_')}{tag}.png")
    grid([r1, r2], f"{name} {an} @ {t:.2f}s").save(p)
    return p


def closeup(name, geo, rgba, glow, focus, views, frame=46, px=520, pose=None, tag="", anims=None, an=None, t=0.0):
    """Close-ups of a world point (rest pose unless pose/an given) from several views."""
    g = gp.load_geo(geo)
    if an is not None:
        pose = gp.sample_anim(anims["animations"][an], t)
    focus = np.asarray(focus, dtype=float)
    tiles = []
    for view in views:
        vn, yaw, pitch = view[:3]
        vp = view[3] if len(view) > 3 else pose
        q = gp.view_matrix(yaw, pitch) @ focus
        im = gp.render(g, rgba, glow, vp, yaw=yaw, pitch=pitch, scale=px / frame, size=(px, px),
                       center=(q[0], q[1]), ground=False)
        ImageDraw.Draw(im).text((6, 4), vn, fill=(230, 230, 240))
        tiles.append(im)
    p = os.path.join(PREVIEW, f"{name}_closeup{tag}.png")
    grid([tiles]).save(p)
    return p


def stage_sheet(name, geo, rgba, glow, views=(("side", 90, -6), ("3/4", 35, -14), ("front", 0, -6),
                                              ("top", 90, -75)), W=520, H=260, pose=None, out=None, title=None):
    """Evolution comparison: columns = stage 1 (stage2_*/stage3_* bones hidden), stage 2, stage 3; each
    row (view) is framed once on the full stage 3 model so the columns line up."""
    import stage_preview as sp
    g = gp.load_geo(geo)
    gs = [sp.stage_geo(g, k) for k in (1, 2, 3)]
    rows = []
    for vn, yaw, pitch in views:
        s, c = fit(bounds(_points(g, pose), yaw, pitch), W, H)
        rows.append([tile(gk, rgba, glow, pose, yaw, pitch, W, H, f"stage {k + 1}  {vn}", None, s, c)
                     for k, gk in enumerate(gs)])
    p = out or os.path.join(PREVIEW, f"{name}_stages.png")
    grid(rows, title or f"{name}: stage bones hidden (stage 1) vs stage 2 vs stage 3").save(p)
    return p
