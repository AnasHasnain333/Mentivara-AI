import pytest
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")

from utils.breathing_component import breathing_html

PAGES = ["pages/screening.py", "pages/computer_vision.py", "pages/breathing_exercise.py",
         "pages/chatbot.py", "pages/about.py"]


def test_home_loads():
    at = AppTest.from_file(APP, default_timeout=60).run()
    assert not at.exception


@pytest.mark.parametrize("page", PAGES)
def test_every_page_loads(page):
    at = AppTest.from_file(APP, default_timeout=60).run()
    at.switch_page(page).run()
    assert not at.exception


def test_full_screening_flow_reaches_results():
    at = AppTest.from_file(APP, default_timeout=90).run()
    at.switch_page("pages/screening.py").run()
    at.button[0].click().run()
    for _ in range(28):
        at.radio[0].set_value(1)
        [b for b in at.button if b.label in ("Next ➡️", "Finish ✅")][0].click().run()
    assert at.session_state["page"] == "results"
    assert not at.exception


def test_chat_input_roundtrip():
    at = AppTest.from_file(APP, default_timeout=60).run()
    at.switch_page("pages/chatbot.py").run()
    at.chat_input[0].set_value("I feel anxious").run()
    assert not at.exception
    assert len(at.session_state["chat"]) == 2


def test_camera_is_off_until_consent():
    at = AppTest.from_file(APP, default_timeout=60).run()
    at.switch_page("pages/computer_vision.py").run()
    assert at.checkbox[0].value is False
    assert any("Tick the box" in i.value for i in at.info)
    assert at.session_state["cv_running"] is False
    assert "cv_cap" not in at.session_state


def test_breathing_widget_has_required_controls():
    html = breathing_html()
    for needle in ['id="start"', 'id="pause"', 'id="resume"', 'id="stop"', 'data-min="1"',
                   'data-min="3"', 'data-min="5"', 'id="skipHold"', 'role="progressbar"',
                   "prefers-reduced-motion"]:
        assert needle in html
    assert "localStorage" not in html and "fetch(" not in html  # no network or storage use


def test_camera_is_released_when_not_on_the_camera_page():
    """If a camera is still held in the session, any other page must release it."""
    class FakeCap:
        released = False

        def release(self):
            FakeCap.released = True

    at = AppTest.from_file(APP, default_timeout=60)
    at.session_state["cv_cap"] = FakeCap()      # seeded before the first run of the Home page
    at.session_state["cv_running"] = True
    at.run()
    assert FakeCap.released
    assert at.session_state["cv_running"] is False
    assert "cv_cap" not in at.session_state
