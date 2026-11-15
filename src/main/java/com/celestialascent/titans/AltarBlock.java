package com.celestialascent.titans;

import com.celestialascent.core.FacingBlock;
import com.celestialascent.core.Scheduler;
import com.mojang.serialization.MapCodec;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.ItemInteractionResult;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jetbrains.annotations.Nullable;
import org.joml.Vector3f;

/** Shrine altar: use the matching Elemental Sigil to begin a ritual that summons the titan. */
public class AltarBlock extends FacingBlock implements EntityBlock {
    public static final int COOLDOWN_TICKS = 12000;
    public static final int RITUAL_TICKS = 60;
    private static final VoxelShape SHAPE = Shapes.or(
            Shapes.box(0, 0, 0, 1, 0.25, 1),
            Shapes.box(0.1875, 0.25, 0.1875, 0.8125, 0.75, 0.8125),
            Shapes.box(0.0625, 0.75, 0.0625, 0.9375, 0.9375, 0.9375));

    public final Element element;

    public AltarBlock(Element element, Properties props) {
        super(props, SHAPE);
        this.element = element;
    }

    @Override
    protected MapCodec<? extends HorizontalDirectionalBlock> codec() {
        throw new UnsupportedOperationException();
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new AltarBlockEntity(pos, state);
    }

    @Override
    protected ItemInteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player,
                                              InteractionHand hand, BlockHitResult hit) {
        if (!(stack.getItem() instanceof SigilItem sigil)) return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
        if (level.isClientSide) return ItemInteractionResult.SUCCESS;
        ServerLevel sl = (ServerLevel) level;
        if (sigil.element != element) {
            player.displayClientMessage(Component.translatable("message.celestialascent.wrong_sigil").withStyle(ChatFormatting.RED), true);
            return ItemInteractionResult.CONSUME;
        }
        if (!(level.getBlockEntity(pos) instanceof AltarBlockEntity be)) return ItemInteractionResult.FAIL;
        EntityType<? extends TitanBoss> type = Titans.titanType(element);
        boolean alive = !level.getEntities(type, new AABB(pos).inflate(64), e -> e.isAlive()).isEmpty();
        if (alive || be.ritualActive) {
            player.displayClientMessage(Component.translatable("message.celestialascent.titan_present").withStyle(ChatFormatting.RED), true);
            return ItemInteractionResult.CONSUME;
        }
        long wait = be.lastSummon + COOLDOWN_TICKS - level.getGameTime();
        if (be.lastSummon > 0 && wait > 0) {
            player.displayClientMessage(Component.translatable("message.celestialascent.altar_cooldown", wait / 1200 + 1).withStyle(ChatFormatting.GOLD), true);
            return ItemInteractionResult.CONSUME;
        }
        if (!player.getAbilities().instabuild) stack.shrink(1);
        be.lastSummon = level.getGameTime();
        be.ritualActive = true;
        be.setChanged();
        Vec3 away = Vec3.atCenterOf(pos).subtract(player.position()).multiply(1, 0, 1);
        Vec3 dir = away.lengthSqr() < 0.01 ? new Vec3(0, 0, -1) : away.normalize();
        startRitual(sl, pos, dir, be);
        return ItemInteractionResult.CONSUME;
    }

    private void startRitual(ServerLevel sl, BlockPos pos, Vec3 dir, AltarBlockEntity be) {
        Vec3 c = Vec3.atCenterOf(pos).add(0, 1.2, 0);
        DustParticleOptions dust = new DustParticleOptions(new Vector3f(
                ((element.color >> 16) & 0xFF) / 255f, ((element.color >> 8) & 0xFF) / 255f, (element.color & 0xFF) / 255f), 2.0f);
        sl.playSound(null, pos, SoundEvents.END_PORTAL_FRAME_FILL, SoundSource.BLOCKS, 2f, 0.6f);
        for (int t = 0; t < RITUAL_TICKS; t += 3) {
            int tick = t;
            Scheduler.later(sl, t + 1, () -> {
                double r = 6 - tick / 12.0;
                for (int k = 0; k < 8; k++) {
                    double a = tick * 0.25 + k * Math.PI / 4;
                    sl.sendParticles(dust, c.x + Math.cos(a) * r, c.y + tick / 20.0, c.z + Math.sin(a) * r, 1, 0, 0, 0, 0);
                }
                if (tick % 15 == 0) sl.playSound(null, pos, SoundEvents.BEACON_AMBIENT, SoundSource.BLOCKS, 2f, 0.5f + tick / 60f);
            });
        }
        Scheduler.later(sl, RITUAL_TICKS, () -> {
            be.ritualActive = false;
            be.setChanged();
            TitanBoss titan = Titans.titanType(element).create(sl);
            if (titan == null) return;
            Vec3 spawn = c.add(dir.scale(7));
            BlockPos ground = BlockPos.containing(spawn.x, pos.getY() + 4, spawn.z);
            while (ground.getY() > pos.getY() - 6 && !sl.getBlockState(ground.below()).isSolid()) ground = ground.below();
            titan.moveTo(spawn.x, ground.getY(), spawn.z, (float) (Math.toDegrees(Math.atan2(-dir.z, -dir.x)) - 90), 0);
            titan.setHome(pos);
            sl.addFreshEntity(titan);
            sl.sendParticles(ParticleTypes.EXPLOSION_EMITTER, spawn.x, ground.getY() + 2, spawn.z, 1, 0, 0, 0, 0);
            sl.playSound(null, pos, SoundEvents.WITHER_SPAWN, SoundSource.HOSTILE, 3f, 0.7f);
            Component msg = Component.translatable("message.celestialascent.titan_awakens",
                    Component.translatable("entity.celestialascent." + element.key + "_titan")).withColor(element.color);
            for (var p : sl.getEntitiesOfClass(Player.class, new AABB(pos).inflate(64))) p.sendSystemMessage(msg);
        });
    }

    /** Remembers the last summon time so each altar has a cooldown. */
    public static class AltarBlockEntity extends BlockEntity {
        long lastSummon;
        boolean ritualActive;

        public AltarBlockEntity(BlockPos pos, BlockState state) {
            super(Titans.ALTAR_BE.get(), pos, state);
        }

        @Override
        protected void saveAdditional(CompoundTag tag, HolderLookup.Provider lookup) {
            super.saveAdditional(tag, lookup);
            tag.putLong("LastSummon", lastSummon);
        }

        @Override
        protected void loadAdditional(CompoundTag tag, HolderLookup.Provider lookup) {
            super.loadAdditional(tag, lookup);
            lastSummon = tag.getLong("LastSummon");
        }
    }
}
