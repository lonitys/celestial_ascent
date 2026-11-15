package com.celestialascent.stars;

import com.celestialascent.CelestialAscent;
import com.celestialascent.boss.BossAttack;
import com.celestialascent.boss.FlyingBoss;
import com.celestialascent.core.Fx;
import com.celestialascent.core.Scheduler;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.BossEvent;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3f;

import java.util.HashSet;
import java.util.Set;
import java.util.UUID;

/** Nebula Leviathan: 1400 HP star-serpent. Lunging bites, nebula breath, constricting coils; star rain in phase 2. */
public class NebulaLeviathan extends FlyingBoss {
    private static final DustParticleOptions NEBULA = new DustParticleOptions(new Vector3f(0.7f, 0.36f, 1f), 2.2f);
    private final Set<UUID> biteHits = new HashSet<>();

    public NebulaLeviathan(EntityType<? extends Monster> type, Level level) {
        super(type, level);
        this.xpReward = 2200;
    }

    public static AttributeSupplier.Builder attributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 1400).add(Attributes.ATTACK_DAMAGE, 20)
                .add(Attributes.MOVEMENT_SPEED, 0.3).add(Attributes.FLYING_SPEED, 0.6).add(Attributes.ARMOR, 20).add(Attributes.ARMOR_TOUGHNESS, 10)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1.0).add(Attributes.FOLLOW_RANGE, 64);
    }

    @Override public ResourceLocation bossId() { return ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "nebula_leviathan"); }
    @Override public double baseMaxHealth() { return 1400; }
    @Override protected float[] phaseThresholds() { return new float[]{0.5f}; }
    @Override protected BossEvent.BossBarColor barColor() { return BossEvent.BossBarColor.PURPLE; }
    @Override protected ParticleOptions ambientParticle() { return NEBULA; }
    @Override protected String moveAnimation() { return "fly"; }
    @Override protected double hoverHeight() { return 4; }
    @Override protected double orbitRadius() { return 12; }
    @Override protected double flySpeed() { return 0.6; }

    private ServerLevel sl() { return (ServerLevel) level(); }

    @Override
    protected void registerAttacks() {
        attacks.add(BossAttack.of("void_bite").range(3, 26).cooldown(60).duration(26).weight(13).mobile()
                .onTick((b, t, i) -> {
                    if (i == 8) {
                        biteHits.clear();
                        setDeltaMovement(t.getEyePosition().subtract(position()).normalize().scale(2.2));
                        playSound(SoundEvents.RAVAGER_ATTACK, 2f, 0.5f);
                    }
                    if (i >= 8 && i <= 20) {
                        for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(1.2), e -> e != this)) {
                            if (biteHits.add(e.getUUID())) {
                                hitTarget(e, 20);
                                e.addEffect(new MobEffectInstance(MobEffects.WITHER, 60, 1), this);
                            }
                        }
                    }
                }));
        attacks.add(BossAttack.of("nebula_breath").range(0, 14).cooldown(110).duration(50).weight(11)
                .onTick((b, t, i) -> {
                    if (i < 10 || i > 44) return;
                    Vec3 mouth = position().add(Vec3.directionFromRotation(getXRot(), getYRot()).scale(2)).add(0, getBbHeight() / 2, 0);
                    Vec3 dir = t.getEyePosition().subtract(mouth).normalize();
                    Fx.cone(sl(), NEBULA, mouth, dir, 14, 3, 16);
                    Fx.cone(sl(), ParticleTypes.REVERSE_PORTAL, mouth, dir, 12, 2, 6);
                    if (i % 3 == 0) {
                        for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(15), e -> e != this)) {
                            Vec3 to = e.getEyePosition().subtract(mouth);
                            if (to.length() < 14 && to.normalize().dot(dir) > Math.cos(Math.toRadians(25))) {
                                hitTarget(e, 4);
                                e.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 80, 0), this);
                            }
                        }
                    }
                }));
        attacks.add(BossAttack.of("coil").range(0, 18).cooldown(150).duration(60).weight(9).mobile()
                .onTick((b, t, i) -> {
                    double a = i * 0.32;
                    Vec3 desired = t.position().add(Math.cos(a) * 4, 1.2, Math.sin(a) * 4);
                    setDeltaMovement(desired.subtract(position()).scale(0.5));
                    sl().sendParticles(NEBULA, getX(), getY() + 1, getZ(), 4, 0.5, 0.5, 0.5, 0);
                    if (i % 10 == 0) {
                        for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, t.getBoundingBox().inflate(4.5), e -> e != this)) {
                            hitTarget(e, 6);
                            e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 3), this);
                        }
                    }
                }));
        attacks.add(BossAttack.of("star_rain").phase(1).range(0, 40).cooldown(140).duration(50).weight(10)
                .onTick((b, t, i) -> {
                    if (i < 10 || i % 5 != 0) return;
                    for (Player p : playersNear(40)) {
                        Vec3 at = ground(p.getX() + random.nextGaussian() * 3, p.getZ() + random.nextGaussian() * 3, p.getY());
                        Fx.marker(sl(), at, Blocks.PURPLE_STAINED_GLASS.defaultBlockState(), 2.4f, 20);
                        Fx.fall(sl(), at, Stars.STARSTONE.get().defaultBlockState(), 1.3f, 24f, 20);
                        Scheduler.later(sl(), 20, () -> {
                            if (!isAlive()) return;
                            level().explode(this, at.x, at.y + 0.3, at.z, 0f, false, Level.ExplosionInteraction.NONE);
                            for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, new AABB(at, at).inflate(2.4, 2.5, 2.4), e -> e != this)) hitTarget(e, 14);
                        });
                    }
                }));
    }
}
