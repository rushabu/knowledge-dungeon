"""Knowledge Dungeon API.

    uvicorn backend.app.main:app --reload     (run from the project root)
"""
import os
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# load .env from the project root without an extra dependency
_env = Path(__file__).resolve().parents[2] / ".env"
if _env.exists():
    for line in _env.read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

from . import battle, db, dm, dungeon, llm, notes  # noqa: E402  (after .env is loaded)

app = FastAPI(title="Knowledge Dungeon")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)
db.init()


@app.get("/api/health")
def health():
    return {"ok": True, "llm": llm.available(), "model": llm.MODEL}


@app.get("/api/dungeons")
def list_dungeons():
    with db.connect() as conn:
        return db.all_dicts(conn.execute(
            "SELECT id, title, xp, is_demo, created_at FROM dungeons ORDER BY id DESC"
        ))


@app.post("/api/dungeons/demo")
def create_demo():
    did = dungeon.build_demo()
    battle.prefetch_in_background(did)
    return {"id": did}


@app.post("/api/dungeons")
async def create_dungeon(file: UploadFile = File(...)):
    text = notes.extract_text(file.filename or "notes.txt", await file.read())
    if len(text) < 300:
        raise HTTPException(400, "Those notes are too short to build a dungeon from.")
    if not llm.available():
        raise HTTPException(503, "Building from your own notes needs an LLM key (LLM_API_KEY). Try the demo dungeon.")
    try:
        did = dungeon.build_from_notes(text)
    except llm.LLMUnavailable as e:
        raise HTTPException(502, f"The Dungeon Master is unavailable: {e}")
    battle.prefetch_in_background(did)  # have the first bosses' questions ready before you get there
    return {"id": did}


@app.get("/api/dungeons/{dungeon_id}")
def get_dungeon(dungeon_id: int):
    with db.connect() as conn:
        snap = dungeon.snapshot(conn, dungeon_id)
    if snap is None:
        raise HTTPException(404, "dungeon not found")
    return snap


@app.post("/api/rooms/{room_id}/fight")
def start_fight(room_id: int):
    try:
        return battle.start_fight(room_id)
    except LookupError as e:
        raise HTTPException(404, str(e))
    except PermissionError as e:
        raise HTTPException(403, str(e))
    except RuntimeError as e:
        raise HTTPException(409, str(e))


@app.get("/api/fights/{fight_id}")
def get_fight(fight_id: int):
    return battle.get_fight(fight_id)


class Answer(BaseModel):
    question_id: int
    choice: int


@app.post("/api/fights/{fight_id}/answer")
def answer(fight_id: int, body: Answer):
    try:
        return battle.answer(fight_id, body.question_id, body.choice)
    except PermissionError as e:
        raise HTTPException(409, str(e))
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.post("/api/fights/{fight_id}/dm")
def dungeon_master_turn(fight_id: int):
    """After a fight ends the UI calls this; the Dungeon Master reviews the map and acts."""
    try:
        turn = dm.turn_after_fight(fight_id)
    except PermissionError as e:
        raise HTTPException(409, str(e))
    with db.connect() as conn:
        row = conn.execute(
            "SELECT r.dungeon_id FROM fights f JOIN rooms r ON r.id = f.room_id WHERE f.id=?", (fight_id,)
        ).fetchone()
    battle.prefetch_in_background(row["dungeon_id"])  # prepare the rooms the DM just pointed to
    return turn
