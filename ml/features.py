"""Topic-agnostic learner features.

The same LearnerState is used to build training rows from ASSISTments and to
score live players in the game, so train and serve features can't drift apart.
Nothing here depends on *which* skill it is, only on how the learner has done
on it, which is what lets a model trained on math transfer to any topic.
"""
from collections import defaultdict, deque

import numpy as np

FEATURE_NAMES = [
    "attempts",        # prior attempts on this skill
    "correct",         # prior correct answers on this skill
    "skill_acc",       # smoothed accuracy on this skill
    "last1", "last2", "last3",  # last outcomes on this skill (-1 = none)
    "streak",          # +n correct run / -n wrong run on this skill
    "log_gap",         # log1p(interactions since this skill was last seen), -1 if never
    "log_total",       # log1p(total prior interactions)
    "global_acc",      # smoothed accuracy across all skills
    "recent_acc",      # accuracy over the last 5 interactions (-1 if none)
    "skills_seen",     # number of distinct skills practised
]


class LearnerState:
    def __init__(self):
        self.t = 0
        self.total_correct = 0
        self.recent = deque(maxlen=5)
        self.attempts = defaultdict(int)
        self.corrects = defaultdict(int)
        self.history = defaultdict(list)   # skill -> list of 0/1
        self.last_seen = {}                # skill -> step index

    def features(self, skill) -> np.ndarray:
        h = self.history[skill]
        n, c = self.attempts[skill], self.corrects[skill]
        last = [h[-k] if len(h) >= k else -1 for k in (1, 2, 3)]
        streak = 0
        for x in reversed(h):
            if streak >= 0 and x == 1:
                streak += 1
            elif streak <= 0 and x == 0:
                streak -= 1
            else:
                break
        gap = np.log1p(self.t - self.last_seen[skill]) if skill in self.last_seen else -1.0
        return np.array([
            n, c, (c + 1) / (n + 2), *last, streak, gap,
            np.log1p(self.t),
            (self.total_correct + 1) / (self.t + 2),
            np.mean(self.recent) if self.recent else -1.0,
            len(self.attempts),
        ], dtype=np.float32)

    def update(self, skill, correct: int):
        self.attempts[skill] += 1
        self.corrects[skill] += correct
        self.history[skill].append(correct)
        self.last_seen[skill] = self.t
        self.total_correct += correct
        self.recent.append(correct)
        self.t += 1


def build_rows(seqs) -> tuple[np.ndarray, np.ndarray]:
    """Feature matrix for every interaction, computed *before* its outcome is seen."""
    X, y = [], []
    for s in seqs:
        state = LearnerState()
        for skill, correct in zip(s.skills, s.correct):
            X.append(state.features(int(skill)))
            y.append(int(correct))
            state.update(int(skill), int(correct))
    return np.stack(X), np.array(y)
