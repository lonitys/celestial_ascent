package com.celestialascent.client;

import com.celestialascent.economy.Coins;
import com.celestialascent.economy.ShopStallBlockEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import org.joml.Matrix4f;

/** Shows the item for sale spinning above the stall counter with its price. */
public class ShopStallRenderer implements BlockEntityRenderer<ShopStallBlockEntity> {
    private final Font font;

    public ShopStallRenderer(BlockEntityRendererProvider.Context ctx) {
        this.font = ctx.getFont();
    }

    @Override
    public void render(ShopStallBlockEntity be, float partialTick, PoseStack pose, MultiBufferSource buffers, int light, int overlay) {
        ItemStack stack = be.template();
        if (stack.isEmpty() || be.getLevel() == null) return;
        float time = be.getLevel().getGameTime() + partialTick;

        pose.pushPose();
        pose.translate(0.5, 0.98 + Math.sin(time / 12.0) * 0.04, 0.5);
        pose.mulPose(Axis.YP.rotationDegrees(time * 2f));
        pose.scale(0.45f, 0.45f, 0.45f);
        Minecraft.getInstance().getItemRenderer().renderStatic(stack, ItemDisplayContext.FIXED, LightTexture.FULL_BRIGHT,
                OverlayTexture.NO_OVERLAY, pose, buffers, be.getLevel(), 0);
        pose.popPose();

        String label = Coins.format(be.price()) + (be.bundle() > 1 ? "  ×" + be.bundle() : "");
        pose.pushPose();
        pose.translate(0.5, 1.42, 0.5);
        pose.mulPose(Minecraft.getInstance().getEntityRenderDispatcher().cameraOrientation());
        pose.scale(0.02f, -0.02f, 0.02f);
        Matrix4f m = pose.last().pose();
        float x = -font.width(label) / 2f;
        font.drawInBatch(label, x, 0, 0xFFD966, false, m, buffers, Font.DisplayMode.NORMAL, 0x60000000, LightTexture.FULL_BRIGHT);
        pose.popPose();
    }
}
