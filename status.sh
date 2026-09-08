#!/usr/bin/env bash
cd "$(dirname "$0")"
echo "============================================================"
echo " CREATOR GROWTH SUITE - FINAL STATUS"
echo "============================================================"
check(){ if [ -e "$2" ]; then printf "%-24s OK\n" "$1"; else printf "%-24s MISSING\n" "$1"; fi; }
check "Avatar" "media/avatar.jpg"
check "AgentTube source" "engines/agenttube/package.json"
check "AgentTube deps" "engines/agenttube/node_modules"
check "MiloAgent source" "engines/miloagent/miloagent.py"
check "MiloAgent deps" "engines/miloagent/.venv/Scripts/python.exe"
check "Video Use source" "engines/video-use/pyproject.toml"
check "Video Use deps" "engines/video-use/.venv/Scripts/python.exe"
check "Trend/script engine" "engines/trend-script-agent"
check "Dashboard" "dashboard/server.py"
echo
powershell.exe -NoProfile -Command '$d=Get-PSDrive C; "C: FREE = {0:N2} GB" -f ($d.Free/1GB)'
echo
echo "Still requires your interactive account authorization where applicable:"
echo "  YouTube / Google OAuth"
echo "  Rumble login/publishing authorization"
echo "  MiloAgent platform login(s)"
echo "  Bandcamp destination/account details"
echo "  Teespring/Amaze destination/account details"
