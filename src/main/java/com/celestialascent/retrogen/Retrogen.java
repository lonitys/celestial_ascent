package com.celestialascent.retrogen;

import com.celestialascent.CelestialAscent;
import com.celestialascent.core.ModConfig;
import com.celestialascent.retrogen.RetrogenData.Status;
import com.mojang.logging.LogUtils;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureSet;
import net.minecraft.world.level.levelgen.structure.StructureStart;
import net.minecraft.world.level.levelgen.structure.pieces.PiecesContainer;
import net.minecraft.world.level.levelgen.structure.placement.RandomSpreadStructurePlacement;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.level.ChunkEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import org.slf4j.Logger;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Optional;

/**
 * Builds Celestial Ascent structures into land that was generated before the mod was installed.
 *
 * <p>Minecraft only places structures while it generates new chunks, so explored land in an existing
 * world would never get a shrine. For every structure cell of our structure sets (the same grid and
 * biome rule a new world uses) this checks the spot that a new world would have used. If it is free,
 * the structure is built there and registered in the chunk like a normal one (maps and /locate find
 * it). If players built there, another structure is in the way or the ground is unusable, it looks
 * for a free spot nearby instead. Nothing is built while a player is close.</p>
 */
@EventBusSubscriber(modid = CelestialAscent.MODID)
public final class Retrogen {
    private Retrogen() {}

    private static final Logger LOG = LogUtils.getLogger();

    /**
     * Stored on a cell's usual chunk when its structure was built elsewhere (structure id -> centre), so the
     * world itself remembers the move even without the retrogen save file.
     */
    public static final java.util.function.Supplier<net.neoforged.neoforge.attachment.AttachmentType<java.util.Map<String, Long>>> MOVED =
            com.celestialascent.core.CAReg.ATTACHMENTS.register("moved_structures", () -> net.neoforged.neoforge.attachment.AttachmentType
                    .<java.util.Map<String, Long>>builder(() -> java.util.Map.of())
                    .serialize(com.mojang.serialization.Codec.unboundedMap(com.mojang.serialization.Codec.STRING, com.mojang.serialization.Codec.LONG))
                    .build());

    static boolean enabled() {
        return ModConfig.RETROGEN.get() && !Boolean.getBoolean("celestialascent.debug.noStructures");
    }

    private static boolean paused() {
        return Boolean.getBoolean("celestialascent.debug.retrogenPaused");
    }

    // ------------------------------------------------------------------ cells

    /** Our random-spread structure sets that can generate in this dimension. */
    static List<Holder<StructureSet>> sets(ServerLevel level) {
        return level.getChunkSource().getGeneratorState().possibleStructureSets().stream()
                .filter(h -> h.unwrapKey().map(k -> k.location().getNamespace().equals(CelestialAscent.MODID)).orElse(false))
                .filter(h -> h.value().placement() instanceof RandomSpreadStructurePlacement)
                .toList();
    }

    static String key(Holder<StructureSet> set, int cellX, int cellZ) {
        return set.unwrapKey().orElseThrow().location() + "|" + cellX + "|" + cellZ;
    }

    private static RandomSpreadStructurePlacement placement(Holder<StructureSet> set) {
        return (RandomSpreadStructurePlacement) set.value().placement();
    }

    private static ChunkPos origin(ServerLevel level, RandomSpreadStructurePlacement p, int cellX, int cellZ) {
        return p.getPotentialStructureChunk(level.getChunkSource().getGeneratorState().getLevelSeed(), cellX * p.spacing(), cellZ * p.spacing());
    }

    /** Queues every cell whose structure spot lies within {@code radius} chunks of {@code center}. */
    public static int scan(ServerLevel level, ChunkPos center, int radius) {
        if (!enabled()) return 0;
        RetrogenData data = RetrogenData.get(level);
        int added = 0;
        for (var set : sets(level)) {
            var p = placement(set);
            int s = p.spacing();
            for (int cx = Math.floorDiv(center.x - radius, s); cx <= Math.floorDiv(center.x + radius, s); cx++) {
                for (int cz = Math.floorDiv(center.z - radius, s); cz <= Math.floorDiv(center.z + radius, s); cz++) {
                    ChunkPos o = origin(level, p, cx, cz);
                    if (Math.max(Math.abs(o.x - center.x), Math.abs(o.z - center.z)) > radius) continue;
                    String k = key(set, cx, cz);
                    if (data.entry(k) == null) {
                        data.enqueue(k);
                        added++;
                    }
                }
            }
        }
        return added;
    }

    // ------------------------------------------------------------------ chunk state

    enum ChunkState { MISSING, PARTIAL, FULL }

    /** Whether a chunk exists and is fully generated, without generating it. */
    static ChunkState chunkState(ServerLevel level, ChunkPos cp) {
        if (level.hasChunk(cp.x, cp.z)) return ChunkState.FULL;
        try {
            Optional<CompoundTag> tag = level.getChunkSource().chunkMap.read(cp).join();
            if (tag.isEmpty()) return ChunkState.MISSING;
            String status = tag.get().getString("Status");
            return status.equals("minecraft:full") || status.equals("full") ? ChunkState.FULL : ChunkState.PARTIAL;
        } catch (RuntimeException e) {
            return ChunkState.PARTIAL;
        }
    }

    // ------------------------------------------------------------------ events

    @SubscribeEvent
    public static void chunkLoad(ChunkEvent.Load e) {
        if (!(e.getLevel() instanceof ServerLevel level) || !(e.getChunk() instanceof LevelChunk) || !enabled()) return;
        ChunkPos cp = e.getChunk().getPos();
        var state = level.getChunkSource().getGeneratorState();
        for (var set : sets(level)) {
            var p = placement(set);
            if (p.isStructureChunk(state, cp.x, cp.z)) {
                RetrogenData.get(level).enqueue(key(set, Math.floorDiv(cp.x, p.spacing()), Math.floorDiv(cp.z, p.spacing())));
            }
        }
    }

    @SubscribeEvent
    public static void login(PlayerEvent.PlayerLoggedInEvent e) {
        if (e.getEntity() instanceof ServerPlayer p) scan(p.serverLevel(), p.chunkPosition(), ModConfig.RETROGEN_RADIUS.get());
    }

    @SubscribeEvent
    public static void changedDimension(PlayerEvent.PlayerChangedDimensionEvent e) {
        if (e.getEntity() instanceof ServerPlayer p) scan(p.serverLevel(), p.chunkPosition(), ModConfig.RETROGEN_RADIUS.get());
    }

    @SubscribeEvent
    public static void tick(ServerTickEvent.Post e) {
        if (!enabled() || paused() || e.getServer().getTickCount() % 10 != 0) return;
        for (ServerLevel level : e.getServer().getAllLevels()) {
            for (String k : RetrogenData.get(level).due(level.getGameTime(), 1)) {
                try {
                    String result = process(level, k, false);
                    LOG.debug("Retrogen {} {}: {}", level.dimension().location(), k, result);
                } catch (RuntimeException ex) {
                    LOG.error("Retrogen failed for {} in {}", k, level.dimension().location(), ex);
                    RetrogenData.get(level).finish(k, Status.BLOCKED, null, null);
                }
            }
        }
    }

    // ------------------------------------------------------------------ processing

    static StructureStart generate(ServerLevel level, Holder<Structure> structure, ChunkPos chunk) {
        var gen = level.getChunkSource().getGenerator();
        return structure.value().generate(level.registryAccess(), gen, gen.getBiomeSource(), level.getChunkSource().randomState(),
                level.getStructureManager(), level.getChunkSource().getGeneratorState().getLevelSeed(), chunk, 0, level,
                structure.value().biomes()::contains);
    }

    /** Decides one cell. Returns a short description of what happened (for logs and the status command). */
    public static String process(ServerLevel level, String key, boolean ignorePlayers) {
        RetrogenData data = RetrogenData.get(level);
        RetrogenData.Entry known = data.entry(key);
        if (known != null && known.done()) return "already " + known.status;
        String[] parts = key.split("\\|");
        var setKey = ResourceKey.create(Registries.STRUCTURE_SET, ResourceLocation.parse(parts[0]));
        var set = level.registryAccess().registryOrThrow(Registries.STRUCTURE_SET).getHolder(setKey);
        if (set.isEmpty() || !(set.get().value().placement() instanceof RandomSpreadStructurePlacement p)) {
            data.finish(key, Status.NONE, null, null);
            return "unknown structure set";
        }
        ChunkPos origin = origin(level, p, Integer.parseInt(parts[1]), Integer.parseInt(parts[2]));
        if (!p.isStructureChunk(level.getChunkSource().getGeneratorState(), origin.x, origin.z)) {
            data.finish(key, Status.NONE, null, null);
            return "no structure in this cell";
        }
        // A set can hold several structures (the trade city has one per biome style): worldgen uses the one whose
        // biome fits, so the retrogen tries them in order and takes the first that generates here.
        List<Holder<Structure>> options = set.get().value().structures().stream().map(e -> e.structure()).toList();
        Holder<Structure> structure = options.get(0);
        ResourceLocation id = structure.unwrapKey().orElseThrow().location();

        switch (chunkState(level, origin)) {
            case MISSING -> {
                data.finish(key, Status.NATURAL, id, null);
                return "not generated yet: normal worldgen builds it";
            }
            case PARTIAL -> {
                data.defer(key, level.getGameTime() + 6000);
                return "waiting for the chunk to finish generating";
            }
            case FULL -> {}
        }
        LevelChunk chunk = level.getChunk(origin.x, origin.z);
        for (Holder<Structure> option : options) {
            ResourceLocation oid = option.unwrapKey().orElseThrow().location();
            StructureStart existing = chunk.getStartForStructure(option.value());
            if (existing != null && existing.isValid()) {
                data.finish(key, Status.NATURAL, oid, centerOf(existing.getBoundingBox()));
                return "already generated normally";
            }
            Long moved = chunk.getData(MOVED).get(oid.toString());
            if (moved != null) {
                data.finish(key, Status.RELOCATED, oid, BlockPos.of(moved));
                return "already built nearby at " + BlockPos.of(moved).toShortString();
            }
        }
        StructureStart start = null;
        for (Holder<Structure> option : options) {
            StructureStart s = generate(level, option, origin);
            if (s.isValid()) {
                structure = option;
                id = option.unwrapKey().orElseThrow().location();
                start = s;
                break;
            }
        }
        if (start == null) {
            data.finish(key, Status.NONE, id, null);
            return "no structure here (biome)";
        }
        SiteCheck.Site site = SiteCheck.evaluate(level, structure, start, ignorePlayers);
        switch (site.result()) {
            case OK -> {
                BoundingBox box = place(level, structure, start, site.dy());
                data.finish(key, Status.PLACED, id, centerOf(box));
                LOG.info("Built {} into existing land at {} ({})", id, centerOf(box).toShortString(), site.reason());
                return "built at " + centerOf(box).toShortString();
            }
            case DEFER -> {
                data.defer(key, level.getGameTime() + 1200);
                return "later: " + site.reason();
            }
            case WRONG_BIOME -> {
                data.finish(key, Status.NONE, id, null);
                return "no structure here (biome)";
            }
            default -> {
                return relocate(level, key, structure, options, origin, p.spacing(), ignorePlayers, site.reason());
            }
        }
    }

    /** Looks for a free spot around the blocked one, nearest first. */
    private static String relocate(ServerLevel level, String key, Holder<Structure> blocked, List<Holder<Structure>> options, ChunkPos origin,
                                   int spacing, boolean ignorePlayers, String why) {
        RetrogenData data = RetrogenData.get(level);
        ResourceLocation blockedId = blocked.unwrapKey().orElseThrow().location();
        int reach = Math.max(4, Math.min(12, spacing / 2));
        List<ChunkPos> candidates = new ArrayList<>();
        for (int r = 3; r <= reach; r += 3) {
            for (int i = -r; i <= r; i += 3) {
                candidates.add(new ChunkPos(origin.x + i, origin.z - r));
                candidates.add(new ChunkPos(origin.x + i, origin.z + r));
                if (Math.abs(i) != r) {
                    candidates.add(new ChunkPos(origin.x - r, origin.z + i));
                    candidates.add(new ChunkPos(origin.x + r, origin.z + i));
                }
            }
        }
        candidates.sort(Comparator.comparingInt(c -> (c.x - origin.x) * (c.x - origin.x) + (c.z - origin.z) * (c.z - origin.z)));
        boolean waiting = false;
        for (ChunkPos c : candidates) {
            if (chunkState(level, c) != ChunkState.FULL) continue; // only land that already exists
            // The blocked structure first, then the other styles of its set (the biome may change nearby).
            Holder<Structure> structure = null;
            StructureStart start = null;
            for (Holder<Structure> option : java.util.stream.Stream.concat(java.util.stream.Stream.of(blocked),
                    options.stream().filter(o -> o != blocked)).toList()) {
                StructureStart s = generate(level, option, c);
                if (s.isValid()) {
                    structure = option;
                    start = s;
                    break;
                }
            }
            if (start == null) continue;
            ResourceLocation id = structure.unwrapKey().orElseThrow().location();
            SiteCheck.Site site = SiteCheck.evaluate(level, structure, start, ignorePlayers);
            if (site.result() == SiteCheck.Result.OK) {
                BoundingBox box = place(level, structure, start, site.dy());
                data.finish(key, Status.RELOCATED, id, centerOf(box));
                LevelChunk usual = level.getChunk(origin.x, origin.z);
                java.util.Map<String, Long> movedMap = new java.util.HashMap<>(usual.getData(MOVED));
                movedMap.put(id.toString(), centerOf(box).asLong());
                usual.setData(MOVED, movedMap);
                LOG.info("Built {} into existing land at {}: the usual spot was unusable ({})", id, centerOf(box).toShortString(), why);
                return "moved (" + why + ") and built at " + centerOf(box).toShortString();
            }
            if (site.result() == SiteCheck.Result.DEFER) waiting = true;
        }
        if (waiting) {
            data.defer(key, level.getGameTime() + 1200);
            return "later: the free spots nearby have players close (" + why + ")";
        }
        data.finish(key, Status.BLOCKED, blockedId, null);
        LOG.info("No free spot for {} near chunk {} ({})", blockedId, origin, why);
        return "no free spot nearby (" + why + ")";
    }

    private static BlockPos centerOf(BoundingBox box) {
        return new BlockPos(box.getCenter().getX(), box.minY(), box.getCenter().getZ());
    }

    /**
     * Builds the structure into the existing chunks it covers and registers it like a generated one.
     * Chunks that do not exist yet build their part themselves when they generate.
     */
    static BoundingBox place(ServerLevel level, Holder<Structure> structure, StructureStart start, int dy) {
        boolean city = SiteCheck.isCity(structure, start);
        if (dy != 0) {
            // A city only lifts or lowers its core: its roads follow the ground and its outskirts sit on them.
            (city ? start.getPieces().subList(0, 1) : start.getPieces()).forEach(piece -> piece.move(0, dy, 0));
            start = new StructureStart(structure.value(), start.getChunkPos(), start.getReferences(), new PiecesContainer(start.getPieces()));
        }
        BoundingBox box = start.getBoundingBox();
        var gen = level.getChunkSource().getGenerator();
        ChunkPos origin = start.getChunkPos();
        for (ChunkPos cp : SiteCheck.chunks(box)) {
            if (chunkState(level, cp) != ChunkState.FULL) continue;
            LevelChunk chunk = level.getChunk(cp.x, cp.z);
            BoundingBox chunkBox = new BoundingBox(cp.getMinBlockX(), level.getMinBuildHeight(), cp.getMinBlockZ(),
                    cp.getMaxBlockX(), level.getMaxBuildHeight() - 1, cp.getMaxBlockZ());
            start.placeInChunk(level, level.structureManager(), gen, level.getRandom(), chunkBox, cp);
            chunk.addReferenceForStructure(structure.value(), origin.toLong());
        }
        LevelChunk originChunk = level.getChunk(origin.x, origin.z);
        originChunk.setStartForStructure(structure.value(), start);
        level.structureCheck.onStructureLoad(origin, originChunk.getAllStarts()); // so maps and /locate see it now
        if (city) {
            for (var piece : start.getPieces()) {
                if (piece instanceof net.minecraft.world.level.levelgen.structure.PoolElementStructurePiece pe
                        && pe.getElement().getProjection() == net.minecraft.world.level.levelgen.structure.pools.StructureTemplatePool.Projection.RIGID) {
                    foundations(level, piece.getBoundingBox());
                }
            }
            BoundingBox core = start.getPieces().get(0).getBoundingBox();
            SiteCheck.groundLevel(structure, core).ifPresent(ground -> blendTerrain(level, core, ground));
        } else {
            foundations(level, box);
            SiteCheck.groundLevel(structure, box).ifPresent(ground -> blendTerrain(level, box, ground));
        }
        return box;
    }

    /**
     * Slopes the land around the structure toward its ground level (one block per block of distance),
     * like the terrain adaptation of a newly generated world, so it stands neither behind a cliff nor on a wall.
     * Only natural blocks are moved; the site check already made sure no player build is this close.
     */
    private static void blendTerrain(ServerLevel level, BoundingBox box, int ground) {
        BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos();
        int m = SiteCheck.BLEND;
        for (int x = box.minX() - m; x <= box.maxX() + m; x++) {
            for (int z = box.minZ() - m; z <= box.maxZ() + m; z++) {
                int d = Math.max(Math.max(box.minX() - x, x - box.maxX()), Math.max(box.minZ() - z, z - box.maxZ()));
                if (d <= 0 || !level.hasChunk(x >> 4, z >> 4)) continue;
                boolean[] water = {false};
                int surface = SiteCheck.groundY(level, x, z, water); // first free block above the ground
                if (water[0]) continue;
                BlockState top = level.getBlockState(p.set(x, surface - 1, z));
                BlockState fill = level.getBlockState(p.set(x, surface - 2, z));
                if (top.hasBlockEntity() || top.is(SiteCheck.PLAYER_MADE)) continue;
                int high = ground + d, low = ground - d;
                if (surface > high) {
                    // Too high: cut the column down, with any plants or tree parts standing on it.
                    int tallest = level.getHeight(net.minecraft.world.level.levelgen.Heightmap.Types.WORLD_SURFACE, x, z);
                    for (int y = tallest; y >= high; y--) {
                        BlockState st = level.getBlockState(p.set(x, y, z));
                        if (st.hasBlockEntity() || st.is(SiteCheck.PLAYER_MADE)) break;
                        if (!st.isAir()) level.setBlock(p, net.minecraft.world.level.block.Blocks.AIR.defaultBlockState(), Block.UPDATE_CLIENTS);
                    }
                    level.setBlock(p.set(x, high - 1, z), top, Block.UPDATE_CLIENTS);
                } else if (surface < low) {
                    // Too low: build the column up with the ground it already has.
                    if (!fill.isCollisionShapeFullBlock(level, p.set(x, surface - 2, z))) fill = top;
                    for (int y = surface - 1; y < low - 1; y++) level.setBlock(p.set(x, y, z), fill, Block.UPDATE_CLIENTS);
                    level.setBlock(p.set(x, low - 1, z), top, Block.UPDATE_CLIENTS);
                }
            }
        }
    }

    /** Fills gaps under the structure's floor down to the ground, so it never floats over a dip. */
    private static void foundations(ServerLevel level, BoundingBox box) {
        BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos();
        for (int x = box.minX(); x <= box.maxX(); x++) {
            for (int z = box.minZ(); z <= box.maxZ(); z++) {
                if (!level.hasChunk(x >> 4, z >> 4)) continue;
                BlockState floor = null;
                int floorY = 0;
                for (int y = box.minY(); y <= box.minY() + 3; y++) {
                    BlockState s = level.getBlockState(p.set(x, y, z));
                    if (!s.isAir() && s.getFluidState().isEmpty()) {
                        floor = s;
                        floorY = y;
                        break;
                    }
                }
                if (floor == null || !floor.isCollisionShapeFullBlock(level, p.set(x, floorY, z)) || floor.hasBlockEntity()) continue;
                for (int y = floorY - 1; y >= Math.max(level.getMinBuildHeight(), floorY - 16); y--) {
                    BlockState below = level.getBlockState(p.set(x, y, z));
                    if (!(below.isAir() || below.canBeReplaced() || !below.getFluidState().isEmpty())) break;
                    level.setBlock(p, floor, Block.UPDATE_CLIENTS);
                }
            }
        }
    }

    // ------------------------------------------------------------------ finding

    /**
     * Nearest structure in {@code tag}: normal ones (including those built late at their usual spot)
     * plus those built at another spot. Decides the closest undecided cells first, so a map or compass
     * used in explored land points at a structure there rather than at unexplored land far away.
     */
    public static BlockPos findNearest(ServerLevel level, TagKey<Structure> tag, BlockPos from, boolean skipKnown) {
        if (enabled()) decideNear(level, tag, new ChunkPos(from), 6);
        BlockPos best = level.findNearestMapStructure(tag, from, 100, skipKnown);
        double bestD = best == null ? Double.MAX_VALUE : horizontal(best, from);
        var reg = level.registryAccess().registryOrThrow(Registries.STRUCTURE);
        for (RetrogenData.Entry e : RetrogenData.get(level).cells().values()) {
            if (e.status != Status.RELOCATED || e.center == null || e.structure == null) continue;
            var h = reg.getHolder(ResourceKey.create(Registries.STRUCTURE, e.structure));
            if (h.isEmpty() || !h.get().is(tag)) continue;
            double d = horizontal(e.center, from);
            if (d < bestD) {
                bestD = d;
                best = e.center;
            }
        }
        return best;
    }

    private static double horizontal(BlockPos a, BlockPos b) {
        double dx = a.getX() - b.getX(), dz = a.getZ() - b.getZ();
        return dx * dx + dz * dz;
    }

    /** Decides up to {@code max} of the nearest undecided cells for structures in {@code tag}. */
    private static void decideNear(ServerLevel level, TagKey<Structure> tag, ChunkPos from, int max) {
        RetrogenData data = RetrogenData.get(level);
        List<String> keys = new ArrayList<>();
        List<Integer> dist = new ArrayList<>();
        for (var set : sets(level)) {
            if (set.value().structures().stream().noneMatch(e -> e.structure().is(tag))) continue;
            var p = placement(set);
            int s = p.spacing(), cx0 = Math.floorDiv(from.x, s), cz0 = Math.floorDiv(from.z, s);
            for (int cx = cx0 - 3; cx <= cx0 + 3; cx++) {
                for (int cz = cz0 - 3; cz <= cz0 + 3; cz++) {
                    String k = key(set, cx, cz);
                    RetrogenData.Entry e = data.entry(k);
                    if (e != null && e.done()) continue;
                    ChunkPos o = origin(level, p, cx, cz);
                    keys.add(k);
                    dist.add((o.x - from.x) * (o.x - from.x) + (o.z - from.z) * (o.z - from.z));
                }
            }
        }
        List<Integer> order = new ArrayList<>();
        for (int i = 0; i < keys.size(); i++) order.add(i);
        order.sort(Comparator.comparingInt(dist::get));
        for (int i = 0; i < Math.min(max, order.size()); i++) {
            String k = keys.get(order.get(i));
            data.enqueue(k);
            process(level, k, false);
        }
    }
}
