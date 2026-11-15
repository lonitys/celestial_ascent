package com.celestialascent.core.station;

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
            }
        };
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
            return;
        }
        be.progress++;
        if (level instanceof ServerLevel sl && be.progress % 5 == 0) {
            sl.sendParticles(ParticleTypes.ENCHANT, pos.getX() + 0.5, pos.getY() + 1.2, pos.getZ() + 0.5, 6, 0.3, 0.3, 0.3, 0.4);
        }
        if (be.progress >= be.type.processTicks) {
            ItemStack result = r.result().apply(be.items.getItem(0).copy());
            be.items.getItem(0).shrink(1);
            for (int i = 0; i < r.mats().size(); i++) be.items.getItem(i + 1).shrink(r.mats().get(i).count());
            be.items.setItem(be.outputSlot(), result);
            be.progress = 0;
            level.playSound(null, pos, SoundEvents.SMITHING_TABLE_USE, SoundSource.BLOCKS, 1f, 0.8f);
            level.playSound(null, pos, SoundEvents.BEACON_POWER_SELECT, SoundSource.BLOCKS, 0.6f, 1.4f);
            if (level instanceof ServerLevel sl) {
                sl.sendParticles(ParticleTypes.END_ROD, pos.getX() + 0.5, pos.getY() + 1.1, pos.getZ() + 0.5, 30, 0.3, 0.4, 0.3, 0.08);
            }
        }
        be.setChanged();
    }

    @Override
    protected void saveAdditional(CompoundTag tag, HolderLookup.Provider lookup) {
        super.saveAdditional(tag, lookup);
        tag.put("Items", items.createTag(lookup));
        tag.putInt("Progress", progress);
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider lookup) {
        super.loadAdditional(tag, lookup);
        items.removeAllItems();
        items.fromTag(tag.getList("Items", Tag.TAG_COMPOUND), lookup);
        progress = tag.getInt("Progress");
    }
}
