package com.celestialascent.core;

import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

import java.util.EnumMap;
import java.util.Map;

/** Horizontally-facing block with a custom shape (defined for NORTH and rotated). */
public class FacingBlock extends HorizontalDirectionalBlock {
    private final Map<Direction, VoxelShape> shapes = new EnumMap<>(Direction.class);

    public FacingBlock(Properties props) {
        this(props, Shapes.block());
    }

    public FacingBlock(Properties props, VoxelShape northShape) {
        super(props);
        registerDefaultState(stateDefinition.any().setValue(FACING, Direction.NORTH));
        for (Direction d : Direction.Plane.HORIZONTAL) shapes.put(d, rotate(northShape, d));
    }

    /** Rotates a shape defined for NORTH to face {@code to}. */
    public static VoxelShape rotate(VoxelShape shape, Direction to) {
        VoxelShape[] out = {Shapes.empty()};
        int times = (to.get2DDataValue() - Direction.NORTH.get2DDataValue() + 4) % 4;
        shape.forAllBoxes((x1, y1, z1, x2, y2, z2) -> {
            double ax1 = x1, az1 = z1, ax2 = x2, az2 = z2;
            for (int i = 0; i < times; i++) {
                double nx1 = 1 - az2, nz1 = ax1, nx2 = 1 - az1, nz2 = ax2;
                ax1 = nx1; az1 = nz1; ax2 = nx2; az2 = nz2;
            }
            out[0] = Shapes.or(out[0], Shapes.box(ax1, y1, az1, ax2, y2, az2));
        });
        return out[0];
    }

    @Override
    protected MapCodec<? extends HorizontalDirectionalBlock> codec() {
        return simpleCodec(FacingBlock::new);
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
        b.add(FACING);
    }

    @Override
    public BlockState getStateForPlacement(BlockPlaceContext ctx) {
        return defaultBlockState().setValue(FACING, ctx.getHorizontalDirection().getOpposite());
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
        return shapes.get(state.getValue(FACING));
    }
}
