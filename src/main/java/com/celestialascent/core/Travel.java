package com.celestialascent.core;

import com.celestialascent.CelestialAscent;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.portal.DimensionTransition;
import net.minecraft.world.phys.Vec3;

/** Dimension keys and safe cross-dimension teleports. */
public final class Travel {
    private Travel() {}

    public static final ResourceKey<Level> FALLEN_STARS = ResourceKey.create(Registries.DIMENSION,
            ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "fallen_stars"));
    public static final ResourceKey<Level> ABYSS = ResourceKey.create(Registries.DIMENSION,
            ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "abyss"));

    private static final String RETURN = "celestialascent_return";

    /** Top standing position at (x, z), or null if the column is empty (void). */
    public static BlockPos surface(ServerLevel level, int x, int z) {
        level.getChunk(x >> 4, z >> 4); // force generation
        int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
        return y <= level.getMinBuildHeight() + 1 ? null : new BlockPos(x, y, z);
    }

    /** Builds a small platform with headroom and returns the standing position above its centre. */
    public static BlockPos platform(ServerLevel level, BlockPos center, BlockState floor, int radius) {
        for (int dx = -radius; dx <= radius; dx++)
            for (int dz = -radius; dz <= radius; dz++) {
                level.setBlockAndUpdate(center.offset(dx, 0, dz), floor);
                for (int dy = 1; dy <= 3; dy++) level.setBlockAndUpdate(center.offset(dx, dy, dz), Blocks.AIR.defaultBlockState());
            }
        return center.above();
    }

    public static void teleport(Entity e, ServerLevel to, Vec3 pos) {
        if (e instanceof ServerPlayer p) {
            p.teleportTo(to, pos.x, pos.y, pos.z, p.getYRot(), p.getXRot());
            p.resetFallDistance();
        } else {
            e.changeDimension(new DimensionTransition(to, pos, Vec3.ZERO, e.getYRot(), e.getXRot(), DimensionTransition.DO_NOTHING));
        }
    }

    /** Remembers where a player left from, so return portals can bring them back. */
    public static void rememberReturn(ServerPlayer p) {
        CompoundTag t = new CompoundTag();
        t.putString("Dim", p.level().dimension().location().toString());
        t.putDouble("X", p.getX());
        t.putDouble("Y", p.getY());
        t.putDouble("Z", p.getZ());
        p.getPersistentData().put(RETURN, t);
    }

    /** Sends a player back to where {@link #rememberReturn} recorded, or to their respawn point. */
    public static void sendBack(ServerPlayer p) {
        CompoundTag t = p.getPersistentData().getCompound(RETURN);
        ServerLevel dest = null;
        if (t.contains("Dim")) {
            dest = p.server.getLevel(ResourceKey.create(Registries.DIMENSION, ResourceLocation.parse(t.getString("Dim"))));
        }
        if (dest != null) {
            teleport(p, dest, new Vec3(t.getDouble("X"), t.getDouble("Y") + 0.5, t.getDouble("Z")));
        } else {
            ServerLevel overworld = p.server.overworld();
            BlockPos spawn = overworld.getSharedSpawnPos();
            BlockPos top = surface(overworld, spawn.getX(), spawn.getZ());
            teleport(p, overworld, Vec3.atBottomCenterOf(top == null ? spawn : top));
        }
    }
}
