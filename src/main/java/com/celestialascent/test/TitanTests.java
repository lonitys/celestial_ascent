package com.celestialascent.test;

import com.celestialascent.CelestialAscent;
import com.celestialascent.armor.ArmorSets;
import com.celestialascent.armor.SetId;
import com.celestialascent.progress.Progress;
import com.celestialascent.titans.Element;
import com.celestialascent.titans.FrostTitan;
import com.celestialascent.titans.TitanAbilities;
import com.celestialascent.titans.Titans;
import net.minecraft.core.BlockPos;
import net.minecraft.core.component.DataComponents;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

import java.util.List;
import java.util.Map;

@GameTestHolder(CelestialAscent.MODID)
@PrefixGameTestTemplate(false)
public final class TitanTests {
    private TitanTests() {}

    @GameTest(template = CoreTests.FLOOR)
    public static void forgeInfusesNetheriteAndKeepsName(GameTestHelper h) {
        ItemStack base = new ItemStack(Items.NETHERITE_CHESTPLATE);
        base.set(DataComponents.CUSTOM_NAME, Component.literal("Old Faithful"));
        base.setDamageValue(100);
        List<ItemStack> mats = List.of(new ItemStack(Titans.CORES.get(Element.FROST).get()), new ItemStack(Titans.TITAN_SHARD.get(), 4));
        var recipe = Titans.FORGE.find(base, mats);
        h.assertTrue(recipe != null, "recipe found");
        ItemStack out = recipe.result().apply(base);
        CoreTests.eq(h, Titans.CHESTPLATE.get(), out.getItem(), "result item");
        CoreTests.eq(h, Element.FROST, out.get(Titans.ELEMENT.get()), "element");
        CoreTests.eq(h, "Old Faithful", out.getHoverName().getString(), "custom name kept");
        CoreTests.eq(h, 0, out.getDamageValue(), "repaired");
        h.assertTrue(Titans.FORGE.find(base, List.of(new ItemStack(Titans.CORES.get(Element.FROST).get()), new ItemStack(Titans.TITAN_SHARD.get(), 3))) == null,
                "three shards are not enough");
        h.succeed();
    }

    @GameTest(template = CoreTests.FLOOR)
    public static void titanElementLevels(GameTestHelper h) {
        ServerPlayer p = h.makeMockServerPlayerInLevel();
        ItemStack helm = new ItemStack(Titans.HELMET.get());
        helm.set(Titans.ELEMENT.get(), Element.FROST);
        ItemStack chest = new ItemStack(Titans.CHESTPLATE.get());
        chest.set(Titans.ELEMENT.get(), Element.FROST);
        ItemStack legs = new ItemStack(Titans.LEGGINGS.get());
        legs.set(Titans.ELEMENT.get(), Element.STORM);
        ItemStack boots = new ItemStack(Titans.BOOTS.get());
        p.setItemSlot(EquipmentSlot.HEAD, helm);
        p.setItemSlot(EquipmentSlot.CHEST, chest);
        p.setItemSlot(EquipmentSlot.LEGS, legs);
        h.assertTrue(ArmorSets.fullSet(p) == null, "three pieces are not a set");
        p.setItemSlot(EquipmentSlot.FEET, boots);
        CoreTests.eq(h, SetId.TITAN, ArmorSets.fullSet(p), "full titan set");
        Map<Element, Integer> lv = new TitanAbilities().levels(p);
        CoreTests.eq(h, 2, lv.get(Element.FROST), "frost II");
        CoreTests.eq(h, 1, lv.get(Element.STORM), "storm I");
        h.assertTrue(!lv.containsKey(Element.MAGMA), "no magma");
        h.succeed();
    }

    @GameTest(template = CoreTests.FLOOR, timeoutTicks = 200)
    public static void titanKillRecordsProgressAndOwnedLoot(GameTestHelper h) {
        ServerPlayer p = h.makeMockServerPlayerInLevel();
        p.moveTo(h.absoluteVec(new net.minecraft.world.phys.Vec3(8, 1, 3)));
        FrostTitan titan = h.spawn(Titans.FROST_TITAN.get(), new BlockPos(8, 1, 10));
        h.runAfterDelay(5, () -> {
            CoreTests.eq(h, 400.0f, titan.getMaxHealth(), "solo max health");
            titan.creditDamage(p, 100);
            titan.hurt(h.getLevel().damageSources().genericKill(), Float.MAX_VALUE);
        });
        h.succeedWhen(() -> {
            h.assertTrue(Progress.has(p, titan.bossId()), "kill recorded");
            List<ItemEntity> drops = h.getLevel().getEntitiesOfClass(ItemEntity.class, p.getBoundingBox().inflate(3));
            h.assertTrue(drops.stream().anyMatch(d -> d.getItem().is(Titans.CORES.get(Element.FROST).get())), "frost core dropped at player");
        });
    }
}
