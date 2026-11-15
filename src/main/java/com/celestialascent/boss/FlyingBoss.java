package com.celestialascent.boss;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/** A boss that flies: circles its target at a hover height and steers directly (no pathfinding). */
public abstract class FlyingBoss extends CelestialBoss {
    protected FlyingBoss(EntityType<? extends Monster> type, Level level) {
        super(type, level);
        setNoGravity(true);
    }

    /** Height above the target to hover at. */
    protected double hoverHeight() { return 6; }

    /** Radius of the circle flown around the target. */
    protected double orbitRadius() { return 9; }

    protected double flySpeed() { return 0.45; }

    @Override
    protected boolean canFlyToTarget() { return true; }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 48f));
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, false));
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        LivingEntity t = getTarget();
        BossAttack a = currentAttack();
        if (inTransition() || (a != null && a.locksMovement)) {
            setDeltaMovement(getDeltaMovement().scale(0.6));
            return;
        }
        if (t == null) {
            setDeltaMovement(getDeltaMovement().scale(0.8).add(0, Math.sin(tickCount / 20.0) * 0.01, 0));
            return;
        }
        double angle = tickCount / 40.0;
        Vec3 desired = t.position().add(Math.cos(angle) * orbitRadius(), hoverHeight() + Math.sin(tickCount / 25.0), Math.sin(angle) * orbitRadius());
        Vec3 to = desired.subtract(position());
        Vec3 want = to.lengthSqr() > 1 ? to.normalize().scale(flySpeed()) : to.scale(0.3);
        setDeltaMovement(getDeltaMovement().scale(0.85).add(want.scale(0.15)));
        getLookControl().setLookAt(t, 30f, 30f);
        faceTowards(t.position());
    }

    @Override
    public void travel(Vec3 input) {
        move(net.minecraft.world.entity.MoverType.SELF, getDeltaMovement());
        setDeltaMovement(getDeltaMovement().scale(0.91));
    }
}
