"""JSON export and import of the whole local database."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from dayplan.database.connection import Database
from dayplan.utils.dates import iso_now

FORMAT_VERSION = 1

_TABLES = (
    "projects",
    "tasks",
    "tags",
    "task_tags",
    "calendar_events",
    "focus_sessions",
    "settings",
)


class BackupService:
    def __init__(self, db: Database) -> None:
        self.db = db

    def export_json(self, path: Path | str) -> Path:
        """Write every table to a portable JSON file."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with self.db.connect() as conn:
            data: dict[str, object] = {
                "version": FORMAT_VERSION,
                "exported_at": iso_now(),
            }
            for table in _TABLES:
                data[table] = [dict(row) for row in conn.execute(f"SELECT * FROM {table}")]

            tags_by_task: dict[str, list[str]] = {}
            for row in conn.execute(
                "SELECT tt.task_id, t.name FROM task_tags tt "
                "JOIN tags t ON t.id = tt.tag_id"
            ):
                tags_by_task.setdefault(row["task_id"], []).append(row["name"])
            for task in data["tasks"]:
                task["tags"] = sorted(tags_by_task.get(task["id"], []))

        target.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return target

    def import_json(self, path: Path | str) -> int:
        """Restore a backup into this database. Returns the number of tasks imported."""
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, dict) or data.get("version") != FORMAT_VERSION:
            raise ValueError("Format backup tidak dikenal atau versinya tidak didukung.")

        with self.db.connect() as conn:
            _insert_rows(conn, "projects", data.get("projects", []))
            _insert_rows(conn, "tasks", data.get("tasks", []), skip={"tags"})
            _insert_rows(conn, "tags", data.get("tags", []))
            _insert_rows(conn, "task_tags", data.get("task_tags", []))
            _insert_rows(conn, "calendar_events", data.get("calendar_events", []))
            _insert_rows(conn, "focus_sessions", data.get("focus_sessions", []))
            _insert_rows(conn, "settings", data.get("settings", []))
            return len(data.get("tasks", []))


def _insert_rows(
    conn: sqlite3.Connection,
    table: str,
    rows: list[dict[str, object]],
    *,
    skip: set[str] | None = None,
) -> None:
    ignored = skip or set()
    for row in rows:
        item = {key: value for key, value in row.items() if key not in ignored}
        if not item:
            continue
        columns = ", ".join(item)
        placeholders = ", ".join("?" for _ in item)
        conn.execute(
            f"INSERT OR REPLACE INTO {table} ({columns}) VALUES ({placeholders})",
            tuple(item.values()),
        )
