package com.celestialascent.economy;

import net.minecraft.world.item.Rarity;

/** Aster coin denominations. Each tier is worth ten of the tier below. */
public enum CoinTier {
    COPPER("copper_aster", 1L, Rarity.COMMON),
    SILVER("silver_aster", 10L, Rarity.COMMON),
    GOLD("gold_aster", 100L, Rarity.UNCOMMON),
    TITAN("titan_aster", 1_000L, Rarity.UNCOMMON),
    ENDER("ender_aster", 10_000L, Rarity.RARE),
    STAR("star_aster", 100_000L, Rarity.EPIC),
    VOID("void_aster", 1_000_000L, Rarity.EPIC);

    public final String id;
    public final long value;
    public final Rarity rarity;

    CoinTier(String id, long value, Rarity rarity) {
        this.id = id;
        this.value = value;
        this.rarity = rarity;
    }
}
