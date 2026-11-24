from __future__ import annotations

from datetime import date

import pytest
from textual.widgets import Button, Input

from dayplan.app import DayPlanApp
from dayplan.widgets.task_table import TaskTable


@pytest.fixture
def app(tmp_path):
    return DayPlanApp(tmp_path / "dayplan.db")


async def test_delete_task_requires_confirmation(app):
    task = app.task_service.create("Hapus via UI")
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("t")
        await pilot.pause()
        table = app.screen.query_one("#task-table", TaskTable)
        table.focus()
        await pilot.press("delete")
        await pilot.pause()
        assert app.task_service.get(task.id) is not None

        await pilot.click("#confirm")
        await pilot.pause()
        assert app.task_service.get(task.id) is None


async def test_create_calendar_event_from_ui(app):
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("c")
        await pilot.pause()
        await pilot.press("n")
        await pilot.pause()
        app.screen.query_one("#e-title", Input).value = "Kuliah UI"
        app.screen.query_one("#e-start", Input).value = "2026-11-24T08:00"
        app.screen.query_one("#e-end", Input).value = "2026-11-24T10:00"
        await pilot.press("ctrl+s")
        await pilot.pause()

        events = [
            e.title
            for e in app.calendar_service.events_between(
                date(2026, 11, 24), date(2026, 11, 24)
            )
        ]
        assert "Kuliah UI" in events


async def test_create_project_from_ui(app):
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("p")
        await pilot.pause()
        await pilot.press("ctrl+n")
        await pilot.pause()
        app.screen.query_one("#p-name", Input).value = "Kuliah"
        await pilot.press("ctrl+s")
        await pilot.pause()

        assert [p.name for p in app.project_service.list_projects()] == ["Kuliah"]


async def test_create_event_from_dashboard(app):
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.click("#dash-new-event")
        await pilot.pause()
        app.screen.query_one("#e-title", Input).value = "Rapat"
        await pilot.press("ctrl+s")
        await pilot.pause()

        assert any(e.title == "Rapat" for e in app.calendar_service.upcoming_events())


async def test_invalid_timezone_is_rejected(app):
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("s")
        await pilot.pause()
        app.screen.query_one("#set-timezone", Input).value = "Bukan/Zona"
        await pilot.press("ctrl+s")
        await pilot.pause()

        assert app.config.get("timezone") == ""


async def test_focus_timer_starts_and_saves_session(app):
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("f")
        await pilot.pause()
        await pilot.click("#focus-start")
        await pilot.pause()

        assert len(app.focus_service.history()) == 1
        assert app.focus_service.history()[0].status == "running"

        await pilot.click("#focus-finish")
        await pilot.pause()
        assert app.focus_service.history()[0].status == "completed"
