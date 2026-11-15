package com.celestialascent.boss;

import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;

import java.util.EnumSet;

/** Walks the boss towards its target unless the current attack pins it in place. */
public class BossChaseGoal extends Goal {
    private final CelestialBoss boss;
    private int repath;

    public BossChaseGoal(CelestialBoss boss) {
        this.boss = boss;
        setFlags(EnumSet.of(Flag.MOVE));
    }

    @Override
    public boolean canUse() {
        LivingEntity t = boss.getTarget();
        return t != null && t.isAlive() && !boss.inTransition();
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public void tick() {
        LivingEntity t = boss.getTarget();
        if (t == null) return;
        BossAttack a = boss.currentAttack();
        if (a != null && a.locksMovement) return;
        if (boss.distanceTo(t) < 2.5 + boss.getBbWidth() / 2) {
            boss.getNavigation().stop();
            return;
        }
        if (--repath <= 0) {
            repath = 10;
            boss.getNavigation().moveTo(t, 1.0);
        }
    }

    @Override
    public void stop() {
        boss.getNavigation().stop();
    }
}
