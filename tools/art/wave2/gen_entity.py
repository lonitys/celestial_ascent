"""Void Wraith entity texture on the vanilla vex UV layout (32x32, 1.21.1 VexModel).

Box layout (texOffs, size w x h x d):
  head      (0,0)   5x5x5      body  (0,10) 3x4x2    robe (0,16) 3x5x2 (-0.2 inflate)
  right arm (23,0)  2x4x2      left arm (23,6) 2x4x2
  wings     (16,14) 0x5x8  -> visible face at u16-24 v22-27
VexModel renders with entityTranslucent, so the robe and wings may be partly
transparent. The vanilla vex.png is read from the Minecraft resources jar to
verify the footprint.
"""
import zipfile
import io

from w2common import *

JAR = os.path.join(os.path.dirname(ASSETS), '..', '..', '..', '..', 'build', 'moddev', 'artifacts',
                   'neoforge-21.1.262-client-extra-aka-minecraft-resources.jar')

V = ['#06030a', '#0e0816', '#170e24', '#211534', '#2d1d46', '#3c285c', '#503878', '#6a4c9a']


def faces(u, v, w, h, d):
    """Rects (x0, y0, x1, y1) exclusive for each cube face, vanilla layout."""
    return {
        'up': (u + d, v, u + d + w, v + d),
        'down': (u + d + w, v, u + d + 2 * w, v + d),
        'right': (u, v + d, u + d, v + d + h),            # west / entity's right side
        'front': (u + d, v + d, u + d + w, v + d + h),
        'left': (u + d + w, v + d, u + 2 * d + w, v + d + h),
        'back': (u + 2 * d + w, v + d, u + 2 * d + 2 * w, v + d + h),
    }


def fill_noise(cv, rect, pal, seed, alpha=255, grain=0.5):
    x0, y0, x1, y1 = rect
    r = rng(seed)
    for y in range(y0, y1):
        for x in range(x0, x1):
            t = (y - y0) / max(1, (y1 - y0 - 1))
            v = 0.62 - 0.35 * t + (r.random() - 0.5) * grain
            k = int(max(0, min(len(pal) - 1, round(v * (len(pal) - 1)))))
            cv.put(x, y, with_alpha(pal[k], alpha))


def vanilla_mask():
    try:
        with zipfile.ZipFile(os.path.abspath(JAR)) as z:
            data = z.read('assets/minecraft/textures/entity/illager/vex.png')
        im = Image.open(io.BytesIO(data)).convert('RGBA')
        return np.array(im)[:, :, 3] > 0, im.size
    except Exception as e:                      # jar missing: fall back to the known footprint
        print('vanilla vex not found:', e)
        return None, (32, 32)


def void_wraith():
    cv = Canvas(32, 32)
    # ------------------------------------------------------------ head (hood)
    H = faces(0, 0, 5, 5, 5)
    fill_noise(cv, H['up'], [V[2], V[3], V[4], V[5]], 1)
    fill_noise(cv, H['down'], [V[0], V[1], V[2]], 2)
    for k in ('right', 'left', 'back'):
        fill_noise(cv, H[k], [V[1], V[2], V[3], V[4], V[5]], 3 + len(k))
    # hood rim highlight along the top edge of the side/back faces
    for k in ('right', 'left', 'back'):
        x0, y0, x1, y1 = H[k]
        for x in range(x0, x1):
            cv.put(x, y0, V[6] if (x % 2) else V[5])
    # face: a void under the hood, rimmed in violet, with burning magenta eyes
    x0, y0, x1, y1 = H['front']
    for y in range(y0, y1):
        for x in range(x0, x1):
            cv.put(x, y, V[0] if y > y0 else V[5])
    cv.put(x0, y0 + 1, V[4])
    cv.put(x1 - 1, y0 + 1, V[4])
    cv.put(x0, y0 + 2, V[3])
    cv.put(x1 - 1, y0 + 2, V[3])
    ey = y0 + 2
    for ex in (x0 + 1, x0 + 3):
        cv.put(ex, ey, '#ffd0f6')
        cv.put(ex, ey + 1, MAGENTA[3])
    cv.put(x0 + 2, ey + 1, '#2a0a2e')
    cv.put(x0 + 2, y1 - 1, MAGENTA[1])            # faint maw glow
    # top of the hood: a pointed crest line
    ux0, uy0, ux1, uy1 = H['up']
    for y in range(uy0, uy1):
        cv.put(ux0 + 2, y, V[6])
    # ------------------------------------------------------------ body (cloak)
    B = faces(0, 10, 3, 4, 2)
    fill_noise(cv, B['up'], [V[3], V[4], V[5]], 11)
    for k in ('right', 'front', 'left', 'back'):
        fill_noise(cv, B[k], [V[1], V[2], V[3], V[4]], 12 + len(k))
    fx0, fy0, fx1, fy1 = B['front']
    # magenta void sigil on the chest
    cv.put(fx0 + 1, fy0 + 1, MAGENTA[4])
    cv.put(fx0 + 1, fy0 + 2, MAGENTA[2])
    cv.put(fx0, fy0 + 1, MAGENTA[1])
    cv.put(fx0 + 2, fy0 + 1, MAGENTA[1])
    # collar highlight
    for k in ('right', 'front', 'left', 'back'):
        x0, y0, x1, y1 = B[k]
        for x in range(x0, x1):
            cv.put(x, y0, V[5])
    for (x, y) in ((1, 15), (4, 15), (5, 15), (9, 15)):           # ragged cloak hem, as vanilla
        cv.put(x, y, TRANSPARENT)
    # ------------------------------------------------------------ robe tail (translucent, tattered)
    R = faces(0, 16, 3, 5, 2)
    for k in ('right', 'front', 'left', 'back'):
        x0, y0, x1, y1 = R[k]
        r = rng(20 + len(k))
        for y in range(y0, y1):
            t = (y - y0) / (y1 - y0 - 1)
            a = int(215 - 105 * t)
            for x in range(x0, x1):
                if y == y1 - 1 and (x + len(k)) % 2 == 0:
                    continue                                   # ragged hem
                if y == y1 - 2 and (x * 3 + len(k)) % 5 == 0:
                    continue
                c = V[3] if r.random() < 0.6 else V[2]
                if (x + y) % 4 == 0 and t > 0.3:
                    c = SICK[1]
                cv.put(x, y, with_alpha(c, a))
    # ------------------------------------------------------------ arms (gaunt, clawed)
    for (u, v) in ((23, 0), (23, 6)):
        A = faces(u, v, 2, 4, 2)
        fill_noise(cv, A['up'], [V[3], V[4]], u + v)
        fill_noise(cv, A['down'], [MAGENTA[1], MAGENTA[2]], u + v + 1)
        for k in ('right', 'front', 'left', 'back'):
            x0, y0, x1, y1 = A[k]
            for y in range(y0, y1):
                for x in range(x0, x1):
                    c = V[4] if y == y0 else V[3] if y < y1 - 1 else '#c8a0e8'
                    if y == y1 - 1 and (x - x0) % 2 == 1:
                        c = MAGENTA[4]                         # glowing claw tips
                    cv.put(x, y, c)
            cv.put(x0, y0 + 1, V[5])
    # ------------------------------------------------------------ wings (tattered membrane)
    wing = [
        "AaabbccD",
        ".aMbbcMd",
        ".abbcc.d",
        "..b.c..d",
        "..b...d.",
    ]
    wpal = {'A': (MAGENTA[4], 240), 'a': (SICK[3], 225), 'b': (SICK[2], 210), 'c': (V[6], 195), 'd': (V[5], 180),
            'D': (V[4], 170), 'M': (MAGENTA[3], 225)}
    for j, row in enumerate(wing):
        for i, ch in enumerate(row):
            if ch in wpal:
                c, a = wpal[ch]
                cv.put(16 + i, 22 + j, with_alpha(c, a))
    return cv


def main():
    cv = void_wraith()
    vm, size = vanilla_mask()
    assert size == (32, 32), size
    if vm is not None:
        mine = cv.a[:, :, 3] > 0
        outside = mine & ~vm
        # wings/robe may be tattered within their face rects; nothing may sit outside the layout
        allowed = vm.copy()
        allowed[22:27, 16:24] = True
        allowed[18:23, 0:10] = True
        bad = mine & ~allowed
        print('pixels outside vanilla footprint:', int(outside.sum()), 'outside layout:', int(bad.sum()))
        assert not bad.any()
    cv.save('textures/entity/void_wraith.png')
    print(sheet([('void_wraith', cv.pil())], 'void_wraith.png', scale=16, bg=(90, 90, 90)))
    return cv


if __name__ == '__main__':
    main()
