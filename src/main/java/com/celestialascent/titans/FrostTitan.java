package com.celestialascent.titans;

import com.celestialascent.boss.BossAttack;
import com.celestialascent.core.Fx;
import com.celestialascent.core.Scheduler;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/** Frost Titan: 400 HP. Ground slams, ice-spike lines, freezing breath; blizzard in phase 2. */
public class FrostTitan extends TitanBoss {
    private static final BlockParticleOption ICE = new BlockParticleOption(ParticleTypes.BLOCK, Blocks.BLUE_ICE.defaultBlockState());

    public FrostTitan(EntityType<? extends Monster> type, Level level) {
        super(type, level);
    }

    @Override public Element element() { return Element.FROST; }
    @Override public double baseMaxHealth() { return 400; }
    @Override protected ParticleOptions ambientParticle() { return ParticleTypes.SNOWFLAKE; }

    private ServerLevel sl() { return (ServerLevel) level(); }

    private void chill(LivingEntity e, int freezeTicks, int slowAmp) {
        e.setTicksFrozen(Math.min(e.getTicksFrozen() + freezeTicks, 400));
        e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, slowAmp), this);
    }

    /** Where each player stood at the last Absolute Zero check. */
    private final java.util.Map<java.util.UUID, Vec3> stillCheck = new java.util.HashMap<>();

    @Override
    protected void registerAttacks() {
        attacks.add(BossAttack.of("slam").range(0, 5.5).cooldown(70).duration(30).weight(14)
                .onTick((b, t, i) -> {
                    if (i == 18) {
                        Vec3 c = position();
                        hitArea(c, 5.0, 14, 1.2);
                        for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, new AABB(c, c).inflate(5), e -> e != this)) chill(e, 80, 1);
                        sl().sendParticles(ICE, c.x, c.y + 0.2, c.z, 80, 2.5, 0.2, 2.5, 0.3);
                        Fx.ring(sl(), ParticleTypes.SNOWFLAKE, c, 4.5, 40, 0.3);
                        for (int k = 0; k < 10; k++) {
                            double a = Math.PI * 2 * k / 10;
                            Fx.spike(sl(), ground(c.x + Math.cos(a) * 3.5, c.z + Math.sin(a) * 3.5, c.y), Blocks.BLUE_ICE.defaultBlockState(),
                                    0.6f, 1.6f + random.nextFloat(), 25, 3, 26, false);
                        }
                        playSound(SoundEvents.GLASS_BREAK, 2f, 0.5f);
                        playSound(SoundEvents.GENERIC_EXPLODE.value(), 1.2f, 0.7f);
                    }
                }));

        attacks.add(BossAttack.of("ice_spikes").range(3, 18).cooldown(80).duration(30).weight(12)
                .onStart((b, t, i) -> {
                    Vec3 dir = flatDirTo(t);
                    for (int k = 1; k <= 12; k++) {
                        Vec3 p = position().add(dir.scale(k * 1.4));
                        Fx.marker(sl(), ground(p.x, p.z, getY()), Blocks.LIGHT_BLUE_STAINED_GLASS.defaultBlockState(), 1.1f, 12 + k * 2);
                    }
                })
                .onTick((b, t, i) -> {
                    if (i != 12) return;
                    Vec3 dir = flatDirTo(t);
                    Vec3 start = position();
                    playSound(SoundEvents.GLASS_BREAK, 2f, 0.7f);
                    for (int k = 1; k <= 12; k++) {
                        int step = k;
                        Scheduler.later(sl(), k * 2, () -> {
                            if (!isAlive()) return;
                            Vec3 p = ground(start.x + dir.x * step * 1.4, start.z + dir.z * step * 1.4, start.y);
                            Fx.spike(sl(), p, (step % 2 == 0 ? Blocks.PACKED_ICE : Blocks.BLUE_ICE).defaultBlockState(),
                                    0.9f, 2.2f + random.nextFloat() * 1.3f, 18, 3, 34, false);
                            sl().sendParticles(ICE, p.x, p.y + 0.5, p.z, 12, 0.4, 0.4, 0.4, 0.2);
                            for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, new AABB(p, p).inflate(1.3, 2.5, 1.3), e -> e != this)) {
                                hitTarget(e, 11);
                                chill(e, 120, 2);
                                e.push(0, 0.6, 0);
                            }
                            playSound(SoundEvents.AMETHYST_BLOCK_BREAK, 1.2f, 0.6f);
                        });
                    }
                }));

        attacks.add(BossAttack.of("frost_breath").range(0, 9).cooldown(120).duration(50).weight(10)
                .onTick((b, t, i) -> {
                    if (i < 10 || i > 45) return;
                    faceTowards(t.position());
                    Vec3 mouth = front(1.2, 0.82);
                    Vec3 dir = t.getEyePosition().subtract(mouth).normalize();
                    Fx.cone(sl(), ParticleTypes.SNOWFLAKE, mouth, dir, 9, 2.2, 14);
                    Fx.cone(sl(), ParticleTypes.CLOUD, mouth, dir, 6, 1.4, 4);
                    if (i % 2 == 0) {
                        for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(10), e -> e != this)) {
                            if (inCone(e, mouth, dir, 28, 9.5)) {
                                hitTarget(e, 2.5f);
                                chill(e, 14, 2);
                            }
                        }
                    }
                    if (i % 8 == 0) playSound(SoundEvents.POWDER_SNOW_STEP, 2f, 0.5f);
                }));

        attacks.add(BossAttack.of("blizzard").phase(1).range(0, 22).cooldown(200).duration(60).weight(9)
                .onTick((b, t, i) -> {
                    Vec3 c = position();
                    for (int k = 0; k < 6; k++) {
                        double a = random.nextDouble() * Math.PI * 2, r = random.nextDouble() * 14;
                        sl().sendParticles(ParticleTypes.SNOWFLAKE, c.x + Math.cos(a) * r, c.y + 4 + random.nextDouble() * 4, c.z + Math.sin(a) * r, 2, 0.5, 0.5, 0.5, 0.05);
                    }
                    if (i % 5 == 0) {
                        for (Player p : playersNear(14)) {
                            hitTarget(p, 2);
                            chill(p, 12, 1);
                        }
                    }
                    if (i % 12 == 6) {
                        for (Player p : playersNear(16)) {
                            Vec3 at = ground(p.getX() + random.nextGaussian() * 1.5, p.getZ() + random.nextGaussian() * 1.5, p.getY());
                            Fx.marker(sl(), at, Blocks.LIGHT_BLUE_STAINED_GLASS.defaultBlockState(), 1.6f, 14);
                            Scheduler.later(sl(), 14, () -> {
                                if (!isAlive()) return;
                                Fx.spike(sl(), at, Blocks.BLUE_ICE.defaultBlockState(), 1.0f, 3.2f, 10, 3, 30, false);
                                for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, new AABB(at, at).inflate(1.2, 3, 1.2), e -> e != this)) {
                                    hitTarget(e, 10);
                                    chill(e, 100, 2);
                                }
                                playSound(SoundEvents.GLASS_BREAK, 1.5f, 0.6f);
                            });
                        }
                    }
                    if (i % 20 == 0) playSound(SoundEvents.ELYTRA_FLYING, 1.5f, 0.6f);
                }));
    
        // Stage 3: the floor freezes over. Anyone who stands still is frozen solid.
        attacks.add(BossAttack.of("absolute_zero").phase(2).range(0, 24).cooldown(400).duration(100).weight(9).animation("attack.blizzard")
                .onStart((b, t, i) -> {
                    hint("absolute_zero");
                    stillCheck.clear();
                    for (Player p : playersNear(24)) stillCheck.put(p.getUUID(), p.position());
                    playSound(SoundEvents.GLASS_BREAK, 3f, 0.3f);
                })
                .onTick((b, t, i) -> {
                    Vec3 c = position();
                    if (i % 4 == 0) {
                        for (int k = 0; k < 6; k++) {
                            double a = random.nextDouble() * Math.PI * 2, r = 2 + random.nextDouble() * 16;
                            Fx.marker(sl(), ground(c.x + Math.cos(a) * r, c.z + Math.sin(a) * r, c.y), Blocks.BLUE_ICE.defaultBlockState(), 1.2f, 30);
                        }
                    }
                    sl().sendParticles(ParticleTypes.SNOWFLAKE, c.x, c.y + 3, c.z, 20, 10, 2, 10, 0.02);
                    if (i < 20 || i % 20 != 0) return;
                    for (Player p : playersNear(24)) {
                        Vec3 before = stillCheck.getOrDefault(p.getUUID(), p.position());
                        if (p.position().distanceTo(before) < 2.0) {
                            p.setTicksFrozen(Math.min(p.getTicksRequiredToFreeze() + 160, p.getTicksFrozen() + 120));
                            p.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.MOVEMENT_SLOWDOWN, 40, 3), this);
                            hitTarget(p, 7);
                            Fx.spike(sl(), p.position(), Blocks.PACKED_ICE.defaultBlockState(), 1.4f, 2.4f, 8, 4, 30, false);
                            playSound(SoundEvents.GLASS_BREAK, 1.5f, 0.5f);
                        } else {
                            chill(p, 20, 0);
                        }
                        stillCheck.put(p.getUUID(), p.position());
                    }
                }));
    }

    @Override
    protected void onPhaseChange(int phase) {
        if (!(level() instanceof ServerLevel s)) return;
        Vec3 c = position();
        for (int k = 0; k < 16; k++) {
            double a = Math.PI * 2 * k / 16;
            Fx.spike(s, ground(c.x + Math.cos(a) * 9, c.z + Math.sin(a) * 9, c.y), Blocks.PACKED_ICE.defaultBlockState(),
                    1.2f, 4f + random.nextFloat() * 2, 10, 8, 200, false);
        }
        hitArea(c, 7, 6, 2.2);
        s.sendParticles(ParticleTypes.SNOWFLAKE, c.x, c.y + 2, c.z, 200, 4, 2, 4, 0.2);
    }
}
