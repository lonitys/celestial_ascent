package com.celestialascent.abyss;

import com.celestialascent.armor.ArmorAbility;
import com.celestialascent.empire.ImperialAbilities;
import com.celestialascent.stars.StellarAbilities;
import com.celestialascent.titans.Element;
import com.celestialascent.titans.TitanAbilities;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;

import java.util.EnumMap;
import java.util.List;
import java.util.Map;

/**
 * Ascendant set: everything the ladder offers. Creative flight and stat bonuses are attribute
 * modifiers (see Abyss.init); this class adds immunities, sustenance and every lower-set ability:
 * all four titan elements at level II, ender blink, star glide/regeneration/night vision, void safety.
 */
public class AscendantAbilities implements ArmorAbility {
    private final TitanAbilities titan = new TitanAbilities() {
        @Override
        public Map<Element, Integer> levels(ServerPlayer p) {
            Map<Element, Integer> all = new EnumMap<>(Element.class);
            for (Element e : Element.values()) all.put(e, 2);
            return all;
        }
    };
    private final ImperialAbilities imperial = new ImperialAbilities();
    private final StellarAbilities stellar = new StellarAbilities();
    private final VoidAbilities voidSet = new VoidAbilities();
    private final List<ArmorAbility> parts = List.of(titan, stellar, voidSet);

    /** Damage the Ascendant set ignores completely. */
    public static boolean immune(DamageSource src) {
        return src.is(DamageTypeTags.IS_FIRE) || src.is(DamageTypeTags.IS_FALL) || src.is(DamageTypeTags.IS_DROWNING)
                || src.is(DamageTypeTags.IS_FREEZING) || src.is(DamageTypes.WITHER) || src.is(DamageTypes.IN_WALL)
                || src.is(DamageTypes.FELL_OUT_OF_WORLD) || src.is(DamageTypes.STARVE);
    }

    @Override
    public void tick(ServerPlayer p) {
        for (ArmorAbility a : parts) a.tick(p);
        p.getFoodData().setFoodLevel(20);
        p.getFoodData().setSaturation(Math.max(p.getFoodData().getSaturationLevel(), 10f));
        if (p.tickCount % 40 == 0) {
            p.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 60, 1, true, false, true));
            if (com.celestialascent.armor.ArmorStages.setStage(p) >= 3) {
                // Set stage III: allies close by regenerate too.
                for (var ally : p.level().getEntitiesOfClass(ServerPlayer.class, p.getBoundingBox().inflate(8), o -> o != p && o.isAlive())) {
                    ally.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 60, 0, true, true, true));
                }
            }
        }
    }

    @Override
    public void onHurt(ServerPlayer p, LivingIncomingDamageEvent e) {
        if (immune(e.getSource())) {
            e.setCanceled(true);
            if (e.getSource().is(DamageTypes.FELL_OUT_OF_WORLD)) voidSet.tick(p);
            return;
        }
        titan.onHurt(p, e);
        voidSet.onHurt(p, e);
    }

    @Override
    public void onAttack(ServerPlayer p, LivingEntity target, LivingIncomingDamageEvent e) {
        if (!target.fireImmune()) target.igniteForSeconds(3);
    }

    @Override
    public void onKey(ServerPlayer p, int key) {
        if (key == 0) {
            if (p.isShiftKeyDown()) voidSet.onKey(p, 0);
            else imperial.onKey(p, 0);
        } else {
            stellar.onKey(p, key);
        }
    }

    @Override
    public void onUnequip(ServerPlayer p) {
        for (ArmorAbility a : parts) a.onUnequip(p);
    }
}
