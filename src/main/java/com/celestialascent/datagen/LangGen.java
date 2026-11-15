package com.celestialascent.datagen;

import com.celestialascent.CelestialAscent;
import com.celestialascent.economy.CoinTier;
import com.celestialascent.economy.Economy;
import com.celestialascent.titans.Element;
import com.celestialascent.titans.Titans;
import net.minecraft.data.PackOutput;
import net.neoforged.neoforge.common.data.LanguageProvider;

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

    private void prefixed(String key, String value) {
        add(key, value);
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
    }
}
