package com.celestialascent.armor;

import net.minecraft.world.item.Rarity;

/** The five armor sets of the ladder, weakest first. */
public enum SetId {
    TITAN("titan", new int[]{4, 7, 9, 4}, 4f, 0.15f, 45, 18, Rarity.RARE),
    IMPERIAL("imperial", new int[]{4, 8, 10, 4}, 5f, 0.2f, 55, 20, Rarity.RARE),
    STELLAR("stellar", new int[]{5, 8, 10, 5}, 6f, 0.25f, 70, 25, Rarity.EPIC),
    VOID("void", new int[]{5, 9, 11, 5}, 7f, 0.3f, 90, 25, Rarity.EPIC),
    ASCENDANT("ascendant", new int[]{6, 9, 12, 6}, 10f, 0.5f, 0, 30, Rarity.EPIC);

    public final String key;
    /** Defense in ArmorItem.Type order: boots, leggings, chestplate, helmet. */
    public final int[] defense;
    public final float toughness;
    public final float knockbackResistance;
    /** Durability multiplier; 0 = unbreakable. */
    public final int durability;
    public final int enchantability;
    public final Rarity rarity;

    SetId(String key, int[] defense, float toughness, float kb, int durability, int enchantability, Rarity rarity) {
        this.key = key;
        this.defense = defense;
        this.toughness = toughness;
        this.knockbackResistance = kb;
        this.durability = durability;
        this.enchantability = enchantability;
        this.rarity = rarity;
    }
}
