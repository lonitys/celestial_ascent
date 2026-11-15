"""Villager profession overlays (64x64, vanilla VillagerModel UV layout).

Layout (texOffs, size w x h x d):
  head 0,0 8x10x8 | hat 32,0 8x10x8 (+0.51) | hat rim 30,47 16x16x1 | nose 24,0 2x4x2
  body 16,20 8x12x6 | robe/jacket 0,38 8x20x6 (+0.5) | arms 44,22 4x8x4 | arms middle 40,38 8x4x4
  legs 0,22 4x12x4
The type layer's robe hides the body box, so torso clothing goes on the robe.
Rim: up-facing brim is 31,48 16x16 (bottom rows = in front of the face), underside 48,48.
"""
import os

from common import *

BOX = {
    'head': (0, 0, 8, 10, 8), 'hat': (32, 0, 8, 10, 8), 'nose': (24, 0, 2, 4, 2),
    'body': (16, 20, 8, 12, 6), 'robe': (0, 38, 8, 20, 6), 'arm': (44, 22, 4, 8, 4),
    'armmid': (40, 38, 8, 4, 4), 'leg': (0, 22, 4, 12, 4),
}
RIM_TOP = (31, 48, 16, 16)
RIM_UNDER = (48, 48, 16, 16)


def face_rect(box, face):
    u, v, w, h, d = BOX[box]
    return {'top': (u + d, v, w, d), 'bottom': (u + d + w, v, w, d), 'right': (u, v + d, d, h),
            'front': (u + d, v + d, w, h), 'left': (u + d + w, v + d, d, h),
            'back': (u + 2 * d + w, v + d, w, h)}[face]


def valid_mask():
    m = np.zeros((64, 64), bool)
    for b in BOX:
        for f in ('top', 'bottom', 'right', 'front', 'left', 'back'):
            x, y, w, h = face_rect(b, f)
            m[y:y + h, x:x + w] = True
    for x, y, w, h in (RIM_TOP, RIM_UNDER, (30, 48, 1, 16), (47, 48, 1, 16), (31, 47, 16, 1), (47, 47, 16, 1)):
        m[y:y + h, x:x + w] = True
    return m


class Overlay:
    def __init__(self):
        self.cv = Canvas(64, 64)

    def paint(self, box, face, rows, pal, ox=0, oy=0):
        x, y, w, h = face_rect(box, face) if isinstance(box, str) else box
        assert len(rows) + oy <= h, (box, face, len(rows), h)
        for r in rows:
            assert len(r) + ox <= w, (box, face, r, w)
        self.cv.grid(rows, pal, x + ox, y + oy)

    def fill(self, box, face, col, rows=None):
        x, y, w, h = face_rect(box, face)
        r0, r1 = rows if rows else (0, h - 1)
        self.cv.rect(x, y + r0, x + w - 1, y + r1, col)

    def check(self):
        bad = self.cv.mask() & ~valid_mask()
        assert not bad.any(), f'pixels outside UV regions at {np.argwhere(bad)[:5]}'


# ======================================================================
# BANKER: dark green-black vest, gold watch chain, shirt sleeves with
# garters, green visor cap.
# ======================================================================
BANKER = {
    '0': '#0b130e', '1': '#121e17', '2': '#1a2b21', '3': '#243b2d', '4': '#30503c',
    'g': '#8a6418', 'G': '#d4a83c', 'H': '#f6dc84',
    's': '#a39b86', 'S': '#cdc6b1', 'T': '#e2dcc8', 'k': '#4e1418', 'K': '#74242a',
    'v': '#1e4a2e', 'V': '#2e6a42', 'w': '#123020',
}


def banker():
    o = Overlay()
    P = BANKER
    # --- vest on the robe (torso rows 0-11)
    o.paint('robe', 'front', [
        "13sSSs31",
        "13sKKs31",
        "123KK321",
        "12233221",
        "122G2221",
        "1222c221",
        "122Gcg21",
        "1222gcH1",
        "122G2221",
        "12222221",
        "12222221",
        "1222.221",
        "111...11",
    ], P)
    o.paint('robe', 'right', [
        "122221", "122221", "122221", "122221", "122221", "122221",
        "122221", "122221", "122221", "122221", "122221", "112211",
    ], P)
    o.paint('robe', 'left', [
        "122221", "122221", "122221", "122221", "122221", "122221",
        "122221", "122221", "122221", "122221", "122221", "112211",
    ], P)
    o.paint('robe', 'back', [
        "12222221",
        "12222221",
        "12222221",
        "12333321",
        "12322321",
        "12222221",
        "12222221",
        "1sssGss1",
        "12222221",
        "12222221",
        "12222221",
        "11111111",
    ], {**P, 's': '#2a4535'})
    o.paint('robe', 'top', [
        "34....43",
        "34....43",
        "34....43",
        "34....43",
        "34....43",
        "34....43",
    ], P)
    # --- shirt sleeves with dark garters
    sleeves = {'right': ["TSSs", "SSSs", "SsSs", "2G22", "3333", "SSSs", "SsSs", "sSss"],
               'front': ["TTSS", "TSSs", "SSsS", "3G33", "3333", "TSSs", "SSsS", "sSss"],
               'left': ["SSss", "SSss", "sSss", "2g22", "2222", "SSss", "Ssss", "ssss"],
               'back': ["SSss", "Ssss", "sSss", "2222", "2222", "Ssss", "ssss", "ssss"]}
    for f, rows in sleeves.items():
        o.paint('arm', f, rows, P)
    o.paint('arm', 'top', ["TTTS", "TTSS", "TSSs", "SSss"], P)
    o.paint('armmid', 'top', ["sS....Ss", "SS....SS", "Ss....sS", "SS....SS"], P)
    o.paint('armmid', 'front', ["Ss....sS", "SS....SS", "Ss....sS", "ss....ss"], P)
    o.paint('armmid', 'right', ["SSss", "SsSs", "SSss", "ssss"], P)
    o.paint('armmid', 'left', ["ssSS", "sSsS", "ssSS", "ssss"], P)
    o.paint('armmid', 'bottom', ["ss....ss", "ss....ss", "ss....ss", "ss....ss"], P)
    # --- visor cap: crown on the hat layer, gold band, visor on the rim
    o.paint('hat', 'top', [
        "23333332",
        "34444432",
        "34433332",
        "343GG332",
        "343GG332",
        "33333322",
        "23333221",
        "12222211",
    ], P)
    for f, shade in (('front', '3'), ('right', '3'), ('left', '2'), ('back', '2')):
        o.paint('hat', f, [shade * 8, shade * 8, "GGGGGGGG", "11111111"], P)
    o.cv.put(40 + 3, 8 + 2, P['H'])           # band glint on the front
    # visor: up-facing brim in front of the face (rim rows 60-62, cols 34-43)
    o.cv.grid(["VVVVVVVVVV", ".vVVVVVVv.", "..wvvvvw.."], P, 34, 60)
    o.cv.grid(["wwwwwwwwww", ".wwwwwwww.", "..wwwwww.."], P, 51, 60)
    o.check()
    return o


# ======================================================================
# TITANSMITH: heavy leather apron, steel shoulder guards, brass goggles.
# ======================================================================
SMITH = {
    'a': '#2a170b', 'b': '#3b2312', 'c': '#52321a', 'd': '#6a4424', 'e': '#86582f',
    't': '#2c3138', 'u': '#474f5a', 'v': '#6a7480', 'w': '#9aa4ae', 'x': '#cdd5db',
    'r': '#8a6a22', 'R': '#c49a3a',
    'L': '#4fc6e8', 'l': '#2a86b0', 'W': '#d8fbff',
    'k': '#1e1a18', 's': '#a8a090',
}


def titansmith():
    o = Overlay()
    P = SMITH
    o.paint('robe', 'front', [
        "vw....wu",
        "wvbbbbvu",
        "uvcddcvt",
        "..cdLc..",
        "..cLWl..",
        "..cdlc..",
        "..cddc..",
        "bRbbbbRb",
        "bcdddcdb",
        "bcdeddcb",
        "bcdkkdcb",
        "bcdsdkcb",
        "bcddddcb",
        "bcdedddb",
        "bcddddcb",
        "bcddddcb",
        "bcdedcdb",
        "bccddccb",
        "abbbbbba",
        ".a.aa.a.",
    ], P)
    for f in ('right', 'left'):
        o.paint('robe', f, [
            "wvvvvu", "vuuuut", "uttttt", "......", "......", "......",
            "......", "bbbbbb", "b.....", "b.....", "b.....", "b.....",
            "b.....", "b.....", "b.....", "b.....", "b.....", "b.....", "a.....",
        ] if f == 'right' else [
            "uvvvvw", "tuuuuv", "tttttu", "......", "......", "......",
            "......", "bbbbbb", ".....b", ".....b", ".....b", ".....b",
            ".....b", ".....b", ".....b", ".....b", ".....b", ".....b", ".....a",
        ], P)
    o.paint('robe', 'back', [
        "uvvvvvvu",
        "tuu..uut",
        "tb....bt",
        "..b..b..",
        "...bb...",
        "...bb...",
        "..b..b..",
        "bbbRRbbb",
        "...bb...",
        "..b..b..",
    ], P)
    o.paint('robe', 'top', [
        "xww..wwv",
        "wvv..vvu",
        "wvu..uvu",
        "wvu..uvu",
        "vvu..uvu",
        "vuu..uut",
    ], P)
    # steel pauldrons over the top of the arms, leather sleeves, heavy gloves
    for f in ('right', 'front', 'left', 'back'):
        o.paint('arm', f, ["wwvv", "vvuu", "tRtt", "cccb", "cdcb", "cccb", "bccb", "bbbb"], P)
    o.paint('arm', 'top', ["xwwv", "wvvu", "wvvu", "vuut"], P)
    o.paint('armmid', 'front', ["bccb.bcc", "cddcbcdd", "cddcbcdd", "bccbbbcc"], P)
    o.paint('armmid', 'top', ["bccbbccb", "cddccddc", "cddccddc", "bccbbccb"], P)
    o.paint('armmid', 'right', ["bccb", "cddc", "cddc", "bccb"], P)
    o.paint('armmid', 'left', ["bccb", "cddc", "cddc", "bccb"], P)
    o.paint('armmid', 'bottom', ["bbbbbbbb", "bccbbccb", "bccbbccb", "bbbbbbbb"], P)
    # goggles pushed up on the forehead (hat rows 2-4)
    o.paint('hat', 'front', [
        "........",
        "........",
        "kRRkkRRk",
        "RLWRRLWR",
        "RllRRllR",
        "kRRkkRRk",
    ], P)
    for f in ('right', 'left', 'back'):
        o.paint('hat', f, ["........", "........", "........", "kkkkkkkk", "kbbbbbbk"], P)
    o.check()
    return o


# ======================================================================
# RELIC DEALER: deep purple hooded robe, gold embroidery, star pendants.
# ======================================================================
RELIC = {
    '0': '#160a22', '1': '#221135', '2': '#30194a', '3': '#432463', '4': '#5a3383', '5': '#7448a6',
    'g': '#8a6420', 'G': '#d6ac46', 'H': '#fbe48a', 'W': '#ffffff',
    'm': '#c040b0', 'c': '#7fe6f5',
}


def relic_dealer():
    o = Overlay()
    P = RELIC
    o.paint('robe', 'front', [
        "33G..G32",
        "323GG322",
        "3233g322",
        "323HW322",
        "32GWHG22",
        "323HG322",
        "3223g322",
        "GGGGGGGG",
        "3g2Gg2g2",
        "323GG322",
        "32gGgg22",
        "323GG322",
        "3233g322",
        "32gGGg22",
        "323GG322",
        "3233g322",
        "32gGGg22",
        "323GG322",
        "GHGGGGHG",
        "g1g11g1g",
    ], P)
    side = [
        "433332", "433332", "432232", "433332", "433332", "432332", "433332",
        "GGGGGG", "433332", "432332", "433332", "433H32", "432G32", "433332",
        "432332", "433332", "433332", "432332", "GGHGGG", "1g11g1",
    ]
    o.paint('robe', 'right', side, P)
    o.paint('robe', 'left', [r[::-1] for r in side], P)
    o.paint('robe', 'back', [
        "33333332",
        "33333332",
        "33344332",
        "334HW432",
        "33GWHG32",
        "334HG432",
        "33344332",
        "GGGGGGGG",
        "33333332",
        "33333322",
        "3333H332",
        "333GWG32",
        "3333G332",
        "33333332",
        "33333322",
        "33333332",
        "33233332",
        "33333332",
        "GHGGGGHG",
        "g1g11g1g",
    ], P)
    o.paint('robe', 'top', [
        "44G..G43",
        "44G..G43",
        "43....32",
        "43....32",
        "43G..G32",
        "33G..G22",
    ], P)
    # wide sleeves with gold cuffs; hands left bare in the middle
    for f in ('right', 'front', 'left', 'back'):
        o.paint('arm', f, ["4443", "4433", "4333", "3332", "4332", "3332", "GGGG", "gHgg"], P)
    o.paint('arm', 'top', ["5444", "4443", "4433", "4332"], P)
    o.paint('armmid', 'front', ["GG....GG", "3g....g3", "32....23", "22....22"], P)
    o.paint('armmid', 'top', ["GG....GG", "43....34", "43....34", "33....33"], P)
    o.paint('armmid', 'right', ["G443", "g333", "3332", "3322"], P)
    o.paint('armmid', 'left', ["344G", "333g", "2333", "2233"], P)
    o.paint('armmid', 'bottom', ["22....22", "22....22", "22....22", "22....22"], P)
    # hood on the hat layer: frames the face with an embroidered edge
    o.paint('hat', 'top', [
        "34444443",
        "45555443",
        "45544433",
        "4544G433",
        "4444H433",
        "44444332",
        "34443322",
        "23333221",
    ], P)
    o.paint('hat', 'front', [
        "4G5HG54G",
        "4GGGGGG4",
        "4G....G3",
        "4G....G3",
        "4G....G3",
        "4G....G3",
        "3G....G2",
        "3G....G2",
        "3G....G2",
        "2G....G2",
    ], P)
    hood_side = [
        "45444444", "44444443", "44443433", "44444433", "44344333",
        "44443333", "43433332", "43333332", "33333222", "33322222",
    ]
    o.paint('hat', 'right', hood_side, P)        # front edge on the right of this face
    o.paint('hat', 'left', [r[::-1] for r in hood_side], P)
    o.paint('hat', 'back', [
        "44444443", "44444433", "44444333", "4444H333", "444GWG33",
        "4444G332", "44433332", "43333322", "33333222", "32222221",
    ], P)
    # a small star pendant hanging at the forehead
    o.cv.grid(["H", "W"], P, 40 + 4, 8 + 2)
    o.check()
    return o


OVERLAYS = {'banker': banker, 'titansmith': titansmith, 'relic_dealer': relic_dealer}
HAT_META = {'banker': 'full', 'titansmith': 'partial', 'relic_dealer': 'full'}


# ======================================================================
# preview: render the VillagerModel boxes with a combined texture
# ======================================================================
def villager_elements(tex):
    def faces(box, mirror=False, infl=0.0):
        u, v, w, h, d = BOX[box]
        q = lambda r: [c / 4 for c in r]
        fr = {
            'north': (u + d, v + d, u + d + w, v + d + h),
            'south': (u + 2 * d + w, v + d, u + 2 * d + 2 * w, v + d + h),
            'east': (u, v + d, u + d, v + d + h),
            'west': (u + d + w, v + d, u + 2 * d + w, v + d + h),
            'up': (u + d + w, v + d, u + d, v),
            'down': (u + d + w, v, u + d + 2 * w, v + d),
        }
        if mirror:
            fr = {k: (r[2], r[1], r[0], r[3]) for k, r in fr.items()}
            fr['east'], fr['west'] = fr['west'], fr['east']
        return {k: {'uv': q(r), 'texture': tex} for k, r in fr.items()}

    def box(ex, ey, ez, w, h, d, infl=0.0):
        # entity space (y down, front -z, -x = entity right) -> preview space
        x0, x1 = -(ex + w) - infl, -ex + infl
        y0, y1 = 24 - (ey + h) - infl, 24 - ey + infl
        return [x0, y0, ez - infl], [x1, y1, ez + d + infl]

    E = []
    for name, (e, infl, mirror, rotn) in {
        'head': ((-4, -10, -4, 8, 10, 8), 0, False, None),
        'hat': ((-4, -10, -4, 8, 10, 8), 0.51, False, None),
        'nose': ((-1, -3, -6, 2, 4, 2), 0, False, None),
        'body': ((-4, 0, -3, 8, 12, 6), 0, False, None),
        'robe': ((-4, 0, -3, 8, 20, 6), 0.5, False, None),
        'leg_r': ((-4, 12, -2, 4, 12, 4), 0, False, None),
        'leg_l': ((0, 12, -2, 4, 12, 4), 0, True, None),
        'arm_r': ((-8, 1, -3, 4, 8, 4), 0, False, 'arms'),
        'arm_l': ((4, 1, -3, 4, 8, 4), 0, True, 'arms'),
        'arm_m': ((-4, 5, -3, 8, 4, 4), 0, False, 'arms'),
    }.items():
        key = {'leg_r': 'leg', 'leg_l': 'leg', 'arm_r': 'arm', 'arm_l': 'arm', 'arm_m': 'armmid'}.get(name, name)
        f, t = box(*e, infl=infl)
        el = {'from': f, 'to': t, 'faces': faces(key, mirror)}
        if rotn:
            el['rotation'] = {'origin': [0, 21, -1], 'axis': 'x', 'angle': 42.97}
        E.append(el)
    # hat rim: horizontal plane at entity y -6..-5
    E.append({'from': [-8, 29, -8], 'to': [8, 30, 8], 'faces': {
        'up': {'uv': [47 / 4, 16, 31 / 4, 12], 'texture': tex},
        'down': {'uv': [12, 12, 16, 16], 'texture': tex}}})
    return E


def mannequin():
    """Neutral stand-in for the vanilla base + biome layers (preview only)."""
    cv = Canvas(64, 64)
    skin, skin_d, robe, robe_d = '#b98a6a', '#9a6e52', '#7d7468', '#635b52'
    for b in ('head', 'nose', 'arm', 'armmid', 'leg', 'body'):
        for f in ('top', 'bottom', 'right', 'front', 'left', 'back'):
            x, y, w, h = face_rect(b, f)
            cv.rect(x, y, x + w - 1, y + h - 1, skin if f in ('front', 'top') else skin_d)
    for f in ('top', 'bottom', 'right', 'front', 'left', 'back'):
        x, y, w, h = face_rect('robe', f)
        cv.rect(x, y, x + w - 1, y + h - 1, robe if f in ('front', 'top') else robe_d)
    # face
    cv.hline(9, 14, 13, '#4a3020')
    for x, c in ((9, '#ffffff'), (10, '#2a6a3a'), (13, '#2a6a3a'), (14, '#ffffff')):
        cv.put(x, 14, c)
    return cv


def render_preview(over, base, tag, tmp_dir=None):
    from model_preview import render_model, _tex_cache
    comb = base.copy()
    comb.paste(over.cv, 0, 0)
    tmp_dir = tmp_dir or os.path.join(PREVIEW, '_tmp')
    os.makedirs(tmp_dir, exist_ok=True)
    path = os.path.join(tmp_dir, f'villager_{tag}.png')
    comb.pil().save(path)
    _tex_cache.pop(path, None)
    m = {'textures': {}, 'elements': villager_elements(path)}
    views = [render_model(m, yaw, 12, S=9, center=(0, 16, 0), size=440) for yaw in (200, 160, 25)]
    return views


def sheet(rows, out_path):
    from PIL import ImageDraw
    cell = max(max(i.width, i.height) for _, r in rows for i in r) + 16
    tw = 64 * 4 + 16
    W = tw + len(rows[0][1]) * cell + 16
    H = len(rows) * (cell + 18) + 16
    im = Image.new('RGBA', (W, H), (118, 118, 118, 255))
    d = ImageDraw.Draw(im)
    for j, (n, (tex, views)) in enumerate([(n, (r[0], r[1:])) for n, r in rows]):
        y = 8 + j * (cell + 18)
        d.text((10, y), n, fill=(15, 15, 15, 255))
        im.alpha_composite(tex.resize((256, 256), Image.NEAREST), (8, y + 18))
        for i, v in enumerate(views):
            im.alpha_composite(v, (tw + 8 + i * cell + (cell - v.width) // 2, y + 18 + (cell - v.height) // 2))
    im.save(out_path)
    return out_path


def main(vanilla_dir=None, out_dir=None):
    rows = []
    base = mannequin()
    for name, fn in OVERLAYS.items():
        o = fn()
        o.cv.save(f'textures/entity/villager/profession/{name}.png')
        write_json(f'textures/entity/villager/profession/{name}.png.mcmeta', {'villager': {'hat': HAT_META[name]}})
        rows.append((name, [o.cv.pil()] + render_preview(o, base, name)))
    print(sheet(rows, os.path.join(PREVIEW, 'villagers.png')))
    if vanilla_dir:
        # optional: preview over the vanilla base + plains layers (kept out of the repo)
        b = Canvas.load(os.path.join(vanilla_dir, 'villager.png'))
        b.paste(Canvas.load(os.path.join(vanilla_dir, 'type', 'plains.png')), 0, 0)
        vrows = []
        for name, fn in OVERLAYS.items():
            o = fn()
            vrows.append((name, [o.cv.pil()] + render_preview(o, b, name + '_v', out_dir)))
        out = os.path.join(out_dir, 'villagers_vanilla.png')
        print(sheet(vrows, out))


if __name__ == '__main__':
    import sys
    # usage: gen_villagers.py [vanilla_villager_texture_dir out_dir]
    main(*(sys.argv[1:3] if len(sys.argv) > 2 else (None, None)))
