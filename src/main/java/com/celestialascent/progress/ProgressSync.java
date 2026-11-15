package com.celestialascent.progress;

import com.celestialascent.CelestialAscent;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.neoforge.network.handling.IPayloadContext;

import java.util.List;

/** Server to client: the player's defeated bosses (for the constellation sky). */
public record ProgressSync(List<ResourceLocation> kills) implements CustomPacketPayload {
    public static final Type<ProgressSync> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "progress_sync"));
    public static final StreamCodec<ByteBuf, ProgressSync> STREAM_CODEC =
            ResourceLocation.STREAM_CODEC.apply(ByteBufCodecs.list()).map(ProgressSync::new, ProgressSync::kills);

    @Override
    public Type<? extends CustomPacketPayload> type() {
        return TYPE;
    }

    /** Client-side copy, read by the sky renderer. */
    public static volatile List<ResourceLocation> clientKills = List.of();

    public static void handle(ProgressSync msg, IPayloadContext ctx) {
        ctx.enqueueWork(() -> clientKills = List.copyOf(msg.kills()));
    }
}
