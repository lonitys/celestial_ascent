package com.celestialascent.core;

import com.celestialascent.economy.Economy;
import com.celestialascent.stars.Stars;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.neoforge.registries.DeferredHolder;

/** Block entity without data. It only exists so a block can draw animated parts (floating crystals, the gate's dragon head). */
public class DisplayBlockEntity extends BlockEntity {
    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<DisplayBlockEntity>> TYPE = CAReg.BLOCK_ENTITIES.register("display",
            () -> BlockEntityType.Builder.of(DisplayBlockEntity::new, Economy.RELIC_PEDESTAL.get(), Economy.CELESTIAL_CRYSTAL.get(), Stars.STAR_GATE_PEDESTAL.get()).build(null));

    public DisplayBlockEntity(BlockPos pos, BlockState state) {
        super(TYPE.get(), pos, state);
    }
}
