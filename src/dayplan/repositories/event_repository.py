"""All SQL for calendar events."""

from __future__ import annotations

from datetime import date

from dayplan.database.connection import Database
from dayplan.models.event import CalendarEvent

_COLUMNS = (
    "id, title, description, start_at, end_at, is_all_day, location, "
    "created_at, updated_at"
)


class EventRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def create(self, event: CalendarEvent) -> CalendarEvent:
        with self.db.connect() as conn:
            conn.execute(
                f"INSERT INTO calendar_events ({_COLUMNS}) VALUES "
                "(:id, :title, :description, :start_at, :end_at, :is_all_day, "
                ":location, :created_at, :updated_at)",
                self._params(event),
            )
        return event

    def update(self, event: CalendarEvent) -> None:
        with self.db.connect() as conn:
            conn.execute(
                "UPDATE calendar_events SET title=:title, description=:description, "
                "start_at=:start_at, end_at=:end_at, is_all_day=:is_all_day, "
                "location=:location, updated_at=:updated_at WHERE id=:id",
                self._params(event),
            )

    def get(self, event_id: str) -> CalendarEvent | None:
        with self.db.connect() as conn:
            row = conn.execute(
                f"SELECT {_COLUMNS} FROM calendar_events WHERE id = ?", (event_id,)
            ).fetchone()
            return CalendarEvent.from_row(row) if row else None

    def delete(self, event_id: str) -> bool:
        with self.db.connect() as conn:
            cursor = conn.execute("DELETE FROM calendar_events WHERE id = ?", (event_id,))
            return cursor.rowcount > 0

    def on_day(self, day: date) -> list[CalendarEvent]:
        return self.between(day, day)

    def between(self, start: date, end: date) -> list[CalendarEvent]:
        with self.db.connect() as conn:
            rows = conn.execute(
                f"SELECT {_COLUMNS} FROM calendar_events "
                "WHERE start_at >= ? AND start_at <= ? ORDER BY start_at, end_at",
                (f"{start.isoformat()}T00:00", f"{end.isoformat()}T23:59"),
            )
            return [CalendarEvent.from_row(row) for row in rows]

    def upcoming(self, since: str, limit: int) -> list[CalendarEvent]:
        with self.db.connect() as conn:
            rows = conn.execute(
                f"SELECT {_COLUMNS} FROM calendar_events "
                "WHERE start_at >= ? ORDER BY start_at LIMIT ?",
                (since, limit),
            )
            return [CalendarEvent.from_row(row) for row in rows]

    @staticmethod
    def _params(event: CalendarEvent) -> dict[str, object]:
        return {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "start_at": event.start_at,
            "end_at": event.end_at,
            "is_all_day": int(event.is_all_day),
            "location": event.location,
            "created_at": event.created_at,
            "updated_at": event.updated_at,
        }
