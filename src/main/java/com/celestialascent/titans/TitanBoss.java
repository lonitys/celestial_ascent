package com.celestialascent.titans;

import com.celestialascent.CelestialAscent;
import com.celestialascent.boss.CelestialBoss;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.BossEvent;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/** Shared base for the four Elemental Titans. */
public abstract class TitanBoss extends CelestialBoss {
    protected TitanBoss(EntityType<? extends Monster> type, Level level) {
        super(type, level);
    }

    public abstract Element element();

    @Override
    public ResourceLocation bossId() {
        return ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, element().key + "_titan");
    }

    @Override
    protected float[] phaseThresholds() {
        return new float[]{0.5f};
    }

    @Override
    protected BossEvent.BossBarColor barColor() {
        return switch (element()) {
            case FROST -> BossEvent.BossBarColor.WHITE;
            case TIDE -> BossEvent.BossBarColor.BLUE;
            case STORM -> BossEvent.BossBarColor.YELLOW;
            case MAGMA -> BossEvent.BossBarColor.RED;
        };
    }

    public static AttributeSupplier.Builder titanAttributes(double health, double damage, double speed, double armor) {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, health)
                .add(Attributes.ATTACK_DAMAGE, damage)
                .add(Attributes.MOVEMENT_SPEED, speed)
                .add(Attributes.ARMOR, armor)
                .add(Attributes.ARMOR_TOUGHNESS, 6)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1.0)
                .add(Attributes.FOLLOW_RANGE, 48)
                .add(Attributes.STEP_HEIGHT, 1.6)
                .add(Attributes.ATTACK_KNOCKBACK, 1.5);
    }

    /** Unit vector from the boss to the target on the horizontal plane. */
    protected Vec3 flatDirTo(LivingEntity target) {
        Vec3 d = target.position().subtract(position());
        Vec3 flat = new Vec3(d.x, 0, d.z);
        return flat.lengthSqr() < 1e-4 ? Vec3.directionFromRotation(0, getYRot()) : flat.normalize();
    }

    /** True if e is inside a cone from origin along dir (half-angle in degrees, max length). */
    protected static boolean inCone(LivingEntity e, Vec3 origin, Vec3 dir, double halfAngleDeg, double length) {
        Vec3 to = e.position().add(0, e.getBbHeight() / 2, 0).subtract(origin);
        double dist = to.length();
        if (dist > length || dist < 0.01) return dist < 0.01;
        double cos = to.normalize().dot(dir.normalize());
        return cos >= Math.cos(Math.toRadians(halfAngleDeg));
    }
}
