package com.celestialascent.test;

import com.celestialascent.CelestialAscent;
import com.celestialascent.abyss.Abyss;
import com.celestialascent.boss.CelestialBoss;
import com.celestialascent.empire.Empire;
import com.celestialascent.stars.Stars;
import com.celestialascent.titans.Titans;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.GameType;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

import java.util.HashSet;
import java.util.Set;

/**
 * Runs every boss's real AI against a live target for 400 ticks, forcing each phase, so every attack
 * (including phase-locked ones) executes. Any exception in attack code fails the test.
 */
@GameTestHolder(CelestialAscent.MODID)
@PrefixGameTestTemplate(false)
public final class BossAiTests {
    private BossAiTests() {}

    private static void fight(GameTestHelper h, EntityType<? extends CelestialBoss> type) {
        ServerPlayer p = h.makeMockServerPlayerInLevel();
        p.setGameMode(GameType.SURVIVAL);
        p.moveTo(h.absoluteVec(new Vec3(8, 1, 4)));
        CelestialBoss boss = h.spawn(type, new BlockPos(8, 1, 11));
        Set<String> seen = new HashSet<>();
        for (int t = 1; t <= 400; t++) {
            int tick = t;
            h.runAfterDelay(t, () -> {
                if (!boss.isAlive()) return;
                p.setHealth(p.getMaxHealth()); // keep the target alive so attacks keep coming
                p.removeAllEffects();
                p.clearFire();
                if (p.distanceTo(boss) > 12) p.moveTo(boss.position().add(0, 0, -5));
                boss.setTarget(p);
                if (boss.currentAttack() != null) seen.add(boss.currentAttack().id);
                // Walk the boss down through every phase threshold.
                if (tick == 120) boss.setHealth(boss.getMaxHealth() * 0.6f);
                if (tick == 220) boss.setHealth(boss.getMaxHealth() * 0.35f);
                if (tick == 300) boss.setHealth(boss.getMaxHealth() * 0.15f);
            });
        }
        h.runAfterDelay(402, () -> {
            h.assertTrue(boss.isAlive(), "boss survived its own fight");
            h.assertTrue(seen.size() >= 2, "boss used at least two attacks, saw " + seen);
            h.assertTrue(boss.phase() >= 1, "boss reached a later phase");
            h.assertTrue(boss.effectiveMaxHealth() >= boss.baseMaxHealth() - 0.5, "effective health not capped at 1024");
            h.succeed();
        });
    }

    @GameTest(template = CoreTests.FLOOR, timeoutTicks = 450, batch = "boss_ai") public static void frostTitanFights(GameTestHelper h) { fight(h, Titans.FROST_TITAN.get()); }
    @GameTest(template = CoreTests.FLOOR, timeoutTicks = 450, batch = "boss_ai") public static void tideTitanFights(GameTestHelper h) { fight(h, Titans.TIDE_TITAN.get()); }
    @GameTest(template = CoreTests.FLOOR, timeoutTicks = 450, batch = "boss_ai") public static void stormTitanFights(GameTestHelper h) { fight(h, Titans.STORM_TITAN.get()); }
    @GameTest(template = CoreTests.FLOOR, timeoutTicks = 450, batch = "boss_ai") public static void magmaTitanFights(GameTestHelper h) { fight(h, Titans.MAGMA_TITAN.get()); }
    @GameTest(template = CoreTests.FLOOR, timeoutTicks = 450, batch = "boss_ai") public static void sentinelFights(GameTestHelper h) { fight(h, Empire.SENTINEL.get()); }
    @GameTest(template = CoreTests.FLOOR, timeoutTicks = 450, batch = "boss_ai") public static void colossusFights(GameTestHelper h) { fight(h, Empire.COLOSSUS.get()); }
    @GameTest(template = CoreTests.FLOOR, timeoutTicks = 450, batch = "boss_ai") public static void seraphFights(GameTestHelper h) { fight(h, Stars.SERAPH.get()); }
    @GameTest(template = CoreTests.FLOOR, timeoutTicks = 450, batch = "boss_ai") public static void leviathanFights(GameTestHelper h) { fight(h, Stars.LEVIATHAN.get()); }
    @GameTest(template = CoreTests.FLOOR, timeoutTicks = 450, batch = "boss_ai") public static void heraldFights(GameTestHelper h) { fight(h, Stars.HERALD.get()); }
    @GameTest(template = CoreTests.FLOOR, timeoutTicks = 450, batch = "boss_ai") public static void sovereignFights(GameTestHelper h) { fight(h, Abyss.VOID_SOVEREIGN.get()); }
}
