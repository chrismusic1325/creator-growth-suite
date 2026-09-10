from .browser import PersistentBrowserAdapter


class BandcampAdapter(PersistentBrowserAdapter):
    name = "bandcamp"
    profile_name = "bandcamp-browser"
    dashboard_url = "https://bandcamp.com"

    def capabilities(self):
        return {
            "connected": self.session_exists(),
            "connection_type": "persistent_browser_session",
            "analytics": False,
            "optimize_existing": False,
            "publish_new": False,
            "sales_destination": True,
            "traffic_destination": True,
            "browser_session": self.session_exists(),
        }
