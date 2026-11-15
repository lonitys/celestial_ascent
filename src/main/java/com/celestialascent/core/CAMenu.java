package com.celestialascent.core;

import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ContainerData;
import net.minecraft.world.inventory.MenuType;
import net.minecraft.world.inventory.Slot;
import org.jetbrains.annotations.Nullable;

import java.util.function.LongSupplier;

/** Shared menu helpers: player inventory layout and long values synced over 16-bit data slots. */
public abstract class CAMenu extends AbstractContainerMenu {
    protected CAMenu(@Nullable MenuType<?> type, int id) {
        super(type, id);
    }

    /** Adds the 27 inventory + 9 hotbar slots with the top-left slot at (x, y). Returns first slot index. */
    protected int addPlayerInventory(Inventory inv, int x, int y) {
        int first = slots.size();
        for (int row = 0; row < 3; row++)
            for (int col = 0; col < 9; col++)
                addSlot(new Slot(inv, col + row * 9 + 9, x + col * 18, y + row * 18));
        for (int col = 0; col < 9; col++)
            addSlot(new Slot(inv, col, x + col * 18, y + 58));
        return first;
    }

    /** Server-side data view of a long as four 16-bit chunks. */
    public static ContainerData longData(LongSupplier value) {
        return new ContainerData() {
            @Override
            public int get(int i) {
                return (int) ((value.getAsLong() >>> (16 * i)) & 0xFFFF);
            }

            @Override
            public void set(int i, int v) {}

            @Override
            public int getCount() {
                return 4;
            }
        };
    }

    /** Reassembles a long from four chunks starting at {@code offset}. */
    public static long readLong(ContainerData data, int offset) {
        long v = 0;
        for (int i = 0; i < 4; i++) v |= ((long) (data.get(offset + i) & 0xFFFF)) << (16 * i);
        return v;
    }
}
