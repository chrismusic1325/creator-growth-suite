from pathlib import Path
import json

from platform_adapters import get_adapters


ROOT = Path(__file__).resolve().parent

adapters = get_adapters(ROOT)

print("=" * 68)
print(" CREATOR GROWTH SUITE - PLATFORM ADAPTER STATUS")
print("=" * 68)

all_present = True

for name, adapter in adapters.items():
    print()
    print(name.upper())
    print("-" * 68)

    try:
        caps = adapter.capabilities()
    except Exception as exc:
        caps = {"error": str(exc)}
        all_present = False

    print(json.dumps(caps, indent=2))

print()
print("=" * 68)
print("STATUS DEFINITIONS")
print("=" * 68)
print("connected=true")
print("  account/service connection exists")
print()
print("optimize_existing=true")
print("  repo contains an executable optimization action")
print()
print("publish_new=true")
print("  repo contains an executable publishing action")
print()
print("traffic_destination=true")
print("  platform may receive promoted traffic")
print()
print("sales_destination=true")
print("  destination may receive tracked sales traffic")
print()
print("No capability is reported TRUE merely because its name")
print("appears in configuration.")
print("=" * 68)
