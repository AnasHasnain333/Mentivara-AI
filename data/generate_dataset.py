"""
Synthetic dataset generator.

COMPATIBILITY NOTE
------------------
If you already have your own data/generate_dataset.py, keep it. train_model.py
only needs a `generate()` function that returns a DataFrame with the columns
q1..q28 (answers 0-3) and "<Disorder>_label" for each disorder.

IMPORTANT: this data is SIMULATED. No real person's answers are used. Labels
come from the same rule-based scorer the app shows, so a model trained on it
only learns to reproduce that rule. It says nothing about real-world accuracy.
"""

import numpy as np
import pandas as pd

from utils.questions import QUESTIONS, DISORDERS, rule_severity

# profile name -> (probability, how to draw each domain's latent severity 0-1)
PROFILES = ["stable", "mixed_mild", "dominant", "severe_multi"]
PROFILE_PROBS = [0.30, 0.30, 0.25, 0.15]


def _latent_levels(profile, rng):
    n = len(DISORDERS)
    if profile == "stable":
        return rng.uniform(0.0, 0.25, n)
    if profile == "mixed_mild":
        return rng.uniform(0.1, 0.55, n)
    if profile == "dominant":
        levels = rng.uniform(0.0, 0.35, n)
        levels[rng.integers(n)] = rng.uniform(0.45, 1.0)
        return levels
    return rng.uniform(0.55, 1.0, n)  # severe_multi


def generate(n_samples=6000, seed=42):
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(n_samples):
        profile = rng.choice(PROFILES, p=PROFILE_PROBS)
        levels = _latent_levels(profile, rng)
        level_by_disorder = dict(zip(DISORDERS, levels))
        answers = []
        for _, disorder, _w in QUESTIONS:
            raw = level_by_disorder[disorder] * 3 + rng.normal(0, 0.7)
            answers.append(int(np.clip(round(raw), 0, 3)))
        row = {f"q{i + 1}": a for i, a in enumerate(answers)}
        for d in DISORDERS:
            row[f"{d}_label"] = rule_severity(d, answers)
        rows.append(row)
    return pd.DataFrame(rows)
