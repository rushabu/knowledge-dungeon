import json
import os
import random
import re
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
    lane INTEGER NOT NULL DEFAULT 0,
    source TEXT                      -- the chapter(s) of the notes this room covers; NULL = all notes
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
    shown_mastery REAL NOT NULL DEFAULT 0,  -- last mastery shown to the player
    boss_hp INTEGER NOT NULL,
    boss_max INTEGER NOT NULL,
    player_hp INTEGER NOT NULL,
    question_ids TEXT NOT NULL,      -- JSON list
    idx INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL,            -- active | won | lost
    dm_done INTEGER NOT NULL DEFAULT 0,
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
        cols = {r["name"] for r in db.execute("PRAGMA table_info(rooms)")}
        if "source" not in cols:  # databases made before rooms knew their chapter
            db.execute("ALTER TABLE rooms ADD COLUMN source TEXT")
        if db.execute("PRAGMA user_version").fetchone()[0] < 1:
            # questions saved before options were shuffled: most had the answer at B
            for q in db.execute("SELECT id, options, answer FROM questions").fetchall():
                options, answer = shuffle_options(json.loads(q["options"]), q["answer"])
                db.execute("UPDATE questions SET options=?, answer=? WHERE id=?", (json.dumps(options), answer, q["id"]))
            db.execute("PRAGMA user_version = 1")


# "None of them" / "All of the above" read wrongly anywhere but last
_PIN_LAST = re.compile(r"\b(none|all) of (them|these|the above)\b|\babove\b", re.I)


def shuffle_options(options: list[str], answer: int) -> tuple[list[str], int]:
    """Shuffle the options and return (options, new answer index).

    Models put the correct answer at B far more often than chance, and ignore prompts asking
    them not to, so where the answer sits must be decided here, not by the model."""
    free = [i for i, o in enumerate(options) if not _PIN_LAST.search(o)]
    random.shuffle(free)
    order = free + [i for i, o in enumerate(options) if _PIN_LAST.search(o)]
    return [options[i] for i in order], order.index(answer)


def insert_question(conn, room_id: int, q: dict, difficulty: str):
    options, answer = shuffle_options(q["options"], q["answer"])
    conn.execute(
        "INSERT INTO questions (room_id, prompt, options, answer, explanation, difficulty) VALUES (?,?,?,?,?,?)",
        (room_id, q["prompt"], json.dumps(options), answer, q.get("explanation", ""), difficulty),
    )


@contextmanager
def connect():
    conn = sqlite3.connect(DB_PATH, timeout=15)  # a background thread also writes
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
