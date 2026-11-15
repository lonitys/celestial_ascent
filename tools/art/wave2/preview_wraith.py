"""Preview: the 1.21.1 vex body (VexModel boxes, converted to y-up) wearing the
void_wraith texture, rendered with the wave-2 model renderer at a few angles."""
from PIL import Image, ImageDraw

from w2common import PREVIEW, os, _font
from w2model import render_model

TEX = 'celestialascent:entity/void_wraith'


def box(name, f, t, u, v, w, h, d, rot=None, mirror_wing=False):
    """Element with entity-cube face rects (pixel uvs on a 32px texture -> /2 for 16-unit uvs)."""
    def r(x0, y0, x1, y1):
        return [x0 / 2, y0 / 2, x1 / 2, y1 / 2]
    fr = {
        'up': r(u + d, v, u + d + w, v + d), 'down': r(u + d + w, v, u + d + 2 * w, v + d),
        'west': r(u, v + d, u + d, v + d + h), 'north': r(u + d, v + d, u + d + w, v + d + h),
        'east': r(u + d + w, v + d, u + 2 * d + w, v + d + h), 'south': r(u + 2 * d + w, v + d, u + 2 * d + 2 * w, v + d + h),
    }
    if mirror_wing:
        fr['east'] = fr['west']
    e = {'name': name, 'from': list(f), 'to': list(t),
         'faces': {k: {'uv': uv, 'texture': '#t'} for k, uv in fr.items()}}
    if rot:
        e['rotation'] = rot
    return e


def vex_model(wing_angle=35):
    Y = lambda yd: 24 - yd      # model space is y-down
    E = []
    E.append(box('head', (-2.5, Y(17.5), -2.5), (2.5, Y(12.5), 2.5), 0, 0, 5, 5, 5))
    E.append(box('body', (-1.5, Y(21.5), -1), (1.5, Y(17.5), 1), 0, 10, 3, 4, 2))
    E.append(box('robe', (-1.3, Y(23.3), -0.8), (1.3, Y(18.7), 0.8), 0, 16, 3, 5, 2))
    E.append(box('right_arm', (-2.9, Y(21.15), -0.9), (-1.1, Y(17.35), 0.9), 23, 0, 2, 4, 2))
    E.append(box('left_arm', (1.1, Y(21.15), -0.9), (2.9, Y(17.35), 0.9), 23, 6, 2, 4, 2))
    E.append(box('left_wing', (0.5, Y(23.5), 1), (0.5, Y(18.5), 9), 16, 14, 0, 5, 8,
                 rot={'axis': 'y', 'angle': -wing_angle, 'origin': [0.5, 0, 1]}, mirror_wing=True))
    E.append(box('right_wing', (-0.5, Y(23.5), 1), (-0.5, Y(18.5), 9), 16, 14, 0, 5, 8,
                 rot={'axis': 'y', 'angle': wing_angle, 'origin': [-0.5, 0, 1]}, mirror_wing=True))
    return {'textures': {'t': TEX}, 'elements': E}


def main():
    m = vex_model()
    views = [(180 + 30, 15), (180 - 35, 20), (30, 15), (90, 10)]
    ims = [render_model(m, yw, pt, S=22, center=(0, 12, 0)) for yw, pt in views]
    pad = 20
    W = sum(i.width for i in ims) + pad * (len(ims) + 1)
    H = max(i.height for i in ims) + 2 * pad
    out = Image.new('RGBA', (W, H * 2), (40, 36, 48, 255))
    light = Image.new('RGBA', (W, H), (150, 150, 150, 255))
    out.paste(light, (0, H))
    x = pad
    for im in ims:
        out.alpha_composite(im, (x, pad))
        out.alpha_composite(im, (x, H + pad))
        x += im.width + pad
    p = os.path.join(PREVIEW, 'void_wraith_model.png')
    out.save(p)
    print(p)


if __name__ == '__main__':
    main()
