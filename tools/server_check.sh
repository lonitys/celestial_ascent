#!/bin/bash
# Feeds commands into the dev server to validate worldgen. Usage: bash tools/server_check.sh | ./gradlew runServer
sleep 75
for s in frost_shrine storm_shrine tide_shrine trade_city; do echo "locate structure celestialascent:$s"; sleep 6; done
echo "execute in minecraft:the_nether run locate structure celestialascent:magma_shrine"; sleep 8
echo "execute in minecraft:the_end run locate structure celestialascent:ruined_capital"; sleep 8
echo "execute in minecraft:the_end run locate structure celestialascent:star_gate"; sleep 8
for s in seraph_sanctum leviathan_sanctum herald_sanctum; do echo "execute in celestialascent:fallen_stars run locate structure celestialascent:$s"; sleep 8; done
echo "execute in celestialascent:fallen_stars run forceload add 0 0"; sleep 10
echo "execute in celestialascent:abyss run forceload add 0 0"; sleep 10
echo "execute in celestialascent:fallen_stars run summon celestialascent:astral_seraph 0 150 0"; sleep 3
echo "execute in celestialascent:abyss run summon celestialascent:void_sovereign 0 60 0"; sleep 3
echo "summon celestialascent:frost_titan 0 100 0"; sleep 3
echo "kill @e[type=celestialascent:astral_seraph]"; echo "kill @e[type=celestialascent:void_sovereign]"; echo "kill @e[type=celestialascent:frost_titan]"
sleep 3
echo "stop"
