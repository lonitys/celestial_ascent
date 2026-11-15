package com.celestialascent.compat;

import net.minecraft.world.level.ItemLike;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Fixed ProjectE EMC values, declared next to each item. Datagen writes them to
 * data/celestialascent/pe_custom_conversions/celestialascent.json, which ProjectE reads when installed.
 */
public final class Emc {
    private Emc() {}

    public static final Map<ItemLike, Long> VALUES = new LinkedHashMap<>();

    public static void set(ItemLike item, long value) {
        VALUES.put(item, value);
    }
}
