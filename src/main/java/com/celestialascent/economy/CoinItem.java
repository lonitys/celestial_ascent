package com.celestialascent.economy;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;

import java.util.List;

public class CoinItem extends Item {
    public final CoinTier tier;

    public CoinItem(CoinTier tier) {
        super(new Properties().rarity(tier.rarity).fireResistant());
        this.tier = tier;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, List<Component> lines, TooltipFlag flag) {
        lines.add(Component.translatable("tooltip.celestialascent.coin_value", Coins.format(tier.value)).withStyle(ChatFormatting.GRAY));
        if (stack.getCount() > 1) {
            lines.add(Component.translatable("tooltip.celestialascent.coin_stack", Coins.format(Coins.valueOf(stack))).withStyle(ChatFormatting.DARK_GRAY));
        }
    }
}
