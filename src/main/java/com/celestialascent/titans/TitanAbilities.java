package com.celestialascent.titans;

import com.celestialascent.CelestialAscent;
import com.celestialascent.armor.ArmorAbility;
import com.celestialascent.armor.ArmorSets;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.core.Holder;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.neoforge.common.NeoForgeMod;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;

import java.util.EnumMap;
import java.util.Map;

/**
 * Elemental abilities of a full Titan set. Each element counts how many pieces carry it:
 * one piece = level I, two or more = level II.
 */
public class TitanAbilities implements ArmorAbility {
    static final ResourceLocation SPEED = ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "titan_storm_speed");
    static final ResourceLocation SWIM = ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "titan_tide_swim");

    /** Element levels for the worn set (overridden by Ascendant armor to grant all at II). */
    public Map<Element, Integer> levels(ServerPlayer p) {
        Map<Element, Integer> out = new EnumMap<>(Element.class);
        for (ItemStack s : ArmorSets.pieces(p)) {
            Element e = TitanArmorItem.element(s);
            if (e != null) out.merge(e, 1, Integer::sum);
        }
        out.replaceAll((e, n) -> Math.min(2, n));
        return out;
    }

    private static int lvl(Map<Element, Integer> m, Element e) {
        return m.getOrDefault(e, 0);
    }

    private static void keep(ServerPlayer p, Holder<MobEffect> effect, int amp) {
        MobEffectInstance cur = p.getEffect(effect);
        if (cur == null || cur.getDuration() < 220) p.addEffect(new MobEffectInstance(effect, 400, amp, true, false, true));
    }

    private static void modifier(ServerPlayer p, Holder<net.minecraft.world.entity.ai.attributes.Attribute> attr, ResourceLocation id, double amount) {
        AttributeInstance inst = p.getAttribute(attr);
        if (inst == null) return;
        if (amount == 0) inst.removeModifier(id);
        else inst.addOrUpdateTransientModifier(new AttributeModifier(id, amount, AttributeModifier.Operation.ADD_MULTIPLIED_BASE));
    }

    @Override
    public void tick(ServerPlayer p) {
        Map<Element, Integer> L = levels(p);
        int frost = lvl(L, Element.FROST), tide = lvl(L, Element.TIDE), storm = lvl(L, Element.STORM), magma = lvl(L, Element.MAGMA);

        if (frost > 0) {
            p.setTicksFrozen(0);
            if (p.onGround()) replaceDisk(p, 1 + frost, Blocks.WATER.defaultBlockState(), Blocks.FROSTED_ICE.defaultBlockState(), true);
        }
        if (tide > 0) {
            keep(p, MobEffects.WATER_BREATHING, 0);
            if (tide >= 2 && p.isInWater()) keep(p, MobEffects.DOLPHINS_GRACE, 0);
            if (tide >= 2 && p.isEyeInFluid(FluidTags.WATER)) keep(p, MobEffects.NIGHT_VISION, 0);
        }
        modifier(p, NeoForgeMod.SWIM_SPEED, SWIM, tide * 0.35);
        modifier(p, Attributes.MOVEMENT_SPEED, SPEED, storm * 0.10);
        if (magma > 0) {
            keep(p, MobEffects.FIRE_RESISTANCE, 0);
            p.clearFire();
            if (magma >= 2 && (p.onGround() || p.isInLava())) {
                replaceDisk(p, 2, Blocks.LAVA.defaultBlockState(), Titans.COOLED_MAGMA.get().defaultBlockState(), false);
            }
        }
    }

    /** Replaces source fluid blocks in a disk under the player's feet (frost walker style). */
    private static void replaceDisk(ServerPlayer p, int radius, BlockState from, BlockState to, boolean melts) {
        ServerLevel level = p.serverLevel();
        BlockPos feet = p.blockPosition();
        BlockPos.MutableBlockPos m = new BlockPos.MutableBlockPos();
        for (BlockPos pos : BlockPos.betweenClosed(feet.offset(-radius, -1, -radius), feet.offset(radius, -1, radius))) {
            if (pos.distToCenterSqr(p.getX(), pos.getY() + 0.5, p.getZ()) > radius * radius) continue;
            m.set(pos.getX(), pos.getY() + 1, pos.getZ());
            BlockState state = level.getBlockState(pos);
            if (state == from && level.getBlockState(m).isAir()) {
                level.setBlockAndUpdate(pos, to);
                level.scheduleTick(pos, to.getBlock(), melts ? Mth.nextInt(p.getRandom(), 60, 120) : Mth.nextInt(p.getRandom(), 80, 140));
            }
        }
    }

    @Override
    public void onHurt(ServerPlayer p, LivingIncomingDamageEvent e) {
        Map<Element, Integer> L = levels(p);
        DamageSource src = e.getSource();
        if (lvl(L, Element.FROST) > 0 && src.is(DamageTypes.FREEZE)) {
            e.setCanceled(true);
            return;
        }
        if (!(src.getEntity() instanceof LivingEntity attacker) || src.getDirectEntity() != attacker || attacker == p) return;
        int frost = lvl(L, Element.FROST), storm = lvl(L, Element.STORM), magma = lvl(L, Element.MAGMA);
        if (frost >= 1) attacker.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, frost >= 2 ? 3 : 1), p);
        if (frost >= 2) attacker.setTicksFrozen(Math.min(attacker.getTicksFrozen() + 140, 300));
        if (storm >= 2 && p.getRandom().nextFloat() < 0.25f) {
            LightningBolt bolt = EntityType.LIGHTNING_BOLT.create(p.serverLevel());
            if (bolt != null) {
                bolt.moveTo(attacker.position());
                bolt.setVisualOnly(true);
                p.serverLevel().addFreshEntity(bolt);
            }
            attacker.hurt(p.damageSources().lightningBolt(), 6);
        }
        if (magma >= 2 && !attacker.fireImmune()) attacker.igniteForSeconds(5);
    }

    @Override
    public void onUnequip(ServerPlayer p) {
        modifier(p, NeoForgeMod.SWIM_SPEED, SWIM, 0);
        modifier(p, Attributes.MOVEMENT_SPEED, SPEED, 0);
    }
}
