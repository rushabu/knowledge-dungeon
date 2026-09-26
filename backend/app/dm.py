"""The Dungeon Master: an agent that reviews the learner's map after every fight.

It works in a small tool loop — look at the map, respawn fading rooms, recommend
where to go next, then narrate. If no LLM is reachable, a rule-based policy makes
the same kinds of moves so the game never stalls.
"""
import json
import logging
import time

from . import db, dungeon, llm

log = logging.getLogger("uvicorn.error")

RESPAWN_BELOW = 0.65                  # tracer mastery under this → the room is fading
SPACING_DAYS = [1, 3, 7, 14, 30]      # review interval after the 1st, 2nd, ... clear
MAX_STEPS = 8

SYSTEM = """You are the Dungeon Master of a study RPG. Rooms are topics from the player's notes.
A knowledge-tracing model gives each room a mastery score (probability the player answers the
next question correctly). Your job after each fight: keep the player learning efficiently.

Use your tools: call get_map first. Respawn cleared rooms whose mastery < 0.65 or whose review is
due (at most 2 per turn). Recommend the one room with the most learning value (respawned or
low-mastery open rooms first; prefer rooms that unlock others). Then call finish with 2-3 sentences
of encouraging, specific, in-character narration in plain text (no markdown)."""

TOOLS = [
    {"type": "function", "function": {
        "name": "get_map",
        "description": "All rooms with status, mastery, attempts, clears, days_since_cleared and review_due.",
        "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {
        "name": "respawn_room",
        "description": "Bring a CLEARED room's boss back so the player must re-fight it (for fading or overdue topics).",
        "parameters": {"type": "object", "properties": {
            "room_id": {"type": "integer"}, "reason": {"type": "string"}}, "required": ["room_id", "reason"]}}},
    {"type": "function", "function": {
        "name": "recommend_room",
        "description": "The ONE room the player should enter next. Must be open or respawned.",
        "parameters": {"type": "object", "properties": {
            "room_id": {"type": "integer"}, "reason": {"type": "string"}}, "required": ["room_id", "reason"]}}},
    {"type": "function", "function": {
        "name": "finish",
        "description": "End your turn with 2-3 sentences of in-character narration to the player.",
        "parameters": {"type": "object", "properties": {"message": {"type": "string"}}, "required": ["message"]}}},
]


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
        reason = "review due" if r["review_due"] else f"mastery down to {round(r['mastery'] * 100)}%"
        _respawn(conn, dungeon_id, r["id"], reason)
        actions.append({"tool": "respawn_room", "args": {"room_id": r["id"], "reason": reason}})
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
        why = ("it has come back to haunt you" if pick["status"] == "respawned"
               else f"your mastery there is only {round(pick['mastery'] * 100)}%")
        actions.append({"tool": "recommend_room", "args": {"room_id": pick["id"], "reason": why}})
        parts.append(f"Your path leads to {pick['title']}: {why}.")
    else:
        parts.append("Every room is conquered. Rest, hero. For now.")
    return " ".join(parts), actions, pick["id"] if pick else None


def _finish_blocked(conn, dungeon_id, recommended, respawns) -> str | None:
    """Guardrails: the LLM chooses how to act, but can't skip the game's core rules."""
    rooms = _map(conn, dungeon_id)
    fading = [r["title"] for r in rooms if r["status"] == "cleared"
              and (r["mastery"] < RESPAWN_BELOW or r["review_due"])]
    if fading and respawns < 2:
        return f"these cleared rooms are fading or due for review, respawn them first: {fading}"
    if recommended is None and any(r["status"] in ("open", "respawned") for r in rooms):
        return "call recommend_room first"
    return None


def _agent(conn, dungeon_id, event):
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"The player just {event}. Take your turn."},
    ]
    actions, recommended, respawns = [], None, 0
    for _ in range(MAX_STEPS):
        try:
            msg = llm.chat_tools(messages, TOOLS)
        except llm.InvalidToolCall as e:
            messages.append({"role": "user", "content": f"Your last tool call was rejected ({str(e)[:300]}). "
                             "Only call tools with valid arguments; skip a tool if it doesn't apply."})
            continue
        calls = msg.tool_calls or []
        if not calls:
            # the model narrated in plain text: treat it as finish, same guardrails
            text = (msg.content or "").strip()
            messages.append({"role": "assistant", "content": text})
            error = _finish_blocked(conn, dungeon_id, recommended, respawns) if text else "call one of your tools"
            if not error:
                actions.append({"tool": "finish"})
                return text, actions, recommended
            messages.append({"role": "user", "content": f"Not finished: {error}. Use your tools."})
            continue
        messages.append({"role": "assistant", "content": msg.content or "", "tool_calls": [
            {"id": c.id, "type": "function", "function": {"name": c.function.name, "arguments": c.function.arguments}}
            for c in calls]})
        for c in calls:
            tool = c.function.name
            try:
                args = json.loads(c.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
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
                error = _finish_blocked(conn, dungeon_id, recommended, respawns)
                if not error and not str(args.get("message", "")).strip():
                    error = "finish needs a message"
                if not error:
                    actions.append({"tool": "finish"})
                    return args["message"].strip(), actions, recommended
                result = {"error": f"not finished: {error}"}
            else:
                result = {"error": f"unknown tool {tool}"}
            actions.append({"tool": tool, "args": args,
                            "ok": "error" not in result if isinstance(result, dict) else True})
            messages.append({"role": "tool", "tool_call_id": c.id, "content": json.dumps(result)})
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
        except llm.LLMUnavailable as e:
            conn.rollback()  # discard half-finished agent moves before the fallback acts
            log.warning("Dungeon Master fell back to rules: %s", e)
            mode = "rules"
            message, actions, recommended = _rule_based(conn, dungeon_id, event)
        message = message.replace("**", "").replace("__", "")
        conn.execute(
            "INSERT INTO dm_log (dungeon_id, message, actions, recommended_room, ts) VALUES (?,?,?,?,?)",
            (dungeon_id, message, json.dumps(actions), recommended, time.time()),
        )
    return {"message": message, "actions": actions, "recommended_room": recommended, "mode": mode}


def turn_after_fight(fight_id: int) -> dict:
    """Run the Dungeon Master's turn for a finished fight, once."""
    with db.connect() as conn:
        f = conn.execute(
            "SELECT f.status, f.dm_done, r.dungeon_id, r.title FROM fights f JOIN rooms r ON r.id = f.room_id WHERE f.id=?",
            (fight_id,),
        ).fetchone()
        if f is None or f["status"] == "active":
            raise PermissionError("the fight isn't over yet")
        if f["dm_done"]:
            last = db.as_dict(conn.execute(
                "SELECT * FROM dm_log WHERE dungeon_id=? ORDER BY id DESC LIMIT 1", (f["dungeon_id"],)).fetchone())
            return last
        conn.execute("UPDATE fights SET dm_done=1 WHERE id=?", (fight_id,))
    return take_turn(f["dungeon_id"], event=f"{f['status']} the fight in '{f['title']}'")
