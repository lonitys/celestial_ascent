package com.celestialascent.abyss;

import com.celestialascent.CelestialAscent;
import com.celestialascent.boss.BossAttack;
import com.celestialascent.boss.CelestialBoss;
import com.celestialascent.core.Fx;
import com.celestialascent.core.Scheduler;
import net.minecraft.core.BlockPos;
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

/**
 * Void Sovereign: 3000 HP, four phases. The final boss, far beyond the Ender Dragon (200 HP).
 * Cleaves, void meteors, black holes, abyssal rends; wraith calls, floor collapse and the Unmaking.
 */
public class VoidSovereign extends CelestialBoss {
    private static final DustParticleOptions VOID = new DustParticleOptions(new Vector3f(0.37f, 0.17f, 0.6f), 2.5f);

    public VoidSovereign(EntityType<? extends Monster> type, Level level) {
        super(type, level);
        this.xpReward = 5000;
    }

    public static AttributeSupplier.Builder attributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 3000).add(Attributes.ATTACK_DAMAGE, 24)
                .add(Attributes.MOVEMENT_SPEED, 0.27).add(Attributes.ARMOR, 25).add(Attributes.ARMOR_TOUGHNESS, 15)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1.0).add(Attributes.FOLLOW_RANGE, 64).add(Attributes.STEP_HEIGHT, 2.0);
    }

    @Override public ResourceLocation bossId() { return ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "void_sovereign"); }
    @Override public double baseMaxHealth() { return 3000; }
    @Override protected float[] phaseThresholds() { return new float[]{0.75f, 0.5f, 0.25f}; }
    @Override protected BossEvent.BossBarColor barColor() { return BossEvent.BossBarColor.PURPLE; }
    @Override protected ParticleOptions ambientParticle() { return VOID; }

    private ServerLevel sl() { return (ServerLevel) level(); }

    private void meteor(Vec3 at) {
        Fx.marker(sl(), at, Blocks.PURPLE_STAINED_GLASS.defaultBlockState(), 3.2f, 22);
        Fx.fall(sl(), at, Blocks.CRYING_OBSIDIAN.defaultBlockState(), 1.8f, 24f, 20);
        Scheduler.later(sl(), 20, () -> {
            if (!isAlive()) return;
            level().explode(this, at.x, at.y + 0.5, at.z, 0f, false, Level.ExplosionInteraction.NONE);
            sl().sendParticles(VOID, at.x, at.y + 0.5, at.z, 40, 1.4, 0.6, 1.4, 0);
            for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, new AABB(at, at).inflate(3, 2.5, 3), e -> e != this)) {
                hitTarget(e, 18);
                e.addEffect(new MobEffectInstance(MobEffects.WITHER, 80, 1), this);
            }
        });
    }

    @Override
    protected void registerAttacks() {
        attacks.add(BossAttack.of("void_cleave").range(0, 6.5).cooldown(60).duration(28).weight(14)
                .onTick((b, t, i) -> {
                    if (i != 16) return;
                    Vec3 dir = Vec3.directionFromRotation(0, getYRot());
                    for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(6.5), e -> e != this)) {
                        Vec3 to = e.position().subtract(position());
                        if (to.length() < 6.5 && to.normalize().dot(dir) > 0.2) {
                            hitTarget(e, 26);
                            e.addEffect(new MobEffectInstance(MobEffects.WITHER, 100, 1), this);
                            e.push(dir.x * 1.2, 0.4, dir.z * 1.2);
                            e.hurtMarked = true;
                        }
                    }
                    Fx.cone(sl(), VOID, front(1, 0.5), dir, 6.5, 4, 60);
                    playSound(SoundEvents.WARDEN_ATTACK_IMPACT, 2f, 0.5f);
                }));
        attacks.add(BossAttack.of("void_meteors").range(0, 40).cooldown(110).duration(50).weight(12)
                .onTick((b, t, i) -> {
                    if (i < 12 || i % 6 != 0) return;
                    var ps = playersNear(40);
                    LivingEntity v = ps.isEmpty() ? t : ps.get(random.nextInt(ps.size()));
                    meteor(ground(v.getX() + random.nextGaussian() * 2, v.getZ() + random.nextGaussian() * 2, v.getY()));
                }));
        attacks.add(BossAttack.of("black_hole").range(0, 24).cooldown(160).duration(60).weight(10)
                .onStart((b, t, i) -> getPersistentData().putLong("Hole", BlockPos.containing(t.position().add(0, 1.5, 0)).asLong()))
                .onTick((b, t, i) -> {
                    Vec3 c = Vec3.atCenterOf(BlockPos.of(getPersistentData().getLong("Hole")));
                    sl().sendParticles(ParticleTypes.REVERSE_PORTAL, c.x, c.y, c.z, 12, 1.5, 1.5, 1.5, 0.3);
                    sl().sendParticles(VOID, c.x, c.y, c.z, 6, 0.4, 0.4, 0.4, 0);
                    for (Player p : playersNear(30)) {
                        Vec3 to = c.subtract(p.position());
                        double d = to.length();
                        if (d < 14) {
                            Vec3 pull = to.normalize().scale(0.09 + (14 - d) * 0.006);
                            p.push(pull.x, pull.y * 0.5, pull.z);
                            p.hurtMarked = true;
                        }
                        if (d < 2.2 && i % 5 == 0) hitTarget(p, 8);
                    }
                    if (i % 20 == 0) playSound(SoundEvents.PORTAL_AMBIENT, 3f, 0.5f);
                }));
        attacks.add(BossAttack.of("abyssal_rend").range(0, 15).cooldown(100).duration(40).weight(11)
                .onTick((b, t, i) -> {
                    if (i != 20) return;
                    Vec3 o = front(1, 0.6);
                    Vec3 dir = t.getEyePosition().subtract(o).normalize();
                    Fx.cone(sl(), VOID, o, dir, 15, 4, 120);
                    Fx.cone(sl(), ParticleTypes.SCULK_SOUL, o, dir, 12, 3, 20);
                    for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(16), e -> e != this)) {
                        Vec3 to = e.getEyePosition().subtract(o);
                        if (to.length() < 15 && to.normalize().dot(dir) > Math.cos(Math.toRadians(30))) {
                            hitTarget(e, 20);
                            e.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 160, 0), this);
                        }
                    }
                    playSound(SoundEvents.WARDEN_SONIC_BOOM, 3f, 0.6f);
                }));
        attacks.add(BossAttack.of("wraith_call").phase(1).range(0, 40).cooldown(240).duration(30).weight(8)
                .onTick((b, t, i) -> {
                    if (i != 15) return;
                    for (int k = 0; k < 2 + phase(); k++) {
                        VoidWraith w = Abyss.VOID_WRAITH.get().create(sl());
                        if (w == null) continue;
                        w.moveTo(getX() + random.nextGaussian() * 3, getY() + 3, getZ() + random.nextGaussian() * 3, 0, 0);
                        w.setTarget(t);
                        sl().addFreshEntity(w);
                    }
                    playSound(SoundEvents.VEX_CHARGE, 3f, 0.5f);
                }));
        attacks.add(BossAttack.of("collapse").phase(2).range(0, 30).cooldown(180).duration(40).weight(9)
                .onTick((b, t, i) -> {
                    if (i != 10) return;
                    for (Player p : playersNear(30)) {
                        BlockPos under = p.blockPosition().below();
                        Fx.marker(sl(), Vec3.atBottomCenterOf(under.above()), Blocks.MAGENTA_STAINED_GLASS.defaultBlockState(), 5f, 25);
                        for (BlockPos q : BlockPos.betweenClosed(under.offset(-2, -1, -2), under.offset(2, 0, 2))) {
                            AbyssalStoneBlock.crack(sl(), q.immutable(), 4 + random.nextInt(10));
                        }
                        Scheduler.later(sl(), 25, () -> {
                            if (isAlive() && p.distanceToSqr(Vec3.atCenterOf(under)) < 9) hitTarget(p, 12);
                        });
                    }
                    playSound(SoundEvents.DEEPSLATE_BREAK, 3f, 0.4f);
                }));
        attacks.add(BossAttack.of("unmaking").phase(3).range(0, 40).cooldown(200).duration(60).weight(10).mobile()
                .onTick((b, t, i) -> {
                    if (i % 18 != 4) return;
                    var ps = playersNear(40);
                    LivingEntity v = ps.isEmpty() ? t : ps.get(random.nextInt(ps.size()));
                    sl().sendParticles(ParticleTypes.REVERSE_PORTAL, getX(), getY() + 2, getZ(), 60, 1, 2, 1, 0.4);
                    Vec3 g = ground(v.getX() + random.nextGaussian() * 2, v.getZ() + random.nextGaussian() * 2, v.getY());
                    teleportTo(g.x, g.y, g.z);
                    faceTowards(v.position());
                    Scheduler.later(sl(), 8, () -> {
                        if (!isAlive()) return;
                        hitArea(position(), 5, 22, 1.6);
                        sl().sendParticles(VOID, getX(), getY() + 0.5, getZ(), 80, 2.5, 0.3, 2.5, 0);
                        playSound(SoundEvents.GENERIC_EXPLODE.value(), 2f, 0.4f);
                    });
                }));
    }

    @Override
    protected void passiveTick(LivingEntity target) {
        if (phase() >= 3 && tickCount % 40 == 0) {
            for (Player p : playersNear(32)) p.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 60, 0), this);
        }
    }

    @Override
    protected void onPhaseChange(int phase) {
        if (level() instanceof ServerLevel s) {
            hitArea(position(), 9, 12, 2.6);
            s.sendParticles(VOID, getX(), getY() + 2, getZ(), 300, 4, 3, 4, 0);
            for (Player p : playersNear(48)) {
                p.sendSystemMessage(net.minecraft.network.chat.Component.translatable("message.celestialascent.sovereign_phase_" + phase).withColor(0xB45CFF));
            }
        }
    }
}
