package com.celestialascent.progress;

import com.celestialascent.CelestialAscent;
import net.minecraft.core.Holder;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.neoforged.neoforge.common.NeoForgeMod;

import java.util.List;

/**
 * One constellation per boss. Defeating the boss adds its constellation to the player's night sky
 * and grants a small permanent bonus. Stars are (azimuth deg, altitude deg); lines join star indices.
 */
public final class Constellations {
    private Constellations() {}

    public record Entry(ResourceLocation boss, String key, Holder<Attribute> attribute, double amount,
                        AttributeModifier.Operation op, int color, float[][] stars, int[][] lines) {}

    private static ResourceLocation id(String path) {
        return ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, path);
    }

    public static final List<Entry> ALL = List.of(
            new Entry(id("frost_titan"), "frost", Attributes.ARMOR, 1, AttributeModifier.Operation.ADD_VALUE, 0x9FE8FF,
                    new float[][]{{20, 40}, {26, 46}, {32, 42}, {30, 34}, {24, 33}}, new int[][]{{0, 1}, {1, 2}, {2, 3}, {3, 4}, {4, 0}}),
            new Entry(id("tide_titan"), "tide", Attributes.OXYGEN_BONUS, 1, AttributeModifier.Operation.ADD_VALUE, 0x3FA9FF,
                    new float[][]{{60, 30}, {66, 36}, {72, 32}, {78, 38}, {84, 33}}, new int[][]{{0, 1}, {1, 2}, {2, 3}, {3, 4}}),
            new Entry(id("storm_titan"), "storm", Attributes.MOVEMENT_SPEED, 0.03, AttributeModifier.Operation.ADD_MULTIPLIED_BASE, 0xE6E27A,
                    new float[][]{{110, 55}, {114, 48}, {108, 44}, {113, 37}, {107, 30}}, new int[][]{{0, 1}, {1, 2}, {2, 3}, {3, 4}}),
            new Entry(id("magma_titan"), "magma", Attributes.BURNING_TIME, -0.1, AttributeModifier.Operation.ADD_MULTIPLIED_BASE, 0xFF7A2E,
                    new float[][]{{150, 35}, {156, 42}, {162, 35}, {156, 28}, {156, 35}}, new int[][]{{0, 1}, {1, 2}, {2, 3}, {3, 0}, {1, 4}, {4, 3}}),
            new Entry(ResourceLocation.withDefaultNamespace("ender_dragon"), "dragon", Attributes.MAX_HEALTH, 2, AttributeModifier.Operation.ADD_VALUE, 0xC77DFF,
                    new float[][]{{190, 50}, {198, 56}, {206, 52}, {214, 58}, {222, 54}, {204, 44}}, new int[][]{{0, 1}, {1, 2}, {2, 3}, {3, 4}, {2, 5}}),
            new Entry(id("ender_colossus"), "colossus", Attributes.ARMOR_TOUGHNESS, 1, AttributeModifier.Operation.ADD_VALUE, 0x8E6BFF,
                    new float[][]{{240, 30}, {240, 42}, {250, 42}, {250, 30}, {245, 50}}, new int[][]{{0, 1}, {1, 2}, {2, 3}, {3, 0}, {1, 4}, {2, 4}}),
            new Entry(id("astral_seraph"), "seraph", Attributes.ENTITY_INTERACTION_RANGE, 0.5, AttributeModifier.Operation.ADD_VALUE, 0xFFFFFF,
                    new float[][]{{280, 45}, {272, 52}, {264, 48}, {288, 52}, {296, 48}, {280, 36}}, new int[][]{{0, 1}, {1, 2}, {0, 3}, {3, 4}, {0, 5}}),
            new Entry(id("nebula_leviathan"), "leviathan", NeoForgeMod.SWIM_SPEED, 0.1, AttributeModifier.Operation.ADD_MULTIPLIED_BASE, 0xB45CFF,
                    new float[][]{{310, 28}, {318, 34}, {326, 30}, {334, 36}, {342, 32}, {350, 38}}, new int[][]{{0, 1}, {1, 2}, {2, 3}, {3, 4}, {4, 5}}),
            new Entry(id("sun_herald"), "herald", Attributes.MAX_HEALTH, 2, AttributeModifier.Operation.ADD_VALUE, 0xFFC93C,
                    new float[][]{{0, 70}, {8, 64}, {-8, 64}, {5, 76}, {-5, 76}}, new int[][]{{0, 1}, {0, 2}, {0, 3}, {0, 4}}),
            new Entry(id("void_sovereign"), "sovereign", Attributes.ATTACK_DAMAGE, 0.05, AttributeModifier.Operation.ADD_MULTIPLIED_BASE, 0x5E2B97,
                    new float[][]{{180, 80}, {170, 74}, {190, 74}, {175, 66}, {185, 66}}, new int[][]{{0, 1}, {0, 2}, {1, 3}, {2, 4}, {3, 4}})
    );

    private static ResourceLocation modifierId(Entry e) {
        return id("constellation_" + e.key());
    }

    /** Re-applies every unlocked constellation bonus as a transient attribute modifier. */
    public static void apply(ServerPlayer player) {
        var kills = Progress.get(player).kills();
        for (Entry e : ALL) {
            AttributeInstance inst = player.getAttribute(e.attribute());
            if (inst == null) continue;
            ResourceLocation mid = modifierId(e);
            if (kills.contains(e.boss())) {
                inst.addOrUpdateTransientModifier(new AttributeModifier(mid, e.amount(), e.op()));
            } else {
                inst.removeModifier(mid);
            }
        }
    }
}
