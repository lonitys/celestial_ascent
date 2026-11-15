package com.celestialascent.armor.client;

import com.celestialascent.CelestialAscent;
import com.celestialascent.armor.CelestialArmorItem;
import com.celestialascent.armor.SetId;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.DefaultedItemGeoModel;
import software.bernie.geckolib.renderer.GeoArmorRenderer;
import software.bernie.geckolib.renderer.layer.AutoGlowingGeoLayer;

/** 3D armor renderer. Texture variant comes from the piece being rendered (e.g. titan element). */
public class CelestialArmorRenderer extends GeoArmorRenderer<CelestialArmorItem> {
    private final SetId set;

    public CelestialArmorRenderer(SetId set) {
        super(new DefaultedItemGeoModel<>(ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "armor/" + set.key + "_armor")));
        this.set = set;
        addRenderLayer(new AutoGlowingGeoLayer<>(this));
    }

    @Override
    public ResourceLocation getTextureLocation(CelestialArmorItem item) {
        String variant = currentStack == null ? "" : item.textureVariant(currentStack);
        return ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID,
                "textures/item/armor/" + set.key + "_armor" + variant + ".png");
    }
}
