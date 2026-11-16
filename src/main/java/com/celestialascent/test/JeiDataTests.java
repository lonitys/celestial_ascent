package com.celestialascent.test;

import com.celestialascent.CelestialAscent;
import com.celestialascent.core.station.StationRecipe;
import com.celestialascent.core.station.StationType;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

import java.util.List;

/** The display data recipe viewers (JEI) show: it has to agree with what the game really does. */
@GameTestHolder(CelestialAscent.MODID)
@PrefixGameTestTemplate(false)
public final class JeiDataTests {
    private JeiDataTests() {}

    /** Every station recipe shows at least one example, and each example really is that recipe. */
    @GameTest(template = CoreTests.FLOOR)
    public static void stationExamplesMatch(GameTestHelper h) {
        int n = 0;
        for (StationType type : StationType.all()) {
            for (StationRecipe r : type.recipes) {
                List<StationRecipe.Example> ex = r.examples().get();
                h.assertTrue(!ex.isEmpty(), type.id + ": a recipe without examples");
                for (StationRecipe.Example e : ex) {
                    h.assertTrue(r.matches(e.base(), e.mats()), type.id + ": example does not match its recipe: " + e.base());
                    h.assertTrue(type.find(e.base(), e.mats()) == r, type.id + ": another recipe claims the example " + e.base());
                    h.assertTrue(!e.result().isEmpty(), type.id + ": empty result for " + e.base());
                    CoreTests.eq(h, e.result().getItem(), r.result().apply(e.base().copy()).getItem(), type.id + ": example result");
                    n++;
                }
            }
        }
        h.assertTrue(n > 100, "expected well over 100 examples, got " + n);
        h.succeed();
    }
}
