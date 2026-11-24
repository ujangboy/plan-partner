"""Derived productivity numbers. The UI only renders these results."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from dayplan.config import Config
from dayplan.database.connection import Database
from dayplan.services.project_service import ProjectService
from dayplan.services.task_service import TaskService
from dayplan.utils.dates import local_now


@dataclass(frozen=True)
class Summary:
    active: int
    completed: int
    overdue: int
    due_today: int
    active_projects: int
    completion_rate: float


@dataclass(frozen=True)
class ProjectProgress:
    name: str
    active: int
    done: int
    percent: int


class StatisticsService:
    def __init__(self, db: Database, config: Config | None = None) -> None:
        self.db = db
        self.config = config or Config(db)
        self.tasks = TaskService(db, self.config)
        self.projects = ProjectService(db, self.config)

    def summary(self) -> Summary:
        today = local_now(self.config.timezone).date().isoformat()
        tasks = self.tasks.list_tasks()
        active = sum(1 for task in tasks if task.is_active)
        completed = sum(1 for task in tasks if task.status == "done")
        total = active + completed
        return Summary(
            active=active,
            completed=completed,
            overdue=sum(1 for task in tasks if self.tasks.is_overdue(task)),
            due_today=sum(1 for task in tasks if task.due_date == today and task.is_active),
            active_projects=len(self.projects.list_projects()),
            completion_rate=round(completed / total * 100) if total else 0,
        )

    def project_progress(self) -> list[ProjectProgress]:
        result = []
        for project in self.projects.list_projects():
            total = project.active_count + project.done_count
            result.append(
                ProjectProgress(
                    name=project.name,
                    active=project.active_count,
                    done=project.done_count,
                    percent=round(project.done_count / total * 100) if total else 0,
                )
            )
        return result

    def daily_completions(self, days: int = 7) -> list[tuple[date, int]]:
        """Completion counts for the trailing ``days`` days, oldest first."""
        today = local_now(self.config.timezone).date()
        result = []
        for offset in reversed(range(days)):
            day = today - timedelta(days=offset)
            with self.db.connect() as conn:
                row = conn.execute(
                    "SELECT COUNT(*) AS total FROM tasks WHERE status = 'done' "
                    "AND substr(completed_at, 1, 10) = ?",
                    (day.isoformat(),),
                ).fetchone()
            result.append((day, int(row["total"])))
        return result

    def upcoming_tasks(self, days: int = 7) -> list[object]:
        today = local_now(self.config.timezone).date()
        end = today + timedelta(days=days)
        return sorted(
            (
                task
                for task in self.tasks.list_tasks()
                if task.due_date and today.isoformat() <= task.due_date <= end.isoformat()
            ),
            key=lambda task: (task.due_date, task.priority),
        )
