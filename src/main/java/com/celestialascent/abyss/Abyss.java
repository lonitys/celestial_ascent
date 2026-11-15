package com.celestialascent.abyss;

import com.celestialascent.CelestialAscent;
import com.celestialascent.armor.ArmorSets;
import com.celestialascent.armor.CelestialArmorItem;
import com.celestialascent.armor.SetId;
import com.celestialascent.compat.Emc;
import com.celestialascent.core.CAReg;
import com.celestialascent.core.Content;
import com.celestialascent.core.Travel;
import com.celestialascent.core.station.StationBlock;
import com.celestialascent.core.station.StationRecipe;
import com.celestialascent.core.station.StationType;
import com.celestialascent.core.station.Stations;
import com.celestialascent.economy.CoinTier;
import com.celestialascent.economy.Professions;
import com.celestialascent.empire.Empire;
import com.celestialascent.progress.Progress;
import com.celestialascent.stars.Stars;
import net.minecraft.core.BlockPos;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.valueproviders.UniformInt;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.SpawnPlacementTypes;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.block.DropExperienceBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.phys.Vec3;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;
import net.neoforged.neoforge.common.NeoForgeMod;
import net.neoforged.neoforge.event.entity.EntityAttributeCreationEvent;
import net.neoforged.neoforge.event.entity.RegisterSpawnPlacementsEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredItem;

import java.util.List;

/** Step 4 and the finale: the Abyss, the Void Sovereign, Void armor and Ascendant armor. */
@EventBusSubscriber(modid = CelestialAscent.MODID)
public final class Abyss {
    private Abyss() {}

    public static final DeferredBlock<AbyssalStoneBlock> ABYSSAL_STONE = Content.block("abyssal_stone",
            () -> new AbyssalStoneBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_BLACK).strength(3f, 6f)
                    .requiresCorrectToolForDrops().sound(SoundType.DEEPSLATE)));
    public static final DeferredBlock<DropExperienceBlock> VOID_ESSENCE_ORE = Content.block("void_essence_ore",
            () -> new DropExperienceBlock(UniformInt.of(6, 12), BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_PURPLE).strength(5f, 9f)
                    .requiresCorrectToolForDrops().sound(SoundType.DEEPSLATE).lightLevel(s -> 9)));

    public static final DeferredItem<Item> VOID_ESSENCE = Content.item("void_essence", () -> new Item(new Item.Properties().rarity(Rarity.EPIC)));
    public static final DeferredItem<Item> VOID_HEART = Content.item("void_heart",
            () -> new Item(new Item.Properties().rarity(Rarity.EPIC).fireResistant().stacksTo(1).component(DataComponents.ENCHANTMENT_GLINT_OVERRIDE, true)));
    public static final DeferredItem<Item> PRIMORDIAL_CORE = Content.item("primordial_core",
            () -> new Item(new Item.Properties().rarity(Rarity.EPIC).fireResistant().stacksTo(16).component(DataComponents.ENCHANTMENT_GLINT_OVERRIDE, true)));
    public static final DeferredItem<AbyssItems.AbyssalBeacon> ABYSSAL_BEACON = Content.item("abyssal_beacon",
            () -> new AbyssItems.AbyssalBeacon(new Item.Properties().rarity(Rarity.EPIC).stacksTo(1).fireResistant()));
    public static final DeferredItem<AbyssItems.AscensionPearl> ASCENSION_PEARL = Content.item("ascension_pearl",
            () -> new AbyssItems.AscensionPearl(new Item.Properties().rarity(Rarity.RARE).stacksTo(16)));

    public static final DeferredItem<CelestialArmorItem> VOID_HELMET = Content.item("void_helmet", () -> new CelestialArmorItem(SetId.VOID, ArmorItem.Type.HELMET, new Item.Properties()));
    public static final DeferredItem<CelestialArmorItem> VOID_CHESTPLATE = Content.item("void_chestplate", () -> new CelestialArmorItem(SetId.VOID, ArmorItem.Type.CHESTPLATE, new Item.Properties()));
    public static final DeferredItem<CelestialArmorItem> VOID_LEGGINGS = Content.item("void_leggings", () -> new CelestialArmorItem(SetId.VOID, ArmorItem.Type.LEGGINGS, new Item.Properties()));
    public static final DeferredItem<CelestialArmorItem> VOID_BOOTS = Content.item("void_boots", () -> new CelestialArmorItem(SetId.VOID, ArmorItem.Type.BOOTS, new Item.Properties()));
    public static final DeferredItem<CelestialArmorItem> ASC_HELMET = Content.item("ascendant_helmet", () -> new CelestialArmorItem(SetId.ASCENDANT, ArmorItem.Type.HELMET, new Item.Properties()));
    public static final DeferredItem<CelestialArmorItem> ASC_CHESTPLATE = Content.item("ascendant_chestplate", () -> new CelestialArmorItem(SetId.ASCENDANT, ArmorItem.Type.CHESTPLATE, new Item.Properties()));
    public static final DeferredItem<CelestialArmorItem> ASC_LEGGINGS = Content.item("ascendant_leggings", () -> new CelestialArmorItem(SetId.ASCENDANT, ArmorItem.Type.LEGGINGS, new Item.Properties()));
    public static final DeferredItem<CelestialArmorItem> ASC_BOOTS = Content.item("ascendant_boots", () -> new CelestialArmorItem(SetId.ASCENDANT, ArmorItem.Type.BOOTS, new Item.Properties()));

    public static final StationType INFUSER = new StationType("void_infuser", 300,
            new int[]{30, 35}, new int[][]{{66, 17}, {66, 53}}, new int[]{124, 35}, new int[]{90, 35});
    public static final DeferredBlock<StationBlock> VOID_INFUSER = Stations.register("void_infuser",
            () -> new StationBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_PURPLE).strength(6f, 1200f).sound(SoundType.SCULK_CATALYST)
                    .requiresCorrectToolForDrops().noOcclusion().lightLevel(s -> 10), () -> INFUSER));
    public static final StationType ASCENSION = new StationType("ascension_altar", 600,
            new int[]{30, 35}, new int[][]{{66, 17}, {66, 35}, {66, 53}}, new int[]{124, 35}, new int[]{90, 35});
    public static final DeferredBlock<StationBlock> ASCENSION_ALTAR = Stations.register("ascension_altar",
            () -> new StationBlock(BlockBehaviour.Properties.of().mapColor(MapColor.GOLD).strength(8f, 3600000f).sound(SoundType.AMETHYST)
                    .requiresCorrectToolForDrops().noOcclusion().lightLevel(s -> 15), () -> ASCENSION));

    public static final DeferredHolder<EntityType<?>, EntityType<VoidWraith>> VOID_WRAITH = CAReg.ENTITIES.register("void_wraith",
            () -> EntityType.Builder.of(VoidWraith::new, MobCategory.MONSTER).sized(0.5f, 0.9f).fireImmune().clientTrackingRange(8).build("void_wraith"));
    public static final DeferredHolder<EntityType<?>, EntityType<VoidSovereign>> VOID_SOVEREIGN = CAReg.ENTITIES.register("void_sovereign",
            () -> EntityType.Builder.of(VoidSovereign::new, MobCategory.MONSTER).sized(2.6f, 5.4f).fireImmune().clientTrackingRange(12).build("void_sovereign"));

    @SubscribeEvent
    public static void attributes(EntityAttributeCreationEvent e) {
        e.put(VOID_WRAITH.get(), VoidWraith.attributes().build());
        e.put(VOID_SOVEREIGN.get(), VoidSovereign.attributes().build());
    }

    @SubscribeEvent
    public static void spawns(RegisterSpawnPlacementsEvent e) {
        e.register(VOID_WRAITH.get(), SpawnPlacementTypes.NO_RESTRICTIONS, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                Monster::checkAnyLightMonsterSpawnRules, RegisterSpawnPlacementsEvent.Operation.REPLACE);
    }

    @SubscribeEvent
    public static void setup(FMLCommonSetupEvent e) {
        e.enqueueWork(Abyss::recipes);
    }

    static void recipes() {
        List<Item> stellar = List.of(Stars.HELMET.get(), Stars.CHESTPLATE.get(), Stars.LEGGINGS.get(), Stars.BOOTS.get());
        List<Item> voidSet = List.of(VOID_HELMET.get(), VOID_CHESTPLATE.get(), VOID_LEGGINGS.get(), VOID_BOOTS.get());
        List<Item> asc = List.of(ASC_HELMET.get(), ASC_CHESTPLATE.get(), ASC_LEGGINGS.get(), ASC_BOOTS.get());
        for (int i = 0; i < 4; i++) {
            Item base = stellar.get(i), out = voidSet.get(i);
            INFUSER.add(new StationRecipe(s -> s.is(base), List.of(
                    new StationRecipe.Mat(Ingredient.of(VOID_ESSENCE.get()), i == 1 ? 12 : 8), new StationRecipe.Mat(Ingredient.of(Stars.STARDUST.get()), 8)),
                    s -> Empire.upgrade(s, out)));
            Item vb = voidSet.get(i), ao = asc.get(i);
            StationRecipe.Mat third = i == 1 ? new StationRecipe.Mat(Ingredient.of(VOID_HEART.get()), 1) : new StationRecipe.Mat(Ingredient.of(VOID_ESSENCE.get()), 16);
            ASCENSION.add(new StationRecipe(s -> s.is(vb), List.of(
                    new StationRecipe.Mat(Ingredient.of(PRIMORDIAL_CORE.get()), 1), new StationRecipe.Mat(Ingredient.of(Stars.STAR_CORE.get()), 1), third),
                    s -> Empire.upgrade(s, ao)));
        }
    }

    /** Falling out of the Fallen Stars drops a worthy player into the Abyss. */
    @SubscribeEvent
    public static void fallIntoAbyss(PlayerTickEvent.Post e) {
        if (!(e.getEntity() instanceof ServerPlayer p) || p.level().dimension() != Travel.FALLEN_STARS || p.getY() > -24) return;
        if (!Progress.has(p, ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "sun_herald"))) {
            if (p.tickCount % 20 == 0) p.displayClientMessage(Component.translatable("message.celestialascent.abyss_rejects"), true);
            return;
        }
        ServerLevel abyss = p.server.getLevel(Travel.ABYSS);
        if (abyss == null) return;
        BlockPos stand = cavePos(abyss, p.getBlockX(), p.getBlockZ());
        Travel.teleport(p, abyss, Vec3.atBottomCenterOf(stand));
        p.displayClientMessage(Component.translatable("message.celestialascent.abyss_enter").withColor(0xB45CFF), false);
    }

    /** First open pocket (solid floor, two air blocks) scanning down from the upper Abyss, else a platform. */
    static BlockPos cavePos(ServerLevel level, int x, int z) {
        level.getChunk(x >> 4, z >> 4);
        for (int dx = 0; dx <= 24; dx += 4) {
            for (int y = 110; y > level.getMinBuildHeight() + 8; y--) {
                BlockPos p = new BlockPos(x + dx, y, z);
                if (level.getBlockState(p).isAir() && level.getBlockState(p.above()).isAir() && level.getBlockState(p.below()).isSolid()) return p;
            }
        }
        return Travel.platform(level, new BlockPos(x, 100, z), ABYSSAL_STONE.get().defaultBlockState(), 2);
    }

    public static void init() {
        ArmorSets.ability(SetId.VOID, new VoidAbilities());
        ArmorSets.ability(SetId.ASCENDANT, new AscendantAbilities());
        ArmorSets.bonus(SetId.VOID, Attributes.MOVEMENT_SPEED, "speed", 0.1, AttributeModifier.Operation.ADD_MULTIPLIED_BASE);
        ArmorSets.bonus(SetId.VOID, Attributes.MAX_HEALTH, "health", 4, AttributeModifier.Operation.ADD_VALUE);

        ArmorSets.bonus(SetId.ASCENDANT, NeoForgeMod.CREATIVE_FLIGHT, "flight", 1, AttributeModifier.Operation.ADD_VALUE);
        ArmorSets.bonus(SetId.ASCENDANT, Attributes.STEP_HEIGHT, "step", 0.6, AttributeModifier.Operation.ADD_VALUE);
        ArmorSets.bonus(SetId.ASCENDANT, Attributes.MOVEMENT_SPEED, "speed", 0.25, AttributeModifier.Operation.ADD_MULTIPLIED_BASE);
        ArmorSets.bonus(SetId.ASCENDANT, Attributes.MAX_HEALTH, "health", 20, AttributeModifier.Operation.ADD_VALUE);
        ArmorSets.bonus(SetId.ASCENDANT, Attributes.ATTACK_DAMAGE, "damage", 6, AttributeModifier.Operation.ADD_VALUE);
        ArmorSets.bonus(SetId.ASCENDANT, Attributes.ATTACK_SPEED, "attack_speed", 0.25, AttributeModifier.Operation.ADD_MULTIPLIED_BASE);
        ArmorSets.bonus(SetId.ASCENDANT, Attributes.ENTITY_INTERACTION_RANGE, "reach", 2, AttributeModifier.Operation.ADD_VALUE);
        ArmorSets.bonus(SetId.ASCENDANT, Attributes.BLOCK_INTERACTION_RANGE, "block_reach", 2, AttributeModifier.Operation.ADD_VALUE);
        ArmorSets.bonus(SetId.ASCENDANT, Attributes.BLOCK_BREAK_SPEED, "mining", 0.5, AttributeModifier.Operation.ADD_MULTIPLIED_BASE);
        ArmorSets.bonus(SetId.ASCENDANT, Attributes.LUCK, "luck", 2, AttributeModifier.Operation.ADD_VALUE);

        Professions.trade(Professions.RELIC_DEALER, 5, Professions.offer(Professions.coin(CoinTier.VOID), 1, VOID_ESSENCE, 6, 4, 50));

        Emc.set(VOID_ESSENCE, 5_000_000);
        Emc.set(VOID_HEART, 250_000_000);
        Emc.set(PRIMORDIAL_CORE, 30_000_000);
        Emc.set(ABYSSAL_BEACON, 90_000_000);
        Emc.set(ASCENSION_PEARL, 6_000_000);
        Emc.set(ABYSSAL_STONE, 64);
        Emc.set(VOID_HELMET, 250_000_000);
        Emc.set(VOID_CHESTPLATE, 400_000_000);
        Emc.set(VOID_LEGGINGS, 350_000_000);
        Emc.set(VOID_BOOTS, 200_000_000);
        Emc.set(ASC_HELMET, 1_000_000_000L);
        Emc.set(ASC_CHESTPLATE, 1_600_000_000L);
        Emc.set(ASC_LEGGINGS, 1_400_000_000L);
        Emc.set(ASC_BOOTS, 800_000_000L);
        Emc.set(VOID_INFUSER, 40_000_000);
        Emc.set(ASCENSION_ALTAR, 150_000_000);
    }
}
