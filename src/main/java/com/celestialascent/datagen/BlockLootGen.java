package com.celestialascent.datagen;

import com.celestialascent.abyss.Abyss;
import com.celestialascent.boss.SummonAltarBlock;
import com.celestialascent.core.CAReg;
import com.celestialascent.core.Content;
import com.celestialascent.empire.Empire;
import com.celestialascent.stars.Stars;
import com.celestialascent.titans.AltarBlock;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderLookup;
import net.minecraft.data.loot.BlockLootSubProvider;
import net.minecraft.world.flag.FeatureFlags;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.storage.loot.BuiltInLootTables;

import java.util.Set;

public class BlockLootGen extends BlockLootSubProvider {
    public BlockLootGen(HolderLookup.Provider lookup) {
        super(Set.of(), FeatureFlags.REGISTRY.allFlags(), lookup);
    }

    @Override
    protected void generate() {
        Set<Block> unbreakable = Set.of(Empire.PYLON.get(), Empire.IMPERIAL_BARRIER.get(), Empire.THRONE.get(),
                Stars.STAR_GATE_FRAME.get(), Stars.STAR_GATE_PEDESTAL.get());
        for (var holder : Content.BLOCKS) {
            Block b = holder.get();
            if (b.getLootTable() == BuiltInLootTables.EMPTY) continue;
            if (b instanceof AltarBlock || b instanceof SummonAltarBlock || unbreakable.contains(b)) add(b, noDrop());
            else if (b == Stars.STARDUST_ORE.get()) add(b, createOreDrop(b, Stars.STARDUST.get()));
            else if (b == Abyss.VOID_ESSENCE_ORE.get()) add(b, createOreDrop(b, Abyss.VOID_ESSENCE.get()));
            else dropSelf(b);
        }
    }

    @Override
    protected Iterable<Block> getKnownBlocks() {
        return CAReg.BLOCKS.getEntries().stream().map(Holder::value)
                .filter(b -> b.getLootTable() != BuiltInLootTables.EMPTY)
                .toList();
    }
}
