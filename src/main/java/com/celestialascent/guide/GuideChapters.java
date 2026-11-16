package com.celestialascent.guide;

import com.celestialascent.abyss.Abyss;
import com.celestialascent.economy.CoinTier;
import com.celestialascent.economy.Economy;
import com.celestialascent.empire.Empire;
import com.celestialascent.guide.GuideBook.Arg;
import com.celestialascent.guide.GuideBook.Builder;
import com.celestialascent.guide.GuideBook.Chapter;
import com.celestialascent.guide.GuideBook.EntityArg;
import com.celestialascent.guide.GuideBook.ItemArg;
import com.celestialascent.guide.GuideBook.KeyArg;
import com.celestialascent.guide.GuideBook.Stack;
import com.celestialascent.stars.Stars;
import com.celestialascent.titans.Element;
import com.celestialascent.titans.Titans;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.ItemLike;

import java.util.List;
import java.util.function.Supplier;

/**
 * The codex text. Every number here mirrors the game code (recipes, costs, health, cooldowns);
 * station recipes and crafting ids are checked by GuideTests.
 */
public final class GuideChapters {
    private GuideChapters() {}

    private static Builder chapter(String id, Supplier<? extends ItemLike> icon, String en, String de) {
        return new Builder(id, icon, en, de);
    }

    private static Arg i(Supplier<? extends ItemLike> item) {
        return new ItemArg(item);
    }

    private static Arg e(Supplier<? extends EntityType<?>> type) {
        return new EntityArg(type);
    }

    private static final Arg ABILITY = new KeyArg("key.celestialascent.ability");
    private static final Arg TOGGLE = new KeyArg("key.celestialascent.toggle");

    private static Stack st(Supplier<? extends ItemLike> item, int count) {
        return new Stack(item, count);
    }

    private static Supplier<ItemLike> coin(CoinTier t) {
        return () -> Economy.coin(t);
    }

    public static final List<Chapter> ALL = List.of(
            // ------------------------------------------------------------------ getting started
            chapter("intro", Guide.CODEX, "Getting Started", "Erste Schritte")
                    .p("welcome",
                            "Celestial Ascent is a ladder of bosses beyond netherite and the Ender Dragon. Each boss drops what you need to reach the next one, and every step gives you a stronger armor set.",
                            "Celestial Ascent ist eine Leiter aus Bossen jenseits von Netherit und dem Enderdrachen. Jeder Boss lässt fallen, was du für den nächsten brauchst, und jede Stufe bringt dir ein stärkeres Rüstungsset.")
                    .h("ladder", "The ladder", "Die Leiter")
                    .p("ladder.list",
                            "1. Elemental Titans: Titan armor\n2. Ender Dragon: Dragon Heart\n3. Lost Ender Empire: Imperial armor\n4. Fallen Stars: Stellar armor\n5. The Abyss: Void armor\n6. Ascension: Ascendant armor",
                            "1. Elementar-Titanen: Titanenrüstung\n2. Enderdrache: Drachenherz\n3. Verlorenes Ender-Imperium: Imperiale Rüstung\n4. Gefallene Sterne: Stellare Rüstung\n5. Der Abgrund: Leerenrüstung\n6. Aufstieg: Aufgestiegene Rüstung")
                    .tip("ladder.tip",
                            "The first page of this book always shows your next step. Click it to jump to the right chapter.",
                            "Die erste Seite dieses Buchs zeigt immer deinen nächsten Schritt. Klicke darauf, um zum passenden Kapitel zu springen.")
                    .h("prepare", "Before you start", "Bevor du loslegst")
                    .p("prepare.text",
                            "Get full netherite armor with good enchantments first. Titan armor is forged from netherite pieces, and it keeps their enchantments, so they are not wasted.",
                            "Besorg dir zuerst volle Netheritrüstung mit guten Verzauberungen. Titanenrüstung wird aus Netheritteilen geschmiedet und behält deren Verzauberungen, sie sind also nicht verloren.")
                    .h("bosses", "Fighting bosses", "Bosse bekämpfen")
                    .p("bosses.text",
                            "One hit can take at most 8%% of a boss's health, so it takes many hits. Bosses can't be lured more than 48 blocks from their altar, and they teleport to you if you hide on a pillar.",
                            "Ein Treffer nimmt höchstens 8 %% der Lebenspunkte eines Bosses, du brauchst also viele Treffer. Bosse lassen sich nicht weiter als 48 Blöcke von ihrem Altar weglocken und teleportieren sich zu dir, wenn du dich auf einer Säule versteckst.")
                    .h("stages", "Three stages", "Drei Stufen")
                    .p("stages.text",
                            "Every boss evolves twice: at two thirds and at one third of its health it changes form, grows, glows brighter and learns new attacks. The boss bar shows the name of its stage.",
                            "Jeder Boss entwickelt sich zweimal: Bei zwei Dritteln und bei einem Drittel seiner Lebenspunkte verwandelt er sich, wächst, leuchtet stärker und lernt neue Angriffe. Die Lebensleiste zeigt den Namen seiner Stufe.")
                    .tip("stages.ultimate",
                            "In its third stage every boss has an ultimate attack of its own. When it starts, your action bar tells you how to survive it.",
                            "In der dritten Stufe hat jeder Boss einen eigenen Ultimate-Angriff. Wenn er beginnt, sagt dir die Aktionsleiste, wie du ihn überlebst.")
                    .p("bosses.team",
                            "Playing together? A boss gets 50%% more health for each extra player nearby. Everyone who dealt at least 5%% of its health in damage gets their own loot.",
                            "Spielt ihr zusammen? Ein Boss bekommt für jeden weiteren Spieler in der Nähe 50 %% mehr Lebenspunkte. Jeder, der mindestens 5 %% seiner Lebenspunkte als Schaden verursacht hat, bekommt eigene Beute.")
                    .p("bosses.stars",
                            "The first time you defeat a boss, its constellation appears in your night sky and you get a small permanent bonus.",
                            "Wenn du einen Boss zum ersten Mal besiegst, erscheint sein Sternbild an deinem Nachthimmel und du bekommst einen kleinen dauerhaften Bonus.")
                    .h("keys", "Keys", "Tasten")
                    .p("keys.text",
                            "%s uses your armor's ability. %s switches its effect on or off (for example night vision). You can change both under Options, Controls.",
                            "%s löst die Fähigkeit deiner Rüstung aus. %s schaltet ihren Effekt ein oder aus (zum Beispiel Nachtsicht). Du kannst beide unter Optionen, Steuerung ändern.",
                            ABILITY, TOGGLE)
                    .tip("lost",
                            "Lost this book? Craft a new one from a book and an amethyst shard.",
                            "Buch verloren? Stell aus einem Buch und einem Amethystsplitter ein neues her.")
                    .craft("celestial_codex")
                    .build(),

            // ------------------------------------------------------------------ economy
            chapter("economy", coin(CoinTier.GOLD), "Coins & Trade", "Münzen & Handel")
                    .p("coins",
                            "Aster coins come in seven tiers. Each is worth ten of the tier below:",
                            "Aster-Münzen gibt es in sieben Stufen. Jede ist zehn Münzen der Stufe darunter wert:")
                    .items(st(coin(CoinTier.COPPER), 1), st(coin(CoinTier.SILVER), 1), st(coin(CoinTier.GOLD), 1), st(coin(CoinTier.TITAN), 1),
                            st(coin(CoinTier.ENDER), 1), st(coin(CoinTier.STAR), 1), st(coin(CoinTier.VOID), 1))
                    .p("coins.values",
                            "%s 1\n%s 10\n%s 100\n%s 1,000\n%s 10,000\n%s 100,000\n%s 1,000,000",
                            "%s 1\n%s 10\n%s 100\n%s 1.000\n%s 10.000\n%s 100.000\n%s 1.000.000",
                            i(coin(CoinTier.COPPER)), i(coin(CoinTier.SILVER)), i(coin(CoinTier.GOLD)), i(coin(CoinTier.TITAN)),
                            i(coin(CoinTier.ENDER)), i(coin(CoinTier.STAR)), i(coin(CoinTier.VOID)))
                    .p("coins.earn",
                            "Your first coins come from a Banker villager (one emerald buys 5 Copper Asters), from boss loot and from Quest Boards.",
                            "Deine ersten Münzen bekommst du bei einem Bankier (ein Smaragd bringt 5 Kupferaster), als Bossbeute und an Auftragstafeln.")
                    .p("coins.split",
                            "Put any coin in the crafting grid to split it into ten of the tier below. To combine small coins, deposit them at a %s and withdraw bigger ones.",
                            "Leg eine Münze ins Handwerksfeld, um sie in zehn der Stufe darunter zu teilen. Um kleine Münzen zusammenzulegen, zahl sie an einem %s ein und heb größere ab.",
                            i(Economy.BANK_COUNTER))
                    .h("bank", "The bank", "Die Bank")
                    .p("bank.text",
                            "A %s keeps coins in your account. Your balance works at every bank, survives death, and shops and pylons can take payment from it.",
                            "Ein %s bewahrt Münzen auf deinem Konto auf. Dein Guthaben gilt an jeder Bank, bleibt beim Tod erhalten, und Läden und Pylonen können davon abbuchen.",
                            i(Economy.BANK_COUNTER))
                    .craft("bank_counter")
                    .h("shops", "Player shops", "Spielerläden")
                    .p("shops.text",
                            "Place a %s, fill its stock and set a price and bundle size. Buyers pay with coins or their bank balance, and the money goes straight into your account, even while you are offline.",
                            "Stell einen %s auf, füll sein Lager und leg Preis und Bündelgröße fest. Käufer zahlen mit Münzen oder ihrem Bankguthaben, und das Geld geht direkt auf dein Konto, auch wenn du offline bist.",
                            i(Economy.SHOP_STALL))
                    .craft("shop_stall")
                    .tip("shops.rent",
                            "Empty stalls in trade cities can be rented for 100 coins: sneak and right-click.",
                            "Freie Stände in Handelsstädten kannst du für 100 Münzen mieten: schleichen und rechtsklicken.")
                    .h("quests", "Quests and growing villages", "Aufträge und wachsende Dörfer")
                    .p("quests.text",
                            "A %s in a village offers three delivery quests each day. They pay coins and raise the village's prosperity. At each prosperity level the village builds something new by itself: stalls, cottages, a smithy, a watchtower.",
                            "Eine %s in einem Dorf bietet jeden Tag drei Lieferaufträge. Sie bringen Münzen und steigern den Wohlstand des Dorfes. Bei jeder Wohlstandsstufe baut das Dorf von selbst etwas Neues: Marktstände, Häuschen, eine Schmiede, einen Wachturm.",
                            i(Economy.QUEST_BOARD))
                    .craft("quest_board")
                    .h("jobs", "New villager jobs", "Neue Berufe")
                    .p("jobs.text",
                            "Place one of these next to a villager without a job:",
                            "Stell einen dieser Blöcke neben einen Dorfbewohner ohne Beruf:")
                    .items(st(Economy.BANK_COUNTER, 1), st(Economy.TITAN_ANVIL, 1), st(Economy.RELIC_PEDESTAL, 1))
                    .p("jobs.list",
                            "Banker (%s): trades emeralds, gold and diamonds for coins, later netherite scrap and totems.\n\nTitansmith (%s): maps to the Titan shrines and Elemental Sigils.\n\nRelic Dealer (%s): Nether Stars, Elytra, Dragon Heads, Stardust and more.",
                            "Bankier (%s): tauscht Smaragde, Gold und Diamanten gegen Münzen, später auch Netheritplatten und Totems.\n\nTitanenschmied (%s): Karten zu den Titanenschreinen und Elementarsiegel.\n\nReliquienhändler (%s): Netherstern, Elytren, Drachenköpfe, Sternenstaub und mehr.",
                            i(Economy.BANK_COUNTER), i(Economy.TITAN_ANVIL), i(Economy.RELIC_PEDESTAL))
                    .craft("titan_anvil")
                    .tip("jobs.pedestal",
                            "Relic Pedestals can't be crafted. You find them in trade cities.",
                            "Reliquiensockel kann man nicht herstellen. Du findest sie in Handelsstädten.")
                    .h("cities", "Trade cities", "Handelsstädte")
                    .p("cities.text",
                            "Rare walled towns in plains, savannas, deserts, taigas, meadows and snowy plains. Each has a bank, a market with stalls to rent and a relic pavilion with a Relic Dealer.",
                            "Seltene ummauerte Städte in Ebenen, Savannen, Wüsten, Taigas, Wiesen und verschneiten Ebenen. Jede hat eine Bank, einen Markt mit Mietständen und einen Reliquienpavillon mit Reliquienhändler.")
                    .build(),

            // ------------------------------------------------------------------ titans
            chapter("titans", Titans.CORES.get(Element.FROST), "Elemental Titans", "Elementar-Titanen")
                    .anchor("titans")
                    .p("intro",
                            "Four titans sleep in shrines across the world. Each one guards an element and drops its core when defeated.",
                            "Vier Titanen schlafen in Schreinen überall auf der Welt. Jeder hütet ein Element und lässt seinen Kern fallen, wenn er besiegt wird.")
                    .items(st(Titans.CORES.get(Element.FROST), 1), st(Titans.CORES.get(Element.TIDE), 1), st(Titans.CORES.get(Element.STORM), 1),
                            st(Titans.CORES.get(Element.MAGMA), 1))
                    .h("find", "Finding the shrines", "Die Schreine finden")
                    .p("find.biomes",
                            "Frost: snowy plains, groves, snowy slopes, ice spikes, frozen peaks.\n\nTide: oceans and deep oceans.\n\nStorm: mountain peaks, windswept hills, meadows.\n\nMagma: in the Nether, in basalt deltas and nether wastes.",
                            "Frost: verschneite Ebenen, Haine, verschneite Hänge, Eiszapfentundra, gefrorene Gipfel.\n\nGezeiten: Ozeane und Tiefsee.\n\nSturm: Berggipfel, windgepeitschte Hügel, Wiesen.\n\nMagma: im Nether, in Basaltdeltas und Netherödnis.")
                    .p("find.rare",
                            "Shrines are rare: at most one in every 400 by 400 blocks, and only where the biome fits.",
                            "Schreine sind selten: höchstens einer pro 400 mal 400 Blöcke, und nur wo das Biom passt.")
                    .tip("find.maps",
                            "The easy way: a Titansmith sells a map to the nearest shrine for 2 %s and a compass. Frost and Storm maps from level 3 (Journeyman), Tide and Magma maps from level 4 (Expert).",
                            "Der einfache Weg: Ein Titanenschmied verkauft dir eine Karte zum nächsten Schrein für 2 %s und einen Kompass. Frost- und Sturmkarten ab Stufe 3 (Geselle), Gezeiten- und Magmakarten ab Stufe 4 (Experte).",
                            i(coin(CoinTier.GOLD)))
                    .tip("find.existing",
                            "Installed the mod in a world you already played? Shrines are also built into land you explored before, at the same spots as in a new world. Where you built something, they move to a free spot nearby instead.",
                            "Die Mod in einer schon gespielten Welt installiert? Schreine entstehen auch in Land, das du schon erkundet hast, an denselben Stellen wie in einer neuen Welt. Wo du etwas gebaut hast, weichen sie auf einen freien Platz in der Nähe aus.")
                    .h("summon", "Summoning", "Beschwören")
                    .p("summon.text",
                            "Craft the matching Elemental Sigil and use it on the altar in the middle of the shrine. After a short ritual the titan awakens.",
                            "Stell das passende Elementarsiegel her und benutze es am Altar in der Mitte des Schreins. Nach einem kurzen Ritual erwacht der Titan.")
                    .craft("frost_sigil")
                    .craft("tide_sigil")
                    .craft("storm_sigil")
                    .craft("magma_sigil")
                    .tip("summon.cooldown",
                            "Each altar rests for 10 minutes after a summon. A Titansmith at level 5 (Master) also sells sigils.",
                            "Jeder Altar ruht nach einer Beschwörung 10 Minuten. Ein Titanenschmied auf Stufe 5 (Meister) verkauft auch Siegel.")
                    .h("fight", "The fight", "Der Kampf")
                    .p("fight.text",
                            "%s 400, %s 450, %s 500 and %s 600 health. At two thirds and at one third of its health each titan evolves and unlocks new attacks, ending with an ultimate.",
                            "%s 400, %s 450, %s 500 und %s 600 Lebenspunkte. Bei zwei Dritteln und bei einem Drittel seiner Lebenspunkte entwickelt sich jeder Titan weiter und setzt neue Angriffe ein, zuletzt einen Ultimate-Angriff.",
                            e(Titans.FROST_TITAN), e(Titans.TIDE_TITAN), e(Titans.STORM_TITAN), e(Titans.MAGMA_TITAN))
                    .p("fight.loot",
                            "Loot: its core, %s (3 to 5) and coins.",
                            "Beute: sein Kern, %s (3 bis 5) und Münzen.",
                            i(Titans.TITAN_SHARD))
                    .anchor("titan_armor")
                    .h("armor", "Titan armor", "Titanenrüstung")
                    .p("armor.forge",
                            "Build a %s. Put a netherite armor piece in it together with one titan core and four shards (%s). The piece keeps its enchantments and name and takes on the core's element.",
                            "Bau eine %s. Leg ein Netherit-Rüstungsteil zusammen mit einem Titanenkern und vier Splittern (%s) hinein. Das Teil behält Verzauberungen und Namen und nimmt das Element des Kerns an.",
                            i(Titans.TITAN_FORGE), i(Titans.TITAN_SHARD))
                    .craft("titan_forge")
                    .station(Titans.TITAN_FORGE, () -> Titans.FORGE, () -> Items.NETHERITE_CHESTPLATE,
                            List.of(st(Titans.CORES.get(Element.FROST), 1), st(Titans.TITAN_SHARD, 4)), Titans.CHESTPLATE)
                    .p("armor.levels",
                            "Wearing all four pieces, an element on one piece gives level I, on two or more pieces level II.",
                            "Trägst du alle vier Teile, gibt ein Element auf einem Teil Stufe I, auf zwei oder mehr Teilen Stufe II.")
                    .p("armor.elements",
                            "Frost: no freezing, frost walking; attackers are slowed (II: frozen).\n\nTide: water breathing, fast swimming (II: dolphin's grace, night vision underwater).\n\nStorm: speed (II: lightning strikes your attackers).\n\nMagma: fire immunity (II: walk on lava, attackers burn).",
                            "Frost: kein Erfrieren, Frostläufer; Angreifer werden verlangsamt (II: eingefroren).\n\nGezeiten: Unterwasseratmung, schnelles Schwimmen (II: Gunst des Delfins, Nachtsicht unter Wasser).\n\nSturm: Tempo (II: Blitze treffen deine Angreifer).\n\nMagma: Feuerimmunität (II: über Lava laufen, Angreifer brennen).")
                    .tip("armor.reinfuse",
                            "Want a different element? Put a Titan piece back in the forge with another core and 2 shards.",
                            "Lieber ein anderes Element? Leg ein Titanenteil mit einem anderen Kern und 2 Splittern zurück in die Schmiede.")
                    .tip("armor.save",
                            "Keep spare cores: the Ascendant armor later needs two cores of every element.",
                            "Heb übrige Kerne auf: Die Aufgestiegene Rüstung braucht später zwei Kerne jedes Elements.")
                    .build(),

            // ------------------------------------------------------------------ dragon
            chapter("dragon", Empire.DRAGON_HEART, "The Ender Dragon", "Der Enderdrache")
                    .anchor("dragon")
                    .p("heart",
                            "When the %s dies, every player within 200 blocks receives a %s. You need Dragon Hearts to find the Star Gate and to wake the Ender Colossus.",
                            "Wenn der %s stirbt, bekommt jeder Spieler im Umkreis von 200 Blöcken ein %s. Drachenherzen brauchst du, um das Sternentor zu finden und den Ender-Koloss zu wecken.",
                            e(() -> EntityType.ENDER_DRAGON), i(Empire.DRAGON_HEART))
                    .items(st(Empire.DRAGON_HEART, 1))
                    .p("more",
                            "Need more hearts? Place four End Crystals on the exit portal to respawn the dragon. Every fight gives another heart.",
                            "Mehr Herzen nötig? Stell vier Endkristalle auf das Ausgangsportal, um den Drachen neu zu beschwören. Jeder Kampf bringt ein weiteres Herz.")
                    .items(st(() -> Items.END_CRYSTAL, 4))
                    .tip("before",
                            "Killed the dragon before you installed this mod? Respawn it once to get your first heart.",
                            "Den Drachen schon vor dieser Mod besiegt? Beschwöre ihn einmal neu, um dein erstes Herz zu bekommen.")
                    .p("count",
                            "You need at least 4 hearts: one for the Star Compass and one for each Ender Colossus you summon. Three Colossus fights give all the cores you need.",
                            "Du brauchst mindestens 4 Herzen: eines für den Sternenkompass und eines für jede Beschwörung des Ender-Kolosses. Drei Kämpfe gegen den Koloss bringen alle Kerne, die du brauchst.")
                    .h("head", "A Dragon Head", "Ein Drachenkopf")
                    .p("head.text",
                            "Also bring a %s from an End ship (Relic Dealers sell them too). It goes on the Star Gate's pedestal.",
                            "Bring außerdem einen %s von einem Endschiff mit (Reliquienhändler verkaufen sie auch). Er kommt auf das Podest des Sternentors.",
                            i(() -> Items.DRAGON_HEAD))
                    .build(),

            // ------------------------------------------------------------------ empire
            chapter("empire", Empire.IMPERIAL_SEAL, "Lost Ender Empire", "Das Ender-Imperium")
                    .anchor("empire")
                    .p("intro",
                            "On the outer End islands (End highlands and midlands, past the gateway) lies the Ruined Capital, a broken city of purpur.",
                            "Auf den äußeren Endinseln (End-Hochland und -Mittelland, hinter dem Transitportal) liegt die verfallene Hauptstadt, eine zerbrochene Stadt aus Purpur.")
                    .h("sentinels", "Sentinel Constructs", "Wächterkonstrukte")
                    .p("sentinels.text",
                            "Every %s guarding the city has 300 health. Defeat them for %s and %s.",
                            "Jedes %s, das die Stadt bewacht, hat 300 Lebenspunkte. Beute: %s und %s.",
                            e(Empire.SENTINEL), i(Empire.IMPERIAL_PLATING), i(Empire.ENDER_GEAR))
                    .items(st(Empire.IMPERIAL_PLATING, 1), st(Empire.ENDER_GEAR, 1))
                    .h("pylons", "Restoring the pylons", "Die Pylonen wiederherstellen")
                    .p("pylons.text",
                            "Three pylons (%s) stand in the city. You can't touch one while a Sentinel is within 24 blocks. Right-click a pylon while carrying 4 × %s, 16 Purpur Blocks and 3,000 coins (your bank balance counts).",
                            "In der Stadt stehen drei Pylonen (%s). Solange ein Wächter näher als 24 Blöcke ist, kannst du sie nicht berühren. Rechtsklicke einen Pylon und hab dabei: 4 × %s, 16 Purpurblöcke und 3.000 Münzen (dein Bankguthaben zählt mit).",
                            i(Empire.PYLON), i(Empire.IMPERIAL_PLATING))
                    .items(st(Empire.IMPERIAL_PLATING, 4), st(() -> Items.PURPUR_BLOCK, 16), st(coin(CoinTier.TITAN), 3))
                    .p("pylons.rewards",
                            "Each pylon gives something else:\n\nPylon of Craft: drops an Imperial Forge.\n\nPylon of Trade: an Ender Merchant appears.\n\nPylon of the Throne: the barrier to the throne hall falls.",
                            "Jeder Pylon belohnt dich anders:\n\nPylon der Schmiede: lässt eine Imperiale Schmiede fallen.\n\nPylon des Handels: ein Ender-Händler erscheint.\n\nPylon des Throns: die Barriere zur Thronhalle fällt.")
                    .anchor("colossus")
                    .h("colossus", "The Ender Colossus", "Der Ender-Koloss")
                    .p("colossus.text",
                            "Use a %s on the empty throne in the throne hall to wake the %s (900 health).",
                            "Benutze ein %s am leeren Thron in der Thronhalle, um den %s (900 Lebenspunkte) zu wecken.",
                            i(Empire.DRAGON_HEART), e(Empire.COLOSSUS))
                    .p("colossus.loot",
                            "Loot: %s, %s, Imperial Plating, Ender Gears and coins.",
                            "Beute: %s, %s, Imperiale Panzerplatten, Enderzahnräder und Münzen.",
                            i(Empire.COLOSSUS_CORE), i(Empire.IMPERIAL_SEAL))
                    .tip("colossus.seal",
                            "Keep your %s! It opens the Star Gate and you need it again for the Ascension Altar.",
                            "Behalte dein %s! Es öffnet das Sternentor, und du brauchst es noch einmal für den Aufstiegsaltar.",
                            i(Empire.IMPERIAL_SEAL))
                    .anchor("imperial_armor")
                    .h("armor", "Imperial armor", "Imperiale Rüstung")
                    .p("armor.text",
                            "%s: upgrade each Titan piece here. The chestplate also needs a Colossus Core.",
                            "%s: Hier wertest du jedes Titanenteil auf. Der Harnisch braucht zusätzlich einen Kolosskern.",
                            i(Empire.IMPERIAL_FORGE))
                    .station(Empire.IMPERIAL_FORGE, () -> Empire.FORGE, Titans.HELMET,
                            List.of(st(Empire.IMPERIAL_PLATING, 4), st(Empire.ENDER_GEAR, 2)), Empire.HELMET)
                    .station(Empire.IMPERIAL_FORGE, () -> Empire.FORGE, Titans.CHESTPLATE,
                            List.of(st(Empire.IMPERIAL_PLATING, 6), st(Empire.ENDER_GEAR, 3), st(Empire.COLOSSUS_CORE, 1)), Empire.CHESTPLATE)
                    .p("armor.craft",
                            "Lost the forge from the pylon? You can craft another:",
                            "Die Schmiede vom Pylon verloren? Du kannst eine neue herstellen:")
                    .craft("imperial_forge")
                    .p("armor.set",
                            "Full set: %s makes you blink to where you look, endermen stay calm, and you get +1 reach.",
                            "Volles Set: %s lässt dich dorthin springen, wohin du schaust, Endermen bleiben ruhig, und du bekommst +1 Reichweite.",
                            ABILITY)
                    .build(),

            // ------------------------------------------------------------------ star gate
            chapter("stargate", Stars.STAR_COMPASS, "The Star Gate", "Das Sternentor")
                    .anchor("stargate")
                    .p("intro",
                            "Somewhere on the outer End islands stands a Star Gate: a dark ring with a pedestal in front of it.",
                            "Irgendwo auf den äußeren Endinseln steht ein Sternentor: ein dunkler Ring mit einem Podest davor.")
                    .h("compass", "The Star Compass", "Der Sternenkompass")
                    .p("compass.text",
                            "Craft a %s and use it in the End. It tells you the direction and distance to the nearest gate.",
                            "Stell einen %s her und benutze ihn im End. Er zeigt dir Richtung und Entfernung zum nächsten Tor.",
                            i(Stars.STAR_COMPASS))
                    .craft("star_compass")
                    .h("open", "Opening the gate", "Das Tor öffnen")
                    .p("open.steps",
                            "1. Use a %s on the %s.\n\n2. Use your %s on the pedestal. It is not used up.\n\n3. The portal opens: step in.",
                            "1. Benutze einen %s am %s.\n\n2. Benutze dein %s am Podest. Es wird nicht verbraucht.\n\n3. Das Portal öffnet sich: Tritt hinein.",
                            i(() -> Items.DRAGON_HEAD), i(Stars.STAR_GATE_PEDESTAL), i(Empire.IMPERIAL_SEAL))
                    .p("open.back",
                            "You arrive in the Fallen Stars next to a small return portal. Walk into it to go back to where you left.",
                            "Du kommst in den Gefallenen Sternen neben einem kleinen Rückportal an. Geh hinein, um dorthin zurückzukehren, wo du aufgebrochen bist.")
                    .build(),

            // ------------------------------------------------------------------ fallen stars
            chapter("stars", Stars.STAR_CORE, "The Fallen Stars", "Gefallene Sterne")
                    .anchor("celestials")
                    .p("intro",
                            "A dimension of floating starstone islands above an endless void, under a sky full of nebulae.",
                            "Eine Dimension aus schwebenden Sternsteininseln über einer endlosen Leere, unter einem Himmel voller Nebel.")
                    .tip("danger",
                            "Don't fall! Until you have defeated the %s, the void below kills you.",
                            "Fall nicht hinunter! Bis du den %s besiegt hast, tötet dich die Leere darunter.",
                            e(Stars.HERALD))
                    .h("stardust", "Stardust", "Sternenstaub")
                    .p("stardust.text",
                            "Mine %s on the islands to get %s. You need 16 to summon each Celestial.",
                            "Bau %s auf den Inseln ab, um %s zu bekommen. Du brauchst 16 für jede Beschwörung.",
                            i(Stars.STARDUST_ORE), i(Stars.STARDUST))
                    .items(st(Stars.STARDUST_ORE, 1), st(Stars.STARDUST, 16))
                    .h("celestials", "The Celestials", "Die Himmlischen")
                    .p("celestials.text",
                            "Three sanctums float among the islands, each with an altar. Use 16 Stardust on an altar to summon its Celestial:\n\n%s: 1,200 health\n%s: 1,400 health\n%s: 1,600 health, only after the other two.",
                            "Zwischen den Inseln schweben drei Heiligtümer mit je einem Altar. Benutze 16 Sternenstaub an einem Altar, um seinen Himmlischen zu beschwören:\n\n%s: 1.200 Lebenspunkte\n%s: 1.400 Lebenspunkte\n%s: 1.600 Lebenspunkte, erst nach den anderen beiden.",
                            e(Stars.SERAPH), e(Stars.LEVIATHAN), e(Stars.HERALD))
                    .anchor("herald")
                    .p("celestials.loot",
                            "Loot: a %s, 8 to 16 Stardust and coins. Each altar can be used again after 10 minutes.",
                            "Beute: ein %s, 8 bis 16 Sternenstaub und Münzen. Jeder Altar ist nach 10 Minuten wieder bereit.",
                            i(Stars.DORMANT_STAR_CORE))
                    .anchor("stellar_armor")
                    .h("armor", "Stellar armor", "Stellare Rüstung")
                    .p("armor.altar",
                            "Build a %s in the Overworld. It only works at night under open sky. A Dormant Star Core placed inside charges into a %s.",
                            "Bau einen %s in der Oberwelt. Er funktioniert nur nachts unter offenem Himmel. Ein ruhender Sternkern darin lädt sich zu einem %s auf.",
                            i(Stars.SKY_ALTAR), i(Stars.STAR_CORE))
                    .craft("sky_altar")
                    .station(Stars.SKY_ALTAR, () -> Stars.SKY_ALTAR_TYPE, Stars.DORMANT_STAR_CORE, List.of(), Stars.STAR_CORE)
                    .p("armor.upgrade",
                            "Then upgrade each Imperial piece with a Star Core and 16 Stardust (the chestplate needs 24).",
                            "Danach wertest du jedes imperiale Teil mit einem Sternkern und 16 Sternenstaub auf (der Harnisch braucht 24).")
                    .station(Stars.SKY_ALTAR, () -> Stars.SKY_ALTAR_TYPE, Empire.HELMET,
                            List.of(st(Stars.STAR_CORE, 1), st(Stars.STARDUST, 16)), Stars.HELMET)
                    .p("armor.set",
                            "Full set: you glide down gently instead of falling (sneak to drop faster), regenerate under the night sky and have night vision (switch it with %s).",
                            "Volles Set: Du gleitest sanft hinab statt zu fallen (schleichen, um schneller zu fallen), regenerierst unter dem Nachthimmel und hast Nachtsicht (umschalten mit %s).",
                            TOGGLE)
                    .tip("armor.cores",
                            "You need 10 Star Cores in total: 4 for Stellar armor, 4 for Ascendant armor and 2 for the Ascension Altar.",
                            "Insgesamt brauchst du 10 Sternkerne: 4 für die Stellare Rüstung, 4 für die Aufgestiegene Rüstung und 2 für den Aufstiegsaltar.")
                    .build(),

            // ------------------------------------------------------------------ abyss
            chapter("abyss", Abyss.VOID_ESSENCE, "The Abyss", "Der Abgrund")
                    .anchor("abyss")
                    .p("enter",
                            "Once you have defeated the Sun Herald, jump off any island in the Fallen Stars. Instead of dying, you fall into the Abyss.",
                            "Sobald du den Sonnenherold besiegt hast, spring von einer beliebigen Insel der Gefallenen Sterne. Statt zu sterben, fällst du in den Abgrund.")
                    .tip("prepare",
                            "Bring Ender Pearls and Stardust. Together with Void Essence they make Ascension Pearls, which take you back to your spawn point from anywhere.",
                            "Nimm Enderperlen und Sternenstaub mit. Zusammen mit Leerenessenz ergeben sie Aufstiegsperlen, die dich von überall zu deinem Spawnpunkt zurückbringen.")
                    .craft("ascension_pearl")
                    .h("ground", "Crumbling ground", "Bröckelnder Boden")
                    .p("ground.text",
                            "%s cracks under your feet and falls away. The deeper you are, the faster it crumbles. Broken stone grows back after a minute. Keep moving!",
                            "%s bekommt unter deinen Füßen Risse und bricht weg. Je tiefer du bist, desto schneller bröckelt er. Zerbrochener Stein wächst nach einer Minute nach. Bleib in Bewegung!",
                            i(Abyss.ABYSSAL_STONE))
                    .h("essence", "Void Essence", "Leerenessenz")
                    .p("essence.text",
                            "%s glows in the stone, most of it deep down. A %s sometimes drops %s too.",
                            "%s leuchtet im Gestein, am meisten in der Tiefe. Ein %s lässt manchmal auch %s fallen.",
                            i(Abyss.VOID_ESSENCE_ORE), e(Abyss.VOID_WRAITH), i(Abyss.VOID_ESSENCE))
                    .items(st(Abyss.VOID_ESSENCE_ORE, 1), st(Abyss.VOID_ESSENCE, 1))
                    .anchor("sovereign")
                    .h("sovereign", "The Void Sovereign", "Der Leerenherrscher")
                    .p("sovereign.text",
                            "Craft an %s and use it below height 40 to call the %s. It has 3,000 health and four phases, calls wraiths and makes the ground collapse under you.",
                            "Stell ein %s her und benutze es unterhalb von Höhe 40, um den %s zu rufen. Er hat 3.000 Lebenspunkte und vier Phasen, ruft Geister herbei und lässt den Boden unter dir einstürzen.",
                            i(Abyss.ABYSSAL_BEACON), e(Abyss.VOID_SOVEREIGN))
                    .craft("abyssal_beacon")
                    .p("sovereign.loot",
                            "Loot: the %s, 12 to 24 Void Essence and coins.",
                            "Beute: das %s, 12 bis 24 Leerenessenz und Münzen.",
                            i(Abyss.VOID_HEART))
                    .anchor("void_armor")
                    .h("armor", "Void armor", "Leerenrüstung")
                    .p("armor.text",
                            "Build a %s and upgrade each Stellar piece with 8 Void Essence and 8 Stardust (the chestplate needs 12 essence).",
                            "Bau einen %s und werte jedes stellare Teil mit 8 Leerenessenz und 8 Sternenstaub auf (der Harnisch braucht 12 Essenz).",
                            i(Abyss.VOID_INFUSER))
                    .craft("void_infuser")
                    .station(Abyss.VOID_INFUSER, () -> Abyss.INFUSER, Stars.HELMET,
                            List.of(st(Abyss.VOID_ESSENCE, 8), st(Stars.STARDUST, 8)), Abyss.VOID_HELMET)
                    .p("armor.set",
                            "Full set: %s dashes you forward, you are immune to wither and darkness, get +2 hearts and +10%% speed, and the void can't kill you.",
                            "Volles Set: %s lässt dich nach vorne sprinten, du bist immun gegen Ausdörrung und Dunkelheit, bekommst +2 Herzen und +10 %% Tempo, und die Leere kann dich nicht töten.",
                            ABILITY)
                    .build(),

            // ------------------------------------------------------------------ ascendant
            chapter("ascendant", Abyss.ASC_CHESTPLATE, "Ascension", "Der Aufstieg")
                    .anchor("ascendant")
                    .p("intro",
                            "The final armor joins the power of every boss on the ladder.",
                            "Die letzte Rüstung vereint die Kraft aller Bosse der Leiter.")
                    .h("primordial", "Primordial Cores", "Urkerne")
                    .p("primordial.text",
                            "Craft a %s from one core of each element, a Colossus Core and Void Essence. One craft makes two, and you need four.",
                            "Stell einen %s aus je einem Kern jedes Elements, einem Kolosskern und Leerenessenz her. Ein Rezept ergibt zwei, und du brauchst vier.",
                            i(Abyss.PRIMORDIAL_CORE))
                    .craft("primordial_core")
                    .h("altar", "The Ascension Altar", "Der Aufstiegsaltar")
                    .craft("ascension_altar")
                    .p("altar.text",
                            "In the %s, combine each Void piece with a Primordial Core, a Star Core and 16 Void Essence. The chestplate takes the %s instead of the essence.",
                            "Im %s verbindest du jedes Leerenteil mit einem Urkern, einem Sternkern und 16 Leerenessenz. Der Harnisch braucht statt der Essenz das %s.",
                            i(Abyss.ASCENSION_ALTAR), i(Abyss.VOID_HEART))
                    .station(Abyss.ASCENSION_ALTAR, () -> Abyss.ASCENSION, Abyss.VOID_HELMET,
                            List.of(st(Abyss.PRIMORDIAL_CORE, 1), st(Stars.STAR_CORE, 1), st(Abyss.VOID_ESSENCE, 16)), Abyss.ASC_HELMET)
                    .station(Abyss.ASCENSION_ALTAR, () -> Abyss.ASCENSION, Abyss.VOID_CHESTPLATE,
                            List.of(st(Abyss.PRIMORDIAL_CORE, 1), st(Stars.STAR_CORE, 1), st(Abyss.VOID_HEART, 1)), Abyss.ASC_CHESTPLATE)
                    .h("list", "Shopping list", "Einkaufsliste")
                    .p("list.text",
                            "For all four pieces:",
                            "Für alle vier Teile:")
                    .items(st(Abyss.PRIMORDIAL_CORE, 4), st(Stars.STAR_CORE, 4), st(Abyss.VOID_HEART, 1), st(Abyss.VOID_ESSENCE, 48))
                    .p("list.altar",
                            "Plus, for the altar: 2 Star Cores, your Imperial Seal, 2 netherite blocks and 4 crying obsidian.",
                            "Dazu für den Altar: 2 Sternkerne, dein Imperiales Siegel, 2 Netheritblöcke und 4 weinender Obsidian.")
                    .h("powers", "Powers", "Kräfte")
                    .p("powers.text",
                            "Creative flight, +10 hearts, +6 attack damage, +25%% speed, +2 reach, faster mining.\n\nImmune to fire, lava, falling, drowning, freezing, wither and the void.\n\nNever hungry, constant Regeneration II, unbreakable.\n\nAll four titan elements at level II.",
                            "Kreativflug, +10 Herzen, +6 Angriffsschaden, +25 %% Tempo, +2 Reichweite, schnelleres Abbauen.\n\nImmun gegen Feuer, Lava, Fallschaden, Ertrinken, Erfrieren, Ausdörrung und die Leere.\n\nNie hungrig, dauerhaft Regeneration II, unzerbrechlich.\n\nAlle vier Titanenelemente auf Stufe II.")
                    .p("powers.keys",
                            "%s: Ender Blink\nSneak + %s: Void Dash\n%s: night vision",
                            "%s: Enderblink\nSchleichen + %s: Leerensprint\n%s: Nachtsicht",
                            ABILITY, ABILITY, TOGGLE)
                    .build(),

            // ------------------------------------------------------------------ constellations
            chapter("constellations", Stars.STARDUST, "Constellations", "Sternbilder")
                    .p("intro",
                            "The first time you defeat a boss, its constellation appears in your night sky (only you see your own) and you keep a bonus forever:",
                            "Wenn du einen Boss zum ersten Mal besiegst, erscheint sein Sternbild an deinem Nachthimmel (nur du siehst deine eigenen) und du behältst für immer einen Bonus:")
                    .p("list",
                            "%s: +1 armor\n%s: breath lasts longer\n%s: +3%% speed\n%s: burning ends sooner\n%s: +1 heart\n%s: +1 armor toughness\n%s: +0.5 reach\n%s: +10%% swim speed\n%s: +1 heart\n%s: +5%% attack damage",
                            "%s: +1 Rüstung\n%s: Atem hält länger\n%s: +3 %% Tempo\n%s: Brennen endet früher\n%s: +1 Herz\n%s: +1 Rüstungshärte\n%s: +0,5 Reichweite\n%s: +10 %% Schwimmtempo\n%s: +1 Herz\n%s: +5 %% Angriffsschaden",
                            e(Titans.FROST_TITAN), e(Titans.TIDE_TITAN), e(Titans.STORM_TITAN), e(Titans.MAGMA_TITAN), e(() -> EntityType.ENDER_DRAGON),
                            e(Empire.COLOSSUS), e(Stars.SERAPH), e(Stars.LEVIATHAN), e(Stars.HERALD), e(Abyss.VOID_SOVEREIGN))
                    .tip("look",
                            "Look up on a clear night to see them.",
                            "Schau in einer klaren Nacht nach oben, um sie zu sehen.")
                    .build(),

            // ------------------------------------------------------------------ projecte
            chapter("projecte", () -> Items.NETHER_STAR, "ProjectE", "ProjectE")
                    .p("intro",
                            "ProjectE is optional. If it is installed:",
                            "ProjectE ist optional. Wenn es installiert ist:")
                    .p("emc",
                            "Every Celestial Ascent item has an EMC value, so you can learn it in a Transmutation Table. The values are high: a Titan Shard is worth 250,000 EMC, an Ascendant Chestplate 1.6 billion.",
                            "Jedes Item aus Celestial Ascent hat einen EMC-Wert, du kannst es also in einem Transmutationstisch lernen. Die Werte sind hoch: Ein Titanensplitter ist 250.000 EMC wert, ein Aufgestiegener Harnisch 1,6 Milliarden.")
                    .p("repair",
                            "Damaged Celestial armor repairs itself once a second using EMC from your transmutation knowledge. Server owners can turn this off in the config (emcRepair).",
                            "Beschädigte Rüstung aus dieser Mod repariert sich einmal pro Sekunde mit EMC aus deinem Transmutationswissen. Serverbetreiber können das in der Konfiguration abschalten (emcRepair).")
                    .tip("without",
                            "Without ProjectE none of this applies. Everything else works the same.",
                            "Ohne ProjectE gilt nichts davon. Alles andere funktioniert genauso.")
                    .build()
    );

    /** Chapter by id, or null. */
    public static Chapter byId(String id) {
        for (Chapter c : ALL) if (c.id().equals(id)) return c;
        return null;
    }
}
