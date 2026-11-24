"""Persistent navigation panel."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import Button, Static

NAV_ITEMS = [
    ("dashboard", "Dashboard", "D"),
    ("tasks", "Tasks", "T"),
    ("calendar", "Calendar", "C"),
    ("projects", "Projects", "P"),
    ("focus", "Focus Mode", "F"),
    ("statistics", "Statistics", ""),
    ("settings", "Settings", "S"),
    ("help", "Help", "?"),
]


class Sidebar(Static):
    def compose(self) -> ComposeResult:
        yield Static(" DAYPLAN TUI", classes="nav-title")
        for name, label, key in NAV_ITEMS:
            caption = f"{label}  [{key}]" if key else label
            yield Button(caption, id=f"nav-{name}", classes="nav-item")

    def set_active(self, name: str) -> None:
        for button in self.query(Button):
            button.set_class(button.id == f"nav-{name}", "-active")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id and event.button.id.startswith("nav-"):
            self.app.switch_screen(event.button.id.removeprefix("nav-"))
