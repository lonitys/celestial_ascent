# JEI Support and the New Trade City — Design

Date: 2026-11-16
Builds on: `2026-11-15-celestial-ascent-design.md` (release 1.0.0)

## 1. Goal

1. Celestial Ascent works with **Just Enough Items (JEI)**. Everything a player can make or get from the
   mod can be found with JEI, including the recipes that today exist only in code.
2. The **trade city** is rebuilt: bigger, more detailed and good-looking. It sits well in the terrain and
   matches its biome, with landmarks in the mod's celestial style.

## 2. Decisions

| Topic | Decision |
|---|---|
| JEI | Optional dependency; native JEI plugin; the mod works the same without JEI |
| City style | Buildings match the biome; celestial landmarks (star spire with a floating crystal, quartz and gold bank) |
| City layout | Walled core as one rigid piece, roads and outskirts as jigsaw pieces that follow the terrain |
| Old cities | Cities already generated in a world stay as they are |
| Out of scope | EMI/REI plugins, rebuilding existing cities |

## 3. JEI

### 3.1 Dependency

- `compileOnly` JEI API `mezz.jei:jei-1.21.1-neoforge-api:19.70.0.469`. In dev runs, add `runtimeOnly` for the full
  `jei-1.21.1-neoforge` (maven.blamejared.com).
- `neoforge.mods.toml`: optional dependency `jei`, `versionRange="[19.0,)"`, side BOTH.
- The plugin lives in `compat/jei/` and carries `@JeiPlugin`. No other class refers to it, so without JEI
  nothing is loaded.

### 3.2 Display data for station recipes

`StationRecipe` has a base predicate and a result function, so JEI cannot list it on its own. Each recipe
also gets **display examples**: rows of base stack, material stacks and result stack.

- Simple upgrades show the base item and the computed result.
- Titan element changes show one row per element.
- Armor evolution shows the piece at stage N with full resonance and the piece at stage N+1.

Examples are built when they are first asked for, because items exist only after registration. A GameTest
checks that every example matches its recipe.

### 3.3 Categories

1. **One category per station** (Titan Forge, Imperial Forge, Sky Altar, Void Infuser, Ascension Altar).
   - The background is cut from the station's own GUI texture (slots, arrow, output), so a recipe looks
     like the station in game.
   - A footer line shows the processing time. The Sky Altar adds "at night, under open sky". Evolution
     recipes add "needs full resonance (600 / 1800)".
   - Catalyst: the station block.
   - Recipe transfer: the + button moves the items into the station's slots.
2. **Boss summoning**: one entry per boss, 10 bosses plus the Ender Dragon.
   - Inputs: the altar or throne block and the offering with its count. The Ender Dragon has no inputs.
   - In the middle: the animated boss model, turning slowly. Its tooltip shows the boss's health and where
     to find it.
   - Outputs: the boss's drops. A **shared `BossDrops` table in code** feeds both datagen (loot tables) and
     JEI, because loot tables are not on the client in multiplayer.
   - So "U" on a Titan core shows which boss drops it.
3. **Villager trades**: one category per profession (Banker, Titansmith, Relic Dealer).
   - Each row shows costs → result and the villager level.
   - `Professions` records a display entry next to each trade listing.
   - Catalyst: the profession's workstation.
4. **Information pages** (JEI's info tab) for things no recipe explains:
   - the coins, with exchange and bank
   - the Dragon Heart (drops from the Ender Dragon)
   - the dormant star core
   - the shop stall, quest board and bank counter
   - the Celestial Codex
   - armor pieces (resonance and evolution)
   - the new Celestial Crystal (3.5)
5. Technical blocks (for example cooled magma and portal blocks) are hidden from the JEI item list.

All JEI text exists in English and German. `LangGen`/`LangGenDe` fail the build if a key is missing.

## 4. The new trade city

### 4.1 Structure

- A custom structure type `celestialascent:city`:
  1. Samples the ground under the core footprint on a 9×9 grid.
  2. Rejects the spot if the height spread is over 6 blocks or over 20 % of the samples are water or lava.
  3. Starts at the median height.
  4. Builds the pieces with `JigsawPlacement`, as vanilla does.
- **Core** (about 63×63, rigid, up to about 32 tall):
  - A foundation skirt reaches 5 blocks down, so slopes are filled instead of cut.
  - `terrain_adaptation: beard_thin`
- **Outskirts** (jigsaw from the four gates):
  - Depth 4, `max_distance_from_center` 112.
  - Road pieces use `terrain_matching`; buildings are `rigid`.
- Templates come from a new `tools/make_city.py`. The trade city part of `make_villages.py` moves there.

### 4.2 Core contents

- **Walls**:
  - 3 thick, with a walkway and crenellations.
  - Four corner towers with pointed roofs.
  - Four gatehouses with arches and iron-bar portcullises, plus banners and lanterns.
- **Central plaza**:
  - The **Star Spire**: a quartz, gold and lapis tower about 26 tall, crowned by the floating, turning
    **Celestial Crystal**.
  - A fountain ring, benches, planters with trees and flowers, and 2 quest boards.
- **Bank**:
  - Quartz columns and gold trim.
  - A vault behind iron bars with gold blocks.
  - 2 bank counters and 2 bankers.
- **Market hall**: covered, with **8 rentable shop stalls** under awnings of different colours.
- **Relic pavilion**: purpur, end stone and amethyst, with the floating relic pedestal and the relic dealer.
- **Titansmith forge**: a chimney, anvils, a blast furnace, lava and the titansmith.
- **Inn**: a bar and 4 beds upstairs that players can sleep in.
- **Housing and guards**:
  - 4 houses with furnished interiors.
  - A guard barracks with 2 iron golems.
  - Gardens.
- **Villagers**: the 4 above plus 4 villagers, each with a free workstation nearby.

### 4.3 Outskirts

- Roads: straight pieces, bends and T-junctions, 3 wide, with lamp posts.
- Side pieces: 2 farm types, a windmill, a stable, 3 small houses, a well, a watchtower and an orchard.

### 4.4 Biome variants

The layout is the same everywhere; `make_city.py` swaps the block palette per variant:

| Variant | Biomes | Materials |
|---|---|---|
| `trade_city` (keeps the old ID) | plains, sunflower plains, meadow | stone bricks, oak, cobblestone |
| `trade_city_desert` | desert | sandstone, cut sandstone, terracotta, birch |
| `trade_city_savanna` | savanna, savanna plateau | acacia, terracotta, mud bricks |
| `trade_city_taiga` | taiga, old growth taiga | spruce, cobblestone, mossy stone bricks |
| `trade_city_snowy` | snowy plains, snowy taiga | spruce, stone bricks, blue ice accents, snow on roofs |

- Every variant keeps the celestial accents: quartz, gold, lapis and light blue glass, amethyst and end rods.
- All five structures share one structure set: `random_spread` with spacing 48 and separation 20, rarer than
  today because the city is bigger.
- The structure tag `celestialascent:trade_city` lists all five, so maps, `/locate` and the Star Compass keep
  working.

### 4.5 Celestial Crystal

- A decorative block. It floats and turns using `FloatingRenderer`, gives light level 15 and drops itself.
- Recipe: 4 amethyst shards, 1 gold ingot and 1 glowstone dust.
- The codex economy chapter mentions it.

### 4.6 Existing worlds

- Retrogen tries each structure of the set and uses the first one whose biome fits. Today it only takes
  the first entry.
- Cities that already generated stay unchanged.
- The codex economy chapter describes the new city, in English and German.

## 5. Testing

- **GameTests**:
  1. Every station recipe's display examples match the recipe and give a non-empty result.
  2. Each `BossDrops` entry equals the items in the boss's generated loot table.
  3. Every trade display is non-empty.
  4. Each city variant's core template loads and contains at least 2 bank counters, 8 shop stalls,
     2 quest boards, a relic pedestal, a Celestial Crystal and 4 beds.
  5. The custom structure type rejects a steep test site.
- **Visual check in a dev run with JEI**:
  - Showcase screenshots of each JEI category, opened through the JEI runtime.
  - Each city variant placed with `/place structure`, on flat land and on natural terrain.
- **Retrogen**: a run in `retroworld` places a city variant.
