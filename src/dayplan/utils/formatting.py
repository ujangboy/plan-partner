"""Human-readable symbols and labels used across the TUI."""

from __future__ import annotations

STATUS_LABELS = {
    "inbox": "Inbox",
    "todo": "Todo",
    "in_progress": "In Progress",
    "waiting": "Waiting",
    "done": "Done",
    "archived": "Archived",
}

STATUS_SYMBOLS = {
    "inbox": "·",
    "todo": "[ ]",
    "in_progress": "[~]",
    "waiting": "[…]",
    "done": "[x]",
    "archived": "[-]",
}

PRIORITY_LABELS = {
    "urgent": "Urgent",
    "high": "High",
    "medium": "Medium",
    "low": "Low",
}

PRIORITY_SYMBOLS = {"urgent": "!!!", "high": "!!", "medium": "!", "low": "-"}


def status_badge(status: str) -> str:
    label = STATUS_LABELS.get(status, status)
    return f"{STATUS_SYMBOLS.get(status, '?')} {label}"


def priority_badge(priority: str) -> str:
    label = PRIORITY_LABELS.get(priority, priority)
    return f"{PRIORITY_SYMBOLS.get(priority, '?')} {label}"


def format_duration(minutes: int | None) -> str:
    if not minutes:
        return "—"
    hours, remainder = divmod(minutes, 60)
    if hours and remainder:
        return f"{hours}j {remainder}m"
    if hours:
        return f"{hours}j"
    return f"{remainder}m"


def truncate(text: str, width: int) -> str:
    """Cut text to ``width`` cells, using an ellipsis when truncated."""
    if width <= 0:
        return ""
    if len(text) <= width:
        return text
    if width == 1:
        return "…"
    return text[: width - 1] + "…"
