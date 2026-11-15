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
        tag(BlockTags.MINEABLE_WITH_AXE).add(Economy.BANK_COUNTER.get(), Economy.SHOP_STALL.get(), Economy.QUEST_BOARD.get());
        tag(BlockTags.MINEABLE_WITH_PICKAXE).add(Economy.TITAN_ANVIL.get(), Economy.RELIC_PEDESTAL.get(), Titans.TITAN_FORGE.get());
        tag(BlockTags.NEEDS_IRON_TOOL).add(Economy.TITAN_ANVIL.get(), Economy.RELIC_PEDESTAL.get());
        tag(BlockTags.NEEDS_DIAMOND_TOOL).add(Titans.TITAN_FORGE.get());
        tag(BlockTags.MINEABLE_WITH_PICKAXE).add(com.celestialascent.stars.Stars.STARSTONE.get(), com.celestialascent.stars.Stars.STARLIT_STARSTONE.get(), com.celestialascent.stars.Stars.STARSTONE_BRICKS.get(),
                com.celestialascent.stars.Stars.STARDUST_ORE.get(), com.celestialascent.stars.Stars.STAR_CRYSTAL.get(), com.celestialascent.stars.Stars.SKY_ALTAR.get(), com.celestialascent.abyss.Abyss.ABYSSAL_STONE.get(), com.celestialascent.abyss.Abyss.VOID_ESSENCE_ORE.get(),
                com.celestialascent.abyss.Abyss.VOID_INFUSER.get(), com.celestialascent.abyss.Abyss.ASCENSION_ALTAR.get(), com.celestialascent.empire.Empire.IMPERIAL_FORGE.get());
        tag(BlockTags.NEEDS_DIAMOND_TOOL).add(com.celestialascent.stars.Stars.STARDUST_ORE.get(), com.celestialascent.abyss.Abyss.VOID_ESSENCE_ORE.get(), com.celestialascent.stars.Stars.SKY_ALTAR.get(),
                com.celestialascent.abyss.Abyss.VOID_INFUSER.get(), com.celestialascent.abyss.Abyss.ASCENSION_ALTAR.get(), com.celestialascent.empire.Empire.IMPERIAL_FORGE.get());
        tag(BlockTags.DRAGON_IMMUNE).add(com.celestialascent.empire.Empire.PYLON.get(), com.celestialascent.empire.Empire.IMPERIAL_BARRIER.get(), com.celestialascent.empire.Empire.THRONE.get(), com.celestialascent.stars.Stars.STAR_GATE_FRAME.get(),
                com.celestialascent.stars.Stars.STAR_GATE_PEDESTAL.get(), com.celestialascent.stars.Stars.STAR_PORTAL.get());
        Titans.ALTARS.values().forEach(a -> tag(BlockTags.DRAGON_IMMUNE).add(a.get()));
        Titans.ALTARS.values().forEach(a -> tag(BlockTags.WITHER_IMMUNE).add(a.get()));
    }
}
