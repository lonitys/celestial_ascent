package com.celestialascent.datagen;

import com.celestialascent.CelestialAscent;
import net.minecraft.core.HolderLookup;
import net.minecraft.data.DataGenerator;
import net.minecraft.data.PackOutput;
import net.minecraft.data.loot.LootTableProvider;
import net.minecraft.world.level.storage.loot.parameters.LootContextParamSets;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.common.data.ExistingFileHelper;
import net.neoforged.neoforge.data.event.GatherDataEvent;

import java.util.List;
import java.util.Set;
import java.util.concurrent.CompletableFuture;

@EventBusSubscriber(modid = CelestialAscent.MODID)
public final class DataGen {
    private DataGen() {}

    @SubscribeEvent
    public static void gather(GatherDataEvent e) {
        DataGenerator gen = e.getGenerator();
        PackOutput out = gen.getPackOutput();
        ExistingFileHelper files = e.getExistingFileHelper();
        CompletableFuture<HolderLookup.Provider> lookup = e.getLookupProvider();

        gen.addProvider(e.includeClient(), new LangGen(out));
        gen.addProvider(e.includeClient(), new ItemModelGen(out, files));
        gen.addProvider(e.includeClient(), new BlockStateGen(out, files));

        gen.addProvider(e.includeServer(), new LootTableProvider(out, Set.of(), List.of(
                new LootTableProvider.SubProviderEntry(BlockLootGen::new, LootContextParamSets.BLOCK),
                new LootTableProvider.SubProviderEntry(EntityLootGen::new, LootContextParamSets.ENTITY)), lookup));
        gen.addProvider(e.includeServer(), new RecipeGen(out, lookup));
        BlockTagGen blockTags = gen.addProvider(e.includeServer(), new BlockTagGen(out, lookup, files));
        gen.addProvider(e.includeServer(), new ItemTagGen(out, lookup, blockTags.contentsGetter(), files));
        gen.addProvider(e.includeServer(), new EmcGen(out));
    }
}
