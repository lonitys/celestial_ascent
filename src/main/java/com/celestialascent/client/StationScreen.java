package com.celestialascent.client;

import com.celestialascent.core.station.StationMenu;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Inventory;

public class StationScreen extends AbstractContainerScreen<StationMenu> {
    public StationScreen(StationMenu menu, Inventory inv, Component title) {
        super(menu, inv, title);
        imageWidth = 176;
        imageHeight = menu.type.imageHeight;
        inventoryLabelY = imageHeight - 94;
    }

    @Override
    protected void renderBg(GuiGraphics g, float partialTick, int mouseX, int mouseY) {
        g.blit(menu.type.gui, leftPos, topPos, 0, 0, imageWidth, imageHeight, 256, 256);
        int w = Math.round(24 * menu.progress());
        if (w > 0) {
            g.blit(menu.type.gui, leftPos + menu.type.arrow[0], topPos + menu.type.arrow[1], 176, 0, w, 16, 256, 256);
        }
    }

    @Override
    protected void renderLabels(GuiGraphics g, int mouseX, int mouseY) {
        g.drawString(font, title, titleLabelX, titleLabelY, 0xF2E6C9, false);
        g.drawString(font, playerInventoryTitle, inventoryLabelX, inventoryLabelY, 0xBFB49A, false);
        if (!menu.conditionOk() && menu.type.conditionKey() != null) {
            Component c = Component.translatable(menu.type.conditionKey());
            g.drawString(font, c, imageWidth - 8 - font.width(c), titleLabelY, 0xFF8080, false);
        }
    }

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
        super.render(g, mouseX, mouseY, partialTick);
        renderTooltip(g, mouseX, mouseY);
    }
}
