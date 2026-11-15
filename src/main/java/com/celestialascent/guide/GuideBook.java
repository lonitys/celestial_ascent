package com.celestialascent.guide;

import com.celestialascent.CelestialAscent;
import com.celestialascent.core.station.StationType;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.ItemLike;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Supplier;

/**
 * Data model of the Celestial Codex. Chapters are plain data (no client classes), so the server can
 * test them and datagen can write both language files from the same source.
 */
public final class GuideBook {
    private GuideBook() {}

    public static final String PREFIX = "guide." + CelestialAscent.MODID + ".";

    /** Every guide string: key -> {english, german}. Filled while chapters are built. */
    static final Map<String, String[]> STRINGS = new LinkedHashMap<>();

    public static Map<String, String[]> strings() {
        // Touch every class that defines guide strings so they are all registered.
        GuideChapters.ALL.size();
        NextStep.values();
        GuideUi.RUNGS.size();
        return STRINGS;
    }

    static String text(String key, String en, String de) {
        String full = PREFIX + key;
        String[] old = STRINGS.put(full, new String[]{en, de});
        if (old != null && !(old[0].equals(en) && old[1].equals(de))) {
            throw new IllegalStateException("Guide string defined twice with different text: " + full);
        }
        return full;
    }

    public record Stack(Supplier<? extends ItemLike> item, int count) {}

    /** Something that fills a %s slot in a translated sentence. */
    public sealed interface Arg permits ItemArg, EntityArg, KeyArg {}

    /** An item name, shown highlighted with the item's tooltip on hover. */
    public record ItemArg(Supplier<? extends ItemLike> item) implements Arg {}

    /** An entity's name (bosses), in the player's language. */
    public record EntityArg(Supplier<? extends EntityType<?>> type) implements Arg {}

    /** The key currently bound to a key mapping (for example "H"). */
    public record KeyArg(String mapping) implements Arg {}

    public sealed interface Element permits Heading, Text, Items, Crafting, Station, Anchor {}

    public record Heading(String key) implements Element {}

    /** A paragraph. Tips are drawn on a tinted card. */
    public record Text(String key, List<Arg> args, boolean tip) implements Element {}

    /** A row of item icons with counts and tooltips. */
    public record Items(List<Stack> stacks) implements Element {}

    /** A vanilla crafting recipe, read from the recipe manager by id. */
    public record Crafting(ResourceLocation recipe) implements Element {}

    /**
     * An upgrade-station recipe. Stations match their base item by predicate, so the display data is
     * written here and a GameTest checks that the station really accepts it.
     */
    public record Station(Supplier<? extends ItemLike> block, Supplier<StationType> type, Supplier<? extends ItemLike> base,
                          List<Stack> mats, Supplier<? extends ItemLike> result) implements Element {}

    /** A jump target inside a chapter (used by the "next step" card). */
    public record Anchor(String id) implements Element {}

    public record Chapter(String id, Supplier<? extends ItemLike> icon, List<Element> elements) {
        public String titleKey() {
            return PREFIX + id;
        }
    }

    /** Fluent chapter builder. Keys are relative to the chapter: "guide.celestialascent.<chapter>.<key>". */
    static final class Builder {
        private final String id;
        private final Supplier<? extends ItemLike> icon;
        private final List<Element> elements = new ArrayList<>();

        Builder(String id, Supplier<? extends ItemLike> icon, String en, String de) {
            this.id = id;
            this.icon = icon;
            text(id, en, de);
        }

        private String key(String sub) {
            return id + "." + sub;
        }

        Builder h(String sub, String en, String de) {
            elements.add(new Heading(text(key(sub), en, de)));
            return this;
        }

        Builder p(String sub, String en, String de, Arg... args) {
            elements.add(new Text(text(key(sub), en, de), List.of(args), false));
            return this;
        }

        Builder tip(String sub, String en, String de, Arg... args) {
            elements.add(new Text(text(key(sub), en, de), List.of(args), true));
            return this;
        }

        Builder items(Stack... stacks) {
            elements.add(new Items(List.of(stacks)));
            return this;
        }

        Builder craft(String recipePath) {
            elements.add(new Crafting(ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, recipePath)));
            return this;
        }

        Builder station(Supplier<? extends ItemLike> block, Supplier<StationType> type, Supplier<? extends ItemLike> base,
                        List<Stack> mats, Supplier<? extends ItemLike> result) {
            elements.add(new Station(block, type, base, mats, result));
            return this;
        }

        Builder anchor(String anchorId) {
            elements.add(new Anchor(anchorId));
            return this;
        }

        Chapter build() {
            return new Chapter(id, icon, List.copyOf(elements));
        }
    }
}
