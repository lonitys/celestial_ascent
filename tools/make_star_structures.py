"""Builds the Star Gate (outer End) and the three Celestial Sanctums (floating islands in the Fallen Stars)."""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nbt  # noqa: E402
import make_shrines  # noqa: E402
from make_shrines import Builder, dump  # noqa: E402

ROOT = os.path.join(HERE, '..', 'src', 'main', 'resources', 'data')
NS = 'celestialascent'


def write(b, size, path):
    bl = [(x, y, z, s) for (x, y, z), s in sorted(b.blocks.items())]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    nbt.write(path, nbt.structure((size, b.h, size), b.palette, bl))


def worldgen(name, pool_dir, biomes, start_height, project, spacing, separation, salt, adaptation='none'):
    s = {'type': 'minecraft:jigsaw', 'biomes': '#%s:has_structure/%s' % (NS, name), 'step': 'surface_structures',
         'spawn_overrides': {}, 'terrain_adaptation': adaptation, 'start_pool': '%s:%s/%s' % (NS, pool_dir, name), 'size': 1,
         'start_height': start_height, 'max_distance_from_center': 80, 'use_expansion_hack': False}
    if project:
        s['project_start_to_heightmap'] = project
    dump(os.path.join(ROOT, NS, 'worldgen', 'structure', name + '.json'), s)
    dump(os.path.join(ROOT, NS, 'worldgen', 'template_pool', pool_dir, name + '.json'), {
        'fallback': 'minecraft:empty', 'elements': [{'weight': 1, 'element': {
            'element_type': 'minecraft:single_pool_element', 'location': '%s:%s/%s' % (NS, pool_dir, name),
            'processors': 'minecraft:empty', 'projection': 'rigid'}}]})
    dump(os.path.join(ROOT, NS, 'worldgen', 'structure_set', name + '.json'), {
        'structures': [{'structure': '%s:%s' % (NS, name), 'weight': 1}],
        'placement': {'type': 'minecraft:random_spread', 'spacing': spacing, 'separation': separation, 'salt': salt}})
    dump(os.path.join(ROOT, NS, 'tags', 'worldgen', 'biome', 'has_structure', name + '.json'), {'values': biomes})
    dump(os.path.join(ROOT, NS, 'tags', 'worldgen', 'structure', name + '.json'), {'values': ['%s:%s' % (NS, name)]})


def star_gate():
    size, c = 25, 12
    make_shrines.SIZE = size
    rnd = random.Random(7)
    b = Builder(16)
    fy = 4
    for x in range(size):
        for z in range(size):
            r = math.hypot(x - c, z - c)
            if r > 12.4:
                continue
            for y in range(max(0, fy - 4 + int(max(0, r - 8))), fy):
                b.set(x, y, z, 'end_stone')
            if r > 11.4:
                fl = 'obsidian'
            elif int(r) % 4 == 0:
                fl = NS + ':starstone_bricks'
            else:
                fl = 'end_stone_bricks' if rnd.random() < 0.85 else 'purpur_block'
            b.set(x, fy, z, fl)
            for y in range(fy + 1, 16):
                b.set(x, y, z, 'air')
    # gate ring (5x5 border) with a 3x3 sealed centre that becomes the portal
    for x in range(c - 2, c + 3):
        for z in range(c - 2, c + 3):
            inner = abs(x - c) <= 1 and abs(z - c) <= 1
            b.set(x, fy, z, 'crying_obsidian' if inner else NS + ':star_gate_frame')
    for (x, z) in ((c - 2, c - 2), (c + 2, c - 2), (c - 2, c + 2), (c + 2, c + 2)):
        for y in range(fy + 1, fy + 5):
            b.set(x, y, z, NS + ':star_gate_frame')
        b.set(x, fy + 5, z, 'end_rod', facing='up')
    b.set(c, fy + 1, c + 5, NS + ':star_gate_pedestal', facing='north', head='false')
    for i in range(8):
        a = math.pi * 2 * i / 8
        x, z = round(c + math.cos(a) * 9), round(c + math.sin(a) * 9)
        h = rnd.randint(3, 6)
        for y in range(fy + 1, fy + 1 + h):
            b.set(x, y, z, 'purpur_pillar' if y % 2 else 'obsidian')
        b.set(x, fy + 1 + h, z, 'end_rod', facing='up')
    write(b, size, os.path.join(ROOT, NS, 'structure', 'stars', 'star_gate.nbt'))
    worldgen('star_gate', 'stars', ['minecraft:end_highlands', 'minecraft:end_midlands'], {'absolute': -fy}, 'WORLD_SURFACE_WG',
             26, 10, 715263001, adaptation='beard_thin')
    print('star gate', len(b.blocks))


def sanctum(name, altar, y_abs, theme, salt):
    size, c, R = 31, 15, 13
    make_shrines.SIZE = size
    rnd = random.Random(salt)
    depth = 14
    b = Builder(depth + 16)
    fy = depth
    for x in range(size):
        for z in range(size):
            r = math.hypot(x - c, z - c)
            if r > R + 0.5:
                continue
            # inverted cone underside with ragged edges
            bottom = fy - int((1 - r / (R + 1)) ** 0.7 * depth) - rnd.randint(0, 1)
            for y in range(max(0, bottom), fy):
                b.set(x, y, z, NS + (':stardust_ore' if rnd.random() < 0.03 else ':starstone'))
            if r > R - 1:
                fl = NS + ':starlit_starstone'
            elif int(r) % 5 == 0:
                fl = theme['ring']
            else:
                fl = NS + ':starstone_bricks' if rnd.random() < 0.8 else NS + ':starstone'
            b.set(x, fy, z, fl)
            for y in range(fy + 1, fy + 16):
                b.set(x, y, z, 'air')
    for i in range(6):
        a = math.pi * 2 * i / 6 + 0.3
        x, z = round(c + math.cos(a) * 10), round(c + math.sin(a) * 10)
        h = 3 + rnd.randint(0, 4)
        for y in range(fy + 1, fy + 1 + h):
            b.set(x, y, z, theme['pillar'])
        b.set(x, fy + 1 + h, z, NS + ':star_crystal', facing='up', waterlogged='false')
    for x in range(c - 2, c + 3):
        for z in range(c - 2, c + 3):
            b.set(x, fy + 1, z, theme['dais'])
    b.set(c, fy + 2, c, NS + ':' + altar, facing='north')
    for (x, z) in ((c - 2, c - 2), (c + 2, c - 2), (c - 2, c + 2), (c + 2, c + 2)):
        b.set(x, fy + 2, z, NS + ':star_crystal', facing='up', waterlogged='false')
    write(b, size, os.path.join(ROOT, NS, 'structure', 'stars', name + '.nbt'))
    worldgen(name, 'stars', ['%s:fallen_stars' % NS], {'absolute': y_abs - fy}, None, 18, 7, salt)
    print(name, len(b.blocks))


if __name__ == '__main__':
    star_gate()
    sanctum('seraph_sanctum', 'seraph_altar', 120, {'ring': 'white_stained_glass', 'pillar': 'quartz_pillar', 'dais': 'smooth_quartz'}, 715263101)
    sanctum('leviathan_sanctum', 'leviathan_altar', 140, {'ring': 'purple_stained_glass', 'pillar': 'purpur_pillar', 'dais': 'amethyst_block'}, 715263102)
    sanctum('herald_sanctum', 'herald_altar', 100, {'ring': 'orange_stained_glass', 'pillar': 'gold_block', 'dais': 'raw_gold_block'}, 715263103)
