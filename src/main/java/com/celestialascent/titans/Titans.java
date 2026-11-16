package com.celestialascent.titans;

import com.celestialascent.CelestialAscent;
import com.celestialascent.armor.ArmorSets;
import com.celestialascent.armor.SetId;
import com.celestialascent.compat.Emc;
import com.celestialascent.core.CAReg;
import com.celestialascent.core.Content;
import com.celestialascent.core.station.StationBlock;
import com.celestialascent.core.station.StationRecipe;
import com.celestialascent.core.station.StationType;
import com.celestialascent.core.station.Stations;
import com.celestialascent.economy.CoinTier;
import com.celestialascent.economy.Professions;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.npc.VillagerTrades;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.MapItem;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.item.trading.ItemCost;
import net.minecraft.world.item.trading.MerchantOffer;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.level.saveddata.maps.MapDecorationTypes;
import net.minecraft.world.level.saveddata.maps.MapItemSavedData;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.entity.EntityAttributeCreationEvent;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredItem;

import java.util.EnumMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Supplier;

/** Step 1 of the ladder: the Elemental Titans, their shrines, materials, forge and armor. */
@EventBusSubscriber(modid = CelestialAscent.MODID)
public final class Titans {
    private Titans() {}

    public static final DeferredHolder<DataComponentType<?>, DataComponentType<Element>> ELEMENT =
            CAReg.COMPONENTS.registerComponentType("element", b -> b.persistent(Element.CODEC).networkSynchronized(Element.STREAM_CODEC));

    // ---- materials ---------------------------------------------------------------------------
    public static final DeferredItem<Item> TITAN_SHARD = Content.item("titan_shard",
            () -> new Item(new Item.Properties().rarity(Rarity.UNCOMMON).fireResistant()));
    public static final Map<Element, DeferredItem<Item>> CORES = new EnumMap<>(Element.class);
    public static final Map<Element, DeferredItem<SigilItem>> SIGILS = new EnumMap<>(Element.class);

    static {
        for (Element e : Element.values()) {
            CORES.put(e, Content.item(e.key + "_core", () -> new Item(new Item.Properties().rarity(Rarity.RARE).fireResistant()
                    .component(DataComponents.ENCHANTMENT_GLINT_OVERRIDE, true))));
        }
        for (Element e : Element.values()) SIGILS.put(e, Content.item(e.key + "_sigil", () -> new SigilItem(e)));
    }

    // ---- armor -----------------------------------------------------------------------------------
    public static final DeferredItem<TitanArmorItem> HELMET = Content.item("titan_helmet", () -> new TitanArmorItem(ArmorItem.Type.HELMET, new Item.Properties()));
    public static final DeferredItem<TitanArmorItem> CHESTPLATE = Content.item("titan_chestplate", () -> new TitanArmorItem(ArmorItem.Type.CHESTPLATE, new Item.Properties()));
    public static final DeferredItem<TitanArmorItem> LEGGINGS = Content.item("titan_leggings", () -> new TitanArmorItem(ArmorItem.Type.LEGGINGS, new Item.Properties()));
    public static final DeferredItem<TitanArmorItem> BOOTS = Content.item("titan_boots", () -> new TitanArmorItem(ArmorItem.Type.BOOTS, new Item.Properties()));

    // ---- blocks ----------------------------------------------------------------------------------
    public static final Map<Element, DeferredBlock<AltarBlock>> ALTARS = new EnumMap<>(Element.class);

    static {
        for (Element e : Element.values()) {
            ALTARS.put(e, Content.block(e.key + "_altar", () -> new AltarBlock(e, BlockBehaviour.Properties.of()
                    .mapColor(switch (e) {
                        case FROST -> MapColor.ICE;
                        case TIDE -> MapColor.COLOR_CYAN;
                        case STORM -> MapColor.TERRACOTTA_WHITE;
                        case MAGMA -> MapColor.COLOR_BLACK;
                    })
                    .strength(-1f, 3600000f).sound(SoundType.DEEPSLATE_BRICKS).noOcclusion().lightLevel(s -> 12))));
        }
    }

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<AltarBlock.AltarBlockEntity>> ALTAR_BE =
            CAReg.BLOCK_ENTITIES.register("titan_altar", () -> BlockEntityType.Builder.of(AltarBlock.AltarBlockEntity::new,
                    ALTARS.values().stream().map(DeferredBlock::get).toArray(net.minecraft.world.level.block.Block[]::new)).build(null));

    public static final DeferredBlock<CooledMagmaBlock> COOLED_MAGMA = Content.blockOnly("cooled_magma",
            () -> new CooledMagmaBlock(BlockBehaviour.Properties.of().mapColor(MapColor.NETHER).strength(0.5f).lightLevel(s -> 3)
                    .sound(SoundType.BASALT).noLootTable()));

    public static final StationType FORGE = new StationType("titan_forge", 100,
            new int[]{30, 35}, new int[][]{{66, 17}, {66, 53}}, new int[]{124, 35}, new int[]{90, 35});

    public static final DeferredBlock<StationBlock> TITAN_FORGE = Stations.register("titan_forge",
            () -> new StationBlock(BlockBehaviour.Properties.of().mapColor(MapColor.DEEPSLATE).strength(6f, 1200f)
                    .sound(SoundType.NETHERITE_BLOCK).requiresCorrectToolForDrops().lightLevel(s -> 9).noOcclusion(), () -> FORGE));

    // ---- entities --------------------------------------------------------------------------------
    public static final DeferredHolder<EntityType<?>, EntityType<FrostTitan>> FROST_TITAN = CAReg.ENTITIES.register("frost_titan",
            () -> EntityType.Builder.of(FrostTitan::new, MobCategory.MONSTER).sized(2.0f, 4.0f).clientTrackingRange(10).build("frost_titan"));
    public static final DeferredHolder<EntityType<?>, EntityType<TideTitan>> TIDE_TITAN = CAReg.ENTITIES.register("tide_titan",
            () -> EntityType.Builder.of(TideTitan::new, MobCategory.MONSTER).sized(2.0f, 4.2f).clientTrackingRange(10).build("tide_titan"));
    public static final DeferredHolder<EntityType<?>, EntityType<StormTitan>> STORM_TITAN = CAReg.ENTITIES.register("storm_titan",
            () -> EntityType.Builder.of(StormTitan::new, MobCategory.MONSTER).sized(2.2f, 4.5f).clientTrackingRange(10).build("storm_titan"));
    public static final DeferredHolder<EntityType<?>, EntityType<MagmaTitan>> MAGMA_TITAN = CAReg.ENTITIES.register("magma_titan",
            () -> EntityType.Builder.of(MagmaTitan::new, MobCategory.MONSTER).sized(2.4f, 4.6f).fireImmune().clientTrackingRange(10).build("magma_titan"));

    public static EntityType<? extends TitanBoss> titanType(Element e) {
        return switch (e) {
            case FROST -> FROST_TITAN.get();
            case TIDE -> TIDE_TITAN.get();
            case STORM -> STORM_TITAN.get();
            case MAGMA -> MAGMA_TITAN.get();
        };
    }

    @SubscribeEvent
    public static void attributes(EntityAttributeCreationEvent e) {
        e.put(FROST_TITAN.get(), TitanBoss.titanAttributes(400, 14, 0.24, 14).build());
        e.put(TIDE_TITAN.get(), TitanBoss.titanAttributes(450, 14, 0.25, 14).build());
        e.put(STORM_TITAN.get(), TitanBoss.titanAttributes(500, 15, 0.27, 12).build());
        e.put(MAGMA_TITAN.get(), TitanBoss.titanAttributes(600, 16, 0.23, 18).build());
    }

    public static TagKey<Structure> shrineTag(Element e) {
        return TagKey.create(Registries.STRUCTURE, ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, e.key + "_shrine"));
    }

    /** Trade: a map to the nearest shrine of an element (Magma maps point into the Nether). */
    private static VillagerTrades.ItemListing shrineMap(Element e) {
        return (trader, random) -> {
            if (!(trader.level() instanceof ServerLevel here)) return null;
            ServerLevel level = e == Element.MAGMA ? here.getServer().getLevel(Level.NETHER) : here;
            if (level == null) return null;
            net.minecraft.core.BlockPos origin = trader.blockPosition();
            if (e == Element.MAGMA) origin = new net.minecraft.core.BlockPos(origin.getX() / 8, 64, origin.getZ() / 8);
            var pos = com.celestialascent.retrogen.Retrogen.findNearest(level, shrineTag(e), origin, true);
            if (pos == null) return null;
            ItemStack map = MapItem.create(level, pos.getX(), pos.getZ(), (byte) 2, true, true);
            MapItem.renderBiomePreviewMap(level, map);
            MapItemSavedData.addTargetDecoration(map, pos, "+", MapDecorationTypes.RED_X);
            map.set(DataComponents.ITEM_NAME, Component.translatable("filled_map.celestialascent." + e.key + "_shrine"));
            return new MerchantOffer(new ItemCost(Professions.coin(CoinTier.GOLD), SHRINE_MAP_GOLD), Optional.of(new ItemCost(Items.COMPASS)), map, 1, 15, 0.2f);
        };
    }

    private static final int SHRINE_MAP_GOLD = 2;

    /** What a shrine map trade shows in recipe viewers: the same costs and a named filled map. */
    private static Professions.TradeDisplay shrineMapDisplay(int level, Element e) {
        return new Professions.TradeDisplay(level, () -> new ItemStack(Professions.coin(CoinTier.GOLD), SHRINE_MAP_GOLD), () -> new ItemStack(Items.COMPASS),
                () -> {
                    ItemStack map = new ItemStack(Items.FILLED_MAP);
                    map.set(DataComponents.ITEM_NAME, Component.translatable("filled_map.celestialascent." + e.key + "_shrine"));
                    return map;
                });
    }

    private static ItemStack infuse(ItemStack base, Item result, Element e) {
        ItemStack out = new ItemStack(result.builtInRegistryHolder(), 1, base.getComponentsPatch());
        out.remove(DataComponents.DAMAGE);
        out.set(ELEMENT.get(), e);
        return out;
    }

    @SubscribeEvent
    public static void setup(net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent e) {
        e.enqueueWork(Titans::recipes);
    }

    /** Station recipes need resolved items, so they are built after registration. */
    static void recipes() {
        List<Supplier<Item>> netherite = List.of(() -> Items.NETHERITE_HELMET, () -> Items.NETHERITE_CHESTPLATE, () -> Items.NETHERITE_LEGGINGS, () -> Items.NETHERITE_BOOTS);
        List<DeferredItem<TitanArmorItem>> titan = List.of(HELMET, CHESTPLATE, LEGGINGS, BOOTS);
        for (int i = 0; i < 4; i++) {
            Supplier<Item> base = netherite.get(i);
            DeferredItem<TitanArmorItem> out = titan.get(i);
            for (Element e : Element.values()) {
                // Netherite piece + core + 4 shards -> infused titan piece (keeps enchantments and name).
                FORGE.add(StationRecipe.of(s -> s.is(base.get()), List.of(
                        new StationRecipe.Mat(Ingredient.of(CORES.get(e)), 1), new StationRecipe.Mat(Ingredient.of(TITAN_SHARD), 4)),
                        s -> infuse(s, out.get(), e), () -> List.of(new ItemStack(base.get()))));
                // Re-infuse an existing titan piece with a different element: core + 2 shards.
                Element other = Element.values()[(e.ordinal() + 1) % Element.values().length];
                FORGE.add(StationRecipe.of(s -> s.is(out.get()) && TitanArmorItem.element(s) != e, List.of(
                        new StationRecipe.Mat(Ingredient.of(CORES.get(e)), 1), new StationRecipe.Mat(Ingredient.of(TITAN_SHARD), 2)),
                        s -> infuse(s, out.get(), e), () -> List.of(infuse(new ItemStack(base.get()), out.get(), other))));
            }
        }
    }

    public static void init() {
        ArmorSets.ability(SetId.TITAN, new TitanAbilities());

        Professions.trade(Professions.TITANSMITH, 2, TITAN_SHARD, 1, Professions.coin(CoinTier.GOLD), 2, 16, 10);
        Professions.trade(Professions.TITANSMITH, 3, shrineMap(Element.FROST), shrineMapDisplay(3, Element.FROST));
        Professions.trade(Professions.TITANSMITH, 3, shrineMap(Element.STORM), shrineMapDisplay(3, Element.STORM));
        Professions.trade(Professions.TITANSMITH, 4, shrineMap(Element.TIDE), shrineMapDisplay(4, Element.TIDE));
        Professions.trade(Professions.TITANSMITH, 4, shrineMap(Element.MAGMA), shrineMapDisplay(4, Element.MAGMA));
        for (Element e : Element.values()) {
            Professions.trade(Professions.TITANSMITH, 5, Professions.coin(CoinTier.TITAN), 1, Items.NETHERITE_SCRAP, 2, SIGILS.get(e), 1, 3, 30);
            Professions.trade(Professions.RELIC_DEALER, 3, CORES.get(e), 1, Professions.coin(CoinTier.TITAN), 2, 4, 20);
        }

        Emc.set(TITAN_SHARD, 250_000);
        for (Element e : Element.values()) {
            Emc.set(CORES.get(e), 2_000_000);
            Emc.set(SIGILS.get(e), 150_000);
        }
        Emc.set(HELMET, 12_000_000);
        Emc.set(CHESTPLATE, 19_200_000);
        Emc.set(LEGGINGS, 16_800_000);
        Emc.set(BOOTS, 9_600_000);
        Emc.set(TITAN_FORGE, 1_500_000);
    }
}
