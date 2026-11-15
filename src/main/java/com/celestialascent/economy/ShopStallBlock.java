package com.celestialascent.economy;

import com.celestialascent.core.FacingBlock;
import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.Containers;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jetbrains.annotations.Nullable;

/** Market stall that sells the owner's stock. Only the owner (or creative players) can break it. */
public class ShopStallBlock extends FacingBlock implements EntityBlock {
    private static final VoxelShape SHAPE = Shapes.or(
            Shapes.box(0, 0, 0, 1, 0.75, 1),
            Shapes.box(0, 0.75, 0.75, 1, 1, 1));

    public ShopStallBlock(Properties props) {
        super(props, SHAPE);
    }

    @Override
    protected MapCodec<? extends HorizontalDirectionalBlock> codec() {
        return simpleCodec(ShopStallBlock::new);
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new ShopStallBlockEntity(pos, state);
    }

    @Override
    public void setPlacedBy(Level level, BlockPos pos, BlockState state, @Nullable LivingEntity placer, ItemStack stack) {
        super.setPlacedBy(level, pos, state, placer, stack);
        if (!level.isClientSide && placer instanceof Player p && level.getBlockEntity(pos) instanceof ShopStallBlockEntity be) {
            be.setOwner(p);
        }
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (!level.isClientSide && player instanceof ServerPlayer sp && level.getBlockEntity(pos) instanceof ShopStallBlockEntity be) {
            if (!be.hasOwner()) {
                if (sp.isShiftKeyDown() && Coins.pay(sp, ShopStallBlockEntity.RENT)) {
                    be.setOwner(sp);
                    sp.displayClientMessage(Component.translatable("message.celestialascent.stall_rented"), true);
                } else {
                    sp.displayClientMessage(Component.translatable("message.celestialascent.stall_unclaimed", Coins.format(ShopStallBlockEntity.RENT)), true);
                }
                return InteractionResult.CONSUME;
            }
            boolean owner = be.isOwner(sp) && !sp.isShiftKeyDown();
            Component title = owner ? Component.translatable("container.celestialascent.shop_manage")
                    : Component.translatable("container.celestialascent.shop", be.ownerName());
            sp.openMenu(new SimpleMenuProvider((id, inv, p) -> ShopMenu.server(id, inv, be, owner), title), buf -> {
                buf.writeBlockPos(pos);
                buf.writeBoolean(owner);
            });
        }
        return InteractionResult.sidedSuccess(level.isClientSide);
    }

    @Override
    protected float getDestroyProgress(BlockState state, Player player, BlockGetter level, BlockPos pos) {
        if (level.getBlockEntity(pos) instanceof ShopStallBlockEntity be && !be.isOwner(player) && !player.isCreative()) {
            return 0f;
        }
        return super.getDestroyProgress(state, player, level, pos);
    }

    @Override
    protected void onRemove(BlockState state, Level level, BlockPos pos, BlockState newState, boolean moved) {
        if (!state.is(newState.getBlock()) && level.getBlockEntity(pos) instanceof ShopStallBlockEntity be) {
            Containers.dropContents(level, pos, be.stock);
        }
        super.onRemove(state, level, pos, newState, moved);
    }
}
