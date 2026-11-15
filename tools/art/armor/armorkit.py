"""Armor pipeline glue: GeckoLib armor bone contract, reference player body, previews, export.

Bone contract (GeckoLib 4 GeoArmorRenderer, Bedrock coordinates, y up, feet at y=0):
  helmet -> armorHead, chestplate -> armorBody + armorRightArm + armorLeftArm,
  leggings -> armorRightLeg + armorLeftLeg, boots -> armorRightBoot + armorLeftBoot.
Decorative bones must be children (descendants) of one of these 8 bones, otherwise they would be
drawn for every armor piece.
"""
import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import armorlib as al
import geo_preview as gp

HERE = os.path.dirname(os.path.abspath(__file__))
PREVIEW = os.path.join(HERE, "preview")

MAIN_BONES = {
    "armorHead": (0, 24, 0),
    "armorBody": (0, 24, 0),
    "armorRightArm": (-5, 22, 0),
    "armorLeftArm": (5, 22, 0),
    "armorRightLeg": (-1.9, 12, 0),
    "armorLeftLeg": (1.9, 12, 0),
    "armorRightBoot": (-1.9, 12, 0),
    "armorLeftBoot": (1.9, 12, 0),
}
PIECES = {
    "helmet": ["armorHead"],
    "chestplate": ["armorBody", "armorRightArm", "armorLeftArm"],
    "leggings": ["armorRightLeg", "armorLeftLeg"],
    "boots": ["armorRightBoot", "armorLeftBoot"],
}

# player body bone -> armor bones driven by it
BODY_TO_ARMOR = {
    "head": ["armorHead"], "body": ["armorBody"], "rightArm": ["armorRightArm"], "leftArm": ["armorLeftArm"],
    "rightLeg": ["armorRightLeg", "armorRightBoot"], "leftLeg": ["armorLeftLeg", "armorLeftBoot"],
}


def new_model(name):
    m = al.Model(name)
    for b, piv in MAIN_BONES.items():
        m.bone(b, None, piv)
    return m


# ============================================================================ reference body

def body_model():
    m = al.Model("player_ref")
    m.bone("head", None, (0, 24, 0)).cube((-4, 24, -4), (8, 8, 8), "head")
    m.bone("body", None, (0, 24, 0)).cube((-4, 12, -2), (8, 12, 4), "shirt")
    m.bone("rightArm", None, (-5, 22, 0)).cube((-8, 12, -2), (4, 12, 4), "arm")
    m.bone("leftArm", None, (5, 22, 0)).cube((4, 12, -2), (4, 12, 4), "arm")
    m.bone("rightLeg", None, (-1.9, 12, 0)).cube((-3.9, 0, -2), (4, 12, 4), "leg")
    m.bone("leftLeg", None, (1.9, 12, 0)).cube((-0.1, 0, -2), (4, 12, 4), "leg")
    return m


SKIN = np.array([196, 150, 122])
HAIR = np.array([62, 40, 24])
SHIRT = np.array([0, 160, 160])
PANTS = np.array([52, 50, 150])
SHOE = np.array([90, 90, 96])


def _body_shader(kind):
    def sh(ctx):
        p = ctx.p
        y = p[:, 1]
        rgb = np.zeros((ctx.N, 3))
        if kind == "head":
            rgb[:] = SKIN
            hair = (y > 30.2) | (ctx.face == "up") | (ctx.face == "south") | ((ctx.face in ("east", "west")) & ((y > 28.5) | (p[:, 2] > 1)))
            rgb[hair] = HAIR
            if ctx.face == "north":
                x = p[:, 0]
                eye = (np.abs(y - 27.5) < 0.5) & (np.abs(np.abs(x) - 2.0) < 1.0)
                rgb[eye] = [250, 250, 250]
                pupil = eye & (np.abs(np.abs(x) - 1.5) < 0.5)
                rgb[pupil] = [70, 60, 160]
                mouth = (np.abs(y - 25.5) < 0.5) & (np.abs(x) < 1.6)
                rgb[mouth] = [120, 70, 60]
        elif kind == "shirt":
            rgb[:] = SHIRT
        elif kind == "arm":
            rgb[:] = np.where((y > 20)[:, None], SHIRT, SKIN)
        elif kind == "leg":
            rgb[:] = np.where((y < 2)[:, None], SHOE, PANTS)
        rgb = rgb * (1.0 + al.vgrad(ctx, 0.1)[:, None] * 0.6)
        return rgb, 255, np.zeros(ctx.N, dtype=bool)
    return sh


_BODY_CACHE = {}


def body_layer():
    if "b" not in _BODY_CACHE:
        m = body_model()
        m.pack()
        shaders = {k: _body_shader(k) for k in ("head", "shirt", "arm", "leg")}
        rgba, glow = al.Painter(m, shaders, ao_strength=0).paint()
        _BODY_CACHE["b"] = (gp.load_geo(m.to_json()), rgba)
    return _BODY_CACHE["b"]


BODY_BOXES = [  # world AABBs of the reference body (used as AO occluders)
    ((-4, 24, -4), (4, 32, 4)), ((-4, 12, -2), (4, 24, 2)), ((-8, 12, -2), (-4, 24, 2)),
    ((4, 12, -2), (8, 24, 2)), ((-3.9, 0, -2), (0.1, 12, 2)), ((-0.1, 0, -2), (3.9, 12, 2)),
]

# ============================================================================ poses

POSES = {
    "rest": {},
    "walk": {"rightArm": (-32, 0, 4), "leftArm": (30, 0, -4), "rightLeg": (28, 0, 0), "leftLeg": (-28, 0, 0),
             "head": (6, 12, 0)},
    "reach": {"rightArm": (-80, 10, 0), "leftArm": (-20, 0, -8), "head": (-10, -15, 0), "rightLeg": (-10, 0, 0),
              "leftLeg": (8, 0, 0)},
}


def pose_dicts(pose_name, anim_pose=None):
    """Returns (body_pose, armor_pose) in geo_preview sample format."""
    P = POSES[pose_name]
    bp, ap = {}, {}
    for b, rot in P.items():
        bp[b] = {"rotation": np.array(rot, dtype=float)}
        for a in BODY_TO_ARMOR[b]:
            ap[a] = {"rotation": np.array(rot, dtype=float)}
    if anim_pose:
        for k, v in anim_pose.items():
            ap.setdefault(k, {}).update(v)
    return bp, ap


# ============================================================================ previews

VIEWS = [("front", 0, -6), ("3/4", 38, -12), ("side", 90, -4), ("back", 180, -8), ("3/4 back", 218, -12)]


def _label(im, text, xy=(6, 4), fill=(235, 235, 245)):
    d = ImageDraw.Draw(im)
    d.text((xy[0] + 1, xy[1] + 1), text, fill=(0, 0, 0))
    d.text(xy, text, fill=fill)


def render_worn(geo, tex, glow, view=("3/4", 38, -12), pose="rest", anim_pose=None, scale=7.0,
                frame=(56, 50), center=(0, 19), hidden=(), body=True, bg=(64, 68, 82)):
    bgeo, btex = body_layer()
    bp, ap = pose_dicts(pose, anim_pose)
    layers = []
    if body:
        layers.append({"geo": bgeo, "tex": btex, "pose": bp})
    layers.append({"geo": geo, "tex": tex, "glow": glow, "pose": ap, "hidden": set(hidden)})
    W, H = int(frame[0] * scale), int(frame[1] * scale)
    return gp.render_layers(layers, yaw=view[1], pitch=view[2], scale=scale, size=(W, H), center=center, bg=bg,
                            grid=False)


def descendants(geo, roots):
    kids = {}
    for b in geo["bones"]:
        kids.setdefault(b.get("parent"), []).append(b["name"])
    out = set()
    stack = list(roots)
    while stack:
        n = stack.pop()
        if n in out:
            continue
        out.add(n)
        stack.extend(kids.get(n, []))
    return out


def hidden_except(geo, piece_names):
    keep = descendants(geo, [b for p in piece_names for b in PIECES[p]])
    return {b["name"] for b in geo["bones"]} - keep


def sheet_views(title, geo, tex, glow, anim_pose=None, scale=10.0, frame=(44, 44), center=(0, 18.5), views=None,
                pose="rest", cols=3, extra_walk=True):
    """Grid of the standard views (front, 3/4, side, back, 3/4 back) + a walking pose."""
    views = views or VIEWS
    tiles = []
    for v in views:
        im = render_worn(geo, tex, glow, v, pose=pose, anim_pose=anim_pose, scale=scale, frame=frame, center=center)
        _label(im, v[0])
        tiles.append(im)
    if extra_walk:
        im = render_worn(geo, tex, glow, ("walk", 30, -10), pose="walk", anim_pose=anim_pose, scale=scale,
                         frame=frame, center=center)
        _label(im, "walk pose 3/4")
        tiles.append(im)
    W, H = tiles[0].size
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (W * cols, H * rows + 18), (22, 22, 28))
    for k, im in enumerate(tiles):
        sheet.paste(im, ((k % cols) * W, 18 + (k // cols) * H))
    _label(sheet, title, (6, 3), (255, 255, 255))
    return sheet


def sheet_details(title, geo, tex, glow, anim_pose=None):
    """Helm close-ups + each armor piece on its own (verifies the bone -> piece mapping)."""
    row1 = []
    for v in (("helm front", 0, -4), ("helm 3/4", 40, -10), ("helm back 3/4", 150, -16)):
        im = render_worn(geo, tex, glow, v, anim_pose=anim_pose, scale=17, frame=(26, 22), center=(0, 29.5))
        _label(im, v[0])
        row1.append(im)
    row2 = []
    for piece in ("helmet", "chestplate", "leggings", "boots"):
        hid = hidden_except(geo, [piece])
        im = render_worn(geo, tex, glow, ("3/4", 38, -12), anim_pose=anim_pose, scale=8, frame=(41, 44),
                         center=(0, 18.5), hidden=hid)
        _label(im, piece + " only")
        row2.append(im)
    w = max(sum(t.size[0] for t in row1), sum(t.size[0] for t in row2))
    h1 = row1[0].size[1]
    h2 = row2[0].size[1]
    sheet = Image.new("RGB", (w, h1 + h2 + 18), (22, 22, 28))
    x = 0
    for t in row1:
        sheet.paste(t, (x, 18))
        x += t.size[0]
    x = 0
    for t in row2:
        sheet.paste(t, (x, 18 + h1))
        x += t.size[0]
    _label(sheet, title, (6, 3), (255, 255, 255))
    return sheet


def sheet_anim(title, geo, tex, glow, anim, times, view=("3/4", 38, -12)):
    tiles = []
    for t in times:
        pose = gp.sample_anim(anim, t)
        im = render_worn(geo, tex, glow, view, anim_pose=pose, scale=5.0, frame=(56, 50))
        _label(im, f"t={t:.2f}s")
        tiles.append(im)
    W, H = tiles[0].size
    sheet = Image.new("RGB", (W * len(tiles), H + 18), (22, 22, 28))
    for i, im in enumerate(tiles):
        sheet.paste(im, (i * W, 18))
    _label(sheet, title, (6, 3), (255, 255, 255))
    return sheet


def lineup(entries, path, views=(("3/4", 38, -12), ("back 3/4", 205, -10)), scale=7, frame=(38, 42),
           center=(0, 18.5)):
    """entries: [(label, geo, tex, glow)] -> one column per entry, one row per view."""
    tiles = []
    for label, geo, tex, glow in entries:
        col = []
        for v in views:
            im = render_worn(geo, tex, glow, v, scale=scale, frame=frame, center=center)
            _label(im, f"{label}  {v[0]}")
            col.append(im)
        tiles.append(col)
    W, H = tiles[0][0].size
    sheet = Image.new("RGB", (W * len(tiles), H * len(views)), (20, 20, 26))
    for c, col in enumerate(tiles):
        for r, im in enumerate(col):
            sheet.paste(im, (c * W, r * H))
    sheet.save(path)
    return path


def texture_sheet(tex, glow, scale=3):
    h, w = tex.shape[:2]
    a = Image.fromarray(tex, "RGBA")
    g = Image.fromarray(glow, "RGBA")
    out = Image.new("RGBA", (w * 2 + 8, h), (40, 40, 48, 255))
    chk = Image.new("RGBA", (w, h), (70, 70, 80, 255))
    out.paste(Image.alpha_composite(chk, a), (0, 0))
    out.paste(Image.alpha_composite(Image.new("RGBA", (w, h), (0, 0, 0, 255)), g), (w + 8, 0))
    return out.resize((out.size[0] * scale, out.size[1] * scale), Image.NEAREST)


# ============================================================================ export

def export_geo(model, path):
    data = model.to_json(visible=(3, 3.5, 1.5))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
    return data


def paint(model, shaders, ao=0.85):
    return al.Painter(model, shaders, ao_strength=ao, occluders=BODY_BOXES).paint()


def save_textures(name, variant, rgba, glow):
    p = al.asset_paths(name, variant)
    al.write_png(rgba, p["tex"])
    al.write_png(glow, p["glow"])
    return p
