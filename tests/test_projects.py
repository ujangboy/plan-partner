from __future__ import annotations

import pytest

from dayplan.database.connection import Database
from dayplan.services.project_service import ProjectService
from dayplan.services.task_service import TaskService


@pytest.fixture
def services(tmp_path):
    db = Database(tmp_path / "dayplan.db")
    return ProjectService(db), TaskService(db)


def test_project_crud_and_counts(services):
    projects, tasks = services
    project = projects.create("Kuliah", description="Tugas semester", color="cyan")
    assert project.id and project.name == "Kuliah"

    tasks.create("Tugas 1", project_id=project.id, status="todo")
    tasks.create("Tugas 2", project_id=project.id, status="done")

    stored = projects.get(project.id)
    assert stored.active_count == 1
    assert stored.done_count == 1
    assert [task.title for task in projects.tasks(project.id)] == ["Tugas 1", "Tugas 2"]

    projects.update(project.id, name="Kuliah 2026")
    assert projects.get(project.id).name == "Kuliah 2026"


def test_project_name_is_required(services):
    projects, _ = services
    with pytest.raises(ValueError, match="Nama proyek"):
        projects.create("  ")


def test_deleting_project_keeps_its_tasks(services):
    projects, tasks = services
    project = projects.create("Personal")
    task = tasks.create("Belajar git", project_id=project.id)

    assert projects.delete(project.id) is True
    assert projects.get(project.id) is None
    remaining = tasks.get(task.id)
    assert remaining is not None and remaining.project_id is None


def test_delete_missing_project_returns_false(services):
    projects, _ = services
    assert projects.delete("tidak-ada") is False
