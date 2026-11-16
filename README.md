# Celestial Ascent

An endgame ladder past netherite and the Ender Dragon: four Elemental Titans, the Lost Ender Empire, the Fallen Stars, the Abyss, and the Ascendant armor, which outclasses everything, including creative flight. Also adds an economy (Aster coins, banks, player shops, quest boards, growing villages, trade cities). JEI and ProjectE support are optional.

**Minecraft 1.21.1 · NeoForge 21.1.219+ · requires GeckoLib 4.9.3+ · JEI and ProjectE optional**

## Install

1. Install NeoForge 21.1.219 or newer for Minecraft 1.21.1.
2. Put these in `.minecraft/mods`:
   - `celestialascent-<version>.jar` (from `build/libs/` after `./gradlew build`)
   - GeckoLib for NeoForge 1.21.1 (4.9.3 or newer)
   - optional: Just Enough Items (JEI) for 1.21.1, which shows every station recipe, armor evolution, boss summon with its drops and villager trade
   - optional: ProjectE for 1.21.1, which gives every Celestial item an EMC value and adds EMC armor repair

## The ladder

| Step | Where | What you do | What you get |
|---|---|---|---|
| 1. Elemental Titans | Overworld + Nether shrines | Craft an Elemental Sigil, use it on the shrine altar, defeat the titan | Titan Cores, Titan Shards → **Titan armor** (Titan Forge: netherite piece + core + 4 shards) |
| ★ Ender Dragon | The End | Kill it | Every player nearby gets a **Dragon Heart** |
| 2. Lost Ender Empire | Ruined Capital, outer End islands | Beat the Sentinel Constructs; restore the 3 Imperial Pylons (4 Imperial Plating + 16 purpur + 3,000 ✦ each); offer a Dragon Heart to the Empty Throne | Imperial Forge, an Ender Merchant, the **Ender Colossus** → Colossus Core + Imperial Seal → **Imperial armor** |
| 3. Fallen Stars | Star Gate, outer End (use the Star Compass to find it) | Put a Dragon Head on the pedestal, present the Imperial Seal, and step through. Offer 16 Stardust at a sanctum altar | Astral Seraph, Nebula Leviathan, then the Sun Herald → Dormant Star Cores. Charge them in a **Sky Altar** at night → **Stellar armor** |
| 4. The Abyss | Fall off the bottom of the Fallen Stars (after beating the Sun Herald) | Mine Void Essence while the ground crumbles under you; use an Abyssal Beacon below y=40 | **Void Sovereign** (3,000 HP) → Void Heart → **Void armor** (Void Infuser) |
| ★ Ascendant | Ascension Altar | Void piece + Primordial Core + Star Core (+ Void Heart for the chest) | **Ascendant armor** |

Every boss kill adds a **constellation** to your night sky and gives a small permanent bonus.

### Three stages

Every boss evolves twice, at 66% and at 33% of its health: new model parts grow out of it (crowns, horns, extra wings and arms), its body darkens with glowing veins in its element's colour, and new attacks unlock. A banner slides in to name the new stage. The boss bar is Celestial Ascent's own: a frame in the boss's colour, notches at the stage thresholds, a trail of recently lost health, three stage gems and the stage name. In the third stage each boss has an ultimate attack of its own, and the action bar tells you how to survive it:

| Boss | Stage 2 | Stage 3 | Ultimate |
|---|---|---|---|
| Frost Titan | Glacial Wrath | Absolute Zero | standing still freezes you: keep moving |
| Tide Titan | Rising Tide | Tsunami | a wall of water rolls across the arena: jump it |
| Storm Titan | Gathering Storm | Tempest | an expanding ring of lightning with two drifting gaps |
| Magma Titan | Molten Core | Cataclysm | six fissures erupt, then six more, turned |
| Sentinel Construct | Overclocked | Overload | an ankle-high beam sweeps once around: jump it |
| Ender Colossus | Rift Walker | Gravity Collapse | gravity well |
| Astral Seraph | Radiant Wings | Crystal Choir | three star crystals heal it until you break them |
| Nebula Leviathan | Starving Deep | Devourer of Stars | inhales everything toward its maw, then bites |
| Sun Herald | Eclipse | Supernova | find cover |
| Void Sovereign | The Deep Calls | The Unmaking | the Abyss collapses |

## Armor evolution

Every armor piece evolves through three stages:

1. **Resonance:** fight while wearing it. Each monster you defeat gives every worn piece a third of its health in resonance; a boss gives half of its health to everyone at the fight. Stage II needs 600, stage III 1,800.
2. **Completion:** put the resonating piece in its set's station with a boss material.

| Set | Station | To stage II | To stage III |
|---|---|---|---|
| Titan | Titan Forge | core of the piece's own element + 3 Titan Shards | 2 cores + 6 shards |
| Imperial | Imperial Forge | 3 Imperial Plating + 2 Ender Gears | Colossus Core + 3 Gears + 3 Plating |
| Stellar | Sky Altar (night) | 12 Stardust | Star Core + 16 Stardust |
| Void | Void Infuser | 8 Void Essence | Primordial Core + 12 Void Essence |
| Ascendant | Ascension Altar | Star Core + 16 Void Essence | Primordial Core + Star Core + Dragon Heart |

Each stage adds armor and toughness and shows new parts on the armor. A full set counts as its lowest piece's stage and strengthens its ability: Titan elements one level higher and then permanent Resistance; Imperial blink 16 and then 20 blocks with an arrival shockwave; Stellar Regeneration II and then falling stars that strike attackers; Void dash every 3 and then 2 seconds, tearing through monsters; Ascendant faster blink and dash, then regeneration for allies nearby. Upgrading a piece into the next set starts its evolution over.

## The Celestial Codex

Every player gets the **Celestial Codex** the first time they join (craft another from a book and an amethyst shard). Its first page shows your next step, worked out from the bosses you have defeated, and a click takes you to the right chapter. Twelve chapters explain every step with the real crafting and station recipes. The whole mod, codex included, is translated into German.

## Existing worlds

Minecraft only builds structures while it generates new land, so in a world you played before installing the mod, explored land would never get a shrine. Celestial Ascent builds them in afterwards, at the same spots a new world would use:

- Around every player who logs in (40 chunks by default) and in every older chunk that loads, it checks the structure grid, a few cells at a time in the background.
- A spot is skipped if anything player-made is there or close by (chests, beds, planks, glass, torches, redstone, crafting stations…), if another structure is in the way, if players spent more than 30 minutes in that chunk, or if the ground is too steep. The structure is then built on a free spot nearby instead, or not at all in that cell.
- Nothing is built while a player is within about 24 blocks, so nobody gets walled in.
- Structures built late are registered like normal ones: Titansmith maps, the Star Compass and `/locate` find them.

### Titan elements

Each Titan armor piece carries one element. With a full set, an element on one piece is level I and on two or more pieces is level II.

- **Frost:** freeze immunity, frost walking, attackers are slowed (II: frozen)
- **Tide:** water breathing, fast swimming (II: dolphin's grace, underwater night vision)
- **Storm:** speed (II: lightning strikes back at attackers)
- **Magma:** fire immunity (II: walk on lava, burn attackers)

You can re-infuse a piece with a different element at the Titan Forge (core + 2 shards).

### Ascendant armor (full set)

- Creative flight, +10 hearts, +6 attack damage, +25% speed, +2 reach, faster mining
- Immune to fire, lava, falling, drowning, freezing, wither and the void
- Never hungry, constant Regeneration II, unbreakable
- All four titan elements at level II
- **H:** Ender Blink · **Sneak+H:** Void Dash · **G:** toggle night vision

## Economy

- **Aster coins:** Copper 1 · Silver 10 · Gold 100 · Titan 1,000 · Ender 10,000 · Star 100,000 · Void 1,000,000. Craft any coin into 10 of the tier below. To combine small coins into big ones, deposit them at a Bank Counter and withdraw the bigger coins.
- **Bank Counter:** deposit and withdraw. Your balance survives death and works at every bank.
- **Shop Stall:** stock it and set a price. Buyers pay with coins or their bank balance, and you're paid into your bank even while offline. Unclaimed stalls in trade cities can be rented for 100 ✦ (sneak + right-click).
- **Quest Board:** three delivery quests per day. They pay coins and raise the village's prosperity, and at each prosperity threshold the village constructs a new building.
- **New villager jobs:** Banker (Bank Counter), Titansmith (Titan Anvil; sells maps to shrines), Relic Dealer (Relic Pedestal; trade cities and the Ender Empire).
- **Trade Cities:** rare walled cities on flat land, built in the style of their biome (plains, desert, savanna, taiga, snowy). Inside: the Star Spire crowned by a floating Celestial Crystal, a quartz bank with two Bankers, a market hall with 8 rentable stalls, a relic pavilion, the Titansmith's forge, an inn and quest boards. Roads lead out to farms, a windmill, a stable and houses.
- **Celestial Crystal:** a decoration block that floats, turns and gives full light (4 amethyst shards, a gold ingot, glowstone dust).

## Keys

- **H:** armor ability
- **G:** armor toggle

Both can be rebound under *Options → Controls → Celestial Ascent*.

## Config (`config/celestialascent-common.toml`)

You can tune boss health and damage, how much health bosses gain per extra player (default +50% each), the share of damage a player must deal to get loot, Abyss crumble speed, the emerald→coin rate, ProjectE EMC repair, whether new players get the codex, and the existing-world options (`buildIntoExploredLand`, `checkRadiusChunks`, `avoidChunksVisitedMinutes`).

## Development

- `./gradlew build`: build the jar
- `./gradlew runGameTestServer`: run the automated tests
- `./gradlew runData`: regenerate models, loot tables, recipes, tags, language and EMC values
- `python tools/art/build_all.py`, `tools/art/*/build_all.py`: regenerate the art
- `python tools/make_*.py`: regenerate structures and dimensions
- `./gradlew runClient -Pshowcase`: scripted screenshot tour of `run/saves/devworld` (`-PshowcaseOnly=<regex>` for some shots)
- `python tools/split_floating.py`: split the floating tops off altar models after regenerating the art
- `python tools/art/bosses/gen_stages.py`: regenerate the stage 2/3 boss textures
- Existing-world test: `./gradlew runServer -PnoStructures -PserverWorld=retroworld` makes a world without this mod's structures (`/celestialascent retrogen pregen <r>`), then run normally with `-PretrogenPaused` and use `/celestialascent retrogen hut|scan|run|status`
