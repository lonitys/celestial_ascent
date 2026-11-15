package com.celestialascent.core.station;

import com.celestialascent.core.CAMenu;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.world.Container;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.ContainerData;
import net.minecraft.world.inventory.SimpleContainerData;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;
import org.jetbrains.annotations.Nullable;

public class StationMenu extends CAMenu {
    public final StationType type;
    @Nullable private final StationBlockEntity be;
    private final ContainerData data;
    private final int outputIndex;

    public static StationMenu client(int id, Inventory inv, RegistryFriendlyByteBuf buf) {
        StationType type = StationType.byId(buf.readUtf());
        return new StationMenu(id, inv, type, null, new SimpleContainer(type.size()), new SimpleContainerData(3));
    }

    public StationMenu(int id, Inventory inv, StationBlockEntity be) {
        this(id, inv, be.type, be, be.items, be.data);
    }

    private StationMenu(int id, Inventory inv, StationType type, @Nullable StationBlockEntity be, Container c, ContainerData data) {
        super(Stations.MENU.get(), id);
        this.type = type;
        this.be = be;
        this.data = data;
        addSlot(new Slot(c, 0, type.base[0], type.base[1]));
        for (int i = 0; i < type.mats.length; i++) addSlot(new Slot(c, i + 1, type.mats[i][0], type.mats[i][1]));
        outputIndex = slots.size();
        addSlot(new Slot(c, type.size() - 1, type.output[0], type.output[1]) {
            @Override
            public boolean mayPlace(ItemStack s) {
                return false;
            }
        });
        addPlayerInventory(inv, 8, 84);
        addDataSlots(data);
    }

    public float progress() {
        int max = data.get(1);
        return max <= 0 ? 0 : data.get(0) / (float) max;
    }

    public boolean conditionOk() {
        return data.get(2) == 1;
    }

    @Override
    public ItemStack quickMoveStack(Player player, int index) {
        Slot slot = slots.get(index);
        if (!slot.hasItem()) return ItemStack.EMPTY;
        ItemStack stack = slot.getItem();
        ItemStack copy = stack.copy();
        int stationSlots = outputIndex + 1;
        if (index < stationSlots) {
            if (!moveItemStackTo(stack, stationSlots, slots.size(), true)) return ItemStack.EMPTY;
        } else if (!moveItemStackTo(stack, 0, outputIndex, false)) {
            return ItemStack.EMPTY;
        }
        if (stack.isEmpty()) slot.setByPlayer(ItemStack.EMPTY);
        else slot.setChanged();
        return copy;
    }

    @Override
    public boolean stillValid(Player player) {
        if (be == null) return true;
        return !be.isRemoved() && player.distanceToSqr(be.getBlockPos().getCenter()) <= 64;
    }
}
