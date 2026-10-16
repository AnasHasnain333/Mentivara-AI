"""
Psychoeducational content library.

COMPATIBILITY NOTE
------------------
If you already have your own utils/treatment_plans.py, keep it. The app needs:
TREATMENT_PLANS[disorder] = {"icon": str, "protocols": [{"title": str, "steps": [str]}]},
GENERAL_GUIDELINES, DISCLAIMER, CRISIS_KEYWORDS, CRISIS_MESSAGE.

Everything here is general self-care information, not medical advice.
"""

DISCLAIMER = (
    "Mentivara AI is an educational demonstration. It is not a diagnostic tool, "
    "not a medical device and not an emergency service. Results are preliminary "
    "screening outputs and cannot replace an assessment by a qualified professional."
)

TREATMENT_PLANS = {
    "Depression": {
        "icon": "🌧️",
        "protocols": [
            {
                "title": "Behavioral activation",
                "steps": [
                    "Pick one small activity you used to enjoy (a short walk, a call with a friend).",
                    "Schedule it for a specific time today, and keep it to 10-15 minutes.",
                    "Notice your mood before and after. Repeat on most days.",
                ],
            },
            {
                "title": "Thought check (CBT-style)",
                "steps": [
                    "Write down a harsh thought you had about yourself.",
                    "Ask: what evidence supports it, and what evidence does not?",
                    "Rewrite it in a fairer, more balanced way.",
                ],
            },
        ],
    },
    "Anxiety": {
        "icon": "🌀",
        "protocols": [
            {
                "title": "Slow breathing",
                "steps": [
                    "Breathe in gently for about 4 seconds, and out for about 4-6 seconds.",
                    "Continue for a few minutes at a pace that feels comfortable.",
                    "Use the Guided Breathing page in this app if you want a visual guide.",
                ],
            },
            {
                "title": "Worry time",
                "steps": [
                    "Set aside 15 minutes each day for worries.",
                    "When a worry appears outside that time, note it and postpone it.",
                    "During worry time, ask which worries you can act on, and plan one small step.",
                ],
            },
        ],
    },
    "ADHD": {
        "icon": "⚡",
        "protocols": [
            {
                "title": "Time-boxed focus",
                "steps": [
                    "Choose one task and work on it for 25 minutes with notifications off.",
                    "Take a 5-minute break, then repeat.",
                    "Write down distracting thoughts instead of acting on them.",
                ],
            },
            {
                "title": "External reminders",
                "steps": [
                    "Put appointments and deadlines in a calendar with alerts.",
                    "Keep a single running to-do list and review it each morning.",
                    "Break big tasks into steps that take under 30 minutes each.",
                ],
            },
        ],
    },
    "Insomnia": {
        "icon": "🌙",
        "protocols": [
            {
                "title": "Sleep hygiene basics",
                "steps": [
                    "Keep a regular sleep and wake time, including weekends.",
                    "Dim screens and lights for an hour before bed.",
                    "Limit caffeine in the afternoon and evening.",
                ],
            },
            {
                "title": "Stimulus control",
                "steps": [
                    "Use the bed only for sleep.",
                    "If you cannot sleep after about 20 minutes, get up and do something calm in low light.",
                    "Return to bed only when you feel sleepy.",
                ],
            },
        ],
    },
}

GENERAL_GUIDELINES = [
    "Aim for regular sleep, meals and some daily movement.",
    "Spend time with people you trust, even briefly.",
    "Limit alcohol and caffeine, which can worsen mood, anxiety and sleep.",
    "Take short breaks from screens and news.",
    "If symptoms last more than two weeks or affect daily life, talk to a doctor or mental health professional.",
]

CRISIS_KEYWORDS = [
    "suicide", "kill myself", "end my life", "want to die",
    "hurt myself", "self harm", "self-harm", "better off dead",
]

CRISIS_MESSAGE = (
    "I'm really sorry you're going through this. You deserve support right now. "
    "If you might act on these thoughts or are in immediate danger, please contact your "
    "local emergency number or go to the nearest emergency department. If you can, "
    "reach out to someone you trust and stay with them."
)
