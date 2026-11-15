package com.celestialascent.economy;

import com.celestialascent.core.FacingBlock;
import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.Shapes;
import org.jetbrains.annotations.Nullable;

import java.util.List;

/** Village quest board: three daily delivery quests paying coins and village prosperity. */
public class QuestBoardBlock extends FacingBlock implements EntityBlock {
    public QuestBoardBlock(Properties props) {
        super(props, Shapes.box(0, 0, 0.75, 1, 1, 1));
    }

    @Override
    protected MapCodec<? extends HorizontalDirectionalBlock> codec() {
        return simpleCodec(QuestBoardBlock::new);
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new BoardEntity(pos, state);
    }

    public static long day(Level level) {
        return level.getDayTime() / 24000L;
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (!level.isClientSide && player instanceof ServerPlayer sp && level.getBlockEntity(pos) instanceof BoardEntity be) {
            be.refresh(level);
            List<Quests.Quest> quests = Quests.forBoard(pos, day(level));
            sp.openMenu(new SimpleMenuProvider((id, inv, p) -> new QuestMenu(id, inv, be, quests),
                    Component.translatable("container.celestialascent.quest_board")), buf -> {
                buf.writeVarInt(quests.size());
                for (Quests.Quest q : quests) q.write(buf);
                buf.writeVarInt(be.completed);
            });
        }
        return InteractionResult.sidedSuccess(level.isClientSide);
    }

    /** Tracks which of today's quests were completed at this board. */
    public static class BoardEntity extends BlockEntity {
        long day = -1;
        int completed;

        public BoardEntity(BlockPos pos, BlockState state) {
            super(Economy.QUEST_BOARD_BE.get(), pos, state);
        }

        void refresh(Level level) {
            long d = day(level);
            if (d != day) {
                day = d;
                completed = 0;
                setChanged();
            }
        }

        boolean done(int i) {
            return (completed & (1 << i)) != 0;
        }

        void markDone(int i) {
            completed |= 1 << i;
            setChanged();
        }

        @Override
        protected void saveAdditional(CompoundTag tag, HolderLookup.Provider lookup) {
            super.saveAdditional(tag, lookup);
            tag.putLong("Day", day);
            tag.putInt("Completed", completed);
        }

        @Override
        protected void loadAdditional(CompoundTag tag, HolderLookup.Provider lookup) {
            super.loadAdditional(tag, lookup);
            day = tag.getLong("Day");
            completed = tag.getInt("Completed");
        }
    }
}
