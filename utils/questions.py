"""
Question bank, item weights and rule-based scoring.

COMPATIBILITY NOTE
------------------
If you already have your own utils/questions.py from the original project,
keep it. The rest of the app only relies on this interface:

    QUESTIONS        list of (question_text, disorder, weight) tuples
    DISORDERS        list of disorder names
    SEVERITY_LEVELS  ["None", "Mild", "Moderate", "Severe"]

The helpers below (THRESHOLDS, max_score, weighted_score, rule_severity)
are used by data/generate_dataset.py and utils/predictor.py in this repo.

The questions are written in the *style* of PHQ-9, GAD-7, ASRS and ISI.
They are NOT the official validated instruments.
"""

DISORDERS = ["Depression", "Anxiety", "ADHD", "Insomnia"]
SEVERITY_LEVELS = ["None", "Mild", "Moderate", "Severe"]

# Answer scale used by the whole questionnaire
ANSWER_LABELS = ["Never", "Sometimes", "Often", "Almost Always"]

# (question text, disorder, weight)
QUESTIONS = [
    # ---- Depression (PHQ-9 style) : q1-q9 ----
    ("Little interest or pleasure in doing things you usually enjoy", "Depression", 1.5),
    ("Feeling down, sad or hopeless", "Depression", 1.5),
    ("Trouble falling asleep, staying asleep, or sleeping too much", "Depression", 1.0),
    ("Feeling tired or having little energy", "Depression", 1.0),
    ("Poor appetite or overeating", "Depression", 1.0),
    ("Feeling bad about yourself, or that you are a failure", "Depression", 1.0),
    ("Trouble concentrating on things like reading or watching TV", "Depression", 1.0),
    ("Moving or speaking noticeably slower, or feeling restless", "Depression", 1.0),
    ("Thoughts that you would be better off dead, or of hurting yourself", "Depression", 1.0),
    # ---- Anxiety (GAD-7 style) : q10-q16 ----
    ("Feeling nervous, anxious or on edge", "Anxiety", 1.5),
    ("Not being able to stop or control worrying", "Anxiety", 1.5),
    ("Worrying too much about different things", "Anxiety", 1.0),
    ("Trouble relaxing", "Anxiety", 1.0),
    ("Being so restless that it is hard to sit still", "Anxiety", 1.0),
    ("Becoming easily annoyed or irritable", "Anxiety", 1.0),
    ("Feeling afraid as if something awful might happen", "Anxiety", 1.0),
    # ---- ADHD (ASRS style) : q17-q22 ----
    ("Trouble wrapping up the final details of a project once the hard parts are done", "ADHD", 1.0),
    ("Difficulty getting things in order when you have to do a task that requires organization", "ADHD", 1.0),
    ("Problems remembering appointments or obligations", "ADHD", 1.0),
    ("Avoiding or delaying tasks that require a lot of thought", "ADHD", 1.5),
    ("Fidgeting or squirming when you have to sit down for a long time", "ADHD", 1.0),
    ("Feeling overly active or compelled to do things, as if driven by a motor", "ADHD", 1.0),
    # ---- Insomnia (ISI style) : q23-q28 ----
    ("Difficulty falling asleep", "Insomnia", 1.5),
    ("Difficulty staying asleep through the night", "Insomnia", 1.5),
    ("Waking up too early and not being able to get back to sleep", "Insomnia", 1.0),
    ("Feeling dissatisfied with your current sleep pattern", "Insomnia", 1.0),
    ("Sleep problems interfering with your daily functioning", "Insomnia", 1.0),
    ("Worrying about your sleep", "Insomnia", 1.0),
]

# Severity thresholds as a fraction of the maximum weighted score of a domain.
# These are simple demo thresholds, NOT clinically validated cut-offs.
THRESHOLDS = {"Mild": 0.20, "Moderate": 0.40, "Severe": 0.60}


def max_score(disorder):
    """Highest possible weighted score for a domain (every item answered 3)."""
    return 3 * sum(w for _, d, w in QUESTIONS if d == disorder)


def weighted_score(disorder, answers):
    """Sum of (answer x weight) over the items that belong to a domain."""
    total = 0.0
    for (_, d, w), a in zip(QUESTIONS, answers):
        if d == disorder and a is not None:
            total += a * w
    return round(total, 1)


def rule_severity(disorder, answers):
    """Deterministic, transparent severity class from the weighted score."""
    ratio = weighted_score(disorder, answers) / max_score(disorder)
    if ratio >= THRESHOLDS["Severe"]:
        return "Severe"
    if ratio >= THRESHOLDS["Moderate"]:
        return "Moderate"
    if ratio >= THRESHOLDS["Mild"]:
        return "Mild"
    return "None"
