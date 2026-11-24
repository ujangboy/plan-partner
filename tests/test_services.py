from __future__ import annotations

from datetime import date

import pytest

from dayplan.database.connection import Database
from dayplan.services.statistics_service import StatisticsService
from dayplan.services.task_service import TaskService
from dayplan.services.project_service import ProjectService


@pytest.fixture
def services(tmp_path):
    db = Database(tmp_path / "dayplan.db")
    return StatisticsService(db), TaskService(db), ProjectService(db)


def test_summary_counts_active_completed_overdue_and_today(services):
    stats, tasks, _ = services
    today = date.today().isoformat()

    tasks.create("Aktif", status="todo")
    tasks.create("Selesai", status="done")
    tasks.create("Terlambat", status="todo", due_date="2020-01-01")
    tasks.create("Hari ini", status="todo", due_date=today)
    tasks.create("Arsip", status="archived")

    summary = stats.summary()
    assert summary.active == 3
    assert summary.completed == 1
    assert summary.overdue == 1
    assert summary.due_today == 1
    assert 0 < summary.completion_rate < 100


def test_project_progress(services):
    stats, tasks, projects = services
    project = projects.create("Kuliah")
    tasks.create("A", project_id=project.id, status="todo")
    tasks.create("B", project_id=project.id, status="done")

    progress = stats.project_progress()
    assert len(progress) == 1
    assert progress[0].name == "Kuliah"
    assert progress[0].percent == 50


def test_daily_completions_counts_completed_at(services):
    stats, _, _ = services
    today = date.today().isoformat()
    with stats.db.connect() as conn:
        conn.execute(
            "INSERT INTO tasks (id, title, status, created_at, updated_at, completed_at) "
            "VALUES ('x', 'X', 'done', ?, ?, ?)",
            (today + "T00:00", today + "T00:00", today + "T10:00"),
        )

    assert stats.daily_completions(days=1)[0][1] == 1
