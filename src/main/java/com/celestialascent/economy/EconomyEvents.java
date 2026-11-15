package com.celestialascent.economy;

import com.celestialascent.CelestialAscent;
import net.minecraft.server.level.ServerLevel;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.entity.player.TradeWithVillagerEvent;

/** Trading with villagers makes their village more prosperous. */
@EventBusSubscriber(modid = CelestialAscent.MODID)
public final class EconomyEvents {
    private EconomyEvents() {}

    @SubscribeEvent
    public static void trade(TradeWithVillagerEvent e) {
        if (e.getAbstractVillager().level() instanceof ServerLevel sl) {
            VillageGrowth.addProsperity(sl, e.getAbstractVillager().blockPosition(), 3, null);
        }
    }
}
