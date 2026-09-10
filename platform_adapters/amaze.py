import json, re, time
from pathlib import Path
from .base import PlatformAdapter
from .live_browser import browser, profile_exists, page_text

class AmazeAdapter(PlatformAdapter):
    name = "amaze"
    profile_name = "amaze-spring-browser"

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
        with browser(self.root, self.profile_name) as page:
            page.goto(
                "https://dashboard.teespring.com/",
                wait_until="domcontentloaded",
                timeout=60000
            )
            page.wait_for_timeout(3000)
            text = page_text(page)
            used = page.url

        metrics = re.findall(
            r'(?i)(orders?|sales?|visitors?|views?|revenue|profit|conversions?)'
            r'\D{0,30}([$]?[\d,.]+)',
            text
        )

        result = {
            "platform": "amaze",
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
