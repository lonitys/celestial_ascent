package com.celestialascent.economy;

import com.celestialascent.core.CAReg;
import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.LegacyRandomSource;
import net.minecraft.world.level.levelgen.WorldgenRandom;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.pools.DimensionPadding;
import net.minecraft.world.level.levelgen.structure.pools.JigsawPlacement;
import net.minecraft.world.level.levelgen.structure.pools.StructureTemplatePool;
import net.minecraft.world.level.levelgen.structure.pools.alias.PoolAliasLookup;
import net.minecraft.world.level.levelgen.structure.templatesystem.LiquidSettings;

import java.util.Arrays;
import java.util.Optional;
import java.util.OptionalInt;

/**
 * The trade city: a square, rigid core (walls, plaza, bank, market) with jigsaw roads and outskirts.
 * Unlike a plain jigsaw structure it only starts where the ground under the whole core is flat and dry,
 * and it centres the core on the chunk whatever rotation the jigsaw picks.
 */
public final class CityStructure extends Structure {
    public static final MapCodec<CityStructure> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
            settingsCodec(i),
            StructureTemplatePool.CODEC.fieldOf("start_pool").forGetter(s -> s.startPool),
            Codec.intRange(0, 20).fieldOf("size").forGetter(s -> s.size),
            Codec.intRange(1, 128).fieldOf("max_distance_from_center").forGetter(s -> s.maxDistance),
            Codec.intRange(4, 64).fieldOf("core_radius").forGetter(s -> s.coreRadius),
            Codec.intRange(0, 16).fieldOf("ground_level").forGetter(s -> s.groundLevel),
            Codec.intRange(1, 32).fieldOf("max_spread").forGetter(s -> s.maxSpread)
    ).apply(i, CityStructure::new));

    /** Share of sampled points that may be water before a site is refused. */
    static final float MAX_WATER = 0.2f;

    private final Holder<StructureTemplatePool> startPool;
    private final int size, maxDistance, coreRadius, groundLevel, maxSpread;

    public CityStructure(StructureSettings settings, Holder<StructureTemplatePool> startPool, int size, int maxDistance,
                         int coreRadius, int groundLevel, int maxSpread) {
        super(settings);
        this.startPool = startPool;
        this.size = size;
        this.maxDistance = maxDistance;
        this.coreRadius = coreRadius;
        this.groundLevel = groundLevel;
        this.maxSpread = maxSpread;
    }

    /**
     * Median ground height of a sampled site, or empty when it is too steep (the spread between the 10th and
     * 90th percentile is over {@code maxSpread}) or too wet (more than {@code maxWater} of the samples are water).
     */
    public static OptionalInt siteHeight(int[] heights, boolean[] water, int maxSpread, float maxWater) {
        int wet = 0;
        for (boolean w : water) if (w) wet++;
        if (wet > water.length * maxWater) return OptionalInt.empty();
        int[] s = heights.clone();
        Arrays.sort(s);
        int spread = s[(int) (s.length * 0.9)] - s[(int) (s.length * 0.1)];
        return spread > maxSpread ? OptionalInt.empty() : OptionalInt.of(s[s.length / 2]);
    }

    @Override
    protected Optional<GenerationStub> findGenerationPoint(GenerationContext ctx) {
        ChunkPos c = ctx.chunkPos();
        int cx = c.getMiddleBlockX(), cz = c.getMiddleBlockZ();
        int[] h = new int[81];
        boolean[] w = new boolean[81];
        for (int i = 0; i < 9; i++) {
            for (int j = 0; j < 9; j++) {
                int x = cx + (i - 4) * coreRadius / 4, z = cz + (j - 4) * coreRadius / 4;
                int surface = ctx.chunkGenerator().getFirstOccupiedHeight(x, z, Heightmap.Types.WORLD_SURFACE_WG, ctx.heightAccessor(), ctx.randomState());
                int floor = ctx.chunkGenerator().getFirstOccupiedHeight(x, z, Heightmap.Types.OCEAN_FLOOR_WG, ctx.heightAccessor(), ctx.randomState());
                h[i * 9 + j] = floor;
                w[i * 9 + j] = surface > floor;
            }
        }
        OptionalInt ground = siteHeight(h, w, maxSpread, MAX_WATER);
        if (ground.isEmpty()) return Optional.empty();

        // JigsawPlacement rotates the start piece around its origin corner, with the first draw of the context's
        // random. Predict that draw (same seeding as GenerationContext) so the core lands centred on this chunk.
        WorldgenRandom predict = new WorldgenRandom(new LegacyRandomSource(0L));
        predict.setLargeFeatureSeed(ctx.seed(), c.x, c.z);
        Rotation rot = Rotation.getRandom(predict);
        int r = coreRadius;
        int ox = switch (rot) { case NONE, COUNTERCLOCKWISE_90 -> cx - r; default -> cx + r; };
        int oz = switch (rot) { case NONE, CLOCKWISE_90 -> cz - r; default -> cz + r; };
        // With no heightmap projection the piece's lowest layer ends up one below the start y, so the template's
        // ground layer (y = groundLevel) sits on the median ground block.
        BlockPos start = new BlockPos(ox, ground.getAsInt() + 1 - groundLevel, oz);
        return JigsawPlacement.addPieces(ctx, startPool, Optional.empty(), size, start, false, Optional.empty(),
                maxDistance, PoolAliasLookup.EMPTY, DimensionPadding.ZERO, LiquidSettings.APPLY_WATERLOGGING);
    }

    @Override
    public StructureType<?> type() {
        return CAReg.CITY_STRUCTURE.get();
    }
}
