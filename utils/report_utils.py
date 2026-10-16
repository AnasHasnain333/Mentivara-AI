"""Builds the downloadable text report."""

from datetime import datetime

from utils import questions as Q
from utils.treatment_plans import DISCLAIMER, TREATMENT_PLANS, GENERAL_GUIDELINES
from utils.model_utils import response_summary, highest_severity

SYNTHETIC_NOTE = (
    "The machine-learning model was trained on SIMULATED (synthetic) data labelled by "
    "the same rule-based scorer shown in this report. Its accuracy on that data only shows "
    "how well it reproduces the rule. It is not evidence of clinical performance. Model "
    "scores are not the probability that you have a condition."
)

SCORING_NOTE = (
    "Scoring method: every answer is 0 (Never) to 3 (Almost Always). Each answer is multiplied "
    "by an item weight and the results are added up per domain. The weighted score is compared "
    "with the fixed demo thresholds in utils/questions.py (share of the maximum score) to give "
    "None / Mild / Moderate / Severe. These thresholds are not clinically validated."
)


def build_report(answers, results):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "MENTIVARA AI - PRELIMINARY WELLNESS SCREENING REPORT",
        "=" * 56,
        f"Generated: {now}",
        "",
        "DISCLAIMER",
        DISCLAIMER,
        "",
        "SUMMARY OF YOUR RESPONSES (0 = Never ... 3 = Almost Always)",
        "-" * 56,
    ]
    summary = response_summary(answers)
    for disorder, s in summary.items():
        lines.append(f"{disorder}: average item score {s['mean']:.2f} / 3 over {s['n_items']} items")
        for q, label in s["frequent"]:
            lines.append(f"    - {label}: {q}")
    lines += ["", "RESULTS", "-" * 56]

    if results:
        for disorder, r in results.items():
            max_s = Q.max_score(disorder) if hasattr(Q, "max_score") else "?"
            lines.append(
                f"{disorder}: weighted score {r['raw_score']} / {max_s} | "
                f"rule-based: {r['rule_severity']} | model-predicted class: {r['ml_severity']} "
                f"(model vote share {r['ml_confidence'] * 100:.0f}%)"
            )
        lines += ["", "RECOMMENDATIONS (general self-care ideas, not medical advice)", "-" * 56]
        flagged = False
        for disorder, r in results.items():
            level = highest_severity(r["rule_severity"], r["ml_severity"])
            if level != "None":
                flagged = True
                lines.append(f"{disorder} ({level}):")
                for protocol in TREATMENT_PLANS[disorder]["protocols"]:
                    lines.append(f"  * {protocol['title']}")
                    for step in protocol["steps"]:
                        lines.append(f"      - {step}")
                if level == "Severe":
                    lines.append("  ! Consider speaking with a qualified mental health professional.")
        if not flagged:
            lines.append("No domain reached the Mild range in this screening.")
    else:
        lines.append("Model results were not available for this report.")

    lines += ["", "GENERAL WELL-BEING GUIDELINES"]
    lines += [f"  - {g}" for g in GENERAL_GUIDELINES]
    lines += ["", "HOW SCORING WORKS", SCORING_NOTE, "", "LIMITATIONS", SYNTHETIC_NOTE, ""]
    lines += [
        "IF YOU NEED URGENT HELP",
        "Contact your local emergency number or a crisis line. Free local helplines: https://findahelpline.com",
    ]
    return "\n".join(lines)
