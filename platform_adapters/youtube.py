from __future__ import annotations

from pathlib import Path
import subprocess
import urllib.request
import json

from .base import PlatformAdapter


class YouTubeAdapter(PlatformAdapter):
    name = "youtube"

    def __init__(self, root: Path):
        super().__init__(root)
        self.agent = self.root / "engines" / "agenttube"

    def _health(self):
        try:
            with urllib.request.urlopen(
                "http://127.0.0.1:3456/health",
                timeout=2,
            ) as r:
                return r.status == 200
        except Exception:
            return False

    def capabilities(self):
        package = self.agent / "package.json"

        scripts = {}

        if package.exists():
            try:
                scripts = json.loads(
                    package.read_text(encoding="utf-8")
                ).get("scripts", {})
            except Exception:
                scripts = {}

        return {
            "connected": self._health(),
            "engine": "AgentTube",
            "analytics": "agent:analytics" in scripts,
            "optimize_existing": (
                "agent:analytics" in scripts and
                "agent:seo" in scripts
            ),
            "publish_new": "agent:publishing" in scripts,
            "sales_destination": False,
            "traffic_destination": True,
        }

    def optimize_existing(self):
        if not self.agent.exists():
            return self.write_result(
                self.result(
                    "optimize_existing",
                    False,
                    "UNAVAILABLE",
                    "AgentTube directory not found.",
                )
            )

        log = self.root / "runtime" / "youtube-existing-optimization.log"

        with log.open("a", encoding="utf-8") as f:
            f.write("\n=== YOUTUBE EXISTING-CONTENT OPTIMIZATION ===\n")

            analytics = subprocess.run(
                ["npm.cmd", "run", "agent:analytics"],
                cwd=self.agent,
                stdout=f,
                stderr=subprocess.STDOUT,
            )

            seo = subprocess.run(
                ["npm.cmd", "run", "agent:seo"],
                cwd=self.agent,
                stdout=f,
                stderr=subprocess.STDOUT,
            )

        ok = analytics.returncode == 0 and seo.returncode == 0

        return self.write_result(
            self.result(
                "optimize_existing",
                ok,
                "ACTION_COMPLETED" if ok else "ACTION_FAILED",
                "AgentTube analytics + SEO optimization cycle executed.",
                {
                    "analytics_exit": analytics.returncode,
                    "seo_exit": seo.returncode,
                    "log": str(log),
                },
            )
        )
