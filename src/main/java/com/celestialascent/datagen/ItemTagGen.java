package com.celestialascent.datagen;

import com.celestialascent.CelestialAscent;
import com.celestialascent.armor.ArmorTiers;
import com.celestialascent.armor.SetId;
import com.celestialascent.titans.Titans;
import net.minecraft.core.HolderLookup;
import net.minecraft.data.PackOutput;
import net.minecraft.data.tags.ItemTagsProvider;
import net.minecraft.tags.ItemTags;
import net.minecraft.world.level.block.Block;
import net.neoforged.neoforge.common.data.ExistingFileHelper;

import java.util.concurrent.CompletableFuture;

public class ItemTagGen extends ItemTagsProvider {
    public ItemTagGen(PackOutput out, CompletableFuture<HolderLookup.Provider> lookup,
                      CompletableFuture<TagLookup<Block>> blockTags, ExistingFileHelper files) {
        super(out, lookup, blockTags, CelestialAscent.MODID, files);
    }

    @Override
    protected void addTags(HolderLookup.Provider lookup) {
        tag(ArmorTiers.repairTag(SetId.TITAN)).add(Titans.TITAN_SHARD.get());
        for (SetId s : SetId.values()) tag(ArmorTiers.repairTag(s));
        tag(ItemTags.HEAD_ARMOR).add(Titans.HELMET.get());
        tag(ItemTags.CHEST_ARMOR).add(Titans.CHESTPLATE.get());
        tag(ItemTags.LEG_ARMOR).add(Titans.LEGGINGS.get());
        tag(ItemTags.FOOT_ARMOR).add(Titans.BOOTS.get());
        tag(ItemTags.TRIMMABLE_ARMOR).add(Titans.HELMET.get(), Titans.CHESTPLATE.get(), Titans.LEGGINGS.get(), Titans.BOOTS.get());
    }
}
