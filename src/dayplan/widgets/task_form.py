"""Modal form for creating and editing a task."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, Static

from dayplan.models.task import PRIORITIES, STATUSES
from dayplan.utils.formatting import PRIORITY_LABELS, STATUS_LABELS


class TaskForm(ModalScreen[dict[str, object] | None]):
    BINDINGS = [
        Binding("escape", "cancel", "Batal"),
        Binding("ctrl+s", "save", "Simpan"),
    ]

    def __init__(self, task: object | None = None) -> None:
        super().__init__()
        self.task_record = task

    def compose(self) -> ComposeResult:
        editing = self.task_record is not None
        values = self.task_record
        with Vertical(classes="form-dialog"):
            yield Static("Edit Tugas" if editing else "Tugas Baru", classes="form-title")
            with VerticalScroll(id="form-scroll"):
                yield self._field("Judul", Input(id="f-title", value=getattr(values, "title", "")))
                yield self._field(
                    "Deskripsi",
                    Input(id="f-description", value=getattr(values, "description", "")),
                )
                yield self._field(
                    "Status",
                    Select(
                        [(STATUS_LABELS[s], s) for s in STATUSES],
                        value=getattr(values, "status", "inbox"),
                        id="f-status",
                    ),
                )
                yield self._field(
                    "Prioritas",
                    Select(
                        [(PRIORITY_LABELS[p], p) for p in PRIORITIES],
                        value=getattr(values, "priority", "medium"),
                        id="f-priority",
                    ),
                )
                yield self._field(
                    "Deadline",
                    Input(placeholder="YYYY-MM-DD", id="f-due", value=getattr(values, "due_date", "") or ""),
                )
                yield self._field(
                    "Jam deadline",
                    Input(placeholder="HH:MM (opsional)", id="f-due-time", value=getattr(values, "due_time", "") or ""),
                )
                yield self._field(
                    "Mulai kerja",
                    Input(placeholder="YYYY-MM-DDTHH:MM", id="f-start", value=getattr(values, "scheduled_start", "") or ""),
                )
                yield self._field(
                    "Selesai kerja",
                    Input(placeholder="YYYY-MM-DDTHH:MM", id="f-end", value=getattr(values, "scheduled_end", "") or ""),
                )
                yield self._field(
                    "Estimasi (menit)",
                    Input(placeholder="90", id="f-estimated", value=str(getattr(values, "estimated_minutes", "") or "")),
                )
                yield self._field("Proyek", Select([("Tanpa proyek", "")], id="f-project"))
                yield self._field(
                    "Tag",
                    Input(placeholder="kuliah, python", id="f-tags", value=", ".join(getattr(values, "tags", []))),
                )
            with Horizontal(classes="button-row"):
                yield Button("Simpan (Ctrl+S)", id="save", variant="primary")
                yield Button("Batal (Esc)", id="cancel")

    @staticmethod
    def _field(label: str, widget: object) -> Horizontal:
        return Horizontal(Label(label), widget, classes="form-field")

    def on_mount(self) -> None:
        select = self.query_one("#f-project", Select)
        projects = self.app.project_service.list_projects()
        options = [("Tanpa proyek", "")] + [(project.name, project.id) for project in projects]
        select.set_options(options)
        current = getattr(self.task_record, "project_id", None) or ""
        select.value = current if any(value == current for _, value in options) else ""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self.action_save()
        elif event.button.id == "cancel":
            self.action_cancel()

    def action_save(self) -> None:
        title = self.query_one("#f-title", Input).value.strip()
        if not title:
            self.app.notify("Judul tugas wajib diisi.", severity="error")
            self.query_one("#f-title", Input).focus()
            return
        self.dismiss(
            {
                "title": title,
                "description": self.query_one("#f-description", Input).value,
                "status": self.query_one("#f-status", Select).value,
                "priority": self.query_one("#f-priority", Select).value,
                "due_date": self.query_one("#f-due", Input).value,
                "due_time": self.query_one("#f-due-time", Input).value,
                "scheduled_start": self.query_one("#f-start", Input).value,
                "scheduled_end": self.query_one("#f-end", Input).value,
                "estimated_minutes": self.query_one("#f-estimated", Input).value,
                "project_id": self.query_one("#f-project", Select).value or None,
                "tags": [
                    tag.strip()
                    for tag in self.query_one("#f-tags", Input).value.split(",")
                    if tag.strip()
                ],
            }
        )

    def action_cancel(self) -> None:
        self.dismiss(None)
