package com.celestialascent.empire;

import com.celestialascent.core.FacingBlock;
import com.celestialascent.core.Scheduler;
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
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.Shapes;

/** The Empty Throne: offer a Dragon Heart to wake the Ender Colossus. */
public class ThroneBlock extends FacingBlock {
    public ThroneBlock(Properties props) {
        super(props, Shapes.or(Shapes.box(0, 0, 0, 1, 0.5, 1), Shapes.box(0, 0.5, 0.75, 1, 1, 1)));
    }

    @Override
    protected MapCodec<? extends HorizontalDirectionalBlock> codec() {
        return simpleCodec(ThroneBlock::new);
    }

    @Override
    protected ItemInteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player,
                                              InteractionHand hand, BlockHitResult hit) {
        if (!stack.is(Empire.DRAGON_HEART.get())) {
            if (!level.isClientSide) player.displayClientMessage(Component.translatable("message.celestialascent.throne_hint"), true);
            return ItemInteractionResult.sidedSuccess(level.isClientSide);
        }
        if (level.isClientSide) return ItemInteractionResult.SUCCESS;
        ServerLevel sl = (ServerLevel) level;
        if (!level.getEntitiesOfClass(EnderColossus.class, new AABB(pos).inflate(64)).isEmpty()) {
            player.displayClientMessage(Component.translatable("message.celestialascent.titan_present").withStyle(ChatFormatting.RED), true);
            return ItemInteractionResult.CONSUME;
        }
        if (!player.getAbilities().instabuild) stack.shrink(1);
        Vec3 c = Vec3.atCenterOf(pos);
        sl.playSound(null, pos, SoundEvents.END_PORTAL_SPAWN, SoundSource.BLOCKS, 2f, 0.6f);
        for (int t = 0; t < 60; t += 4) {
            int tick = t;
            Scheduler.later(sl, t + 1, () -> sl.sendParticles(ParticleTypes.REVERSE_PORTAL, c.x, c.y + 1 + tick / 15.0, c.z, 30, 1.2, 0.6, 1.2, 0.08));
        }
        Scheduler.later(sl, 60, () -> {
            EnderColossus boss = Empire.COLOSSUS.get().create(sl);
            if (boss == null) return;
            var facing = state.getValue(FACING);
            BlockPos spawn = pos.relative(facing, 7);
            boss.moveTo(spawn.getX() + 0.5, spawn.getY(), spawn.getZ() + 0.5, facing.toYRot() + 180, 0);
            boss.setHome(pos);
            sl.addFreshEntity(boss);
            sl.sendParticles(ParticleTypes.EXPLOSION_EMITTER, boss.getX(), boss.getY() + 2, boss.getZ(), 1, 0, 0, 0, 0);
            sl.playSound(null, pos, SoundEvents.WITHER_SPAWN, SoundSource.HOSTILE, 3f, 0.5f);
            Component msg = Component.translatable("message.celestialascent.colossus_awakens").withColor(0x8E6BFF);
            for (Player p : sl.getEntitiesOfClass(Player.class, new AABB(pos).inflate(64))) p.sendSystemMessage(msg);
        });
        return ItemInteractionResult.CONSUME;
    }
}
