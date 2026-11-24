from __future__ import annotations

from datetime import date

import pytest

from dayplan.database.connection import Database
from dayplan.services.calendar_service import CalendarService
from dayplan.services.task_service import TaskService


@pytest.fixture
def services(tmp_path):
    db = Database(tmp_path / "dayplan.db")
    return CalendarService(db), TaskService(db)


def test_event_crud(services):
    calendar, _ = services
    event = calendar.create_event(
        "Kuliah",
        start_at="2026-11-24T08:00",
        end_at="2026-11-24T10:00",
        location="Ruang 301",
    )
    assert event.id and event.location == "Ruang 301"
    assert calendar.get_event(event.id).title == "Kuliah"

    calendar.update_event(event.id, title="Kuliah Database")
    assert calendar.get_event(event.id).title == "Kuliah Database"

    assert calendar.delete_event(event.id) is True
    assert calendar.get_event(event.id) is None


def test_all_day_event_uses_full_day_range(services):
    calendar, _ = services
    event = calendar.create_all_day_event("Libur", date(2026, 11, 25))
    assert event.is_all_day is True
    assert event.start_at == "2026-11-25T00:00"
    assert event.end_at == "2026-11-25T23:59"


def test_event_validation(services):
    calendar, _ = services
    with pytest.raises(ValueError, match="Judul"):
        calendar.create_event("", "2026-11-24T08:00", "2026-11-24T10:00")
    with pytest.raises(ValueError, match="sesudah"):
        calendar.create_event("Task", "2026-11-24T10:00", "2026-11-24T08:00")


def test_events_on_day_and_between(services):
    calendar, _ = services
    calendar.create_event("Pagi", "2026-11-24T08:00", "2026-11-24T09:00")
    calendar.create_event("Malam", "2026-11-25T19:00", "2026-11-25T20:00")

    assert [e.title for e in calendar.events_on(date(2026, 11, 24))] == ["Pagi"]
    between = calendar.events_between(date(2026, 11, 24), date(2026, 11, 25))
    assert [e.title for e in between] == ["Pagi", "Malam"]


def test_agenda_merges_events_deadlines_and_schedules_in_time_order(services):
    calendar, tasks = services
    calendar.create_event("Kuliah", "2026-11-24T08:00", "2026-11-24T10:00")
    tasks.create("Laporan", due_date="2026-11-24", due_time="23:59", status="todo")
    tasks.create(
        "Belajar Python",
        scheduled_start="2026-11-24T19:00",
        scheduled_end="2026-11-24T20:30",
        status="todo",
    )

    agenda = calendar.agenda_for(date(2026, 11, 24))
    assert [item.kind for item in agenda] == ["event", "scheduled", "deadline"]
    assert [item.label for item in agenda] == ["Kuliah", "Belajar Python", "Laporan"]


def test_agenda_excludes_completed_deadlines(services):
    calendar, tasks = services
    tasks.create("Selesai", due_date="2026-11-24", status="done")
    assert calendar.agenda_for(date(2026, 11, 24)) == []


def test_upcoming_events(services):
    calendar, _ = services
    calendar.create_event("Besok", "2026-11-25T08:00", "2026-11-25T09:00")
    calendar.create_event("Lusa", "2026-11-26T08:00", "2026-11-26T09:00")

    assert [
        e.title
        for e in calendar.upcoming_events(limit=1, from_date=date(2026, 11, 24))
    ] == ["Besok"]
