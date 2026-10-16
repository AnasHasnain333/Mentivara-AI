"""
Rule-based wellness chatbot content and routing.

This is NOT a generative AI model and NOT an autonomous agent. It matches
keywords to a small set of curated, general-information replies. It cannot
understand context, give medical advice or provide crisis support.
"""

import re

from utils.safety_utils import detect_crisis, CRISIS_RESPONSE

GENERAL_INFO_NOTE = (
    "_This is general wellness information, not professional medical advice._"
)

TOPICS = {
    "stress": {
        "label": "Stress tips",
        "keywords": ["stress", "overwhelm", "pressure", "burnout", "burned out", "too much"],
        "reply": (
            "Stress is a normal response to pressure, and small habits can ease it:\n\n"
            "- **Write it down.** List what is on your mind, then circle one thing you can do today.\n"
            "- **Break tasks into small steps** and start with the smallest.\n"
            "- **Take a short walk** or stretch for five minutes.\n"
            "- **Pause with slow breathing.** The Breathing Exercise page can guide you.\n"
            "- **Talk to someone** you trust about what is weighing on you."
        ),
    },
    "anxiety": {
        "label": "Feeling anxious",
        "keywords": ["anxious", "anxiety", "worried", "worry", "panic", "nervous", "on edge", "afraid"],
        "reply": (
            "Feeling anxious is uncomfortable, and it does pass. Things that can help in the moment:\n\n"
            "- **Slow your breathing:** in for about 4 seconds, out for about 6, at a pace that feels comfortable.\n"
            "- **Ground yourself** with the 5-4-3-2-1 exercise (ask me for *grounding*).\n"
            "- **Name it:** saying 'I am feeling anxious right now' can reduce its pull.\n\n"
            "If anxiety is frequent or gets in the way of daily life, a doctor or therapist can help."
        ),
    },
    "low_mood": {
        "label": "Low mood",
        "keywords": ["sad", "feeling down", "depress", "hopeless", "empty", "lonely", "worthless", "unmotivated"],
        "reply": (
            "I'm sorry things feel heavy right now. A few gentle ideas:\n\n"
            "- **Do one small thing** you used to enjoy, even for 10 minutes.\n"
            "- **Get daylight and move** a little, such as a short walk.\n"
            "- **Reach out** to a friend or family member, even with a short message.\n\n"
            "If low mood lasts more than two weeks or affects your daily life, please consider talking "
            "to a doctor or mental health professional. You do not have to handle it alone."
        ),
    },
    "sleep": {
        "label": "Sleep tips",
        "keywords": ["sleep", "insomnia", "awake", "tired", "can't sleep", "cant sleep", "nightmare"],
        "reply": (
            "Sleep habits that help many people:\n\n"
            "- **Keep regular times** for going to bed and waking up.\n"
            "- **Dim screens and lights** for an hour before bed.\n"
            "- **Limit caffeine** in the afternoon and evening.\n"
            "- **If you cannot sleep after about 20 minutes,** get up and do something calm in low light.\n\n"
            "If poor sleep continues for weeks, talk to a doctor."
        ),
    },
    "focus": {
        "label": "Focus and distraction",
        "keywords": ["focus", "distract", "forget", "procrastinat", "concentrat", "attention"],
        "reply": (
            "Some practical ways to support focus:\n\n"
            "- **Time-box:** work 25 minutes on one task, then rest 5.\n"
            "- **Turn off notifications** and keep your phone out of reach.\n"
            "- **Use reminders and a single to-do list.**\n"
            "- **Start tiny:** commit to just two minutes of the task.\n\n"
            "If focus problems have been lifelong or affect work or study, a professional assessment can help."
        ),
    },
    "grounding": {
        "label": "Grounding exercise",
        "keywords": ["ground", "grounding", "5-4-3-2-1", "present moment", "calm down", "calm me"],
        "reply": (
            "Try the **5-4-3-2-1 grounding exercise.** Take your time:\n\n"
            "1. Name **5** things you can see.\n"
            "2. Name **4** things you can feel (your feet on the floor, your clothes).\n"
            "3. Name **3** things you can hear.\n"
            "4. Name **2** things you can smell.\n"
            "5. Name **1** thing you can taste, or take one slow breath.\n\n"
            "Stop whenever you like."
        ),
    },
    "breathing": {
        "label": "Breathing",
        "keywords": ["breath", "breathe", "breathing", "relax"],
        "reply": (
            "Slow breathing can help you feel calmer. Breathe in gently for about 4 seconds, hold for 2 "
            "if that feels comfortable (or skip the hold), and breathe out for about 4 to 6 seconds.\n\n"
            "Open the **Breathing Exercise** page in the sidebar for an animated guide with a timer."
        ),
    },
    "professional_help": {
        "label": "When to seek help",
        "keywords": ["therapist", "therapy", "doctor", "professional", "counsel", "psychiatr", "psycholog",
                     "seek help", "need help"],
        "reply": (
            "Consider reaching out to a doctor or mental health professional if:\n\n"
            "- difficult feelings last more than a couple of weeks,\n"
            "- they affect your work, studies, sleep, appetite or relationships,\n"
            "- you feel unable to cope, or you have thoughts of harming yourself.\n\n"
            "Asking for help is a sign of strength. A family doctor is a good first step. "
            "For urgent situations, contact your local emergency number."
        ),
    },
    "about_screening": {
        "label": "About the screening",
        "keywords": ["screening", "questionnaire", "result", "score", "quiz", "test"],
        "reply": (
            "The **Screening** page asks 28 questions inspired by common scales for depression, anxiety, "
            "ADHD and sleep. It is an educational demo, not a diagnosis. Results show a transparent "
            "rule-based reading next to a machine-learning prediction trained on synthetic data."
        ),
    },
}

GREETING_WORDS = {"hello", "hi", "hey", "salam", "assalam"}
GREETING_PHRASES = ("good morning", "good evening", "good afternoon", "assalam")

DEFAULT_REPLY = (
    "Thanks for sharing. I'm a simple rule-based assistant, so I work best with topics like "
    "**stress, anxiety, low mood, sleep, focus, grounding or breathing**. "
    "Tap one of the buttons above, or tell me more in a few words."
)

WELCOME = (
    "Hi, I'm the Mentivara wellness assistant. I'm a **simple rule-based chatbot**, not an AI "
    "doctor and not a generative AI. I can share general tips on stress, grounding, breathing and "
    "sleep, and point you to professional help when it makes sense. How are you feeling today?"
)


def _matches(text, keywords):
    return any(re.search(r"\b" + re.escape(k), text) for k in keywords)


def _is_greeting(text):
    """True for short messages that start with a greeting (whole words only)."""
    words = re.findall(r"[a-z']+", text)
    if not words or len(words) > 4:
        return False
    return words[0] in GREETING_WORDS or text.startswith(GREETING_PHRASES)


def respond(user_text):
    """Return (reply_markdown, topic_key_or_None)."""
    if detect_crisis(user_text):
        return CRISIS_RESPONSE, "crisis"

    t = user_text.lower().replace("\u2019", "'")
    # Most specific topics first so 'grounding' beats 'calm'
    order = ["grounding", "breathing", "professional_help", "about_screening",
             "anxiety", "low_mood", "sleep", "focus", "stress"]
    for key in order:
        if _matches(t, TOPICS[key]["keywords"]):
            return TOPICS[key]["reply"] + "\n\n" + GENERAL_INFO_NOTE, key

    if _is_greeting(t):
        return "Hello! How are you feeling today? You can tell me, or pick a topic above.", "greeting"
    return DEFAULT_REPLY, None
