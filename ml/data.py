"""Loaders for the ASSISTments 2009 benchmark split (DKVMN format).

Each student takes three lines in the CSV:
    <sequence length>
    <comma-separated skill ids, 1..110>
    <comma-separated correctness, 0/1>
"""
from dataclasses import dataclass
from pathlib import Path

import numpy as np

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
NUM_SKILLS = 110

SPLITS = {
    "train": "assist2009_updated_train1.csv",
    "valid": "assist2009_updated_valid1.csv",
    "test": "assist2009_updated_test.csv",
}


@dataclass
class Sequence:
    skills: np.ndarray   # int, 1..NUM_SKILLS
    correct: np.ndarray  # int, 0/1


def load_split(name: str) -> list[Sequence]:
    lines = (RAW_DIR / SPLITS[name]).read_text().strip().splitlines()
    seqs = []
    for i in range(0, len(lines), 3):
        skills = np.array([int(x) for x in lines[i + 1].strip().strip(",").split(",")])
        correct = np.array([int(x) for x in lines[i + 2].strip().strip(",").split(",")])
        assert len(skills) == len(correct) == int(lines[i])
        seqs.append(Sequence(skills, correct))
    return seqs


def load_skill_names() -> dict[int, str]:
    names = {}
    for line in (RAW_DIR / "assist2009_updated_skill_mapping.txt").read_text().splitlines():
        if line.strip():
            sid, name = line.split("\t", 1)
            names[int(sid)] = name.strip()
    return names
