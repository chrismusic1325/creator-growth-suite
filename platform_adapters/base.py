from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any
import json
import time


@dataclass
class AdapterResult:
    platform: str
    action: str
    ok: bool
    status: str
    detail: str = ""
    evidence: Dict[str, Any] | None = None

    def to_dict(self):
        d = asdict(self)
        d["timestamp"] = int(time.time())
        return d


class PlatformAdapter:
    name = "base"

    def __init__(self, root: Path):
        self.root = Path(root)

    def capabilities(self) -> Dict[str, Any]:
        return {
            "connected": False,
            "analytics": False,
            "optimize_existing": False,
            "publish_new": False,
            "sales_destination": False,
            "traffic_destination": False,
        }

    def result(
        self,
        action: str,
        ok: bool,
        status: str,
        detail: str = "",
        evidence: Dict[str, Any] | None = None,
    ):
        return AdapterResult(
            platform=self.name,
            action=action,
            ok=ok,
            status=status,
            detail=detail,
            evidence=evidence or {},
        )

    def write_result(self, result: AdapterResult):
        out = self.root / "runtime" / "platform-actions.jsonl"
        out.parent.mkdir(parents=True, exist_ok=True)

        with out.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result.to_dict(), ensure_ascii=False) + "\n")

        return result
