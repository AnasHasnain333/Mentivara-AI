import streamlit as st

from utils.ui import APP_NAME, TAGLINE, page_header, note
from utils.treatment_plans import DISCLAIMER
from utils.report_utils import SYNTHETIC_NOTE
from utils.safety_utils import URGENT_HELP_NOTICE

page_header("ℹ️ About", f"{APP_NAME}: {TAGLINE}")

st.write(
    "Mentivara AI is a student project built for an AI bootcamp final project. It shows how "
    "machine learning, computer vision and simple conversational design can be combined into one "
    "Streamlit app for wellness education."
)
note(DISCLAIMER)
st.write("")

st.subheader("Technologies used")
st.markdown(
    "- **Machine learning:** scikit-learn RandomForest classifiers (one per domain) trained on synthetic data.\n"
    "- **Rule-based scoring:** a transparent weighted-sum scorer that is shown next to the model.\n"
    "- **Computer vision:** OpenCV (webcam capture and a built-in Haar face detector) and MediaPipe Face Landmarker (face boxes and a landmark mesh).\n"
    "- **Interactive UI:** Streamlit, Plotly charts, and a small HTML/JS component for the breathing animation.\n"
    "- **Chatbot:** keyword rules with curated answers. It is not generative AI."
)

st.subheader("Limitations")
st.markdown(
    f"- {SYNTHETIC_NOTE}\n"
    "- The questionnaire is *inspired by* PHQ-9, GAD-7, ASRS and ISI but is not the official instruments.\n"
    "- The camera demo only finds faces and draws boxes and landmarks. It does not recognise people, read emotions or assess health.\n"
    "- The chatbot's safety check uses keywords and can miss indirect wording.\n"
    "- Nothing here replaces a qualified professional."
)

st.subheader("Privacy")
st.markdown(
    "- No accounts, no database and no analytics.\n"
    "- Questionnaire answers live only in your browser session. The report is generated when you click download.\n"
    "- The webcam is read by the computer running the app, only after you press Start. Frames are processed in memory and never saved or sent anywhere by this code.\n"
    "- Run the app on your own computer to keep everything on your own device."
)

st.subheader("Need urgent help?")
st.write(URGENT_HELP_NOTICE)

st.subheader("Author")
st.markdown(
    "**Anas Hasnain**, BS Artificial Intelligence · AI Intern at Decoder Lab  \n"
    "[GitHub](https://github.com/AnasHasnain333) · "
    "[LinkedIn](https://linkedin.com/in/anas-hasnain-a28277323)"
)
