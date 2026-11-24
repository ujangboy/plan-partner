"""Task list with search, filters, sorting and full CRUD."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, Select

from dayplan.models.task import PRIORITIES, STATUSES
from dayplan.screens.base import BaseScreen
from dayplan.utils.formatting import PRIORITY_LABELS, STATUS_LABELS
from dayplan.widgets.confirm import ConfirmDialog
from dayplan.widgets.task_form import TaskForm
from dayplan.widgets.task_table import TaskTable

_STATUS_OPTIONS = [("Semua status", "")] + [(STATUS_LABELS[s], s) for s in STATUSES] + [
    ("Aktif", "active")
]
_PRIORITY_OPTIONS = [("Semua prioritas", "")] + [
    (PRIORITY_LABELS[p], p) for p in PRIORITIES
]
_SORT_OPTIONS = [
    ("Terbaru", "created"),
    ("Deadline", "due"),
    ("Prioritas", "priority"),
]


class TasksScreen(BaseScreen):
    TITLE = "Tasks"
    BINDINGS = [
        Binding("ctrl+n", "new_task", "New Task"),
        Binding("ctrl+f", "search", "Search"),
        Binding("e", "edit", "Edit", show=False),
        Binding("space", "toggle", "Done", show=False),
        Binding("delete", "delete", "Delete", show=False),
        Binding("r", "refresh", "Refresh", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.editing_task_id: str | None = None

    def build_content(self) -> ComposeResult:
        with Vertical() as container:
            with Horizontal(classes="filter-row"):
                yield Input(placeholder="Cari tugas... (Ctrl+F)", id="search")
                yield Select(_STATUS_OPTIONS, value="", id="status-filter")
                yield Select(_PRIORITY_OPTIONS, value="", id="priority-filter")
                yield Select(_SORT_OPTIONS, value="created", id="sort-filter")
            yield TaskTable(id="task-table")
            with Horizontal(classes="button-row"):
                yield Button("Tambah (Ctrl+N)", id="btn-add", variant="primary")
                yield Button("Edit (E)", id="btn-edit")
                yield Button("Selesai (Spasi)", id="btn-done")
                yield Button("Hapus (Del)", id="btn-delete", variant="error")
                yield Button("Refresh (R)", id="btn-refresh")
        return container

    def on_mount(self) -> None:
        super().on_mount()
        self.refresh_data()

    def refresh_data(self) -> None:
        query = self.query_one("#search", Input).value
        status = self.query_one("#status-filter", Select).value
        priority = self.query_one("#priority-filter", Select).value
        sort = self.query_one("#sort-filter", Select).value
        if status == "active":
            tasks = [
                task
                for task in self.app.task_service.list_tasks(sort=sort, query=query)
                if task.is_active
            ]
        else:
            tasks = self.app.task_service.list_tasks(
                status=status or None,
                priority=priority or None,
                query=query,
                sort=sort,
                include_archived=status == "archived",
            )
        overdue = {
            task.id
            for task in tasks
            if self.app.task_service.is_overdue(task)
        }
        self.query_one("#task-table", TaskTable).load(tasks, overdue)

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search":
            self.refresh_data()

    def on_select_changed(self) -> None:
        self.refresh_data()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        actions = {
            "btn-add": self.action_new_task,
            "btn-edit": self.action_edit,
            "btn-done": self.action_toggle,
            "btn-delete": self.action_delete,
            "btn-refresh": self.action_refresh,
        }
        action = actions.get(event.button.id or "")
        if action:
            action()

    def action_refresh(self) -> None:
        self.refresh_data()
        self.status("Daftar tugas diperbarui.")

    def action_search(self) -> None:
        self.query_one("#search", Input).focus()

    def action_new_task(self) -> None:
        self.editing_task_id = None
        self.app.push_screen(TaskForm(), self._after_form)

    def action_edit(self) -> None:
        task_id = self.query_one("#task-table", TaskTable).selected_task_id()
        if not task_id:
            self.status("Pilih tugas terlebih dahulu.", )
            return
        self.editing_task_id = task_id
        self.app.push_screen(TaskForm(self.app.task_service.get(task_id)), self._after_form)

    def _after_form(self, values: dict[str, object] | None) -> None:
        if values is None:
            return
        task_id = self.editing_task_id
        try:
            if task_id and self.app.task_service.get(task_id):
                self.app.task_service.update(task_id, **values)
                self.status("Tugas diperbarui.")
            else:
                self.app.task_service.create(**values)
                self.status("Tugas dibuat.")
        except (ValueError, LookupError) as error:
            self.status(str(error))
            return
        self.refresh_data()

    def action_toggle(self) -> None:
        if self.is_typing():
            return
        task_id = self.query_one("#task-table", TaskTable).selected_task_id()
        if not task_id:
            self.status("Pilih tugas terlebih dahulu.")
            return
        try:
            task = self.app.task_service.toggle_done(task_id)
            self.status(f"{task.title}: {task.status}")
        except LookupError as error:
            self.status(str(error))
        self.refresh_data()

    def action_delete(self) -> None:
        if self.is_typing():
            return
        task_id = self.query_one("#task-table", TaskTable).selected_task_id()
        if not task_id:
            self.status("Pilih tugas terlebih dahulu.")
            return
        task = self.app.task_service.get(task_id)
        self.app.push_screen(
            ConfirmDialog(f"Hapus tugas '{task.title}'?"),
            lambda confirmed: self._confirm_delete(confirmed, task_id),
        )

    def _confirm_delete(self, confirmed: bool | None, task_id: str) -> None:
        if not confirmed:
            return
        self.app.task_service.delete(task_id)
        self.status("Tugas dihapus.")
        self.refresh_data()
