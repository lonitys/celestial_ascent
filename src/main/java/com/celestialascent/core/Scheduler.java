package com.celestialascent.core;

import com.celestialascent.CelestialAscent;
import net.minecraft.server.level.ServerLevel;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.server.ServerStoppedEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

/** Runs tasks a number of server ticks in the future (attack wind-ups, effect cleanup). */
@EventBusSubscriber(modid = CelestialAscent.MODID)
public final class Scheduler {
    private Scheduler() {}

    private record Task(ServerLevel level, long at, Runnable run) {}

    private static final List<Task> TASKS = new ArrayList<>();
    private static final List<Task> PENDING = new ArrayList<>();

    public static void later(ServerLevel level, int delayTicks, Runnable run) {
        synchronized (PENDING) {
            PENDING.add(new Task(level, level.getGameTime() + Math.max(1, delayTicks), run));
        }
    }

    @SubscribeEvent
    public static void tick(ServerTickEvent.Post e) {
        synchronized (PENDING) {
            TASKS.addAll(PENDING);
            PENDING.clear();
        }
        Iterator<Task> it = TASKS.iterator();
        while (it.hasNext()) {
            Task t = it.next();
            if (t.level.getGameTime() >= t.at) {
                it.remove();
                try {
                    t.run.run();
                } catch (RuntimeException ex) {
                    org.slf4j.LoggerFactory.getLogger(CelestialAscent.MODID).error("Scheduled task failed", ex);
                }
            }
        }
    }

    @SubscribeEvent
    public static void stopped(ServerStoppedEvent e) {
        TASKS.clear();
        synchronized (PENDING) {
            PENDING.clear();
        }
    }
}
