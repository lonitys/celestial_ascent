package com.celestialascent.datagen;

import com.celestialascent.boss.BossDrops;
import com.celestialascent.core.CAReg;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderLookup;
import net.minecraft.data.loot.EntityLootSubProvider;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.flag.FeatureFlags;
import net.minecraft.world.level.ItemLike;
import net.minecraft.world.level.storage.loot.LootPool;
import net.minecraft.world.level.storage.loot.LootTable;
import net.minecraft.world.level.storage.loot.entries.LootItem;
import net.minecraft.world.level.storage.loot.functions.EnchantedCountIncreaseFunction;
import net.minecraft.world.level.storage.loot.functions.SetItemCountFunction;
import net.minecraft.world.level.storage.loot.providers.number.ConstantValue;
import net.minecraft.world.level.storage.loot.providers.number.UniformGenerator;

import java.util.stream.Stream;

/** Boss loot. Each eligible player rolls the table separately (see CelestialBoss). */
public class EntityLootGen extends EntityLootSubProvider {
    public EntityLootGen(HolderLookup.Provider lookup) {
        super(FeatureFlags.REGISTRY.allFlags(), lookup);
    }

    protected LootPool.Builder fixed(ItemLike item, float min, float max) {
        return LootPool.lootPool().setRolls(ConstantValue.exactly(1))
                .add(LootItem.lootTableItem(item).apply(SetItemCountFunction.setCount(UniformGenerator.between(min, max))));
    }

    protected LootPool.Builder looted(ItemLike item, float min, float max) {
        return LootPool.lootPool().setRolls(ConstantValue.exactly(1))
                .add(LootItem.lootTableItem(item).apply(SetItemCountFunction.setCount(UniformGenerator.between(min, max)))
                        .apply(EnchantedCountIncreaseFunction.lootingMultiplier(registries, UniformGenerator.between(0, 1))));
    }

    @Override
    public void generate() {
        // Boss tables come from the shared BossDrops list, which JEI shows as well.
        for (BossDrops.Entry e : BossDrops.all()) {
            LootTable.Builder table = LootTable.lootTable();
            for (BossDrops.Drop d : e.drops()) {
                table.withPool(d.looting() ? looted(d.item().get(), d.min(), d.max()) : fixed(d.item().get(), d.min(), d.max()));
            }
            add(e.type().get(), table);
        }
        add(com.celestialascent.abyss.Abyss.VOID_WRAITH.get(), LootTable.lootTable()
                .withPool(LootPool.lootPool().setRolls(ConstantValue.exactly(1))
                        .add(LootItem.lootTableItem(com.celestialascent.abyss.Abyss.VOID_ESSENCE)
                                .when(net.minecraft.world.level.storage.loot.predicates.LootItemRandomChanceCondition.randomChance(0.2f))
                                .apply(EnchantedCountIncreaseFunction.lootingMultiplier(registries, UniformGenerator.between(0, 1))))));
    }

    @Override
    protected Stream<EntityType<?>> getKnownEntityTypes() {
        return CAReg.ENTITIES.getEntries().stream().map(Holder::value).filter(t -> t.getCategory() == net.minecraft.world.entity.MobCategory.MONSTER);
    }
}
