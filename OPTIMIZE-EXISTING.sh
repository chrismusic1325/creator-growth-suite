#!/usr/bin/env bash

cd "$HOME/creator-growth-suite" || exit 1

python - <<'PY'
from pathlib import Path
from platform_adapters import get_adapters

root = Path.home() / "creator-growth-suite"
adapter = get_adapters(root)["youtube"]

r = adapter.optimize_existing()

print()
print(r.to_dict())
PY
