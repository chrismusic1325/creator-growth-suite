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

# ============================================================
# Creator Growth Suite - hidden Rumble Edit implementation
# ============================================================

def _cgs_rumble_hidden_edit(self, max_items=1):
    import json
    import time
    from pathlib import Path
    from .live_browser import browser

    results = []

    with browser(self.root, self.profile_name) as page:

        page.goto(
            "https://rumble.com/account/content?type=all",
            wait_until="domcontentloaded",
            timeout=60000
        )

        page.wait_for_timeout(4000)

        edits = page.locator('a.action#edit')

        total = edits.count()

        count = min(total, max_items)

        for i in range(count):

            try:
                target = edits.nth(i)

                before_url = page.url

                # Fire the real DOM click even though Rumble keeps
                # the anchor hidden in the page markup.
                target.evaluate("(el) => el.click()")

                page.wait_for_timeout(2500)

                # Collect what appeared after the JS event.
                visible_textareas = page.locator(
                    "textarea:visible"
                )

                visible_inputs = page.locator(
                    'input:visible'
                )

                dialogs = page.locator(
                    '[role="dialog"]:visible, '
                    '.modal:visible, '
                    '[class*="modal"]:visible'
                )

                desc = page.locator(
                    'textarea[name*="description" i]:visible, '
                    'textarea[id*="description" i]:visible, '
                    'textarea[placeholder*="description" i]:visible'
                )

                title = page.locator(
                    'input[name*="title" i]:visible, '
                    'input[id*="title" i]:visible, '
                    'input[placeholder*="title" i]:visible'
                )

                # Broader fallback because Rumble may not label
                # the textarea semantically.
                if desc.count() == 0 and visible_textareas.count():
                    desc = visible_textareas

                editor_found = (
                    desc.count() > 0
                    or title.count() > 0
                    or dialogs.count() > 0
                    or page.url != before_url
                )

                if not editor_found:
                    results.append({
                        "editor_found": False,
                        "status": "DOM_CLICK_FIRED_NO_EDITOR",
                        "before_url": before_url,
                        "after_url": page.url,
                        "visible_textareas": visible_textareas.count(),
                        "visible_inputs": visible_inputs.count(),
                        "dialogs": dialogs.count()
                    })
                    continue

                if desc.count() == 0:
                    results.append({
                        "editor_found": True,
                        "changed": False,
                        "status": "EDITOR_REACHED",
                        "url": page.url,
                        "dialogs": dialogs.count(),
                        "visible_inputs": visible_inputs.count()
                    })
                    continue

                box = desc.first

                try:
                    existing = box.input_value()
                except Exception:
                    existing = box.inner_text()

                footer = (
                    "\n\n"
                    "More from The Traveling Vagabond 7:\n"
                    "YouTube: https://www.youtube.com/@thetravelingvagabond7\n"
                    "Music: https://thetravelingvagabond7.bandcamp.com/"
                )

                if "thetravelingvagabond7.bandcamp.com" in existing:

                    results.append({
                        "editor_found": True,
                        "changed": False,
                        "status": "ALREADY_OPTIMIZED",
                        "url": page.url
                    })
                    continue

                box.fill(existing.rstrip() + footer)

                save = page.locator(
                    'button:has-text("Save"):visible, '
                    'button:has-text("Update"):visible, '
                    'button:has-text("Submit"):visible, '
                    'button[type="submit"]:visible, '
                    'input[type="submit"]:visible'
                )

                if save.count() == 0:
                    results.append({
                        "editor_found": True,
                        "changed": False,
                        "status": "EDITOR_REACHED_SAVE_NOT_FOUND",
                        "url": page.url
                    })
                    continue

                save.first.click(force=True)
                page.wait_for_timeout(2500)

                results.append({
                    "editor_found": True,
                    "changed": True,
                    "status": "SAVED",
                    "url": page.url
                })

            except Exception as exc:

                results.append({
                    "editor_found": False,
                    "status": "ERROR",
                    "error": str(exc)
                })

    result = {
        "platform": "rumble",
        "action": "optimize_existing",
        "timestamp": int(time.time()),
        "edit_controls_found": total,
        "attempted": len(results),
        "results": results
    }

    out = (
        Path(self.root)
        / "runtime"
        / "live-platform-actions.jsonl"
    )

    with out.open("a", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")

    return result


RumbleAdapter.optimize_existing = _cgs_rumble_hidden_edit

