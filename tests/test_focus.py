from __future__ import annotations

import pytest

from dayplan.database.connection import Database
from dayplan.services.focus_service import FocusService
from dayplan.services.task_service import TaskService


@pytest.fixture
def services(tmp_path):
    db = Database(tmp_path / "dayplan.db")
    return FocusService(db), TaskService(db)


def test_start_and_complete_session(services):
    focus, tasks = services
    task = tasks.create("Belajar Python")
    session = focus.start(task_id=task.id, minutes=25)

    assert session.status == "running"
    assert session.started_at
    assert focus.get(session.id).task_id == task.id

    done = focus.complete(session.id)
    assert done.status == "completed" and done.completed_at


def test_history_is_newest_first(services):
    focus, _ = services
    first = focus.start(minutes=25)
    focus.complete(first.id)
    second = focus.start(minutes=5)

    history = focus.history()
    assert [session.id for session in history] == [second.id, first.id]


def test_start_with_unknown_task_is_rejected(services):
    focus, _ = services
    with pytest.raises(LookupError, match="Tugas"):
        focus.start(task_id="tidak-ada", minutes=25)


def test_cancel_session(services):
    focus, _ = services
    session = focus.start(minutes=25)
    assert focus.cancel(session.id).status == "cancelled"
