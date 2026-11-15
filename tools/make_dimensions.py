"""Generates the Fallen Stars and Abyss dimensions (types, noise settings, biomes, features).

Noise routers are taken from vanilla (floating_islands / caves) read straight from the Minecraft jar,
with our own blocks, fluids and surface rules.
"""
import copy
import json
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from make_shrines import dump  # noqa: E402

ROOT = os.path.join(HERE, '..', 'src', 'main', 'resources', 'data')
NS = 'celestialascent'
JAR = os.path.join(HERE, '..', 'build', 'moddev', 'artifacts', 'neoforge-21.1.262-client-extra-aka-minecraft-resources.jar')


def vanilla(path):
    with zipfile.ZipFile(JAR) as z:
        return json.loads(z.read('data/minecraft/' + path))


def block(name, **props):
    e = {'Name': name if ':' in name else 'minecraft:' + name}
    if props:
        e['Properties'] = props
    return e


def ns(name):
    return NS + ':' + name


AIR = block('air')


def rule_block(state):
    return {'type': 'minecraft:block', 'result_state': state}


def fallen_stars():
    ns_ = vanilla('worldgen/noise_settings/floating_islands.json')
    ns_['default_block'] = block(ns('starstone'))
    ns_['default_fluid'] = AIR
    ns_['ore_veins_enabled'] = False
    ns_['aquifers_enabled'] = False
    ns_['disable_mob_generation'] = False
    ns_['sea_level'] = -64
    ns_['spawn_target'] = []
    ns_['surface_rule'] = {
        'type': 'minecraft:sequence',
        'sequence': [
            {'type': 'minecraft:condition',
             'if_true': {'type': 'minecraft:stone_depth', 'offset': 0, 'surface_type': 'floor', 'add_surface_depth': False, 'secondary_depth_range': 0},
             'then_run': rule_block(block(ns('starlit_starstone')))},
            rule_block(block(ns('starstone'))),
        ]}
    dump(os.path.join(ROOT, NS, 'worldgen', 'noise_settings', 'fallen_stars.json'), ns_)

    dump(os.path.join(ROOT, NS, 'dimension_type', 'fallen_stars.json'), {
        'ultrawarm': False, 'natural': False, 'coordinate_scale': 1.0, 'has_skylight': True, 'has_ceiling': False,
        'ambient_light': 0.3, 'fixed_time': 18000, 'monster_spawn_light_level': 0, 'monster_spawn_block_light_limit': 0,
        'piglin_safe': False, 'bed_works': False, 'respawn_anchor_works': False, 'has_raids': False,
        'logical_height': 256, 'min_y': 0, 'height': 256, 'infiniburn': '#minecraft:infiniburn_end',
        'effects': ns('fallen_stars')})
    dump(os.path.join(ROOT, NS, 'dimension', 'fallen_stars.json'), {
        'type': ns('fallen_stars'),
        'generator': {'type': 'minecraft:noise', 'settings': ns('fallen_stars'),
                      'biome_source': {'type': 'minecraft:fixed', 'biome': ns('fallen_stars')}}})

    ore('stardust_ore', ns('starstone'), ns('stardust_ore'), size=7, count=14, lo=0, hi=255)
    dump(os.path.join(ROOT, NS, 'worldgen', 'configured_feature', 'star_crystal.json'), {
        'type': 'minecraft:simple_block', 'config': {'to_place': {'type': 'minecraft:simple_state_provider', 'state': block(ns('star_crystal'))}}})
    dump(os.path.join(ROOT, NS, 'worldgen', 'placed_feature', 'star_crystal.json'), {
        'feature': ns('star_crystal'),
        'placement': [{'type': 'minecraft:count', 'count': 10}, {'type': 'minecraft:in_square'},
                      {'type': 'minecraft:heightmap', 'heightmap': 'WORLD_SURFACE_WG'},
                      {'type': 'minecraft:block_predicate_filter', 'predicate': {'type': 'minecraft:all_of', 'predicates': [
                          {'type': 'minecraft:matching_blocks', 'blocks': 'minecraft:air'},
                          {'type': 'minecraft:matching_blocks', 'offset': [0, -1, 0], 'blocks': [ns('starlit_starstone'), ns('starstone')]}]}},
                      {'type': 'minecraft:biome'}]})
    biome('fallen_stars', sky=0x05030F, fog=0x140E2E, particle='minecraft:end_rod', prob=0.0015,
          features={6: [ns('stardust_ore')], 9: [ns('star_crystal')]},
          monsters=[{'type': 'minecraft:enderman', 'weight': 10, 'minCount': 1, 'maxCount': 2}],
          music='minecraft:music.end')


def abyss():
    ns_ = vanilla('worldgen/noise_settings/caves.json')
    ns_['default_block'] = block(ns('abyssal_stone'))
    ns_['default_fluid'] = AIR
    ns_['ore_veins_enabled'] = False
    ns_['aquifers_enabled'] = False
    ns_['sea_level'] = -64
    ns_['spawn_target'] = []
    ns_['surface_rule'] = {
        'type': 'minecraft:sequence',
        'sequence': [
            {'type': 'minecraft:condition',
             'if_true': {'type': 'minecraft:vertical_gradient', 'random_name': 'minecraft:bedrock_floor',
                         'true_at_and_below': {'above_bottom': 0}, 'false_at_and_above': {'above_bottom': 5}},
             'then_run': rule_block(block('bedrock'))},
            {'type': 'minecraft:condition',
             'if_true': {'type': 'minecraft:not', 'invert': {'type': 'minecraft:vertical_gradient', 'random_name': 'minecraft:bedrock_roof',
                                                              'true_at_and_below': {'below_top': 5}, 'false_at_and_above': {'below_top': 0}}},
             'then_run': rule_block(block('bedrock'))},
            rule_block(block(ns('abyssal_stone'))),
        ]}
    dump(os.path.join(ROOT, NS, 'worldgen', 'noise_settings', 'abyss.json'), ns_)
    nh = ns_['noise']
    dump(os.path.join(ROOT, NS, 'dimension_type', 'abyss.json'), {
        'ultrawarm': False, 'natural': False, 'coordinate_scale': 1.0, 'has_skylight': False, 'has_ceiling': True,
        'ambient_light': 0.04, 'monster_spawn_light_level': 0, 'monster_spawn_block_light_limit': 0,
        'piglin_safe': False, 'bed_works': False, 'respawn_anchor_works': False, 'has_raids': False,
        'logical_height': nh['height'], 'min_y': nh['min_y'], 'height': nh['height'], 'infiniburn': '#minecraft:infiniburn_end',
        'effects': ns('abyss')})
    dump(os.path.join(ROOT, NS, 'dimension', 'abyss.json'), {
        'type': ns('abyss'),
        'generator': {'type': 'minecraft:noise', 'settings': ns('abyss'),
                      'biome_source': {'type': 'minecraft:fixed', 'biome': ns('abyss')}}})
    lo = nh['min_y']
    ore('void_essence_ore', ns('abyssal_stone'), ns('void_essence_ore'), size=5, count=9, lo=lo, hi=lo + 140)
    ore('void_essence_ore_upper', ns('abyssal_stone'), ns('void_essence_ore'), size=4, count=3, lo=lo + 140, hi=lo + nh['height'] - 8,
        configured='void_essence_ore')
    biome('abyss', sky=0x000000, fog=0x0A0612, particle='minecraft:reverse_portal', prob=0.004,
          features={6: [ns('void_essence_ore'), ns('void_essence_ore_upper')]},
          monsters=[{'type': ns('void_wraith'), 'weight': 40, 'minCount': 1, 'maxCount': 2},
                    {'type': 'minecraft:enderman', 'weight': 6, 'minCount': 1, 'maxCount': 1}],
          music='minecraft:music.nether.soul_sand_valley')


def ore(name, target, state, size, count, lo, hi, configured=None):
    cfg = configured or name
    if configured is None:
        dump(os.path.join(ROOT, NS, 'worldgen', 'configured_feature', name + '.json'), {
            'type': 'minecraft:ore', 'config': {'size': size, 'discard_chance_on_air_exposure': 0.0, 'targets': [
                {'target': {'predicate_type': 'minecraft:block_match', 'block': target}, 'state': block(state)}]}})
    dump(os.path.join(ROOT, NS, 'worldgen', 'placed_feature', name + '.json'), {
        'feature': ns(cfg),
        'placement': [{'type': 'minecraft:count', 'count': count}, {'type': 'minecraft:in_square'},
                      {'type': 'minecraft:height_range', 'height': {'type': 'minecraft:uniform',
                                                                    'min_inclusive': {'absolute': lo}, 'max_inclusive': {'absolute': hi}}},
                      {'type': 'minecraft:biome'}]})


def biome(name, sky, fog, particle, prob, features, monsters, music):
    steps = [[] for _ in range(11)]
    for k, v in features.items():
        steps[k] = v
    dump(os.path.join(ROOT, NS, 'worldgen', 'biome', name + '.json'), {
        'has_precipitation': False, 'temperature': 0.5, 'downfall': 0.0,
        'effects': {'sky_color': sky, 'fog_color': fog, 'water_color': 0x3F2A8C, 'water_fog_color': 0x1A1040,
                    'mood_sound': {'sound': 'minecraft:ambient.cave', 'tick_delay': 6000, 'block_search_extent': 8, 'offset': 2.0},
                    'particle': {'options': {'type': particle}, 'probability': prob},
                    'music': {'sound': music, 'min_delay': 6000, 'max_delay': 24000, 'replace_current_music': False}},
        'spawners': {'monster': monsters, 'creature': [], 'ambient': [], 'axolotls': [], 'underground_water_creature': [],
                     'water_creature': [], 'water_ambient': [], 'misc': []},
        'spawn_costs': {}, 'carvers': {}, 'features': steps})


if __name__ == '__main__':
    fallen_stars()
    abyss()
    print('dimensions written')
