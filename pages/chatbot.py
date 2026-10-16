import streamlit as st

from utils.chatbot_utils import TOPICS, WELCOME, GENERAL_INFO_NOTE, respond
from utils.ui import page_header, note
from utils.safety_utils import URGENT_HELP_NOTICE

page_header("💬 Wellness Chatbot", "Simple, rule-based tips. Not a doctor and not generative AI.")
note(
    "This assistant matches keywords to a small set of prepared answers. It cannot diagnose, "
    "give medical advice or handle emergencies. " + URGENT_HELP_NOTICE
)
st.write("")

QUICK = ["stress", "anxiety", "grounding", "breathing", "sleep", "professional_help"]


def add_exchange(user_text):
    reply, topic = respond(user_text)
    st.session_state.chat.append(("user", user_text))
    st.session_state.chat.append(("assistant", reply))
    if topic and topic not in ("greeting",):
        st.session_state.chat_topics[topic] = st.session_state.chat_topics.get(topic, 0) + 1


# quick-topic buttons
cols = st.columns(3)
for n, key in enumerate(QUICK):
    if cols[n % 3].button(TOPICS[key]["label"], key=f"quick_{key}", use_container_width=True):
        add_exchange(TOPICS[key]["label"])
        st.rerun()

user_input = st.chat_input("Tell me how you're feeling or ask for a tip...")
if user_input:
    add_exchange(user_input)
    st.rerun()

# conversation
with st.chat_message("assistant"):
    st.markdown(WELCOME)
if not st.session_state.chat:
    st.caption("Empty so far. Tap a topic above or type a message.")
for role, msg in st.session_state.chat:
    with st.chat_message(role):
        st.markdown(msg)

# topics summary (replaces the old 'risk snapshot': counting keywords is not a risk measure)
if st.session_state.chat:
    c1, c2 = st.columns(2)
    with c1:
        with st.expander("Topics we talked about"):
            topics = st.session_state.chat_topics
            if topics:
                for key, n in topics.items():
                    label = TOPICS[key]["label"] if key in TOPICS else "Safety message"
                    st.write(f"- {label}: {n}")
                st.caption("This only counts topics. It is not a measure of your wellbeing. "
                           "For that, try the Screening page.")
            else:
                st.write("No specific topics yet.")
    with c2:
        if st.button("Clear conversation", use_container_width=True):
            st.session_state.chat = []
            st.session_state.chat_topics = {}
            st.rerun()
