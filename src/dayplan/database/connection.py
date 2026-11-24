"""SQLite connection lifecycle for DayPlan."""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from dayplan.database.migrations import migrate


def default_db_path() -> Path:
    """Return the platform-appropriate location of ``dayplan.db``."""
    override = os.environ.get("DAYPLAN_DATA_DIR")
    base = Path(override) if override else Path.home() / ".dayplan"
    return base / "dayplan.db"


class Database:
    """Owns the database path; hands out short-lived configured connections."""

    def __init__(self, path: Path | str | None = None) -> None:
        self.path = Path(path) if path is not None else default_db_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        """Yield a connection with foreign keys on and migrations applied."""
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        try:
            migrate(conn)
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
