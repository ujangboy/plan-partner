"""Monthly, daily and agenda calendar views."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta

from rich import box
from rich.table import Table
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, DataTable, Input, Static, TabbedContent, TabPane

from dayplan.screens.base import BaseScreen
from dayplan.services.calendar_service import AgendaItem
from dayplan.utils.dates import add_months, parse_iso, today
from dayplan.utils.formatting import truncate
from dayplan.widgets.calendar_grid import CalendarGrid
from dayplan.widgets.confirm import ConfirmDialog
from dayplan.widgets.event_form import EventForm


class CalendarScreen(BaseScreen):
    TITLE = "Calendar"
    BINDINGS = [
        Binding("[", "previous_month", "Bulan sebelumnya", show=False),
        Binding("]", "next_month", "Bulan berikutnya", show=False),
        Binding("g", "go_today", "Hari ini", show=False),
        Binding("n", "new_event", "Kegiatan", show=False),
        Binding("e", "edit_event", "Edit", show=False),
        Binding("delete", "delete_event", "Hapus", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        current = today()
        self.year, self.month = current.year, current.month
        self.selected: date = current
        self.daily_items: list[AgendaItem] = []
        self.selected_event_id: str | None = None

    def build_content(self) -> ComposeResult:
        with Vertical() as container:
            with Horizontal(classes="MonthNav"):
                yield Button("◀", id="cal-prev")
                yield Static("", id="cal-month-label", classes="month-label")
                yield Button("▶", id="cal-next")
                yield Button("Hari ini", id="cal-today")
                yield Input(placeholder="YYYY-MM-DD", id="cal-date")
                yield Button("Pilih", id="cal-pick")
            with TabbedContent(initial="monthly"):
                with TabPane("Bulanan", id="monthly"):
                    yield CalendarGrid(id="cal-grid")
                    yield Static(id="cal-hint", classes="panel")
                with TabPane("Harian", id="daily"):
                    yield Static(id="daily-title", classes="panel-title")
                    yield DataTable(id="daily-table")
                    with Horizontal(classes="button-row"):
                        yield Button("Kegiatan Baru (N)", id="daily-new", variant="primary")
                        yield Button("Edit (E)", id="daily-edit")
                        yield Button("Hapus (Del)", id="daily-delete", variant="error")
                with TabPane("Agenda", id="agenda"):
                    yield Static(id="agenda-list")
        return container

    def on_mount(self) -> None:
        super().on_mount()
        table = self.query_one("#daily-table", DataTable)
        table.add_columns("Waktu", "Agenda", "Jenis")
        for column, width in zip(table.columns.values(), (14, 46, 14)):
            column.width = width
        self.refresh_data()

    def refresh_data(self) -> None:
        app = self.app
        self.query_one("#cal-month-label", Static).update(
            f"{self.month:02d}/{self.year}"
        )
        first = date(self.year, self.month, 1)
        last = add_months(first, 1) - timedelta(days=1)
        marks: dict[date, dict[str, int]] = defaultdict(
            lambda: {"events": 0, "tasks": 0, "overdue": 0}
        )
        now = app.task_service
        for task in now.list_tasks():
            if task.due_date:
                parsed = parse_iso(task.due_date)
                if parsed and first <= parsed.date() <= last:
                    marks[parsed.date()]["tasks"] += 1
                    if now.is_overdue(task):
                        marks[parsed.date()]["overdue"] += 1
            if task.scheduled_start:
                parsed = parse_iso(task.scheduled_start)
                if parsed and first <= parsed.date() <= last:
                    marks[parsed.date()]["tasks"] += 1
        for event in app.calendar_service.events_between(first, last):
            parsed = parse_iso(event.start_at)
            if parsed:
                marks[parsed.date()]["events"] += 1

        self.query_one("#cal-grid", CalendarGrid).set_month(
            self.year,
            self.month,
            dict(marks),
            self.selected if self.selected.month == self.month else None,
            today(app.config.timezone),
        )
        self.query_one("#cal-hint", Static).update(
            f"Dipilih: {self.selected.isoformat()} • [ / ] ganti bulan • G hari ini • N kegiatan baru"
        )
        self._refresh_daily()
        self._refresh_agenda()

    def _refresh_daily(self) -> None:
        self.query_one("#daily-title", Static).update(
            f"AGENDA {self.selected.strftime('%A, %d %B %Y')}"
        )
        self.daily_items = self.app.calendar_service.agenda_for(self.selected)
        table = self.query_one("#daily-table", DataTable)
        table.clear(columns=False)
        for item in self.daily_items:
            table.add_row(self.app.fmt_time(item.start), truncate(item.label, 44), item.kind)
        if not self.daily_items:
            table.add_row("—", "Tidak ada agenda pada tanggal ini.", "")

    def _refresh_agenda(self) -> None:
        table = Table(box=box.SIMPLE, show_header=True, expand=True)
        for heading in ("Waktu", "Agenda", "Jenis"):
            table.add_column(heading, width=18 if heading == "Waktu" else None)
        start = self.selected
        end = start + timedelta(days=7)
        rows: list[tuple[str, str, str]] = []
        for event in self.app.calendar_service.events_between(start, end):
            rows.append((self.app.fmt_time(event.start_at), event.title, "event"))
        for task in self.app.task_service.list_tasks():
            if task.due_date and start.isoformat() <= task.due_date <= end.isoformat():
                rows.append((task.due_date, task.title, "deadline"))
        for row in sorted(rows, key=lambda item: item[0]):
            table.add_row(row[0], truncate(row[1], 48), row[2])
        if not rows:
            table.add_row("—", "Tidak ada agenda mendatang.", "")
        self.query_one("#agenda-list", Static).update(table)

    def _set_selected(self, day: date) -> None:
        self.selected = day
        self.year, self.month = day.year, day.month
        self.refresh_data()
        self.query_one(TabbedContent).active = "daily"

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.data_table.id != "daily-table":
            return
        if event.cursor_row < len(self.daily_items):
            item = self.daily_items[event.cursor_row]
            self.selected_event_id = item.ref_id if item.kind == "event" else None

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "cal-date":
            self.action_pick_date()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        actions = {
            "cal-prev": self.action_previous_month,
            "cal-next": self.action_next_month,
            "cal-today": self.action_go_today,
            "cal-pick": self.action_pick_date,
            "daily-new": self.action_new_event,
            "daily-edit": self.action_edit_event,
            "daily-delete": self.action_delete_event,
        }
        action = actions.get(event.button.id or "")
        if action:
            action()

    def action_previous_month(self) -> None:
        first = add_months(date(self.year, self.month, 1), -1)
        self.year, self.month = first.year, first.month
        self.refresh_data()

    def action_next_month(self) -> None:
        first = add_months(date(self.year, self.month, 1), 1)
        self.year, self.month = first.year, first.month
        self.refresh_data()

    def action_go_today(self) -> None:
        self._set_selected(today(self.app.config.timezone))

    def action_pick_date(self) -> None:
        value = self.query_one("#cal-date", Input).value.strip()
        try:
            day = date.fromisoformat(value)
        except ValueError:
            self.status("Tanggal harus berformat YYYY-MM-DD.")
            return
        self._set_selected(day)

    def action_new_event(self) -> None:
        if self.is_typing():
            return
        self.app.push_screen(
            EventForm(default_date=self.selected.isoformat()), self._after_form
        )

    def action_edit_event(self) -> None:
        event = self.app.calendar_service.get_event(self.selected_event_id or "")
        if event is None:
            self.status("Pilih kegiatan kalender terlebih dahulu.")
            return
        self.app.push_screen(EventForm(event), self._after_form)

    def _after_form(self, values: dict[str, object] | None) -> None:
        if values is None:
            return
        try:
            selected = self.app.calendar_service.get_event(self.selected_event_id or "")
            if selected:
                self.app.calendar_service.update_event(selected.id, **values)
                self.status("Kegiatan diperbarui.")
            else:
                self.app.calendar_service.create_event(**values)
                self.status("Kegiatan dibuat.")
        except (ValueError, LookupError) as error:
            self.status(str(error))
            return
        self.selected_event_id = None
        self.refresh_data()

    def action_delete_event(self) -> None:
        event = self.app.calendar_service.get_event(self.selected_event_id or "")
        if event is None:
            self.status("Pilih kegiatan kalender terlebih dahulu.")
            return
        self.app.push_screen(
            ConfirmDialog(f"Hapus kegiatan '{event.title}'?"),
            lambda confirmed: self._confirm_delete(confirmed, event.id),
        )

    def _confirm_delete(self, confirmed: bool | None, event_id: str) -> None:
        if not confirmed:
            return
        self.app.calendar_service.delete_event(event_id)
        self.selected_event_id = None
        self.status("Kegiatan dihapus.")
        self.refresh_data()
