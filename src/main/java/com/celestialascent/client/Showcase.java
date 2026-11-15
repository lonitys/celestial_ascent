package com.celestialascent.client;

import com.celestialascent.CelestialAscent;
import com.celestialascent.core.Content;
import com.celestialascent.progress.Constellations;
import com.celestialascent.progress.Progress;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.ClientTickEvent;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

/**
 * Development-only visual verification: with -Dcelestialascent.showcase=true the client runs a
 * scripted tour of the mod's content in singleplayer and saves screenshots to screenshots/ca_*.png.
 */
@EventBusSubscriber(modid = CelestialAscent.MODID, value = Dist.CLIENT)
public final class Showcase {
    private Showcase() {}

    private static final boolean ENABLED = Boolean.getBoolean("celestialascent.showcase");
    private static final String ONLY = System.getProperty("celestialascent.showcase.only", "");

    private record Step(int ticks, Consumer<ServerPlayer> server, String shot, float yaw, float pitch, CameraType camera) {}

    private static final List<Step> STEPS = new ArrayList<>();
    private static int index = -1, timer = 0, startDelay = 100;

    private static void cmd(ServerPlayer p, String c) {
        MinecraftServer s = p.server;
        s.getCommands().performPrefixedCommand(p.createCommandSourceStack().withPermission(4).withSuppressedOutput(), c);
    }

    private static void step(int wait, String shot, float yaw, float pitch, String... commands) {
        STEPS.add(new Step(wait, p -> { for (String c : commands) cmd(p, c); }, shot, yaw, pitch, CameraType.FIRST_PERSON));
    }

    private static void step(int wait, String shot, float yaw, float pitch, CameraType cam, Consumer<ServerPlayer> action) {
        STEPS.add(new Step(wait, action, shot, yaw, pitch, cam));
    }

    private static String stand(int x, String set, String element) {
        String comp = element == null ? "" : ",components:{\"celestialascent:element\":\"" + element + "\"}";
        String[] pieces = {"boots", "leggings", "chestplate", "helmet"};
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 4; i++) {
            if (i > 0) sb.append(',');
            sb.append("{id:\"celestialascent:").append(set).append('_').append(pieces[i]).append("\",count:1").append(comp).append('}');
        }
        return "summon armor_stand " + x + " 201 6 {ShowArms:1b,NoBasePlate:1b,NoGravity:1b,Rotation:[180f,0f],ArmorItems:[" + sb + "]}";
    }

    private static String boss(String id, double x, double y, double z) {
        return "summon celestialascent:" + id + " " + x + " " + y + " " + z + " {NoAI:1b,Rotation:[180f,0f],PersistenceRequired:1b}";
    }

    private static final String CLEAR = "kill @e[type=!player]";

    private static void build() {
        String stage = "fill -24 199 -12 24 199 24 minecraft:smooth_quartz";
        step(60, null, 0, 0, "gamemode creative", "time set 6000", "weather clear", "gamerule doDaylightCycle false",
                "gamerule doMobSpawning false", "gamerule doWeatherCycle false", "gamerule sendCommandFeedback false",
                "fill -24 200 -12 24 230 24 minecraft:air", stage, "tp @s 0 200 -8 0 0");
        // Titans
        step(80, "titans", 0, 8, CLEAR, boss("frost_titan", -9, 200, 8), boss("tide_titan", -3, 200, 8),
                boss("storm_titan", 3, 200, 8), boss("magma_titan", 9, 200, 8), "tp @s 0 202 -10 0 8");
        for (String t : new String[]{"frost_titan", "tide_titan", "storm_titan", "magma_titan"}) {
            step(50, t, 0, 0, CLEAR, boss(t, 0, 200, 2), "tp @s 0 202.5 -6 0 0");
        }
        // Later bosses
        step(80, "bosses", 0, 6, CLEAR, boss("sentinel_construct", -11, 200, 8), boss("ender_colossus", -5, 200, 10),
                boss("sun_herald", 1, 200, 8), boss("void_sovereign", 7, 200, 10), boss("astral_seraph", 12, 203, 8),
                boss("nebula_leviathan", 0, 208, 14), "tp @s 0 203 -12 0 6");
        for (String t : new String[]{"sentinel_construct", "ender_colossus", "astral_seraph", "nebula_leviathan", "sun_herald", "void_sovereign"}) {
            boolean big = t.equals("ender_colossus") || t.equals("void_sovereign");
            step(50, t, 0, big ? -10 : 0, CLEAR, boss(t, 0, t.equals("astral_seraph") || t.equals("nebula_leviathan") ? 202 : 200, 3),
                    "tp @s 0 " + (big ? "203" : "202.5") + " " + (big ? "-9" : "-6") + " 0 0");
        }
        // Armor on stands
        step(60, "armor", 0, 10, CLEAR, stand(-8, "titan", null), stand(-6, "titan", "frost"), stand(-4, "titan", "tide"),
                stand(-2, "titan", "storm"), stand(0, "titan", "magma"), stand(2, "imperial", null), stand(4, "stellar", null),
                stand(6, "void", null), stand(8, "ascendant", null), "tp @s 0 202 -2 0 10");
        step(40, "armor_close_titan", 0, 10, "tp @s -5 202 2.5 0 10");
        step(40, "armor_close_late", 0, 10, "tp @s 5 202 2.5 0 10");
        step(40, "armor_back", 180, 10, "tp @s 0 202 12 180 10");
        step(60, "player_ascendant", 0, 0, CameraType.THIRD_PERSON_FRONT, p -> {
            cmd(p, CLEAR);
            cmd(p, "item replace entity @s armor.head with celestialascent:ascendant_helmet");
            cmd(p, "item replace entity @s armor.chest with celestialascent:ascendant_chestplate");
            cmd(p, "item replace entity @s armor.legs with celestialascent:ascendant_leggings");
            cmd(p, "item replace entity @s armor.feet with celestialascent:ascendant_boots");
            cmd(p, "tp @s 0 200 0 180 15");
        });
        step(30, null, 0, 0, "clear @s");
        // Every block on a shelf
        STEPS.add(new Step(60, p -> {
            cmd(p, CLEAR);
            cmd(p, "fill -24 200 -12 24 230 24 minecraft:air");
            int i = 0;
            for (var b : Content.BLOCKS) {
                var id = BuiltInRegistries.BLOCK.getKey(b.get());
                int x = -15 + (i % 16) * 2, z = 4 + (i / 16) * 3;
                p.serverLevel().setBlockAndUpdate(new BlockPos(x, 200, z), b.get().defaultBlockState());
                i++;
            }
            cmd(p, "tp @s 0 205 -6 0 28");
        }, "blocks", 0, 28, CameraType.FIRST_PERSON));
        // GUIs
        String[][] guis = {{"bank_counter", "gui_bank"}, {"shop_stall", "gui_shop"}, {"titan_forge", "gui_titan_forge"},
                {"quest_board", "gui_quest_board"}, {"imperial_forge", "gui_imperial_forge"}, {"sky_altar", "gui_sky_altar"},
                {"void_infuser", "gui_void_infuser"}, {"ascension_altar", "gui_ascension_altar"}};
        for (String[] g : guis) {
            STEPS.add(new Step(30, p -> {
                p.closeContainer();
                BlockPos at = new BlockPos(0, 200, 2);
                var block = BuiltInRegistries.BLOCK.get(net.minecraft.resources.ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, g[0]));
                p.serverLevel().setBlockAndUpdate(at, block.defaultBlockState());
                if (p.serverLevel().getBlockEntity(at) instanceof com.celestialascent.economy.ShopStallBlockEntity be) be.setOwner(p);
                cmd(p, "tp @s 0 200 0 0 30");
                p.serverLevel().getBlockState(at).useWithoutItem(p.serverLevel(), p,
                        new BlockHitResult(Vec3.atCenterOf(at), Direction.NORTH, at, false));
            }, g[1], 0, 30, CameraType.FIRST_PERSON));
        }
        STEPS.add(new Step(10, ServerPlayer::closeContainer, null, 0, 0, CameraType.FIRST_PERSON));
        // Constellations
        STEPS.add(new Step(80, p -> {
            for (var c : Constellations.ALL) Progress.recordKill(p, c.boss());
            cmd(p, "time set 18000");
            cmd(p, "tp @s 0 200 0 30 -55");
        }, "constellations_1", 30, -55, CameraType.FIRST_PERSON));
        step(30, "constellations_2", 200, -50, "tp @s 0 200 0 200 -50");
        step(30, "constellations_3", 300, -70, "tp @s 0 200 0 300 -70");
        // Dimensions
        step(160, "fallen_stars", 0, 5, "time set 6000", "execute in celestialascent:fallen_stars run tp @s -150 170 140 30 15");
        step(40, "fallen_stars_sky", 0, -40, "execute in celestialascent:fallen_stars run tp @s -150 170 140 120 -40");
        step(160, "abyss", 0, 0, "execute in celestialascent:abyss run tp @s 0 60 0 0 0", "effect give @s night_vision 999 0 true");
        // Structures (devworld seed)
        step(220, "trade_city", 0, 40, "effect clear @s", "execute in minecraft:overworld run tp @s -320 150 -390 0 40");
        step(220, "tide_shrine", 0, 40, "execute in minecraft:overworld run tp @s -880 110 -400 0 40");
        step(220, "ruined_capital", 0, 35, "execute in minecraft:the_end run tp @s -1316 110 60 0 35");
        step(220, "star_gate", 0, 40, "execute in minecraft:the_end run tp @s -1028 90 -720 0 40");
        step(220, "sanctum", 0, 25, "execute in celestialascent:fallen_stars run tp @s -145 165 135 0 25");
    }

    @SubscribeEvent
    public static void tick(ClientTickEvent.Post e) {
        if (!ENABLED) return;
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || mc.getSingleplayerServer() == null) return;
        if (STEPS.isEmpty()) build();
        if (startDelay-- > 0) return;
        if (index >= 0 && --timer > 0) return;
        if (index >= 0) {
            Step done = STEPS.get(index);
            if (done.shot() != null && (ONLY.isEmpty() || done.shot().matches(ONLY))) {
                Screenshot.grab(mc.gameDirectory, "ca_" + done.shot() + ".png", mc.getMainRenderTarget(), msg -> {});
            }
        }
        index++;
        if (index >= STEPS.size()) {
            mc.stop();
            return;
        }
        Step s = STEPS.get(index);
        mc.options.hideGui = true;
        mc.options.setCameraType(s.camera());
        timer = s.ticks();
        MinecraftServer server = mc.getSingleplayerServer();
        var uuid = mc.player.getUUID();
        server.execute(() -> {
            ServerPlayer p = server.getPlayerList().getPlayer(uuid);
            if (p != null) s.server().accept(p);
        });
    }
}
