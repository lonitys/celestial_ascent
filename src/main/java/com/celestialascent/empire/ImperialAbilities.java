package com.celestialascent.empire;

import com.celestialascent.armor.ArmorAbility;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Imperial set: ender blink on the ability key. Range and cooldown improve with the set stage
 * (12/16/20 blocks, 5/3.75/2.5 s); at stage III the arrival sends out a shockwave.
 */
public class ImperialAbilities implements ArmorAbility {
    public static final double RANGE = 12;
    public static final int COOLDOWN = 100;

    static double range(int setStage) {
        return RANGE + 4 * Math.max(0, setStage - 1);
    }

    static int cooldown(int setStage) {
        return COOLDOWN - 25 * Math.max(0, setStage - 1);
    }
    private final Map<UUID, Long> lastBlink = new HashMap<>();

    @Override
    public void onKey(ServerPlayer p, int key) {
        if (key != 0) return;
        long now = p.level().getGameTime();
        int stage = com.celestialascent.armor.ArmorStages.setStage(p);
        if (now - lastBlink.getOrDefault(p.getUUID(), -1000L) < cooldown(stage)) return;
        Vec3 target = blinkTarget(p, range(stage));
        if (target == null) return;
        lastBlink.put(p.getUUID(), now);
        var level = p.serverLevel();
        level.sendParticles(ParticleTypes.PORTAL, p.getX(), p.getY() + 1, p.getZ(), 40, 0.4, 0.8, 0.4, 0.4);
        p.teleportTo(target.x, target.y, target.z);
        p.resetFallDistance();
        level.sendParticles(ParticleTypes.REVERSE_PORTAL, target.x, target.y + 1, target.z, 40, 0.4, 0.8, 0.4, 0.1);
        level.playSound(null, BlockPos.containing(target), SoundEvents.ENDERMAN_TELEPORT, SoundSource.PLAYERS, 1f, 1.3f);
        if (stage >= 3) {
            // Arrival shockwave: nearby monsters are thrown back.
            level.sendParticles(ParticleTypes.DRAGON_BREATH, target.x, target.y + 0.3, target.z, 60, 1.5, 0.2, 1.5, 0.02);
            for (var e : level.getEntitiesOfClass(net.minecraft.world.entity.LivingEntity.class, p.getBoundingBox().inflate(3),
                    e -> e != p && e instanceof net.minecraft.world.entity.monster.Enemy)) {
                e.hurt(p.damageSources().playerAttack(p), 6);
                Vec3 away = e.position().subtract(target).normalize();
                e.push(away.x * 1.2, 0.4, away.z * 1.2);
            }
        }
    }

    /** Furthest safe spot along the look direction, stopping before solid blocks. */
    static Vec3 blinkTarget(ServerPlayer p, double range) {
        Vec3 eye = p.getEyePosition();
        Vec3 end = eye.add(p.getLookAngle().scale(range));
        BlockHitResult hit = p.level().clip(new ClipContext(eye, end, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, p));
        Vec3 stop = hit.getType() == HitResult.Type.BLOCK ? hit.getLocation().subtract(p.getLookAngle().scale(0.6)) : end;
        Vec3 feet = stop.subtract(0, p.getEyeHeight(), 0);
        for (int i = 0; i < 3; i++) {
            if (p.level().noCollision(p, p.getBoundingBox().move(feet.subtract(p.position())))) return feet;
            feet = feet.add(0, 1, 0);
        }
        return null;
    }
}
