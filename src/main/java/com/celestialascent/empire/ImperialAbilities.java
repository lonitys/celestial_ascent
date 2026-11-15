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

/** Imperial set: ender blink on the ability key (12 blocks, 5 s cooldown). */
public class ImperialAbilities implements ArmorAbility {
    public static final double RANGE = 12;
    public static final int COOLDOWN = 100;
    private final Map<UUID, Long> lastBlink = new HashMap<>();

    @Override
    public void onKey(ServerPlayer p, int key) {
        if (key != 0) return;
        long now = p.level().getGameTime();
        if (now - lastBlink.getOrDefault(p.getUUID(), -1000L) < COOLDOWN) return;
        Vec3 target = blinkTarget(p);
        if (target == null) return;
        lastBlink.put(p.getUUID(), now);
        var level = p.serverLevel();
        level.sendParticles(ParticleTypes.PORTAL, p.getX(), p.getY() + 1, p.getZ(), 40, 0.4, 0.8, 0.4, 0.4);
        p.teleportTo(target.x, target.y, target.z);
        p.resetFallDistance();
        level.sendParticles(ParticleTypes.REVERSE_PORTAL, target.x, target.y + 1, target.z, 40, 0.4, 0.8, 0.4, 0.1);
        level.playSound(null, BlockPos.containing(target), SoundEvents.ENDERMAN_TELEPORT, SoundSource.PLAYERS, 1f, 1.3f);
    }

    /** Furthest safe spot along the look direction, stopping before solid blocks. */
    static Vec3 blinkTarget(ServerPlayer p) {
        Vec3 eye = p.getEyePosition();
        Vec3 end = eye.add(p.getLookAngle().scale(RANGE));
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
