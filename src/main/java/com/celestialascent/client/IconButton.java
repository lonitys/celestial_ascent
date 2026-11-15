package com.celestialascent.client;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.Tooltip;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;

/** Vanilla-styled button that draws an item icon (and optional label) instead of plain text. */
public class IconButton extends Button {
    private final ItemStack icon;

    public IconButton(int x, int y, int w, int h, ItemStack icon, Component tooltip, OnPress onPress) {
        super(x, y, w, h, Component.empty(), onPress, DEFAULT_NARRATION);
        this.icon = icon;
        setTooltip(Tooltip.create(tooltip));
    }

    @Override
    protected void renderWidget(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
        super.renderWidget(g, mouseX, mouseY, partialTick);
        g.renderItem(icon, getX() + (width - 16) / 2, getY() + (height - 16) / 2);
    }
}
