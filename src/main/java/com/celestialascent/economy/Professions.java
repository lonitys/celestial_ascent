package com.celestialascent.economy;

import com.celestialascent.CelestialAscent;
import com.celestialascent.core.CAReg;
import com.celestialascent.core.ModConfig;
import com.google.common.collect.ImmutableSet;
import it.unimi.dsi.fastutil.ints.Int2ObjectMap;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.ai.village.poi.PoiType;
import net.minecraft.world.entity.npc.VillagerProfession;
import net.minecraft.world.entity.npc.VillagerTrades;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.trading.ItemCost;
import net.minecraft.world.item.trading.MerchantOffer;
import net.minecraft.world.level.ItemLike;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.village.VillagerTradesEvent;
import net.neoforged.neoforge.registries.DeferredHolder;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.function.Supplier;

/** Banker, Titansmith and Relic Dealer professions. Other modules add trades through {@link #trade}. */
@EventBusSubscriber(modid = CelestialAscent.MODID)
public final class Professions {
    private Professions() {}

    private static Set<BlockState> allStates(Supplier<? extends Block> block) {
        return ImmutableSet.copyOf(block.get().getStateDefinition().getPossibleStates());
    }

    public static final DeferredHolder<PoiType, PoiType> BANKER_POI = CAReg.POI.register("banker",
            () -> new PoiType(allStates(Economy.BANK_COUNTER), 1, 1));
    public static final DeferredHolder<PoiType, PoiType> TITANSMITH_POI = CAReg.POI.register("titansmith",
            () -> new PoiType(allStates(Economy.TITAN_ANVIL), 1, 1));
    public static final DeferredHolder<PoiType, PoiType> RELIC_DEALER_POI = CAReg.POI.register("relic_dealer",
            () -> new PoiType(allStates(Economy.RELIC_PEDESTAL), 1, 1));

    public static final DeferredHolder<VillagerProfession, VillagerProfession> BANKER = profession("banker", BANKER_POI);
    public static final DeferredHolder<VillagerProfession, VillagerProfession> TITANSMITH = profession("titansmith", TITANSMITH_POI);
    public static final DeferredHolder<VillagerProfession, VillagerProfession> RELIC_DEALER = profession("relic_dealer", RELIC_DEALER_POI);

    private static DeferredHolder<VillagerProfession, VillagerProfession> profession(String name, DeferredHolder<PoiType, PoiType> poi) {
        return CAReg.PROFESSIONS.register(name, () -> new VillagerProfession(name,
                h -> h.is(poi.getKey()), h -> h.is(poi.getKey()), ImmutableSet.of(), ImmutableSet.of(),
                SoundEvents.VILLAGER_WORK_CARTOGRAPHER));
    }

    private static final Map<Supplier<VillagerProfession>, Map<Integer, List<VillagerTrades.ItemListing>>> TRADES = new HashMap<>();

    /** Adds a trade for a profession at a villager level (1..5). */
    public static void trade(Supplier<VillagerProfession> prof, int level, VillagerTrades.ItemListing listing) {
        TRADES.computeIfAbsent(prof, p -> new HashMap<>()).computeIfAbsent(level, l -> new ArrayList<>()).add(listing);
    }

    /**
     * Fixed trade. Items are resolved when the offer is generated, so deferred items may be passed
     * before registration completes.
     */
    public static VillagerTrades.ItemListing offer(ItemLike cost, int costCount, ItemLike result, int resultCount, int maxUses, int xp) {
        return (trader, random) -> new MerchantOffer(new ItemCost(cost, costCount), new ItemStack(result, resultCount), maxUses, xp, 0.05f);
    }

    public static VillagerTrades.ItemListing offer2(ItemLike cost, int costCount, ItemLike cost2, int cost2Count,
                                                    ItemLike result, int resultCount, int maxUses, int xp) {
        return (trader, random) -> new MerchantOffer(new ItemCost(cost, costCount), Optional.of(new ItemCost(cost2, cost2Count)),
                new ItemStack(result, resultCount), maxUses, xp, 0.05f);
    }

    /** Deferred coin reference (safe to use before registration). */
    public static ItemLike coin(CoinTier t) {
        return Economy.COINS.get(t);
    }

    public static void init() {
        // Banker: currency exchange and savings goods.
        trade(BANKER, 1, (trader, random) -> new MerchantOffer(new ItemCost(Items.EMERALD, 1),
                new ItemStack(coin(CoinTier.COPPER), ModConfig.EMERALD_TO_COPPER.get()), 32, 2, 0.0f));
        trade(BANKER, 1, offer(coin(CoinTier.COPPER), 8, Items.EMERALD, 1, 32, 2));
        trade(BANKER, 2, offer(Items.GOLD_INGOT, 4, coin(CoinTier.SILVER), 1, 16, 5));
        trade(BANKER, 2, offer(Items.DIAMOND, 1, coin(CoinTier.SILVER), 3, 16, 10));
        trade(BANKER, 3, offer(coin(CoinTier.SILVER), 4, Items.DIAMOND, 1, 12, 10));
        trade(BANKER, 3, offer(coin(CoinTier.SILVER), 2, Items.NAME_TAG, 1, 8, 10));
        trade(BANKER, 4, offer(Items.NETHERITE_INGOT, 1, coin(CoinTier.GOLD), 3, 8, 20));
        trade(BANKER, 4, offer(coin(CoinTier.GOLD), 1, Items.ENDER_PEARL, 8, 8, 15));
        trade(BANKER, 5, offer(coin(CoinTier.GOLD), 4, Items.NETHERITE_SCRAP, 1, 4, 30));
        trade(BANKER, 5, offer(coin(CoinTier.GOLD), 2, Items.TOTEM_OF_UNDYING, 1, 2, 30));

        // Titansmith: metals and netherite (titan materials are added by the titans module).
        trade(TITANSMITH, 1, offer(Items.IRON_INGOT, 6, coin(CoinTier.COPPER), 4, 16, 2));
        trade(TITANSMITH, 1, offer(coin(CoinTier.COPPER), 6, Items.IRON_BLOCK, 1, 12, 2));
        trade(TITANSMITH, 2, offer(Items.DIAMOND, 2, coin(CoinTier.SILVER), 5, 12, 10));
        trade(TITANSMITH, 3, offer(Items.NETHERITE_SCRAP, 1, coin(CoinTier.SILVER), 9, 8, 15));
        trade(TITANSMITH, 4, offer(coin(CoinTier.GOLD), 2, Items.NETHERITE_UPGRADE_SMITHING_TEMPLATE, 1, 4, 20));

        // Relic dealer: rare goods (boss materials are added by the ladder modules).
        trade(RELIC_DEALER, 1, offer(coin(CoinTier.GOLD), 1, Items.ECHO_SHARD, 2, 8, 10));
        trade(RELIC_DEALER, 2, offer(coin(CoinTier.GOLD), 3, Items.HEART_OF_THE_SEA, 1, 4, 15));
        trade(RELIC_DEALER, 3, offer(coin(CoinTier.GOLD), 5, Items.NETHER_STAR, 1, 2, 25));
        trade(RELIC_DEALER, 4, offer(coin(CoinTier.TITAN), 2, Items.ELYTRA, 1, 1, 30));
        trade(RELIC_DEALER, 5, offer(coin(CoinTier.TITAN), 3, Items.DRAGON_HEAD, 1, 1, 40));
    }

    @SubscribeEvent
    public static void onTrades(VillagerTradesEvent e) {
        for (Map.Entry<Supplier<VillagerProfession>, Map<Integer, List<VillagerTrades.ItemListing>>> entry : TRADES.entrySet()) {
            if (e.getType() != entry.getKey().get()) continue;
            Int2ObjectMap<List<VillagerTrades.ItemListing>> trades = e.getTrades();
            entry.getValue().forEach((lvl, list) -> trades.computeIfAbsent((int) lvl, k -> new ArrayList<>()).addAll(list));
        }
    }
}
