package com.celestialascent.datagen;

import com.celestialascent.CelestialAscent;
import com.celestialascent.core.Content;
import com.celestialascent.core.FacingBlock;
import com.celestialascent.titans.Titans;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.data.PackOutput;
import net.neoforged.neoforge.client.model.generators.BlockStateProvider;
import net.neoforged.neoforge.common.data.ExistingFileHelper;

/** Blockstates. Block models themselves are authored by tools/art and must already exist. */
public class BlockStateGen extends BlockStateProvider {
    public BlockStateGen(PackOutput out, ExistingFileHelper files) {
        super(out, CelestialAscent.MODID, files);
    }

    @Override
    protected void registerStatesAndModels() {
        for (var holder : Content.BLOCKS) {
            var block = holder.get();
            String name = BuiltInRegistries.BLOCK.getKey(block).getPath();
            if (block instanceof com.celestialascent.empire.PylonBlock) {
                var broken = models().getExistingFile(modLoc("block/" + name));
                var restored = models().getExistingFile(modLoc("block/" + name + "_restored"));
                getVariantBuilder(block).forAllStates(st -> net.neoforged.neoforge.client.model.generators.ConfiguredModel.builder()
                        .modelFile(st.getValue(com.celestialascent.empire.PylonBlock.RESTORED) ? restored : broken).build());
                continue;
            }
            var model = models().getExistingFile(modLoc("block/" + name));
            if (block instanceof FacingBlock) horizontalBlock(block, model);
            else simpleBlock(block, model);
        }
        simpleBlock(Titans.COOLED_MAGMA.get(), models().cubeAll("cooled_magma", mcLoc("block/magma")));
    }
}
