"""Safe wrappers around prediction and training so the UI never crashes."""

from utils.questions import QUESTIONS, DISORDERS, SEVERITY_LEVELS, ANSWER_LABELS


def safe_predict(answers):
    """Return (results, error_message). Exactly one of them is None."""
    try:
        from utils.predictor import predict
        return predict(answers), None
    except FileNotFoundError:
        return None, "missing_model"
    except Exception as exc:  # unreadable pickle, sklearn mismatch, etc.
        return None, f"{type(exc).__name__}: {exc}"


def train_now():
    """Run train_model.main() from inside the app and reload the model cache."""
    import train_model
    from utils import predictor

    train_model.main()
    predictor.reset_cache()


def highest_severity(*levels):
    """Return the most severe level from the ones given."""
    return max(levels, key=lambda lvl: SEVERITY_LEVELS.index(lvl))


def response_summary(answers):
    """Per-domain summary of the raw answers (independent of any model)."""
    summary = {}
    for disorder in DISORDERS:
        items = [(q, a) for (q, d, _w), a in zip(QUESTIONS, answers) if d == disorder]
        values = [a if a is not None else 0 for _, a in items]
        frequent = [(q, ANSWER_LABELS[a]) for q, a in items if (a or 0) >= 2]
        summary[disorder] = {
            "n_items": len(items),
            "mean": sum(values) / len(values) if values else 0.0,
            "frequent": frequent,
        }
    return summary
