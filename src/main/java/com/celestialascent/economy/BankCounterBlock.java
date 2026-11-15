package com.celestialascent.economy;

import com.celestialascent.core.FacingBlock;
import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.ContainerLevelAccess;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/** Bank counter: deposit and withdraw Aster coins. Banker villager workstation. */
public class BankCounterBlock extends FacingBlock {
    private static final VoxelShape SHAPE = Shapes.or(
            Shapes.box(0, 0, 0.125, 1, 0.875, 1),
            Shapes.box(0, 0.875, 0, 1, 1, 1));

    public BankCounterBlock(Properties props) {
        super(props, SHAPE);
    }

    @Override
    protected MapCodec<? extends HorizontalDirectionalBlock> codec() {
        return simpleCodec(BankCounterBlock::new);
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (!level.isClientSide) {
            player.openMenu(new SimpleMenuProvider(
                    (id, inv, p) -> new BankMenu(id, inv, ContainerLevelAccess.create(level, pos)),
                    Component.translatable("container.celestialascent.bank")));
        }
        return InteractionResult.sidedSuccess(level.isClientSide);
    }
}
