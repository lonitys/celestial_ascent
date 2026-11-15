package com.celestialascent.core.station;

import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;

import java.util.List;
import java.util.function.Predicate;
import java.util.function.UnaryOperator;

/**
 * An upgrade recipe: a base item plus materials (one per material slot, in order) produce a result
 * computed from the base stack, so enchantments and names can carry over.
 */
public record StationRecipe(Predicate<ItemStack> base, List<Mat> mats, UnaryOperator<ItemStack> result) {
    public record Mat(Ingredient ingredient, int count) {
        public boolean test(ItemStack s) {
            return ingredient.test(s) && s.getCount() >= count;
        }
    }

    /** True if the base and every material slot satisfy this recipe. */
    public boolean matches(ItemStack baseStack, List<ItemStack> matStacks) {
        if (baseStack.isEmpty() || !base.test(baseStack) || matStacks.size() < mats.size()) return false;
        for (int i = 0; i < mats.size(); i++) {
            if (!mats.get(i).test(matStacks.get(i))) return false;
        }
        for (int i = mats.size(); i < matStacks.size(); i++) {
            if (!matStacks.get(i).isEmpty()) return false;
        }
        return true;
    }
}
