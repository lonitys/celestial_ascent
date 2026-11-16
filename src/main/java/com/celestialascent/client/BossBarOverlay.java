package com.celestialascent.client;

import com.celestialascent.CelestialAscent;
import com.celestialascent.boss.BossStagePayload;
import com.celestialascent.boss.CelestialBoss;
import com.mojang.blaze3d.systems.RenderSystem;
import net.minecraft.ChatFormatting;
import net.minecraft.Util;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.ClientPlayerNetworkEvent;
import net.neoforged.neoforge.client.event.CustomizeGuiOverlayEvent;
import net.neoforged.neoforge.client.event.RegisterGuiLayersEvent;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * The boss bar for Celestial bosses (replacing the vanilla one): an ornate frame in the boss's colour,
 * threshold notches at the stage changes, a trail of recently lost health, three stage gems and the
 * stage name. When a boss evolves the bar flashes and a large stage banner slides in.
 */
@EventBusSubscriber(modid = CelestialAscent.MODID, value = Dist.CLIENT)
public final class BossBarOverlay {
    private BossBarOverlay() {}

    private static final ResourceLocation TEX = ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "textures/gui/boss_bar.png");
    private static final int TW = 256, TH = 64;
    private static final int FRAME_W = 206, FRAME_H = 14, FILL_W = 200, FILL_H = 8;
    private static final int GOLD = 0xE6C25A;

    private record Info(ResourceLocation boss, int stage, int color, long changedAt) {}

    private static final Map<UUID, Info> BARS = new HashMap<>();
    /** Health shown by the lagging trail, per bar. */
    private static final Map<UUID, Float> TRAIL = new HashMap<>();

    private static Component bannerBoss, bannerStage;
    private static int bannerNumber, bannerColor;
    private static long bannerStart = Long.MIN_VALUE / 2;

    public static void accept(BossStagePayload m) {
        long now = Util.getMillis();
        Info old = BARS.get(m.bar());
        boolean changed = m.announce() || (old != null && old.stage() != m.stage());
        BARS.put(m.bar(), new Info(m.boss(), m.stage(), m.color(), changed ? now : old == null ? Long.MIN_VALUE / 2 : old.changedAt()));
        if (m.announce()) {
            bannerBoss = Component.translatable("entity." + m.boss().getNamespace() + "." + m.boss().getPath());
            bannerStage = Component.translatable("boss." + m.boss().getNamespace() + "." + m.boss().getPath() + ".stage" + (m.stage() + 1));
            bannerNumber = m.stage() + 1;
            bannerColor = m.color();
            bannerStart = now;
            Minecraft.getInstance().getSoundManager().play(SimpleSoundInstance.forUI(SoundEvents.ELDER_GUARDIAN_CURSE, 0.8f, 0.5f));
        }
    }

    @SubscribeEvent
    public static void loggedOut(ClientPlayerNetworkEvent.LoggingOut e) {
        BARS.clear();
        TRAIL.clear();
        bannerStage = null;
    }

    private static String roman(int n) {
        return n == 1 ? "I" : n == 2 ? "II" : "III";
    }

    private static void tint(GuiGraphics g, int rgb, float alpha) {
        g.setColor(((rgb >> 16) & 255) / 255f, ((rgb >> 8) & 255) / 255f, (rgb & 255) / 255f, alpha);
    }

    // ------------------------------------------------------------------ the bar

    @SubscribeEvent
    public static void bossBar(CustomizeGuiOverlayEvent.BossEventProgress e) {
        Info info = BARS.get(e.getBossEvent().getId());
        if (info == null) return;
        e.setCanceled(true);
        e.setIncrement(40);
        GuiGraphics g = e.getGuiGraphics();
        Font font = Minecraft.getInstance().font;
        int cx = e.getWindow().getGuiScaledWidth() / 2, x = cx - FRAME_W / 2, y = e.getY();
        long now = Util.getMillis();
        float flash = Math.max(0, 1 - (now - info.changedAt()) / 900f);
        float progress = e.getBossEvent().getProgress();
        float trail = TRAIL.getOrDefault(e.getBossEvent().getId(), progress);
        trail = trail > progress ? trail + (progress - trail) * 0.04f : progress;
        TRAIL.put(e.getBossEvent().getId(), trail);

        Component name = Component.translatable("entity." + info.boss().getNamespace() + "." + info.boss().getPath()).withStyle(ChatFormatting.BOLD);
        g.drawString(font, name, cx - font.width(name) / 2, y - 10, info.color(), true);

        RenderSystem.enableBlend();
        g.blit(TEX, x, y, 0, 0, FRAME_W, FRAME_H, TW, TH);
        int filled = Math.round(FILL_W * progress), trailW = Math.round(FILL_W * trail) - filled;
        if (trailW > 0) {
            g.setColor(1f, 1f, 1f, 0.7f);
            g.blit(TEX, x + 3 + filled, y + 3, filled, 24, trailW, FILL_H, TW, TH);
        }
        tint(g, info.color(), 1f);
        g.blit(TEX, x + 3, y + 3, 0, 16, filled, FILL_H, TW, TH);
        g.setColor(1f, 1f, 1f, 1f);
        for (float t : CelestialBoss.STAGES) g.blit(TEX, x + 3 + Math.round(FILL_W * t) - 1, y + 2, 36, 34, 3, 10, TW, TH);
        if (flash > 0) g.fill(x + 3, y + 3, x + 3 + FILL_W, y + 3 + FILL_H, ((int) (flash * 220) << 24) | 0xFFFFFF);

        // Stage gems and the stage name.
        Component stageName = info.stage() == 0 ? null
                : Component.translatable("boss." + info.boss().getNamespace() + "." + info.boss().getPath() + ".stage" + (info.stage() + 1));
        int textW = stageName == null ? 0 : font.width(stageName) + 6;
        int rowW = 3 * 11 + 2 * 3 + textW, rx = cx - rowW / 2, ry = y + FRAME_H + 2;
        for (int i = 0; i < 3; i++) {
            int gx = rx + i * 14;
            boolean lit = i <= info.stage();
            if (!lit) {
                g.blit(TEX, gx, ry, 0, 34, 11, 11, TW, TH);
                continue;
            }
            boolean newest = i == info.stage() && flash > 0;
            g.pose().pushPose();
            if (newest) {
                float s = 1 + 0.6f * flash;
                g.pose().translate(gx + 5.5f, ry + 5.5f, 0);
                g.pose().scale(s, s, 1);
                g.pose().translate(-(gx + 5.5f), -(ry + 5.5f), 0);
            }
            tint(g, info.color(), 1f);
            g.blit(TEX, gx, ry, 12, 34, 11, 11, TW, TH);
            g.setColor(1f, 1f, 1f, 1f);
            g.blit(TEX, gx, ry, 24, 34, 11, 11, TW, TH);
            g.pose().popPose();
        }
        if (stageName != null) g.drawString(font, stageName, rx + 3 * 14 + 4, ry + 2, 0xE8E8E8, true);
        RenderSystem.disableBlend();
    }

    // ------------------------------------------------------------------ the stage banner

    @SubscribeEvent
    public static void layers(RegisterGuiLayersEvent e) {
        e.registerAboveAll(ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "stage_banner"), BossBarOverlay::banner);
    }

    private static void banner(GuiGraphics g, DeltaTracker delta) {
        if (bannerStage == null) return;
        long age = Util.getMillis() - bannerStart;
        if (age < 0 || age > 4400) return;
        float in = Math.min(1, age / 450f), out = age > 3500 ? Math.max(0, 1 - (age - 3500) / 900f) : 1;
        float a = Math.min(in, out);
        if (a <= 0.02f) return;
        Font font = Minecraft.getInstance().font;
        int w = g.guiWidth(), h = g.guiHeight(), c = bannerColor & 0xFFFFFF;

        // The screen edges pulse in the boss's colour.
        float pulse = (float) (0.65 + 0.35 * Math.sin(age / 140.0));
        int edge = Math.max(4, (int) (a * pulse * 110));
        g.fillGradient(0, 0, w, h / 5, (edge << 24) | c, c);
        g.fillGradient(0, h - h / 5, w, h, c, (edge << 24) | c);

        float ease = 1 - (1 - in) * (1 - in);
        int cy = (int) (h * 0.26f - (1 - ease) * 24);

        // A dark band that fades out toward the sides.
        int bandHalf = Math.min(w / 2, 190);
        for (int i = 0; i < bandHalf; i += 2) {
            int alpha = (int) (a * 150 * (1 - (float) i / bandHalf));
            g.fill(w / 2 - i - 2, cy - 28, w / 2 - i, cy + 38, alpha << 24);
            g.fill(w / 2 + i, cy - 28, w / 2 + i + 2, cy + 38, alpha << 24);
        }

        int ta = Math.max(4, (int) (a * 255)) << 24;
        Component stage = Component.translatable("boss.celestialascent.banner", roman(bannerNumber)).withStyle(ChatFormatting.BOLD);
        int stageW = font.width(stage) * 3;
        g.pose().pushPose();
        g.pose().translate(w / 2f, cy - 12, 0);
        g.pose().scale(3, 3, 1);
        g.drawString(font, stage, -font.width(stage) / 2, 0, ta | c, true);
        g.pose().popPose();

        // Gold lines either side of the stage number.
        int lineY = cy + 1, gap = stageW / 2 + 10, len = 70;
        g.fill(w / 2 - gap - len, lineY, w / 2 - gap, lineY + 1, ta | GOLD);
        g.fill(w / 2 + gap, lineY, w / 2 + gap + len, lineY + 1, ta | GOLD);

        g.pose().pushPose();
        g.pose().translate(w / 2f, cy + 16, 0);
        g.pose().scale(2, 2, 1);
        g.drawString(font, bannerStage, -font.width(bannerStage) / 2, 0, ta | 0xF4F4F4, true);
        g.pose().popPose();
        g.drawString(font, bannerBoss, w / 2 - font.width(bannerBoss) / 2, cy - 25, ta | 0xB8B8B8, true);
    }
}
