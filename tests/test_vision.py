"""Tests for the computer vision module (no physical webcam needed)."""

import os

import pytest
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")

from utils import cv_utils

pytestmark = pytest.mark.skipif(not cv_utils.CV2_AVAILABLE, reason="OpenCV is not installed")


@pytest.fixture
def blank():
    return cv_utils.np.zeros((240, 320, 3), dtype=cv_utils.np.uint8)


@pytest.fixture
def no_model(monkeypatch, tmp_path):
    """Pretend the MediaPipe model file is missing."""
    monkeypatch.setattr(cv_utils, "MODEL_PATH", str(tmp_path / "missing.task"))


@pytest.fixture
def video_file(tmp_path):
    """A short synthetic video that stands in for a webcam."""
    path = str(tmp_path / "cam.avi")
    writer = cv_utils.cv2.VideoWriter(path, cv_utils.cv2.VideoWriter_fourcc(*"MJPG"), 15, (160, 120))
    rng = cv_utils.np.random.default_rng(0)
    for _ in range(12):
        writer.write(rng.integers(0, 255, (120, 160, 3), dtype=cv_utils.np.uint8))
    writer.release()
    return path


def test_environment_report_lists_every_check():
    names = [row[0] for row in cv_utils.environment_report()]
    for expected in ["Python", "OpenCV", "Haar cascade file", "MediaPipe (Tasks API)", "Face landmarker model"]:
        assert expected in names


def test_haar_cascade_file_exists_and_loads():
    assert os.path.isfile(cv_utils.haar_path())
    assert _haar_ok()


def _haar_ok():
    return len(cv_utils.HaarDetector().detect(cv_utils.np.zeros((100, 100, 3), dtype=cv_utils.np.uint8))) == 0


def test_engine_handles_blank_frame_and_does_not_modify_input(blank, no_model):
    engine, _ = cv_utils.create_engine("auto", video_mode=False)
    before = blank.copy()
    out, info = engine.process(blank)
    engine.close()
    assert info["face_count"] == 0 and info["boxes"] == []
    assert out.shape == blank.shape
    assert (blank == before).all()


def test_falls_back_to_opencv_when_model_missing(no_model):
    engine, notes = cv_utils.create_engine("auto", video_mode=True)
    engine.close()
    assert engine.backend == "OpenCV Haar cascade"
    assert notes and "download_models.py" in notes[0]


def test_explicit_opencv_choice_skips_mediapipe(no_model):
    engine, notes = cv_utils.create_engine("opencv", video_mode=False)
    engine.close()
    assert engine.backend == "OpenCV Haar cascade" and notes == []


def test_open_camera_reports_clear_error_for_missing_source():
    cap, used, error = cv_utils.open_camera("/definitely/not/a/camera.avi")
    assert cap is None and used is None
    assert "Could not open a camera" in error and "Upload" in error


def test_open_camera_reads_frames_and_releases(video_file):
    cap, used, error = cv_utils.open_camera(video_file)
    assert cap is not None and error is None
    ok, frame = cap.read()
    cap.release()
    assert ok and frame.shape[:2] == (120, 160)
    assert not cap.isOpened()


def test_decode_image_rejects_garbage():
    assert cv_utils.decode_image(b"not an image") is None


def test_download_rejects_tiny_file_and_cleans_up(tmp_path):
    src = tmp_path / "tiny.bin"
    src.write_bytes(b"PK" + b"0" * 100)
    dest = tmp_path / "models" / "m.task"
    ok, message = cv_utils.download_model(url=src.as_uri(), dest=str(dest))
    assert not ok and "invalid" in message
    assert not dest.exists() and not os.path.exists(str(dest) + ".part")


def test_download_accepts_valid_looking_file(tmp_path):
    src = tmp_path / "ok.task"
    src.write_bytes(b"PK" + b"0" * 1_200_000)
    dest = tmp_path / "models" / "m.task"
    ok, message = cv_utils.download_model(url=src.as_uri(), dest=str(dest))
    assert ok and dest.exists()


def test_download_failure_is_reported_not_raised(tmp_path):
    ok, message = cv_utils.download_model(url=(tmp_path / "nope").as_uri(), dest=str(tmp_path / "m.task"))
    assert not ok and "Could not download" in message


def test_live_page_start_then_feed_ends_cleanly(monkeypatch, video_file, no_model):
    """Start the camera on the page with a video standing in for the webcam."""
    real_open = cv_utils.open_camera
    monkeypatch.setattr(cv_utils, "open_camera", lambda source=None, max_index=3: real_open(video_file))

    at = AppTest.from_file(APP, default_timeout=60).run()
    at.switch_page("pages/computer_vision.py").run()
    at.checkbox(key="cv_consent_live").check().run()
    start = [b for b in at.button if "Start camera" in b.label][0]
    start.click().run()                       # runs the live loop until the 'camera' stops sending frames
    assert not at.exception
    assert any("stopped sending frames" in e.value for e in at.error)
    assert at.session_state["cv_running"] is False
    assert "cv_cap" not in at.session_state   # camera was released


def test_live_page_shows_actionable_error_without_camera(monkeypatch, no_model):
    monkeypatch.setattr(cv_utils, "open_camera",
                        lambda source=None, max_index=3: (None, None, "Could not open a camera (test)."))
    at = AppTest.from_file(APP, default_timeout=60).run()
    at.switch_page("pages/computer_vision.py").run()
    at.checkbox(key="cv_consent_live").check().run()
    [b for b in at.button if "Start camera" in b.label][0].click().run()
    assert not at.exception
    assert any("Could not open a camera" in e.value for e in at.error)
    assert at.session_state["cv_running"] is False
