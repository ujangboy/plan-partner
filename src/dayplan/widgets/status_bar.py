"""One-line status/message bar."""

from __future__ import annotations

from textual.reactive import reactive
from textual.widgets import Static


class StatusBar(Static):
    message: reactive[str] = reactive("Ready • Ctrl+N new task • ? help")

    def watch_message(self, value: str) -> None:
        self.update(value)

    def set_message(self, value: str) -> None:
        self.message = value
