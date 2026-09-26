"""Boss fights: adaptive difficulty from the tracer, questions from the notes."""
import json
import logging
import random
import threading
import time

from . import db, dungeon, llm, notes, tracer

PLAYER_HEARTS = 3
XP_BY_DIFFICULTY = {"easy": 30, "medium": 50, "hard": 80}

log = logging.getLogger("uvicorn.error")

QUESTION_SYSTEM = """You write multiple-choice questions for a study game, using ONLY facts from the provided notes.
Return ONLY JSON: {"questions": [{"prompt": "...", "options": ["A", "B", "C", "D"], "answer": <index 0-3>,
"explanation": "<1-2 sentences on why, citing the notes>"}]}
Difficulty guide — easy: recall a definition or fact. medium: apply or compare concepts.
hard: multi-step reasoning, edge cases, or a small scenario. Only include a calculation if the notes
show how to do it, and double-check the arithmetic. Wrong options must be plausible.
Every question must test the TOPIC itself; the notes may mention other topics, so ignore those.
Vary which index is correct. Never repeat a question from the AVOID list."""


def difficulty_for(mastery: float) -> str:
    return "easy" if mastery < 0.5 else "medium" if mastery < 0.75 else "hard"


def boss_hp_for(mastery: float) -> int:
    # weaker topics get longer fights: more practice where it's needed
    return 3 + round((1 - mastery) * 3)


VERIFY_SYSTEM = """You check quiz questions against study notes. Solve each question yourself using ONLY the
notes. Return ONLY JSON: {"results": [{"i": <question index>, "answer": <your answer index 0-3>,
"ambiguous": <true if the question is unclear, self-contradictory, or has more than one defensible answer>}]}"""


def _items(out, key) -> list:
    """Models sometimes return the bare list instead of {key: [...]}."""
    return out if isinstance(out, list) else out.get(key) or []


def _verified(questions, context, effort=None) -> list[dict]:
    """Keep questions an independent solver answers the same way, without ambiguity."""
    if not questions:
        return []
    blind = [{"i": i, "prompt": q["prompt"], "options": q["options"]} for i, q in enumerate(questions)]
    try:
        out = llm.chat_json(VERIFY_SYSTEM, f"NOTES:\n{context}\n\nQUESTIONS:\n{json.dumps(blind)}",
                            temperature=0, effort=effort)
    except llm.LLMUnavailable:
        return questions  # can't verify right now; better to play than to stall
    ok = {r.get("i") for r in _items(out, "results")
          if isinstance(r, dict) and not r.get("ambiguous") and r.get("i") in range(len(questions))
          and r.get("answer") == questions[r["i"]]["answer"]}
    return [q for i, q in enumerate(questions) if i in ok]


def _effort(difficulty):
    # hard questions involve reasoning/arithmetic; give the model more room to think
    return "medium" if difficulty == "hard" else None


def _draft_questions(room, difficulty, count, context, avoid) -> list[dict]:
    out = llm.chat_json(
        QUESTION_SYSTEM,
        f"TOPIC: {room['title']} ({room['summary']})\nDIFFICULTY: {difficulty}\nCOUNT: {count}\n"
        f"AVOID: {json.dumps(avoid[-15:])}\nNOTES:\n{context}",
        temperature=0.7, effort=_effort(difficulty),
    )
    return [
        q for q in _items(out, "questions")
        if isinstance(q, dict) and isinstance(q.get("options"), list) and len(q["options"]) == 4 and q.get("answer") in range(4)
    ]


def _generate_questions(room, difficulty, n) -> int:
    """Draft, verify and store up to n new questions for a room. Returns how many were stored."""
    with db.connect() as conn:
        d = conn.execute("SELECT notes FROM dungeons WHERE id=?", (room["dungeon_id"],)).fetchone()
        avoid = [r["prompt"] for r in conn.execute("SELECT prompt FROM questions WHERE room_id=?", (room["id"],))]
    source = room.get("source") or d["notes"]  # search only the room's own chapter when it has one
    context = "\n---\n".join(notes.relevant_chunks(notes.chunk(source), room["title"], room["keywords"]))
    kept = []
    for _ in range(2):  # a second round if the verifier rejected too many
        drafts = _draft_questions(room, difficulty, n - len(kept) + 2, context, avoid + [q["prompt"] for q in kept])
        kept += _verified(drafts, context, _effort(difficulty))
        if len(kept) >= n:
            break
    with db.connect() as conn:  # short write transaction, never held across LLM calls
        for q in kept[:n]:
            conn.execute(
                "INSERT INTO questions (room_id, prompt, options, answer, explanation, difficulty) VALUES (?,?,?,?,?,?)",
                (room["id"], q["prompt"], json.dumps(q["options"]), q["answer"], q.get("explanation", ""), difficulty),
            )
    return len(kept[:n])


def _plan(conn, room) -> tuple[float, str, int, int]:
    """(mastery, difficulty, boss hp, questions needed) for a room right now."""
    m = tracer.mastery(dungeon.learner_state(conn, room["dungeon_id"]), [room["id"]])[room["id"]]
    hp = boss_hp_for(m)
    return m, difficulty_for(m), hp, hp + PLAYER_HEARTS - 1


def _fresh_count(conn, room_id, difficulty) -> int:
    return conn.execute(
        """SELECT COUNT(*) FROM questions q WHERE q.room_id=? AND q.difficulty=?
           AND NOT EXISTS (SELECT 1 FROM interactions i WHERE i.question_id = q.id)""",
        (room_id, difficulty),
    ).fetchone()[0]


def prepare_room(room_id: int) -> int:
    """Make sure a room has enough unplayed questions for its next fight. Returns how many were added."""
    if not llm.available():
        return 0
    with db.connect() as conn:
        room = db.as_dict(conn.execute("SELECT * FROM rooms WHERE id=?", (room_id,)).fetchone())
        _, difficulty, _, need = _plan(conn, room)
        missing = need - _fresh_count(conn, room_id, difficulty)
    if missing <= 0:
        return 0
    try:
        return _generate_questions(room, difficulty, missing)
    except llm.LLMUnavailable as e:
        log.warning("could not prepare questions for room %s: %s", room_id, e)
        return 0


_prefetch_lock = threading.Lock()


def prefetch(dungeon_id: int):
    """Background job: prepare the rooms the player is likely to enter next, most likely first."""
    if not llm.available() or not _prefetch_lock.acquire(blocking=False):
        return  # one prefetch at a time keeps us under the provider's rate limit
    try:
        with db.connect() as conn:
            snap = dungeon.snapshot(conn, dungeon_id)
        rec = (snap["dm"] or {}).get("recommended_room")
        playable = [r for r in snap["rooms"] if r["status"] in ("open", "respawned")]
        playable.sort(key=lambda r: (r["id"] != rec, r["status"] != "respawned", r["mastery"]))
        for r in playable[:3]:
            prepare_room(r["id"])
    finally:
        _prefetch_lock.release()


def prefetch_in_background(dungeon_id: int):
    threading.Thread(target=prefetch, args=(dungeon_id,), daemon=True).start()


def _pick_questions(conn, room, difficulty, n) -> list[int]:
    """Unplayed questions at the right difficulty first; generate on the spot only if the bank is short."""
    if _fresh_count(conn, room["id"], difficulty) < n and llm.available():
        try:
            _generate_questions(room, difficulty, n - _fresh_count(conn, room["id"], difficulty))
        except llm.LLMUnavailable:
            pass  # fall back to whatever the bank has
    bank = conn.execute(
        """SELECT q.id FROM questions q
           LEFT JOIN interactions i ON i.question_id = q.id
           WHERE q.room_id=?
           GROUP BY q.id
           ORDER BY COUNT(i.id) = 0 AND q.difficulty = ? DESC, COUNT(i.id) ASC, (q.difficulty = ?) DESC, RANDOM()""",
        (room["id"], difficulty, difficulty),
    ).fetchall()
    return [r["id"] for r in bank][:n]


def _public_question(conn, qid):
    return db.as_dict(conn.execute("SELECT id, prompt, options, difficulty FROM questions WHERE id=?", (qid,)).fetchone())


def start_fight(room_id: int) -> dict:
    with db.connect() as conn:
        room = db.as_dict(conn.execute("SELECT * FROM rooms WHERE id=?", (room_id,)).fetchone())
        if room is None:
            raise LookupError("room not found")
        if room["status"] == "locked":
            raise PermissionError("this room is still locked")
        m, difficulty, hp, need = _plan(conn, room)
        qids = _pick_questions(conn, room, difficulty, need)
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
    # before any answers in a room, start_mastery is only the tracer's prior, not a score to show
    tested = conn.execute(
        "SELECT 1 FROM interactions WHERE room_id=? AND ts < ? LIMIT 1", (room["id"], f["started_at"])
    ).fetchone() is not None
    view = {
        "id": f["id"], "status": f["status"], "difficulty": f["difficulty"],
        "mastery": f["start_mastery"] if tested else None,
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
    return view  # the Dungeon Master's turn runs separately: POST /api/fights/{id}/dm
