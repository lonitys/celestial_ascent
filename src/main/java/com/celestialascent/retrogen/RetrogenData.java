package com.celestialascent.retrogen;

import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Per-dimension record of every structure cell the retrogen has looked at, so each cell is decided
 * once: left to normal worldgen, built late, moved to a free spot, or found to have no structure.
 */
public final class RetrogenData extends SavedData {
    public enum Status {
        /** Not decided yet (waiting for its turn, for chunks to finish loading, or for players to leave). */
        PENDING,
        /** Normal worldgen placed it, or will when the chunk is generated. */
        NATURAL,
        /** No structure belongs in this cell (wrong biome, as in a new world). */
        NONE,
        /** Built late at the spot a new world would have used. */
        PLACED,
        /** That spot was taken (player builds, another structure, terrain), so it was built nearby instead. */
        RELOCATED,
        /** No free spot was found around this cell. */
        BLOCKED
    }

    public static final class Entry {
        public Status status = Status.PENDING;
        public ResourceLocation structure;
        public BlockPos center;
        long nextTry;
        int tries;

        public boolean done() {
            return status != Status.PENDING;
        }
    }

    private final Map<String, Entry> cells = new LinkedHashMap<>();

    private static final Factory<RetrogenData> FACTORY = new Factory<>(RetrogenData::new, RetrogenData::load, null);

    public static RetrogenData get(ServerLevel level) {
        return level.getDataStorage().computeIfAbsent(FACTORY, "celestialascent_retrogen");
    }

    public Entry entry(String key) {
        return cells.get(key);
    }

    public Map<String, Entry> cells() {
        return cells;
    }

    /** Queues a cell unless it is already known. */
    public void enqueue(String key) {
        if (cells.containsKey(key)) return;
        cells.put(key, new Entry());
        setDirty();
    }

    public void finish(String key, Status status, ResourceLocation structure, BlockPos center) {
        Entry e = cells.computeIfAbsent(key, k -> new Entry());
        e.status = status;
        e.structure = structure;
        e.center = center;
        setDirty();
    }

    public void defer(String key, long until) {
        Entry e = cells.computeIfAbsent(key, k -> new Entry());
        e.nextTry = until;
        e.tries++;
        setDirty();
    }

    /** Pending cells whose retry time has come, oldest first. */
    public List<String> due(long now, int max) {
        List<String> out = new ArrayList<>();
        for (var e : cells.entrySet()) {
            if (e.getValue().status == Status.PENDING && e.getValue().nextTry <= now) {
                out.add(e.getKey());
                if (out.size() >= max) break;
            }
        }
        return out;
    }

    @Override
    public CompoundTag save(CompoundTag tag, HolderLookup.Provider lookup) {
        CompoundTag all = new CompoundTag();
        cells.forEach((k, e) -> {
            CompoundTag t = new CompoundTag();
            t.putString("Status", e.status.name());
            if (e.structure != null) t.putString("Structure", e.structure.toString());
            if (e.center != null) t.putLong("Center", e.center.asLong());
            t.putLong("NextTry", e.nextTry);
            t.putInt("Tries", e.tries);
            all.put(k, t);
        });
        tag.put("Cells", all);
        return tag;
    }

    private static RetrogenData load(CompoundTag tag, HolderLookup.Provider lookup) {
        RetrogenData d = new RetrogenData();
        CompoundTag all = tag.getCompound("Cells");
        for (String k : all.getAllKeys()) {
            CompoundTag t = all.getCompound(k);
            Entry e = new Entry();
            try {
                e.status = Status.valueOf(t.getString("Status"));
            } catch (IllegalArgumentException ex) {
                e.status = Status.PENDING;
            }
            if (t.contains("Structure")) e.structure = ResourceLocation.tryParse(t.getString("Structure"));
            if (t.contains("Center")) e.center = BlockPos.of(t.getLong("Center"));
            e.nextTry = t.getLong("NextTry");
            e.tries = t.getInt("Tries");
            d.cells.put(k, e);
        }
        return d;
    }
}
