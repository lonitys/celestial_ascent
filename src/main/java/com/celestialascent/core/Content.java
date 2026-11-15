package com.celestialascent.core;

import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredItem;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;

/** Registration helpers that also add entries to the creative tab and datagen lists. */
public final class Content {
    private Content() {}

    /** Items whose model is a flat generated sprite (datagen uses this list). */
    public static final List<DeferredItem<? extends Item>> FLAT_ITEMS = new ArrayList<>();
    /** Blocks registered through {@link #block}, with their block items. */
    public static final List<DeferredBlock<? extends Block>> BLOCKS = new ArrayList<>();

    public static <I extends Item> DeferredItem<I> item(String name, Supplier<I> sup) {
        DeferredItem<I> item = CAReg.ITEMS.register(name, sup);
        CAReg.TAB_ORDER.add(item);
        FLAT_ITEMS.add(item);
        return item;
    }

    /** Item that is registered but has a custom (non-flat) model. */
    public static <I extends Item> DeferredItem<I> customItem(String name, Supplier<I> sup) {
        DeferredItem<I> item = CAReg.ITEMS.register(name, sup);
        CAReg.TAB_ORDER.add(item);
        return item;
    }

    public static <B extends Block> DeferredBlock<B> block(String name, Supplier<B> sup) {
        return block(name, sup, new Item.Properties());
    }

    public static <B extends Block> DeferredBlock<B> block(String name, Supplier<B> sup, Item.Properties itemProps) {
        DeferredBlock<B> block = CAReg.BLOCKS.register(name, sup);
        DeferredItem<BlockItem> item = CAReg.ITEMS.register(name, () -> new BlockItem(block.get(), itemProps));
        CAReg.TAB_ORDER.add(item);
        BLOCKS.add(block);
        return block;
    }

    /** Block without an item (technical blocks such as portals). */
    public static <B extends Block> DeferredBlock<B> blockOnly(String name, Supplier<B> sup) {
        return CAReg.BLOCKS.register(name, sup);
    }
}
