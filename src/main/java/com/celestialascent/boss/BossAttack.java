package com.celestialascent.boss;

import net.minecraft.world.entity.LivingEntity;

/**
 * One boss attack. Built fluently, e.g.
 * {@code BossAttack.of("slam").phase(0).cooldown(80).duration(40).range(0, 6).onTick((b, t, i) -> ...)}.
 * The attack's id is also the name of its triggerable animation ("attack.&lt;id&gt;").
 */
public final class BossAttack {
    @FunctionalInterface
    public interface Tick {
        void run(CelestialBoss boss, LivingEntity target, int tick);
    }

    @FunctionalInterface
    public interface Check {
        boolean test(CelestialBoss boss, LivingEntity target);
    }

    public final String id;
    int minPhase = 0;
    int maxPhase = Integer.MAX_VALUE;
    int cooldown = 60;
    int duration = 20;
    int weight = 10;
    double minRange = 0;
    double maxRange = 64;
    boolean locksMovement = true;
    boolean animated = true;
    Check extra = (b, t) -> true;
    Tick onStart = (b, t, i) -> {};
    Tick onTick = (b, t, i) -> {};
    Tick onEnd = (b, t, i) -> {};

    private BossAttack(String id) {
        this.id = id;
    }

    public static BossAttack of(String id) {
        return new BossAttack(id);
    }

    public BossAttack phase(int min) { this.minPhase = min; return this; }
    public BossAttack phases(int min, int max) { this.minPhase = min; this.maxPhase = max; return this; }
    public BossAttack cooldown(int ticks) { this.cooldown = ticks; return this; }
    public BossAttack duration(int ticks) { this.duration = ticks; return this; }
    public BossAttack weight(int w) { this.weight = w; return this; }
    public BossAttack range(double min, double max) { this.minRange = min; this.maxRange = max; return this; }
    public BossAttack mobile() { this.locksMovement = false; return this; }
    public BossAttack noAnimation() { this.animated = false; return this; }
    public BossAttack when(Check c) { this.extra = c; return this; }
    public BossAttack onStart(Tick t) { this.onStart = t; return this; }
    public BossAttack onTick(Tick t) { this.onTick = t; return this; }
    public BossAttack onEnd(Tick t) { this.onEnd = t; return this; }

    boolean usable(CelestialBoss boss, LivingEntity target, int phase) {
        if (phase < minPhase || phase > maxPhase) return false;
        double d = boss.distanceTo(target);
        return d >= minRange && d <= maxRange && extra.test(boss, target);
    }
}
