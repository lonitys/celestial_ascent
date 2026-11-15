package com.celestialascent.titans;

import net.minecraft.ChatFormatting;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.TooltipFlag;

import java.util.List;

/** Elemental Sigil: used on the matching shrine altar to summon its titan. */
public class SigilItem extends Item {
    public final Element element;

    public SigilItem(Element element) {
        super(new Properties().rarity(Rarity.RARE).stacksTo(16).fireResistant().component(DataComponents.ENCHANTMENT_GLINT_OVERRIDE, true));
        this.element = element;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, List<Component> lines, TooltipFlag flag) {
        lines.add(Component.translatable("tooltip.celestialascent.sigil",
                Component.translatable("block.celestialascent." + element.key + "_altar")).withStyle(ChatFormatting.GRAY));
    }
}
