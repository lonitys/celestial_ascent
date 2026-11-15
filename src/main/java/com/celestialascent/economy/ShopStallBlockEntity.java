package com.celestialascent.economy;

import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import org.jetbrains.annotations.Nullable;

import java.util.UUID;

/** Player shop: the owner stocks up to 9 stacks; buyers pay coins or bank balance per bundle. */
public class ShopStallBlockEntity extends BlockEntity {
    public static final long MAX_PRICE = 1_000_000_000_000L;

    public final SimpleContainer stock = new SimpleContainer(9) {
        @Override
        public void setChanged() {
            super.setChanged();
            ShopStallBlockEntity.this.changed();
        }
    };
    @Nullable private UUID owner;
    private String ownerName = "";
    private long price = 10;
    private int bundle = 1;

    public ShopStallBlockEntity(BlockPos pos, BlockState state) {
        super(Economy.SHOP_STALL_BE.get(), pos, state);
    }

    /** Rent for an unclaimed stall (trade city stalls start without an owner). */
    public static final long RENT = 100;

    public boolean isOwner(Player p) {
        return owner != null && owner.equals(p.getUUID());
    }

    public boolean hasOwner() {
        return owner != null;
    }

    public void setOwner(Player p) {
        owner = p.getUUID();
        ownerName = p.getGameProfile().getName();
        changed();
    }

    public String ownerName() { return ownerName; }
    public long price() { return price; }
    public int bundle() { return bundle; }

    public void setPrice(long p) {
        price = Math.max(1, Math.min(MAX_PRICE, p));
        changed();
    }

    public void setBundle(int b) {
        bundle = Math.max(1, Math.min(64, b));
        changed();
    }

    /** The item for sale: the first stocked stack (count 1), or empty. */
    public ItemStack template() {
        for (int i = 0; i < stock.getContainerSize(); i++) {
            ItemStack s = stock.getItem(i);
            if (!s.isEmpty()) return s.copyWithCount(1);
        }
        return ItemStack.EMPTY;
    }

    /** Number of stocked items identical to the template. */
    public int stockCount() {
        ItemStack t = template();
        if (t.isEmpty()) return 0;
        int n = 0;
        for (int i = 0; i < stock.getContainerSize(); i++) {
            ItemStack s = stock.getItem(i);
            if (ItemStack.isSameItemSameComponents(s, t)) n += s.getCount();
        }
        return n;
    }

    /** Result of a purchase attempt. */
    public enum Purchase { OK, OWN_SHOP, OUT_OF_STOCK, CANNOT_AFFORD }

    public Purchase buy(ServerPlayer buyer) {
        if (owner != null && owner.equals(buyer.getUUID())) return Purchase.OWN_SHOP;
        ItemStack t = template();
        if (t.isEmpty() || stockCount() < bundle) return Purchase.OUT_OF_STOCK;
        if (!Coins.pay(buyer, price)) return Purchase.CANNOT_AFFORD;
        int left = bundle;
        for (int i = 0; i < stock.getContainerSize() && left > 0; i++) {
            ItemStack s = stock.getItem(i);
            if (ItemStack.isSameItemSameComponents(s, t)) {
                int take = Math.min(left, s.getCount());
                s.shrink(take);
                left -= take;
            }
        }
        stock.setChanged();
        ItemStack bought = t.copyWithCount(bundle);
        if (!buyer.getInventory().add(bought)) buyer.drop(bought, false);
        if (owner != null) {
            Bank.get(buyer.server).deposit(owner, price);
            ServerPlayer o = buyer.server.getPlayerList().getPlayer(owner);
            if (o != null) {
                o.sendSystemMessage(Component.translatable("message.celestialascent.shop_sold",
                        buyer.getDisplayName(), bundle, t.getHoverName(), Coins.format(price)));
            }
        }
        buyer.level().playSound(null, worldPosition, SoundEvents.VILLAGER_YES, SoundSource.BLOCKS, 0.6f, 1.2f);
        return Purchase.OK;
    }

    private void changed() {
        setChanged();
        if (level != null && !level.isClientSide) {
            level.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), 3);
        }
    }

    @Override
    protected void saveAdditional(CompoundTag tag, HolderLookup.Provider lookup) {
        super.saveAdditional(tag, lookup);
        tag.put("Stock", stock.createTag(lookup));
        if (owner != null) tag.putUUID("Owner", owner);
        tag.putString("OwnerName", ownerName);
        tag.putLong("Price", price);
        tag.putInt("Bundle", bundle);
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider lookup) {
        super.loadAdditional(tag, lookup);
        stock.removeAllItems();
        stock.fromTag(tag.getList("Stock", Tag.TAG_COMPOUND), lookup);
        owner = tag.hasUUID("Owner") ? tag.getUUID("Owner") : null;
        ownerName = tag.getString("OwnerName");
        price = Math.max(1, tag.getLong("Price"));
        bundle = Math.max(1, tag.getInt("Bundle"));
    }

    @Override
    public CompoundTag getUpdateTag(HolderLookup.Provider lookup) {
        return saveCustomOnly(lookup);
    }

    @Nullable
    @Override
    public Packet<ClientGamePacketListener> getUpdatePacket() {
        return ClientboundBlockEntityDataPacket.create(this);
    }
}
