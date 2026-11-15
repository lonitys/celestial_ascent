package com.celestialascent.titans;

import com.celestialascent.boss.BossAttack;
import com.celestialascent.core.Fx;
import com.celestialascent.core.Scheduler;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/** Magma Titan: 600 HP, three phases. Meteors, eruptions, flame breath; burning ground; enrage at 30%. */
public class MagmaTitan extends TitanBoss {
    public MagmaTitan(EntityType<? extends Monster> type, Level level) {
        super(type, level);
    }

    @Override public Element element() { return Element.MAGMA; }
    @Override public double baseMaxHealth() { return 600; }
    @Override protected float[] phaseThresholds() { return new float[]{0.6f, 0.3f}; }
    @Override protected ParticleOptions ambientParticle() { return ParticleTypes.LAVA; }

    private ServerLevel sl() { return (ServerLevel) level(); }

    private void burn(LivingEntity e, int seconds) {
        if (!e.fireImmune()) e.igniteForSeconds(seconds);
    }

    private void meteorAt(Vec3 at) {
        Fx.marker(sl(), at, Blocks.ORANGE_STAINED_GLASS.defaultBlockState(), 3.0f, 22);
        Fx.fall(sl(), at, Blocks.MAGMA_BLOCK.defaultBlockState(), 1.6f, 22f, 20);
        Scheduler.later(sl(), 20, () -> {
            if (!isAlive()) return;
            level().explode(this, at.x, at.y + 0.5, at.z, 0.0f, false, Level.ExplosionInteraction.NONE);
            sl().sendParticles(ParticleTypes.LAVA, at.x, at.y + 0.3, at.z, 20, 1, 0.3, 1, 0.3);
            sl().sendParticles(ParticleTypes.LARGE_SMOKE, at.x, at.y + 0.5, at.z, 20, 1, 0.5, 1, 0.05);
            for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, new AABB(at, at).inflate(2.8, 2.5, 2.8), e -> e != this)) {
                hitTarget(e, 13);
                burn(e, 5);
                Vec3 push = e.position().subtract(at).normalize();
                e.push(push.x, 0.5, push.z);
                e.hurtMarked = true;
            }
        });
    }

    @Override
    protected void registerAttacks() {
        attacks.add(BossAttack.of("meteor").range(0, 32).cooldown(110).duration(50).weight(12)
                .onTick((b, t, i) -> {
                    if (i < 15 || (i - 15) % 6 != 0) return;
                    var players = playersNear(32);
                    LivingEntity victim = players.isEmpty() ? t : players.get(random.nextInt(players.size()));
                    meteorAt(ground(victim.getX() + random.nextGaussian() * 2.5, victim.getZ() + random.nextGaussian() * 2.5, victim.getY()));
                    if (i == 15) playSound(SoundEvents.BLAZE_SHOOT, 2f, 0.5f);
                }));

        attacks.add(BossAttack.of("eruption").range(0, 6.5).cooldown(80).duration(36).weight(13)
                .onTick((b, t, i) -> {
                    if (i != 20) return;
                    Vec3 c = position();
                    hitArea(c, 6, 16, 1.4);
                    for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(6), e -> e != this)) burn(e, 5);
                    for (int ring = 1; ring <= 3; ring++) {
                        int r = ring;
                        Scheduler.later(sl(), ring * 3, () -> {
                            int n = 6 + r * 4;
                            for (int k = 0; k < n; k++) {
                                double a = Math.PI * 2 * k / n + r;
                                Vec3 p = ground(c.x + Math.cos(a) * r * 2, c.z + Math.sin(a) * r * 2, c.y);
                                Fx.spike(sl(), p, (k % 3 == 0 ? Blocks.MAGMA_BLOCK : Blocks.BASALT).defaultBlockState(),
                                        0.8f, 1.2f + random.nextFloat() * 1.4f, 20, 3, 24, k % 3 == 0);
                            }
                        });
                    }
                    sl().sendParticles(ParticleTypes.LAVA, c.x, c.y + 0.5, c.z, 60, 3, 0.4, 3, 0.4);
                    playSound(SoundEvents.GENERIC_EXPLODE.value(), 2f, 0.6f);
                }));

        attacks.add(BossAttack.of("flame_breath").range(0, 10).cooldown(120).duration(50).weight(10)
                .onTick((b, t, i) -> {
                    if (i < 10 || i > 45) return;
                    faceTowards(t.position());
                    Vec3 mouth = front(1.4, 0.82);
                    Vec3 dir = t.getEyePosition().subtract(mouth).normalize();
                    Fx.cone(sl(), ParticleTypes.FLAME, mouth, dir, 10, 2.4, 18);
                    Fx.cone(sl(), ParticleTypes.SMOKE, mouth, dir, 8, 1.6, 4);
                    if (i % 2 == 0) {
                        for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(11), e -> e != this)) {
                            if (inCone(e, mouth, dir, 28, 10.5)) {
                                hitTarget(e, 2.5f);
                                burn(e, 4);
                            }
                        }
                    }
                    if (i % 10 == 0) playSound(SoundEvents.FIRECHARGE_USE, 2f, 0.5f);
                }));

        attacks.add(BossAttack.of("lava_pool").phase(1).range(0, 20).cooldown(140).duration(30).weight(10)
                .onTick((b, t, i) -> {
                    if (i != 16) return;
                    for (Player p : playersNear(20)) {
                        Vec3 c = ground(p.getX(), p.getZ(), p.getY());
                        Fx.marker(sl(), c, Blocks.MAGMA_BLOCK.defaultBlockState(), 4.0f, 110);
                        for (int k = 1; k <= 10; k++) {
                            Scheduler.later(sl(), 10 + k * 10, () -> {
                                if (!isAlive()) return;
                                sl().sendParticles(ParticleTypes.FLAME, c.x, c.y + 0.2, c.z, 12, 1.4, 0.05, 1.4, 0.01);
                                for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, new AABB(c, c).inflate(2, 1.5, 2), e -> e != this)) {
                                    hitTarget(e, 3);
                                    burn(e, 3);
                                }
                            });
                        }
                    }
                    playSound(SoundEvents.LAVA_POP, 2f, 0.5f);
                }));
    }

    @Override
    protected void passiveTick(LivingEntity target) {
        if (phase() >= 2 && tickCount % 20 == 0 && level() instanceof ServerLevel) {
            for (Player p : playersNear(4.5)) burn(p, 3);
            Fx.ring(sl(), ParticleTypes.FLAME, position().add(0, 0.2, 0), 4.5, 30, 0);
        }
    }

    @Override
    protected void onPhaseChange(int phase) {
        if (!(level() instanceof ServerLevel)) return;
        Vec3 c = position();
        hitArea(c, 7, 8, 2.0);
        sl().sendParticles(ParticleTypes.LAVA, c.x, c.y + 2, c.z, 120, 3, 2, 3, 0.5);
        if (phase == 2) {
            AttributeInstance speed = getAttribute(Attributes.MOVEMENT_SPEED);
            if (speed != null) {
                speed.addOrUpdateTransientModifier(new AttributeModifier(
                        ResourceLocation.fromNamespaceAndPath("celestialascent", "magma_enrage"), 0.25, AttributeModifier.Operation.ADD_MULTIPLIED_BASE));
            }
        }
    }
}
