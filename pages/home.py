import streamlit as st

from utils.ui import APP_NAME, TAGLINE, page_header, card, note
from utils.treatment_plans import DISCLAIMER

page_header(f"🧠 {APP_NAME}", TAGLINE)
st.write(
    "A learning project that combines a machine-learning questionnaire, a camera demo "
    "built with OpenCV and MediaPipe, a guided breathing exercise and a simple "
    "wellness chatbot in one Streamlit app."
)
note(DISCLAIMER)
st.write("")

features = [
    ("📋 Screening", "Answer 28 questions on depression, anxiety, ADHD and sleep. "
     "See a rule-based result next to a trained model's prediction.", "pages/screening.py", "Start screening"),
    ("📷 Computer Vision", "See OpenCV and MediaPipe find faces on your own camera. "
     "A technology demo only. It never judges emotions or health.", "pages/computer_vision.py", "Open camera demo"),
    ("🌬️ Breathing Exercise", "A gentle animated guide with a timer. "
     "Works without a camera and you can stop at any time.", "pages/breathing_exercise.py", "Start breathing"),
    ("💬 Chatbot", "A simple rule-based assistant with stress tips, grounding exercises "
     "and guidance on when to seek support.", "pages/chatbot.py", "Open chatbot"),
]

for row in (features[:2], features[2:]):
    cols = st.columns(2)
    for col, (title, body, target, label) in zip(cols, row):
        with col:
            card(title, body)
            if st.button(label, key=f"home_{target}", use_container_width=True):
                st.switch_page(target)
    st.write("")

st.caption("The Breathing Exercise needs nothing from you except a minute of time.")
