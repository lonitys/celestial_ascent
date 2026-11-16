package com.celestialascent.core.station;

import com.google.common.base.Suppliers;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;

import java.util.List;
import java.util.function.Predicate;
import java.util.function.Supplier;
import java.util.function.UnaryOperator;

/**
 * An upgrade recipe: a base item plus materials (one per material slot, in order) produce a result
 * computed from the base stack, so enchantments and names can carry over.
 *
 * <p>Because base and result are functions, recipe viewers cannot list them on their own; each recipe
 * also carries {@link Example}s, concrete rows built the first time they are asked for.
 */
public record StationRecipe(Predicate<ItemStack> base, List<Mat> mats, UnaryOperator<ItemStack> result,
                            Supplier<List<Example>> examples) {
    public record Mat(Ingredient ingredient, int count) {
        public boolean test(ItemStack s) {
            return ingredient.test(s) && s.getCount() >= count;
        }
    }

    /** One concrete case for recipe viewers: a base stack, the material stacks and the result. */
    public record Example(ItemStack base, List<ItemStack> mats, ItemStack result) {}

    /** Examples built from sample base stacks: the materials are the first item of each ingredient. */
    public static Supplier<List<Example>> from(List<Mat> mats, UnaryOperator<ItemStack> result, Supplier<List<ItemStack>> bases) {
        return Suppliers.memoize(() -> bases.get().stream().map(b -> {
            List<ItemStack> ms = mats.stream().map(m -> m.ingredient().getItems()[0].copyWithCount(m.count())).toList();
            return new Example(b, ms, result.apply(b.copy()));
        }).toList());
    }

    /** The usual way to make a recipe: its examples come from sample base stacks. */
    public static StationRecipe of(Predicate<ItemStack> base, List<Mat> mats, UnaryOperator<ItemStack> result, Supplier<List<ItemStack>> bases) {
        return new StationRecipe(base, mats, result, from(mats, result, bases));
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
