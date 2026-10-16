import pytest

from utils.questions import QUESTIONS, DISORDERS, SEVERITY_LEVELS, rule_severity, max_score
from utils.predictor import predict
from utils.chatbot_utils import respond, TOPICS
from utils.safety_utils import detect_crisis, self_harm_item_endorsed, self_harm_item_indices
from utils.report_utils import build_report
from utils.model_utils import safe_predict, response_summary


def test_question_bank_shape():
    assert len(QUESTIONS) == 28
    assert {d for _, d, _ in QUESTIONS} == set(DISORDERS)
    assert all(w > 0 for _, _, w in QUESTIONS)


@pytest.mark.parametrize("disorder", DISORDERS)
def test_rule_severity_extremes(disorder):
    assert rule_severity(disorder, [0] * 28) == "None"
    assert rule_severity(disorder, [3] * 28) == "Severe"
    assert max_score(disorder) > 0


def test_predict_interface():
    res = predict([2] * 28)
    assert set(res) == set(DISORDERS)
    for r in res.values():
        assert r["ml_severity"] in SEVERITY_LEVELS
        assert r["rule_severity"] in SEVERITY_LEVELS
        assert abs(sum(r["ml_probabilities"].values()) - 1.0) < 1e-6


def test_model_agrees_on_extremes():
    low, high = predict([0] * 28), predict([3] * 28)
    assert all(r["ml_severity"] == "None" for r in low.values())
    assert all(r["ml_severity"] == "Severe" for r in high.values())


def test_safe_predict_wrong_length_is_handled():
    results, error = safe_predict([1, 2, 3])
    assert results is None and error


@pytest.mark.parametrize("text", [
    "I want to kill myself", "thinking about suicide", "I don't want to live anymore",
    "i dont want to be alive", "I want to end my life", "better off dead", "I might hurt myself",
])
def test_crisis_detected(text):
    assert detect_crisis(text)
    reply, topic = respond(text)
    assert topic == "crisis" and "emergency" in reply.lower()


@pytest.mark.parametrize("text", [
    "I have a killer exam tomorrow", "high school is hard", "can't sleep", "hello", "write it down",
])
def test_benign_messages_not_flagged(text):
    assert not detect_crisis(text)


@pytest.mark.parametrize("text,topic", [
    ("so stressed about exams", "stress"), ("I'm anxious", "anxiety"), ("can't sleep", "sleep"),
    ("help me calm down", "grounding"), ("I can't focus", "focus"), ("hi", "greeting"),
])
def test_chatbot_routing(text, topic):
    assert respond(text)[1] == topic


def test_chatbot_default_is_honest_about_being_rule_based():
    reply, topic = respond("blah blah")
    assert topic is None and "rule-based" in reply


def test_all_topics_have_replies():
    assert all(t["reply"] and t["keywords"] for t in TOPICS.values())


def test_self_harm_item_flag():
    idx = self_harm_item_indices()
    assert len(idx) == 1
    answers = [0] * 28
    assert not self_harm_item_endorsed(answers)
    answers[idx[0]] = 1
    assert self_harm_item_endorsed(answers)


def test_report_has_required_disclosures():
    answers = [2] * 28
    report = build_report(answers, predict(answers))
    for phrase in ["DISCLAIMER", "SIMULATED", "not clinically validated", "findahelpline", "HOW SCORING WORKS"]:
        assert phrase in report


def test_report_without_model_still_builds():
    assert "not available" in build_report([1] * 28, None)


def test_response_summary_counts_frequent_items():
    answers = [0] * 28
    answers[0] = 3
    s = response_summary(answers)
    assert len(s["Depression"]["frequent"]) == 1 and s["Anxiety"]["frequent"] == []


def test_synthetic_dataset_columns():
    from data.generate_dataset import generate
    df = generate(n_samples=300)
    assert all(f"q{i + 1}" in df for i in range(28))
    assert all(f"{d}_label" in df for d in DISORDERS)
    assert df[[f"q{i + 1}" for i in range(28)]].min().min() >= 0
    assert df[[f"q{i + 1}" for i in range(28)]].max().max() <= 3
