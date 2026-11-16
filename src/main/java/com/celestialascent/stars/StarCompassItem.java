package com.celestialascent.stars;

import com.celestialascent.CelestialAscent;
import com.celestialascent.core.Fx;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.TagKey;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.phys.Vec3;

/** Points to the nearest Star Gate when used in the End (direction, distance and a trail of light). */
public class StarCompassItem extends Item {
    public static final TagKey<Structure> STAR_GATE = TagKey.create(Registries.STRUCTURE,
            ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "star_gate"));
    private static final String[] DIRS = {"south", "south_west", "west", "north_west", "north", "north_east", "east", "south_east"};

    public StarCompassItem(Properties props) {
        super(props);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!(level instanceof ServerLevel sl)) return InteractionResultHolder.success(stack);
        if (level.dimension() != Level.END) {
            player.displayClientMessage(Component.translatable("message.celestialascent.compass_spins"), true);
            return InteractionResultHolder.consume(stack);
        }
        BlockPos gate = com.celestialascent.retrogen.Retrogen.findNearest(sl, STAR_GATE, player.blockPosition(), false);
        if (gate == null) {
            player.displayClientMessage(Component.translatable("message.celestialascent.compass_nothing"), true);
            return InteractionResultHolder.consume(stack);
        }
        double dx = gate.getX() - player.getX(), dz = gate.getZ() - player.getZ();
        int dist = (int) Math.sqrt(dx * dx + dz * dz);
        float yaw = (float) Math.toDegrees(Math.atan2(-dx, dz));
        int idx = Math.floorMod(Math.round(yaw / 45f), 8);
        player.displayClientMessage(Component.translatable("message.celestialascent.compass_points",
                Component.translatable("direction.celestialascent." + DIRS[idx]), dist), true);
        Vec3 dir = new Vec3(dx, 0, dz).normalize();
        Vec3 start = player.getEyePosition().add(dir.scale(1.5)).subtract(0, 0.4, 0);
        Fx.line(sl, ParticleTypes.END_ROD, start, start.add(dir.scale(12)), 0.5);
        sl.playSound(null, player.blockPosition(), SoundEvents.AMETHYST_BLOCK_CHIME, player.getSoundSource(), 1f, 1.5f);
        player.getCooldowns().addCooldown(this, 40);
        return InteractionResultHolder.consume(stack);
    }
}
