package com.celestialascent.titans;

import com.celestialascent.armor.CelestialArmorItem;
import com.celestialascent.armor.SetId;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;

import java.util.List;

/** Titan armor piece. Its element (data component) decides abilities and texture. */
public class TitanArmorItem extends CelestialArmorItem {
    public TitanArmorItem(Type type, Properties props) {
        super(SetId.TITAN, type, props);
    }

    public static Element element(ItemStack stack) {
        return stack.get(Titans.ELEMENT.get());
    }

    @Override
    public String textureVariant(ItemStack stack) {
        Element e = element(stack);
        return e == null ? "" : "_" + e.key;
    }

    @Override
    public Component getName(ItemStack stack) {
        Element e = element(stack);
        if (e == null) return super.getName(stack);
        return Component.translatable("item.celestialascent.titan_infused",
                Component.translatable("element.celestialascent." + e.key), super.getName(stack)).withColor(e.color);
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, List<Component> lines, TooltipFlag flag) {
        Element e = element(stack);
        if (e != null) {
            lines.add(Component.translatable("tooltip.celestialascent.element", Component.translatable("element.celestialascent." + e.key))
                    .withColor(e.color));
        } else {
            lines.add(Component.translatable("tooltip.celestialascent.no_element").withStyle(ChatFormatting.DARK_GRAY));
        }
        super.appendHoverText(stack, ctx, lines, flag);
    }
}
