package com.celestialascent.titans;

import com.celestialascent.boss.BossAttack;
import com.celestialascent.core.Fx;
import com.celestialascent.core.Scheduler;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.Drowned;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.ThrownTrident;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import java.util.HashSet;
import java.util.Set;
import java.util.UUID;

/** Tide Titan: 450 HP. Trident volleys, tidal waves, a whirlpool pull; water jet and drowned guards in phase 2. */
public class TideTitan extends TitanBoss {
    public TideTitan(EntityType<? extends Monster> type, Level level) {
        super(type, level);
    }

    @Override public Element element() { return Element.TIDE; }
    @Override public double baseMaxHealth() { return 450; }
    @Override protected ParticleOptions ambientParticle() { return ParticleTypes.DRIPPING_WATER; }

    private ServerLevel sl() { return (ServerLevel) level(); }

    private void throwTrident(LivingEntity target, double spreadDeg) {
        Vec3 hand = front(0.8, 0.75).add(Vec3.directionFromRotation(0, getYRot() + 90).scale(1.1));
        ThrownTrident tr = new ThrownTrident(level(), this, new ItemStack(Items.TRIDENT));
        tr.setPos(hand.x, hand.y, hand.z);
        tr.pickup = AbstractArrow.Pickup.DISALLOWED;
        Vec3 aim = target.getEyePosition().subtract(hand);
        double yaw = Math.atan2(aim.z, aim.x) + Math.toRadians(spreadDeg);
        double flat = Math.sqrt(aim.x * aim.x + aim.z * aim.z);
        tr.shoot(Math.cos(yaw) * flat, aim.y + flat * 0.08, Math.sin(yaw) * flat, 2.4f, 1.0f);
        level().addFreshEntity(tr);
        Scheduler.later(sl(), 80, tr::discard);
    }

    @Override
    protected void registerAttacks() {
        attacks.add(BossAttack.of("trident_throw").range(4, 30).cooldown(60).duration(30).weight(12)
                .onTick((b, t, i) -> {
                    if (i != 15) return;
                    throwTrident(t, 0);
                    if (phase() >= 1) {
                        throwTrident(t, -12);
                        throwTrident(t, 12);
                    }
                    playSound(SoundEvents.TRIDENT_THROW.value(), 2f, 0.6f);
                }));

        attacks.add(BossAttack.of("tidal_wave").range(0, 14).cooldown(90).duration(40).weight(12)
                .onTick((b, t, i) -> {
                    if (i != 16) return;
                    Vec3 dir = flatDirTo(t);
                    Vec3 side = new Vec3(-dir.z, 0, dir.x);
                    Vec3 start = position();
                    Set<UUID> hit = new HashSet<>();
                    playSound(SoundEvents.GENERIC_SPLASH, 2f, 0.5f);
                    for (int k = 1; k <= 12; k++) {
                        int step = k;
                        Scheduler.later(sl(), k, () -> {
                            if (!isAlive()) return;
                            Vec3 crest = start.add(dir.scale(step * 1.1));
                            for (int s = -3; s <= 3; s++) {
                                Vec3 p = ground(crest.x + side.x * s * 0.9, crest.z + side.z * s * 0.9, start.y);
                                sl().sendParticles(ParticleTypes.SPLASH, p.x, p.y + 0.6, p.z, 8, 0.3, 0.4, 0.3, 0.3);
                                sl().sendParticles(ParticleTypes.BUBBLE_POP, p.x, p.y + 1.2, p.z, 3, 0.3, 0.3, 0.3, 0.05);
                                if (s % 2 == 0) Fx.spike(sl(), p, Blocks.LIGHT_BLUE_STAINED_GLASS.defaultBlockState(), 0.9f, 1.4f, 0, 2, 6, false);
                            }
                            AABB box = new AABB(crest, crest).inflate(3.2, 2, 3.2);
                            for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, box, e -> e != this && !(e instanceof Drowned))) {
                                if (hit.add(e.getUUID())) {
                                    hitTarget(e, 9);
                                    e.push(dir.x * 1.6, 0.55, dir.z * 1.6);
                                    e.hurtMarked = true;
                                    e.clearFire();
                                }
                            }
                        });
                    }
                }));

        attacks.add(BossAttack.of("whirlpool").range(0, 16).cooldown(160).duration(60).weight(9)
                .onTick((b, t, i) -> {
                    Vec3 c = position();
                    double r = 2 + (i % 20) * 0.6;
                    for (int k = 0; k < 6; k++) {
                        double a = (i * 0.35) + k * Math.PI / 3;
                        sl().sendParticles(ParticleTypes.BUBBLE_COLUMN_UP, c.x + Math.cos(a) * r, c.y + 0.3, c.z + Math.sin(a) * r, 1, 0, 0, 0, 0);
                        sl().sendParticles(ParticleTypes.SPLASH, c.x + Math.cos(a) * r, c.y + 0.5, c.z + Math.sin(a) * r, 2, 0.1, 0.1, 0.1, 0);
                    }
                    for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(14), e -> e != this && !(e instanceof Drowned))) {
                        Vec3 pull = c.subtract(e.position());
                        double d = pull.length();
                        if (d < 0.5) continue;
                        Vec3 tangent = new Vec3(-pull.z, 0, pull.x).normalize().scale(0.06);
                        Vec3 v = pull.normalize().scale(0.11).add(tangent);
                        e.push(v.x, 0, v.z);
                        e.hurtMarked = true;
                        if (i % 10 == 0 && d < 3.5) hitTarget(e, 4);
                    }
                    if (i % 15 == 0) playSound(SoundEvents.BUBBLE_COLUMN_WHIRLPOOL_INSIDE, 2f, 0.7f);
                }));

        attacks.add(BossAttack.of("water_jet").phase(1).range(2, 20).cooldown(100).duration(40).weight(10)
                .onTick((b, t, i) -> {
                    if (i < 10 || i > 36) return;
                    faceTowards(t.position());
                    Vec3 from = front(1.5, 0.7);
                    Vec3 dir = t.getEyePosition().subtract(from).normalize();
                    Vec3 to = from.add(dir.scale(20));
                    Fx.line(sl(), ParticleTypes.SPLASH, from, to, 0.5);
                    Fx.line(sl(), ParticleTypes.BUBBLE_POP, from, to, 1.2);
                    if (i % 4 == 0) {
                        for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, new AABB(from, to).inflate(1.2), e -> e != this && !(e instanceof Drowned))) {
                            Vec3 rel = e.position().add(0, e.getBbHeight() / 2, 0).subtract(from);
                            double along = rel.dot(dir);
                            if (along < 0 || rel.subtract(dir.scale(along)).length() > 1.3) continue;
                            hitTarget(e, 3.5f);
                            e.push(dir.x * 0.6, 0.15, dir.z * 0.6);
                            e.hurtMarked = true;
                        }
                    }
                    if (i % 6 == 0) playSound(SoundEvents.PLAYER_SPLASH_HIGH_SPEED, 1.5f, 0.6f);
                }));
    }

    @Override
    protected void onPhaseChange(int phase) {
        if (!(level() instanceof ServerLevel s)) return;
        for (int k = 0; k < 3; k++) {
            Drowned d = EntityType.DROWNED.create(s);
            if (d == null) continue;
            double a = Math.PI * 2 * k / 3;
            Vec3 p = ground(getX() + Math.cos(a) * 4, getZ() + Math.sin(a) * 4, getY());
            d.moveTo(p.x, p.y, p.z, random.nextFloat() * 360, 0);
            d.setItemSlot(EquipmentSlot.MAINHAND, new ItemStack(Items.TRIDENT));
            d.setItemSlot(EquipmentSlot.HEAD, new ItemStack(Items.TURTLE_HELMET));
            d.setDropChance(EquipmentSlot.MAINHAND, 0f);
            d.setDropChance(EquipmentSlot.HEAD, 0f);
            d.setTarget(getTarget());
            s.addFreshEntity(d);
            s.sendParticles(ParticleTypes.SPLASH, p.x, p.y + 1, p.z, 30, 0.5, 1, 0.5, 0.3);
        }
        playSound(SoundEvents.ELDER_GUARDIAN_CURSE, 2f, 0.8f);
    }
}
