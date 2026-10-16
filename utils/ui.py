"""Shared look and feel: one stylesheet and a few small layout helpers."""

import streamlit as st

APP_NAME = "Mentivara AI"
TAGLINE = "Multimodal AI for Mental Wellness Support"

# Calm blue / teal / white / neutral palette
TEAL = "#0F766E"
BLUE = "#2563A6"
INK = "#16323F"
MUTED = "#5B7083"
SOFT = "#EEF5F7"
BORDER = "#D5E3E8"

SEVERITY_COLOR = {
    "None": "#2E9E6B",
    "Mild": "#D9B227",
    "Moderate": "#E0782B",
    "Severe": "#CC3F3F",
}

_CSS = f"""
<style>
  .block-container {{ max-width: 1000px; padding-top: 2rem; padding-bottom: 3rem; }}
  h1, h2, h3 {{ color: {INK}; letter-spacing: -0.01em; }}
  [data-testid="stSidebar"] {{ background: {SOFT}; }}
  .mv-hero h1 {{ font-size: 2.4rem; margin-bottom: 0.2rem; }}
  .mv-hero p {{ color: {MUTED}; font-size: 1.1rem; margin-top: 0; }}
  .mv-card {{
      border: 1px solid {BORDER}; border-radius: 10px; padding: 1rem 1.2rem;
      background: #fff; height: 100%;
  }}
  .mv-card h4 {{ margin: 0 0 0.3rem 0; color: {TEAL}; }}
  .mv-card p {{ margin: 0; color: {INK}; font-size: 0.95rem; }}
  .mv-note {{
      border-left: 4px solid {BLUE}; background: {SOFT}; padding: 0.7rem 1rem;
      border-radius: 4px; color: {INK}; font-size: 0.93rem;
  }}
  .mv-badge {{
      display: inline-block; padding: 0.1rem 0.6rem; border-radius: 999px;
      color: #fff; font-size: 0.8rem; font-weight: 600;
  }}
  .mv-status {{
      display: inline-block; padding: 0.25rem 0.8rem; border-radius: 999px;
      font-weight: 600; font-size: 0.9rem; color: #fff;
  }}
  .stButton > button[kind="primary"] {{ background: {TEAL}; border-color: {TEAL}; }}
  @media (max-width: 640px) {{ .mv-hero h1 {{ font-size: 1.7rem; }} }}
</style>
"""


def inject_css():
    st.markdown(_CSS, unsafe_allow_html=True)


def page_header(title, subtitle=None):
    html = f"<div class='mv-hero'><h1>{title}</h1>"
    if subtitle:
        html += f"<p>{subtitle}</p>"
    st.markdown(html + "</div>", unsafe_allow_html=True)


def card(title, body):
    st.markdown(f"<div class='mv-card'><h4>{title}</h4><p>{body}</p></div>", unsafe_allow_html=True)


def note(text):
    st.markdown(f"<div class='mv-note'>{text}</div>", unsafe_allow_html=True)


def badge(level):
    color = SEVERITY_COLOR.get(level, MUTED)
    return f"<span class='mv-badge' style='background:{color}'>{level}</span>"


def status_pill(text, ok):
    color = "#2E9E6B" if ok else "#8A99A6"
    return f"<span class='mv-status' style='background:{color}'>{text}</span>"


def release_camera_resources():
    """Release the webcam and detector held in this session. Safe to call at any time."""
    ss = st.session_state
    cap = ss.pop("cv_cap", None)
    if cap is not None:
        try:
            cap.release()
        except Exception:
            pass
    engine = ss.pop("cv_engine", None)
    if engine is not None:
        try:
            engine.close()
        except Exception:
            pass
    ss.pop("cv_engine_key", None)
    ss["cv_running"] = False
