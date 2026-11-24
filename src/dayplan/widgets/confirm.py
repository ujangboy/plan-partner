"""Destructive-action confirmation dialog."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class ConfirmDialog(ModalScreen[bool]):
    BINDINGS = [
        Binding("escape", "cancel", "Batal"),
        Binding("enter", "confirm", "Hapus"),
    ]

    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        with Vertical(classes="confirm-dialog"):
            yield Static(self.message)
            with Horizontal(classes="button-row"):
                yield Button("Batal (Esc)", id="cancel", variant="primary")
                yield Button("Hapus", id="confirm", variant="error")

    def on_mount(self) -> None:
        self.query_one("#cancel", Button).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "confirm")

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)
