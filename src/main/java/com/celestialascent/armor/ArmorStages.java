package com.celestialascent.armor;

import com.celestialascent.CelestialAscent;
import com.celestialascent.abyss.Abyss;
import com.celestialascent.boss.CelestialBoss;
import com.celestialascent.core.CAReg;
import com.celestialascent.core.station.StationRecipe;
import com.celestialascent.core.station.StationType;
import com.celestialascent.empire.Empire;
import com.celestialascent.stars.Stars;
import com.celestialascent.titans.Element;
import com.celestialascent.titans.TitanArmorItem;
import com.celestialascent.titans.Titans;
import com.mojang.serialization.Codec;
import net.minecraft.ChatFormatting;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.EquipmentSlotGroup;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.boss.enderdragon.EnderDragon;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.ItemLike;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;
import net.neoforged.neoforge.event.ItemAttributeModifierEvent;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;
import net.neoforged.neoforge.registries.DeferredHolder;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;

/**
 * Armor evolution. Every piece of the five sets has a stage (1 to 3). Fighting while wearing it fills
 * its resonance (monsters a third of their health, bosses half of theirs); once full, the evolution is
 * completed at the set's station with a boss material. Each stage adds armor and toughness, shows new
 * model parts (bones named stage2_/stage3_) and, for a full set, strengthens the set ability by the
 * lowest stage among the four pieces.
 */
@EventBusSubscriber(modid = CelestialAscent.MODID)
public final class ArmorStages {
    private ArmorStages() {}

    public static final int MAX_STAGE = 3;
    /** Resonance needed to leave stage 1 and stage 2. */
    private static final int[] REQUIRED = {0, 600, 1800};

    public static final DeferredHolder<DataComponentType<?>, DataComponentType<Integer>> STAGE =
            CAReg.COMPONENTS.registerComponentType("armor_stage", b -> b.persistent(Codec.intRange(1, MAX_STAGE)).networkSynchronized(ByteBufCodecs.VAR_INT));
    public static final DeferredHolder<DataComponentType<?>, DataComponentType<Integer>> RESONANCE =
            CAReg.COMPONENTS.registerComponentType("resonance", b -> b.persistent(Codec.intRange(0, Integer.MAX_VALUE)).networkSynchronized(ByteBufCodecs.VAR_INT));

    public static boolean evolves(ItemStack s) {
        return s.getItem() instanceof CelestialArmorItem;
    }

    public static int stage(ItemStack s) {
        return evolves(s) ? s.getOrDefault(STAGE.get(), 1) : 0;
    }

    public static int resonance(ItemStack s) {
        return s.getOrDefault(RESONANCE.get(), 0);
    }

    /** Resonance needed for the next stage, or 0 at the last stage. */
    public static int required(ItemStack s) {
        int st = stage(s);
        return st >= MAX_STAGE || st < 1 ? 0 : REQUIRED[st];
    }

    public static boolean ready(ItemStack s) {
        return evolves(s) && stage(s) < MAX_STAGE && resonance(s) >= required(s);
    }

    /** Lowest stage among a full set's pieces (0 without a full set): the set ability's strength. */
    public static int setStage(LivingEntity e) {
        if (ArmorSets.fullSet(e) == null) return 0;
        int min = MAX_STAGE;
        for (ItemStack s : ArmorSets.pieces(e)) min = Math.min(min, stage(s));
        return min;
    }

    /** The evolved copy: next stage, resonance spent, fully repaired. */
    public static ItemStack evolve(ItemStack s) {
        ItemStack out = s.copy();
        out.set(STAGE.get(), Math.min(MAX_STAGE, stage(s) + 1));
        out.remove(RESONANCE.get());
        out.remove(DataComponents.DAMAGE);
        return out;
    }

    /** Clears stage and resonance (an armor piece upgraded into the next set starts over). */
    public static void reset(ItemStack s) {
        s.remove(STAGE.get());
        s.remove(RESONANCE.get());
    }

    // ------------------------------------------------------------------ evolution recipes

    /** Where and with what a set completes each evolution. */
    public record Evolution(StationType station, Supplier<? extends ItemLike> stationBlock, List<StationRecipe.Mat> toStage2,
                            List<StationRecipe.Mat> toStage3) {
        public List<StationRecipe.Mat> mats(int fromStage) {
            return fromStage == 1 ? toStage2 : toStage3;
        }
    }

    private static StationRecipe.Mat mat(Supplier<? extends ItemLike> item, int count) {
        return new StationRecipe.Mat(Ingredient.of(item.get()), count);
    }

    /** Evolution per set, filled in common setup (items must be registered). */
    private static final java.util.Map<SetId, Evolution> EVOLUTIONS = new java.util.EnumMap<>(SetId.class);

    public static Evolution evolution(SetId set) {
        return EVOLUTIONS.get(set);
    }

    /** Materials to evolve this piece from its current stage (titan pieces need cores of their own element). */
    public static List<StationRecipe.Mat> matsFor(ItemStack s) {
        if (!(s.getItem() instanceof CelestialArmorItem a) || stage(s) >= MAX_STAGE) return List.of();
        if (a instanceof TitanArmorItem && TitanArmorItem.element(s) != null) return titanMats(TitanArmorItem.element(s), stage(s));
        Evolution ev = EVOLUTIONS.get(a.set);
        return ev == null ? List.of() : ev.mats(stage(s));
    }

    private static List<StationRecipe.Mat> titanMats(Element e, int fromStage) {
        return fromStage == 1 ? List.of(mat(Titans.CORES.get(e), 1), mat(Titans.TITAN_SHARD, 3))
                : List.of(mat(Titans.CORES.get(e), 2), mat(Titans.TITAN_SHARD, 6));
    }

    @SubscribeEvent
    public static void setup(FMLCommonSetupEvent e) {
        e.enqueueWork(ArmorStages::recipes);
    }

    static void recipes() {
        EVOLUTIONS.put(SetId.TITAN, new Evolution(Titans.FORGE, Titans.TITAN_FORGE, List.of(), List.of()));
        EVOLUTIONS.put(SetId.IMPERIAL, new Evolution(Empire.FORGE, Empire.IMPERIAL_FORGE,
                List.of(mat(Empire.IMPERIAL_PLATING, 3), mat(Empire.ENDER_GEAR, 2)),
                List.of(mat(Empire.COLOSSUS_CORE, 1), mat(Empire.ENDER_GEAR, 3), mat(Empire.IMPERIAL_PLATING, 3))));
        EVOLUTIONS.put(SetId.STELLAR, new Evolution(Stars.SKY_ALTAR_TYPE, Stars.SKY_ALTAR,
                List.of(mat(Stars.STARDUST, 12)),
                List.of(mat(Stars.STAR_CORE, 1), mat(Stars.STARDUST, 16))));
        EVOLUTIONS.put(SetId.VOID, new Evolution(Abyss.INFUSER, Abyss.VOID_INFUSER,
                List.of(mat(Abyss.VOID_ESSENCE, 8)),
                List.of(mat(Abyss.PRIMORDIAL_CORE, 1), mat(Abyss.VOID_ESSENCE, 12))));
        EVOLUTIONS.put(SetId.ASCENDANT, new Evolution(Abyss.ASCENSION, Abyss.ASCENSION_ALTAR,
                List.of(mat(Stars.STAR_CORE, 1), mat(Abyss.VOID_ESSENCE, 16)),
                List.of(mat(Abyss.PRIMORDIAL_CORE, 1), mat(Stars.STAR_CORE, 1), mat(Empire.DRAGON_HEART, 1))));

        for (var holder : CAReg.ITEMS.getEntries()) {
            if (!(holder.get() instanceof CelestialArmorItem piece)) continue;
            Evolution ev = EVOLUTIONS.get(piece.set);
            for (int from = 1; from < MAX_STAGE; from++) {
                int stageFrom = from;
                if (piece instanceof TitanArmorItem) {
                    for (Element el : Element.values()) {
                        ev.station().add(new StationRecipe(s -> s.is(piece) && TitanArmorItem.element(s) == el && stage(s) == stageFrom && ready(s),
                                titanMats(el, stageFrom), ArmorStages::evolve));
                    }
                } else {
                    ev.station().add(new StationRecipe(s -> s.is(piece) && stage(s) == stageFrom && ready(s), ev.mats(stageFrom), ArmorStages::evolve));
                }
            }
        }
    }

    // ------------------------------------------------------------------ resonance

    /** Resonance a kill is worth: bosses half their (true) health, the dragon 300, monsters a third of theirs. */
    public static int worth(LivingEntity victim) {
        if (victim instanceof CelestialBoss boss) return (int) (boss.effectiveMaxHealth() / 2);
        if (victim instanceof EnderDragon) return 300;
        if (victim instanceof Enemy) return Mth.ceil(victim.getMaxHealth() / 3f);
        return 0;
    }

    /** Adds resonance to every worn piece that can still grow. Returns the pieces that just became ready. */
    public static List<ItemStack> addResonance(Player p, int amount) {
        List<ItemStack> ready = new ArrayList<>();
        if (amount <= 0) return ready;
        for (ItemStack s : ArmorSets.pieces(p)) {
            if (!evolves(s) || stage(s) >= MAX_STAGE) continue;
            int need = required(s), before = resonance(s);
            if (before >= need) continue;
            int after = Math.min(need, before + amount);
            s.set(RESONANCE.get(), after);
            if (after >= need) ready.add(s);
        }
        return ready;
    }

    @SubscribeEvent
    public static void onKill(LivingDeathEvent e) {
        LivingEntity victim = e.getEntity();
        if (victim.level().isClientSide) return;
        int worth = worth(victim);
        if (worth <= 0) return;
        List<ServerPlayer> earners = new ArrayList<>();
        if (victim instanceof CelestialBoss || victim instanceof EnderDragon) {
            // Everyone at the fight resonates, not only the one who landed the last hit.
            earners.addAll(victim.level().getEntitiesOfClass(ServerPlayer.class, victim.getBoundingBox().inflate(64), pl -> pl.isAlive() && !pl.isSpectator()));
        } else if (e.getSource().getEntity() instanceof ServerPlayer killer) {
            earners.add(killer);
        }
        for (ServerPlayer p : earners) {
            for (ItemStack s : addResonance(p, worth)) {
                Evolution ev = s.getItem() instanceof CelestialArmorItem a ? EVOLUTIONS.get(a.set) : null;
                Component station = ev == null ? Component.empty() : new ItemStack(ev.stationBlock().get()).getHoverName();
                p.sendSystemMessage(Component.translatable("message.celestialascent.resonance_full", s.getHoverName(), station).withStyle(ChatFormatting.LIGHT_PURPLE));
                p.level().playSound(null, p.blockPosition(), SoundEvents.AMETHYST_BLOCK_RESONATE, SoundSource.PLAYERS, 1f, 1.2f);
            }
        }
    }

    // ------------------------------------------------------------------ stats

    /** Each stage adds armor and toughness to the piece; the last also some knockback resistance. */
    @SubscribeEvent
    public static void attributes(ItemAttributeModifierEvent e) {
        ItemStack s = e.getItemStack();
        int st = stage(s);
        if (st < 2 || !(s.getItem() instanceof CelestialArmorItem a)) return;
        EquipmentSlot slot = a.getEquipmentSlot();
        EquipmentSlotGroup group = EquipmentSlotGroup.bySlot(slot);
        String n = slot.getName();
        e.addModifier(Attributes.ARMOR, new AttributeModifier(id("stage_armor_" + n), st == 2 ? 1 : 2, AttributeModifier.Operation.ADD_VALUE), group);
        e.addModifier(Attributes.ARMOR_TOUGHNESS, new AttributeModifier(id("stage_toughness_" + n), st == 2 ? 0.5 : 1, AttributeModifier.Operation.ADD_VALUE), group);
        if (st == 3) e.addModifier(Attributes.KNOCKBACK_RESISTANCE, new AttributeModifier(id("stage_knockback_" + n), 0.05, AttributeModifier.Operation.ADD_VALUE), group);
    }

    private static ResourceLocation id(String path) {
        return ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, path);
    }

    // ------------------------------------------------------------------ tooltip

    /** Stage, resonance bar and what the next evolution needs. */
    public static void tooltip(ItemStack s, List<Component> lines) {
        int st = stage(s);
        if (st < 1) return;
        String roman = st == 1 ? "I" : st == 2 ? "II" : "III";
        lines.add(Component.translatable("tooltip.celestialascent.stage", roman).withStyle(st == 3 ? ChatFormatting.LIGHT_PURPLE : ChatFormatting.AQUA));
        if (st >= MAX_STAGE) {
            lines.add(Component.literal(" ").append(Component.translatable("tooltip.celestialascent.max_stage")).withStyle(ChatFormatting.DARK_PURPLE));
            return;
        }
        int res = resonance(s), need = required(s);
        int filled = Math.round(20f * res / need);
        Component bar = Component.literal("|".repeat(filled)).withStyle(ChatFormatting.LIGHT_PURPLE)
                .append(Component.literal("|".repeat(20 - filled)).withStyle(ChatFormatting.DARK_GRAY));
        lines.add(Component.literal(" ").append(bar).append(Component.literal(" ")).append(
                Component.translatable("tooltip.celestialascent.resonance", res, need).withStyle(ChatFormatting.GRAY)));
        if (res >= need && s.getItem() instanceof CelestialArmorItem a && EVOLUTIONS.containsKey(a.set)) {
            Component station = new ItemStack(EVOLUTIONS.get(a.set).stationBlock().get()).getHoverName();
            lines.add(Component.literal(" ").append(Component.translatable("tooltip.celestialascent.ready", station)).withStyle(ChatFormatting.GREEN));
            for (StationRecipe.Mat m : matsFor(s)) {
                ItemStack[] options = m.ingredient().getItems();
                if (options.length == 0) continue;
                lines.add(Component.literal("   " + m.count() + " × ").append(options[0].getHoverName()).withStyle(ChatFormatting.GRAY));
            }
        } else {
            lines.add(Component.literal(" ").append(Component.translatable("tooltip.celestialascent.resonance_hint")).withStyle(ChatFormatting.DARK_GRAY));
        }
    }

    /** All evolvable armor items (for tests and the codex). */
    public static List<Item> pieces() {
        List<Item> out = new ArrayList<>();
        for (var holder : CAReg.ITEMS.getEntries()) if (holder.get() instanceof CelestialArmorItem) out.add(holder.get());
        return out;
    }
}
