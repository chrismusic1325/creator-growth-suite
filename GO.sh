#!/usr/bin/env bash
set +e

ROOT="$HOME/creator-growth-suite"
AGENT="$ROOT/engines/agenttube"
MILO="$ROOT/engines/miloagent"
RUNTIME="$ROOT/runtime"

mkdir -p "$RUNTIME"

cd "$ROOT" || exit 1

clear

echo "============================================================"
echo " CREATOR GROWTH SUITE"
echo "============================================================"
echo
echo "PRIORITY:"
echo "  EXISTING CONTENT OPTIMIZATION"
echo
echo "AgentTube:"
echo "  YouTube + Rumble"
echo
echo "MiloAgent:"
echo "  YouTube + Rumble + Bandcamp + Amaze/Teespring"
echo
echo "Manual:"
echo "  Trend + Script"
echo "  Video Use"
echo
echo "Free only:"
echo "  YES"
echo "============================================================"

[ -f "$ROOT/.creator-local.env" ] && source "$ROOT/.creator-local.env"
[ -f "$ROOT/launchers/free-only-env.sh" ] && source "$ROOT/launchers/free-only-env.sh"

export OPTIMIZE_EXISTING_ONLY=1

unset OPENAI_API_KEY
unset ANTHROPIC_API_KEY
unset REPLICATE_API_KEY
unset REPLICATE_API_TOKEN

echo
echo "[1/4] Starting dashboard..."

nohup python "$ROOT/dashboard/server.py" \
  > "$RUNTIME/dashboard.log" 2>&1 &

sleep 3

echo "[2/4] Starting AgentTube..."

(
  cd "$AGENT" || exit 1
  nohup npm start \
    > "$RUNTIME/agenttube.log" 2>&1 &
)

sleep 6

echo "[3/4] Starting MiloAgent..."

MILOPY="$MILO/.venv/Scripts/python.exe"

if [ -f "$MILOPY" ]; then
  (
    cd "$MILO" || exit 1
    nohup "$MILOPY" miloagent.py run \
      > "$RUNTIME/miloagent.log" 2>&1 &
  )
else
  echo "Milo Python environment missing."
fi

echo "[4/4] Starting current optimization cycle..."

if [ -x "$ROOT/OPTIMIZE-EXISTING.sh" ]; then
  nohup "$ROOT/OPTIMIZE-EXISTING.sh" \
    > "$RUNTIME/existing-content-optimization.log" 2>&1 &
fi

sleep 3

cmd.exe /c start "" "http://127.0.0.1:8765" \
  >/dev/null 2>&1

echo
echo "============================================================"
echo " CREATOR GROWTH SUITE STARTED"
echo "============================================================"
echo
echo "Dashboard:"
echo "  http://127.0.0.1:8765"
echo
echo "Capability status:"
echo "  python platform-status.py"
echo
echo "============================================================"
