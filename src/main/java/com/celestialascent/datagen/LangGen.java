package com.celestialascent.datagen;

import com.celestialascent.CelestialAscent;
import com.celestialascent.economy.CoinTier;
import com.celestialascent.economy.Economy;
import com.celestialascent.titans.Element;
import com.celestialascent.titans.Titans;
import net.minecraft.data.PackOutput;
import net.neoforged.neoforge.common.data.LanguageProvider;

import java.util.LinkedHashMap;
import java.util.Map;

public class LangGen extends LanguageProvider {
    public LangGen(PackOutput out) {
        super(out, CelestialAscent.MODID, "en_us");
    }

    private static String title(String id) {
        StringBuilder sb = new StringBuilder();
        for (String w : id.split("_")) {
            if (!sb.isEmpty()) sb.append(' ');
            sb.append(Character.toUpperCase(w.charAt(0))).append(w.substring(1));
        }
        return sb.toString();
    }

    /** All English entries, collected without writing a file (used to check the German translation). */
    static Map<String, String> english() {
        Map<String, String> out = new LinkedHashMap<>();
        new LangGen(null) {
            @Override
            public void add(String key, String value) {
                if (out.put(key, value) != null) throw new IllegalStateException("Duplicate key " + key);
            }
        }.addTranslations();
        return out;
    }

    @Override
    protected void addTranslations() {
        add("itemGroup.celestialascent", "Celestial Ascent");
        add("key.categories.celestialascent", "Celestial Ascent");
        add("key.celestialascent.ability", "Armor Ability");
        add("key.celestialascent.toggle", "Armor Toggle");

        // ---- economy ----
        for (CoinTier t : CoinTier.values()) add(Economy.coin(t), title(t.id));
        add(Economy.BANK_COUNTER.get(), "Bank Counter");
        add(Economy.SHOP_STALL.get(), "Shop Stall");
        add(Economy.TITAN_ANVIL.get(), "Titan Anvil");
        add(Economy.RELIC_PEDESTAL.get(), "Relic Pedestal");
        add(Economy.CELESTIAL_CRYSTAL.get(), "Celestial Crystal");
        add("entity.minecraft.villager.celestialascent.banker", "Banker");
        add("entity.minecraft.villager.celestialascent.titansmith", "Titansmith");
        add("entity.minecraft.villager.celestialascent.relic_dealer", "Relic Dealer");
        add("tooltip.celestialascent.coin_value", "Worth %s");
        add("tooltip.celestialascent.coin_stack", "Stack: %s");
        add("container.celestialascent.bank", "Bank");
        add("container.celestialascent.shop", "%s's Shop");
        add("container.celestialascent.shop_manage", "Manage Shop");
        add("gui.celestialascent.balance", "Balance: %s");
        add("gui.celestialascent.carried", "Carried: %s");
        add("gui.celestialascent.withdraw", "Withdraw one %s (%s)\nShift-click: withdraw ten");
        add("gui.celestialascent.deposit_all", "Deposit All Coins");
        add("gui.celestialascent.price", "Price per bundle");
        add("gui.celestialascent.bundle", "Bundle: %s");
        add("gui.celestialascent.buy", "Buy");
        add("gui.celestialascent.sold_out", "Sold out");
        add("gui.celestialascent.in_stock", "In stock: %s");
        add("message.celestialascent.shop_sold", "%s bought %s × %s from your shop for %s");
        add("message.celestialascent.shop_own_shop", "You can't buy from your own shop");
        add("message.celestialascent.shop_out_of_stock", "This shop is out of stock");
        add("message.celestialascent.shop_cannot_afford", "You can't afford this (coins or bank balance)");

        add(com.celestialascent.economy.Economy.QUEST_BOARD.get(), "Quest Board");
        add("container.celestialascent.quest_board", "Quest Board");
        add("gui.celestialascent.deliver", "Deliver");
        add("gui.celestialascent.quest_done", "Done");
        add("gui.celestialascent.quest_line", "Bring %s × %s");
        add("message.celestialascent.quest_missing", "You need %s × %s");
        add("message.celestialascent.prosperity", "Village prosperity: %s (next building at %s)");
        add("message.celestialascent.village_grew", "The village has grown: a new %s was built!");
        add("message.celestialascent.stall_rented", "You rented this stall. Right-click to stock it.");
        add("message.celestialascent.stall_unclaimed", "Unclaimed stall. Sneak + right-click to rent it for %s");
        add("building.celestialascent.market_stall", "Market Stall");
        add("building.celestialascent.lamp_post", "Lamp Post");
        add("building.celestialascent.cottage", "Cottage");
        add("building.celestialascent.bank_kiosk", "Bank Kiosk");
        add("building.celestialascent.garden", "Garden");
        add("building.celestialascent.fountain", "Fountain");
        add("building.celestialascent.watchtower", "Watchtower");
        add("building.celestialascent.smithy", "Smithy");

        // ---- titans ----
        add(Titans.TITAN_SHARD.get(), "Titan Shard");
        for (Element e : Element.values()) {
            String el = title(e.key);
            add("element.celestialascent." + e.key, el);
            add(Titans.CORES.get(e).get(), el + " Titan Core");
            add(Titans.SIGILS.get(e).get(), el + " Sigil");
            add(Titans.ALTARS.get(e).get(), el + " Shrine Altar");
            add("entity.celestialascent." + e.key + "_titan", el + " Titan");
            add("filled_map.celestialascent." + e.key + "_shrine", el + " Shrine Map");
        }
        add(Titans.HELMET.get(), "Titan Helmet");
        add(Titans.CHESTPLATE.get(), "Titan Chestplate");
        add(Titans.LEGGINGS.get(), "Titan Leggings");
        add(Titans.BOOTS.get(), "Titan Boots");
        add(Titans.TITAN_FORGE.get(), "Titan Forge");
        add(Titans.COOLED_MAGMA.get(), "Cooled Magma");
        add("container.celestialascent.titan_forge", "Titan Forge");
        add("item.celestialascent.titan_infused", "%s-Infused %s");
        add("tooltip.celestialascent.element", "Element: %s");
        add("tooltip.celestialascent.no_element", "Not infused");
        add("tooltip.celestialascent.sigil", "Use on a %s to summon its titan");
        add("tooltip.celestialascent.set.titan", "Titan Set (all 4 pieces):");
        add("tooltip.celestialascent.set.titan.1", "Each element: level I on one piece, II on two");
        add("tooltip.celestialascent.set.titan.2", "Frost: freeze immunity, frost walking, chills attackers");
        add("tooltip.celestialascent.set.titan.3", "Tide: water breathing, fast swimming, dolphin's grace");
        add("tooltip.celestialascent.set.titan.4", "Storm: speed, lightning strikes back at attackers");
        add("tooltip.celestialascent.set.titan.5", "Magma: fire immunity, lava walking, burns attackers");
        add("message.celestialascent.wrong_sigil", "This altar answers to a different element");
        add("message.celestialascent.titan_present", "A titan already stirs here");
        add("message.celestialascent.altar_cooldown", "The altar is recovering (%s min)");
        add("message.celestialascent.titan_awakens", "The %s awakens!");

        // ---- empire ----
        add(com.celestialascent.empire.Empire.DRAGON_HEART.get(), "Dragon Heart");
        add(com.celestialascent.empire.Empire.IMPERIAL_PLATING.get(), "Imperial Plating");
        add(com.celestialascent.empire.Empire.ENDER_GEAR.get(), "Ender Gear");
        add(com.celestialascent.empire.Empire.COLOSSUS_CORE.get(), "Colossus Core");
        add(com.celestialascent.empire.Empire.IMPERIAL_SEAL.get(), "Imperial Seal");
        add(com.celestialascent.empire.Empire.HELMET.get(), "Imperial Helmet");
        add(com.celestialascent.empire.Empire.CHESTPLATE.get(), "Imperial Chestplate");
        add(com.celestialascent.empire.Empire.LEGGINGS.get(), "Imperial Leggings");
        add(com.celestialascent.empire.Empire.BOOTS.get(), "Imperial Boots");
        add(com.celestialascent.empire.Empire.PYLON.get(), "Imperial Pylon");
        add(com.celestialascent.empire.Empire.IMPERIAL_BARRIER.get(), "Imperial Barrier");
        add(com.celestialascent.empire.Empire.THRONE.get(), "Empty Throne");
        add(com.celestialascent.empire.Empire.IMPERIAL_FORGE.get(), "Imperial Forge");
        add("container.celestialascent.imperial_forge", "Imperial Forge");
        add("entity.celestialascent.sentinel_construct", "Sentinel Construct");
        add("entity.celestialascent.ender_colossus", "Ender Colossus");
        add("entity.celestialascent.ender_merchant", "Ender Merchant");
        add("tooltip.celestialascent.set.imperial", "Imperial Set (all 4 pieces):");
        add("tooltip.celestialascent.set.imperial.1", "Ender Blink: press the Armor Ability key (H)");
        add("tooltip.celestialascent.set.imperial.2", "Endermen stay calm; +1 reach");
        add("message.celestialascent.dragon_heart", "The dragon's heart still beats. The Lost Ender Empire stirs on the outer islands...");
        add("message.celestialascent.pylon_guarded", "A Sentinel Construct guards this pylon");
        add("message.celestialascent.pylon_needs", "To restore this pylon bring %s Imperial Plating, %s Purpur Blocks and %s");
        add("message.celestialascent.pylon_restore.craft", "The Pylon of Craft blazes to life! The Imperial Forge is yours.");
        add("message.celestialascent.pylon_restore.trade", "The Pylon of Trade glows. An Ender Merchant steps out of the void.");
        add("message.celestialascent.pylon_restore.throne", "The Pylon of the Throne roars. The Throne Hall's barrier falls!");
        add("message.celestialascent.pylon_restored.craft", "Pylon of Craft (restored)");
        add("message.celestialascent.pylon_restored.trade", "Pylon of Trade (restored)");
        add("message.celestialascent.pylon_restored.throne", "Pylon of the Throne (restored)");
        add("message.celestialascent.throne_hint", "The throne hungers for a Dragon Heart");
        add("message.celestialascent.colossus_awakens", "The Ender Colossus rises from the Empty Throne!");

        // ---- stars & abyss ----
        add(com.celestialascent.stars.Stars.STARSTONE.get(), "Starstone");
        add(com.celestialascent.stars.Stars.STARLIT_STARSTONE.get(), "Starlit Starstone");
        add(com.celestialascent.stars.Stars.STARSTONE_BRICKS.get(), "Starstone Bricks");
        add(com.celestialascent.stars.Stars.STARDUST_ORE.get(), "Stardust Ore");
        add(com.celestialascent.stars.Stars.STAR_CRYSTAL.get(), "Star Crystal");
        add(com.celestialascent.stars.Stars.STAR_GATE_FRAME.get(), "Star Gate Frame");
        add(com.celestialascent.stars.Stars.STAR_GATE_PEDESTAL.get(), "Star Gate Pedestal");
        add(com.celestialascent.stars.Stars.STAR_PORTAL.get(), "Star Portal");
        add(com.celestialascent.stars.Stars.STARDUST.get(), "Stardust");
        add(com.celestialascent.stars.Stars.DORMANT_STAR_CORE.get(), "Dormant Star Core");
        add(com.celestialascent.stars.Stars.STAR_CORE.get(), "Star Core");
        add(com.celestialascent.stars.Stars.STAR_COMPASS.get(), "Star Compass");
        add(com.celestialascent.stars.Stars.HELMET.get(), "Stellar Helmet");
        add(com.celestialascent.stars.Stars.CHESTPLATE.get(), "Stellar Chestplate");
        add(com.celestialascent.stars.Stars.LEGGINGS.get(), "Stellar Leggings");
        add(com.celestialascent.stars.Stars.BOOTS.get(), "Stellar Boots");
        add(com.celestialascent.stars.Stars.SERAPH_ALTAR.get(), "Seraph Altar");
        add(com.celestialascent.stars.Stars.LEVIATHAN_ALTAR.get(), "Leviathan Altar");
        add(com.celestialascent.stars.Stars.HERALD_ALTAR.get(), "Herald Altar");
        add(com.celestialascent.stars.Stars.SKY_ALTAR.get(), "Sky Altar");
        add(com.celestialascent.abyss.Abyss.ABYSSAL_STONE.get(), "Abyssal Stone");
        add(com.celestialascent.abyss.Abyss.VOID_ESSENCE_ORE.get(), "Void Essence Ore");
        add(com.celestialascent.abyss.Abyss.VOID_ESSENCE.get(), "Void Essence");
        add(com.celestialascent.abyss.Abyss.VOID_HEART.get(), "Void Heart");
        add(com.celestialascent.abyss.Abyss.PRIMORDIAL_CORE.get(), "Primordial Core");
        add(com.celestialascent.abyss.Abyss.ABYSSAL_BEACON.get(), "Abyssal Beacon");
        add(com.celestialascent.abyss.Abyss.ASCENSION_PEARL.get(), "Ascension Pearl");
        add(com.celestialascent.abyss.Abyss.VOID_HELMET.get(), "Void Helmet");
        add(com.celestialascent.abyss.Abyss.VOID_CHESTPLATE.get(), "Void Chestplate");
        add(com.celestialascent.abyss.Abyss.VOID_LEGGINGS.get(), "Void Leggings");
        add(com.celestialascent.abyss.Abyss.VOID_BOOTS.get(), "Void Boots");
        add(com.celestialascent.abyss.Abyss.ASC_HELMET.get(), "Ascendant Crown");
        add(com.celestialascent.abyss.Abyss.ASC_CHESTPLATE.get(), "Ascendant Chestplate");
        add(com.celestialascent.abyss.Abyss.ASC_LEGGINGS.get(), "Ascendant Leggings");
        add(com.celestialascent.abyss.Abyss.ASC_BOOTS.get(), "Ascendant Boots");
        add(com.celestialascent.abyss.Abyss.VOID_INFUSER.get(), "Void Infuser");
        add(com.celestialascent.abyss.Abyss.ASCENSION_ALTAR.get(), "Ascension Altar");
        add("container.celestialascent.sky_altar", "Sky Altar");
        add("container.celestialascent.void_infuser", "Void Infuser");
        add("container.celestialascent.ascension_altar", "Ascension Altar");
        add("gui.celestialascent.needs_night_sky", "Needs the open night sky");
        add("entity.celestialascent.astral_seraph", "Astral Seraph");
        add("entity.celestialascent.nebula_leviathan", "Nebula Leviathan");
        add("entity.celestialascent.sun_herald", "Sun Herald");
        add("entity.celestialascent.void_sovereign", "Void Sovereign");
        add("entity.celestialascent.void_wraith", "Void Wraith");
        add("tooltip.celestialascent.set.stellar", "Stellar Set (all 4 pieces):");
        add("tooltip.celestialascent.set.stellar.1", "Star glide: fall gently (sneak to drop)");
        add("tooltip.celestialascent.set.stellar.2", "Regeneration under the night sky");
        add("tooltip.celestialascent.set.stellar.3", "Night vision (toggle with G)");
        add("tooltip.celestialascent.set.void", "Void Set (all 4 pieces):");
        add("tooltip.celestialascent.set.void.1", "Void Dash: press the Armor Ability key (H)");
        add("tooltip.celestialascent.set.void.2", "Immune to wither and darkness; +2 hearts, +10% speed");
        add("tooltip.celestialascent.set.void.3", "The void cannot claim you");
        add("tooltip.celestialascent.set.ascendant", "Ascendant Set (all 4 pieces):");
        add("tooltip.celestialascent.set.ascendant.1", "Creative flight, +10 hearts, +6 damage, +25% speed, +2 reach");
        add("tooltip.celestialascent.set.ascendant.2", "Immune to fire, lava, falling, drowning, freezing, wither and the void");
        add("tooltip.celestialascent.set.ascendant.3", "Never hungry; constant Regeneration II; unbreakable");
        add("tooltip.celestialascent.set.ascendant.4", "All four titan elements at level II");
        add("tooltip.celestialascent.set.ascendant.5", "H: Ender Blink · Sneak+H: Void Dash · G: night vision");
        add("message.celestialascent.altar_requires", "You must first defeat the %s");
        add("message.celestialascent.altar_offer", "Offer %s × %s to the altar");
        add("message.celestialascent.gate_head", "The dragon head settles on the pedestal. Now present the Imperial Seal.");
        add("message.celestialascent.gate_needs_head", "The pedestal awaits a Dragon Head");
        add("message.celestialascent.gate_needs_seal", "Present the Imperial Seal to open the gate");
        add("message.celestialascent.gate_open", "The Star Gate opens onto the Fallen Stars!");
        add("message.celestialascent.compass_spins", "The needle spins wildly. It only works in the End.");
        add("message.celestialascent.compass_nothing", "No Star Gate answers the compass");
        add("message.celestialascent.compass_points", "A Star Gate lies %s, %s blocks away");
        add("direction.celestialascent.north", "north");
        add("direction.celestialascent.north_east", "north-east");
        add("direction.celestialascent.east", "east");
        add("direction.celestialascent.south_east", "south-east");
        add("direction.celestialascent.south", "south");
        add("direction.celestialascent.south_west", "south-west");
        add("direction.celestialascent.west", "west");
        add("direction.celestialascent.north_west", "north-west");
        add("message.celestialascent.night_vision_on", "Night vision on");
        add("message.celestialascent.night_vision_off", "Night vision off");
        add("message.celestialascent.herald_eclipse", "The Sun Herald darkens the sky: ECLIPSE!");
        add("message.celestialascent.herald_supernova", "The Sun Herald burns white-hot. Find cover before the SUPERNOVA!");
        add("message.celestialascent.abyss_rejects", "The void below rejects you. Defeat the Sun Herald first.");
        add("message.celestialascent.abyss_enter", "You fall through the bottom of the stars... into the Abyss.");
        add("message.celestialascent.beacon_deeper", "The beacon only answers deep in the Abyss (below y=40)");
        add("message.celestialascent.sovereign_awakens", "THE VOID SOVEREIGN AWAKENS");
        add("message.celestialascent.sovereign_phase_1", "The Sovereign calls the wraiths of the deep!");
        add("message.celestialascent.sovereign_phase_3", "THE UNMAKING HAS BEGUN");

        // ---- progression ----
        add("message.celestialascent.boss_defeated", "%s has been defeated!");
        add("message.celestialascent.constellation", "A new constellation appears in your night sky: %s");
        add("constellation.celestialascent.frost", "The Glacier Crown");
        add("constellation.celestialascent.tide", "The Leviathan's Wake");
        add("constellation.celestialascent.storm", "The Thunder Spear");
        add("constellation.celestialascent.magma", "The Ember Heart");
        add("constellation.celestialascent.dragon", "The Last Dragon");
        add("constellation.celestialascent.colossus", "The Fallen Throne");
        add("constellation.celestialascent.seraph", "The Astral Wing");
        add("constellation.celestialascent.leviathan", "The Nebula Coil");
        add("constellation.celestialascent.herald", "The Sun's Herald");
        add("constellation.celestialascent.sovereign", "The Void Sovereign");

        // ---- boss stages ----
        add("boss.celestialascent.frost_titan.stage2", "Glacial Wrath");
        add("boss.celestialascent.frost_titan.stage3", "Absolute Zero");
        add("boss.celestialascent.tide_titan.stage2", "Rising Tide");
        add("boss.celestialascent.tide_titan.stage3", "Tsunami");
        add("boss.celestialascent.storm_titan.stage2", "Gathering Storm");
        add("boss.celestialascent.storm_titan.stage3", "Tempest");
        add("boss.celestialascent.magma_titan.stage2", "Molten Core");
        add("boss.celestialascent.magma_titan.stage3", "Cataclysm");
        add("boss.celestialascent.sentinel_construct.stage2", "Overclocked");
        add("boss.celestialascent.sentinel_construct.stage3", "Overload");
        add("boss.celestialascent.ender_colossus.stage2", "Rift Walker");
        add("boss.celestialascent.ender_colossus.stage3", "Gravity Collapse");
        add("boss.celestialascent.astral_seraph.stage2", "Radiant Wings");
        add("boss.celestialascent.astral_seraph.stage3", "Crystal Choir");
        add("boss.celestialascent.nebula_leviathan.stage2", "Starving Deep");
        add("boss.celestialascent.nebula_leviathan.stage3", "Devourer of Stars");
        add("boss.celestialascent.sun_herald.stage2", "Eclipse");
        add("boss.celestialascent.sun_herald.stage3", "Supernova");
        add("boss.celestialascent.void_sovereign.stage2", "The Deep Calls");
        add("boss.celestialascent.void_sovereign.stage3", "The Unmaking");

        // ---- attack hints ----
        add("message.celestialascent.hint.absolute_zero", "Keep moving or freeze!");
        add("message.celestialascent.hint.tsunami", "Jump over the wave!");
        add("message.celestialascent.hint.tempest", "Find a gap in the lightning ring!");
        add("message.celestialascent.hint.cataclysm", "Stay off the glowing cracks!");
        add("message.celestialascent.hint.overload", "Jump over the beam!");
        add("message.celestialascent.hint.crystal_choir", "Break the crystals before they heal it!");
        add("message.celestialascent.hint.devour", "Run from its maw!");

        // ---- stages: banner, armor evolution ----
        add("boss.celestialascent.banner", "STAGE %s");
        add("tooltip.celestialascent.stage", "Stage %s");
        add("tooltip.celestialascent.max_stage", "Fully evolved");
        add("tooltip.celestialascent.resonance", "%s / %s resonance");
        add("tooltip.celestialascent.ready", "Ready to evolve at: %s");
        add("tooltip.celestialascent.resonance_hint", "Fight while wearing it to fill its resonance");
        add("message.celestialascent.resonance_full", "%s is resonating! Complete its evolution at: %s");
        add("message.celestialascent.evolved", "%s reached stage %s!");
        add("tooltip.celestialascent.set_stage.titan.2", "Set stage II: every element counts one level higher");
        add("tooltip.celestialascent.set_stage.titan.3", "Set stage III: permanent Resistance I");
        add("tooltip.celestialascent.set_stage.imperial.2", "Set stage II: blink 16 blocks, every 3.75 s");
        add("tooltip.celestialascent.set_stage.imperial.3", "Set stage III: blink 20 blocks, every 2.5 s, shockwave on arrival");
        add("tooltip.celestialascent.set_stage.stellar.2", "Set stage II: Regeneration II under the night sky");
        add("tooltip.celestialascent.set_stage.stellar.3", "Set stage III: falling stars strike your attackers at night");
        add("tooltip.celestialascent.set_stage.void.2", "Set stage II: Void Dash every 3 s");
        add("tooltip.celestialascent.set_stage.void.3", "Set stage III: Void Dash every 2 s, tears through monsters");
        add("tooltip.celestialascent.set_stage.ascendant.2", "Set stage II: farther blink, faster dash");
        add("tooltip.celestialascent.set_stage.ascendant.3", "Set stage III: allies near you regenerate");

        // ---- codex ----
        add(com.celestialascent.guide.Guide.CODEX.get(), "Celestial Codex");
        add("tooltip.celestialascent.codex", "Right-click to read");
        add("message.celestialascent.codex_given", "You received the Celestial Codex. Right-click it to see what to do next.");
        for (var e : com.celestialascent.guide.GuideBook.strings().entrySet()) add(e.getKey(), e.getValue()[0]);
    }
}
