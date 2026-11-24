"""Key/value settings persistence."""

from __future__ import annotations

from dayplan.database.connection import Database


class SettingsRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def all(self) -> dict[str, str]:
        with self.db.connect() as conn:
            return {row["key"]: row["value"] for row in conn.execute("SELECT key, value FROM settings")}

    def set(self, key: str, value: str) -> None:
        with self.db.connect() as conn:
            conn.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value),
            )

    def set_many(self, values: dict[str, str]) -> None:
        for key, value in values.items():
            self.set(key, value)
