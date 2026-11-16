package com.celestialascent.core;

import com.celestialascent.CelestialAscent;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.RegisterCommandsEvent;

import java.util.Map;
import java.util.TreeMap;

/** Operator tools: /celestialascent scan &lt;radius&gt; counts structure blocks around you (worldgen checks). */
@EventBusSubscriber(modid = CelestialAscent.MODID)
public final class DebugCommands {
    private DebugCommands() {}

    @SubscribeEvent
    public static void register(RegisterCommandsEvent e) {
        if (net.neoforged.fml.loading.FMLEnvironment.production) return; // worldgen checks for development only
        e.getDispatcher().register(Commands.literal("celestialascent").requires(s -> s.hasPermission(2))
                .then(Commands.literal("gen").then(Commands.argument("structure", net.minecraft.commands.arguments.ResourceLocationArgument.id()).executes(ctx -> {
                    var src = ctx.getSource();
                    var level = src.getLevel();
                    var id = net.minecraft.commands.arguments.ResourceLocationArgument.getId(ctx, "structure");
                    var structure = level.registryAccess().registryOrThrow(net.minecraft.core.registries.Registries.STRUCTURE).get(id);
                    if (structure == null) {
                        src.sendFailure(Component.literal("no structure " + id));
                        return 0;
                    }
                    var gen = level.getChunkSource().getGenerator();
                    BlockPos c = BlockPos.containing(src.getPosition());
                    var start = structure.generate(level.registryAccess(), gen, gen.getBiomeSource(), level.getChunkSource().randomState(),
                            level.getStructureManager(), level.getSeed(), new net.minecraft.world.level.ChunkPos(c), 0, level, b -> true);
                    StringBuilder sb = new StringBuilder("valid=" + start.isValid() + " pieces=" + start.getPieces().size());
                    start.getPieces().forEach(p -> {
                        sb.append(" | ").append(p.getClass().getSimpleName()).append(' ').append(p.getBoundingBox());
                        if (p instanceof net.minecraft.world.level.levelgen.structure.PoolElementStructurePiece pe) {
                            sb.append(" elem=").append(pe.getElement()).append(" pos=").append(pe.getPosition().toShortString());
                        }
                    });
                    src.sendSuccess(() -> Component.literal(sb.toString()), false);
                    return 1;
                })))
                .then(Commands.literal("verify").then(Commands.argument("structure", net.minecraft.commands.arguments.ResourceLocationArgument.id()).executes(ctx -> {
                    var src = ctx.getSource();
                    var level = src.getLevel();
                    var id = net.minecraft.commands.arguments.ResourceLocationArgument.getId(ctx, "structure");
                    var reg = level.registryAccess().registryOrThrow(net.minecraft.core.registries.Registries.STRUCTURE);
                    var holder = reg.getHolder(net.minecraft.resources.ResourceKey.create(net.minecraft.core.registries.Registries.STRUCTURE, id));
                    if (holder.isEmpty()) {
                        src.sendFailure(Component.literal("no structure " + id));
                        return 0;
                    }
                    var found = level.getChunkSource().getGenerator().findNearestMapStructure(level,
                            net.minecraft.core.HolderSet.direct(holder.get()), BlockPos.containing(src.getPosition()), 100, false);
                    if (found == null) {
                        src.sendFailure(Component.literal("verify " + id + ": none found"));
                        return 0;
                    }
                    BlockPos at = found.getFirst();
                    var startChunk = level.getChunk(at.getX() >> 4, at.getZ() >> 4, net.minecraft.world.level.chunk.status.ChunkStatus.STRUCTURE_STARTS);
                    var start = startChunk.getStartForStructure(holder.get().value());
                    if (start == null || !start.isValid()) {
                        src.sendFailure(Component.literal("verify " + id + ": no start at " + at.toShortString()));
                        return 0;
                    }
                    var bb = start.getBoundingBox();
                    for (int cx = bb.minX() >> 4; cx <= bb.maxX() >> 4; cx++)
                        for (int cz = bb.minZ() >> 4; cz <= bb.maxZ() >> 4; cz++) level.getChunk(cx, cz); // generate fully
                    Map<String, Integer> counts = new TreeMap<>();
                    int solid = 0;
                    for (BlockPos p : BlockPos.betweenClosed(bb.minX(), bb.minY(), bb.minZ(), bb.maxX(), bb.maxY(), bb.maxZ())) {
                        BlockState s = level.getBlockState(p);
                        if (!s.isAir()) solid++;
                        var bid = BuiltInRegistries.BLOCK.getKey(s.getBlock());
                        if (bid.getNamespace().equals(CelestialAscent.MODID)) counts.merge(bid.getPath(), 1, Integer::sum);
                    }
                    int solidF = solid;
                    src.sendSuccess(() -> Component.literal("verify " + id + " at " + bb + " solid=" + solidF + " mod=" + counts), false);
                    return counts.isEmpty() ? 0 : 1;
                })))
                .then(Commands.literal("starts").executes(ctx -> {
                    var src = ctx.getSource();
                    BlockPos c = BlockPos.containing(src.getPosition());
                    var level = src.getLevel();
                    StringBuilder sb = new StringBuilder();
                    for (int dx = -4; dx <= 4; dx++)
                        for (int dz = -4; dz <= 4; dz++) {
                            var chunk = level.getChunk((c.getX() >> 4) + dx, (c.getZ() >> 4) + dz, net.minecraft.world.level.chunk.status.ChunkStatus.STRUCTURE_STARTS);
                            chunk.getAllStarts().forEach((structure, start) -> {
                                if (!start.isValid()) return;
                                var key = level.registryAccess().registryOrThrow(net.minecraft.core.registries.Registries.STRUCTURE).getKey(structure);
                                if (key == null || !key.getNamespace().equals(CelestialAscent.MODID)) return;
                                sb.append(key.getPath()).append(" pieces=").append(start.getPieces().size());
                                start.getPieces().forEach(p -> sb.append(' ').append(p.getBoundingBox()));
                                sb.append("; ");
                            });
                        }
                    src.sendSuccess(() -> Component.literal("starts: " + sb), false);
                    return 1;
                }))
                .then(Commands.literal("scan").then(Commands.argument("radius", IntegerArgumentType.integer(1, 64)).executes(ctx -> {
                    int r = IntegerArgumentType.getInteger(ctx, "radius");
                    var src = ctx.getSource();
                    BlockPos c = BlockPos.containing(src.getPosition());
                    Map<String, Integer> counts = new TreeMap<>();
                    var level = src.getLevel();
                    for (BlockPos p : BlockPos.betweenClosed(c.offset(-r, -r, -r), c.offset(r, r, r))) {
                        BlockState s = level.getBlockState(p);
                        var id = BuiltInRegistries.BLOCK.getKey(s.getBlock());
                        if (id.getNamespace().equals(CelestialAscent.MODID) || s.is(net.minecraft.world.level.block.Blocks.PURPUR_BLOCK)
                                || s.is(net.minecraft.world.level.block.Blocks.PRISMARINE_BRICKS) || s.is(net.minecraft.world.level.block.Blocks.STONE_BRICKS)) {
                            counts.merge(id.getPath(), 1, Integer::sum);
                        }
                    }
                    src.sendSuccess(() -> Component.literal("scan " + c.toShortString() + " r=" + r + ": " + counts), false);
                    return counts.size();
                }))));
    }
}
