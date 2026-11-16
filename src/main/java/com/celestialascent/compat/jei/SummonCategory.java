package com.celestialascent.compat.jei;

import com.celestialascent.CelestialAscent;
import com.celestialascent.boss.BossDrops;
import com.celestialascent.boss.BossSummons;
import com.celestialascent.stars.Stars;
import com.mojang.logging.LogUtils;
import mezz.jei.api.gui.builder.IRecipeLayoutBuilder;
import mezz.jei.api.gui.builder.ITooltipBuilder;
import mezz.jei.api.gui.drawable.IDrawable;
import mezz.jei.api.gui.ingredient.IRecipeSlotsView;
import mezz.jei.api.helpers.IGuiHelper;
import mezz.jei.api.recipe.IFocusGroup;
import mezz.jei.api.recipe.RecipeIngredientRole;
import mezz.jei.api.recipe.RecipeType;
import mezz.jei.api.recipe.category.IRecipeCategory;
import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.InventoryScreen;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.network.chat.Component;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.boss.enderdragon.EnderDragon;
import net.minecraft.world.item.ItemStack;
import org.joml.Matrix4f;
import org.joml.Quaternionf;
import org.joml.Vector3f;
import org.joml.Vector4f;
import org.slf4j.Logger;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * Boss summoning: the altar or throne and the offering on the left, the boss turning slowly in the
 * middle (its tooltip gives health and where to find it), its drops on the right.
 */
final class SummonCategory implements IRecipeCategory<BossSummons.Summon> {
    static final RecipeType<BossSummons.Summon> TYPE = RecipeType.create(CelestialAscent.MODID, "summon", BossSummons.Summon.class);

    private static final int WIDTH = 150, HEIGHT = 108;
    /** The boss stands in this box (feet on its bottom edge). */
    private static final int BOX_X0 = 24, BOX_X1 = 108, BOX_Y0 = 2, BOX_Y1 = 62;
    private static final int TEXT = 0xFF404040;
    private static final float SMALL = 0.75f;
    private static final Logger LOGGER = LogUtils.getLogger();

    /**
     * Bosses whose model reaches well past their hitbox: {width while turning, height, lift} in blocks,
     * where lift raises the feet for models that hang below their origin.
     */
    private static final Map<EntityType<?>, float[]> VISUAL_SIZE = new HashMap<>();

    private final IDrawable icon;
    private final Component title = Component.translatable("jei.celestialascent.summon");
    private final Map<EntityType<?>, Optional<LivingEntity>> entities = new HashMap<>();
    private ClientLevel entityLevel;

    SummonCategory(IGuiHelper gui) {
        this.icon = gui.createDrawableItemLike(Stars.SERAPH_ALTAR.get());
        VISUAL_SIZE.put(Stars.SERAPH.get(), new float[]{4.6f, 3.6f, 0f});
        VISUAL_SIZE.put(Stars.LEVIATHAN.get(), new float[]{6.5f, 3.0f, 0.5f});
    }

    @Override
    public RecipeType<BossSummons.Summon> getRecipeType() {
        return TYPE;
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
    public void setRecipe(IRecipeLayoutBuilder builder, BossSummons.Summon s, IFocusGroup focuses) {
        for (int i = 0; i < s.inputs().size(); i++) {
            builder.addSlot(RecipeIngredientRole.INPUT, 4, 10 + i * 20).setStandardSlotBackground().addItemStack(s.inputs().get(i).get());
        }
        List<BossDrops.Drop> drops = BossSummons.drops(s);
        for (int i = 0; i < drops.size(); i++) {
            BossDrops.Drop d = drops.get(i);
            builder.addSlot(RecipeIngredientRole.OUTPUT, WIDTH - 37 + (i % 2) * 18, 4 + (i / 2) * 18).setStandardSlotBackground()
                    .addItemStack(new ItemStack(d.item().get(), d.max()))
                    .addRichTooltipCallback((view, tooltip) -> {
                        String count = d.min() == d.max() ? String.valueOf(d.min()) : d.min() + "–" + d.max();
                        tooltip.add(Component.translatable("jei.celestialascent.drop_count", count).withStyle(ChatFormatting.GOLD));
                        if (d.looting()) tooltip.add(Component.translatable("jei.celestialascent.drop_looting").withStyle(ChatFormatting.GRAY));
                    });
        }
    }

    @Override
    public void draw(BossSummons.Summon s, IRecipeSlotsView slots, GuiGraphics g, double mouseX, double mouseY) {
        Font font = Minecraft.getInstance().font;
        entity(s.type().get()).ifPresent(e -> renderBoss(g, e));
        Component name = s.type().get().getDescription();
        g.drawString(font, name, (WIDTH - font.width(name)) / 2, BOX_Y1 + 3, TEXT, false);
        // Where to go, in small text over the full width.
        List<FormattedCharSequence> lines = font.split(Component.translatable(s.whereKey()), (int) (WIDTH / SMALL));
        g.pose().pushPose();
        g.pose().translate(0, BOX_Y1 + 14, 0);
        g.pose().scale(SMALL, SMALL, 1);
        for (int i = 0; i < lines.size(); i++) {
            FormattedCharSequence line = lines.get(i);
            g.drawString(font, line, (int) ((WIDTH / SMALL - font.width(line)) / 2), i * font.lineHeight, TEXT, false);
        }
        g.pose().popPose();
    }

    @Override
    public void getTooltip(ITooltipBuilder tooltip, BossSummons.Summon s, IRecipeSlotsView slots, double mouseX, double mouseY) {
        if (mouseX < BOX_X0 || mouseX >= BOX_X1 || mouseY < BOX_Y0 || mouseY >= BOX_Y1 + 12) return;
        tooltip.add(s.type().get().getDescription());
        entity(s.type().get()).ifPresent(e -> tooltip.add(
                Component.translatable("jei.celestialascent.health", Mth.ceil(e.getMaxHealth())).withStyle(ChatFormatting.RED)));
        if (s.type().get() != EntityType.ENDER_DRAGON) {
            tooltip.add(Component.translatable("jei.celestialascent.drop_each").withStyle(ChatFormatting.GRAY));
        }
    }

    /** One display copy per boss type, made in the current client level (empty if it cannot be made). */
    private Optional<LivingEntity> entity(EntityType<?> type) {
        ClientLevel level = Minecraft.getInstance().level;
        if (level == null) return Optional.empty();
        if (level != entityLevel) {
            entities.clear();
            entityLevel = level;
        }
        return entities.computeIfAbsent(type, t -> {
            try {
                Entity e = t.create(level);
                return e instanceof LivingEntity living ? Optional.of(living) : Optional.empty();
            } catch (RuntimeException ex) {
                LOGGER.warn("JEI: cannot create a display copy of {}", t, ex);
                return Optional.empty();
            }
        });
    }

    /** Draws the boss standing in its box, scaled to fit and turning slowly. */
    private void renderBoss(GuiGraphics g, LivingEntity e) {
        float boxW = BOX_X1 - BOX_X0, boxH = BOX_Y1 - BOX_Y0;
        boolean dragon = e instanceof EnderDragon;
        float[] size = VISUAL_SIZE.get(e.getType());
        float scale;
        if (dragon) scale = boxW / 15f; // seen from above, its wings span about 13 blocks
        else if (size != null) scale = Math.min(boxH * 0.95f / size[1], boxW * 0.95f / size[0]);
        else scale = Math.min(boxH * 0.92f / e.getBbHeight(), boxW * 0.62f / e.getBbWidth());
        // Facing the viewer, turned by the pose (the dragon's renderer ignores the entity's yaw).
        float spin = (System.currentTimeMillis() % 14400L) / 40f * Mth.DEG_TO_RAD;
        e.yBodyRot = e.yBodyRotO = 180f;
        e.setYRot(180f);
        e.yRotO = 180f;
        e.yHeadRot = e.yHeadRotO = 180f;
        e.setXRot(0);
        e.xRotO = 0;
        Quaternionf tilt = new Quaternionf().rotateX((dragon ? -28f : -8f) * Mth.DEG_TO_RAD);
        Quaternionf pose = new Quaternionf().rotateZ(Mth.PI).mul(tilt).rotateY(spin);
        float feet = dragon ? BOX_Y1 - 14 : BOX_Y1 - 2 - (size != null ? size[2] * scale : 0);
        // Wings and tails must not cover the slots or the text: clip to the box (scissor works in screen space).
        Matrix4f m = g.pose().last().pose();
        Vector4f lo = m.transform(new Vector4f(BOX_X0, BOX_Y0, 0, 1)), hi = m.transform(new Vector4f(BOX_X1, BOX_Y1, 0, 1));
        g.enableScissor(Mth.floor(lo.x), Mth.floor(lo.y), Mth.ceil(hi.x), Mth.ceil(hi.y));
        try {
            InventoryScreen.renderEntityInInventory(g, (BOX_X0 + BOX_X1) / 2f, feet, scale, new Vector3f(), pose, tilt, e);
        } catch (RuntimeException ex) {
            LOGGER.warn("JEI: cannot render {}", e.getType(), ex);
            entities.put(e.getType(), Optional.empty());
        } finally {
            g.disableScissor();
        }
    }
}
