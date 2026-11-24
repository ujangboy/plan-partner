"""Project management screen."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, DataTable, Static

from dayplan.screens.base import BaseScreen
from dayplan.utils.formatting import status_badge, truncate
from dayplan.widgets.confirm import ConfirmDialog
from dayplan.widgets.project_form import ProjectForm


class ProjectsScreen(BaseScreen):
    TITLE = "Projects"
    BINDINGS = [
        Binding("ctrl+n", "new_project", "New Project"),
        Binding("e", "edit_project", "Edit", show=False),
        Binding("delete", "delete_project", "Delete", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.selected_project_id: str | None = None

    def build_content(self) -> ComposeResult:
        with Vertical() as container:
            yield DataTable(id="project-table")
            with Horizontal(classes="button-row"):
                yield Button("Proyek Baru (Ctrl+N)", id="proj-add", variant="primary")
                yield Button("Edit (E)", id="proj-edit")
                yield Button("Hapus (Del)", id="proj-delete", variant="error")
            with Vertical(classes="panel"):
                yield Static("TUGAS DALAM PROYEK", classes="panel-title")
                yield Static(id="project-tasks")
        return container

    def on_mount(self) -> None:
        super().on_mount()
        table = self.query_one("#project-table", DataTable)
        table.add_columns("Nama", "Aktif", "Selesai", "Progres", "Deskripsi")
        for column, width in zip(table.columns.values(), (24, 10, 10, 12, 40)):
            column.width = width
        self.refresh_data()

    def refresh_data(self) -> None:
        projects = self.app.project_service.list_projects()
        table = self.query_one("#project-table", DataTable)
        table.clear(columns=False)
        for project in projects:
            total = project.active_count + project.done_count
            percent = round(project.done_count / total * 100) if total else 0
            table.add_row(
                truncate(project.name, 22),
                str(project.active_count),
                str(project.done_count),
                f"{percent}%",
                truncate(project.description, 38),
            )
        if not projects:
            table.add_row("—", "", "", "", "Belum ada proyek. Tekan Ctrl+N.")

        tasks = (
            self.app.project_service.tasks(self.selected_project_id)
            if self.selected_project_id
            else []
        )
        lines = [
            f"{status_badge(task.status)}  {truncate(task.title, 60)}"
            for task in tasks
        ]
        self.query_one("#project-tasks", Static).update(
            "\n".join(lines) if lines else "Pilih proyek untuk melihat tugasnya."
        )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.data_table.id != "project-table":
            return
        projects = self.app.project_service.list_projects()
        if event.cursor_row < len(projects):
            self.selected_project_id = projects[event.cursor_row].id
            self.refresh_data()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        actions = {
            "proj-add": self.action_new_project,
            "proj-edit": self.action_edit_project,
            "proj-delete": self.action_delete_project,
        }
        action = actions.get(event.button.id or "")
        if action:
            action()

    def action_new_project(self) -> None:
        self.app.push_screen(ProjectForm(), self._after_form)

    def action_edit_project(self) -> None:
        if not self.selected_project_id:
            self.status("Pilih proyek terlebih dahulu.")
            return
        project = self.app.project_service.get(self.selected_project_id)
        self.app.push_screen(ProjectForm(project), self._after_form)

    def _after_form(self, values: dict[str, str] | None) -> None:
        if values is None:
            return
        try:
            if self.selected_project_id and self.app.project_service.get(self.selected_project_id):
                self.app.project_service.update(self.selected_project_id, **values)
                self.status("Proyek diperbarui.")
            else:
                created = self.app.project_service.create(**values)
                self.selected_project_id = created.id
                self.status("Proyek dibuat.")
        except ValueError as error:
            self.status(str(error))
            return
        self.refresh_data()

    def action_delete_project(self) -> None:
        if not self.selected_project_id:
            self.status("Pilih proyek terlebih dahulu.")
            return
        project = self.app.project_service.get(self.selected_project_id)
        self.app.push_screen(
            ConfirmDialog(
                f"Hapus proyek '{project.name}'? Tugas di dalamnya akan tetap ada tanpa proyek."
            ),
            lambda confirmed: self._confirm_delete(confirmed, project.id),
        )

    def _confirm_delete(self, confirmed: bool | None, project_id: str) -> None:
        if not confirmed:
            return
        self.app.project_service.delete(project_id)
        self.selected_project_id = None
        self.status("Proyek dihapus; tugasnya tetap tersimpan.")
        self.refresh_data()
