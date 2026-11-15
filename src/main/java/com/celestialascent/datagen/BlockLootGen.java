package com.celestialascent.datagen;

import com.celestialascent.core.CAReg;
import com.celestialascent.core.Content;
import com.celestialascent.titans.AltarBlock;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderLookup;
import net.minecraft.data.loot.BlockLootSubProvider;
import net.minecraft.world.flag.FeatureFlags;
import net.minecraft.world.level.block.Block;

import java.util.Set;

public class BlockLootGen extends BlockLootSubProvider {
    public BlockLootGen(HolderLookup.Provider lookup) {
        super(Set.of(), FeatureFlags.REGISTRY.allFlags(), lookup);
    }

    @Override
    protected void generate() {
        for (var holder : Content.BLOCKS) {
            Block b = holder.get();
            if (b instanceof AltarBlock) add(b, noDrop());
            else dropSelf(b);
        }
    }

    @Override
    protected Iterable<Block> getKnownBlocks() {
        // Only blocks that have a loot table (technical blocks use noLootTable()).
        return CAReg.BLOCKS.getEntries().stream().map(Holder::value)
                .filter(b -> b.getLootTable() != net.minecraft.world.level.storage.loot.BuiltInLootTables.EMPTY)
                .toList();
    }
}
