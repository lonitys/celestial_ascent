package com.celestialascent.armor;

import com.celestialascent.armor.client.CelestialArmorRenderer;
import net.minecraft.ChatFormatting;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.Unbreakable;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.animatable.GeoItem;
import software.bernie.geckolib.animatable.client.GeoRenderProvider;
import software.bernie.geckolib.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.animation.AnimatableManager;
import software.bernie.geckolib.animation.AnimationController;
import software.bernie.geckolib.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

import java.util.List;
import java.util.function.Consumer;

/**
 * Armor piece of one of the five sets, rendered as a 3D GeckoLib model
 * (geo/item/armor/&lt;set&gt;_armor.geo.json, textures/item/armor/&lt;set&gt;_armor[variant].png).
 */
public class CelestialArmorItem extends ArmorItem implements GeoItem {
    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("idle");
    public final SetId set;
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);

    public CelestialArmorItem(SetId set, Type type, Properties props) {
        super(ArmorTiers.material(set), type, configure(set, type, props));
        this.set = set;
    }

    private static Properties configure(SetId set, Type type, Properties p) {
        p = p.stacksTo(1).rarity(set.rarity).fireResistant();
        if (set.durability > 0) {
            p = p.durability(type.getDurability(set.durability));
        } else {
            p = p.component(DataComponents.UNBREAKABLE, new Unbreakable(false));
        }
        return p;
    }

    /** Texture suffix for this stack (e.g. titan element); "" for the default texture. */
    public String textureVariant(ItemStack stack) {
        return "";
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, List<Component> lines, TooltipFlag flag) {
        lines.add(Component.translatable("tooltip.celestialascent.set." + set.key).withStyle(ChatFormatting.GOLD));
        for (int i = 1; i <= 6; i++) {
            String key = "tooltip.celestialascent.set." + set.key + "." + i;
            if (!net.minecraft.locale.Language.getInstance().has(key)) break;
            lines.add(Component.literal(" ").append(Component.translatable(key)).withStyle(ChatFormatting.GRAY));
        }
        // What the set ability gains at set stages II and III (the lowest stage of the four pieces counts).
        for (int st = 2; st <= ArmorStages.MAX_STAGE; st++) {
            boolean active = ArmorStages.stage(stack) >= st;
            lines.add(Component.literal(" ").append(Component.translatable("tooltip.celestialascent.set_stage." + set.key + "." + st))
                    .withStyle(active ? ChatFormatting.AQUA : ChatFormatting.DARK_GRAY));
        }
        ArmorStages.tooltip(stack, lines);
        super.appendHoverText(stack, ctx, lines, flag);
    }

    @Override
    public void createGeoRenderer(Consumer<GeoRenderProvider> consumer) {
        consumer.accept(new GeoRenderProvider() {
            private CelestialArmorRenderer renderer;

            @Override
            public <T extends LivingEntity> HumanoidModel<?> getGeoArmorRenderer(@Nullable T entity, ItemStack stack,
                                                                                 @Nullable EquipmentSlot slot, @Nullable HumanoidModel<T> original) {
                if (renderer == null) renderer = new CelestialArmorRenderer(set);
                return renderer;
            }
        });
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "idle", 0, state -> state.setAndContinue(IDLE)));
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return cache;
    }
}
