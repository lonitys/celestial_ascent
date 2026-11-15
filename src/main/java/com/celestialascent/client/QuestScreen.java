package com.celestialascent.client;

import com.celestialascent.CelestialAscent;
import com.celestialascent.economy.Coins;
import com.celestialascent.economy.QuestMenu;
import com.celestialascent.economy.Quests;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.ItemStack;

import java.util.ArrayList;
import java.util.List;

public class QuestScreen extends AbstractContainerScreen<QuestMenu> {
    private static final ResourceLocation BG = ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "textures/gui/quest_board.png");
    private final List<Button> buttons = new ArrayList<>();

    public QuestScreen(QuestMenu menu, Inventory inv, Component title) {
        super(menu, inv, title);
        imageWidth = 176;
        imageHeight = 186;
        inventoryLabelY = imageHeight - 94;
    }

    @Override
    protected void init() {
        super.init();
        buttons.clear();
        for (int i = 0; i < menu.quests.size(); i++) {
            int id = i;
            Button b = Button.builder(Component.translatable("gui.celestialascent.deliver"), btn -> {
                if (minecraft != null && minecraft.gameMode != null) minecraft.gameMode.handleInventoryButtonClick(menu.containerId, id);
            }).bounds(leftPos + 118, topPos + 20 + i * 24, 50, 18).build();
            buttons.add(addRenderableWidget(b));
        }
    }

    @Override
    protected void containerTick() {
        super.containerTick();
        for (int i = 0; i < buttons.size(); i++) {
            boolean done = menu.done(i);
            buttons.get(i).active = !done;
            buttons.get(i).setMessage(Component.translatable(done ? "gui.celestialascent.quest_done" : "gui.celestialascent.deliver"));
        }
    }

    @Override
    protected void renderBg(GuiGraphics g, float partialTick, int mouseX, int mouseY) {
        g.blit(BG, leftPos, topPos, 0, 0, imageWidth, imageHeight, 256, 256);
    }

    @Override
    protected void renderLabels(GuiGraphics g, int mouseX, int mouseY) {
        g.drawString(font, title, titleLabelX, titleLabelY, 0xF2E6C9, false);
        g.drawString(font, playerInventoryTitle, inventoryLabelX, inventoryLabelY, 0xBFB49A, false);
        for (int i = 0; i < menu.quests.size(); i++) {
            Quests.Quest q = menu.quests.get(i);
            int y = 20 + i * 24;
            g.renderItem(new ItemStack(q.item()), 10, y + 1);
            int color = menu.done(i) ? 0x7A8F6A : 0xF2E6C9;
            g.drawString(font, Component.translatable("gui.celestialascent.quest_line", q.count(), q.item().getDescription()), 30, y + 1, color, false);
            g.drawString(font, Coins.format(q.reward()), 30, y + 11, 0xFFD966, false);
        }
    }

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
        super.render(g, mouseX, mouseY, partialTick);
        renderTooltip(g, mouseX, mouseY);
    }
}
