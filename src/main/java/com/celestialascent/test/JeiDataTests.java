package com.celestialascent.test;

import com.celestialascent.CelestialAscent;
import com.celestialascent.boss.BossDrops;
import com.celestialascent.boss.BossSummons;
import com.celestialascent.core.station.StationRecipe;
import com.celestialascent.core.station.StationType;
import com.celestialascent.economy.Professions;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.npc.Villager;
import net.minecraft.world.entity.npc.VillagerProfession;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.trading.MerchantOffer;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.storage.loot.LootParams;
import net.minecraft.world.level.storage.loot.LootTable;
import net.minecraft.world.level.storage.loot.parameters.LootContextParamSets;
import net.minecraft.world.level.storage.loot.parameters.LootContextParams;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Supplier;

/** The display data recipe viewers (JEI) show: it has to agree with what the game really does. */
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
                    CoreTests.eq(h, e.result().getItem(), r.result().apply(e.base().copy()).getItem(), type.id + ": example result");
                    n++;
                }
            }
        }
        h.assertTrue(n > 100, "expected well over 100 examples, got " + n);
        h.succeed();
    }

    /** The drops JEI lists for each boss are exactly what its generated loot table gives (without looting). */
    @GameTest(template = CoreTests.FLOOR)
    public static void bossDropsMatchLootTables(GameTestHelper h) {
        var server = h.getLevel().getServer();
        h.assertTrue(BossDrops.all().size() == 10, "ten bosses have drop tables, got " + BossDrops.all().size());
        for (BossDrops.Entry e : BossDrops.all()) {
            EntityType<?> type = e.type().get();
            LootTable table = server.reloadableRegistries().getLootTable(type.getDefaultLootTable());
            LootParams params = new LootParams.Builder(h.getLevel())
                    .withParameter(LootContextParams.THIS_ENTITY, h.makeMockPlayer(GameType.SURVIVAL))
                    .withParameter(LootContextParams.ORIGIN, Vec3.ZERO)
                    .withParameter(LootContextParams.DAMAGE_SOURCE, h.getLevel().damageSources().generic())
                    .create(LootContextParamSets.ENTITY);
            Map<Item, BossDrops.Drop> listed = new HashMap<>();
            for (BossDrops.Drop d : e.drops()) listed.put(d.item().get().asItem(), d);
            Set<Item> inTable = new HashSet<>();
            // Every boss pool is guaranteed, so rolling often sees every item and checks the counts.
            for (int i = 0; i < 64; i++) {
                Map<Item, Integer> roll = new HashMap<>();
                for (ItemStack s : table.getRandomItems(params)) roll.merge(s.getItem(), s.getCount(), Integer::sum);
                for (var r : roll.entrySet()) {
                    inTable.add(r.getKey());
                    BossDrops.Drop d = listed.get(r.getKey());
                    if (d != null) h.assertTrue(r.getValue() >= d.min() && r.getValue() <= d.max(),
                            type.getDescriptionId() + ": " + r.getValue() + " x " + r.getKey() + " is outside " + d.min() + "-" + d.max());
                }
            }
            h.assertTrue(inTable.equals(listed.keySet()), type.getDescriptionId() + ": JEI lists " + listed.keySet() + " but the table drops " + inTable);
        }
        h.assertTrue(BossSummons.all().size() == 11, "ten bosses and the Ender Dragon can be summoned, got " + BossSummons.all().size());
        for (BossSummons.Summon s : BossSummons.all()) {
            h.assertTrue(!BossSummons.drops(s).isEmpty(), s.type().get().getDescriptionId() + " shows its drops");
        }
        h.succeed();
    }

    /** Every trade of the three professions has a display, and fixed trades show exactly the offer they make. */
    @GameTest(template = CoreTests.FLOOR)
    public static void tradesHaveDisplays(GameTestHelper h) {
        Villager trader = h.spawn(EntityType.VILLAGER, 1, 2, 1);
        int compared = 0;
        for (Supplier<VillagerProfession> prof : List.of(Professions.BANKER, Professions.TITANSMITH, Professions.RELIC_DEALER)) {
            List<Professions.TradeDisplay> list = Professions.displays(prof);
            h.assertTrue(list.size() >= 5, "few trades for " + prof.get());
            for (Professions.TradeDisplay t : list) {
                h.assertTrue(!t.result().get().isEmpty() && !t.costA().get().isEmpty(), "empty trade display for " + prof.get());
                h.assertTrue(t.level() >= 1 && t.level() <= 5, "bad level " + t.level());
            }
            for (Professions.Trade t : Professions.trades(prof)) {
                if (t.display().result().get().is(Items.FILLED_MAP)) continue; // shrine maps search the world for a shrine
                MerchantOffer offer = t.listing().getOffer(trader, trader.getRandom());
                h.assertTrue(offer != null, prof.get() + ": a fixed trade made no offer");
                String what = prof.get() + " level " + t.display().level() + " " + offer.getResult();
                h.assertTrue(ItemStack.isSameItemSameComponents(offer.getCostA(), t.display().costA().get())
                        && offer.getCostA().getCount() == t.display().costA().get().getCount(), what + ": first cost differs");
                h.assertTrue(ItemStack.isSameItemSameComponents(offer.getCostB(), t.display().costB().get())
                        && offer.getCostB().getCount() == t.display().costB().get().getCount(), what + ": second cost differs");
                h.assertTrue(ItemStack.isSameItemSameComponents(offer.getResult(), t.display().result().get())
                        && offer.getResult().getCount() == t.display().result().get().getCount(), what + ": result differs");
                compared++;
            }
        }
        h.assertTrue(compared >= 25, "compared only " + compared + " offers with their displays");
        h.succeed();
    }
}
