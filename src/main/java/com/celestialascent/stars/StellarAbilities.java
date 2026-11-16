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
            p.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 60, 0, true, false, true));
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

    @Override
    public void onUnequip(ServerPlayer p) {
        p.removeEffect(MobEffects.NIGHT_VISION);
    }
}
