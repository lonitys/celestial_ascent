package com.celestialascent.compat.jei;

import com.celestialascent.CelestialAscent;
import com.celestialascent.armor.ArmorStages;
import com.celestialascent.core.station.StationRecipe;
import com.celestialascent.core.station.StationType;
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

import java.util.ArrayList;
import java.util.List;

/**
 * One category per upgrade station. The background is cut from the station's own GUI texture (slots,
 * arrow and output frame), so a recipe looks like the station in game; a footer gives the processing
 * time and conditions (open night sky, full resonance for evolutions).
 */
final class StationCategory implements IRecipeCategory<StationRecipe.Example> {
    /** The region of the station texture that is shown: from left of the base slot to past the output frame. */
    private static final int U = 24, V = 12, CROP_W = 124, CROP_H = 62;
    private static final int LINE = 10;
    private static final int TEXT = 0xFF404040;

    private final StationType station;
    private final RecipeType<StationRecipe.Example> type;
    private final IDrawable background;
    private final IDrawable icon;
    private final Component title;
    /** Room for the footer: the time, the station's condition (if any) and the resonance an evolution needs. */
    private final int height;

    StationCategory(IGuiHelper gui, StationType station, ItemLike block) {
        this.station = station;
        this.height = CROP_H + 4 + LINE * (station.conditionKey() == null ? 2 : 3);
        this.type = type(station);
        this.background = gui.drawableBuilder(station.gui, U, V, CROP_W, CROP_H).setTextureSize(256, 256).build();
        this.icon = gui.createDrawableItemLike(block);
        this.title = new ItemStack(block).getHoverName();
    }

    static RecipeType<StationRecipe.Example> type(StationType station) {
        return RecipeType.create(CelestialAscent.MODID, "station/" + station.id, StationRecipe.Example.class);
    }

    @Override
    public RecipeType<StationRecipe.Example> getRecipeType() {
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
        return CROP_W;
    }

    @Override
    public int getHeight() {
        return height;
    }

    @Override
    public void setRecipe(IRecipeLayoutBuilder builder, StationRecipe.Example ex, IFocusGroup focuses) {
        // Inputs in menu order (base, then materials) so recipe transfer fills the right slots.
        builder.addSlot(RecipeIngredientRole.INPUT, station.base[0] - U, station.base[1] - V).addItemStack(ex.base());
        for (int i = 0; i < ex.mats().size() && i < station.mats.length; i++) {
            builder.addSlot(RecipeIngredientRole.INPUT, station.mats[i][0] - U, station.mats[i][1] - V).addItemStack(ex.mats().get(i));
        }
        builder.addSlot(RecipeIngredientRole.OUTPUT, station.output[0] - U, station.output[1] - V).addItemStack(ex.result());
    }

    @Override
    public void draw(StationRecipe.Example ex, IRecipeSlotsView slots, GuiGraphics g, double mouseX, double mouseY) {
        background.draw(g, 0, 0);
        List<Component> parts = new ArrayList<>();
        int ticks = station.processTicks;
        parts.add(Component.translatable("jei.celestialascent.time", ticks % 20 == 0 ? String.valueOf(ticks / 20) : String.format("%.1f", ticks / 20f)));
        if (station.conditionKey() != null) parts.add(Component.translatable(station.conditionKey()));
        if (ArmorStages.stage(ex.base()) > 0 && ArmorStages.ready(ex.base())) {
            parts.add(Component.translatable("jei.celestialascent.needs_resonance", ArmorStages.required(ex.base())));
        }
        drawFooter(g, Minecraft.getInstance().font, parts);
    }

    /** Centered lines below the crop; parts share a line when they fit, a part wider than the crop is scaled down. */
    private static void drawFooter(GuiGraphics g, Font font, List<Component> parts) {
        List<Component> lines = new ArrayList<>();
        Component sep = Component.literal("  ·  ");
        for (Component part : parts) {
            boolean join = !lines.isEmpty() && font.width(lines.getLast()) + font.width(sep) + font.width(part) <= CROP_W;
            if (join) {
                lines.set(lines.size() - 1, Component.empty().append(lines.getLast()).append(sep).append(part));
            } else {
                lines.add(part);
            }
        }
        int y = CROP_H + 3;
        for (Component line : lines) {
            int w = font.width(line);
            if (w <= CROP_W) {
                g.drawString(font, line, (CROP_W - w) / 2, y, TEXT, false);
            } else {
                float s = CROP_W / (float) w;
                g.pose().pushPose();
                g.pose().translate(0, y + (1 - s) * font.lineHeight / 2f, 0);
                g.pose().scale(s, s, 1);
                g.drawString(font, line, 0, 0, TEXT, false);
                g.pose().popPose();
            }
            y += LINE;
        }
    }
}
