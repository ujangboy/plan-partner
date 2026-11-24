"""Focus session persistence. Timer state itself lives in the Focus screen."""

from __future__ import annotations

from uuid import uuid4

from dayplan.config import Config
from dayplan.database.connection import Database
from dayplan.models.focus_session import FocusSession
from dayplan.repositories.focus_repository import FocusRepository
from dayplan.utils.dates import iso_now


class FocusService:
    def __init__(self, db: Database, config: Config | None = None) -> None:
        self.db = db
        self.config = config or Config(db)
        self.repo = FocusRepository(db)

    def start(self, task_id: str | None = None, minutes: int | None = None) -> FocusSession:
        if task_id:
            from dayplan.repositories.task_repository import TaskRepository

            if TaskRepository(self.db).get(task_id) is None:
                raise LookupError("Tugas tidak ditemukan.")
        duration = int(minutes) if minutes else self.config.focus_minutes
        if duration <= 0:
            raise ValueError("Durasi fokus harus lebih dari nol.")
        return self.repo.create(
            FocusSession(
                id=str(uuid4()),
                task_id=task_id,
                duration_minutes=duration,
                started_at=iso_now(),
                status="running",
            )
        )

    def get(self, session_id: str) -> FocusSession | None:
        return self.repo.get(session_id)

    def complete(self, session_id: str) -> FocusSession:
        return self._finish(session_id, "completed")

    def cancel(self, session_id: str) -> FocusSession:
        return self._finish(session_id, "cancelled")

    def history(self, limit: int = 50) -> list[FocusSession]:
        return self.repo.history(limit)

    def _finish(self, session_id: str, status: str) -> FocusSession:
        session = self.get(session_id)
        if session is None:
            raise LookupError("Sesi fokus tidak ditemukan.")
        session.status = status
        session.completed_at = iso_now()
        self.repo.update(session)
        return session
