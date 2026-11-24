"""Shared screen chrome, navigation bindings and typing guards."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Select, Static, TextArea

from dayplan.widgets.sidebar import Sidebar
from dayplan.widgets.status_bar import StatusBar

_TYPING_WIDGETS = (Input, TextArea, Select)


class BaseScreen(Screen):
    TITLE = "DayPlan"

    def __init__(self, **kwargs: object) -> None:
        name = type(self).__name__.removesuffix("Screen").lower()
        super().__init__(name=name, **kwargs)

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("?", "help", "Help"),
        Binding("d", "dashboard", "Dashboard", show=False),
        Binding("t", "tasks", "Tasks", show=False),
        Binding("c", "calendar", "Calendar", show=False),
        Binding("p", "projects", "Projects", show=False),
        Binding("f", "focus", "Focus", show=False),
        Binding("s", "settings", "Settings", show=False),
        Binding("escape", "back", "Back", show=False),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="shell"):
            yield Sidebar()
            with Vertical(id="main"):
                yield Static(self.TITLE, classes="screen-title")
                yield from self.build_content()
        yield StatusBar()
        yield Footer()

    def build_content(self):
        """Subclasses return the main content widget."""
        raise NotImplementedError

    def on_mount(self) -> None:
        self.query_one(Sidebar).set_active(self.name or "")

    def is_typing(self) -> bool:
        return isinstance(self.focused, _TYPING_WIDGETS)

    def status(self, message: str) -> None:
        self.query_one(StatusBar).set_message(message)
        self.notify(message, timeout=3)

    def action_quit(self) -> None:
        if not self.is_typing():
            self.app.action_quit()

    def action_help(self) -> None:
        if not self.is_typing():
            self.app.switch_screen("help")

    def action_dashboard(self) -> None:
        if not self.is_typing():
            self.app.switch_screen("dashboard")

    def action_tasks(self) -> None:
        if not self.is_typing():
            self.app.switch_screen("tasks")

    def action_calendar(self) -> None:
        if not self.is_typing():
            self.app.switch_screen("calendar")

    def action_projects(self) -> None:
        if not self.is_typing():
            self.app.switch_screen("projects")

    def action_focus(self) -> None:
        if not self.is_typing():
            self.app.switch_screen("focus")

    def action_settings(self) -> None:
        if not self.is_typing():
            self.app.switch_screen("settings")

    def action_back(self) -> None:
        if not self.is_typing():
            self.app.switch_screen("dashboard")
