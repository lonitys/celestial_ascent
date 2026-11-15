package com.celestialascent.datagen;

import com.celestialascent.CelestialAscent;
import com.celestialascent.economy.CoinTier;
import com.celestialascent.economy.Economy;
import com.celestialascent.titans.Element;
import com.celestialascent.titans.Titans;
import net.minecraft.core.HolderLookup;
import net.minecraft.data.PackOutput;
import net.minecraft.data.recipes.RecipeCategory;
import net.minecraft.data.recipes.RecipeOutput;
import net.minecraft.data.recipes.RecipeProvider;
import net.minecraft.data.recipes.ShapedRecipeBuilder;
import net.minecraft.data.recipes.ShapelessRecipeBuilder;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.ItemTags;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;

import java.util.concurrent.CompletableFuture;

public class RecipeGen extends RecipeProvider {
    public RecipeGen(PackOutput out, CompletableFuture<HolderLookup.Provider> lookup) {
        super(out, lookup);
    }

    private static ResourceLocation id(String path) {
        return ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, path);
    }

    @Override
    protected void buildRecipes(RecipeOutput out) {
        CoinTier[] tiers = CoinTier.values();
        for (int i = 0; i + 1 < tiers.length; i++) {
            Item low = Economy.coin(tiers[i]), high = Economy.coin(tiers[i + 1]);
            ShapelessRecipeBuilder.shapeless(RecipeCategory.MISC, high).requires(low, 9).requires(low)
                    .unlockedBy("has_coin", has(low)).save(out, id(tiers[i + 1].id + "_from_" + tiers[i].id));
            ShapelessRecipeBuilder.shapeless(RecipeCategory.MISC, low, 10).requires(high)
                    .unlockedBy("has_coin", has(high)).save(out, id(tiers[i].id + "_from_" + tiers[i + 1].id));
        }

        ShapedRecipeBuilder.shaped(RecipeCategory.DECORATIONS, Economy.BANK_COUNTER.get())
                .pattern("GGG").pattern("PEP").pattern("PPP")
                .define('G', Items.GOLD_INGOT).define('E', Items.EMERALD_BLOCK).define('P', Items.DARK_OAK_PLANKS)
                .unlockedBy("has_emerald", has(Items.EMERALD)).save(out);
        ShapedRecipeBuilder.shaped(RecipeCategory.DECORATIONS, Economy.SHOP_STALL.get())
                .pattern("WWW").pattern("PCP").pattern("PPP")
                .define('W', Items.RED_WOOL).define('C', Items.CHEST).define('P', ItemTags.PLANKS)
                .unlockedBy("has_chest", has(Items.CHEST)).save(out);
        ShapedRecipeBuilder.shaped(RecipeCategory.DECORATIONS, Economy.TITAN_ANVIL.get())
                .pattern("BBB").pattern(" A ").pattern("III")
                .define('B', Items.IRON_BLOCK).define('A', Items.ANVIL).define('I', Items.IRON_INGOT)
                .unlockedBy("has_anvil", has(Items.ANVIL)).save(out);
        ShapedRecipeBuilder.shaped(RecipeCategory.MISC, Titans.TITAN_FORGE.get())
                .pattern("SNS").pattern("BFB").pattern("OOO")
                .define('S', Titans.TITAN_SHARD).define('N', Items.NETHERITE_INGOT).define('B', Items.POLISHED_BLACKSTONE_BRICKS)
                .define('F', Items.BLAST_FURNACE).define('O', Items.OBSIDIAN)
                .unlockedBy("has_shard", has(Titans.TITAN_SHARD)).save(out);

        ShapedRecipeBuilder.shaped(RecipeCategory.TOOLS, com.celestialascent.stars.Stars.STAR_COMPASS.get())
                .pattern("EHE").pattern("ECE").pattern(" E ")
                .define('E', Items.ENDER_EYE).define('H', com.celestialascent.empire.Empire.DRAGON_HEART).define('C', Items.COMPASS)
                .unlockedBy("has_heart", has(com.celestialascent.empire.Empire.DRAGON_HEART)).save(out);
        ShapedRecipeBuilder.shaped(RecipeCategory.MISC, com.celestialascent.empire.Empire.IMPERIAL_FORGE.get())
                .pattern("PGP").pattern("GFG").pattern("OOO")
                .define('P', com.celestialascent.empire.Empire.IMPERIAL_PLATING).define('G', com.celestialascent.empire.Empire.ENDER_GEAR)
                .define('F', Titans.TITAN_FORGE.get()).define('O', Items.OBSIDIAN)
                .unlockedBy("has_plating", has(com.celestialascent.empire.Empire.IMPERIAL_PLATING)).save(out);
        ShapedRecipeBuilder.shaped(RecipeCategory.MISC, com.celestialascent.stars.Stars.SKY_ALTAR.get())
                .pattern("ASA").pattern("SBS").pattern("OOO")
                .define('A', Items.AMETHYST_BLOCK).define('S', com.celestialascent.stars.Stars.STARDUST).define('B', Items.BEACON).define('O', Items.OBSIDIAN)
                .unlockedBy("has_stardust", has(com.celestialascent.stars.Stars.STARDUST)).save(out);
        ShapedRecipeBuilder.shaped(RecipeCategory.BUILDING_BLOCKS, com.celestialascent.stars.Stars.STARSTONE_BRICKS.get(), 4)
                .pattern("SS").pattern("SS").define('S', com.celestialascent.stars.Stars.STARSTONE.get())
                .unlockedBy("has_starstone", has(com.celestialascent.stars.Stars.STARSTONE.get())).save(out);
        ShapedRecipeBuilder.shaped(RecipeCategory.MISC, com.celestialascent.abyss.Abyss.VOID_INFUSER.get())
                .pattern("VEV").pattern("ECE").pattern("OOO")
                .define('V', com.celestialascent.abyss.Abyss.VOID_ESSENCE).define('E', Items.ECHO_SHARD).define('C', Items.SCULK_CATALYST)
                .define('O', Items.CRYING_OBSIDIAN)
                .unlockedBy("has_essence", has(com.celestialascent.abyss.Abyss.VOID_ESSENCE)).save(out);
        ShapedRecipeBuilder.shaped(RecipeCategory.MISC, com.celestialascent.abyss.Abyss.PRIMORDIAL_CORE.get(), 2)
                .pattern("FVT").pattern("VCV").pattern("SVM")
                .define('F', Titans.CORES.get(Element.FROST)).define('T', Titans.CORES.get(Element.TIDE))
                .define('S', Titans.CORES.get(Element.STORM)).define('M', Titans.CORES.get(Element.MAGMA))
                .define('V', com.celestialascent.abyss.Abyss.VOID_ESSENCE).define('C', com.celestialascent.empire.Empire.COLOSSUS_CORE)
                .unlockedBy("has_essence", has(com.celestialascent.abyss.Abyss.VOID_ESSENCE)).save(out);
        ShapedRecipeBuilder.shaped(RecipeCategory.MISC, com.celestialascent.abyss.Abyss.ABYSSAL_BEACON.get())
                .pattern("VSV").pattern("SNS").pattern("VSV")
                .define('V', com.celestialascent.abyss.Abyss.VOID_ESSENCE).define('S', com.celestialascent.stars.Stars.STARDUST).define('N', Items.NETHER_STAR)
                .unlockedBy("has_essence", has(com.celestialascent.abyss.Abyss.VOID_ESSENCE)).save(out);
        ShapelessRecipeBuilder.shapeless(RecipeCategory.TOOLS, com.celestialascent.abyss.Abyss.ASCENSION_PEARL.get(), 2)
                .requires(Items.ENDER_PEARL).requires(com.celestialascent.abyss.Abyss.VOID_ESSENCE).requires(com.celestialascent.stars.Stars.STARDUST)
                .unlockedBy("has_essence", has(com.celestialascent.abyss.Abyss.VOID_ESSENCE)).save(out);
        ShapedRecipeBuilder.shaped(RecipeCategory.MISC, com.celestialascent.abyss.Abyss.ASCENSION_ALTAR.get())
                .pattern("OSO").pattern("NIN").pattern("OSO")
                .define('O', Items.CRYING_OBSIDIAN).define('S', com.celestialascent.stars.Stars.STAR_CORE).define('N', Items.NETHERITE_BLOCK)
                .define('I', com.celestialascent.empire.Empire.IMPERIAL_SEAL)
                .unlockedBy("has_heart", has(com.celestialascent.abyss.Abyss.VOID_HEART)).save(out);

        ShapedRecipeBuilder.shaped(RecipeCategory.DECORATIONS, Economy.QUEST_BOARD.get())
                .pattern("PPP").pattern("PBP").pattern("PPP")
                .define('P', ItemTags.PLANKS).define('B', Items.BOOK)
                .unlockedBy("has_book", has(Items.BOOK)).save(out);

        sigil(out, Element.FROST, Items.BLUE_ICE, Items.DIAMOND);
        sigil(out, Element.TIDE, Items.PRISMARINE_SHARD, Items.NAUTILUS_SHELL);
        sigil(out, Element.STORM, Items.LIGHTNING_ROD, Items.AMETHYST_SHARD);
        sigil(out, Element.MAGMA, Items.MAGMA_CREAM, Items.BLAZE_ROD);
    }

    private void sigil(RecipeOutput out, Element e, Item corner, Item edge) {
        ShapedRecipeBuilder.shaped(RecipeCategory.MISC, Titans.SIGILS.get(e).get())
                .pattern("CEC").pattern("ENE").pattern("CEC")
                .define('C', corner).define('E', edge).define('N', Items.NETHERITE_SCRAP)
                .unlockedBy("has_scrap", has(Items.NETHERITE_SCRAP)).save(out);
    }
}
