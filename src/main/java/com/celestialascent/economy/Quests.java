package com.celestialascent.economy;

import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;

/** Daily delivery quests offered by quest boards. Each board rolls three quests per in-game day. */
public final class Quests {
    private Quests() {}

    public record Quest(Item item, int count, long reward, int prosperity) {
        public void write(RegistryFriendlyByteBuf buf) {
            buf.writeResourceLocation(BuiltInRegistries.ITEM.getKey(item));
            buf.writeVarInt(count);
            buf.writeVarLong(reward);
            buf.writeVarInt(prosperity);
        }

        public static Quest read(RegistryFriendlyByteBuf buf) {
            Item item = BuiltInRegistries.ITEM.get(buf.readResourceLocation());
            return new Quest(item, buf.readVarInt(), buf.readVarLong(), buf.readVarInt());
        }
    }

    private record Template(Supplier<Item> item, int min, int max, long unitPrice) {}

    private static final List<Template> POOL = new ArrayList<>();

    static void add(Supplier<Item> item, int min, int max, long unit) {
        POOL.add(new Template(item, min, max, unit));
    }

    static {
        add(() -> Items.WHEAT, 24, 48, 1);
        add(() -> Items.BREAD, 12, 24, 3);
        add(() -> Items.COOKED_BEEF, 12, 24, 4);
        add(() -> Items.OAK_LOG, 32, 64, 1);
        add(() -> Items.COBBLESTONE, 48, 64, 1);
        add(() -> Items.GLASS, 24, 48, 2);
        add(() -> Items.COAL, 24, 48, 2);
        add(() -> Items.IRON_INGOT, 8, 24, 8);
        add(() -> Items.GOLD_INGOT, 6, 16, 12);
        add(() -> Items.REDSTONE, 24, 48, 3);
        add(() -> Items.LAPIS_LAZULI, 16, 32, 4);
        add(() -> Items.DIAMOND, 2, 5, 90);
        add(() -> Items.BONE, 16, 32, 3);
        add(() -> Items.STRING, 16, 32, 3);
        add(() -> Items.GUNPOWDER, 12, 24, 6);
        add(() -> Items.LEATHER, 12, 24, 4);
        add(() -> Items.BOOK, 4, 10, 12);
        add(() -> Items.ENDER_PEARL, 4, 8, 25);
        add(() -> Items.BLAZE_ROD, 4, 8, 30);
        add(() -> Items.SLIME_BALL, 6, 12, 15);
        add(() -> Items.AMETHYST_SHARD, 8, 16, 10);
        add(() -> Items.PHANTOM_MEMBRANE, 3, 6, 40);
    }

    /** The three quests a board at {@code pos} offers on {@code day}. */
    public static List<Quest> forBoard(BlockPos pos, long day) {
        RandomSource r = RandomSource.create(pos.asLong() * 31 + day * 0x9E3779B97F4A7C15L);
        List<Template> pool = new ArrayList<>(POOL);
        List<Quest> out = new ArrayList<>(3);
        for (int i = 0; i < 3 && !pool.isEmpty(); i++) {
            Template t = pool.remove(r.nextInt(pool.size()));
            int count = t.min + r.nextInt(t.max - t.min + 1);
            long reward = Math.max(10, Math.round(count * t.unitPrice * (1.0 + r.nextDouble() * 0.5)));
            out.add(new Quest(t.item.get(), count, reward, (int) Math.max(5, reward / 3)));
        }
        return out;
    }
}
