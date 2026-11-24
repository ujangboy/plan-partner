"""Modal form for projects."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static

from dayplan.models.project import Project


class ProjectForm(ModalScreen[dict[str, str] | None]):
    BINDINGS = [
        Binding("escape", "cancel", "Batal"),
        Binding("ctrl+s", "save", "Simpan"),
    ]

    def __init__(self, project: Project | None = None) -> None:
        super().__init__()
        self.project = project

    def compose(self) -> ComposeResult:
        with Vertical(classes="form-dialog"):
            yield Static("Proyek Baru" if self.project is None else "Edit Proyek", classes="form-title")
            yield Horizontal(Label("Nama"), Input(id="p-name", value=getattr(self.project, "name", "")), classes="form-field")
            yield Horizontal(Label("Deskripsi"), Input(id="p-description", value=getattr(self.project, "description", "")), classes="form-field")
            yield Horizontal(Label("Warna"), Input(id="p-color", value=getattr(self.project, "color", "")), classes="form-field")
            with Horizontal(classes="button-row"):
                yield Button("Simpan (Ctrl+S)", id="save", variant="primary")
                yield Button("Batal (Esc)", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self.action_save()
        elif event.button.id == "cancel":
            self.action_cancel()

    def action_save(self) -> None:
        name = self.query_one("#p-name", Input).value.strip()
        if not name:
            self.app.notify("Nama proyek wajib diisi.", severity="error")
            return
        self.dismiss(
            {
                "name": name,
                "description": self.query_one("#p-description", Input).value,
                "color": self.query_one("#p-color", Input).value,
            }
        )

    def action_cancel(self) -> None:
        self.dismiss(None)
