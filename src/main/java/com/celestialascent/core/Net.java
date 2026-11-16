package com.celestialascent.core;

import com.celestialascent.CelestialAscent;
import com.celestialascent.armor.AbilityKey;
import com.celestialascent.progress.ProgressSync;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.network.event.RegisterPayloadHandlersEvent;
import net.neoforged.neoforge.network.registration.PayloadRegistrar;

@EventBusSubscriber(modid = CelestialAscent.MODID)
public final class Net {
    private Net() {}

    @SubscribeEvent
    public static void register(RegisterPayloadHandlersEvent e) {
        PayloadRegistrar r = e.registrar("1");
        r.playToClient(ProgressSync.TYPE, ProgressSync.STREAM_CODEC, ProgressSync::handle);
        r.playToServer(AbilityKey.TYPE, AbilityKey.STREAM_CODEC, AbilityKey::handle);
        r.playToClient(com.celestialascent.boss.BossStagePayload.TYPE, com.celestialascent.boss.BossStagePayload.STREAM_CODEC,
                com.celestialascent.boss.BossStagePayload::handle);
    }
}
