package com.celestialascent.client;

import com.celestialascent.CelestialAscent;
import com.celestialascent.titans.Titans;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.EntityRenderersEvent;

/** Entity renderers for ladder content. */
@EventBusSubscriber(modid = CelestialAscent.MODID, value = Dist.CLIENT)
public final class ContentClient {
    private ContentClient() {}

    @SubscribeEvent
    public static void renderers(EntityRenderersEvent.RegisterRenderers e) {
        e.registerEntityRenderer(Titans.FROST_TITAN.get(), ctx -> new BossRenderer<>(ctx, "frost_titan", 1.4f));
        e.registerEntityRenderer(Titans.TIDE_TITAN.get(), ctx -> new BossRenderer<>(ctx, "tide_titan", 1.4f));
        e.registerEntityRenderer(Titans.STORM_TITAN.get(), ctx -> new BossRenderer<>(ctx, "storm_titan", 1.2f));
        e.registerEntityRenderer(Titans.MAGMA_TITAN.get(), ctx -> new BossRenderer<>(ctx, "magma_titan", 1.6f));
        e.registerEntityRenderer(com.celestialascent.empire.Empire.SENTINEL.get(), ctx -> new BossRenderer<>(ctx, "sentinel_construct", 1.0f));
        e.registerEntityRenderer(com.celestialascent.empire.Empire.COLOSSUS.get(), ctx -> new BossRenderer<>(ctx, "ender_colossus", 2.0f));
        e.registerEntityRenderer(com.celestialascent.stars.Stars.SERAPH.get(), ctx -> new BossRenderer<>(ctx, "astral_seraph", 1.2f));
        e.registerEntityRenderer(com.celestialascent.stars.Stars.LEVIATHAN.get(), ctx -> new BossRenderer<>(ctx, "nebula_leviathan", 1.2f));
        e.registerEntityRenderer(com.celestialascent.stars.Stars.HERALD.get(), ctx -> new BossRenderer<>(ctx, "sun_herald", 1.2f));
        e.registerEntityRenderer(com.celestialascent.abyss.Abyss.VOID_SOVEREIGN.get(), ctx -> new BossRenderer<>(ctx, "void_sovereign", 2.0f));
        e.registerEntityRenderer(com.celestialascent.abyss.Abyss.VOID_WRAITH.get(), VoidWraithRenderer::new);
    }
}
