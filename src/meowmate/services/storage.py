from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from src.meowmate.domain.models import AppSettings, CatStats


APP_NAME = "MeowMate"
PROJECT_ROOT = Path(__file__).resolve().parents[3]


class SettingsStore:
    def __init__(self) -> None:
        self.path = PROJECT_ROOT / "data" / "settings.json"

    def load(self) -> AppSettings:
        if not self.path.exists():
            return AppSettings()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            stats_data = data.pop("stats", {})
            settings = AppSettings(**data, stats=CatStats(**stats_data))
            settings.clamp()
            return settings
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            return AppSettings()

    def save(self, settings: AppSettings) -> None:
        settings.clamp()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(_to_plain_dict(settings), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def _to_plain_dict(settings: AppSettings) -> dict[str, Any]:
    return asdict(settings)
