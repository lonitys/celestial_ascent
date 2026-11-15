package com.celestialascent.boss;

import com.celestialascent.core.CAReg;
import com.celestialascent.core.FacingBlock;
import com.celestialascent.core.Scheduler;
import com.celestialascent.progress.Progress;
import com.mojang.serialization.MapCodec;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.ItemInteractionResult;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.Shapes;
import net.neoforged.neoforge.registries.DeferredHolder;
import org.joml.Vector3f;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;

/**
 * Generic boss altar: offer {@code count} of an item to summon a boss after a short ritual.
 * Optionally requires prior boss kills (progression order) and has a cooldown.
 */
public class SummonAltarBlock extends FacingBlock implements EntityBlock {
    /** Every summon altar, so the shared block entity type can list them. */
    public static final List<Supplier<? extends Block>> ALL = new ArrayList<>();

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<AltarEntity>> BE =
            CAReg.BLOCK_ENTITIES.register("summon_altar", () -> BlockEntityType.Builder.of(AltarEntity::new,
                    ALL.stream().map(Supplier::get).toArray(Block[]::new)).build(null));

    private final Supplier<? extends EntityType<? extends CelestialBoss>> boss;
    private final Supplier<? extends Item> cost;
    private final int count;
    private final List<ResourceLocation> requires;
    private final int color;
    private final int cooldown;

    public SummonAltarBlock(Properties props, Supplier<? extends EntityType<? extends CelestialBoss>> boss, Supplier<? extends Item> cost,
                            int count, List<ResourceLocation> requires, int color, int cooldown) {
        super(props, Shapes.or(Shapes.box(0, 0, 0, 1, 0.25, 1), Shapes.box(0.1875, 0.25, 0.1875, 0.8125, 0.75, 0.8125),
                Shapes.box(0.0625, 0.75, 0.0625, 0.9375, 0.9375, 0.9375)));
        this.boss = boss;
        this.cost = cost;
        this.count = count;
        this.requires = requires;
        this.color = color;
        this.cooldown = cooldown;
    }

    @Override
    protected MapCodec<? extends HorizontalDirectionalBlock> codec() {
        throw new UnsupportedOperationException();
    }

    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new AltarEntity(pos, state);
    }

    @Override
    protected ItemInteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player,
                                              InteractionHand hand, BlockHitResult hit) {
        if (level.isClientSide) return ItemInteractionResult.SUCCESS;
        ServerLevel sl = (ServerLevel) level;
        for (ResourceLocation r : requires) {
            if (!Progress.has(player, r)) {
                player.displayClientMessage(Component.translatable("message.celestialascent.altar_requires",
                        Component.translatable("entity." + r.getNamespace() + "." + r.getPath())).withStyle(ChatFormatting.RED), true);
                return ItemInteractionResult.CONSUME;
            }
        }
        if (!stack.is(cost.get()) || stack.getCount() < count) {
            player.displayClientMessage(Component.translatable("message.celestialascent.altar_offer", count, cost.get().getDescription()), true);
            return ItemInteractionResult.CONSUME;
        }
        if (!(level.getBlockEntity(pos) instanceof AltarEntity be)) return ItemInteractionResult.FAIL;
        if (be.ritual || !level.getEntities(boss.get(), new AABB(pos).inflate(64), e -> e.isAlive()).isEmpty()) {
            player.displayClientMessage(Component.translatable("message.celestialascent.titan_present").withStyle(ChatFormatting.RED), true);
            return ItemInteractionResult.CONSUME;
        }
        long wait = be.last + cooldown - level.getGameTime();
        if (be.last > 0 && wait > 0) {
            player.displayClientMessage(Component.translatable("message.celestialascent.altar_cooldown", wait / 1200 + 1).withStyle(ChatFormatting.GOLD), true);
            return ItemInteractionResult.CONSUME;
        }
        if (!player.getAbilities().instabuild) stack.shrink(count);
        be.last = level.getGameTime();
        be.ritual = true;
        be.setChanged();
        Vec3 c = Vec3.atCenterOf(pos).add(0, 1, 0);
        DustParticleOptions dust = new DustParticleOptions(new Vector3f(((color >> 16) & 255) / 255f, ((color >> 8) & 255) / 255f, (color & 255) / 255f), 2f);
        sl.playSound(null, pos, SoundEvents.END_PORTAL_FRAME_FILL, SoundSource.BLOCKS, 2f, 0.6f);
        for (int t = 0; t < 60; t += 3) {
            int tick = t;
            Scheduler.later(sl, t + 1, () -> {
                double r = 6 - tick / 12.0;
                for (int k = 0; k < 8; k++) {
                    double a = tick * 0.25 + k * Math.PI / 4;
                    sl.sendParticles(dust, c.x + Math.cos(a) * r, c.y + tick / 20.0, c.z + Math.sin(a) * r, 1, 0, 0, 0, 0);
                }
            });
        }
        Vec3 away = c.subtract(player.position()).multiply(1, 0, 1);
        Vec3 dir = away.lengthSqr() < 0.01 ? new Vec3(0, 0, -1) : away.normalize();
        Scheduler.later(sl, 60, () -> {
            be.ritual = false;
            CelestialBoss b = boss.get().create(sl);
            if (b == null) return;
            Vec3 at = c.add(dir.scale(8)).add(0, 1, 0);
            b.moveTo(at.x, at.y, at.z, (float) Math.toDegrees(Math.atan2(-dir.z, -dir.x)) - 90, 0);
            b.setHome(pos);
            sl.addFreshEntity(b);
            sl.sendParticles(ParticleTypes.EXPLOSION_EMITTER, at.x, at.y + 1, at.z, 1, 0, 0, 0, 0);
            sl.playSound(null, pos, SoundEvents.WITHER_SPAWN, SoundSource.HOSTILE, 3f, 0.8f);
            Component msg = Component.translatable("message.celestialascent.titan_awakens", b.getDisplayName()).withColor(color);
            for (Player p : sl.getEntitiesOfClass(Player.class, new AABB(pos).inflate(64))) p.sendSystemMessage(msg);
        });
        return ItemInteractionResult.CONSUME;
    }

    public static class AltarEntity extends BlockEntity {
        long last;
        boolean ritual;

        public AltarEntity(BlockPos pos, BlockState state) {
            super(BE.get(), pos, state);
        }

        @Override
        protected void saveAdditional(CompoundTag tag, HolderLookup.Provider lookup) {
            super.saveAdditional(tag, lookup);
            tag.putLong("Last", last);
        }

        @Override
        protected void loadAdditional(CompoundTag tag, HolderLookup.Provider lookup) {
            super.loadAdditional(tag, lookup);
            last = tag.getLong("Last");
        }
    }
}
