import time

import streamlit as st

from utils import cv_utils
from utils.ui import page_header, note, status_pill, release_camera_resources

page_header("📷 Camera-Based Wellness Interaction",
            "Live face detection with OpenCV and MediaPipe")
note(
    "<b>This is a computer vision demonstration, not a clinical assessment.</b> "
    "It only finds faces and draws boxes and landmarks. It does not recognise people, read emotions, "
    "or tell anything about your mental health. Nothing is recorded or saved."
)
st.write("")


def show_image(target, bgr):
    """Display a BGR image (works across Streamlit versions)."""
    rgb = bgr[:, :, ::-1]
    try:
        target.image(rgb, channels="RGB", width="stretch")
    except TypeError:
        target.image(rgb, channels="RGB", use_container_width=True)


def explain_missing_opencv():
    st.error(
        "OpenCV could not be loaded, so the camera demo is unavailable. The rest of the app still works.\n\n"
        f"Details: `{cv_utils.CV2_ERROR}`\n\n"
        "Fix: install the project dependencies into **the same Python environment that runs Streamlit**:\n\n"
        "`.\\.venv313\\Scripts\\python.exe -m pip install -r requirements313.txt`"
    )


if not cv_utils.CV2_AVAILABLE:
    release_camera_resources()
    explain_missing_opencv()
    st.stop()

# ------------------------------------------------------------------ setup status
with st.expander("System check", expanded=False):
    for name, ok, detail in cv_utils.environment_report():
        st.markdown(f"{'✅' if ok else '⚠️'} **{name}**: `{detail}`")

if cv_utils.MEDIAPIPE_AVAILABLE and not cv_utils.model_present():
    st.info(
        "**Optional upgrade:** download the MediaPipe face model (about 4 MB, one time) to add the facial "
        "landmark mesh. Without it, the app uses OpenCV's built-in face detector (boxes only)."
    )
    if st.button("⬇️ Download face model"):
        with st.spinner("Downloading..."):
            ok, message = cv_utils.download_model()
        (st.success if ok else st.error)(message)
        if ok:
            st.rerun()
elif not cv_utils.MEDIAPIPE_AVAILABLE:
    st.caption(f"MediaPipe is not available ({cv_utils.MEDIAPIPE_ERROR}). Using OpenCV face detection.")

BACKENDS = {"Auto (best available)": "auto", "MediaPipe landmarks": "mediapipe", "OpenCV boxes only": "opencv"}


@st.cache_resource(show_spinner=False)
def still_engine(prefer):
    return cv_utils.create_engine(prefer, video_mode=False)[0]


def analyse_still(data, prefer):
    bgr = cv_utils.decode_image(data)
    if bgr is None:
        st.error("That image could not be read. Please try a JPG or PNG.")
        return
    if bgr.shape[1] > 960:  # keep large photos fast
        scale = 960 / bgr.shape[1]
        bgr = cv_utils.cv2.resize(bgr, (960, int(bgr.shape[0] * scale)))
    engine = still_engine(prefer)
    out, info = engine.process(bgr)
    show_image(st, out)
    n = info["face_count"]
    label = f"{n} face{'s' if n != 1 else ''} detected" if n else "No face detected"
    st.markdown(status_pill(label, n > 0) + f" &nbsp; <small>{info['backend']}</small>", unsafe_allow_html=True)
    if not n:
        st.caption("Try a front-facing photo with even lighting and nothing covering the face.")


tab_live, tab_snap, tab_upload = st.tabs(["🎥 Live camera", "📸 Snapshot", "🖼️ Upload a photo"])

# ------------------------------------------------------------------ LIVE CAMERA
with tab_live:
    st.write("The camera stays **off** until you tick the box and press **Start camera**. "
             "Press **Stop camera** or leave this page and it is released immediately.")
    consent = st.checkbox("I understand why the camera is used and agree to turn it on for this demo.",
                          key="cv_consent_live")
    ss = st.session_state
    ss.setdefault("cv_running", False)

    if not consent:
        release_camera_resources()
        st.info("Tick the box above to show the camera controls.")
    else:
        c1, c2, c3 = st.columns(3)
        backend_label = c1.selectbox("Detector", list(BACKENDS), key="cv_backend")
        cam_choice = c2.selectbox("Camera", ["Auto-detect", "0", "1", "2"], key="cv_cam",
                                  help="Auto-detect tries cameras 0, 1 and 2.")
        show_mesh = c3.checkbox("Show full mesh", value=False, key="cv_mesh",
                                help="Draws every landmark connection (needs the MediaPipe model).")
        prefer = BACKENDS[backend_label]

        b1, b2 = st.columns(2)
        start = b1.button("▶ Start camera", type="primary", disabled=ss.cv_running)
        stop = b2.button("■ Stop camera", disabled=not ss.cv_running)
        if start:
            ss.cv_running = True
            ss.pop("cv_error", None)
        if stop:
            release_camera_resources()

        status_ph = st.empty()
        frame_ph = st.empty()

        if ss.get("cv_error"):
            st.error(ss.cv_error)

        if not ss.cv_running:
            status_ph.markdown(status_pill("Camera off", False), unsafe_allow_html=True)
            if not ss.get("cv_error"):
                frame_ph.info("Press **Start camera** when you are ready.")
        else:
            # ---- open the camera once and keep it in session state across reruns
            if ss.get("cv_cap") is None:
                with st.spinner("Starting camera..."):
                    source = None if cam_choice == "Auto-detect" else int(cam_choice)
                    cap, used, error = cv_utils.open_camera(source)
                if cap is None:
                    release_camera_resources()
                    ss.cv_error = error
                    st.rerun()
                ss.cv_cap = cap
            # ---- (re)create the detector if the choice changed
            key = (prefer,)
            if ss.get("cv_engine") is None or ss.get("cv_engine_key") != key:
                if ss.get("cv_engine") is not None:
                    ss.cv_engine.close()
                try:
                    with st.spinner("Loading face detector..."):
                        ss.cv_engine, notes = cv_utils.create_engine(prefer, video_mode=True)
                    ss.cv_engine_key = key
                    for n in notes:
                        st.warning(n)
                except Exception as exc:
                    release_camera_resources()
                    ss.cv_error = f"Face detector could not start: {exc}"
                    st.rerun()

            cap, engine = ss.cv_cap, ss.cv_engine
            engine.show_mesh = show_mesh
            failures, fps, last = 0, 0.0, time.time()
            while ss.cv_running:
                ok, frame = cap.read()
                if not ok or frame is None:
                    failures += 1
                    if failures >= 30:  # camera unplugged, taken by another app, or stream ended
                        release_camera_resources()
                        ss.cv_error = ("The camera stopped sending frames. Check that it is connected and "
                                       "not used by another app, then press Start camera again.")
                        st.rerun()
                    time.sleep(0.03)
                    continue
                failures = 0
                frame = cv_utils.cv2.flip(frame, 1)  # mirror view
                out, info = engine.process(frame)
                now = time.time()
                fps = 0.85 * fps + 0.15 * (1 / max(now - last, 1e-6))
                last = now
                show_image(frame_ph, out)
                n = info["face_count"]
                label = f"Face Detected ({n})" if n else "No face detected"
                status_ph.markdown(
                    status_pill("Camera on", True) + " &nbsp; " + status_pill(label, n > 0)
                    + f" &nbsp; <small>{info['backend']} · {fps:.0f} FPS</small>",
                    unsafe_allow_html=True,
                )
                time.sleep(max(0.0, 0.04 - (time.time() - now)))  # cap near 25 FPS to save CPU

        with st.expander("Camera not working?"):
            st.markdown(
                "- **Permission blocked:** Windows Settings → Privacy & security → Camera → turn on "
                "*Let desktop apps access your camera*.\n"
                "- **Camera in use:** close Zoom, Teams, the Windows Camera app and other browser tabs.\n"
                "- **Wrong camera:** pick `0`, `1` or `2` in the Camera box.\n"
                "- **Test outside Streamlit:** run `python scripts/test_webcam.py` (see the README).\n"
                "- **No webcam:** use the Upload tab. Nothing else in the app needs a camera."
            )

# ------------------------------------------------------------------ SNAPSHOT
with tab_snap:
    st.write("Take one photo with your browser's camera. It is analysed in memory and not stored.")
    if st.checkbox("I agree to use my camera to take a single photo.", key="cv_consent_snap"):
        shot = st.camera_input("Take a photo")
        if shot is not None:
            analyse_still(shot.getvalue(), "auto")
    else:
        st.info("Tick the box to show the camera.")

# ------------------------------------------------------------------ UPLOAD
with tab_upload:
    st.write("No webcam? Upload a photo of a face (yours, or one you have permission to use). "
             "It is analysed in memory only.")
    upload = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
    if upload is None:
        st.info("Upload an image to see face detection in action.")
    else:
        analyse_still(upload.getvalue(), "auto")

with st.expander("How it works (for your presentation)"):
    st.markdown(
        "1. **Capture:** OpenCV reads frames from the webcam (`cv2.VideoCapture`).\n"
        "2. **Detect:** MediaPipe Face Landmarker finds faces and facial landmark points. If its model "
        "file is not installed, OpenCV's Haar cascade finds face boxes instead.\n"
        "3. **Draw:** bounding boxes, a label, and (with MediaPipe) the face contour mesh are drawn on the frame.\n"
        "4. **Show:** the annotated frame is displayed in Streamlit about 25 times per second.\n\n"
        "Detection only finds *where* a face is. It cannot tell who someone is, how they feel, or "
        "anything about their health."
    )
