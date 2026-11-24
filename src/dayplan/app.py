"""DayPlan TUI application entry point and service container."""

from __future__ import annotations

from datetime import date, datetime, time
from pathlib import Path

from textual.app import App

from dayplan.config import Config
from dayplan.database.connection import Database
from dayplan.screens.calendar import CalendarScreen
from dayplan.screens.dashboard import DashboardScreen
from dayplan.screens.focus import FocusScreen
from dayplan.screens.help import HelpScreen
from dayplan.screens.projects import ProjectsScreen
from dayplan.screens.settings import SettingsScreen
from dayplan.screens.statistics import StatisticsScreen
from dayplan.screens.tasks import TasksScreen
from dayplan.services.backup_service import BackupService
from dayplan.services.calendar_service import CalendarService
from dayplan.services.focus_service import FocusService
from dayplan.services.project_service import ProjectService
from dayplan.services.statistics_service import StatisticsService
from dayplan.services.task_service import TaskService
from dayplan.utils.dates import format_date, format_time


class DayPlanApp(App):
    TITLE = "DayPlan TUI"
    SUB_TITLE = "Offline-first productivity"
    CSS_PATH = "styles/app.tcss"

    SCREENS = {
        "dashboard": DashboardScreen,
        "tasks": TasksScreen,
        "calendar": CalendarScreen,
        "projects": ProjectsScreen,
        "focus": FocusScreen,
        "statistics": StatisticsScreen,
        "settings": SettingsScreen,
        "help": HelpScreen,
    }

    def __init__(self, db_path: Path | str | None = None) -> None:
        super().__init__()
        self._db = Database(db_path)
        self._config = Config(self._db)
        self._task_service = TaskService(self._db, self._config)
        self._project_service = ProjectService(self._db, self._config)
        self._calendar_service = CalendarService(self._db, self._config)
        self._statistics_service = StatisticsService(self._db, self._config)
        self._focus_service = FocusService(self._db, self._config)
        self._backup_service = BackupService(self._db)
        self.theme = (
            "textual-dark" if self._config.get("theme") == "dark" else "textual-light"
        )

    @property
    def db(self) -> Database:
        return self._db

    @property
    def config(self) -> Config:
        return self._config

    @property
    def task_service(self) -> TaskService:
        return self._task_service

    @property
    def project_service(self) -> ProjectService:
        return self._project_service

    @property
    def calendar_service(self) -> CalendarService:
        return self._calendar_service

    @property
    def statistics_service(self) -> StatisticsService:
        return self._statistics_service

    @property
    def stats_service(self) -> StatisticsService:
        return self._statistics_service

    @property
    def focus_service(self) -> FocusService:
        return self._focus_service

    @property
    def backup_service(self) -> BackupService:
        return self._backup_service

    def fmt_date(self, value: date | datetime | None) -> str:
        return format_date(value, self._config.get("date_format"))

    def fmt_time(self, value: datetime | time | str | None) -> str:
        return format_time(value, self._config.get("time_format"))

    def on_mount(self) -> None:
        self.push_screen("dashboard")


def main() -> None:
    DayPlanApp().run()


if __name__ == "__main__":
    main()
