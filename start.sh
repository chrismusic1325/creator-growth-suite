#!/usr/bin/env bash
cd "$(dirname "$0")"
if command -v python >/dev/null 2>&1; then
  python dashboard/server.py
elif command -v py >/dev/null 2>&1; then
  py dashboard/server.py
else
  python3 dashboard/server.py
fi
echo
read -p "Press Enter to close..."
