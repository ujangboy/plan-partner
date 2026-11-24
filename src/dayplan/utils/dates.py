"""Date/time helpers. All stored values are ISO 8601 strings."""

from __future__ import annotations

from calendar import Calendar
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

_DATE_FMT = "%Y-%m-%d"
_TIME_FMT = "%H:%M"


def parse_iso(value: str | None) -> datetime | None:
    """Parse an ISO 8601 date or datetime into a datetime, or ``None``."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None


def iso_now() -> str:
    """Return the current UTC instant as an ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def local_now(tz_name: str | None = None) -> datetime:
    """Return the current time in the configured timezone (naive)."""
    tz = ZoneInfo(tz_name) if tz_name else datetime.now().astimezone().tzinfo
    return datetime.now(tz).replace(tzinfo=None)


def today(tz_name: str | None = None) -> date:
    """Return today's date in the configured timezone."""
    return local_now(tz_name).date()


def format_date(value: date | datetime | None, pattern: str = _DATE_FMT) -> str:
    if value is None:
        return "—"
    return value.strftime(pattern)


def format_time(
    value: datetime | time | str | None, pattern: str = _TIME_FMT
) -> str:
    if value is None:
        return "—"
    if isinstance(value, str):
        parsed = parse_iso(value)
        return parsed.strftime(pattern) if parsed else value
    return value.strftime(pattern)


def combine_date_time(day: date, clock: str | None) -> str | None:
    """Combine a date and an ``HH:MM`` string into an ISO datetime string."""
    if not clock:
        return None
    hour, minute = (int(part) for part in clock.split(":")[:2])
    return datetime.combine(day, time(hour, minute)).isoformat(timespec="minutes")


def month_grid(year: int, month: int) -> list[list[date | None]]:
    """Return a Monday-first 6-week calendar grid for the given month."""
    weeks: list[list[date | None]] = []
    for week in Calendar(firstweekday=0).monthdayscalendar(year, month):
        weeks.append([date(year, month, day) if day else None for day in week])
    return weeks


def add_months(day: date, count: int) -> date:
    """Shift a date by whole months, clamping the day to the target month."""
    month_index = day.month - 1 + count
    year = day.year + month_index // 12
    month = month_index % 12 + 1
    from calendar import monthrange

    return date(year, month, min(day.day, monthrange(year, month)[1]))


def week_bounds(day: date) -> tuple[date, date]:
    """Return Monday and Sunday of the week containing ``day``."""
    start = day - timedelta(days=day.weekday())
    return start, start + timedelta(days=6)


def is_overdue(
    due_date: str | None, now: datetime, completed_at: str | None = None
) -> bool:
    """A task is overdue when it is incomplete and its deadline has passed."""
    if completed_at or not due_date:
        return False
    deadline = parse_iso(due_date)
    if deadline is None:
        return False
    # A date-only deadline lasts the whole day; only an explicit time can
    # make it overdue before midnight.
    if "T" in due_date:
        return deadline < now
    return deadline.date() < now.date()
