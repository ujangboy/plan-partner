"""Pomodoro focus timer with persisted session history."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, DataTable, ProgressBar, Select, Static

from dayplan.screens.base import BaseScreen
from dayplan.utils.formatting import truncate


class FocusScreen(BaseScreen):
    TITLE = "Focus Mode"

    def __init__(self) -> None:
        super().__init__()
        self.mode = "focus"
        self.total_seconds = 25 * 60
        self.seconds_left = self.total_seconds
        self.running = False
        self.session_id: str | None = None
        self.selected_task_id: str | None = None
        self.timer = None

    def _duration(self, key: str) -> int:
        return int(getattr(self.app.config, key))

    def build_content(self) -> ComposeResult:
        with VerticalScroll() as container:
            with Vertical(classes="panel"):
                yield Static("PILIH TUGAS", classes="panel-title")
                yield Select([("Tanpa tugas", "")], id="focus-task")
            with Vertical(classes="panel"):
                yield Static(id="focus-mode", classes="panel-title")
                yield Static(id="timer", classes="timer-display")
                yield ProgressBar(total=1, id="focus-progress", classes="progress-bar")
                with Horizontal(classes="button-row"):
                    yield Button("Mulai", id="focus-start", variant="primary")
                    yield Button("Jeda", id="focus-pause")
                    yield Button("Lanjut", id="focus-resume")
                    yield Button("Ulang", id="focus-reset")
                    yield Button("Selesai", id="focus-finish")
            with Vertical(classes="panel"):
                yield Static("RIWAYAT SESI", classes="panel-title")
                yield DataTable(id="focus-history")
        return container

    def on_mount(self) -> None:
        super().on_mount()
        table = self.query_one("#focus-history", DataTable)
        table.add_columns("Waktu mulai", "Tugas", "Durasi", "Status")
        for column, width in zip(table.columns.values(), (22, 34, 10, 14)):
            column.width = width
        options = [("Tanpa tugas", "")] + [
            (truncate(task.title, 40), task.id)
            for task in self.app.task_service.list_tasks()
        ]
        self.query_one("#focus-task", Select).set_options(options)
        self._refresh_history()
        self._set_mode("focus")
        self.timer = self.set_interval(1.0, self.tick)

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "focus-task":
            self.selected_task_id = event.value or None

    def _update_display(self) -> None:
        minutes, seconds = divmod(max(self.seconds_left, 0), 60)
        self.query_one("#timer", Static).update(f"{minutes:02d}:{seconds:02d}")
        labels = {"focus": "FOKUS", "short": "ISTIRAHAT SINGKAT", "long": "ISTIRAHAT PANJANG"}
        self.query_one("#focus-mode", Static).update(
            f"{labels[self.mode]} — {self.total_seconds // 60} menit"
        )
        progress = 1 - self.seconds_left / self.total_seconds if self.total_seconds else 0
        self.query_one("#focus-progress", ProgressBar).progress = max(0, min(progress, 1))

    def _set_mode(self, mode: str) -> None:
        self.mode = mode
        key = {
            "focus": "focus_minutes",
            "short": "short_break_minutes",
            "long": "long_break_minutes",
        }[mode]
        self.total_seconds = self._duration(key) * 60
        self.seconds_left = self.total_seconds
        self.running = False
        self.session_id = None
        self._update_display()

    def tick(self) -> None:
        if not self.running:
            return
        self.seconds_left -= 1
        if self.seconds_left <= 0:
            self.seconds_left = 0
            self.running = False
            if self.session_id:
                self.app.focus_service.complete(self.session_id)
                self.session_id = None
            self.notify("Sesi selesai. Istirahat singkat dimulai.", title="Focus")
            self._refresh_history()
            self._set_mode("short")
            return
        self._update_display()

    def _refresh_history(self) -> None:
        table = self.query_one("#focus-history", DataTable)
        table.clear(columns=False)
        tasks = {
            task.id: task.title for task in self.app.task_service.list_tasks(include_archived=True)
        }
        for session in self.app.focus_service.history(20):
            table.add_row(
                session.started_at[:16].replace("T", " "),
                truncate(tasks.get(session.task_id or "", "—"), 32),
                f"{session.duration_minutes}m",
                session.status,
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        actions = {
            "focus-start": self.action_start,
            "focus-pause": self.action_pause,
            "focus-resume": self.action_resume,
            "focus-reset": self.action_reset,
            "focus-finish": self.action_finish,
        }
        action = actions.get(event.button.id or "")
        if action:
            action()

    def action_start(self) -> None:
        minutes = max(self.total_seconds // 60, 1)
        if self.mode == "focus":
            session = self.app.focus_service.start(self.selected_task_id, minutes)
            self.session_id = session.id
            self._refresh_history()
        self.running = True
        self.status("Timer dimulai.")

    def action_pause(self) -> None:
        self.running = False
        self.status("Timer dijeda.")

    def action_resume(self) -> None:
        if self.seconds_left <= 0:
            self.status("Timer sudah habis. Ulangi terlebih dahulu.")
            return
        self.running = True
        self.status("Timer dilanjutkan.")

    def action_reset(self) -> None:
        self.running = False
        if self.session_id:
            self.app.focus_service.cancel(self.session_id)
            self.session_id = None
            self._refresh_history()
        self.seconds_left = self.total_seconds
        self._update_display()
        self.status("Timer diulang.")

    def action_finish(self) -> None:
        if self.session_id:
            self.app.focus_service.complete(self.session_id)
            self.session_id = None
        self.running = False
        self._refresh_history()
        self.status("Sesi fokus disimpan.")
