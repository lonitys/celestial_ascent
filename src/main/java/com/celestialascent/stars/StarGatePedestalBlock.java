package com.celestialascent.stars;

import com.celestialascent.core.FacingBlock;
import com.celestialascent.empire.Empire;
import com.mojang.serialization.MapCodec;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.ItemInteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.Shapes;

/**
 * Star Gate pedestal. Place a Dragon Head on it, then present the Imperial Seal: the 3x3 gate floor
 * five blocks in front of the pedestal (one block lower) becomes a Star Portal.
 */
public class StarGatePedestalBlock extends FacingBlock implements net.minecraft.world.level.block.EntityBlock {
    public static final BooleanProperty HEAD = BooleanProperty.create("head");

    public StarGatePedestalBlock(Properties props) {
        super(props, Shapes.or(Shapes.box(0.125, 0, 0.125, 0.875, 0.25, 0.875), Shapes.box(0.25, 0.25, 0.25, 0.75, 0.875, 0.75),
                Shapes.box(0.125, 0.875, 0.125, 0.875, 1, 0.875)));
        registerDefaultState(defaultBlockState().setValue(HEAD, false));
    }

    @Override
    protected MapCodec<? extends HorizontalDirectionalBlock> codec() {
        return simpleCodec(StarGatePedestalBlock::new);
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
        super.createBlockStateDefinition(b);
        b.add(HEAD);
    }

    public static BlockPos gateCenter(BlockPos pedestal, BlockState state) {
        return pedestal.relative(state.getValue(FACING), 5).below();
    }

    @Override
    protected ItemInteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player,
                                              InteractionHand hand, BlockHitResult hit) {
        if (level.isClientSide) return ItemInteractionResult.SUCCESS;
        ServerLevel sl = (ServerLevel) level;
        if (!state.getValue(HEAD)) {
            if (stack.is(Items.DRAGON_HEAD)) {
                if (!player.getAbilities().instabuild) stack.shrink(1);
                level.setBlockAndUpdate(pos, state.setValue(HEAD, true));
                sl.playSound(null, pos, SoundEvents.ENDER_DRAGON_GROWL, SoundSource.BLOCKS, 1f, 1.2f);
                player.displayClientMessage(Component.translatable("message.celestialascent.gate_head"), true);
            } else {
                player.displayClientMessage(Component.translatable("message.celestialascent.gate_needs_head").withStyle(ChatFormatting.LIGHT_PURPLE), true);
            }
            return ItemInteractionResult.CONSUME;
        }
        if (!stack.is(Empire.IMPERIAL_SEAL.get())) {
            player.displayClientMessage(Component.translatable("message.celestialascent.gate_needs_seal").withStyle(ChatFormatting.LIGHT_PURPLE), true);
            return ItemInteractionResult.CONSUME;
        }
        BlockPos c = gateCenter(pos, state);
        for (int dx = -1; dx <= 1; dx++)
            for (int dz = -1; dz <= 1; dz++) sl.setBlockAndUpdate(c.offset(dx, 0, dz), Stars.STAR_PORTAL.get().defaultBlockState());
        sl.playSound(null, c, SoundEvents.END_PORTAL_SPAWN, SoundSource.BLOCKS, 3f, 1.2f);
        sl.sendParticles(ParticleTypes.END_ROD, c.getX() + 0.5, c.getY() + 1, c.getZ() + 0.5, 150, 1.5, 2, 1.5, 0.1);
        Component msg = Component.translatable("message.celestialascent.gate_open").withColor(0xFFFFFF);
        for (Player p : sl.getEntitiesOfClass(Player.class, new AABB(pos).inflate(48))) p.sendSystemMessage(msg);
        return ItemInteractionResult.CONSUME;
    }

    @Override
    public net.minecraft.world.level.block.entity.BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new com.celestialascent.core.DisplayBlockEntity(pos, state); // draws the floating dragon head
    }
}
