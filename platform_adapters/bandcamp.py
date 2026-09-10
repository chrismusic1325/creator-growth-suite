import json, re, time
from pathlib import Path
from .base import PlatformAdapter
from .live_browser import browser, profile_exists, page_text

class BandcampAdapter(PlatformAdapter):
    name = "bandcamp"
    profile_name = "bandcamp-browser"

    def capabilities(self):
        return {
            "connected": profile_exists(self.root, self.profile_name),
            "connection_type": "persistent_browser_session",
            "analytics": True,
            "optimize_existing": False,
            "publish_new": False,
            "sales_destination": True,
            "traffic_destination": True,
            "browser_session": profile_exists(self.root, self.profile_name)
        }

    def analytics_snapshot(self):
        urls = [
            "https://bandcamp.com/stats",
            "https://thetravelingvagabond7.bandcamp.com/"
        ]

        text = ""
        used = ""

        with browser(self.root, self.profile_name) as page:
            for url in urls:
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    page.wait_for_timeout(2500)
                    text = page_text(page)
                    used = page.url
                    if text:
                        break
                except Exception:
                    pass

        metrics = re.findall(
            r'(?i)(plays?|sales?|visitors?|views?|purchases?)\D{0,30}([\d,.]+)',
            text
        )

        result = {
            "platform": "bandcamp",
            "action": "analytics_snapshot",
            "timestamp": int(time.time()),
            "url": used,
            "metrics_found": metrics[:100]
        }

        self._write(result)
        return result

    def _write(self, obj):
        out = Path(self.root) / "runtime" / "live-platform-actions.jsonl"
        with out.open("a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\\n")
