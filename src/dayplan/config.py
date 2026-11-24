"""Application configuration backed by the ``settings`` table."""

from __future__ import annotations

from dayplan.database.connection import Database
from dayplan.repositories.settings_repository import SettingsRepository

DEFAULTS: dict[str, str] = {
    "theme": "dark",
    "date_format": "%Y-%m-%d",
    "time_format": "%H:%M",
    "timezone": "",
    "default_priority": "medium",
    "focus_minutes": "25",
    "short_break_minutes": "5",
    "long_break_minutes": "15",
}


class Config:
    """Small typed facade over persisted settings."""

    def __init__(self, db: Database) -> None:
        self._store = SettingsRepository(db)
        self._cache = {**DEFAULTS, **self._store.all()}

    def get(self, key: str) -> str:
        return self._cache[key]

    def set(self, key: str, value: str) -> None:
        if key not in DEFAULTS:
            raise KeyError(f"Pengaturan '{key}' tidak dikenal.")
        self._cache[key] = value
        self._store.set(key, value)

    def set_many(self, values: dict[str, str]) -> None:
        for key, value in values.items():
            self.set(key, value)

    @property
    def timezone(self) -> str | None:
        return self.get("timezone") or None

    @property
    def focus_minutes(self) -> int:
        return int(self.get("focus_minutes"))

    @property
    def short_break_minutes(self) -> int:
        return int(self.get("short_break_minutes"))

    @property
    def long_break_minutes(self) -> int:
        return int(self.get("long_break_minutes"))
