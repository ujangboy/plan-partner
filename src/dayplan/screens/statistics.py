"""Aggregated productivity statistics."""

from __future__ import annotations

from rich import box
from rich.table import Table
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Static

from dayplan.screens.base import BaseScreen


class StatisticsScreen(BaseScreen):
    TITLE = "Statistics"

    def build_content(self) -> ComposeResult:
        with VerticalScroll() as container:
            with Vertical(classes="panel"):
                yield Static("RINGKASAN", classes="panel-title")
                yield Static(id="stats-summary")
            with Vertical(classes="panel"):
                yield Static("PENYELESAIAN 7 HARI TERAKHIR", classes="panel-title")
                yield Static(id="stats-weekly")
            with Vertical(classes="panel"):
                yield Static("PROGRES PROYEK", classes="panel-title")
                yield Static(id="stats-projects")
                with Horizontal(classes="button-row"):
                    yield Button("Refresh (R)", id="stats-refresh")
        return container

    def on_mount(self) -> None:
        super().on_mount()
        self.refresh_data()

    def refresh_data(self) -> None:
        stats = self.app.stats_service

        summary = Table(box=box.SIMPLE_HEAVY, show_header=True, expand=True)
        for heading in ("Aktif", "Selesai", "Terlambat", "Hari ini", "Proyek", "Persentase"):
            summary.add_column(heading, justify="center")
        data = stats.summary()
        summary.add_row(
            str(data.active), str(data.completed), str(data.overdue),
            str(data.due_today), str(data.active_projects), f"{data.completion_rate}%",
        )
        self.query_one("#stats-summary", Static).update(summary)

        weekly = Table(box=box.SIMPLE, show_header=True, expand=True)
        weekly.add_column("Tanggal", width=14)
        weekly.add_column("Selesai", width=10)
        weekly.add_column("Grafik")
        for day, count in stats.daily_completions(7):
            weekly.add_row(self.app.fmt_date(day), str(count), "█" * min(count, 40))
        self.query_one("#stats-weekly", Static).update(weekly)

        progress = Table(box=box.SIMPLE, show_header=True, expand=True)
        for heading in ("Proyek", "Aktif", "Selesai", "Persentase", "Grafik"):
            progress.add_column(heading, width=20 if heading == "Proyek" else None)
        for item in stats.project_progress():
            progress.add_row(
                item.name, str(item.active), str(item.done), f"{item.percent}%",
                "█" * (item.percent // 5),
            )
        if not stats.project_progress():
            progress.add_row("—", "", "", "", "Belum ada proyek.")
        self.query_one("#stats-projects", Static).update(progress)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "stats-refresh":
            self.refresh_data()
            self.status("Statistik diperbarui.")
