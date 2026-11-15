package com.celestialascent.client;

import com.celestialascent.CelestialAscent;
import com.celestialascent.armor.AbilityKey;
import com.celestialascent.economy.Economy;
import com.mojang.blaze3d.platform.InputConstants;
import net.minecraft.client.KeyMapping;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.client.event.EntityRenderersEvent;
import net.neoforged.neoforge.client.event.RegisterKeyMappingsEvent;
import net.neoforged.neoforge.client.event.RegisterMenuScreensEvent;
import net.neoforged.neoforge.network.PacketDistributor;
import org.lwjgl.glfw.GLFW;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

@EventBusSubscriber(modid = CelestialAscent.MODID, value = Dist.CLIENT)
public final class ClientSetup {
    private ClientSetup() {}

    public static final KeyMapping ABILITY = new KeyMapping("key.celestialascent.ability", InputConstants.Type.KEYSYM,
            GLFW.GLFW_KEY_H, "key.categories.celestialascent");
    public static final KeyMapping TOGGLE = new KeyMapping("key.celestialascent.toggle", InputConstants.Type.KEYSYM,
            GLFW.GLFW_KEY_G, "key.categories.celestialascent");

    @SubscribeEvent
    public static void keys(RegisterKeyMappingsEvent e) {
        e.register(ABILITY);
        e.register(TOGGLE);
    }

    @SubscribeEvent
    public static void screens(RegisterMenuScreensEvent e) {
        e.register(Economy.BANK_MENU.get(), BankScreen::new);
        e.register(Economy.SHOP_MENU.get(), ShopScreen::new);
        e.register(com.celestialascent.core.station.Stations.MENU.get(), StationScreen::new);
        e.register(Economy.QUEST_MENU.get(), QuestScreen::new);
    }

    @SubscribeEvent
    public static void renderers(EntityRenderersEvent.RegisterRenderers e) {
        e.registerBlockEntityRenderer(Economy.SHOP_STALL_BE.get(), ShopStallRenderer::new);
        e.registerBlockEntityRenderer(com.celestialascent.titans.Titans.ALTAR_BE.get(), FloatingRenderer::new);
        e.registerBlockEntityRenderer(com.celestialascent.boss.SummonAltarBlock.BE.get(), FloatingRenderer::new);
        e.registerBlockEntityRenderer(com.celestialascent.empire.Empire.PYLON_BE.get(), FloatingRenderer::new);
        e.registerBlockEntityRenderer(com.celestialascent.core.station.Stations.BE.get(), FloatingRenderer::new);
        e.registerBlockEntityRenderer(com.celestialascent.core.DisplayBlockEntity.TYPE.get(), FloatingRenderer::new);
    }

    @SubscribeEvent
    public static void models(net.neoforged.neoforge.client.event.ModelEvent.RegisterAdditional e) {
        FloatingRenderer.models().forEach(e::register);
    }

    @EventBusSubscriber(modid = CelestialAscent.MODID, value = Dist.CLIENT)
    public static final class GameEvents {
        private GameEvents() {}

        @SubscribeEvent
        public static void tick(ClientTickEvent.Post e) {
            while (ABILITY.consumeClick()) PacketDistributor.sendToServer(new AbilityKey(0));
            while (TOGGLE.consumeClick()) PacketDistributor.sendToServer(new AbilityKey(1));
        }
    }
}
