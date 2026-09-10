#!/usr/bin/env bash

cd "$HOME/creator-growth-suite" || exit 1

python - <<'PY'
from pathlib import Path
from platform_adapters import get_adapters

root = Path.home() / "creator-growth-suite"

adapters = get_adapters(root)

for name in ("rumble", "bandcamp", "amaze"):
    result = adapters[name].open_dashboard()
    print(result.to_dict())
PY
