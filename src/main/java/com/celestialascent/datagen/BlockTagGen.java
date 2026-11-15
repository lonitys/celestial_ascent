package com.celestialascent.datagen;

import com.celestialascent.CelestialAscent;
import com.celestialascent.economy.Economy;
import com.celestialascent.titans.Titans;
import net.minecraft.core.HolderLookup;
import net.minecraft.data.PackOutput;
import net.minecraft.tags.BlockTags;
import net.neoforged.neoforge.common.data.BlockTagsProvider;
import net.neoforged.neoforge.common.data.ExistingFileHelper;

import java.util.concurrent.CompletableFuture;

public class BlockTagGen extends BlockTagsProvider {
    public BlockTagGen(PackOutput out, CompletableFuture<HolderLookup.Provider> lookup, ExistingFileHelper files) {
        super(out, lookup, CelestialAscent.MODID, files);
    }

    @Override
    protected void addTags(HolderLookup.Provider lookup) {
        tag(BlockTags.MINEABLE_WITH_AXE).add(Economy.BANK_COUNTER.get(), Economy.SHOP_STALL.get());
        tag(BlockTags.MINEABLE_WITH_PICKAXE).add(Economy.TITAN_ANVIL.get(), Economy.RELIC_PEDESTAL.get(), Titans.TITAN_FORGE.get());
        tag(BlockTags.NEEDS_IRON_TOOL).add(Economy.TITAN_ANVIL.get(), Economy.RELIC_PEDESTAL.get());
        tag(BlockTags.NEEDS_DIAMOND_TOOL).add(Titans.TITAN_FORGE.get());
        Titans.ALTARS.values().forEach(a -> tag(BlockTags.DRAGON_IMMUNE).add(a.get()));
        Titans.ALTARS.values().forEach(a -> tag(BlockTags.WITHER_IMMUNE).add(a.get()));
    }
}
