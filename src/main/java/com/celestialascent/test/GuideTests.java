package com.celestialascent.test;

import com.celestialascent.CelestialAscent;
import com.celestialascent.datagen.LangGenDe;
import com.celestialascent.guide.Guide;
import com.celestialascent.guide.GuideBook;
import com.celestialascent.guide.GuideChapters;
import com.celestialascent.guide.NextStep;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

import java.util.ArrayList;
import java.util.List;
import java.util.Set;

/** The codex: given once, its next step follows the ladder, and every recipe it shows really exists. */
@GameTestHolder(CelestialAscent.MODID)
@PrefixGameTestTemplate(false)
public final class GuideTests {
    private GuideTests() {}

    @GameTest(template = CoreTests.FLOOR)
    public static void codexIsGivenOnce(GameTestHelper h) {
        // Creating the mock player logs it in, which already hands out the codex.
        ServerPlayer p = h.makeMockServerPlayerInLevel();
        h.assertTrue(p.getData(Guide.RECEIVED), "login marks the codex as given");
        CoreTests.eq(h, 1, p.getInventory().countItem(Guide.CODEX.get()), "login put the codex in the inventory");
        h.assertTrue(!Guide.giveOnce(p), "logging in again gives nothing");
        CoreTests.eq(h, 1, p.getInventory().countItem(Guide.CODEX.get()), "still one codex");

        p.setData(Guide.RECEIVED, false);
        p.getInventory().clearContent();
        h.assertTrue(Guide.giveOnce(p), "a player who never had it gets one");
        CoreTests.eq(h, 1, p.getInventory().countItem(Guide.CODEX.get()), "exactly one codex");
        h.succeed();
    }

    @GameTest(template = CoreTests.FLOOR)
    public static void nextStepFollowsTheLadder(GameTestHelper h) {
        List<ResourceLocation> kills = new ArrayList<>();
        CoreTests.eq(h, NextStep.TITANS, NextStep.of(kills, false), "fresh player");
        kills.addAll(NextStep.TITAN_IDS.subList(0, 3));
        CoreTests.eq(h, NextStep.TITANS, NextStep.of(kills, false), "three titans are not enough");
        kills.add(NextStep.TITAN_IDS.get(3));
        CoreTests.eq(h, NextStep.DRAGON, NextStep.of(kills, false), "all titans");
        kills.add(NextStep.DRAGON_ID);
        CoreTests.eq(h, NextStep.EMPIRE, NextStep.of(kills, false), "dragon");
        kills.add(NextStep.COLOSSUS_ID);
        CoreTests.eq(h, NextStep.CELESTIALS, NextStep.of(kills, false), "colossus");
        kills.add(NextStep.CELESTIAL_IDS.get(0));
        CoreTests.eq(h, NextStep.CELESTIALS, NextStep.of(kills, false), "one celestial");
        kills.add(NextStep.CELESTIAL_IDS.get(1));
        CoreTests.eq(h, NextStep.HERALD, NextStep.of(kills, false), "both celestials");
        kills.add(NextStep.HERALD_ID);
        CoreTests.eq(h, NextStep.SOVEREIGN, NextStep.of(kills, false), "herald");
        kills.add(NextStep.SOVEREIGN_ID);
        CoreTests.eq(h, NextStep.ASCEND, NextStep.of(kills, false), "every boss");
        CoreTests.eq(h, NextStep.DONE, NextStep.of(kills, true), "wearing Ascendant armor");

        for (NextStep step : NextStep.values()) {
            GuideBook.Chapter c = GuideChapters.byId(step.chapter);
            h.assertTrue(c != null, step + " points at a missing chapter " + step.chapter);
            if (step.anchor != null) {
                boolean found = c.elements().stream().anyMatch(e -> e instanceof GuideBook.Anchor a && a.id().equals(step.anchor));
                h.assertTrue(found, step + " points at a missing anchor " + step.anchor);
            }
        }
        h.succeed();
    }

    @GameTest(template = CoreTests.FLOOR)
    public static void codexRecipesExist(GameTestHelper h) {
        var recipes = h.getLevel().getRecipeManager();
        int stations = 0, crafts = 0;
        for (GuideBook.Chapter c : GuideChapters.ALL) {
            for (GuideBook.Element e : c.elements()) {
                if (e instanceof GuideBook.Crafting cr) {
                    h.assertTrue(recipes.byKey(cr.recipe()).isPresent(), "crafting recipe " + cr.recipe() + " in chapter " + c.id());
                    crafts++;
                } else if (e instanceof GuideBook.Station st) {
                    ItemStack base = new ItemStack(st.base().get());
                    List<ItemStack> mats = st.mats().stream().map(m -> new ItemStack(m.item().get(), m.count())).toList();
                    var recipe = st.type().get().find(base, mats);
                    h.assertTrue(recipe != null, "station " + st.type().get().id + " accepts " + base.getItem() + " + " + mats);
                    ItemStack out = recipe.result().apply(base.copy());
                    CoreTests.eq(h, st.result().get().asItem(), out.getItem(), "station result in chapter " + c.id());
                    stations++;
                }
            }
        }
        h.assertTrue(crafts >= 15 && stations >= 8, "codex shows recipes (" + crafts + " crafting, " + stations + " station)");
        h.succeed();
    }

    @GameTest(template = CoreTests.FLOOR)
    public static void codexTextIsComplete(GameTestHelper h) {
        var strings = GuideBook.strings();
        for (var e : strings.entrySet()) {
            String[] v = e.getValue();
            h.assertTrue(!v[0].isBlank() && !v[1].isBlank(), "text in both languages: " + e.getKey());
            CoreTests.eq(h, LangGenDe.argCount(v[0]), LangGenDe.argCount(v[1]), "same arguments in both languages: " + e.getKey());
        }
        Set<String> seen = new java.util.HashSet<>();
        for (GuideBook.Chapter c : GuideChapters.ALL) {
            h.assertTrue(seen.add(c.id()), "unique chapter id " + c.id());
            for (GuideBook.Element e : c.elements()) {
                if (e instanceof GuideBook.Text t) {
                    CoreTests.eq(h, t.args().size(), LangGenDe.argCount(strings.get(t.key())[0]), "argument count of " + t.key());
                }
            }
        }
        h.succeed();
    }
}
