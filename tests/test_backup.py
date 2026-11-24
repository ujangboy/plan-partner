from __future__ import annotations

import json
from datetime import date

import pytest

from dayplan.database.connection import Database
from dayplan.services.backup_service import BackupService
from dayplan.services.calendar_service import CalendarService
from dayplan.services.project_service import ProjectService
from dayplan.services.task_service import TaskService


@pytest.fixture
def services(tmp_path):
    db = Database(tmp_path / "dayplan.db")
    return BackupService(db), TaskService(db), ProjectService(db), CalendarService(db)


def test_export_contains_all_entities(services, tmp_path):
    backup, tasks, projects, calendar = services
    project = projects.create("Kuliah")
    tasks.create("Laporan", project_id=project.id, tags=["kuliah"])
    calendar.create_event("Kuliah", "2026-11-24T08:00", "2026-11-24T10:00")

    target = tmp_path / "backup.json"
    backup.export_json(target)
    data = json.loads(target.read_text(encoding="utf-8"))

    assert data["version"] == 1
    assert len(data["tasks"]) == 1
    assert len(data["projects"]) == 1
    assert len(data["calendar_events"]) == 1
    assert data["tasks"][0]["tags"] == ["kuliah"]


def test_import_round_trip(services, tmp_path):
    backup, tasks, projects, calendar = services
    project = projects.create("Kuliah")
    tasks.create("Laporan", project_id=project.id, due_date="2026-11-25")
    calendar.create_event("Kuliah", "2026-11-24T08:00", "2026-11-24T10:00")

    target = tmp_path / "backup.json"
    backup.export_json(target)

    other_db = Database(tmp_path / "restored.db")
    restored = BackupService(other_db)
    restored.import_json(target)

    assert len(TaskService(other_db).list_tasks()) == 1
    assert len(ProjectService(other_db).list_projects()) == 1
    assert CalendarService(other_db).events_on(date(2026, 11, 24))


def test_import_rejects_invalid_payload(services, tmp_path):
    backup, _, _, _ = services
    target = tmp_path / "broken.json"
    target.write_text('{"version": 99}', encoding="utf-8")
    with pytest.raises(ValueError, match="versi"):
        backup.import_json(target)
