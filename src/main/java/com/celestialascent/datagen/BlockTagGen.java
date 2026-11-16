package com.celestialascent.datagen;

import com.celestialascent.CelestialAscent;
import com.celestialascent.economy.Economy;
import com.celestialascent.titans.Titans;
import net.minecraft.core.HolderLookup;
import net.minecraft.data.PackOutput;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.level.block.Blocks;
import net.neoforged.neoforge.common.Tags;
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
        tag(BlockTags.MINEABLE_WITH_PICKAXE).add(Economy.TITAN_ANVIL.get(), Economy.RELIC_PEDESTAL.get(), Economy.CELESTIAL_CRYSTAL.get(), Titans.TITAN_FORGE.get());
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

        // Blocks that only exist where someone built (or inside structures): the retrogen never builds over them.
        tag(com.celestialascent.retrogen.SiteCheck.PLAYER_MADE)
                .addTags(BlockTags.BEDS, BlockTags.PLANKS, BlockTags.WOOL, BlockTags.WOOL_CARPETS, BlockTags.DOORS, BlockTags.TRAPDOORS,
                        BlockTags.FENCES, BlockTags.FENCE_GATES, BlockTags.ALL_SIGNS, BlockTags.BANNERS, BlockTags.RAILS, BlockTags.SHULKER_BOXES,
                        BlockTags.CANDLES, BlockTags.BUTTONS, BlockTags.PRESSURE_PLATES, BlockTags.SLABS, BlockTags.STAIRS, BlockTags.WALLS,
                        BlockTags.CAULDRONS, BlockTags.FLOWER_POTS, BlockTags.ANVIL, BlockTags.CAMPFIRES,
                        Tags.Blocks.GLASS_BLOCKS, Tags.Blocks.GLASS_PANES, Tags.Blocks.CHESTS, Tags.Blocks.BARRELS, Tags.Blocks.CONCRETES,
                        Tags.Blocks.GLAZED_TERRACOTTAS)
                .add(Blocks.CRAFTING_TABLE, Blocks.CRAFTER, Blocks.FURNACE, Blocks.BLAST_FURNACE, Blocks.SMOKER, Blocks.ENCHANTING_TABLE,
                        Blocks.BOOKSHELF, Blocks.CHISELED_BOOKSHELF, Blocks.BREWING_STAND, Blocks.HOPPER, Blocks.DROPPER, Blocks.DISPENSER,
                        Blocks.OBSERVER, Blocks.PISTON, Blocks.STICKY_PISTON, Blocks.REDSTONE_WIRE, Blocks.REDSTONE_TORCH, Blocks.REDSTONE_WALL_TORCH,
                        Blocks.REPEATER, Blocks.COMPARATOR, Blocks.LEVER, Blocks.TARGET, Blocks.DAYLIGHT_DETECTOR, Blocks.TNT, Blocks.TORCH,
                        Blocks.WALL_TORCH, Blocks.SOUL_TORCH, Blocks.SOUL_WALL_TORCH, Blocks.LANTERN, Blocks.SOUL_LANTERN, Blocks.FARMLAND,
                        Blocks.BEACON, Blocks.JUKEBOX, Blocks.NOTE_BLOCK, Blocks.LOOM, Blocks.CARTOGRAPHY_TABLE, Blocks.FLETCHING_TABLE,
                        Blocks.SMITHING_TABLE, Blocks.GRINDSTONE, Blocks.STONECUTTER, Blocks.COMPOSTER, Blocks.LECTERN, Blocks.BELL,
                        Blocks.RESPAWN_ANCHOR, Blocks.LODESTONE, Blocks.SCAFFOLDING, Blocks.LADDER, Blocks.IRON_BARS, Blocks.CHAIN, Blocks.END_ROD,
                        Blocks.ENDER_CHEST, Blocks.CAKE, Blocks.BRICKS, Blocks.STONE_BRICKS, Blocks.MOSSY_STONE_BRICKS, Blocks.CRACKED_STONE_BRICKS,
                        Blocks.NETHER_BRICKS, Blocks.RED_NETHER_BRICKS, Blocks.PURPUR_BLOCK, Blocks.PURPUR_PILLAR, Blocks.END_STONE_BRICKS,
                        Blocks.SMOOTH_STONE, Blocks.POLISHED_ANDESITE, Blocks.POLISHED_DIORITE, Blocks.POLISHED_GRANITE, Blocks.POLISHED_DEEPSLATE,
                        Blocks.POLISHED_BLACKSTONE, Blocks.POLISHED_BLACKSTONE_BRICKS, Blocks.QUARTZ_BLOCK, Blocks.SMOOTH_QUARTZ, Blocks.SEA_LANTERN,
                        Blocks.IRON_BLOCK, Blocks.GOLD_BLOCK, Blocks.DIAMOND_BLOCK, Blocks.EMERALD_BLOCK, Blocks.NETHERITE_BLOCK, Blocks.LAPIS_BLOCK,
                        Blocks.REDSTONE_BLOCK,
                        Economy.BANK_COUNTER.get(), Economy.SHOP_STALL.get(), Economy.QUEST_BOARD.get(), Economy.TITAN_ANVIL.get(),
                        Economy.RELIC_PEDESTAL.get(), Titans.TITAN_FORGE.get(), com.celestialascent.empire.Empire.IMPERIAL_FORGE.get(),
                        com.celestialascent.stars.Stars.SKY_ALTAR.get(), com.celestialascent.abyss.Abyss.VOID_INFUSER.get(),
                        com.celestialascent.abyss.Abyss.ASCENSION_ALTAR.get());
    }
}
