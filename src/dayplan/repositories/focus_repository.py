"""All SQL for focus sessions."""

from __future__ import annotations

from dayplan.database.connection import Database
from dayplan.models.focus_session import FocusSession


class FocusRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def create(self, session: FocusSession) -> FocusSession:
        with self.db.connect() as conn:
            conn.execute(
                "INSERT INTO focus_sessions "
                "(id, task_id, duration_minutes, started_at, completed_at, status) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    session.id,
                    session.task_id,
                    session.duration_minutes,
                    session.started_at,
                    session.completed_at,
                    session.status,
                ),
            )
        return session

    def update(self, session: FocusSession) -> None:
        with self.db.connect() as conn:
            conn.execute(
                "UPDATE focus_sessions SET completed_at = ?, status = ? WHERE id = ?",
                (session.completed_at, session.status, session.id),
            )

    def get(self, session_id: str) -> FocusSession | None:
        with self.db.connect() as conn:
            row = conn.execute(
                "SELECT * FROM focus_sessions WHERE id = ?", (session_id,)
            ).fetchone()
            return FocusSession.from_row(row) if row else None

    def history(self, limit: int = 50) -> list[FocusSession]:
        with self.db.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM focus_sessions ORDER BY started_at DESC LIMIT ?",
                (limit,),
            )
            return [FocusSession.from_row(row) for row in rows]
