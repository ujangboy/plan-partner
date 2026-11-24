"""Canonical SQLite schema for DayPlan.

All timestamps are ISO 8601. Date-only values use ``YYYY-MM-DD`` and
time-of-day values use ``HH:MM`` in the configured local timezone.
"""

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS projects (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    color       TEXT NOT NULL DEFAULT '',
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    id                TEXT PRIMARY KEY,
    title             TEXT NOT NULL,
    description       TEXT NOT NULL DEFAULT '',
    status            TEXT NOT NULL DEFAULT 'inbox',
    priority          TEXT NOT NULL DEFAULT 'medium',
    due_date          TEXT,
    due_time          TEXT,
    scheduled_start   TEXT,
    scheduled_end     TEXT,
    estimated_minutes INTEGER,
    project_id        TEXT REFERENCES projects(id) ON DELETE SET NULL,
    created_at        TEXT NOT NULL,
    updated_at        TEXT NOT NULL,
    completed_at      TEXT
);

CREATE TABLE IF NOT EXISTS tags (
    id   TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS task_tags (
    task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id  TEXT NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, tag_id)
);

CREATE TABLE IF NOT EXISTS calendar_events (
    id          TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    start_at    TEXT NOT NULL,
    end_at      TEXT NOT NULL,
    is_all_day  INTEGER NOT NULL DEFAULT 0,
    location    TEXT NOT NULL DEFAULT '',
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS focus_sessions (
    id               TEXT PRIMARY KEY,
    task_id          TEXT REFERENCES tasks(id) ON DELETE SET NULL,
    duration_minutes INTEGER NOT NULL,
    started_at       TEXT NOT NULL,
    completed_at     TEXT,
    status           TEXT NOT NULL DEFAULT 'planned'
);

CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_events_start_at ON calendar_events(start_at);
CREATE INDEX IF NOT EXISTS idx_focus_started_at ON focus_sessions(started_at);
"""
