package com.celestialascent.guide;

import com.celestialascent.abyss.Abyss;
import com.celestialascent.empire.Empire;
import com.celestialascent.stars.Stars;
import com.celestialascent.titans.Titans;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.ItemLike;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;

/** Strings and progress rungs for the codex's front page. */
public final class GuideUi {
    private GuideUi() {}

    public static final String TITLE = GuideBook.text("ui.title", "Celestial Codex", "Himmelskodex");
    public static final String NEXT = GuideBook.text("ui.next", "Your next step", "Dein nächster Schritt");
    public static final String OPEN = GuideBook.text("ui.open", "Open the chapter", "Zum Kapitel");
    public static final String ASCENT = GuideBook.text("ui.ascent", "Your ascent", "Dein Aufstieg");
    public static final String DEFEATED = GuideBook.text("ui.defeated", "Bosses defeated: %s of %s", "Besiegte Bosse: %s von %s");
    public static final String CONTENTS = GuideBook.text("ui.contents", "Contents", "Inhalt");
    public static final String MISSING_RECIPE = GuideBook.text("ui.missing_recipe", "Recipe not found", "Rezept nicht gefunden");
    public static final String WEAR_SET = GuideBook.text("ui.wear_set", "Wear all four pieces", "Trage alle vier Teile");

    /** One medallion on the front page: an icon and the bosses it stands for. */
    public record Rung(String key, Supplier<? extends ItemLike> icon, List<ResourceLocation> bosses) {}

    public static final List<Rung> RUNGS = List.of(
            new Rung(GuideBook.text("ui.rung.titans", "Elemental Titans", "Elementar-Titanen"), Titans.TITAN_SHARD, NextStep.TITAN_IDS),
            new Rung(GuideBook.text("ui.rung.dragon", "Ender Dragon", "Enderdrache"), Empire.DRAGON_HEART, List.of(NextStep.DRAGON_ID)),
            new Rung(GuideBook.text("ui.rung.colossus", "Lost Ender Empire", "Ender-Imperium"), Empire.IMPERIAL_SEAL, List.of(NextStep.COLOSSUS_ID)),
            new Rung(GuideBook.text("ui.rung.celestials", "Fallen Stars", "Gefallene Sterne"), Stars.STAR_CORE, celestials()),
            new Rung(GuideBook.text("ui.rung.abyss", "The Abyss", "Der Abgrund"), Abyss.VOID_HEART, List.of(NextStep.SOVEREIGN_ID)),
            new Rung(GuideBook.text("ui.rung.ascendant", "Ascension", "Aufstieg"), Abyss.ASC_CHESTPLATE, List.of()));

    private static List<ResourceLocation> celestials() {
        List<ResourceLocation> all = new ArrayList<>(NextStep.CELESTIAL_IDS);
        all.add(NextStep.HERALD_ID);
        return List.copyOf(all);
    }

    /** Total number of bosses counted on the front page. */
    public static int bossCount() {
        return RUNGS.stream().mapToInt(r -> r.bosses().size()).sum();
    }
}
