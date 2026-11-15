"""Builds the four Titan shrine structures (NBT) and their worldgen JSON.

Each shrine is a circular arena (radius 15) with a patterned floor, ruined pillars, decorations and the
element altar in the centre. Air inside the arena clears terrain; positions outside are structure void.
"""
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
import nbt  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), '..', 'src', 'main', 'resources', 'data')
NS = 'celestialascent'
SIZE = 33
C = 16          # centre
R = 15          # arena radius


class Builder:
    def __init__(self, height):
        self.h = height
        self.blocks = {}
        self.palette = []
        self.index = {}

    def state(self, name, **props):
        key = (name, tuple(sorted(props.items())))
        if key not in self.index:
            e = {'Name': name if ':' in name else 'minecraft:' + name}
            if props:
                e['Properties'] = {k: str(v).lower() for k, v in props.items()}
            self.index[key] = len(self.palette)
            self.palette.append(e)
        return self.index[key]

    def set(self, x, y, z, name, **props):
        if 0 <= x < SIZE and 0 <= y < self.h and 0 <= z < SIZE:
            self.blocks[(x, y, z)] = self.state(name, **props)

    def get(self, x, y, z):
        return self.blocks.get((x, y, z))

    def write(self, path):
        bl = [(x, y, z, s) for (x, y, z), s in sorted(self.blocks.items())]
        os.makedirs(os.path.dirname(path), exist_ok=True)
        nbt.write(path, nbt.structure((SIZE, self.h, SIZE), self.palette, bl))


def dist(x, z):
    return math.hypot(x - C, z - C)


def arena(b, floor_y, clear_to, floor_fn, rim, foundation, depth=3):
    """Floor disk with foundation below and air above."""
    for x in range(SIZE):
        for z in range(SIZE):
            d = dist(x, z)
            if d > R + 0.5:
                continue
            for y in range(max(0, floor_y - depth), floor_y):
                b.set(x, y, z, foundation)
            b.set(x, floor_y, z, rim if d > R - 1 else floor_fn(x, z, d))
            for y in range(floor_y + 1, clear_to):
                b.set(x, y, z, 'air')


def pillars(b, floor_y, n, radius, height_fn, body, cap, base, rnd):
    out = []
    for i in range(n):
        a = math.pi * 2 * i / n + math.pi / n
        px, pz = round(C + math.cos(a) * radius), round(C + math.sin(a) * radius)
        h = height_fn(i, rnd)
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                b.set(px + dx, floor_y + 1, pz + dz, base)
        for y in range(floor_y + 2, floor_y + 2 + h):
            b.set(px, y, pz, body(i, y))
        b.set(px, floor_y + 2 + h, pz, cap)
        out.append((px, floor_y + 2 + h, pz, h))
    return out


def dais(b, floor_y, step, top, altar):
    for x in range(C - 3, C + 4):
        for z in range(C - 3, C + 4):
            b.set(x, floor_y + 1, z, step)
    for x in range(C - 2, C + 3):
        for z in range(C - 2, C + 3):
            b.set(x, floor_y + 2, z, top)
    b.set(C, floor_y + 3, C, NS + ':' + altar, facing='north')


# ---------------------------------------------------------------------------------------------
def frost():
    rnd = random.Random(11)
    b = Builder(18)
    fy = 3

    def floor(x, z, d):
        if int(d) % 5 == 0:
            return 'blue_ice'
        if (x + z) % 2 == 0 and d < 6:
            return 'polished_diorite'
        return 'packed_ice' if rnd.random() < 0.8 else 'snow_block'

    arena(b, fy, 18, floor, 'polished_deepslate', 'packed_ice')
    pil = pillars(b, fy, 8, 12, lambda i, r: 5 + r.randint(0, 4) if i % 3 else 3 + r.randint(0, 1),
                  lambda i, y: 'packed_ice' if y % 3 else 'blue_ice', 'blue_ice', 'deepslate_tiles', rnd)
    for (px, top, pz, h) in pil:
        b.set(px, top + 1, pz, 'soul_lantern')
        for k in range(1, 3):
            b.set(px, top - k, pz + 1 if k % 2 else pz - 1, 'ice')
    for i in range(14):
        a = rnd.random() * math.pi * 2
        r = rnd.uniform(5, 13)
        x, z = round(C + math.cos(a) * r), round(C + math.sin(a) * r)
        if b.get(x, fy + 1, z) is None or b.palette[b.get(x, fy + 1, z)]['Name'] == 'minecraft:air':
            for y in range(fy + 1, fy + 1 + rnd.randint(1, 3)):
                b.set(x, y, z, 'ice')
    dais(b, fy, 'deepslate_tile_stairs' if False else 'polished_deepslate', 'blue_ice', 'frost_altar')
    for (x, z) in ((C - 2, C - 2), (C + 2, C - 2), (C - 2, C + 2), (C + 2, C + 2)):
        b.set(x, fy + 3, z, 'soul_lantern')
    return b, fy


def tide():
    rnd = random.Random(22)
    depth = 10
    b = Builder(18 + depth)
    fy = depth

    def floor(x, z, d):
        if int(d) in (4, 9):
            return 'dark_prismarine'
        if int(d) == 13:
            return 'sea_lantern' if (x * 7 + z * 3) % 5 == 0 else 'prismarine_bricks'
        return 'prismarine_bricks' if rnd.random() < 0.75 else 'prismarine'

    arena(b, fy, fy + 15, floor, 'dark_prismarine', 'prismarine', depth=2)
    # support legs into the sea
    for i in range(12):
        a = math.pi * 2 * i / 12
        px, pz = round(C + math.cos(a) * 13), round(C + math.sin(a) * 13)
        for y in range(0, fy - 1):
            b.set(px, y, pz, 'prismarine_bricks' if y % 4 else 'dark_prismarine')
    for (x, z) in ((C, C), (C - 6, C), (C + 6, C), (C, C - 6), (C, C + 6)):
        for y in range(0, fy - 1):
            b.set(x, y, z, 'dark_prismarine')
    pil = pillars(b, fy, 8, 12, lambda i, r: 4 + r.randint(0, 4),
                  lambda i, y: 'prismarine' if y % 4 else 'dark_prismarine', 'sea_lantern', 'prismarine_bricks', rnd)
    for (px, top, pz, h) in pil:
        b.set(px, top + 1, pz, 'conduit') if rnd.random() < 0.25 else b.set(px, top + 1, pz, 'lantern')
    dais(b, fy, 'dark_prismarine', 'prismarine_bricks', 'tide_altar')
    for (x, z) in ((C - 3, C), (C + 3, C), (C, C - 3), (C, C + 3)):
        b.set(x, fy + 2, z, 'sea_lantern')
    return b, fy


def storm():
    rnd = random.Random(33)
    b = Builder(20)
    fy = 3

    def floor(x, z, d):
        ang = math.atan2(z - C, x - C)
        if int((ang + math.pi) / (math.pi / 4)) % 2 == 0 and 3 < d < 12:
            return 'deepslate_tiles'
        if int(d) == 12:
            return 'waxed_oxidized_cut_copper'
        return 'calcite' if rnd.random() < 0.85 else 'smooth_basalt'

    arena(b, fy, 20, floor, 'polished_deepslate', 'calcite')
    pil = pillars(b, fy, 8, 12, lambda i, r: 7 + r.randint(0, 4),
                  lambda i, y: 'calcite' if y % 3 else 'waxed_oxidized_copper', 'waxed_oxidized_chiseled_copper', 'polished_deepslate', rnd)
    for (px, top, pz, h) in pil:
        b.set(px, top + 1, pz, 'lightning_rod')
        b.set(px + 1, top - 2, pz, 'amethyst_cluster', facing='east')
        b.set(px - 1, top - 3, pz, 'amethyst_cluster', facing='west')
    for i in range(10):
        a = rnd.random() * math.pi * 2
        r = rnd.uniform(5, 12)
        x, z = round(C + math.cos(a) * r), round(C + math.sin(a) * r)
        b.set(x, fy + 1, z, 'amethyst_block')
        b.set(x, fy + 2, z, 'large_amethyst_bud', facing='up')
    dais(b, fy, 'polished_deepslate', 'calcite', 'storm_altar')
    for (x, z) in ((C - 2, C - 2), (C + 2, C - 2), (C - 2, C + 2), (C + 2, C + 2)):
        b.set(x, fy + 3, z, 'lightning_rod')
    return b, fy


def magma():
    rnd = random.Random(44)
    b = Builder(18)
    fy = 3

    def floor(x, z, d):
        if int(d) % 4 == 0 and d > 2:
            return 'magma_block'
        if (x % 4 == 0 or z % 4 == 0) and d < 11:
            return 'gilded_blackstone' if rnd.random() < 0.1 else 'polished_blackstone'
        return 'polished_blackstone_bricks' if rnd.random() < 0.85 else 'cracked_polished_blackstone_bricks'

    arena(b, fy, 18, floor, 'blackstone', 'basalt', depth=4)
    pil = pillars(b, fy, 8, 12, lambda i, r: 5 + r.randint(0, 4),
                  lambda i, y: 'basalt' if y % 3 else 'crying_obsidian', 'polished_basalt', 'polished_blackstone', rnd)
    for (px, top, pz, h) in pil:
        b.set(px, top + 1, pz, 'lava_cauldron')
        b.set(px, top - 1, pz + 1, 'shroomlight')
    dais(b, fy, 'polished_blackstone', 'gilded_blackstone', 'magma_altar')
    for (x, z) in ((C - 2, C - 2), (C + 2, C - 2), (C - 2, C + 2), (C + 2, C + 2)):
        b.set(x, fy + 3, z, 'lava_cauldron')
    return b, fy


SHRINES = {
    'frost': (frost, ['minecraft:frozen_peaks', 'minecraft:ice_spikes', 'minecraft:snowy_slopes', 'minecraft:snowy_plains', 'minecraft:grove'],
              'surface', 715261001),
    'tide': (tide, ['minecraft:deep_ocean', 'minecraft:deep_cold_ocean', 'minecraft:deep_lukewarm_ocean', 'minecraft:ocean',
                    'minecraft:lukewarm_ocean', 'minecraft:warm_ocean'], 'sea', 715261002),
    'storm': (storm, ['minecraft:jagged_peaks', 'minecraft:stony_peaks', 'minecraft:windswept_hills', 'minecraft:windswept_gravelly_hills',
                      'minecraft:windswept_savanna', 'minecraft:meadow'], 'surface', 715261003),
    'magma': (magma, ['minecraft:basalt_deltas', 'minecraft:nether_wastes'], 'nether', 715261004),
}


def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=2)


def main():
    for key, (fn, biomes, mode, salt) in SHRINES.items():
        b, fy = fn()
        b.write(os.path.join(ROOT, NS, 'structure', 'shrines', key + '_shrine.nbt'))
        structure = {
            'type': 'minecraft:jigsaw',
            'biomes': '#%s:has_structure/%s_shrine' % (NS, key),
            'step': 'surface_structures',
            'spawn_overrides': {},
            'terrain_adaptation': 'beard_thin',
            'start_pool': '%s:shrines/%s' % (NS, key),
            'size': 1,
            'max_distance_from_center': 80,
            'use_expansion_hack': False,
        }
        if mode == 'nether':
            structure['start_height'] = {'absolute': 32 - fy}
        elif mode == 'sea':
            structure['start_height'] = {'absolute': -fy + 1}
            structure['project_start_to_heightmap'] = 'WORLD_SURFACE_WG'
        else:
            structure['start_height'] = {'absolute': -fy}
            structure['project_start_to_heightmap'] = 'WORLD_SURFACE_WG'
        dump(os.path.join(ROOT, NS, 'worldgen', 'structure', key + '_shrine.json'), structure)
        dump(os.path.join(ROOT, NS, 'worldgen', 'template_pool', 'shrines', key + '.json'), {
            'fallback': 'minecraft:empty',
            'elements': [{'weight': 1, 'element': {'element_type': 'minecraft:single_pool_element',
                                                   'location': '%s:shrines/%s_shrine' % (NS, key),
                                                   'processors': 'minecraft:empty', 'projection': 'rigid'}}]})
        dump(os.path.join(ROOT, NS, 'worldgen', 'structure_set', key + '_shrine.json'), {
            'structures': [{'structure': '%s:%s_shrine' % (NS, key), 'weight': 1}],
            'placement': {'type': 'minecraft:random_spread', 'spacing': 34, 'separation': 14, 'salt': salt}})
        dump(os.path.join(ROOT, NS, 'tags', 'worldgen', 'biome', 'has_structure', key + '_shrine.json'), {'values': biomes})
        dump(os.path.join(ROOT, NS, 'tags', 'worldgen', 'structure', key + '_shrine.json'), {'values': ['%s:%s_shrine' % (NS, key)]})
        print('shrine', key, len(b.blocks), 'blocks')
    dump(os.path.join(ROOT, 'minecraft', 'tags', 'point_of_interest_type', 'acquirable_job_site.json'),
         {'replace': False, 'values': ['%s:banker' % NS, '%s:titansmith' % NS, '%s:relic_dealer' % NS]})


if __name__ == '__main__':
    main()
