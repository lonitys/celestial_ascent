package com.celestialascent;

import com.celestialascent.armor.ArmorTiers;
import com.celestialascent.core.CAReg;
import com.celestialascent.core.ModConfig;
import com.celestialascent.progress.Progress;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;

@Mod(CelestialAscent.MODID)
public final class CelestialAscent {
    public static final String MODID = "celestialascent";

    public CelestialAscent(IEventBus modBus, ModContainer container) {
        container.registerConfig(net.neoforged.fml.config.ModConfig.Type.COMMON, ModConfig.SPEC);
        // Load content classes so their static registrations are queued before the registers fire.
        Progress.TYPE.getClass();
        ArmorTiers.init();
        com.celestialascent.economy.Economy.init();
        com.celestialascent.titans.Titans.init();
        com.celestialascent.empire.Empire.init();
        com.celestialascent.stars.Stars.init();
        com.celestialascent.abyss.Abyss.init();
        com.celestialascent.guide.Guide.init();
        com.celestialascent.core.DisplayBlockEntity.TYPE.getClass();
        com.celestialascent.retrogen.Retrogen.MOVED.getClass();
        CAReg.register(modBus);
    }
}
