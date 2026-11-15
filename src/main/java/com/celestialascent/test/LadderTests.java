package com.celestialascent.test;

import com.celestialascent.CelestialAscent;
import com.celestialascent.abyss.Abyss;
import com.celestialascent.abyss.AbyssalStoneBlock;
import com.celestialascent.abyss.AscendantAbilities;
import com.celestialascent.compat.ProjectECompat;
import com.celestialascent.economy.Bank;
import com.celestialascent.economy.CoinTier;
import com.celestialascent.economy.Coins;
import com.celestialascent.economy.Economy;
import com.celestialascent.economy.Quests;
import com.celestialascent.economy.ShopStallBlockEntity;
import com.celestialascent.economy.VillageGrowth;
import com.celestialascent.empire.Empire;
import com.celestialascent.empire.PylonBlock;
import com.celestialascent.stars.StarGatePedestalBlock;
import com.celestialascent.stars.Stars;
import com.celestialascent.titans.Element;
import com.celestialascent.titans.Titans;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

import java.util.List;

@GameTestHolder(CelestialAscent.MODID)
@PrefixGameTestTemplate(false)
public final class LadderTests {
    private LadderTests() {}

    private static BlockHitResult hit(BlockPos abs) {
        return new BlockHitResult(Vec3.atCenterOf(abs), Direction.UP, abs, false);
    }

    @GameTest(template = CoreTests.FLOOR)
    public static void pylonRestorationCostsAndUnlocksForge(GameTestHelper h) {
        BlockPos rel = new BlockPos(4, 1, 4);
        h.setBlock(rel, Empire.PYLON.get().defaultBlockState().setValue(PylonBlock.KIND, PylonBlock.Kind.CRAFT));
        ServerPlayer p = h.makeMockServerPlayerInLevel();
        p.setGameMode(net.minecraft.world.level.GameType.SURVIVAL);
        p.getInventory().clearContent();
        BlockPos abs = h.absolutePos(rel);
        BlockState st = h.getLevel().getBlockState(abs);
        st.useWithoutItem(h.getLevel(), p, hit(abs));
        h.assertTrue(!h.getLevel().getBlockState(abs).getValue(PylonBlock.RESTORED), "not restored without materials");
        p.getInventory().add(new ItemStack(Empire.IMPERIAL_PLATING.get(), PylonBlock.PLATING));
        p.getInventory().add(new ItemStack(Items.PURPUR_BLOCK, PylonBlock.PURPUR));
        p.getInventory().add(new ItemStack(Economy.coin(CoinTier.TITAN), 3));
        h.getLevel().getBlockState(abs).useWithoutItem(h.getLevel(), p, hit(abs));
        h.assertTrue(h.getLevel().getBlockState(abs).getValue(PylonBlock.RESTORED), "restored");
        CoreTests.eq(h, 0, p.getInventory().countItem(Empire.IMPERIAL_PLATING.get()), "plating consumed");
        CoreTests.eq(h, 0L, Coins.countInventory(p), "coins consumed");
        h.succeedWhen(() -> h.assertTrue(!h.getLevel().getEntitiesOfClass(net.minecraft.world.entity.item.ItemEntity.class,
                new net.minecraft.world.phys.AABB(abs).inflate(3), e -> e.getItem().is(Empire.IMPERIAL_FORGE.get().asItem())).isEmpty(), "forge dropped"));
    }

    @GameTest(template = CoreTests.FLOOR)
    public static void throneBarrierFallsWithThronePylon(GameTestHelper h) {
        BlockPos pylon = new BlockPos(2, 1, 2), barrier = new BlockPos(10, 2, 10);
        h.setBlock(barrier, Empire.IMPERIAL_BARRIER.get());
        h.setBlock(pylon, Empire.PYLON.get().defaultBlockState().setValue(PylonBlock.KIND, PylonBlock.Kind.THRONE));
        PylonBlock.restore(h.getLevel(), h.absolutePos(pylon), h.getLevel().getBlockState(h.absolutePos(pylon)));
        h.assertBlockPresent(Blocks.AIR, barrier);
        h.succeed();
    }

    @GameTest(template = CoreTests.FLOOR)
    public static void imperialForgeUpgradesTitanChest(GameTestHelper h) {
        ItemStack chest = new ItemStack(Titans.CHESTPLATE.get());
        chest.set(Titans.ELEMENT.get(), Element.STORM);
        var r = Empire.FORGE.find(chest, List.of(new ItemStack(Empire.IMPERIAL_PLATING.get(), 6), new ItemStack(Empire.ENDER_GEAR.get(), 3),
                new ItemStack(Empire.COLOSSUS_CORE.get())));
        h.assertTrue(r != null, "chest recipe needs colossus core and matches");
        CoreTests.eq(h, Empire.CHESTPLATE.get(), r.result().apply(chest).getItem(), "imperial chestplate");
        h.assertTrue(Empire.FORGE.find(chest, List.of(new ItemStack(Empire.IMPERIAL_PLATING.get(), 6), new ItemStack(Empire.ENDER_GEAR.get(), 3), ItemStack.EMPTY)) == null,
                "chest without core fails");
        h.succeed();
    }

    @GameTest(template = CoreTests.FLOOR)
    public static void starGateOpensWithHeadAndSeal(GameTestHelper h) {
        BlockPos rel = new BlockPos(8, 2, 13);
        h.setBlock(rel, Stars.STAR_GATE_PEDESTAL.get().defaultBlockState().setValue(StarGatePedestalBlock.FACING, Direction.NORTH));
        ServerPlayer p = h.makeMockServerPlayerInLevel();
        BlockPos abs = h.absolutePos(rel);
        p.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(Items.DRAGON_HEAD));
        h.getLevel().getBlockState(abs).useItemOn(p.getMainHandItem(), h.getLevel(), p, InteractionHand.MAIN_HAND, hit(abs));
        h.assertTrue(h.getLevel().getBlockState(abs).getValue(StarGatePedestalBlock.HEAD), "head placed");
        p.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(Empire.IMPERIAL_SEAL.get()));
        h.getLevel().getBlockState(abs).useItemOn(p.getMainHandItem(), h.getLevel(), p, InteractionHand.MAIN_HAND, hit(abs));
        BlockPos center = StarGatePedestalBlock.gateCenter(abs, h.getLevel().getBlockState(abs));
        h.assertTrue(h.getLevel().getBlockState(center).is(Stars.STAR_PORTAL.get()), "portal centre");
        h.assertTrue(h.getLevel().getBlockState(center.offset(1, 0, 1)).is(Stars.STAR_PORTAL.get()), "portal corner");
        CoreTests.eq(h, 1, p.getMainHandItem().getCount(), "seal kept");
        h.succeed();
    }

    @GameTest(template = CoreTests.FLOOR)
    public static void skyAltarNeedsNightSky(GameTestHelper h) {
        h.getLevel().setDayTime(6000);
        BlockPos abs = h.absolutePos(new BlockPos(3, 1, 3));
        h.assertTrue(!Stars.SKY_ALTAR_TYPE.conditionMet(h.getLevel(), abs), "not by day");
        h.assertTrue(Stars.SKY_ALTAR_TYPE.find(new ItemStack(Stars.DORMANT_STAR_CORE.get()), List.of(ItemStack.EMPTY, ItemStack.EMPTY)) != null,
                "dormant core charges with no materials");
        h.succeed();
    }

    @GameTest(template = CoreTests.FLOOR, timeoutTicks = 200)
    public static void abyssalStoneCrumbles(GameTestHelper h) {
        BlockPos rel = new BlockPos(5, 1, 5);
        h.setBlock(rel, Abyss.ABYSSAL_STONE.get());
        AbyssalStoneBlock.crack(h.getLevel(), h.absolutePos(rel), 1);
        h.succeedWhen(() -> h.assertBlockPresent(Blocks.AIR, rel));
    }

    @GameTest(template = CoreTests.FLOOR)
    public static void crumbleSpeedByDepth(GameTestHelper h) {
        h.assertTrue(AbyssalStoneBlock.stageTicks(100) > AbyssalStoneBlock.stageTicks(30), "middle faster than shallow");
        h.assertTrue(AbyssalStoneBlock.stageTicks(30) > AbyssalStoneBlock.stageTicks(-20), "deep fastest");
        h.succeed();
    }

    @GameTest(template = CoreTests.FLOOR)
    public static void ascendantImmunities(GameTestHelper h) {
        var src = h.getLevel().damageSources();
        h.assertTrue(AscendantAbilities.immune(src.lava()), "lava");
        h.assertTrue(AscendantAbilities.immune(src.fall()), "fall");
        h.assertTrue(AscendantAbilities.immune(src.drown()), "drowning");
        h.assertTrue(AscendantAbilities.immune(src.freeze()), "freezing");
        h.assertTrue(AscendantAbilities.immune(src.fellOutOfWorld()), "void");
        h.assertTrue(!AscendantAbilities.immune(src.generic()), "not invincible");
        var r = Abyss.ASCENSION.find(new ItemStack(Abyss.VOID_CHESTPLATE.get()), List.of(new ItemStack(Abyss.PRIMORDIAL_CORE.get()),
                new ItemStack(Stars.STAR_CORE.get()), new ItemStack(Abyss.VOID_HEART.get())));
        h.assertTrue(r != null && r.result().apply(new ItemStack(Abyss.VOID_CHESTPLATE.get())).is(Abyss.ASC_CHESTPLATE.get()), "ascendant chest recipe");
        h.succeed();
    }

    @GameTest(template = CoreTests.FLOOR)
    public static void questsAreDailyAndDeterministic(GameTestHelper h) {
        BlockPos pos = new BlockPos(100, 64, 200);
        var a = Quests.forBoard(pos, 5);
        var b = Quests.forBoard(pos, 5);
        CoreTests.eq(h, 3, a.size(), "three quests");
        CoreTests.eq(h, a, b, "same board, same day, same quests");
        h.assertTrue(!a.equals(Quests.forBoard(pos, 6)) || !a.equals(Quests.forBoard(pos.east(), 5)), "quests vary");
        h.assertTrue(a.stream().allMatch(q -> q.reward() > 0 && q.count() > 0), "valid quests");
        h.succeed();
    }

    @GameTest(template = CoreTests.FLOOR)
    public static void villageGrowthThresholds(GameTestHelper h) {
        CoreTests.eq(h, 0, VillageGrowth.levelFor(99), "below first");
        CoreTests.eq(h, 1, VillageGrowth.levelFor(100), "first building");
        CoreTests.eq(h, VillageGrowth.THRESHOLDS.length, VillageGrowth.levelFor(1_000_000), "max");
        CoreTests.eq(h, VillageGrowth.THRESHOLDS.length, VillageGrowth.BUILDINGS.length, "one building per threshold");
        h.succeed();
    }

    @GameTest(template = CoreTests.FLOOR)
    public static void unownedStallCanBeRented(GameTestHelper h) {
        BlockPos rel = new BlockPos(6, 1, 6);
        h.setBlock(rel, Economy.SHOP_STALL.get());
        BlockPos abs = h.absolutePos(rel);
        ShopStallBlockEntity be = (ShopStallBlockEntity) h.getLevel().getBlockEntity(abs);
        ServerPlayer p = h.makeMockServerPlayerInLevel();
        p.getInventory().clearContent();
        h.assertTrue(!be.hasOwner() && !be.isOwner(p), "unowned stall belongs to nobody");
        Bank.get(h.getLevel().getServer()).deposit(p.getUUID(), ShopStallBlockEntity.RENT);
        p.setShiftKeyDown(true);
        h.getLevel().getBlockState(abs).useWithoutItem(h.getLevel(), p, hit(abs));
        h.assertTrue(be.isOwner(p), "rented with bank balance");
        h.succeed();
    }

    @GameTest(template = CoreTests.FLOOR)
    public static void emcRepairCost(GameTestHelper h) {
        CoreTests.eq(h, 3333L, ProjectECompat.costPerPoint(19_200_000, 720), "titan chest");
        CoreTests.eq(h, 16L, ProjectECompat.costPerPoint(100, 720), "minimum cost");
        h.succeed();
    }
}
