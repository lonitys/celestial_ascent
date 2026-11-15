package com.celestialascent.datagen;

import com.celestialascent.CelestialAscent;
import com.celestialascent.compat.Emc;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.data.CachedOutput;
import net.minecraft.data.DataProvider;
import net.minecraft.data.PackOutput;

import java.nio.file.Path;
import java.util.concurrent.CompletableFuture;

/** Writes fixed EMC values in ProjectE's custom-conversion format. Ignored when ProjectE is absent. */
public class EmcGen implements DataProvider {
    private final PackOutput out;

    public EmcGen(PackOutput out) {
        this.out = out;
    }

    @Override
    public CompletableFuture<?> run(CachedOutput cache) {
        JsonArray before = new JsonArray();
        Emc.VALUES.forEach((item, value) -> {
            JsonObject o = new JsonObject();
            o.addProperty("type", "projecte:item");
            o.addProperty("id", BuiltInRegistries.ITEM.getKey(item.asItem()).toString());
            o.addProperty("emc_value", value);
            before.add(o);
        });
        JsonObject values = new JsonObject();
        values.add("before", before);
        JsonObject root = new JsonObject();
        root.addProperty("comment", "Celestial Ascent fixed EMC values");
        root.add("values", values);
        Path path = out.getOutputFolder(PackOutput.Target.DATA_PACK)
                .resolve(CelestialAscent.MODID).resolve("pe_custom_conversions").resolve(CelestialAscent.MODID + ".json");
        return DataProvider.saveStable(cache, root, path);
    }

    @Override
    public String getName() {
        return "Celestial Ascent EMC values";
    }
}
