"""
Loads the trained model bundle and runs inference.

COMPATIBILITY NOTE
------------------
If you already have your own utils/predictor.py, keep it. The app only needs
`predict(answers)` to return, for every disorder:

    {
      "raw_score": float,           # weighted score
      "ml_severity": str,           # None / Mild / Moderate / Severe
      "ml_confidence": float,       # 0-1 (see UI wording: NOT a probability of a disorder)
      "ml_probabilities": {level: float},
      "rule_severity": str,
    }
"""

import os

import joblib
import pandas as pd

from utils.questions import SEVERITY_LEVELS, weighted_score, rule_severity

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model", "mental_health_model.pkl")

_bundle = None


def model_exists():
    return os.path.exists(MODEL_PATH)


def load_bundle():
    """Load (and cache) the model bundle. Raises FileNotFoundError if missing."""
    global _bundle
    if _bundle is None:
        if not model_exists():
            raise FileNotFoundError(MODEL_PATH)
        _bundle = joblib.load(MODEL_PATH)
    return _bundle


def reset_cache():
    global _bundle
    _bundle = None


def predict(answers):
    bundle = load_bundle()
    cols = bundle["feature_columns"]
    X = pd.DataFrame([list(answers)], columns=cols)

    results = {}
    for disorder, clf in bundle["models"].items():
        proba = clf.predict_proba(X)[0]
        by_class = {str(c): float(p) for c, p in zip(clf.classes_, proba)}
        by_class = {lvl: by_class.get(lvl, 0.0) for lvl in SEVERITY_LEVELS}
        top = max(by_class, key=by_class.get)
        results[disorder] = {
            "raw_score": weighted_score(disorder, answers),
            "ml_severity": top,
            "ml_confidence": by_class[top],
            "ml_probabilities": by_class,
            "rule_severity": rule_severity(disorder, answers),
        }
    return results
