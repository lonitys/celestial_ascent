#!/bin/bash
sleep 60
echo "forceload add 200 200 260 260"; sleep 8
echo "place template celestialascent:shrines/frost_shrine 200 120 200"; sleep 4
echo "place structure celestialascent:frost_shrine 300 100 300"; sleep 6
echo "place jigsaw celestialascent:shrines/frost minecraft:empty 1 400 100 400"; sleep 6
echo "execute in celestialascent:fallen_stars run place structure celestialascent:seraph_sanctum 0 120 0"; sleep 6
echo "stop"
