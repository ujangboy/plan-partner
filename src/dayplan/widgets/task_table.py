"""Reusable task DataTable with row-to-id mapping."""

from __future__ import annotations

from textual.widgets import DataTable

from dayplan.models.task import Task
from dayplan.utils.formatting import (
    format_duration,
    priority_badge,
    status_badge,
    truncate,
)


class TaskTable(DataTable):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(cursor_type="row", zebra_stripes=True, **kwargs)
        self.task_ids: dict[int, str] = {}

    def on_mount(self) -> None:
        self.add_columns("Status", "Judul", "Prioritas", "Deadline", "Estimasi", "Proyek")
        widths = [16, 40, 12, 13, 10, 14]
        for column, width in zip(self.columns.values(), widths):
            column.width = width

    def load(self, tasks: list[Task], overdue: set[str] | None = None) -> None:
        overdue = overdue or set()
        self.clear(columns=False)
        self.task_ids.clear()
        for task in tasks:
            deadline = task.due_date or "—"
            if task.id in overdue:
                deadline = f"! {deadline}"
            index = self.row_count
            self.add_row(
                status_badge(task.status),
                truncate(task.title, 38),
                priority_badge(task.priority),
                deadline,
                format_duration(task.estimated_minutes),
                truncate(task.project_id[:8] if task.project_id else "—", 12),
            )
            self.task_ids[index] = task.id

    def selected_task_id(self) -> str | None:
        return self.task_ids.get(self.cursor_row)
