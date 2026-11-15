package com.celestialascent.stars;

import com.celestialascent.CelestialAscent;
import com.celestialascent.boss.BossAttack;
import com.celestialascent.boss.FlyingBoss;
import com.celestialascent.core.Fx;
import com.celestialascent.core.Scheduler;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.BossEvent;
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

import java.util.HashSet;
import java.util.Set;
import java.util.UUID;

/** Astral Seraph: 1200 HP flying celestial. Falling light lances, wing gusts, dives; radiant nova in phase 2. */
public class AstralSeraph extends FlyingBoss {
    private final Set<UUID> diveHits = new HashSet<>();

    public AstralSeraph(EntityType<? extends Monster> type, Level level) {
        super(type, level);
        this.xpReward = 2000;
    }

    public static AttributeSupplier.Builder attributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 1200).add(Attributes.ATTACK_DAMAGE, 18)
                .add(Attributes.MOVEMENT_SPEED, 0.3).add(Attributes.FLYING_SPEED, 0.6).add(Attributes.ARMOR, 18).add(Attributes.ARMOR_TOUGHNESS, 10)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1.0).add(Attributes.FOLLOW_RANGE, 64);
    }

    @Override public ResourceLocation bossId() { return ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "astral_seraph"); }
    @Override public double baseMaxHealth() { return 1200; }
    @Override protected float[] phaseThresholds() { return new float[]{0.5f}; }
    @Override protected BossEvent.BossBarColor barColor() { return BossEvent.BossBarColor.WHITE; }
    @Override protected ParticleOptions ambientParticle() { return ParticleTypes.END_ROD; }
    @Override protected String moveAnimation() { return "fly"; }
    @Override protected int animTransition() { return 0; } // spinning halo/crown parts

    private ServerLevel sl() { return (ServerLevel) level(); }

    private void lance(Vec3 at) {
        Fx.marker(sl(), at, Blocks.WHITE_STAINED_GLASS.defaultBlockState(), 1.8f, 20);
        Fx.fall(sl(), at, Blocks.END_ROD.defaultBlockState(), 1.4f, 18f, 18);
        Scheduler.later(sl(), 18, () -> {
            if (!isAlive()) return;
            sl().sendParticles(ParticleTypes.END_ROD, at.x, at.y + 0.5, at.z, 30, 0.6, 0.6, 0.6, 0.15);
            sl().sendParticles(ParticleTypes.FLASH, at.x, at.y + 0.5, at.z, 1, 0, 0, 0, 0);
            for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, new AABB(at, at).inflate(1.8, 2.5, 1.8), e -> e != this)) hitTarget(e, 16);
            playSound(SoundEvents.AMETHYST_BLOCK_RESONATE, 2f, 1.6f);
        });
    }

    @Override
    protected void registerAttacks() {
        attacks.add(BossAttack.of("light_lances").range(0, 40).cooldown(80).duration(40).weight(13)
                .onTick((b, t, i) -> {
                    if (i < 8 || i % 4 != 0) return;
                    for (Player p : playersNear(40)) {
                        Vec3 lead = p.position().add(p.getDeltaMovement().scale(10));
                        lance(ground(lead.x + random.nextGaussian(), lead.z + random.nextGaussian(), p.getY()));
                    }
                }));
        attacks.add(BossAttack.of("wing_gust").range(0, 16).cooldown(70).duration(30).weight(11)
                .onTick((b, t, i) -> {
                    if (i != 14) return;
                    Vec3 o = position().add(0, getBbHeight() / 2, 0);
                    Vec3 dir = t.getEyePosition().subtract(o).normalize();
                    Fx.cone(sl(), ParticleTypes.CLOUD, o, dir, 16, 4, 70);
                    Fx.cone(sl(), ParticleTypes.END_ROD, o, dir, 14, 3, 30);
                    for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(17), e -> e != this)) {
                        Vec3 to = e.position().add(0, e.getBbHeight() / 2, 0).subtract(o);
                        if (to.length() < 16.5 && to.normalize().dot(dir) > Math.cos(Math.toRadians(32))) {
                            hitTarget(e, 9);
                            e.push(dir.x * 2.2, 0.6, dir.z * 2.2);
                            e.hurtMarked = true;
                        }
                    }
                    playSound(SoundEvents.ENDER_DRAGON_FLAP, 2f, 1.3f);
                }));
        attacks.add(BossAttack.of("dive").range(4, 30).cooldown(90).duration(30).weight(11).mobile()
                .onTick((b, t, i) -> {
                    if (i == 10) {
                        diveHits.clear();
                        Vec3 dir = t.position().add(0, 1, 0).subtract(position()).normalize();
                        setDeltaMovement(dir.scale(2.4));
                        playSound(SoundEvents.PHANTOM_SWOOP, 2f, 0.6f);
                    }
                    if (i >= 10 && i <= 24) {
                        sl().sendParticles(ParticleTypes.END_ROD, getX(), getY() + 1, getZ(), 6, 0.6, 0.6, 0.6, 0.05);
                        for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(1.5), e -> e != this)) {
                            if (diveHits.add(e.getUUID())) {
                                hitTarget(e, 18);
                                e.push(0, 0.8, 0);
                                e.hurtMarked = true;
                            }
                        }
                    }
                }));
        attacks.add(BossAttack.of("radiant_nova").phase(1).range(0, 24).cooldown(160).duration(50).weight(10)
                .onTick((b, t, i) -> {
                    if (i < 20) {
                        sl().sendParticles(ParticleTypes.END_ROD, getX(), getY() + getBbHeight() / 2, getZ(), 10, 1.5, 1.5, 1.5, 0.02);
                        return;
                    }
                    double r = (i - 20) * 0.9;
                    Vec3 c = ground(getX(), getZ(), getY() - 8).add(0, 0.6, 0);
                    Fx.ring(sl(), ParticleTypes.END_ROD, c, r, 48, 0);
                    for (Player p : playersNear(30)) {
                        double d = Math.hypot(p.getX() - c.x, p.getZ() - c.z);
                        if (Math.abs(d - r) < 0.9 && p.getY() - c.y < 2.2) hitTarget(p, 14);
                    }
                    if (i == 20) playSound(SoundEvents.BEACON_DEACTIVATE, 3f, 1.6f);
                }));
    }

    @Override
    protected void onPhaseChange(int phase) {
        if (level() instanceof ServerLevel s) {
            s.sendParticles(ParticleTypes.END_ROD, getX(), getY() + 1.5, getZ(), 200, 3, 3, 3, 0.2);
            for (Player p : playersNear(40)) lance(ground(p.getX(), p.getZ(), p.getY()));
        }
    }
}
