package com.celestialascent.compat.jei;

import com.celestialascent.boss.BossSummons;
import com.celestialascent.core.station.StationMenu;
import com.celestialascent.core.station.StationRecipe;
import com.celestialascent.core.station.StationType;
import mezz.jei.api.constants.RecipeTypes;
import mezz.jei.api.constants.VanillaTypes;
import mezz.jei.api.recipe.IFocus;
import mezz.jei.api.recipe.RecipeIngredientRole;
import mezz.jei.api.recipe.category.IRecipeCategory;
import mezz.jei.api.runtime.IJeiRuntime;
import net.minecraft.client.Minecraft;
import net.minecraft.world.item.ItemStack;

import java.util.List;
import java.util.function.Predicate;

/**
 * Opens JEI pages for the dev-only screenshot showcase. Only called through a separate method in
 * {@code client.Showcase}, and only when JEI is loaded.
 */
public final class JeiShowcase {
    private JeiShowcase() {}

    static IJeiRuntime runtime;

    public static boolean ready() {
        return runtime != null;
    }

    /** Shows the recipes (OUTPUT) or uses (INPUT) of a stack, like pressing R or U on it. */
    public static void show(ItemStack stack, RecipeIngredientRole role) {
        if (runtime == null) return;
        runtime.getRecipesGui().show(runtime.getJeiHelpers().getFocusFactory().createFocus(role, VanillaTypes.ITEM_STACK, stack));
    }

    /** Like pressing R on a stack. */
    public static void showRecipes(ItemStack stack) {
        show(stack, RecipeIngredientRole.OUTPUT);
    }

    /** Like pressing U on a stack. */
    public static void showUses(ItemStack stack) {
        show(stack, RecipeIngredientRole.INPUT);
    }

    /** Like pressing R on a stack, but opened on one station's tab. */
    public static void showStationRecipes(StationType type, ItemStack result) {
        showIn(runtime == null ? null : runtime.getRecipeManager().getRecipeCategory(StationCategory.type(type)), result);
    }

    /** Like pressing R on a boss drop, opened on the summoning tab. */
    public static void showSummonsOf(ItemStack drop) {
        showIn(runtime == null ? null : runtime.getRecipeManager().getRecipeCategory(SummonCategory.TYPE), drop);
    }

    private static <T> void showIn(IRecipeCategory<T> category, ItemStack output) {
        if (runtime == null || category == null) return;
        IFocus<ItemStack> focus = runtime.getJeiHelpers().getFocusFactory().createFocus(RecipeIngredientRole.OUTPUT, VanillaTypes.ITEM_STACK, output);
        var recipes = runtime.getRecipeManager().createRecipeLookup(category.getRecipeType()).limitFocus(List.of(focus)).get().toList();
        runtime.getRecipesGui().showRecipes(category, recipes, List.of(focus));
    }

    public static void showStation(StationType type) {
        if (runtime != null) runtime.getRecipesGui().showTypes(List.of(StationCategory.type(type)));
    }

    public static void showSummons() {
        if (runtime != null) runtime.getRecipesGui().showTypes(List.of(SummonCategory.TYPE));
    }

    /** Just these summons (indexes into {@link BossSummons#all()}), so every boss can be checked on screen. */
    public static void showSummons(int... indexes) {
        if (runtime == null) return;
        List<BossSummons.Summon> all = BossSummons.all();
        List<BossSummons.Summon> picked = java.util.Arrays.stream(indexes).filter(i -> i < all.size()).mapToObj(all::get).toList();
        runtime.getRecipesGui().showRecipes(runtime.getRecipeManager().getRecipeCategory(SummonCategory.TYPE), picked, List.of());
    }

    public static void showTrades(String profession) {
        if (runtime != null) runtime.getRecipesGui().showTypes(List.of(TradeCategory.type(profession)));
    }

    /** The information page of a stack, opened directly on JEI's info category. */
    public static void showInfo(ItemStack stack) {
        showIn(runtime == null ? null : runtime.getRecipeManager().getRecipeCategory(RecipeTypes.INFORMATION), stack);
    }

    /**
     * Presses the + button for the first recipe of the open station screen that {@code which} accepts.
     * Returns false if there is no such screen, recipe or handler, or JEI refused the transfer.
     */
    public static boolean transfer(StationType type, Predicate<StationRecipe.Example> which) {
        Minecraft mc = Minecraft.getInstance();
        if (runtime == null || mc.player == null || !(mc.player.containerMenu instanceof StationMenu menu) || menu.type != type) return false;
        IRecipeCategory<StationRecipe.Example> category = runtime.getRecipeManager().getRecipeCategory(StationCategory.type(type));
        var recipe = runtime.getRecipeManager().createRecipeLookup(StationCategory.type(type)).get().filter(which).findFirst();
        if (recipe.isEmpty()) return false;
        var layout = runtime.getRecipeManager().createRecipeLayoutDrawable(category, recipe.get(), runtime.getJeiHelpers().getFocusFactory().getEmptyFocusGroup());
        var handler = runtime.getRecipeTransferManager().getRecipeTransferHandler(menu, category);
        if (layout.isEmpty() || handler.isEmpty()) return false;
        var error = handler.get().transferRecipe(menu, recipe.get(), layout.get().getRecipeSlotsView(), mc.player, false, true);
        return error == null;
    }
}
