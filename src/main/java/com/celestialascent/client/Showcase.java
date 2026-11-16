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

    /** An armor stand wearing a full set at an evolution stage (front view). */
    private static String stagedStand(double x, String set, String element, int stage) {
        String comp = ",components:{\"celestialascent:armor_stage\":" + stage + (element == null ? "" : ",\"celestialascent:element\":\"" + element + "\"") + "}";
        String[] pieces = {"boots", "leggings", "chestplate", "helmet"};
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 4; i++) {
            if (i > 0) sb.append(',');
            sb.append("{id:\"celestialascent:").append(set).append('_').append(pieces[i]).append("\",count:1").append(comp).append('}');
        }
        return "summon armor_stand " + x + " 200 -5 {ShowArms:1b,NoBasePlate:1b,NoGravity:1b,Rotation:[180f,0f],ArmorItems:[" + sb + "]}";
    }

    private static String boss(String id, double x, double y, double z) {
        return "summon celestialascent:" + id + " " + x + " " + y + " " + z + " {NoAI:1b,Rotation:[180f,0f],PersistenceRequired:1b}";
    }

    private static final String CLEAR = "tp @e[type=!player] 0 -500 0";

    private static void build() {
        String stage = "fill -24 199 -12 24 199 24 minecraft:smooth_quartz";
        // Go there first and hover so the chunks load before the stage is built.
        STEPS.add(new Step(120, p -> {
            cmd(p, "gamemode creative");
            cmd(p, "tp @s 0 210 -8 0 0");
            p.getAbilities().flying = true;
            p.onUpdateAbilities();
        }, null, 0, 0, CameraType.FIRST_PERSON));
        step(40, null, 0, 0, "time set 6000", "weather clear", "gamerule doDaylightCycle false",
                "gamerule doMobSpawning false", "gamerule doWeatherCycle false", "gamerule sendCommandFeedback false",
                "gamerule doEntityDrops false", "gamerule doMobLoot false",
                "fill -24 200 -12 24 212 24 minecraft:air", stage, "tp @s 0 200 -8 0 0");
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
        // Armor evolution: each set at stage I, II and III
        for (String[] set : new String[][]{{"titan", "frost"}, {"imperial", null}, {"stellar", null}, {"void", null}, {"ascendant", null}}) {
            step(40, "armor_stages_" + set[0], 0, 8, CLEAR, stagedStand(-2.2, set[0], set[1], 1), stagedStand(0, set[0], set[1], 2),
                    stagedStand(2.2, set[0], set[1], 3), "tp @s 0 201.3 -8.6 0 8");
            step(25, "armor_stages_" + set[0] + "_back", 180, 8, "tp @s 0 201.3 -1.4 180 8");
        }
        // Gallery for the CurseForge page: clean platform, night (glow shows), no chat
        step(60, "gallery_setup", 0, 0, "kill @e[type=!minecraft:player]", "fill -24 200 -12 24 212 24 minecraft:air",
                "fill -24 199 -12 24 199 24 minecraft:polished_deepslate", "time set 18000", "tp @s 0 202 -8 0 0");
        Object[][] trios = {{"astral_seraph", 6, 11, 202}, {"void_sovereign", 6, 12, 200}, {"frost_titan", 5, 10, 200}, {"sun_herald", 5, 10, 200},
                {"ender_colossus", 6, 13, 200}};
        for (Object[] t : trios) {
            String id = (String) t[0];
            int gap = (Integer) t[1], dist = (Integer) t[2], y = (Integer) t[3];
            step(60, "gallery_" + id, 0, 4, CLEAR,
                    "summon celestialascent:" + id + " " + gap + " " + y + " 4 {NoAI:1b,Rotation:[180f,0f],PersistenceRequired:1b,Phase:0}",
                    "summon celestialascent:" + id + " 0 " + y + " 4 {NoAI:1b,Rotation:[180f,0f],PersistenceRequired:1b,Phase:1}",
                    "summon celestialascent:" + id + " " + (-gap) + " " + y + " 4 {NoAI:1b,Rotation:[180f,0f],PersistenceRequired:1b,Phase:2}",
                    "tp @s 0 " + (y + 2.5) + " " + (4 - dist) + " 0 4");
        }
        step(50, "gallery_armor_ascendant", 180, 6, CLEAR, stagedStand(-2.2, "ascendant", null, 1), stagedStand(0, "ascendant", null, 2),
                stagedStand(2.2, "ascendant", null, 3), "tp @s 0 201.5 2.4 180 7");
        step(30, "gallery_armor_titan", 0, 6, CLEAR, stagedStand(-2.2, "titan", "frost", 1), stagedStand(0, "titan", "frost", 2),
                stagedStand(2.2, "titan", "frost", 3), "tp @s 0 201.5 -12.4 0 7");
        STEPS.add(new Step(60, p -> {
            cmd(p, CLEAR);
            String[] row = {"frost_altar", "tide_altar", "storm_altar", "magma_altar", "seraph_altar", "leviathan_altar", "herald_altar"};
            for (int i = 0; i < row.length; i++) cmd(p, "setblock " + (-9 + i * 3) + " 200 8 celestialascent:" + row[i] + "[facing=south]");
            String[] row2 = {"relic_pedestal[facing=south]", "imperial_pylon[restored=true]", "star_gate_pedestal[facing=south,head=true]",
                    "sky_altar[facing=south]", "void_infuser[facing=south]", "ascension_altar[facing=south]"};
            for (int i = 0; i < row2.length; i++) cmd(p, "setblock " + (-8 + i * 3) + " 200 4 celestialascent:" + row2[i]);
            if (p.serverLevel().getBlockEntity(new BlockPos(1, 200, 4)) instanceof com.celestialascent.core.station.StationBlockEntity st) {
                st.items.setItem(0, new net.minecraft.world.item.ItemStack(com.celestialascent.abyss.Abyss.ASC_CHESTPLATE.get()));
            }
            cmd(p, "tp @s 0 203 -3 0 24");
        }, "gallery_altars", 0, 24, CameraType.FIRST_PERSON));
        step(90, "gallery_cleanup", 0, 0, "kill @e[type=!minecraft:player]", "fill -24 200 -12 24 212 24 minecraft:air",
                "fill -24 199 -12 24 199 24 minecraft:smooth_quartz", "time set 6000");
        STEPS.add(new Step(60, p -> {
            cmd(p, "summon celestialascent:magma_titan 0 200 9 {Rotation:[180f,0f],PersistenceRequired:1b}");
            cmd(p, "tp @s 0 202 -4 0 4");
        }, "hud_gallery_bar", 0, 4, CameraType.FIRST_PERSON));
        step(14, "hud_gallery_banner", 0, 4, "data merge entity @e[type=celestialascent:magma_titan,limit=1] {Health:340f}");
        step(10, "gallery_end", 0, 0, "kill @e[type=!minecraft:player]");
        // HUD: the custom boss bar and the stage banner (a real stage change: the titan loses health)
        // Earlier shots leave bosses whose bars would fill the screen (named so it only runs with the HUD shots).
        step(90, "hud_clear", 0, 0, "kill @e[type=!minecraft:player]", "fill -24 200 -12 24 212 24 minecraft:air");
        STEPS.add(new Step(50, p -> {
            cmd(p, "summon celestialascent:frost_titan 0 200 10 {Rotation:[180f,0f],PersistenceRequired:1b}");
            cmd(p, "tp @s 0 202 -3 0 5");
        }, "hud_bar", 0, 5, CameraType.FIRST_PERSON));
        step(14, "hud_banner", 0, 5, "data merge entity @e[type=celestialascent:frost_titan,limit=1] {Health:220f}");
        step(95, "hud_stage2", 0, 5, "tp @s 0 202 -3 0 5");
        step(14, "hud_banner3", 0, 5, "data merge entity @e[type=celestialascent:frost_titan,limit=1] {Health:110f}");
        step(95, "hud_stage3", 0, 5, "tp @s 0 202 -3 0 5");
        // Evolution: each boss in its three stages side by side (stage textures, growth)
        Object[][] stages = {{"frost_titan", 5, 12, 200}, {"tide_titan", 5, 12, 200}, {"storm_titan", 5, 12, 200}, {"magma_titan", 5, 12, 200},
                {"sentinel_construct", 4, 10, 200}, {"ender_colossus", 7, 17, 200}, {"astral_seraph", 5, 12, 202},
                {"nebula_leviathan", 8, 18, 204}, {"sun_herald", 5, 12, 200}, {"void_sovereign", 7, 16, 200}};
        for (Object[] st : stages) {
            String id = (String) st[0];
            int gap = (Integer) st[1], dist = (Integer) st[2], y = (Integer) st[3];
            String[] cmds = new String[5];
            cmds[0] = CLEAR;
            for (int k = 0; k < 3; k++) {
                cmds[k + 1] = "summon celestialascent:" + id + " " + ((1 - k) * gap) + " " + y + " 4 {NoAI:1b,Rotation:[180f,0f],PersistenceRequired:1b,Phase:" + k + "}";
            }
            cmds[4] = "tp @s 0 " + (y + 2.5) + " " + (4 - dist) + " 0 4";
            step(50, "stages_" + id, 0, 4, cmds);
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
            cmd(p, "fill -24 200 -12 24 212 24 minecraft:air");
            int i = 0;
            for (var b : Content.BLOCKS) {
                var id = BuiltInRegistries.BLOCK.getKey(b.get());
                int x = -15 + (i % 16) * 2, z = 4 + (i / 16) * 3;
                p.serverLevel().setBlockAndUpdate(new BlockPos(x, 200, z), b.get().defaultBlockState());
                i++;
            }
            cmd(p, "tp @s -8 202.2 1 0 20");
        }, "blocks", 0, 20, CameraType.FIRST_PERSON));
        step(30, "blocks_2", 0, 20, "tp @s 8 202.2 1 0 20");
        step(30, "blocks_3", 0, 25, "tp @s 0 202.6 4 0 25");
        // Floating tops: every animated block in a row, a restored pylon, the gate pedestal with its head, a station with an item
        STEPS.add(new Step(60, p -> {
            cmd(p, CLEAR);
            cmd(p, "fill -12 199 0 12 199 12 minecraft:smooth_stone");
            cmd(p, "fill -12 200 0 12 210 12 minecraft:air");
            String[] row = {"frost_altar", "tide_altar", "storm_altar", "magma_altar", "seraph_altar", "leviathan_altar", "herald_altar"};
            for (int i = 0; i < row.length; i++) cmd(p, "setblock " + (-9 + i * 3) + " 200 8 celestialascent:" + row[i] + "[facing=south]");
            String[] row2 = {"relic_pedestal[facing=south]", "imperial_pylon[restored=true]", "star_gate_pedestal[facing=south,head=true]",
                    "sky_altar[facing=south]", "void_infuser[facing=south]", "ascension_altar[facing=south]"};
            for (int i = 0; i < row2.length; i++) cmd(p, "setblock " + (-8 + i * 3) + " 200 4 celestialascent:" + row2[i]);
            if (p.serverLevel().getBlockEntity(new BlockPos(1, 200, 4)) instanceof com.celestialascent.core.station.StationBlockEntity st) {
                st.items.setItem(0, new net.minecraft.world.item.ItemStack(com.celestialascent.empire.Empire.CHESTPLATE.get()));
            }
            cmd(p, "time set 6000");
            cmd(p, "tp @s 0 203 -4 0 22");
        }, "floating", 0, 22, CameraType.FIRST_PERSON));
        step(13, "floating_later", 0, 22, "tp @s 0 203 -4 0 22");
        step(30, "floating_close", 0, 25, "tp @s -3 201.8 1.5 0 25");
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
        // The codex: front page at two stages of progress, then one spread per chapter section
        codex("codex_front", List.of("celestialascent:frost_titan", "celestialascent:tide_titan"), null, null);
        codex("codex_front_late", Constellations.ALL.stream().map(c -> c.boss().toString()).toList(), null, null);
        String[][] spreads = {{"intro", null}, {"economy", null}, {"titans", "titans"}, {"titans", "titan_armor"}, {"dragon", null},
                {"empire", "empire"}, {"empire", "imperial_armor"}, {"stargate", null}, {"stars", "celestials"}, {"stars", "stellar_armor"},
                {"abyss", "abyss"}, {"abyss", "void_armor"}, {"ascendant", null}, {"evolution", null}, {"constellations", null}, {"projecte", null}};
        for (String[] sp : spreads) codex("codex_" + sp[0] + (sp[1] == null ? "" : "_" + sp[1]), null, sp[0], sp[1]);
        STEPS.add(new Step(10, p -> Minecraft.getInstance().execute(() -> Minecraft.getInstance().setScreen(null)), null, 0, 0, CameraType.FIRST_PERSON));
        // Constellations
        STEPS.add(new Step(80, p -> {
            for (var c : Constellations.ALL) Progress.recordKill(p, c.boss());
            cmd(p, "time set 18000");
            cmd(p, "tp @s 0 200 0 30 -55");
        }, "constellations_1", 30, -55, CameraType.FIRST_PERSON));
        step(30, "constellations_2", 200, -50, "tp @s 0 200 0 200 -50");
        step(30, "constellations_3", 300, -70, "tp @s 0 200 0 300 -70");
        // Dimensions and structures, seen as a spectator from above
        step(200, "fallen_stars", 0, 15, "gamemode spectator", "time set 6000",
                "execute in celestialascent:fallen_stars run tp @s 0 235 0 0 15");
        step(40, "fallen_stars_sky", 0, -35, "execute in celestialascent:fallen_stars run tp @s 0 235 0 135 -35");
        step(200, "sanctum", 0, 30, "execute in celestialascent:fallen_stars run tp @s -303 140 5 0 30");
        STEPS.add(new Step(200, p -> {
            var abyss = p.server.getLevel(com.celestialascent.core.Travel.ABYSS);
            BlockPos at = com.celestialascent.abyss.Abyss.cavePos(abyss, 0, 0);
            cmd(p, "effect give @s night_vision 999 0 true");
            cmd(p, "execute in celestialascent:abyss run tp @s " + at.getX() + " " + (at.getY() + 1) + " " + at.getZ() + " 0 10");
        }, "abyss", 0, 10, CameraType.FIRST_PERSON));
        // Structure locations on the devworld seed (from /celestialascent verify)
        step(300, "trade_city", 0, 40, "effect clear @s", "execute in minecraft:overworld run tp @s -343 105 -380 0 40");
        step(300, "frost_shrine_view", 0, 38, "execute in minecraft:overworld run tp @s -1152 140 470 0 38");
        step(300, "tide_shrine", 0, 35, "execute in minecraft:overworld run tp @s -160 95 10 0 35");
        step(300, "storm_shrine_view", 0, 40, "execute in minecraft:overworld run tp @s -256 190 505 0 40");
        step(300, "magma_shrine_view", 0, 15, "execute in minecraft:the_nether run tp @s -336 40 176 0 15");
        step(300, "ruined_capital", 0, 35, "execute in minecraft:the_end run tp @s -1316 85 60 0 35");
        step(300, "star_gate", 0, 35, "execute in minecraft:the_end run tp @s -1052 75 -725 0 35");
    }

    /** Opens the codex on the client; {@code kills} (if given) replaces the player's progress first. */
    private static void codex(String shot, List<String> kills, String chapter, String anchor) {
        STEPS.add(new Step(25, p -> {
            // No closeContainer() here: its packet can arrive after the screen opens and close it again.
            if (kills != null) {
                p.setData(Progress.TYPE, new Progress(kills.stream().map(net.minecraft.resources.ResourceLocation::parse).toList()));
                Progress.sync(p);
            }
            Minecraft.getInstance().execute(() -> GuideScreen.open(chapter, anchor));
        }, shot, 0, 30, CameraType.FIRST_PERSON));
    }

    @SubscribeEvent
    public static void tick(ClientTickEvent.Post e) {
        if (!ENABLED) return;
        Minecraft mc = Minecraft.getInstance();
        // The dev world was made by the dedicated server, so NeoForge asks once about experimental settings.
        if (mc.screen instanceof net.minecraft.client.gui.screens.BackupConfirmScreen screen) {
            for (var child : screen.children()) {
                if (child instanceof net.minecraft.client.gui.components.Button b
                        && b.getMessage().getContents() instanceof net.minecraft.network.chat.contents.TranslatableContents tc
                        && tc.getKey().equals("selectWorld.backupJoinSkipButton")) {
                    b.onPress();
                    return;
                }
            }
        }
        if (mc.screen instanceof net.minecraft.client.gui.screens.DeathScreen && mc.player != null) {
            mc.player.respawn();
            mc.setScreen(null);
        }
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
        while (s.shot() != null && !ONLY.isEmpty() && !s.shot().matches(ONLY)) {
            if (++index >= STEPS.size()) {
                mc.stop();
                return;
            }
            s = STEPS.get(index);
        }
        Step step = s;
        mc.options.hideGui = step.shot() == null || !step.shot().startsWith("hud_"); // HUD shots keep the HUD
        mc.options.chatVisibility().set(net.minecraft.world.entity.player.ChatVisiblity.HIDDEN); // no chat in screenshots
        mc.options.fov().set(step.shot() != null && step.shot().startsWith("gallery_") ? 45 : 70); // gallery: tighter framing
        mc.options.setCameraType(step.camera());
        timer = step.ticks();
        MinecraftServer server = mc.getSingleplayerServer();
        var uuid = mc.player.getUUID();
        server.execute(() -> {
            ServerPlayer p = server.getPlayerList().getPlayer(uuid);
            if (p != null) step.server().accept(p);
        });
    }
}
