"""Pomodoro focus session model."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass
class FocusSession:
    id: str
    duration_minutes: int
    started_at: str
    task_id: str | None = None
    completed_at: str | None = None
    status: str = "planned"

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> FocusSession:
        return cls(**dict(row))
