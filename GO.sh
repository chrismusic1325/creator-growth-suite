#!/usr/bin/env bash
set +e

ROOT="$HOME/creator-growth-suite"
AGENT="$ROOT/engines/agenttube"
MILO="$ROOT/engines/miloagent"
MILOPY="$MILO/.venv/Scripts/python.exe"
RUNTIME="$ROOT/runtime"

mkdir -p "$RUNTIME"
cd "$ROOT" || exit 1

clear

echo "============================================================"
echo " CREATOR GROWTH SUITE"
echo "============================================================"
echo
echo "AgentTube:"
echo "  YouTube + Rumble"
echo "  Existing-content optimization first"
echo
echo "MiloAgent:"
echo "  NATIVE MILO ENGINE"
echo "  3-minute action cycle"
echo "  Destinations:"
echo "    YouTube"
echo "    Rumble"
echo "    Bandcamp"
echo "    Amaze / Teespring"
echo
echo "Daily targets:"
echo "  1,000 unique subscribers"
echo "  35,000 long-form views"
echo "  1,500,000 qualified Shorts views"
echo "  200 sales conversions"
echo "  1,000 unique visitors"
echo
echo "Trend + Script: MANUAL"
echo "Video Use:      MANUAL"
echo "Cost:           FREE ONLY"
echo "============================================================"

[ -f "$ROOT/.creator-local.env" ] && \
    source "$ROOT/.creator-local.env"

[ -f "$ROOT/launchers/free-only-env.sh" ] && \
    source "$ROOT/launchers/free-only-env.sh"

export OPTIMIZE_EXISTING_ONLY=1

unset OPENAI_API_KEY
unset REPLICATE_API_KEY
unset REPLICATE_API_TOKEN
unset ANTHROPIC_API_KEY

# Stop stale copies belonging to THIS suite only.
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

echo
echo "[1/3] Dashboard"

nohup python "$ROOT/dashboard/server.py" \
    > "$RUNTIME/dashboard.log" 2>&1 &

sleep 3

echo "[2/3] AgentTube"

(
    cd "$AGENT" || exit 1

    nohup npm start \
        > "$RUNTIME/agenttube.log" 2>&1 &
)

sleep 7

echo "[3/3] Native MiloAgent"

if [ -f "$MILOPY" ]; then
    (
        cd "$MILO" || exit 1

        nohup "$MILOPY" miloagent.py run \
            > "$RUNTIME/miloagent.log" 2>&1 &
    )
else
    echo "ERROR: Milo Python environment missing."
fi

sleep 4

# Run current YouTube optimization without invoking video generation.
if [ -x "$ROOT/OPTIMIZE-EXISTING.sh" ]; then
    nohup "$ROOT/OPTIMIZE-EXISTING.sh" \
        > "$RUNTIME/existing-content-optimization.log" 2>&1 &
fi

cmd.exe /c start "" "http://127.0.0.1:8765" \
    >/dev/null 2>&1

echo
echo "============================================================"
echo " RUNNING"
echo "============================================================"
echo
echo "AgentTube + native MiloAgent are running."
echo
echo "Milo retains its original scheduler/action system."
echo "Only its Creator Growth destinations/goals were redirected."
echo
echo "Normal command:"
echo
echo "  cd ~/creator-growth-suite && ./GO.sh"
echo
echo "============================================================"
