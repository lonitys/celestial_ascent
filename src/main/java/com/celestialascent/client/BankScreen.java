package com.celestialascent.client;

import com.celestialascent.CelestialAscent;
import com.celestialascent.economy.BankMenu;
import com.celestialascent.economy.CoinTier;
import com.celestialascent.economy.Coins;
import com.celestialascent.economy.Economy;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.ItemStack;

public class BankScreen extends AbstractContainerScreen<BankMenu> {
    private static final ResourceLocation BG = ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "textures/gui/bank.png");

    public BankScreen(BankMenu menu, Inventory inv, Component title) {
        super(menu, inv, title);
        imageWidth = 176;
        imageHeight = 186;
        inventoryLabelY = imageHeight - 94;
    }

    @Override
    protected void init() {
        super.init();
        CoinTier[] tiers = CoinTier.values();
        for (int i = 0; i < tiers.length; i++) {
            CoinTier t = tiers[i];
            int idx = i;
            addRenderableWidget(new IconButton(leftPos + 8 + i * 23, topPos + 50, 22, 22, new ItemStack(Economy.coin(t)),
                    Component.translatable("gui.celestialascent.withdraw", Component.translatable("item.celestialascent." + t.id), Coins.format(t.value)),
                    b -> click(Screen.hasShiftDown() ? BankMenu.WITHDRAW_TEN + idx : BankMenu.WITHDRAW_ONE + idx)));
        }
        addRenderableWidget(Button.builder(Component.translatable("gui.celestialascent.deposit_all"), b -> click(BankMenu.DEPOSIT_ALL))
                .bounds(leftPos + 8, topPos + 76, 160, 14).build());
    }

    private void click(int id) {
        if (minecraft != null && minecraft.gameMode != null) minecraft.gameMode.handleInventoryButtonClick(menu.containerId, id);
    }

    @Override
    protected void renderBg(GuiGraphics g, float partialTick, int mouseX, int mouseY) {
        g.blit(BG, leftPos, topPos, 0, 0, imageWidth, imageHeight, 256, 256);
    }

    @Override
    protected void renderLabels(GuiGraphics g, int mouseX, int mouseY) {
        g.drawString(font, title, titleLabelX, titleLabelY, 0xF2E6C9, false);
        g.drawString(font, playerInventoryTitle, inventoryLabelX, inventoryLabelY, 0xBFB49A, false);
        Component bal = Component.translatable("gui.celestialascent.balance", Coins.format(menu.balance()));
        g.drawString(font, bal, (imageWidth - font.width(bal)) / 2, 22, 0xFFD966, true);
        Component carried = Component.translatable("gui.celestialascent.carried", Coins.format(Coins.countInventory(minecraft.player)));
        g.drawString(font, carried, (imageWidth - font.width(carried)) / 2, 36, 0xA89F88, false);
    }

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
        super.render(g, mouseX, mouseY, partialTick);
        renderTooltip(g, mouseX, mouseY);
    }
}
