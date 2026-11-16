package com.celestialascent.datagen;

import com.celestialascent.CelestialAscent;
import com.celestialascent.guide.GuideBook;
import net.minecraft.data.PackOutput;
import net.neoforged.neoforge.common.data.LanguageProvider;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * German translation. Every English key must have a German entry with the same number of format
 * arguments, otherwise datagen fails, so the two files cannot drift apart.
 */
public class LangGenDe extends LanguageProvider {
    public LangGenDe(PackOutput out) {
        super(out, CelestialAscent.MODID, "de_de");
    }

    private static final Map<String, String> DE = new HashMap<>();

    private static void de(String key, String value) {
        if (DE.put(key, value) != null) throw new IllegalStateException("Duplicate German key " + key);
    }

    private static final Pattern ARG = Pattern.compile("%(?:(\\d+)\\$)?([A-Za-z%]|$)");

    /** Number of format arguments in a translation string (ignores %%). */
    public static int argCount(String s) {
        Matcher m = ARG.matcher(s);
        int n = 0;
        while (m.find()) if (!"%".equals(m.group(2))) n++;
        return n;
    }

    @Override
    protected void addTranslations() {
        Map<String, String> english = LangGen.english();
        Map<String, String[]> guide = GuideBook.strings();
        List<String> problems = new ArrayList<>();
        for (var e : english.entrySet()) {
            String key = e.getKey();
            String german = guide.containsKey(key) ? guide.get(key)[1] : DE.get(key);
            if (german == null) {
                problems.add("missing: " + key);
                continue;
            }
            if (argCount(german) != argCount(e.getValue())) problems.add("argument count differs: " + key);
            add(key, german);
        }
        for (String key : DE.keySet()) if (!english.containsKey(key)) problems.add("no English original: " + key);
        if (!problems.isEmpty()) throw new IllegalStateException("German translation problems:\n" + String.join("\n", problems));
    }

    static {
        de("itemGroup.celestialascent", "Celestial Ascent");
        de("key.categories.celestialascent", "Celestial Ascent");
        de("key.celestialascent.ability", "Rüstungsfähigkeit");
        de("key.celestialascent.toggle", "Rüstungseffekt umschalten");

        // ---- economy ----
        de("item.celestialascent.copper_aster", "Kupferaster");
        de("item.celestialascent.silver_aster", "Silberaster");
        de("item.celestialascent.gold_aster", "Goldaster");
        de("item.celestialascent.titan_aster", "Titanaster");
        de("item.celestialascent.ender_aster", "Enderaster");
        de("item.celestialascent.star_aster", "Sternaster");
        de("item.celestialascent.void_aster", "Leerenaster");
        de("block.celestialascent.bank_counter", "Bankschalter");
        de("block.celestialascent.shop_stall", "Marktstand");
        de("block.celestialascent.titan_anvil", "Titanenamboss");
        de("block.celestialascent.relic_pedestal", "Reliquiensockel");
        de("entity.minecraft.villager.celestialascent.banker", "Bankier");
        de("entity.minecraft.villager.celestialascent.titansmith", "Titanenschmied");
        de("entity.minecraft.villager.celestialascent.relic_dealer", "Reliquienhändler");
        de("tooltip.celestialascent.coin_value", "Wert: %s");
        de("tooltip.celestialascent.coin_stack", "Stapel: %s");
        de("container.celestialascent.bank", "Bank");
        de("container.celestialascent.shop", "Laden von %s");
        de("container.celestialascent.shop_manage", "Laden verwalten");
        de("gui.celestialascent.balance", "Guthaben: %s");
        de("gui.celestialascent.carried", "Dabei: %s");
        de("gui.celestialascent.withdraw", "1 × %s abheben (%s)\nShift-Klick: 10 abheben");
        de("gui.celestialascent.deposit_all", "Alle Münzen einzahlen");
        de("gui.celestialascent.price", "Preis pro Bündel");
        de("gui.celestialascent.bundle", "Bündel: %s");
        de("gui.celestialascent.buy", "Kaufen");
        de("gui.celestialascent.sold_out", "Ausverkauft");
        de("gui.celestialascent.in_stock", "Vorrat: %s");
        de("message.celestialascent.shop_sold", "%s hat %s × %s in deinem Laden für %s gekauft");
        de("message.celestialascent.shop_own_shop", "Du kannst nicht in deinem eigenen Laden kaufen");
        de("message.celestialascent.shop_cannot_afford", "Das kannst du dir nicht leisten (Münzen oder Bankguthaben)");
        de("message.celestialascent.shop_out_of_stock", "Dieser Laden ist ausverkauft");
        de("message.celestialascent.stall_unclaimed", "Freier Stand. Schleichen + Rechtsklick, um ihn für %s zu mieten");
        de("message.celestialascent.stall_rented", "Du hast diesen Stand gemietet. Rechtsklick, um Waren einzulegen.");
        de("block.celestialascent.quest_board", "Auftragstafel");
        de("container.celestialascent.quest_board", "Auftragstafel");
        de("gui.celestialascent.deliver", "Abgeben");
        de("gui.celestialascent.quest_done", "Erledigt");
        de("gui.celestialascent.quest_line", "Bring %s × %s");
        de("message.celestialascent.quest_missing", "Du brauchst %s × %s");
        de("message.celestialascent.prosperity", "Wohlstand des Dorfes: %s (nächstes Gebäude bei %s)");
        de("message.celestialascent.village_grew", "Das Dorf ist gewachsen: Ein neues Gebäude (%s) wurde gebaut!");
        de("building.celestialascent.market_stall", "Marktstand");
        de("building.celestialascent.lamp_post", "Laternenpfahl");
        de("building.celestialascent.cottage", "Häuschen");
        de("building.celestialascent.garden", "Garten");
        de("building.celestialascent.fountain", "Brunnen");
        de("building.celestialascent.smithy", "Schmiede");
        de("building.celestialascent.bank_kiosk", "Bankkiosk");
        de("building.celestialascent.watchtower", "Wachturm");

        // ---- titans ----
        de("item.celestialascent.titan_shard", "Titanensplitter");
        de("item.celestialascent.frost_core", "Frosttitanen-Kern");
        de("item.celestialascent.tide_core", "Gezeitentitanen-Kern");
        de("item.celestialascent.storm_core", "Sturmtitanen-Kern");
        de("item.celestialascent.magma_core", "Magmatitanen-Kern");
        de("item.celestialascent.frost_sigil", "Frostsiegel");
        de("item.celestialascent.tide_sigil", "Gezeitensiegel");
        de("item.celestialascent.storm_sigil", "Sturmsiegel");
        de("item.celestialascent.magma_sigil", "Magmasiegel");
        de("block.celestialascent.frost_altar", "Frostschrein-Altar");
        de("block.celestialascent.tide_altar", "Gezeitenschrein-Altar");
        de("block.celestialascent.storm_altar", "Sturmschrein-Altar");
        de("block.celestialascent.magma_altar", "Magmaschrein-Altar");
        de("entity.celestialascent.frost_titan", "Frosttitan");
        de("entity.celestialascent.tide_titan", "Gezeitentitan");
        de("entity.celestialascent.storm_titan", "Sturmtitan");
        de("entity.celestialascent.magma_titan", "Magmatitan");
        de("element.celestialascent.frost", "Frost");
        de("element.celestialascent.tide", "Gezeiten");
        de("element.celestialascent.storm", "Sturm");
        de("element.celestialascent.magma", "Magma");
        de("filled_map.celestialascent.frost_shrine", "Frostschrein-Karte");
        de("filled_map.celestialascent.tide_shrine", "Gezeitenschrein-Karte");
        de("filled_map.celestialascent.storm_shrine", "Sturmschrein-Karte");
        de("filled_map.celestialascent.magma_shrine", "Magmaschrein-Karte");
        de("item.celestialascent.titan_helmet", "Titanenhelm");
        de("item.celestialascent.titan_chestplate", "Titanenharnisch");
        de("item.celestialascent.titan_leggings", "Titanenbeinschutz");
        de("item.celestialascent.titan_boots", "Titanenstiefel");
        de("item.celestialascent.titan_infused", "%2$s (%1$s)");
        de("tooltip.celestialascent.element", "Element: %s");
        de("tooltip.celestialascent.no_element", "Ohne Element");
        de("tooltip.celestialascent.sigil", "Am %s benutzen, um seinen Titanen zu beschwören");
        de("tooltip.celestialascent.set.titan", "Titanenset (alle 4 Teile):");
        de("tooltip.celestialascent.set.titan.1", "Je Element: Stufe I auf einem Teil, II auf zwei");
        de("tooltip.celestialascent.set.titan.2", "Frost: kein Erfrieren, Frostläufer, verlangsamt Angreifer");
        de("tooltip.celestialascent.set.titan.3", "Gezeiten: Unterwasseratmung, schnelles Schwimmen, Gunst des Delfins");
        de("tooltip.celestialascent.set.titan.4", "Sturm: Tempo, Blitze schlagen in Angreifer ein");
        de("tooltip.celestialascent.set.titan.5", "Magma: Feuerimmunität, über Lava laufen, verbrennt Angreifer");
        de("block.celestialascent.titan_forge", "Titanenschmiede");
        de("container.celestialascent.titan_forge", "Titanenschmiede");
        de("message.celestialascent.titan_awakens", "Der %s erwacht!");
        de("message.celestialascent.titan_present", "Hier regt sich bereits ein Titan");
        de("message.celestialascent.wrong_sigil", "Dieser Altar antwortet einem anderen Element");
        de("message.celestialascent.altar_cooldown", "Der Altar erholt sich (%s Min.)");
        de("block.celestialascent.cooled_magma", "Abgekühltes Magma");

        // ---- empire ----
        de("item.celestialascent.dragon_heart", "Drachenherz");
        de("item.celestialascent.imperial_plating", "Imperiale Panzerplatte");
        de("item.celestialascent.ender_gear", "Enderzahnrad");
        de("item.celestialascent.colossus_core", "Kolosskern");
        de("item.celestialascent.imperial_seal", "Imperiales Siegel");
        de("item.celestialascent.imperial_helmet", "Imperialer Helm");
        de("item.celestialascent.imperial_chestplate", "Imperialer Harnisch");
        de("item.celestialascent.imperial_leggings", "Imperialer Beinschutz");
        de("item.celestialascent.imperial_boots", "Imperiale Stiefel");
        de("block.celestialascent.imperial_pylon", "Imperialer Pylon");
        de("block.celestialascent.imperial_barrier", "Imperiale Barriere");
        de("block.celestialascent.empty_throne", "Leerer Thron");
        de("block.celestialascent.imperial_forge", "Imperiale Schmiede");
        de("container.celestialascent.imperial_forge", "Imperiale Schmiede");
        de("entity.celestialascent.sentinel_construct", "Wächterkonstrukt");
        de("entity.celestialascent.ender_colossus", "Ender-Koloss");
        de("entity.celestialascent.ender_merchant", "Ender-Händler");
        de("message.celestialascent.dragon_heart", "Das Herz des Drachen schlägt noch. Auf den äußeren Inseln regt sich das verlorene Ender-Imperium ...");
        de("message.celestialascent.pylon_guarded", "Ein Wächterkonstrukt bewacht diesen Pylon");
        de("message.celestialascent.pylon_needs", "Um diesen Pylon wiederherzustellen, bring %s Imperiale Panzerplatten, %s Purpurblöcke und %s");
        de("message.celestialascent.pylon_restore.craft", "Der Pylon der Schmiede erwacht! Die Imperiale Schmiede gehört dir.");
        de("message.celestialascent.pylon_restore.trade", "Der Pylon des Handels leuchtet. Ein Ender-Händler tritt aus der Leere.");
        de("message.celestialascent.pylon_restore.throne", "Der Pylon des Throns brüllt. Die Barriere der Thronhalle fällt!");
        de("message.celestialascent.pylon_restored.craft", "Pylon der Schmiede (wiederhergestellt)");
        de("message.celestialascent.pylon_restored.trade", "Pylon des Handels (wiederhergestellt)");
        de("message.celestialascent.pylon_restored.throne", "Pylon des Throns (wiederhergestellt)");
        de("message.celestialascent.throne_hint", "Der Thron verlangt nach einem Drachenherz");
        de("message.celestialascent.colossus_awakens", "Der Ender-Koloss erhebt sich vom Leeren Thron!");
        de("tooltip.celestialascent.set.imperial", "Imperiales Set (alle 4 Teile):");
        de("tooltip.celestialascent.set.imperial.1", "Enderblink: Taste für Rüstungsfähigkeit drücken (H)");
        de("tooltip.celestialascent.set.imperial.2", "Endermen bleiben ruhig; +1 Reichweite");

        // ---- stars ----
        de("block.celestialascent.starstone", "Sternstein");
        de("block.celestialascent.starlit_starstone", "Leuchtender Sternstein");
        de("block.celestialascent.starstone_bricks", "Sternsteinziegel");
        de("block.celestialascent.stardust_ore", "Sternenstaub-Erz");
        de("block.celestialascent.star_crystal", "Sternkristall");
        de("block.celestialascent.star_gate_frame", "Sternentor-Rahmen");
        de("block.celestialascent.star_gate_pedestal", "Sternentor-Podest");
        de("block.celestialascent.star_portal", "Sternenportal");
        de("block.celestialascent.seraph_altar", "Seraph-Altar");
        de("block.celestialascent.leviathan_altar", "Leviathan-Altar");
        de("block.celestialascent.herald_altar", "Herold-Altar");
        de("block.celestialascent.sky_altar", "Himmelsaltar");
        de("container.celestialascent.sky_altar", "Himmelsaltar");
        de("gui.celestialascent.needs_night_sky", "Braucht den offenen Nachthimmel");
        de("item.celestialascent.stardust", "Sternenstaub");
        de("item.celestialascent.dormant_star_core", "Ruhender Sternkern");
        de("item.celestialascent.star_core", "Sternkern");
        de("item.celestialascent.star_compass", "Sternenkompass");
        de("item.celestialascent.stellar_helmet", "Stellarer Helm");
        de("item.celestialascent.stellar_chestplate", "Stellarer Harnisch");
        de("item.celestialascent.stellar_leggings", "Stellarer Beinschutz");
        de("item.celestialascent.stellar_boots", "Stellare Stiefel");
        de("entity.celestialascent.astral_seraph", "Astralseraph");
        de("entity.celestialascent.nebula_leviathan", "Nebelleviathan");
        de("entity.celestialascent.sun_herald", "Sonnenherold");
        de("message.celestialascent.gate_needs_head", "Das Podest erwartet einen Drachenkopf");
        de("message.celestialascent.gate_head", "Der Drachenkopf ruht auf dem Podest. Zeige nun das Imperiale Siegel vor.");
        de("message.celestialascent.gate_needs_seal", "Zeige das Imperiale Siegel vor, um das Tor zu öffnen");
        de("message.celestialascent.gate_open", "Das Sternentor öffnet sich zu den Gefallenen Sternen!");
        de("message.celestialascent.compass_spins", "Die Nadel dreht sich wild. Er funktioniert nur im End.");
        de("message.celestialascent.compass_nothing", "Kein Sternentor antwortet dem Kompass");
        de("message.celestialascent.compass_points", "Ein Sternentor liegt im %s, %s Blöcke entfernt");
        de("direction.celestialascent.north", "Norden");
        de("direction.celestialascent.north_east", "Nordosten");
        de("direction.celestialascent.east", "Osten");
        de("direction.celestialascent.south_east", "Südosten");
        de("direction.celestialascent.south", "Süden");
        de("direction.celestialascent.south_west", "Südwesten");
        de("direction.celestialascent.west", "Westen");
        de("direction.celestialascent.north_west", "Nordwesten");
        de("message.celestialascent.altar_offer", "Opfere dem Altar %s × %s");
        de("message.celestialascent.altar_requires", "Du musst zuerst den %s besiegen");
        de("message.celestialascent.herald_eclipse", "Der Sonnenherold verdunkelt den Himmel: FINSTERNIS!");
        de("message.celestialascent.herald_supernova", "Der Sonnenherold glüht weiß. Such Deckung vor der SUPERNOVA!");
        de("tooltip.celestialascent.set.stellar", "Stellares Set (alle 4 Teile):");
        de("tooltip.celestialascent.set.stellar.1", "Sternengleiten: sanft fallen (schleichen zum Fallenlassen)");
        de("tooltip.celestialascent.set.stellar.2", "Regeneration unter dem Nachthimmel");
        de("tooltip.celestialascent.set.stellar.3", "Nachtsicht (mit G umschalten)");
        de("message.celestialascent.night_vision_on", "Nachtsicht an");
        de("message.celestialascent.night_vision_off", "Nachtsicht aus");

        // ---- abyss ----
        de("block.celestialascent.abyssal_stone", "Abgrundstein");
        de("block.celestialascent.void_essence_ore", "Leerenessenz-Erz");
        de("block.celestialascent.void_infuser", "Leereninfusor");
        de("container.celestialascent.void_infuser", "Leereninfusor");
        de("block.celestialascent.ascension_altar", "Aufstiegsaltar");
        de("container.celestialascent.ascension_altar", "Aufstiegsaltar");
        de("item.celestialascent.void_essence", "Leerenessenz");
        de("item.celestialascent.void_heart", "Leerenherz");
        de("item.celestialascent.primordial_core", "Urkern");
        de("item.celestialascent.abyssal_beacon", "Abgrundleuchtfeuer");
        de("item.celestialascent.ascension_pearl", "Aufstiegsperle");
        de("item.celestialascent.void_helmet", "Leerenhelm");
        de("item.celestialascent.void_chestplate", "Leerenharnisch");
        de("item.celestialascent.void_leggings", "Leerenbeinschutz");
        de("item.celestialascent.void_boots", "Leerenstiefel");
        de("item.celestialascent.ascendant_helmet", "Aufgestiegene Krone");
        de("item.celestialascent.ascendant_chestplate", "Aufgestiegener Harnisch");
        de("item.celestialascent.ascendant_leggings", "Aufgestiegener Beinschutz");
        de("item.celestialascent.ascendant_boots", "Aufgestiegene Stiefel");
        de("entity.celestialascent.void_wraith", "Leerengeist");
        de("entity.celestialascent.void_sovereign", "Leerenherrscher");
        de("tooltip.celestialascent.set.void", "Leerenset (alle 4 Teile):");
        de("tooltip.celestialascent.set.void.1", "Leerensprint: Taste für Rüstungsfähigkeit drücken (H)");
        de("tooltip.celestialascent.set.void.2", "Immun gegen Ausdörrung und Dunkelheit; +2 Herzen, +10% Tempo");
        de("tooltip.celestialascent.set.void.3", "Die Leere kann dich nicht holen");
        de("tooltip.celestialascent.set.ascendant", "Aufgestiegenes Set (alle 4 Teile):");
        de("tooltip.celestialascent.set.ascendant.1", "Kreativflug, +10 Herzen, +6 Schaden, +25% Tempo, +2 Reichweite");
        de("tooltip.celestialascent.set.ascendant.2", "Immun gegen Feuer, Lava, Fallschaden, Ertrinken, Erfrieren, Ausdörrung und die Leere");
        de("tooltip.celestialascent.set.ascendant.3", "Nie hungrig; dauerhaft Regeneration II; unzerbrechlich");
        de("tooltip.celestialascent.set.ascendant.4", "Alle vier Titanenelemente auf Stufe II");
        de("tooltip.celestialascent.set.ascendant.5", "H: Enderblink · Schleichen+H: Leerensprint · G: Nachtsicht");
        de("message.celestialascent.abyss_rejects", "Die Leere unter dir weist dich ab. Besiege zuerst den Sonnenherold.");
        de("message.celestialascent.abyss_enter", "Du fällst durch den Grund der Sterne ... in den Abgrund.");
        de("message.celestialascent.beacon_deeper", "Das Leuchtfeuer antwortet nur tief im Abgrund (unter y=40)");
        de("message.celestialascent.sovereign_awakens", "DER LEERENHERRSCHER ERWACHT");
        de("message.celestialascent.sovereign_phase_1", "Der Herrscher ruft die Geister der Tiefe!");
        de("message.celestialascent.sovereign_phase_3", "DIE AUSLÖSCHUNG HAT BEGONNEN");

        // ---- progression ----
        de("message.celestialascent.boss_defeated", "%s wurde besiegt!");
        de("message.celestialascent.constellation", "Ein neues Sternbild erscheint an deinem Nachthimmel: %s");
        de("constellation.celestialascent.frost", "Die Gletscherkrone");
        de("constellation.celestialascent.tide", "Das Kielwasser des Leviathans");
        de("constellation.celestialascent.storm", "Der Donnerspeer");
        de("constellation.celestialascent.magma", "Das Glutherz");
        de("constellation.celestialascent.dragon", "Der letzte Drache");
        de("constellation.celestialascent.colossus", "Der gefallene Thron");
        de("constellation.celestialascent.seraph", "Die Astralschwinge");
        de("constellation.celestialascent.leviathan", "Die Nebelwindung");
        de("constellation.celestialascent.herald", "Der Herold der Sonne");
        de("constellation.celestialascent.sovereign", "Der Leerenherrscher");

        // ---- boss stages ----
        de("boss.celestialascent.frost_titan.stage2", "Gletscherzorn");
        de("boss.celestialascent.frost_titan.stage3", "Absoluter Nullpunkt");
        de("boss.celestialascent.tide_titan.stage2", "Steigende Flut");
        de("boss.celestialascent.tide_titan.stage3", "Tsunami");
        de("boss.celestialascent.storm_titan.stage2", "Aufziehender Sturm");
        de("boss.celestialascent.storm_titan.stage3", "Orkan");
        de("boss.celestialascent.magma_titan.stage2", "Glühender Kern");
        de("boss.celestialascent.magma_titan.stage3", "Kataklysmus");
        de("boss.celestialascent.sentinel_construct.stage2", "Übertaktet");
        de("boss.celestialascent.sentinel_construct.stage3", "Überlastung");
        de("boss.celestialascent.ender_colossus.stage2", "Rissgänger");
        de("boss.celestialascent.ender_colossus.stage3", "Schwerkraftkollaps");
        de("boss.celestialascent.astral_seraph.stage2", "Strahlende Schwingen");
        de("boss.celestialascent.astral_seraph.stage3", "Kristallchor");
        de("boss.celestialascent.nebula_leviathan.stage2", "Hungrige Tiefe");
        de("boss.celestialascent.nebula_leviathan.stage3", "Sternenfresser");
        de("boss.celestialascent.sun_herald.stage2", "Finsternis");
        de("boss.celestialascent.sun_herald.stage3", "Supernova");
        de("boss.celestialascent.void_sovereign.stage2", "Die Tiefe ruft");
        de("boss.celestialascent.void_sovereign.stage3", "Die Auslöschung");

        // ---- attack hints ----
        de("message.celestialascent.hint.absolute_zero", "Bleib in Bewegung oder erfriere!");
        de("message.celestialascent.hint.tsunami", "Spring über die Welle!");
        de("message.celestialascent.hint.tempest", "Finde eine Lücke im Blitzring!");
        de("message.celestialascent.hint.cataclysm", "Weg von den glühenden Rissen!");
        de("message.celestialascent.hint.overload", "Spring über den Strahl!");
        de("message.celestialascent.hint.crystal_choir", "Zerschlag die Kristalle, bevor sie ihn heilen!");
        de("message.celestialascent.hint.devour", "Lauf weg von seinem Schlund!");

        // ---- stages: banner, armor evolution ----
        de("boss.celestialascent.banner", "STUFE %s");
        de("tooltip.celestialascent.stage", "Stufe %s");
        de("tooltip.celestialascent.max_stage", "Voll entwickelt");
        de("tooltip.celestialascent.resonance", "%s / %s Resonanz");
        de("tooltip.celestialascent.ready", "Bereit zur Entwicklung: %s");
        de("tooltip.celestialascent.resonance_hint", "Kämpfe damit, um die Resonanz zu füllen");
        de("message.celestialascent.resonance_full", "%s resoniert! Schließe die Entwicklung ab: %s");
        de("message.celestialascent.evolved", "%s hat Stufe %s erreicht!");
        de("tooltip.celestialascent.set_stage.titan.2", "Set-Stufe II: Jedes Element zählt eine Stufe höher");
        de("tooltip.celestialascent.set_stage.titan.3", "Set-Stufe III: dauerhaft Resistenz I");
        de("tooltip.celestialascent.set_stage.imperial.2", "Set-Stufe II: Blink 16 Blöcke, alle 3,75 s");
        de("tooltip.celestialascent.set_stage.imperial.3", "Set-Stufe III: Blink 20 Blöcke, alle 2,5 s, Druckwelle bei der Ankunft");
        de("tooltip.celestialascent.set_stage.stellar.2", "Set-Stufe II: Regeneration II unter dem Nachthimmel");
        de("tooltip.celestialascent.set_stage.stellar.3", "Set-Stufe III: Sternschnuppen treffen nachts deine Angreifer");
        de("tooltip.celestialascent.set_stage.void.2", "Set-Stufe II: Leerensprint alle 3 s");
        de("tooltip.celestialascent.set_stage.void.3", "Set-Stufe III: Leerensprint alle 2 s, reißt Monster mit");
        de("tooltip.celestialascent.set_stage.ascendant.2", "Set-Stufe II: weiterer Blink, schnellerer Sprint");
        de("tooltip.celestialascent.set_stage.ascendant.3", "Set-Stufe III: Verbündete in deiner Nähe regenerieren");

        // ---- codex ----
        de("item.celestialascent.celestial_codex", "Himmelskodex");
        de("tooltip.celestialascent.codex", "Rechtsklick zum Lesen");
        de("message.celestialascent.codex_given", "Du hast den Himmelskodex erhalten. Rechtsklicke ihn, um zu sehen, was als Nächstes zu tun ist.");
    }
}
