"""Modal form for calendar events."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Checkbox, Input, Label, Static

from dayplan.models.event import CalendarEvent


class EventForm(ModalScreen[dict[str, object] | None]):
    BINDINGS = [
        Binding("escape", "cancel", "Batal"),
        Binding("ctrl+s", "save", "Simpan"),
    ]

    def __init__(
        self, event: CalendarEvent | None = None, default_date: str = ""
    ) -> None:
        super().__init__()
        self.event = event
        self.default_date = default_date

    def compose(self) -> ComposeResult:
        with Vertical(classes="form-dialog"):
            yield Static("Kegiatan Baru" if self.event is None else "Edit Kegiatan", classes="form-title")
            with VerticalScroll():
                yield self._field("Judul", Input(id="e-title", value=getattr(self.event, "title", "")))
                yield self._field(
                    "Mulai",
                    Input(
                        placeholder="YYYY-MM-DDTHH:MM",
                        id="e-start",
                        value=getattr(self.event, "start_at", "") or f"{self.default_date}T08:00",
                    ),
                )
                yield self._field(
                    "Selesai",
                    Input(
                        placeholder="YYYY-MM-DDTHH:MM",
                        id="e-end",
                        value=getattr(self.event, "end_at", "") or f"{self.default_date}T09:00",
                    ),
                )
                yield self._field(
                    "Lokasi", Input(id="e-location", value=getattr(self.event, "location", ""))
                )
                yield self._field(
                    "Deskripsi",
                    Input(id="e-description", value=getattr(self.event, "description", "")),
                )
                yield Horizontal(
                    Label("Sepanjang hari"),
                    Checkbox(value=getattr(self.event, "is_all_day", False), id="e-allday"),
                    classes="form-field",
                )
            with Horizontal(classes="button-row"):
                yield Button("Simpan (Ctrl+S)", id="save", variant="primary")
                yield Button("Batal (Esc)", id="cancel")

    @staticmethod
    def _field(label: str, widget: object) -> Horizontal:
        return Horizontal(Label(label), widget, classes="form-field")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self.action_save()
        elif event.button.id == "cancel":
            self.action_cancel()

    def action_save(self) -> None:
        title = self.query_one("#e-title", Input).value.strip()
        if not title:
            self.app.notify("Judul kegiatan wajib diisi.", severity="error")
            return
        self.dismiss(
            {
                "title": title,
                "start_at": self.query_one("#e-start", Input).value,
                "end_at": self.query_one("#e-end", Input).value,
                "location": self.query_one("#e-location", Input).value,
                "description": self.query_one("#e-description", Input).value,
                "is_all_day": self.query_one("#e-allday", Checkbox).value,
            }
        )

    def action_cancel(self) -> None:
        self.dismiss(None)
