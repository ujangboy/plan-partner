"""Project model."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass
class Project:
    id: str
    name: str
    description: str = ""
    color: str = ""
    created_at: str = ""
    active_count: int = 0
    done_count: int = 0

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> Project:
        return cls(**dict(row))
