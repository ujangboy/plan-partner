"""All SQL for projects."""

from __future__ import annotations

import sqlite3
from uuid import uuid4

from dayplan.database.connection import Database
from dayplan.models.project import Project

_SELECT = """
SELECT p.id, p.name, p.description, p.color, p.created_at,
       (SELECT COUNT(*) FROM tasks t WHERE t.project_id = p.id
          AND t.status NOT IN ('done', 'archived')) AS active_count,
       (SELECT COUNT(*) FROM tasks t WHERE t.project_id = p.id
          AND t.status = 'done') AS done_count
FROM projects p
"""


class ProjectRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def create(self, project: Project) -> Project:
        with self.db.connect() as conn:
            conn.execute(
                "INSERT INTO projects (id, name, description, color, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (project.id, project.name, project.description, project.color, project.created_at),
            )
        return project

    def update(self, project: Project) -> None:
        with self.db.connect() as conn:
            conn.execute(
                "UPDATE projects SET name = ?, description = ?, color = ? WHERE id = ?",
                (project.name, project.description, project.color, project.id),
            )

    def get(self, project_id: str) -> Project | None:
        with self.db.connect() as conn:
            row = conn.execute(
                _SELECT + " WHERE p.id = ?", (project_id,)
            ).fetchone()
            return Project.from_row(row) if row else None

    def delete(self, project_id: str) -> bool:
        with self.db.connect() as conn:
            cursor = conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            return cursor.rowcount > 0

    def list_projects(self) -> list[Project]:
        with self.db.connect() as conn:
            return [
                Project.from_row(row)
                for row in conn.execute(_SELECT + " ORDER BY p.name COLLATE NOCASE")
            ]

    @staticmethod
    def new_id() -> str:
        return str(uuid4())
