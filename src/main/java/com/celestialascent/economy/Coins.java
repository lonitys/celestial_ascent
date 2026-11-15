package com.celestialascent.economy;

import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;

import java.util.ArrayList;
import java.util.List;

/** Coin value math and inventory payment helpers. */
public final class Coins {
    private Coins() {}

    /** Value of one item of this stack (0 if not a coin). */
    public static long unitValue(ItemStack stack) {
        return stack.getItem() instanceof CoinItem c ? c.tier.value : 0;
    }

    /** Total value of this stack. */
    public static long valueOf(ItemStack stack) {
        return unitValue(stack) * stack.getCount();
    }

    /** Splits an amount into the fewest coin stacks (greedy, largest tier first). */
    public static List<ItemStack> breakdown(long amount) {
        List<ItemStack> out = new ArrayList<>();
        CoinTier[] tiers = CoinTier.values();
        for (int i = tiers.length - 1; i >= 0 && amount > 0; i--) {
            long n = amount / tiers[i].value;
            amount -= n * tiers[i].value;
            while (n > 0) {
                int c = (int) Math.min(n, 64);
                out.add(new ItemStack(Economy.coin(tiers[i]), c));
                n -= c;
            }
        }
        return out;
    }

    /** Value of all coins in the player's inventory. */
    public static long countInventory(Player p) {
        long total = 0;
        Inventory inv = p.getInventory();
        for (int i = 0; i < inv.getContainerSize(); i++) total += valueOf(inv.getItem(i));
        return total;
    }

    /** Removes every coin from the inventory and returns their total value. */
    public static long takeAll(Player p) {
        long total = 0;
        Inventory inv = p.getInventory();
        for (int i = 0; i < inv.getContainerSize(); i++) {
            ItemStack s = inv.getItem(i);
            long v = valueOf(s);
            if (v > 0) {
                total += v;
                inv.setItem(i, ItemStack.EMPTY);
            }
        }
        return total;
    }

    /** Gives coins worth {@code amount}; anything that does not fit is dropped at the player's feet. */
    public static void give(Player p, long amount) {
        for (ItemStack s : breakdown(amount)) {
            if (!p.getInventory().add(s)) p.drop(s, false);
        }
    }

    /** Removes coins worth exactly {@code amount} from the inventory (making change). False if not enough. */
    public static boolean removeFromInventory(Player p, long amount) {
        if (amount <= 0) return true;
        if (countInventory(p) < amount) return false;
        long total = takeAll(p);
        give(p, total - amount);
        return true;
    }

    /** Pays with carried coins first, then the bank balance. False (and nothing taken) if short. */
    public static boolean pay(Player p, long amount) {
        if (amount <= 0) return true;
        if (countInventory(p) >= amount) return removeFromInventory(p, amount);
        if (p instanceof ServerPlayer sp) {
            Bank bank = Bank.get(sp.server);
            if (bank.balance(sp.getUUID()) >= amount) return bank.withdraw(sp.getUUID(), amount);
        }
        return false;
    }

    /** Human-readable amount, e.g. "1,250 ✦". */
    public static String format(long amount) {
        return String.format("%,d ✦", amount);
    }
}
