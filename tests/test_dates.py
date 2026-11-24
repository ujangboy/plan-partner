from __future__ import annotations

from datetime import date, datetime

from dayplan.utils.dates import is_overdue, month_grid, parse_iso, week_bounds


def test_month_grid_handles_leap_february():
    grid = month_grid(2028, 2)

    flat = [day for week in grid for day in week if day is not None]
    assert min(flat) == date(2028, 2, 1)
    assert max(flat) == date(2028, 2, 29)
    assert all(len(week) == 7 for week in grid)


def test_month_grid_pads_with_none():
    grid = month_grid(2026, 11)
    assert all(day is None for day in grid[0][:6])
    assert grid[0][6] == date(2026, 11, 1)


def test_parse_iso_accepts_date_and_datetime():
    assert parse_iso("2026-11-24") == datetime(2026, 11, 24)
    assert parse_iso("2026-11-24T19:00:00") == datetime(2026, 11, 24, 19)


def test_is_overdue_ignores_completed_and_future():
    now = datetime(2026, 11, 24, 12)

    assert is_overdue("2026-11-23", now, completed_at=None)
    assert not is_overdue("2026-11-25", now, completed_at=None)
    assert not is_overdue("2026-11-23", now, completed_at="2026-11-23T09:00:00")


def test_week_bounds_include_full_monday_to_sunday():
    start, end = week_bounds(date(2026, 11, 25))
    assert start == date(2026, 11, 23)
    assert end == date(2026, 11, 29)
