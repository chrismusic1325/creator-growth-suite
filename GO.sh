#!/usr/bin/env bash
set +e

ROOT="$HOME/creator-growth-suite"
AGENT="$ROOT/engines/agenttube"
MILO="$ROOT/engines/miloagent"
PY="$MILO/.venv/Scripts/python.exe"
RUNTIME="$ROOT/runtime"

cd "$ROOT" || {
    echo "ERROR: Creator Growth Suite not found."
    exit 1
}

mkdir -p "$RUNTIME"

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
echo "  Native Milo engine"
echo "  YouTube"
echo "  Rumble"
echo "  Bandcamp"
echo "  Amaze / Teespring"
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

# ------------------------------------------------------------
# Free-only environment
# ------------------------------------------------------------

[ -f "$ROOT/.creator-local.env" ] &&
    source "$ROOT/.creator-local.env"

[ -f "$ROOT/launchers/free-only-env.sh" ] &&
    source "$ROOT/launchers/free-only-env.sh"

unset OPENAI_API_KEY
unset ANTHROPIC_API_KEY
unset REPLICATE_API_KEY
unset REPLICATE_API_TOKEN

export OPTIMIZE_EXISTING_ONLY=1

# ------------------------------------------------------------
# Dependencies required by CURRENT implementation
# ------------------------------------------------------------

if [ ! -f "$PY" ]; then
    echo
    echo "ERROR: Milo Python environment is missing:"
    echo "  $PY"
    echo
    exit 1
fi

"$PY" -c "import playwright" >/dev/null 2>&1

if [ $? -ne 0 ]; then
    echo
    echo "Installing missing free Playwright Python package..."
    "$PY" -m pip install --disable-pip-version-check playwright || exit 1
fi

# AgentTube dependencies only if actually absent.
if [ ! -d "$AGENT/node_modules" ]; then
    echo
    echo "Installing missing AgentTube dependencies..."
    (
        cd "$AGENT" || exit 1
        npm install
    ) || exit 1
fi

# ------------------------------------------------------------
# Stop stale copies from THIS repo only
# ------------------------------------------------------------

echo
echo "[1/3] Clearing stale Creator Growth processes..."

powershell.exe -NoProfile -Command '
Get-CimInstance Win32_Process |
Where-Object {
    $_.CommandLine -like "*creator-growth-suite*" -and
    $_.Name -in @("node.exe","python.exe","pythonw.exe","py.exe")
} |
ForEach-Object {
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
}
' >/dev/null 2>&1

sleep 2

# ------------------------------------------------------------
# Dashboard
# ------------------------------------------------------------

echo "[2/3] Starting dashboard..."

nohup python "$ROOT/dashboard/server.py" \
    > "$RUNTIME/dashboard.log" 2>&1 &

sleep 3

# ------------------------------------------------------------
# AgentTube
# ------------------------------------------------------------

echo "[3/3] Starting AgentTube + native Milo..."

(
    cd "$AGENT" || exit 1
    nohup npm start \
        > "$RUNTIME/agenttube.log" 2>&1 &
)

# Milo remains the native Milo runtime.
(
    cd "$MILO" || exit 1
    nohup "$PY" miloagent.py run \
        > "$RUNTIME/miloagent.log" 2>&1 &
)

sleep 8

# Existing-content optimization remains priority.
if [ -x "$ROOT/OPTIMIZE-EXISTING.sh" ]; then
    nohup "$ROOT/OPTIMIZE-EXISTING.sh" \
        > "$RUNTIME/existing-content-optimization.log" 2>&1 &
fi

# ------------------------------------------------------------
# Actual status
# ------------------------------------------------------------

echo
echo "============================================================"
echo " SERVICE STATUS"
echo "============================================================"

powershell.exe -NoProfile -Command '
foreach($p in @(8765,3456,8420)){
    $c = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue
    if($c){
        Write-Host "PORT $p : RUNNING"
    } else {
        if($p -eq 8420){
            Write-Host "PORT $p : OPTIONAL / background Milo may still be running"
        } else {
            Write-Host "PORT $p : NOT RUNNING"
        }
    }
}
'

echo
echo "AgentTube log:"
grep -E \
'initialized successfully|running on port 3456|ERROR|Error|failed' \
"$RUNTIME/agenttube.log" 2>/dev/null | tail -5

echo
echo "Milo log:"
grep -E \
'started in background|_scan_all_safe|_act_on_best_safe|ERROR|Error|failed' \
"$RUNTIME/miloagent.log" 2>/dev/null | tail -8

echo
echo "============================================================"
echo " STARTUP COMPLETE"
echo "============================================================"
echo
echo "Dashboard:"
echo "  http://127.0.0.1:8765"
echo
echo "AgentTube:"
echo "  http://127.0.0.1:3456"
echo
echo "From any future Git Bash window use:"
echo
echo "  cd ~/creator-growth-suite && ./GO.sh"
echo
echo "============================================================"

cmd.exe /c start "" "http://127.0.0.1:8765" >/dev/null 2>&1
