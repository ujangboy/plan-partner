"""Input validation shared by forms and services."""

from __future__ import annotations

import re
from datetime import date, datetime

from dayplan.utils.dates import parse_iso

_TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
_STATUSES = {"inbox", "todo", "in_progress", "waiting", "done", "archived"}
_PRIORITIES = {"urgent", "high", "medium", "low"}


def validate_title(title: str) -> str:
    cleaned = title.strip()
    if not cleaned:
        raise ValueError("Judul tugas tidak boleh kosong.")
    return cleaned


def validate_date(value: str | None, field: str = "Tanggal") -> str | None:
    if not value or not value.strip():
        return None
    parsed = parse_iso(value.strip())
    if parsed is None or parsed.time().hour or parsed.time().minute:
        raise ValueError(f"{field} harus berformat YYYY-MM-DD.")
    return parsed.date().isoformat()


def validate_time(value: str | None) -> str | None:
    if not value or not value.strip():
        return None
    cleaned = value.strip()
    if not _TIME_RE.match(cleaned):
        raise ValueError("Jam harus berformat HH:MM (00:00–23:59).")
    return cleaned


def validate_datetime(value: str | None, field: str = "Waktu") -> str | None:
    if not value or not value.strip():
        return None
    parsed = parse_iso(value)
    if parsed is None:
        raise ValueError(f"{field} tidak valid.")
    return parsed.isoformat(timespec="minutes")


def validate_minutes(value: str | int | None) -> int | None:
    if value is None or value == "":
        return None
    minutes = int(value)
    if minutes < 0:
        raise ValueError("Durasi tidak boleh negatif.")
    return minutes


def validate_status(value: str) -> str:
    if value not in _STATUSES:
        raise ValueError(f"Status '{value}' tidak dikenal.")
    return value


def validate_priority(value: str) -> str:
    if value not in _PRIORITIES:
        raise ValueError(f"Prioritas '{value}' tidak dikenal.")
    return value


def validate_datetime_order(start: str | None, end: str | None) -> None:
    if not start or not end:
        return
    first, last = parse_iso(start), parse_iso(end)
    if first and last and last <= first:
        raise ValueError("Waktu selesai harus sesudah waktu mulai.")
