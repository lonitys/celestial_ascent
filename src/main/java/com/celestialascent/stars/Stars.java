package com.celestialascent.stars;

import com.celestialascent.CelestialAscent;
import com.celestialascent.armor.ArmorSets;
import com.celestialascent.armor.CelestialArmorItem;
import com.celestialascent.armor.SetId;
import com.celestialascent.boss.SummonAltarBlock;
import com.celestialascent.compat.Emc;
import com.celestialascent.core.CAReg;
import com.celestialascent.core.Content;
import com.celestialascent.core.station.StationBlock;
import com.celestialascent.core.station.StationRecipe;
import com.celestialascent.core.station.StationType;
import com.celestialascent.core.station.Stations;
import com.celestialascent.economy.CoinTier;
import com.celestialascent.economy.Professions;
import com.celestialascent.empire.Empire;
import net.minecraft.core.component.DataComponents;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.DropExperienceBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.level.material.PushReaction;
import net.minecraft.util.valueproviders.UniformInt;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;
import net.neoforged.neoforge.event.entity.EntityAttributeCreationEvent;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredItem;

import java.util.List;

/** Step 3: the Star Gate, the Fallen Stars dimension, the Celestials and Stellar armor. */
@EventBusSubscriber(modid = CelestialAscent.MODID)
public final class Stars {
    private Stars() {}

    private static ResourceLocation id(String p) {
        return ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, p);
    }

    private static BlockBehaviour.Properties starstone() {
        return BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_BLUE).strength(3f, 9f).requiresCorrectToolForDrops().sound(SoundType.DEEPSLATE);
    }

    // ---- blocks ----
    public static final DeferredBlock<Block> STARSTONE = Content.block("starstone", () -> new Block(starstone()));
    public static final DeferredBlock<Block> STARLIT_STARSTONE = Content.block("starlit_starstone", () -> new Block(starstone().lightLevel(s -> 4)));
    public static final DeferredBlock<Block> STARSTONE_BRICKS = Content.block("starstone_bricks", () -> new Block(starstone()));
    public static final DeferredBlock<DropExperienceBlock> STARDUST_ORE = Content.block("stardust_ore",
            () -> new DropExperienceBlock(UniformInt.of(4, 8), starstone().strength(4.5f, 9f).lightLevel(s -> 7)));
    public static final DeferredBlock<Block> STAR_CRYSTAL = Content.block("star_crystal",
            () -> new net.minecraft.world.level.block.AmethystClusterBlock(7, 3, BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_LIGHT_BLUE)
                    .strength(1.5f).sound(SoundType.AMETHYST_CLUSTER).lightLevel(s -> 10).noOcclusion().pushReaction(PushReaction.DESTROY)));
    public static final DeferredBlock<Block> STAR_GATE_FRAME = Content.block("star_gate_frame",
            () -> new Block(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_BLACK).strength(-1f, 3600000f).sound(SoundType.STONE).lightLevel(s -> 6)));
    public static final DeferredBlock<StarGatePedestalBlock> STAR_GATE_PEDESTAL = Content.block("star_gate_pedestal",
            () -> new StarGatePedestalBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_BLACK).strength(-1f, 3600000f).noOcclusion().lightLevel(s -> 8)));
    public static final DeferredBlock<StarPortalBlock> STAR_PORTAL = Content.blockOnly("star_portal",
            () -> new StarPortalBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_BLACK).noCollission().lightLevel(s -> 15)
                    .strength(-1f, 3600000f).noLootTable().pushReaction(PushReaction.BLOCK)));

    // ---- items ----
    public static final DeferredItem<Item> STARDUST = Content.item("stardust", () -> new Item(new Item.Properties().rarity(Rarity.RARE)));
    public static final DeferredItem<Item> DORMANT_STAR_CORE = Content.item("dormant_star_core",
            () -> new Item(new Item.Properties().rarity(Rarity.EPIC).fireResistant().stacksTo(16)));
    public static final DeferredItem<Item> STAR_CORE = Content.item("star_core",
            () -> new Item(new Item.Properties().rarity(Rarity.EPIC).fireResistant().stacksTo(16).component(DataComponents.ENCHANTMENT_GLINT_OVERRIDE, true)));
    public static final DeferredItem<StarCompassItem> STAR_COMPASS = Content.item("star_compass",
            () -> new StarCompassItem(new Item.Properties().rarity(Rarity.EPIC).stacksTo(1)));

    public static final DeferredItem<CelestialArmorItem> HELMET = Content.item("stellar_helmet", () -> new CelestialArmorItem(SetId.STELLAR, ArmorItem.Type.HELMET, new Item.Properties()));
    public static final DeferredItem<CelestialArmorItem> CHESTPLATE = Content.item("stellar_chestplate", () -> new CelestialArmorItem(SetId.STELLAR, ArmorItem.Type.CHESTPLATE, new Item.Properties()));
    public static final DeferredItem<CelestialArmorItem> LEGGINGS = Content.item("stellar_leggings", () -> new CelestialArmorItem(SetId.STELLAR, ArmorItem.Type.LEGGINGS, new Item.Properties()));
    public static final DeferredItem<CelestialArmorItem> BOOTS = Content.item("stellar_boots", () -> new CelestialArmorItem(SetId.STELLAR, ArmorItem.Type.BOOTS, new Item.Properties()));

    // ---- entities ----
    public static final DeferredHolder<EntityType<?>, EntityType<AstralSeraph>> SERAPH = CAReg.ENTITIES.register("astral_seraph",
            () -> EntityType.Builder.of(AstralSeraph::new, MobCategory.MONSTER).sized(2.0f, 3.2f).fireImmune().clientTrackingRange(12).build("astral_seraph"));
    public static final DeferredHolder<EntityType<?>, EntityType<NebulaLeviathan>> LEVIATHAN = CAReg.ENTITIES.register("nebula_leviathan",
            () -> EntityType.Builder.of(NebulaLeviathan::new, MobCategory.MONSTER).sized(2.6f, 2.0f).fireImmune().clientTrackingRange(12).build("nebula_leviathan"));
    public static final DeferredHolder<EntityType<?>, EntityType<SunHerald>> HERALD = CAReg.ENTITIES.register("sun_herald",
            () -> EntityType.Builder.of(SunHerald::new, MobCategory.MONSTER).sized(1.8f, 4.0f).fireImmune().clientTrackingRange(12).build("sun_herald"));

    // ---- altars & stations ----
    private static DeferredBlock<SummonAltarBlock> altar(String name, java.util.function.Supplier<? extends EntityType<? extends com.celestialascent.boss.CelestialBoss>> boss,
                                                         List<ResourceLocation> req, int color) {
        DeferredBlock<SummonAltarBlock> b = Content.block(name, () -> new SummonAltarBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_BLUE)
                .strength(-1f, 3600000f).sound(SoundType.AMETHYST).noOcclusion().lightLevel(s -> 12), boss, STARDUST, 16, req, color, 12000));
        SummonAltarBlock.ALL.add(b);
        return b;
    }

    public static final DeferredBlock<SummonAltarBlock> SERAPH_ALTAR = altar("seraph_altar", SERAPH, List.of(), 0xFFFFFF);
    public static final DeferredBlock<SummonAltarBlock> LEVIATHAN_ALTAR = altar("leviathan_altar", LEVIATHAN, List.of(), 0xB45CFF);
    public static final DeferredBlock<SummonAltarBlock> HERALD_ALTAR = altar("herald_altar", HERALD, List.of(id("astral_seraph"), id("nebula_leviathan")), 0xFFC93C);

    public static final StationType SKY_ALTAR_TYPE = new StationType("sky_altar", 1200,
            new int[]{30, 35}, new int[][]{{66, 17}, {66, 53}}, new int[]{124, 35}, new int[]{90, 35})
            .condition((level, pos) -> level.dimension() == Level.OVERWORLD && nightSky(level) && level.canSeeSky(pos.above()),
                    "gui.celestialascent.needs_night_sky");
    public static final DeferredBlock<StationBlock> SKY_ALTAR = Stations.register("sky_altar",
            () -> new StationBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_BLUE).strength(5f, 1200f).sound(SoundType.AMETHYST)
                    .requiresCorrectToolForDrops().noOcclusion().lightLevel(s -> 12), () -> SKY_ALTAR_TYPE));

    /**
     * True between dusk and dawn by the clock. Vanilla's isNight() is also true in a daytime thunderstorm,
     * which would let the Sky Altar charge at noon.
     */
    public static boolean nightSky(Level level) {
        long t = level.getDayTime() % 24000L;
        return t >= 13000L && t <= 23000L;
    }

    @SubscribeEvent
    public static void attributes(EntityAttributeCreationEvent e) {
        e.put(SERAPH.get(), AstralSeraph.attributes().build());
        e.put(LEVIATHAN.get(), NebulaLeviathan.attributes().build());
        e.put(HERALD.get(), SunHerald.attributes().build());
    }

    @SubscribeEvent
    public static void setup(FMLCommonSetupEvent e) {
        e.enqueueWork(Stars::recipes);
    }

    static void recipes() {
        // Charge a Dormant Star Core under the night sky (no materials).
        SKY_ALTAR_TYPE.add(new StationRecipe(s -> s.is(DORMANT_STAR_CORE.get()), List.of(), s -> new ItemStack(STAR_CORE.get())));
        List<Item> imperial = List.of(Empire.HELMET.get(), Empire.CHESTPLATE.get(), Empire.LEGGINGS.get(), Empire.BOOTS.get());
        List<DeferredItem<CelestialArmorItem>> stellar = List.of(HELMET, CHESTPLATE, LEGGINGS, BOOTS);
        for (int i = 0; i < 4; i++) {
            Item base = imperial.get(i);
            Item out = stellar.get(i).get();
            SKY_ALTAR_TYPE.add(new StationRecipe(s -> s.is(base), List.of(
                    new StationRecipe.Mat(Ingredient.of(STAR_CORE.get()), 1), new StationRecipe.Mat(Ingredient.of(STARDUST.get()), i == 1 ? 24 : 16)),
                    s -> Empire.upgrade(s, out)));
        }
    }

    public static void init() {
        ArmorSets.ability(SetId.STELLAR, new StellarAbilities());
        Professions.trade(Professions.RELIC_DEALER, 5, Professions.offer(Professions.coin(CoinTier.STAR), 1, STARDUST, 8, 6, 40));

        Emc.set(STARDUST, 800_000);
        Emc.set(DORMANT_STAR_CORE, 20_000_000);
        Emc.set(STAR_CORE, 40_000_000);
        Emc.set(STAR_COMPASS, 6_000_000);
        Emc.set(STARSTONE, 64);
        Emc.set(STARLIT_STARSTONE, 96);
        Emc.set(STARSTONE_BRICKS, 64);
        Emc.set(STAR_CRYSTAL, 4_096);
        Emc.set(HELMET, 120_000_000);
        Emc.set(CHESTPLATE, 192_000_000);
        Emc.set(LEGGINGS, 168_000_000);
        Emc.set(BOOTS, 96_000_000);
        Emc.set(SKY_ALTAR, 24_000_000);
    }
}
