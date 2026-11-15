"""Writes the GameTest arena: 16x10x16 with a stone floor."""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
import nbt

out = os.path.join(os.path.dirname(__file__), '..', 'src', 'main', 'resources', 'data', 'celestialascent', 'structure', 'test_floor.nbt')
palette = [{'Name': 'minecraft:stone'}, {'Name': 'minecraft:air'}]
blocks = [(x, 0, z, 0) for x in range(16) for z in range(16)]
blocks += [(x, y, z, 1) for x in range(16) for y in range(1, 10) for z in range(16)]
nbt.write(out, nbt.structure((16, 10, 16), palette, blocks))
print('wrote', os.path.abspath(out))
