package com.celestialascent.empire;

import com.celestialascent.CelestialAscent;
import com.celestialascent.boss.BossAttack;
import com.celestialascent.boss.CelestialBoss;
import com.celestialascent.core.Fx;
import com.celestialascent.core.Scheduler;
import net.minecraft.core.Direction;
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
import net.minecraft.world.entity.projectile.ShulkerBullet;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/** Ender Colossus: 900 HP, three phases. The Empire's last war machine, waiting on the Empty Throne. */
public class EnderColossus extends CelestialBoss {
    private float sweepStartYaw;

    public EnderColossus(EntityType<? extends Monster> type, Level level) {
        super(type, level);
        this.xpReward = 1500;
    }

    public static AttributeSupplier.Builder attributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 900).add(Attributes.ATTACK_DAMAGE, 18)
                .add(Attributes.MOVEMENT_SPEED, 0.25).add(Attributes.ARMOR, 20).add(Attributes.ARMOR_TOUGHNESS, 10)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1.0).add(Attributes.FOLLOW_RANGE, 64).add(Attributes.STEP_HEIGHT, 2.0);
    }

    @Override public ResourceLocation bossId() { return ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "ender_colossus"); }
    @Override public double baseMaxHealth() { return 900; }
    @Override protected float[] phaseThresholds() { return new float[]{0.66f, 0.33f}; }
    @Override protected BossEvent.BossBarColor barColor() { return BossEvent.BossBarColor.PURPLE; }
    @Override protected ParticleOptions ambientParticle() { return ParticleTypes.REVERSE_PORTAL; }

    private ServerLevel sl() { return (ServerLevel) level(); }

    @Override
    protected void registerAttacks() {
        attacks.add(BossAttack.of("void_slam").range(0, 6.5).cooldown(70).duration(32).weight(13)
                .onTick((b, t, i) -> {
                    if (i != 18) return;
                    Vec3 c = position();
                    hitArea(c, 6.5, 18, 1.5);
                    for (int k = 0; k < 14; k++) {
                        double a = Math.PI * 2 * k / 14;
                        Fx.spike(sl(), ground(c.x + Math.cos(a) * 4.5, c.z + Math.sin(a) * 4.5, c.y),
                                (k % 2 == 0 ? Blocks.OBSIDIAN : Blocks.PURPUR_PILLAR).defaultBlockState(), 0.7f, 1.8f + random.nextFloat(), 20, 3, 26, false);
                    }
                    sl().sendParticles(ParticleTypes.REVERSE_PORTAL, c.x, c.y + 0.5, c.z, 120, 3, 0.3, 3, 0.2);
                    playSound(SoundEvents.GENERIC_EXPLODE.value(), 2f, 0.5f);
                }));

        attacks.add(BossAttack.of("ender_beam").range(4, 24).cooldown(110).duration(50).weight(11)
                .onStart((b, t, i) -> {
                    faceTowards(t.position());
                    sweepStartYaw = getYRot() - 45;
                })
                .onTick((b, t, i) -> {
                    if (i < 10) return;
                    float yaw = sweepStartYaw + (i - 10) * (90f / 40f);
                    setYRot(yaw);
                    setYBodyRot(yaw);
                    setYHeadRot(yaw);
                    Vec3 eye = position().add(0, getBbHeight() * 0.8, 0);
                    Vec3 dir = Vec3.directionFromRotation(10, yaw);
                    Vec3 end = eye.add(dir.scale(24));
                    Fx.line(sl(), ParticleTypes.DRAGON_BREATH, eye, end, 0.5);
                    if (i % 3 == 0) {
                        for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, new AABB(eye, end).inflate(1.5), e -> e != this)) {
                            Vec3 rel = e.position().add(0, e.getBbHeight() / 2, 0).subtract(eye);
                            double along = rel.dot(dir);
                            if (along > 0 && rel.subtract(dir.scale(along)).length() < 1.6) hitTarget(e, 5);
                        }
                    }
                    if (i % 10 == 0) playSound(SoundEvents.ENDER_DRAGON_GROWL, 1.5f, 1.6f);
                }));

        attacks.add(BossAttack.of("rift_blink").range(6, 30).cooldown(90).duration(28).weight(11)
                .onTick((b, t, i) -> {
                    if (i == 6) {
                        sl().sendParticles(ParticleTypes.PORTAL, getX(), getY() + 2, getZ(), 80, 1, 2, 1, 0.5);
                        Vec3 behind = t.position().subtract(Vec3.directionFromRotation(0, t.getYRot()).scale(3));
                        Vec3 g = ground(behind.x, behind.z, t.getY());
                        teleportTo(g.x, g.y, g.z);
                        faceTowards(t.position());
                        playSound(SoundEvents.ENDERMAN_TELEPORT, 2f, 0.5f);
                    }
                    if (i == 16) {
                        hitArea(position(), 4.5, 15, 1.4);
                        sl().sendParticles(ParticleTypes.REVERSE_PORTAL, getX(), getY() + 0.5, getZ(), 60, 2, 0.3, 2, 0.2);
                        playSound(SoundEvents.IRON_GOLEM_ATTACK, 2f, 0.4f);
                    }
                }));

        attacks.add(BossAttack.of("shulker_barrage").phase(1).range(0, 30).cooldown(120).duration(40).weight(10)
                .onTick((b, t, i) -> {
                    if (i < 8 || i % 5 != 0) return;
                    var players = playersNear(30);
                    LivingEntity victim = players.isEmpty() ? t : players.get(random.nextInt(players.size()));
                    ShulkerBullet bullet = new ShulkerBullet(level(), this, victim, Direction.Axis.Y);
                    bullet.setPos(getX(), getY() + getBbHeight() * 0.85, getZ());
                    level().addFreshEntity(bullet);
                    playSound(SoundEvents.SHULKER_SHOOT, 2f, 0.7f);
                }));

        attacks.add(BossAttack.of("gravity_well").phase(2).range(0, 18).cooldown(160).duration(50).weight(10)
                .onTick((b, t, i) -> {
                    Vec3 c = position();
                    if (i < 34) {
                        for (Player p : playersNear(16)) {
                            Vec3 pull = c.subtract(p.position()).normalize().scale(0.12);
                            p.push(pull.x, 0.04, pull.z);
                            p.hurtMarked = true;
                        }
                        Fx.ring(sl(), ParticleTypes.REVERSE_PORTAL, c.add(0, 0.5, 0), 14 - i * 0.35, 24, 0);
                    }
                    if (i == 34) {
                        for (Player p : playersNear(7)) p.addEffect(new MobEffectInstance(MobEffects.LEVITATION, 30, 2), this);
                        playSound(SoundEvents.ENDER_DRAGON_FLAP, 2f, 0.5f);
                    }
                    if (i == 46) {
                        hitArea(c, 7, 20, 1.0);
                        sl().sendParticles(ParticleTypes.EXPLOSION_EMITTER, c.x, c.y + 1, c.z, 1, 0, 0, 0, 0);
                    }
                }));
    }

    @Override
    protected void onPhaseChange(int phase) {
        if (!(level() instanceof ServerLevel s)) return;
        hitArea(position(), 8, 8, 2.4);
        for (int k = 0; k < phase + 1; k++) {
            Scheduler.later(s, 10 + k * 10, () -> {
                SentinelConstruct guard = Empire.SENTINEL.get().create(s);
                if (guard == null || !isAlive()) return;
                Vec3 p = ground(getX() + random.nextGaussian() * 6, getZ() + random.nextGaussian() * 6, getY());
                guard.moveTo(p.x, p.y, p.z, random.nextFloat() * 360, 0);
                s.addFreshEntity(guard);
                s.sendParticles(ParticleTypes.REVERSE_PORTAL, p.x, p.y + 1.5, p.z, 60, 0.6, 1.2, 0.6, 0.1);
            });
        }
        playSound(SoundEvents.ENDER_DRAGON_GROWL, 3f, 0.5f);
    }
}
