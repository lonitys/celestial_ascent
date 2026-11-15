package com.celestialascent.abyss;

import com.celestialascent.core.ModConfig;
import com.celestialascent.core.Scheduler;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.IntegerProperty;

/**
 * Abyssal stone cracks under players' feet and crumbles away; the deeper you are, the faster.
 * Crumbled blocks reform after a minute.
 */
public class AbyssalStoneBlock extends Block {
    public static final IntegerProperty CRACK = IntegerProperty.create("crack", 0, 3);

    public AbyssalStoneBlock(Properties props) {
        super(props);
        registerDefaultState(stateDefinition.any().setValue(CRACK, 0));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
        b.add(CRACK);
    }

    /** Ticks per crack stage at height y (shallow 40, middle 24, deep 12), scaled by config. */
    public static int stageTicks(int y) {
        int base = y > 64 ? 40 : y > 0 ? 24 : 12;
        double speed = ModConfig.ABYSS_CRUMBLE_SPEED.get();
        return speed <= 0 ? Integer.MAX_VALUE : Math.max(2, (int) Math.round(base / speed));
    }

    @Override
    public void stepOn(Level level, BlockPos pos, BlockState state, Entity entity) {
        if (!level.isClientSide && entity instanceof Player p && !p.isCreative() && !p.isSpectator() && state.getValue(CRACK) == 0
                && !level.getBlockTicks().hasScheduledTick(pos, this)) {
            int t = stageTicks(pos.getY());
            if (t != Integer.MAX_VALUE) level.scheduleTick(pos, this, t);
        }
        super.stepOn(level, pos, state, entity);
    }

    /** Starts crumbling this block (used by the Void Sovereign's collapse attack). */
    public static void crack(ServerLevel level, BlockPos pos, int delay) {
        if (level.getBlockState(pos).getBlock() instanceof AbyssalStoneBlock b) level.scheduleTick(pos, b, delay);
    }

    @Override
    protected void tick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        int c = state.getValue(CRACK);
        if (c < 3) {
            level.setBlockAndUpdate(pos, state.setValue(CRACK, c + 1));
            level.playSound(null, pos, SoundEvents.DEEPSLATE_BREAK, SoundSource.BLOCKS, 0.6f, 0.6f + c * 0.2f);
            level.scheduleTick(pos, this, stageTicks(pos.getY()));
            return;
        }
        level.setBlockAndUpdate(pos, Blocks.AIR.defaultBlockState());
        level.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, defaultBlockState()), pos.getX() + 0.5, pos.getY() + 0.5, pos.getZ() + 0.5,
                20, 0.3, 0.3, 0.3, 0.1);
        level.playSound(null, pos, SoundEvents.DEEPSLATE_BRICKS_BREAK, SoundSource.BLOCKS, 1f, 0.5f);
        Scheduler.later(level, 1200, () -> {
            if (level.getBlockState(pos).isAir()) level.setBlockAndUpdate(pos, defaultBlockState());
        });
    }
}
