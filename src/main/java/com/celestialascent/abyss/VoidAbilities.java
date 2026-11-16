package com.celestialascent.abyss;

import com.celestialascent.armor.ArmorAbility;
import com.celestialascent.core.Travel;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Void set: void dash on the ability key (brief invulnerability), immunity to wither and darkness,
 * and the void cannot claim you: falling out of the world returns you to your last footing.
 */
public class VoidAbilities implements ArmorAbility {
    public static final int DASH_COOLDOWN = 80;
    private final Map<UUID, Long> lastDash = new HashMap<>();
    private final Map<UUID, Long> invulnerableUntil = new HashMap<>();
    private final Map<UUID, BlockPos> lastFooting = new HashMap<>();

    @Override
    public void tick(ServerPlayer p) {
        if (p.hasEffect(MobEffects.WITHER)) p.removeEffect(MobEffects.WITHER);
        if (p.hasEffect(MobEffects.DARKNESS)) p.removeEffect(MobEffects.DARKNESS);
        if (p.onGround()) lastFooting.put(p.getUUID(), p.blockPosition());
        boolean intoVoid = p.getY() < p.level().getMinBuildHeight() - 8;
        // In the Fallen Stars the void is the way into the Abyss, so it is left alone there.
        if (intoVoid && p.level().dimension() != Travel.FALLEN_STARS) {
            BlockPos back = lastFooting.getOrDefault(p.getUUID(), p.level().getSharedSpawnPos());
            p.teleportTo(back.getX() + 0.5, back.getY() + 1, back.getZ() + 0.5);
            p.resetFallDistance();
            p.setDeltaMovement(Vec3.ZERO);
            p.serverLevel().playSound(null, back, SoundEvents.ENDERMAN_TELEPORT, SoundSource.PLAYERS, 1f, 0.5f);
        }
    }

    @Override
    public void onKey(ServerPlayer p, int key) {
        if (key != 0) return;
        long now = p.level().getGameTime();
        int stage = com.celestialascent.armor.ArmorStages.setStage(p);
        if (now - lastDash.getOrDefault(p.getUUID(), -1000L) < DASH_COOLDOWN - 20 * Math.max(0, stage - 1)) return;
        lastDash.put(p.getUUID(), now);
        invulnerableUntil.put(p.getUUID(), now + 12);
        Vec3 look = p.getLookAngle();
        p.setDeltaMovement(look.x * 2.4, Math.max(0.2, look.y * 1.4), look.z * 2.4);
        p.hurtMarked = true;
        p.resetFallDistance();
        p.serverLevel().sendParticles(ParticleTypes.REVERSE_PORTAL, p.getX(), p.getY() + 1, p.getZ(), 40, 0.4, 0.8, 0.4, 0.2);
        p.serverLevel().playSound(null, p.blockPosition(), SoundEvents.ENDER_DRAGON_FLAP, SoundSource.PLAYERS, 0.8f, 1.6f);
        if (stage >= 3) {
            // Set stage III: the dash tears through the monsters it passes.
            java.util.Set<UUID> hit = new java.util.HashSet<>();
            for (int t = 1; t <= 8; t++) {
                com.celestialascent.core.Scheduler.later(p.serverLevel(), t, () -> {
                    if (!p.isAlive()) return;
                    for (var e : p.level().getEntitiesOfClass(net.minecraft.world.entity.LivingEntity.class, p.getBoundingBox().inflate(1.2),
                            e -> e != p && e instanceof net.minecraft.world.entity.monster.Enemy && hit.add(e.getUUID()))) {
                        e.hurt(p.damageSources().playerAttack(p), 5);
                        p.serverLevel().sendParticles(ParticleTypes.REVERSE_PORTAL, e.getX(), e.getY() + 1, e.getZ(), 20, 0.3, 0.5, 0.3, 0.2);
                    }
                });
            }
        }
    }

    @Override
    public void onHurt(ServerPlayer p, LivingIncomingDamageEvent e) {
        if (p.level().getGameTime() < invulnerableUntil.getOrDefault(p.getUUID(), 0L) && !e.getSource().is(DamageTypes.FELL_OUT_OF_WORLD)) {
            e.setCanceled(true);
        }
    }
}
