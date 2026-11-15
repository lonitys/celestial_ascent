package com.celestialascent.titans;

import com.mojang.serialization.Codec;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.util.StringRepresentable;

/** The four titan elements. */
public enum Element implements StringRepresentable {
    FROST("frost", 0x9FE8FF),
    TIDE("tide", 0x3FA9FF),
    STORM("storm", 0xE6E27A),
    MAGMA("magma", 0xFF7A2E);

    public static final Codec<Element> CODEC = StringRepresentable.fromEnum(Element::values);
    public static final StreamCodec<ByteBuf, Element> STREAM_CODEC = ByteBufCodecs.idMapper(i -> values()[i], Element::ordinal);

    public final String key;
    public final int color;

    Element(String key, int color) {
        this.key = key;
        this.color = color;
    }

    @Override
    public String getSerializedName() {
        return key;
    }
}
