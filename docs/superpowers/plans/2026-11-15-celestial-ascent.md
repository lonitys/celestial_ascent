# Celestial Ascent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Celestial Ascent mod described in `docs/superpowers/specs/2026-11-15-celestial-ascent-design.md`, stage by stage, each stage playable and tested.

**Architecture:** One NeoForge mod (`celestialascent`) with shared frameworks (`boss`, `armor`, `progress`) and content modules (`economy`, `titans`, `empire`, `stars`, `abyss`). Each module owns its registry class and datagen providers. Art is produced by Python generators in `tools/art/` into `src/main/resources/assets`.

**Tech Stack:** Java 21, NeoForge 21.1.219+ (MC 1.21.1), ModDevGradle 2.0.148, Parchment 2024.11.17, GeckoLib 4.9.3, Python 3 + Pillow/numpy for art, NeoForge GameTest for tests.

**Execution note:** executed inline by the same agent that wrote the spec, so code lives in the source tree rather than being duplicated here. Every task lists exact files, the interfaces it exposes, and how it is verified.

---

**Status (2026-11-15):** Stages 0–6 implemented. 32/32 GameTests pass (incl. AI fights for all 10 bosses);
all 10 structures verified in a generated world (`/celestialascent verify`); in-game screenshot tour reviewed
(`./gradlew runClient -Pshowcase`). Release jar: `./gradlew build` → `build/libs/`.

## File structure (locked)

```
src/main/java/com/celestialascent/
  CelestialAscent.java            @Mod entry; wires module registries + listeners
  core/ModConfig.java             ModConfigSpec (boss scaling, crumble speed, economy prices)
  core/Net.java                   payload registration
  core/datagen/*.java             DataGen entry + providers (models, lang, loot, recipes, tags, EMC)
  progress/Progress.java          attachment record: Set<ResourceLocation> bosses, codec, sync
  progress/ProgressEvents.java    copy on death, login sync, constellation bonuses
  boss/CelestialBoss.java         base boss entity (bar, phases, scaling, loot, anti-cheese)
  boss/BossLoot.java              per-player loot helper
  armor/CelestialArmorItem.java   GeckoLib armor item with tier + set id
  armor/ArmorSets.java            set detection (full set worn?) + ability dispatch
  armor/ArmorTiers.java           ArmorMaterial registrations
  armor/client/*.java             GeoArmorRenderer + model
  economy/Coins.java              coin items + values + exchange math
  economy/Bank.java               SavedData UUID->long
  economy/BankCounterBlock.java   + menu/screen
  economy/ShopStallBlock.java     + block entity, menu/screen
  economy/Professions.java        POI + professions + trades
  titans/... empire/... stars/... abyss/...
tools/art/                         python generators (textures, geo, animations)
src/main/resources/data/celestialascent/structure/empty.nbt   gametest template
```

## Stage 0 — Scaffold and frameworks

### Task 0.1: Gradle project
**Files:** `build.gradle`, `settings.gradle`, `gradle.properties`, `gradle/`, `gradlew*` (copied from jjk_mod), `src/main/templates/META-INF/neoforge.mods.toml`
- [ ] Copy wrapper + build files from `C:\modwork\jjk_mod`; set `mod_id=celestialascent`, `mod_name=Celestial Ascent`, `mod_group_id=com.celestialascent`.
- [ ] Add GeckoLib repo `https://dl.cloudsmith.io/public/geckolib3/geckolib/maven/` and `implementation "software.bernie.geckolib:geckolib-neoforge-1.21.1:4.9.3"`; mods.toml dependency (required) on geckolib, optional on projecte.
- [ ] Verify: `./gradlew compileJava` → BUILD SUCCESSFUL.

### Task 0.2: Entry, config, GameTest harness
**Files:** `CelestialAscent.java`, `core/ModConfig.java`, `test/SmokeTests.java`, `data/.../structure/empty.nbt` (written by `tools/make_empty_structure.py`)
- [ ] Write failing gametest `SmokeTests.modLoads` asserting a registered item exists.
- [ ] `./gradlew runGameTestServer` → fails (item missing). Implement registration. → passes.
- [ ] Commit.

### Task 0.3: Progression attachment
**Files:** `progress/Progress.java`, `progress/ProgressEvents.java`, `test/ProgressTests.java`
- Interface: `Progress.get(Player)`, `Progress.recordKill(ServerPlayer, ResourceLocation bossId)` returns true if new; `Progress.has(Player, id)`.
- [ ] Test: record kill → has() true, second record returns false; survives `copyOnDeath`.

### Task 0.4: Boss framework
**Files:** `boss/CelestialBoss.java`, `boss/BossLoot.java`, `test/BossTests.java`
- Interface: abstract `bossId()`, `baseMaxHealth()`, `phaseThresholds()`, `onPhaseChange(int)`, `barColor()`; static `scaledHealth(base, players, perPlayer)`.
- [ ] Tests: `scaledHealth(400,1,0.5)=400`, `(400,3,0.5)=800`; damage tracking awards loot only to ≥5% contributors; kill records progression.

### Task 0.5: Armor framework
**Files:** `armor/ArmorTiers.java`, `armor/CelestialArmorItem.java`, `armor/ArmorSets.java`, `armor/client/CelestialArmorRenderer.java`
- Interface: `ArmorSets.wearingFullSet(LivingEntity, SetId)`; `CelestialArmorItem(Holder<ArmorMaterial>, Type, SetId)`.
- [ ] Test: equip full titan set on a mock player → true; remove boots → false.

### Task 0.6: Datagen + EMC provider
**Files:** `core/datagen/DataGen.java`, `ModelGen.java`, `LangGen.java`, `LootGen.java`, `RecipeGen.java`, `EmcGen.java`
- [ ] `./gradlew runData` produces `data/projecte/pe_custom_conversions/celestialascent.json` with `values.before` entries for every registered item that has an EMC value.

## Stage 1 — Economy core
- 1.1 Coins (7 items, exchange recipes 10↔1, values) — test `Coins.valueOf`, `Coins.breakdown(long)` greedy split.
- 1.2 Bank SavedData — tests deposit/withdraw/insufficient funds.
- 1.3 Bank Counter block + menu + screen (deposit carried coins, withdraw by denomination).
- 1.4 Professions: Banker, Titansmith, Relic Dealer POIs/workstations + coin trades — test POI registered, trades non-empty.
- 1.5 Shop Stall block entity + menu: owner config, purchase with coins or bank — tests purchase transfers item and credits owner.
- 1.6 Art: coin, block textures. Client screenshot check.

## Stage 2 — Elemental Titans
- 2.1 Titan materials (shards, cores ×4, sigils ×4) + recipes + EMC.
- 2.2 Shrine altar block + four shrine structures (worldgen structure + template sets, biome tags).
- 2.3 Titan entities ×4 (GeckoLib) on boss framework, attacks per phase.
- 2.4 Titan Forge block + menu + recipe logic (netherite piece + core + 4 shards → titan piece with element component).
- 2.5 Titan armor + element abilities (levels I/II) — tests for ability resolution.
- 2.6 Art: titan models/animations/HD textures; titan armor model; shrine blocks.

## Stage 3 — Dragon Heart + Ender Empire
- 3.1 Dragon Heart drop via `LivingDeathEvent` on EnderDragon for participating players.
- 3.2 Imperial Pylon block + restoration menu (Dragon Heart awaken, material/coin cost, unlocks).
- 3.3 Ruined Capital structure on outer End islands.
- 3.4 Sentinel Construct mini-boss, Ender Colossus boss.
- 3.5 Imperial Forge + Imperial armor + blink ability.
- 3.6 Ender Merchant trader.

## Stage 4 — Fallen Stars
- 4.1 Dimension + dimension type + custom sky effects + starstone island generation.
- 4.2 Star Gate structure, Star Compass, pedestal activation, portal teleport.
- 4.3 Celestials ×3, Dormant Star Core.
- 4.4 Sky Altar charging + Stellar armor.
- 4.5 Constellation sky renderer + permanent bonuses.

## Stage 5 — Abyss + finale
- 5.1 Abyss dimension + layered generation + rifts.
- 5.2 Crumbling abyssal blocks (depth bands).
- 5.3 Void Essence, Void Wraith mob, Void Sovereign boss.
- 5.4 Void Infuser + Void armor; Ascension Altar + Ascendant armor (creative flight etc.).
- 5.5 ProjectE EMC auto-repair (reflection).

## Stage 6 — Villages and cities
- 6.1 Quest Board + quests.
- 6.2 Village prosperity + growth placement.
- 6.3 Trade city structure.

## Verification per stage
`./gradlew build` and `./gradlew runGameTestServer` both green; headless/client run checks listed in each task; commit at end of each task.
