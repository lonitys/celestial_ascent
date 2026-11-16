package com.celestialascent.stars;

import com.celestialascent.CelestialAscent;
import com.celestialascent.boss.BossAttack;
import com.celestialascent.boss.CelestialBoss;
import com.celestialascent.core.Fx;
import com.celestialascent.core.Scheduler;
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
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/**
 * Sun Herald: 1600 HP, three phases. Solar flares, sunbursts and corona rings; an eclipse in phase 2
 * and a supernova in phase 3 that must be survived behind cover.
 */
public class SunHerald extends CelestialBoss {
    public SunHerald(EntityType<? extends Monster> type, Level level) {
        super(type, level);
        this.xpReward = 2600;
    }

    public static AttributeSupplier.Builder attributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 1600).add(Attributes.ATTACK_DAMAGE, 20)
                .add(Attributes.MOVEMENT_SPEED, 0.27).add(Attributes.ARMOR, 22).add(Attributes.ARMOR_TOUGHNESS, 12)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1.0).add(Attributes.FOLLOW_RANGE, 64).add(Attributes.STEP_HEIGHT, 1.5);
    }

    @Override public ResourceLocation bossId() { return ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "sun_herald"); }
    @Override public double baseMaxHealth() { return 1600; }
    @Override protected BossEvent.BossBarColor barColor() { return BossEvent.BossBarColor.YELLOW; }
    @Override protected ParticleOptions ambientParticle() { return ParticleTypes.FLAME; }
    @Override protected int animTransition() { return 0; } // spinning halo/crown parts

    private ServerLevel sl() { return (ServerLevel) level(); }

    private void burn(LivingEntity e, int s) {
        if (!e.fireImmune()) e.igniteForSeconds(s);
    }

    @Override
    protected void registerAttacks() {
        attacks.add(BossAttack.of("solar_flare").range(3, 28).cooldown(70).duration(40).weight(13)
                .onTick((b, t, i) -> {
                    if (i < 10 || i > 36) return;
                    faceTowards(t.position());
                    Vec3 eye = front(0.5, 0.8);
                    Vec3 end = t.getEyePosition();
                    var hit = level().clip(new ClipContext(eye, end, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, this));
                    Vec3 stop = hit.getType() == HitResult.Type.BLOCK ? hit.getLocation() : end;
                    Fx.line(sl(), ParticleTypes.FLAME, eye, stop, 0.35);
                    Fx.line(sl(), ParticleTypes.SMALL_FLAME, eye, stop, 0.5);
                    if (i % 4 == 0 && stop == end) {
                        hitTarget(t, 5);
                        burn(t, 4);
                    }
                }));
        attacks.add(BossAttack.of("sunburst").range(0, 7).cooldown(70).duration(32).weight(13)
                .onTick((b, t, i) -> {
                    if (i != 18) return;
                    hitArea(position(), 7, 20, 1.6);
                    for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(7), e -> e != this)) burn(e, 6);
                    sl().sendParticles(ParticleTypes.FLAME, getX(), getY() + 1, getZ(), 150, 3, 1, 3, 0.2);
                    sl().sendParticles(ParticleTypes.EXPLOSION, getX(), getY() + 1.5, getZ(), 6, 2, 0.5, 2, 0);
                    playSound(SoundEvents.GENERIC_EXPLODE.value(), 2f, 0.8f);
                }));
        attacks.add(BossAttack.of("corona_ring").range(0, 30).cooldown(120).duration(60).weight(10)
                .onTick((b, t, i) -> {
                    if (i < 10) return;
                    double r = (i - 10) * 0.6;
                    Vec3 c = position().add(0, 0.3, 0);
                    Fx.ring(sl(), ParticleTypes.FLAME, c, r, 56, 0);
                    for (Player p : playersNear(32)) {
                        double d = Math.hypot(p.getX() - c.x, p.getZ() - c.z);
                        if (Math.abs(d - r) < 0.8 && p.getY() - c.y < 1.5) {
                            hitTarget(p, 12);
                            burn(p, 5);
                        }
                    }
                }));
        attacks.add(BossAttack.of("eclipse").phase(1).range(0, 32).cooldown(200).duration(60).weight(9)
                .onTick((b, t, i) -> {
                    if (i == 0) {
                        for (Player p : playersNear(40)) p.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 200, 0), this);
                        playSound(SoundEvents.WARDEN_SONIC_CHARGE, 3f, 0.5f);
                    }
                    if (i % 15 == 5) {
                        for (Player p : playersNear(32)) {
                            Vec3 at = ground(p.getX(), p.getZ(), p.getY());
                            Fx.marker(sl(), at, Blocks.ORANGE_STAINED_GLASS.defaultBlockState(), 2.6f, 15);
                            Scheduler.later(sl(), 15, () -> {
                                if (!isAlive()) return;
                                Fx.spike(sl(), at, Blocks.SHROOMLIGHT.defaultBlockState(), 1.2f, 5f, 0, 3, 14, true);
                                for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, new AABB(at, at).inflate(1.4, 5, 1.4), e -> e != this)) {
                                    hitTarget(e, 15);
                                    burn(e, 5);
                                }
                            });
                        }
                    }
                }));
        attacks.add(BossAttack.of("supernova").phase(2).range(0, 40).cooldown(320).duration(80).weight(8)
                .onTick((b, t, i) -> {
                    if (i < 60) {
                        Fx.ring(sl(), ParticleTypes.FLAME, position().add(0, getBbHeight() / 2, 0), 6 - i * 0.09, 30, 0);
                        if (i % 20 == 0) playSound(SoundEvents.BEACON_POWER_SELECT, 3f, 0.5f + i / 60f);
                        return;
                    }
                    if (i == 60) {
                        Vec3 core = position().add(0, getBbHeight() / 2, 0);
                        for (Player p : playersNear(40)) {
                            var hit = level().clip(new ClipContext(core, p.getEyePosition(), ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, this));
                            if (hit.getType() == HitResult.Type.MISS) {
                                hitTarget(p, 34);
                                burn(p, 8);
                            }
                        }
                        sl().sendParticles(ParticleTypes.FLASH, core.x, core.y, core.z, 3, 1, 1, 1, 0);
                        sl().sendParticles(ParticleTypes.FLAME, core.x, core.y, core.z, 400, 8, 4, 8, 0.4);
                        playSound(SoundEvents.GENERIC_EXPLODE.value(), 4f, 0.4f);
                    }
                }));
    }

    @Override
    protected void onPhaseChange(int phase) {
        if (level() instanceof ServerLevel s) {
            hitArea(position(), 8, 10, 2.5);
            s.sendParticles(ParticleTypes.FLAME, getX(), getY() + 2, getZ(), 200, 3, 2, 3, 0.3);
            for (Player p : playersNear(40)) {
                p.sendSystemMessage(net.minecraft.network.chat.Component.translatable(
                        phase == 2 ? "message.celestialascent.herald_supernova" : "message.celestialascent.herald_eclipse").withColor(0xFFC93C));
            }
        }
    }
}
