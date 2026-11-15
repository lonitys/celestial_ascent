"""Village growth building templates and the Trade City structure."""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nbt  # noqa: E402
from make_shrines import dump  # noqa: E402

ROOT = os.path.join(HERE, '..', 'src', 'main', 'resources', 'data')
NS = 'celestialascent'


class B:
    """Sparse block builder with explicit size (positions outside stay structure void)."""

    def __init__(self, w, h, d):
        self.w, self.h, self.d = w, h, d
        self.blocks, self.palette, self.index, self.entities = {}, [], {}, []

    def st(self, name, **props):
        key = (name, tuple(sorted(props.items())))
        if key not in self.index:
            e = {'Name': name if ':' in name else 'minecraft:' + name}
            if props:
                e['Properties'] = {k: str(v).lower() for k, v in props.items()}
            self.index[key] = len(self.palette)
            self.palette.append(e)
        return self.index[key]

    def set(self, x, y, z, name, **props):
        if 0 <= x < self.w and 0 <= y < self.h and 0 <= z < self.d:
            self.blocks[(x, y, z)] = self.st(name, **props)

    def box(self, x0, y0, z0, x1, y1, z1, name, hollow=False, **props):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(z0, z1 + 1):
                    if hollow and x0 < x < x1 and z0 < z < z1 and y0 < y < y1:
                        continue
                    self.set(x, y, z, name, **props)

    def clear(self, x0, y0, z0, x1, y1, z1):
        self.box(x0, y0, z0, x1, y1, z1, 'air')

    def door(self, x, y, z, facing, wood='oak'):
        self.set(x, y, z, wood + '_door', facing=facing, half='lower', hinge='left', open='false', powered='false')
        self.set(x, y + 1, z, wood + '_door', facing=facing, half='upper', hinge='left', open='false', powered='false')

    def villager(self, x, y, z, profession, level=2):
        self.entities.append((x, y, z, {
            'id': 'minecraft:villager', 'PersistenceRequired': nbt.Byte(1), 'Xp': 10 * level,
            'VillagerData': {'level': level, 'profession': profession, 'type': 'minecraft:plains'}}))

    def write(self, path):
        bl = [(x, y, z, s) for (x, y, z), s in sorted(self.blocks.items())]
        os.makedirs(os.path.dirname(path), exist_ok=True)
        nbt.write(path, nbt.structure((self.w, self.h, self.d), self.palette, bl, entities=self.entities))


# ---- village additions (origin = ground level; y=0 is the foundation layer) -----------------------
def market_stall(ox=0, oz=0, b=None):
    b = b or B(5, 6, 5)
    b.clear(ox, 1, oz, ox + 4, 5, oz + 4)
    b.box(ox, 0, oz, ox + 4, 0, oz + 4, 'spruce_planks')
    for (x, z) in ((0, 0), (4, 0), (0, 4), (4, 4)):
        b.box(ox + x, 1, oz + z, ox + x, 3, oz + z, 'spruce_fence')
    for x in range(5):
        for z in range(5):
            b.set(ox + x, 4, oz + z, 'red_wool' if (x + z) % 2 == 0 else 'white_wool')
    b.set(ox + 2, 1, oz + 1, NS + ':shop_stall', facing='south')
    b.set(ox + 1, 1, oz + 1, 'barrel', facing='up', open='false')
    b.set(ox + 3, 1, oz + 1, 'composter', level='0')
    b.set(ox + 2, 3, oz + 2, 'lantern', hanging='true', waterlogged='false')
    return b


def lamp_post():
    b = B(3, 6, 3)
    b.clear(0, 1, 0, 2, 5, 2)
    b.box(0, 0, 0, 2, 0, 2, 'cobblestone')
    b.box(1, 1, 1, 1, 3, 1, 'spruce_fence')
    b.set(1, 4, 1, 'spruce_planks')
    for (dx, dz, f) in ((0, 1, 'west'), (2, 1, 'east')):
        b.set(dx, 4, dz, 'spruce_trapdoor', facing=f, half='top', open='false', powered='false', waterlogged='false')
    b.set(1, 5, 1, 'lantern', hanging='false', waterlogged='false')
    return b


def cottage(ox=0, oz=0, b=None, wood='oak'):
    b = b or B(7, 8, 7)
    b.clear(ox, 1, oz, ox + 6, 7, oz + 6)
    b.box(ox, 0, oz, ox + 6, 0, oz + 6, 'cobblestone')
    b.box(ox, 1, oz, ox + 6, 3, oz + 6, wood + '_planks', hollow=True)
    for (x, z) in ((0, 0), (6, 0), (0, 6), (6, 6)):
        b.box(ox + x, 1, oz + z, ox + x, 3, oz + z, wood + '_log', axis='y')
    for (x, z) in ((0, 3), (6, 3), (3, 6)):
        b.set(ox + x, 2, oz + z, 'glass_pane')
    b.door(ox + 3, 1, oz, 'north', wood)
    for i in range(4):
        y = 4 + i
        if i == 3:
            b.box(ox + 3, y, oz - 0, ox + 3, y, oz + 6, wood + '_planks')
            continue
        b.box(ox + i, y, oz, ox + i, y, oz + 6, 'stone_brick_stairs', facing='east', half='bottom', shape='straight', waterlogged='false')
        b.box(ox + 6 - i, y, oz, ox + 6 - i, y, oz + 6, 'stone_brick_stairs', facing='west', half='bottom', shape='straight', waterlogged='false')
        b.box(ox + i + 1, y, oz, ox + 5 - i, y, oz, wood + '_planks')
        b.box(ox + i + 1, y, oz + 6, ox + 5 - i, y, oz + 6, wood + '_planks')
    b.set(ox + 1, 1, oz + 5, 'white_bed', facing='south', part='head', occupied='false')
    b.set(ox + 1, 1, oz + 4, 'white_bed', facing='south', part='foot', occupied='false')
    b.set(ox + 5, 1, oz + 5, 'crafting_table')
    b.set(ox + 5, 1, oz + 1, 'barrel', facing='up', open='false')
    b.set(ox + 3, 3, oz + 3, 'lantern', hanging='true', waterlogged='false')
    return b


def bank_kiosk():
    b = B(5, 6, 5)
    b.clear(0, 1, 0, 4, 5, 4)
    b.box(0, 0, 0, 4, 0, 4, 'stone_bricks')
    for (x, z) in ((0, 0), (4, 0), (0, 4), (4, 4)):
        b.box(x, 1, z, x, 3, z, 'stone_brick_wall', up='true', north='none', south='none', east='none', west='none', waterlogged='false')
    b.box(0, 4, 0, 4, 4, 4, 'dark_oak_slab', type='bottom', waterlogged='false')
    b.set(2, 4, 2, 'gold_block')
    b.set(2, 1, 2, NS + ':bank_counter', facing='north')
    b.set(2, 3, 2, 'lantern', hanging='true', waterlogged='false')
    return b


def garden():
    b = B(7, 3, 5)
    b.clear(0, 1, 0, 6, 2, 4)
    b.box(0, 0, 0, 6, 0, 4, 'oak_log', axis='x')
    for x in range(1, 6):
        for z in range(1, 4):
            if (x, z) == (3, 2):
                b.set(x, 0, z, 'water')
                continue
            b.set(x, 0, z, 'farmland', moisture='7')
            b.set(x, 1, z, ['wheat', 'carrots', 'potatoes', 'beetroots'][(x + z) % 4], age='3' if (x + z) % 4 == 3 else '7')
    return b


def fountain():
    b = B(5, 5, 5)
    b.clear(0, 1, 0, 4, 4, 4)
    b.box(0, 0, 0, 4, 0, 4, 'stone_bricks')
    b.box(0, 1, 0, 4, 1, 4, 'stone_brick_wall', up='true', north='none', south='none', east='none', west='none', waterlogged='false')
    b.box(1, 1, 1, 3, 1, 3, 'water')
    b.box(2, 1, 2, 2, 3, 2, 'chiseled_stone_bricks')
    b.set(2, 4, 2, 'water')
    return b


def watchtower():
    b = B(5, 11, 5)
    b.clear(0, 1, 0, 4, 10, 4)
    b.box(0, 0, 0, 4, 0, 4, 'cobblestone')
    for (x, z) in ((0, 0), (4, 0), (0, 4), (4, 4)):
        b.box(x, 1, z, x, 7, z, 'spruce_log', axis='y')
    b.box(2, 1, 1, 2, 7, 1, 'ladder', facing='south', waterlogged='false')
    b.box(0, 8, 0, 4, 8, 4, 'spruce_planks')
    b.set(2, 8, 1, 'spruce_trapdoor', facing='south', half='top', open='false', powered='false', waterlogged='false')
    for x in range(5):
        for z in range(5):
            if x in (0, 4) or z in (0, 4):
                b.set(x, 9, z, 'spruce_fence')
    b.set(2, 9, 2, 'lantern', hanging='false', waterlogged='false')
    return b


def smithy():
    b = B(7, 7, 6)
    b.clear(0, 1, 0, 6, 6, 5)
    b.box(0, 0, 0, 6, 0, 5, 'stone_bricks')
    b.box(0, 1, 4, 6, 3, 5, 'cobblestone')
    b.box(0, 1, 0, 0, 3, 5, 'cobblestone')
    b.box(0, 4, 0, 6, 4, 5, 'spruce_slab', type='bottom', waterlogged='false')
    for (x, z) in ((6, 0), (3, 0)):
        b.box(x, 1, z, x, 3, z, 'spruce_fence')
    b.set(3, 1, 2, NS + ':titan_anvil', facing='north')
    b.set(1, 1, 3, 'blast_furnace', facing='east', lit='false')
    b.set(5, 1, 3, 'smithing_table')
    b.box(1, 1, 5, 1, 6, 5, 'bricks')
    b.set(1, 1, 1, 'lava_cauldron')
    return b


# ---- trade city ---------------------------------------------------------------------------------
def trade_city():
    S = 47
    c = S // 2
    rnd = random.Random(99)
    b = B(S, 16, S)
    b.clear(0, 1, 0, S - 1, 15, S - 1)
    for x in range(S):
        for z in range(S):
            b.set(x, 0, z, 'dirt_path' if (abs(x - c) <= 1 or abs(z - c) <= 1) else ('stone_bricks' if math.hypot(x - c, z - c) < 7 else 'grass_block'))
    # walls with four gates
    for i in range(S):
        for (x, z) in ((i, 0), (i, S - 1), (0, i), (S - 1, i)):
            gate = abs(i - c) <= 1
            if gate:
                continue
            b.box(x, 1, z, x, 3, z, 'stone_bricks')
            if i % 2 == 0:
                b.set(x, 4, z, 'stone_brick_wall', up='true', north='none', south='none', east='none', west='none', waterlogged='false')
    for (x, z) in ((0, 0), (S - 1, 0), (0, S - 1), (S - 1, S - 1)):
        b.box(x, 1, z, x, 6, z, 'chiseled_stone_bricks')
        b.set(x, 7, z, 'lantern', hanging='false', waterlogged='false')
    # central plaza fountain
    for x in range(c - 2, c + 3):
        for z in range(c - 2, c + 3):
            edge = abs(x - c) == 2 or abs(z - c) == 2
            b.set(x, 1, z, 'stone_brick_wall' if edge else 'water', **({'up': 'true', 'north': 'none', 'south': 'none', 'east': 'none', 'west': 'none',
                                                                       'waterlogged': 'false'} if edge else {}))
    b.box(c, 1, c, c, 3, c, 'chiseled_stone_bricks')
    b.set(c, 4, c, 'gold_block')
    b.set(c + 3, 1, c + 3, NS + ':quest_board', facing='north')
    b.set(c - 3, 1, c - 3, NS + ':quest_board', facing='south')
    # bank (north-east quadrant)
    bx, bz = c + 4, 4
    b.box(bx, 0, bz, bx + 10, 0, bz + 8, 'polished_andesite')
    b.box(bx, 1, bz, bx + 10, 5, bz + 8, 'stone_bricks', hollow=True)
    b.box(bx, 6, bz, bx + 10, 6, bz + 8, 'dark_oak_planks')
    b.box(bx + 4, 1, bz + 8, bx + 6, 3, bz + 8, 'air')
    for x in (bx + 2, bx + 8):
        b.set(x, 1, bz + 3, NS + ':bank_counter', facing='south')
        b.set(x, 3, bz + 3, 'gold_block')
    for x in range(bx + 1, bx + 10, 3):
        b.set(x, 3, bz, 'glass_pane')
        b.set(x, 5, bz + 4, 'lantern', hanging='true', waterlogged='false')
    b.villager(bx + 3, 1, bz + 5, NS + ':banker', 2)
    b.villager(bx + 7, 1, bz + 5, NS + ':banker', 3)
    # market rows (south)
    for i in range(3):
        market_stall(4 + i * 6, c + 4, b)
        market_stall(4 + i * 6, c + 12, b)
    # relic pavilion (north-west)
    px, pz = 5, 5
    b.box(px, 0, pz, px + 8, 0, pz + 8, 'purpur_block')
    for (x, z) in ((px, pz), (px + 8, pz), (px, pz + 8), (px + 8, pz + 8)):
        b.box(x, 1, z, x, 4, z, 'purpur_pillar', axis='y')
    b.box(px, 5, pz, px + 8, 5, pz + 8, 'purpur_slab', type='bottom', waterlogged='false')
    b.set(px + 4, 1, pz + 4, NS + ':relic_pedestal', facing='south')
    b.set(px + 4, 4, pz + 4, 'end_rod', facing='down')
    b.villager(px + 4, 1, pz + 6, NS + ':relic_dealer', 3)
    # smithy (south-east) and cottages
    sm = smithy()
    for (x, y, z), s in sm.blocks.items():
        e = sm.palette[s]
        b.set(c + 6 + x, y, c + 6 + z, e['Name'], **e.get('Properties', {}))
    b.villager(c + 9, 1, c + 9, NS + ':titansmith', 2)
    cottage(c + 15, c + 6, b, 'spruce')
    cottage(c + 15, c + 15, b, 'oak')
    cottage(c + 6, c + 15, b, 'birch')
    # lamp posts along the roads
    for k in (6, 14, 32, 40):
        for (x, z) in ((k, c + 3), (c - 3, k)):
            b.box(x, 1, z, x, 3, z, 'spruce_fence')
            b.set(x, 4, z, 'lantern', hanging='false', waterlogged='false')
    b.villager(c, 1, c + 6, 'minecraft:none', 1)
    b.villager(c + 6, 1, c, 'minecraft:none', 1)
    return b


def main():
    parts = {'market_stall': market_stall(), 'lamp_post': lamp_post(), 'cottage': cottage(), 'bank_kiosk': bank_kiosk(),
             'garden': garden(), 'fountain': fountain(), 'watchtower': watchtower(), 'smithy': smithy()}
    for name, b in parts.items():
        b.write(os.path.join(ROOT, NS, 'structure', 'village', name + '.nbt'))
    city = trade_city()
    city.write(os.path.join(ROOT, NS, 'structure', 'city', 'trade_city.nbt'))
    dump(os.path.join(ROOT, NS, 'worldgen', 'structure', 'trade_city.json'), {
        'type': 'minecraft:jigsaw', 'biomes': '#%s:has_structure/trade_city' % NS, 'step': 'surface_structures',
        'spawn_overrides': {}, 'terrain_adaptation': 'beard_box', 'start_pool': '%s:city/trade_city' % NS, 'size': 1,
        'start_height': {'absolute': 0}, 'project_start_to_heightmap': 'WORLD_SURFACE_WG',
        'max_distance_from_center': 80, 'use_expansion_hack': False})
    dump(os.path.join(ROOT, NS, 'worldgen', 'template_pool', 'city', 'trade_city.json'), {
        'fallback': 'minecraft:empty', 'elements': [{'weight': 1, 'element': {
            'element_type': 'minecraft:single_pool_element', 'location': '%s:city/trade_city' % NS,
            'processors': 'minecraft:empty', 'projection': 'rigid'}}]})
    dump(os.path.join(ROOT, NS, 'worldgen', 'structure_set', 'trade_city.json'), {
        'structures': [{'structure': '%s:trade_city' % NS, 'weight': 1}],
        'placement': {'type': 'minecraft:random_spread', 'spacing': 44, 'separation': 18, 'salt': 715264001}})
    dump(os.path.join(ROOT, NS, 'tags', 'worldgen', 'biome', 'has_structure', 'trade_city.json'), {'values': [
        'minecraft:plains', 'minecraft:sunflower_plains', 'minecraft:savanna', 'minecraft:desert', 'minecraft:taiga',
        'minecraft:meadow', 'minecraft:snowy_plains']})
    dump(os.path.join(ROOT, NS, 'tags', 'worldgen', 'structure', 'trade_city.json'), {'values': ['%s:trade_city' % NS]})
    print('village parts', len(parts), 'city blocks', len(city.blocks), 'villagers', len(city.entities))


if __name__ == '__main__':
    main()
