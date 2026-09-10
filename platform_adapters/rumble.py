from pathlib import Path
import json, re, time
from .base import PlatformAdapter
from .live_browser import browser, profile_exists, page_text

class RumbleAdapter(PlatformAdapter):
    name = "rumble"
    profile_name = "rumble-browser"

    def capabilities(self):
        return {
            "connected": profile_exists(self.root, self.profile_name),
            "connection_type": "persistent_browser_session",
            "analytics": True,
            "optimize_existing": True,
            "publish_new": True,
            "sales_destination": False,
            "traffic_destination": True,
            "browser_session": profile_exists(self.root, self.profile_name)
        }

    def analytics_snapshot(self):
        with browser(self.root, self.profile_name) as page:
            page.goto(
                "https://rumble.com/account/content",
                wait_until="domcontentloaded",
                timeout=60000
            )
            page.wait_for_timeout(3000)
            text = page_text(page)

        nums = re.findall(
            r'(?i)(views?|followers?|comments?|likes?)\D{0,20}([\d,.]+)',
            text
        )

        result = {
            "platform": "rumble",
            "action": "analytics_snapshot",
            "timestamp": int(time.time()),
            "page": "account/content",
            "metrics_found": nums[:100]
        }

        self._write_live(result)
        return result

    def inventory(self):
        with browser(self.root, self.profile_name) as page:
            page.goto(
                "https://rumble.com/account/content",
                wait_until="domcontentloaded",
                timeout=60000
            )
            page.wait_for_timeout(3000)

            links = page.locator("a").evaluate_all("""
                els => els.map(a => ({
                    text:(a.innerText||'').trim(),
                    href:a.href||''
                })).filter(x =>
                    /edit/i.test(x.text) ||
                    /edit/i.test(x.href)
                )
            """)

        return links

    def optimize_existing(self, max_items=10):
        links = self.inventory()
        edits = []

        footer = (
            "\\n\\nFollow The Traveling Vagabond 7:\\n"
            "YouTube: https://www.youtube.com/@thetravelingvagabond7\\n"
            "Music: https://thetravelingvagabond7.bandcamp.com/"
        )

        for item in links[:max_items]:
            href = item.get("href")
            if not href:
                continue

            try:
                with browser(self.root, self.profile_name) as page:
                    page.goto(href, wait_until="domcontentloaded", timeout=60000)
                    page.wait_for_timeout(2000)

                    desc = page.locator(
                        'textarea[name*="description" i], textarea[id*="description" i], textarea'
                    ).first

                    if desc.count():
                        existing = desc.input_value()

                        if "thetravelingvagabond7.bandcamp.com" not in existing:
                            desc.fill(existing.rstrip() + footer)

                            saved = False

                            for label in ("Save", "Update", "Submit"):
                                b = page.get_by_role(
                                    "button",
                                    name=re.compile(label, re.I)
                                )

                                if b.count():
                                    b.first.click()
                                    page.wait_for_timeout(2000)
                                    saved = True
                                    break

                            edits.append({
                                "href": href,
                                "changed": saved
                            })

            except Exception as exc:
                edits.append({
                    "href": href,
                    "changed": False,
                    "error": str(exc)
                })

        result = {
            "platform": "rumble",
            "action": "optimize_existing",
            "timestamp": int(time.time()),
            "attempted": len(edits),
            "results": edits
        }

        self._write_live(result)
        return result

    def publish_file(self, filepath, title, description):
        path = Path(filepath)

        if not path.exists():
            raise FileNotFoundError(path)

        with browser(self.root, self.profile_name) as page:
            page.goto(
                "https://rumble.com/upload.php",
                wait_until="domcontentloaded",
                timeout=60000
            )

            page.set_input_files('input[type="file"]', str(path))

            title_box = page.locator(
                'input[name*="title" i], input[id*="title" i]'
            ).first

            if title_box.count():
                title_box.fill(title)

            desc = page.locator(
                'textarea[name*="description" i], textarea'
            ).first

            if desc.count():
                desc.fill(description)

            result = {
                "platform": "rumble",
                "action": "upload_form_filled",
                "timestamp": int(time.time()),
                "file": str(path)
            }

            self._write_live(result)
            return result

    def _write_live(self, obj):
        out = Path(self.root) / "runtime" / "live-platform-actions.jsonl"
        with out.open("a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\\n")
