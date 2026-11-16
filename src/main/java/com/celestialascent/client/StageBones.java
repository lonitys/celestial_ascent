package com.celestialascent.client;

import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.cache.object.GeoBone;

/**
 * Evolution parts of boss and armor models: bones named {@code stage2_*} are shown from stage 2 on,
 * {@code stage3_*} only in stage 3 (see tools/art). Newly shown parts can be scaled in (grow).
 */
public final class StageBones {
    private StageBones() {}

    public static void apply(BakedGeoModel model, int stage, float grow2, float grow3) {
        for (GeoBone b : model.topLevelBones()) visit(b, stage, grow2, grow3);
    }

    private static void visit(GeoBone b, int stage, float grow2, float grow3) {
        String name = b.getName();
        if (name.startsWith("stage2_")) show(b, stage >= 2, grow2);
        else if (name.startsWith("stage3_")) show(b, stage >= 3, grow3);
        for (GeoBone child : b.getChildBones()) visit(child, stage, grow2, grow3);
    }

    private static void show(GeoBone b, boolean visible, float grow) {
        b.setHidden(!visible);
        b.setChildrenHidden(!visible);
        if (visible) {
            float s = Math.max(0.001f, grow);
            b.updateScale(s, s, s);
        }
    }
}
