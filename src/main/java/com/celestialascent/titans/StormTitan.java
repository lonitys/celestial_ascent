package com.celestialascent.titans;

import com.celestialascent.boss.BossAttack;
import com.celestialascent.core.Fx;
import com.celestialascent.core.Scheduler;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;

/** Storm Titan: 500 HP. Called lightning, wind gusts, thunder claps; dashes and storm aura in phase 2. */
public class StormTitan extends TitanBoss {
    public StormTitan(EntityType<? extends Monster> type, Level level) {
        super(type, level);
    }

    @Override public Element element() { return Element.STORM; }
    @Override public double baseMaxHealth() { return 500; }
    @Override protected ParticleOptions ambientParticle() { return ParticleTypes.ELECTRIC_SPARK; }
    @Override protected int animTransition() { return 0; } // vortex rings spin in whole turns

    private ServerLevel sl() { return (ServerLevel) level(); }

    /** Visual lightning plus our own controlled damage (no fire, no block damage). */
    private void strike(Vec3 at, float damage, double radius) {
        LightningBolt bolt = EntityType.LIGHTNING_BOLT.create(sl());
        if (bolt != null) {
            bolt.moveTo(at.x, at.y, at.z);
            bolt.setVisualOnly(true);
            sl().addFreshEntity(bolt);
        }
        for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, new AABB(at, at).inflate(radius, 3, radius), e -> e != this)) {
            hitTarget(e, damage);
        }
        sl().sendParticles(ParticleTypes.ELECTRIC_SPARK, at.x, at.y + 0.5, at.z, 40, 0.8, 0.8, 0.8, 0.4);
    }

    @Override
    protected void registerAttacks() {
        attacks.add(BossAttack.of("lightning_call").range(0, 30).cooldown(90).duration(40).weight(13)
                .onStart((b, t, i) -> {
                    List<Vec3> spots = new ArrayList<>();
                    for (Player p : playersNear(30)) spots.add(ground(p.getX(), p.getZ(), p.getY()));
                    for (int k = 0; k < 3 + phase() * 2; k++) {
                        Vec3 c = t.position();
                        spots.add(ground(c.x + random.nextGaussian() * 5, c.z + random.nextGaussian() * 5, c.y));
                    }
                    for (Vec3 s : spots) {
                        Fx.marker(sl(), s, Blocks.YELLOW_STAINED_GLASS.defaultBlockState(), 2.4f, 25);
                        Scheduler.later(sl(), 25, () -> {
                            if (isAlive()) strike(s, 15, 1.6);
                        });
                    }
                    playSound(SoundEvents.BEACON_ACTIVATE, 2f, 1.8f);
                }));

        attacks.add(BossAttack.of("wind_gust").range(0, 12).cooldown(70).duration(30).weight(11)
                .onTick((b, t, i) -> {
                    if (i != 14) return;
                    Vec3 origin = front(1, 0.6);
                    Vec3 dir = flatDirTo(t);
                    Fx.cone(sl(), ParticleTypes.CLOUD, origin, dir, 12, 4, 80);
                    Fx.cone(sl(), ParticleTypes.GUST, origin, dir, 10, 3, 6);
                    for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(13), e -> e != this)) {
                        if (inCone(e, origin, dir, 35, 12.5)) {
                            hitTarget(e, 6);
                            e.push(dir.x * 2.6, 0.7, dir.z * 2.6);
                            e.hurtMarked = true;
                        }
                    }
                    playSound(SoundEvents.BREEZE_WIND_CHARGE_BURST.value(), 2f, 0.6f);
                }));

        attacks.add(BossAttack.of("thunder_clap").range(0, 6).cooldown(80).duration(30).weight(12)
                .onTick((b, t, i) -> {
                    if (i != 16) return;
                    Vec3 c = position();
                    hitArea(c, 5.5, 14, 1.6);
                    for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(5.5), e -> e != this)) {
                        e.addEffect(new MobEffectInstance(MobEffects.CONFUSION, 80, 0), this);
                    }
                    sl().sendParticles(ParticleTypes.FLASH, c.x, c.y + 2.5, c.z, 1, 0, 0, 0, 0);
                    Fx.ring(sl(), ParticleTypes.ELECTRIC_SPARK, c.add(0, 0.3, 0), 5, 60, 0);
                    Fx.ring(sl(), ParticleTypes.CLOUD, c.add(0, 0.3, 0), 3, 30, 0);
                    playSound(SoundEvents.LIGHTNING_BOLT_THUNDER, 2f, 1.2f);
                }));

        attacks.add(BossAttack.of("storm_dash").phase(1).range(6, 24).cooldown(90).duration(24).weight(10).mobile()
                .onTick((b, t, i) -> {
                    if (i == 6) {
                        Vec3 dir = t.position().subtract(position()).normalize();
                        setDeltaMovement(dir.x * 2.2, 0.15, dir.z * 2.2);
                        hurtMarked = true;
                        playSound(SoundEvents.TRIDENT_RIPTIDE_3.value(), 2f, 0.7f);
                        dashHits.clear();
                    }
                    if (i >= 6 && i <= 20) {
                        sl().sendParticles(ParticleTypes.ELECTRIC_SPARK, getX(), getY() + 2, getZ(), 12, 0.8, 1.2, 0.8, 0.2);
                        for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(1.5), e -> e != this)) {
                            if (dashHits.add(e.getUUID())) {
                                hitTarget(e, 13);
                                Vec3 push = e.position().subtract(position()).normalize();
                                e.push(push.x * 1.5, 0.5, push.z * 1.5);
                                e.hurtMarked = true;
                            }
                        }
                    }
                })
                .onEnd((b, t, i) -> dashHits.clear()));
    }

    private final Set<UUID> dashHits = new HashSet<>();

    @Override
    protected void passiveTick(LivingEntity target) {
        // Phase 2: the sky itself attacks.
        if (phase() >= 1 && tickCount % 50 == 0 && level() instanceof ServerLevel) {
            for (Player p : playersNear(24)) {
                Vec3 s = ground(p.getX() + random.nextGaussian() * 3, p.getZ() + random.nextGaussian() * 3, p.getY());
                Fx.marker(sl(), s, Blocks.YELLOW_STAINED_GLASS.defaultBlockState(), 1.8f, 20);
                Scheduler.later(sl(), 20, () -> {
                    if (isAlive()) strike(s, 9, 1.3);
                });
            }
        }
    }

    @Override
    protected void onPhaseChange(int phase) {
        if (!(level() instanceof ServerLevel)) return;
        Vec3 c = position();
        for (int k = 0; k < 8; k++) {
            double a = Math.PI * 2 * k / 8;
            Vec3 s = ground(c.x + Math.cos(a) * 7, c.z + Math.sin(a) * 7, c.y);
            Scheduler.later(sl(), 4 + k * 3, () -> strike(s, 8, 1.5));
        }
        sl().setWeatherParameters(0, 6000, true, true);
    }
}
