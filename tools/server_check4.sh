#!/bin/bash
sleep 60
echo "forceload add 1000 1000 1100 1100"; sleep 30
echo "place template celestialascent:shrines/frost_shrine 1010 100 1010"; sleep 4
echo "execute positioned 1026 104 1026 run celestialascent scan 20"; sleep 4
echo "place structure celestialascent:storm_shrine 1070 100 1070"; sleep 8
echo "execute positioned 1070 90 1070 run celestialascent scan 40"; sleep 6
echo "stop"
