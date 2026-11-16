"""The trade city: a walled core, terrain-following roads and outskirts, in five biome styles.

Templates are authored once with logical block names ('@wall', '@plank_stairs', ...). Each biome
variant maps them to real blocks, then connections (fences, walls, panes) are computed and the
templates are written to data/celestialascent/structure/city/<variant>/.

Conventions: x = east, z = south, y = up. Buildings are authored facing NORTH (their front is the
z = 0 side, usually a porch row) and stamped into the core with quarter turns. Every template's
y = 0 is its ground layer; the core's ground layer is y = G (it has a foundation skirt below).

Run: python tools/make_city.py
"""
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

# ------------------------------------------------------------------------------------------------ palettes
WOOD = {'plains': 'oak', 'desert': 'birch', 'savanna': 'acacia', 'taiga': 'spruce', 'snowy': 'spruce'}


def stone_set(full, stairs, slab, wall=None):
    return {'': full, '_stairs': stairs, '_slab': slab, '_wall': wall}


VARIANTS = {
    'plains': dict(
        wall=stone_set('stone_bricks', 'stone_brick_stairs', 'stone_brick_slab', 'stone_brick_wall'),
        trim=stone_set('polished_andesite', 'polished_andesite_stairs', 'polished_andesite_slab', 'andesite_wall'),
        roof=stone_set('spruce_planks', 'spruce_stairs', 'spruce_slab'),
        wood='oak', log='oak_log', path='dirt_path', path2='cobblestone', ground='grass_block', leaves='oak_leaves',
        villager='plains', crops=['wheat', 'carrots'], flowers=['poppy', 'dandelion', 'cornflower', 'azure_bluet', 'oxeye_daisy'],
        bed='blue', awnings=['red', 'yellow', 'blue', 'lime', 'orange', 'light_blue', 'magenta', 'white'], dirt='dirt'),
    'desert': dict(
        wall=stone_set('sandstone', 'sandstone_stairs', 'sandstone_slab', 'sandstone_wall'),
        trim=stone_set('smooth_sandstone', 'smooth_sandstone_stairs', 'smooth_sandstone_slab', 'sandstone_wall'),
        roof=stone_set('cut_sandstone', 'smooth_sandstone_stairs', 'smooth_sandstone_slab'),
        wood='birch', log='birch_log', path='smooth_sandstone', path2='sand', ground='sand', leaves='jungle_leaves',
        villager='desert', crops=['wheat', 'beetroots'], flowers=['dead_bush'],
        bed='cyan', awnings=['cyan', 'yellow', 'red', 'light_blue', 'orange', 'white', 'magenta', 'lime'], dirt='sandstone'),
    'savanna': dict(
        wall=stone_set('mud_bricks', 'mud_brick_stairs', 'mud_brick_slab', 'mud_brick_wall'),
        trim=stone_set('smooth_sandstone', 'smooth_sandstone_stairs', 'smooth_sandstone_slab', 'sandstone_wall'),
        roof=stone_set('dark_oak_planks', 'dark_oak_stairs', 'dark_oak_slab'),
        wood='acacia', log='acacia_log', path='coarse_dirt', path2='dirt_path', ground='grass_block', leaves='acacia_leaves',
        villager='savanna', crops=['wheat', 'beetroots'], flowers=['dandelion', 'allium', 'poppy'],
        bed='orange', awnings=['orange', 'yellow', 'red', 'brown', 'lime', 'light_blue', 'white', 'magenta'], dirt='dirt'),
    'taiga': dict(
        wall=stone_set('cobblestone', 'cobblestone_stairs', 'cobblestone_slab', 'cobblestone_wall'),
        trim=stone_set('mossy_stone_bricks', 'mossy_stone_brick_stairs', 'mossy_stone_brick_slab', 'mossy_stone_brick_wall'),
        roof=stone_set('dark_oak_planks', 'dark_oak_stairs', 'dark_oak_slab'),
        wood='spruce', log='spruce_log', path='dirt_path', path2='coarse_dirt', ground='grass_block', leaves='spruce_leaves',
        villager='taiga', crops=['potatoes', 'carrots'], flowers=['fern', 'lily_of_the_valley', 'cornflower'],
        bed='green', awnings=['green', 'red', 'brown', 'white', 'lime', 'light_blue', 'yellow', 'orange'], dirt='dirt'),
    'snowy': dict(
        wall=stone_set('stone_bricks', 'stone_brick_stairs', 'stone_brick_slab', 'stone_brick_wall'),
        trim=stone_set('polished_diorite', 'polished_diorite_stairs', 'polished_diorite_slab', 'diorite_wall'),
        roof=stone_set('deepslate_tiles', 'deepslate_tile_stairs', 'deepslate_tile_slab'),
        wood='spruce', log='stripped_spruce_log', path='stone_bricks', path2='gravel', ground='snow_block', leaves='spruce_leaves',
        villager='snow', crops=['potatoes', 'beetroots'], flowers=[],
        bed='light_blue', awnings=['light_blue', 'red', 'blue', 'white', 'cyan', 'yellow', 'lime', 'magenta'], dirt='dirt'),
}

BIOMES = {
    'plains': ['minecraft:plains', 'minecraft:sunflower_plains', 'minecraft:meadow'],
    'desert': ['minecraft:desert'],
    'savanna': ['minecraft:savanna', 'minecraft:savanna_plateau'],
    'taiga': ['minecraft:taiga', 'minecraft:old_growth_pine_taiga', 'minecraft:old_growth_spruce_taiga'],
    'snowy': ['minecraft:snowy_plains', 'minecraft:snowy_taiga'],
}
STRUCTURE_ID = {'plains': 'trade_city', 'desert': 'trade_city_desert', 'savanna': 'trade_city_savanna',
                'taiga': 'trade_city_taiga', 'snowy': 'trade_city_snowy'}


def resolve(name, v):
    """Logical block name -> real block id for variant v (real names pass through)."""
    if not name.startswith('@'):
        return name if ':' in name else 'minecraft:' + name
    p = VARIANTS[v]
    key = name[1:]
    w = p['wood']
    table = {
        'plank': w + '_planks', 'plank_stairs': w + '_stairs', 'plank_slab': w + '_slab', 'fence': w + '_fence',
        'fence_gate': w + '_fence_gate', 'door': w + '_door', 'trapdoor': w + '_trapdoor', 'log': p['log'],
        'stripped_log': 'stripped_' + p['log'].replace('stripped_', ''), 'pressure_plate': w + '_pressure_plate',
        'path': p['path'], 'path2': p['path2'], 'ground': p['ground'], 'leaves': p['leaves'], 'dirt': p['dirt'],
        'bed': p['bed'] + '_bed', 'banner': 'blue_wall_banner',
    }
    for fam in ('wall', 'trim', 'roof'):
        for suf, real in p[fam].items():
            table[fam + suf] = real or p['wall']['_wall']
    if key.startswith('wool_'):
        return 'minecraft:' + key[5:] + '_wool'
    if key.startswith('carpet_'):
        return 'minecraft:' + key[7:] + '_carpet'
    return 'minecraft:' + table[key]


# ------------------------------------------------------------------------------------------------ template builder
H4 = ('north', 'east', 'south', 'west')
CW = {'north': 'east', 'east': 'south', 'south': 'west', 'west': 'north', 'up': 'up', 'down': 'down'}


def rot_facing(f, r):
    for _ in range(r % 4):
        f = CW[f]
    return f


class Tpl:
    def __init__(self, w, h, d):
        self.w, self.h, self.d = w, h, d
        self.blocks = {}      # (x, y, z) -> (name, props dict, nbt or None)
        self.entities = []    # (x, y, z, nbt)

    # -- basic edits
    def set(self, x, y, z, name, nbt_=None, **props):
        if 0 <= x < self.w and 0 <= y < self.h and 0 <= z < self.d:
            self.blocks[(x, y, z)] = (name, {k: str(v).lower() for k, v in props.items()}, nbt_)

    def get(self, x, y, z):
        b = self.blocks.get((x, y, z))
        return b[0] if b else None

    def box(self, x0, y0, z0, x1, y1, z1, name, **props):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    self.set(x, y, z, name, **props)

    def walls(self, x0, y0, z0, x1, y1, z1, name, **props):
        """Hollow box sides (no top or bottom)."""
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, z0, name, **props)
                self.set(x, y, z1, name, **props)
            for z in range(z0, z1 + 1):
                self.set(x0, y, z, name, **props)
                self.set(x1, y, z, name, **props)

    def air(self, x0, y0, z0, x1, y1, z1):
        self.box(x0, y0, z0, x1, y1, z1, 'air')

    # -- common blocks
    def stairs(self, x, y, z, name, facing, half='bottom'):
        self.set(x, y, z, name, facing=facing, half=half, shape='straight', waterlogged='false')

    def slab(self, x, y, z, name, kind='bottom'):
        self.set(x, y, z, name, type=kind, waterlogged='false')

    def log(self, x, y, z, name='@log', axis='y'):
        self.set(x, y, z, name, axis=axis)

    def door(self, x, y, z, facing, name='@door', hinge='left'):
        self.set(x, y, z, name, facing=facing, half='lower', hinge=hinge, open='false', powered='false')
        self.set(x, y + 1, z, name, facing=facing, half='upper', hinge=hinge, open='false', powered='false')

    def lantern(self, x, y, z, hanging=False, soul=False):
        self.set(x, y, z, 'soul_lantern' if soul else 'lantern', hanging=hanging, waterlogged='false')

    def leaves(self, x, y, z, name='@leaves'):
        if self.get(x, y, z) in (None, 'air'):
            self.set(x, y, z, name, distance=1, persistent='true', waterlogged='false')

    def bed(self, x, y, z, facing, color='@bed'):
        """facing = direction from foot to head."""
        dx, dz = {'north': (0, -1), 'south': (0, 1), 'east': (1, 0), 'west': (-1, 0)}[facing]
        self.set(x, y, z, color, facing=facing, part='foot', occupied='false')
        self.set(x + dx, y, z + dz, color, facing=facing, part='head', occupied='false')

    def chest(self, x, y, z, facing):
        self.set(x, y, z, 'chest', facing=facing, type='single', waterlogged='false')

    def mod(self, x, y, z, name, facing):
        self.set(x, y, z, NS + ':' + name, facing=facing)

    def villager(self, x, y, z, profession, level=2, vtype='@villager'):
        self.entities.append((x, y, z, {
            'id': 'minecraft:villager', 'PersistenceRequired': nbt.Byte(1), 'Xp': 10 * level,
            'VillagerData': {'level': level, 'profession': profession, 'type': vtype}}))

    def mob(self, x, y, z, eid, **extra):
        tag = {'id': eid, 'PersistenceRequired': nbt.Byte(1)}
        tag.update(extra)
        self.entities.append((x, y, z, tag))

    def jigsaw(self, x, y, z, facing, name, target, pool, final):
        self.set(x, y, z, 'jigsaw', nbt_={
            'id': 'minecraft:jigsaw', 'name': NS + ':' + name, 'target': NS + ':' + target if target != 'empty' else 'minecraft:empty',
            'pool': pool, 'final_state': final, 'joint': 'aligned', 'placement_priority': 0, 'selection_priority': 0},
            orientation=facing + '_up')

    # -- stamping a sub-template with a quarter turn (clockwise), keeping existing blocks under its void
    def stamp(self, sub, ox, oy, oz, r=0, keep_jigsaws=False):
        for (x, y, z), (name, props, tag) in sub.blocks.items():
            if name == 'jigsaw' and not keep_jigsaws:
                fs = tag['final_state']
                name, props, tag = ('air' if fs == 'minecraft:air' else fs), {}, None
            nx, nz = rot_xz(x, z, sub.w, sub.d, r)
            p = dict(props)
            if 'facing' in p:
                p['facing'] = rot_facing(p['facing'], r)
            if 'axis' in p and r % 2 == 1 and p['axis'] in ('x', 'z'):
                p['axis'] = 'z' if p['axis'] == 'x' else 'x'
            if name == 'jigsaw':
                p = dict(props)
                f, up = p['orientation'].split('_')
                p['orientation'] = rot_facing(f, r) + '_' + up
            self.blocks[(ox + nx, oy + y, oz + nz)] = (name, p, tag)
        for (x, y, z, tag) in sub.entities:
            nx, nz = rot_xz(x, z, sub.w, sub.d, r)
            self.entities.append((ox + nx, oy + y, oz + nz, tag))

    def footprint(self, r):
        return (self.d, self.w) if r % 2 else (self.w, self.d)


def rot_xz(x, z, w, d, r):
    for _ in range(r % 4):
        x, z, w, d = d - 1 - z, x, d, w
    return x, z


# ------------------------------------------------------------------------------------------------ resolve + connect + write
NON_FULL = ('stairs', 'slab', 'fence', '_wall', 'pane', 'iron_bars', 'door', 'trapdoor', ':air', 'water', 'lava', 'lantern',
            'torch', 'leaves', 'poppy', 'dandelion', 'cornflower', 'bluet', 'daisy', 'allium', 'lily', 'short_grass', 'fern',
            'bush', '_bed', 'chest', 'carpet', 'banner', 'rod', 'chain', 'campfire', 'cluster', 'anvil', 'bell', 'ladder',
            'potted', 'wheat', 'carrots', 'potatoes', 'beetroots', 'farmland', 'dirt_path', 'jigsaw', 'button', 'plate',
            'sign', 'brewing', 'cauldron', 'grindstone', 'lectern', 'composter', 'stonecutter', 'candle',
            'celestialascent:', 'sugar_cane', 'cactus', 'pickle', 'kelp', 'vine', 'stem', 'gate', 'target', 'pumpkin', 'melon')


def is_full(real):
    if real is None or real == 'minecraft:snow':
        return False
    return not any(k in real for k in NON_FULL)


def kind(real):
    if real is None:
        return None
    if real.endswith('_fence') or real.endswith('nether_brick_fence'):
        return 'fence'
    if real.endswith('_fence_gate'):
        return 'gate'
    if real.endswith('_wall') and 'banner' not in real and 'sign' not in real and 'torch' not in real:
        return 'wall'
    if real.endswith('_pane') or real.endswith('iron_bars'):
        return 'pane'
    return None


OFFS = {'north': (0, -1), 'south': (0, 1), 'east': (1, 0), 'west': (-1, 0)}


def connect(real_blocks):
    """Fill fence/wall/pane connection properties from neighbours (jigsaw pieces skip shape updates)."""
    for (x, y, z), (real, props, tag) in list(real_blocks.items()):
        k = kind(real)
        if k not in ('fence', 'wall', 'pane'):
            continue
        n = {}
        for d, (dx, dz) in OFFS.items():
            other = real_blocks.get((x + dx, y, z + dz))
            o = other[0] if other else None
            ok = kind(o)
            if k == 'fence':
                c = ok in ('fence', 'gate') or (is_full(o) and ok is None)
                c = c and not (ok == 'fence' and ('nether' in o) != ('nether' in real))
            elif k == 'wall':
                c = ok in ('wall', 'pane', 'gate') or (is_full(o) and ok is None)
            else:
                c = ok in ('pane', 'wall') or (is_full(o) and ok is None)
            n[d] = c
        if k == 'wall':
            above = real_blocks.get((x, y + 1, z))
            straight = (n['north'] and n['south'] and not n['east'] and not n['west']) or \
                       (n['east'] and n['west'] and not n['north'] and not n['south'])
            props = dict(props)
            for d in H4:
                props[d] = 'low' if n[d] else 'none'
            props['up'] = 'false' if straight and not (above and above[0] not in ('minecraft:air',)) else 'true'
            props['waterlogged'] = 'false'
        else:
            props = dict(props)
            for d in H4:
                props[d] = 'true' if n[d] else 'false'
            props['waterlogged'] = 'false'
        real_blocks[(x, y, z)] = (real, props, tag)


def write(tpl, rel, v):
    real = {}
    for pos, (name, props, tag) in tpl.blocks.items():
        r = resolve(name, v)
        if tag and 'final_state' in tag:
            tag = dict(tag)
            fs = tag['final_state']
            tag['final_state'] = resolve(fs, v) if fs.startswith('@') else fs
            tag['pool'] = tag['pool'].replace('{v}', v)
        if r.endswith('_log') or r.endswith('_wood') or 'pillar' in r or r.endswith('hay_block') or r.endswith('basalt'):
            props = dict(props)
            props.setdefault('axis', 'y')
        if r.endswith('snow_block') and False:
            pass
        real[pos] = (r, props, tag)
    connect(real)
    palette, index, bl = [], {}, []
    for (x, y, z), (r, props, tag) in sorted(real.items(), key=lambda kv: (kv[0][1], kv[0][2], kv[0][0])):
        key = (r, tuple(sorted(props.items())))
        if key not in index:
            e = {'Name': r}
            if props:
                e['Properties'] = dict(props)
            index[key] = len(palette)
            palette.append(e)
        bl.append((x, y, z, index[key], tag))
    ents = []
    for (x, y, z, tag) in tpl.entities:
        t = dict(tag)
        if 'VillagerData' in t:
            vd = dict(t['VillagerData'])
            if vd['type'] == '@villager':
                vd['type'] = 'minecraft:' + VARIANTS[v]['villager']
            t['VillagerData'] = vd
        ents.append((x, y, z, t))
    path = os.path.join(ROOT, NS, 'structure', 'city', v, rel + '.nbt')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    nbt.write(path, nbt.structure((tpl.w, tpl.h, tpl.d), palette, bl, entities=ents))
    return len(bl)


# ================================================================================================ buildings
def flowerpot(t, x, y, z, rnd):
    t.set(x, y, z, rnd.choice(['potted_poppy', 'potted_dandelion', 'potted_cornflower', 'potted_azure_bluet', 'potted_fern',
                               'potted_red_tulip', 'potted_allium']))


def window(t, x, y, z, tall=2, glass='glass_pane'):
    for k in range(tall):
        t.set(x, y + k, z, glass)


def gable_roof_x(t, x0, x1, z0, z1, y0, ridge_cap=True, overhang=1, mat='@roof'):
    """Pitched roof with the ridge along x, covering z0..z1 (eaves overhang included in the range)."""
    depth = z1 - z0 + 1
    layers = (depth + 1) // 2
    for k in range(layers):
        y = y0 + k
        za, zb = z0 + k, z1 - k
        for x in range(x0, x1 + 1):
            if za < zb:
                t.stairs(x, y, za, mat + '_stairs', 'south')
                t.stairs(x, y, zb, mat + '_stairs', 'north')
            elif za == zb:
                t.slab(x, y, za, mat + '_slab') if ridge_cap else t.set(x, y, za, mat)
        # gable ends: fill below the slope with wall/plank
    return y0 + layers


def gable_fill_x(t, x, z0, z1, y0, mat):
    depth = z1 - z0 + 1
    for k in range((depth + 1) // 2):
        for z in range(z0 + k + 1, z1 - k):
            t.set(x, y0 + k, z, mat)


def gable_roof_z(t, z0, z1, x0, x1, y0, mat='@roof'):
    width = x1 - x0 + 1
    layers = (width + 1) // 2
    for k in range(layers):
        y = y0 + k
        xa, xb = x0 + k, x1 - k
        for z in range(z0, z1 + 1):
            if xa < xb:
                t.stairs(xa, y, z, mat + '_stairs', 'east')
                t.stairs(xb, y, z, mat + '_stairs', 'west')
            elif xa == xb:
                t.slab(xa, y, z, mat + '_slab')
    return y0 + layers


def gable_fill_z(t, z, x0, x1, y0, mat):
    width = x1 - x0 + 1
    for k in range((width + 1) // 2):
        for x in range(x0 + k + 1, x1 - k):
            t.set(x, y0 + k, z, mat)


def house_a(seed):
    """Two-storey house, half-timbered, gable roof along z. 7 wide, 11 deep (z0 porch)."""
    rnd = random.Random(seed)
    t = Tpl(9, 16, 12)
    X0, X1, Z0, Z1 = 1, 7, 2, 10
    t.air(0, 1, 0, 8, 15, 11)
    t.box(0, 0, 0, 8, 0, 11, '@ground')
    t.box(X0, 0, Z0, X1, 0, Z1, '@trim')
    t.box(X0 + 1, 0, Z0 + 1, X1 - 1, 0, Z1 - 1, '@plank')
    # ground floor stone, upper floor timber
    t.walls(X0, 1, Z0, X1, 3, Z1, '@wall')
    t.walls(X0, 4, Z0, X1, 4, Z1, '@log', axis='x')
    for z in (Z0, Z1):
        for x in range(X0, X1 + 1):
            t.log(x, 4, z, axis='x')
    for x in (X0, X1):
        for z in range(Z0 + 1, Z1):
            t.log(x, 4, z, axis='z')
    t.walls(X0, 5, Z0, X1, 6, Z1, '@plank')
    for (x, z) in ((X0, Z0), (X1, Z0), (X0, Z1), (X1, Z1)):
        t.box(x, 1, z, x, 6, z, '@log')
    t.box(X0 + 1, 4, Z0 + 1, X1 - 1, 4, Z1 - 1, '@plank')
    # roof (gable along z), overhanging one block on the sides and ends
    top = gable_roof_z(t, Z0 - 1, Z1 + 1, X0 - 1, X1 + 1, 7)
    for z in (Z0, Z1):
        gable_fill_z(t, z, X0 - 1, X1 + 1, 7, '@plank')
    # door, porch, path
    t.door(4, 1, Z0, 'north')
    t.slab(3, 3, Z0 - 1, '@plank_slab', 'top')
    t.slab(4, 3, Z0 - 1, '@plank_slab', 'top')
    t.slab(5, 3, Z0 - 1, '@plank_slab', 'top')
    t.lantern(3, 2, Z0 - 1, hanging=True)
    t.box(4, 0, 0, 4, 0, Z0 - 1, '@path')
    t.jigsaw(4, 1, 0, 'north', 'building', 'lot', 'minecraft:empty', 'minecraft:air')
    # windows
    for z in (5, 8):
        window(t, X0, 2, z, 1)
        window(t, X1, 2, z, 1)
        window(t, X0, 5, z, 1)
        window(t, X1, 5, z, 1)
    window(t, 2, 2, Z0, 1)
    window(t, 6, 2, Z0, 1)
    window(t, 3, 5, Z0, 2)
    window(t, 5, 5, Z0, 2)
    window(t, 4, 5, Z1, 2)
    for x in (2, 6):
        t.set(x, 1, Z0 - 1, '@trapdoor', facing='north', half='top', open='false', powered='false', waterlogged='false')
        flowerpot(t, x, 2, Z0 - 1, rnd) if False else None
    # interior: kitchen + table below, bed and chest above, ladder
    t.set(2, 1, 9, 'furnace', facing='east', lit='false')
    t.set(2, 1, 8, 'crafting_table')
    t.set(6, 1, 9, 'barrel', facing='up', open='false')
    t.set(6, 1, 8, 'bookshelf')
    t.set(6, 2, 8, 'bookshelf')
    t.set(4, 1, 6, '@fence')
    t.set(4, 2, 6, '@pressure_plate', powered='false')
    t.stairs(3, 1, 6, '@plank_stairs', 'east')
    t.stairs(5, 1, 6, '@plank_stairs', 'west')
    for y in range(1, 5):
        t.set(6, y, 3, 'ladder', facing='south', waterlogged='false')
    t.air(6, 4, 3, 6, 4, 3)
    t.set(6, 4, 3, 'ladder', facing='south', waterlogged='false')
    t.bed(3, 5, 8, 'south')
    t.bed(5, 5, 8, 'south')
    t.chest(2, 5, 4, 'east')
    flowerpot(t, 4, 5, 9, rnd)
    t.lantern(4, 3, 6, hanging=True)
    t.lantern(4, 7, 6, hanging=True)
    # chimney
    t.box(X1 - 1, 7, Z1, X1 - 1, top + 1, Z1, 'bricks')
    t.set(X1 - 1, top + 2, Z1, 'campfire', facing='north', lit='true', signal_fire='false', waterlogged='false')
    return t


def house_b(seed):
    """Wide house, gable along x, with a side garden and balcony. 9 wide, 10 deep (z0 porch)."""
    rnd = random.Random(seed)
    t = Tpl(11, 13, 11)
    X0, X1, Z0, Z1 = 1, 9, 2, 8
    t.air(0, 1, 0, 10, 12, 10)
    t.box(0, 0, 0, 10, 0, 10, '@ground')
    t.box(X0, 0, Z0, X1, 0, Z1, '@trim')
    t.box(X0 + 1, 0, Z0 + 1, X1 - 1, 0, Z1 - 1, '@plank')
    t.walls(X0, 1, Z0, X1, 4, Z1, '@plank')
    for (x, z) in ((X0, Z0), (X1, Z0), (X0, Z1), (X1, Z1), (5, Z0), (5, Z1)):
        t.box(x, 1, z, x, 4, z, '@log')
    t.walls(X0, 1, Z0, X1, 1, Z1, '@wall')
    t.door(5, 1, Z0, 'north')
    t.air(5, 3, Z0, 5, 3, Z0)
    t.set(5, 3, Z0, '@log', axis='y')
    top = gable_roof_x(t, X0 - 1, X1 + 1, Z0 - 1, Z1 + 1, 5)
    for x in (X0, X1):
        gable_fill_x(t, x, Z0 - 1, Z1 + 1, 5, '@plank')
    for x in (2, 3, 7, 8):
        window(t, x, 2, Z0, 2)
        window(t, x, 2, Z1, 2)
    window(t, X0, 2, 5, 2)
    window(t, X1, 2, 5, 2)
    # porch roof + lanterns
    for x in range(3, 8):
        t.slab(x, 4, Z0 - 1, '@plank_slab', 'top')
    t.set(3, 1, Z0 - 1, '@fence')
    t.set(3, 2, Z0 - 1, '@fence')
    t.set(3, 3, Z0 - 1, '@fence')
    t.set(7, 1, Z0 - 1, '@fence')
    t.set(7, 2, Z0 - 1, '@fence')
    t.set(7, 3, Z0 - 1, '@fence')
    t.lantern(5, 3, Z0 - 1, hanging=True)
    t.box(5, 0, 0, 5, 0, Z0 - 1, '@path')
    t.jigsaw(5, 1, 0, 'north', 'building', 'lot', 'minecraft:empty', 'minecraft:air')
    # interior
    t.bed(2, 1, 6, 'south')
    t.bed(8, 1, 6, 'south')
    t.chest(2, 1, 3, 'south')
    t.set(8, 1, 3, 'crafting_table')
    t.set(7, 1, 7, 'smoker', facing='north', lit='false')
    t.set(4, 1, 7, 'bookshelf')
    t.set(6, 1, 7, 'bookshelf')
    t.set(5, 1, 6, '@fence')
    t.set(5, 2, 6, '@pressure_plate', powered='false')
    t.lantern(5, 4, 5, hanging=True)
    flowerpot(t, 4, 2, 7, rnd)
    flowerpot(t, 6, 2, 7, rnd)
    # side flower boxes
    for x in (2, 3, 7, 8):
        t.set(x, 1, Z0 - 1, '@trapdoor', facing='north', half='top', open='false', powered='false', waterlogged='false') if x not in (3, 7) else None
    t.box(X1 - 1, 5, Z1, X1 - 1, top + 1, Z1, 'bricks')
    t.set(X1 - 1, top + 2, Z1, 'campfire', facing='north', lit='true', signal_fire='false', waterlogged='false')
    return t


def bank():
    """Quartz bank with a columned portico, pediment, counters and a vault. 15 wide, 15 deep."""
    t = Tpl(15, 15, 15)
    t.air(0, 1, 0, 14, 14, 14)
    t.box(0, 0, 0, 14, 0, 14, '@trim')
    # raised floor and front steps
    t.box(0, 1, 2, 14, 1, 14, 'quartz_bricks')
    for x in range(3, 12):
        t.stairs(x, 1, 1, 'quartz_stairs', 'south')
    t.box(1, 1, 2, 13, 1, 4, 'smooth_quartz')
    # portico columns
    for x in (1, 4, 10, 13):
        t.set(x, 2, 2, 'chiseled_quartz_block')
        t.box(x, 3, 2, x, 7, 2, 'quartz_pillar', axis='y')
    t.box(0, 8, 1, 14, 8, 4, 'smooth_quartz')
    for x in range(0, 15):
        t.set(x, 8, 1, 'gold_block' if x % 4 == 1 else 'quartz_bricks')
    # pediment
    for k in range(4):
        for x in range(k, 15 - k):
            if x in (k, 14 - k):
                t.stairs(x, 9 + k, 1, 'quartz_stairs', 'east' if x == k else 'west')
            else:
                t.set(x, 9 + k, 1, 'smooth_quartz')
    t.set(7, 10, 1, 'lapis_block')
    t.set(7, 11, 1, 'gold_block')
    # main hall walls
    t.walls(0, 2, 5, 14, 8, 14, '@wall')
    t.box(0, 2, 5, 14, 2, 14, '@trim')
    t.walls(0, 2, 5, 14, 2, 14, '@trim')
    t.air(1, 2, 6, 13, 8, 13)
    t.box(1, 1, 6, 13, 1, 13, 'smooth_quartz')
    for x in range(1, 14):
        for z in range(6, 14):
            if (x + z) % 4 == 0:
                t.set(x, 1, z, 'lapis_block' if (x * z) % 3 == 0 else 'quartz_bricks')
    t.set(7, 1, 9, 'gold_block')
    # front wall (z 5) in quartz with a three-wide arched entry
    t.box(0, 2, 5, 14, 8, 5, 'quartz_bricks')
    t.air(6, 2, 5, 8, 4, 5)
    t.stairs(6, 5, 5, 'quartz_stairs', 'east', 'top')
    t.stairs(8, 5, 5, 'quartz_stairs', 'west', 'top')
    for x in (2, 12):
        window(t, x, 4, 5, 2, 'light_blue_stained_glass_pane')
    for z in (7, 10, 13):
        window(t, 0, 4, z, 3, 'light_blue_stained_glass_pane')
        window(t, 14, 4, z, 3, 'light_blue_stained_glass_pane')
    # roof: hip of roof stairs over the hall plus a gold-trimmed cornice
    for x in range(0, 15):
        t.set(x, 8, 14, '@trim')
    t.box(0, 9, 5, 14, 9, 14, '@trim_slab', type='bottom', waterlogged='false')
    for k in range(4):
        for x in range(k, 15 - k):
            for z in range(5 + k, 15 - k):
                edge = x in (k, 14 - k) or z in (5 + k, 14 - k)
                if edge:
                    if z == 5 + k:
                        t.stairs(x, 10 + k, z, '@roof_stairs', 'south')
                    elif z == 14 - k:
                        t.stairs(x, 10 + k, z, '@roof_stairs', 'north')
                    elif x == k:
                        t.stairs(x, 10 + k, z, '@roof_stairs', 'east')
                    else:
                        t.stairs(x, 10 + k, z, '@roof_stairs', 'west')
    t.box(4, 13, 9, 10, 13, 10, '@roof')
    t.box(4, 14, 9, 10, 14, 10, '@roof_slab', type='bottom', waterlogged='false')
    # counters, bankers, vault
    t.mod(4, 2, 9, 'bank_counter', 'north')
    t.mod(10, 2, 9, 'bank_counter', 'north')
    for x in (3, 5, 9, 11):
        t.set(x, 2, 9, '@trim_slab', type='top', waterlogged='false')
    t.villager(4, 2, 10, NS + ':banker', 2)
    t.villager(10, 2, 10, NS + ':banker', 3)
    t.box(1, 2, 11, 13, 4, 11, 'iron_bars')
    t.air(7, 2, 11, 7, 3, 11)
    t.set(7, 2, 11, 'iron_door', facing='north', half='lower', hinge='left', open='false', powered='false')
    t.set(7, 3, 11, 'iron_door', facing='north', half='upper', hinge='left', open='false', powered='false')
    for x in (2, 3, 4, 10, 11, 12):
        t.set(x, 2, 13, 'gold_block')
    for x in (2, 3, 11, 12):
        t.set(x, 3, 13, 'gold_block')
    t.set(5, 2, 13, 'chest', facing='north', type='single', waterlogged='false')
    t.set(9, 2, 13, 'chest', facing='north', type='single', waterlogged='false')
    t.box(6, 2, 13, 8, 2, 13, 'raw_gold_block')
    # chandeliers
    for x in (4, 10):
        t.set(x, 8, 8, 'chain', axis='y', waterlogged='false')
        t.set(x, 7, 8, 'chain', axis='y', waterlogged='false')
        t.lantern(x, 6, 8, hanging=True)
    t.lantern(7, 7, 3, hanging=True)
    return t


def market_hall(awnings):
    """Covered market with 8 rentable shop stalls under coloured awnings. 25 wide, 11 deep."""
    t = Tpl(25, 13, 11)
    t.air(0, 1, 0, 24, 12, 10)
    t.box(0, 0, 0, 24, 0, 10, '@trim')
    t.box(1, 0, 4, 23, 0, 6, '@path')
    for x in range(0, 25, 3):
        t.set(x, 0, 5, 'chiseled_quartz_block' if x % 6 == 0 else '@path2')
    # columns and beams
    for x in (0, 6, 12, 18, 24):
        for z in (0, 10):
            t.box(x, 1, z, x, 5, z, '@log')
    for x in range(0, 25):
        for z in (0, 10):
            if x % 6:
                t.log(x, 5, z, axis='x')
    for z in range(1, 10):
        for x in (0, 24):
            t.log(x, 5, z, axis='z')
    gable_roof_x(t, 0, 24, -1 + 1, 10, 6)
    for x in (0, 24):
        gable_fill_x(t, x, 0, 10, 6, '@plank')
    # stalls: north row faces south, south row faces north
    xs = (3, 9, 15, 21)
    i = 0
    for row_z, facing, back in ((2, 'south', 1), (8, 'north', 9)):
        for x in xs:
            c = awnings[i % len(awnings)]
            i += 1
            t.mod(x, 1, row_z, 'shop_stall', facing)
            t.set(x - 1, 1, row_z, 'barrel', facing='up', open='false')
            t.set(x + 1, 1, back, 'barrel', facing='up', open='false')
            t.slab(x + 1, 1, row_z, '@plank_slab', 'top')
            for dx in (-1, 0, 1):
                t.set(x + dx, 4, back, '@wool_' + c)
                t.set(x + dx, 4, row_z, '@carpet_' + c) if False else None
                t.set(x + dx, 3, row_z if False else back, '@wool_' + c) if dx == 0 and False else None
            t.set(x - 1, 3, back, '@fence')
            t.set(x + 1, 3, back, '@fence')
            t.set(x - 1, 2, back, '@fence')
            t.set(x + 1, 2, back, '@fence')
    for x in (3, 9, 15, 21):
        t.box(x, 6, 5, x, 10, 5, 'chain', axis='y', waterlogged='false')
        t.lantern(x, 5, 5, hanging=True)
    return t


def relic_pavilion():
    """Open purpur pavilion with the relic pedestal and amethyst. 11 x 11."""
    t = Tpl(11, 11, 11)
    t.air(0, 1, 0, 10, 10, 10)
    t.box(0, 0, 0, 10, 0, 10, 'end_stone_bricks')
    t.box(1, 1, 1, 9, 1, 9, 'purpur_block')
    t.walls(1, 1, 1, 9, 1, 9, 'end_stone_bricks')
    for x in range(3, 8):
        t.stairs(x, 1, 0, 'purpur_stairs', 'south')
    for (x, z) in ((1, 1), (9, 1), (1, 9), (9, 9), (5, 1), (1, 5), (9, 5), (5, 9)):
        if (x, z) in ((5, 1),):
            continue
        t.box(x, 2, z, x, 6, z, 'purpur_pillar', axis='y')
    # dome
    t.box(1, 7, 1, 9, 7, 9, 'purpur_block')
    t.walls(0, 7, 0, 10, 7, 10, 'purpur_slab', type='bottom', waterlogged='false')
    t.box(2, 8, 2, 8, 8, 8, 'purpur_block')
    t.walls(1, 8, 1, 9, 8, 9, 'purpur_stairs', facing='north', half='bottom', shape='straight', waterlogged='false')
    for x in range(1, 10):
        t.stairs(x, 8, 1, 'purpur_stairs', 'south')
        t.stairs(x, 8, 9, 'purpur_stairs', 'north')
    for z in range(2, 9):
        t.stairs(1, 8, z, 'purpur_stairs', 'east')
        t.stairs(9, 8, z, 'purpur_stairs', 'west')
    t.box(3, 9, 3, 7, 9, 7, 'purpur_slab', type='bottom', waterlogged='false')
    t.set(5, 9, 5, 'amethyst_block')
    t.set(5, 10, 5, 'end_rod', facing='up')
    t.air(2, 7, 2, 8, 7, 8)
    t.box(2, 8, 2, 8, 8, 8, 'purpur_block')
    t.set(5, 7, 5, 'end_rod', facing='down')
    t.set(5, 6, 5, 'end_rod', facing='down')
    # pedestal, amethyst, dealer
    t.box(4, 1, 4, 6, 1, 6, 'end_stone_bricks')
    t.set(5, 1, 5, 'amethyst_block')
    t.mod(5, 2, 5, 'relic_pedestal', 'north')
    for (x, z) in ((2, 2), (8, 2), (2, 8), (8, 8)):
        t.set(x, 2, z, 'amethyst_cluster', facing='up', waterlogged='false')
    t.villager(5, 2, 7, NS + ':relic_dealer', 3)
    return t


def forge():
    """Titansmith forge: stone workshop with chimney, lava pit and the titan anvil. 11 wide, 10 deep."""
    t = Tpl(11, 17, 10)
    t.air(0, 1, 0, 10, 16, 9)
    t.box(0, 0, 0, 10, 0, 9, '@trim')
    t.box(1, 0, 2, 9, 0, 8, 'polished_blackstone_bricks')
    t.walls(0, 1, 1, 10, 5, 9, '@wall')
    t.air(2, 1, 1, 8, 3, 1)        # wide open front
    t.box(1, 4, 1, 9, 4, 1, '@log', axis='x')
    for x in (1, 9):
        t.box(x, 1, 1, x, 3, 1, '@log')
    t.air(1, 1, 2, 9, 5, 8)
    t.walls(0, 1, 1, 10, 1, 9, '@trim')
    t.air(2, 1, 1, 8, 1, 1)
    gable_roof_x(t, 0, 10, 0, 9, 6)
    for x in (0, 10):
        gable_fill_x(t, x, 0, 9, 6, '@wall')
    # chimney with smoke
    t.box(7, 1, 7, 9, 13, 9, 'bricks')
    t.air(8, 1, 8, 8, 12, 8)
    t.set(8, 1, 8, 'magma_block')
    t.set(8, 13, 8, 'campfire', facing='north', lit='true', signal_fire='true', waterlogged='false')
    t.set(8, 2, 7, 'iron_bars')
    t.air(8, 1, 7, 8, 1, 7)
    t.set(8, 1, 7, 'lava')
    t.set(7, 1, 6, 'iron_bars')
    t.set(9, 1, 6, 'iron_bars')
    t.set(8, 1, 6, 'iron_bars')
    # workshop
    t.mod(5, 1, 5, 'titan_anvil', 'north')
    t.set(3, 1, 7, 'anvil', facing='east')
    t.set(2, 1, 8, 'smithing_table')
    t.set(4, 1, 8, 'blast_furnace', facing='north', lit='false')
    t.set(5, 1, 8, 'grindstone', face='floor', facing='north')
    t.set(2, 1, 5, 'barrel', facing='up', open='false')
    t.set(2, 1, 4, 'chest', facing='east', type='single', waterlogged='false')
    t.set(2, 1, 3, 'water_cauldron', level=3)
    t.lantern(5, 4, 4, hanging=True)
    t.set(1, 3, 5, 'wall_torch', facing='east')
    t.villager(5, 1, 3, NS + ':titansmith', 2)
    window(t, 0, 2, 4, 2)
    window(t, 10, 2, 4, 2)
    return t


def inn(rnd):
    """Two-storey inn with a bar, hearth and four beds upstairs. 13 wide, 12 deep (z0 porch)."""
    t = Tpl(13, 15, 12)
    X0, X1, Z0, Z1 = 0, 12, 1, 11
    t.air(0, 1, 0, 12, 14, 11)
    t.box(0, 0, 0, 12, 0, 11, '@trim')
    t.box(1, 0, 2, 11, 0, 10, '@plank')
    t.walls(X0, 1, Z0, X1, 4, Z1, '@wall')
    t.box(X0, 5, Z0, X1, 5, Z1, '@plank')
    for z in (Z0, Z1):
        for x in range(X0, X1 + 1):
            t.log(x, 5, z, axis='x')
    for x in (X0, X1):
        for z in range(Z0, Z1 + 1):
            t.log(x, 5, z, axis='z')
    t.walls(X0, 6, Z0, X1, 8, Z1, '@plank')
    for (x, z) in ((X0, Z0), (X1, Z0), (X0, Z1), (X1, Z1), (4, Z0), (8, Z0), (4, Z1), (8, Z1)):
        t.box(x, 6, z, x, 8, z, '@log')
    t.air(1, 6, 2, 11, 8, 10)
    gable_roof_x(t, X0 - 1 + 1, X1, Z0 - 1, Z1, 9)
    for x in (X0, X1):
        gable_fill_x(t, x, Z0 - 1, Z1, 9, '@plank')
    # door and porch
    t.door(6, 1, Z0, 'north', hinge='left')
    t.box(6, 0, 0, 6, 0, 0, '@path')
    t.lantern(5, 3, 0, hanging=False) if False else None
    t.set(5, 3, 0, 'wall_torch', facing='north')
    t.set(7, 3, 0, 'wall_torch', facing='north')
    # balcony over the door
    for x in range(3, 10):
        t.slab(x, 5, 0, '@plank_slab', 'top')
        t.set(x, 6, 0, '@fence')
    t.door(6, 6, Z0, 'north')
    # windows
    for x in (2, 3, 9, 10):
        window(t, x, 2, Z0, 2)
    for z in (4, 7):
        window(t, X0, 2, z, 2)
        window(t, X1, 2, z, 2)
        window(t, X0, 7, z, 1)
        window(t, X1, 7, z, 1)
    for x in (2, 10):
        window(t, x, 7, Z1, 1)
    # bar
    for z in range(6, 10):
        t.set(8, 1, z, 'barrel', facing='west', open='false')
        t.slab(8, 2, z, '@plank_slab', 'bottom')
    t.set(8, 2, 7, 'brewing_stand', has_bottle_0='false', has_bottle_1='false', has_bottle_2='false')
    t.set(10, 1, 10, 'barrel', facing='up', open='false')
    t.set(11, 1, 10, 'barrel', facing='up', open='false')
    t.set(10, 2, 10, 'barrel', facing='up', open='false')
    for z in (6, 8):
        t.stairs(7, 1, z, '@plank_stairs', 'east')
    # tables
    for (x, z) in ((3, 4), (3, 8)):
        t.set(x, 1, z, '@fence')
        t.set(x, 2, z, '@carpet_red' if False else '@pressure_plate', powered='false')
        t.stairs(x - 1, 1, z, '@plank_stairs', 'east')
        t.stairs(x + 1, 1, z, '@plank_stairs', 'west')
    # hearth
    t.box(5, 1, Z1, 7, 4, Z1, 'bricks')
    t.set(6, 1, Z1 - 1, 'campfire', facing='north', lit='true', signal_fire='false', waterlogged='false')
    t.box(5, 2, Z1 - 1, 7, 4, Z1 - 1, 'bricks')
    t.air(6, 2, Z1 - 1, 6, 2, Z1 - 1)
    t.set(6, 2, Z1 - 1, 'bricks') if False else None
    # stairs up (ladder)
    for y in range(1, 6):
        t.set(1, y, 10, 'ladder', facing='east', waterlogged='false')
    t.air(1, 5, 10, 1, 5, 10)
    t.set(1, 5, 10, 'ladder', facing='east', waterlogged='false')
    # upstairs: four beds, chests, lanterns
    for (x, z, f) in ((2, 3, 'south'), (4, 3, 'south'), (8, 3, 'south'), (10, 3, 'south')):
        t.bed(x, 6, z, f)
    for x in (3, 9):
        t.chest(x, 6, 3, 'south')
    t.set(6, 6, 9, 'lectern', facing='north', has_book='false', powered='false')
    t.lantern(6, 4, 6, hanging=True)
    t.lantern(6, 8, 6, hanging=True)
    t.lantern(3, 4, 4, hanging=True) if False else None
    return t


def barracks():
    """Guard barracks with a training yard. 11 wide, 9 deep."""
    t = Tpl(11, 9, 9)
    t.air(0, 1, 0, 10, 8, 8)
    t.box(0, 0, 0, 10, 0, 8, '@trim')
    t.walls(0, 1, 3, 10, 4, 8, '@wall')
    t.box(0, 5, 3, 10, 5, 8, '@wall')
    for x in range(0, 11, 2):
        t.set(x, 6, 3, '@wall_wall')
        t.set(x, 6, 8, '@wall_wall')
    for z in range(3, 9, 2):
        t.set(0, 6, z, '@wall_wall')
        t.set(10, 6, z, '@wall_wall')
    t.air(1, 1, 4, 9, 4, 7)
    t.door(5, 1, 3, 'north', name='spruce_door' if False else '@door')
    for x in (2, 8):
        t.set(x, 2, 3, 'iron_bars')
    t.bed(2, 1, 5, 'south')
    t.bed(8, 1, 5, 'south')
    t.set(5, 1, 7, 'cartography_table')
    t.chest(4, 1, 7, 'north')
    t.lantern(5, 4, 5, hanging=True)
    # training yard: fence ring with targets
    for x in range(0, 11):
        t.set(x, 1, 0, '@fence') if x not in (4, 5, 6) else None
    t.set(0, 1, 1, '@fence')
    t.set(0, 1, 2, '@fence')
    t.set(10, 1, 1, '@fence')
    t.set(10, 1, 2, '@fence')
    t.set(2, 1, 1, 'target')
    t.set(8, 1, 1, 'hay_block', axis='y')
    t.set(8, 2, 1, 'carved_pumpkin', facing='north')
    t.mob(3, 1, 1, 'minecraft:iron_golem', PlayerCreated=nbt.Byte(0))
    t.mob(7, 1, 2, 'minecraft:iron_golem', PlayerCreated=nbt.Byte(0))
    t.set(5, 7, 5, 'blue_banner' if False else '@banner', facing='north') if False else None
    return t


def cottage(seed):
    """Small single-storey cottage with a loft window. 7 wide, 9 deep (z0 porch)."""
    rnd = random.Random(seed)
    t = Tpl(7, 11, 9)
    X0, X1, Z0, Z1 = 0, 6, 2, 8
    t.air(0, 1, 0, 6, 10, 8)
    t.box(0, 0, 0, 6, 0, 8, '@ground')
    t.box(X0, 0, Z0, X1, 0, Z1, '@trim')
    t.box(X0 + 1, 0, Z0 + 1, X1 - 1, 0, Z1 - 1, '@plank')
    t.walls(X0, 1, Z0, X1, 3, Z1, '@plank')
    t.walls(X0, 1, Z0, X1, 1, Z1, '@wall')
    for (x, z) in ((X0, Z0), (X1, Z0), (X0, Z1), (X1, Z1)):
        t.box(x, 1, z, x, 3, z, '@log')
    gable_roof_z(t, Z0 - 1, Z1, X0 - 1 + 1, X1, 4)
    for z in (Z0, Z1):
        gable_fill_z(t, z, X0, X1, 4, '@plank')
    t.door(3, 1, Z0, 'north')
    window(t, 1, 2, Z0, 1)
    window(t, 5, 2, Z0, 1)
    window(t, 3, 5, Z0, 1)
    window(t, X0, 2, 5, 1)
    window(t, X1, 2, 5, 1)
    t.box(3, 0, 0, 3, 0, Z0 - 1, '@path')
    t.lantern(2, 3, Z0 - 1, hanging=False) if False else None
    t.set(2, 1, Z0 - 1, '@fence')
    t.set(2, 2, Z0 - 1, 'lantern', hanging='false', waterlogged='false')
    t.bed(1, 1, 6, 'south')
    t.set(5, 1, 7, 'crafting_table')
    t.set(5, 1, 6, 'furnace', facing='west', lit='false')
    t.chest(1, 1, 3, 'east')
    flowerpot(t, 5, 1, 3, rnd)
    t.lantern(3, 3, 5, hanging=True)
    t.jigsaw(3, 1, 0, 'north', 'building', 'lot', 'minecraft:empty', 'minecraft:air')
    return t


def tree(t, x, y, z, height=4):
    t.box(x, y, z, x, y + height - 1, z, '@log')
    for dy in range(height - 2, height + 2):
        r = 2 if dy < height else 1
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if abs(dx) + abs(dz) <= r + (1 if dy == height - 1 else 0) and not (dx == 0 and dz == 0 and dy < height):
                    t.leaves(x + dx, y + dy, z + dz)


# ================================================================================================ core
S = 63          # core size
C = S // 2      # centre
G = 0           # ground layer (the bottom: beard_thin adapts the terrain to a rigid piece's bottom layer)
HGT = 30


def core(v, seed=7):
    rnd = random.Random(seed)
    p = VARIANTS[v]
    t = Tpl(S, HGT, S)
    # ground
    t.box(0, G, 0, S - 1, G, S - 1, '@ground')
    t.air(0, G + 1, 0, S - 1, HGT - 1, S - 1)

    def dist(x, z):
        return math.hypot(x - C, z - C)

    # ---- streets: N-S and E-W, 5 wide, with curbs
    for i in range(3, S - 3):
        for k in range(C - 2, C + 3):
            for (x, z) in ((k, i), (i, k)):
                edge = k in (C - 2, C + 2)
                t.set(x, G, z, '@path2' if edge or rnd.random() < 0.15 else '@path')
    # ---- plaza: paved disc with radial quartz rays and a lapis ring
    for x in range(C - 10, C + 11):
        for z in range(C - 10, C + 11):
            d = dist(x, z)
            if d <= 10.3:
                ang = math.atan2(z - C, x - C)
                ray = abs(((ang / (math.pi / 4)) + 0.5) % 1 - 0.5) < 0.09 and d > 5.5
                if 9.4 < d <= 10.3:
                    t.set(x, G, z, 'lapis_block' if (x + z) % 2 == 0 else '@trim')
                elif ray:
                    t.set(x, G, z, 'quartz_bricks')
                else:
                    t.set(x, G, z, '@trim' if (x * 7 + z * 3) % 5 else '@path2')
    # ---- fountain: a raised basin around the spire, glowing floor, rim of quartz with slabs
    for x in range(C - 6, C + 7):
        for z in range(C - 6, C + 7):
            d = dist(x, z)
            if d < 4.6:
                t.set(x, G, z, 'sea_lantern' if abs(d - 3.5) < 0.6 and (x + z) % 2 == 0 else 'prismarine_bricks')
                t.set(x, G + 1, z, 'water', level=0)
            elif d < 5.6:
                t.set(x, G, z, 'quartz_bricks')
                t.set(x, G + 1, z, 'quartz_bricks')
                t.slab(x, G + 2, z, 'smooth_quartz_slab')
    # ---- Star Spire
    b0, b1 = C - 2, C + 2
    t.box(b0, G, b0, b1, G + 8, b1, 'quartz_bricks')
    for (x, z) in ((b0, b0), (b1, b0), (b0, b1), (b1, b1)):
        t.box(x, G, z, x, G + 8, z, 'quartz_pillar', axis='y')
        t.set(x, G + 9, z, 'end_rod', facing='up')
    for x in range(b0, b1 + 1):
        for z in range(b0, b1 + 1):
            if x in (b0, b1) or z in (b0, b1):
                t.set(x, G + 4, z, 'gold_block' if (x + z) % 2 == 0 else 'chiseled_quartz_block')
    for (x, z, f) in ((C, b0, 'north'), (C, b1, 'south'), (b0, C, 'west'), (b1, C, 'east')):
        t.set(x, G + 2, z, 'lapis_block')
        t.set(x, G + 6, z, 'light_blue_stained_glass')
    t.box(C - 1, G + 9, C - 1, C + 1, G + 18, C + 1, 'quartz_pillar', axis='y')
    for y in (G + 9, G + 13, G + 18):
        for (x, z) in ((C - 1, C - 1), (C + 1, C - 1), (C - 1, C + 1), (C + 1, C + 1)):
            t.set(x, y, z, 'gold_block' if y != G + 13 else 'lapis_block')
    for (x, z) in ((C, C - 1), (C, C + 1), (C - 1, C), (C + 1, C)):
        t.set(x, G + 15, z, 'light_blue_stained_glass')
        t.set(x, G + 16, z, 'light_blue_stained_glass')
    for (x, z, f) in ((C - 1, C - 1, 'up'), (C + 1, C - 1, 'up'), (C - 1, C + 1, 'up'), (C + 1, C + 1, 'up')):
        t.set(x, G + 19, z, 'end_rod', facing='up')
    for y, b in zip(range(G + 19, G + 27), ['quartz_pillar', 'quartz_pillar', 'quartz_pillar', 'gold_block', 'chiseled_quartz_block',
                                             'lapis_block', 'quartz_pillar', 'gold_block']):
        t.set(C, y, C, b, **({'axis': 'y'} if 'pillar' in b else {}))
    t.mod(C, G + 27, C, 'celestial_crystal', 'north')
    # flying buttresses from the base to the shaft
    for (x, z, f) in ((C, b0 - 0, 'south'), (C, b1, 'north'), (b0, C, 'east'), (b1, C, 'west')):
        t.stairs(x, G + 9, z, 'quartz_stairs', f)

    # ---- walls with walkway and crenellations
    WH = G + 7     # top of wall (walkway)
    for i in range(S):
        for depth in range(3):
            for (x, z) in ((i, depth), (i, S - 1 - depth), (depth, i), (S - 1 - depth, i)):
                t.box(x, G, z, x, WH, z, '@wall')
                if depth == 0:
                    t.set(x, G + 5, z, '@trim')
                    if i % 2 == 0:
                        t.set(x, WH + 1, z, '@wall')
                    else:
                        t.slab(x, WH + 1, z, '@wall_slab')
                elif depth == 2:
                    t.set(x, WH + 1, z, '@wall_wall')
    # inner pilasters with lanterns
    for i in range(10, S - 10, 6):
        for (x, z, f) in ((i, 3, 'south'), (i, S - 4, 'north'), (3, i, 'east'), (S - 4, i, 'west')):
            if abs(i - C) <= 7:
                continue
            t.box(x, G + 1, z, x, WH, z, '@trim')
            t.lantern(x, WH + 1, z)
    # arrow slits on the outer face
    for i in range(12, S - 12, 6):
        if abs(i - C) <= 8:
            continue
        for (x, z) in ((i, 0), (i, S - 1), (0, i), (S - 1, i)):
            t.air(x, G + 3, z, x, G + 4, z)

    # ---- corner towers (octagonal, pointed roofs)
    for (tx, tz) in ((0, 0), (S - 9, 0), (0, S - 9), (S - 9, S - 9)):
        tower(t, tx, tz, rnd)
        mx, mz = tx > 0, tz > 0
        for (lx, lz) in ((7, 1), (1, 7)):
            x, z = (8 - lx if mx else lx), (8 - lz if mz else lz)
            t.air(tx + x, WH + 1, tz + z, tx + x, WH + 2, tz + z)
    # ---- gatehouses on the four sides, with the road jigsaws
    gh = gatehouse()
    t.stamp(gh, C - 6, G, 0, 0, keep_jigsaws=True)            # north: front faces north
    t.stamp(gh, S - 6, G, C - 6, 1, keep_jigsaws=True)        # east
    t.stamp(gh, C - 6, G, S - 6, 2, keep_jigsaws=True)        # south
    t.stamp(gh, 0, G, C - 6, 3, keep_jigsaws=True)            # west
    # ---- buildings
    placed = []

    def put(tpl, x0, z0, r, name):
        w, d = tpl.footprint(r)
        for (a, b, c2, e, n) in placed:
            if x0 < a + c2 and a < x0 + w and z0 < b + e and b < z0 + d:
                raise SystemExit(f'{v}: {name} overlaps {n}')
        placed.append((x0, z0, w, d, name))
        t.stamp(tpl, x0, G, z0, r)

    put(bank(), 43, 9, 2, 'bank')                         # NE, front faces south
    put(relic_pavilion(), 14, 12, 2, 'relic pavilion')    # NW, faces south
    put(barracks(), 12, 3, 2, 'barracks')                 # NW by the north gate, yard faces south
    put(house_a(11), 3, 13, 2, 'house nw')                # NW west strip, faces south
    put(house_a(12), 34, 11, 2, 'house ne')               # NE, faces south
    put(inn(rnd), 9, 36, 0, 'inn')                        # SW, faces north (toward the E-W street)
    put(forge(), 14, 48, 1, 'forge')                      # SW by the N-S street, faces east
    put(market_hall(p['awnings']), 35, 43, 0, 'market hall')   # SE, faces north
    put(cottage(14), 48, 34, 0, 'cottage se')             # SE, faces north toward the E-W street
    # trees and a composter in the open corners
    for (x, z) in ((5, 51), (10, 51), (5, 40), (5, 45), (41, 5), (48, 5), (57, 38), (57, 41), (24, 5)):
        tree(t, x, G + 1, z)
    t.set(8, G + 1, 49, 'composter', level=0)
    # ---- plaza furniture: planters with trees, benches, quest boards, bell, lamps
    for (px, pz) in ((C - 7, C - 7), (C + 7, C - 7), (C - 7, C + 7), (C + 7, C + 7)):
        t.walls(px - 1, G + 1, pz - 1, px + 1, G + 1, pz + 1, '@trim')
        t.set(px, G + 1, pz, 'grass_block' if v != 'desert' else 'sand')
        t.box(px, G + 2, pz, px, G + 4, pz, '@log')
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                for dy in (5, 6):
                    if abs(dx) + abs(dz) <= (3 if dy == 5 else 2) and not (dx == 0 and dz == 0 and dy == 5):
                        t.leaves(px + dx, G + dy, pz + dz)
        t.leaves(px, G + 7, pz)
        for (dx, dz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            t.set(px + dx, G + 2, pz + dz, 'lantern', hanging='false', waterlogged='false')
    for (x, z, f) in ((C - 3, C - 8, 'south'), (C + 3, C - 8, 'south'), (C - 3, C + 8, 'north'), (C + 3, C + 8, 'north')):
        t.stairs(x, G + 1, z, '@plank_stairs', 'north' if f == 'south' else 'south')
    for (x, z, f) in ((C - 8, C - 3, 'east'), (C - 8, C + 3, 'east'), (C + 8, C - 3, 'west'), (C + 8, C + 3, 'west')):
        t.stairs(x, G + 1, z, '@plank_stairs', 'west' if f == 'east' else 'east')
    t.mod(C - 3, G + 1, C - 9, 'quest_board', 'north')
    t.mod(C + 3, G + 1, C + 9, 'quest_board', 'south')
    t.mod(C - 9, G + 1, C + 3, 'quest_board', 'west')
    t.mod(C + 9, G + 1, C - 3, 'quest_board', 'east')
    t.set(C + 9, G + 1, C + 9, '@trim')
    t.set(C + 9, G + 2, C + 9, 'bell', attachment='floor', facing='north', powered='false')
    # lamps along the streets
    def built(x, z):
        return any(a <= x < a + w and b <= z < b + d for (a, b, w, d, _) in placed)
    for i in list(range(6, C - 10, 7)) + list(range(C + 11, S - 5, 7)):
        for (x, z) in ((C - 3, i), (C + 3, i), (i, C - 3), (i, C + 3)):
            if t.get(x, G + 1, z) not in (None, 'air') or built(x, z):
                continue
            t.box(x, G + 1, z, x, G + 3, z, '@fence')
            t.lantern(x, G + 4, z)
    # ---- villagers, free workstations, gardens
    t.villager(C - 4, G + 1, C - 11, 'minecraft:none', 1)
    t.villager(C + 11, G + 1, C + 4, 'minecraft:none', 1)
    t.villager(C - 11, G + 1, C - 4, 'minecraft:none', 1)
    t.villager(C + 4, G + 1, C + 11, 'minecraft:none', 1)
    gardens(t, rnd, v)
    return t


def tower(t, tx, tz, rnd):
    def inside(x, z):
        return not (min(x, 8 - x) + min(z, 8 - z) < 2)
    for x in range(9):
        for z in range(9):
            if not inside(x, z):
                continue
            edge = not inside(x - 1, z) or not inside(x + 1, z) or not inside(x, z - 1) or not inside(x, z + 1)
            for y in range(G, G + 13):
                t.set(tx + x, y, tz + z, '@wall' if edge or y <= G else 'air')
            if edge:
                t.set(tx + x, G + 6, tz + z, '@trim')
                t.set(tx + x, G + 12, tz + z, '@trim')
            t.set(tx + x, G + 7, tz + z, '@wall') if not edge else None
    # windows
    for (x, z) in ((4, 0), (4, 8), (0, 4), (8, 4)):
        t.set(tx + x, G + 3, tz + z, 'light_blue_stained_glass_pane')
        t.set(tx + x, G + 9, tz + z, 'light_blue_stained_glass_pane')
        t.set(tx + x, G + 10, tz + z, 'light_blue_stained_glass_pane')
    t.lantern(tx + 4, G + 11, tz + 4, hanging=True)
    # pointed roof: rings of stairs climbing inward
    for k in range(5):
        y = G + 13 + k
        lo, hi = k, 8 - k
        for x in range(lo, hi + 1):
            for z in range(lo, hi + 1):
                if not inside(x, z) and k == 0:
                    continue
                if x in (lo, hi) or z in (lo, hi):
                    if lo == hi:
                        t.set(tx + x, y, tz + z, '@roof')
                    elif z == lo:
                        t.stairs(tx + x, y, tz + z, '@roof_stairs', 'south')
                    elif z == hi:
                        t.stairs(tx + x, y, tz + z, '@roof_stairs', 'north')
                    elif x == lo:
                        t.stairs(tx + x, y, tz + z, '@roof_stairs', 'east')
                    else:
                        t.stairs(tx + x, y, tz + z, '@roof_stairs', 'west')
    t.set(tx + 4, G + 18, tz + 4, 'gold_block')
    t.set(tx + 4, G + 19, tz + 4, 'end_rod', facing='up')


def gatehouse():
    """13 wide, 6 deep, front (outside) facing north. Arched passage 5 wide, portcullis teeth, banners."""
    t = Tpl(13, 15, 6)
    t.air(3, 1, 0, 9, 14, 0)
    t.box(0, 0, 0, 12, 0, 5, '@path2')
    t.box(4, 0, 0, 8, 0, 5, '@path')
    for x in range(13):
        for z in range(6):
            tower_part = x <= 2 or x >= 10
            top = 13 if tower_part else 11
            if not tower_part and z == 0:
                continue          # recess for the banners
            t.box(x, 1, z, x, top, z, '@wall')
    # passage and arch
    t.air(4, 1, 0, 8, 5, 5)
    for z in range(1, 6):
        t.stairs(4, 6, z, '@wall_stairs', 'east', 'top')
        t.stairs(8, 6, z, '@wall_stairs', 'west', 'top')
        t.air(5, 6, z, 7, 6, z)
        t.stairs(5, 7, z, '@wall_stairs', 'east', 'top') if False else None
    t.box(4, 6, 1, 8, 6, 1, 'iron_bars')
    t.air(4, 6, 1, 4, 6, 1)
    t.air(8, 6, 1, 8, 6, 1)
    t.box(5, 6, 1, 7, 6, 1, 'iron_bars')
    # trim bands, crenellations, banners, lanterns
    for x in range(13):
        top = 13 if (x <= 2 or x >= 10) else 11
        for z in range(6):
            if not (x <= 2 or x >= 10) and z == 0:
                continue
            if t.get(x, top, z) == '@wall':
                t.set(x, top - 1, z, '@trim') if z in (0, 1, 5) or x in (0, 12) else None
                if (x + z) % 2 == 0 and (z in (0, 1, 5) or x in (0, 2, 10, 12)):
                    t.set(x, top + 1, z, '@wall')
    for x in (3, 9):
        t.set(x, 8, 0, '@banner', facing='north')
        t.set(x, 9, 0, 'air') if False else None
    for x in (3, 9):
        t.lantern(x, 3, 0) if False else None
    t.set(3, 4, 0, 'wall_torch', facing='north') if False else None
    t.lantern(6, 5, 3, hanging=True)
    t.set(6, 9, 1, 'chiseled_quartz_block')
    t.set(6, 10, 1, 'gold_block')
    t.set(6, 8, 0, 'lapis_block') if False else None
    # the road connector: on the outer ground, facing out
    t.jigsaw(6, 0, 0, 'north', 'gate', 'road', NS + ':city/{v}/approach', '@path')
    return t


def gardens(t, rnd, v):
    """Flowers and grass on open ground, hedges along some walls."""
    p = VARIANTS[v]
    ground = resolve('@ground', v)
    for x in range(3, S - 3):
        for z in range(3, S - 3):
            if t.get(x, G, z) != '@ground' or t.get(x, G + 1, z) not in (None, 'air'):
                continue
            r = rnd.random()
            if p['flowers'] and r < 0.07:
                t.set(x, G + 1, z, rnd.choice(p['flowers']))
            elif v not in ('desert', 'snowy') and r < 0.2:
                t.set(x, G + 1, z, 'short_grass')


# ================================================================================================ roads and outskirts
ROAD_W = 5


def road(length, side_lots=True, bend=None, tee=False, lamps=True):
    """A road piece running north from its entry (south end). 1-tall path, lamp posts, side lots.

    bend: 'left'/'right' turns the exit 90 degrees; tee: exits both left and right as well as forward."""
    w = ROAD_W + 4         # lamps and lot jigsaws sit one block outside the path on each side
    t = Tpl(w, 5, length)
    x0, x1 = 2, 2 + ROAD_W - 1
    rnd = random.Random(length * 31 + (7 if bend else 0) + (3 if tee else 0))
    for z in range(length):
        for x in range(x0, x1 + 1):
            edge = x in (x0, x1)
            t.set(x, 0, z, '@path2' if edge or rnd.random() < 0.12 else '@path')
            t.set(x, 1, z, 'air')
            t.set(x, 2, z, 'air')
    mid = 2 + ROAD_W // 2
    t.jigsaw(mid, 0, length - 1, 'south', 'road', 'gate', 'minecraft:empty', '@path')
    if bend or tee:
        # widen the end into a square junction
        for z in range(0, ROAD_W):
            for x in range(0, w):
                t.set(x, 0, z, '@path2' if x in (0, w - 1) or z in (0, ROAD_W - 1) else '@path')
                t.set(x, 1, z, 'air')
                t.set(x, 2, z, 'air')
        jz = ROAD_W // 2
        if bend == 'left' or tee:
            t.jigsaw(0, 0, jz, 'west', 'road_next', 'road', NS + ':city/{v}/roads', '@path')
        if bend == 'right' or tee:
            t.jigsaw(w - 1, 0, jz, 'east', 'road_next', 'road', NS + ':city/{v}/roads', '@path')
        if tee:
            t.jigsaw(mid, 0, 0, 'north', 'road_next', 'road', NS + ':city/{v}/roads', '@path')
    else:
        t.jigsaw(mid, 0, 0, 'north', 'road_next', 'road', NS + ':city/{v}/roads', '@path')
    if side_lots:
        start = ROAD_W + 2 if (bend or tee) else 2
        for z in range(start + 2, length - 2, 8):
            t.jigsaw(0, 1, z, 'west', 'lot', 'building', NS + ':city/{v}/outskirts', 'minecraft:air')
            t.jigsaw(w - 1, 1, z + 4 if z + 4 < length - 1 else z, 'east', 'lot', 'building', NS + ':city/{v}/outskirts', 'minecraft:air')
    if lamps:
        for z in range(3, length - 1, 8):
            if t.get(1, 1, z) is None:
                t.box(1, 1, z, 1, 3, z, '@fence')
                t.lantern(1, 4, z)
    return t


def road_end():
    t = Tpl(ROAD_W + 4, 5, 3)
    x0, x1 = 2, 2 + ROAD_W - 1
    for z in range(3):
        for x in range(x0, x1 + 1):
            t.set(x, 0, z, '@path2' if z == 0 or x in (x0, x1) else '@path')
            t.set(x, 1, z, 'air')
    mid = 2 + ROAD_W // 2
    t.jigsaw(mid, 0, 2, 'south', 'road', 'gate', 'minecraft:empty', '@path')
    t.box(mid, 1, 0, mid, 2, 0, '@fence')
    t.lantern(mid, 3, 0)
    return t


def lot_base(w, d, ground=True, h=12):
    """Outskirt piece: entry jigsaw at the front middle (z = 0, y = 1), facing north toward the road."""
    t = Tpl(w, h, d)
    if ground:
        t.box(0, 0, 0, w - 1, 0, d - 1, '@ground')
    t.air(0, 1, 0, w - 1, h - 1, d - 1)
    t.jigsaw(w // 2, 1, 0, 'north', 'building', 'lot', 'minecraft:empty', 'minecraft:air')
    t.set(w // 2, 0, 0, '@path')
    return t


def farm(crop, seed):
    rnd = random.Random(seed)
    t = lot_base(11, 11)
    t.walls(0, 0, 1, 10, 0, 10, '@log', axis='x')
    for z in range(1, 11):
        t.log(0, 0, z, axis='z')
        t.log(10, 0, z, axis='z')
    for x in range(1, 10):
        t.log(x, 0, 1, axis='x')
        t.log(x, 0, 10, axis='x')
    for x in range(1, 10):
        for z in range(2, 10):
            if x == 5:
                t.set(x, 0, z, 'water', level=0)
            else:
                t.set(x, 0, z, 'farmland', moisture=7)
                age = 3 if crop == 'beetroots' else 7
                t.set(x, 1, z, crop, age=rnd.choice([age, age, age - 1]))
    t.set(5, 1, 6, 'composter', level=0)
    t.air(5, 1, 6, 5, 1, 6)
    t.set(5, 0, 6, 'farmland', moisture=7)
    t.set(5, 1, 6, 'composter', level=0)
    t.box(5, 0, 0, 5, 0, 1, '@path')
    for (x, z) in ((0, 1), (10, 1), (0, 10), (10, 10)):
        t.set(x, 1, z, '@fence')
        t.set(x, 2, z, 'lantern', hanging='false', waterlogged='false')
    return t


def farm_pumpkin(seed):
    rnd = random.Random(seed)
    t = lot_base(9, 9)
    for x in range(0, 9):
        for z in range(1, 9):
            edge = x in (0, 8) or z in (1, 8)
            if edge:
                t.set(x, 1, z, '@fence')
            elif x == 4:
                t.set(x, 0, z, 'water', level=0)
            else:
                if rnd.random() < 0.6:
                    t.set(x, 0, z, 'farmland', moisture=7)
                if rnd.random() < 0.35:
                    t.set(x, 1, z, rnd.choice(['pumpkin', 'melon']))
    t.set(4, 1, 1, '@fence_gate', facing='north', open='false', powered='false', in_wall='false')
    t.set(4, 0, 1, '@path')
    t.air(4, 0, 2, 4, 0, 2)
    t.set(4, 0, 2, '@path')
    t.air(4, 0, 0, 4, 0, 0)
    t.set(4, 0, 0, '@path')
    return t


def windmill():
    t = lot_base(9, 9, h=15)
    t.box(2, 0, 2, 6, 0, 6, '@trim')
    t.walls(2, 1, 2, 6, 9, 6, '@wall')
    t.walls(2, 5, 2, 6, 5, 6, '@trim')
    t.air(3, 1, 3, 5, 9, 5)
    t.door(4, 1, 2, 'north')
    t.box(4, 0, 0, 4, 0, 1, '@path')
    gable_roof_x(t, 1, 7, 1, 7, 10)
    for x in (2, 6):
        gable_fill_x(t, x, 1, 7, 10, '@plank')
    # sails on the north face: a hub with four arms
    hub = (4, 8, 1)
    t.set(*hub, '@log', axis='z')
    for k in range(1, 4):
        for (dx, dy) in ((0, k), (0, -k), (k, 0), (-k, 0)):
            t.set(hub[0] + dx, hub[1] + dy, 0, '@fence')
            if k >= 2:
                sx, sy = (1, 0) if dx == 0 else (0, 1)
                t.set(hub[0] + dx + sx, hub[1] + dy + sy, 0, 'white_wool')
    t.set(4, 2, 4, 'barrel', facing='up', open='false')
    t.set(3, 1, 5, 'hay_block', axis='y')
    t.set(5, 1, 5, 'hay_block', axis='y')
    t.lantern(4, 4, 4, hanging=True)
    return t


def stable():
    t = lot_base(11, 9)
    t.box(1, 0, 4, 9, 0, 8, '@plank')
    for x in (1, 5, 9):
        for z in (4, 8):
            t.box(x, 1, z, x, 3, z, '@log')
    t.walls(1, 1, 8, 9, 3, 8, '@plank')
    for x in range(1, 10):
        t.slab(x, 4, 4, '@plank_slab', 'bottom')
        t.slab(x, 4, 5, '@plank_slab', 'bottom')
        t.set(x, 4, 6, '@plank')
        t.slab(x, 4, 7, '@plank_slab', 'bottom')
        t.slab(x, 4, 8, '@plank_slab', 'bottom')
    for z in range(5, 8):
        t.set(5, 1, z, '@fence')
    for x in range(0, 11):
        t.set(x, 1, 1, '@fence') if x != 5 else t.set(x, 1, 1, '@fence_gate', facing='north', open='false', powered='false', in_wall='false')
    for z in range(1, 4):
        t.set(0, 1, z, '@fence')
        t.set(10, 1, z, '@fence')
    t.set(2, 1, 7, 'hay_block', axis='y')
    t.set(8, 1, 7, 'hay_block', axis='y')
    t.set(3, 1, 7, 'water_cauldron', level=3)
    t.mob(3, 1, 6, 'minecraft:horse', Variant=nbt.Int(0) if hasattr(nbt, 'Int') else 0)
    t.mob(7, 1, 6, 'minecraft:horse', Variant=769)
    t.lantern(5, 3, 3, hanging=False) if False else None
    t.set(5, 1, 0, '@path')
    return t


def well():
    t = lot_base(7, 7)
    t.box(1, 0, 2, 5, 0, 6, '@path2')
    t.walls(2, 1, 3, 4, 1, 5, '@trim')
    t.set(3, 0, 4, 'water', level=0)
    t.set(3, 1, 4, 'water', level=0)
    t.set(3, -1, 4, 'water') if False else None
    for (x, z) in ((2, 3), (4, 3), (2, 5), (4, 5)):
        t.box(x, 2, z, x, 3, z, '@fence')
    t.box(2, 4, 3, 4, 4, 5, '@roof_slab', type='bottom', waterlogged='false')
    t.set(3, 3, 4, 'lantern', hanging='true', waterlogged='false')
    t.box(3, 0, 0, 3, 0, 2, '@path')
    return t


def watchtower():
    t = lot_base(7, 7)
    for (x, z) in ((1, 2), (5, 2), (1, 6), (5, 6)):
        t.box(x, 1, z, x, 9, z, '@log')
    t.box(1, 9, 2, 5, 9, 6, '@plank')
    for x in range(1, 6):
        for z in range(2, 7):
            if x in (1, 5) or z in (2, 6):
                t.set(x, 10, z, '@fence')
    for y in range(1, 10):
        t.set(3, y, 3, 'ladder', facing='south', waterlogged='false')
    t.air(3, 9, 3, 3, 9, 3)
    t.set(3, 9, 3, 'ladder', facing='south', waterlogged='false')
    gable_roof_x(t, 0, 6, 1, 7, 11) if False else None
    t.box(1, 11, 2, 5, 11, 6, '@roof_slab', type='bottom', waterlogged='false')
    for (x, z) in ((1, 2), (5, 2), (1, 6), (5, 6)):
        t.set(x, 10, z, '@log', axis='y')
    t.lantern(3, 10, 5)
    t.box(3, 0, 0, 3, 0, 2, '@path')
    return t


def orchard(seed, v):
    rnd = random.Random(seed)
    t = lot_base(11, 11)
    for (x, z) in ((2, 3), (8, 3), (5, 6), (2, 9), (8, 9)):
        t.box(x, 1, z, x, 3, z, '@log')
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                for dy in (3, 4, 5):
                    if abs(dx) + abs(dz) <= (3 if dy < 5 else 1) and (dx or dz or dy == 5):
                        if rnd.random() < 0.9:
                            t.leaves(x + dx, dy, z + dz)
    berries = 'sweet_berry_bush' if v in ('taiga', 'snowy') else None
    for _ in range(8):
        x, z = rnd.randrange(1, 10), rnd.randrange(1, 10)
        if t.get(x, 1, z) in (None, 'air'):
            if berries:
                t.set(x, 1, z, berries, age=3)
            elif VARIANTS[v]['flowers']:
                t.set(x, 1, z, rnd.choice(VARIANTS[v]['flowers']))
    t.set(5, 0, 0, '@path')
    return t


def lamp_lot():
    t = lot_base(3, 3)
    t.box(1, 1, 1, 1, 3, 1, '@fence')
    t.lantern(1, 4, 1)
    t.set(1, 0, 1, '@trim')
    return t


# ================================================================================================ main
def main():
    counts = {}
    for v in VARIANTS:
        n = {}
        n['core'] = write(core(v), 'core', v)
        roads = {'road_long': road(17), 'road_short': road(9), 'road_bend_left': road(9, bend='left'),
                 'road_bend_right': road(9, bend='right'), 'road_tee': road(9, tee=True)}
        for k, tpl in roads.items():
            write(tpl, k, v)
        write(road_end(), 'road_end', v)
        write(road(13, side_lots=False), 'road_approach', v)
        p = VARIANTS[v]
        outs = {'house_a': house_a(21), 'house_b': house_b(22), 'house_c': cottage(23),
                'farm_a': farm(p['crops'][0], 31), 'farm_b': farm(p['crops'][1], 32), 'farm_pumpkin': farm_pumpkin(33),
                'windmill': windmill(), 'stable': stable(), 'well': well(), 'watchtower': watchtower(),
                'orchard': orchard(41, v), 'lamp': lamp_lot()}
        for k, tpl in outs.items():
            write(tpl, 'outskirts/' + k, v)
        counts[v] = (len(roads), len(outs))

        loc = lambda k: f'{NS}:city/{v}/{k}'
        def el(k, w, proj='rigid'):
            return {'weight': w, 'element': {'element_type': 'minecraft:single_pool_element', 'location': loc(k),
                                             'processors': 'minecraft:empty', 'projection': proj}}
        dump(os.path.join(ROOT, NS, 'worldgen', 'template_pool', 'city', v, 'core.json'),
             {'fallback': 'minecraft:empty', 'elements': [el('core', 1)]})
        dump(os.path.join(ROOT, NS, 'worldgen', 'template_pool', 'city', v, 'roads.json'),
             {'fallback': f'{NS}:city/{v}/road_ends', 'elements': [
                 el('road_long', 4, 'terrain_matching'), el('road_short', 3, 'terrain_matching'),
                 el('road_bend_left', 1, 'terrain_matching'), el('road_bend_right', 1, 'terrain_matching'),
                 el('road_tee', 1, 'terrain_matching')]})
        dump(os.path.join(ROOT, NS, 'worldgen', 'template_pool', 'city', v, 'approach.json'),
             {'fallback': f'{NS}:city/{v}/road_ends', 'elements': [el('road_approach', 1, 'terrain_matching')]})
        dump(os.path.join(ROOT, NS, 'worldgen', 'template_pool', 'city', v, 'road_ends.json'),
             {'fallback': 'minecraft:empty', 'elements': [el('road_end', 1, 'terrain_matching')]})
        weights = {'house_a': 3, 'house_b': 3, 'house_c': 2, 'farm_a': 2, 'farm_b': 2, 'farm_pumpkin': 1, 'windmill': 1,
                   'stable': 1, 'well': 1, 'watchtower': 1, 'orchard': 1, 'lamp': 2}
        dump(os.path.join(ROOT, NS, 'worldgen', 'template_pool', 'city', v, 'outskirts.json'),
             {'fallback': 'minecraft:empty', 'elements': [el('outskirts/' + k, w) for k, w in weights.items()]})
        sid = STRUCTURE_ID[v]
        dump(os.path.join(ROOT, NS, 'worldgen', 'structure', sid + '.json'), {
            'type': f'{NS}:city', 'biomes': f'#{NS}:has_structure/{sid}', 'step': 'surface_structures',
            'spawn_overrides': {}, 'terrain_adaptation': 'beard_thin', 'start_pool': f'{NS}:city/{v}/core', 'size': 6,
            'max_distance_from_center': 112, 'core_radius': C, 'ground_level': G, 'max_spread': 6})
        dump(os.path.join(ROOT, NS, 'tags', 'worldgen', 'biome', 'has_structure', sid + '.json'), {'values': BIOMES[v]})
    dump(os.path.join(ROOT, NS, 'worldgen', 'structure_set', 'trade_city.json'), {
        'structures': [{'structure': f'{NS}:{STRUCTURE_ID[v]}', 'weight': 1} for v in VARIANTS],
        'placement': {'type': 'minecraft:random_spread', 'spacing': 48, 'separation': 20, 'salt': 715264001}})
    dump(os.path.join(ROOT, NS, 'tags', 'worldgen', 'structure', 'trade_city.json'),
         {'values': [f'{NS}:{STRUCTURE_ID[v]}' for v in VARIANTS]})
    old_pool = os.path.join(ROOT, NS, 'worldgen', 'template_pool', 'city', 'trade_city.json')
    if os.path.exists(old_pool):
        os.remove(old_pool)
    print('city variants', len(VARIANTS), counts)


if __name__ == '__main__':
    main()
