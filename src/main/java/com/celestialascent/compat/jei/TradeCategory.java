package com.celestialascent.compat.jei;

import com.celestialascent.CelestialAscent;
import com.celestialascent.economy.Professions;
import mezz.jei.api.gui.builder.IRecipeLayoutBuilder;
import mezz.jei.api.gui.drawable.IDrawable;
import mezz.jei.api.gui.ingredient.IRecipeSlotsView;
import mezz.jei.api.helpers.IGuiHelper;
import mezz.jei.api.recipe.IFocusGroup;
import mezz.jei.api.recipe.RecipeIngredientRole;
import mezz.jei.api.recipe.RecipeType;
import mezz.jei.api.recipe.category.IRecipeCategory;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ItemLike;

/** The trades of one of this mod's villager professions: costs, result and the villager level. */
final class TradeCategory implements IRecipeCategory<Professions.TradeDisplay> {
    private static final int WIDTH = 140, HEIGHT = 26;
    private static final int TEXT = 0xFF404040;

    private final RecipeType<Professions.TradeDisplay> type;
    private final Component title;
    private final IDrawable icon;
    private final IDrawable arrow;

    TradeCategory(IGuiHelper gui, String profession, ItemLike workstation) {
        this.type = type(profession);
        this.title = Component.translatable("jei.celestialascent.trades." + profession);
        this.icon = gui.createDrawableItemLike(workstation);
        this.arrow = gui.getRecipeArrow();
    }

    static RecipeType<Professions.TradeDisplay> type(String profession) {
        return RecipeType.create(CelestialAscent.MODID, "trades/" + profession, Professions.TradeDisplay.class);
    }

    @Override
    public RecipeType<Professions.TradeDisplay> getRecipeType() {
        return type;
    }

    @Override
    public Component getTitle() {
        return title;
    }

    @Override
    public IDrawable getIcon() {
        return icon;
    }

    @Override
    public int getWidth() {
        return WIDTH;
    }

    @Override
    public int getHeight() {
        return HEIGHT;
    }

    @Override
    public void setRecipe(IRecipeLayoutBuilder builder, Professions.TradeDisplay t, IFocusGroup focuses) {
        builder.addSlot(RecipeIngredientRole.INPUT, 5, 5).setStandardSlotBackground().addItemStack(t.costA().get());
        ItemStack costB = t.costB().get();
        var second = builder.addSlot(RecipeIngredientRole.INPUT, 25, 5).setStandardSlotBackground();
        if (!costB.isEmpty()) second.addItemStack(costB);
        builder.addSlot(RecipeIngredientRole.OUTPUT, 79, 5).setStandardSlotBackground().addItemStack(t.result().get());
    }

    @Override
    public void draw(Professions.TradeDisplay t, IRecipeSlotsView slots, GuiGraphics g, double mouseX, double mouseY) {
        arrow.draw(g, 48, 4);
        Font font = Minecraft.getInstance().font;
        Component level = Component.translatable("jei.celestialascent.level", t.level());
        g.drawString(font, level, WIDTH - 2 - font.width(level), (HEIGHT - font.lineHeight) / 2 + 1, TEXT, false);
    }
}
