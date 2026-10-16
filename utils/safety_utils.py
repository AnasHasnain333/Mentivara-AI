"""
Safety helpers: crisis-language detection and standard disclaimers.

LIMITATION: keyword matching is a simple safety net, not a guarantee. It will miss
indirect or unusual wording and can flag harmless sentences. The app therefore
always shows a general "if you need urgent help" notice and never relies on this
check alone.
"""

import re

from utils.questions import QUESTIONS
from utils.treatment_plans import CRISIS_KEYWORDS

# Phrases (matched on normalised, lower-case text) that suggest possible immediate danger.
_EXTRA_PATTERNS = [
    r"\bkill (myself|me)\b",
    r"\bend (my|it all|my own) life\b",
    r"\bsuicid\w*",
    r"\bwant(ed)? to die\b",
    r"\bdon'?t want to (live|be alive|be here)\b",
    r"\bno reason to (live|go on)\b",
    r"\bbetter off (dead|without me)\b",
    r"\b(hurt|harm|cut|injure) myself\b",
    r"\bself[- ]?harm\w*",
    r"\boverdose\b",
    r"\bcan'?t go on\b",
    r"\btake my own life\b",
]

_PATTERNS = [re.compile(p) for p in _EXTRA_PATTERNS]
_PATTERNS += [re.compile(re.escape(k.lower())) for k in CRISIS_KEYWORDS]


def _normalise(text):
    text = text.lower().replace("\u2019", "'").replace("\u2018", "'")
    return re.sub(r"\s+", " ", text).strip()


def detect_crisis(text):
    """True if the message contains wording that may indicate immediate danger."""
    t = _normalise(text or "")
    return any(p.search(t) for p in _PATTERNS)


# Supportive response shown when crisis language is detected.
CRISIS_RESPONSE = (
    "I'm really sorry you're feeling this way, and I'm glad you said it out loud. "
    "**Your safety matters most right now.**\n\n"
    "- If you might act on these thoughts, or you are in immediate danger, **contact your "
    "local emergency number or go to the nearest emergency department now.**\n"
    "- If you can, **reach out to someone you trust** (a family member, friend or "
    "neighbour) and ask them to stay with you.\n"
    "- A crisis line can talk with you right away. You can find free, local helplines "
    "for your country at https://findahelpline.com.\n\n"
    "I'm a simple, rule-based program, so I can't provide crisis support myself. "
    "You deserve to talk to a real person."
)

URGENT_HELP_NOTICE = (
    "Mentivara AI is not an emergency service. If you or someone else is in immediate "
    "danger, contact your local emergency number or a crisis line "
    "(free local helplines: https://findahelpline.com)."
)


def self_harm_item_indices():
    """Indices of questionnaire items that ask about self-harm / being better off dead."""
    flagged = []
    for i, (text, _d, _w) in enumerate(QUESTIONS):
        t = text.lower()
        if "better off dead" in t or "hurting yourself" in t or "self-harm" in t:
            flagged.append(i)
    return flagged


def self_harm_item_endorsed(answers):
    """True if the user answered anything above 'Never' on a self-harm item."""
    return any((answers[i] or 0) >= 1 for i in self_harm_item_indices() if i < len(answers))
