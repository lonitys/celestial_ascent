package com.celestialascent.client;

import com.celestialascent.CelestialAscent;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.VexRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.monster.Vex;

/** Void Wraith uses the vex body with its own spectral texture. */
public class VoidWraithRenderer extends VexRenderer {
    private static final ResourceLocation TEX = ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "textures/entity/void_wraith.png");

    public VoidWraithRenderer(EntityRendererProvider.Context ctx) {
        super(ctx);
    }

    @Override
    public ResourceLocation getTextureLocation(Vex entity) {
        return TEX;
    }
}
