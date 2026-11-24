"""Small, explicit migration runner.

Each migration is a plain SQL script keyed by the schema version it
produces. Migrations run inside the caller's connection transaction and
are safe to replay on an already-current database.
"""

from __future__ import annotations

import sqlite3

from dayplan.database.schema import SCHEMA_SQL

SCHEMA_VERSION = 1

MIGRATIONS: dict[int, str] = {1: SCHEMA_SQL}


def get_version(conn: sqlite3.Connection) -> int:
    """Return the current schema version, or 0 for a brand-new database."""
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL)"
    )
    row = conn.execute("SELECT version FROM schema_version LIMIT 1").fetchone()
    return int(row[0]) if row else 0


def migrate(conn: sqlite3.Connection) -> None:
    """Apply every pending migration in order."""
    current = get_version(conn)
    for version in sorted(MIGRATIONS):
        if version <= current:
            continue
        conn.executescript(MIGRATIONS[version])
        conn.execute("DELETE FROM schema_version")
        conn.execute("INSERT INTO schema_version (version) VALUES (?)", (version,))
