"""Task business logic: validation, lifecycle and derived state."""

from __future__ import annotations

from datetime import date
from uuid import uuid4

from dayplan.config import Config
from dayplan.database.connection import Database
from dayplan.models.task import Task
from dayplan.repositories.task_repository import TaskRepository
from dayplan.utils.dates import iso_now, is_overdue as _is_overdue, local_now
from dayplan.utils.validators import (
    validate_date,
    validate_datetime,
    validate_datetime_order,
    validate_minutes,
    validate_priority,
    validate_status,
    validate_time,
    validate_title,
)

_EDITABLE = {
    "title",
    "description",
    "status",
    "priority",
    "due_date",
    "due_time",
    "scheduled_start",
    "scheduled_end",
    "estimated_minutes",
    "project_id",
    "tags",
}


class TaskService:
    def __init__(self, db: Database, config: Config | None = None) -> None:
        self.db = db
        self.config = config or Config(db)
        self.repo = TaskRepository(db)

    def create(
        self,
        title: str,
        *,
        description: str = "",
        status: str = "inbox",
        priority: str | None = None,
        due_date: str | None = None,
        due_time: str | None = None,
        scheduled_start: str | None = None,
        scheduled_end: str | None = None,
        estimated_minutes: str | int | None = None,
        project_id: str | None = None,
        tags: list[str] | None = None,
    ) -> Task:
        now = iso_now()
        task = Task(
            id=str(uuid4()),
            title=validate_title(title),
            description=description.strip(),
            status=validate_status(status),
            priority=validate_priority(priority or self.config.get("default_priority")),
            due_date=validate_date(due_date, "Deadline"),
            due_time=validate_time(due_time),
            scheduled_start=validate_datetime(scheduled_start, "Jadwal mulai"),
            scheduled_end=validate_datetime(scheduled_end, "Jadwal selesai"),
            estimated_minutes=validate_minutes(estimated_minutes),
            project_id=project_id or None,
            created_at=now,
            updated_at=now,
            completed_at=now if status == "done" else None,
            tags=list(tags or []),
        )
        validate_datetime_order(task.scheduled_start, task.scheduled_end)
        return self.repo.create(task)

    def get(self, task_id: str) -> Task | None:
        return self.repo.get(task_id)

    def list_tasks(
        self,
        *,
        status: str | None = None,
        priority: str | None = None,
        query: str = "",
        sort: str = "created",
        include_archived: bool = False,
        project_id: str | None = None,
    ) -> list[Task]:
        return self.repo.list_tasks(
            status=status,
            priority=priority,
            query=query,
            sort=sort,
            include_archived=include_archived,
            project_id=project_id,
        )

    def update(self, task_id: str, **changes: object) -> Task:
        task = self.get(task_id)
        if task is None:
            raise LookupError("Tugas tidak ditemukan.")

        for key, value in changes.items():
            if key in _EDITABLE and value is not None:
                setattr(task, key, value)

        task.title = validate_title(task.title)
        task.status = validate_status(task.status)
        task.priority = validate_priority(task.priority)
        task.due_date = validate_date(task.due_date, "Deadline")
        task.due_time = validate_time(task.due_time)
        task.scheduled_start = validate_datetime(task.scheduled_start, "Jadwal mulai")
        task.scheduled_end = validate_datetime(task.scheduled_end, "Jadwal selesai")
        task.estimated_minutes = validate_minutes(task.estimated_minutes)
        validate_datetime_order(task.scheduled_start, task.scheduled_end)

        if task.status == "done" and task.completed_at is None:
            task.completed_at = iso_now()
        elif task.status != "done":
            task.completed_at = None
        task.updated_at = iso_now()
        self.repo.update(task)
        return task

    def toggle_done(self, task_id: str) -> Task:
        task = self.get(task_id)
        if task is None:
            raise LookupError("Tugas tidak ditemukan.")
        return self.update(
            task_id, status="todo" if task.status == "done" else "done"
        )

    def delete(self, task_id: str) -> bool:
        return self.repo.delete(task_id)

    def is_overdue(self, task: Task, now: object = None) -> bool:
        current = now or local_now(self.config.timezone)
        return _is_overdue(task.due_date, current, task.completed_at)

    def due_on(self, day: date) -> list[Task]:
        """Tasks whose deadline falls on ``day``."""
        return [t for t in self.list_tasks() if t.due_date == day.isoformat()]

    def scheduled_on(self, day: date) -> list[Task]:
        """Tasks scheduled to be worked on during ``day``."""
        prefix = day.isoformat()
        return [
            t
            for t in self.list_tasks()
            if t.scheduled_start and t.scheduled_start.startswith(prefix)
        ]
