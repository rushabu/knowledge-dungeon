import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(os.getenv("DB_PATH", Path(__file__).resolve().parents[1] / "dungeon.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS dungeons (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    notes TEXT NOT NULL,
    xp INTEGER NOT NULL DEFAULT 0,
    is_demo INTEGER NOT NULL DEFAULT 0,
    created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY,
    dungeon_id INTEGER NOT NULL REFERENCES dungeons(id),
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    keywords TEXT NOT NULL,          -- JSON list
    prereqs TEXT NOT NULL,           -- JSON list of room ids
    boss_name TEXT NOT NULL,
    boss_flavor TEXT NOT NULL,
    status TEXT NOT NULL,            -- locked | open | cleared | respawned
    clears INTEGER NOT NULL DEFAULT 0,
    cleared_at REAL,
    depth INTEGER NOT NULL DEFAULT 0,
    lane INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY,
    room_id INTEGER NOT NULL REFERENCES rooms(id),
    prompt TEXT NOT NULL,
    options TEXT NOT NULL,           -- JSON list of 4 strings
    answer INTEGER NOT NULL,
    explanation TEXT NOT NULL,
    difficulty TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS fights (
    id INTEGER PRIMARY KEY,
    room_id INTEGER NOT NULL REFERENCES rooms(id),
    difficulty TEXT NOT NULL,
    start_mastery REAL NOT NULL DEFAULT 0,
    boss_hp INTEGER NOT NULL,
    boss_max INTEGER NOT NULL,
    player_hp INTEGER NOT NULL,
    question_ids TEXT NOT NULL,      -- JSON list
    idx INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL,            -- active | won | lost
    started_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY,
    dungeon_id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    correct INTEGER NOT NULL,
    ts REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS dm_log (
    id INTEGER PRIMARY KEY,
    dungeon_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    actions TEXT NOT NULL,           -- JSON list of tool calls the DM made
    recommended_room INTEGER,
    ts REAL NOT NULL
);
"""

JSON_COLS = {"keywords", "prereqs", "options", "question_ids", "actions"}


def init():
    with connect() as db:
        db.executescript(SCHEMA)


@contextmanager
def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def as_dict(row) -> dict | None:
    if row is None:
        return None
    d = dict(row)
    for k in JSON_COLS & d.keys():
        d[k] = json.loads(d[k])
    return d


def all_dicts(rows) -> list[dict]:
    return [as_dict(r) for r in rows]
