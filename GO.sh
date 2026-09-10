#!/usr/bin/env bash

ROOT="$HOME/creator-growth-suite"
cd "$ROOT" || exit 1

clear
echo "============================================================"
echo " CREATOR GROWTH SUITE"
echo "============================================================"
echo
echo "AgentTube  : YouTube + Rumble"
echo "MiloAgent  : YouTube + Rumble + Bandcamp + Amaze/Teespring"
echo "Trend+Script: manual"
echo "Video Use   : manual"
echo
echo "Starting dashboard..."
echo

exec bash "$ROOT/start.sh"
