package com.celestialascent.titans;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;

/** Temporary crust created when walking on lava in Magma II armor; melts back into lava. */
public class CooledMagmaBlock extends Block {
    public CooledMagmaBlock(Properties props) {
        super(props);
    }

    @Override
    protected void tick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        level.setBlockAndUpdate(pos, Blocks.LAVA.defaultBlockState());
    }
}
