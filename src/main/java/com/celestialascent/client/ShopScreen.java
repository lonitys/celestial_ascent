package com.celestialascent.client;

import com.celestialascent.CelestialAscent;
import com.celestialascent.economy.Coins;
import com.celestialascent.economy.ShopMenu;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.ItemStack;

public class ShopScreen extends AbstractContainerScreen<ShopMenu> {
    private static final ResourceLocation BG_OWNER = ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "textures/gui/shop_owner.png");
    private static final ResourceLocation BG_BUYER = ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "textures/gui/shop_buyer.png");
    private static final String[] DELTA_LABELS = {"-1k", "-100", "-10", "-1", "+1", "+10", "+100", "+1k"};

    public ShopScreen(ShopMenu menu, Inventory inv, Component title) {
        super(menu, inv, title);
        imageWidth = 176;
        imageHeight = 204;
        inventoryLabelY = imageHeight - 94;
    }

    @Override
    protected void init() {
        super.init();
        if (menu.owner) {
            for (int i = 0; i < 8; i++) {
                int id = i;
                int col = i % 4, row = i / 4;
                addRenderableWidget(Button.builder(Component.literal(DELTA_LABELS[i]), b -> click(id))
                        .bounds(leftPos + 70 + col * 25, topPos + 42 + row * 16, 24, 14).build());
            }
            addRenderableWidget(Button.builder(Component.literal("×10"), b -> click(10)).bounds(leftPos + 70, topPos + 76, 49, 14).build());
            addRenderableWidget(Button.builder(Component.literal("÷10"), b -> click(11)).bounds(leftPos + 120, topPos + 76, 49, 14).build());
            addRenderableWidget(Button.builder(Component.literal("-"), b -> click(8)).bounds(leftPos + 130, topPos + 93, 18, 14).build());
            addRenderableWidget(Button.builder(Component.literal("+"), b -> click(9)).bounds(leftPos + 150, topPos + 93, 18, 14).build());
        } else {
            addRenderableWidget(Button.builder(Component.translatable("gui.celestialascent.buy"), b -> click(ShopMenu.BUY))
                    .bounds(leftPos + 70, topPos + 86, 98, 18).build());
        }
    }

    private void click(int id) {
        if (minecraft != null && minecraft.gameMode != null) minecraft.gameMode.handleInventoryButtonClick(menu.containerId, id);
    }

    @Override
    protected void renderBg(GuiGraphics g, float partialTick, int mouseX, int mouseY) {
        g.blit(menu.owner ? BG_OWNER : BG_BUYER, leftPos, topPos, 0, 0, imageWidth, imageHeight, 256, 256);
    }

    @Override
    protected void renderLabels(GuiGraphics g, int mouseX, int mouseY) {
        g.drawString(font, title, titleLabelX, titleLabelY, 0xF2E6C9, false);
        g.drawString(font, playerInventoryTitle, inventoryLabelX, inventoryLabelY, 0xBFB49A, false);
        if (menu.owner) {
            g.drawString(font, Component.translatable("gui.celestialascent.price"), 70, 18, 0xBFB49A, false);
            g.drawString(font, Coins.format(menu.price()), 70, 29, 0xFFD966, true);
            g.drawString(font, Component.translatable("gui.celestialascent.bundle", menu.bundle()), 70, 96, 0xF2E6C9, false);
        } else {
            ItemStack shown = menu.getSlot(0).getItem();
            if (shown.isEmpty()) {
                g.drawString(font, Component.translatable("gui.celestialascent.sold_out"), 70, 24, 0xFF7070, false);
            } else {
                g.drawString(font, shown.getHoverName(), 70, 22, 0xF2E6C9, false);
                g.drawString(font, Component.translatable("gui.celestialascent.bundle", menu.bundle()), 70, 36, 0xBFB49A, false);
            }
            g.drawString(font, Coins.format(menu.price()), 70, 52, 0xFFD966, true);
            g.drawString(font, Component.translatable("gui.celestialascent.in_stock", menu.stock()), 70, 68, 0xA89F88, false);
        }
    }

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
        super.render(g, mouseX, mouseY, partialTick);
        renderTooltip(g, mouseX, mouseY);
    }
}
