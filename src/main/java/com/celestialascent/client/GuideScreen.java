package com.celestialascent.client;

import com.celestialascent.CelestialAscent;
import com.celestialascent.armor.ArmorSets;
import com.celestialascent.armor.SetId;
import com.celestialascent.guide.GuideBook;
import com.celestialascent.guide.GuideBook.Arg;
import com.celestialascent.guide.GuideBook.Chapter;
import com.celestialascent.guide.GuideBook.Element;
import com.celestialascent.guide.GuideBook.Stack;
import com.celestialascent.guide.GuideChapters;
import com.celestialascent.guide.GuideUi;
import com.celestialascent.guide.NextStep;
import com.celestialascent.progress.ProgressSync;
import net.minecraft.ChatFormatting;
import net.minecraft.Util;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.locale.Language;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.FormattedText;
import net.minecraft.network.chat.HoverEvent;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.network.chat.Style;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.ShapedRecipe;
import org.lwjgl.glfw.GLFW;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

/** The Celestial Codex: a two-page book with a front page (next step, progress, contents) and chapters. */
public class GuideScreen extends Screen {
    private static final ResourceLocation TEX = ResourceLocation.fromNamespaceAndPath(CelestialAscent.MODID, "textures/gui/codex.png");
    private static final int TEX_W = 512, TEX_H = 256;

    static final int BOOK_W = 300, BOOK_H = 200;
    static final int PAGE_W = 124, PAGE_H = 160, TOP = 16;
    private static final int[] PAGE_X = {20, 156};
    private static final int FOOTER_Y = 181;

    // Sprite positions in codex.png (see tools/art/gen_codex.py).
    private static final int ARROW_W = 18, ARROW_H = 10;
    private static final int ARROW_NEXT_U = 304, ARROW_PREV_U = 322;
    private static final int HOME_U = 340, HOME_SIZE = 13;
    private static final int SLOT_U = 356;
    private static final int BIG_ARROW_U = 376, BIG_ARROW_W = 22, BIG_ARROW_H = 15;
    private static final int SMALL_ARROW_U = 400, SMALL_ARROW_W = 10, SMALL_ARROW_H = 9;
    private static final int PLUS_U = 412, PLUS_SIZE = 7;
    private static final int CHECK_U = 420, CHECK_SIZE = 9;
    private static final int ORNAMENT_U = 304, ORNAMENT_V = 24, ORNAMENT_W = 100, ORNAMENT_H = 5;
    private static final int MEDAL_U = 304, MEDAL_GOLD_U = 322, MEDAL_V = 32;

    // Ink on parchment.
    private static final int INK = 0x3B2A1A;
    private static final int INK_SOFT = 0x7A6446;
    private static final int HEADING = 0x2A2F55;
    private static final int LINK = 0x7A3E9D;
    private static final int ENTITY = 0x8B2E2E;
    private static final int KEY = 0x24577F;
    private static final int GOLD_LINE = 0xFFB08A3E;
    private static final int TIP_BG = 0xFFE9D8AE;
    private static final int TIP_EDGE = 0xFFC9A54C;
    private static final int CARD_BG = 0xFFE2D5B8;
    private static final int CARD_BG_HOVER = 0xFFEADFC4;
    private static final int CARD_EDGE = 0xFF2A2F55;
    private static final int HOVER_ROW = 0x30C9A54C;

    private static int lastChapter = -1, lastSpread = 0;

    private int chapter = lastChapter;
    private int spread = lastSpread;
    private int left, top;
    private final Map<Integer, Layout> layouts = new HashMap<>();

    /** Clickable areas, rebuilt every frame while rendering. */
    private final List<Hit> hits = new ArrayList<>();
    private ItemStack hoverStack = ItemStack.EMPTY;
    private Style hoverStyle;
    private List<Component> hoverLines;

    private record Hit(int x0, int y0, int x1, int y1, Runnable action) {
        boolean contains(double x, double y) {
            return x >= x0 && x < x1 && y >= y0 && y < y1;
        }
    }

    public GuideScreen() {
        super(Component.translatable(GuideUi.TITLE));
    }

    public static void open() {
        Minecraft.getInstance().setScreen(new GuideScreen());
    }

    /** Opens the codex at a chapter and optional anchor, or at the front page if chapterId is null (dev showcase). */
    public static void open(String chapterId, String anchor) {
        GuideScreen s = new GuideScreen();
        Minecraft.getInstance().setScreen(s);
        s.chapter = -1;
        s.spread = 0;
        if (chapterId != null) s.jump(chapterId, anchor);
    }

    @Override
    protected void init() {
        left = (width - BOOK_W) / 2;
        top = (height - BOOK_H) / 2;
        layouts.clear(); // font or language may have changed
        if (chapter >= GuideChapters.ALL.size()) chapter = -1;
        if (chapter >= 0) spread = Math.min(spread, layout(chapter).spreads() - 1);
    }

    @Override
    public void removed() {
        lastChapter = chapter;
        lastSpread = spread;
    }

    // ------------------------------------------------------------------ navigation

    private void turn() {
        minecraft.getSoundManager().play(SimpleSoundInstance.forUI(SoundEvents.BOOK_PAGE_TURN, 1.0F));
    }

    private boolean hasNext() {
        return chapter < 0 || spread + 1 < layout(chapter).spreads() || chapter + 1 < GuideChapters.ALL.size();
    }

    private boolean hasPrev() {
        return chapter >= 0;
    }

    private void next() {
        if (!hasNext()) return;
        if (chapter < 0) {
            chapter = 0;
            spread = 0;
        } else if (spread + 1 < layout(chapter).spreads()) {
            spread++;
        } else {
            chapter++;
            spread = 0;
        }
        turn();
    }

    private void prev() {
        if (!hasPrev()) return;
        if (spread > 0) {
            spread--;
        } else if (chapter > 0) {
            chapter--;
            spread = layout(chapter).spreads() - 1;
        } else {
            chapter = -1;
            spread = 0;
        }
        turn();
    }

    private void home() {
        if (chapter < 0) return;
        chapter = -1;
        spread = 0;
        turn();
    }

    private void jump(String chapterId, String anchor) {
        for (int i = 0; i < GuideChapters.ALL.size(); i++) {
            if (!GuideChapters.ALL.get(i).id().equals(chapterId)) continue;
            chapter = i;
            Integer page = anchor == null ? null : layout(i).anchors.get(anchor);
            spread = page == null ? 0 : page / 2;
            return;
        }
    }

    @Override
    public boolean mouseClicked(double mx, double my, int button) {
        if (button == 0) {
            for (Hit h : hits) {
                if (h.contains(mx, my)) {
                    h.action().run();
                    return true;
                }
            }
        }
        return super.mouseClicked(mx, my, button);
    }

    @Override
    public boolean mouseScrolled(double mx, double my, double sx, double sy) {
        if (sy < 0) next();
        else if (sy > 0) prev();
        return true;
    }

    @Override
    public boolean keyPressed(int key, int scan, int mods) {
        switch (key) {
            case GLFW.GLFW_KEY_RIGHT, GLFW.GLFW_KEY_PAGE_DOWN -> next();
            case GLFW.GLFW_KEY_LEFT, GLFW.GLFW_KEY_PAGE_UP -> prev();
            case GLFW.GLFW_KEY_HOME, GLFW.GLFW_KEY_BACKSPACE -> home();
            default -> {
                return super.keyPressed(key, scan, mods);
            }
        }
        return true;
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }

    // ------------------------------------------------------------------ rendering

    @Override
    public void render(GuiGraphics g, int mx, int my, float partialTick) {
        super.render(g, mx, my, partialTick); // background (no widgets)
        hits.clear();
        hoverStack = ItemStack.EMPTY;
        hoverStyle = null;
        hoverLines = null;

        g.blit(TEX, left, top, 0, 0, BOOK_W, BOOK_H, TEX_W, TEX_H);
        if (chapter < 0) {
            renderFront(g, mx, my);
        } else {
            Layout l = layout(chapter);
            for (int side = 0; side < 2; side++) {
                int page = spread * 2 + side;
                if (page >= l.pages.size()) continue;
                int x = left + PAGE_X[side];
                for (Placed p : l.pages.get(page)) p.block().render(g, x, top + TOP + p.y(), mx, my);
                String num = String.valueOf(page + 1);
                g.drawString(font, num, x + (PAGE_W - font.width(num)) / 2, top + FOOTER_Y, INK_SOFT, false);
            }
        }
        renderNav(g, mx, my);

        if (!hoverStack.isEmpty()) g.renderTooltip(font, hoverStack, mx, my);
        else if (hoverLines != null) g.renderComponentTooltip(font, hoverLines, mx, my);
        else if (hoverStyle != null) g.renderComponentHoverEffect(font, hoverStyle, mx, my);
    }

    private static boolean over(int mx, int my, int x, int y, int w, int h) {
        return mx >= x && mx < x + w && my >= y && my < y + h;
    }

    private void sprite(GuiGraphics g, int x, int y, int u, int v, int w, int h) {
        g.blit(TEX, x, y, u, v, w, h, TEX_W, TEX_H);
    }

    private void renderNav(GuiGraphics g, int mx, int my) {
        int y = top + FOOTER_Y;
        if (hasPrev()) {
            int x = left + 14;
            boolean hov = over(mx, my, x, y, ARROW_W, ARROW_H);
            sprite(g, x, y, ARROW_PREV_U, hov ? ARROW_H : 0, ARROW_W, ARROW_H);
            hits.add(new Hit(x, y, x + ARROW_W, y + ARROW_H, this::prev));
        }
        if (hasNext()) {
            int x = left + BOOK_W - 14 - ARROW_W;
            boolean hov = over(mx, my, x, y, ARROW_W, ARROW_H);
            sprite(g, x, y, ARROW_NEXT_U, hov ? ARROW_H : 0, ARROW_W, ARROW_H);
            hits.add(new Hit(x, y, x + ARROW_W, y + ARROW_H, this::next));
        }
        if (chapter >= 0) {
            int x = left + (BOOK_W - HOME_SIZE) / 2, hy = top + BOOK_H - HOME_SIZE - 6;
            boolean hov = over(mx, my, x, hy, HOME_SIZE, HOME_SIZE);
            sprite(g, x, hy, HOME_U, hov ? HOME_SIZE : 0, HOME_SIZE, HOME_SIZE);
            hits.add(new Hit(x, hy, x + HOME_SIZE, hy + HOME_SIZE, this::home));
            if (hov) hoverLines = List.of(Component.translatable(GuideUi.CONTENTS));
        }
    }

    // ---- front page ----

    private void renderFront(GuiGraphics g, int mx, int my) {
        Set<ResourceLocation> kills = Set.copyOf(ProgressSync.clientKills);
        boolean ascended = minecraft.player != null && ArmorSets.fullSet(minecraft.player) == SetId.ASCENDANT;
        NextStep step = NextStep.of(kills, ascended);

        // Left page: title, next step card, and the progress medallions anchored to the bottom.
        int x = left + PAGE_X[0], y = top + TOP;
        Component title = Component.translatable(GuideUi.TITLE).withStyle(ChatFormatting.BOLD);
        g.drawString(font, title, x + (PAGE_W - font.width(title)) / 2, y, HEADING, false);
        sprite(g, x + (PAGE_W - ORNAMENT_W) / 2, y + 12, ORNAMENT_U, ORNAMENT_V, ORNAMENT_W, ORNAMENT_H);
        y += 22;

        g.drawString(font, Component.translatable(GuideUi.NEXT), x, y, INK_SOFT, false);
        g.drawString(font, "»", x + PAGE_W - 7, y, LINK, false);
        y += 11;
        List<FormattedCharSequence> stepTitle = font.split(Component.translatable(step.titleKey).withStyle(ChatFormatting.BOLD), PAGE_W - 10);
        List<FormattedCharSequence> stepDesc = font.split(Component.translatable(step.descKey), PAGE_W - 10);
        int cardH = 4 + stepTitle.size() * 10 + 1 + stepDesc.size() * 10 + 3;
        boolean cardHover = over(mx, my, x, y, PAGE_W, cardH);
        g.fill(x, y, x + PAGE_W, y + cardH, cardHover ? CARD_BG_HOVER : CARD_BG);
        g.fill(x, y, x + 2, y + cardH, CARD_EDGE);
        g.fill(x + 2, y, x + PAGE_W, y + 1, TIP_EDGE);
        g.fill(x + 2, y + cardH - 1, x + PAGE_W, y + cardH, TIP_EDGE);
        int ty = y + 4;
        for (FormattedCharSequence line : stepTitle) {
            g.drawString(font, line, x + 6, ty, HEADING, false);
            if (cardHover) g.fill(x + 6, ty + 9, x + 6 + font.width(line), ty + 10, HEADING | 0xFF000000);
            ty += 10;
        }
        ty += 1;
        for (FormattedCharSequence line : stepDesc) {
            g.drawString(font, line, x + 6, ty, INK, false);
            ty += 10;
        }
        hits.add(new Hit(x, y, x + PAGE_W, y + cardH, () -> {
            jump(step.chapter, step.anchor);
            turn();
        }));
        if (cardHover) hoverLines = List.of(Component.translatable(GuideUi.OPEN));

        y = top + TOP + PAGE_H - 31;
        int done = 0;
        int pitch = 21, mx0 = x + (PAGE_W - (18 + pitch * (GuideUi.RUNGS.size() - 1))) / 2;
        for (int i = 0; i < GuideUi.RUNGS.size(); i++) {
            GuideUi.Rung r = GuideUi.RUNGS.get(i);
            int count = (int) r.bosses().stream().filter(kills::contains).count();
            done += count;
            boolean complete = r.bosses().isEmpty() ? ascended : count == r.bosses().size();
            int cx = mx0 + i * pitch;
            if (i > 0) g.fill(cx - pitch + 18, y + 8, cx, y + 10, complete ? GOLD_LINE : 0xFFB9A57E);
            sprite(g, cx, y, complete ? MEDAL_GOLD_U : MEDAL_U, MEDAL_V, 18, 18);
            g.renderItem(new ItemStack(r.icon().get()), cx + 1, y + 1);
            if (complete) {
                g.pose().pushPose();
                g.pose().translate(0, 0, 200); // above the item
                sprite(g, cx + 11, y + 11, CHECK_U, 0, CHECK_SIZE, CHECK_SIZE);
                g.pose().popPose();
            } else if (count > 0) {
                String frac = count + "/" + r.bosses().size();
                int fw = font.width(frac), fx = cx + 19 - fw, fy = y + 11;
                g.pose().pushPose();
                g.pose().translate(0, 0, 200);
                g.fill(fx - 2, fy - 1, fx + fw, fy + 8, 0xFF2A2F55);
                g.fill(fx - 2, fy - 1, fx + fw, fy, 0xFFC9A54C);
                g.drawString(font, frac, fx, fy, 0xFFF2E6C9, false);
                g.pose().popPose();
            }
            if (over(mx, my, cx, y, 18, 18)) hoverLines = rungTooltip(r, kills, ascended);
        }
        y += 21;
        Component total = Component.translatable(GuideUi.DEFEATED, done, GuideUi.bossCount());
        g.drawString(font, total, x + (PAGE_W - font.width(total)) / 2, y, INK_SOFT, false);

        // Right page: contents.
        x = left + PAGE_X[1];
        y = top + TOP;
        Component contents = Component.translatable(GuideUi.CONTENTS).withStyle(ChatFormatting.BOLD);
        g.drawString(font, contents, x + (PAGE_W - font.width(contents)) / 2, y, HEADING, false);
        sprite(g, x + (PAGE_W - ORNAMENT_W) / 2, y + 12, ORNAMENT_U, ORNAMENT_V, ORNAMENT_W, ORNAMENT_H);
        y += 24;
        for (int i = 0; i < GuideChapters.ALL.size(); i++) {
            Chapter c = GuideChapters.ALL.get(i);
            int rowY = y + i * 11;
            boolean hov = over(mx, my, x, rowY - 1, PAGE_W, 11);
            if (hov) g.fill(x - 2, rowY - 1, x + PAGE_W + 2, rowY + 10, HOVER_ROW);
            g.pose().pushPose();
            g.pose().translate(x + 1, rowY - 1, 0);
            g.pose().scale(0.65f, 0.65f, 1f);
            g.renderItem(new ItemStack(c.icon().get()), 0, 0);
            g.pose().popPose();
            Component name = Component.translatable(c.titleKey()).withStyle(hov ? Style.EMPTY.withUnderlined(true) : Style.EMPTY);
            g.drawString(font, ellipsize(name, PAGE_W - 16), x + 16, rowY + 1, hov ? LINK : INK, false);
            int index = i;
            hits.add(new Hit(x, rowY - 1, x + PAGE_W, rowY + 10, () -> {
                chapter = index;
                spread = 0;
                turn();
            }));
        }
    }

    private List<Component> rungTooltip(GuideUi.Rung r, Set<ResourceLocation> kills, boolean ascended) {
        List<Component> lines = new ArrayList<>();
        lines.add(Component.translatable(r.key()).withStyle(ChatFormatting.GOLD));
        if (r.bosses().isEmpty()) {
            lines.add(Component.translatable(GuideUi.WEAR_SET).withStyle(ascended ? ChatFormatting.GREEN : ChatFormatting.GRAY));
        }
        for (ResourceLocation id : r.bosses()) {
            Component name = Component.translatable("entity." + id.getNamespace() + "." + id.getPath());
            lines.add(name.copy().withStyle(kills.contains(id) ? ChatFormatting.GREEN : ChatFormatting.GRAY));
        }
        return lines;
    }

    private FormattedCharSequence ellipsize(Component text, int width) {
        if (font.width(text) <= width) return text.getVisualOrderText();
        FormattedText cut = font.substrByWidth(text, width - font.width("..."));
        return Language.getInstance().getVisualOrder(FormattedText.composite(cut, Component.literal("...")));
    }

    // ------------------------------------------------------------------ chapter layout

    private record Placed(Block block, int y) {}

    private static final class Layout {
        final List<List<Placed>> pages = new ArrayList<>();
        final Map<String, Integer> anchors = new HashMap<>();

        int spreads() {
            return Math.max(1, (pages.size() + 1) / 2);
        }
    }

    private interface Block {
        int height();

        void render(GuiGraphics g, int x, int y, int mx, int my);
    }

    /** Flows blocks onto fixed-height pages. Gaps vanish at the top of a page. */
    private static final class Pager {
        final Layout layout;
        List<Placed> page = new ArrayList<>();
        int y;
        final List<String> pendingAnchors = new ArrayList<>();

        Pager(Layout layout) {
            this.layout = layout;
            layout.pages.add(page);
        }

        void gap(int h) {
            if (y > 0) y += h;
        }

        /** Starts a new page unless {@code h} more pixels fit on this one. */
        void ensure(int h) {
            if (y > 0 && y + h > PAGE_H) {
                page = new ArrayList<>();
                layout.pages.add(page);
                y = 0;
            }
        }

        int room() {
            return PAGE_H - y;
        }

        void add(Block b) {
            add(b, 0);
        }

        /** Adds a block, also requiring {@code keep} pixels after it on the same page (headings). */
        void add(Block b, int keep) {
            if (y > 0 && y + b.height() + keep > PAGE_H) {
                page = new ArrayList<>();
                layout.pages.add(page);
                y = 0;
            }
            for (String a : pendingAnchors) layout.anchors.put(a, layout.pages.size() - 1);
            pendingAnchors.clear();
            page.add(new Placed(b, y));
            y += b.height();
        }
    }

    private Layout layout(int index) {
        return layouts.computeIfAbsent(index, i -> build(GuideChapters.ALL.get(i)));
    }

    private Layout build(Chapter c) {
        Layout layout = new Layout();
        Pager p = new Pager(layout);
        List<FormattedCharSequence> title = font.split(Component.translatable(c.titleKey()).withStyle(ChatFormatting.BOLD), PAGE_W);
        p.add(new TitleBlock(title));
        p.gap(4);
        for (Element e : c.elements()) {
            switch (e) {
                case GuideBook.Heading h -> {
                    p.gap(4);
                    p.add(new HeadingBlock(Component.translatable(h.key()).withStyle(ChatFormatting.BOLD)), 20);
                    p.gap(2);
                }
                case GuideBook.Text t -> {
                    Component text = Component.translatable(t.key(), t.args().stream().map(this::argument).toArray());
                    if (t.tip()) {
                        // Tip cards stay on one page whenever they fit on one.
                        List<FormattedCharSequence> lines = font.split(text, PAGE_W - 9);
                        p.gap(2);
                        p.ensure(Math.min(PAGE_H, 3 + lines.size() * 10 + 4));
                        p.add(new TipPad(true), 10);
                        for (FormattedCharSequence line : lines) p.add(new LineBlock(line, 6, true));
                        p.add(new TipPad(false));
                        p.gap(5);
                    } else {
                        // Short paragraphs move whole; long ones split but leave at least two lines behind.
                        List<FormattedCharSequence> lines = font.split(text, PAGE_W);
                        int need = lines.size() * 10;
                        if (need > p.room() && (lines.size() <= 4 || p.room() < 20)) p.ensure(need);
                        for (FormattedCharSequence line : lines) p.add(new LineBlock(line, 0, false));
                        p.gap(4);
                    }
                }
                case GuideBook.Items it -> {
                    // Balanced rows of at most six (seven items become 4 + 3).
                    int n = it.stacks().size(), rows = (n + 5) / 6, per = (n + rows - 1) / rows;
                    p.ensure(rows * 20);
                    for (int from = 0; from < n; from += per) {
                        p.add(new ItemsBlock(it.stacks().subList(from, Math.min(n, from + per))));
                    }
                    p.gap(4);
                }
                case GuideBook.Crafting cr -> {
                    p.add(new CraftBlock(cr.recipe()));
                    p.gap(5);
                }
                case GuideBook.Station st -> {
                    p.add(new StationBlock(st));
                    p.gap(5);
                }
                case GuideBook.Anchor a -> p.pendingAnchors.add(a.id());
            }
        }
        return layout;
    }

    private Component argument(Arg a) {
        return switch (a) {
            case GuideBook.ItemArg i -> {
                ItemStack stack = new ItemStack(i.item().get());
                yield stack.getHoverName().copy().withStyle(s -> s.withColor(LINK)
                        .withHoverEvent(new HoverEvent(HoverEvent.Action.SHOW_ITEM, new HoverEvent.ItemStackInfo(stack))));
            }
            case GuideBook.EntityArg en -> en.type().get().getDescription().copy().withColor(ENTITY);
            case GuideBook.KeyArg k -> Component.keybind(k.mapping()).withStyle(ChatFormatting.BOLD).withColor(KEY);
        };
    }

    private ItemStack stack(Stack s) {
        return new ItemStack(s.item().get(), s.count());
    }

    /** Draws an item in a parchment slot and records it for the tooltip. */
    private void slot(GuiGraphics g, ItemStack stack, int x, int y, int mx, int my) {
        sprite(g, x, y, SLOT_U, 0, 18, 18);
        if (stack.isEmpty()) return;
        g.renderItem(stack, x + 1, y + 1);
        g.renderItemDecorations(font, stack, x + 1, y + 1);
        if (over(mx, my, x, y, 18, 18)) hoverStack = stack;
    }

    private final class TitleBlock implements Block {
        final List<FormattedCharSequence> lines;

        TitleBlock(List<FormattedCharSequence> lines) {
            this.lines = lines;
        }

        @Override
        public int height() {
            return lines.size() * 10 + 10;
        }

        @Override
        public void render(GuiGraphics g, int x, int y, int mx, int my) {
            int ly = y;
            for (FormattedCharSequence line : lines) {
                g.drawString(font, line, x + (PAGE_W - font.width(line)) / 2, ly, HEADING, false);
                ly += 10;
            }
            sprite(g, x + (PAGE_W - ORNAMENT_W) / 2, ly + 2, ORNAMENT_U, ORNAMENT_V, ORNAMENT_W, ORNAMENT_H);
        }
    }

    private final class HeadingBlock implements Block {
        final List<FormattedCharSequence> lines;

        HeadingBlock(Component text) {
            this.lines = font.split(text, PAGE_W);
        }

        @Override
        public int height() {
            return lines.size() * 10 + 3;
        }

        @Override
        public void render(GuiGraphics g, int x, int y, int mx, int my) {
            int ly = y, widest = 0;
            for (FormattedCharSequence line : lines) {
                g.drawString(font, line, x, ly, HEADING, false);
                widest = Math.max(widest, font.width(line));
                ly += 10;
            }
            g.fill(x, ly, x + widest, ly + 1, GOLD_LINE);
        }
    }

    private final class LineBlock implements Block {
        final FormattedCharSequence text;
        final int indent;
        final boolean tip;

        LineBlock(FormattedCharSequence text, int indent, boolean tip) {
            this.text = text;
            this.indent = indent;
            this.tip = tip;
        }

        @Override
        public int height() {
            return 10;
        }

        @Override
        public void render(GuiGraphics g, int x, int y, int mx, int my) {
            if (tip) {
                g.fill(x, y - 1, x + PAGE_W, y + 10, TIP_BG);
                g.fill(x, y - 1, x + 2, y + 10, TIP_EDGE);
            }
            int tx = x + indent;
            g.drawString(font, text, tx, y, INK, false);
            if (over(mx, my, tx, y - 1, PAGE_W - indent, 10)) {
                Style s = font.getSplitter().componentStyleAtWidth(text, mx - tx);
                if (s != null && s.getHoverEvent() != null) hoverStyle = s;
            }
        }
    }

    /** Top or bottom edge of a tip card. */
    private static final class TipPad implements Block {
        final boolean topEdge;

        TipPad(boolean topEdge) {
            this.topEdge = topEdge;
        }

        @Override
        public int height() {
            return topEdge ? 3 : 4;
        }

        @Override
        public void render(GuiGraphics g, int x, int y, int mx, int my) {
            int y0 = topEdge ? y : y - 1, y1 = topEdge ? y + 3 : y + 2;
            g.fill(x, y0, x + PAGE_W, y1, TIP_BG);
            g.fill(x, y0, x + 2, y1, TIP_EDGE);
        }
    }

    private final class ItemsBlock implements Block {
        final List<Stack> stacks;

        ItemsBlock(List<Stack> stacks) {
            this.stacks = stacks;
        }

        @Override
        public int height() {
            return 20;
        }

        @Override
        public void render(GuiGraphics g, int x, int y, int mx, int my) {
            int w = stacks.size() * 20 - 2, sx = x + (PAGE_W - w) / 2;
            for (int i = 0; i < stacks.size(); i++) slot(g, stack(stacks.get(i)), sx + i * 20, y, mx, my);
        }
    }

    private final class CraftBlock implements Block {
        final ResourceLocation id;

        CraftBlock(ResourceLocation id) {
            this.id = id;
        }

        @Override
        public int height() {
            return 56;
        }

        @Override
        public void render(GuiGraphics g, int x, int y, int mx, int my) {
            var holder = minecraft.level == null ? null : minecraft.level.getRecipeManager().byKey(id).orElse(null);
            if (holder == null) {
                Component missing = Component.translatable(GuideUi.MISSING_RECIPE);
                g.drawString(font, missing, x + (PAGE_W - font.width(missing)) / 2, y + 24, ENTITY, false);
                return;
            }
            Recipe<?> recipe = holder.value();
            List<Ingredient> ings = recipe.getIngredients();
            int w = 3;
            if (recipe instanceof ShapedRecipe shaped) w = shaped.getWidth();
            int total = 54 + 6 + BIG_ARROW_W + 6 + 18, gx = x + (PAGE_W - total) / 2;
            long cycle = Util.getMillis() / 1000;
            for (int row = 0; row < 3; row++) {
                for (int col = 0; col < 3; col++) {
                    int idx = row * w + col;
                    ItemStack shown = ItemStack.EMPTY;
                    if (col < w && idx < ings.size()) {
                        ItemStack[] options = ings.get(idx).getItems();
                        if (options.length > 0) shown = options[(int) (cycle % options.length)];
                    }
                    slot(g, shown, gx + col * 18, y + row * 18, mx, my);
                }
            }
            int ax = gx + 54 + 6;
            sprite(g, ax, y + 27 - BIG_ARROW_H / 2, BIG_ARROW_U, 0, BIG_ARROW_W, BIG_ARROW_H);
            slot(g, recipe.getResultItem(minecraft.level.registryAccess()), ax + BIG_ARROW_W + 6, y + 18, mx, my);
        }
    }

    private final class StationBlock implements Block {
        final GuideBook.Station station;

        StationBlock(GuideBook.Station station) {
            this.station = station;
        }

        @Override
        public int height() {
            return 40;
        }

        @Override
        public void render(GuiGraphics g, int x, int y, int mx, int my) {
            ItemStack block = new ItemStack(station.block().get());
            g.renderItem(block, x, y);
            if (over(mx, my, x, y, 16, 16)) hoverStack = block;
            g.drawString(font, ellipsize(block.getHoverName(), PAGE_W - 20), x + 20, y + 4, INK_SOFT, false);

            int n = station.mats().size();
            int total = 18 + (n > 0 ? 3 + PLUS_SIZE + 3 + n * 18 : 0) + 3 + SMALL_ARROW_W + 3 + 18;
            int sx = x + (PAGE_W - total) / 2, sy = y + 20;
            slot(g, new ItemStack(station.base().get()), sx, sy, mx, my);
            sx += 18;
            if (n > 0) {
                sprite(g, sx + 3, sy + 6, PLUS_U, 0, PLUS_SIZE, PLUS_SIZE);
                sx += 3 + PLUS_SIZE + 3;
                for (Stack m : station.mats()) {
                    slot(g, stack(m), sx, sy, mx, my);
                    sx += 18;
                }
            }
            sprite(g, sx + 3, sy + 5, SMALL_ARROW_U, 0, SMALL_ARROW_W, SMALL_ARROW_H);
            sx += 3 + SMALL_ARROW_W + 3;
            slot(g, new ItemStack(station.result().get()), sx, sy, mx, my);
        }
    }
}
