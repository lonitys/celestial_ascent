package com.celestialascent.client;

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
    public BossRenderer(EntityRendererProvider.Context ctx, String name, float shadow) {
        super(ctx, new DefaultedEntityGeoModel<>(ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, name), true));
        this.shadowRadius = shadow;
        addRenderLayer(new AutoGlowingGeoLayer<>(this));
    }

    @Override
    protected float getDeathMaxRotation(T animatable) {
        return 0f; // the model's own death animation plays instead of the vanilla tip-over
    }
}
