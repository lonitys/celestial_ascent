package com.celestialascent.economy;

import com.celestialascent.core.CAMenu;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.ContainerData;
import net.minecraft.world.inventory.ContainerLevelAccess;
import net.minecraft.world.inventory.SimpleContainerData;
import net.minecraft.world.item.ItemStack;

/**
 * Bank screen. Buttons: 0 = deposit all carried coins; 10+tier = withdraw one coin of that tier;
 * 20+tier = withdraw ten.
 */
public class BankMenu extends CAMenu {
    public static final int DEPOSIT_ALL = 0;
    public static final int WITHDRAW_ONE = 10;
    public static final int WITHDRAW_TEN = 20;

    private final ContainerLevelAccess access;
    private final ContainerData data;

    /** Client constructor. */
    public BankMenu(int id, Inventory inv) {
        this(id, inv, ContainerLevelAccess.NULL, new SimpleContainerData(4));
    }

    /** Server constructor. */
    public BankMenu(int id, Inventory inv, ContainerLevelAccess access) {
        this(id, inv, access, longData(() -> inv.player instanceof ServerPlayer sp ? Bank.get(sp.server).balance(sp.getUUID()) : 0));
    }

    private BankMenu(int id, Inventory inv, ContainerLevelAccess access, ContainerData data) {
        super(Economy.BANK_MENU.get(), id);
        this.access = access;
        this.data = data;
        addPlayerInventory(inv, 8, 104);
        addDataSlots(data);
    }

    public long balance() {
        return readLong(data, 0);
    }

    @Override
    public boolean clickMenuButton(Player player, int id) {
        if (!(player instanceof ServerPlayer sp)) return false;
        Bank bank = Bank.get(sp.server);
        if (id == DEPOSIT_ALL) {
            long v = Coins.takeAll(sp);
            if (v <= 0) return false;
            bank.deposit(sp.getUUID(), v);
            sp.level().playSound(null, sp.blockPosition(), SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.PLAYERS, 1f, 1.4f);
            return true;
        }
        int tierIdx = id >= WITHDRAW_TEN ? id - WITHDRAW_TEN : id - WITHDRAW_ONE;
        int count = id >= WITHDRAW_TEN ? 10 : 1;
        if (tierIdx < 0 || tierIdx >= CoinTier.values().length) return false;
        CoinTier tier = CoinTier.values()[tierIdx];
        if (!bank.withdraw(sp.getUUID(), tier.value * count)) return false;
        ItemStack coins = new ItemStack(Economy.coin(tier), count);
        if (!sp.getInventory().add(coins)) sp.drop(coins, false);
        sp.level().playSound(null, sp.blockPosition(), SoundEvents.CHAIN_PLACE, SoundSource.PLAYERS, 0.8f, 1.6f);
        return true;
    }

    @Override
    public ItemStack quickMoveStack(Player player, int index) {
        return ItemStack.EMPTY;
    }

    @Override
    public boolean stillValid(Player player) {
        return stillValid(access, player, Economy.BANK_COUNTER.get());
    }
}
