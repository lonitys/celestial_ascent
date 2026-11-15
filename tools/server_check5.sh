#!/bin/bash
sleep 60
echo "forceload add 2000 2000 2100 2100"; sleep 30
echo "place structure celestialascent:storm_shrine 2050 100 2050"; sleep 8
echo "execute positioned 2050 100 2050 run celestialascent starts"; sleep 3
echo "execute positioned 2050 60 2050 run celestialascent scan 64"; sleep 15
echo "stop"
