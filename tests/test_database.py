from __future__ import annotations

import sqlite3

from dayplan.database.connection import Database
from dayplan.database.migrations import SCHEMA_VERSION, get_version


def test_database_creates_schema_and_sets_version(tmp_path):
    db = Database(tmp_path / "dayplan.db")

    with db.connect() as conn:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        assert {
            "tasks",
            "projects",
            "tags",
            "task_tags",
            "calendar_events",
            "focus_sessions",
            "settings",
        } <= tables
        assert get_version(conn) == SCHEMA_VERSION


def test_foreign_keys_are_enforced(tmp_path):
    db = Database(tmp_path / "dayplan.db")

    with db.connect() as conn:
        try:
            conn.execute(
                "INSERT INTO tasks (id, title, project_id, created_at, updated_at) "
                "VALUES ('t1', 'Task', 'missing-project', 'now', 'now')"
            )
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("foreign key violation was not rejected")
        conn.rollback()


def test_database_is_idempotent(tmp_path):
    path = tmp_path / "dayplan.db"
    Database(path)
    with Database(path).connect() as conn:
        assert get_version(conn) == SCHEMA_VERSION
