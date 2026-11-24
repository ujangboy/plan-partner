"""Calendar events, agendas and the task/calendar integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import uuid4

from dayplan.config import Config
from dayplan.database.connection import Database
from dayplan.models.event import CalendarEvent
from dayplan.repositories.event_repository import EventRepository
from dayplan.utils.dates import iso_now, local_now
from dayplan.utils.validators import (
    validate_datetime,
    validate_datetime_order,
    validate_title,
)
from dayplan.services.task_service import TaskService


@dataclass(frozen=True)
class AgendaItem:
    """One chronological entry on a day, regardless of its source."""

    start: str
    label: str
    kind: str  # "event", "scheduled" or "deadline"
    detail: str = ""
    ref_id: str = ""


class CalendarService:
    def __init__(self, db: Database, config: Config | None = None) -> None:
        self.db = db
        self.config = config or Config(db)
        self.events = EventRepository(db)
        self.tasks = TaskService(db, self.config)

    def create_event(
        self,
        title: str,
        start_at: str,
        end_at: str,
        *,
        description: str = "",
        location: str = "",
        is_all_day: bool = False,
    ) -> CalendarEvent:
        start = validate_datetime(start_at, "Waktu mulai")
        end = validate_datetime(end_at, "Waktu selesai")
        if not start or not end:
            raise ValueError("Waktu mulai dan selesai wajib diisi.")
        validate_datetime_order(start, end)
        now = iso_now()
        return self.events.create(
            CalendarEvent(
                id=str(uuid4()),
                title=validate_title(title),
                start_at=start,
                end_at=end,
                description=description.strip(),
                location=location.strip(),
                is_all_day=is_all_day,
                created_at=now,
                updated_at=now,
            )
        )

    def create_all_day_event(self, title: str, day: date, **kwargs: object) -> CalendarEvent:
        return self.create_event(
            title,
            f"{day.isoformat()}T00:00",
            f"{day.isoformat()}T23:59",
            is_all_day=True,
            **kwargs,
        )

    def get_event(self, event_id: str) -> CalendarEvent | None:
        return self.events.get(event_id)

    def update_event(self, event_id: str, **changes: object) -> CalendarEvent:
        event = self.get_event(event_id)
        if event is None:
            raise LookupError("Kegiatan tidak ditemukan.")
        for key in ("title", "description", "location"):
            value = changes.get(key)
            if value is not None:
                setattr(event, key, str(value).strip())
        if changes.get("start_at") is not None:
            event.start_at = validate_datetime(str(changes["start_at"]), "Waktu mulai") or event.start_at
        if changes.get("end_at") is not None:
            event.end_at = validate_datetime(str(changes["end_at"]), "Waktu selesai") or event.end_at
        if not event.title.strip():
            raise ValueError("Judul kegiatan tidak boleh kosong.")
        validate_datetime_order(event.start_at, event.end_at)
        event.updated_at = iso_now()
        self.events.update(event)
        return event

    def delete_event(self, event_id: str) -> bool:
        return self.events.delete(event_id)

    def events_on(self, day: date) -> list[CalendarEvent]:
        return self.events.on_day(day)

    def events_between(self, start: date, end: date) -> list[CalendarEvent]:
        return self.events.between(start, end)

    def upcoming_events(self, limit: int = 10, from_date: date | None = None) -> list[CalendarEvent]:
        since = (from_date or local_now(self.config.timezone).date()).isoformat() + "T00:00"
        return self.events.upcoming(since, limit)

    def agenda_for(self, day: date) -> list[AgendaItem]:
        """Merge events, scheduled work and deadlines into one timeline."""
        items = [
            AgendaItem(event.start_at, event.title, "event", event.location, event.id)
            for event in self.events_on(day)
        ]
        for task in self.tasks.scheduled_on(day):
            items.append(
                AgendaItem(
                    task.scheduled_start or "",
                    task.title,
                    "scheduled",
                    "Jadwal kerja",
                    task.id,
                )
            )
        for task in self.tasks.due_on(day):
            if task.is_done:
                continue
            moment = f"{day.isoformat()}T{task.due_time or '23:59'}"
            items.append(
                AgendaItem(moment, task.title, "deadline", "Deadline", task.id)
            )
        return sorted(items, key=lambda item: item.start)
