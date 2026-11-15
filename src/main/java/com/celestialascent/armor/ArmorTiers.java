package com.celestialascent.armor;

import com.celestialascent.CelestialAscent;
import com.celestialascent.core.CAReg;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.crafting.Ingredient;
import net.neoforged.neoforge.registries.DeferredHolder;

import java.util.EnumMap;
import java.util.List;
import java.util.Map;

/** Registers one ArmorMaterial per set. Repair items come from tag celestialascent:repairs/&lt;set&gt;. */
public final class ArmorTiers {
    private ArmorTiers() {}

    public static final Map<SetId, DeferredHolder<ArmorMaterial, ArmorMaterial>> MATERIALS = new EnumMap<>(SetId.class);

    public static TagKey<Item> repairTag(SetId set) {
        return TagKey.create(Registries.ITEM, ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "repairs/" + set.key));
    }

    static {
        for (SetId set : SetId.values()) {
            MATERIALS.put(set, CAReg.ARMOR_MATERIALS.register(set.key, () -> {
                Map<ArmorItem.Type, Integer> def = new EnumMap<>(ArmorItem.Type.class);
                def.put(ArmorItem.Type.BOOTS, set.defense[0]);
                def.put(ArmorItem.Type.LEGGINGS, set.defense[1]);
                def.put(ArmorItem.Type.CHESTPLATE, set.defense[2]);
                def.put(ArmorItem.Type.HELMET, set.defense[3]);
                def.put(ArmorItem.Type.BODY, set.defense[2]);
                return new ArmorMaterial(def, set.enchantability, SoundEvents.ARMOR_EQUIP_NETHERITE,
                        () -> Ingredient.of(repairTag(set)),
                        List.of(new ArmorMaterial.Layer(ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, set.key))),
                        set.toughness, set.knockbackResistance);
            }));
        }
    }

    public static Holder<ArmorMaterial> material(SetId set) {
        return MATERIALS.get(set);
    }

    public static void init() {}
}
