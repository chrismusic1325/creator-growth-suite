#!/usr/bin/env bash
set +e

ROOT="$HOME/creator-growth-suite"
AGENT="$ROOT/engines/agenttube"
MILO="$ROOT/engines/miloagent"
PY="$MILO/.venv/Scripts/python.exe"
RUNTIME="$ROOT/runtime"

mkdir -p "$RUNTIME"
cd "$ROOT" || exit 1

clear
echo "============================================================"
echo " CREATOR GROWTH SUITE"
echo "============================================================"
echo "AgentTube : YouTube + Rumble"
echo "Milo      : YouTube + Rumble + Bandcamp + Amaze/Teespring"
echo "Priority  : EXISTING CONTENT OPTIMIZATION"
echo "Manual    : Trend + Script / Video Use"
echo "Cost      : FREE ONLY"
echo "============================================================"

[ -f "$ROOT/.creator-local.env" ] && source "$ROOT/.creator-local.env"
[ -f "$ROOT/launchers/free-only-env.sh" ] && source "$ROOT/launchers/free-only-env.sh"

export OPTIMIZE_EXISTING_ONLY=1

unset OPENAI_API_KEY
unset ANTHROPIC_API_KEY
unset REPLICATE_API_KEY
unset REPLICATE_API_TOKEN

powershell.exe -NoProfile -Command '
Get-CimInstance Win32_Process |
Where-Object {
 $_.CommandLine -like "*creator-growth-suite*" -and
 $_.Name -in @("node.exe","python.exe","pythonw.exe","py.exe")
} |
ForEach-Object {
 Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
}
' 2>/dev/null

sleep 2

echo "[1/4] Dashboard"
nohup python "$ROOT/dashboard/server.py" \
 > "$RUNTIME/dashboard.log" 2>&1 &

sleep 3

echo "[2/4] AgentTube"
(
 cd "$AGENT" || exit 1
 nohup npm start > "$RUNTIME/agenttube.log" 2>&1 &
)

sleep 6

echo "[3/4] MiloAgent"
if [ -f "$PY" ]; then
 (
  cd "$MILO" || exit 1
  nohup "$PY" miloagent.py run > "$RUNTIME/miloagent.log" 2>&1 &
 )
fi

echo "[4/4] Live platform implementation"
if [ -f "$PY" ]; then
 nohup "$PY" -m orchestrator.live_cycle \
 > "$RUNTIME/live-cycle.log" 2>&1 &
fi

sleep 3

cmd.exe /c start "" "http://127.0.0.1:8765" >/dev/null 2>&1

echo
echo "============================================================"
echo " CREATOR GROWTH SUITE RUNNING"
echo "============================================================"
echo "Dashboard: http://127.0.0.1:8765"
echo "Live actions: runtime/live-platform-actions.jsonl"
echo "Cycle log:    runtime/live-cycle.log"
echo "============================================================"
