# ============================================================
# Mentivara AI - AI-Based Mental Health Screening and Wellness Support System
# Developer: Anas Hasnain (BS Artificial Intelligence)

# ============================================================

import streamlit as st

from utils.ui import APP_NAME, TAGLINE, inject_css, release_camera_resources
from utils.treatment_plans import DISCLAIMER
from utils.safety_utils import URGENT_HELP_NOTICE

st.set_page_config(
    page_title=f"{APP_NAME} - {TAGLINE}",
    page_icon="🧠",
    layout="centered",
)
inject_css()

# ---------- shared session state (survives page switches) ----------
from utils.questions import QUESTIONS  # noqa: E402

defaults = {
    "page": "intro",                        # screening flow: intro / quiz / results
    "answers": [None] * len(QUESTIONS),
    "q_index": 0,
    "chat": [],                             # list of (role, message)
    "chat_topics": {},                      # topic -> number of times discussed
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------- navigation ----------
navigation = st.navigation(
    [
        st.Page("pages/home.py", title="Home", icon="🏠", default=True),
        st.Page("pages/screening.py", title="Screening", icon="📋"),
        st.Page("pages/computer_vision.py", title="Computer Vision", icon="📷"),
        st.Page("pages/breathing_exercise.py", title="Breathing Exercise", icon="🌬️"),
        st.Page("pages/chatbot.py", title="Chatbot", icon="💬"),
        st.Page("pages/about.py", title="About", icon="ℹ️"),
    ]
)

# Never leave the webcam running when the user is on another page
#if navigation.title != "Computer Vision":
# release_camera_resources()

with st.sidebar:
    st.markdown(f"**🧠 {APP_NAME}**")
    st.caption(TAGLINE)
    st.info(DISCLAIMER)
    st.caption(URGENT_HELP_NOTICE)

navigation.run()
