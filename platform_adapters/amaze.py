from .browser import PersistentBrowserAdapter


class AmazeAdapter(PersistentBrowserAdapter):
    name = "amaze"
    profile_name = "amaze-spring-browser"
    dashboard_url = "https://dashboard.teespring.com/overview/"

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
