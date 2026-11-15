package com.celestialascent.guide;

import com.celestialascent.CelestialAscent;
import com.celestialascent.compat.Emc;
import com.celestialascent.core.CAReg;
import com.celestialascent.core.Content;
import com.celestialascent.core.ModConfig;
import com.mojang.serialization.Codec;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.attachment.AttachmentType;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.registries.DeferredItem;

import java.util.function.Supplier;

/** The Celestial Codex: an in-game guide every player receives once. */
@EventBusSubscriber(modid = CelestialAscent.MODID)
public final class Guide {
    private Guide() {}

    public static final DeferredItem<GuideBookItem> CODEX = Content.item("celestial_codex",
            () -> new GuideBookItem(new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON)));

    /** Whether this player has already been given a codex (kept through death). */
    public static final Supplier<AttachmentType<Boolean>> RECEIVED = CAReg.ATTACHMENTS.register("received_codex",
            () -> AttachmentType.builder(() -> false).serialize(Codec.BOOL).copyOnDeath().build());

    /** Gives the codex the first time a player joins. Returns true if it was given now. */
    public static boolean giveOnce(ServerPlayer player) {
        if (player.getData(RECEIVED)) return false;
        player.setData(RECEIVED, true);
        ItemStack book = new ItemStack(CODEX.get());
        if (!player.getInventory().add(book)) player.drop(book, false);
        player.sendSystemMessage(Component.translatable("message.celestialascent.codex_given").withStyle(ChatFormatting.GOLD));
        return true;
    }

    @SubscribeEvent
    public static void login(PlayerEvent.PlayerLoggedInEvent e) {
        if (e.getEntity() instanceof ServerPlayer p && ModConfig.GIVE_CODEX.get()) giveOnce(p);
    }

    public static void init() {
        Emc.set(CODEX, 512);
    }
}
