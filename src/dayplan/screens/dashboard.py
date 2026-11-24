"""Landing screen: the productivity snapshot."""

from __future__ import annotations

from rich import box
from rich.table import Table
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Static

from dayplan.screens.base import BaseScreen
from dayplan.utils.dates import today
from dayplan.utils.formatting import priority_badge, truncate


class DashboardScreen(BaseScreen):
    TITLE = "Dashboard"
    BINDINGS = [Binding("ctrl+n", "new_task", "New Task")]

    def build_content(self) -> ComposeResult:
        with VerticalScroll() as container:
            yield Static(id="stats", classes="panel")
            with Vertical(classes="panel"):
                yield Static("AGENDA HARI INI", classes="panel-title")
                yield Static(id="today-agenda")
                with Horizontal(classes="button-row"):
                    yield Button("Tambah Kegiatan", id="dash-new-event")
            with Vertical(classes="panel"):
                yield Static("TUGAS MENDATANG", classes="panel-title")
                yield Static(id="upcoming")
            with Vertical(classes="panel"):
                yield Static("PROGRES PROYEK", classes="panel-title")
                yield Static(id="progress")
        return container

    def on_mount(self) -> None:
        super().on_mount()
        self.refresh_data()

    def refresh_data(self) -> None:
        app = self.app
        summary = app.stats_service.summary()
        stats = Table(box=box.SIMPLE_HEAVY, show_header=True, expand=True)
        for heading in ("Aktif", "Selesai", "Terlambat", "Hari Ini", "Proyek", "Persentase"):
            stats.add_column(heading, justify="center")
        stats.add_row(
            str(summary.active),
            str(summary.completed),
            str(summary.overdue),
            str(summary.due_today),
            str(summary.active_projects),
            f"{summary.completion_rate}%",
        )
        self.query_one("#stats", Static).update(stats)

        day = today(app.config.timezone)
        agenda = Table(box=box.SIMPLE, show_header=True, expand=True)
        for heading in ("Waktu", "Agenda", "Jenis"):
            agenda.add_column(heading, width=14 if heading == "Waktu" else None)
        items = app.calendar_service.agenda_for(day)
        for item in items:
            agenda.add_row(
                app.fmt_time(item.start),
                truncate(item.label, 48),
                item.kind,
            )
        if not items:
            agenda.add_row("—", "Tidak ada agenda hari ini.", "")
        self.query_one("#today-agenda", Static).update(agenda)

        upcoming = Table(box=box.SIMPLE, show_header=True, expand=True)
        for heading in ("Deadline", "Prioritas", "Tugas"):
            upcoming.add_column(heading, width=12 if heading != "Tugas" else None)
        tasks = app.stats_service.upcoming_tasks(7)
        for task in tasks:
            upcoming.add_row(
                task.due_date or "—",
                priority_badge(task.priority),
                truncate(task.title, 46),
            )
        if not tasks:
            upcoming.add_row("—", "", "Tidak ada deadline 7 hari ke depan.")
        self.query_one("#upcoming", Static).update(upcoming)

        progress = Table(box=box.SIMPLE, show_header=True, expand=True)
        for heading in ("Proyek", "Aktif", "Selesai", "Progres"):
            progress.add_column(heading, width=20 if heading == "Proyek" else None)
        for item in app.stats_service.project_progress():
            progress.add_row(
                truncate(item.name, 18),
                str(item.active),
                str(item.done),
                f"{item.percent}%",
            )
        if not app.stats_service.project_progress():
            progress.add_row("—", "", "", "Belum ada proyek.")
        self.query_one("#progress", Static).update(progress)

    def action_new_task(self) -> None:
        from dayplan.widgets.task_form import TaskForm

        self.app.push_screen(TaskForm(), lambda values: self._after_task(values))

    def _after_task(self, values: dict[str, object] | None) -> None:
        if values is None:
            return
        try:
            self.app.task_service.create(**values)
        except ValueError as error:
            self.status(str(error))
            return
        self.status("Tugas dibuat.")
        self.refresh_data()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "dash-new-event":
            from dayplan.widgets.event_form import EventForm

            self.app.push_screen(
                EventForm(default_date=today(self.app.config.timezone).isoformat()),
                self._after_event,
            )

    def _after_event(self, values: dict[str, object] | None) -> None:
        if values is None:
            return
        try:
            self.app.calendar_service.create_event(**values)
        except (ValueError, LookupError) as error:
            self.status(str(error))
            return
        self.status("Kegiatan dibuat.")
        self.refresh_data()
