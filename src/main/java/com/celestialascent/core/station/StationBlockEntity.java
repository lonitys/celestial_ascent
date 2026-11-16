package com.celestialascent.core.station;

import net.minecraft.core.NonNullList;
import net.minecraft.nbt.ListTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.world.ContainerHelper;
import net.minecraft.world.level.block.Block;

import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.inventory.ContainerData;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;

import java.util.ArrayList;
import java.util.List;

/** Shared block entity for all upgrade stations. Slot 0 = base, 1..n = materials, last = output. */
public class StationBlockEntity extends BlockEntity {
    public final StationType type;
    public final SimpleContainer items;
    private int progress;
    private boolean conditionOk = true;

    public final ContainerData data = new ContainerData() {
        @Override
        public int get(int i) {
            return switch (i) {
                case 0 -> progress;
                case 1 -> type.processTicks;
                default -> conditionOk ? 1 : 0;
            };
        }

        @Override
        public void set(int i, int v) {}

        @Override
        public int getCount() {
            return 3;
        }
    };

    public StationBlockEntity(BlockPos pos, BlockState state) {
        super(Stations.BE.get(), pos, state);
        this.type = ((StationBlock) state.getBlock()).type();
        this.items = new SimpleContainer(type.size()) {
            @Override
            public void setChanged() {
                super.setChanged();
                StationBlockEntity.this.setChanged();
                syncToClients(); // the renderer shows the item floating above the station
            }
        };
    }

    /** Client copy: whether the station is working (the floating item spins faster). */
    private boolean active;
    private boolean sentActive;
    private boolean loading;

    public boolean active() {
        return active;
    }

    private void syncToClients() {
        if (!loading && level != null && !level.isClientSide) level.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), Block.UPDATE_CLIENTS);
    }

    /** Writes the slots with their slot numbers (a plain SimpleContainer tag would shift items between slots on reload). */
    private void saveItems(CompoundTag tag, HolderLookup.Provider lookup) {
        NonNullList<ItemStack> list = NonNullList.withSize(items.getContainerSize(), ItemStack.EMPTY);
        for (int i = 0; i < list.size(); i++) list.set(i, items.getItem(i));
        ContainerHelper.saveAllItems(tag, list, true, lookup);
    }

    private void loadItems(CompoundTag tag, HolderLookup.Provider lookup) {
        loading = true;
        try {
            ListTag stored = tag.getList("Items", Tag.TAG_COMPOUND);
            items.removeAllItems();
            if (!stored.isEmpty() && !stored.getCompound(0).contains("Slot")) {
                items.fromTag(stored, lookup); // saves from before slot numbers were written
                return;
            }
            NonNullList<ItemStack> list = NonNullList.withSize(items.getContainerSize(), ItemStack.EMPTY);
            ContainerHelper.loadAllItems(tag, list, lookup);
            for (int i = 0; i < list.size(); i++) items.setItem(i, list.get(i));
        } finally {
            loading = false;
        }
    }

    @Override
    public CompoundTag getUpdateTag(HolderLookup.Provider lookup) {
        CompoundTag tag = new CompoundTag();
        saveItems(tag, lookup);
        tag.putBoolean("Active", progress > 0);
        return tag;
    }

    @Override
    public Packet<ClientGamePacketListener> getUpdatePacket() {
        return ClientboundBlockEntityDataPacket.create(this);
    }

    public int outputSlot() {
        return type.size() - 1;
    }

    private List<ItemStack> mats() {
        List<ItemStack> out = new ArrayList<>();
        for (int i = 1; i <= type.mats.length; i++) out.add(items.getItem(i));
        return out;
    }

    public static void serverTick(Level level, BlockPos pos, BlockState state, StationBlockEntity be) {
        be.conditionOk = be.type.conditionMet(level, pos);
        StationRecipe r = be.type.find(be.items.getItem(0), be.mats());
        if (r == null || !be.items.getItem(be.outputSlot()).isEmpty() || !be.conditionOk) {
            if (be.progress != 0) {
                be.progress = 0;
                be.setChanged();
            }
            if (be.sentActive) {
                be.sentActive = false;
                be.syncToClients();
            }
            return;
        }
        be.progress++;
        if (level instanceof ServerLevel sl && be.progress % 5 == 0) {
            sl.sendParticles(ParticleTypes.ENCHANT, pos.getX() + 0.5, pos.getY() + 1.2, pos.getZ() + 0.5, 6, 0.3, 0.3, 0.3, 0.4);
        }
        if (be.progress >= be.type.processTicks) {
            ItemStack result = r.result().apply(be.items.getItem(0).copy());
            boolean evolved = com.celestialascent.armor.ArmorStages.stage(result) > com.celestialascent.armor.ArmorStages.stage(be.items.getItem(0))
                    && result.is(be.items.getItem(0).getItem());
            be.items.getItem(0).shrink(1);
            for (int i = 0; i < r.mats().size(); i++) be.items.getItem(i + 1).shrink(r.mats().get(i).count());
            be.items.setItem(be.outputSlot(), result);
            be.progress = 0;
            level.playSound(null, pos, SoundEvents.SMITHING_TABLE_USE, SoundSource.BLOCKS, 1f, 0.8f);
            level.playSound(null, pos, SoundEvents.BEACON_POWER_SELECT, SoundSource.BLOCKS, 0.6f, 1.4f);
            if (level instanceof ServerLevel sl) {
                sl.sendParticles(ParticleTypes.END_ROD, pos.getX() + 0.5, pos.getY() + 1.1, pos.getZ() + 0.5, 30, 0.3, 0.4, 0.3, 0.08);
                if (evolved) {
                    sl.sendParticles(ParticleTypes.TOTEM_OF_UNDYING, pos.getX() + 0.5, pos.getY() + 1.4, pos.getZ() + 0.5, 60, 0.4, 0.6, 0.4, 0.4);
                    level.playSound(null, pos, SoundEvents.UI_TOAST_CHALLENGE_COMPLETE, SoundSource.BLOCKS, 1f, 1f);
                    int newStage = com.celestialascent.armor.ArmorStages.stage(result);
                    var msg = net.minecraft.network.chat.Component.translatable("message.celestialascent.evolved", result.getHoverName(), newStage == 2 ? "II" : "III")
                            .withStyle(net.minecraft.ChatFormatting.LIGHT_PURPLE);
                    for (var p : sl.getEntitiesOfClass(net.minecraft.server.level.ServerPlayer.class, new net.minecraft.world.phys.AABB(pos).inflate(8))) p.sendSystemMessage(msg);
                }
            }
        }
        be.setChanged();
        if (be.sentActive != be.progress > 0) {
            be.sentActive = be.progress > 0;
            be.syncToClients();
        }
    }

    @Override
    protected void saveAdditional(CompoundTag tag, HolderLookup.Provider lookup) {
        super.saveAdditional(tag, lookup);
        saveItems(tag, lookup);
        tag.putInt("Progress", progress);
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider lookup) {
        super.loadAdditional(tag, lookup);
        loadItems(tag, lookup);
        progress = tag.getInt("Progress");
        active = tag.getBoolean("Active");
    }
}
