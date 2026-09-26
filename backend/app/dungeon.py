"""Building dungeons from notes, and the rules for how rooms lock and unlock."""
import json
import time
from pathlib import Path

from . import db, llm, tracer

DEMO_DIR = Path(__file__).resolve().parents[1] / "demo"

BUILD_SYSTEM = """You are the Dungeon Master of a study RPG. You turn a student's notes into a dungeon.
Each room is one topic from the notes. Return ONLY JSON in this exact shape:
{"title": "<short dungeon name>",
 "rooms": [{"key": "r1", "title": "<topic>", "summary": "<1-2 sentences, from the notes>",
            "keywords": ["<3-6 terms from the notes>"], "prereqs": ["<keys of rooms that must be learned first>"],
            "boss_name": "<fun boss name tied to the topic>", "boss_flavor": "<one playful sentence>"}]}
Rules: 5 to 9 rooms. Order rooms from foundational to advanced. A room's prereqs may only
reference rooms listed BEFORE it. At least one room has no prereqs. Only use topics in the notes."""


def build_from_notes(notes: str) -> int:
    plan = llm.chat_json(BUILD_SYSTEM, f"NOTES:\n{notes[:24000]}", max_tokens=6000)
    rooms = plan.get("rooms") or []
    if len(rooms) < 2:
        raise llm.LLMUnavailable("the model could not find enough topics in these notes")
    return _save(plan.get("title") or "Unnamed Dungeon", notes, rooms, questions={}, is_demo=False)


def build_demo() -> int:
    demo = json.loads((DEMO_DIR / "os_dungeon.json").read_text(encoding="utf-8"))
    notes = (DEMO_DIR / "os_notes.md").read_text(encoding="utf-8")
    questions = {r["key"]: r.pop("questions") for r in demo["rooms"]}
    return _save(demo["title"], notes, demo["rooms"], questions, is_demo=True)


def _save(title, notes, rooms, questions, is_demo) -> int:
    rooms = rooms[:9]
    keys = [str(r.get("key") or f"r{i}") for i, r in enumerate(rooms)]
    # keep only backward-pointing prereqs, which guarantees an acyclic map
    prereq_keys = [
        [p for p in dict.fromkeys(map(str, r.get("prereqs") or [])) if p in keys[:i]]
        for i, r in enumerate(rooms)
    ]
    depth = []
    for pk in prereq_keys:
        depth.append(1 + max((depth[keys.index(p)] for p in pk), default=-1))
    lanes = {}
    with db.connect() as conn:
        did = conn.execute(
            "INSERT INTO dungeons (title, notes, is_demo, created_at) VALUES (?,?,?,?)",
            (title, notes, int(is_demo), time.time()),
        ).lastrowid
        ids = {}
        for r, key, pk, d in zip(rooms, keys, prereq_keys, depth):
            lane = lanes.get(d, 0)
            lanes[d] = lane + 1
            ids[key] = conn.execute(
                """INSERT INTO rooms (dungeon_id, title, summary, keywords, prereqs, boss_name,
                   boss_flavor, status, depth, lane) VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (did, r["title"], r.get("summary", ""), json.dumps(r.get("keywords") or [r["title"]]),
                 json.dumps([ids[p] for p in pk]), r.get("boss_name") or f"Guardian of {r['title']}",
                 r.get("boss_flavor") or "", "open" if not pk else "locked", d, lane),
            ).lastrowid
            for q in questions.get(key, []):
                conn.execute(
                    "INSERT INTO questions (room_id, prompt, options, answer, explanation, difficulty) VALUES (?,?,?,?,?,?)",
                    (ids[key], q["prompt"], json.dumps(q["options"]), q["answer"], q["explanation"], q["difficulty"]),
                )
    return did


def unlock_ready_rooms(conn, dungeon_id):
    rooms = db.all_dicts(conn.execute("SELECT * FROM rooms WHERE dungeon_id=?", (dungeon_id,)))
    learned = {r["id"] for r in rooms if r["status"] in ("cleared", "respawned")}
    unlocked = []
    for r in rooms:
        if r["status"] == "locked" and all(p in learned for p in r["prereqs"]):
            conn.execute("UPDATE rooms SET status='open' WHERE id=?", (r["id"],))
            unlocked.append(r["id"])
    return unlocked


def learner_state(conn, dungeon_id):
    rows = conn.execute(
        "SELECT room_id, correct FROM interactions WHERE dungeon_id=? ORDER BY id", (dungeon_id,)
    ).fetchall()
    return tracer.replay([(r["room_id"], r["correct"]) for r in rows])


def snapshot(conn, dungeon_id) -> dict:
    """Everything the UI and the Dungeon Master need to know about a dungeon."""
    dungeon = db.as_dict(conn.execute("SELECT * FROM dungeons WHERE id=?", (dungeon_id,)).fetchone())
    if dungeon is None:
        return None
    rooms = db.all_dicts(conn.execute("SELECT * FROM rooms WHERE dungeon_id=? ORDER BY id", (dungeon_id,)))
    state = learner_state(conn, dungeon_id)
    m = tracer.mastery(state, [r["id"] for r in rooms])
    now = time.time()
    for r in rooms:
        r["mastery"] = m[r["id"]]
        r["attempts"] = state.attempts.get(r["id"], 0)
        r["days_since_cleared"] = round((now - r["cleared_at"]) / 86400, 2) if r["cleared_at"] else None
    last_dm = db.as_dict(conn.execute(
        "SELECT * FROM dm_log WHERE dungeon_id=? ORDER BY id DESC LIMIT 1", (dungeon_id,)
    ).fetchone())
    dungeon.pop("notes")
    return {"dungeon": dungeon, "rooms": rooms, "dm": last_dm, "llm": llm.available()}
