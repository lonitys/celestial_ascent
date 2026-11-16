package com.celestialascent.retrogen;

import com.celestialascent.CelestialAscent;
import com.celestialascent.retrogen.RetrogenData.Status;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.ResourceLocationArgument;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.structure.placement.RandomSpreadStructurePlacement;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.RegisterCommandsEvent;

import java.util.EnumMap;
import java.util.List;
import java.util.Map;

/**
 * Operator commands for the retrogen: {@code /celestialascent retrogen status|scan|run|pregen|hut}.
 * pregen and hut exist to test it (generate land, then put a "player build" on a structure spot).
 */
@EventBusSubscriber(modid = CelestialAscent.MODID)
public final class RetrogenCommands {
    private RetrogenCommands() {}

    @SubscribeEvent
    public static void register(RegisterCommandsEvent e) {
        e.getDispatcher().register(Commands.literal("celestialascent").requires(s -> s.hasPermission(2))
                .then(Commands.literal("retrogen")
                        .then(Commands.literal("status").executes(ctx -> status(ctx.getSource())))
                        .then(Commands.literal("scan").then(Commands.argument("radius", IntegerArgumentType.integer(1, 256)).executes(ctx -> {
                            var src = ctx.getSource();
                            int n = Retrogen.scan(src.getLevel(), new ChunkPos(BlockPos.containing(src.getPosition())), IntegerArgumentType.getInteger(ctx, "radius"));
                            src.sendSuccess(() -> Component.literal("retrogen: queued " + n + " cells"), false);
                            return n;
                        })))
                        .then(Commands.literal("run").executes(ctx -> run(ctx.getSource())))
                        .then(Commands.literal("pregen").then(Commands.argument("radius", IntegerArgumentType.integer(1, 64)).executes(ctx -> {
                            var src = ctx.getSource();
                            int r = IntegerArgumentType.getInteger(ctx, "radius");
                            ChunkPos c = new ChunkPos(BlockPos.containing(src.getPosition()));
                            int n = 0;
                            for (int x = c.x - r; x <= c.x + r; x++)
                                for (int z = c.z - r; z <= c.z + r; z++) {
                                    src.getLevel().getChunk(x, z);
                                    n++;
                                }
                            int total = n;
                            src.sendSuccess(() -> Component.literal("retrogen: generated " + total + " chunks"), false);
                            return n;
                        })))
                        .then(Commands.literal("hut").then(Commands.argument("set", ResourceLocationArgument.id()).executes(ctx -> hut(ctx.getSource(),
                                ResourceLocationArgument.getId(ctx, "set")))))));
    }

    private static int status(CommandSourceStack src) {
        ServerLevel level = src.getLevel();
        Map<Status, Integer> counts = new EnumMap<>(Status.class);
        StringBuilder built = new StringBuilder();
        RetrogenData.get(level).cells().forEach((k, e) -> {
            counts.merge(e.status, 1, Integer::sum);
            if (e.status == Status.PLACED || e.status == Status.RELOCATED || e.status == Status.BLOCKED) {
                built.append("\n  ").append(e.status).append(' ').append(e.structure == null ? "?" : e.structure.getPath())
                        .append(e.center == null ? "" : " at " + e.center.toShortString());
            }
        });
        src.sendSuccess(() -> Component.literal("retrogen " + level.dimension().location() + ": " + counts + built), false);
        return counts.size();
    }

    private static int run(CommandSourceStack src) {
        ServerLevel level = src.getLevel();
        RetrogenData data = RetrogenData.get(level);
        List<String> pending = data.cells().entrySet().stream().filter(en -> !en.getValue().done()).map(Map.Entry::getKey).toList();
        StringBuilder sb = new StringBuilder();
        for (String k : pending) {
            String result = Retrogen.process(level, k, true);
            if (!result.startsWith("not generated") && !result.startsWith("no structure")) sb.append("\n  ").append(k).append(": ").append(result);
        }
        src.sendSuccess(() -> Component.literal("retrogen: decided " + pending.size() + " cells" + sb), false);
        return pending.size();
    }

    /** Builds a small wooden hut with a chest on the nearest spot where a structure of this set would go. */
    private static int hut(CommandSourceStack src, net.minecraft.resources.ResourceLocation setId) {
        ServerLevel level = src.getLevel();
        var set = level.registryAccess().registryOrThrow(Registries.STRUCTURE_SET).getHolder(ResourceKey.create(Registries.STRUCTURE_SET, setId));
        if (set.isEmpty() || !(set.get().value().placement() instanceof RandomSpreadStructurePlacement p)) {
            src.sendFailure(Component.literal("no random-spread structure set " + setId));
            return 0;
        }
        var structure = set.get().value().structures().get(0).structure();
        ChunkPos from = new ChunkPos(BlockPos.containing(src.getPosition()));
        int s = p.spacing();
        BlockPos best = null;
        double bestD = Double.MAX_VALUE;
        for (int cx = Math.floorDiv(from.x, s) - 3; cx <= Math.floorDiv(from.x, s) + 3; cx++) {
            for (int cz = Math.floorDiv(from.z, s) - 3; cz <= Math.floorDiv(from.z, s) + 3; cz++) {
                ChunkPos o = p.getPotentialStructureChunk(level.getChunkSource().getGeneratorState().getLevelSeed(), cx * s, cz * s);
                if (!p.isStructureChunk(level.getChunkSource().getGeneratorState(), o.x, o.z)) continue;
                if (Retrogen.chunkState(level, o) != Retrogen.ChunkState.FULL) continue;
                var start = Retrogen.generate(level, structure, o);
                if (!start.isValid()) continue;
                var c = start.getBoundingBox().getCenter();
                double d = (double) (o.x - from.x) * (o.x - from.x) + (double) (o.z - from.z) * (o.z - from.z);
                if (d < bestD) {
                    bestD = d;
                    best = new BlockPos(c.getX(), 0, c.getZ());
                }
            }
        }
        if (best == null) {
            src.sendFailure(Component.literal("no spot for " + setId + " in generated land nearby"));
            return 0;
        }
        int y = SiteCheck.groundY(level, best.getX(), best.getZ(), null);
        BlockPos base = new BlockPos(best.getX(), y, best.getZ());
        for (int dx = -2; dx <= 2; dx++)
            for (int dz = -2; dz <= 2; dz++) {
                level.setBlockAndUpdate(base.offset(dx, -1, dz), Blocks.OAK_PLANKS.defaultBlockState());
                for (int dy = 0; dy < 3; dy++) {
                    boolean wall = Math.abs(dx) == 2 || Math.abs(dz) == 2;
                    level.setBlockAndUpdate(base.offset(dx, dy, dz), wall ? Blocks.OAK_PLANKS.defaultBlockState() : Blocks.AIR.defaultBlockState());
                }
                level.setBlockAndUpdate(base.offset(dx, 3, dz), Blocks.OAK_SLAB.defaultBlockState());
            }
        level.setBlockAndUpdate(base, Blocks.CHEST.defaultBlockState());
        BlockPos chest = base;
        src.sendSuccess(() -> Component.literal("hut with a chest at " + chest.toShortString()), false);
        return 1;
    }
}
