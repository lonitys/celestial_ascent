package com.celestialascent.boss;

import com.celestialascent.CelestialAscent;
import io.netty.buffer.ByteBuf;
import net.minecraft.core.UUIDUtil;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.neoforge.network.handling.IPayloadContext;

import java.util.UUID;

/**
 * Server to client: which boss a boss bar belongs to and its stage (for the custom boss bar);
 * {@code announce} plays the stage banner because the boss has just evolved.
 */
public record BossStagePayload(UUID bar, ResourceLocation boss, int stage, int color, boolean announce) implements CustomPacketPayload {
    public static final Type<BossStagePayload> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "boss_stage"));
    public static final StreamCodec<ByteBuf, BossStagePayload> STREAM_CODEC = StreamCodec.composite(
            UUIDUtil.STREAM_CODEC, BossStagePayload::bar,
            ResourceLocation.STREAM_CODEC, BossStagePayload::boss,
            ByteBufCodecs.VAR_INT, BossStagePayload::stage,
            ByteBufCodecs.INT, BossStagePayload::color,
            ByteBufCodecs.BOOL, BossStagePayload::announce,
            BossStagePayload::new);

    @Override
    public Type<? extends CustomPacketPayload> type() {
        return TYPE;
    }

    public static void handle(BossStagePayload msg, IPayloadContext ctx) {
        ctx.enqueueWork(() -> com.celestialascent.client.BossBarOverlay.accept(msg)); // only ever runs on the client
    }
}
