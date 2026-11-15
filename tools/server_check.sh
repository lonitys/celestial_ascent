#!/bin/bash
# Validates worldgen on a fresh dev world: every structure is found, generated and contains its blocks.
# Usage: rm -rf run/devworld; bash tools/server_check.sh | ./gradlew runServer
sleep 80
for s in frost_shrine storm_shrine tide_shrine trade_city; do echo "celestialascent verify celestialascent:$s"; sleep 25; done
echo "execute in minecraft:the_nether run celestialascent verify celestialascent:magma_shrine"; sleep 30
echo "execute in minecraft:the_end run celestialascent verify celestialascent:ruined_capital"; sleep 30
echo "execute in minecraft:the_end run celestialascent verify celestialascent:star_gate"; sleep 30
for s in seraph_sanctum leviathan_sanctum herald_sanctum; do echo "execute in celestialascent:fallen_stars run celestialascent verify celestialascent:$s"; sleep 25; done
echo "stop"
