package com.celestialascent.test;

import com.celestialascent.CelestialAscent;
import com.celestialascent.boss.CelestialBoss;
import com.celestialascent.economy.Bank;
import com.celestialascent.economy.CoinTier;
import com.celestialascent.economy.Coins;
import com.celestialascent.economy.Economy;
import com.celestialascent.economy.ShopStallBlockEntity;
import com.celestialascent.progress.Progress;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

import java.util.List;

/** Logic tests for frameworks and the economy. Run with ./gradlew runGameTestServer. */
@GameTestHolder(CelestialAscent.MODID)
@PrefixGameTestTemplate(false)
public final class CoreTests {
    private CoreTests() {}

    static final String FLOOR = "test_floor";

    static void eq(GameTestHelper h, Object expected, Object actual, String what) {
        if (!java.util.Objects.equals(expected, actual)) h.fail(what + ": expected " + expected + " but was " + actual);
    }

    @GameTest(template = FLOOR)
    public static void coinBreakdownIsGreedy(GameTestHelper h) {
        List<ItemStack> parts = Coins.breakdown(1_234_567);
        long sum = parts.stream().mapToLong(Coins::valueOf).sum();
        eq(h, 1_234_567L, sum, "breakdown total");
        eq(h, Economy.coin(CoinTier.VOID), parts.get(0).getItem(), "largest coin first");
        eq(h, 7, parts.size(), "one stack per tier");
        eq(h, 0, Coins.breakdown(0).size(), "zero amount");
        h.succeed();
    }

    @GameTest(template = FLOOR)
    public static void paymentMakesChange(GameTestHelper h) {
        ServerPlayer p = h.makeMockServerPlayerInLevel();
        p.getInventory().clearContent();
        p.getInventory().add(new ItemStack(Economy.coin(CoinTier.GOLD), 2)); // 200
        h.assertTrue(Coins.removeFromInventory(p, 35), "pay 35 from 200");
        eq(h, 165L, Coins.countInventory(p), "change returned");
        h.assertTrue(!Coins.removeFromInventory(p, 1000), "cannot overpay");
        eq(h, 165L, Coins.countInventory(p), "failed payment takes nothing");
        h.succeed();
    }

    @GameTest(template = FLOOR)
    public static void bankDepositWithdraw(GameTestHelper h) {
        ServerPlayer p = h.makeMockServerPlayerInLevel();
        Bank bank = Bank.get(h.getLevel().getServer());
        long start = bank.balance(p.getUUID());
        bank.deposit(p.getUUID(), 500);
        eq(h, start + 500, bank.balance(p.getUUID()), "after deposit");
        h.assertTrue(!bank.withdraw(p.getUUID(), start + 501), "overdraw refused");
        h.assertTrue(bank.withdraw(p.getUUID(), 200), "withdraw 200");
        eq(h, start + 300, bank.balance(p.getUUID()), "after withdraw");
        h.succeed();
    }

    @GameTest(template = FLOOR)
    public static void shopPurchaseTransfersItemsAndMoney(GameTestHelper h) {
        BlockPos rel = new BlockPos(2, 1, 2);
        h.setBlock(rel, Economy.SHOP_STALL.get());
        ShopStallBlockEntity be = (ShopStallBlockEntity) h.getLevel().getBlockEntity(h.absolutePos(rel));
        ServerPlayer seller = h.makeMockServerPlayerInLevel();
        ServerPlayer buyer = h.makeMockServerPlayerInLevel();
        be.setOwner(seller);
        be.setPrice(50);
        be.setBundle(4);
        be.stock.setItem(0, new ItemStack(Items.DIAMOND, 6));

        Bank bank = Bank.get(h.getLevel().getServer());
        long sellerBefore = bank.balance(seller.getUUID());
        buyer.getInventory().clearContent();
        buyer.getInventory().add(new ItemStack(Economy.coin(CoinTier.SILVER), 6)); // 60

        eq(h, ShopStallBlockEntity.Purchase.OWN_SHOP, be.buy(seller), "owner cannot buy");
        eq(h, ShopStallBlockEntity.Purchase.OK, be.buy(buyer), "first purchase");
        eq(h, 2, be.stockCount(), "stock reduced by bundle");
        eq(h, 10L, Coins.countInventory(buyer), "buyer paid 50");
        eq(h, sellerBefore + 50, bank.balance(seller.getUUID()), "seller credited");
        h.assertTrue(buyer.getInventory().countItem(Items.DIAMOND) == 4, "buyer received 4 diamonds");
        eq(h, ShopStallBlockEntity.Purchase.OUT_OF_STOCK, be.buy(buyer), "only 2 left of a 4-bundle");
        be.stock.setItem(1, new ItemStack(Items.DIAMOND, 10));
        eq(h, ShopStallBlockEntity.Purchase.CANNOT_AFFORD, be.buy(buyer), "buyer has 10 left");
        h.succeed();
    }

    @GameTest(template = FLOOR)
    public static void bossHealthScalesWithPlayers(GameTestHelper h) {
        eq(h, 400.0, CelestialBoss.scaledHealth(400, 1, 0.5), "solo");
        eq(h, 800.0, CelestialBoss.scaledHealth(400, 3, 0.5), "three players");
        eq(h, 400.0, CelestialBoss.scaledHealth(400, 0, 0.5), "no players counts as one");
        h.succeed();
    }

    @GameTest(template = FLOOR)
    public static void bossPhasesFromHealth(GameTestHelper h) {
        float[] t = {0.66f, 0.33f};
        eq(h, 0, CelestialBoss.phaseFor(1.0f, t), "full health");
        eq(h, 1, CelestialBoss.phaseFor(0.6f, t), "below 66%");
        eq(h, 2, CelestialBoss.phaseFor(0.1f, t), "below 33%");
        h.succeed();
    }

    @GameTest(template = FLOOR)
    public static void progressRecordsFirstKillOnly(GameTestHelper h) {
        ServerPlayer p = h.makeMockServerPlayerInLevel();
        ResourceLocation id = ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "frost_titan");
        h.assertTrue(!Progress.has(p, id), "fresh player has no kills");
        h.assertTrue(Progress.recordKill(p, id), "first kill is new");
        h.assertTrue(!Progress.recordKill(p, id), "second kill is not new");
        h.assertTrue(Progress.has(p, id), "kill remembered");
        h.assertTrue(p.getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.ARMOR)
                .getModifier(ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "constellation_frost")) != null, "constellation bonus applied");
        h.succeed();
    }
}
