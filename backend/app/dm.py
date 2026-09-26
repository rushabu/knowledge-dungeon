"""The Dungeon Master: an agent that reviews the learner's map after every fight.

It works in a small tool loop — look at the map, respawn fading rooms, recommend
where to go next, then narrate. If no LLM is reachable, a rule-based policy makes
the same kinds of moves so the game never stalls.
"""
import json
import time

from . import db, dungeon, llm

RESPAWN_BELOW = 0.65                  # tracer mastery under this → the room is fading
SPACING_DAYS = [1, 3, 7, 14, 30]      # review interval after the 1st, 2nd, ... clear
MAX_STEPS = 6

SYSTEM = """You are the Dungeon Master of a study RPG. Rooms are topics from the player's notes.
A knowledge-tracing model gives each room a mastery score (probability the player answers the
next question correctly). Your job after each fight: keep the player learning efficiently.

You act by calling ONE tool per reply, as JSON: {"tool": "<name>", "args": {...}}
Tools:
- get_map {}                               → all rooms with status, mastery, attempts, clears, days_since_cleared, review_due
- respawn_room {"room_id": int, "reason": str}   → a CLEARED room comes back so it must be re-fought (use for fading or overdue topics)
- recommend_room {"room_id": int, "reason": str} → the ONE room the player should enter next (must be open or respawned)
- finish {"message": str}                  → end your turn with 2-3 sentences of in-character narration to the player

Guidelines: respawn cleared rooms whose mastery < 0.65 or whose review is due — at most 2 per turn.
Recommend the room with the most learning value (respawned or low-mastery open rooms first;
prefer rooms that unlock others). Always call get_map first and finish last. Be encouraging and specific."""


def _map(conn, dungeon_id):
    snap = dungeon.snapshot(conn, dungeon_id)
    rows = []
    for r in snap["rooms"]:
        due = (
            r["status"] == "cleared" and r["days_since_cleared"] is not None
            and r["days_since_cleared"] >= SPACING_DAYS[min(r["clears"], len(SPACING_DAYS)) - 1]
        )
        rows.append({k: r[k] for k in ("id", "title", "status", "mastery", "attempts", "clears", "days_since_cleared", "prereqs")}
                    | {"review_due": due})
    return rows


def _respawn(conn, dungeon_id, room_id, reason):
    room = db.as_dict(conn.execute("SELECT * FROM rooms WHERE id=? AND dungeon_id=?", (room_id, dungeon_id)).fetchone())
    if room is None or room["status"] != "cleared":
        return {"error": "only cleared rooms in this dungeon can respawn"}
    conn.execute("UPDATE rooms SET status='respawned' WHERE id=?", (room_id,))
    return {"ok": True, "room": room["title"], "reason": reason}


def _recommend_ok(conn, dungeon_id, room_id):
    row = conn.execute("SELECT status FROM rooms WHERE id=? AND dungeon_id=?", (room_id, dungeon_id)).fetchone()
    return row is not None and row["status"] in ("open", "respawned")


def _rule_based(conn, dungeon_id, event):
    """Deterministic fallback with the same policy the LLM is asked to follow."""
    actions, rooms = [{"tool": "get_map"}], _map(conn, dungeon_id)
    fading = sorted(
        (r for r in rooms if r["status"] == "cleared" and (r["mastery"] < RESPAWN_BELOW or r["review_due"])),
        key=lambda r: r["mastery"],
    )[:2]
    for r in fading:
        _respawn(conn, dungeon_id, r["id"], "mastery fading")
        actions.append({"tool": "respawn_room", "args": {"room_id": r["id"]}})
        r["status"] = "respawned"
    candidates = [r for r in rooms if r["status"] in ("open", "respawned")]
    unlocks = {r["id"]: sum(r["id"] in o["prereqs"] for o in rooms) for r in candidates}
    pick = min(candidates, key=lambda r: (r["status"] != "respawned", r["mastery"] - 0.05 * unlocks[r["id"]]), default=None)
    won = event.startswith("won")
    parts = ["Well fought, adventurer." if won else "A setback, not a defeat. Every scar is a lesson."]
    if fading:
        parts.append("But beware: the ghosts of " + " and ".join(r["title"] for r in fading)
                     + " have risen again. Your grip on them is slipping.")
    if pick:
        actions.append({"tool": "recommend_room", "args": {"room_id": pick["id"]}})
        why = ("it has come back to haunt you" if pick["status"] == "respawned"
               else f"your mastery there is only {round(pick['mastery'] * 100)}%")
        parts.append(f"Your path leads to {pick['title']}: {why}.")
    else:
        parts.append("Every room is conquered. Rest, hero. For now.")
    return " ".join(parts), actions, pick["id"] if pick else None


def _agent(conn, dungeon_id, event):
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"The player just {event}. Take your turn."},
    ]
    actions, recommended, respawns = [], None, 0
    for _ in range(MAX_STEPS):
        reply = llm.chat(messages, temperature=0.3, max_tokens=400)
        try:
            call = llm.extract_json(reply)
            tool, args = call["tool"], call.get("args") or {}
        except (ValueError, KeyError, TypeError):
            result = {"error": 'reply with one JSON tool call, e.g. {"tool": "get_map", "args": {}}'}
            tool, args = None, {}
        if tool == "get_map":
            result = _map(conn, dungeon_id)
        elif tool == "respawn_room":
            if respawns >= 2:
                result = {"error": "respawn limit reached for this turn"}
            else:
                result = _respawn(conn, dungeon_id, int(args.get("room_id", -1)), args.get("reason", ""))
                respawns += "ok" in result
        elif tool == "recommend_room":
            rid = int(args.get("room_id", -1))
            result = {"ok": True} if _recommend_ok(conn, dungeon_id, rid) else {"error": "room must be open or respawned"}
            if "ok" in result:
                recommended = rid
        elif tool == "finish":
            actions.append({"tool": "finish"})
            return args.get("message", "").strip(), actions, recommended
        elif tool is not None:
            result = {"error": f"unknown tool {tool}"}
        if tool:
            actions.append({"tool": tool, "args": args, "ok": "error" not in result if isinstance(result, dict) else True})
        messages += [
            {"role": "assistant", "content": reply},
            {"role": "user", "content": "TOOL RESULT: " + json.dumps(result)},
        ]
    raise llm.LLMUnavailable("dungeon master did not finish its turn")


def take_turn(dungeon_id: int, event: str) -> dict:
    with db.connect() as conn:
        mode = "agent"
        try:
            if not llm.available():
                raise llm.LLMUnavailable("no key")
            message, actions, recommended = _agent(conn, dungeon_id, event)
            if not message:
                raise llm.LLMUnavailable("empty narration")
        except llm.LLMUnavailable:
            conn.rollback()  # discard half-finished agent moves before the fallback acts
            mode = "rules"
            message, actions, recommended = _rule_based(conn, dungeon_id, event)
        conn.execute(
            "INSERT INTO dm_log (dungeon_id, message, actions, recommended_room, ts) VALUES (?,?,?,?,?)",
            (dungeon_id, message, json.dumps(actions), recommended, time.time()),
        )
    return {"message": message, "actions": actions, "recommended_room": recommended, "mode": mode}
