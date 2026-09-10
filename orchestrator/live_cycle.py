from pathlib import Path
import json, time, sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from platform_adapters import get_adapters

OUT = ROOT / "runtime" / "live-cycle.jsonl"

def record(obj):
    obj["timestamp"] = int(time.time())
    with OUT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\\n")
    print(json.dumps(obj, ensure_ascii=False), flush=True)

def cycle():
    adapters = get_adapters(ROOT)

    # PRIORITY 1: existing YouTube optimization
    try:
        result = adapters["youtube"].optimize_existing()
        record({
            "platform": "youtube",
            "priority": "existing_content_optimization",
            "result": result.to_dict() if hasattr(result, "to_dict") else str(result)
        })
    except Exception as exc:
        record({"platform":"youtube","error":str(exc)})

    # PRIORITY 2: existing Rumble optimization
    try:
        result = adapters["rumble"].optimize_existing(max_items=10)
        record({
            "platform": "rumble",
            "priority": "existing_content_optimization",
            "result": result
        })
    except Exception as exc:
        record({"platform":"rumble","error":str(exc)})

    # Metrics / conversion destinations
    for name in ("rumble", "bandcamp", "amaze"):
        try:
            result = adapters[name].analytics_snapshot()
            record({
                "platform": name,
                "priority": "metrics_and_conversion_tracking",
                "result": result
            })
        except Exception as exc:
            record({"platform":name,"error":str(exc)})

def main():
    once = "--once" in sys.argv

    while True:
        cycle()

        if once:
            break

        time.sleep(1800)

if __name__ == "__main__":
    main()
