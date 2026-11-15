package com.celestialascent.client;

import com.celestialascent.CelestialAscent;
import com.celestialascent.core.Travel;
import com.celestialascent.progress.Constellations;
import com.celestialascent.progress.ProgressSync;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.BufferBuilder;
import com.mojang.blaze3d.vertex.BufferUploader;
import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.mojang.blaze3d.vertex.MeshData;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.Tesselator;
import com.mojang.blaze3d.vertex.VertexFormat;
import com.mojang.math.Axis;
import net.minecraft.client.Camera;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.renderer.DimensionSpecialEffects;
import net.minecraft.client.renderer.GameRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.RegisterDimensionSpecialEffectsEvent;
import net.neoforged.neoforge.client.event.RenderLevelStageEvent;
import org.joml.Matrix4f;
import org.joml.Vector3f;

import java.util.List;

/** Constellations in the Overworld night sky, plus the Fallen Stars and Abyss sky effects. */
@EventBusSubscriber(modid = CelestialAscent.MODID, value = Dist.CLIENT)
public final class SkyRenderer {
    private SkyRenderer() {}

    private static final double RADIUS = 100;

    /** Unit direction for azimuth/altitude degrees in sky space (before the day-cycle rotation). */
    static Vector3f dir(float azimuth, float altitude) {
        double az = Math.toRadians(azimuth), alt = Math.toRadians(altitude);
        // Sky space is rotated by the time of day; at midnight it is upside down, so stars meant to be
        // overhead at night live in the negative-y half.
        return new Vector3f((float) (Math.cos(alt) * Math.sin(az)), (float) -Math.sin(alt), (float) (Math.cos(alt) * Math.cos(az)));
    }

    /** Camera-facing quad on the sky sphere. */
    static void star(BufferBuilder b, Matrix4f m, Vector3f d, float size, int rgb, float alpha) {
        Vector3f c = new Vector3f(d).mul((float) RADIUS);
        Vector3f up = Math.abs(d.y) > 0.9f ? new Vector3f(1, 0, 0) : new Vector3f(0, 1, 0);
        Vector3f r = new Vector3f(d).cross(up).normalize().mul(size);
        Vector3f u = new Vector3f(r).cross(d).normalize().mul(size);
        float R = ((rgb >> 16) & 255) / 255f, G = ((rgb >> 8) & 255) / 255f, B = (rgb & 255) / 255f;
        b.addVertex(m, c.x - r.x - u.x, c.y - r.y - u.y, c.z - r.z - u.z).setColor(R, G, B, alpha);
        b.addVertex(m, c.x + r.x - u.x, c.y + r.y - u.y, c.z + r.z - u.z).setColor(R, G, B, alpha);
        b.addVertex(m, c.x + r.x + u.x, c.y + r.y + u.y, c.z + r.z + u.z).setColor(R, G, B, alpha);
        b.addVertex(m, c.x - r.x + u.x, c.y - r.y + u.y, c.z - r.z + u.z).setColor(R, G, B, alpha);
    }

    /** Soft radial glow: four quads fading from the centre colour to transparent edges (no hard rim). */
    static void glow(BufferBuilder b, Matrix4f m, Vector3f d, float size, int rgb, float alpha) {
        Vector3f c = new Vector3f(d).mul((float) RADIUS);
        Vector3f up = Math.abs(d.y) > 0.9f ? new Vector3f(1, 0, 0) : new Vector3f(0, 1, 0);
        Vector3f r = new Vector3f(d).cross(up).normalize().mul(size);
        Vector3f u = new Vector3f(r).cross(d).normalize().mul(size);
        float R = ((rgb >> 16) & 255) / 255f, G = ((rgb >> 8) & 255) / 255f, B = (rgb & 255) / 255f;
        float[][] ring = {{1, 0}, {0.7f, 0.7f}, {0, 1}, {-0.7f, 0.7f}, {-1, 0}, {-0.7f, -0.7f}, {0, -1}, {0.7f, -0.7f}};
        for (int i = 0; i < 8; i += 2) {
            float[] a = ring[i], mid = ring[(i + 1) % 8], e = ring[(i + 2) % 8];
            b.addVertex(m, c.x, c.y, c.z).setColor(R, G, B, alpha);
            b.addVertex(m, c.x + r.x * a[0] + u.x * a[1], c.y + r.y * a[0] + u.y * a[1], c.z + r.z * a[0] + u.z * a[1]).setColor(R, G, B, 0f);
            b.addVertex(m, c.x + r.x * mid[0] + u.x * mid[1], c.y + r.y * mid[0] + u.y * mid[1], c.z + r.z * mid[0] + u.z * mid[1]).setColor(R, G, B, 0f);
            b.addVertex(m, c.x + r.x * e[0] + u.x * e[1], c.y + r.y * e[0] + u.y * e[1], c.z + r.z * e[0] + u.z * e[1]).setColor(R, G, B, 0f);
        }
    }

    /** Thin quad between two sky directions (a constellation line). */
    static void line(BufferBuilder b, Matrix4f m, Vector3f a, Vector3f c, float width, int rgb, float alpha) {
        Vector3f pa = new Vector3f(a).mul((float) RADIUS), pc = new Vector3f(c).mul((float) RADIUS);
        Vector3f along = new Vector3f(pc).sub(pa);
        Vector3f side = new Vector3f(along).cross(new Vector3f(pa).add(pc).normalize()).normalize().mul(width);
        float R = ((rgb >> 16) & 255) / 255f, G = ((rgb >> 8) & 255) / 255f, B = (rgb & 255) / 255f;
        b.addVertex(m, pa.x - side.x, pa.y - side.y, pa.z - side.z).setColor(R, G, B, alpha);
        b.addVertex(m, pc.x - side.x, pc.y - side.y, pc.z - side.z).setColor(R, G, B, alpha);
        b.addVertex(m, pc.x + side.x, pc.y + side.y, pc.z + side.z).setColor(R, G, B, alpha);
        b.addVertex(m, pa.x + side.x, pa.y + side.y, pa.z + side.z).setColor(R, G, B, alpha);
    }

    static void beginAdditive() {
        RenderSystem.enableBlend();
        RenderSystem.blendFunc(com.mojang.blaze3d.platform.GlStateManager.SourceFactor.SRC_ALPHA, com.mojang.blaze3d.platform.GlStateManager.DestFactor.ONE);
        RenderSystem.depthMask(false);
        RenderSystem.disableCull();
        RenderSystem.setShader(GameRenderer::getPositionColorShader);
    }

    static void end() {
        RenderSystem.depthMask(true);
        RenderSystem.enableCull();
        RenderSystem.defaultBlendFunc();
        RenderSystem.disableBlend();
    }

    @SubscribeEvent
    public static void afterSky(RenderLevelStageEvent e) {
        if (e.getStage() != RenderLevelStageEvent.Stage.AFTER_SKY) return;
        ClientLevel level = Minecraft.getInstance().level;
        if (level == null || level.dimension() != Level.OVERWORLD) return;
        List<ResourceLocation> kills = ProgressSync.clientKills;
        if (kills.isEmpty()) return;
        float pt = e.getPartialTick().getGameTimeDeltaPartialTick(false);
        float brightness = level.getStarBrightness(pt) * (1.0f - level.getRainLevel(pt)) * 1.6f;
        if (brightness <= 0.02f) return;

        PoseStack pose = new PoseStack();
        pose.mulPose(e.getModelViewMatrix());
        pose.mulPose(Axis.YP.rotationDegrees(-90.0F));
        pose.mulPose(Axis.XP.rotationDegrees(level.getTimeOfDay(pt) * 360.0F));
        Matrix4f m = pose.last().pose();

        beginAdditive();
        BufferBuilder b = Tesselator.getInstance().begin(VertexFormat.Mode.QUADS, DefaultVertexFormat.POSITION_COLOR);
        long t = level.getGameTime();
        for (Constellations.Entry c : Constellations.ALL) {
            if (!kills.contains(c.boss())) continue;
            Vector3f[] dirs = new Vector3f[c.stars().length];
            for (int i = 0; i < dirs.length; i++) dirs[i] = dir(c.stars()[i][0], c.stars()[i][1]);
            for (int[] l : c.lines()) line(b, m, dirs[l[0]], dirs[l[1]], 0.12f, c.color(), 0.35f * brightness);
            for (int i = 0; i < dirs.length; i++) {
                float tw = 0.8f + 0.2f * (float) Math.sin((t + i * 37) / 9.0);
                star(b, m, dirs[i], 0.9f, c.color(), 0.35f * brightness);
                star(b, m, dirs[i], 0.42f * tw, 0xFFFFFF, Math.min(1f, brightness));
            }
        }
        MeshData mesh = b.build();
        if (mesh != null) BufferUploader.drawWithShader(mesh);
        end();
    }

    @SubscribeEvent
    public static void effects(RegisterDimensionSpecialEffectsEvent e) {
        e.register(Travel.FALLEN_STARS.location(), new FallenStarsEffects());
        e.register(Travel.ABYSS.location(), new AbyssEffects());
    }

    /** Endless star field with drifting nebula clouds. */
    static final class FallenStarsEffects extends DimensionSpecialEffects {
        private static final int STARS = 2200;
        private final float[] az = new float[STARS], alt = new float[STARS], size = new float[STARS];
        private final int[] color = new int[STARS];

        FallenStarsEffects() {
            super(Float.NaN, false, SkyType.NONE, false, false);
            RandomSource r = RandomSource.create(4242L);
            int[] palette = {0xFFFFFF, 0xBFD8FF, 0xFFE9C4, 0xD9C2FF, 0x9FE8FF, 0xFFC0E8};
            for (int i = 0; i < STARS; i++) {
                az[i] = r.nextFloat() * 360f;
                alt[i] = (float) Math.toDegrees(Math.asin(r.nextFloat() * 2 - 1));
                size[i] = 0.12f + r.nextFloat() * r.nextFloat() * 0.7f;
                color[i] = palette[r.nextInt(palette.length)];
            }
        }

        @Override
        public Vec3 getBrightnessDependentFogColor(Vec3 fog, float brightness) {
            return fog.scale(0.6);
        }

        @Override
        public boolean isFoggyAt(int x, int z) {
            return false;
        }

        @Override
        public boolean renderSky(ClientLevel level, int ticks, float partialTick, Matrix4f modelView, Camera camera,
                                 Matrix4f projection, boolean isFoggy, Runnable setupFog) {
            PoseStack pose = new PoseStack();
            pose.mulPose(modelView);
            pose.mulPose(Axis.YP.rotationDegrees((ticks + partialTick) * 0.004f));
            Matrix4f m = pose.last().pose();
            beginAdditive();
            BufferBuilder b = Tesselator.getInstance().begin(VertexFormat.Mode.QUADS, DefaultVertexFormat.POSITION_COLOR);
            // Nebulae: large faint overlapping glows.
            int[][] neb = {{40, 20, 0x5A2CA0}, {70, 35, 0x2C5AA0}, {200, -10, 0xA02C7A}, {260, 50, 0x2CA08E}, {330, 5, 0x6B2CA0}, {150, -40, 0x2C3FA0}};
            for (int[] n : neb) {
                for (int k = 0; k < 5; k++) glow(b, m, dir(n[0] + k * 5f, n[1] + (k % 3) * 4f - 4f), 26f + k * 6f, n[2], 0.16f);
            }
            float time = ticks + partialTick;
            for (int i = 0; i < STARS; i++) {
                float tw = 0.65f + 0.35f * (float) Math.sin(time / (6f + (i % 7)) + i);
                star(b, m, dir(az[i], alt[i]), size[i], color[i], Math.min(1f, 0.55f + size[i]) * tw);
            }
            MeshData mesh = b.build();
            if (mesh != null) BufferUploader.drawWithShader(mesh);
            end();
            return true;
        }
    }

    /** Lightless depths: no sky, thick violet-black fog. */
    static final class AbyssEffects extends DimensionSpecialEffects {
        AbyssEffects() {
            super(Float.NaN, false, SkyType.NONE, false, true);
        }

        @Override
        public Vec3 getBrightnessDependentFogColor(Vec3 fog, float brightness) {
            return fog.scale(0.2);
        }

        @Override
        public boolean isFoggyAt(int x, int z) {
            return true;
        }
    }
}
