# Celestial Ascent — Design

Date: 2026-11-15
Mod id: `celestialascent` · Package: `com.celestialascent`
Platform: Minecraft Java 1.21.1, NeoForge 21.1.219 or newer, Java 21
Location: `C:\modwork\celestial_ascent`

## 1. Goal

A large content mod that adds a four-step endgame ladder beyond netherite and the Ender Dragon, a final
armor set that outclasses ProjectE gem armor (creative flight included), and an economy layer (coins, bank,
new villager professions, player shops, trade cities, growing villages). Works in singleplayer and
multiplayer. ProjectE is optional: when present, every mod item has an EMC value and extra EMC features
switch on.

## 2. Decisions (from brainstorming)

| Topic | Decision |
|---|---|
| Scope | Everything designed together, built in playable stages |
| ProjectE | Optional; EMC values + extras only when installed |
| Themes | All four, as a ladder: Titans → (Dragon) → Ender Empire → Fallen Stars → Abyss |
| Art | 16x textures for blocks/items; HD (2x density) for armor and bosses |
| Players | Singleplayer and multiplayer (boss scaling, per-player loot, player shops) |
| Villages | Upgrade vanilla villages AND rare trade cities |
| Money | Physical coins AND bank balance |
| Architecture | One mod, internal modules, shared frameworks |

## 3. Architecture

Dependencies: **GeckoLib 4.9.x** (required; animated bosses, 3D armor). **ProjectE** (optional; EMC via
`data/projecte/pe_custom_conversions/celestialascent.json`, ignored when absent). JEI/EMI optional later.

Packages:

- `core` — mod entry, registries (DeferredRegister per module), config, networking, data generation.
- `boss` — shared boss framework (see 3.1).
- `armor` — shared armor framework (see 3.2).
- `progress` — per-player progression attachment: bosses defeated, constellations, keys. Synced to client.
- `titans`, `empire`, `stars`, `abyss` — step content. Depend only on shared frameworks, never on each other
  (except item references for keys/recipes through registry objects).
- `economy` — coins, bank, professions, shops, village growth, trade city.
- `compat.projecte` — EMC data generation (always generated; harmless without ProjectE).

Data generation produces item/block models, blockstates, loot tables, recipes, tags, lang, EMC JSON.
Art assets (GeckoLib geo/animation JSON and PNG textures) are produced by generator tools in `tools/`
and committed.

### 3.1 Boss framework

`CelestialBoss` abstract entity (extends `Monster`, implements `GeoEntity`):

- `ServerBossEvent` health bar, coloured per step.
- Phases: boss defines phase thresholds (fractions of max HP). Entering a phase triggers a transition
  (brief invulnerability + animation) and switches the attack set.
- Multiplayer scaling: on spawn and every 5 s, max HP = base × (1 + `scalePerPlayer` × (n − 1)) where n
  = players within 64 blocks (config, default 0.5). Current HP keeps its fraction.
- Per-player loot: every player who dealt ≥ 5% of max HP gets the boss loot dropped at their feet, owned
  by them for 30 s.
- Anti-cheese: immune to suffocation, drowning, fall, cactus, and `inWall`; teleports to its target if the
  target is out of reach for 8 s (pillaring, holes); cannot ride vehicles; no knockback below phase 2.
- Arena: a boss summoned at a shrine remembers its home and leashes back if dragged > 48 blocks away.
- On death: records the kill in every participating player's progression (constellation unlock).

### 3.2 Armor framework

- `CelestialArmorItem` (GeckoLib 3D armor renderer, HD texture) with tier stats.
- Set bonus = abilities granted when all four pieces of a set are worn. Abilities are small classes
  (`ArmorAbility`) ticked server-side; toggles bound to keys (default: `G` toggle ability menu, `H`
  primary ability) sent via network payload.
- Creative flight via NeoForge `NeoForgeMod.CREATIVE_FLIGHT` attribute modifier.
- Armor pieces carry data components (e.g. titan element) used by abilities and render tint.

Armor stats (vanilla netherite: 3/8/6/3, toughness 3, KB 0.1, durability multiplier 37):

| Set | Def (helm/chest/legs/boots) | Toughness | KB res | Durability mult |
|---|---|---|---|---|
| Titan | 4/9/7/4 | 4 | 0.15 | 45 |
| Imperial | 4/10/8/4 | 5 | 0.2 | 55 |
| Stellar | 5/10/8/5 | 6 | 0.25 | 70 |
| Void | 5/11/9/5 | 7 | 0.3 | 90 |
| Ascendant | 6/12/9/6 (armor attribute caps at 30) | 10 | 0.5 | unbreakable |

## 4. The ladder

### Step 1 — Elemental Titans (Overworld + Nether, harder than netherite gear, easier than Dragon)

- **Shrines**: four structures, one per titan, generated in their biome: Frost (frozen peaks / ice
  spikes), Tide (deep ocean, underwater ruin), Storm (windswept/jagged peaks), Magma (Nether basalt
  deltas). Each has an altar block.
- **Summoning**: right-click the altar with an **Elemental Sigil** (crafted: netherite scrap + biome item:
  blue ice / heart of the sea / lightning rod + amethyst / magma cream + blaze rod). Shrine altar cools
  down 10 min after a summon.
- **Titans** (base HP): Frost 400, Tide 450, Storm 500, Magma 600. Each two phases with unique attacks
  (ice spikes/slow; water jets/whirlpool pull; lightning strikes/wind knockback; fire meteors/lava pools).
- **Drops**: 1 Titan Core of its element + 3–5 Titan Shards.
- **Hunt-and-fuse**: **Titan Forge** block. Input: a netherite armor piece + a Titan Core + 4 Titan Shards
  → Titan armor piece infused with that core's element. Set abilities are the elements across the four
  pieces; an element on 2+ pieces is level II.
  - Frost: immune to freezing, walk on water (frost walker), attackers get Slowness (II: freeze).
  - Tide: water breathing, fast swimming (II: dolphin's grace + night vision underwater).
  - Storm: +speed (II: chance to strike attackers with lightning).
  - Magma: fire immunity (II: walk on lava, set attackers on fire).

### Ender Dragon

On each kill every participating player receives a **Dragon Heart** (once per player kill, via
progression). Dragon Heart unlocks the Empire's restoration and is part of the Star Gate key.

### Step 2 — Lost Ender Empire (outer End islands)

- **Ruined Capital**: large structure on outer End islands (≥ 1000 blocks from 0,0), with broken
  **Imperial Pylons**.
- **Rebuild**: right-click a pylon with a Dragon Heart once to awaken it; then each pylon needs
  materials + coins to restore (Restoration menu). Restoring pylons unlocks in order: Imperial Forge,
  Ender Merchant (trader), Throne Hall gate.
- **War machines**: **Sentinel Construct** (mini-boss, 300 HP, guards each pylon district) drops
  Imperial Plating + Ender Gears. **Ender Colossus** (boss, 900 HP, three phases) in the Throne Hall
  drops **Colossus Core** + the **Imperial Seal**.
- **Salvage**: Imperial Forge assembles Imperial armor: Titan armor piece + Imperial Plating + Ender Gears
  (+ Colossus Core for chestplate). Set ability: short-range ender blink (H key, 5 s cooldown), immune to
  endermen aggro, reach +1.

### Step 3 — Fallen Stars (new dimension)

- **Star Gate**: rare structure on outer End islands; located with a **Star Compass** (Dragon Heart +
  compass + ender eyes). Activation: place a Dragon Head on the gate pedestal and use the Imperial Seal.
- **Dimension** `celestialascent:fallen_stars`: floating islands of starstone in a star-filled void,
  permanent night, custom sky.
- **Celestials** (bosses): **Astral Seraph** 1200 HP (flying, fast), **Nebula Leviathan** 1400 HP
  (serpentine, void-swimming), **Sun Herald** 1600 HP (three phases, solar flares). Each drops a
  **Dormant Star Core**.
- **Charge under the stars**: **Sky Altar** in the Overworld; at night with open sky, a Dormant Star Core
  charges over one in-game night into a **Star Core**. Stellar armor = Imperial piece + Star Core +
  Stardust at the altar. Set ability: slow-fall glide, regeneration at night, night vision.
- **Constellations**: every boss kill (all 10 bosses incl. Dragon) adds a constellation to that player's
  night sky and a small permanent bonus (+1 heart, +3% speed, +1 armor, etc.).

### Step 4 — The Abyss (new dimension)

- Entered through **Abyss Rifts** at the bottom of the Fallen Stars islands (fall into one).
- **Dimension** `celestialascent:abyss`: dark layered caverns of abyssal stone. Abyssal blocks near
  players start to crack and then fall; crumble speed increases with depth (three depth bands).
- **Dive and survive**: **Void Essence** found in clusters, more common deeper. Void Wraith mobs.
- **Void Sovereign** (final boss, 3000 HP, four phases) at the bottom; drops the **Void Heart**.
- Void armor = Stellar piece + Void Essence ×8 at the Void Infuser. Set ability: void dash, immune to void
  damage for 5 s after falling into the void (teleport back up).

### Final — Ascendant Armor

- **Ascension Altar**: fuse a full Void set + Void Heart + one Titan Core of each element + Imperial Seal
  + 3 Star Cores → Ascendant armor (4 pieces crafted individually; Void Heart only for chestplate).
- Full-set abilities: creative flight, immunity to fire/lava/drowning/fall/freezing/void (teleport up),
  night vision (toggle), step assist, +speed, no hunger loss, regeneration, all titan level-II effects,
  ender blink. Unbreakable.

## 5. Economy

- **Currency "Aster"** coins: Copper 1, Silver 10, Gold 100, Titan 1 000, Ender 10 000, Star 100 000, Void
  1 000 000. 10 of one tier ↔ 1 of the next by crafting.
- **Bank**: per-player balance (world SavedData, UUID → long). **Bank Counter** block: deposit /
  withdraw menu. Balance persists through death. Usable at any bank counter.
- **Professions** (vanilla villagers): **Banker** (Bank Counter; exchanges emeralds ↔ coins),
  **Titansmith** (Titan Anvil; buys titan materials, sells sigils), **Relic Dealer** (Relic Pedestal;
  sells/buys boss materials for high coins — only spawns in trade cities). Trades priced in coins.
- **Player shops**: **Shop Stall** block. Owner stocks items and sets a price; buyers pay with coins or
  bank balance; owner's balance credited (works while offline).
- **Quest Board**: block in villages; gather/kill/deliver quests paying coins and village prosperity.
- **Village growth**: prosperity per village (SavedData keyed by bell position). At thresholds the
  village builds an addition (house, wall section, market stall) from structure templates, placed a few
  blocks per tick on valid ground near the bell.
- **Trade cities**: rare structure (plains/desert/savanna/taiga), contains bank, market of shop stalls,
  relic dealer, quest board.

## 6. ProjectE (optional)

EMC values (fixed, via `pe_custom_conversions`) — reference: diamond 8 192, netherite ingot 57 344,
red matter 466 944:

| Item | EMC |
|---|---|
| Copper/Silver/Gold Aster | 32 / 320 / 3 200 |
| Titan/Ender/Star/Void Aster | 32 000 / 320 000 / 3 200 000 / 32 000 000 |
| Titan Shard / Titan Core | 250 000 / 2 000 000 |
| Dragon Heart | 5 000 000 |
| Imperial Plating / Ender Gear / Colossus Core / Imperial Seal | 1 500 000 / 1 000 000 / 15 000 000 / 25 000 000 |
| Stardust / Dormant Star Core / Star Core | 800 000 / 20 000 000 / 40 000 000 |
| Void Essence / Void Heart | 5 000 000 / 250 000 000 |
| Titan / Imperial / Stellar / Void armor piece | 12M / 40M / 120M / 250M (×1.6 chest, ×1.4 legs, ×1 helm, ×0.8 boots) |
| Ascendant armor piece | 1 000 000 000 (chest 1 600 000 000) |

Extra when ProjectE is installed: mod armor auto-repairs by drawing EMC from the wearer's transmutation
EMC (reflection-based, so no compile dependency).

## 7. Art pipeline

- Blocks/items: 16x16 PNGs from `tools/` generators, hand-tuned palettes per theme.
- Bosses and armor: GeckoLib `.geo.json` (Bedrock geometry) + `.animation.json` + HD textures, produced
  by generator tools so geometry is precise and reproducible.
- Emissive (glowing) layers via GeckoLib `AutoGlowingGeoLayer` (`*_glowmask.png`).
- Every model is checked in a client run with screenshots before its stage is complete.

## 8. Build stages

0. Scaffold, frameworks (boss, armor, progression), config, datagen, EMC generation.
1. Economy core: coins, bank, Bank Counter, professions & trades, Shop Stall.
2. Step 1 Titans: sigils, shrines, four titans, Titan Forge, Titan armor.
3. Dragon Heart + Step 2 Empire.
4. Step 3 Fallen Stars + constellations.
5. Step 4 Abyss + Void Sovereign + Ascendant armor.
6. Quest Board, village growth, trade cities.

## 9. Testing

- NeoForge GameTests for logic: coin exchange, bank deposit/withdraw, shop purchase, forge recipes,
  set-bonus detection, progression recording, boss scaling.
- Headless server runs (`runServer` with scripted commands) for summoning, worldgen and structure
  placement.
- Client runs with screenshots for models, textures, sky, and armor rendering.
- Each stage ends with build + all tests passing before the next starts.
