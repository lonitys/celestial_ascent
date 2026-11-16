package com.celestialascent.empire;

import com.celestialascent.CelestialAscent;
import com.celestialascent.armor.ArmorSets;
import com.celestialascent.armor.CelestialArmorItem;
import com.celestialascent.armor.SetId;
import com.celestialascent.boss.CelestialBoss;
import com.celestialascent.compat.Emc;
import com.celestialascent.core.CAReg;
import com.celestialascent.core.Content;
import com.celestialascent.core.station.StationBlock;
import com.celestialascent.core.station.StationRecipe;
import com.celestialascent.core.station.StationType;
import com.celestialascent.core.station.Stations;
import com.celestialascent.economy.CoinTier;
import com.celestialascent.economy.Professions;
import com.celestialascent.progress.Constellations;
import com.celestialascent.progress.Progress;
import com.celestialascent.titans.Titans;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.boss.enderdragon.EnderDragon;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.level.material.PushReaction;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;
import net.neoforged.neoforge.event.entity.EntityAttributeCreationEvent;
import net.neoforged.neoforge.event.entity.living.EnderManAngerEvent;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredItem;

import java.util.List;

/** Step 2: the Dragon Heart and the Lost Ender Empire. */
@EventBusSubscriber(modid = CelestialAscent.MODID)
public final class Empire {
    private Empire() {}

    private static Item.Properties rare() {
        return new Item.Properties().rarity(Rarity.RARE).fireResistant();
    }

    public static final DeferredItem<Item> DRAGON_HEART = Content.item("dragon_heart",
            () -> new Item(new Item.Properties().rarity(Rarity.EPIC).fireResistant().stacksTo(16)));
    public static final DeferredItem<Item> IMPERIAL_PLATING = Content.item("imperial_plating", () -> new Item(rare()));
    public static final DeferredItem<Item> ENDER_GEAR = Content.item("ender_gear", () -> new Item(rare()));
    public static final DeferredItem<Item> COLOSSUS_CORE = Content.item("colossus_core",
            () -> new Item(new Item.Properties().rarity(Rarity.EPIC).fireResistant().component(DataComponents.ENCHANTMENT_GLINT_OVERRIDE, true)));
    public static final DeferredItem<Item> IMPERIAL_SEAL = Content.item("imperial_seal",
            () -> new Item(new Item.Properties().rarity(Rarity.EPIC).fireResistant().stacksTo(1).component(DataComponents.ENCHANTMENT_GLINT_OVERRIDE, true)));

    public static final DeferredItem<CelestialArmorItem> HELMET = Content.item("imperial_helmet", () -> new CelestialArmorItem(SetId.IMPERIAL, ArmorItem.Type.HELMET, new Item.Properties()));
    public static final DeferredItem<CelestialArmorItem> CHESTPLATE = Content.item("imperial_chestplate", () -> new CelestialArmorItem(SetId.IMPERIAL, ArmorItem.Type.CHESTPLATE, new Item.Properties()));
    public static final DeferredItem<CelestialArmorItem> LEGGINGS = Content.item("imperial_leggings", () -> new CelestialArmorItem(SetId.IMPERIAL, ArmorItem.Type.LEGGINGS, new Item.Properties()));
    public static final DeferredItem<CelestialArmorItem> BOOTS = Content.item("imperial_boots", () -> new CelestialArmorItem(SetId.IMPERIAL, ArmorItem.Type.BOOTS, new Item.Properties()));

    public static final DeferredBlock<PylonBlock> PYLON = Content.block("imperial_pylon",
            () -> new PylonBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_PURPLE).strength(-1f, 3600000f)
                    .sound(SoundType.AMETHYST).lightLevel(s -> s.getValue(PylonBlock.RESTORED) ? 15 : 6).noOcclusion().pushReaction(PushReaction.BLOCK)));
    public static final DeferredBlock<Block> IMPERIAL_BARRIER = Content.block("imperial_barrier",
            () -> new net.minecraft.world.level.block.TransparentBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_MAGENTA)
                    .strength(-1f, 3600000f).sound(SoundType.GLASS).lightLevel(s -> 8).noOcclusion().noLootTable()
                    .isViewBlocking((s, l, p) -> false).isSuffocating((s, l, p) -> false).pushReaction(PushReaction.BLOCK)));
    public static final DeferredBlock<ThroneBlock> THRONE = Content.block("empty_throne",
            () -> new ThroneBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_PURPLE).strength(-1f, 3600000f)
                    .sound(SoundType.STONE).lightLevel(s -> 7).noOcclusion()));

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<PylonBlock.PylonBlockEntity>> PYLON_BE =
            CAReg.BLOCK_ENTITIES.register("imperial_pylon", () -> BlockEntityType.Builder.of(PylonBlock.PylonBlockEntity::new, PYLON.get()).build(null));

    public static final StationType FORGE = new StationType("imperial_forge", 140,
            new int[]{30, 35}, new int[][]{{66, 17}, {66, 35}, {66, 53}}, new int[]{124, 35}, new int[]{90, 35});
    public static final DeferredBlock<StationBlock> IMPERIAL_FORGE = Stations.register("imperial_forge",
            () -> new StationBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_PURPLE).strength(6f, 1200f)
                    .sound(SoundType.NETHERITE_BLOCK).requiresCorrectToolForDrops().lightLevel(s -> 11).noOcclusion(), () -> FORGE));

    public static final DeferredHolder<EntityType<?>, EntityType<SentinelConstruct>> SENTINEL = CAReg.ENTITIES.register("sentinel_construct",
            () -> EntityType.Builder.of(SentinelConstruct::new, MobCategory.MONSTER).sized(1.6f, 3.2f).clientTrackingRange(10).build("sentinel_construct"));
    public static final DeferredHolder<EntityType<?>, EntityType<EnderColossus>> COLOSSUS = CAReg.ENTITIES.register("ender_colossus",
            () -> EntityType.Builder.of(EnderColossus::new, MobCategory.MONSTER).sized(3.0f, 6.0f).fireImmune().clientTrackingRange(12).build("ender_colossus"));

    @SubscribeEvent
    public static void attributes(EntityAttributeCreationEvent e) {
        e.put(SENTINEL.get(), SentinelConstruct.attributes().build());
        e.put(COLOSSUS.get(), EnderColossus.attributes().build());
    }

    @SubscribeEvent
    public static void setup(FMLCommonSetupEvent e) {
        e.enqueueWork(Empire::recipes);
    }

    static void recipes() {
        List<Item> titan = List.of(Titans.HELMET.get(), Titans.CHESTPLATE.get(), Titans.LEGGINGS.get(), Titans.BOOTS.get());
        List<DeferredItem<CelestialArmorItem>> imperial = List.of(HELMET, CHESTPLATE, LEGGINGS, BOOTS);
        for (int i = 0; i < 4; i++) {
            Item base = titan.get(i);
            Item out = imperial.get(i).get();
            List<StationRecipe.Mat> mats = i == 1
                    ? List.of(new StationRecipe.Mat(Ingredient.of(IMPERIAL_PLATING.get()), 6), new StationRecipe.Mat(Ingredient.of(ENDER_GEAR.get()), 3),
                              new StationRecipe.Mat(Ingredient.of(COLOSSUS_CORE.get()), 1))
                    : List.of(new StationRecipe.Mat(Ingredient.of(IMPERIAL_PLATING.get()), 4), new StationRecipe.Mat(Ingredient.of(ENDER_GEAR.get()), 2));
            FORGE.add(StationRecipe.of(s -> s.is(base), mats, s -> upgrade(s, out), () -> List.of(new ItemStack(base))));
        }
    }

    /** Copies components (enchantments, names, element) onto the upgraded piece and repairs it. */
    public static ItemStack upgrade(ItemStack base, Item result) {
        ItemStack out = new ItemStack(result.builtInRegistryHolder(), 1, base.getComponentsPatch());
        out.remove(DataComponents.DAMAGE);
        com.celestialascent.armor.ArmorStages.reset(out); // a new set starts its evolution over
        return out;
    }

    /** Every player near a slain Ender Dragon receives a Dragon Heart and the dragon constellation. */
    @SubscribeEvent
    public static void dragonDeath(LivingDeathEvent e) {
        if (!(e.getEntity() instanceof EnderDragon dragon) || !(dragon.level() instanceof ServerLevel sl)) return;
        ResourceLocation id = ResourceLocation.withDefaultNamespace("ender_dragon");
        Constellations.Entry entry = Constellations.ALL.stream().filter(c -> c.boss().equals(id)).findFirst().orElse(null);
        for (ServerPlayer p : sl.getPlayers(p -> p.isAlive() && !p.isSpectator() && p.distanceTo(dragon) < 200)) {
            CelestialBoss.giveOwned(sl, p, new ItemStack(DRAGON_HEART.get()));
            p.sendSystemMessage(Component.translatable("message.celestialascent.dragon_heart").withColor(0xC77DFF));
            if (Progress.recordKill(p, id) && entry != null) {
                p.sendSystemMessage(Component.translatable("message.celestialascent.constellation",
                        Component.translatable("constellation.celestialascent." + entry.key())).withColor(entry.color()));
            }
        }
    }

    @SubscribeEvent
    public static void enderman(EnderManAngerEvent e) {
        SetId set = ArmorSets.fullSet(e.getPlayer());
        if (set == SetId.IMPERIAL || set == SetId.ASCENDANT) e.setCanceled(true);
    }

    public static void init() {
        ArmorSets.ability(SetId.IMPERIAL, new ImperialAbilities());
        ArmorSets.bonus(SetId.IMPERIAL, Attributes.ENTITY_INTERACTION_RANGE, "reach", 1.0, AttributeModifier.Operation.ADD_VALUE);
        ArmorSets.bonus(SetId.IMPERIAL, Attributes.BLOCK_INTERACTION_RANGE, "block_reach", 1.0, AttributeModifier.Operation.ADD_VALUE);

        Professions.trade(Professions.RELIC_DEALER, 4, Professions.offer(Professions.coin(CoinTier.ENDER), 1, IMPERIAL_PLATING, 2, 6, 25));
        Professions.trade(Professions.RELIC_DEALER, 5, Professions.offer(DRAGON_HEART, 1, Professions.coin(CoinTier.ENDER), 4, 2, 40));

        Emc.set(DRAGON_HEART, 5_000_000);
        Emc.set(IMPERIAL_PLATING, 1_500_000);
        Emc.set(ENDER_GEAR, 1_000_000);
        Emc.set(COLOSSUS_CORE, 15_000_000);
        Emc.set(IMPERIAL_SEAL, 25_000_000);
        Emc.set(HELMET, 40_000_000);
        Emc.set(CHESTPLATE, 64_000_000);
        Emc.set(LEGGINGS, 56_000_000);
        Emc.set(BOOTS, 32_000_000);
        Emc.set(IMPERIAL_FORGE, 6_000_000);
    }
}
