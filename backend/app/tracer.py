"""Serves the trained topic-agnostic tracer to the game."""
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np

from ml.features import LearnerState

MODEL_PATH = Path(__file__).resolve().parents[2] / "ml" / "artifacts" / "tracer.joblib"


@lru_cache
def _model():
    return joblib.load(MODEL_PATH)["model"]


def replay(interactions) -> LearnerState:
    """Rebuild a learner's state from (room_id, correct) pairs in play order."""
    state = LearnerState()
    for room_id, correct in interactions:
        state.update(room_id, int(correct))
    return state


def mastery(state: LearnerState, room_ids) -> dict:
    """P(next answer correct) for each room — our mastery estimate."""
    if not room_ids:
        return {}
    X = np.stack([state.features(r) for r in room_ids])
    p = _model().predict_proba(X)[:, 1]
    return {r: round(float(v), 3) for r, v in zip(room_ids, p)}
