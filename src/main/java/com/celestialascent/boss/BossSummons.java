package com.celestialascent.boss;

import com.celestialascent.abyss.Abyss;
import com.celestialascent.empire.Empire;
import com.celestialascent.stars.Stars;
import com.celestialascent.titans.Element;
import com.celestialascent.titans.Titans;
import com.google.common.base.Suppliers;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ItemLike;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;

/**
 * How each boss is called, for recipe viewers: the altar or throne block and the offering, plus a
 * translation key that says where to go. The Ender Dragon is listed too, because it drops the Dragon Heart.
 */
public final class BossSummons {
    private BossSummons() {}

    /** {@code inputs}: the summoning block first, then the offering; {@code whereKey}: where and how. */
    public record Summon(Supplier<? extends EntityType<?>> type, List<Supplier<ItemStack>> inputs, String whereKey) {}

    private static final String WHERE = "jei.celestialascent.where.";

    /** The Ender Dragon's loot table is vanilla's; this mod adds the Dragon Heart for every player nearby. */
    private static final Supplier<List<BossDrops.Drop>> DRAGON_DROPS =
            Suppliers.memoize(() -> List.of(new BossDrops.Drop(Empire.DRAGON_HEART, 1, 1, false)));

    private static final Supplier<List<Summon>> ALL = Suppliers.memoize(BossSummons::build);

    /** Every summon in ladder order (titans, the dragon, the empire, the stars, the abyss). */
    public static List<Summon> all() {
        return ALL.get();
    }

    /** What the boss drops: its {@link BossDrops} table, or the Dragon Heart for the Ender Dragon. */
    public static List<BossDrops.Drop> drops(Summon s) {
        EntityType<?> type = s.type().get();
        if (type == EntityType.ENDER_DRAGON) return DRAGON_DROPS.get();
        return BossDrops.of(type).map(BossDrops.Entry::drops).orElse(List.of());
    }

    private static Supplier<ItemStack> stack(Supplier<? extends ItemLike> item, int count) {
        return () -> new ItemStack(item.get(), count);
    }

    private static List<Summon> build() {
        List<Summon> out = new ArrayList<>();
        for (Element e : Element.values()) {
            out.add(new Summon(() -> Titans.titanType(e), List.of(stack(Titans.ALTARS.get(e), 1), stack(Titans.SIGILS.get(e), 1)), WHERE + "shrine"));
        }
        out.add(new Summon(() -> EntityType.ENDER_DRAGON, List.of(), WHERE + "end"));
        out.add(new Summon(Empire.SENTINEL, List.of(stack(Empire.PYLON, 1)), WHERE + "capital"));
        out.add(new Summon(Empire.COLOSSUS, List.of(stack(Empire.THRONE, 1), stack(Empire.DRAGON_HEART, 1)), WHERE + "throne"));
        out.add(new Summon(Stars.SERAPH, List.of(stack(Stars.SERAPH_ALTAR, 1), stack(Stars.STARDUST, 16)), WHERE + "fallen_stars"));
        out.add(new Summon(Stars.LEVIATHAN, List.of(stack(Stars.LEVIATHAN_ALTAR, 1), stack(Stars.STARDUST, 16)), WHERE + "fallen_stars"));
        out.add(new Summon(Stars.HERALD, List.of(stack(Stars.HERALD_ALTAR, 1), stack(Stars.STARDUST, 16)), WHERE + "herald"));
        out.add(new Summon(Abyss.VOID_SOVEREIGN, List.of(stack(Abyss.ABYSSAL_BEACON, 1)), WHERE + "abyss"));
        return List.copyOf(out);
    }
}
