package com.celestialascent.armor;

import com.celestialascent.CelestialAscent;
import net.minecraft.core.Holder;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.item.ItemStack;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;

import java.util.ArrayList;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/** Full-set detection, set attribute bonuses and ability dispatch. */
@EventBusSubscriber(modid = CelestialAscent.MODID)
public final class ArmorSets {
    private ArmorSets() {}

    public record AttrBonus(Holder<Attribute> attribute, ResourceLocation id, double amount, AttributeModifier.Operation op) {}

    private static final Map<SetId, List<ArmorAbility>> ABILITIES = new EnumMap<>(SetId.class);
    private static final Map<SetId, List<AttrBonus>> BONUSES = new EnumMap<>(SetId.class);
    private static final Map<UUID, SetId> WORN = new HashMap<>();
    private static final EquipmentSlot[] SLOTS = {EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET};

    public static void ability(SetId set, ArmorAbility ability) {
        ABILITIES.computeIfAbsent(set, s -> new ArrayList<>()).add(ability);
    }

    public static void bonus(SetId set, Holder<Attribute> attr, String name, double amount, AttributeModifier.Operation op) {
        BONUSES.computeIfAbsent(set, s -> new ArrayList<>())
                .add(new AttrBonus(attr, ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "set_" + set.key + "_" + name), amount, op));
    }

    /** The set worn in all four armor slots, or null. */
    public static SetId fullSet(LivingEntity e) {
        SetId found = null;
        for (EquipmentSlot slot : SLOTS) {
            ItemStack s = e.getItemBySlot(slot);
            if (!(s.getItem() instanceof CelestialArmorItem a)) return null;
            if (found == null) found = a.set;
            else if (found != a.set) return null;
        }
        return found;
    }

    /** The four worn armor stacks, helmet first. */
    public static List<ItemStack> pieces(LivingEntity e) {
        List<ItemStack> out = new ArrayList<>(4);
        for (EquipmentSlot slot : SLOTS) out.add(e.getItemBySlot(slot));
        return out;
    }

    private static List<ArmorAbility> abilities(SetId set) {
        return set == null ? List.of() : ABILITIES.getOrDefault(set, List.of());
    }

    /** Applies or removes set attribute bonuses so they match {@code set}. */
    static void syncBonuses(ServerPlayer p, SetId set) {
        for (Map.Entry<SetId, List<AttrBonus>> e : BONUSES.entrySet()) {
            for (AttrBonus b : e.getValue()) {
                AttributeInstance inst = p.getAttribute(b.attribute());
                if (inst == null) continue;
                if (e.getKey() == set) inst.addOrUpdateTransientModifier(new AttributeModifier(b.id(), b.amount(), b.op()));
                else inst.removeModifier(b.id());
            }
        }
    }

    @SubscribeEvent
    public static void onTick(PlayerTickEvent.Post e) {
        if (!(e.getEntity() instanceof ServerPlayer p)) return;
        SetId set = fullSet(p);
        SetId before = WORN.get(p.getUUID());
        if (set != before) {
            for (ArmorAbility a : abilities(before)) a.onUnequip(p);
            syncBonuses(p, set);
            if (set == null) WORN.remove(p.getUUID());
            else WORN.put(p.getUUID(), set);
            // Losing creative flight mid-air: stop flying (the attribute alone does not do this).
            if (!p.isCreative() && !p.isSpectator() && !p.mayFly() && p.getAbilities().flying) {
                p.getAbilities().flying = false;
                p.onUpdateAbilities();
            }
        }
        for (ArmorAbility a : abilities(set)) a.tick(p);
    }

    @SubscribeEvent
    public static void onHurt(LivingIncomingDamageEvent e) {
        if (e.getEntity() instanceof ServerPlayer victim) {
            for (ArmorAbility a : abilities(fullSet(victim))) a.onHurt(victim, e);
        }
        if (e.getSource().getEntity() instanceof ServerPlayer attacker && attacker != e.getEntity()) {
            for (ArmorAbility a : abilities(fullSet(attacker))) a.onAttack(attacker, e.getEntity(), e);
        }
    }

    @SubscribeEvent
    public static void onLogout(PlayerEvent.PlayerLoggedOutEvent e) {
        WORN.remove(e.getEntity().getUUID());
    }

    /** Called from the ability-key payload. */
    public static void onKey(ServerPlayer p, int key) {
        for (ArmorAbility a : abilities(fullSet(p))) a.onKey(p, key);
    }
}
