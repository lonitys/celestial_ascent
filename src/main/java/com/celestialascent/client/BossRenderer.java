package com.celestialascent.client;

import com.mojang.blaze3d.vertex.PoseStack;
import software.bernie.geckolib.cache.object.BakedGeoModel;

import com.celestialascent.CelestialAscent;
import com.celestialascent.boss.CelestialBoss;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.DefaultedEntityGeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import software.bernie.geckolib.renderer.layer.AutoGlowingGeoLayer;

/**
 * Renderer for any Celestial boss: geo/entity/&lt;name&gt;.geo.json, textures/entity/&lt;name&gt;.png
 * (+ _glowmask), animations/entity/&lt;name&gt;.animation.json. The "head" bone tracks the look direction.
 */
public class BossRenderer<T extends CelestialBoss> extends GeoEntityRenderer<T> {
    /** Texture per stage: &lt;name&gt;.png, &lt;name&gt;_stage2.png, &lt;name&gt;_stage3.png (tools/art/bosses/gen_stages.py). */
    private final ResourceLocation[] stageTextures;

    public BossRenderer(EntityRendererProvider.Context ctx, String name, float shadow) {
        super(ctx, new DefaultedEntityGeoModel<>(ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, name), true));
        this.shadowRadius = shadow;
        addRenderLayer(new AutoGlowingGeoLayer<>(this)); // glow masks follow the stage texture (<texture>_glowmask.png)
        this.stageTextures = new ResourceLocation[]{
                ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "textures/entity/" + name + ".png"),
                ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "textures/entity/" + name + "_stage2.png"),
                ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "textures/entity/" + name + "_stage3.png")};
    }

    @Override
    public ResourceLocation getTextureLocation(T animatable) {
        return stageTextures[Math.min(2, Math.max(0, animatable.phase()))];
    }

    /** Bosses grow a little with every stage. */
    @Override
    public void scaleModelForRender(float widthScale, float heightScale, PoseStack poseStack, T animatable, BakedGeoModel model,
                                    boolean isReRender, float partialTick, int packedLight, int packedOverlay) {
        float s = animatable.stageScale(partialTick);
        super.scaleModelForRender(widthScale * s, heightScale * s, poseStack, animatable, model, isReRender, partialTick, packedLight, packedOverlay);
    }

    @Override
    protected float getDeathMaxRotation(T animatable) {
        return 0f; // the model's own death animation plays instead of the vanilla tip-over
    }
}
