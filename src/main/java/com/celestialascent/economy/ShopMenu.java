package com.celestialascent.economy;

import com.celestialascent.core.CAMenu;
import net.minecraft.core.BlockPos;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.Container;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.ContainerData;
import net.minecraft.world.inventory.SimpleContainerData;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;
import org.jetbrains.annotations.Nullable;

/**
 * Shop stall menu. Owners see 9 stock slots and price controls; buyers see the offer and a Buy button.
 * Data: [0..3] price, [4] bundle, [5] stock count.
 * Buttons: 0..7 price deltas, 8/9 bundle -/+, 10/11 price x10 / /10, 20 buy.
 */
public class ShopMenu extends CAMenu {
    public static final long[] PRICE_DELTAS = {-1000, -100, -10, -1, 1, 10, 100, 1000};
    public static final int BUY = 20;

    public final boolean owner;
    @Nullable private final ShopStallBlockEntity be;
    private final ContainerData data;
    private final Container display;

    /** Client constructor. */
    public static ShopMenu client(int id, Inventory inv, RegistryFriendlyByteBuf buf) {
        buf.readBlockPos();
        boolean owner = buf.readBoolean();
        return new ShopMenu(id, inv, null, owner, owner ? new SimpleContainer(9) : new SimpleContainer(1), new SimpleContainerData(6));
    }

    /** Server constructor. */
    public static ShopMenu server(int id, Inventory inv, ShopStallBlockEntity be, boolean owner) {
        ContainerData d = new ContainerData() {
            final ContainerData price = longData(be::price);

            @Override
            public int get(int i) {
                return i < 4 ? price.get(i) : i == 4 ? be.bundle() : Math.min(be.stockCount(), 32767);
            }

            @Override
            public void set(int i, int v) {}

            @Override
            public int getCount() {
                return 6;
            }
        };
        return new ShopMenu(id, inv, be, owner, owner ? be.stock : new SimpleContainer(1), d);
    }

    private ShopMenu(int id, Inventory inv, @Nullable ShopStallBlockEntity be, boolean owner, Container container, ContainerData data) {
        super(Economy.SHOP_MENU.get(), id);
        this.owner = owner;
        this.be = be;
        this.data = data;
        this.display = container;
        if (owner) {
            for (int r = 0; r < 3; r++)
                for (int c = 0; c < 3; c++)
                    addSlot(new Slot(container, c + r * 3, 8 + c * 18, 22 + r * 18));
        } else {
            addSlot(new Slot(container, 0, 26, 40) {
                @Override public boolean mayPickup(Player p) { return false; }
                @Override public boolean mayPlace(ItemStack s) { return false; }
            });
        }
        addPlayerInventory(inv, 8, 122);
        addDataSlots(data);
        refreshDisplay();
    }

    private void refreshDisplay() {
        if (!owner && be != null) {
            ItemStack t = be.template();
            display.setItem(0, t.isEmpty() ? ItemStack.EMPTY : t.copyWithCount(be.bundle()));
        }
    }

    @Override
    public void broadcastChanges() {
        refreshDisplay();
        super.broadcastChanges();
    }

    public long price() { return readLong(data, 0); }
    public int bundle() { return data.get(4); }
    public int stock() { return data.get(5); }

    @Override
    public boolean clickMenuButton(Player player, int id) {
        if (be == null || !(player instanceof ServerPlayer sp)) return false;
        if (id == BUY && !owner) {
            ShopStallBlockEntity.Purchase r = be.buy(sp);
            if (r != ShopStallBlockEntity.Purchase.OK) {
                sp.displayClientMessage(Component.translatable("message.celestialascent.shop_" + r.name().toLowerCase()), true);
            }
            return true;
        }
        if (!owner || !be.isOwner(sp)) return false;
        if (id >= 0 && id < PRICE_DELTAS.length) be.setPrice(be.price() + PRICE_DELTAS[id]);
        else if (id == 8) be.setBundle(be.bundle() - 1);
        else if (id == 9) be.setBundle(be.bundle() + 1);
        else if (id == 10) be.setPrice(be.price() * 10);
        else if (id == 11) be.setPrice(be.price() / 10);
        else return false;
        return true;
    }

    @Override
    public ItemStack quickMoveStack(Player player, int index) {
        if (!owner) return ItemStack.EMPTY;
        Slot slot = slots.get(index);
        if (!slot.hasItem()) return ItemStack.EMPTY;
        ItemStack stack = slot.getItem();
        ItemStack copy = stack.copy();
        if (index < 9) {
            if (!moveItemStackTo(stack, 9, slots.size(), true)) return ItemStack.EMPTY;
        } else if (!moveItemStackTo(stack, 0, 9, false)) {
            return ItemStack.EMPTY;
        }
        if (stack.isEmpty()) slot.setByPlayer(ItemStack.EMPTY);
        else slot.setChanged();
        return copy;
    }

    @Override
    public boolean stillValid(Player player) {
        if (be == null) return true;
        BlockPos p = be.getBlockPos();
        return !be.isRemoved() && player.distanceToSqr(p.getX() + 0.5, p.getY() + 0.5, p.getZ() + 0.5) <= 64;
    }
}
