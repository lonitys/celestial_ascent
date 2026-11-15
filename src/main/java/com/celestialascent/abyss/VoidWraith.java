package com.celestialascent.abyss;

import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.monster.Vex;
import net.minecraft.world.level.Level;

/** Void Wraith: a phasing spirit of the Abyss that drains light from those it touches. */
public class VoidWraith extends Vex {
    public VoidWraith(EntityType<? extends Vex> type, Level level) {
        super(type, level);
        this.xpReward = 12;
    }

    public static AttributeSupplier.Builder attributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 40).add(Attributes.ATTACK_DAMAGE, 8)
                .add(Attributes.FLYING_SPEED, 0.6).add(Attributes.MOVEMENT_SPEED, 0.6).add(Attributes.FOLLOW_RANGE, 32);
    }

    @Override
    public boolean doHurtTarget(Entity target) {
        boolean hit = super.doHurtTarget(target);
        if (hit && target instanceof LivingEntity l) l.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 100, 0), this);
        return hit;
    }

    @Override
    public boolean removeWhenFarAway(double dist) {
        return true;
    }
}
