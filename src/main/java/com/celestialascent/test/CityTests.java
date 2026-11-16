package com.celestialascent.test;

import com.celestialascent.CelestialAscent;
import com.celestialascent.economy.CityStructure;
import com.celestialascent.economy.Economy;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.BedBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructurePlaceSettings;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplate;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

import java.util.Arrays;
import java.util.List;

/** The trade city: its crystal, its terrain check and what every biome variant's core contains. */
@GameTestHolder(CelestialAscent.MODID)
@PrefixGameTestTemplate(false)
public final class CityTests {
    private CityTests() {}

    static final List<String> VARIANTS = List.of("plains", "desert", "savanna", "taiga", "snowy");

    @GameTest(template = CoreTests.FLOOR)
    public static void crystalIsCraftableAndGlows(GameTestHelper h) {
        var recipes = h.getLevel().getRecipeManager();
        h.assertTrue(recipes.byKey(ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "celestial_crystal")).isPresent(),
                "the crystal has a recipe");
        BlockPos p = new BlockPos(1, 2, 1);
        h.setBlock(p, Economy.CELESTIAL_CRYSTAL.get());
        CoreTests.eq(h, 15, h.getBlockState(p).getLightEmission(), "crystal light");
        h.succeed();
    }

    @GameTest(template = CoreTests.FLOOR)
    public static void citySiteCheck(GameTestHelper h) {
        int[] flat = new int[81];
        Arrays.fill(flat, 70);
        boolean[] dry = new boolean[81];
        h.assertTrue(CityStructure.siteHeight(flat, dry, 6, 0.2f).isPresent(), "flat dry land is fine");
        CoreTests.eq(h, 70, CityStructure.siteHeight(flat, dry, 6, 0.2f).getAsInt(), "median height");
        int[] steep = flat.clone();
        for (int i = 0; i < 81; i++) steep[i] = 60 + (i % 9) * 3;
        h.assertTrue(CityStructure.siteHeight(steep, dry, 6, 0.2f).isEmpty(), "a 24-block slope is refused");
        boolean[] wet = new boolean[81];
        for (int i = 0; i < 30; i++) wet[i] = true;
        h.assertTrue(CityStructure.siteHeight(flat, wet, 6, 0.2f).isEmpty(), "a lake is refused");
        int[] bumpy = flat.clone();
        bumpy[3] = 90;
        bumpy[40] = 50;
        h.assertTrue(CityStructure.siteHeight(bumpy, dry, 6, 0.2f).isPresent(), "a single tree or hole does not refuse a site");
        h.succeed();
    }

    @GameTest(template = CoreTests.FLOOR)
    public static void cityCoresHaveEverything(GameTestHelper h) {
        var mgr = h.getLevel().getStructureManager();
        var settings = new StructurePlaceSettings();
        for (String v : VARIANTS) {
            StructureTemplate t = mgr.get(ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "city/" + v + "/core")).orElse(null);
            h.assertTrue(t != null, "core template for " + v);
            atLeast(h, 2, t.filterBlocks(BlockPos.ZERO, settings, Economy.BANK_COUNTER.get()).size(), v + " bank counters");
            atLeast(h, 8, t.filterBlocks(BlockPos.ZERO, settings, Economy.SHOP_STALL.get()).size(), v + " shop stalls");
            atLeast(h, 2, t.filterBlocks(BlockPos.ZERO, settings, Economy.QUEST_BOARD.get()).size(), v + " quest boards");
            atLeast(h, 1, t.filterBlocks(BlockPos.ZERO, settings, Economy.RELIC_PEDESTAL.get()).size(), v + " relic pedestal");
            atLeast(h, 1, t.filterBlocks(BlockPos.ZERO, settings, Economy.CELESTIAL_CRYSTAL.get()).size(), v + " celestial crystal");
            int beds = 0;
            for (Block b : BuiltInRegistries.BLOCK) if (b instanceof BedBlock) beds += t.filterBlocks(BlockPos.ZERO, settings, b).size();
            atLeast(h, 8, beds, v + " bed halves (4 beds)");
        }
        h.succeed();
    }

    static void atLeast(GameTestHelper h, int min, int actual, String what) {
        h.assertTrue(actual >= min, what + ": expected at least " + min + ", got " + actual);
    }
}
