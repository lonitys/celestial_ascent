package com.celestialascent.economy;

import com.celestialascent.core.CAReg;
import com.celestialascent.core.Content;
import com.celestialascent.core.FacingBlock;
import net.minecraft.world.flag.FeatureFlags;
import net.minecraft.world.inventory.MenuType;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.phys.shapes.Shapes;
import net.neoforged.neoforge.common.extensions.IMenuTypeExtension;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredItem;

import java.util.EnumMap;
import java.util.Map;

/** Economy content: Aster coins, bank, shop stalls and profession workstations. */
public final class Economy {
    private Economy() {}

    public static final Map<CoinTier, DeferredItem<CoinItem>> COINS = new EnumMap<>(CoinTier.class);

    static {
        for (CoinTier t : CoinTier.values()) COINS.put(t, Content.item(t.id, () -> new CoinItem(t)));
    }

    public static final DeferredBlock<BankCounterBlock> BANK_COUNTER = Content.block("bank_counter",
            () -> new BankCounterBlock(BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(2.5f).sound(SoundType.WOOD).noOcclusion()));

    public static final DeferredBlock<ShopStallBlock> SHOP_STALL = Content.block("shop_stall",
            () -> new ShopStallBlock(BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(2.5f, 3600000f).sound(SoundType.WOOD).noOcclusion()));

    public static final DeferredBlock<FacingBlock> TITAN_ANVIL = Content.block("titan_anvil",
            () -> new FacingBlock(BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(5f, 1200f).sound(SoundType.ANVIL)
                    .requiresCorrectToolForDrops().noOcclusion(),
                    Shapes.or(Shapes.box(0.125, 0, 0.125, 0.875, 0.25, 0.875), Shapes.box(0.25, 0.25, 0.3125, 0.75, 0.625, 0.6875),
                            Shapes.box(0, 0.625, 0.1875, 1, 1, 0.8125))));

    public static final DeferredBlock<FacingBlock> RELIC_PEDESTAL = Content.block("relic_pedestal",
            () -> new FacingBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_PURPLE).strength(4f, 1200f).sound(SoundType.AMETHYST)
                    .requiresCorrectToolForDrops().noOcclusion().lightLevel(s -> 10),
                    Shapes.or(Shapes.box(0.125, 0, 0.125, 0.875, 0.1875, 0.875), Shapes.box(0.25, 0.1875, 0.25, 0.75, 0.75, 0.75),
                            Shapes.box(0.125, 0.75, 0.125, 0.875, 0.875, 0.875))));

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<ShopStallBlockEntity>> SHOP_STALL_BE =
            CAReg.BLOCK_ENTITIES.register("shop_stall", () -> BlockEntityType.Builder.of(ShopStallBlockEntity::new, SHOP_STALL.get()).build(null));

    public static final DeferredHolder<MenuType<?>, MenuType<BankMenu>> BANK_MENU =
            CAReg.MENUS.register("bank", () -> new MenuType<>(BankMenu::new, FeatureFlags.DEFAULT_FLAGS));

    public static final DeferredHolder<MenuType<?>, MenuType<ShopMenu>> SHOP_MENU =
            CAReg.MENUS.register("shop", () -> IMenuTypeExtension.create(ShopMenu::client));

    public static Item coin(CoinTier tier) {
        return COINS.get(tier).get();
    }

    public static void init() {
        Professions.init();
    }
}
