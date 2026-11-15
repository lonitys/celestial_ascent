package com.celestialascent.economy;

import com.celestialascent.core.CAMenu;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.ContainerData;
import net.minecraft.world.inventory.SimpleContainerData;
import net.minecraft.world.item.ItemStack;
import org.jetbrains.annotations.Nullable;

import java.util.ArrayList;
import java.util.List;

/** Quest board menu: button i delivers quest i. Data slot 0 = completed bitmask. */
public class QuestMenu extends CAMenu {
    public final List<Quests.Quest> quests;
    @Nullable private final QuestBoardBlock.BoardEntity board;
    private final ContainerData data;

    public static QuestMenu client(int id, Inventory inv, RegistryFriendlyByteBuf buf) {
        int n = buf.readVarInt();
        List<Quests.Quest> qs = new ArrayList<>();
        for (int i = 0; i < n; i++) qs.add(Quests.Quest.read(buf));
        SimpleContainerData d = new SimpleContainerData(1);
        d.set(0, buf.readVarInt());
        return new QuestMenu(id, inv, null, qs, d);
    }

    public QuestMenu(int id, Inventory inv, QuestBoardBlock.BoardEntity board, List<Quests.Quest> quests) {
        this(id, inv, board, quests, new ContainerData() {
            @Override public int get(int i) { return board.completed; }
            @Override public void set(int i, int v) {}
            @Override public int getCount() { return 1; }
        });
    }

    private QuestMenu(int id, Inventory inv, @Nullable QuestBoardBlock.BoardEntity board, List<Quests.Quest> quests, ContainerData data) {
        super(Economy.QUEST_MENU.get(), id);
        this.board = board;
        this.quests = quests;
        this.data = data;
        addPlayerInventory(inv, 8, 104);
        addDataSlots(data);
    }

    public boolean done(int i) {
        return (data.get(0) & (1 << i)) != 0;
    }

    @Override
    public boolean clickMenuButton(Player player, int id) {
        if (board == null || !(player instanceof ServerPlayer sp) || id < 0 || id >= quests.size() || board.done(id)) return false;
        Quests.Quest q = quests.get(id);
        if (sp.getInventory().countItem(q.item()) < q.count()) {
            sp.displayClientMessage(Component.translatable("message.celestialascent.quest_missing", q.count(), q.item().getDescription()), true);
            return false;
        }
        int left = q.count();
        var inv = sp.getInventory();
        for (int i = 0; i < inv.getContainerSize() && left > 0; i++) {
            ItemStack s = inv.getItem(i);
            if (s.is(q.item())) {
                int t = Math.min(left, s.getCount());
                s.shrink(t);
                left -= t;
            }
        }
        board.markDone(id);
        Coins.give(sp, q.reward());
        sp.level().playSound(null, sp.blockPosition(), SoundEvents.VILLAGER_CELEBRATE, SoundSource.NEUTRAL, 1f, 1f);
        sp.level().playSound(null, sp.blockPosition(), SoundEvents.PLAYER_LEVELUP, SoundSource.PLAYERS, 0.6f, 1.4f);
        sp.giveExperiencePoints(Math.max(5, (int) (q.reward() / 10)));
        VillageGrowth.addProsperity((ServerLevel) sp.level(), board.getBlockPos(), q.prosperity(), sp);
        return true;
    }

    @Override
    public ItemStack quickMoveStack(Player player, int index) {
        return ItemStack.EMPTY;
    }

    @Override
    public boolean stillValid(Player player) {
        return board == null || (!board.isRemoved() && player.distanceToSqr(board.getBlockPos().getCenter()) <= 64);
    }
}
