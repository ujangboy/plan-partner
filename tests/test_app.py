from __future__ import annotations

import pytest
from textual.widgets import Input, Select, Static

from dayplan.app import DayPlanApp


@pytest.fixture
def app(tmp_path):
    return DayPlanApp(tmp_path / "dayplan.db")


async def test_app_boots_on_dashboard(app):
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        assert app.screen.name == "dashboard"
        assert app.screen.query_one("#stats", Static) is not None
        assert app.screen.query_one("#today-agenda", Static) is not None


async def test_keyboard_navigation(app):
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        for key, expected in [
            ("t", "tasks"),
            ("c", "calendar"),
            ("p", "projects"),
            ("f", "focus"),
            ("s", "settings"),
            ("?", "help"),
            ("d", "dashboard"),
        ]:
            await pilot.press(key)
            await pilot.pause()
            assert app.screen.name == expected, key


async def test_quick_add_from_dashboard(app):
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        await pilot.press("ctrl+n")
        await pilot.pause()
        app.screen.query_one("#f-title", Input).value = "Tugas dari UI"
        await pilot.press("ctrl+s")
        await pilot.pause()

        titles = [task.title for task in app.task_service.list_tasks()]
        assert "Tugas dari UI" in titles


async def test_letter_key_does_not_navigate_while_typing(app):
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("t")
        await pilot.pause()
        search = app.screen.query_one("#search", Input)
        search.focus()
        await pilot.press("c")
        await pilot.pause()

        assert app.screen.name == "tasks"
        assert search.value == "c"


async def test_calendar_month_navigation(app):
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("c")
        await pilot.pause()
        label = app.screen.query_one("#cal-month-label", Static)
        before = str(label.content)
        await pilot.press("]")
        await pilot.pause()
        assert str(label.content) != before
        await pilot.press("g")
        await pilot.pause()
        assert str(label.content) == before


async def test_settings_theme_persists(app):
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("s")
        await pilot.pause()
        app.screen.query_one("#set-theme", Select).value = "light"
        await pilot.press("ctrl+s")
        await pilot.pause()

        assert app.config.get("theme") == "light"
        assert app.theme == "textual-light"


async def test_all_screens_render_at_small_terminal(app):
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()
        for name in ["dashboard", "tasks", "calendar", "projects", "focus", "statistics", "settings", "help"]:
            app.switch_screen(name)
            await pilot.pause()
            assert app.screen.name == name
