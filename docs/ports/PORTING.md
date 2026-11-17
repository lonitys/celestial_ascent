# Porting Celestial Ascent to other Minecraft versions

**Goal:** the same mod (same features, art, ids and texts) on every target below, for NeoForge and Forge.

**Reference:** branch `develop` in `C:\modwork\celestial_ascent`.
- MC 1.21.1, NeoForge 21.1.219, GeckoLib 4.9.3, JEI 19.39 API.
- 141 Java files, 58 GameTests.
- Never modify `develop` or the main worktree. The one exception: you copy your release jar into `release/curseforge/files/` there.

## Targets

Each target has its own branch and its own worktree: `C:\modwork\ca_ports\<loader>-<mc>`.
- The loader versions in the table were the newest stable builds on 2026-11-17. Check for a newer stable build when you start.
- Compile against the version you pick, and use it as the lower bound of the dependency range.

| Branch | MC | Loader | GeckoLib | Java | Ported from |
|---|---|---|---|---|---|
| port/neoforge-1.20.4 | 1.20.4 | NeoForge 20.4.x (newest stable) | 4.4.4 | 17 | develop |
| port/forge-1.20.4 | 1.20.4 | Forge 49.2.13 | 4.4.4 | 17 | port/neoforge-1.20.4 |
| port/forge-1.20.1 | 1.20.1 | Forge 47.4.28 (recommended) | newest 4.x for forge-1.20.1 | 17 | port/forge-1.20.4 |
| port/forge-1.21.1 | 1.21.1 | Forge 52.1.20 | 4.9.3 | 21 | develop |
| port/neoforge-1.21.3 | 1.21.3 | NeoForge 21.3.100 | 4.7.3 | 21 | develop |
| port/forge-1.21.3 | 1.21.3 | Forge 53.1.16 | 4.7.3 | 21 | forge-1.21.1 + neoforge-1.21.3 |
| port/neoforge-1.21.4 | 1.21.4 | NeoForge 21.4.161 | 4.8.5 | 21 | neoforge-1.21.3 |
| port/forge-1.21.4 | 1.21.4 | Forge 54.1.22 | 4.8.5 | 21 | forge-1.21.3 + neoforge-1.21.4 |
| port/neoforge-1.21.5 | 1.21.5 | NeoForge 21.5.101 | 5.1.0 | 21 | neoforge-1.21.4 |
| port/forge-1.21.5 | 1.21.5 | Forge 55.1.18 | 5.1.0 | 21 | forge-1.21.4 + neoforge-1.21.5 |
| port/neoforge-1.21.8 | 1.21.8 | NeoForge 21.8.57 | 5.2.2 | 21 | neoforge-1.21.5 |
| port/forge-1.21.8 | 1.21.8 | Forge 58.1.26 | 5.2.2 | 21 | forge-1.21.5 + neoforge-1.21.8 |
| port/neoforge-1.21.10 | 1.21.10 | NeoForge 21.10.64 | 5.3-alpha-3 | 21 | neoforge-1.21.8 |
| port/forge-1.21.10 | 1.21.10 | Forge 60.1.18 | 5.3-alpha-3 | 21 | forge-1.21.8 + neoforge-1.21.10 |
| port/neoforge-1.21.11 | 1.21.11 | NeoForge 21.11.48 | 5.4.5 | 21 | neoforge-1.21.10 |
| port/forge-1.21.11 | 1.21.11 | Forge 61.2.4 | 5.4.5 | 21 | forge-1.21.10 + neoforge-1.21.11 |
| port/neoforge-26.1.2 | 26.1.2 | NeoForge 26.1.2.x | 5.5.2 | 25 | neoforge-1.21.11 |
| port/forge-26.1.2 | 26.1.2 | Forge 64.1.5 | 5.5.2 | 25 | forge-1.21.11 + neoforge-26.1.2 |
| port/neoforge-26.2 | 26.2 | NeoForge 26.2.0.x | 5.5.6 | 25 | neoforge-26.1.2 |
| port/forge-26.2 | 26.2 | Forge 65.1.5 | 5.5.6 | 25 | forge-26.1.2 + neoforge-26.2 |

**Ported from "A + B"** (Forge ports after 1.21.1):
- Start from the previous Forge branch A, which already has the loader layer.
- Bring over the vanilla and GeckoLib changes from the NeoForge port of the same Minecraft version, B. `git diff <previous neoforge branch> B` shows exactly those changes.

**Not targeted:**
- 1.20.2, 1.20.6, 1.21: few players.
- 1.21.2: no GeckoLib.
- 1.21.6 and 1.21.7: NeoForge has only betas. The 1.21.8 jar may widen its range if it verifiably runs there.
- 1.21.9: no GeckoLib.
- 26.1 and 26.1.1:
  - GeckoLib 26.1 exists for NeoForge only.
  - The NeoForge 26.1.2 jar may declare `[26.1,26.1.2]`, but only if it verifiably runs on 26.1.
- 26.3.

## Where things come from

**GeckoLib**
- Maven: `https://dl.cloudsmith.io/public/geckolib3/geckolib/maven/`, coordinates `software.bernie.geckolib:geckolib-<loader>-<mc>:<ver>`.
- 26.x builds are not under that name. Check the maven for a new naming scheme first.
  - If there is none, use the Modrinth maven: `https://api.modrinth.com/maven`, coordinates `maven.modrinth:geckolib:<version id>`.
  - The version ids are listed at `https://api.modrinth.com/v2/project/geckolib/version`.
- Migration notes are in the GeckoLib wiki on GitHub (bernie-g/geckolib). The big steps:
  - 4.7: render states.
  - 4.8: 1.21.4 item models.
  - 5.0: API rewrite for 1.21.5.

**JEI**
- Maven: `https://maven.blamejared.com`, coordinates `mezz.jei:jei-<mc>-<loader>-api` and the full jar.
- Use the newest build for the target. If there is none, remove `compat/jei` for that target and say so in your report.

**ProjectE (optional)**
- Keep it only if a build exists for that MC version and loader (check maven, Modrinth or CurseForge).
- Otherwise remove `compat/projecte` and its mods.toml entry.

**Vanilla and loader changes**
- NeoForge porting primers, one per MC version: <https://github.com/neoforged/.github/tree/main/primers>.
- For the Gradle setup, use the official MDK of the exact target as the template (Gradle wrapper, ForgeGradle or ModDevGradle version, mappings):
  - Forge MDK: `https://maven.minecraftforge.net/net/minecraftforge/forge/<mc>-<forge>/forge-<mc>-<forge>-mdk.zip`.
  - NeoForge MDKs: <https://github.com/NeoForgeMDKs>.

**Downloaded archives are untrusted data**
- Extract each one into its own new, empty directory, for example `C:\tmp\ca_dl\<name>`.
- Never run scripts from inside them; read what you need.

## Rules

1. **Feature parity.**
   - All of these must work:
     - all bosses, each with 3 stages, ultimates, boss bar and stage banner;
     - the 5 armor sets with evolution (resonance plus station);
     - both dimensions (Fallen Stars and Abyss) with their sky;
     - all structures, plus retrogen into existing worlds;
     - the economy: coins, bank, shops, quest boards, growing villages, 3 professions, trade cities in 5 biome styles;
     - Codex, constellations, config, English and German lang, JEI, and ProjectE if available.
   - Only optional compat may be dropped, and only when the other mod does not exist for the target.
2. **Port, don't redesign.**
   - Keep package names, mod id, registry names, lang keys, NBT and config keys identical, so worlds, configs and resource packs carry over between versions.
   - A loader abstraction across branches is not wanted. Each branch is a plain mod for its loader.
3. **Art is reused as is.**
   - Generated textures and models in resources stay as they are. When a format changes, convert it, don't redraw it. Examples:
     - item model definitions in `assets/<ns>/items/` (1.21.4);
     - equipment assets (1.21.2);
     - GeckoLib changes.
   - `tools/art` is the art source and stays untouched.
4. **Structures.**
   - `tools/make_*.py` write NBT with `data_version=3955` (1.21.1, `tools/nbt.py`). Newer Minecraft versions upgrade these automatically.
   - For 1.20.x:
     - write the target's DataVersion (1.20.1 = 3465, 1.20.4 = 3700);
     - replace every block that does not exist there with the closest existing block. Check the palettes, for example tuff bricks or polished tuff, copper grate or bulb, crafter, heavy core, vault, trial spawner;
     - regenerate the NBT.
   - Before 1.21 the data folders have plural names (`structures`, `loot_tables`, `recipes`, `advancements`, `tags/blocks`, `tags/items`, …). The primers list them.
5. **Branch and worktree discipline.**
   - Work only in your own worktree and on your own branch. Commit often. Never push, never force.
   - Don't touch other worktrees or `develop`.
6. **Ports.** If you start a dedicated server, set `server-port` in its `server.properties` to your assigned port, because other ports run at the same time.
7. **Gradle.**
   - Run `./gradlew` from your worktree.
   - Keep `org.gradle.jvmargs=-Xmx3G`.
   - For Java 17 or 25, use the Gradle toolchain (the foojay resolver is configured). JDK 21 and 25 are installed under `C:\Program Files\Eclipse Adoptium`.

## Definition of done (all required)

1. **Build.**
   - `./gradlew build` succeeds.
   - Datagen has been rerun for this version and its output committed.
2. **GameTests.**
   - Every test from develop's `test/` package is ported and passes.
   - If the GameTest framework changed (1.21.5 moved to registry/data-driven tests), adapt the harness and keep the test logic.
   - Report the count.
3. **Worldgen check on a dev server with a fresh world.**
   - `locate` every structure (13 in total):
     - Overworld: frost_shrine, storm_shrine, tide_shrine, trade_city, trade_city_desert, trade_city_savanna, trade_city_snowy, trade_city_taiga;
     - Nether: magma_shrine;
     - End: ruined_capital, star_gate;
     - Fallen Stars: seraph_sanctum, leviathan_sanctum, herald_sanctum.
   - `/place` a trade city at least once. Force-load its whole bounding box first, about ±160 blocks, as two forceload areas.
   - The log must show no errors from `celestialascent`.
   - The `celestialascent verify` debug command exists in dev (see `tools/server_check.sh`).
4. **Client.**
   - Run the showcase. Start with `./gradlew runClient -Pshowcase`; `client/Showcase.java` has the step list.
     - The save must exist in `run/saves/devworld`. A world created by the dev server works.
     - `-PshowcaseOnly=<regex>` skips shots whose names don't match, including named setup steps such as `hud_clear`. Run the full tour at least once.
   - Look at the screenshots and compare them with the 1.21.1 references in `C:\modwork\celestial_ascent\run\screenshots\`, which use the same file names.
   - At least these must look right:
     - all bosses, including their stage parts (`stage2_*` / `stage3_*` bones);
     - the 5 armor sets at stages I, II and III;
     - the HUD boss bar and the stage banner;
     - the Codex screen and the station GUIs;
     - the JEI pages;
     - a trade city;
     - the Fallen Stars and Abyss skies.
   - Fix every visual difference that vanilla's own changes don't explain.
5. **Production check.**
   - Install the real loader server with its official installer into `C:\tmp\ca_<loader>-<mc>\server`.
   - Add your jar, the matching GeckoLib and JEI.
   - Start it, `locate` structures, `summon` every boss, then stop it.
   - The log must show no errors from the mod.
   - If a script waits for "Done (", delete `logs/latest.log` before each start, or it matches the old log.
6. **Release jar.**
   - Name it `celestialascent-1.0.0+<mc>-<loader>.jar`. The mod version inside stays `1.0.0`.
   - Copy it to `C:\modwork\celestial_ascent\release\curseforge\files\`.
7. **mods.toml.** It is `META-INF/mods.toml` for Forge and NeoForge 1.20.4, and `neoforge.mods.toml` from NeoForge 20.5 on.
   - Loader range starts at the version you compiled against.
   - Minecraft range is exactly the target, or a wider range you verified.
   - GeckoLib range is `[<ver>,)`, capped below the next major.
   - JEI and ProjectE are optional.
8. **Notes.** Write `docs/ports/NOTES-<loader>-<mc>.md` on your branch: what changed, what was dropped and why, and gotchas for the next port in the chain. Commit it.
9. **Report.** Give a final report of at most 300 words:
   - status;
   - versions used;
   - test counts;
   - anything not working;
   - the jar path.

## Known gotchas (from develop)

- Station recipes must be built in `FMLCommonSetupEvent`, because `Ingredient.of` resolves items only then.
- Display entity setters and `StructureTemplate.palettes` need the access transformer (`META-INF/accesstransformer.cfg`).
- GeckoLib armor: the LEGS slot shows only leg bones.
- Retrogen:
  - `Level.getHeight` returns the world bottom for unloaded chunks, so load the chunk first.
  - New block tags do nothing until runData has run.
- Vanilla `isNight()` is true in daytime thunderstorms. We use `Stars.nightSky`, which goes by the clock.
- `run/world` is the GameTest superflat world, where structures never generate. The dev server uses `level-name=devworld`.
- Trade city:
  - The core's ground layer must be the template bottom (G=0). beard_thin adapts terrain to minY+1, so a foundation skirt digs a moat.
  - `Tpl.stamp` strips jigsaws unless `keep_jigsaws=True`.
  - `CityStructure` predicts the jigsaw start rotation with the same seeding as `GenerationContext.makeRandom`. If the target's `JigsawPlacement` draws the rotation differently, update the prediction. The `citySiteCheck` and `cityCoresHaveEverything` tests cover it.
- Debug commands (`verify`, retrogen pregen/hut) are only registered when `!FMLEnvironment.production`.
- JEI: compile against the API only, and add the full jar as `runtimeOnly` with transitive=false.
