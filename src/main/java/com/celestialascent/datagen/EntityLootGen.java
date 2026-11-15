package com.celestialascent.datagen;

import com.celestialascent.core.CAReg;
import com.celestialascent.economy.CoinTier;
import com.celestialascent.economy.Economy;
import com.celestialascent.titans.Element;
import com.celestialascent.titans.Titans;
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
        for (Element e : Element.values()) {
            add(Titans.titanType(e), LootTable.lootTable()
                    .withPool(fixed(Titans.CORES.get(e), 1, 1))
                    .withPool(looted(Titans.TITAN_SHARD, 3, 5))
                    .withPool(fixed(Economy.coin(CoinTier.TITAN), 1, 3))
                    .withPool(fixed(Economy.coin(CoinTier.GOLD), 4, 9)));
        }
        add(com.celestialascent.empire.Empire.SENTINEL.get(), LootTable.lootTable()
                .withPool(looted(com.celestialascent.empire.Empire.IMPERIAL_PLATING, 2, 4))
                .withPool(looted(com.celestialascent.empire.Empire.ENDER_GEAR, 1, 3))
                .withPool(fixed(Economy.coin(CoinTier.TITAN), 1, 2)));
        add(com.celestialascent.empire.Empire.COLOSSUS.get(), LootTable.lootTable()
                .withPool(fixed(com.celestialascent.empire.Empire.COLOSSUS_CORE, 1, 1))
                .withPool(fixed(com.celestialascent.empire.Empire.IMPERIAL_SEAL, 1, 1))
                .withPool(looted(com.celestialascent.empire.Empire.ENDER_GEAR, 3, 6))
                .withPool(looted(com.celestialascent.empire.Empire.IMPERIAL_PLATING, 4, 8))
                .withPool(fixed(Economy.coin(CoinTier.ENDER), 1, 2))
                .withPool(fixed(Economy.coin(CoinTier.TITAN), 3, 6)));
    }

    @Override
    protected Stream<EntityType<?>> getKnownEntityTypes() {
        return CAReg.ENTITIES.getEntries().stream().map(Holder::value).filter(t -> t.getCategory() == net.minecraft.world.entity.MobCategory.MONSTER);
    }
}
