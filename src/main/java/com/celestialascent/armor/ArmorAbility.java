package com.celestialascent.armor;

import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;

/** Behaviour granted by wearing a full armor set. All hooks run server-side. */
public interface ArmorAbility {
    /** Every tick while the full set is worn. */
    default void tick(ServerPlayer player) {}

    /** The wearer is about to take damage; may cancel or reduce it. */
    default void onHurt(ServerPlayer player, LivingIncomingDamageEvent event) {}

    /** The wearer is about to damage {@code target}. */
    default void onAttack(ServerPlayer player, LivingEntity target, LivingIncomingDamageEvent event) {}

    /** Ability key pressed: 0 = primary (H), 1 = toggle (G). */
    default void onKey(ServerPlayer player, int key) {}

    /** The set was taken off. */
    default void onUnequip(ServerPlayer player) {}
}
