package com.celestialascent.economy;

import com.celestialascent.CelestialAscent;
import com.celestialascent.core.Scheduler;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.ai.village.poi.PoiManager;
import net.minecraft.world.entity.ai.village.poi.PoiTypes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructurePlaceSettings;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplate;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.phys.AABB;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * Village prosperity. Quests and trade raise a village's prosperity (keyed by its bell); at each
 * threshold the village constructs a new building block by block on free, flat ground near the bell.
 */
public final class VillageGrowth extends SavedData {
    private static final String NAME = "celestialascent_villages";
    public static final int[] THRESHOLDS = {100, 250, 500, 900, 1400, 2000, 2800, 3800, 5000, 6500};
    public static final String[] BUILDINGS = {"market_stall", "lamp_post", "cottage", "bank_kiosk", "garden",
            "cottage", "fountain", "watchtower", "smithy", "cottage"};

    private final Map<Long, int[]> villages = new HashMap<>(); // bell -> {prosperity, level}

    public static VillageGrowth get(ServerLevel level) {
        return level.getServer().overworld().getDataStorage().computeIfAbsent(new Factory<>(VillageGrowth::new, VillageGrowth::load), NAME);
    }

    public int prosperity(BlockPos bell) {
        return villages.getOrDefault(bell.asLong(), new int[2])[0];
    }

    public int level(BlockPos bell) {
        return villages.getOrDefault(bell.asLong(), new int[2])[1];
    }

    /** Number of thresholds at or below a prosperity value. */
    public static int levelFor(int prosperity) {
        int l = 0;
        for (int t : THRESHOLDS) if (prosperity >= t) l++;
        return l;
    }

    public static Optional<BlockPos> nearestBell(ServerLevel level, BlockPos near) {
        return level.getPoiManager().findClosest(h -> h.is(PoiTypes.MEETING), near, 64, PoiManager.Occupancy.ANY);
    }

    /** Adds prosperity to the village nearest {@code near}; builds any newly earned buildings. */
    public static void addProsperity(ServerLevel level, BlockPos near, int amount, Player by) {
        if (level.dimension() != net.minecraft.world.level.Level.OVERWORLD) return;
        Optional<BlockPos> bell = nearestBell(level, near);
        if (bell.isEmpty()) return;
        VillageGrowth data = get(level);
        int[] v = data.villages.computeIfAbsent(bell.get().asLong(), k -> new int[2]);
        v[0] += amount;
        int target = levelFor(v[0]);
        data.setDirty();
        if (by instanceof ServerPlayer sp) {
            int next = v[1] < THRESHOLDS.length ? THRESHOLDS[Math.min(v[1], THRESHOLDS.length - 1)] : -1;
            sp.displayClientMessage(Component.translatable("message.celestialascent.prosperity", v[0], next < 0 ? "max" : String.valueOf(next)), true);
        }
        while (v[1] < target) {
            String building = BUILDINGS[v[1] % BUILDINGS.length];
            v[1]++;
            build(level, bell.get(), building);
        }
    }

    /** Finds a free, roughly flat spot near the bell and constructs the named building there. */
    public static boolean build(ServerLevel level, BlockPos bell, String name) {
        ResourceLocation id = ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "village/" + name);
        Optional<StructureTemplate> opt = level.getStructureManager().get(id);
        if (opt.isEmpty()) return false;
        StructureTemplate t = opt.get();
        var size = t.getSize();
        RandomSource r = level.random;
        for (int attempt = 0; attempt < 40; attempt++) {
            double a = r.nextDouble() * Math.PI * 2, d = 10 + r.nextDouble() * 22;
            int x = bell.getX() + (int) (Math.cos(a) * d), z = bell.getZ() + (int) (Math.sin(a) * d);
            BlockPos origin = siteAt(level, x, z, size.getX(), size.getZ());
            if (origin != null) {
                construct(level, t, origin, name);
                return true;
            }
        }
        return false;
    }

    /** Ground origin if the footprint is flat (±1), natural ground, dry and unbuilt; otherwise null. */
    static BlockPos siteAt(ServerLevel level, int x0, int z0, int w, int d) {
        int min = Integer.MAX_VALUE, max = Integer.MIN_VALUE;
        for (int x = x0; x < x0 + w; x++) {
            for (int z = z0; z < z0 + d; z++) {
                int y = level.getHeight(Heightmap.Types.WORLD_SURFACE, x, z);
                BlockState ground = level.getBlockState(new BlockPos(x, y - 1, z));
                boolean natural = ground.is(BlockTags.DIRT) || ground.is(BlockTags.SAND) || ground.is(Blocks.GRAVEL)
                        || ground.is(BlockTags.BASE_STONE_OVERWORLD) || ground.is(Blocks.SNOW_BLOCK) || ground.is(Blocks.DIRT_PATH);
                if (!natural || !level.getFluidState(new BlockPos(x, y, z)).isEmpty()) return null;
                min = Math.min(min, y);
                max = Math.max(max, y);
            }
        }
        if (max - min > 1) return null;
        AABB box = new AABB(x0, min, z0, x0 + w, min + 6, z0 + d);
        if (!level.getEntitiesOfClass(Player.class, box.inflate(1)).isEmpty()) return null;
        return new BlockPos(x0, min, z0);
    }

    /** Places the template a few blocks per tick, bottom layer first, with building effects. */
    static void construct(ServerLevel level, StructureTemplate t, BlockPos origin, String name) {
        if (t.palettes.isEmpty()) return;
        List<StructureTemplate.StructureBlockInfo> infos = StructureTemplate.processBlockInfos(level, origin, origin,
                new StructurePlaceSettings(), new ArrayList<>(t.palettes.get(0).blocks()), t);
        infos.sort(Comparator.<StructureTemplate.StructureBlockInfo>comparingInt(i -> i.pos().getY()).thenComparingInt(i -> i.pos().getX())
                .thenComparingInt(i -> i.pos().getZ()));
        int perTick = 4;
        for (int i = 0; i < infos.size(); i += perTick) {
            int from = i;
            Scheduler.later(level, 1 + i / perTick, () -> {
                for (int k = from; k < Math.min(from + perTick, infos.size()); k++) {
                    var info = infos.get(k);
                    level.setBlock(info.pos(), info.state(), 3);
                    if (info.nbt() != null && level.getBlockEntity(info.pos()) != null) {
                        level.getBlockEntity(info.pos()).loadWithComponents(info.nbt(), level.registryAccess());
                    }
                    if (!info.state().isAir() && k % 3 == 0) {
                        level.sendParticles(ParticleTypes.HAPPY_VILLAGER, info.pos().getX() + 0.5, info.pos().getY() + 0.8, info.pos().getZ() + 0.5, 1, 0.2, 0.2, 0.2, 0);
                    }
                }
                if (from % 24 == 0) level.playSound(null, origin, SoundEvents.WOOD_PLACE, SoundSource.BLOCKS, 0.8f, 0.8f + level.random.nextFloat() * 0.4f);
            });
        }
        Scheduler.later(level, 2 + infos.size() / perTick, () -> {
            level.playSound(null, origin, SoundEvents.VILLAGER_CELEBRATE, SoundSource.NEUTRAL, 1.5f, 1f);
            Component msg = Component.translatable("message.celestialascent.village_grew",
                    Component.translatable("building.celestialascent." + name)).withColor(0x8BE37A);
            for (Player p : level.getEntitiesOfClass(Player.class, new AABB(origin).inflate(96))) p.sendSystemMessage(msg);
        });
    }

    private static VillageGrowth load(CompoundTag tag, HolderLookup.Provider lookup) {
        VillageGrowth g = new VillageGrowth();
        CompoundTag v = tag.getCompound("Villages");
        for (String k : v.getAllKeys()) {
            int[] arr = v.getIntArray(k);
            if (arr.length == 2) g.villages.put(Long.parseLong(k), arr);
        }
        return g;
    }

    @Override
    public CompoundTag save(CompoundTag tag, HolderLookup.Provider lookup) {
        CompoundTag v = new CompoundTag();
        villages.forEach((k, arr) -> v.putIntArray(Long.toString(k), arr));
        tag.put("Villages", v);
        return tag;
    }
}
