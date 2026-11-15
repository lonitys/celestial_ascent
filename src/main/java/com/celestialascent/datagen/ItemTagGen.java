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
        tag(ArmorTiers.repairTag(SetId.IMPERIAL)).add(com.celestialascent.empire.Empire.IMPERIAL_PLATING.get());
        tag(ArmorTiers.repairTag(SetId.STELLAR)).add(com.celestialascent.stars.Stars.STARDUST.get());
        tag(ArmorTiers.repairTag(SetId.VOID)).add(com.celestialascent.abyss.Abyss.VOID_ESSENCE.get());
        tag(ArmorTiers.repairTag(SetId.ASCENDANT));
        java.util.List<java.util.List<net.minecraft.world.item.Item>> sets = java.util.List.of(
                java.util.List.of(Titans.HELMET.get(), Titans.CHESTPLATE.get(), Titans.LEGGINGS.get(), Titans.BOOTS.get()),
                java.util.List.of(com.celestialascent.empire.Empire.HELMET.get(), com.celestialascent.empire.Empire.CHESTPLATE.get(), com.celestialascent.empire.Empire.LEGGINGS.get(), com.celestialascent.empire.Empire.BOOTS.get()),
                java.util.List.of(com.celestialascent.stars.Stars.HELMET.get(), com.celestialascent.stars.Stars.CHESTPLATE.get(), com.celestialascent.stars.Stars.LEGGINGS.get(), com.celestialascent.stars.Stars.BOOTS.get()),
                java.util.List.of(com.celestialascent.abyss.Abyss.VOID_HELMET.get(), com.celestialascent.abyss.Abyss.VOID_CHESTPLATE.get(), com.celestialascent.abyss.Abyss.VOID_LEGGINGS.get(), com.celestialascent.abyss.Abyss.VOID_BOOTS.get()),
                java.util.List.of(com.celestialascent.abyss.Abyss.ASC_HELMET.get(), com.celestialascent.abyss.Abyss.ASC_CHESTPLATE.get(), com.celestialascent.abyss.Abyss.ASC_LEGGINGS.get(), com.celestialascent.abyss.Abyss.ASC_BOOTS.get()));
        for (var set : sets) {
            var all = set.toArray(net.minecraft.world.item.Item[]::new);
            tag(ItemTags.HEAD_ARMOR).add(set.get(0));
            tag(ItemTags.CHEST_ARMOR).add(set.get(1));
            tag(ItemTags.LEG_ARMOR).add(set.get(2));
            tag(ItemTags.FOOT_ARMOR).add(set.get(3));
            tag(ItemTags.HEAD_ARMOR_ENCHANTABLE).add(set.get(0));
            tag(ItemTags.CHEST_ARMOR_ENCHANTABLE).add(set.get(1));
            tag(ItemTags.LEG_ARMOR_ENCHANTABLE).add(set.get(2));
            tag(ItemTags.FOOT_ARMOR_ENCHANTABLE).add(set.get(3));
            tag(ItemTags.ARMOR_ENCHANTABLE).add(all);
            tag(ItemTags.DURABILITY_ENCHANTABLE).add(all);
            tag(ItemTags.EQUIPPABLE_ENCHANTABLE).add(all);
        }
    }
}
