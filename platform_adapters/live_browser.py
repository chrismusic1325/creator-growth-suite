from pathlib import Path
from contextlib import contextmanager
from playwright.sync_api import sync_playwright

def profile_exists(root, name):
    p = Path(root) / "account-profiles" / name
    return p.exists() and any(p.iterdir())

@contextmanager
def browser(root, profile):
    root = Path(root)
    user_data = root / "account-profiles" / profile
    user_data.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            str(user_data),
            channel="chrome",
            headless=False,
            args=["--start-maximized"],
            viewport=None
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            yield page
        finally:
            ctx.close()

def page_text(page):
    try:
        return page.locator("body").inner_text(timeout=10000)
    except Exception:
        return ""
