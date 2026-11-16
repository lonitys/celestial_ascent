package com.celestialascent.core.station;

import com.celestialascent.CelestialAscent;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

import java.util.ArrayList;
import java.util.Collection;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.BiPredicate;

/**
 * Describes an upgrade station: GUI layout, processing time, recipes and an optional world condition
 * (for example the Sky Altar only works at night under open sky).
 */
public final class StationType {
    private static final Map<String, StationType> BY_ID = new LinkedHashMap<>();

    public final String id;
    public final ResourceLocation gui;
    public final int imageHeight;
    public final int[] base;
    public final int[][] mats;
    public final int[] output;
    public final int[] arrow;
    public final int processTicks;
    public final List<StationRecipe> recipes = new ArrayList<>();
    private BiPredicate<Level, BlockPos> condition = (l, p) -> true;
    private String conditionKey;

    public StationType(String id, int processTicks, int[] base, int[][] mats, int[] output, int[] arrow) {
        this.id = id;
        this.gui = ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "textures/gui/" + id + ".png");
        this.imageHeight = 166;
        this.processTicks = processTicks;
        this.base = base;
        this.mats = mats;
        this.output = output;
        this.arrow = arrow;
        BY_ID.put(id, this);
    }

    public static StationType byId(String id) {
        return BY_ID.get(id);
    }

    /** Every station type, in registration order. */
    public static Collection<StationType> all() {
        return BY_ID.values();
    }

    public StationType condition(BiPredicate<Level, BlockPos> c, String translationKey) {
        this.condition = c;
        this.conditionKey = translationKey;
        return this;
    }

    public boolean conditionMet(Level level, BlockPos pos) {
        return condition.test(level, pos);
    }

    public String conditionKey() {
        return conditionKey;
    }

    public void add(StationRecipe r) {
        recipes.add(r);
    }

    public StationRecipe find(ItemStack base, List<ItemStack> mats) {
        for (StationRecipe r : recipes) if (r.matches(base, mats)) return r;
        return null;
    }

    /** Container size: base + materials + output. */
    public int size() {
        return 2 + mats.length;
    }
}
