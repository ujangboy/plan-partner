"""Task model and its vocabulary."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field

STATUSES = ("inbox", "todo", "in_progress", "waiting", "done", "archived")
PRIORITIES = ("urgent", "high", "medium", "low")
ACTIVE_STATUSES = ("inbox", "todo", "in_progress", "waiting")


@dataclass
class Task:
    id: str
    title: str
    description: str = ""
    status: str = "inbox"
    priority: str = "medium"
    due_date: str | None = None
    due_time: str | None = None
    scheduled_start: str | None = None
    scheduled_end: str | None = None
    estimated_minutes: int | None = None
    project_id: str | None = None
    created_at: str = ""
    updated_at: str = ""
    completed_at: str | None = None
    tags: list[str] = field(default_factory=list)

    @property
    def is_done(self) -> bool:
        return self.status == "done"

    @property
    def is_active(self) -> bool:
        return self.status in ACTIVE_STATUSES

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> Task:
        data = dict(row)
        data.pop("tags", None)
        return cls(**data)
