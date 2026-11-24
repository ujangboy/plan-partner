"""Project business logic. Deleting a project never deletes its tasks."""

from __future__ import annotations

from dayplan.config import Config
from dayplan.database.connection import Database
from dayplan.models.project import Project
from dayplan.repositories.project_repository import ProjectRepository
from dayplan.repositories.task_repository import TaskRepository
from dayplan.utils.dates import iso_now


class ProjectService:
    def __init__(self, db: Database, config: Config | None = None) -> None:
        self.db = db
        self.config = config or Config(db)
        self.repo = ProjectRepository(db)
        self.task_repo = TaskRepository(db)

    def create(
        self, name: str, description: str = "", color: str = ""
    ) -> Project:
        cleaned = name.strip()
        if not cleaned:
            raise ValueError("Nama proyek tidak boleh kosong.")
        return self.repo.create(
            Project(
                id=ProjectRepository.new_id(),
                name=cleaned,
                description=description.strip(),
                color=color.strip(),
                created_at=iso_now(),
            )
        )

    def get(self, project_id: str) -> Project | None:
        return self.repo.get(project_id)

    def update(self, project_id: str, **changes: object) -> Project:
        project = self.get(project_id)
        if project is None:
            raise LookupError("Proyek tidak ditemukan.")
        for key in ("name", "description", "color"):
            value = changes.get(key)
            if value is not None:
                setattr(project, key, str(value).strip())
        if not project.name:
            raise ValueError("Nama proyek tidak boleh kosong.")
        self.repo.update(project)
        return project

    def delete(self, project_id: str) -> bool:
        return self.repo.delete(project_id)

    def list_projects(self) -> list[Project]:
        return self.repo.list_projects()

    def tasks(self, project_id: str) -> list[object]:
        """Tasks in a project; tasks survive project deletion via SET NULL."""
        return self.task_repo.list_tasks(project_id=project_id)
