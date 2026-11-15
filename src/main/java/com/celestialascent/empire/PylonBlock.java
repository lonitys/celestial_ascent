package com.celestialascent.empire;

import com.celestialascent.economy.CoinTier;
import com.celestialascent.economy.Coins;
import com.celestialascent.economy.Professions;
import com.mojang.serialization.MapCodec;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.util.StringRepresentable;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.npc.Villager;
import net.minecraft.world.entity.npc.VillagerData;
import net.minecraft.world.entity.npc.VillagerType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jetbrains.annotations.Nullable;

/**
 * Imperial Pylon of the Ruined Capital. While broken it calls Sentinel Constructs to defend it.
 * Restoring it (Imperial Plating, purpur and coins) unlocks its reward: the Imperial Forge,
 * an Ender merchant, or the opening of the Throne Hall.
 */
public class PylonBlock extends Block implements EntityBlock {
    public enum Kind implements StringRepresentable {
        CRAFT, TRADE, THRONE;

        @Override
        public String getSerializedName() {
            return name().toLowerCase();
        }
    }

    public static final EnumProperty<Kind> KIND = EnumProperty.create("kind", Kind.class);
    public static final BooleanProperty RESTORED = BooleanProperty.create("restored");
    public static final int PLATING = 4, PURPUR = 16;
    public static final long COST = CoinTier.TITAN.value * 3;
    private static final VoxelShape SHAPE = Shapes.or(Shapes.box(0.125, 0, 0.125, 0.875, 0.25, 0.875), Shapes.box(0.25, 0.25, 0.25, 0.75, 1, 0.75));

    public PylonBlock(Properties props) {
        super(props);
        registerDefaultState(stateDefinition.any().setValue(KIND, Kind.CRAFT).setValue(RESTORED, false));
    }

    @Override
    protected MapCodec<? extends Block> codec() {
        return simpleCodec(PylonBlock::new);
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
        b.add(KIND, RESTORED);
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
        return SHAPE;
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new PylonBlockEntity(pos, state);
    }

    @Nullable
    @Override
    @SuppressWarnings("unchecked")
    public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level level, BlockState state, BlockEntityType<T> type) {
        if (level.isClientSide || state.getValue(RESTORED) || type != Empire.PYLON_BE.get()) return null;
        return (l, p, s, be) -> ((PylonBlockEntity) be).serverTick((ServerLevel) l, p);
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (state.getValue(RESTORED)) {
            for (int i = 0; i < 3; i++) {
                level.addParticle(ParticleTypes.END_ROD, pos.getX() + 0.5 + random.nextGaussian() * 0.1, pos.getY() + 1 + random.nextFloat() * 6,
                        pos.getZ() + 0.5 + random.nextGaussian() * 0.1, 0, 0.15, 0);
            }
        } else if (random.nextInt(3) == 0) {
            level.addParticle(ParticleTypes.REVERSE_PORTAL, pos.getX() + random.nextFloat(), pos.getY() + 1.1, pos.getZ() + random.nextFloat(), 0, 0.02, 0);
        }
    }

    private static int count(Player p, Item item) {
        return p.getInventory().countItem(item);
    }

    private static void take(Player p, Item item, int n) {
        var inv = p.getInventory();
        for (int i = 0; i < inv.getContainerSize() && n > 0; i++) {
            ItemStack s = inv.getItem(i);
            if (s.is(item)) {
                int t = Math.min(n, s.getCount());
                s.shrink(t);
                n -= t;
            }
        }
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (level.isClientSide) return InteractionResult.SUCCESS;
        if (state.getValue(RESTORED)) {
            player.displayClientMessage(Component.translatable("message.celestialascent.pylon_restored." + state.getValue(KIND).getSerializedName()), true);
            return InteractionResult.CONSUME;
        }
        if (!level.getEntitiesOfClass(SentinelConstruct.class, new AABB(pos).inflate(24)).isEmpty()) {
            player.displayClientMessage(Component.translatable("message.celestialascent.pylon_guarded").withStyle(ChatFormatting.RED), true);
            return InteractionResult.CONSUME;
        }
        boolean creative = player.getAbilities().instabuild;
        boolean hasItems = count(player, Empire.IMPERIAL_PLATING.get()) >= PLATING && count(player, Items.PURPUR_BLOCK) >= PURPUR;
        long money = Coins.countInventory(player) + (player instanceof ServerPlayer sp ? com.celestialascent.economy.Bank.get(sp.server).balance(sp.getUUID()) : 0);
        if (!creative && (!hasItems || money < COST)) {
            player.sendSystemMessage(Component.translatable("message.celestialascent.pylon_needs", PLATING, PURPUR, Coins.format(COST)).withStyle(ChatFormatting.LIGHT_PURPLE));
            return InteractionResult.CONSUME;
        }
        if (!creative) {
            take(player, Empire.IMPERIAL_PLATING.get(), PLATING);
            take(player, Items.PURPUR_BLOCK, PURPUR);
            Coins.pay(player, COST);
        }
        restore((ServerLevel) level, pos, state);
        return InteractionResult.CONSUME;
    }

    public static void restore(ServerLevel level, BlockPos pos, BlockState state) {
        level.setBlockAndUpdate(pos, state.setValue(RESTORED, true));
        level.playSound(null, pos, SoundEvents.BEACON_ACTIVATE, SoundSource.BLOCKS, 3f, 0.8f);
        level.playSound(null, pos, SoundEvents.END_PORTAL_SPAWN, SoundSource.BLOCKS, 1f, 1.4f);
        level.sendParticles(ParticleTypes.END_ROD, pos.getX() + 0.5, pos.getY() + 2, pos.getZ() + 0.5, 120, 0.4, 3, 0.4, 0.05);
        switch (state.getValue(KIND)) {
            case CRAFT -> {
                ItemEntity forge = new ItemEntity(level, pos.getX() + 0.5, pos.getY() + 1.5, pos.getZ() + 0.5, new ItemStack(Empire.IMPERIAL_FORGE.get()));
                forge.setGlowingTag(true);
                level.addFreshEntity(forge);
            }
            case TRADE -> {
                Villager v = EntityType.VILLAGER.create(level);
                if (v != null) {
                    v.setVillagerData(new VillagerData(VillagerType.PLAINS, Professions.RELIC_DEALER.get(), 5));
                    v.setVillagerXp(250);
                    v.setPersistenceRequired();
                    v.setCustomName(Component.translatable("entity.celestialascent.ender_merchant"));
                    v.moveTo(pos.getX() + 2.5, pos.getY(), pos.getZ() + 0.5, 0, 0);
                    level.addFreshEntity(v);
                }
            }
            case THRONE -> {
                BlockPos.MutableBlockPos m = new BlockPos.MutableBlockPos();
                int removed = 0;
                for (int x = -48; x <= 48; x++)
                    for (int y = -16; y <= 24; y++)
                        for (int z = -48; z <= 48; z++) {
                            m.set(pos.getX() + x, pos.getY() + y, pos.getZ() + z);
                            if (level.getBlockState(m).is(Empire.IMPERIAL_BARRIER.get())) {
                                level.setBlock(m, net.minecraft.world.level.block.Blocks.AIR.defaultBlockState(), 3);
                                if (++removed % 4 == 0) level.sendParticles(ParticleTypes.REVERSE_PORTAL, m.getX() + 0.5, m.getY() + 0.5, m.getZ() + 0.5, 6, 0.3, 0.3, 0.3, 0.05);
                            }
                        }
                level.playSound(null, pos, SoundEvents.IRON_DOOR_OPEN, SoundSource.BLOCKS, 3f, 0.5f);
            }
        }
        Component msg = Component.translatable("message.celestialascent.pylon_restore." + state.getValue(KIND).getSerializedName()).withColor(0xC77DFF);
        for (Player p : level.getEntitiesOfClass(Player.class, new AABB(pos).inflate(64))) p.sendSystemMessage(msg);
    }

    /** Spawns a Sentinel Construct when players approach an unrestored pylon (3 min cooldown). */
    public static class PylonBlockEntity extends BlockEntity {
        private long lastSpawn = -100000;

        public PylonBlockEntity(BlockPos pos, BlockState state) {
            super(Empire.PYLON_BE.get(), pos, state);
        }

        void serverTick(ServerLevel level, BlockPos pos) {
            if (level.getGameTime() % 40 != 0 || level.getGameTime() - lastSpawn < 3600) return;
            AABB near = new AABB(pos).inflate(14);
            if (level.getEntitiesOfClass(Player.class, near, p -> !p.isSpectator() && !p.isCreative()).isEmpty()) return;
            if (!level.getEntitiesOfClass(SentinelConstruct.class, new AABB(pos).inflate(32)).isEmpty()) return;
            SentinelConstruct s = Empire.SENTINEL.get().create(level);
            if (s == null) return;
            s.moveTo(pos.getX() + 0.5, pos.getY() + 1, pos.getZ() + 3.5, 180, 0);
            s.setHome(pos);
            level.addFreshEntity(s);
            level.sendParticles(ParticleTypes.REVERSE_PORTAL, s.getX(), s.getY() + 1.5, s.getZ(), 60, 0.6, 1.2, 0.6, 0.1);
            level.playSound(null, pos, SoundEvents.IRON_GOLEM_REPAIR, SoundSource.HOSTILE, 2f, 0.5f);
            lastSpawn = level.getGameTime();
            setChanged();
        }

        @Override
        protected void saveAdditional(CompoundTag tag, HolderLookup.Provider lookup) {
            super.saveAdditional(tag, lookup);
            tag.putLong("LastSpawn", lastSpawn);
        }

        @Override
        protected void loadAdditional(CompoundTag tag, HolderLookup.Provider lookup) {
            super.loadAdditional(tag, lookup);
            lastSpawn = tag.getLong("LastSpawn");
        }
    }
}
