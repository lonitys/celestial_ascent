package com.celestialascent.empire;

import com.celestialascent.CelestialAscent;
import com.celestialascent.boss.BossAttack;
import com.celestialascent.boss.CelestialBoss;
import com.celestialascent.core.Fx;
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
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

import java.util.HashSet;
import java.util.Set;
import java.util.UUID;

/** Sentinel Construct: 300 HP war machine guarding each Imperial Pylon. */
public class SentinelConstruct extends CelestialBoss {
    private final Set<UUID> chargeHits = new HashSet<>();

    public SentinelConstruct(EntityType<? extends Monster> type, Level level) {
        super(type, level);
        this.xpReward = 150;
    }

    public static AttributeSupplier.Builder attributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 300).add(Attributes.ATTACK_DAMAGE, 12)
                .add(Attributes.MOVEMENT_SPEED, 0.26).add(Attributes.ARMOR, 16).add(Attributes.ARMOR_TOUGHNESS, 6)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1.0).add(Attributes.FOLLOW_RANGE, 40).add(Attributes.STEP_HEIGHT, 1.2);
    }

    @Override public ResourceLocation bossId() { return ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "sentinel_construct"); }
    @Override public double baseMaxHealth() { return 300; }
    @Override protected float[] phaseThresholds() { return new float[]{0.4f}; }
    @Override protected BossEvent.BossBarColor barColor() { return BossEvent.BossBarColor.PURPLE; }
    @Override protected ParticleOptions ambientParticle() { return ParticleTypes.PORTAL; }

    private ServerLevel sl() { return (ServerLevel) level(); }

    @Override
    protected void registerAttacks() {
        attacks.add(BossAttack.of("laser").range(3, 24).cooldown(70).duration(36).weight(12)
                .onTick((b, t, i) -> {
                    if (i < 10 || i > 32) return;
                    faceTowards(t.position());
                    Vec3 eye = front(0.6, 0.78);
                    Vec3 end = t.getEyePosition();
                    var hit = level().clip(new ClipContext(eye, end, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, this));
                    Vec3 stop = hit.getType() == HitResult.Type.BLOCK ? hit.getLocation() : end;
                    Fx.line(sl(), ParticleTypes.DRAGON_BREATH, eye, stop, 0.4);
                    Fx.line(sl(), ParticleTypes.END_ROD, eye, stop, 1.2);
                    if (i % 4 == 0 && stop == end) hitTarget(t, 3.5f);
                    if (i % 8 == 0) playSound(SoundEvents.BEACON_AMBIENT, 1.5f, 1.8f);
                }));
        attacks.add(BossAttack.of("stomp").range(0, 4.5).cooldown(60).duration(28).weight(12)
                .onTick((b, t, i) -> {
                    if (i != 16) return;
                    hitArea(position(), 4.5, 12, 1.3);
                    Fx.ring(sl(), ParticleTypes.REVERSE_PORTAL, position().add(0, 0.2, 0), 4, 40, 0);
                    playSound(SoundEvents.IRON_GOLEM_ATTACK, 2f, 0.5f);
                }));
        attacks.add(BossAttack.of("charge").phase(1).range(5, 18).cooldown(80).duration(26).weight(10).mobile()
                .onTick((b, t, i) -> {
                    if (i == 8) {
                        chargeHits.clear();
                        Vec3 dir = t.position().subtract(position()).normalize();
                        setDeltaMovement(dir.x * 1.8, 0.1, dir.z * 1.8);
                        hurtMarked = true;
                        playSound(SoundEvents.RAVAGER_ROAR, 1.5f, 1.2f);
                    }
                    if (i >= 8 && i <= 22) {
                        for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(1.2), e -> e != this)) {
                            if (chargeHits.add(e.getUUID())) {
                                hitTarget(e, 12);
                                Vec3 push = e.position().subtract(position()).normalize();
                                e.push(push.x * 1.4, 0.5, push.z * 1.4);
                                e.hurtMarked = true;
                            }
                        }
                    }
                }));
    }
}
