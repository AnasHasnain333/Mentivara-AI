import plotly.graph_objects as go
import streamlit as st

from utils import questions as Q
from utils.questions import QUESTIONS, DISORDERS, SEVERITY_LEVELS, ANSWER_LABELS
from utils.treatment_plans import TREATMENT_PLANS, GENERAL_GUIDELINES, DISCLAIMER
from utils.model_utils import safe_predict, train_now, highest_severity, response_summary
from utils.report_utils import build_report, SYNTHETIC_NOTE, SCORING_NOTE
from utils.safety_utils import self_harm_item_endorsed, CRISIS_RESPONSE
from utils.ui import SEVERITY_COLOR, TEAL, INK, page_header, badge, note


def reset_quiz():
    st.session_state.page = "intro"
    st.session_state.answers = [None] * len(QUESTIONS)
    st.session_state.q_index = 0


page_header("📋 Wellness Screening", "A short questionnaire with two independent readings of your answers")

# ------------------------------------------------------------------ INTRO
if st.session_state.page == "intro":
    st.write(
        "The 28 questions are written in the style of widely used screening scales "
        "(PHQ-9, GAD-7, ASRS, ISI) and cover **depression, anxiety, ADHD and insomnia**. "
        "They are **not** the official validated instruments."
    )
    st.write(
        "Your answers are scored two ways: a transparent **rule-based scorer** and a "
        "**machine-learning model** (one RandomForest per domain)."
    )
    note(DISCLAIMER)
    st.write("")
    st.write("Answer each question for roughly the last two weeks:")
    st.markdown("`0 = Never` · `1 = Sometimes` · `2 = Often` · `3 = Almost Always`")
    if st.button("Start screening", type="primary"):
        st.session_state.page = "quiz"
        st.rerun()

# ------------------------------------------------------------------ QUIZ
elif st.session_state.page == "quiz":
    i = st.session_state.q_index
    total = len(QUESTIONS)
    question, disorder, _ = QUESTIONS[i]

    st.progress(i / total, text=f"Question {i + 1} of {total}")
    st.subheader(question)
    st.caption(f"Category: {disorder}")

    saved = st.session_state.answers[i]
    choice = st.radio(
        "Your answer",
        options=[0, 1, 2, 3],
        format_func=lambda x: ANSWER_LABELS[x],
        index=saved if saved is not None else 0,
        key=f"radio_{i}",
        horizontal=True,
    )

    col_back, col_next = st.columns(2)
    with col_back:
        if i > 0 and st.button("⬅️ Back", use_container_width=True):
            st.session_state.answers[i] = choice
            st.session_state.q_index -= 1
            st.rerun()
    with col_next:
        label = "Next ➡️" if i < total - 1 else "Finish ✅"
        if st.button(label, type="primary", use_container_width=True):
            st.session_state.answers[i] = choice
            if i < total - 1:
                st.session_state.q_index += 1
            else:
                st.session_state.page = "results"
            st.rerun()

    if st.button("Cancel and go back to the start"):
        reset_quiz()
        st.rerun()

# ------------------------------------------------------------------ RESULTS
elif st.session_state.page == "results":
    answers = [a if a is not None else 0 for a in st.session_state.answers]
    st.header("🩺 Your preliminary results")
    note(DISCLAIMER)

    if self_harm_item_endorsed(answers):
        st.error(
            "You indicated thoughts of being better off dead or hurting yourself. "
            "Thank you for being honest. Please take that seriously."
        )
        st.markdown(CRISIS_RESPONSE)

    # ---- model prediction (graceful if missing) ----
    with st.spinner("Analysing your answers..."):
        results, error = safe_predict(answers)

    if error == "missing_model":
        st.warning(
            "The trained model file (`model/mental_health_model.pkl`) was not found, so only "
            "your questionnaire summary can be shown. Train it now (takes a few seconds), "
            "or run `python train_model.py` in a terminal."
        )
        if st.button("Train model now", type="primary"):
            with st.spinner("Generating synthetic data and training..."):
                try:
                    train_now()
                    st.rerun()
                except Exception as exc:
                    st.error(f"Training failed: {exc}")
    elif error:
        st.error(
            f"The model could not be loaded ({error}). A common cause is a scikit-learn "
            "version change. Re-run `python train_model.py` to rebuild the model."
        )

    # ---- summary of responses ----
    summary = response_summary(answers)
    st.subheader("Summary of your responses")
    cols = st.columns(len(DISORDERS))
    for col, disorder in zip(cols, DISORDERS):
        s = summary[disorder]
        col.metric(f"{TREATMENT_PLANS[disorder]['icon']} {disorder}", f"{s['mean']:.1f} / 3",
                   help="Average answer on this domain's items (0 = Never, 3 = Almost Always).")
    st.caption("Average answer per domain. Items answered 'Often' or 'Almost Always' are listed below.")

    # ---- chart ----
    if results:
        fig = go.Figure()
        if hasattr(Q, "max_score"):
            fig.add_trace(go.Bar(
                x=DISORDERS, y=[Q.max_score(d) for d in DISORDERS],
                marker_color="#E3ECEF", name="Maximum possible", hoverinfo="skip",
            ))
        fig.add_trace(go.Bar(
            x=DISORDERS,
            y=[results[d]["raw_score"] for d in DISORDERS],
            marker_color=[SEVERITY_COLOR[results[d]["ml_severity"]] for d in DISORDERS],
            text=[results[d]["ml_severity"] for d in DISORDERS],
            textposition="outside",
            name="Your weighted score",
        ))
        fig.update_layout(
            title="Weighted score per domain (bar colour = model-predicted class)",
            barmode="overlay", yaxis_title="Weighted score", height=360,
            margin=dict(t=60, b=20), showlegend=False,
            font=dict(color=INK, size=14), plot_bgcolor="white",
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---- per-domain details ----
    any_flag = False
    for disorder in DISORDERS:
        plan = TREATMENT_PLANS[disorder]
        r = results[disorder] if results else None
        s = summary[disorder]
        if r:
            level = highest_severity(r["rule_severity"], r["ml_severity"])
            title = (f"{plan['icon']} {disorder}: rule-based {r['rule_severity']} · "
                     f"model {r['ml_severity']}")
        else:
            level = "None"
            title = f"{plan['icon']} {disorder}: average answer {s['mean']:.1f} / 3"

        with st.expander(title, expanded=(level != "None")):
            if r:
                st.markdown(
                    f"Rule-based reading: {badge(r['rule_severity'])} &nbsp; "
                    f"Model reading: {badge(r['ml_severity'])} &nbsp; "
                    f"Weighted score: **{r['raw_score']}**",
                    unsafe_allow_html=True,
                )
                if r["rule_severity"] != r["ml_severity"]:
                    st.caption("The two readings differ. The rule-based reading is the "
                               "transparent one: you can check it by hand.")
            if s["frequent"]:
                st.markdown("**Items you answered 'Often' or 'Almost Always':**")
                for q, label in s["frequent"]:
                    st.markdown(f"- {q} ({label})")
            else:
                st.markdown("No items in this domain were answered 'Often' or 'Almost Always'.")

            if level != "None":
                any_flag = True
                st.markdown("#### Wellness suggestions")
                for protocol in plan["protocols"]:
                    st.markdown(f"**{protocol['title']}**")
                    for step in protocol["steps"]:
                        st.markdown(f"- {step}")
                if level == "Severe":
                    st.error("This domain is in the highest range of this screening. Consider "
                             "talking with a doctor or a qualified mental health professional.")
            else:
                st.success("This domain did not reach the Mild range in this screening.")

            if r:
                with st.popover("Technical details"):
                    st.write("Random-forest vote share per severity class:")
                    for lvl in SEVERITY_LEVELS:
                        st.write(f"{lvl}: {r['ml_probabilities'].get(lvl, 0) * 100:.0f}%")
                    st.caption("These are the model's relative scores on synthetic training data. "
                               "They are **not** the probability that you have a condition.")

    st.subheader("🌿 General well-being guidelines")
    for g in GENERAL_GUIDELINES:
        st.markdown(f"- {g}")
    if results and not any_flag:
        st.success("No domain reached the Mild range in this screening.")

    # ---- transparency ----
    with st.expander("How the scoring works and what this result means", expanded=False):
        st.markdown(f"**Scoring.** {SCORING_NOTE}")
        if hasattr(Q, "THRESHOLDS"):
            st.table({
                "Level": list(Q.THRESHOLDS.keys()),
                "Share of the maximum score": [f"at least {int(v * 100)}%" for v in Q.THRESHOLDS.values()],
            })
        st.markdown(f"**Model limitation.** {SYNTHETIC_NOTE}")
        st.markdown("Treat these results as an educational overview of how you have been "
                    "feeling, not as a diagnosis.")

    # ---- download + retake ----
    st.download_button(
        "⬇️ Download report (.txt)",
        data=build_report(answers, results),
        file_name="mentivara_screening_report.txt",
        mime="text/plain",
    )
    if st.button("🔄 Retake screening"):
        reset_quiz()
        st.rerun()
