package com.celestialascent.core;

import net.neoforged.neoforge.common.ModConfigSpec;

/** Server-side tunables (config/celestialascent-common.toml). */
public final class ModConfig {
    private ModConfig() {}
    public static final ModConfigSpec SPEC;
    public static final ModConfigSpec.DoubleValue BOSS_HEALTH_MULT;
    public static final ModConfigSpec.DoubleValue BOSS_DAMAGE_MULT;
    public static final ModConfigSpec.DoubleValue BOSS_SCALE_PER_PLAYER;
    public static final ModConfigSpec.DoubleValue BOSS_LOOT_SHARE;
    public static final ModConfigSpec.DoubleValue ABYSS_CRUMBLE_SPEED;
    public static final ModConfigSpec.IntValue EMERALD_TO_COPPER;
    public static final ModConfigSpec.BooleanValue PROJECTE_REPAIR;
    public static final ModConfigSpec.BooleanValue GIVE_CODEX;
    public static final ModConfigSpec.BooleanValue RETROGEN;
    public static final ModConfigSpec.IntValue RETROGEN_RADIUS;
    public static final ModConfigSpec.IntValue RETROGEN_AVOID_MINUTES;

    static {
        ModConfigSpec.Builder b = new ModConfigSpec.Builder();
        b.push("bosses");
        BOSS_HEALTH_MULT = b.comment("Multiplier for every boss's base health").defineInRange("healthMultiplier", 1.0, 0.1, 20.0);
        BOSS_DAMAGE_MULT = b.comment("Multiplier for every boss's damage").defineInRange("damageMultiplier", 1.0, 0.1, 20.0);
        BOSS_SCALE_PER_PLAYER = b.comment("Extra max health per additional player within 64 blocks (0.5 = +50% each)").defineInRange("scalePerPlayer", 0.5, 0.0, 5.0);
        BOSS_LOOT_SHARE = b.comment("Fraction of a boss's max health a player must deal to receive loot").defineInRange("lootShare", 0.05, 0.0, 1.0);
        b.pop();
        b.push("abyss");
        ABYSS_CRUMBLE_SPEED = b.comment("Multiplier for how fast abyssal blocks crumble").defineInRange("crumbleSpeed", 1.0, 0.0, 10.0);
        b.pop();
        b.push("economy");
        EMERALD_TO_COPPER = b.comment("Copper Asters a banker pays per emerald").defineInRange("emeraldToCopper", 5, 1, 1000);
        b.pop();
        b.push("projecte");
        PROJECTE_REPAIR = b.comment("When ProjectE is installed, mod armor repairs itself using the wearer's EMC").define("emcRepair", true);
        b.pop();
        b.push("codex");
        GIVE_CODEX = b.comment("Give every player a Celestial Codex (the in-game guide) the first time they join").define("giveOnFirstJoin", true);
        b.pop();
        b.push("existingWorlds");
        RETROGEN = b.comment("Build shrines, cities, the Ruined Capital and the Star Gate into land generated before this mod was installed.",
                "Spots with player builds, other structures or unusable ground are skipped and a free spot nearby is used instead.")
                .define("buildIntoExploredLand", true);
        RETROGEN_RADIUS = b.comment("Around each player who logs in, check this many chunks for structures to build").defineInRange("checkRadiusChunks", 40, 8, 128);
        RETROGEN_AVOID_MINUTES = b.comment("Never build in chunks where players have spent more than this many minutes (bases). 0 turns the check off")
                .defineInRange("avoidChunksVisitedMinutes", 30, 0, 100000);
        b.pop();
        SPEC = b.build();
    }
}
