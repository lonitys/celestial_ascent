# JEI Support and the New Trade City Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every Celestial Ascent recipe, summon, drop and trade visible in JEI, and replace the trade city with a walled, biome-styled city with terrain-following outskirts.

**Architecture:**
- **JEI.** An optional `@JeiPlugin` in `compat/jei` reads display data that the mod itself owns:
  - station recipe examples on `StationRecipe`
  - `BossDrops` / `BossSummons` tables in `boss/` (also used by loot datagen)
  - trade displays recorded by `Professions`
- **City.** A custom structure type `celestialascent:city`:
  - It checks the terrain under the core, then runs vanilla `JigsawPlacement`.
  - Templates for five biome variants come from a new `tools/make_city.py`.

**Tech Stack:**
- NeoForge 21.1.219, MC 1.21.1, Java 21
- JEI 19.70.0.469 (API compileOnly, full jar in dev runtime)
- GeckoLib 4.9.3
- Python 3 for the template generator (`tools/nbt.py`)

Spec: `docs/superpowers/specs/2026-11-16-jei-and-trade-city-design.md`

**Work split.** Part A (JEI) and Part B (city) touch different files. The only shared files are `LangGen.java`,
`LangGenDe.java` and `Showcase.java`, and each part appends its own block to them. The two parts can run
in parallel, with Part A in a worktree, and be merged afterwards.

**Commands used throughout** (run from the repo root, Git Bash):
- `./gradlew runData` regenerates `src/generated` (lang, loot, models, recipes). Run it after changing datagen
  or adding blocks or items.
- `./gradlew runGameTestServer` runs all GameTests. It must end with `All N required tests passed :)`.
- `./gradlew build` builds the jar.
- `./gradlew runClient -Pshowcase -PshowcaseOnly='<regex>'` runs showcase steps that take screenshots. The PNGs
  land in `run/screenshots/`.

---

## File map

**Part A: JEI**
- Modify `gradle.properties`: add `jei_version=19.70.0.469`.
- Modify `build.gradle`: add the blamejared maven, `compileOnly` for the API, `runtimeOnly` for the full jar.
- Modify `src/main/templates/META-INF/neoforge.mods.toml`: add an optional `jei` dependency.
- Modify `core/station/StationRecipe.java`: add the `examples` component and the `Example` record.
- Modify the recipe registrations, each passing examples:
  - `titans/Titans.java`
  - `empire/Empire.java`
  - `stars/Stars.java`
  - `abyss/Abyss.java`
  - `armor/ArmorStages.java`
- Create `boss/BossDrops.java`: drop table per boss, used by datagen and JEI.
- Create `boss/BossSummons.java`: how each boss is called (inputs, requirement key).
- Modify `datagen/EntityLootGen.java`: build boss tables from `BossDrops`.
- Modify `economy/Professions.java`: record a `TradeDisplay` for every trade.
- Modify `titans/Titans.java`: give shrine-map trades a display.
- Create `compat/jei/CelestialJeiPlugin.java`: categories, recipes, catalysts, transfer, info pages, hiding.
- Create `compat/jei/StationCategory.java`
- Create `compat/jei/SummonCategory.java`
- Create `compat/jei/TradeCategory.java`
- Create `compat/jei/JeiShowcase.java`: opens JEI pages for showcase screenshots.
- Modify `datagen/LangGen.java` and `datagen/LangGenDe.java`: add `jei.celestialascent.*` keys.
- Create `test/JeiDataTests.java`.
- Modify `client/Showcase.java`: add `jei_*` steps.

**Part B: City**
- Create `economy/CelestialCrystalBlock.java`. Register it in `economy/Economy.java`. Add it to the
  `DisplayBlockEntity` valid blocks, to a `FloatingRenderer` spec, and to the datagen classes:
  `BlockStateGen`, `ItemModelGen`, `BlockLootGen`, `RecipeGen`, `LangGen`, `LangGenDe` and `EmcGen` (if the EMC table lists blocks).
- Create the model and texture art through `tools/art/` (follow `gen_economy_blocks.py` and `split_floating.py`).
- Create `retrogen/CityStructure.java`: the custom structure type with the terrain check.
- Modify `core/CAReg.java`: add the `STRUCTURE_TYPES` DeferredRegister and register it on the mod bus.
- Create `tools/make_city.py`. Modify `tools/make_villages.py` to remove `trade_city()` and its JSON from `main()`.
- Generated output:
  - `data/celestialascent/structure/city/<variant>/*.nbt`
  - `worldgen/structure/trade_city*.json`
  - `worldgen/template_pool/city/<variant>/*.json`
  - `worldgen/structure_set/trade_city.json`
  - the biome tags for the variants, and the `trade_city` structure tag
- Modify `retrogen/Retrogen.java`: choose the first structure in the set that generates.
- Modify `retrogen/SiteCheck.java`: set ground offsets for the city variants.
- Modify `guide/GuideChapters.java`: new trade city text and the crystal.
- Create `test/CityTests.java`.
- Modify `client/Showcase.java`: add `city_*` steps.
- Modify `README.md` and `release/curseforge/description.md`, `.html` and `changelog.md`.

---

# Part A: JEI

### Task A1: JEI dependency

**Files:** `gradle.properties`, `build.gradle`, `src/main/templates/META-INF/neoforge.mods.toml`

- [ ] **Step 1: Add the version.** Add `jei_version=19.70.0.469` to `gradle.properties`.
- [ ] **Step 2: Add the repository and dependencies** in `build.gradle`:

```groovy
repositories {
    maven {
        name = 'BlameJared (JEI)'
        url = 'https://maven.blamejared.com/'
        content { includeGroup('mezz.jei') }
    }
}
dependencies {
    compileOnly "mezz.jei:jei-${minecraft_version}-neoforge-api:${jei_version}"
    runtimeOnly "mezz.jei:jei-${minecraft_version}-neoforge:${jei_version}"
}
```

  Also add `jei_version: jei_version` to the `replaceProperties` map used to expand `neoforge.mods.toml`.

- [ ] **Step 3: Add the optional dependency** to `neoforge.mods.toml`, after the ProjectE block:

```toml
[[dependencies.${mod_id}]]
    modId="jei"
    type="optional"
    versionRange="[19.0,)"
    ordering="NONE"
    side="BOTH"
```

- [ ] **Step 4: Verify.** Run `./gradlew compileJava`; expected: `BUILD SUCCESSFUL`. Then run `./gradlew runClient`
  briefly and check that the log contains `jei` loading and no Celestial Ascent errors.
- [ ] **Step 5: Commit** with the message `JEI as optional dependency`.

### Task A2: Display examples on station recipes

**Files:** `core/station/StationRecipe.java`, `titans/Titans.java`, `empire/Empire.java`, `stars/Stars.java`,
`abyss/Abyss.java`, `armor/ArmorStages.java`, `test/JeiDataTests.java`

- [ ] **Step 1: Write the failing test** in `test/JeiDataTests.java`:

```java
@GameTestHolder(CelestialAscent.MODID)
@PrefixGameTestTemplate(false)
public final class JeiDataTests {
    private JeiDataTests() {}

    /** Every station recipe shows at least one example, and each example really is that recipe. */
    @GameTest(template = CoreTests.FLOOR)
    public static void stationExamplesMatch(GameTestHelper h) {
        int n = 0;
        for (StationType type : StationType.all()) {
            for (StationRecipe r : type.recipes) {
                List<StationRecipe.Example> ex = r.examples().get();
                h.assertTrue(!ex.isEmpty(), type.id + ": a recipe without examples");
                for (StationRecipe.Example e : ex) {
                    h.assertTrue(r.matches(e.base(), e.mats()), type.id + ": example does not match its recipe: " + e.base());
                    h.assertTrue(type.find(e.base(), e.mats()) == r, type.id + ": another recipe claims the example " + e.base());
                    h.assertTrue(!e.result().isEmpty(), type.id + ": empty result for " + e.base());
                    n++;
                }
            }
        }
        h.assertTrue(n > 100, "expected well over 100 examples, got " + n);
        h.succeed();
    }
}
```

- [ ] **Step 2: Confirm it fails.** Run `./gradlew compileJava`; expected: it does not compile, because
  `examples()`, `Example` and `StationType.all()` are missing.

- [ ] **Step 3: Implement.**

  `StationRecipe` becomes:

```java
public record StationRecipe(Predicate<ItemStack> base, List<Mat> mats, UnaryOperator<ItemStack> result,
                            Supplier<List<Example>> examples) {
    public record Mat(Ingredient ingredient, int count) { /* unchanged */ }

    /** One concrete case for recipe viewers: a base stack, the material stacks and the result. */
    public record Example(ItemStack base, List<ItemStack> mats, ItemStack result) {}

    /** Examples built from sample base stacks: materials are the first item of each ingredient. */
    public static Supplier<List<Example>> from(List<Mat> mats, UnaryOperator<ItemStack> result, Supplier<List<ItemStack>> bases) {
        return com.google.common.base.Suppliers.memoize(() -> bases.get().stream().map(b -> {
            List<ItemStack> ms = mats.stream().map(m -> m.ingredient().getItems()[0].copyWithCount(m.count())).toList();
            return new Example(b, ms, result.apply(b.copy()));
        }).toList());
    }

    /** The usual way to make a recipe: its examples come from sample base stacks. */
    public static StationRecipe of(Predicate<ItemStack> base, List<Mat> mats, UnaryOperator<ItemStack> result, Supplier<List<ItemStack>> bases) {
        return new StationRecipe(base, mats, result, from(mats, result, bases));
    }
    // matches(...) unchanged
}
```

  Add to `StationType`: `public static Collection<StationType> all() { return BY_ID.values(); }`.

  Call sites, each passing its sample bases:
  - `Titans.recipes()`:
    - Infusion: base `new ItemStack(netherite piece)`.
    - Re-infusion: base `infuse(new ItemStack(netherite piece), out, other)`, where `other` is the next element
      after `e` (`Element.values()[(e.ordinal()+1) % 4]`).
  - `Empire.recipes()`, `Stars.recipes()` (both kinds) and `Abyss.recipes()` (both stations): base `new ItemStack(base item)`.
  - `ArmorStages.recipes()`: base built by a new helper `ArmorStages.sample(Item piece, Element elOrNull, int stage)`.
    It makes a stack and sets `ARMOR_STAGE` to `stage` and `RESONANCE` to `required(stack)`. For titan pieces it
    first calls `TitanArmorItem.setElement(stack, el)`, or whatever helper `infuse` uses.

- [ ] **Step 4: Confirm it passes.** Run `./gradlew runGameTestServer`; expected: `All 53 required tests passed :)`.
- [ ] **Step 5: Commit** with the message `Station recipes carry display examples`.

### Task A3: Shared boss drops and summons

**Files:** create `boss/BossDrops.java` and `boss/BossSummons.java`; modify `datagen/EntityLootGen.java` and
`test/JeiDataTests.java`

- [ ] **Step 1: Write the failing test** in `JeiDataTests`:

```java
/** The drop list JEI shows is exactly what the generated loot table contains. */
@GameTest(template = CoreTests.FLOOR)
public static void bossDropsMatchLootTables(GameTestHelper h) {
    var server = h.getLevel().getServer();
    for (BossDrops.Entry e : BossDrops.all()) {
        var key = e.type().get().getDefaultLootTable();
        LootTable table = server.reloadableRegistries().getLootTable(key);
        Set<Item> inTable = new HashSet<>();
        // Walk pools via an access-free route: roll the table 64 times with max looting and collect items.
        LootParams params = new LootParams.Builder(h.getLevel())
                .withParameter(LootContextParams.THIS_ENTITY, h.makeMockPlayer(GameType.SURVIVAL))
                .withParameter(LootContextParams.ORIGIN, Vec3.ZERO)
                .withParameter(LootContextParams.DAMAGE_SOURCE, h.getLevel().damageSources().generic())
                .create(LootContextParamSets.ENTITY);
        for (int i = 0; i < 64; i++) table.getRandomItems(params).forEach(s -> inTable.add(s.getItem()));
        Set<Item> listed = e.drops().stream().map(d -> d.item().get().asItem()).collect(Collectors.toSet());
        h.assertTrue(inTable.equals(listed), e.type().get().getDescriptionId() + ": JEI lists " + listed + " but the table drops " + inTable);
    }
    h.succeed();
}
```

  Exclude chance-based drops from the equality check: `BossDrops` lists only guaranteed pools, and the wraith is
  not a boss.

- [ ] **Step 2: Confirm it fails.** Run `./gradlew compileJava`; expected: it fails because `BossDrops` is missing.

- [ ] **Step 3: Implement.**

  `BossDrops`:

```java
/** Boss drops in one place: datagen builds the loot tables from it and JEI shows it. */
public final class BossDrops {
    public record Drop(Supplier<? extends ItemLike> item, int min, int max, boolean looting) {}
    public record Entry(Supplier<? extends EntityType<?>> type, List<Drop> drops) {}
    private static final List<Entry> ALL = new ArrayList<>();
    public static List<Entry> all() { if (ALL.isEmpty()) build(); return ALL; }
    public static Optional<Entry> of(EntityType<?> t) { return all().stream().filter(e -> e.type().get() == t).findFirst(); }
    private static Drop fixed(Supplier<? extends ItemLike> i, int min, int max) { return new Drop(i, min, max, false); }
    private static Drop looted(Supplier<? extends ItemLike> i, int min, int max) { return new Drop(i, min, max, true); }
    private static void build() { /* the exact pools from EntityLootGen today */ }
}
```

  `build()` copies today's numbers:
  - **Titans**: core 1, titan shard 3–5 (looting), titan coin 1–3, gold coin 4–9.
  - **Sentinel**: plating 2–4 (looting), gear 1–3 (looting), titan coin 1–2.
  - **Colossus**: colossus core 1, imperial seal 1, gear 3–6 (looting), plating 4–8 (looting), ender coin 1–2,
    titan coin 3–6.
  - **Seraph, Leviathan and Herald**: dormant star core 1, stardust 8–16 (looting), star coin 1, ender coin 2–4.
  - **Sovereign**: void heart 1, void essence 12–24 (looting), void coin 1–2, star coin 3–6.

  `EntityLootGen.generate()` loops `BossDrops.all()` and maps each `Drop` to `fixed(...)` or `looted(...)`.
  The wraith table stays hand-written.

  `BossSummons`:

```java
/** How each boss is called, for recipe viewers. inputs: blocks and offerings; whereKey: a translation key. */
public final class BossSummons {
    public record Summon(Supplier<? extends EntityType<?>> type, List<Supplier<ItemStack>> inputs, String whereKey) {}
    public static List<Summon> all() { /* one per boss, in ladder order, plus the Ender Dragon */ }
}
```

  Entries:
  - **4 Titans**: the titan altar of the element plus its sigil ×1. Where key `jei.celestialascent.where.shrine`.
  - **Sentinel**: the imperial pylon. `where.capital`.
  - **Colossus**: the throne plus the dragon heart ×1. `where.throne`.
  - **Seraph and Leviathan**: their altar plus stardust ×16. `where.fallen_stars`.
  - **Herald**: its altar plus stardust ×16. `where.herald`, which mentions the two earlier kills.
  - **Sovereign**: the abyssal beacon ×1. `where.abyss`.
  - **Ender Dragon**: no inputs. `where.end`. Its drops come from a synthetic entry, `Empire.DRAGON_HEART` ×1, kept
    in `BossSummons` and not in `BossDrops`, because the dragon has a vanilla loot table.

- [ ] **Step 4: Confirm it passes.** Run `./gradlew runData`. `git diff --stat src/generated` must show no
  loot-table change. Then run `./gradlew runGameTestServer`; expected: `All 54 required tests passed :)`.
- [ ] **Step 5: Commit** with the message `Boss drops and summons in shared tables`.

### Task A4: Trade displays

**Files:** `economy/Professions.java`, `titans/Titans.java`, `test/JeiDataTests.java`

- [ ] **Step 1: Write the failing test:**

```java
@GameTest(template = CoreTests.FLOOR)
public static void tradesHaveDisplays(GameTestHelper h) {
    for (var prof : List.of(Professions.BANKER, Professions.TITANSMITH, Professions.RELIC_DEALER)) {
        List<Professions.TradeDisplay> list = Professions.displays(prof);
        h.assertTrue(list.size() >= 5, "few trades for " + prof.get());
        for (var t : list) {
            h.assertTrue(!t.result().get().isEmpty() && !t.costA().get().isEmpty(), "empty trade display");
            h.assertTrue(t.level() >= 1 && t.level() <= 5, "bad level");
        }
    }
    h.succeed();
}
```

- [ ] **Step 2:** Run `./gradlew compileJava`. It must fail because `TradeDisplay` is missing.
- [ ] **Step 3: Implement.**
  - Add `public record TradeDisplay(int level, Supplier<ItemStack> costA, Supplier<ItemStack> costB, Supplier<ItemStack> result) {}`.
  - Change `trade(prof, level, listing)` into `trade(prof, level, listing, TradeDisplay display)`, which records both.
  - `offer(...)` and `offer2(...)` return a small record `Listing(VillagerTrades.ItemListing listing, ...)` that
    already knows its display. Simpler alternative: keep `offer` returning `ItemListing`, but add overloads
    `trade(prof, level, cost, costCount, result, resultCount, maxUses, xp)` and the two-cost form. They build
    both the listing and the display. Use the overloads everywhere a fixed offer is used today.
  - Special cases:
    - The banker's emerald → copper trade shows `ModConfig.EMERALD_TO_COPPER` default 5 at display time.
    - `Titans.shrineMap(e)` shows costs `coin(TITAN)` ×N and, as result, a `Items.FILLED_MAP` named
      `item.celestialascent.shrine_map.<element>` (use the same cost numbers as the listing).
  - `public static List<TradeDisplay> displays(Supplier<VillagerProfession> prof)` returns them sorted by level.
- [ ] **Step 4:** Run `./gradlew runGameTestServer`; expected: `All 55 required tests passed :)`.
- [ ] **Step 5: Commit** with the message `Villager trades record displays for recipe viewers`.

### Task A5: The JEI plugin

**Files:** create the four classes in `compat/jei/`; modify `LangGen.java` and `LangGenDe.java`

First check the API: open
`~/.gradle/caches/**/jei-1.21.1-neoforge-api-19.70.0.469.jar` (or the IDE sources) and confirm the signatures
of `IRecipeCategory` (`getWidth`/`getHeight`/`draw`/`setRecipe`), `IRecipeLayoutBuilder.addSlot(RecipeIngredientRole, x, y)`,
`IGuiHelper.createDrawable`, `IRecipeTransferRegistration.addRecipeTransferHandler(Class, MenuType, RecipeType, int, int, int, int)`
and `IIngredientManager.removeIngredientsAtRuntime`. Adapt the code below to the real signatures.

- [ ] **Step 1: `StationCategory`.** It implements `IRecipeCategory<StationRecipe.Example>`; there is one instance per `StationType`.
  - `RecipeType`: `RecipeType.create(MODID, "station/" + type.id, StationRecipe.Example.class)`.
  - Background: `guiHelper.createDrawable(type.gui, 24, 12, 124, 58)`. That is the region from just left of the
    base slot (x 30) to past the output (x 124+18), and from y 17 to y 71. Draw it at (0, 0). Slot coordinates
    are `type.base`, `type.mats[i]` and `type.output`, minus the (24, 12) origin, plus 1.
  - Height: 58 + 12 for a footer line. The footer reads `jei.celestialascent.time` ("%s s") from
    `type.processTicks / 20`.
    - Sky Altar: add `type.conditionKey()` text.
    - Evolution examples: detect them with `ArmorStages.stage(base) > 0 && ArmorStages.ready(base)`, then add
      `jei.celestialascent.needs_resonance`.
  - Icon: `guiHelper.createDrawableItemStack(new ItemStack(station block))`.
  - Title: the station block's name.
  - The arrow is part of the GUI texture crop, so it is static. That is enough.
- [ ] **Step 2: `SummonCategory`.** It implements `IRecipeCategory<BossSummons.Summon>`, size 150 × 74.
  - Input slots go on the left, stacked: the first input at (4, 10), the next at (4, 30).
  - Drop output slots form a 2-column grid on the right, from (112, 4). Each slot tooltip adds
    `jei.celestialascent.drop_count` with "min–max", plus "(+ Looting)" when `looting` is true.
  - `draw()` renders the boss in the middle at (56, 66) with `InventoryScreen.renderEntityInInventory`.
    - Create the entity once per type with `type.create(Minecraft.getInstance().level)` and cache it in a map.
    - Scale it to fit 50 px tall from `entity.getBbHeight()`.
    - Turn it by `(System.currentTimeMillis() / 40) % 360`.
    - For GeckoLib bosses this works through the normal entity renderer.
    - If `create` returns null or an exception is thrown, draw only the name.
  - Below the boss, draw its name and the `whereKey` text (split to the width, small font).
  - Tooltip on the boss area: max health from `entity.getMaxHealth()`.
- [ ] **Step 3: `TradeCategory`.** It implements `IRecipeCategory<Professions.TradeDisplay>`, with one
  `RecipeType` per profession and size 120 × 28.
  - Layout: costA at (4, 5), costB at (24, 5), an arrow sprite, and the result at (96, 5).
  - Text "Level N" in the right corner (`jei.celestialascent.level`).
  - Catalyst: the profession's POI block, taken from `Professions` (bank counter, titan anvil or whatever block
    the POI uses).
- [ ] **Step 4: `CelestialJeiPlugin`.** Annotate it with `@JeiPlugin` and implement `IModPlugin`. `getPluginUid` is `MODID:jei`.
  - `registerCategories`: one `StationCategory` per `StationType.all()`, one `SummonCategory`, and three `TradeCategory`.
  - `registerRecipes`:
    - Station examples per type: flatten `recipe.examples().get()`.
    - `BossSummons.all()`.
    - `Professions.displays(prof)`.
    - Info pages through `registration.addItemStackInfo(stack, Component...)`, using the keys
      `jei.celestialascent.info.<name>` for:
      - all 7 coins, under one key
      - the dragon heart
      - the dormant star core
      - the shop stall
      - the quest board
      - the bank counter
      - the codex
      - one shared key for every armor piece (resonance)
      - the celestial crystal, if Part B has merged (guard with a registry lookup, so A builds alone)
  - `registerRecipeCatalysts`: each station block → its station type, every summon altar block, the throne,
    the titan altars and the pylon → summon, and the workstations → trades.
  - `registerRecipeTransferHandlers`: for each station type,
    `addRecipeTransferHandler(StationMenu.class, Stations.MENU.get(), type, 0, type.size() - 1, type.size(), 36)`.
    Slot order in `StationMenu` is base, then materials, then output. Check the menu's slot indices and adjust.
    Guard against the wrong station: wrap it in a custom `IRecipeTransferInfo` whose `canHandle(menu, recipe)`
    checks `menu.type == this type`.
  - `onRuntimeAvailable`:
    - Store the runtime in `JeiShowcase.runtime`.
    - Hide technical blocks with `removeIngredientsAtRuntime`: `Titans.COOLED_MAGMA`, the star portal block, the
      abyss crumbling blocks, and any block whose item is not in a creative tab.
- [ ] **Step 5: Language.**
  - Add the keys to `LangGen.english()` and `LangGenDe`:
    - the category titles (the station names come from the blocks; trades: "Banker Trades" / "Bankier-Angebote", etc.)
    - "Summoning" / "Beschwörung"
    - time, resonance, level and drop count
    - the 7 where-texts
    - the 9 info pages
  - Run `./gradlew runData`. It must succeed: `LangGenDe` fails on missing keys.
- [ ] **Step 6: Build and check in game.** Run `./gradlew build`, then `./gradlew runClient`.
  - Press `R` on a Titan Helmet: the Titan Forge page appears, styled like the forge, with 8 rows per piece.
  - Press `U` on the Frost Titan core: the Frost Titan summon shows.
  - Press `R` on a Void Heart: the Sovereign summon shows.
  - On a station, the + button fills the slots.
  - The Codex and the coins have info tabs.
- [ ] **Step 7: Commit** with the message `JEI plugin: stations, summons, trades, info pages`.

### Task A6: Showcase screenshots of JEI

**Files:** `compat/jei/JeiShowcase.java`, `client/Showcase.java`

- [ ] **Step 1:** In `JeiShowcase`, add `static IJeiRuntime runtime` and
  `static void show(ItemStack stack, RecipeIngredientRole role)`. The method calls
  `runtime.getRecipesGui().show(runtime.getJeiHelpers().getFocusFactory().createFocus(role, VanillaTypes.ITEM_STACK, stack))`.
- [ ] **Step 2:** Add showcase steps `jei_titan_forge`, `jei_summon_frost`, `jei_trades_titansmith`, `jei_sky_altar`
  and `jei_info_coin`. Each runs on the client thread and only when `ModList.get().isLoaded("jei")`. The
  showcase must not reference `JeiShowcase` from a class that is loaded without JEI: call it through a lambda in
  a separate method.
- [ ] **Step 3:** Run `./gradlew runClient -Pshowcase -PshowcaseOnly='jei_.*'` and look at every PNG. The layout must be
  clean, with no overlapping text and the boss fully visible.
- [ ] **Step 4: Commit** with the message `Showcase shots of the JEI pages`.

---

# Part B: The new trade city

### Task B1: Celestial Crystal block

**Files:** `economy/CelestialCrystalBlock.java`, `economy/Economy.java`, `core/DisplayBlockEntity.java`,
`client/FloatingRenderer.java`, the datagen classes, `tools/art/gen_economy_blocks.py` (or a new
`gen_city_blocks.py`), `test/CityTests.java`

- [ ] **Step 1: Write the failing test:**

```java
@GameTest(template = CoreTests.FLOOR)
public static void crystalIsCraftableAndDropsItself(GameTestHelper h) {
    var recipes = h.getLevel().getRecipeManager();
    h.assertTrue(recipes.byKey(CelestialAscent.id("celestial_crystal")).isPresent(), "crystal recipe exists");
    BlockPos p = new BlockPos(1, 2, 1);
    h.setBlock(p, Economy.CELESTIAL_CRYSTAL.get());
    h.assertTrue(h.getBlockState(p).getLightEmission() == 15, "full light");
    h.succeed();
}
```

- [ ] **Step 2:** Run `./gradlew compileJava`. It must fail because `CELESTIAL_CRYSTAL` is missing.
- [ ] **Step 3: Implement.**
  - `CelestialCrystalBlock` extends `Block` and implements `EntityBlock`. It returns `DisplayBlockEntity`,
    has a small base shape (a 6×2×6 px socket), uses `noOcclusion` and light 15.
  - Register it with `Content.block("celestial_crystal", ...)` in `Economy`.
  - Add it to the `DisplayBlockEntity.TYPE` valid blocks.
  - `FloatingRenderer`: add `spec("celestial_crystal", 0, part("celestial_crystal", 6f, 1.5f, 0.05f, 1.5f, true))`.
  - Art:
    - A base model `block/celestial_crystal` (the socket) and a floating part `block/floating/celestial_crystal`:
      an octahedral crystal built from stacked cubes, 10 px wide and 16 px tall, in light blue and white, with
      gold rings.
    - A 16× texture.
    - An item model that shows socket and crystal together.
  - Recipe: shaped, ` A ` / `AGA` / ` D ` with A = amethyst shard, G = gold ingot, D = glowstone dust. That gives
    1 crystal: 4 amethyst, 1 gold, 1 glowstone.
  - Loot: `dropSelf`.
  - Lang: "Celestial Crystal" / "Himmelskristall".
  - EMC: if `EmcGen` lists blocks, add 50 000.
- [ ] **Step 4:** Run `./gradlew runData` and `runGameTestServer`. All tests must pass.
- [ ] **Step 5: Check in game.** In a creative world, place the crystal. It must float and turn and give light 15.
- [ ] **Step 6: Commit** with the message `Celestial Crystal decoration block`.

### Task B2: City structure type

**Files:** `retrogen/CityStructure.java`, `core/CAReg.java`, `test/CityTests.java`

- [ ] **Step 1: Write the failing test** for the pure site check:

```java
@GameTest(template = CoreTests.FLOOR)
public static void citySiteCheck(GameTestHelper h) {
    int[] flat = new int[81]; java.util.Arrays.fill(flat, 70);
    boolean[] dry = new boolean[81];
    h.assertTrue(CityStructure.siteHeight(flat, dry, 6, 0.2f).isPresent(), "flat dry land is fine");
    int[] steep = flat.clone(); for (int i = 0; i < 81; i++) steep[i] = 60 + (i % 9) * 3;
    h.assertTrue(CityStructure.siteHeight(steep, dry, 6, 0.2f).isEmpty(), "a 24-block slope is rejected");
    boolean[] wet = new boolean[81]; for (int i = 0; i < 30; i++) wet[i] = true;
    h.assertTrue(CityStructure.siteHeight(flat, wet, 6, 0.2f).isEmpty(), "a lake is rejected");
    h.succeed();
}
```

- [ ] **Step 2:** Run `./gradlew compileJava`. It must fail because `CityStructure` is missing.
- [ ] **Step 3: Implement.** Before writing it, read
  `net.minecraft.world.level.levelgen.structure.structures.JigsawStructure` in the decompiled sources and mirror
  its `findGenerationPoint` call to `JigsawPlacement.addPieces`, with the 1.21.1 parameters (`PoolAliasLookup`,
  `DimensionPadding`, `LiquidSettings`).

```java
public final class CityStructure extends Structure {
    public static final MapCodec<CityStructure> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
            settingsCodec(i),
            StructureTemplatePool.CODEC.fieldOf("start_pool").forGetter(s -> s.startPool),
            Codec.intRange(1, 20).fieldOf("size").forGetter(s -> s.size),
            Codec.intRange(1, 128).fieldOf("max_distance_from_center").forGetter(s -> s.maxDistance),
            Codec.intRange(8, 64).fieldOf("core_radius").forGetter(s -> s.coreRadius),
            Codec.intRange(0, 16).fieldOf("ground_level").forGetter(s -> s.groundLevel),
            Codec.intRange(1, 32).fieldOf("max_spread").forGetter(s -> s.maxSpread)
    ).apply(i, CityStructure::new));
    // fields + constructor

    /** Median ground height when the sampled site is flat and dry enough, else empty. */
    public static OptionalInt siteHeight(int[] heights, boolean[] water, int maxSpread, float maxWater) {
        int wet = 0; for (boolean w : water) if (w) wet++;
        if (wet > water.length * maxWater) return OptionalInt.empty();
        int[] s = heights.clone(); java.util.Arrays.sort(s);
        int spread = s[(int) (s.length * 0.9)] - s[(int) (s.length * 0.1)];
        return spread > maxSpread ? OptionalInt.empty() : OptionalInt.of(s[s.length / 2]);
    }

    @Override
    protected Optional<GenerationStub> findGenerationPoint(GenerationContext ctx) {
        ChunkPos c = ctx.chunkPos();
        int cx = c.getMiddleBlockX(), cz = c.getMiddleBlockZ();
        int[] h = new int[81]; boolean[] w = new boolean[81];
        for (int i = 0; i < 9; i++) for (int j = 0; j < 9; j++) {
            int x = cx + (i - 4) * coreRadius / 4, z = cz + (j - 4) * coreRadius / 4;
            int surface = ctx.chunkGenerator().getFirstOccupiedHeight(x, z, Heightmap.Types.WORLD_SURFACE_WG, ctx.heightAccessor(), ctx.randomState());
            int floor = ctx.chunkGenerator().getFirstOccupiedHeight(x, z, Heightmap.Types.OCEAN_FLOOR_WG, ctx.heightAccessor(), ctx.randomState());
            h[i * 9 + j] = floor; w[i * 9 + j] = surface > floor;
        }
        OptionalInt y = siteHeight(h, w, maxSpread, 0.2f);
        if (y.isEmpty()) return Optional.empty();
        // The start piece's ground layer (template y = groundLevel) must sit on the median ground height.
        BlockPos start = new BlockPos(cx, y.getAsInt() + 1 - groundLevel, cz);   // verify the +1 against JigsawPlacement's groundLevelDelta
        return JigsawPlacement.addPieces(ctx, startPool, Optional.empty(), size, start, false, Optional.empty(),
                maxDistance, PoolAliasLookup.EMPTY, DimensionPadding.ZERO, LiquidSettings.APPLY_WATERLOGGING);
    }

    @Override public StructureType<?> type() { return CAReg.CITY_STRUCTURE.get(); }
}
```

  In `CAReg`, add
  `STRUCTURE_TYPES = DeferredRegister.create(Registries.STRUCTURE_TYPE, M)` and
  `CITY_STRUCTURE = STRUCTURE_TYPES.register("city", () -> () -> CityStructure.CODEC)`. Register it on the mod
  bus with the others.
- [ ] **Step 4:** Run `./gradlew runGameTestServer`. All tests must pass.
- [ ] **Step 5: Commit** with the message `City structure type with a terrain check`.

### Task B3: City templates (`tools/make_city.py`)

**Files:** create `tools/make_city.py`; modify `tools/make_villages.py`. Generated: the templates and JSON files.

This is the big creative task. It has 5 variants. Each variant has one core, about 5 road pieces and 12 side
pieces. Use the `B` builder from `make_villages.py` (import it).

- [ ] **Step 1: Palette system.**
  - Write every template with **logical block names**: `@wall`, `@wall_slab`, `@wall_stairs`, `@wall_wall`,
    `@trim`, `@plank`, `@plank_stairs`, `@plank_slab`, `@log`, `@roof`, `@roof_stairs`, `@roof_slab`, `@path`,
    `@path2`, `@fence`, `@door`, `@trapdoor`, `@leaves`, `@ground` and `@accent`.
  - Each variant maps them to real blocks:

| logical | plains | desert | savanna | taiga | snowy |
|---|---|---|---|---|---|
| wall | stone_bricks | sandstone | terracotta | cobblestone | stone_bricks |
| trim | polished_andesite | cut_sandstone | smooth_sandstone | mossy_stone_bricks | polished_diorite |
| plank | oak_planks | birch_planks | acacia_planks | spruce_planks | spruce_planks |
| log | oak_log | stripped_birch_log | acacia_log | spruce_log | stripped_spruce_log |
| roof | dark_oak (stairs/slab/planks) | smooth_sandstone (stairs/slab) | acacia (stairs/slab) | spruce (stairs/slab) | deepslate_tile (stairs/slab) |
| path | dirt_path | sandstone / smooth_sandstone | coarse_dirt / dirt_path | dirt_path / coarse_dirt | stone_bricks / gravel |
| leaves | oak_leaves | birch_leaves (in planters) | acacia_leaves | spruce_leaves | spruce_leaves |
| ground | grass_block | sand | grass_block | podzol | snow_block |

  - Stair, slab and wall variants come from the base name with a lookup table, because not every block has
    every form. Fall back to the trim's form when one is missing.
  - The celestial accents are fixed blocks in every variant: `quartz_block`, `quartz_pillar`, `chiseled_quartz_block`,
    `gold_block`, `lapis_block`, `light_blue_stained_glass`, `amethyst_block`, `end_rod`, and the Celestial Crystal.
  - The snowy variant adds `snow` layers on roofs and the ground after building.
- [ ] **Step 2: Core template** (63 × 34 × 63; ground layer at template y = 5; `ground_level` 5).
  - Foundation: `@wall`/`cobblestone` fills y 0–4 under every wall, tower and building footprint, plus the whole
    plaza.
  - Ground: y 5 is `@ground`. Streets are `@path`/`@path2` with a seeded mix, plus a quartz cross pattern around the plaza.
  - **Walls:**
    - Ring from x/z 0..62, 3 thick, 7 high.
    - A walkway at y 12 with crenellations (alternating `@wall_wall`) and torches every 6.
  - **Corner towers:**
    - 9 × 9, 14 high.
    - Pointed `@roof_stairs` roof up to y 26, with a gold-block finial and an end rod.
    - Windows of light blue glass panes.
  - **Gatehouses** at the 4 mid-sides:
    - 11 wide, 12 high, an arched opening 5 wide × 6 high, and iron-bar portcullis teeth at the arch top.
    - Banners, 2 per gate, in blue with a light blue pattern: plain `blue_wall_banner`, no pattern NBT needed.
    - Lanterns.
    - A jigsaw at the outer ground of each gate facing outward: `name celestialascent:gate`,
      `target celestialascent:road`, `pool celestialascent:city/<v>/roads`, `final_state @path`, `joint aligned`.
  - **Plaza** (center, radius 9):
    - A 3-tier fountain: outer ring of 15, a quartz basin, water.
    - **Star Spire** in the middle: 5 × 5 quartz-pillar base, tapering to 3 × 3, then a 1 × 1 gold/lapis needle up to
      y 31. The **Celestial Crystal** sits at the top with nothing above it.
    - 4 quest boards facing the plaza.
    - Benches from `@plank_stairs`, planters with `@leaves` trees, flower beds and lamp posts.
  - **Bank** (NE quadrant, 17 × 13):
    - Quartz front with 4 quartz pillars and gold trim.
    - Stairs up to the door and a gold-and-lapis sign stripe.
    - Inside: 2 bank counters, a vault behind iron bars with 6 gold blocks and 2 chests (empty), chandeliers
      (chains and lanterns), and 2 bankers.
  - **Market hall** (south half, 25 × 11):
    - Open sides, `@log` columns and an `@roof` canopy.
    - 8 `celestialascent:shop_stall` blocks under awnings of colored wool, each stall a different color.
    - Barrels and crates.
  - **Relic pavilion** (NW, 11 × 11): purpur pillars, an end stone brick floor, amethyst corner clusters, the
    relic pedestal in the center, and the relic dealer.
  - **Titansmith forge** (SE corner block, 11 × 9):
    - A `@wall` chimney up to y 20 with campfire smoke.
    - Anvil, smithing table, blast furnace and a lava pit behind iron bars.
    - The titansmith.
  - **Inn** (west, 13 × 11, 2 floors):
    - Bar with barrels and brewing stand.
    - 4 beds upstairs.
    - Wooden balcony.
  - **Houses**: 4 houses (7 × 9, 2 floors) along the east and west streets, with beds, crafting table,
    bookshelves, flower pots, windows and a chimney.
  - **Barracks** by the north gate: armor stands and 2 iron golems (entities with `PersistenceRequired`).
  - **Gardens**: hedges and flowers in free corners.
  - **Villagers**:
    - 2 bankers, the titansmith and the relic dealer.
    - 4 `minecraft:none` villagers.
    - A free workstation next to each: composter, lectern, cartography table and barrel.
- [ ] **Step 3: Road pieces** (pool `city/<v>/roads`, projection `terrain_matching`). Each is 1 block tall:
  path blocks, plus lamp posts made as separate small `rigid` features attached by side jigsaws.
  - `road_straight_long` (5 wide × 16), `road_straight` (5 × 9), `road_bend_left`, `road_bend_right` and `road_tee`.
  - The entry jigsaw at the back is named `celestialascent:road`.
  - Forward jigsaws: `name celestialascent:road_next`, `target celestialascent:road`, pool roads.
  - Side jigsaws every 8 blocks: `name celestialascent:lot`, `target celestialascent:building`,
    pool `city/<v>/outskirts`.
  - Fallback pool `city/<v>/road_ends` holds `road_end`: a 5 × 3 path with a lamp post.
- [ ] **Step 4: Outskirts** (pool `city/<v>/outskirts`, `rigid`). Each piece has one entry jigsaw on its road
  side: `name celestialascent:building`, `target celestialascent:lot`, facing the road.
  - `farm_wheat` (9 × 9, crops by variant: wheat, potatoes in taiga or snowy, beetroot in savanna, and in desert
    cactus with sugar cane by a water channel)
  - `farm_pumpkin`
  - `windmill` (7 × 7 tower with 4 sail arms of wool and fences, 16 tall)
  - `stable` (horses as entities, hay)
  - `house_small_a`, `house_small_b`, `house_small_c`
  - `well`
  - `watchtower` (from `make_villages.watchtower` with the palette)
  - `orchard` (fruit trees: leaves on logs, with sweet berry bushes in taiga)
  - `lamp_post`
  - Weights: houses 3 each, farms 2, the rest 1.
- [ ] **Step 5: JSON.**
  - Write `worldgen/structure/trade_city.json` (plains) and `trade_city_desert|savanna|taiga|snowy.json`:

```json
{ "type": "celestialascent:city", "biomes": "#celestialascent:has_structure/trade_city_<v>",
  "step": "surface_structures", "spawn_overrides": {}, "terrain_adaptation": "beard_thin",
  "start_pool": "celestialascent:city/<v>/core", "size": 6, "max_distance_from_center": 112,
  "core_radius": 31, "ground_level": 5, "max_spread": 6 }
```

  - Template pools:
    - `city/<v>/core`: one element.
    - `city/<v>/roads`: the road pieces, terrain_matching, with fallback `city/<v>/road_ends`.
    - `city/<v>/road_ends`
    - `city/<v>/outskirts`: fallback `minecraft:empty`.
  - Structure set `trade_city.json`: all 5 structures with weight 1, `random_spread` with spacing 48, separation 20
    and the old salt 715264001.
  - Biome tags:
    - plains: plains, sunflower_plains, meadow
    - desert: desert
    - savanna: savanna, savanna_plateau
    - taiga: taiga, old_growth_pine_taiga, old_growth_spruce_taiga
    - snowy: snowy_plains, snowy_taiga
  - The structure tag `celestialascent:trade_city` lists all 5.
  - Delete the old `structure/city/trade_city.nbt` and the old `template_pool/city/trade_city.json`.
- [ ] **Step 6:** In `make_villages.py`, remove `trade_city()` and its writes from `main()`. Keep the village parts.
- [ ] **Step 7: Generate and check.** Run `python tools/make_city.py`. It must print the template counts:
  5 cores, 25 road pieces, 5 road ends and 55 outskirts.
- [ ] **Step 8: Commit** with the message `New trade city templates in five biome styles`.

### Task B4: Retrogen picks the fitting variant

**Files:** `retrogen/Retrogen.java`, `retrogen/SiteCheck.java`

- [ ] **Step 1:** In `Retrogen.process` (around line 201), replace `structures().get(0)` with a loop over the set's
  structures. Generate each with `Retrogen.generate(level, structure, origin)` and use the first whose start is
  valid. The `MISSING`/`PARTIAL` branches only need an id, so use the first entry's id there.
- [ ] **Step 2:** Check every other `get(0)` in `retrogen/` (`RetrogenCommands.hut`, `findNearest`) and make them work
  with multi-structure sets the same way.
- [ ] **Step 3:** In `SiteCheck.GROUND_OFFSET`, add the 5 city ids with value 5: the core's ground layer is template
  y 5. Check how the offset is used there and confirm it matches.
- [ ] **Step 4:** Run `./gradlew runGameTestServer`. All tests must pass, including `retrogenSeesPlayerBuilds`.
- [ ] **Step 5: Commit** with the message `Retrogen chooses the structure variant that fits the biome`.

### Task B5: Tests, codex and visual check

**Files:** `test/CityTests.java`, `guide/GuideChapters.java`, `client/Showcase.java`, `README.md`, `release/curseforge/*`

- [ ] **Step 1: Template content test:**

```java
@GameTest(template = CoreTests.FLOOR)
public static void cityCoresHaveEverything(GameTestHelper h) {
    var mgr = h.getLevel().getStructureManager();
    for (String v : List.of("plains", "desert", "savanna", "taiga", "snowy")) {
        var t = mgr.get(CelestialAscent.id("city/" + v + "/core")).orElse(null);
        h.assertTrue(t != null, "core template for " + v);
        var settings = new StructurePlaceSettings();
        CoreTests.atLeast(h, 2, t.filterBlocks(BlockPos.ZERO, settings, Economy.BANK_COUNTER.get()).size(), v + " bank counters");
        CoreTests.atLeast(h, 8, t.filterBlocks(BlockPos.ZERO, settings, Economy.SHOP_STALL.get()).size(), v + " shop stalls");
        CoreTests.atLeast(h, 2, t.filterBlocks(BlockPos.ZERO, settings, Economy.QUEST_BOARD.get()).size(), v + " quest boards");
        CoreTests.atLeast(h, 1, t.filterBlocks(BlockPos.ZERO, settings, Economy.RELIC_PEDESTAL.get()).size(), v + " relic pedestal");
        CoreTests.atLeast(h, 1, t.filterBlocks(BlockPos.ZERO, settings, Economy.CELESTIAL_CRYSTAL.get()).size(), v + " crystal");
        int beds = 0; for (Block b : BuiltInRegistries.BLOCK) if (b instanceof BedBlock) beds += t.filterBlocks(BlockPos.ZERO, settings, b).size();
        CoreTests.atLeast(h, 8, beds, v + " bed halves (4 beds)");
    }
    h.succeed();
}
```

  Add `CoreTests.atLeast(h, min, actual, what)` if it does not exist.

- [ ] **Step 2:** Run `./gradlew runGameTestServer`. All tests must pass.
- [ ] **Step 3: Codex.** In the `cities` section of `GuideChapters`, rewrite the text in EN and DE: walled
  cities in the biome's style, the Star Spire, the bank, a market hall with 8 rentable stalls, the inn, the
  relic pavilion and the outskirts. Add a line about the Celestial Crystal with its recipe:
  `.craft("celestial_crystal")`. Then run `./gradlew runData`.
- [ ] **Step 4: Showcase.**
  - Add steps `city_setup`: a flat area at y 200 far from spawn, cleared in fills of at most 32 768 blocks.
  - Then for each variant, `city_<v>`: run `place structure celestialascent:trade_city[_<v>] ~ ~ ~`, which
    ignores the biome, and take an aerial screenshot plus one street-level shot.
  - Natural check: `/locate structure #celestialascent:trade_city` in the devworld, teleport there, take a screenshot.
- [ ] **Step 5: Look at the screenshots.** Iterate on `make_city.py` until the city looks good:
  - no floating or cut-off pieces
  - roads follow the terrain
  - no buildings intersect each other
  - the Star Spire crystal is visible from the gates
- [ ] **Step 6: Retrogen check.**
  - Run `runServer -PnoStructures -PserverWorld=retroworld`, then with `-PretrogenPaused`.
  - Use `/celestialascent retrogen scan 64`, then `run`. It must report a city variant `PLACED` or `RELOCATED`.
- [ ] **Step 7: Release texts.** Update the README and `release/curseforge/description.md` (and regenerate `.html`):
  - JEI support (optional)
  - the new cities in five styles
  - the Celestial Crystal

  Also update `changelog.md`.
- [ ] **Step 8:** Run `./gradlew build`, copy the jar to `release/curseforge/` and `dist/`, and commit with the
  message `Codex, showcase and release texts for the new trade city`.

---

## Final integration

- [ ] Merge Part A into the main tree. Resolve append-only conflicts in `LangGen`, `LangGenDe` and `Showcase`.
- [ ] Run `./gradlew runData`, `runGameTestServer` and `build`. Expected: all tests pass (52 + 3 JEI + 3 city = 58).
- [ ] Do one dev client run with JEI and check the crystal's info page appears.
- [ ] Update `memory/celestial-ascent-mod.md` with the JEI plugin location, `make_city.py` and the city structure type.
