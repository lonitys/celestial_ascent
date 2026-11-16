package com.celestialascent.retrogen;

import com.celestialascent.CelestialAscent;
import com.celestialascent.core.ModConfig;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.chunk.status.ChunkStatus;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureStart;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;

/** Decides whether a structure may be built late at a spot without damaging anything players made. */
public final class SiteCheck {
    private SiteCheck() {}

    /** Blocks that never generate naturally outside structures: finding one means someone built here. */
    public static final TagKey<Block> PLAYER_MADE = TagKey.create(Registries.BLOCK,
            ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "retrogen_avoid"));

    /** Structures placed at a fixed height instead of on the surface. */
    private static final Set<String> FIXED_HEIGHT = Set.of("magma_shrine");
    /** Structures that stand in water. */
    private static final Set<String> IN_WATER = Set.of("tide_shrine");

    public enum Result {
        OK,
        /** Try again later: players are close, or some chunks are only partly generated. */
        DEFER,
        /** This spot can't be used; look for another. */
        BLOCKED,
        /** The biome here is wrong for this structure. */
        WRONG_BIOME
    }

    public record Site(Result result, int dy, String reason) {
        static Site of(Result r, String reason) {
            return new Site(r, 0, reason);
        }
    }

    /**
     * Ground height at a column, ignoring trees and plants: the first free block above soil, stone or water.
     * Loads the chunk (level heights read as the world bottom for unloaded chunks), so only call it for land that exists.
     */
    public static int groundY(ServerLevel level, int x, int z, boolean[] water) {
        LevelChunk chunk = level.getChunk(x >> 4, z >> 4);
        BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos(x, chunk.getHeight(Heightmap.Types.WORLD_SURFACE, x & 15, z & 15), z);
        while (p.getY() > level.getMinBuildHeight()) {
            BlockState s = level.getBlockState(p);
            if (!s.getFluidState().isEmpty()) {
                if (water != null) water[0] = true;
                break;
            }
            if (s.isAir() || s.canBeReplaced() || s.is(BlockTags.LEAVES) || s.is(BlockTags.LOGS) || s.is(Blocks.BAMBOO)
                    || s.is(Blocks.CACTUS) || s.is(Blocks.SUGAR_CANE) || s.is(Blocks.BROWN_MUSHROOM_BLOCK) || s.is(Blocks.RED_MUSHROOM_BLOCK)
                    || s.is(Blocks.MUSHROOM_STEM)) {
                p.move(0, -1, 0);
                continue;
            }
            break;
        }
        return p.getY() + 1;
    }

    /** The first block in the box that a player must have placed, or null. */
    public static BlockPos findPlayerBuild(ServerLevel level, BoundingBox box) {
        int minY = Math.max(level.getMinBuildHeight(), box.minY()), maxY = Math.min(level.getMaxBuildHeight() - 1, box.maxY());
        for (int cx = box.minX() >> 4; cx <= box.maxX() >> 4; cx++) {
            for (int cz = box.minZ() >> 4; cz <= box.maxZ() >> 4; cz++) {
                if (!level.hasChunk(cx, cz)) continue;
                LevelChunk chunk = level.getChunk(cx, cz);
                int x0 = Math.max(box.minX(), cx << 4), x1 = Math.min(box.maxX(), (cx << 4) + 15);
                int z0 = Math.max(box.minZ(), cz << 4), z1 = Math.min(box.maxZ(), (cz << 4) + 15);
                BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos();
                for (int y = minY; y <= maxY; y++)
                    for (int x = x0; x <= x1; x++)
                        for (int z = z0; z <= z1; z++) {
                            p.set(x, y, z);
                            if (chunk.getBlockState(p).is(PLAYER_MADE)) return p.immutable();
                        }
            }
        }
        return null;
    }

    /** How far around the structure the land is sloped toward it after building. */
    static final int BLEND = 6;

    /**
     * Blocks between the bottom of each structure and the ground it stands on (the negative start height of
     * its jigsaw definition). Structures not listed (in water or at a fixed height) get no terrain blending.
     */
    private static final Map<String, Integer> GROUND_OFFSET = Map.of("frost_shrine", 3, "storm_shrine", 3, "ruined_capital", 5,
            "star_gate", 4, "trade_city", 0, "trade_city_desert", 0, "trade_city_savanna", 0, "trade_city_taiga", 0, "trade_city_snowy", 0);

    /**
     * A trade city: a rigid walled core (the first piece) with roads and outskirts that follow the terrain.
     * Terrain, height and blending go by the core; player builds and other structures are checked over the whole city.
     */
    static boolean isCity(Holder<Structure> structure, StructureStart start) {
        String id = structure.unwrapKey().map(k -> k.location().getPath()).orElse("");
        return id.startsWith("trade_city") && !start.getPieces().isEmpty();
    }

    static java.util.Optional<Integer> groundLevel(Holder<Structure> structure, BoundingBox box) {
        String id = structure.unwrapKey().map(k -> k.location().getPath()).orElse("");
        Integer off = GROUND_OFFSET.get(id);
        return off == null ? java.util.Optional.empty() : java.util.Optional.of(box.minY() + off);
    }

    /** The structure's box plus the blended margin and a little more: no player build may be in here. */
    static BoundingBox scanBox(BoundingBox box) {
        int m = BLEND + 2;
        return new BoundingBox(box.minX() - m, box.minY() - 2, box.minZ() - m, box.maxX() + m, box.maxY() + 6, box.maxZ() + m);
    }

    static List<ChunkPos> chunks(BoundingBox box) {
        List<ChunkPos> out = new ArrayList<>();
        for (int cx = box.minX() >> 4; cx <= box.maxX() >> 4; cx++)
            for (int cz = box.minZ() >> 4; cz <= box.maxZ() >> 4; cz++) out.add(new ChunkPos(cx, cz));
        return out;
    }

    /**
     * Checks the spot of {@code start}. Loads the existing chunks it covers. On OK, {@code dy} moves the
     * structure from the generator's terrain height to the real ground (players may have dug or built up).
     */
    static Site evaluate(ServerLevel level, Holder<Structure> structure, StructureStart start, boolean ignorePlayers) {
        BoundingBox box = start.getBoundingBox();
        String id = structure.unwrapKey().map(k -> k.location().getPath()).orElse("");
        boolean city = isCity(structure, start);
        BoundingBox core = city ? start.getPieces().get(0).getBoundingBox() : box;

        if (!ignorePlayers) {
            BoundingBox near = box.inflatedBy(24);
            for (var p : level.players()) {
                if (near.isInside(p.blockPosition())) return Site.of(Result.DEFER, "a player is nearby");
            }
        }

        // Every covered chunk must be fully generated or not generated at all (those generate their part later).
        for (ChunkPos cp : chunks(box)) {
            switch (Retrogen.chunkState(level, cp)) {
                case PARTIAL -> {
                    return Site.of(Result.DEFER, "chunk " + cp + " is only partly generated");
                }
                case FULL -> level.getChunk(cp.x, cp.z);
                case MISSING -> {}
            }
        }
        // The real biome must fit too (worlds from older versions can differ from today's generator).
        // Only checked where the land exists: measuring a missing chunk would generate it.
        var center = core.getCenter();
        if (Retrogen.chunkState(level, new ChunkPos(center.getX() >> 4, center.getZ() >> 4)) == Retrogen.ChunkState.FULL) {
            int groundCenter = FIXED_HEIGHT.contains(id) ? center.getY() : groundY(level, center.getX(), center.getZ(), null);
            if (!structure.value().biomes().contains(level.getBiome(new BlockPos(center.getX(), groundCenter, center.getZ())))) {
                return Site.of(Result.WRONG_BIOME, "wrong biome");
            }
        }

        long inhabitedLimit = ModConfig.RETROGEN_AVOID_MINUTES.get() * 1200L;
        for (ChunkPos cp : chunks(box)) {
            if (!level.hasChunk(cp.x, cp.z)) continue;
            LevelChunk chunk = level.getChunk(cp.x, cp.z);
            // Only real overlaps count: deep mineshafts are referenced by many surface chunks without touching them.
            for (Map.Entry<Structure, it.unimi.dsi.fastutil.longs.LongSet> ref : chunk.getAllReferences().entrySet()) {
                for (long startChunk : ref.getValue()) {
                    ChunkPos sp = new ChunkPos(startChunk);
                    StructureStart other = level.getChunk(sp.x, sp.z, ChunkStatus.STRUCTURE_STARTS).getStartForStructure(ref.getKey());
                    if (other != null && other.isValid() && other.getPieces().stream().anyMatch(pc -> pc.getBoundingBox().intersects(scanBox(box)))) {
                        return Site.of(Result.BLOCKED, "overlaps another structure");
                    }
                }
            }
            if (inhabitedLimit > 0 && chunk.getInhabitedTime() > inhabitedLimit) {
                return Site.of(Result.BLOCKED, "players spent a long time in chunk " + cp);
            }
        }

        int dy = 0;
        String terrain = "fixed height";
        if (!FIXED_HEIGHT.contains(id)) {
            // Terrain: sample the footprint every 4 blocks.
            List<Integer> heights = new ArrayList<>();
            int water = 0;
            for (int x = core.minX(); x <= core.maxX(); x += 4) {
                for (int z = core.minZ(); z <= core.maxZ(); z += 4) {
                    if (!level.hasChunk(x >> 4, z >> 4)) continue;
                    boolean[] w = {false};
                    heights.add(groundY(level, x, z, w));
                    if (w[0]) water++;
                }
            }
            if (heights.isEmpty()) return Site.of(Result.DEFER, "no loaded ground to measure");
            int[] h = heights.stream().mapToInt(Integer::intValue).sorted().toArray();
            int median = h[h.length / 2];
            if (!IN_WATER.contains(id)) {
                if (water > heights.size() * 0.35) return Site.of(Result.BLOCKED, "too much water");
                int spread = h[(int) (h.length * 0.9)] - h[(int) (h.length * 0.1)];
                if (spread > 14) return Site.of(Result.BLOCKED, "ground too uneven (" + spread + " blocks)");
            }
            var gen = level.getChunkSource().getGenerator();
            int generated = gen.getFirstFreeHeight(center.getX(), center.getZ(), Heightmap.Types.WORLD_SURFACE_WG, level, level.getChunkSource().randomState());
            // A city's core has its ground layer at a known height above its bottom; others stand where the generator put them.
            dy = city ? median - (core.minY() + GROUND_OFFSET.getOrDefault(id, 0) + 1) : median - generated;
            terrain = "ground " + h[0] + ".." + h[h.length - 1] + ", median " + median;
        }

        // Builds are checked where the structure will really stand (after the height correction).
        // A city moves only its core (roads follow the ground anyway), so look over the whole height range.
        BoundingBox moved = city ? new BoundingBox(box.minX(), box.minY() - Math.abs(dy), box.minZ(), box.maxX(), box.maxY() + Math.abs(dy), box.maxZ())
                : box.moved(0, dy, 0);
        BlockPos build = findPlayerBuild(level, scanBox(moved));
        if (build != null) return Site.of(Result.BLOCKED, "player-made block at " + build.toShortString());
        return new Site(Result.OK, dy, terrain);
    }
}
