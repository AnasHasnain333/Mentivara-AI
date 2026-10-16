import streamlit.components.v1 as components
import streamlit as st

from utils.breathing_component import breathing_html
from utils.ui import page_header, note

page_header("🌬️ Guided Breathing & Relaxation", "A gentle, animated breathing guide. No camera needed.")

st.write(
    "Pick a length and a pace, then press **Start**. The circle grows as you breathe in, "
    "stays still while you hold, and shrinks as you breathe out. You can pause, resume or stop "
    "whenever you want."
)

# Everything below runs in the browser, so reruns never reset the timer.
components.html(breathing_html(), height=760, scrolling=True)

st.caption("Sessions are rounded to a whole number of breaths, so the timer can differ from "
           "the chosen length by a few seconds.")

note(
    "Breathing exercises can help you feel calmer for a moment. They are not a treatment for "
    "any mental health condition. Never force yourself to hold your breath. If you feel dizzy or "
    "uncomfortable, stop and breathe normally."
)
