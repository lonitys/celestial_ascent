package com.celestialascent.test;

import com.celestialascent.CelestialAscent;
import com.celestialascent.armor.ArmorStages;
import com.celestialascent.empire.Empire;
import com.celestialascent.stars.Stars;
import com.celestialascent.titans.Element;
import com.celestialascent.titans.Titans;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.GameType;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

import java.util.List;

/** Armor evolution: resonance from fighting, completion at the set's station, stats and resets. */
@GameTestHolder(CelestialAscent.MODID)
@PrefixGameTestTemplate(false)
public final class ArmorStageTests {
    private ArmorStageTests() {}

    private static void wearImperial(ServerPlayer p) {
        p.setItemSlot(EquipmentSlot.HEAD, new ItemStack(Empire.HELMET.get()));
        p.setItemSlot(EquipmentSlot.CHEST, new ItemStack(Empire.CHESTPLATE.get()));
        p.setItemSlot(EquipmentSlot.LEGS, new ItemStack(Empire.LEGGINGS.get()));
        p.setItemSlot(EquipmentSlot.FEET, new ItemStack(Empire.BOOTS.get()));
    }

    @GameTest(template = CoreTests.FLOOR)
    public static void killsFillResonance(GameTestHelper h) {
        ServerPlayer p = h.makeMockServerPlayerInLevel();
        p.setGameMode(GameType.SURVIVAL);
        wearImperial(p);
        var zombie = h.spawn(EntityType.ZOMBIE, new BlockPos(4, 1, 4));
        zombie.hurt(p.damageSources().playerAttack(p), 1000);
        int worth = ArmorStages.worth(zombie);
        CoreTests.eq(h, 7, worth, "a zombie (20 health) is worth 7");
        for (ItemStack s : List.of(p.getItemBySlot(EquipmentSlot.HEAD), p.getItemBySlot(EquipmentSlot.FEET))) {
            CoreTests.eq(h, 7, ArmorStages.resonance(s), "every worn piece resonates");
        }
        ArmorStages.addResonance(p, 100_000);
        CoreTests.eq(h, 600, ArmorStages.resonance(p.getItemBySlot(EquipmentSlot.HEAD)), "resonance stops at what stage II needs");
        h.assertTrue(ArmorStages.ready(p.getItemBySlot(EquipmentSlot.HEAD)), "ready to evolve");
        CoreTests.eq(h, 1, ArmorStages.setStage(p), "a fresh set is set stage I");
        h.succeed();
    }

    @GameTest(template = CoreTests.FLOOR)
    public static void stationCompletesEvolution(GameTestHelper h) {
        ItemStack helm = new ItemStack(Empire.HELMET.get());
        List<ItemStack> mats2 = List.of(new ItemStack(Empire.IMPERIAL_PLATING.get(), 3), new ItemStack(Empire.ENDER_GEAR.get(), 2));
        h.assertTrue(Empire.FORGE.find(helm, mats2) == null, "no evolution without full resonance");
        helm.set(ArmorStages.RESONANCE.get(), 600);
        var r = Empire.FORGE.find(helm, mats2);
        h.assertTrue(r != null, "full resonance + materials evolves at the Imperial Forge");
        ItemStack two = r.result().apply(helm.copy());
        CoreTests.eq(h, 2, ArmorStages.stage(two), "stage II");
        CoreTests.eq(h, 0, ArmorStages.resonance(two), "resonance spent");
        two.set(ArmorStages.RESONANCE.get(), 1800);
        List<ItemStack> mats3 = List.of(new ItemStack(Empire.COLOSSUS_CORE.get()), new ItemStack(Empire.ENDER_GEAR.get(), 3),
                new ItemStack(Empire.IMPERIAL_PLATING.get(), 3));
        h.assertTrue(Empire.FORGE.find(two, mats2) == null, "stage III needs its own materials");
        ItemStack three = Empire.FORGE.find(two, mats3).result().apply(two.copy());
        CoreTests.eq(h, 3, ArmorStages.stage(three), "stage III");
        CoreTests.eq(h, 0, ArmorStages.required(three), "nothing after stage III");

        // Moving the piece into the next set starts over.
        ItemStack stellar = Stars.SKY_ALTAR_TYPE.find(three, List.of(new ItemStack(Stars.STAR_CORE.get()), new ItemStack(Stars.STARDUST.get(), 16)))
                .result().apply(three.copy());
        h.assertTrue(stellar.is(Stars.HELMET.get()), "upgraded to stellar");
        CoreTests.eq(h, 1, ArmorStages.stage(stellar), "a new set starts at stage I");
        h.succeed();
    }

    @GameTest(template = CoreTests.FLOOR)
    public static void titanEvolutionNeedsItsOwnElement(GameTestHelper h) {
        ItemStack helm = new ItemStack(Titans.HELMET.get());
        helm.set(Titans.ELEMENT.get(), Element.FROST);
        helm.set(ArmorStages.RESONANCE.get(), 600);
        var frost = Titans.FORGE.find(helm, List.of(new ItemStack(Titans.CORES.get(Element.FROST).get()), new ItemStack(Titans.TITAN_SHARD.get(), 3)));
        h.assertTrue(frost != null, "frost core evolves a frost piece");
        ItemStack evolved = frost.result().apply(helm.copy());
        CoreTests.eq(h, 2, ArmorStages.stage(evolved), "stage II");
        CoreTests.eq(h, Element.FROST, evolved.get(Titans.ELEMENT.get()), "keeps its element");
        var tide = Titans.FORGE.find(helm, List.of(new ItemStack(Titans.CORES.get(Element.TIDE).get()), new ItemStack(Titans.TITAN_SHARD.get(), 3)));
        ItemStack reinfused = tide.result().apply(helm.copy());
        CoreTests.eq(h, Element.TIDE, reinfused.get(Titans.ELEMENT.get()), "another element's core re-infuses instead");
        CoreTests.eq(h, 1, ArmorStages.stage(reinfused), "re-infusing does not evolve");
        h.succeed();
    }

    @GameTest(template = CoreTests.FLOOR)
    public static void stagesAddArmor(GameTestHelper h) {
        ItemStack one = new ItemStack(Empire.CHESTPLATE.get());
        ItemStack three = one.copy();
        three.set(ArmorStages.STAGE.get(), 3);
        CoreTests.eq(h, armor(one) + 2.0, armor(three), "stage III adds 2 armor");
        h.succeed();
    }

    private static double armor(ItemStack s) {
        double[] sum = {0};
        s.getAttributeModifiers().forEach(EquipmentSlot.CHEST, (attr, mod) -> {
            if (attr.is(Attributes.ARMOR)) sum[0] += mod.amount();
        });
        return sum[0];
    }
}
