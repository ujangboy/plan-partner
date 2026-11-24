"""Appearance, date/time, Pomodoro and data settings."""

from __future__ import annotations

from datetime import date
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Input, Label, Select, Static

from dayplan.models.task import PRIORITIES
from dayplan.screens.base import BaseScreen
from dayplan.utils.formatting import PRIORITY_LABELS


class SettingsScreen(BaseScreen):
    TITLE = "Settings"
    BINDINGS = [Binding("ctrl+s", "save", "Save")]

    def build_content(self) -> ComposeResult:
        app = self.app
        with VerticalScroll() as container:
            with Vertical(classes="panel"):
                yield Static("TAMPILAN & WAKTU", classes="panel-title")
                yield self._field("Tema", Select([("Dark", "dark"), ("Light", "light")], id="set-theme"))
                yield self._field("Format tanggal", Input(id="set-date-format"))
                yield self._field("Format jam", Input(id="set-time-format"))
                yield self._field("Zona waktu", Input(placeholder="Asia/Jakarta (kosong = lokal)", id="set-timezone"))
                yield self._field(
                    "Prioritas default",
                    Select([(PRIORITY_LABELS[p], p) for p in PRIORITIES], id="set-priority"),
                )
            with Vertical(classes="panel"):
                yield Static("DURASI POMODORO", classes="panel-title")
                yield self._field("Fokus (menit)", Input(id="set-focus"))
                yield self._field("Istirahat singkat (menit)", Input(id="set-short"))
                yield self._field("Istirahat panjang (menit)", Input(id="set-long"))
            with Vertical(classes="panel"):
                yield Static("DATA & BACKUP", classes="panel-title")
                yield self._field("Path ekspor JSON", Input(id="set-export-path", value=str(app.db.path.with_suffix(".json"))))
                yield self._field("Path impor JSON", Input(id="set-import-path"))
                with Horizontal(classes="button-row"):
                    yield Button("Simpan (Ctrl+S)", id="set-save", variant="primary")
                    yield Button("Export JSON", id="set-export")
                    yield Button("Import JSON", id="set-import")
            with Vertical(classes="panel"):
                yield Static("INFORMASI DATABASE", classes="panel-title")
                yield Static(id="set-db-info")
        return container

    @staticmethod
    def _field(label: str, widget: object) -> Horizontal:
        return Horizontal(Label(label), widget, classes="form-field")

    def on_mount(self) -> None:
        super().on_mount()
        config = self.app.config
        self.query_one("#set-theme", Select).value = config.get("theme")
        self.query_one("#set-date-format", Input).value = config.get("date_format")
        self.query_one("#set-time-format", Input).value = config.get("time_format")
        self.query_one("#set-timezone", Input).value = config.get("timezone")
        self.query_one("#set-priority", Select).value = config.get("default_priority")
        self.query_one("#set-focus", Input).value = config.get("focus_minutes")
        self.query_one("#set-short", Input).value = config.get("short_break_minutes")
        self.query_one("#set-long", Input).value = config.get("long_break_minutes")
        self.query_one("#set-db-info", Static).update(
            f"Database: {self.app.db.path}\nUkuran: {self.app.db.path.stat().st_size if self.app.db.path.exists() else 0} bytes"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "set-save":
            self.action_save()
        elif event.button.id == "set-export":
            self.action_export()
        elif event.button.id == "set-import":
            self.action_import()

    def action_save(self) -> None:
        values = {
            "theme": self.query_one("#set-theme", Select).value,
            "date_format": self.query_one("#set-date-format", Input).value,
            "time_format": self.query_one("#set-time-format", Input).value,
            "timezone": self.query_one("#set-timezone", Input).value,
            "default_priority": self.query_one("#set-priority", Select).value,
            "focus_minutes": self.query_one("#set-focus", Input).value,
            "short_break_minutes": self.query_one("#set-short", Input).value,
            "long_break_minutes": self.query_one("#set-long", Input).value,
        }
        try:
            for key in ("focus_minutes", "short_break_minutes", "long_break_minutes"):
                if int(values[key]) <= 0:
                    raise ValueError("Durasi harus lebih dari nol.")
            if values["timezone"]:
                try:
                    ZoneInfo(values["timezone"])
                except (ZoneInfoNotFoundError, ValueError) as error:
                    raise ValueError("Zona waktu tidak dikenal.") from error
            for key in ("date_format", "time_format"):
                date.today().strftime(values[key])
            self.app.config.set_many(values)
        except ValueError as error:
            self.status(str(error))
            return
        self.app.theme = "textual-dark" if values["theme"] == "dark" else "textual-light"
        self.status("Pengaturan disimpan.")

    def action_export(self) -> None:
        path = self.query_one("#set-export-path", Input).value.strip()
        if not path:
            self.status("Isi path ekspor terlebih dahulu.")
            return
        try:
            self.app.backup_service.export_json(path)
            self.status(f"Backup Ditulis: {path}")
        except OSError as error:
            self.status(f"Gagal menulis backup: {error}")

    def action_import(self) -> None:
        path = self.query_one("#set-import-path", Input).value.strip()
        if not path:
            self.status("Isi path impor terlebih dahulu.")
            return
        try:
            count = self.app.backup_service.import_json(path)
            self.status(f"{count} tugas berhasil dipulihkan.")
        except (OSError, ValueError) as error:
            self.status(f"Gagal mengimpor: {error}")
