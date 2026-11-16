package com.celestialascent.client;

import com.celestialascent.CelestialAscent;
import com.celestialascent.core.FacingBlock;
import com.celestialascent.core.station.StationBlockEntity;
import com.celestialascent.empire.PylonBlock;
import com.celestialascent.stars.StarGatePedestalBlock;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.client.resources.model.ModelResourceLocation;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.neoforged.neoforge.client.model.data.ModelData;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Predicate;

/**
 * Draws the decorative tops of altars and pedestals floating, bobbing and turning above their base
 * (the base itself is the static block model), and the item inside a station hovering over it.
 */
public class FloatingRenderer<T extends BlockEntity> implements BlockEntityRenderer<T> {
    /**
     * One floating part. Heights in blocks, bob speed in radians per tick, spin in degrees per tick.
     * {@code pulse} scales the part around {@code pivotY}; {@code faceBlock} keeps the block's facing instead of spinning.
     */
    record Part(ResourceLocation model, float lift, float bob, float bobSpeed, float spin, boolean glow, float pulse, float pivotY,
                boolean faceBlock, Predicate<BlockState> when) {}

    private record Spec(List<Part> parts, float itemY) {}

    private static final float PX = 1 / 16f;
    private static final Map<String, Spec> SPECS = new HashMap<>();

    private static Part part(String model, float liftPx, float bobPx, float bobSpeed, float spin, boolean glow) {
        return new Part(ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "block/floating/" + model),
                liftPx * PX, bobPx * PX, bobSpeed, spin, glow, 0, 0, false, s -> true);
    }

    private static void spec(String block, float itemY, Part... parts) {
        SPECS.put(block, new Spec(List.of(parts), itemY));
    }

    static {
        spec("frost_altar", 0, part("frost_altar", 1.5f, 1f, 0.07f, 0.8f, false));
        spec("tide_altar", 0, part("tide_altar", 1.5f, 1.5f, 0.06f, 1.2f, false));
        spec("storm_altar", 0, part("storm_altar", 1f, 0.75f, 0.15f, 3f, true));
        spec("magma_altar", 0, part("magma_altar", 1.25f, 0.75f, 0.05f, 0.6f, true));
        spec("seraph_altar", 0, part("seraph_altar", 1.5f, 1f, 0.06f, 0.6f, false));
        spec("leviathan_altar", 0, part("leviathan_altar", 1.5f, 1.25f, 0.05f, 1f, false));
        spec("herald_altar", 0, part("herald_altar", 1.5f, 1f, 0.06f, 1.5f, true));
        spec("relic_pedestal", 0, part("relic_pedestal", 1.5f, 1f, 0.07f, 1f, true));
        spec("sky_altar", 1.6f, part("sky_altar", 1f, 0.75f, 0.08f, 1.5f, true));
        Part orb = part("void_infuser", 0.5f, 0.75f, 0.09f, 2f, true);
        spec("void_infuser", 1.45f, new Part(orb.model(), orb.lift(), orb.bob(), orb.bobSpeed(), orb.spin(), true, 0.08f, 17 * PX, false, s -> true));
        spec("ascension_altar", 1.5f, part("ascension_altar_gem", 1f, 0.75f, 0.07f, 1.5f, true),
                part("ascension_altar_halo", 1f, 0.5f, 0.05f, -1f, true));
        Part crystal = part("imperial_pylon_restored", 2f, 1f, 0.06f, 1.2f, true);
        spec("imperial_pylon", 0, new Part(crystal.model(), crystal.lift(), crystal.bob(), crystal.bobSpeed(), crystal.spin(), true, 0, 0, false,
                s -> s.getValue(PylonBlock.RESTORED)));
        Part head = part("star_gate_pedestal_head", 1.5f, 1f, 0.05f, 0, false);
        spec("star_gate_pedestal", 0, new Part(head.model(), head.lift(), head.bob(), head.bobSpeed(), 0, false, 0, 0, true,
                s -> s.getValue(StarGatePedestalBlock.HEAD)));
        spec("celestial_crystal", 0, part("celestial_crystal_gem", 3f, 1.5f, 0.05f, 1.2f, true),
                part("celestial_crystal_ring", 3f, 1f, 0.05f, -2.5f, true));
        spec("titan_forge", 1.4f);
        spec("imperial_forge", 1.3f);
    }

    /** Every floating model, registered as an additional model in ClientSetup. */
    public static List<ModelResourceLocation> models() {
        return SPECS.values().stream().flatMap(s -> s.parts().stream()).map(p -> ModelResourceLocation.standalone(p.model())).toList();
    }

    private final Map<Block, Spec> byBlock = new HashMap<>();
    private final RandomSource random = RandomSource.create();

    public FloatingRenderer(BlockEntityRendererProvider.Context ctx) {}

    private Spec spec(Block block) {
        return byBlock.computeIfAbsent(block, b -> {
            ResourceLocation id = BuiltInRegistries.BLOCK.getKey(b);
            Spec s = CelestialAscent.MODID.equals(id.getNamespace()) ? SPECS.get(id.getPath()) : null;
            return s == null ? new Spec(List.of(), 0) : s;
        });
    }

    /** Each block gets its own phase so neighbouring altars don't bob in step. */
    private static float phase(BlockPos pos) {
        return (Mth.getSeed(pos) & 1023) / 7f;
    }

    @Override
    public void render(T be, float partialTick, PoseStack pose, MultiBufferSource buffers, int light, int overlay) {
        if (be.getLevel() == null) return;
        BlockState state = be.getBlockState();
        Spec spec = spec(state.getBlock());
        boolean working = be instanceof StationBlockEntity st && st.active();
        float time = (be.getLevel().getGameTime() % 72000L) + partialTick + phase(be.getBlockPos());
        Minecraft mc = Minecraft.getInstance();

        for (Part p : spec.parts()) {
            if (!p.when().test(state)) continue;
            BakedModel model = mc.getModelManager().getModel(ModelResourceLocation.standalone(p.model()));
            pose.pushPose();
            pose.translate(0.5, p.lift() + Mth.sin(time * p.bobSpeed()) * p.bob(), 0.5);
            if (p.faceBlock()) {
                int rot = ((int) state.getValue(FacingBlock.FACING).toYRot() + 180) % 360; // same as the blockstate
                pose.mulPose(Axis.YP.rotationDegrees(-rot));
            } else {
                pose.mulPose(Axis.YP.rotationDegrees(time * p.spin() * (working ? 3 : 1)));
            }
            if (p.pulse() > 0) {
                float s = 1 + Mth.sin(time * 0.15f) * p.pulse();
                pose.translate(0, p.pivotY(), 0);
                pose.scale(s, s, s);
                pose.translate(0, -p.pivotY(), 0);
            }
            pose.translate(-0.5, 0, -0.5);
            if (p.glow()) {
                mc.getBlockRenderer().getModelRenderer().renderModel(pose.last(), buffers.getBuffer(RenderType.cutout()), state, model,
                        1f, 1f, 1f, LightTexture.FULL_BRIGHT, OverlayTexture.NO_OVERLAY, ModelData.EMPTY, RenderType.cutout());
            } else {
                mc.getBlockRenderer().getModelRenderer().tesselateBlock(be.getLevel(), model, state, be.getBlockPos(), pose,
                        buffers.getBuffer(RenderType.cutout()), false, random, 42L, OverlayTexture.NO_OVERLAY, ModelData.EMPTY, RenderType.cutout());
            }
            pose.popPose();
        }

        if (be instanceof StationBlockEntity st && spec.itemY() > 0) {
            ItemStack shown = st.items.getItem(0).isEmpty() ? st.items.getItem(st.outputSlot()) : st.items.getItem(0);
            if (!shown.isEmpty()) {
                pose.pushPose();
                pose.translate(0.5, spec.itemY() + Mth.sin(time * 0.08f) * 0.05f, 0.5);
                pose.mulPose(Axis.YP.rotationDegrees(time * (working ? 6f : 1.5f)));
                pose.scale(0.9f, 0.9f, 0.9f);
                mc.getItemRenderer().renderStatic(shown, ItemDisplayContext.GROUND, LightTexture.FULL_BRIGHT, OverlayTexture.NO_OVERLAY,
                        pose, buffers, be.getLevel(), (int) be.getBlockPos().asLong());
                pose.popPose();
            }
        }
    }

    @Override
    public AABB getRenderBoundingBox(T be) {
        BlockPos pos = be.getBlockPos();
        return new AABB(pos.getX(), pos.getY(), pos.getZ(), pos.getX() + 1, pos.getY() + 2.5, pos.getZ() + 1);
    }
}
