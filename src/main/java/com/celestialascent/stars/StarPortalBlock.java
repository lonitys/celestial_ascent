package com.celestialascent.stars;

import com.celestialascent.core.Scheduler;
import com.celestialascent.core.Travel;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * The Star Gate's portal surface. From the End it leads to the Fallen Stars (building an arrival
 * platform with a return portal if needed); from the Fallen Stars it leads back where you came from.
 */
public class StarPortalBlock extends Block {
    private static final VoxelShape SHAPE = Shapes.box(0, 0.375, 0, 1, 0.75, 1);

    public StarPortalBlock(Properties props) {
        super(props);
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
        return SHAPE;
    }

    @Override
    protected VoxelShape getCollisionShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
        return Shapes.empty();
    }

    @Override
    protected void entityInside(BlockState state, Level level, BlockPos pos, Entity entity) {
        if (!(level instanceof ServerLevel sl) || !(entity instanceof ServerPlayer p) || p.isOnPortalCooldown() || p.isPassenger()) return;
        p.setPortalCooldown(100);
        Scheduler.later(sl, 1, () -> travel(sl, p));
    }

    private static void travel(ServerLevel from, ServerPlayer p) {
        if (from.dimension() == Travel.FALLEN_STARS) {
            Travel.sendBack(p);
            return;
        }
        ServerLevel stars = from.getServer().getLevel(Travel.FALLEN_STARS);
        if (stars == null) return;
        Travel.rememberReturn(p);
        int x = p.getBlockX(), z = p.getBlockZ();
        BlockPos top = Travel.surface(stars, x, z);
        BlockPos stand;
        if (top == null) {
            stand = Travel.platform(stars, new BlockPos(x, 110, z), Stars.STARSTONE_BRICKS.get().defaultBlockState(), 3);
            stars.setBlockAndUpdate(new BlockPos(x + 3, 110, z), Stars.STAR_PORTAL.get().defaultBlockState());
        } else {
            stand = top;
            if (stars.getBlockState(top.offset(3, -1, 0)).isSolid()) stars.setBlockAndUpdate(top.offset(3, -1, 0), Stars.STAR_PORTAL.get().defaultBlockState());
        }
        Travel.teleport(p, stars, Vec3.atBottomCenterOf(stand));
        p.setPortalCooldown(100);
        stars.playSound(null, stand, SoundEvents.END_PORTAL_SPAWN, SoundSource.PLAYERS, 0.8f, 1.5f);
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource r) {
        for (int i = 0; i < 2; i++) {
            level.addParticle(ParticleTypes.END_ROD, pos.getX() + r.nextFloat(), pos.getY() + 0.8, pos.getZ() + r.nextFloat(), 0, 0.04 + r.nextFloat() * 0.05, 0);
        }
        if (r.nextInt(4) == 0) level.addParticle(ParticleTypes.REVERSE_PORTAL, pos.getX() + r.nextFloat(), pos.getY() + 0.8, pos.getZ() + r.nextFloat(), 0, 0.1, 0);
    }
}
