from __future__ import annotations

from pathlib import Path
import os
import subprocess

from .base import PlatformAdapter


class PersistentBrowserAdapter(PlatformAdapter):
    profile_name = ""
    dashboard_url = ""

    @property
    def profile(self):
        return self.root / "account-profiles" / self.profile_name

    def browser_available(self):
        candidates = [
            Path(os.environ.get("PROGRAMFILES", "C:/Program Files"))
            / "Google/Chrome/Application/chrome.exe",

            Path(os.environ.get("PROGRAMFILES(X86)", "C:/Program Files (x86)"))
            / "Google/Chrome/Application/chrome.exe",
        ]

        return next((p for p in candidates if p.exists()), None)

    def session_exists(self):
        return self.profile.exists() and any(self.profile.iterdir())

    def open_dashboard(self):
        chrome = self.browser_available()

        if not chrome:
            return self.write_result(
                self.result(
                    "open_dashboard",
                    False,
                    "UNAVAILABLE",
                    "Google Chrome executable not found.",
                )
            )

        self.profile.mkdir(parents=True, exist_ok=True)

        subprocess.Popen([
            str(chrome),
            f"--user-data-dir={self.profile}",
            "--new-window",
            self.dashboard_url,
        ])

        return self.write_result(
            self.result(
                "open_dashboard",
                True,
                "ACTION_COMPLETED",
                "Persistent authenticated browser profile opened.",
                {
                    "profile": str(self.profile),
                    "url": self.dashboard_url,
                },
            )
        )
