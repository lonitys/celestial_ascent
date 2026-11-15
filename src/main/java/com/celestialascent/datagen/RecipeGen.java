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
