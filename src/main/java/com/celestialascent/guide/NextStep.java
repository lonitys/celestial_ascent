package com.celestialascent.guide;

import com.celestialascent.CelestialAscent;
import net.minecraft.resources.ResourceLocation;

import java.util.Collection;
import java.util.List;

/**
 * The player's next goal on the ladder, worked out from their defeated bosses. Shown on the codex's
 * first page; clicking it jumps to {@link #chapter} at {@link #anchor}.
 */
public enum NextStep {
    TITANS("titans", "titans",
            "Hunt the Elemental Titans", "Jage die Elementar-Titanen",
            "Craft an Elemental Sigil and use it on the altar of the matching shrine.",
            "Stell ein Elementarsiegel her und benutze es am Altar des passenden Schreins."),
    DRAGON("dragon", "dragon",
            "Slay the Ender Dragon", "Besiege den Enderdrachen",
            "Every player nearby gets a Dragon Heart. Killed it before? Respawn it with End Crystals.",
            "Jeder Spieler in der Nähe erhält ein Drachenherz. Schon besiegt? Mit Endkristallen neu beschwören."),
    EMPIRE("empire", "empire",
            "Wake the Ender Colossus", "Wecke den Ender-Koloss",
            "Find the Ruined Capital in the outer End, restore its pylons and offer a Dragon Heart at the throne.",
            "Finde die Hauptstadt im äußeren End, stelle die Pylonen wieder her und opfere am Thron ein Drachenherz."),
    CELESTIALS("stars", "celestials",
            "Cross the Star Gate", "Durchschreite das Sternentor",
            "Find the gate with a Star Compass, open it and defeat the Astral Seraph and the Nebula Leviathan.",
            "Finde das Tor mit dem Sternenkompass, öffne es und besiege Astralseraph und Nebelleviathan."),
    HERALD("stars", "herald",
            "Challenge the Sun Herald", "Fordere den Sonnenherold heraus",
            "Offer 16 Stardust at the third altar in the Fallen Stars.",
            "Opfere 16 Sternenstaub am dritten Altar in den Gefallenen Sternen."),
    SOVEREIGN("abyss", "abyss",
            "Descend into the Abyss", "Steig hinab in den Abgrund",
            "Jump off the Fallen Stars, mine Void Essence and call the Void Sovereign with an Abyssal Beacon.",
            "Spring von den Gefallenen Sternen, sammle Leerenessenz und rufe den Leerenherrscher mit einem Abgrundleuchtfeuer."),
    ASCEND("ascendant", "ascendant",
            "Forge Ascendant armor", "Schmiede die Aufgestiegene Rüstung",
            "Combine your Void armor with Primordial Cores and Star Cores at the Ascension Altar.",
            "Verbinde deine Leerenrüstung am Aufstiegsaltar mit Urkernen und Sternkernen."),
    DONE("constellations", null,
            "You have ascended", "Du bist aufgestiegen",
            "Every constellation shines for you. Fight the bosses again with friends or build a trading empire.",
            "Alle Sternbilder leuchten für dich. Bekämpfe die Bosse mit Freunden oder baue ein Handelsimperium auf.");

    public final String chapter;
    /** Anchor inside the chapter, or null for its first page. */
    public final String anchor;
    public final String titleKey;
    public final String descKey;

    NextStep(String chapter, String anchor, String titleEn, String titleDe, String descEn, String descDe) {
        this.chapter = chapter;
        this.anchor = anchor;
        String k = name().toLowerCase(java.util.Locale.ROOT);
        this.titleKey = GuideBook.text("next." + k, titleEn, titleDe);
        this.descKey = GuideBook.text("next." + k + ".desc", descEn, descDe);
    }

    private static ResourceLocation mod(String path) {
        return ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, path);
    }

    public static final List<ResourceLocation> TITAN_IDS = List.of(mod("frost_titan"), mod("tide_titan"), mod("storm_titan"), mod("magma_titan"));
    public static final ResourceLocation DRAGON_ID = ResourceLocation.withDefaultNamespace("ender_dragon");
    public static final ResourceLocation COLOSSUS_ID = mod("ender_colossus");
    public static final List<ResourceLocation> CELESTIAL_IDS = List.of(mod("astral_seraph"), mod("nebula_leviathan"));
    public static final ResourceLocation HERALD_ID = mod("sun_herald");
    public static final ResourceLocation SOVEREIGN_ID = mod("void_sovereign");

    /** The first unfinished step in ladder order. */
    public static NextStep of(Collection<ResourceLocation> kills, boolean wearingAscendant) {
        if (!kills.containsAll(TITAN_IDS)) return TITANS;
        if (!kills.contains(DRAGON_ID)) return DRAGON;
        if (!kills.contains(COLOSSUS_ID)) return EMPIRE;
        if (!kills.containsAll(CELESTIAL_IDS)) return CELESTIALS;
        if (!kills.contains(HERALD_ID)) return HERALD;
        if (!kills.contains(SOVEREIGN_ID)) return SOVEREIGN;
        return wearingAscendant ? DONE : ASCEND;
    }
}
