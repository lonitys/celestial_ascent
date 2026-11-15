package com.celestialascent.abyss;

import com.celestialascent.core.Scheduler;
import com.celestialascent.core.Travel;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/** Abyss utility items. */
public final class AbyssItems {
    private AbyssItems() {}

    /** Used deep in the Abyss (below y=40) to call the Void Sovereign. */
    public static class AbyssalBeacon extends Item {
        public AbyssalBeacon(Properties p) {
            super(p);
        }

        @Override
        public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
            ItemStack stack = player.getItemInHand(hand);
            if (!(level instanceof ServerLevel sl)) return InteractionResultHolder.success(stack);
            if (level.dimension() != Travel.ABYSS || player.getY() > 40) {
                player.displayClientMessage(Component.translatable("message.celestialascent.beacon_deeper").withStyle(ChatFormatting.LIGHT_PURPLE), true);
                return InteractionResultHolder.fail(stack);
            }
            if (!level.getEntitiesOfClass(VoidSovereign.class, new AABB(player.blockPosition()).inflate(96)).isEmpty()) {
                player.displayClientMessage(Component.translatable("message.celestialascent.titan_present").withStyle(ChatFormatting.RED), true);
                return InteractionResultHolder.fail(stack);
            }
            if (!player.getAbilities().instabuild) stack.shrink(1);
            Vec3 look = player.getLookAngle().multiply(1, 0, 1).normalize();
            Vec3 at = player.position().add(look.scale(9));
            sl.playSound(null, player.blockPosition(), SoundEvents.WARDEN_EMERGE, SoundSource.HOSTILE, 3f, 0.5f);
            for (int t = 0; t < 80; t += 4) {
                int tick = t;
                Scheduler.later(sl, t + 1, () -> sl.sendParticles(ParticleTypes.REVERSE_PORTAL, at.x, at.y + tick / 20.0, at.z, 40, 1.5, 1, 1.5, 0.1));
            }
            Scheduler.later(sl, 80, () -> {
                VoidSovereign boss = Abyss.VOID_SOVEREIGN.get().create(sl);
                if (boss == null) return;
                BlockPos g = BlockPos.containing(at);
                while (g.getY() > sl.getMinBuildHeight() + 6 && !sl.getBlockState(g.below()).isSolid()) g = g.below();
                boss.moveTo(at.x, g.getY(), at.z, player.getYRot() + 180, 0);
                boss.setHome(g);
                sl.addFreshEntity(boss);
                sl.sendParticles(ParticleTypes.EXPLOSION_EMITTER, at.x, g.getY() + 2, at.z, 2, 1, 1, 1, 0);
                sl.playSound(null, g, SoundEvents.WITHER_SPAWN, SoundSource.HOSTILE, 4f, 0.4f);
                Component msg = Component.translatable("message.celestialascent.sovereign_awakens").withColor(0xB45CFF);
                for (Player p : sl.getEntitiesOfClass(Player.class, new AABB(g).inflate(96))) p.sendSystemMessage(msg);
            });
            return InteractionResultHolder.consume(stack);
        }
    }

    /** Returns the user to their respawn point from any dimension. */
    public static class AscensionPearl extends Item {
        public AscensionPearl(Properties p) {
            super(p);
        }

        @Override
        public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
            ItemStack stack = player.getItemInHand(hand);
            if (!(player instanceof ServerPlayer sp)) return InteractionResultHolder.success(stack);
            ServerLevel dest = sp.server.getLevel(sp.getRespawnDimension());
            BlockPos pos = sp.getRespawnPosition();
            if (dest == null || pos == null) {
                dest = sp.server.overworld();
                pos = dest.getSharedSpawnPos();
            }
            BlockPos top = Travel.surface(dest, pos.getX(), pos.getZ());
            BlockPos stand = sp.getRespawnPosition() != null ? pos.above() : (top == null ? pos : top);
            sp.serverLevel().sendParticles(ParticleTypes.REVERSE_PORTAL, sp.getX(), sp.getY() + 1, sp.getZ(), 60, 0.5, 1, 0.5, 0.2);
            Travel.teleport(sp, dest, Vec3.atBottomCenterOf(stand));
            dest.playSound(null, stand, SoundEvents.ENDERMAN_TELEPORT, SoundSource.PLAYERS, 1f, 0.8f);
            if (!sp.getAbilities().instabuild) stack.shrink(1);
            sp.getCooldowns().addCooldown(this, 100);
            return InteractionResultHolder.consume(stack);
        }
    }
}
