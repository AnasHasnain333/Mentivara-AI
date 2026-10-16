# ============================================================
# Train ML model(s) for the Mental Health Screening Assistant
#
# Trains one RandomForestClassifier per disorder (Depression,
# Anxiety, ADHD, Insomnia) that predicts severity class
# (None / Mild / Moderate / Severe) directly from the 28 raw
# item-level answers (0-3 scale each) — not just the weighted sum.
# This lets the model pick up on answer *patterns*, not only
# the linear score the rule-based engine uses.
#
# Usage:
#   python train_model.py
#
# Produces:
#   model/mental_health_model.pkl   (dict of trained classifiers + metadata)
#   model/training_report.txt       (per-disorder accuracy / F1 report)
# ============================================================

import os
import sys
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

sys.path.append(os.path.dirname(__file__))
from utils.questions import QUESTIONS, DISORDERS, SEVERITY_LEVELS
from data.generate_dataset import generate

MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")
os.makedirs(MODEL_DIR, exist_ok=True)


def main():
    print("Generating synthetic training data...")
    df = generate()

    feature_cols = [f"q{i+1}" for i in range(len(QUESTIONS))]
    X = df[feature_cols]

    models = {}
    report_lines = []
    report_lines.append("MENTAL HEALTH SCREENING MODEL — TRAINING REPORT")
    report_lines.append("=" * 55)

    for disorder in DISORDERS:
        y = df[f"{disorder}_label"]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        clf = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_leaf=3,
            random_state=42,
            class_weight="balanced",
        )
        clf.fit(X_train, y_train)

        preds = clf.predict(X_test)
        acc = accuracy_score(y_test, preds)
        report = classification_report(y_test, preds, zero_division=0)

        print(f"\n[{disorder}] Test accuracy: {acc:.3f}")
        print(report)

        report_lines.append(f"\n{disorder} — Test accuracy: {acc:.3f}")
        report_lines.append(report)

        models[disorder] = clf

    bundle = {
        "models": models,
        "feature_columns": feature_cols,
        "disorders": DISORDERS,
        "severity_levels": SEVERITY_LEVELS,
        "question_bank": QUESTIONS,
    }

    model_path = os.path.join(MODEL_DIR, "mental_health_model.pkl")
    joblib.dump(bundle, model_path)
    print(f"\nSaved trained model bundle -> {model_path}")

    report_path = os.path.join(MODEL_DIR, "training_report.txt")
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines))
    print(f"Saved training report -> {report_path}")


if __name__ == "__main__":
    main()
