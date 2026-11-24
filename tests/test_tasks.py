from __future__ import annotations

import pytest

from dayplan.database.connection import Database
from dayplan.services.task_service import TaskService
from dayplan.utils.dates import local_now


@pytest.fixture
def service(tmp_path):
    return TaskService(Database(tmp_path / "dayplan.db"))


def test_create_persists_task_with_defaults(service):
    task = service.create("Mengerjakan laporan database")

    assert task.id
    assert task.status == "inbox"
    assert task.priority == "medium"
    assert task.created_at and task.updated_at
    assert service.get(task.id).title == "Mengerjakan laporan database"


def test_create_rejects_empty_title(service):
    with pytest.raises(ValueError, match="Judul"):
        service.create("   ")


def test_create_validates_dates_and_priority(service):
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        service.create("Task", due_date="25/11/2026")
    with pytest.raises(ValueError, match="Prioritas"):
        service.create("Task", priority="critical")


def test_create_stores_schedule_and_tags(service):
    task = service.create(
        "Belajar Python",
        due_date="2026-11-26",
        due_time="23:59",
        scheduled_start="2026-11-24T19:00",
        scheduled_end="2026-11-24T20:30",
        estimated_minutes=90,
        tags=["kuliah", "python"],
    )

    stored = service.get(task.id)
    assert stored.due_date == "2026-11-26"
    assert stored.scheduled_start == "2026-11-24T19:00"
    assert stored.estimated_minutes == 90
    assert set(stored.tags) == {"kuliah", "python"}


def test_update_changes_fields_and_timestamp(service):
    task = service.create("Draft")
    updated = service.update(task.id, title="Final", priority="high", status="todo")

    assert updated.title == "Final"
    assert updated.priority == "high"
    assert updated.status == "todo"
    assert service.get(task.id).title == "Final"


def test_toggle_done_sets_and_clears_completed_at(service):
    task = service.create("Task")
    assert task.completed_at is None

    done = service.toggle_done(task.id)
    assert done.status == "done" and done.completed_at

    active = service.toggle_done(task.id)
    assert active.status == "todo" and active.completed_at is None


def test_delete_removes_task(service):
    task = service.create("Hapus saya")
    assert service.delete(task.id) is True
    assert service.get(task.id) is None
    assert service.delete(task.id) is False


def test_filter_search_and_sort(service):
    service.create("Laporan", priority="urgent", due_date="2026-11-25", status="todo")
    service.create("Belajar", priority="low", due_date="2026-11-24", status="todo")
    service.create("Arsip lama", status="archived")

    todo = service.list_tasks(status="todo")
    assert {task.title for task in todo} == {"Laporan", "Belajar"}

    found = service.list_tasks(query="lap")
    assert [task.title for task in found] == ["Laporan"]

    by_due = service.list_tasks(status="todo", sort="due")
    assert [task.title for task in by_due] == ["Belajar", "Laporan"]

    by_priority = service.list_tasks(status="todo", sort="priority")
    assert [task.title for task in by_priority] == ["Laporan", "Belajar"]

    archived = service.list_tasks(status="archived")
    assert [task.title for task in archived] == ["Arsip lama"]


def test_overdue_uses_configured_timezone(service):
    task = service.create("Terlambat", due_date="2020-01-01")
    assert service.is_overdue(task) is True

    future = service.create("Masa depan", due_date="2099-01-01")
    assert service.is_overdue(future) is False


def test_schedule_validation_rejects_reversed_times(service):
    with pytest.raises(ValueError, match="sesudah"):
        service.create(
            "Task",
            scheduled_start="2026-11-24T20:00",
            scheduled_end="2026-11-24T19:00",
        )
