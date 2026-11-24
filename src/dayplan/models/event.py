"""Calendar event model — a time-bound commitment, distinct from a task."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass
class CalendarEvent:
    id: str
    title: str
    start_at: str
    end_at: str
    description: str = ""
    is_all_day: bool = False
    location: str = ""
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> CalendarEvent:
        data = dict(row)
        data["is_all_day"] = bool(data["is_all_day"])
        return cls(**data)
