package com.celestialascent.core;

import com.mojang.math.Transformation;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.Brightness;
import net.minecraft.world.entity.Display;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import org.joml.Quaternionf;
import org.joml.Vector3f;

/** Server-side visual effects built from vanilla display entities and particles. */
public final class Fx {
    private Fx() {}

    /**
     * A block that grows out of the ground (scale 0 to full height over {@code riseTicks}),
     * holds, then sinks back and disappears after {@code lifeTicks}.
     */
    public static void spike(ServerLevel level, Vec3 base, BlockState state, float width, float height, float tiltDeg,
                             int riseTicks, int lifeTicks, boolean glow) {
        Display.BlockDisplay d = new Display.BlockDisplay(EntityType.BLOCK_DISPLAY, level);
        d.setBlockState(state);
        d.setPos(base.x, base.y, base.z);
        d.setViewRange(2.0f);
        if (glow) d.setBrightnessOverride(new Brightness(15, 15));
        Quaternionf tilt = new Quaternionf().rotateXYZ((float) Math.toRadians(tiltDeg * (level.random.nextFloat() - 0.5f)),
                (float) Math.toRadians(level.random.nextFloat() * 360), (float) Math.toRadians(tiltDeg * (level.random.nextFloat() - 0.5f)));
        d.setTransformation(transform(width, 0.01f, tilt));
        level.addFreshEntity(d);
        Scheduler.later(level, 2, () -> {
            d.setTransformationInterpolationDelay(0);
            d.setTransformationInterpolationDuration(riseTicks);
            d.setTransformation(transform(width, height, tilt));
        });
        Scheduler.later(level, Math.max(riseTicks + 3, lifeTicks - 6), () -> {
            d.setTransformationInterpolationDelay(0);
            d.setTransformationInterpolationDuration(6);
            d.setTransformation(transform(width * 0.6f, 0.01f, tilt));
        });
        Scheduler.later(level, lifeTicks, d::discard);
    }

    private static Transformation transform(float width, float height, Quaternionf rot) {
        // Centre the block horizontally on the entity position; grow upwards from its base.
        Vector3f t = new Vector3f(-width / 2f, 0, -width / 2f).rotate(rot);
        return new Transformation(t, rot, new Vector3f(width, height, width), new Quaternionf());
    }

    /** A block that falls from {@code height} above {@code impact} over {@code ticks}, then vanishes. */
    public static void fall(ServerLevel level, Vec3 impact, BlockState state, float size, float height, int ticks) {
        Display.BlockDisplay d = new Display.BlockDisplay(EntityType.BLOCK_DISPLAY, level);
        d.setBlockState(state);
        d.setPos(impact.x, impact.y, impact.z);
        d.setViewRange(3.0f);
        d.setBrightnessOverride(new Brightness(15, 15));
        Quaternionf spin = new Quaternionf().rotateXYZ(0.4f, level.random.nextFloat() * 6f, 0.3f);
        d.setTransformation(new Transformation(new Vector3f(-size / 2f, height, -size / 2f), spin, new Vector3f(size, size, size), new Quaternionf()));
        level.addFreshEntity(d);
        Scheduler.later(level, 2, () -> {
            d.setTransformationInterpolationDelay(0);
            d.setTransformationInterpolationDuration(ticks - 2);
            d.setTransformation(new Transformation(new Vector3f(-size / 2f, 0, -size / 2f), spin, new Vector3f(size, size, size), new Quaternionf()));
        });
        Scheduler.later(level, ticks + 1, d::discard);
    }

    /** A flat glowing tile on the ground used as an attack warning marker. */
    public static void marker(ServerLevel level, Vec3 center, BlockState state, float size, int lifeTicks) {
        Display.BlockDisplay d = new Display.BlockDisplay(EntityType.BLOCK_DISPLAY, level);
        d.setBlockState(state);
        d.setPos(center.x, center.y + 0.02, center.z);
        d.setBrightnessOverride(new Brightness(15, 15));
        d.setTransformation(new Transformation(new Vector3f(-size / 2f, 0, -size / 2f), new Quaternionf(),
                new Vector3f(size, 0.02f, size), new Quaternionf()));
        level.addFreshEntity(d);
        Scheduler.later(level, lifeTicks, d::discard);
    }

    /** Ring of particles. */
    public static void ring(ServerLevel level, ParticleOptions p, Vec3 c, double radius, int count, double dy) {
        for (int i = 0; i < count; i++) {
            double a = Math.PI * 2 * i / count;
            level.sendParticles(p, c.x + Math.cos(a) * radius, c.y + dy, c.z + Math.sin(a) * radius, 1, 0, 0.02, 0, 0.01);
        }
    }

    /** Line of particles from a to b. */
    public static void line(ServerLevel level, ParticleOptions p, Vec3 a, Vec3 b, double step) {
        Vec3 d = b.subtract(a);
        int n = Math.max(1, (int) (d.length() / step));
        for (int i = 0; i <= n; i++) {
            Vec3 q = a.add(d.scale(i / (double) n));
            level.sendParticles(p, q.x, q.y, q.z, 1, 0.05, 0.05, 0.05, 0);
        }
    }

    /** Cone of particles from origin along dir. */
    public static void cone(ServerLevel level, ParticleOptions p, Vec3 origin, Vec3 dir, double length, double spread, int count) {
        Vec3 n = dir.normalize();
        for (int i = 0; i < count; i++) {
            double t = level.random.nextDouble() * length;
            Vec3 q = origin.add(n.scale(t)).add((level.random.nextDouble() - 0.5) * spread * t / length * 2,
                    (level.random.nextDouble() - 0.5) * spread * t / length * 2, (level.random.nextDouble() - 0.5) * spread * t / length * 2);
            level.sendParticles(p, q.x, q.y, q.z, 1, 0, 0, 0, 0);
        }
    }
}
