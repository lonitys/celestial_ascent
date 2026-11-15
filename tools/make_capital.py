"""Builds the Ruined Capital of the Lost Ender Empire (outer End islands) and its worldgen JSON.

Layout (57x57): an end-stone island plaza with broken walls; three pylon plazas (Craft, Trade,
Throne) at radius 18; a central Throne Hall sealed by an Imperial Barrier until the Throne pylon is
restored. Inside the hall: the Empty Throne on a dais.
"""
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
import nbt  # noqa: E402
from make_shrines import Builder, dump  # noqa: E402
import make_shrines  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), '..', 'src', 'main', 'resources', 'data')
NS = 'celestialascent'
S = 57
C = 28
R = 27


def main():
    make_shrines.SIZE = S
    rnd = random.Random(1337)
    b = Builder(26)
    fy = 5

    def d(x, z):
        return math.hypot(x - C, z - C)

    # island + plaza floor + air clearance
    for x in range(S):
        for z in range(S):
            r = d(x, z)
            if r > R + 0.5:
                continue
            depth = int(5 - max(0, r - 18) / 2)
            for y in range(max(0, fy - depth), fy):
                b.set(x, y, z, 'end_stone')
            if r > R - 1:
                fl = 'obsidian'
            elif int(r) % 6 == 0:
                fl = 'purpur_block'
            elif (x + z) % 7 == 0:
                fl = 'purpur_pillar'
            else:
                fl = 'end_stone_bricks' if rnd.random() < 0.82 else 'end_stone'
            b.set(x, fy, z, fl)
            for y in range(fy + 1, 26):
                b.set(x, y, z, 'air')

    # broken perimeter wall
    for i in range(160):
        a = math.pi * 2 * i / 160
        x, z = round(C + math.cos(a) * (R - 1)), round(C + math.sin(a) * (R - 1))
        h = 0 if (i // 9) % 3 == 0 else rnd.randint(1, 5)
        for y in range(fy + 1, fy + 1 + h):
            b.set(x, y, z, 'purpur_block' if y % 3 else 'end_stone_bricks')
        if h >= 4 and i % 11 == 0:
            b.set(x, fy + 1 + h, z, 'end_rod', facing='up')

    # pylon plazas
    kinds = [('craft', 90), ('trade', 210), ('throne', 330)]
    for kind, deg in kinds:
        a = math.radians(deg)
        px, pz = round(C + math.cos(a) * 18), round(C + math.sin(a) * 18)
        for x in range(px - 3, px + 4):
            for z in range(pz - 3, pz + 4):
                edge = abs(x - px) == 3 or abs(z - pz) == 3
                b.set(x, fy + 1, z, 'purpur_block' if edge else 'obsidian')
        b.set(px, fy + 2, pz, NS + ':imperial_pylon', kind=kind, restored='false')
        for (cx, cz) in ((px - 3, pz - 3), (px + 3, pz - 3), (px - 3, pz + 3), (px + 3, pz + 3)):
            h = rnd.randint(2, 5)
            for y in range(fy + 2, fy + 2 + h):
                b.set(cx, y, cz, 'purpur_pillar')
            b.set(cx, fy + 2 + h, cz, 'end_rod', facing='up')
        if kind == 'trade':
            b.set(px + 2, fy + 2, pz - 2, NS + ':relic_pedestal', facing='north')

    # throne hall (15x15, walls 9 high), entrance facing south (+z)
    hx0, hx1, hz0, hz1 = C - 7, C + 7, C - 7, C + 7
    top = fy + 10
    for x in range(hx0, hx1 + 1):
        for z in range(hz0, hz1 + 1):
            wall = x in (hx0, hx1) or z in (hz0, hz1)
            b.set(x, fy, z, 'purpur_block' if (x + z) % 2 else 'obsidian')
            if wall:
                for y in range(fy + 1, top):
                    corner = x in (hx0, hx1) and z in (hz0, hz1)
                    if corner:
                        st = 'purpur_pillar'
                    elif y in (fy + 4, fy + 5) and (x - hx0) % 4 == 2 and z != hz1:
                        st = 'magenta_stained_glass'
                    elif rnd.random() < 0.06 and y > fy + 6:
                        st = 'air'  # ruined gaps
                    else:
                        st = 'purpur_block'
                    b.set(x, y, z, st)
            # roof with a ruined hole
            if d(x, z) > 3:
                b.set(x, top, z, 'purpur_slab', type='bottom')
    # entrance + barrier
    for x in range(C - 1, C + 2):
        for y in range(fy + 1, fy + 5):
            b.set(x, y, hz1, NS + ':imperial_barrier')
    # interior lighting and carpet path
    for z in range(hz0 + 2, hz1):
        b.set(C, fy + 1, z, 'magenta_carpet')
    for (x, z) in ((hx0 + 2, hz0 + 2), (hx1 - 2, hz0 + 2), (hx0 + 2, hz1 - 2), (hx1 - 2, hz1 - 2)):
        for y in range(fy + 1, fy + 4):
            b.set(x, y, z, 'purpur_pillar')
        b.set(x, fy + 4, z, 'end_rod', facing='up')
    # dais + throne at the north end
    for x in range(C - 2, C + 3):
        for z in range(hz0 + 1, hz0 + 4):
            b.set(x, fy + 1, z, 'obsidian')
    b.set(C, fy + 2, hz0 + 2, NS + ':empty_throne', facing='south')
    for x in (C - 2, C + 2):
        b.set(x, fy + 2, hz0 + 1, 'end_rod', facing='up')

    # scattered rubble and chorus
    for i in range(40):
        a = rnd.random() * math.pi * 2
        r = rnd.uniform(9, 25)
        x, z = round(C + math.cos(a) * r), round(C + math.sin(a) * r)
        if b.get(x, fy + 1, z) is not None and b.palette[b.get(x, fy + 1, z)]['Name'] == 'minecraft:air':
            b.set(x, fy + 1, z, rnd.choice(['purpur_stairs', 'end_stone_brick_slab', 'purpur_slab', 'chorus_flower']))

    path = os.path.join(ROOT, NS, 'structure', 'empire', 'ruined_capital.nbt')
    bl = [(x, y, z, s) for (x, y, z), s in sorted(b.blocks.items())]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    nbt.write(path, nbt.structure((S, b.h, S), b.palette, bl))

    dump(os.path.join(ROOT, NS, 'worldgen', 'structure', 'ruined_capital.json'), {
        'type': 'minecraft:jigsaw', 'biomes': '#%s:has_structure/ruined_capital' % NS, 'step': 'surface_structures',
        'spawn_overrides': {}, 'terrain_adaptation': 'beard_thin', 'start_pool': '%s:empire/capital' % NS, 'size': 1,
        'start_height': {'absolute': -fy}, 'project_start_to_heightmap': 'WORLD_SURFACE_WG',
        'max_distance_from_center': 80, 'use_expansion_hack': False})
    dump(os.path.join(ROOT, NS, 'worldgen', 'template_pool', 'empire', 'capital.json'), {
        'fallback': 'minecraft:empty', 'elements': [{'weight': 1, 'element': {
            'element_type': 'minecraft:single_pool_element', 'location': '%s:empire/ruined_capital' % NS,
            'processors': 'minecraft:empty', 'projection': 'rigid'}}]})
    dump(os.path.join(ROOT, NS, 'worldgen', 'structure_set', 'ruined_capital.json'), {
        'structures': [{'structure': '%s:ruined_capital' % NS, 'weight': 1}],
        'placement': {'type': 'minecraft:random_spread', 'spacing': 28, 'separation': 12, 'salt': 715262001}})
    dump(os.path.join(ROOT, NS, 'tags', 'worldgen', 'biome', 'has_structure', 'ruined_capital.json'),
         {'values': ['minecraft:end_highlands', 'minecraft:end_midlands']})
    dump(os.path.join(ROOT, NS, 'tags', 'worldgen', 'structure', 'ruined_capital.json'), {'values': ['%s:ruined_capital' % NS]})
    print('capital', len(b.blocks), 'blocks')


if __name__ == '__main__':
    main()
