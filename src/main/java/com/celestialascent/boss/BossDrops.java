package com.celestialascent.boss;

import com.celestialascent.abyss.Abyss;
import com.celestialascent.economy.CoinTier;
import com.celestialascent.economy.Economy;
import com.celestialascent.empire.Empire;
import com.celestialascent.stars.Stars;
import com.celestialascent.titans.Element;
import com.celestialascent.titans.Titans;
import com.google.common.base.Suppliers;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.ItemLike;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.function.Supplier;

/**
 * Boss drops in one place: datagen builds the loot tables from it and recipe viewers (JEI) show it, since
 * loot tables are not sent to clients. Every pool is guaranteed (one roll, a uniform count); looting adds
 * up to one more per level where {@code looting} is set.
 */
public final class BossDrops {
    private BossDrops() {}

    public record Drop(Supplier<? extends ItemLike> item, int min, int max, boolean looting) {}

    public record Entry(Supplier<? extends EntityType<?>> type, List<Drop> drops) {}

    private static final Supplier<List<Entry>> ALL = Suppliers.memoize(BossDrops::build);

    /** Every boss with its drops, in ladder order. Needs registered items, so it is built on first use. */
    public static List<Entry> all() {
        return ALL.get();
    }

    public static Optional<Entry> of(EntityType<?> type) {
        return all().stream().filter(e -> e.type().get() == type).findFirst();
    }

    private static Drop fixed(Supplier<? extends ItemLike> item, int min, int max) {
        return new Drop(item, min, max, false);
    }

    private static Drop looted(Supplier<? extends ItemLike> item, int min, int max) {
        return new Drop(item, min, max, true);
    }

    private static Supplier<? extends ItemLike> coin(CoinTier t) {
        return Economy.COINS.get(t);
    }

    private static List<Entry> build() {
        List<Entry> out = new ArrayList<>();
        for (Element e : Element.values()) {
            out.add(new Entry(() -> Titans.titanType(e), List.of(
                    fixed(Titans.CORES.get(e), 1, 1),
                    looted(Titans.TITAN_SHARD, 3, 5),
                    fixed(coin(CoinTier.TITAN), 1, 3),
                    fixed(coin(CoinTier.GOLD), 4, 9))));
        }
        out.add(new Entry(Empire.SENTINEL, List.of(
                looted(Empire.IMPERIAL_PLATING, 2, 4),
                looted(Empire.ENDER_GEAR, 1, 3),
                fixed(coin(CoinTier.TITAN), 1, 2))));
        out.add(new Entry(Empire.COLOSSUS, List.of(
                fixed(Empire.COLOSSUS_CORE, 1, 1),
                fixed(Empire.IMPERIAL_SEAL, 1, 1),
                looted(Empire.ENDER_GEAR, 3, 6),
                looted(Empire.IMPERIAL_PLATING, 4, 8),
                fixed(coin(CoinTier.ENDER), 1, 2),
                fixed(coin(CoinTier.TITAN), 3, 6))));
        for (Supplier<? extends EntityType<?>> type : List.of(Stars.SERAPH, Stars.LEVIATHAN, Stars.HERALD)) {
            out.add(new Entry(type, List.of(
                    fixed(Stars.DORMANT_STAR_CORE, 1, 1),
                    looted(Stars.STARDUST, 8, 16),
                    fixed(coin(CoinTier.STAR), 1, 1),
                    fixed(coin(CoinTier.ENDER), 2, 4))));
        }
        out.add(new Entry(Abyss.VOID_SOVEREIGN, List.of(
                fixed(Abyss.VOID_HEART, 1, 1),
                looted(Abyss.VOID_ESSENCE, 12, 24),
                fixed(coin(CoinTier.VOID), 1, 2),
                fixed(coin(CoinTier.STAR), 3, 6))));
        return List.copyOf(out);
    }
}
