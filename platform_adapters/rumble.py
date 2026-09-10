from pathlib import Path

from .browser import PersistentBrowserAdapter


class RumbleAdapter(PersistentBrowserAdapter):
    name = "rumble"
    profile_name = "rumble-browser"
    dashboard_url = "https://rumble.com/account/content"

    def capabilities(self):
        return {
            "connected": self.session_exists(),
            "connection_type": "persistent_browser_session",
            "analytics": False,
            "optimize_existing": False,
            "publish_new": False,
            "sales_destination": False,
            "traffic_destination": True,

            # IMPORTANT:
            # These remain False until executable Rumble edit/upload
            # actions exist. This prevents the suite from claiming
            # Rumble optimization merely because the browser is logged in.
            "browser_session": self.session_exists(),
        }
