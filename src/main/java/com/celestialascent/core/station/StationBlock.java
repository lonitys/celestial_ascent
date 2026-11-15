package com.celestialascent.core.station;

import com.celestialascent.core.FacingBlock;
import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.Containers;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jetbrains.annotations.Nullable;

import java.util.function.Supplier;

/** Block for an upgrade station; its {@link StationType} defines layout and recipes. */
public class StationBlock extends FacingBlock implements EntityBlock {
    private final Supplier<StationType> type;

    public StationBlock(Properties props, Supplier<StationType> type) {
        this(props, type, Shapes.block());
    }

    public StationBlock(Properties props, Supplier<StationType> type, VoxelShape shape) {
        super(props, shape);
        this.type = type;
    }

    public StationType type() {
        return type.get();
    }

    @Override
    protected MapCodec<? extends HorizontalDirectionalBlock> codec() {
        throw new UnsupportedOperationException("Station blocks are not data-driven");
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new StationBlockEntity(pos, state);
    }

    @Nullable
    @Override
    @SuppressWarnings("unchecked")
    public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level level, BlockState state, BlockEntityType<T> t) {
        if (level.isClientSide || t != Stations.BE.get()) return null;
        return (lvl, pos, st, be) -> StationBlockEntity.serverTick(lvl, pos, st, (StationBlockEntity) be);
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (!level.isClientSide && player instanceof ServerPlayer sp && level.getBlockEntity(pos) instanceof StationBlockEntity be) {
            sp.openMenu(new SimpleMenuProvider((id, inv, p) -> new StationMenu(id, inv, be),
                    Component.translatable("container.celestialascent." + type().id)), buf -> buf.writeUtf(type().id));
        }
        return InteractionResult.sidedSuccess(level.isClientSide);
    }

    @Override
    protected void onRemove(BlockState state, Level level, BlockPos pos, BlockState newState, boolean moved) {
        if (!state.is(newState.getBlock()) && level.getBlockEntity(pos) instanceof StationBlockEntity be) {
            Containers.dropContents(level, pos, be.items);
        }
        super.onRemove(state, level, pos, newState, moved);
    }
}
