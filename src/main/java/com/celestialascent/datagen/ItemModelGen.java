package com.celestialascent.datagen;

import com.celestialascent.CelestialAscent;
import com.celestialascent.core.Content;
import com.celestialascent.stars.Stars;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.data.PackOutput;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.neoforge.client.model.generators.ItemModelProvider;
import net.neoforged.neoforge.common.data.ExistingFileHelper;

public class ItemModelGen extends ItemModelProvider {
    public ItemModelGen(PackOutput out, ExistingFileHelper files) {
        super(out, CelestialAscent.MODID, files);
    }

    @Override
    protected void registerModels() {
        for (var item : Content.FLAT_ITEMS) {
            ResourceLocation id = BuiltInRegistries.ITEM.getKey(item.get());
            if (BlockStateGen.LENIENT && !existingFileHelper.exists(modLoc("item/" + id.getPath()), net.minecraft.server.packs.PackType.CLIENT_RESOURCES, ".png", "textures")) continue;
            basicItem(item.get());
        }
        for (var block : Content.BLOCKS) {
            ResourceLocation id = BuiltInRegistries.BLOCK.getKey(block.get());
            if (BlockStateGen.SKIPPED.contains(id.getPath())) continue;
            if (block.get() == Stars.STAR_CRYSTAL.get()) {
                withExistingParent(id.getPath(), mcLoc("item/generated")).texture("layer0", modLoc("block/" + id.getPath()));
            } else {
                withExistingParent(id.getPath(), modLoc("block/" + id.getPath()));
            }
        }
    }
}
