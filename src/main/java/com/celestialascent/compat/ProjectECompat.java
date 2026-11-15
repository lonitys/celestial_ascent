package com.celestialascent.compat;

import com.celestialascent.CelestialAscent;
import com.celestialascent.armor.ArmorSets;
import com.celestialascent.armor.CelestialArmorItem;
import com.celestialascent.core.ModConfig;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.ModList;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.capabilities.EntityCapability;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.lang.reflect.Method;
import java.math.BigInteger;

/**
 * Optional ProjectE integration without a compile-time dependency: worn Celestial armor slowly
 * repairs itself by spending the wearer's transmutation EMC.
 */
@EventBusSubscriber(modid = CelestialAscent.MODID)
public final class ProjectECompat {
    private ProjectECompat() {}

    private static final Logger LOG = LoggerFactory.getLogger("celestialascent/projecte");
    private static boolean tried;
    private static EntityCapability<Object, Void> knowledge;
    private static Method getEmc, setEmc, syncEmc;

    @SuppressWarnings("unchecked")
    static boolean available() {
        if (tried) return knowledge != null;
        tried = true;
        if (!ModList.get().isLoaded("projecte")) return false;
        try {
            Class<?> k = Class.forName("moze_intel.projecte.api.capabilities.IKnowledgeProvider");
            knowledge = (EntityCapability<Object, Void>) (EntityCapability<?, Void>) EntityCapability.createVoid(
                    ResourceLocation.fromNamespaceAndPath("projecte", "knowledge"), k);
            getEmc = k.getMethod("getEmc");
            setEmc = k.getMethod("setEmc", BigInteger.class);
            syncEmc = k.getMethod("syncEmc", ServerPlayer.class);
            LOG.info("ProjectE detected: EMC armor repair enabled");
            return true;
        } catch (ReflectiveOperationException | LinkageError e) {
            LOG.warn("ProjectE present but its API could not be reached; EMC repair disabled", e);
            knowledge = null;
            return false;
        }
    }

    /** EMC per durability point: a fraction of the piece's EMC value spread over its durability. */
    public static long costPerPoint(long itemEmc, int maxDamage) {
        if (maxDamage <= 0) return Long.MAX_VALUE;
        return Math.max(16, itemEmc / maxDamage / 8);
    }

    @SubscribeEvent
    public static void tick(PlayerTickEvent.Post e) {
        if (!(e.getEntity() instanceof ServerPlayer p) || p.tickCount % 20 != 0 || !ModConfig.PROJECTE_REPAIR.get() || !available()) return;
        Object provider = p.getCapability(knowledge);
        if (provider == null) return;
        try {
            BigInteger emc = (BigInteger) getEmc.invoke(provider);
            BigInteger start = emc;
            for (ItemStack s : ArmorSets.pieces(p)) {
                if (!(s.getItem() instanceof CelestialArmorItem) || !s.isDamaged()) continue;
                Long value = Emc.VALUES.entrySet().stream().filter(en -> en.getKey().asItem() == s.getItem()).map(java.util.Map.Entry::getValue).findFirst().orElse(null);
                if (value == null) continue;
                BigInteger cost = BigInteger.valueOf(costPerPoint(value, s.getMaxDamage()));
                int points = Math.min(5, s.getDamageValue());
                while (points > 0 && emc.compareTo(cost) >= 0) {
                    emc = emc.subtract(cost);
                    s.setDamageValue(s.getDamageValue() - 1);
                    points--;
                }
            }
            if (!emc.equals(start)) {
                setEmc.invoke(provider, emc);
                syncEmc.invoke(provider, p);
            }
        } catch (ReflectiveOperationException ex) {
            LOG.warn("EMC repair failed; disabling", ex);
            knowledge = null;
        }
    }
}
