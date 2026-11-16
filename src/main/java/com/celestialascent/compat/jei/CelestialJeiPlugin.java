package com.celestialascent.compat.jei;

import com.celestialascent.CelestialAscent;
import com.celestialascent.armor.ArmorStages;
import com.celestialascent.boss.BossSummons;
import com.celestialascent.boss.SummonAltarBlock;
import com.celestialascent.core.CAReg;
import com.celestialascent.core.station.StationBlock;
import com.celestialascent.core.station.StationMenu;
import com.celestialascent.core.station.StationRecipe;
import com.celestialascent.core.station.StationType;
import com.celestialascent.core.station.Stations;
import com.celestialascent.economy.CoinTier;
import com.celestialascent.economy.Economy;
import com.celestialascent.economy.Professions;
import com.celestialascent.empire.Empire;
import com.celestialascent.guide.Guide;
import com.celestialascent.stars.Stars;
import com.celestialascent.titans.Titans;
import mezz.jei.api.IModPlugin;
import mezz.jei.api.JeiPlugin;
import mezz.jei.api.constants.VanillaTypes;
import mezz.jei.api.helpers.IGuiHelper;
import mezz.jei.api.recipe.RecipeType;
import mezz.jei.api.recipe.transfer.IRecipeTransferInfo;
import mezz.jei.api.registration.IRecipeCatalystRegistration;
import mezz.jei.api.registration.IRecipeCategoryRegistration;
import mezz.jei.api.registration.IRecipeRegistration;
import mezz.jei.api.registration.IRecipeTransferRegistration;
import mezz.jei.api.runtime.IJeiRuntime;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.npc.VillagerProfession;
import net.minecraft.world.inventory.MenuType;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.ItemLike;
import net.minecraft.world.level.block.Block;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.function.Supplier;
import java.util.stream.Collectors;

/**
 * JEI support. Only JEI loads this class (through {@link JeiPlugin}); nothing else in the mod refers to
 * the {@code compat.jei} package except the dev-only showcase behind a mod-loaded check.
 */
@JeiPlugin
public final class CelestialJeiPlugin implements IModPlugin {
    private static final ResourceLocation UID = ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "jei");

    /** A profession with its workstation, for the trade categories. */
    private record Profession(String name, Supplier<VillagerProfession> profession, Supplier<? extends ItemLike> workstation) {}

    private static List<Profession> professions() {
        return List.of(new Profession("banker", Professions.BANKER, Economy.BANK_COUNTER),
                new Profession("titansmith", Professions.TITANSMITH, Economy.TITAN_ANVIL),
                new Profession("relic_dealer", Professions.RELIC_DEALER, Economy.RELIC_PEDESTAL));
    }

    /** Each station type with the block that hosts it. */
    private static Map<StationType, Block> stationBlocks() {
        Map<StationType, Block> out = new LinkedHashMap<>();
        for (var holder : Stations.BLOCKS) {
            StationBlock block = holder.get();
            out.putIfAbsent(block.type(), block);
        }
        return out;
    }

    @Override
    public ResourceLocation getPluginUid() {
        return UID;
    }

    @Override
    public void registerCategories(IRecipeCategoryRegistration registration) {
        IGuiHelper gui = registration.getJeiHelpers().getGuiHelper();
        stationBlocks().forEach((type, block) -> registration.addRecipeCategories(new StationCategory(gui, type, block)));
        registration.addRecipeCategories(new SummonCategory(gui));
        for (Profession p : professions()) registration.addRecipeCategories(new TradeCategory(gui, p.name(), p.workstation().get()));
    }

    @Override
    public void registerRecipes(IRecipeRegistration registration) {
        for (StationType type : stationBlocks().keySet()) {
            List<StationRecipe.Example> examples = new ArrayList<>();
            for (StationRecipe r : type.recipes) examples.addAll(r.examples().get());
            // Upgrades first, then armor evolutions (the modules add their recipes in no fixed order).
            examples.sort(Comparator.comparing(e -> ArmorStages.stage(e.base()) > 0 && ArmorStages.ready(e.base())));
            registration.addRecipes(StationCategory.type(type), examples);
        }
        registration.addRecipes(SummonCategory.TYPE, BossSummons.all());
        for (Profession p : professions()) registration.addRecipes(TradeCategory.type(p.name()), Professions.displays(p.profession()));

        info(registration, Economy.COINS.values().stream().map(c -> new ItemStack(c.get())).toList(), "coins");
        info(registration, List.of(new ItemStack(Empire.DRAGON_HEART.get())), "dragon_heart");
        info(registration, List.of(new ItemStack(Stars.DORMANT_STAR_CORE.get())), "dormant_star_core");
        info(registration, List.of(new ItemStack(Economy.SHOP_STALL.get())), "shop_stall");
        info(registration, List.of(new ItemStack(Economy.QUEST_BOARD.get())), "quest_board");
        info(registration, List.of(new ItemStack(Economy.BANK_COUNTER.get())), "bank_counter");
        info(registration, List.of(new ItemStack(Guide.CODEX.get())), "codex");
        info(registration, ArmorStages.pieces().stream().map(ItemStack::new).toList(), "armor");
        // The Celestial Crystal belongs to the trade city update; look it up so this builds without it.
        Optional<Item> crystal = BuiltInRegistries.ITEM.getOptional(ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "celestial_crystal"));
        crystal.ifPresent(item -> info(registration, List.of(new ItemStack(item)), "celestial_crystal"));
    }

    private static void info(IRecipeRegistration registration, List<ItemStack> stacks, String key) {
        registration.addItemStackInfo(stacks, Component.translatable("jei.celestialascent.info." + key));
    }

    @Override
    public void registerRecipeCatalysts(IRecipeCatalystRegistration registration) {
        stationBlocks().forEach((type, block) -> registration.addRecipeCatalyst(block, StationCategory.type(type)));
        for (var altar : Titans.ALTARS.values()) registration.addRecipeCatalyst(altar.get(), SummonCategory.TYPE);
        registration.addRecipeCatalyst(Empire.PYLON.get(), SummonCategory.TYPE);
        registration.addRecipeCatalyst(Empire.THRONE.get(), SummonCategory.TYPE);
        for (Supplier<? extends Block> altar : SummonAltarBlock.ALL) registration.addRecipeCatalyst(altar.get(), SummonCategory.TYPE);
        registration.addRecipeCatalyst(com.celestialascent.abyss.Abyss.ABYSSAL_BEACON.get(), SummonCategory.TYPE);
        for (Profession p : professions()) registration.addRecipeCatalyst(p.workstation().get(), TradeCategory.type(p.name()));
    }

    @Override
    public void registerRecipeTransferHandlers(IRecipeTransferRegistration registration) {
        for (StationType type : stationBlocks().keySet()) registration.addRecipeTransferHandler(new StationTransfer(type));
    }

    /** The + button: base and materials go into the station's slots (menu order: base, materials, output, inventory). */
    private record StationTransfer(StationType station) implements IRecipeTransferInfo<StationMenu, StationRecipe.Example> {
        @Override
        public Class<? extends StationMenu> getContainerClass() {
            return StationMenu.class;
        }

        @Override
        public Optional<MenuType<StationMenu>> getMenuType() {
            return Optional.of(Stations.MENU.get());
        }

        @Override
        public RecipeType<StationRecipe.Example> getRecipeType() {
            return StationCategory.type(station);
        }

        @Override
        public boolean canHandle(StationMenu menu, StationRecipe.Example recipe) {
            return menu.type == station; // every station shares one menu type
        }

        @Override
        public List<Slot> getRecipeSlots(StationMenu menu, StationRecipe.Example recipe) {
            return menu.slots.subList(0, 1 + station.mats.length);
        }

        @Override
        public List<Slot> getInventorySlots(StationMenu menu, StationRecipe.Example recipe) {
            return menu.slots.subList(station.size(), station.size() + 36);
        }

        /**
         * Complete sets cap every slot at the smallest stack limit among them: the armor piece (1) would
         * leave a single shard. Each slot gets the count the recipe shows instead.
         */
        @Override
        public boolean requireCompleteSets(StationMenu menu, StationRecipe.Example recipe) {
            return false;
        }
    }

    @Override
    public void onRuntimeAvailable(IJeiRuntime runtime) {
        JeiShowcase.runtime = runtime;
        // Technical blocks (cooled magma, the star portal) have no item. Hide anything else of ours that the
        // creative tab leaves out, so the JEI list matches the tab.
        Set<Item> inTab = CAReg.TAB_ORDER.stream().map(s -> s.get().asItem()).collect(Collectors.toSet());
        List<ItemStack> hidden = CAReg.ITEMS.getEntries().stream().map(h -> h.get()).filter(i -> !inTab.contains(i) && i != Items.AIR)
                .map(ItemStack::new).toList();
        if (!hidden.isEmpty()) runtime.getIngredientManager().removeIngredientsAtRuntime(VanillaTypes.ITEM_STACK, hidden);
    }

    @Override
    public void onRuntimeUnavailable() {
        JeiShowcase.runtime = null;
    }
}
