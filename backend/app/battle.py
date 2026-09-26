"""Boss fights: adaptive difficulty from the tracer, questions from the notes."""
import json
import random
import time

from . import db, dm, dungeon, llm, notes, tracer

PLAYER_HEARTS = 3
XP_BY_DIFFICULTY = {"easy": 30, "medium": 50, "hard": 80}

QUESTION_SYSTEM = """You write multiple-choice questions for a study game, using ONLY facts from the provided notes.
Return ONLY JSON: {"questions": [{"prompt": "...", "options": ["A", "B", "C", "D"], "answer": <index 0-3>,
"explanation": "<1-2 sentences on why, citing the notes>"}]}
Difficulty guide — easy: recall a definition or fact. medium: apply or compare concepts.
hard: multi-step reasoning, edge cases, or a small scenario. Wrong options must be plausible.
Vary which index is correct. Never repeat a question from the AVOID list."""


def difficulty_for(mastery: float) -> str:
    return "easy" if mastery < 0.5 else "medium" if mastery < 0.75 else "hard"


def boss_hp_for(mastery: float) -> int:
    # weaker topics get longer fights: more practice where it's needed
    return 3 + round((1 - mastery) * 3)


def _generate_questions(conn, room, difficulty, n) -> list[int]:
    d = db.as_dict(conn.execute("SELECT notes FROM dungeons WHERE id=?", (room["dungeon_id"],)).fetchone())
    context = "\n---\n".join(notes.relevant_chunks(notes.chunk(d["notes"]), [room["title"], *room["keywords"]]))
    seen = [r["prompt"] for r in conn.execute("SELECT prompt FROM questions WHERE room_id=?", (room["id"],))]
    out = llm.chat_json(
        QUESTION_SYSTEM,
        f"TOPIC: {room['title']}\nDIFFICULTY: {difficulty}\nCOUNT: {n}\n"
        f"AVOID: {json.dumps(seen[-15:])}\nNOTES:\n{context}",
        temperature=0.7,
    )
    ids = []
    for q in out.get("questions", []):
        opts = q.get("options")
        if not (isinstance(opts, list) and len(opts) == 4 and q.get("answer") in range(4)):
            continue  # drop malformed questions rather than crash a fight
        ids.append(conn.execute(
            "INSERT INTO questions (room_id, prompt, options, answer, explanation, difficulty) VALUES (?,?,?,?,?,?)",
            (room["id"], q["prompt"], json.dumps(opts), q["answer"], q.get("explanation", ""), difficulty),
        ).lastrowid)
    return ids


def _pick_questions(conn, room, difficulty, n) -> list[int]:
    """Fresh LLM questions when possible; otherwise reuse the room's question bank."""
    ids = []
    if llm.available():
        try:
            ids = _generate_questions(conn, room, difficulty, n)
        except llm.LLMUnavailable:
            ids = []
    if len(ids) < n:
        # least-practised questions first, preferring the target difficulty
        bank = conn.execute(
            """SELECT q.id FROM questions q
               LEFT JOIN interactions i ON i.question_id = q.id
               WHERE q.room_id=?
               GROUP BY q.id
               ORDER BY (q.difficulty = ?) DESC, COUNT(i.id) ASC, RANDOM()""",
            (room["id"], difficulty),
        ).fetchall()
        ids += [r["id"] for r in bank if r["id"] not in ids][: n - len(ids)]
    return ids


def _public_question(conn, qid):
    return db.as_dict(conn.execute("SELECT id, prompt, options, difficulty FROM questions WHERE id=?", (qid,)).fetchone())


def start_fight(room_id: int) -> dict:
    with db.connect() as conn:
        room = db.as_dict(conn.execute("SELECT * FROM rooms WHERE id=?", (room_id,)).fetchone())
        if room is None:
            raise LookupError("room not found")
        if room["status"] == "locked":
            raise PermissionError("this room is still locked")
        state = dungeon.learner_state(conn, room["dungeon_id"])
        m = tracer.mastery(state, [room_id])[room_id]
        difficulty, hp = difficulty_for(m), boss_hp_for(m)
        qids = _pick_questions(conn, room, difficulty, hp + PLAYER_HEARTS - 1)
        if len(qids) < hp:
            raise RuntimeError("not enough questions for this room — set LLM_API_KEY to generate more")
        random.shuffle(qids)
        fid = conn.execute(
            """INSERT INTO fights (room_id, difficulty, start_mastery, shown_mastery, boss_hp, boss_max, player_hp,
               question_ids, status, started_at) VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (room_id, difficulty, m, m, hp, hp, PLAYER_HEARTS, json.dumps(qids), "active", time.time()),
        ).lastrowid
        return _fight_view(conn, fid)


def _fight_view(conn, fid, **extra) -> dict:
    f = db.as_dict(conn.execute("SELECT * FROM fights WHERE id=?", (fid,)).fetchone())
    room = db.as_dict(conn.execute("SELECT * FROM rooms WHERE id=?", (f["room_id"],)).fetchone())
    view = {
        "id": f["id"], "status": f["status"], "difficulty": f["difficulty"], "mastery": f["start_mastery"],
        "boss": {"name": room["boss_name"], "flavor": room["boss_flavor"], "hp": f["boss_hp"], "max_hp": f["boss_max"]},
        "player_hp": f["player_hp"], "max_player_hp": PLAYER_HEARTS,
        "room": {"id": room["id"], "title": room["title"], "dungeon_id": room["dungeon_id"]},
        "question": None, **extra,
    }
    if f["status"] == "active" and f["idx"] < len(f["question_ids"]):
        view["question"] = _public_question(conn, f["question_ids"][f["idx"]])
    return view


def get_fight(fid: int) -> dict:
    with db.connect() as conn:
        return _fight_view(conn, fid)


def answer(fid: int, question_id: int, choice: int) -> dict:
    with db.connect() as conn:
        f = db.as_dict(conn.execute("SELECT * FROM fights WHERE id=?", (fid,)).fetchone())
        if f is None or f["status"] != "active":
            raise PermissionError("this fight is over")
        if f["question_ids"][f["idx"]] != question_id:
            raise ValueError("that is not the current question")
        q = db.as_dict(conn.execute("SELECT * FROM questions WHERE id=?", (question_id,)).fetchone())
        room = db.as_dict(conn.execute("SELECT * FROM rooms WHERE id=?", (f["room_id"],)).fetchone())
        correct = int(choice == q["answer"])
        conn.execute(
            "INSERT INTO interactions (dungeon_id, room_id, question_id, correct, ts) VALUES (?,?,?,?,?)",
            (room["dungeon_id"], room["id"], question_id, correct, time.time()),
        )
        boss_hp = f["boss_hp"] - correct
        player_hp = f["player_hp"] - (1 - correct)
        idx = f["idx"] + 1
        status = "won" if boss_hp <= 0 else "lost" if player_hp <= 0 or idx >= len(f["question_ids"]) else "active"
        conn.execute(
            "UPDATE fights SET boss_hp=?, player_hp=?, idx=?, status=? WHERE id=?",
            (boss_hp, player_hp, idx, status, fid),
        )
        outcome = {"correct": bool(correct), "answer": q["answer"], "explanation": q["explanation"]}
        if status == "won":
            conn.execute(
                "UPDATE rooms SET status='cleared', clears=clears+1, cleared_at=? WHERE id=?",
                (time.time(), room["id"]),
            )
            outcome["xp_gained"] = XP_BY_DIFFICULTY[f["difficulty"]]
            conn.execute("UPDATE dungeons SET xp=xp+? WHERE id=?", (outcome["xp_gained"], room["dungeon_id"]))
            outcome["unlocked"] = dungeon.unlock_ready_rooms(conn, room["dungeon_id"])
        state = dungeon.learner_state(conn, room["dungeon_id"])
        after = tracer.mastery(state, [room["id"]])[room["id"]]
        # game rule: a correct answer never *shows* a drop; the raw score still drives the game
        outcome["mastery"] = max(f["shown_mastery"], after) if correct else after
        conn.execute("UPDATE fights SET shown_mastery=? WHERE id=?", (outcome["mastery"], fid))
        view = _fight_view(conn, fid, outcome=outcome)
    if status != "active":
        # the Dungeon Master reviews the whole map after every fight
        view["dm"] = dm.take_turn(room["dungeon_id"], event=f"{status} the fight in '{room['title']}'")
    return view
