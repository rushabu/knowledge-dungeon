"""Train and evaluate the knowledge-tracing models.

    python -m ml.train            # tracer + baselines + DKT benchmark
    python -m ml.train --no-dkt   # skip the (slower) DKT run

Writes ml/artifacts/tracer.joblib (used by the game) and ml/artifacts/metrics.json.
"""
import argparse
import json
import time
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, brier_score_loss, roc_auc_score

from .data import load_split
from .features import FEATURE_NAMES, build_rows

ARTIFACTS = Path(__file__).resolve().parent / "artifacts"


def evaluate(y, p):
    return {
        "auc": round(float(roc_auc_score(y, p)), 4),
        "accuracy": round(float(accuracy_score(y, p >= 0.5)), 4),
        "brier": round(float(brier_score_loss(y, p)), 4),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-dkt", action="store_true")
    args = ap.parse_args()
    ARTIFACTS.mkdir(exist_ok=True)

    train, valid, test = load_split("train"), load_split("valid"), load_split("test")
    Xtr, ytr = build_rows(train + valid)
    Xte, yte = build_rows(test)
    print(f"rows: train {len(ytr):,}  test {len(yte):,}  features {len(FEATURE_NAMES)}")

    metrics = {"dataset": "ASSISTments 2009 (DKVMN benchmark split)"}

    # Baseline 0: always predict the learner's smoothed global accuracy
    metrics["baseline_global_acc"] = evaluate(yte, Xte[:, FEATURE_NAMES.index("global_acc")])

    # Baseline 1: logistic regression on the same features (PFA-like)
    lr = LogisticRegression(max_iter=1000).fit(Xtr, ytr)
    metrics["logistic_regression"] = evaluate(yte, lr.predict_proba(Xte)[:, 1])

    # Main model: gradient-boosted topic-agnostic tracer
    t0 = time.time()
    tracer = HistGradientBoostingClassifier(
        max_iter=400, learning_rate=0.05, max_leaf_nodes=31,
        early_stopping=True, validation_fraction=0.1, random_state=0,
    ).fit(Xtr, ytr)
    metrics["tracer"] = evaluate(yte, tracer.predict_proba(Xte)[:, 1])
    metrics["tracer"]["train_seconds"] = round(time.time() - t0, 1)
    joblib.dump({"model": tracer, "features": FEATURE_NAMES}, ARTIFACTS / "tracer.joblib")

    if not args.no_dkt:
        from .dkt import train_dkt
        t0 = time.time()
        _, dkt_metrics = train_dkt(train, valid, test)
        dkt_metrics = {k: round(v, 4) for k, v in dkt_metrics.items()}
        dkt_metrics["train_seconds"] = round(time.time() - t0, 1)
        metrics["dkt_skill_specific"] = dkt_metrics

    (ARTIFACTS / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
