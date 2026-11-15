package com.celestialascent.core.station;

import com.celestialascent.core.CAReg;
import com.celestialascent.core.Content;
import net.minecraft.world.inventory.MenuType;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.neoforged.neoforge.common.extensions.IMenuTypeExtension;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;

import java.util.ArrayList;
import java.util.List;

/** Shared block entity and menu types for every upgrade station. */
public final class Stations {
    private Stations() {}

    /** Every station block, collected as modules register them. */
    public static final List<DeferredBlock<? extends StationBlock>> BLOCKS = new ArrayList<>();

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<StationBlockEntity>> BE =
            CAReg.BLOCK_ENTITIES.register("station", () -> BlockEntityType.Builder.of(StationBlockEntity::new,
                    BLOCKS.stream().map(DeferredBlock::get).toArray(Block[]::new)).build(null));

    public static final DeferredHolder<MenuType<?>, MenuType<StationMenu>> MENU =
            CAReg.MENUS.register("station", () -> IMenuTypeExtension.create(StationMenu::client));

    public static <B extends StationBlock> DeferredBlock<B> register(String name, java.util.function.Supplier<B> sup) {
        DeferredBlock<B> b = Content.block(name, sup);
        BLOCKS.add(b);
        return b;
    }
}
