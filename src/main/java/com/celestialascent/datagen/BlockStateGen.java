package com.celestialascent.datagen;

import com.celestialascent.CelestialAscent;
import com.celestialascent.abyss.Abyss;
import com.celestialascent.abyss.AbyssalStoneBlock;
import com.celestialascent.core.Content;
import com.celestialascent.core.FacingBlock;
import com.celestialascent.empire.Empire;
import com.celestialascent.empire.PylonBlock;
import com.celestialascent.stars.StarGatePedestalBlock;
import com.celestialascent.stars.Stars;
import com.celestialascent.titans.Titans;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.data.PackOutput;
import net.minecraft.world.level.block.AmethystClusterBlock;
import net.minecraft.world.level.block.Block;
import net.neoforged.neoforge.client.model.generators.BlockStateProvider;
import net.neoforged.neoforge.client.model.generators.ConfiguredModel;
import net.neoforged.neoforge.client.model.generators.ModelFile;
import net.neoforged.neoforge.common.data.ExistingFileHelper;

import java.util.Set;

/** Blockstates. Shaped block models are authored by tools/art; simple cubes are generated here. */
public class BlockStateGen extends BlockStateProvider {
    public BlockStateGen(PackOutput out, ExistingFileHelper files) {
        super(out, CelestialAscent.MODID, files);
    }

    private static String name(Block b) {
        return BuiltInRegistries.BLOCK.getKey(b).getPath();
    }

    private ModelFile existing(String name) {
        return models().getExistingFile(modLoc("block/" + name));
    }

    @Override
    protected void registerStatesAndModels() {
        Set<Block> cubes = Set.of(Stars.STARSTONE.get(), Stars.STARLIT_STARSTONE.get(), Stars.STARSTONE_BRICKS.get(), Stars.STARDUST_ORE.get(),
                Stars.STAR_GATE_FRAME.get(), Abyss.VOID_ESSENCE_ORE.get());
        for (var holder : Content.BLOCKS) {
            Block block = holder.get();
            String name = name(block);
            if (cubes.contains(block)) {
                simpleBlock(block);
            } else if (block == Empire.IMPERIAL_BARRIER.get()) {
                simpleBlock(block, models().cubeAll(name, modLoc("block/" + name)).renderType("translucent"));
            } else if (block instanceof PylonBlock) {
                ModelFile broken = existing(name), restored = existing(name + "_restored");
                getVariantBuilder(block).forAllStates(st -> ConfiguredModel.builder().modelFile(st.getValue(PylonBlock.RESTORED) ? restored : broken).build());
            } else if (block instanceof StarGatePedestalBlock) {
                ModelFile plain = existing(name), head = existing(name + "_head");
                getVariantBuilder(block).forAllStates(st -> ConfiguredModel.builder()
                        .modelFile(st.getValue(StarGatePedestalBlock.HEAD) ? head : plain)
                        .rotationY(((int) st.getValue(FacingBlock.FACING).toYRot() + 180) % 360).build());
            } else if (block instanceof AbyssalStoneBlock) {
                ModelFile[] stages = new ModelFile[4];
                for (int i = 0; i < 4; i++) {
                    String n = i == 0 ? name : name + "_crack" + i;
                    stages[i] = models().cubeAll(n, modLoc("block/" + n));
                }
                getVariantBuilder(block).forAllStates(st -> ConfiguredModel.builder().modelFile(stages[st.getValue(AbyssalStoneBlock.CRACK)]).build());
            } else if (block instanceof AmethystClusterBlock) {
                ModelFile cross = models().cross(name, modLoc("block/" + name)).renderType("cutout");
                getVariantBuilder(block).forAllStatesExcept(st -> {
                    Direction d = st.getValue(AmethystClusterBlock.FACING);
                    int x = d == Direction.DOWN ? 180 : d == Direction.UP ? 0 : 90;
                    int y = switch (d) { case EAST -> 90; case SOUTH -> 180; case WEST -> 270; default -> 0; };
                    return ConfiguredModel.builder().modelFile(cross).rotationX(x).rotationY(y).build();
                }, AmethystClusterBlock.WATERLOGGED);
            } else if (block instanceof FacingBlock) {
                horizontalBlock(block, existing(name));
            } else {
                simpleBlock(block, existing(name));
            }
        }
        simpleBlock(Titans.COOLED_MAGMA.get(), models().cubeAll("cooled_magma", mcLoc("block/magma")));
        simpleBlock(Stars.STAR_PORTAL.get(), existing("star_portal"));
    }
}
