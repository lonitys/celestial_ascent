package com.celestialascent.armor;

import com.celestialascent.CelestialAscent;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.neoforge.network.handling.IPayloadContext;

/** Client to server: an armor ability key was pressed (0 = primary, 1 = toggle). */
public record AbilityKey(int key) implements CustomPacketPayload {
    public static final Type<AbilityKey> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "ability_key"));
    public static final StreamCodec<ByteBuf, AbilityKey> STREAM_CODEC = ByteBufCodecs.VAR_INT.map(AbilityKey::new, AbilityKey::key);

    @Override
    public Type<? extends CustomPacketPayload> type() {
        return TYPE;
    }

    public static void handle(AbilityKey msg, IPayloadContext ctx) {
        ctx.enqueueWork(() -> {
            if (ctx.player() instanceof ServerPlayer sp && (msg.key == 0 || msg.key == 1)) ArmorSets.onKey(sp, msg.key);
        });
    }
}
