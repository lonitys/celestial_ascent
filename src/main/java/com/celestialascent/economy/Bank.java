package com.celestialascent.economy;

import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/** World-wide bank balances, saved with the overworld. Balances survive death. */
public final class Bank extends SavedData {
    private static final String NAME = "celestialascent_bank";
    private final Map<UUID, Long> balances = new HashMap<>();

    public static Bank get(MinecraftServer server) {
        return server.overworld().getDataStorage().computeIfAbsent(new Factory<>(Bank::new, Bank::load), NAME);
    }

    public long balance(UUID id) {
        return balances.getOrDefault(id, 0L);
    }

    public void deposit(UUID id, long amount) {
        if (amount <= 0) return;
        balances.merge(id, amount, (a, b) -> {
            long sum = a + b;
            return sum < 0 ? Long.MAX_VALUE : sum; // overflow guard
        });
        setDirty();
    }

    /** Withdraws if the balance covers it. Returns false (and changes nothing) otherwise. */
    public boolean withdraw(UUID id, long amount) {
        if (amount <= 0) return true;
        long bal = balance(id);
        if (bal < amount) return false;
        balances.put(id, bal - amount);
        setDirty();
        return true;
    }

    private static Bank load(CompoundTag tag, HolderLookup.Provider lookup) {
        Bank b = new Bank();
        CompoundTag accounts = tag.getCompound("Accounts");
        for (String key : accounts.getAllKeys()) {
            try {
                b.balances.put(UUID.fromString(key), accounts.getLong(key));
            } catch (IllegalArgumentException ignored) {
                // skip corrupt keys
            }
        }
        return b;
    }

    @Override
    public CompoundTag save(CompoundTag tag, HolderLookup.Provider lookup) {
        CompoundTag accounts = new CompoundTag();
        balances.forEach((id, bal) -> accounts.putLong(id.toString(), bal));
        tag.put("Accounts", accounts);
        return tag;
    }
}
