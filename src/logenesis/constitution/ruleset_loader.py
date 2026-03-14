from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class RulesetLoader:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def load(self) -> dict[str, Any]:
        with self.path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data
