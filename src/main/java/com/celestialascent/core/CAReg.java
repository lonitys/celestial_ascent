package com.celestialascent.core;

import com.celestialascent.CelestialAscent;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.village.poi.PoiType;
import net.minecraft.world.entity.npc.VillagerProfession;
import net.minecraft.world.inventory.MenuType;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.sounds.SoundEvent;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.attachment.AttachmentType;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.registries.NeoForgeRegistries;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;

/** Shared deferred registers. Content modules add entries from their own classes. */
public final class CAReg {
    private CAReg() {}
    private static final String M = CelestialAscent.MODID;

    public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(M);
    public static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(M);
    public static final DeferredRegister<BlockEntityType<?>> BLOCK_ENTITIES = DeferredRegister.create(Registries.BLOCK_ENTITY_TYPE, M);
    public static final DeferredRegister<EntityType<?>> ENTITIES = DeferredRegister.create(Registries.ENTITY_TYPE, M);
    public static final DeferredRegister<MenuType<?>> MENUS = DeferredRegister.create(Registries.MENU, M);
    public static final DeferredRegister.DataComponents COMPONENTS = DeferredRegister.createDataComponents(Registries.DATA_COMPONENT_TYPE, M);
    public static final DeferredRegister<AttachmentType<?>> ATTACHMENTS = DeferredRegister.create(NeoForgeRegistries.ATTACHMENT_TYPES, M);
    public static final DeferredRegister<ArmorMaterial> ARMOR_MATERIALS = DeferredRegister.create(Registries.ARMOR_MATERIAL, M);
    public static final DeferredRegister<CreativeModeTab> TABS = DeferredRegister.create(Registries.CREATIVE_MODE_TAB, M);
    public static final DeferredRegister<PoiType> POI = DeferredRegister.create(Registries.POINT_OF_INTEREST_TYPE, M);
    public static final DeferredRegister<VillagerProfession> PROFESSIONS = DeferredRegister.create(Registries.VILLAGER_PROFESSION, M);
    public static final DeferredRegister<SoundEvent> SOUNDS = DeferredRegister.create(Registries.SOUND_EVENT, M);
    public static final DeferredRegister<net.minecraft.world.level.levelgen.structure.StructureType<?>> STRUCTURE_TYPES =
            DeferredRegister.create(Registries.STRUCTURE_TYPE, M);

    /** The trade city: a jigsaw structure that only starts on flat, dry ground. */
    public static final DeferredHolder<net.minecraft.world.level.levelgen.structure.StructureType<?>,
            net.minecraft.world.level.levelgen.structure.StructureType<com.celestialascent.economy.CityStructure>> CITY_STRUCTURE =
            STRUCTURE_TYPES.register("city", () -> () -> com.celestialascent.economy.CityStructure.CODEC);

    /** Items shown in the creative tab, in registration order. */
    public static final List<Supplier<? extends net.minecraft.world.level.ItemLike>> TAB_ORDER = new ArrayList<>();

    public static final DeferredHolder<CreativeModeTab, CreativeModeTab> TAB = TABS.register("main", () -> CreativeModeTab.builder()
            .title(Component.translatable("itemGroup.celestialascent"))
            .icon(() -> new ItemStack(net.minecraft.core.registries.BuiltInRegistries.ITEM.get(
                    net.minecraft.resources.ResourceLocation.fromNamespaceAndPath(M, "ascendant_chestplate"))))
            .displayItems((params, out) -> TAB_ORDER.forEach(s -> out.accept(s.get())))
            .build());

    public static void register(IEventBus bus) {
        ITEMS.register(bus);
        BLOCKS.register(bus);
        BLOCK_ENTITIES.register(bus);
        ENTITIES.register(bus);
        MENUS.register(bus);
        COMPONENTS.register(bus);
        ATTACHMENTS.register(bus);
        ARMOR_MATERIALS.register(bus);
        TABS.register(bus);
        POI.register(bus);
        PROFESSIONS.register(bus);
        SOUNDS.register(bus);
        STRUCTURE_TYPES.register(bus);
    }
}
