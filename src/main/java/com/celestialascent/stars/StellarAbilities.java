package com.celestialascent.stars;

import com.celestialascent.armor.ArmorAbility;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;

import java.util.HashSet;
import java.util.Set;
import java.util.UUID;

/** Stellar set: star glide while falling, regeneration under the night sky, toggleable night vision (G). */
public class StellarAbilities implements ArmorAbility {
    private final Set<UUID> nightVisionOff = new HashSet<>();

    public static boolean underNightSky(ServerPlayer p) {
        var level = p.serverLevel();
        return level.dimension() == com.celestialascent.core.Travel.FALLEN_STARS
                || (Stars.nightSky(level) && level.canSeeSky(p.blockPosition().above()));
    }

    @Override
    public void tick(ServerPlayer p) {
        if (!p.onGround() && !p.isShiftKeyDown() && p.getDeltaMovement().y < -0.35 && !p.getAbilities().flying) {
            p.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING, 10, 0, true, false, true));
        }
        if (p.tickCount % 40 == 0 && underNightSky(p)) {
            int amp = com.celestialascent.armor.ArmorStages.setStage(p) >= 2 ? 1 : 0;
            p.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 60, amp, true, false, true));
        }
        if (!nightVisionOff.contains(p.getUUID())) {
            MobEffectInstance nv = p.getEffect(MobEffects.NIGHT_VISION);
            if (nv == null || nv.getDuration() < 240) p.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION, 400, 0, true, false, true));
        }
    }

    @Override
    public void onKey(ServerPlayer p, int key) {
        if (key != 1) return;
        if (!nightVisionOff.remove(p.getUUID())) {
            nightVisionOff.add(p.getUUID());
            p.removeEffect(MobEffects.NIGHT_VISION);
            p.displayClientMessage(Component.translatable("message.celestialascent.night_vision_off"), true);
        } else {
            p.displayClientMessage(Component.translatable("message.celestialascent.night_vision_on"), true);
        }
    }

    private final java.util.Map<UUID, Long> lastStar = new java.util.HashMap<>();

    /** Set stage III: under the night sky, a falling star strikes whoever hurts you (every 2 s at most). */
    @Override
    public void onHurt(ServerPlayer p, net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent e) {
        if (com.celestialascent.armor.ArmorStages.setStage(p) < 3 || !underNightSky(p)) return;
        if (!(e.getSource().getEntity() instanceof net.minecraft.world.entity.LivingEntity attacker) || attacker == p) return;
        long now = p.level().getGameTime();
        if (now - lastStar.getOrDefault(p.getUUID(), -1000L) < 40) return;
        lastStar.put(p.getUUID(), now);
        var level = p.serverLevel();
        var at = attacker.position();
        com.celestialascent.core.Fx.fall(level, at, Stars.STAR_CRYSTAL.get().defaultBlockState(), 1.0f, 12f, 10);
        com.celestialascent.core.Scheduler.later(level, 10, () -> {
            if (!attacker.isAlive()) return;
            attacker.hurt(p.damageSources().indirectMagic(p, p), 8);
            level.sendParticles(net.minecraft.core.particles.ParticleTypes.WAX_ON, at.x, at.y + 1, at.z, 25, 0.5, 0.6, 0.5, 0.3);
            level.playSound(null, attacker.blockPosition(), net.minecraft.sounds.SoundEvents.AMETHYST_CLUSTER_BREAK, net.minecraft.sounds.SoundSource.PLAYERS, 1f, 1.2f);
        });
    }

    @Override
    public void onUnequip(ServerPlayer p) {
        p.removeEffect(MobEffects.NIGHT_VISION);
    }
}
