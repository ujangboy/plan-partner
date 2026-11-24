"""All SQL for tasks and their tags."""

from __future__ import annotations

import sqlite3
from uuid import uuid4

from dayplan.database.connection import Database
from dayplan.models.task import Task

_COLUMNS = (
    "id, title, description, status, priority, due_date, due_time, "
    "scheduled_start, scheduled_end, estimated_minutes, project_id, "
    "created_at, updated_at, completed_at"
)

_SORT_SQL = {
    "created": "created_at DESC",
    "due": "due_date IS NULL, due_date ASC, created_at DESC",
    "priority": (
        "CASE priority WHEN 'urgent' THEN 0 WHEN 'high' THEN 1 "
        "WHEN 'medium' THEN 2 ELSE 3 END, created_at DESC"
    ),
}


class TaskRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def create(self, task: Task) -> Task:
        with self.db.connect() as conn:
            conn.execute(
                f"INSERT INTO tasks ({_COLUMNS}) VALUES "
                "(:id, :title, :description, :status, :priority, :due_date, :due_time, "
                ":scheduled_start, :scheduled_end, :estimated_minutes, :project_id, "
                ":created_at, :updated_at, :completed_at)",
                self._params(task),
            )
            self._set_tags(conn, task)
        return task

    def update(self, task: Task) -> None:
        params = self._params(task)
        with self.db.connect() as conn:
            conn.execute(
                "UPDATE tasks SET title=:title, description=:description, status=:status, "
                "priority=:priority, due_date=:due_date, due_time=:due_time, "
                "scheduled_start=:scheduled_start, scheduled_end=:scheduled_end, "
                "estimated_minutes=:estimated_minutes, project_id=:project_id, "
                "updated_at=:updated_at, completed_at=:completed_at WHERE id=:id",
                params,
            )
            self._set_tags(conn, task)

    def get(self, task_id: str) -> Task | None:
        with self.db.connect() as conn:
            row = conn.execute(
                f"SELECT {_COLUMNS} FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
            if row is None:
                return None
            task = Task.from_row(row)
            task.tags = self._tags_for(conn, task_id)
            return task

    def delete(self, task_id: str) -> bool:
        with self.db.connect() as conn:
            cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            return cursor.rowcount > 0

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
        where: list[str] = []
        params: list[object] = []
        if status:
            where.append("status = ?")
            params.append(status)
        elif not include_archived:
            where.append("status != 'archived'")
        if priority:
            where.append("priority = ?")
            params.append(priority)
        if project_id:
            where.append("project_id = ?")
            params.append(project_id)
        if query.strip():
            where.append("(title LIKE ? OR description LIKE ?)")
            pattern = f"%{query.strip()}%"
            params.extend([pattern, pattern])

        sql = f"SELECT {_COLUMNS} FROM tasks"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY " + _SORT_SQL.get(sort, _SORT_SQL["created"])

        with self.db.connect() as conn:
            return [Task.from_row(row) for row in conn.execute(sql, params)]

    def count_by_status(self) -> dict[str, int]:
        with self.db.connect() as conn:
            return {
                row["status"]: row["total"]
                for row in conn.execute(
                    "SELECT status, COUNT(*) AS total FROM tasks GROUP BY status"
                )
            }

    @staticmethod
    def _params(task: Task) -> dict[str, object]:
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date,
            "due_time": task.due_time,
            "scheduled_start": task.scheduled_start,
            "scheduled_end": task.scheduled_end,
            "estimated_minutes": task.estimated_minutes,
            "project_id": task.project_id,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "completed_at": task.completed_at,
        }

    @staticmethod
    def _tags_for(conn: sqlite3.Connection, task_id: str) -> list[str]:
        return [
            row[0]
            for row in conn.execute(
                "SELECT t.name FROM tags t JOIN task_tags tt ON tt.tag_id = t.id "
                "WHERE tt.task_id = ? ORDER BY t.name",
                (task_id,),
            )
        ]

    @staticmethod
    def _set_tags(conn: sqlite3.Connection, task: Task) -> None:
        conn.execute("DELETE FROM task_tags WHERE task_id = ?", (task.id,))
        seen: set[str] = set()
        for raw in task.tags:
            name = raw.strip().lower()
            if not name or name in seen:
                continue
            seen.add(name)
            conn.execute(
                "INSERT OR IGNORE INTO tags (id, name) VALUES (?, ?)",
                (str(uuid4()), name),
            )
            tag_id = conn.execute(
                "SELECT id FROM tags WHERE name = ?", (name,)
            ).fetchone()[0]
            conn.execute(
                "INSERT INTO task_tags (task_id, tag_id) VALUES (?, ?)",
                (task.id, tag_id),
            )
