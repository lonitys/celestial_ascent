package com.celestialascent.core;

import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.VoxelShape;

/** A facing block with a {@link DisplayBlockEntity}, so its decoration can be animated. */
public class DisplayFacingBlock extends FacingBlock implements EntityBlock {
    public DisplayFacingBlock(Properties props) {
        super(props);
    }

    public DisplayFacingBlock(Properties props, VoxelShape northShape) {
        super(props, northShape);
    }

    @Override
    protected MapCodec<? extends HorizontalDirectionalBlock> codec() {
        return simpleCodec(DisplayFacingBlock::new);
    }

    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new DisplayBlockEntity(pos, state);
    }
}
