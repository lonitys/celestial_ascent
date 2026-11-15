package com.celestialascent.progress;

import com.celestialascent.core.CAReg;
import com.mojang.serialization.Codec;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.neoforged.neoforge.attachment.AttachmentType;
import net.neoforged.neoforge.network.PacketDistributor;

import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
import java.util.function.Supplier;

/** Per-player record of defeated bosses. Drives constellations, keys and unlocks. */
public final class Progress {
    public static final Codec<Progress> CODEC = ResourceLocation.CODEC.listOf()
            .xmap(Progress::new, p -> new ArrayList<>(p.kills));

    public static final Supplier<AttachmentType<Progress>> TYPE = CAReg.ATTACHMENTS.register("progress",
            () -> AttachmentType.builder(() -> new Progress(List.of())).serialize(CODEC).copyOnDeath().build());

    private final Set<ResourceLocation> kills;

    public Progress(List<ResourceLocation> kills) {
        this.kills = new LinkedHashSet<>(kills);
    }

    public Set<ResourceLocation> kills() {
        return Collections.unmodifiableSet(kills);
    }

    public static Progress get(Player player) {
        return player.getData(TYPE);
    }

    public static boolean has(Player player, ResourceLocation bossId) {
        return get(player).kills.contains(bossId);
    }

    /** Records a boss kill. Returns true the first time this player defeats that boss. */
    public static boolean recordKill(ServerPlayer player, ResourceLocation bossId) {
        Progress p = get(player);
        boolean added = p.kills.add(bossId);
        if (added) {
            player.setData(TYPE, p); // marks the attachment for saving
            Constellations.apply(player);
            sync(player);
        }
        return added;
    }

    public static void sync(ServerPlayer player) {
        // Mock (gametest) players and clients without the mod have no channel for this payload.
        if (player.connection == null || !player.connection.hasChannel(ProgressSync.TYPE)) return;
        PacketDistributor.sendToPlayer(player, new ProgressSync(new ArrayList<>(get(player).kills)));
    }
}
