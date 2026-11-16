"""Custom boss bar sprites (textures/gui/boss_bar.png, 256x64), drawn by client/BossBarOverlay.

  frame   206x14 at (0,0)   dark body, gold trim, diamond end caps; the fill sits at (3,3), 200x8
  fill    200x8  at (0,16)  greyscale with a highlight, tinted with the boss colour at runtime
  chip    200x8  at (0,24)  white, the recently lost health (drawn translucent)
  gems    11x11  at (0,34) empty, (12,34) lit (greyscale, tinted), (24,34) shine overlay
  notch   3x10   at (36,34) stage threshold marker
"""
from common import *

OUT = '#07060c'
GOLD_HI = '#F2D27A'
GOLD = '#C9A54C'
GOLD_SH = '#7A5C22'
BODY = '#16121f'
BODY_HI = '#241d33'


def frame(cv):
    w, h = 206, 14
    # end caps: small diamonds at the left and right
    for cx in (2, w - 3):
        for dy in range(-3, 4):
            half = 3 - abs(dy)
            for dx in range(-half, half + 1):
                cv.put(cx + dx, 7 + dy, GOLD if abs(dx) + abs(dy) < 3 else GOLD_SH)
        cv.put(cx, 5, GOLD_HI)
    # body
    cv.rect(2, 1, w - 3, h - 2, OUT)
    cv.rect(3, 2, w - 4, h - 3, BODY)
    cv.hline(3, w - 4, 2, BODY_HI)
    # gold trim around the fill area
    cv.hline(3, w - 4, 1, GOLD_HI)
    cv.hline(3, w - 4, h - 2, GOLD_SH)
    cv.vline(2, 2, h - 3, GOLD)
    cv.vline(w - 3, 2, h - 3, GOLD_SH)
    # inner well where the fill goes
    cv.rect(3, 3, 202, 10, '#0a0810')
    # tick marks every 10%
    for i in range(1, 10):
        x = 3 + i * 20
        cv.put(x, 1, GOLD_SH)
        cv.put(x, h - 2, GOLD)


def fill(cv, oy):
    ramp_v = [235, 255, 225, 205, 190, 175, 160, 140]
    for y in range(8):
        for x in range(200):
            v = ramp_v[y] - (12 if (x // 2 + y) % 7 == 0 else 0)
            cv.put(x, oy + y, (v, v, v, 255))


def chip(cv, oy):
    for y in range(8):
        for x in range(200):
            cv.put(x, oy + y, (255, 255, 255, 255))


def gem(cv, ox, oy, mode):
    rows = [
        ".....#.....",
        "....#a#....",
        "...#aab#...",
        "..#aabbb#..",
        ".#aabbbbc#.",
        "#aabbbbbcc#",
        ".#bbbbbcc#.",
        "..#bbbcc#..",
        "...#bcc#...",
        "....#c#....",
        ".....#.....",
    ]
    if mode == 'empty':
        pal = {'#': GOLD_SH, 'a': '#3a3348', 'b': '#241e30', 'c': '#16121f'}
    elif mode == 'lit':
        pal = {'#': GOLD, 'a': (255, 255, 255, 255), 'b': (200, 200, 200, 255), 'c': (130, 130, 130, 255)}
    else:  # shine
        pal = {'a': (255, 255, 255, 200)}
    cv.grid(rows, pal, ox, oy)


def notch(cv, ox, oy):
    cv.vline(ox + 1, oy, oy + 9, OUT)
    cv.put(ox, oy, GOLD_HI)
    cv.put(ox + 1, oy, GOLD_HI)
    cv.put(ox + 2, oy, GOLD_HI)
    cv.put(ox, oy + 9, GOLD_SH)
    cv.put(ox + 2, oy + 9, GOLD_SH)


def main():
    cv = Canvas(256, 64)
    frame(cv)
    fill(cv, 16)
    chip(cv, 24)
    gem(cv, 0, 34, 'empty')
    gem(cv, 12, 34, 'lit')
    gem(cv, 24, 34, 'shine')
    notch(cv, 36, 34)
    print(cv.save('textures/gui/boss_bar.png'))
    cv.pil().resize((1024, 256), Image.NEAREST).save(os.path.join(PREVIEW, 'boss_bar.png'))


if __name__ == '__main__':
    main()
